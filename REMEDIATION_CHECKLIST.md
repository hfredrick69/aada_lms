# HIPAA/NIST Remediation Checklist

## Phase 1: IMMEDIATE (Week 1-2) - CRITICAL
Complete these items before any production deployment.

### 1. Enable HTTPS/TLS
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure reverse proxy (Nginx/Caddy) with SSL
- [ ] Update CORS to use `https://` instead of `http://`
- [ ] Add HSTS header: `Strict-Transport-Security: max-age=31536000`
- [ ] Add Secure flag to cookies
- [ ] Redirect all HTTP traffic to HTTPS
- [ ] Test with SSL Labs (https://www.ssllabs.com/ssltest/)
- **Files to update:** `docker-compose.yml`, `backend/app/main.py`
- **Time estimate:** 2-3 hours

### 2. Remove Default Credentials
- [ ] Delete default passwords from `.env.example`
- [ ] Update `docker-compose.yml` to use `${DB_PASSWORD}` from environment
- [ ] Implement `.env` file in `.gitignore` (already done?)
- [ ] Add `.env.local` with production values (not in repo)
- [ ] Change database password from "changeme"
- [ ] Change JWT secret from "change_me"
- [ ] Implement environment variable validation
- [ ] Add pre-commit hook to prevent credential commits
- **Files to update:** `.env.example`, `docker-compose.yml`, `app/core/config.py`
- **Time estimate:** 1-2 hours

### 3. Implement Basic RBAC
- [ ] Create `@require_admin` decorator
- [ ] Create `@require_student` decorator
- [ ] Create `@require_role(role_name)` generic decorator
- [ ] Define role matrix for each endpoint
- [ ] Update all admin endpoints to check roles
- [ ] Update user/roles endpoints with role checks
- [ ] Add role checks to sensitive data endpoints (transcripts, finance, credentials)
- [ ] Create tests for unauthorized access (should return 403)
- **Files to update:** `backend/app/core/security.py`, all routers
- **Time estimate:** 8-16 hours

Admin endpoints requiring role check:
```
POST   /api/users/              - admin only
GET    /api/users/              - admin only
PUT    /api/users/{user_id}     - admin only
DELETE /api/users/{user_id}     - admin only
POST   /api/roles/              - admin only
DELETE /api/roles/{role_id}     - admin only
```

### 4. Add Authentication Logging
- [ ] Log all login attempts (success/failure)
- [ ] Log logout events
- [ ] Log failed login attempts with username
- [ ] Implement account lockout after 5 failed attempts
- [ ] Add timestamp to each log entry
- [ ] Store logs in database (AuditLog table)
- [ ] Create database indexes on user_id and timestamp
- [ ] Test logging functionality
- **Files to create:** `backend/app/utils/audit_logger.py`
- **Files to update:** `backend/app/routers/auth.py`
- **Time estimate:** 4-6 hours

---

## Phase 2: URGENT (Week 3-4) - HIGH RISK
Complete these items before processing real student data.

### 1. Implement Audit Logging Middleware
- [ ] Create audit middleware that logs all requests
- [ ] Log: user_id, endpoint, method, IP address, timestamp, status code
- [ ] Implement PHI access tracking (mark sensitive endpoints)
- [ ] Log all CRUD operations on compliance models
- [ ] Log all access to: credentials, transcripts, finance, complaints
- [ ] Add request/response size to logs
- [ ] Implement log rotation (daily files)
- [ ] Store logs in database for searching
- [ ] Create compliance report generator
- [ ] Test audit trail completeness
- **Files to create:** `backend/app/middleware/audit_middleware.py`
- **Files to update:** `backend/app/main.py`
- **Time estimate:** 16-20 hours

Endpoints to mark as PHI-accessing:
```
GET    /api/transcripts/
POST   /api/transcripts/
GET    /api/credentials/
POST   /api/credentials/
GET    /api/finance/withdrawals
GET    /api/finance/refunds
POST   /api/finance/withdrawals
GET    /api/complaints/
POST   /api/complaints/
PUT    /api/complaints/{complaint_id}
GET    /api/attendance/
POST   /api/attendance/
```

### 2. Add Password Policy Enforcement
- [ ] Minimum 12 characters (NIST 800-63B)
- [ ] Require: uppercase + lowercase + number + symbol
- [ ] Prevent password reuse (last 12 passwords)
- [ ] Password expiration: 90 days
- [ ] Password history table in database
- [ ] Add password strength meter on frontend
- [ ] Notify users of expiration 7 days before
- [ ] Force change on next login after expiration
- **Libraries:** `validators`, `passlib`, `pydantic`
- **Files to create:** `backend/app/utils/password_policy.py`
- **Files to update:** `backend/app/routers/users.py`, `backend/app/schemas/auth.py`
- **Time estimate:** 6-8 hours

### 3. Enable Database Encryption
- [ ] Enable PostgreSQL `pgcrypto` extension
- [ ] Identify PHI fields (email, names, phone, SSN if stored)
- [ ] Create encryption/decryption functions
- [ ] Encrypt sensitive columns: email, first_name, last_name
- [ ] Implement field-level encryption in ORM
- [ ] Create migration to encrypt existing data
- [ ] Test encrypted data is unreadable in database
- [ ] Document encryption scheme
- [ ] Implement encrypted backups
- **Files to update:** Database models, migration scripts
- **Time estimate:** 4-6 hours

### 4. Create Security Documentation
- [ ] Write Access Control Policy (who can access what)
- [ ] Write Password Policy document
- [ ] Write Encryption Policy
- [ ] Write Incident Response Plan
- [ ] Write Breach Notification Plan (60-day timeline)
- [ ] Write Data Retention Policy
- [ ] Write User Account Lifecycle Policy
- [ ] Write Backup & Recovery Policy
- [ ] Create Security Checklist for deployments
- **Files to create:** `docs/security/` folder
- **Time estimate:** 8-12 hours

---

## Phase 3: IMPORTANT (Week 5-8) - MEDIUM RISK
Complete these for full compliance.

### 1. Implement Multi-Factor Authentication (MFA)
- [ ] Choose MFA method (TOTP - Google Authenticator, or SMS)
- [ ] Create MFA table in database
- [ ] Implement TOTP generation/validation
- [ ] Add MFA setup on user account creation
- [ ] Require MFA for admin accounts (mandatory)
- [ ] Make MFA optional for students (recommended)
- [ ] Add backup codes for account recovery
- [ ] Test MFA flow end-to-end
- [ ] Create frontend UI for MFA setup
- **Libraries:** `pyotp`, `qrcode`
- **Files to create:** `backend/app/routers/mfa.py`
- **Time estimate:** 20-30 hours

### 2. Add Session Management
- [ ] Create sessions table in database
- [ ] Track session creation time and last activity
- [ ] Implement automatic logout on 15-minute inactivity
- [ ] Limit to 2-3 concurrent sessions per user
- [ ] Invalidate sessions on password change
- [ ] Invalidate sessions on role change
- [ ] Add session management endpoint for users
- [ ] Log session creation/termination in audit
- [ ] Test session timeout functionality
- **Files to create:** `backend/app/routers/sessions.py`
- **Time estimate:** 12-16 hours

### 3. Implement Token Refresh
- [ ] Separate access tokens (15-minute TTL) from refresh tokens (7-day TTL)
- [ ] Create refresh token table
- [ ] Implement token refresh endpoint
- [ ] Store refresh tokens in database (not JWT)
- [ ] Validate refresh tokens on use
- [ ] Revoke refresh tokens on logout
- [ ] Track refresh token usage (detect token reuse attacks)
- [ ] Add token blacklist for revoked tokens
- **Files to update:** `backend/app/core/security.py`, `backend/app/routers/auth.py`
- **Time estimate:** 8-12 hours

### 4. Add Monitoring & Alerting
- [ ] Set up ELK Stack (Elasticsearch/Logstash/Kibana) or CloudWatch
- [ ] Create dashboards for security events
- [ ] Set up alerts for:
  - Multiple failed login attempts (>5 in 15 min)
  - Unusual access patterns
  - Bulk data exports
  - Failed API calls returning 403
  - After-hours access
- [ ] Configure email/Slack notifications
- [ ] Create runbook for responding to alerts
- [ ] Test alerting system
- **Tools:** Elasticsearch, Splunk, AWS CloudWatch, Datadog
- **Time estimate:** 24-32 hours

### 5. Conduct Security Testing
- [ ] Perform manual penetration testing
- [ ] Test IDOR vulnerabilities
- [ ] Test RBAC enforcement
- [ ] Test authentication bypass
- [ ] Test SQL injection
- [ ] Test XSS vulnerabilities
- [ ] Test CSRF protection
- [ ] Create security test suite
- [ ] Document findings and remediation
- **Tools:** Burp Suite, OWASP ZAP, manual testing
- **Time estimate:** 16-20 hours

---

## Security Testing Checklist

### Authentication Tests
- [ ] Test login with correct credentials (should succeed)
- [ ] Test login with incorrect password (should fail)
- [ ] Test login with non-existent user (should fail)
- [ ] Test expired token (should return 401)
- [ ] Test invalid token format (should return 401)
- [ ] Test missing authentication header (should return 401)
- [ ] Test bearer token removed (should return 401)
- [ ] Test token from different environment (should fail)

### Authorization Tests
- [ ] Test student cannot access other student's data
- [ ] Test student cannot access admin endpoints
- [ ] Test admin can access all data
- [ ] Test user cannot elevate their own role
- [ ] Test 403 returned for unauthorized access
- [ ] Test role-based filtering works correctly
- [ ] Test program-based filtering works correctly

### Encryption Tests
- [ ] Test passwords are hashed (not plaintext)
- [ ] Test database passwords use PBKDF2-SHA256
- [ ] Test HTTPS enforced (HTTP redirects)
- [ ] Test HSTS header present
- [ ] Test database encryption enabled
- [ ] Test backups are encrypted

### Input Validation Tests
- [ ] Test invalid UUID format rejected
- [ ] Test oversized strings rejected
- [ ] Test negative numbers rejected
- [ ] Test SQL injection prevented
- [ ] Test XSS prevented in responses
- [ ] Test parameter tampering detected

### Rate Limiting Tests
- [ ] Test repeated login attempts blocked after 5 failures
- [ ] Test account locked for 15 minutes after lockout
- [ ] Test rate limiting on API endpoints
- [ ] Test rate limiting per IP address

---

## HIPAA Compliance Checklist

- [ ] Business Associate Agreements documented for all vendors
- [ ] Encryption at rest verified
- [ ] Encryption in transit verified (TLS 1.2+)
- [ ] Access controls enforced (RBAC)
- [ ] Audit trails comprehensive
- [ ] Incident response plan documented
- [ ] Breach notification procedures documented
- [ ] Data retention policies documented
- [ ] Password policies compliant
- [ ] Workforce security training completed
- [ ] Security risk analysis completed
- [ ] Annual compliance certification conducted

---

## NIST Compliance Checklist

### IDENTIFY Function
- [ ] Asset inventory created
- [ ] Asset criticality assessed
- [ ] Business environment documented
- [ ] Risk assessment completed
- [ ] Risk management strategy defined
- [ ] Supply chain risks assessed

### PROTECT Function
- [ ] Access control policy implemented
- [ ] Data security controls enforced
- [ ] Information protection controls in place
- [ ] Protective technology deployed
- [ ] Encryption enabled
- [ ] Password policies enforced

### DETECT Function
- [ ] Monitoring systems deployed
- [ ] Anomaly detection configured
- [ ] Logging comprehensive
- [ ] Detection processes documented
- [ ] SIEM configured

### RESPOND Function
- [ ] Incident response plan written
- [ ] Communication procedures documented
- [ ] Mitigation procedures defined
- [ ] Response team identified
- [ ] Testing schedule established

### RECOVER Function
- [ ] Recovery plan written
- [ ] RTO/RPO defined
- [ ] Backup testing scheduled
- [ ] Disaster recovery procedures documented
- [ ] Improvement process established

---

## Sign-Off

- [ ] Phase 1 completed by: _____________ Date: _______
- [ ] Phase 2 completed by: _____________ Date: _______
- [ ] Phase 3 completed by: _____________ Date: _______
- [ ] Security audit passed: _____________ Date: _______
- [ ] HIPAA compliance certified: _____________ Date: _______
- [ ] Ready for production deployment: _____________ Date: _______

