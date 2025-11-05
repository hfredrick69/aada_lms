# AADA LMS - Security & Compliance

## Overview

The AADA Learning Management System handles sensitive student educational records and must comply with federal regulations governing privacy and data protection. This document outlines compliance requirements, implementation details, and ongoing responsibilities.

## Regulatory Frameworks

### FERPA (Family Educational Rights and Privacy Act)

**Applicability**: The AADA LMS stores and processes educational records subject to FERPA.

**Key Requirements**:
1. **Student Consent**: Written consent required to disclose education records to third parties
2. **Access Rights**: Students must be able to view their own records
3. **Amendment Rights**: Students can request corrections to inaccurate records
4. **Directory Information**: Must define what constitutes directory information
5. **Audit Trail**: Log who accessed student records and when

**AADA Implementation**:
- Role-based access control (students can only access own records)
- Admin/instructor access logged and auditable
- Secure authentication (httpOnly JWT cookies)
- Data export controls (admin only)
- Retention policies enforced

### PHI (Protected Health Information)

**Applicability**: Externship records may contain health-related information.

**Key Requirements** (HIPAA-adjacent):
1. **Minimum Necessary**: Only collect health information required for educational purposes
2. **Access Controls**: Limit access to authorized personnel
3. **Encryption**: Protect data in transit and at rest
4. **Breach Notification**: Procedures for handling data breaches

**AADA Implementation**:
- Externship records marked as sensitive
- HTTPS required in production
- Database encryption at rest (PostgreSQL)
- Access logging for audit purposes
- Limited fields collected (supervisor info, hours, verification)

### State Regulations

**GNPEC (Georgia Nonpublic Postsecondary Education Commission)**:
- Attendance tracking requirements
- Transcript record-keeping
- Refund policy compliance
- Withdrawal documentation

**Implementation**:
- Attendance table with clock-in/clock-out records
- Transcript generation and retention
- Withdrawal/refund tracking tables
- Compliance reports generated from database

## Data Classification

### Highly Sensitive (FERPA Protected)
- **Student academic records**: Grades, transcripts, attendance
- **Financial records**: Tuition payments, refunds, withdrawals
- **Disciplinary records**: Complaints, violations
- **Credentials**: Certifications, licenses

**Access Control**: Students (own only), Instructors (enrolled courses), Admins (all)

### Sensitive
- **Externship records**: Supervisor info, placement sites, hours
- **User authentication data**: Email, hashed passwords
- **Enrollment information**: Program assignments, status

**Access Control**: Role-based with logging

### Internal Use
- **Course content metadata**: Module titles, descriptions
- **Program information**: Curriculum structure
- **System configuration**: Non-sensitive settings

**Access Control**: Authenticated users

### Public
- **Program descriptions**: General course information
- **Institution information**: Contact, accreditation

**Access Control**: No restriction

## Technical Security Controls

### Authentication & Authorization

**Implemented** (See AUTH_SECURITY.md for details):
- JWT tokens in httpOnly cookies
- Bcrypt password hashing (12 rounds)
- Role-based access control (student, instructor, admin)
- Session timeout and auto-refresh
- CORS restrictions

**Production Requirements**:
- HTTPS enforced (TLS 1.2+)
- Strong password policy enforced
- Account lockout after failed login attempts
- Multi-factor authentication (planned)

### Data Protection

**In Transit**:
- HTTPS/TLS for all connections
- Certificate pinning (future consideration)
- Secure cookie flags (Secure, HttpOnly, SameSite)

**At Rest**:
- PostgreSQL database encryption (production)
- Encrypted backups
- Secure file storage for uploads
- Environment variable secrets management

**Application Level**:
- Input validation and sanitization
- Parameterized SQL queries (SQLAlchemy ORM)
- XSS protection (React escapes by default)
- CSRF protection (SameSite cookies)

### Network Security

**Development**:
- Docker internal network for service communication
- Exposed ports limited to necessary services
- No production secrets in docker-compose.yml

**Production**:
- Private VPC for database
- Application firewall (WAF)
- Rate limiting on API endpoints
- DDoS protection (CloudFlare/AWS Shield)
- IP allowlisting for admin functions (optional)

### Access Control Implementation

**Database Level**:
```python
# Example: Students can only query their own records
@router.get("/transcripts", response_model=List[TranscriptRead])
def list_transcripts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "student":
        # Restrict to own records
        return db.query(Transcript).filter(
            Transcript.user_id == current_user.id
        ).all()
    elif current_user.role == "admin":
        # Admin can see all
        return db.query(Transcript).all()
    else:
        raise HTTPException(status_code=403, detail="Access denied")
```

**Frontend Level**:
```typescript
// Route protection based on role
<Route path="/students" element={
  <ProtectedRoute requiredRole={["admin", "instructor"]}>
    <StudentsPage />
  </ProtectedRoute>
} />
```

## Audit & Logging

### Audit Requirements

**FERPA Audit Events**:
- Who accessed student records
- When access occurred
- What records were accessed
- Purpose of access (if applicable)
- Any modifications made

**System Audit Events**:
- Authentication events (login, logout, failures)
- Authorization failures (permission denied)
- Data exports (transcript downloads, reports)
- Administrative actions (user creation, role changes)
- System configuration changes

### Logging Implementation

**Database Audit Table** (Planned):
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),  -- e.g., "VIEW_TRANSCRIPT", "EXPORT_DATA"
    resource_type VARCHAR(50),  -- e.g., "Transcript", "User"
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    details JSONB
);
```

**Application Logging**:
```python
# Structured logging
import logging
logger = logging.getLogger(__name__)

@router.get("/transcripts/{transcript_id}")
def get_transcript(transcript_id: int, current_user: User = ...):
    logger.info(
        "Transcript accessed",
        extra={
            "user_id": current_user.id,
            "transcript_id": transcript_id,
            "action": "VIEW_TRANSCRIPT"
        }
    )
    # ... fetch transcript
```

### Log Retention

**Production Requirements**:
- **Application logs**: 90 days minimum
- **Audit logs**: 3 years (FERPA requirement)
- **Security logs**: 1 year minimum
- **System logs**: 30 days

**Storage**:
- Centralized logging (CloudWatch, ELK, Splunk)
- Immutable storage for audit logs
- Automated archival to cold storage
- Regular backup verification

## Data Retention & Disposal

### Retention Policies

| Data Type | Retention Period | Justification |
|-----------|------------------|---------------|
| Student records | 5 years post-graduation | FERPA + State requirements |
| Transcripts | Permanent | Educational records |
| Financial records | 7 years | IRS requirements |
| Attendance logs | 5 years | State compliance |
| Audit logs | 3 years | FERPA audit requirement |
| Application logs | 90 days | Operational needs |
| User accounts (inactive) | 2 years | Business decision |

### Secure Disposal

**Data Deletion Procedure**:
1. Soft delete with retention period (mark as deleted, hide from queries)
2. Hard delete after retention period expires
3. Automated purge jobs scheduled monthly
4. Verification of deletion completion
5. Audit log of deletion events

**Implementation**:
```python
# Soft delete (set deleted_at timestamp)
user.deleted_at = datetime.utcnow()
db.commit()

# Exclude from queries
active_users = db.query(User).filter(User.deleted_at.is_(None)).all()

# Purge job (runs monthly)
cutoff_date = datetime.utcnow() - timedelta(days=730)  # 2 years
users_to_purge = db.query(User).filter(
    User.deleted_at < cutoff_date
).all()
for user in users_to_purge:
    db.delete(user)  # Hard delete
db.commit()
```

## Incident Response

### Data Breach Procedure

**Detection**:
- Monitor for unusual access patterns
- Alert on bulk data exports
- Automated security scanning
- User-reported suspicious activity

**Response Steps**:
1. **Contain**: Immediately revoke compromised credentials
2. **Investigate**: Determine scope and impact
3. **Notify**: Inform affected students within 72 hours (FERPA)
4. **Remediate**: Fix vulnerability, enhance security
5. **Document**: Complete incident report for audit
6. **Review**: Post-mortem and process improvement

**Notification Template**:
```
Subject: Important Security Notice - AADA LMS

Dear [Student Name],

We are writing to inform you of a security incident that may have affected 
your educational records in the AADA Learning Management System.

What happened: [Brief description]
What information was involved: [Data types]
What we are doing: [Remediation steps]
What you should do: [Recommended actions]

We take your privacy seriously and are committed to protecting your information.

Contact: security@aada.edu
```

### Security Incident Categories

**P1 - Critical**:
- Unauthorized access to student records
- Data breach or exfiltration
- System compromise
- Ransomware attack

**Response Time**: Immediate (within 1 hour)

**P2 - High**:
- Attempted unauthorized access (blocked)
- Vulnerability discovered
- Authentication bypass attempt

**Response Time**: Within 4 hours

**P3 - Medium**:
- Failed login attempts (pattern detected)
- Minor security policy violation
- Suspicious activity reported

**Response Time**: Within 24 hours

## Compliance Checklist

### FERPA Compliance

- [x] Role-based access control implemented
- [x] Students can access own records
- [ ] Annual privacy notice sent to students
- [ ] Consent forms for third-party disclosure
- [ ] Audit logging of record access
- [ ] Data retention policy documented
- [ ] Procedures for amendment requests
- [ ] Directory information policy defined
- [ ] Training for staff on FERPA requirements
- [ ] Regular compliance audits scheduled

### Security Best Practices

- [x] Passwords hashed with bcrypt
- [x] HTTPS enforced (production)
- [x] SQL injection prevention (ORM)
- [x] XSS prevention (React escaping)
- [x] CSRF protection (SameSite cookies)
- [ ] Rate limiting on API endpoints
- [ ] Input validation on all endpoints
- [ ] Output encoding
- [ ] Security headers configured
- [ ] Dependency vulnerability scanning
- [ ] Regular security updates
- [ ] Penetration testing annually

### Data Protection

- [x] Data classification defined
- [ ] Encryption at rest (production)
- [x] Encryption in transit (HTTPS)
- [ ] Secure backup procedures
- [ ] Disaster recovery plan
- [ ] Data breach response plan
- [ ] Third-party vendor assessments
- [ ] Privacy impact assessment completed

## Third-Party Services

### Current Integrations

**Development**:
- None currently (all services self-hosted in Docker)

**Planned**:
- Email service (SendGrid, SES) - Student notifications
- Cloud storage (S3) - File uploads, backups
- CDN (CloudFront) - Content delivery
- Payment processor (Stripe) - Tuition payments

### Vendor Assessment

**Before Integration**:
1. Review privacy policy and terms of service
2. Assess data handling practices
3. Verify compliance certifications (SOC 2, ISO 27001)
4. Execute Data Processing Agreement (DPA)
5. Document data flows and access controls
6. Configure minimum necessary access
7. Monitor for security updates

### Data Processing Agreements

**Required Elements**:
- Purpose of data processing
- Types of data shared
- Security measures required
- Data retention and deletion
- Breach notification requirements
- Right to audit compliance
- Liability and indemnification

## User Training

### Staff Training Requirements

**All Staff**:
- FERPA basics (annual)
- Password security
- Phishing awareness
- Incident reporting

**Administrators**:
- Advanced FERPA compliance
- Data classification
- Access control management
- Audit log review
- Incident response procedures

**Instructors**:
- FERPA for educators
- Appropriate student data access
- Grading privacy
- Communication security

### Training Schedule

- Initial training: Within 30 days of hire
- Annual refresher: Every 12 months
- Updated training: When policies change
- Incident-based training: After security events

## Monitoring & Compliance

### Ongoing Monitoring

**Automated**:
- Failed login attempts (threshold alerts)
- Bulk data access (flag for review)
- Unusual access patterns (anomaly detection)
- Security vulnerability scans (weekly)
- Dependency updates (daily)

**Manual**:
- Audit log review (monthly)
- Access control review (quarterly)
- Security policy review (annually)
- Compliance assessment (annually)

### Regular Assessments

**Internal Audits**:
- Quarterly access control review
- Monthly audit log sampling
- Annual full compliance audit

**External Audits**:
- Annual penetration testing
- Compliance audit (if required by accreditation)
- Third-party security assessment

**Metrics to Track**:
- Failed login attempts per day
- Average time to detect incidents
- Average time to remediate vulnerabilities
- Number of compliance violations
- Training completion rates

## Production Security Configuration

### Environment Variables (Production)

```bash
# Secrets (use secrets manager)
SECRET_KEY=<256-bit random key>
DATABASE_URL=<encrypted connection string>
POSTGRES_PASSWORD=<strong password>

# Security settings
ALLOWED_ORIGINS=https://admin.aada.edu,https://learn.aada.edu
COOKIE_SECURE=True
COOKIE_SAMESITE=strict
SESSION_TIMEOUT=1800  # 30 minutes

# Compliance
AUDIT_LOGGING=True
LOG_LEVEL=INFO
DATA_RETENTION_DAYS=1825  # 5 years
```

### Security Headers

**Required Headers** (Nginx/CloudFront):
```nginx
# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# XSS protection
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

# HTTPS enforcement
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Referrer policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Database Security

**PostgreSQL Configuration**:
- SSL required for connections
- Strong password policy enforced
- Least privilege access (app user cannot drop tables)
- Network access restricted to application subnet
- Regular backups with encryption
- Point-in-time recovery enabled

**Access Control**:
```sql
-- Application user (limited privileges)
CREATE USER aada_app WITH PASSWORD '<strong_password>';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO aada_app;

-- Backup user (read-only)
CREATE USER aada_backup WITH PASSWORD '<strong_password>';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO aada_backup;

-- Admin user (full access, use sparingly)
-- Use default postgres user only for schema migrations
```

## Future Compliance Enhancements

1. **GDPR Compliance** (if serving EU students):
   - Right to be forgotten implementation
   - Data portability features
   - Consent management

2. **Accessibility (WCAG 2.1 AA)**:
   - Screen reader compatibility
   - Keyboard navigation
   - Color contrast compliance

3. **SOC 2 Certification**:
   - Formal security controls
   - Independent audit
   - Trust center for transparency

4. **Enhanced Audit Trail**:
   - Blockchain-based immutable logs
   - Real-time compliance dashboards
   - Automated compliance reporting

---

**Last Updated**: 2025-11-04  
**Maintained By**: Compliance Officer & Security Team  
**Next Review**: 2026-02-04
