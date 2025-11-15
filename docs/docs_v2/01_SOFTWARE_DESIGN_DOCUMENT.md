# AADA LMS - Software Design Document (SDD)

**Document Version:** 2.0
**Last Updated:** November 14, 2025
**System Version:** 1.0
**Classification:** Internal Use
**Owner:** AADA Technical Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [System Architecture](#3-system-architecture)
4. [Data Architecture](#4-data-architecture)
5. [Security Architecture](#5-security-architecture)
6. [API Design](#6-api-design)
7. [Integration Architecture](#7-integration-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Quality Attributes](#9-quality-attributes)
10. [Technology Stack](#10-technology-stack)
11. [Appendices](#11-appendices)

---

## 1. Executive Summary

### 1.1 Purpose
The AADA Learning Management System (LMS) is a HIPAA-compliant healthcare education platform designed to deliver interactive educational content, manage student enrollment, track academic progress, handle financial transactions, and maintain comprehensive compliance records for healthcare training programs.

### 1.2 Scope
This Software Design Document describes the architecture, components, interfaces, and design decisions for the AADA LMS. It serves as the authoritative technical reference for development, maintenance, security audits, and compliance verification.

### 1.3 Key Capabilities
- **Student Management**: Registration, enrollment, progress tracking, certification
- **Content Delivery**: H5P interactive content, SCORM/xAPI learning standards
- **Document Management**: Electronic signature workflows with complete audit trails
- **Financial Operations**: Payment processing, refund management, financial ledger
- **Compliance Tracking**: HIPAA, FERPA, NIST, SOC 2, institutional accreditation
- **CRM Integration**: Lead management, lead scoring, enrollment funnel tracking
- **Audit & Reporting**: Comprehensive audit logging, compliance reports, analytics

### 1.4 Design Principles
1. **Security First**: All design decisions prioritize data security and privacy
2. **Compliance by Design**: HIPAA/NIST/FERPA requirements integrated from ground up
3. **Auditability**: Complete audit trail for all system operations
4. **Scalability**: Stateless architecture supporting horizontal scaling
5. **Maintainability**: Clear separation of concerns, well-documented codebase
6. **User Experience**: Intuitive interfaces for students, staff, and administrators

---

## 2. System Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Systems                         │
├─────────────────────────────────────────────────────────────────┤
│  Azure Cloud Services  │  SendGrid/ACS  │  Payment Gateway     │
└──────────────┬──────────────────┬───────────────┬──────────────┘
               │                  │               │
               ▼                  ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AADA LMS Platform                        │
├──────────────────┬───────────────────┬──────────────────────────┤
│  Student Portal  │  Admin Portal     │  Public APIs             │
│  (React/TS)      │  (React/MUI)      │  (REST)                  │
└──────────────────┴───────────────────┴──────────────────────────┘
               │                  │               │
               └──────────────────┼───────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API (FastAPI)                       │
├──────────────────┬───────────────────┬──────────────────────────┤
│  Authentication  │  Business Logic   │  Data Access Layer       │
│  & Authorization │  Services         │  (SQLAlchemy ORM)        │
└──────────────────┴───────────────────┴──────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL 16 Database (with pgcrypto)              │
│                     (PHI Encrypted at Rest)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 User Personas

| Role | Description | Key Functions |
|------|-------------|---------------|
| **Student** | End-users accessing educational content | View courses, complete modules, sign documents, track progress |
| **Instructor** | Faculty delivering and grading content | Manage course content, grade assignments, track student performance |
| **Registrar** | Enrollment and records management | Enroll students, manage transcripts, issue credentials |
| **Finance** | Financial operations staff | Process payments, manage refunds, financial reporting |
| **Admin** | System administrators | User management, system configuration, compliance oversight |
| **Staff** | General administrative staff | Student support, document management, reporting |

### 2.3 System Features Map

```
AADA LMS
├── User Management
│   ├── Registration (3-step with email verification)
│   ├── Authentication (JWT + Refresh Tokens)
│   ├── Role-Based Access Control (6 roles)
│   └── Profile Management
├── Academic Management
│   ├── Program & Course Catalog
│   ├── Module Management
│   ├── Student Enrollment
│   ├── Progress Tracking
│   └── Transcript Generation
├── Content Delivery
│   ├── H5P Interactive Content
│   ├── xAPI/Tin Can Tracking
│   ├── SCORM Support
│   └── Progress Persistence
├── Document Management
│   ├── Template Management
│   ├── Electronic Signature Workflow
│   ├── Public Signing Links
│   └── Document Audit Trail
├── Financial Management
│   ├── Payment Processing
│   ├── Refund Management (45-day policy)
│   ├── Financial Ledger
│   └── Financial Reporting
├── Compliance & Accreditation
│   ├── Attendance Tracking
│   ├── Skills Checkoffs
│   ├── Externship Management
│   ├── Credential Tracking
│   ├── Complaint Management
│   └── Withdrawal Processing
├── CRM & Lead Management
│   ├── Lead Capture & Scoring
│   ├── Lead Source Tracking
│   ├── Enrollment Funnel Analytics
│   └── Custom Field Management
└── Audit & Reporting
    ├── Comprehensive Audit Logs
    ├── PHI Access Tracking
    ├── Compliance Reports
    └── Analytics Dashboard
```

---

## 3. System Architecture

### 3.1 Architectural Style

**Multi-Tier Layered Architecture** with the following layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  Student Portal (React)  │  Admin Portal (React)                │
│  - User Interfaces       │  - Management Consoles               │
│  - Client-side Validation│  - Reporting Dashboards              │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS/REST
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                 │
│  FastAPI REST API (25 Routers, 100+ Endpoints)                  │
│  - Request Validation (Pydantic)                                │
│  - Authentication Middleware (JWT)                              │
│  - Security Middleware (Headers, CORS)                          │
│  - Rate Limiting                                                │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│  Service Components:                                            │
│  - Email Service (SendGrid/ACS/Console)                         │
│  - PDF Service (Document Generation & Signing)                  │
│  - Token Service (JWT & Refresh Token Management)               │
│  - File Validation Service (Security Scanning)                  │
│  - Encryption Service (pgcrypto wrapper)                        │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                             │
│  SQLAlchemy ORM                                                 │
│  - Models (26+ tables)                                          │
│  - Repositories                                                 │
│  - Database Sessions                                            │
│  - Migration Management (Alembic)                               │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  PostgreSQL 16 with pgcrypto Extension                          │
│  - Primary Data Storage                                         │
│  - AES-256 Encryption (PHI fields)                              │
│  - Transaction Management                                       │
│  - Connection Pooling                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Architecture

#### 3.2.1 Backend Components

**Location**: `/backend/app/`

| Component | Path | Purpose | Key Dependencies |
|-----------|------|---------|------------------|
| **Core Services** | `core/` | Security, config, RBAC, file validation | pydantic, bcrypt, PyJWT |
| **API Routers** | `routers/` | REST endpoint handlers (25 modules) | FastAPI, pydantic |
| **Data Models** | `db/models/` | SQLAlchemy ORM models (26+ tables) | SQLAlchemy, pgcrypto |
| **Schemas** | `schemas/` | Request/response validation | Pydantic |
| **Middleware** | `middleware/` | Security headers, rate limiting, audit | FastAPI middleware |
| **Services** | `services/` | Business logic (email, PDF, tokens) | ReportLab, SendGrid |
| **Utilities** | `utils/` | Encryption, helpers | cryptography |

**Key Backend Files**:
- `app/core/security.py` - JWT, bcrypt, token management (5.2 KB)
- `app/core/rbac.py` - Role-based access control (3.1 KB)
- `app/core/file_validation.py` - Upload security (15.8 KB)
- `app/middleware/security.py` - Security headers & audit logging
- `app/db/base.py` - Database session management
- `app/main.py` - Application entry point

#### 3.2.2 Frontend Components

**Student Portal** (`/student_portal/`)
- **Framework**: React 18 + TypeScript + Vite
- **UI Library**: Tailwind CSS
- **Key Features**:
  - Dashboard with enrolled courses
  - Progress tracking with resume capability
  - Document signing (Signature Pad)
  - Payment status tracking
  - Responsive design

**Admin Portal** (`/admin_portal/`)
- **Framework**: React 18 + Material-UI + Vite
- **Key Features**:
  - Student roster management
  - Enrollment CRUD operations
  - Financial tracking & refunds
  - Document template management
  - CRM & lead management
  - Audit log viewer
  - Bulk operations support

**Shared Frontend Infrastructure**:
- Axios HTTP client with interceptors
- Automatic JWT token injection
- Token refresh on 401 responses
- Centralized error handling
- Form validation (React Hook Form)

### 3.3 Request Flow

**Authenticated Request Flow**:

```
1. User Action (Frontend)
   │
   ▼
2. Axios Interceptor
   │ - Inject JWT token in Authorization header
   │ - Add CSRF protection
   ▼
3. FastAPI Router
   │ - CORS validation
   │ - Rate limiting check
   │
   ▼
4. Authentication Middleware
   │ - Verify JWT signature
   │ - Check token expiration
   │ - Extract user identity
   │
   ▼
5. Authorization Check (RBAC)
   │ - Verify user role
   │ - Check endpoint permissions
   │
   ▼
6. Request Validation (Pydantic)
   │ - Validate request schema
   │ - Sanitize inputs
   │
   ▼
7. Business Logic (Service Layer)
   │ - Execute business rules
   │ - Validate business constraints
   │
   ▼
8. Data Access (ORM)
   │ - Database queries
   │ - Encrypt PHI fields (write)
   │ - Decrypt PHI fields (read)
   │
   ▼
9. Audit Logging
   │ - Log request (user, endpoint, status, IP, PHI flag)
   │
   ▼
10. Response
   │ - Format response (Pydantic schema)
   │ - Add security headers
   │ - Return to client
   │
   ▼
11. Axios Interceptor (Response)
   │ - Handle errors
   │ - Refresh token if 401
   │ - Update UI state
```

### 3.4 Security Layers

The system implements defense-in-depth with 7 security layers:

1. **Network Layer**: HTTPS/TLS encryption, CORS policies
2. **Application Layer**: Security headers (HSTS, CSP, X-Frame-Options)
3. **Authentication Layer**: JWT tokens, bcrypt passwords, refresh tokens
4. **Authorization Layer**: RBAC with 6 roles, per-endpoint checks
5. **Input Validation Layer**: Pydantic schemas, file validation, sanitization
6. **Data Layer**: AES-256 encryption, pgcrypto for PHI
7. **Audit Layer**: Comprehensive logging of all operations

---

## 4. Data Architecture

### 4.1 Database Schema Overview

**Database**: PostgreSQL 16
**Extension**: pgcrypto (for encryption)
**Migration Tool**: Alembic
**ORM**: SQLAlchemy 2.x

**Schema Organization**:
- **public** schema: Core application tables (26+ tables)
- **compliance** schema: Compliance-specific tables (8 tables)
- **crm** schema: CRM and lead management (3 tables)

### 4.2 Core Data Models

#### 4.2.1 User Management

**User Table** (`users`)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,  -- Encrypted with pgcrypto
    first_name VARCHAR(100),              -- Encrypted with pgcrypto
    last_name VARCHAR(100),               -- Encrypted with pgcrypto
    password_hash VARCHAR(255) NOT NULL,  -- Bcrypt hashed
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Role Management** (`roles`, `user_roles`)
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,  -- admin, staff, registrar, instructor, finance, student
    description TEXT
);

CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);
```

#### 4.2.2 Academic Management

**Programs** (`programs`)
```sql
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_weeks INTEGER,
    clock_hours INTEGER,  -- For accreditation
    tuition DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Modules** (`modules`)
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    content_type VARCHAR(50),  -- 'h5p', 'scorm', 'xapi'
    content_id VARCHAR(255),
    clock_hours DECIMAL(5, 2),
    is_required BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Enrollments** (`enrollments`)
```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    enrollment_date DATE NOT NULL,
    completion_date DATE,
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, withdrawn, suspended
    payment_status VARCHAR(50) DEFAULT 'pending',  -- pending, paid, refunded
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, program_id)
);
```

**Progress Tracking** (`module_progress`)
```sql
CREATE TABLE module_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'not_started',  -- not_started, in_progress, completed
    progress_percentage INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    state_data JSONB,  -- Stores resume position, answers, etc.
    UNIQUE(enrollment_id, module_id)
);
```

#### 4.2.3 Document Management

**Document Templates** (`document_templates`)
```sql
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(100),  -- enrollment_agreement, refund_policy, etc.
    pdf_path VARCHAR(500),
    signature_fields JSONB,  -- Coordinates for signature placements
    is_active BOOLEAN DEFAULT true,
    requires_countersignature BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Signed Documents** (`signed_documents`)
```sql
CREATE TABLE signed_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES document_templates(id),
    user_id UUID REFERENCES users(id),
    enrollment_id UUID REFERENCES enrollments(id),
    document_data JSONB,  -- Populated template data
    signed_pdf_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'created',  -- created, sent, viewed, signed, completed
    signing_token VARCHAR(255) UNIQUE,  -- Public signing link token
    token_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Document Signatures** (`document_signatures`)
```sql
CREATE TABLE document_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES signed_documents(id) ON DELETE CASCADE,
    signer_name VARCHAR(255) NOT NULL,     -- Encrypted
    signer_email VARCHAR(255) NOT NULL,    -- Encrypted
    signature_data TEXT NOT NULL,          -- Base64 encoded signature image
    signature_type VARCHAR(50),            -- 'student', 'official', 'witness'
    ip_address VARCHAR(45),                -- IPv6 support
    user_agent TEXT,
    signed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Document Audit Trail** (`document_audit_logs`)
```sql
CREATE TABLE document_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES signed_documents(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,  -- created, sent, viewed, signed, countersigned, completed, downloaded
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),           -- Encrypted
    ip_address VARCHAR(45),
    user_agent TEXT,
    event_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient audit queries
CREATE INDEX idx_doc_audit_document ON document_audit_logs(document_id, created_at DESC);
```

#### 4.2.4 Financial Management

**Financial Ledger** (`compliance.financial_ledgers`)
```sql
CREATE TABLE compliance.financial_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL,  -- payment, refund, adjustment, scholarship
    amount DECIMAL(10, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    description TEXT,
    payment_method VARCHAR(50),
    reference_number VARCHAR(100),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Refunds** (`compliance.refunds`)
```sql
CREATE TABLE compliance.refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    requested_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    reason TEXT NOT NULL,                   -- Encrypted
    refund_amount DECIMAL(10, 2) NOT NULL,
    refund_percentage DECIMAL(5, 2),
    progress_at_withdrawal INTEGER,         -- Progress % when withdrawn
    request_date DATE NOT NULL,
    approval_date DATE,
    refund_date DATE,
    status VARCHAR(50) DEFAULT 'pending',   -- pending, approved, denied, processed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.5 Compliance Tracking

**Attendance Logs** (`compliance.attendance_logs`)
```sql
CREATE TABLE compliance.attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    clock_hours DECIMAL(5, 2) NOT NULL,
    activity_description TEXT,
    logged_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Skills Checkoffs** (`compliance.skill_checkoffs`)
```sql
CREATE TABLE compliance.skill_checkoffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100),
    competency_level VARCHAR(50),  -- novice, intermediate, proficient, expert
    assessment_date DATE NOT NULL,
    assessed_by UUID REFERENCES users(id),
    notes TEXT,                    -- Encrypted
    passed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Credentials** (`compliance.credentials`)
```sql
CREATE TABLE compliance.credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    credential_type VARCHAR(100) NOT NULL,  -- certification, license, degree
    credential_name VARCHAR(255) NOT NULL,
    issuing_authority VARCHAR(255),
    credential_number VARCHAR(100),         -- Encrypted
    issue_date DATE,
    expiration_date DATE,
    verification_url VARCHAR(500),
    document_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Transcripts** (`compliance.transcripts`)
```sql
CREATE TABLE compliance.transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID REFERENCES enrollments(id) ON DELETE CASCADE,
    transcript_data JSONB NOT NULL,  -- Structured transcript information
    gpa DECIMAL(3, 2),
    total_clock_hours DECIMAL(7, 2),
    generated_date DATE NOT NULL,
    generated_by UUID REFERENCES users(id),
    pdf_path VARCHAR(500),
    is_official BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.6 CRM & Lead Management

**Leads** (`crm.leads`)
```sql
CREATE TABLE crm.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100),               -- Encrypted
    last_name VARCHAR(100),                -- Encrypted
    email VARCHAR(255) UNIQUE NOT NULL,    -- Encrypted
    phone VARCHAR(20),                     -- Encrypted
    source_id UUID REFERENCES crm.lead_sources(id),
    status VARCHAR(50) DEFAULT 'new',      -- new, contacted, qualified, enrolled, lost
    lead_score INTEGER DEFAULT 0,          -- 0-100 scoring
    program_interest UUID REFERENCES programs(id),
    notes TEXT,                            -- Encrypted
    custom_fields JSONB,
    enrolled_user_id UUID REFERENCES users(id),  -- Set when converted to student
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.7 Learning Standards

**xAPI Statements** (`xapi_statements`)
```sql
CREATE TABLE xapi_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    statement_id UUID UNIQUE NOT NULL,
    verb VARCHAR(255) NOT NULL,          -- experienced, completed, passed, failed
    object_id VARCHAR(500) NOT NULL,     -- Activity IRI
    object_type VARCHAR(100),
    result JSONB,                        -- Score, completion, duration
    context JSONB,                       -- Course, platform, extensions
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    stored TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    authority JSONB
);
```

#### 4.2.8 Security & Audit

**Audit Logs** (`audit_logs`)
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,         -- GET, POST, PUT, DELETE
    status_code INTEGER NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_body JSONB,                  -- Sanitized
    phi_access BOOLEAN DEFAULT false,    -- Flag for HIPAA tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient audit queries
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_phi ON audit_logs(phi_access, created_at DESC);
CREATE INDEX idx_audit_status ON audit_logs(status_code, created_at DESC);
CREATE INDEX idx_audit_endpoint ON audit_logs(endpoint, created_at DESC);
```

**Refresh Tokens** (`refresh_tokens`)
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,    -- SHA-256 hashed
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    use_count INTEGER DEFAULT 0,         -- Track token usage
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_refresh_token_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_token_hash ON refresh_tokens(token_hash);
```

### 4.3 Data Encryption Strategy

**Fields Encrypted at Rest** (using PostgreSQL pgcrypto):
- `users.email`
- `users.first_name`
- `users.last_name`
- `document_signatures.signer_name`
- `document_signatures.signer_email`
- `document_audit_logs.user_email`
- `crm.leads.first_name`
- `crm.leads.last_name`
- `crm.leads.email`
- `crm.leads.phone`
- `crm.leads.notes`
- `compliance.credentials.credential_number`
- `compliance.refunds.reason`
- `compliance.skill_checkoffs.notes`

**Encryption Method**:
```sql
-- Write
pgp_sym_encrypt('sensitive_data', current_setting('app.encryption_key'))

-- Read
pgp_sym_decrypt(encrypted_column::bytea, current_setting('app.encryption_key'))
```

**Encryption Key Management**:
- Key stored in environment variable `ENCRYPTION_KEY`
- 32-byte random key (256-bit)
- Rotated every 90 days (per policy)
- Access controlled via Azure Key Vault (production)

### 4.4 Database Relationships

**Entity Relationship Diagram (Key Relationships)**:

```
users ──┬──< user_roles >── roles
        │
        ├──< enrollments >──┬── programs
        │                   │
        │                   └──< module_progress >── modules
        │
        ├──< signed_documents ──┬──< document_signatures
        │                       │
        │                       ├──< document_audit_logs
        │                       │
        │                       └── document_templates
        │
        ├──< audit_logs
        │
        ├──< refresh_tokens
        │
        └──< compliance tables (attendance, skills, credentials, etc.)

crm.leads ──> programs (program_interest)
          └─> users (enrolled_user_id, when converted)
```

### 4.5 Data Retention Policy

| Data Type | Retention Period | Notes |
|-----------|------------------|-------|
| **Audit Logs** | Indefinite | Required for HIPAA compliance |
| **Document Audit Logs** | Indefinite | Legal requirement for e-signatures |
| **User Accounts** | 7 years post-withdrawal | FERPA requirement |
| **Financial Records** | 7 years | IRS requirement |
| **Transcripts** | Permanent | Institutional requirement |
| **Session Tokens** | 7 days max | Auto-cleanup on expiration |
| **Registration Requests** | 30 days | Auto-cleanup if not completed |

---

## 5. Security Architecture

### 5.1 Authentication System

**Multi-Factor Authentication Flow**:

```
Registration Flow (3 Steps):
1. User submits email + password
   │
   ▼
2. System validates password policy (NIST compliant)
   │ - Min 12 characters
   │ - Uppercase, lowercase, digit, special character
   │
   ▼
3. System generates verification token (30-min expiry)
   │
   ▼
4. Email sent with verification link
   │
   ▼
5. User clicks link (completes registration within 15 min)
   │
   ▼
6. Account activated, JWT token issued

Login Flow:
1. User submits email + password
   │
   ▼
2. System retrieves user, verifies bcrypt hash
   │
   ▼
3. Check account status (is_active, is_verified)
   │
   ▼
4. Check failed login attempts (max 5, 30-min lockout)
   │
   ▼
5. Issue JWT access token (15-min expiry)
   │
   ▼
6. Issue refresh token (7-day expiry)
   │
   ▼
7. Store refresh token hash in database
   │
   ▼
8. Return tokens (access token in body, refresh in httpOnly cookie)
```

**Token Structure**:

**Access Token (JWT)**:
```json
{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "roles": ["student"],
  "exp": 1699999999,
  "iat": 1699998999,
  "type": "access"
}
```

**Refresh Token**:
- Random 32-byte urlsafe string
- SHA-256 hashed before database storage
- Tied to specific device (IP + User-Agent tracked)
- Single-use or limited-use to prevent replay attacks

### 5.2 Authorization System (RBAC)

**Role Hierarchy**:

```
┌─────────────────────────────────────────────────────────────┐
│  ADMIN (Full System Access)                                 │
│  - All permissions                                          │
│  - User management                                          │
│  - System configuration                                     │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  STAFF (Administrative Access)                              │
│  - Student management                                       │
│  - Enrollment management                                    │
│  - Document management                                      │
│  - Reporting                                                │
└─────────────────────────────────────────────────────────────┘
           │
           ├──┬──┬──┐
           │  │  │  │
           ▼  ▼  ▼  ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│REGISTRAR│ │INSTRUCTOR│ │ FINANCE│ │ STUDENT│
│         │ │          │ │        │ │        │
│Enrollment│ │Course    │ │Payment │ │Own data│
│Records  │ │Delivery  │ │Refunds │ │Access  │
│Transcripts│ │Grading  │ │Reports │ │        │
└────────┘ └────────┘ └────────┘ └────────┘
```

**Permission Matrix**:

| Endpoint | Admin | Staff | Registrar | Instructor | Finance | Student |
|----------|-------|-------|-----------|------------|---------|---------|
| `POST /users` | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `GET /users` | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| `GET /users/{id}` | ✓ | ✓ | ✓ | ✓ | ✓ | Self only |
| `POST /enrollments` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `GET /enrollments` | ✓ | ✓ | ✓ | ✓ | ✓ | Self only |
| `POST /payments` | ✓ | ✓ | ✗ | ✗ | ✓ | Self only |
| `POST /refunds` | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `GET /transcripts` | ✓ | ✓ | ✓ | ✗ | ✗ | Self only |
| `GET /audit-logs` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `POST /documents` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `GET /documents/sign/{token}` | Public (with valid token) | | | | | |

**Permission Implementation** (`/backend/app/core/rbac.py`):

```python
# Decorator-based authorization
@router.get("/users")
@require_role(["admin", "staff", "registrar"])
async def list_users(current_user: User = Depends(get_current_user)):
    # Endpoint implementation
    pass

# Function-based authorization
def can_access_enrollment(user: User, enrollment: Enrollment) -> bool:
    # Admin/staff can access all
    if user.has_role(["admin", "staff", "registrar"]):
        return True
    # Students can only access their own
    if user.has_role("student") and enrollment.user_id == user.id:
        return True
    return False
```

### 5.3 Input Validation & Sanitization

**Validation Layers**:

1. **Client-side Validation** (React Hook Form)
   - Format validation
   - Required field checks
   - Real-time feedback

2. **API Schema Validation** (Pydantic)
   - Type validation
   - Range validation
   - Pattern matching (regex)
   - Custom validators

3. **Business Rule Validation** (Service Layer)
   - Referential integrity
   - Business constraints
   - State machine validation

**Example Pydantic Schema** (`/backend/app/schemas/user.py`):

```python
from pydantic import BaseModel, EmailStr, constr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=12, max_length=128)
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)

    @validator('password')
    def validate_password_complexity(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```

### 5.4 File Upload Security

**7-Layer Security Validation** (`/backend/app/core/file_validation.py`):

```python
def validate_and_sanitize_file(file: UploadFile) -> bool:
    # Layer 1: Extension validation
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if not file.filename.endswith(tuple(allowed_extensions)):
        raise ValueError("Invalid file extension")

    # Layer 2: Magic bytes verification
    magic_bytes = file.file.read(8)
    file.file.seek(0)
    if not verify_magic_bytes(magic_bytes, file.filename):
        raise ValueError("File type mismatch")

    # Layer 3: File size limits
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
    if file.size > MAX_PDF_SIZE:
        raise ValueError("File too large")

    # Layer 4: PDF sanitization (if PDF)
    if file.filename.endswith('.pdf'):
        sanitize_pdf(file)  # Remove JavaScript, embedded files, forms

    # Layer 5: Image sanitization (if image)
    if file.filename.endswith(('.png', '.jpg', '.jpeg')):
        strip_exif_data(file)  # Remove metadata

    # Layer 6: Virus scanning (optional, ClamAV)
    if ENABLE_VIRUS_SCAN:
        scan_for_viruses(file)

    # Layer 7: Structure validation
    validate_file_structure(file)

    return True
```

**PDF Sanitization**:
- Remove JavaScript
- Remove embedded files
- Remove form fields (XFA forms)
- Validate PDF structure
- Flatten annotations

**Image Sanitization**:
- Strip EXIF metadata (location, camera info)
- Validate image dimensions
- Re-encode to remove embedded data
- Validate image structure

### 5.5 Rate Limiting

**Implementation** (`/backend/app/middleware/rate_limit.py`):

```python
# IP-based sliding window rate limiting
RATE_LIMITS = {
    "/api/auth/login": (5, 300),        # 5 attempts per 5 minutes
    "/api/auth/register": (3, 3600),    # 3 per hour
    "/api/documents/sign": (10, 60),    # 10 per minute
    "DEFAULT": (100, 60)                # 100 per minute default
}

# Redis-upgradeable (currently in-memory)
# For production: Use Redis for distributed rate limiting
```

### 5.6 Security Headers

**HTTP Security Headers** (applied to all responses):

```python
# HSTS - Force HTTPS
Strict-Transport-Security: max-age=31536000; includeSubDomains

# Prevent clickjacking
X-Frame-Options: SAMEORIGIN

# Prevent MIME sniffing
X-Content-Type-Options: nosniff

# Content Security Policy
Content-Security-Policy:
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval' h5p.org *.h5p.org;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' data:;

# Referrer Policy
Referrer-Policy: strict-origin-when-cross-origin

# Permissions Policy
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 5.7 Session Management

**Session Security Features**:
- 30-minute session timeout (configurable)
- 15-minute JWT token lifetime (short-lived)
- 7-day refresh token lifetime
- Automatic token refresh on activity
- Account lockout after 5 failed attempts
- 30-minute lockout duration
- Concurrent session tracking
- Token revocation capability

**Session Tracking**:
```python
refresh_tokens table stores:
- User ID
- Token hash (SHA-256)
- IP address
- User agent
- Use count
- Expiration timestamp
- Revocation status
```

---

## 6. API Design

### 6.1 API Overview

**API Type**: RESTful HTTP API
**Framework**: FastAPI 0.104+
**Protocol**: HTTPS (TLS 1.2+)
**Authentication**: JWT Bearer Token
**Response Format**: JSON
**API Version**: v1 (path-based versioning ready)

**Base URLs**:
- Development: `http://localhost:8000`
- Staging: `https://staging-api.aada.edu`
- Production: `https://api.aada.edu`

### 6.2 API Router Structure

**25 API Routers** (`/backend/app/routers/`):

| Router | Prefix | Purpose | Key Endpoints |
|--------|--------|---------|---------------|
| `auth.py` | `/auth` | Authentication & registration | `POST /register`, `POST /login`, `POST /refresh`, `POST /logout` |
| `users.py` | `/users` | User management | `GET /users`, `GET /users/{id}`, `PUT /users/{id}`, `DELETE /users/{id}` |
| `roles.py` | `/roles` | Role management | `GET /roles`, `POST /roles`, `PUT /roles/{id}` |
| `programs.py` | `/programs` | Program catalog | `GET /programs`, `POST /programs`, `PUT /programs/{id}` |
| `modules.py` | `/modules` | Course modules | `GET /modules`, `POST /modules`, `PUT /modules/{id}` |
| `enrollments.py` | `/enrollments` | Student enrollment | `GET /enrollments`, `POST /enrollments`, `PUT /enrollments/{id}` |
| `progress.py` | `/progress` | Learning progress | `GET /progress/{enrollment_id}`, `PUT /progress/{module_id}` |
| `documents.py` | `/documents` | Document management | `GET /documents`, `POST /documents`, `GET /documents/{id}/sign-url` |
| `public_signing.py` | `/sign` | Public signing | `GET /sign/{token}`, `POST /sign/{token}` |
| `payments.py` | `/payments` | Payment processing | `POST /payments`, `GET /payments/{enrollment_id}` |
| `finance.py` | `/finance` | Financial operations | `POST /refunds`, `GET /ledger`, `GET /reports` |
| `leads.py` | `/leads` | CRM lead management | `GET /leads`, `POST /leads`, `PUT /leads/{id}`, `POST /leads/{id}/convert` |
| `students.py` | `/students` | Student operations | `GET /students`, `GET /students/{id}`, `GET /students/{id}/dashboard` |
| `transcripts.py` | `/transcripts` | Transcript management | `GET /transcripts/{enrollment_id}`, `POST /transcripts/generate` |
| `credentials.py` | `/credentials` | Credential tracking | `GET /credentials`, `POST /credentials`, `PUT /credentials/{id}` |
| `attendance.py` | `/attendance` | Attendance logging | `GET /attendance/{enrollment_id}`, `POST /attendance` |
| `skills.py` | `/skills` | Skills checkoffs | `GET /skills/{enrollment_id}`, `POST /skills` |
| `externships.py` | `/externships` | Externship tracking | `GET /externships`, `POST /externships`, `PUT /externships/{id}` |
| `complaints.py` | `/complaints` | Complaint management | `GET /complaints`, `POST /complaints`, `PUT /complaints/{id}` |
| `h5p.py` | `/h5p` | H5P content delivery | `GET /h5p/{content_id}`, `POST /h5p/result` |
| `xapi.py` | `/xapi` | xAPI/Tin Can statements | `POST /xapi/statements`, `GET /xapi/statements` |
| `scorm.py` | `/scorm` | SCORM tracking | `POST /scorm/init`, `PUT /scorm/commit` |
| `content.py` | `/content` | Content management | `GET /content`, `POST /content`, `PUT /content/{id}` |
| `audit.py` | `/audit` | Audit log queries | `GET /audit`, `GET /audit/phi-access` |
| `reports.py` | `/reports` | Reporting & analytics | `GET /reports/enrollment`, `GET /reports/financial`, `GET /reports/compliance` |

### 6.3 API Endpoint Examples

#### 6.3.1 Authentication Endpoints

**POST /auth/register/step1** - Initiate registration
```http
POST /auth/register/step1
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "SecurePass123!@#",
  "first_name": "John",
  "last_name": "Doe"
}

Response 200:
{
  "message": "Verification email sent",
  "email": "student@example.com"
}
```

**POST /auth/login** - Authenticate user
```http
POST /auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "SecurePass123!@#"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "refresh_token": "8f3b7c2d1e5a9f6b4c8e2d7a1b5f3c9e",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["student"]
  }
}

Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**POST /auth/refresh** - Refresh access token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "8f3b7c2d1e5a9f6b4c8e2d7a1b5f3c9e"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 6.3.2 Student Management Endpoints

**GET /students** - List students (admin/staff/registrar)
```http
GET /students?page=1&limit=20&status=active
Authorization: Bearer <access_token>

Response 200:
{
  "total": 156,
  "page": 1,
  "limit": 20,
  "students": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "student@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "enrollment_count": 2,
      "created_at": "2024-01-15T10:30:00Z"
    },
    ...
  ]
}
```

**GET /students/{id}/dashboard** - Student dashboard (student self-access)
```http
GET /students/550e8400-e29b-41d4-a716-446655440000/dashboard
Authorization: Bearer <access_token>

Response 200:
{
  "student": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "enrollments": [
    {
      "id": "enrollment_uuid",
      "program": {
        "id": "program_uuid",
        "name": "Medical Assistant Program",
        "duration_weeks": 36
      },
      "enrollment_date": "2024-01-15",
      "status": "active",
      "overall_progress": 65,
      "modules": [
        {
          "id": "module_uuid",
          "title": "Anatomy & Physiology",
          "status": "completed",
          "progress": 100,
          "completed_at": "2024-02-20T15:30:00Z"
        },
        {
          "id": "module_uuid_2",
          "title": "Clinical Procedures",
          "status": "in_progress",
          "progress": 45,
          "last_accessed": "2024-03-10T09:15:00Z"
        }
      ]
    }
  ],
  "documents_pending": 1,
  "payment_status": "paid"
}
```

#### 6.3.3 Enrollment Endpoints

**POST /enrollments** - Create enrollment
```http
POST /enrollments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "program_id": "program_uuid",
  "enrollment_date": "2024-03-15",
  "payment_status": "pending"
}

Response 201:
{
  "id": "enrollment_uuid",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "program_id": "program_uuid",
  "enrollment_date": "2024-03-15",
  "status": "active",
  "payment_status": "pending",
  "created_at": "2024-03-15T10:00:00Z"
}
```

#### 6.3.4 Document & E-Signature Endpoints

**POST /documents** - Create signed document from template
```http
POST /documents
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "template_id": "template_uuid",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "enrollment_id": "enrollment_uuid",
  "document_data": {
    "student_name": "John Doe",
    "program_name": "Medical Assistant Program",
    "tuition": "15000",
    "start_date": "2024-03-15"
  }
}

Response 201:
{
  "id": "document_uuid",
  "template_id": "template_uuid",
  "status": "created",
  "signing_token": "secure_random_token_32chars",
  "token_expires_at": "2024-03-22T10:00:00Z",
  "sign_url": "https://student-portal.aada.edu/sign/secure_random_token_32chars"
}
```

**GET /sign/{token}** - Public signing page (no auth required)
```http
GET /sign/secure_random_token_32chars

Response 200:
{
  "document": {
    "id": "document_uuid",
    "template_name": "Enrollment Agreement",
    "student_name": "John Doe",
    "program_name": "Medical Assistant Program",
    "document_data": {...},
    "pdf_url": "/api/documents/document_uuid/preview"
  },
  "requires_countersignature": true,
  "expires_at": "2024-03-22T10:00:00Z"
}
```

**POST /sign/{token}** - Submit signature
```http
POST /sign/secure_random_token_32chars
Content-Type: application/json

{
  "signer_name": "John Doe",
  "signer_email": "student@example.com",
  "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "signature_type": "student"
}

Response 200:
{
  "message": "Document signed successfully",
  "document_id": "document_uuid",
  "status": "signed",
  "requires_countersignature": true
}
```

#### 6.3.5 Progress Tracking Endpoints

**PUT /progress/{module_id}** - Update module progress
```http
PUT /progress/module_uuid
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "progress_percentage": 75,
  "status": "in_progress",
  "state_data": {
    "current_slide": 15,
    "total_slides": 20,
    "quiz_answers": {...},
    "last_video_position": 245
  }
}

Response 200:
{
  "id": "progress_uuid",
  "enrollment_id": "enrollment_uuid",
  "module_id": "module_uuid",
  "status": "in_progress",
  "progress_percentage": 75,
  "last_accessed": "2024-03-15T14:30:00Z",
  "state_data": {...}
}
```

#### 6.3.6 Financial Endpoints

**POST /finance/refunds** - Request refund
```http
POST /finance/refunds
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "reason": "Student unable to continue due to medical reasons",
  "progress_at_withdrawal": 35
}

Response 201:
{
  "id": "refund_uuid",
  "enrollment_id": "enrollment_uuid",
  "refund_percentage": 70,
  "refund_amount": 10500.00,
  "status": "pending",
  "request_date": "2024-03-15",
  "approval_required": true
}
```

**GET /finance/ledger/{enrollment_id}** - Get financial ledger
```http
GET /finance/ledger/enrollment_uuid
Authorization: Bearer <access_token>

Response 200:
{
  "enrollment_id": "enrollment_uuid",
  "transactions": [
    {
      "id": "transaction_uuid",
      "transaction_type": "payment",
      "amount": 15000.00,
      "transaction_date": "2024-03-15",
      "payment_method": "credit_card",
      "reference_number": "PAY_123456"
    },
    {
      "id": "refund_uuid",
      "transaction_type": "refund",
      "amount": -10500.00,
      "transaction_date": "2024-04-01",
      "reference_number": "REFUND_789012"
    }
  ],
  "balance": 4500.00
}
```

#### 6.3.7 Audit Endpoints

**GET /audit** - Query audit logs (admin only)
```http
GET /audit?user_id=550e8400-e29b-41d4-a716-446655440000&start_date=2024-03-01&end_date=2024-03-31
Authorization: Bearer <access_token>

Response 200:
{
  "total": 1247,
  "logs": [
    {
      "id": "log_uuid",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "endpoint": "/students/dashboard",
      "method": "GET",
      "status_code": 200,
      "ip_address": "192.168.1.100",
      "phi_access": false,
      "created_at": "2024-03-15T14:30:00Z"
    },
    ...
  ]
}
```

**GET /audit/phi-access** - Query PHI access logs (admin only)
```http
GET /audit/phi-access?start_date=2024-03-01&end_date=2024-03-31
Authorization: Bearer <access_token>

Response 200:
{
  "total": 87,
  "logs": [
    {
      "id": "log_uuid",
      "user_id": "admin_uuid",
      "user_email": "admin@aada.edu",
      "endpoint": "/students",
      "method": "GET",
      "ip_address": "10.0.1.50",
      "phi_access": true,
      "created_at": "2024-03-15T10:15:00Z"
    },
    ...
  ]
}
```

### 6.4 API Error Handling

**Standard Error Response Format**:

```json
{
  "detail": "Human-readable error message",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Invalid email format"],
    "password": ["Password must contain uppercase letter"]
  },
  "request_id": "req_uuid",
  "timestamp": "2024-03-15T14:30:00Z"
}
```

**HTTP Status Codes**:

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 OK | Success | Successful GET, PUT, DELETE |
| 201 Created | Resource created | Successful POST |
| 400 Bad Request | Invalid input | Validation errors |
| 401 Unauthorized | Authentication required | Missing or invalid token |
| 403 Forbidden | Insufficient permissions | Authorization failure |
| 404 Not Found | Resource not found | Invalid ID or path |
| 409 Conflict | Duplicate resource | Email already exists, etc. |
| 422 Unprocessable Entity | Validation error | Pydantic validation failure |
| 429 Too Many Requests | Rate limit exceeded | Slow down |
| 500 Internal Server Error | Server error | Unhandled exception |

### 6.5 API Pagination

**Standard Pagination Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Pagination Response Format**:
```json
{
  "total": 156,
  "page": 1,
  "limit": 20,
  "pages": 8,
  "data": [...]
}
```

### 6.6 API Filtering & Sorting

**Filtering**:
- Query parameters for filtering: `?status=active&program_id=uuid`
- Date ranges: `?start_date=2024-01-01&end_date=2024-12-31`

**Sorting**:
- `?sort_by=created_at&order=desc`
- Default: Creation date descending

---

## 7. Integration Architecture

### 7.1 Email Integration

**Email Providers** (configurable via `EMAIL_PROVIDER`):

1. **Console** (Development)
   - Logs email to console
   - No external dependencies

2. **SendGrid** (Production)
   - API-based delivery
   - Configuration: `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`
   - Templates: Transactional emails

3. **Azure Communication Services (ACS)** (Azure-native)
   - Recommended for Azure deployments
   - Configuration: `ACS_CONNECTION_STRING`, `ACS_SENDER_EMAIL`
   - Lower latency in Azure regions

**Email Types**:
- Registration verification emails (30-min expiry)
- Document signing notifications
- Enrollment confirmations
- Payment receipts
- Refund notifications
- Administrative alerts

### 7.2 H5P Integration

**H5P Content Delivery**:
- Interactive learning content (quizzes, presentations, games)
- Content stored in `/backend/app/static/h5p/`
- Result tracking via xAPI statements
- Progress persistence

**H5P Libraries Used**:
- H5P.MultiChoice
- H5P.InteractiveVideo
- H5P.CoursePresentation
- And more (extensible)

### 7.3 Learning Standards Integration

**xAPI (Experience API / Tin Can)**:
- Standard for tracking learning experiences
- Statement format: Actor-Verb-Object
- Learning Record Store (LRS) built-in
- Compliance with ADL xAPI specification 1.0.3

**SCORM (Shareable Content Object Reference Model)**:
- Legacy SCORM 1.2 and 2004 support
- Runtime API for content communication
- CMI data model implementation

### 7.4 Payment Integration (Future)

**Payment Gateway Integration Points**:
- Stripe (recommended)
- Square
- Authorize.Net

**Current Implementation**:
- Manual payment recording
- Payment ledger tracking
- Refund workflow

### 7.5 Azure Cloud Integration

**Azure Services Used**:

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Azure App Service** | Backend hosting | Linux container, Python 3.11 |
| **Azure Static Web Apps** | Frontend hosting | React builds, CDN |
| **Azure PostgreSQL** | Database | Flexible Server, pgcrypto enabled |
| **Azure Blob Storage** | Document storage | Private containers, SAS tokens |
| **Azure Container Registry (ACR)** | Docker images | Private registry |
| **Azure Key Vault** | Secret management | Keys, connection strings |
| **Azure Application Insights** | Monitoring | Logs, metrics, traces |
| **Azure Communication Services** | Email delivery | Transactional emails |

**Deployment Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Front Door (CDN)                  │
│                    (Optional - for global)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────┐           ┌──────────────────┐
│ Azure Static     │           │ Azure App Service│
│ Web Apps         │           │ (Backend API)    │
│ - Student Portal │           │ - FastAPI        │
│ - Admin Portal   │           │ - Gunicorn       │
└──────────────────┘           └────────┬─────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │                             │
                         ▼                             ▼
              ┌──────────────────┐         ┌──────────────────┐
              │ Azure PostgreSQL │         │ Azure Blob       │
              │ Flexible Server  │         │ Storage          │
              │ - Primary DB     │         │ - Documents      │
              │ - Encrypted      │         │ - H5P Content    │
              └──────────────────┘         └──────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Azure Key Vault  │
              │ - Secrets        │
              │ - Encryption Keys│
              └──────────────────┘
```

---

## 8. Deployment Architecture

### 8.1 Development Environment

**Docker Compose Setup** (`docker-compose.yml`):

```yaml
services:
  # PostgreSQL Database
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: aada
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: aada_lms
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Backend API
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg2://aada:changeme@db:5432/aada_lms
      JWT_SECRET_KEY: dev_secret_key
      ENCRYPTION_KEY: dev_encryption_key_32_bytes_long
      EMAIL_PROVIDER: console
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Student Portal
  student_portal:
    build: ./student_portal
    volumes:
      - ./student_portal:/app
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
    command: npm run dev -- --host

  # Admin Portal
  admin_portal:
    build: ./admin_portal
    volumes:
      - ./admin_portal:/app
    ports:
      - "5174:5174"
    environment:
      VITE_API_URL: http://localhost:8000
    command: npm run dev -- --host
```

**Development Workflow**:
1. Clone repository
2. Create `.env` file from `.env.example`
3. Run `docker-compose up -d`
4. Access:
   - Backend API: http://localhost:8000
   - Student Portal: http://localhost:5173
   - Admin Portal: http://localhost:5174
   - API Docs: http://localhost:8000/docs

### 8.2 Production Deployment

**Azure Deployment Script** (`azure-deploy.sh`):

```bash
#!/bin/bash
# Full deployment automation script
# See /backend/AZURE_DEPLOYMENT.md for details

# 1. Build Docker images
docker build -t aadalms.azurecr.io/backend:latest -f backend/Dockerfile.prod backend/
docker build -t aadalms.azurecr.io/student-portal:latest student_portal/
docker build -t aadalms.azurecr.io/admin-portal:latest admin_portal/

# 2. Push to Azure Container Registry
az acr login --name aadalms
docker push aadalms.azurecr.io/backend:latest
docker push aadalms.azurecr.io/student-portal:latest
docker push aadalms.azurecr.io/admin-portal:latest

# 3. Deploy to Azure App Service
az webapp config container set \
  --name aada-lms-backend \
  --resource-group aada-lms-prod \
  --docker-custom-image-name aadalms.azurecr.io/backend:latest

# 4. Run database migrations
az webapp ssh --name aada-lms-backend --resource-group aada-lms-prod \
  --command "cd /app && alembic upgrade head"

# 5. Deploy frontends to Azure Static Web Apps
# (Handled by GitHub Actions on push to main)
```

**Production Environment Variables** (stored in Azure Key Vault):

```bash
# Database
DATABASE_URL=postgresql+psycopg2://user@host.postgres.database.azure.com:5432/aada_lms?sslmode=require
ENCRYPTION_KEY=<32-byte-random-key-from-key-vault>

# JWT
JWT_SECRET_KEY=<64-byte-urlsafe-random-key>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
EMAIL_PROVIDER=acs
ACS_CONNECTION_STRING=<azure-communication-services-connection-string>
ACS_SENDER_EMAIL=noreply@aada.edu

# CORS
ALLOWED_ORIGINS=https://student.aada.edu,https://admin.aada.edu

# URLs
BACKEND_BASE_URL=https://api.aada.edu
FRONTEND_BASE_URL=https://student.aada.edu
```

### 8.3 Scalability Considerations

**Horizontal Scaling**:
- Stateless backend (no server-side sessions)
- Connection pooling (SQLAlchemy)
- Redis for distributed rate limiting (upgrade path)
- Azure App Service scaling (manual or auto)

**Database Scaling**:
- PostgreSQL connection pooling
- Read replicas for reporting queries
- Partitioning for large tables (audit_logs)

**CDN & Caching**:
- Azure Front Door for global CDN
- Browser caching for static assets
- API response caching (future)

### 8.4 Backup & Disaster Recovery

**Database Backups**:
- Automated daily backups (Azure PostgreSQL)
- Point-in-time restore (7 days)
- Geo-redundant backups (cross-region)

**Document Backups**:
- Azure Blob Storage geo-replication
- Versioning enabled
- Soft delete (30-day retention)

**Application Backups**:
- Docker images in ACR
- Git repository (GitHub)
- Infrastructure as Code (ARM templates)

**Recovery Time Objective (RTO)**: 4 hours
**Recovery Point Objective (RPO)**: 1 hour

---

## 9. Quality Attributes

### 9.1 Security

**Measures**:
- Encryption at rest (AES-256) and in transit (TLS 1.2+)
- Strong authentication (bcrypt, JWT, refresh tokens)
- Role-based access control (RBAC)
- Comprehensive audit logging
- Input validation and sanitization
- File upload security (7 layers)
- Rate limiting
- Security headers
- Regular security updates

**Compliance**:
- HIPAA compliant (PHI encryption, audit logs)
- NIST SP 800-63B password standards
- FERPA compliant (student records protection)
- SOC 2 Type II ready

### 9.2 Reliability

**Measures**:
- Database transactions (ACID compliance)
- Error handling and logging
- Health checks and monitoring
- Automatic retries for transient failures
- Connection pooling
- Circuit breakers (future)

**Availability Target**: 99.9% uptime (8.76 hours downtime/year)

### 9.3 Performance

**Measures**:
- Database indexing (optimized queries)
- Connection pooling
- Lazy loading (relationships)
- Pagination (limit large result sets)
- CDN for static assets
- Caching strategy (future: Redis)

**Performance Targets**:
- API response time: < 200ms (p95)
- Page load time: < 2 seconds
- Database query time: < 50ms (p95)

### 9.4 Scalability

**Measures**:
- Stateless architecture
- Horizontal scaling capability
- Database connection pooling
- Load balancing (Azure App Service)
- Microservices-ready architecture

**Capacity Targets**:
- 10,000 concurrent users
- 1,000,000 total students
- 100 requests/second per instance

### 9.5 Maintainability

**Measures**:
- Clear code organization
- Comprehensive documentation
- Type hints (Python, TypeScript)
- Linting and formatting (Black, ESLint)
- Unit and integration tests
- CI/CD pipeline
- Database migrations (Alembic)

**Code Quality Metrics**:
- Test coverage: > 80%
- Documentation coverage: 100% (public APIs)
- Code complexity: < 10 (cyclomatic complexity)

### 9.6 Usability

**Measures**:
- Intuitive UI/UX
- Responsive design (mobile-friendly)
- Accessibility (WCAG 2.1 Level AA)
- Clear error messages
- User feedback mechanisms
- Help documentation

---

## 10. Technology Stack

### 10.1 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | 0.104+ | Web framework |
| **SQLAlchemy** | 2.0+ | ORM |
| **Alembic** | 1.12+ | Database migrations |
| **Pydantic** | 2.0+ | Data validation |
| **PostgreSQL** | 16 | Database |
| **pgcrypto** | - | Encryption extension |
| **bcrypt** | 4.0+ | Password hashing |
| **PyJWT** | 2.8+ | JWT tokens |
| **python-multipart** | 0.0.6+ | File uploads |
| **ReportLab** | 4.0+ | PDF generation |
| **Pillow** | 10.0+ | Image processing |
| **SendGrid** | 6.10+ | Email delivery |
| **Azure SDK** | - | Azure integration |
| **Uvicorn** | 0.24+ | ASGI server |
| **Gunicorn** | 21.2+ | Production server |

### 10.2 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2+ | UI framework |
| **TypeScript** | 5.0+ | Type safety |
| **Vite** | 4.5+ | Build tool |
| **Axios** | 1.6+ | HTTP client |
| **React Router** | 6.18+ | Routing |
| **React Hook Form** | 7.48+ | Form handling |
| **Material-UI (MUI)** | 5.14+ | Component library (Admin) |
| **Tailwind CSS** | 3.3+ | Utility CSS (Student) |
| **Signature Pad** | 4.1+ | E-signature capture |

### 10.3 Infrastructure

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Local development |
| **Azure App Service** | Backend hosting |
| **Azure Static Web Apps** | Frontend hosting |
| **Azure PostgreSQL** | Managed database |
| **Azure Blob Storage** | Document storage |
| **Azure Container Registry** | Docker registry |
| **Azure Key Vault** | Secret management |
| **GitHub Actions** | CI/CD |

### 10.4 Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **Pytest** | Backend testing |
| **Vitest** | Frontend testing |
| **Black** | Python code formatting |
| **Ruff** | Python linting |
| **ESLint** | TypeScript linting |
| **Prettier** | Code formatting |

---

## 11. Appendices

### 11.1 Glossary

| Term | Definition |
|------|------------|
| **PHI** | Protected Health Information - personally identifiable health data covered by HIPAA |
| **RBAC** | Role-Based Access Control - authorization based on user roles |
| **JWT** | JSON Web Token - stateless authentication token |
| **xAPI** | Experience API (Tin Can) - learning activity tracking standard |
| **SCORM** | Shareable Content Object Reference Model - e-learning standard |
| **H5P** | HTML5 Package - interactive content creation framework |
| **LRS** | Learning Record Store - repository for xAPI statements |
| **pgcrypto** | PostgreSQL extension for encryption functions |
| **CORS** | Cross-Origin Resource Sharing - browser security mechanism |
| **HSTS** | HTTP Strict Transport Security - force HTTPS |
| **CSP** | Content Security Policy - XSS protection |

### 11.2 References

- HIPAA Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/
- NIST SP 800-63B Digital Identity Guidelines: https://pages.nist.gov/800-63-3/sp800-63b.html
- FERPA Requirements: https://www2.ed.gov/policy/gen/guid/fpco/ferpa/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- xAPI Specification: https://github.com/adlnet/xAPI-Spec
- Azure App Service: https://docs.microsoft.com/en-us/azure/app-service/

### 11.3 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | AADA Dev Team | Initial version |
| 2.0 | 2024-11-14 | Claude Code | Comprehensive update post-codebase review |

### 11.4 Contact Information

**Technical Support**: support@aada.edu
**Security Issues**: security@aada.edu
**Compliance**: compliance@aada.edu

---

**END OF DOCUMENT**
