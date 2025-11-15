# AADA LMS - Security Architecture Document

**Document Version:** 2.0
**Last Updated:** November 14, 2025
**Classification:** Confidential
**Owner:** AADA Security Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Security Architecture Overview](#2-security-architecture-overview)
3. [Defense in Depth Strategy](#3-defense-in-depth-strategy)
4. [Authentication Architecture](#4-authentication-architecture)
5. [Authorization Architecture](#5-authorization-architecture)
6. [Data Protection Architecture](#6-data-protection-architecture)
7. [Network Security](#7-network-security)
8. [Application Security](#8-application-security)
9. [Infrastructure Security](#9-infrastructure-security)
10. [Monitoring and Detection](#10-monitoring-and-detection)
11. [Incident Response](#11-incident-response)
12. [Security Operations](#12-security-operations)

---

## 1. Executive Summary

### 1.1 Purpose
This document describes the comprehensive security architecture of the AADA Learning Management System, detailing the technical controls, processes, and procedures that protect Protected Health Information (PHI) and ensure compliance with HIPAA, NIST, and other regulatory requirements.

### 1.2 Security Posture

**Security Level**: High (Healthcare Education Platform)

**Key Security Achievements**:
- ✓ Zero-trust architecture with explicit verification at every layer
- ✓ Encryption at rest and in transit for all PHI
- ✓ Comprehensive audit logging of all system activity
- ✓ Role-based access control with least privilege principle
- ✓ Multi-layered defense with 7 security layers
- ✓ Continuous monitoring and threat detection
- ✓ Incident response capability with documented procedures

### 1.3 Threat Model

**Primary Threats**:
1. **Data Breach**: Unauthorized access to PHI
2. **Account Compromise**: Stolen credentials, session hijacking
3. **Malicious Code**: File uploads containing malware
4. **Denial of Service**: Service disruption via rate limiting abuse
5. **Insider Threats**: Unauthorized access by authorized users
6. **Man-in-the-Middle**: Interception of data in transit
7. **SQL Injection**: Database manipulation via input attacks
8. **Cross-Site Scripting (XSS)**: Client-side code injection

**Mitigation**: Each threat mitigated through multiple overlapping controls

---

## 2. Security Architecture Overview

### 2.1 Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────────┘

Layer 7: Audit & Monitoring
├─ Comprehensive audit logging (all API requests)
├─ PHI access tracking
├─ Anomaly detection
└─ Security alerts

Layer 6: Data Protection
├─ AES-256 encryption at rest (pgcrypto)
├─ TLS 1.2+ encryption in transit
├─ Bcrypt password hashing
└─ Secure key management (Azure Key Vault)

Layer 5: Input Validation
├─ Pydantic schema validation
├─ File upload security (7-layer validation)
├─ SQL injection prevention (ORM)
└─ XSS prevention (output encoding)

Layer 4: Authorization
├─ Role-Based Access Control (RBAC)
├─ Per-endpoint permission checks
├─ Data isolation (students see own data)
└─ Minimum necessary access principle

Layer 3: Authentication
├─ JWT token-based authentication
├─ Bcrypt password hashing
├─ Session management (timeout, revocation)
└─ Account lockout (5 failed attempts)

Layer 2: Application Security
├─ Security headers (HSTS, CSP, X-Frame-Options)
├─ CORS policy enforcement
├─ Rate limiting (IP-based)
└─ Error handling (no info leakage)

Layer 1: Network Security
├─ HTTPS/TLS only (no HTTP)
├─ Azure network security groups
├─ DDoS protection (Azure)
└─ API gateway (future enhancement)

┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│  Azure Cloud Security (SOC 2, HIPAA, ISO 27001 certified)      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Security Principles

1. **Zero Trust**: Never trust, always verify
2. **Defense in Depth**: Multiple overlapping security controls
3. **Least Privilege**: Minimum access necessary to perform job function
4. **Separation of Duties**: No single user has complete control
5. **Fail Secure**: System defaults to secure state on failure
6. **Complete Mediation**: Every access request checked
7. **Open Design**: Security through implementation, not obscurity
8. **Economy of Mechanism**: Simple, verifiable security controls
9. **Psychological Acceptability**: Usable security controls
10. **Audit Trail**: Complete logging for accountability

### 2.3 Security Boundaries

**Trust Boundaries**:
1. **External → Application**: HTTPS/TLS, authentication required
2. **Application → Database**: PostgreSQL SSL/TLS, credentials required
3. **Application → Azure Services**: Managed identities, secure connections
4. **User → System**: Authentication, authorization, session management

**Data Zones**:
- **Public Zone**: Anonymous access (health check, public signing)
- **Authenticated Zone**: Requires valid JWT token
- **PHI Zone**: Additional access controls, comprehensive logging
- **Administrative Zone**: Elevated privileges, enhanced monitoring

---

## 3. Defense in Depth Strategy

### 3.1 Seven-Layer Security Model

#### Layer 1: Network Security
**Purpose**: Protect network perimeter and traffic

**Controls**:
- HTTPS/TLS 1.2+ enforced (no HTTP)
- Azure network security groups
- Azure DDoS protection
- No direct database access (API-only)
- CORS policy enforcement

**Code**: `/backend/app/main.py` (CORS middleware)

#### Layer 2: Application Security
**Purpose**: Protect application layer

**Controls**:
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Rate limiting (5-100 requests per timeframe)
- Error handling (sanitized error messages)
- Session management (timeout, revocation)

**Code**: `/backend/app/middleware/security.py`

#### Layer 3: Authentication
**Purpose**: Verify user identity

**Controls**:
- JWT tokens (HS256, 15-minute expiry)
- Bcrypt password hashing (cost factor 12)
- Refresh tokens (SHA-256 hashed storage)
- Account lockout (5 failed attempts, 30-min lockout)
- Email verification (registration)

**Code**: `/backend/app/core/security.py`, `/backend/app/routers/auth.py`

#### Layer 4: Authorization
**Purpose**: Control access to resources

**Controls**:
- Role-Based Access Control (6 roles)
- Per-endpoint permission checks
- Data isolation (user can only access own data)
- Minimum necessary access principle

**Code**: `/backend/app/core/rbac.py`

#### Layer 5: Input Validation
**Purpose**: Prevent malicious input

**Controls**:
- Pydantic schema validation
- File upload validation (7 layers)
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (output encoding, CSP)
- CSRF protection (SameSite cookies)

**Code**: `/backend/app/schemas/`, `/backend/app/core/file_validation.py`

#### Layer 6: Data Protection
**Purpose**: Protect data confidentiality and integrity

**Controls**:
- Encryption at rest (AES-256 via pgcrypto)
- Encryption in transit (TLS 1.2+)
- Password hashing (bcrypt)
- Secure key management (Azure Key Vault)
- Database transactions (ACID compliance)

**Code**: `/backend/app/utils/encryption.py`

#### Layer 7: Audit & Monitoring
**Purpose**: Detect and respond to security events

**Controls**:
- Comprehensive audit logging
- PHI access tracking
- Failed login monitoring
- Security alerts
- Forensic analysis capability

**Code**: `/backend/app/middleware/security.py`, `/backend/app/db/models/audit_log.py`

### 3.2 Attack Surface Analysis

| Attack Vector | Exposure Level | Mitigation | Residual Risk |
|---------------|----------------|------------|---------------|
| **Credential Theft** | Medium | Bcrypt hashing, account lockout, MFA (planned) | Low |
| **Session Hijacking** | Low | Short token lifetime, HTTPS-only, token binding | Very Low |
| **SQL Injection** | Very Low | ORM, parameterized queries | Negligible |
| **XSS** | Low | CSP, output encoding, sanitization | Very Low |
| **CSRF** | Low | SameSite cookies, CORS | Very Low |
| **File Upload Attack** | Low | 7-layer validation, sanitization, scanning | Very Low |
| **DDoS** | Medium | Azure DDoS protection, rate limiting | Low |
| **PHI Exposure** | Low | Encryption, access controls, audit logging | Very Low |
| **Insider Threat** | Medium | RBAC, audit logs, data isolation | Low |

---

## 4. Authentication Architecture

### 4.1 Authentication Flow

```
Registration:
1. User submits email + password
   ↓
2. Validate email format (Pydantic)
   ↓
3. Validate password policy (NIST SP 800-63B)
   - Min 12 characters
   - Uppercase, lowercase, digit, special character
   ↓
4. Hash password (bcrypt, cost 12)
   ↓
5. Generate verification token (32 bytes random)
   ↓
6. Send verification email (30-min expiry)
   ↓
7. User clicks verification link
   ↓
8. Account activated, JWT issued

Login:
1. User submits email + password
   ↓
2. Retrieve user record (encrypted email lookup)
   ↓
3. Verify bcrypt hash
   ↓
4. Check account status (active, verified, not locked)
   ↓
5. Check failed login attempts (<5)
   ↓
6. Issue JWT access token (15-min expiry)
   ↓
7. Issue refresh token (7-day expiry, hashed storage)
   ↓
8. Log successful login to audit trail
   ↓
9. Return tokens (access in body, refresh in httpOnly cookie)

Token Refresh:
1. Client submits refresh token
   ↓
2. Verify token hash in database
   ↓
3. Check expiration
   ↓
4. Check revocation status
   ↓
5. Issue new access token (15-min expiry)
   ↓
6. Update refresh token use count
   ↓
7. Log token refresh to audit trail

Logout:
1. Client submits logout request
   ↓
2. Revoke refresh token (is_revoked = true)
   ↓
3. Log logout to audit trail
   ↓
4. Client discards access token
```

### 4.2 Password Security

**Storage**:
```python
# Bcrypt with automatic salt generation
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)  # 2^12 = 4096 iterations
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

**Policy** (NIST SP 800-63B Compliant):
- Minimum length: 12 characters
- Complexity: Uppercase + lowercase + digit + special character
- Maximum length: 128 characters
- No password hints
- No security questions
- Unicode support
- No periodic expiration (recommended by NIST)

**Future Enhancements**:
- Compromised password check (Have I Been Pwned API)
- Password strength meter
- Passkey/WebAuthn support

### 4.3 Token Security

**JWT Access Token**:
- Algorithm: HS256 (HMAC-SHA256)
- Lifetime: 15 minutes
- Payload: User ID, email, roles, expiration
- Storage: Client memory (not localStorage for XSS protection)
- Transmission: Authorization header (Bearer scheme)

**Refresh Token**:
- Type: Cryptographically random (32 bytes)
- Lifetime: 7 days
- Storage: SHA-256 hash in database
- Transmission: httpOnly secure cookie (CSRF protection)
- Binding: IP address and user agent tracked

**Token Rotation** (Future Enhancement):
- One-time use refresh tokens
- Automatic token family revocation on suspicious activity

### 4.4 Session Management

**Session Parameters**:
- Idle timeout: 30 minutes
- Absolute timeout: 7 days (refresh token lifetime)
- Concurrent sessions: Allowed (tracked)

**Session Security**:
- No server-side session storage (stateless JWT)
- Client-side timeout enforcement
- Server-side token validation on every request
- Token revocation capability

### 4.5 Account Lockout

**Lockout Policy**:
- Threshold: 5 failed login attempts
- Duration: 30 minutes
- Notification: Email alert (future enhancement)
- Reset: Automatic after duration or admin intervention

**Implementation**:
```python
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Check lockout status
if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(403, "Account locked")

# Increment failed attempts
user.failed_login_attempts += 1
if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
    user.locked_until = datetime.utcnow() + timedelta(minutes=30)

# Reset on successful login
user.failed_login_attempts = 0
user.locked_until = None
```

---

## 5. Authorization Architecture

### 5.1 Role-Based Access Control (RBAC)

**Role Hierarchy**:

```
                    ┌────────┐
                    │ ADMIN  │ (Superuser)
                    └───┬────┘
                        │
                  ┌─────┴─────┐
                  │   STAFF   │ (Administrative)
                  └─────┬─────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────┴────┐   ┌─────┴──────┐  ┌────┴─────┐
   │REGISTRAR│   │ INSTRUCTOR │  │  FINANCE │
   └────┬────┘   └─────┬──────┘  └────┬─────┘
        │              │              │
        └──────────────┴──────────────┘
                       │
                  ┌────┴────┐
                  │ STUDENT │ (End User)
                  └─────────┘
```

**Role Definitions**:

| Role | Scope | Key Permissions |
|------|-------|-----------------|
| **Admin** | System-wide | All operations, user management, system configuration |
| **Staff** | Organization | Student management, enrollment, documents, reporting |
| **Registrar** | Academic | Enrollment, transcripts, credentials, attendance |
| **Instructor** | Course-specific | Course content, student progress, grading |
| **Finance** | Financial | Payments, refunds, financial reporting |
| **Student** | Self-only | Own enrollment, progress, documents, payments |

### 5.2 Permission Matrix

**Endpoint Permissions**:

| Endpoint Pattern | Admin | Staff | Registrar | Instructor | Finance | Student |
|------------------|-------|-------|-----------|------------|---------|---------|
| `POST /users` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `GET /users` | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| `GET /users/{id}` | ✓ | ✓ | ✓ | ✓ | ✓ | Self |
| `PUT /users/{id}` | ✓ | ✓ | ✗ | ✗ | ✗ | Self |
| `DELETE /users/{id}` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `POST /enrollments` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `GET /enrollments` | ✓ | ✓ | ✓ | Assigned | ✓ | Self |
| `POST /payments` | ✓ | ✓ | ✗ | ✗ | ✓ | Self |
| `POST /refunds` | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `GET /transcripts` | ✓ | ✓ | ✓ | ✗ | ✗ | Self |
| `GET /audit-logs` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `POST /documents` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |

### 5.3 Authorization Implementation

**Decorator-Based Authorization**:
```python
# /backend/app/core/rbac.py

from functools import wraps
from fastapi import HTTPException

def require_role(allowed_roles: list[str]):
    """Decorator to enforce role-based access control."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(401, "Authentication required")

            user_roles = [role.name for role in current_user.roles]

            if not any(role in allowed_roles for role in user_roles):
                raise HTTPException(403, "Insufficient permissions")

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.get("/students")
@require_role(["admin", "staff", "registrar"])
async def list_students(current_user: User = Depends(get_current_user)):
    return get_students()
```

**Data Isolation**:
```python
@router.get("/enrollments/{id}")
async def get_enrollment(id: UUID, current_user: User = Depends(get_current_user)):
    enrollment = get_enrollment_by_id(id)

    # Admin/staff can access all enrollments
    if current_user.has_role(["admin", "staff", "registrar"]):
        return enrollment

    # Students can only access their own enrollments
    if current_user.has_role("student") and enrollment.user_id == current_user.id:
        return enrollment

    raise HTTPException(403, "Access denied")
```

### 5.4 Minimum Necessary Access

**Principle**: Users access only the minimum PHI necessary for their job function.

**Implementation**:
- **Students**: Only own records
- **Instructors**: Only students in assigned courses
- **Registrar**: All academic records (job function)
- **Finance**: Financial + enrollment data only
- **Staff**: Limited PHI access
- **Admin**: Full access (logged and monitored)

**Enforcement**: Programmatic data filtering based on role

---

## 6. Data Protection Architecture

### 6.1 Encryption Strategy

**Data Classification**:

| Classification | Examples | Encryption Required | Access Control |
|----------------|----------|---------------------|----------------|
| **PHI** | Name, email, health records | ✓ At rest + in transit | Role-based, logged |
| **PII** | Address, phone, SSN | ✓ At rest + in transit | Role-based, logged |
| **Financial** | Payment info, account numbers | ✓ At rest + in transit | Role-based, logged |
| **Educational** | Grades, transcripts | ✓ In transit | Role-based |
| **System** | Logs, metadata | ✓ In transit | Admin-only |

### 6.2 Encryption at Rest

**Database Encryption (PostgreSQL pgcrypto)**:

**Encrypted Fields**:
- `users.email`
- `users.first_name`
- `users.last_name`
- `document_signatures.signer_name`
- `document_signatures.signer_email`
- `crm.leads.*` (all PII fields)
- `compliance.credentials.credential_number`
- `compliance.*.notes` (all notes fields)

**Encryption Method**: AES-256 symmetric encryption

**Implementation**:
```sql
-- Encryption (write)
INSERT INTO users (email, first_name, last_name)
VALUES (
    pgp_sym_encrypt('user@example.com', current_setting('app.encryption_key')),
    pgp_sym_encrypt('John', current_setting('app.encryption_key')),
    pgp_sym_encrypt('Doe', current_setting('app.encryption_key'))
);

-- Decryption (read)
SELECT
    id,
    pgp_sym_decrypt(email::bytea, current_setting('app.encryption_key')) AS email,
    pgp_sym_decrypt(first_name::bytea, current_setting('app.encryption_key')) AS first_name,
    pgp_sym_decrypt(last_name::bytea, current_setting('app.encryption_key')) AS last_name
FROM users;
```

**Key Management**:
- **Development**: Environment variable
- **Production**: Azure Key Vault
- **Rotation**: Every 90 days
- **Algorithm**: AES-256-CBC

### 6.3 Encryption in Transit

**TLS/HTTPS Configuration**:
- **Protocol**: TLS 1.2+ (TLS 1.0/1.1 disabled)
- **Cipher Suites**: Strong ciphers only (AES-GCM preferred)
- **Certificate**: Azure-managed SSL certificate
- **HSTS**: Enforced (max-age=31536000)

**Database Connections**:
- **Protocol**: PostgreSQL SSL/TLS
- **Configuration**: `sslmode=require` in connection string
- **Verification**: Server certificate validated

**Email Transmission**:
- **SendGrid**: TLS for SMTP
- **Azure Communication Services**: HTTPS for API, TLS for SMTP

### 6.4 Key Management

**Key Types**:

| Key Type | Purpose | Length | Storage | Rotation |
|----------|---------|--------|---------|----------|
| **JWT Secret** | Token signing | 64 bytes | Azure Key Vault | 90 days |
| **Encryption Key** | Database encryption | 32 bytes (256-bit) | Azure Key Vault | 90 days |
| **TLS Certificate** | HTTPS | 2048-bit RSA | Azure App Service | Annual |
| **Refresh Token Salt** | Token hashing | N/A (SHA-256) | N/A | N/A |

**Key Generation**:
```python
import secrets

# JWT secret key (64 bytes = 512 bits)
jwt_secret = secrets.token_urlsafe(64)

# Database encryption key (32 bytes = 256 bits)
encryption_key = secrets.token_bytes(32)

# Refresh token (32 bytes = 256 bits)
refresh_token = secrets.token_urlsafe(32)
```

**Key Rotation Process**:
1. Generate new key
2. Store in Azure Key Vault with version tag
3. Update application configuration
4. Re-encrypt data with new key (for data-encrypting keys)
5. Retain old key for decryption (key versioning)
6. Deactivate old key after re-encryption complete

### 6.5 Password Hashing

**Algorithm**: Bcrypt (adaptive hashing)

**Configuration**:
- Cost factor: 12 (2^12 = 4096 rounds)
- Automatic salt generation
- Future-proof (cost factor increases over time)

**Properties**:
- Resistant to rainbow table attacks (salted)
- Resistant to brute force (computationally expensive)
- Resistant to GPU attacks (memory-hard)

---

## 7. Network Security

### 7.1 Network Architecture

```
                   ┌──────────────┐
                   │   Internet   │
                   └──────┬───────┘
                          │
                     HTTPS/TLS
                          │
                   ┌──────▼───────┐
                   │ Azure Front  │ (Optional CDN)
                   │     Door     │
                   └──────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                                   │
  ┌─────▼──────┐                  ┌────────▼────────┐
  │   Azure    │                  │  Azure App      │
  │   Static   │                  │  Service        │
  │  Web Apps  │                  │  (Backend API)  │
  │ (Frontends)│                  └────────┬────────┘
  └────────────┘                           │
                              ┌────────────┼────────────┐
                              │                         │
                     ┌────────▼────────┐    ┌──────────▼────────┐
                     │ Azure PostgreSQL│    │  Azure Blob       │
                     │  (Database)     │    │  Storage (Docs)   │
                     └─────────────────┘    └───────────────────┘
                              │
                     ┌────────▼────────┐
                     │  Azure Key      │
                     │  Vault (Secrets)│
                     └─────────────────┘
```

### 7.2 Firewall Rules

**Azure Network Security Groups**:
- Allow HTTPS (443) from internet → App Service
- Allow PostgreSQL (5432) from App Service → PostgreSQL
- Allow HTTPS (443) from App Service → Blob Storage
- Deny all other inbound traffic
- Deny all other outbound traffic (except listed)

**Application-Level Firewall**:
- CORS: Whitelist specific origins only
- Rate limiting: IP-based throttling
- No direct database access (API-only)

### 7.3 CORS Policy

**Configuration**:
```python
# /backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://student.aada.edu",
    "https://admin.aada.edu",
    "http://localhost:5173",  # Development only
    "http://localhost:5174"   # Development only
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Purpose**:
- Prevent cross-origin attacks
- Allow only trusted frontends
- Enforce same-origin policy

### 7.4 DDoS Protection

**Azure DDoS Protection**:
- Always-on traffic monitoring
- Automatic attack mitigation
- Real-time attack metrics

**Application-Level Rate Limiting**:
```python
# Rate limits per endpoint
RATE_LIMITS = {
    "/api/auth/login": (5, 300),        # 5 attempts per 5 minutes
    "/api/auth/register": (3, 3600),    # 3 per hour
    "/api/documents/sign": (10, 60),    # 10 per minute
    "DEFAULT": (100, 60)                # 100 per minute
}
```

**Future Enhancement**: Redis-based distributed rate limiting

---

## 8. Application Security

### 8.1 Security Headers

**Headers Enforced on All Responses**:

```python
# /backend/app/middleware/security.py

SECURITY_HEADERS = {
    # Force HTTPS for 1 year
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",

    # Prevent clickjacking
    "X-Frame-Options": "SAMEORIGIN",

    # Prevent MIME sniffing
    "X-Content-Type-Options": "nosniff",

    # Content Security Policy
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' h5p.org *.h5p.org; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'self'"
    ),

    # Referrer policy
    "Referrer-Policy": "strict-origin-when-cross-origin",

    # Permissions policy
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",

    # XSS protection (legacy browsers)
    "X-XSS-Protection": "1; mode=block"
}
```

### 8.2 Input Validation

**Validation Layers**:

1. **Client-Side** (React Hook Form):
   - Format validation
   - Required field checks
   - Real-time feedback

2. **API Layer** (Pydantic):
   - Type validation
   - Range validation
   - Pattern matching
   - Custom validators

3. **Business Layer**:
   - Business rule validation
   - Referential integrity
   - State machine validation

**Example Pydantic Schema**:
```python
from pydantic import BaseModel, EmailStr, constr, validator

class UserCreate(BaseModel):
    email: EmailStr  # Email format validation
    password: constr(min_length=12, max_length=128)
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)

    @validator('password')
    def validate_password_complexity(cls, v):
        # Custom password validation
        if not re.search(r'[A-Z]', v):
            raise ValueError('Must contain uppercase')
        # ... additional checks
        return v
```

### 8.3 File Upload Security

**7-Layer Validation**:

1. **Extension Validation**: Whitelist (.pdf, .png, .jpg, .jpeg)
2. **Magic Bytes Verification**: Verify actual file type
3. **File Size Limits**: 10MB PDFs, 5MB images
4. **PDF Sanitization**: Remove JavaScript, forms, embedded files
5. **Image Sanitization**: Strip EXIF metadata
6. **Virus Scanning**: Optional ClamAV integration
7. **Structure Validation**: Validate PDF/image structure

**Code Reference**: `/backend/app/core/file_validation.py`

### 8.4 Error Handling

**Security Principles**:
- No sensitive information in error messages
- Generic errors to external users
- Detailed errors logged internally
- No stack traces in production

**Implementation**:
```python
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log detailed error internally
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return generic error to user
    return JSONResponse(
        status_code=500,
        content={"detail": "An error occurred. Please try again later."}
    )
```

### 8.5 SQL Injection Prevention

**Mitigation**:
- SQLAlchemy ORM (parameterized queries)
- No raw SQL (except verified queries)
- Input validation (Pydantic)
- Principle of least privilege (database user)

**Safe Query Example**:
```python
# SQLAlchemy automatically parameterizes queries
user = db.query(User).filter(User.email == email).first()

# NOT: f"SELECT * FROM users WHERE email = '{email}'"  # Vulnerable!
```

### 8.6 XSS Prevention

**Mitigation**:
- Content Security Policy (CSP)
- Output encoding (React auto-escapes)
- Input validation
- HttpOnly cookies (no JavaScript access)

**React Auto-Escaping**:
```jsx
// Safe: React automatically escapes
<div>{userInput}</div>

// Dangerous (avoid):
<div dangerouslySetInnerHTML={{__html: userInput}} />
```

---

## 9. Infrastructure Security

### 9.1 Azure Security Features

**Leveraged Azure Security**:
- **Azure App Service**: Managed platform, automatic patching
- **Azure PostgreSQL**: Encryption at rest, TLS in transit, firewall
- **Azure Blob Storage**: Encryption at rest, HTTPS-only, access controls
- **Azure Key Vault**: Hardware security modules (HSM), audit logging
- **Azure DDoS Protection**: Always-on protection
- **Azure Security Center**: Threat detection, recommendations

### 9.2 Container Security

**Docker Image Security**:
- Minimal base image (python:3.11-slim)
- No root user (dedicated app user)
- Vulnerability scanning (GitHub Dependabot)
- Image signing (future enhancement)

**Dockerfile Security**:
```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER app

# Copy application code
COPY --chown=app:app . /app
WORKDIR /app

# Run as non-root
CMD ["gunicorn", "app.main:app"]
```

### 9.3 Secrets Management

**Azure Key Vault**:
- Centralized secret storage
- Access control (managed identities)
- Audit logging
- Secret versioning
- Automatic rotation support

**Secret Types**:
- Database credentials
- JWT secret key
- Encryption keys
- Email API keys
- Third-party API keys

**Access Pattern**:
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Use managed identity (no credentials in code)
credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://aada-vault.vault.azure.net/", credential=credential)

# Retrieve secret
jwt_secret = client.get_secret("jwt-secret-key").value
```

### 9.4 Backup Security

**Backup Encryption**:
- Database backups encrypted at rest
- Geo-redundant storage
- Access controls (RBAC)

**Backup Testing**:
- Quarterly restoration tests
- Documented restore procedures
- Recovery time objectives (RTO: 4 hours)

---

## 10. Monitoring and Detection

### 10.1 Audit Logging

**Comprehensive Logging**:
- All API requests (endpoint, method, user, timestamp, status)
- Authentication events (login, logout, failed attempts)
- Authorization failures (403 responses)
- PHI access (flagged for HIPAA compliance)
- Administrative actions
- Data modifications
- System errors

**Log Structure**:
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    request_body = Column(JSONB)  # Sanitized
    phi_access = Column(Boolean, default=False)  # HIPAA flag
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
```

**Log Retention**: Indefinite (HIPAA requirement)

### 10.2 Security Monitoring

**Monitored Events**:
- Failed login attempts (threshold: 3+ in 5 minutes)
- Account lockouts
- PHI access outside business hours
- High-privilege actions (admin operations)
- Error rate spikes
- Rate limit violations

**Alerting**:
- Email alerts to security team
- Azure Application Insights integration
- Future: SIEM integration

### 10.3 Anomaly Detection (Planned)

**Planned Capabilities**:
- Unusual access patterns (time, location, volume)
- Privilege escalation attempts
- Data exfiltration detection
- Account compromise indicators

**Tools**:
- Azure Security Center
- Custom detection rules
- Machine learning (future)

---

## 11. Incident Response

### 11.1 Incident Response Plan

**Phases**:
1. **Preparation**: IR team, tools, procedures
2. **Detection**: Monitoring, alerts, user reports
3. **Analysis**: Severity assessment, PHI impact
4. **Containment**: Isolate affected systems
5. **Eradication**: Remove threat, patch vulnerabilities
6. **Recovery**: Restore systems, verify integrity
7. **Post-Incident**: Root cause analysis, lessons learned

**Document**: `INCIDENT_RESPONSE_PLAN.md`

### 11.2 Security Event Response

**Event Categories**:

| Category | Examples | Response Time | Escalation |
|----------|----------|---------------|------------|
| **Critical** | Data breach, ransomware | Immediate | CISO, CEO |
| **High** | Account compromise, PHI exposure | 1 hour | Security team, CTO |
| **Medium** | Failed login attempts, rate limit abuse | 4 hours | Security analyst |
| **Low** | Misconfiguration, policy violation | 24 hours | IT team |

### 11.3 Breach Notification

**HIPAA Breach Notification**:
- Assessment within 24 hours
- Individual notification within 60 days (if PHI compromised)
- HHS notification within 60 days (if >500 individuals)
- Media notification (if >500 in same state)

**Procedure**: See HIPAA Compliance Document (Section 8)

---

## 12. Security Operations

### 12.1 Security Assessments

**Schedule**:
- Monthly vulnerability scans
- Quarterly penetration testing
- Annual comprehensive security assessment
- Annual HIPAA security risk assessment

**Testing Scope**:
- Web application security (OWASP Top 10)
- API security
- Authentication and authorization
- Data protection
- Network security
- Social engineering (phishing simulations)

### 12.2 Vulnerability Management

**Process**:
1. **Identification**: Automated scanning, security advisories
2. **Assessment**: Severity rating (CVSS score)
3. **Prioritization**: Based on severity and exploitability
4. **Remediation**: Patching within SLA
5. **Verification**: Confirm fix effectiveness

**Remediation SLA**:
- Critical: 72 hours
- High: 7 days
- Medium: 30 days
- Low: 90 days

### 12.3 Security Training

**Annual Training**:
- HIPAA security and privacy
- Security awareness
- Phishing recognition
- Incident reporting

**Role-Specific Training**:
- Developers: Secure coding (OWASP)
- Administrators: Access control, audit log review
- All staff: Data handling, privacy

### 12.4 Security Metrics

**Key Metrics**:
- Mean time to detect (MTTD)
- Mean time to respond (MTTR)
- Vulnerability remediation time
- Security training completion rate
- Failed login rate
- PHI access audit completion rate

**Reporting**: Monthly to security team, quarterly to executive leadership

---

**END OF DOCUMENT**

**Classification**: Confidential
**Distribution**: Security team, compliance team, executive leadership, auditors (NDA required)
