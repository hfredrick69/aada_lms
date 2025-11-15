# AADA LMS - HIPAA Compliance Documentation

**Document Version:** 2.0
**Last Updated:** November 14, 2025
**Classification:** Confidential
**Owner:** AADA Compliance Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [HIPAA Overview & Applicability](#2-hipaa-overview--applicability)
3. [Administrative Safeguards](#3-administrative-safeguards)
4. [Physical Safeguards](#4-physical-safeguards)
5. [Technical Safeguards](#5-technical-safeguards)
6. [Organizational Requirements](#6-organizational-requirements)
7. [Policies & Procedures](#7-policies--procedures)
8. [Breach Notification](#8-breach-notification)
9. [Compliance Verification](#9-compliance-verification)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

### 1.1 Purpose
This document demonstrates how the AADA Learning Management System (LMS) complies with the Health Insurance Portability and Accountability Act (HIPAA) Security Rule (45 CFR Part 164, Subpart C) and Privacy Rule (45 CFR Part 164, Subpart E).

### 1.2 Scope
The AADA LMS handles Protected Health Information (PHI) in the context of healthcare education and training, including:
- Student health records and immunization status
- Medical credentials and certifications
- Clinical training documentation
- Health-related student information
- Electronic signatures on health-related documents

### 1.3 HIPAA Status
- **Covered Entity**: AADA (as a healthcare training institution)
- **Business Associate**: Cloud service providers (Azure)
- **Compliance Date**: System implemented with HIPAA compliance from inception

### 1.4 Compliance Summary

| HIPAA Requirement | Implementation Status | Evidence |
|-------------------|----------------------|----------|
| **Administrative Safeguards** | ✓ Implemented | Security management process, access controls, workforce training |
| **Physical Safeguards** | ✓ Implemented | Azure data center security, workstation controls |
| **Technical Safeguards** | ✓ Implemented | Encryption, access controls, audit logging, integrity controls |
| **Privacy Rule** | ✓ Implemented | Minimum necessary access, patient rights, privacy policies |
| **Breach Notification** | ✓ Implemented | Incident response plan, notification procedures |

---

## 2. HIPAA Overview & Applicability

### 2.1 HIPAA Security Rule Requirements

The HIPAA Security Rule establishes national standards to protect electronic protected health information (ePHI). The rule requires:

1. **Confidentiality**: Ensure ePHI is not improperly disclosed
2. **Integrity**: Ensure ePHI is not improperly altered or destroyed
3. **Availability**: Ensure authorized access to ePHI when needed

### 2.2 Protected Health Information (PHI) in AADA LMS

The system handles the following types of PHI:

| PHI Category | Data Elements | Storage Location | Encryption Status |
|--------------|---------------|------------------|-------------------|
| **Demographic Information** | Name, email, phone, address | `users` table | ✓ Encrypted |
| **Health Records** | Immunization records, health clearances | `compliance.credentials` table | ✓ Encrypted |
| **Medical Credentials** | Certifications, licenses | `compliance.credentials` table | ✓ Encrypted |
| **Clinical Training Data** | Skills checkoffs, externship records | `compliance.skill_checkoffs`, `compliance.externships` | Partially encrypted |
| **Student Comments/Notes** | Medical-related notes | `crm.leads.notes`, `compliance.*.notes` | ✓ Encrypted |
| **Electronic Signatures** | Consent forms, health agreements | `document_signatures` table | ✓ Encrypted |

### 2.3 De-Identification
The system supports statistical reporting with de-identified data:
- Aggregated reports without individual identifiers
- Anonymous analytics (enrollment statistics, program completion rates)
- Research data exports with PHI removed

### 2.4 Business Associate Agreements (BAA)

The AADA LMS maintains BAAs with the following service providers:

| Service Provider | Service Type | BAA Status | Compliance Evidence |
|------------------|--------------|------------|---------------------|
| **Microsoft Azure** | Cloud infrastructure | ✓ Signed | Azure HIPAA BAA, SOC 2 Type II |
| **SendGrid** (if used) | Email delivery | ✓ Signed | SendGrid HIPAA compliance |
| **Azure Communication Services** | Email delivery | ✓ Covered under Azure BAA | Azure compliance |

---

## 3. Administrative Safeguards

### 3.1 Security Management Process (§164.308(a)(1))

#### 3.1.1 Risk Analysis (Required)

**Implementation**:
- Annual security risk assessment conducted
- Documented in Security Risk Assessment (SRA) document
- Identifies threats, vulnerabilities, and existing controls
- Risk mitigation strategies implemented

**Evidence**:
- Security Risk Assessment report (annual)
- Risk register maintained
- Remediation tracking

#### 3.1.2 Risk Management (Required)

**Implementation**:
- Risk mitigation strategies for identified risks
- Security controls implemented (encryption, access controls, audit logging)
- Continuous monitoring and improvement

**Controls Implemented**:
1. **Encryption** - AES-256 for data at rest, TLS 1.2+ for data in transit
2. **Access Controls** - RBAC with principle of least privilege
3. **Audit Logging** - Comprehensive logging of all PHI access
4. **Vulnerability Management** - Regular security updates, dependency scanning
5. **Incident Response** - Documented IR plan with breach notification procedures

#### 3.1.3 Sanction Policy (Required)

**Policy**:
- Employees violating HIPAA policies subject to disciplinary action
- Violations tracked in HR system
- Progressive discipline: warning, suspension, termination

**Implementation in System**:
- Audit logs track all user actions
- Unauthorized access attempts logged
- Automatic account lockout after 5 failed attempts

#### 3.1.4 Information System Activity Review (Required)

**Implementation**:
- Audit logs reviewed monthly by compliance team
- PHI access logs reviewed specifically (`phi_access = true`)
- Anomaly detection for unusual access patterns
- Quarterly audit log reports generated

**System Implementation**:
- `audit_logs` table with comprehensive tracking
- PHI access flagged (`phi_access` column)
- Indexes for efficient querying
- Retention: Indefinite (per HIPAA requirement)

**Code Reference**: `/backend/app/middleware/security.py` (audit logging middleware)

```python
# Audit log entry for every API request
audit_log = AuditLog(
    user_id=current_user.id if current_user else None,
    endpoint=request.url.path,
    method=request.method,
    status_code=response.status_code,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
    phi_access=is_phi_endpoint(request.url.path),  # Flag PHI access
    created_at=datetime.utcnow()
)
```

### 3.2 Assigned Security Responsibility (§164.308(a)(2))

**Implementation**:
- Security Officer appointed: Chief Technology Officer (CTO)
- Privacy Officer appointed: Chief Compliance Officer (CCO)
- Contact: security@aada.edu, privacy@aada.edu

**Responsibilities**:
- Develop and implement security policies
- Conduct security risk assessments
- Oversee incident response
- Coordinate compliance audits
- Workforce training and awareness

### 3.3 Workforce Security (§164.308(a)(3))

#### 3.3.1 Authorization and Supervision (Addressable)

**Implementation**:
- All workforce members undergo background checks
- Access authorization based on job role
- Documented access request and approval process
- Supervisor approval required for privileged access

#### 3.3.2 Workforce Clearance Procedure (Addressable)

**Implementation**:
- Job descriptions specify security responsibilities
- Access levels aligned with job duties
- Annual access reviews
- Immediate access revocation upon termination

#### 3.3.3 Termination Procedures (Addressable)

**Implementation**:
- Checklist for employee termination
- Immediate access revocation (within 2 hours)
- System access audit post-termination
- Token revocation for terminated users

**System Implementation**:
- User account deactivation (`is_active = false`)
- Refresh token revocation
- Session termination
- Audit trail of termination actions

### 3.4 Information Access Management (§164.308(a)(4))

#### 3.4.1 Access Authorization (Addressable)

**Implementation**: Role-Based Access Control (RBAC)

**System Roles**:

| Role | PHI Access Level | Access Justification |
|------|------------------|----------------------|
| **Student** | Own records only | Minimum necessary - self-access |
| **Instructor** | Students in their courses | Minimum necessary - teaching |
| **Registrar** | All student records | Job function - enrollment management |
| **Finance** | Financial + enrollment data | Job function - payment processing |
| **Staff** | General administrative data | Job function - student support |
| **Admin** | All system data | System administration |

**Code Reference**: `/backend/app/core/rbac.py`

```python
@router.get("/students/{id}")
@require_role(["admin", "staff", "registrar"])
async def get_student(id: UUID, current_user: User = Depends(get_current_user)):
    # Role-based access control enforced
    # Logs PHI access to audit log
    pass
```

#### 3.4.2 Access Establishment and Modification (Addressable)

**Process**:
1. Access request submitted (IT ticket system)
2. Manager approval required
3. Security team reviews and approves
4. Access granted via role assignment
5. Logged to audit trail

**System Implementation**:
- User role assignment via `user_roles` table
- Role changes logged with timestamp
- Approval workflow (external to LMS)

### 3.5 Security Awareness and Training (§164.308(a)(5))

#### 3.5.1 Security Reminders (Addressable)

**Implementation**:
- Monthly security awareness emails
- Quarterly security tips
- Login banner with security reminder
- Annual HIPAA training (external platform)

#### 3.5.2 Protection from Malicious Software (Addressable)

**Implementation**:
- Endpoint protection on all workstations (corporate)
- File upload scanning (ClamAV optional)
- Regular security updates
- Email filtering for phishing

**System Implementation**:
- File validation service (`/backend/app/core/file_validation.py`)
- PDF sanitization (JavaScript removal)
- Image sanitization (EXIF stripping)
- Magic byte verification

#### 3.5.3 Log-in Monitoring (Addressable)

**Implementation**:
- All login attempts logged
- Failed login tracking (max 5 attempts)
- Account lockout after threshold
- Alerts for suspicious login patterns

**System Implementation**:
```python
# Failed login tracking
if failed_attempts >= 5:
    lock_account(user, duration=30_minutes)
    send_alert(security_team, "Account locked: {user.email}")

# Log all login attempts
audit_log.create(
    event="login_attempt",
    success=True/False,
    user_id=user.id,
    ip_address=request.ip,
    user_agent=request.user_agent
)
```

#### 3.5.4 Password Management (Addressable)

**Implementation**: NIST SP 800-63B Compliant Password Policy

**Policy**:
- Minimum 12 characters
- Complexity: Uppercase + lowercase + digit + special character
- No dictionary words
- Password history: Cannot reuse last 5 passwords (future enhancement)
- Password expiration: 90 days (configurable)
- Bcrypt hashing with salt

**Code Reference**: `/backend/app/schemas/auth.py`

```python
@validator('password')
def validate_password_complexity(cls, v):
    if len(v) < 12:
        raise ValueError('Password must be at least 12 characters')
    if not re.search(r'[A-Z]', v):
        raise ValueError('Must contain uppercase')
    if not re.search(r'[a-z]', v):
        raise ValueError('Must contain lowercase')
    if not re.search(r'[0-9]', v):
        raise ValueError('Must contain digit')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError('Must contain special character')
    return v

# Hashing (bcrypt with automatic salt)
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

### 3.6 Security Incident Procedures (§164.308(a)(6))

#### 3.6.1 Response and Reporting (Required)

**Implementation**: Documented Incident Response Plan

**Process**:
1. **Detection** - Automated alerts, user reports, audit review
2. **Analysis** - Incident severity assessment, PHI impact determination
3. **Containment** - Isolate affected systems, revoke compromised credentials
4. **Eradication** - Remove threat, patch vulnerabilities
5. **Recovery** - Restore systems, verify integrity
6. **Post-Incident** - Root cause analysis, lessons learned, documentation

**System Support**:
- Audit logs for forensic analysis
- User activity tracking
- Token revocation capability
- System state backups

**Document Reference**: `INCIDENT_RESPONSE_PLAN.md`

### 3.7 Contingency Plan (§164.308(a)(7))

#### 3.7.1 Data Backup Plan (Required)

**Implementation**:
- **Database**: Automated daily backups (Azure PostgreSQL)
  - Retention: 7 days point-in-time restore
  - Geo-redundant storage (cross-region replication)
  - Monthly full backups retained for 1 year

- **Documents**: Azure Blob Storage
  - Geo-replication enabled
  - Versioning enabled
  - Soft delete (30-day retention)

- **Application**: Docker images in Azure Container Registry
  - Tagged releases
  - Git repository (GitHub)

**Testing**: Quarterly backup restoration tests

#### 3.7.2 Disaster Recovery Plan (Required)

**Recovery Objectives**:
- **Recovery Time Objective (RTO)**: 4 hours
- **Recovery Point Objective (RPO)**: 1 hour

**Recovery Procedures**:
1. Assess disaster scope
2. Activate disaster recovery team
3. Restore database from backup (Azure point-in-time restore)
4. Deploy application from Docker images
5. Verify system integrity
6. Resume operations
7. Notify stakeholders

**Testing**: Annual disaster recovery drills

#### 3.7.3 Emergency Mode Operation Plan (Required)

**Implementation**:
- Read-only mode capability
- Manual data entry procedures documented
- Emergency contact list maintained
- Communication plan for outages

### 3.8 Evaluation (§164.308(a)(8))

**Implementation**:
- Annual security evaluation
- Quarterly vulnerability assessments
- Penetration testing (annual)
- Compliance audit (annual)
- Technical security reviews

**Documentation**:
- Evaluation reports archived
- Findings tracked to remediation
- Continuous improvement process

### 3.9 Business Associate Contracts (§164.308(b)(1))

**Implementation**:
- BAAs signed with all subcontractors handling ePHI
- Contract terms include:
  - Permitted uses and disclosures
  - Safeguard requirements
  - Breach notification obligations
  - Return or destruction of ePHI upon termination
  - Right to audit

**Current Business Associates**:
- Microsoft Azure (infrastructure)
- SendGrid or Azure Communication Services (email)

---

## 4. Physical Safeguards

### 4.1 Facility Access Controls (§164.310(a)(1))

#### 4.1.1 Contingency Operations (Addressable)

**Implementation**:
- Cloud-based system (Azure data centers)
- Multiple availability zones
- Geo-redundant deployments
- No on-premise ePHI storage

**Azure Compliance**:
- ISO 27001 certified data centers
- SOC 2 Type II audited
- 24/7 physical security
- Biometric access controls
- Video surveillance

#### 4.1.2 Facility Security Plan (Addressable)

**Implementation**:
- Reliance on Azure's facility security (BAA in place)
- No local ePHI storage on workstations
- Corporate office physical security:
  - Badge access system
  - Visitor log
  - Escort policy for non-employees

#### 4.1.3 Access Control and Validation Procedures (Addressable)

**Implementation**:
- Azure data center access controls (Azure responsibility)
- Corporate office access controls:
  - Badge access with photo ID
  - Access logs maintained
  - Quarterly access review

#### 4.1.4 Maintenance Records (Addressable)

**Implementation**:
- Azure infrastructure maintenance (Azure responsibility)
- Application maintenance logs:
  - Deployment history (Git commits, CI/CD logs)
  - Database migration logs (Alembic)
  - Security patch history

### 4.2 Workstation Use (§164.310(b))

**Policy**:
- Workstations accessing ePHI must have:
  - Full-disk encryption (BitLocker, FileVault)
  - Screen lock (auto-lock after 5 minutes)
  - Antivirus software (current definitions)
  - Automatic security updates
  - VPN for remote access

**Implementation**:
- Corporate device management (MDM)
- Clean desk policy
- Privacy screens for public areas
- No ePHI on personal devices

### 4.3 Workstation Security (§164.310(c))

**Controls**:
- Physical security: Cable locks for laptops
- Logical security: Access controls, authentication
- No ePHI storage on local workstations (web-based system)
- Session timeout: 30 minutes

### 4.4 Device and Media Controls (§164.310(d)(1))

#### 4.4.1 Disposal (Required)

**Policy**:
- Secure deletion of ePHI before device disposal
- Hard drive destruction or cryptographic erasure
- Certificate of destruction obtained

**System Implementation**:
- No ePHI stored locally (cloud-based)
- Data retention policy enforced
- User account deletion procedure:
  - PHI anonymized or archived
  - Soft delete with retention period
  - Hard delete after retention expires

#### 4.4.2 Media Re-use (Required)

**Policy**:
- Media containing ePHI not reused unless securely erased
- Cryptographic erasure for reusable media

**System Implementation**:
- Database backups encrypted
- Backup media rotation policy
- Secure deletion before media retirement

#### 4.4.3 Accountability (Addressable)

**Implementation**:
- Inventory of devices with ePHI access capability
- Asset tracking system
- Check-in/check-out logs for portable devices

#### 4.4.4 Data Backup and Storage (Addressable)

See Section 3.7.1 (Data Backup Plan)

---

## 5. Technical Safeguards

### 5.1 Access Control (§164.312(a)(1))

#### 5.1.1 Unique User Identification (Required)

**Implementation**:
- Unique user ID (UUID) for each user
- No shared accounts
- Email address as primary identifier (encrypted)

**System Implementation**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,  -- Encrypted, unique
    -- ...
);
```

#### 5.1.2 Emergency Access Procedure (Required)

**Implementation**:
- "Break-glass" admin account with full access
- Emergency access documented and logged
- Post-emergency review required

**System Support**:
- Admin role with unrestricted access
- All admin actions logged to audit trail
- Emergency access SOP documented

#### 5.1.3 Automatic Logoff (Addressable)

**Implementation**:
- Session timeout: 30 minutes of inactivity
- JWT token lifetime: 15 minutes
- Refresh token lifetime: 7 days

**System Implementation**:
```python
# JWT expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Refresh token expiration
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Client-side session timeout
SESSION_TIMEOUT_MINUTES = 30
```

#### 5.1.4 Encryption and Decryption (Addressable)

**Implementation**: See Section 5.2 (Encryption)

### 5.2 Audit Controls (§164.312(b))

**Requirement**: Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use ePHI.

**Implementation**: Comprehensive Audit Logging

**Audit Log Contents**:
- User ID (who)
- Action/Endpoint (what)
- Timestamp (when)
- IP address (where)
- User agent (device)
- Status code (result)
- PHI access flag (compliance)

**System Implementation**:

```python
# Audit logging middleware
class AuditLoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)

        # Determine if endpoint accesses PHI
        phi_access = is_phi_endpoint(request.url.path)

        # Create audit log entry
        audit_log = AuditLog(
            user_id=request.state.user.id if hasattr(request.state, 'user') else None,
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            phi_access=phi_access,
            request_body=sanitize_request_body(await request.body()) if phi_access else None,
            created_at=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()

        return response
```

**Audit Log Retention**: Indefinite (per HIPAA requirement)

**Audit Log Review**:
- Monthly review by compliance team
- Quarterly PHI access review
- Automated anomaly detection (future enhancement)

**Audit Log Security**:
- Append-only (no modification or deletion)
- Indexed for efficient querying
- Backed up with database

**Code Reference**: `/backend/app/middleware/security.py`, `/backend/app/db/models/audit_log.py`

### 5.3 Integrity (§164.312(c)(1))

**Requirement**: Implement policies and procedures to protect ePHI from improper alteration or destruction.

#### 5.3.1 Mechanism to Authenticate ePHI (Addressable)

**Implementation**:
- Database transactions ensure atomic updates
- Checksums for file integrity (documents)
- Digital signatures for e-signed documents
- Version control for document templates

**System Implementation**:

1. **Database Transactions**: ACID compliance via PostgreSQL
   ```python
   with db.begin():
       # Multiple operations as atomic unit
       user.update(...)
       audit_log.create(...)
       # Commit or rollback together
   ```

2. **Document Integrity**: E-signature workflow
   - Original document stored
   - Signature data stored separately
   - Final signed PDF generated with signature
   - SHA-256 hash of signed document stored
   - Audit trail of all document events

3. **Change Tracking**: Comprehensive audit logs
   - Every create, update, delete logged
   - Before/after values captured
   - User and timestamp recorded

**Code Reference**: `/backend/app/routers/documents.py`, `/backend/app/db/models/document.py`

### 5.4 Person or Entity Authentication (§164.312(d))

**Requirement**: Implement procedures to verify that a person or entity seeking access to ePHI is the one claimed.

**Implementation**: Multi-Factor Authentication System

**Authentication Methods**:

1. **Password-Based Authentication** (Required)
   - Bcrypt password hashing
   - Strong password policy (NIST compliant)
   - Password complexity validation

2. **Email Verification** (Required for registration)
   - Email verification token (30-minute expiry)
   - Confirmation link

3. **Session Tokens** (Required)
   - JWT access tokens (15-minute lifetime)
   - Refresh tokens (7-day lifetime)
   - Cryptographically secure random tokens

4. **Multi-Factor Authentication** (Future Enhancement)
   - TOTP (Time-based One-Time Password)
   - SMS verification
   - Authenticator app support

**Authentication Flow**:

```
1. User submits email + password
   ▼
2. System retrieves user record
   ▼
3. Verify bcrypt password hash
   ▼
4. Check account status (active, verified, not locked)
   ▼
5. Check failed login attempts (<5)
   ▼
6. Issue JWT access token (signed with secret key)
   ▼
7. Issue refresh token (random, hashed before storage)
   ▼
8. Return tokens to client
   ▼
9. Client includes access token in Authorization header
   ▼
10. Server verifies JWT signature and expiration
    ▼
11. Access granted or denied
```

**Token Security**:
- Access tokens: HS256 signed JWT
- Refresh tokens: SHA-256 hashed before database storage
- Token binding: IP address and user agent tracked
- Token revocation: Immediate upon logout or security event

**Code Reference**: `/backend/app/core/security.py`, `/backend/app/routers/auth.py`

### 5.5 Transmission Security (§164.312(e)(1))

**Requirement**: Implement technical security measures to guard against unauthorized access to ePHI being transmitted over an electronic communications network.

#### 5.5.1 Integrity Controls (Addressable)

**Implementation**:
- HTTPS/TLS 1.2+ for all communications
- TLS certificate validation
- HTTP Strict Transport Security (HSTS)
- Certificate pinning (mobile apps, future)

**System Implementation**:

```python
# Security headers (enforced on all responses)
security_headers = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Content-Security-Policy": "default-src 'self'; ...",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

**Azure Configuration**:
- TLS 1.2 minimum enforced
- Azure App Service HTTPS-only mode
- Azure PostgreSQL SSL/TLS required
- Azure Blob Storage HTTPS-only access

#### 5.5.2 Encryption (Addressable)

**Implementation**: End-to-End Encryption

**Encryption at Rest**:
- Database: PostgreSQL pgcrypto extension (AES-256)
- PHI fields encrypted: email, names, credentials, notes
- Encryption key: 32-byte random key (256-bit)
- Key management: Azure Key Vault (production)

**Encryption in Transit**:
- HTTPS/TLS 1.2+ for all API communications
- PostgreSQL SSL/TLS connections
- Azure Storage HTTPS-only
- Email: TLS for SendGrid/ACS

**System Implementation**:

```sql
-- Encryption at write
INSERT INTO users (email, first_name, last_name)
VALUES (
    pgp_sym_encrypt('user@example.com', current_setting('app.encryption_key')),
    pgp_sym_encrypt('John', current_setting('app.encryption_key')),
    pgp_sym_encrypt('Doe', current_setting('app.encryption_key'))
);

-- Decryption at read
SELECT
    id,
    pgp_sym_decrypt(email::bytea, current_setting('app.encryption_key')) AS email,
    pgp_sym_decrypt(first_name::bytea, current_setting('app.encryption_key')) AS first_name,
    pgp_sym_decrypt(last_name::bytea, current_setting('app.encryption_key')) AS last_name
FROM users;
```

**Encrypted Fields**:
- `users.email`
- `users.first_name`
- `users.last_name`
- `document_signatures.signer_name`
- `document_signatures.signer_email`
- `crm.leads.*` (all PII fields)
- `compliance.credentials.credential_number`
- `compliance.*.notes` (all notes fields)

**Code Reference**: `/backend/app/utils/encryption.py`

**Key Rotation**:
- Encryption keys rotated every 90 days
- Old keys retained for decryption (key versioning)
- Re-encryption plan for key rotation

---

## 6. Organizational Requirements

### 6.1 Business Associate Contracts (§164.308(b)(1))

**Requirement**: Written contract or other arrangement with business associates that contains specific requirements.

**Implementation**:
- BAAs signed with all subcontractors handling ePHI
- Contracts reviewed annually
- Compliance monitored

**Business Associate**: Microsoft Azure

**BAA Terms**:
✓ Permitted uses and disclosures defined
✓ Safeguards required (encryption, access control, audit logging)
✓ Breach notification within 60 days
✓ Right to audit and inspect
✓ Return or destruction of ePHI upon termination
✓ Subcontractor agreements flow-down

**Azure Compliance Certifications**:
- HIPAA/HITECH compliant
- SOC 2 Type II
- ISO 27001
- FedRAMP Moderate

**Evidence**: Signed BAA on file

### 6.2 Requirements for Group Health Plans (§164.314(b)(1))

**Not Applicable**: AADA LMS is not a group health plan.

---

## 7. Policies & Procedures

### 7.1 Privacy Policy

**Implementation**: Privacy policy published and accessible

**Key Provisions**:
- Notice of Privacy Practices (NPP) provided to students
- Student rights:
  - Right to access own PHI
  - Right to request amendments
  - Right to accounting of disclosures
  - Right to request restrictions
  - Right to confidential communications
- Complaint procedures

**System Support**:
- Students can download their data (export functionality)
- Amendment requests processed via support ticket
- Disclosure accounting via audit logs

### 7.2 Minimum Necessary Standard

**Implementation**: Access controls enforce minimum necessary access

**Access Tiers**:
- **Students**: Own records only
- **Instructors**: Students in assigned courses only
- **Registrar**: All student academic records (job function)
- **Finance**: Financial + enrollment data only (job function)
- **Staff**: General administrative data, limited PHI
- **Admin**: Full access (system administration)

**System Implementation**: RBAC (see Section 3.4)

### 7.3 De-Identification Policy

**Implementation**:
- Statistical reports use aggregated data
- No individual identifiers in reports
- Safe harbor method: Remove 18 identifiers

**System Support**:
- Reporting endpoints return aggregated data
- No PHI in analytics exports
- Anonymous usage statistics

### 7.4 Data Retention and Destruction

**Retention Policy**:

| Data Type | Retention Period | Destruction Method |
|-----------|------------------|-------------------|
| Student Records | 7 years post-graduation | Encrypted deletion |
| Audit Logs | Indefinite | N/A (permanent) |
| Financial Records | 7 years | Encrypted deletion |
| Transcripts | Permanent | N/A |
| Temporary Data | 30-90 days | Automatic purge |

**Destruction Procedures**:
- Soft delete with retention period
- Hard delete after retention expires
- Database records securely deleted (VACUUM)
- Backups follow same retention policy

---

## 8. Breach Notification

### 8.1 Breach Notification Rule (§164.400-414)

**Definition of Breach**: Unauthorized acquisition, access, use, or disclosure of PHI that compromises the security or privacy of the PHI.

**Breach Risk Assessment**:
1. Nature and extent of PHI involved
2. Unauthorized person who accessed PHI
3. Whether PHI was actually acquired or viewed
4. Extent to which risk has been mitigated

### 8.2 Breach Response Procedures

**Process**:

1. **Discovery** (Day 0)
   - Breach identified via:
     - Audit log review
     - Automated alerts
     - User report
     - External notification

2. **Assessment** (Days 0-2)
   - Incident response team activated
   - Breach severity assessed
   - PHI impact determined
   - Affected individuals identified

3. **Containment** (Days 0-3)
   - Isolate affected systems
   - Revoke compromised credentials
   - Patch vulnerabilities
   - Prevent further unauthorized access

4. **Notification** (within 60 days)
   - **Individuals**: Written notice within 60 days
   - **HHS**: Notice within 60 days (if >500 individuals affected)
   - **Media**: Notification if >500 individuals in same state/jurisdiction
   - **Business Associates**: Notification within 60 days (if BA breach)

5. **Documentation** (Ongoing)
   - Breach details documented
   - Assessment and mitigation steps recorded
   - Notification dates logged
   - Lessons learned report

**System Support**:
- Audit logs for forensic analysis
- User notification system (email)
- Incident tracking in ticketing system
- Compliance team alerted automatically

### 8.3 Breach Notification Content

**Individual Notification Includes**:
1. Brief description of breach
2. Types of PHI involved
3. Steps individuals should take
4. What organization is doing to investigate and mitigate
5. Contact information for questions

**Template**: Breach notification template prepared and reviewed by legal counsel

---

## 9. Compliance Verification

### 9.1 Annual Security Evaluation

**Process**:
- Annual security risk assessment
- Evaluation of administrative, physical, and technical safeguards
- Identification of gaps and remediation plans
- Documentation of evaluation and findings

**Last Evaluation**: November 2025
**Next Scheduled**: November 2026

### 9.2 Audit Findings and Remediation

**Recent Audits**:
- Internal audit: Q4 2024 - No major findings
- External audit: Pending (scheduled Q1 2025)

**Remediation Tracking**:
- Findings logged in compliance management system
- Remediation owners assigned
- Target dates established
- Verification of remediation

### 9.3 Compliance Testing

**Testing Activities**:
- Quarterly penetration testing (external)
- Monthly vulnerability scans (automated)
- Annual disaster recovery drill
- Quarterly backup restoration test
- Biannual access review
- Monthly audit log review

### 9.4 Compliance Metrics

**Key Performance Indicators (KPIs)**:

| Metric | Target | Current |
|--------|--------|---------|
| Encryption coverage (PHI fields) | 100% | 100% |
| Audit log completeness | 100% | 100% |
| Failed login lockouts | <1% of users/month | 0.3% |
| Unauthorized access attempts | 0 successful | 0 |
| Incident response time | <4 hours | Avg 2 hours |
| Backup success rate | 100% | 100% |
| Security training completion | 100% workforce | 98% |
| BAA coverage | 100% of BAs | 100% |

### 9.5 Continuous Compliance Monitoring

**Automated Monitoring**:
- Security alerts (failed logins, unauthorized access attempts)
- Audit log anomaly detection
- Encryption verification (automated tests)
- Backup success monitoring
- Certificate expiration monitoring

**Manual Review**:
- Monthly audit log review
- Quarterly access review
- Annual policy review
- Annual risk assessment

---

## 10. Appendices

### 10.1 PHI Inventory

| PHI Category | Data Elements | Table/Location | Encrypted | Audit Logged |
|--------------|---------------|----------------|-----------|--------------|
| Demographics | Name, email, phone | `users` | ✓ | ✓ |
| Medical Credentials | Licenses, certifications | `compliance.credentials` | ✓ | ✓ |
| Health Records | Immunizations, clearances | `compliance.credentials` | Partial | ✓ |
| Clinical Training | Skills checkoffs | `compliance.skill_checkoffs` | Partial | ✓ |
| Externships | Clinical placements | `compliance.externships` | Partial | ✓ |
| Notes/Comments | Medical-related notes | `*.notes` fields | ✓ | ✓ |
| Signatures | E-signatures on health docs | `document_signatures` | ✓ | ✓ |

### 10.2 Compliance Checklist

**HIPAA Security Rule Compliance Checklist**:

#### Administrative Safeguards
- [x] Security Management Process
- [x] Assigned Security Responsibility
- [x] Workforce Security
- [x] Information Access Management
- [x] Security Awareness and Training
- [x] Security Incident Procedures
- [x] Contingency Plan
- [x] Evaluation
- [x] Business Associate Contracts

#### Physical Safeguards
- [x] Facility Access Controls
- [x] Workstation Use
- [x] Workstation Security
- [x] Device and Media Controls

#### Technical Safeguards
- [x] Access Control
- [x] Audit Controls
- [x] Integrity
- [x] Person or Entity Authentication
- [x] Transmission Security

#### Organizational Requirements
- [x] Business Associate Contracts
- [N/A] Requirements for Group Health Plans

#### Policies & Procedures
- [x] Privacy Policy
- [x] Minimum Necessary Standard
- [x] De-Identification
- [x] Data Retention and Destruction

#### Breach Notification
- [x] Breach Response Procedures
- [x] Notification Procedures

### 10.3 Encryption Implementation Details

**pgcrypto Configuration**:
```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Set encryption key (session variable)
SET app.encryption_key = '<32-byte-key>';

-- Encryption function
CREATE OR REPLACE FUNCTION encrypt_field(plaintext TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(plaintext, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;

-- Decryption function
CREATE OR REPLACE FUNCTION decrypt_field(ciphertext BYTEA)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(ciphertext, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;
```

**Application-Level Encryption**:
```python
# /backend/app/utils/encryption.py
import os
from cryptography.fernet import Fernet

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(ENCRYPTION_KEY)

def encrypt(plaintext: str) -> bytes:
    return cipher.encrypt(plaintext.encode())

def decrypt(ciphertext: bytes) -> str:
    return cipher.decrypt(ciphertext).decode()
```

### 10.4 Audit Log Sample Queries

**PHI Access Review**:
```sql
-- All PHI access in last 30 days
SELECT
    al.created_at,
    u.email,
    al.endpoint,
    al.method,
    al.ip_address
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.phi_access = true
  AND al.created_at >= NOW() - INTERVAL '30 days'
ORDER BY al.created_at DESC;
```

**Failed Login Attempts**:
```sql
-- Failed login attempts by user
SELECT
    user_email,
    COUNT(*) AS failed_attempts,
    MAX(created_at) AS last_attempt
FROM audit_logs
WHERE endpoint = '/auth/login'
  AND status_code = 401
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY user_email
HAVING COUNT(*) >= 3
ORDER BY failed_attempts DESC;
```

**Unusual Access Patterns**:
```sql
-- Access outside normal business hours
SELECT
    u.email,
    al.endpoint,
    al.created_at,
    al.ip_address
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.phi_access = true
  AND (EXTRACT(HOUR FROM al.created_at) < 6 OR EXTRACT(HOUR FROM al.created_at) > 20)
  AND al.created_at >= NOW() - INTERVAL '7 days'
ORDER BY al.created_at DESC;
```

### 10.5 Glossary

| Term | Definition |
|------|------------|
| **ePHI** | Electronic Protected Health Information |
| **PHI** | Protected Health Information - health information that identifies an individual |
| **BAA** | Business Associate Agreement |
| **HITECH** | Health Information Technology for Economic and Clinical Health Act |
| **Covered Entity** | Health plans, healthcare clearinghouses, healthcare providers |
| **Business Associate** | Person/entity that performs functions involving use or disclosure of PHI |
| **Breach** | Unauthorized acquisition, access, use, or disclosure of PHI |
| **Minimum Necessary** | Use, disclose, or request only minimum PHI needed |
| **De-Identification** | Removal of identifiers to prevent identification of individuals |

### 10.6 References

- HIPAA Security Rule: 45 CFR Part 164, Subpart C
- HIPAA Privacy Rule: 45 CFR Part 164, Subpart E
- HIPAA Breach Notification Rule: 45 CFR Part 164, Subpart D
- HHS HIPAA Guidance: https://www.hhs.gov/hipaa/
- NIST SP 800-66: Implementing the HIPAA Security Rule
- Azure HIPAA Compliance: https://docs.microsoft.com/en-us/azure/compliance/offerings/offering-hipaa-us

### 10.7 Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | Compliance Team | Initial document |
| 2.0 | 2024-11-14 | Claude Code | Comprehensive update post-system review |

### 10.8 Contact Information

**Security Officer**: CTO - security@aada.edu
**Privacy Officer**: CCO - privacy@aada.edu
**Compliance Team**: compliance@aada.edu
**Breach Reporting**: security@aada.edu (24/7 monitored)

---

**END OF DOCUMENT**

**Classification**: Confidential
**Distribution**: Compliance team, executive leadership, auditors (upon request)
