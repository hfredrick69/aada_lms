# AADA LMS - Systems Integration Specification
**Version:** 3.0
**Date:** December 1, 2024
**Status:** Active Development - Lead-Based Document Signing Complete

---

## Executive Summary

The Atlanta Academy of Dental Assisting (AADA) Learning Management System (LMS) is a comprehensive educational platform designed for dental assistant training programs. This document specifies the technical architecture, data models, API endpoints, security implementation, and integration points for the system.

**Recent Updates:**
- ✅ Lead-based document signing workflow (no authentication required)
- ✅ CRM integration with lead sources and lead management
- ✅ Token-based secure document signing (512-bit cryptographic tokens)
- ✅ Rate limiting on public endpoints (10 requests/60 seconds)
- ✅ ESIGN Act compliance (IP tracking, user agent, timestamps)
- ✅ Public signing page for leads (React TypeScript)
- ✅ Admin portal UI for sending documents to leads
- ✅ Comprehensive E2E tests for signing workflow
- ✅ Complete RBAC implementation with 6 distinct roles
- ✅ All roles standardized to lowercase
- ✅ Comprehensive test suite for role permissions

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [CRM & Lead Management](#crm--lead-management)
6. [Document Signing System](#document-signing-system)
7. [API Endpoints](#api-endpoints)
8. [Security & Compliance](#security--compliance)
9. [Authentication & Authorization](#authentication--authorization)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Architecture](#deployment-architecture)
12. [Integration Points](#integration-points)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                              │
│  ┌──────────────────┐        ┌──────────────────┐           │
│  │  Admin Portal    │        │  Student Portal  │           │
│  │  (React + Vite)  │        │  (React + Vite)  │           │
│  │  Port: 5173      │        │  Port: 5174      │           │
│  └──────────────────┘        └──────────────────┘           │
│         │                              │                      │
│         │                              │                      │
│         └──────────────┬───────────────┘                      │
│                        │                                      │
│                        ▼                                      │
│              ┌──────────────────┐                            │
│              │ Public Signing   │                            │
│              │ Page (No Auth)   │                            │
│              │ /sign/:token     │                            │
│              └──────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                          │
│              FastAPI Backend (Port: 8000)                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Router  │  │ RBAC Module  │  │ Audit Logger │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Public Sign  │  │ Rate Limiter │  │ Token Service│      │
│  │    Router    │  │  Middleware  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Programs &  │  │  Compliance  │  │    Users &   │      │
│  │   Modules    │  │   Tracking   │  │    Roles     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Enrollment  │  │   Financial  │  │  H5P Content │      │
│  │  Management  │  │   Ledgers    │  │   Delivery   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │     CRM &    │  │  Document    │                         │
│  │     Leads    │  │   Signing    │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Persistence Layer                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         PostgreSQL Database (Port: 5432)             │   │
│  │                                                       │   │
│  │  Schemas:                                            │   │
│  │  - public (users, roles, programs, enrollments)     │   │
│  │  - compliance (attendance, credentials, transcripts) │   │
│  │  - audit (audit_logs, session tracking)             │   │
│  │  - crm (leads, lead_sources)                        │   │
│  │  - documents (templates, documents, audit_trail)    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**Admin Portal (`admin_portal/`)**
- User management (CRUD operations for all roles)
- Program and module configuration
- Compliance tracking and reporting
- Financial ledger management
- Enrollment management
- **Lead management and document sending**

**Student Portal (`frontend/aada_web/`)**
- Course enrollment and progress tracking
- H5P interactive content delivery
- Module completion tracking
- Personal transcript access
- **Public document signing (no auth required)**

**Backend API (`backend/`)**
- RESTful API endpoints
- Business logic processing
- RBAC enforcement
- Data validation
- Audit logging
- **Token-based public signing**
- **Rate limiting on public endpoints**

---

## Technology Stack

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18.3.1 | UI components |
| Build Tool | Vite | 5.4.11 | Development & build |
| Routing | React Router | 7.0.1 | Client-side routing |
| HTTP Client | Axios | 1.7.7 | API communication |
| Signature Canvas | react-signature-canvas | 4.2.0 | Digital signature capture |
| Testing | Vitest | 2.1.5 | Unit testing |
| E2E Testing | Playwright | 1.48.2 | End-to-end testing |

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.115.5 | REST API |
| ORM | SQLAlchemy | 2.0.36 | Database ORM |
| Migrations | Alembic | 1.14.0 | Schema versioning |
| Auth | python-jose | 3.3.0 | JWT tokens |
| Password | passlib[bcrypt] | 1.7.4 | Password hashing |
| Validation | Pydantic | 2.10.2 | Data validation |
| Cryptography | secrets | stdlib | Secure token generation |
| Testing | pytest | 8.3.3 | Unit testing |

### Database
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| RDBMS | PostgreSQL | 15.x | Primary database |
| Extensions | citext | - | Case-insensitive text |
| Extensions | pgcrypto | - | Encryption functions |

### DevOps
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Containerization | Docker | 24.x | Application containers |
| Orchestration | Docker Compose | 2.x | Multi-container apps |
| CI/CD | Git Hooks | - | Pre-commit linting |

---

## Database Schema

### Core Tables

#### `users` Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `roles` Table
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL, -- lowercase: admin, staff, instructor, finance, registrar, student
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `user_roles` Table (Junction)
```sql
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);
```

### CRM Schema Tables

#### `crm.lead_sources` Table
```sql
CREATE TABLE crm.lead_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `crm.leads` Table
```sql
CREATE TABLE crm.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    lead_source_id UUID REFERENCES crm.lead_sources(id),
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'enrolled', 'lost')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Document Management Schema Tables

#### `document_templates` Table
```sql
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    file_path TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `documents` Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES document_templates(id),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    lead_id UUID REFERENCES crm.leads(id) ON DELETE SET NULL,
    signing_token TEXT UNIQUE,
    token_expires_at TIMESTAMP,
    signer_name TEXT NOT NULL,
    signer_email TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'student_signed', 'admin_signed', 'completed', 'voided')),
    student_signed_at TIMESTAMP,
    student_signature_data TEXT,
    student_ip_address TEXT,
    student_user_agent TEXT,
    admin_signed_at TIMESTAMP,
    admin_signed_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CHECK (user_id IS NOT NULL OR lead_id IS NOT NULL)
);
```

#### `document_audit_trail` Table
```sql
CREATE TABLE document_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB,
    ip_address TEXT,
    user_agent TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Role-Based Access Control (RBAC)

### Role Hierarchy

```
admin (highest privileges)
  │
  ├─ staff (instructor permissions + student CRUD)
  │    │
  │    └─ instructor (program/module management, attendance, skills)
  │
  ├─ finance (financial operations only)
  │
  ├─ registrar (student records, credentials, transcripts)
  │
  └─ student (own data only)
```

### Role Definitions

#### 1. **admin** (System Administrator)
**Permissions:**
- ✅ Full system access
- ✅ Create/update/delete programs and modules
- ✅ Create/update/delete users (all roles)
- ✅ View/manage all data across all users
- ✅ Access all compliance reports
- ✅ Manage system configuration
- ✅ Manage leads and send documents

#### 2. **staff** (Administrative Staff)
**Permissions:**
- ✅ All instructor permissions
- ✅ Create/update/delete student accounts
- ✅ Manage enrollments
- ✅ View all student data
- ✅ Generate compliance reports
- ✅ Manage leads and send documents
- ❌ Cannot delete programs/modules (admin only)

#### 3. **instructor** (Course Instructor)
**Permissions:**
- ✅ Create/update programs and modules
- ✅ View all student progress in assigned modules
- ✅ Manage attendance records
- ✅ Approve skill checkoffs
- ❌ Cannot create/delete student accounts
- ❌ Cannot manage leads
- ❌ Cannot delete programs/modules (admin only)

#### 4. **finance** (Finance Staff)
**Permissions:**
- ✅ View/manage financial ledgers
- ✅ Process payments and refunds
- ✅ View student enrollment financial data
- ✅ Generate financial reports
- ❌ Cannot create/update programs
- ❌ Cannot manage student accounts
- ❌ Cannot manage leads

#### 5. **registrar** (Registrar Office)
**Permissions:**
- ✅ Manage student enrollment records
- ✅ Issue credentials and transcripts
- ✅ View compliance reports
- ✅ Manage withdrawals
- ❌ Cannot create/update programs
- ❌ Cannot manage financial records
- ❌ Cannot manage leads

#### 6. **student** (Enrolled Student)
**Permissions:**
- ✅ View own enrolled courses
- ✅ Access course content (H5P modules)
- ✅ View own progress and grades
- ✅ View own transcript
- ✅ View own documents
- ❌ Cannot view other students' data
- ❌ Cannot manage programs or users

---

## CRM & Lead Management

### Lead Lifecycle

```
1. New Lead Created (status: 'new')
   ↓
2. Lead Contacted (status: 'contacted')
   ↓
3. Lead Qualified (status: 'qualified')
   ↓
4. Document Sent for Signature
   ↓
5. Document Signed by Lead
   ↓
6. Lead Enrolled (status: 'enrolled') OR Lost (status: 'lost')
```

### Lead Sources

Common lead sources tracked in the system:
- Website inquiry
- Phone call
- Walk-in
- Referral
- Social media
- Email campaign
- Event/Job fair

### Document Sending Workflow

**Admin/Staff Actions:**
1. Navigate to Leads page
2. Select lead from list
3. Click "Send Document" button
4. Select document template
5. Generate secure signing link
6. Copy link and send to lead via email/SMS

**Lead Actions:**
1. Receive signing link (valid for 30 days)
2. Click link to access public signing page
3. Review document
4. Provide digital signature
5. Type full name
6. Submit signature

**Security Measures:**
- 512-bit cryptographic signing tokens
- 30-day token expiration
- Single-use tokens (invalidated after signing)
- Rate limiting: 10 requests per 60 seconds
- IP address and user agent tracking
- ESIGN Act compliance

---

## Document Signing System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Document Signing Flow                       │
└─────────────────────────────────────────────────────────────┘

1. Admin Portal:
   - Admin/Staff selects lead
   - Selects document template
   - Clicks "Generate Signing Link"

2. Backend (POST /api/documents/send):
   - Creates document record
   - Generates 512-bit secure token
   - Sets 30-day expiration
   - Returns signing_token

3. Admin Portal:
   - Displays signing link
   - Copy to clipboard
   - Send to lead via email/SMS

4. Lead:
   - Clicks link: /sign/{token}
   - No authentication required

5. Public Signing Page (GET /api/public/sign/{token}):
   - Validates token
   - Checks expiration
   - Returns document details

6. Lead Signs:
   - Draws signature on canvas
   - Types full name
   - Submits (POST /api/public/sign/{token})

7. Backend:
   - Validates signature data
   - Captures IP address
   - Captures user agent
   - Updates document status
   - Creates audit trail
   - Invalidates token

8. Success:
   - Lead sees confirmation
   - Document status: 'student_signed'
   - Admin can view signed document
```

### Token Service

**Implementation:** `backend/app/services/token_service.py`

```python
import secrets
from datetime import datetime, timedelta

def generate_signing_token() -> str:
    """Generate cryptographically secure 512-bit token"""
    return secrets.token_urlsafe(64)

def create_document_token(template_id: str, lead_id: str, db: Session):
    """Create document with signing token"""
    token = generate_signing_token()
    expires_at = datetime.utcnow() + timedelta(days=30)

    document = Document(
        template_id=template_id,
        lead_id=lead_id,
        signing_token=token,
        token_expires_at=expires_at,
        status='pending'
    )
    db.add(document)
    db.commit()
    return document
```

### Rate Limiting

**Implementation:** `backend/app/middleware/rate_limit.py`

```python
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

# Sliding window: 10 requests per 60 seconds
RATE_LIMIT = 10
WINDOW_SECONDS = 60

request_log = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith('/api/public/'):
        client_ip = request.client.host
        now = datetime.utcnow()

        # Clean old requests
        request_log[client_ip] = [
            req_time for req_time in request_log[client_ip]
            if now - req_time < timedelta(seconds=WINDOW_SECONDS)
        ]

        # Check rate limit
        if len(request_log[client_ip]) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Too many requests")

        request_log[client_ip].append(now)

    return await call_next(request)
```

### ESIGN Act Compliance

**Required Data Captured:**
- ✅ Signature data (base64 PNG)
- ✅ Typed name (confirmation)
- ✅ Timestamp (UTC)
- ✅ IP address
- ✅ User agent (browser/device)
- ✅ Electronic signature consent (displayed to user)

**Audit Trail Events:**
- `document_sent` - Document sent to lead
- `document_viewed` - Lead accessed signing page
- `document_signed` - Lead submitted signature
- `token_expired` - Signing token expired
- `token_invalidated` - Token used (single-use)

---

## API Endpoints

### Base URL
```
Development: http://localhost:8000
Production: https://api.aada.edu
```

### Public Endpoints (No Authentication)

#### GET `/api/public/sign/{token}`
**Purpose:** Get document details for signing

**Rate Limit:** 10 requests per 60 seconds per IP

**Response (200 OK):**
```json
{
  "id": "uuid",
  "template_name": "Enrollment Agreement",
  "signer_name": "Jane Prospect",
  "signer_email": "jane.prospect@test.com",
  "content": "Document content here..."
}
```

**Error Responses:**
- `404 Not Found` - Invalid or expired token
- `400 Bad Request` - Document already signed
- `429 Too Many Requests` - Rate limit exceeded

#### POST `/api/public/sign/{token}`
**Purpose:** Submit signature

**Rate Limit:** 10 requests per 60 seconds per IP

**Request:**
```json
{
  "signature_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB...",
  "typed_name": "Jane Prospect"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Document signed successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid signature data or empty name
- `404 Not Found` - Invalid or expired token
- `400 Bad Request` - Document already signed
- `429 Too Many Requests` - Rate limit exceeded

### Document Management Endpoints (Authenticated)

#### GET `/api/documents/templates`
**Purpose:** List document templates

**Required Roles:** `admin`, `staff`

**Query Parameters:**
- `active_only` (boolean) - Filter active templates only (default: true)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Enrollment Agreement",
    "description": "Standard enrollment agreement",
    "version": 1,
    "is_active": true,
    "created_at": "2024-12-01T10:00:00Z"
  }
]
```

#### POST `/api/documents/send`
**Purpose:** Send document to lead or user

**Required Roles:** `admin`, `staff`

**Request (for lead):**
```json
{
  "template_id": "uuid",
  "lead_id": "uuid"
}
```

**Request (for user):**
```json
{
  "template_id": "uuid",
  "user_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "template_id": "uuid",
  "lead_id": "uuid",
  "signing_token": "abc123...xyz",
  "token_expires_at": "2025-01-01T10:00:00Z",
  "status": "pending",
  "signer_name": "Jane Prospect",
  "signer_email": "jane.prospect@test.com"
}
```

#### GET `/api/documents/{document_id}`
**Purpose:** Get document details

**Required Roles:** `admin`, `staff` (all), `student` (own only)

**Response:**
```json
{
  "id": "uuid",
  "template_id": "uuid",
  "status": "student_signed",
  "signer_name": "Jane Prospect",
  "signer_email": "jane.prospect@test.com",
  "student_signed_at": "2024-12-01T14:30:00Z",
  "student_signature_data": "iVBORw0KGgo...",
  "student_ip_address": "192.168.1.1",
  "created_at": "2024-12-01T10:00:00Z"
}
```

#### GET `/api/documents/{document_id}/audit-trail`
**Purpose:** Get audit trail for document

**Required Roles:** `admin`, `staff`

**Response:**
```json
{
  "document_id": "uuid",
  "logs": [
    {
      "id": "uuid",
      "event_type": "document_sent",
      "event_data": {"sent_by": "admin@aada.edu"},
      "ip_address": "192.168.1.100",
      "created_at": "2024-12-01T10:00:00Z"
    },
    {
      "id": "uuid",
      "event_type": "document_signed",
      "event_data": {"typed_name": "Jane Prospect"},
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-12-01T14:30:00Z"
    }
  ]
}
```

### CRM Endpoints (Authenticated)

#### GET `/api/crm/leads/sources`
**Purpose:** List lead sources

**Required Roles:** `admin`, `staff`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Website Inquiry",
    "description": "Leads from website contact form",
    "created_at": "2024-12-01T10:00:00Z"
  }
]
```

#### GET `/api/crm/leads`
**Purpose:** List leads

**Required Roles:** `admin`, `staff`

**Query Parameters:**
- `status` - Filter by status
- `lead_source_id` - Filter by source

**Response:**
```json
[
  {
    "id": "uuid",
    "first_name": "Jane",
    "last_name": "Prospect",
    "email": "jane.prospect@test.com",
    "phone": "555-0123",
    "status": "qualified",
    "lead_source_id": "uuid",
    "created_at": "2024-12-01T10:00:00Z"
  }
]
```

#### POST `/api/crm/leads`
**Purpose:** Create new lead

**Required Roles:** `admin`, `staff`

**Request:**
```json
{
  "first_name": "Jane",
  "last_name": "Prospect",
  "email": "jane.prospect@test.com",
  "phone": "555-0123",
  "lead_source_id": "uuid",
  "notes": "Interested in dental assistant program"
}
```

---

## Security & Compliance

### HIPAA Compliance

**Phase 1-4 Security Measures (Complete):**

#### Phase 1: Password Policy & Audit Logging
- ✅ NIST SP 800-63B compliant password requirements
  - Minimum 12 characters
  - Requires: uppercase, lowercase, digit, special character
- ✅ Bcrypt password hashing (cost factor: 12)
- ✅ Comprehensive audit logging for all PHI access
- ✅ Account lockout after 5 failed attempts (30 min)

#### Phase 2: Role-Based Access Control
- ✅ 6-role system (admin, staff, instructor, finance, registrar, student)
- ✅ Permission-based authorization
- ✅ Multiple roles per user support
- ✅ Staff role hierarchy
- ✅ Audit logging for role changes

#### Phase 3: Token Refresh & Revocation
- ✅ Access tokens: 15-minute lifetime
- ✅ Refresh tokens: 7-day lifetime
- ✅ Token rotation on refresh (enhanced security)
- ✅ Database-backed token revocation
- ✅ SHA-256 token hashing in database

#### Phase 4: httpOnly Cookies & Encryption
- ✅ httpOnly cookie authentication (XSS protection)
- ✅ Automatic token refresh interceptors
- ✅ PostgreSQL pgcrypto extension enabled
- ✅ Encryption helper functions for PHI data
- ✅ Backwards compatible with Authorization header

#### Phase 5: Public Signing Security
- ✅ 512-bit cryptographic tokens for public access
- ✅ 30-day token expiration
- ✅ Single-use tokens (invalidated after signing)
- ✅ Rate limiting: 10 requests per 60 seconds
- ✅ IP address and user agent tracking
- ✅ ESIGN Act compliance

### Rate Limiting

**Public Endpoints:**
- `/api/public/sign/{token}` - 10 requests per 60 seconds per IP
- Sliding window algorithm
- 429 Too Many Requests response when exceeded
- Protects against abuse and DDoS

**Implementation:**
- Middleware-based rate limiting
- In-memory request log (production: Redis recommended)
- Automatic cleanup of expired entries

### Security Headers

All API responses include:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; frame-ancestors 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=()
```

### Audit Logging

**PHI Endpoints (Automatically Logged):**
- `/api/users`
- `/api/enrollments`
- `/api/transcripts`
- `/api/credentials`
- `/api/externships`
- `/api/attendance`
- `/api/finance/ledgers`

**Document Signing Endpoints (Logged):**
- `/api/documents/send` - Document sent to lead/user
- `/api/public/sign/{token}` - Document signed
- `/api/documents/{id}` - Document accessed

**Logged Information:**
- Timestamp
- User ID and email (if authenticated)
- Endpoint accessed
- HTTP method
- IP address
- User agent
- Event-specific data (JSONB)

---

## Authentication & Authorization

### JWT Token Structure

**Access Token Payload:**
```json
{
  "sub": "admin@aada.edu",
  "exp": 1699368900,
  "iat": 1699368000,
  "type": "access"
}
```

**Refresh Token Payload:**
```json
{
  "sub": "admin@aada.edu",
  "exp": 1699972800,
  "iat": 1699368000,
  "type": "refresh",
  "jti": "unique-token-id"
}
```

### Authorization Flow

```
1. User submits credentials → POST /api/auth/login
2. Backend validates credentials
3. Backend generates access + refresh tokens
4. Tokens set as httpOnly cookies
5. User makes authenticated request
6. Backend validates token from cookie (or Authorization header)
7. Backend checks user roles
8. Backend enforces RBAC rules
9. Backend logs PHI access
10. Response returned to client
```

### Public Signing Flow (No Authentication)

```
1. Lead receives signing link with token
2. Lead clicks link → /sign/{token}
3. Frontend extracts token from URL
4. Frontend requests document → GET /api/public/sign/{token}
5. Backend validates token (existence, expiration, not used)
6. Backend checks rate limit
7. Backend returns document details
8. Lead draws signature and types name
9. Lead submits → POST /api/public/sign/{token}
10. Backend validates signature data
11. Backend captures IP and user agent
12. Backend updates document status
13. Backend creates audit trail
14. Backend invalidates token
15. Success response returned
```

---

## Testing Strategy

### Backend Testing

**Unit Tests** (`backend/tests/`)
- `test_token_service.py` - Token generation and validation (18 tests)
- `test_auth_endpoints.py` - Authentication flow
- `test_security_compliance.py` - HIPAA/NIST compliance
- `test_role_permissions.py` - RBAC permissions for all 6 roles
- `test_users_api.py` - User management
- `test_roles_api.py` - Role management

**Test Coverage:**
- Password policy enforcement
- Security headers
- RBAC enforcement for all roles
- Token refresh and rotation
- Audit logging
- Cross-role access control
- Role hierarchy
- Document signing tokens
- Rate limiting

**Run Tests:**
```bash
docker exec aada_lms-backend-1 sh -c "cd /code && python3 -m pytest backend/tests/ -v"
```

### Frontend Testing

**E2E Tests** (Playwright)

`e2e-tests/lead-document-signing.spec.ts`:
- Complete lead signing workflow (create lead → send doc → sign → verify)
- Invalid token handling (404 error)
- Double-signing prevention (400 error)
- Rate limiting enforcement (429 error)
- Audit trail verification
- Signature data validation

**Test Scenarios:**
1. **Complete Workflow:**
   - Admin logs in
   - Admin creates lead
   - Admin sends document to lead
   - Lead accesses public signing page (no auth)
   - Lead submits signature
   - Verify document status changed to 'student_signed'
   - Verify signature data captured

2. **Security Tests:**
   - Invalid token returns 404
   - Expired token returns 404
   - Already-signed document returns 400
   - Rate limit exceeded returns 429
   - Empty signature data returns 400
   - Empty typed name returns 400

3. **Audit Trail:**
   - Verify 'document_sent' event logged
   - Verify 'document_signed' event logged
   - Verify IP and user agent captured

**Run Tests:**
```bash
cd /Users/herbert/Projects/AADA/OnlineCourse/aada_lms
npm run test:e2e
```

---

## Deployment Architecture

### Docker Compose Services

```yaml
services:
  db:
    image: postgres:15
    ports: 5432:5432

  backend:
    build: ./backend
    ports: 8000:8000
    depends_on: [db]

  admin_portal:
    build: ./admin_portal
    ports: 5173:5173
    depends_on: [backend]

  frontend:
    build: ./frontend/aada_web
    ports: 5174:5174
    depends_on: [backend]
```

### Environment Configuration

**Backend (.env):**
```bash
DATABASE_URL=postgresql://aada:password@db:5432/aada_lms
SECRET_KEY=<secure-random-key>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
SESSION_TIMEOUT_MINUTES=30
SIGNING_TOKEN_EXPIRE_DAYS=30
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=false
```

---

## Integration Points

### H5P Content Delivery

**Location:** `backend/app/static/modules/`

**Integration:**
- H5P content extracted and served statically
- Module content linked to database records
- xAPI statements tracked for completion

**Example Module:**
- `module1/M1_H5P_EthicsBranching/` - Ethics branching scenario
- `module1/M1_H5P_HIPAAHotspot/` - HIPAA compliance hotspot activity

### xAPI Statement Tracking

**Table:** `xapi_statements`

**Example Statement:**
```json
{
  "actor": {
    "mbox": "mailto:alice.student@aada.edu",
    "name": "Alice Student"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed"
  },
  "object": {
    "id": "http://aada.edu/modules/uuid-here"
  },
  "timestamp": "2024-12-01T14:30:00Z"
}
```

### Future Integration Points

**Planned:**
- ✅ Instructor assignment system (instructor→module→student)
- Email notification system (SendGrid) - for sending signing links
- Payment gateway integration (Stripe/PayPal)
- Document storage (AWS S3) - for signed PDFs
- Video conferencing (Zoom API)
- SMS notifications (Twilio) - for sending signing links

---

## Appendices

### A. Database Migration Commands

```bash
# Create new migration
docker exec aada_lms-backend-1 sh -c "cd /code && alembic revision --autogenerate -m 'description'"

# Apply migrations
docker exec aada_lms-backend-1 sh -c "cd /code && alembic upgrade head"

# Rollback migration
docker exec aada_lms-backend-1 sh -c "cd /code && alembic downgrade -1"
```

### B. API Documentation

**Interactive API Docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### C. System Requirements

**Development:**
- Docker Desktop 24.x+
- Node.js 18.x+
- Python 3.11+
- PostgreSQL 15.x+

**Production:**
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ storage
- SSL certificate

### D. Monitoring & Logging

**Log Files:**
- Backend: Docker logs (`docker-compose logs backend`)
- Frontend: Browser console
- Database: PostgreSQL logs

**Metrics:**
- API response times
- Database query performance
- Authentication success/failure rates
- Role-based access denials
- Rate limit violations
- Document signing completion rate

---

## Change Log

### Version 3.0 (December 1, 2024)
- ✅ Lead-based document signing workflow
- ✅ CRM integration with leads and lead sources
- ✅ Token-based public signing (512-bit cryptographic tokens)
- ✅ Rate limiting on public endpoints (10 req/60s)
- ✅ ESIGN Act compliance (IP, user agent, timestamps)
- ✅ Public signing page (React TypeScript)
- ✅ Admin portal UI for document sending
- ✅ SendDocumentModal component
- ✅ E2E tests for signing workflow
- ✅ Document audit trail
- ✅ Migration: 0010_lead_based_signing.py
- ✅ Token service with unit tests (18/18 passing)
- ✅ Rate limiting middleware

### Version 2.0 (November 5, 2025)
- ✅ Complete RBAC implementation with 6 roles
- ✅ All roles standardized to lowercase
- ✅ Comprehensive test suite (`test_role_permissions.py`)
- ✅ Test accounts for all roles
- ✅ Staff role hierarchy
- ✅ Updated TEST_CREDENTIALS.md
- ✅ Enhanced RBAC documentation

### Version 1.0 (November 4, 2025)
- Initial system architecture
- Database schema design
- Authentication implementation
- Basic RBAC structure
- H5P content integration

---

## Contact & Support

**Project Repository:** https://github.com/aada/lms
**Documentation:** See `/TEST_CREDENTIALS.md` for test accounts
**Issues:** Report via GitHub Issues

---

**Document Version:** 3.0
**Last Updated:** December 1, 2024
**Next Review:** January 1, 2025
