# AADA LMS - Systems Integration Specification
**Version:** 2.0
**Date:** November 5, 2025
**Status:** Active Development - RBAC Phase Complete

---

## Executive Summary

The American Academy of Dental Assisting (AADA) Learning Management System (LMS) is a comprehensive educational platform designed for dental assistant training programs. This document specifies the technical architecture, data models, API endpoints, security implementation, and integration points for the system.

**Recent Updates:**
- ✅ Complete RBAC implementation with 6 distinct roles
- ✅ All roles standardized to lowercase
- ✅ Comprehensive test suite for role permissions
- ✅ Test accounts created for all roles
- ✅ Staff role hierarchy implemented

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [API Endpoints](#api-endpoints)
6. [Security & Compliance](#security--compliance)
7. [Authentication & Authorization](#authentication--authorization)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Architecture](#deployment-architecture)
10. [Integration Points](#integration-points)

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

**Student Portal (`frontend/aada_web/`)**
- Course enrollment and progress tracking
- H5P interactive content delivery
- Module completion tracking
- Personal transcript access

**Backend API (`backend/`)**
- RESTful API endpoints
- Business logic processing
- RBAC enforcement
- Data validation
- Audit logging

---

## Technology Stack

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18.3.1 | UI components |
| Build Tool | Vite | 5.4.11 | Development & build |
| Routing | React Router | 7.0.1 | Client-side routing |
| HTTP Client | Axios | 1.7.7 | API communication |
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

#### `programs` Table
```sql
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    credential_level TEXT CHECK (credential_level IN ('certificate', 'diploma', 'degree')),
    total_clock_hours INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `modules` Table
```sql
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    delivery_type TEXT CHECK (delivery_type IN ('online', 'in_person', 'hybrid', 'externship')),
    clock_hours INTEGER NOT NULL,
    requires_in_person BOOLEAN DEFAULT FALSE,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (program_id, code)
);
```

#### `enrollments` Table
```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    expected_end_date DATE,
    actual_end_date DATE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'withdrawn', 'suspended')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Compliance Schema Tables

#### `compliance.attendance_logs` Table
```sql
CREATE TABLE compliance.attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    session_type TEXT CHECK (session_type IN ('live', 'lab', 'externship')),
    session_ref TEXT,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `compliance.credentials` Table
```sql
CREATE TABLE compliance.credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    credential_type TEXT NOT NULL,
    issued_at TIMESTAMP NOT NULL,
    cert_serial TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `compliance.transcripts` Table
```sql
CREATE TABLE compliance.transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    gpa DECIMAL(3, 2),
    generated_at TIMESTAMP NOT NULL,
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `compliance.financial_ledgers` Table
```sql
CREATE TABLE compliance.financial_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    line_type TEXT CHECK (line_type IN ('tuition', 'fee', 'payment', 'refund', 'adjustment')),
    amount_cents BIGINT NOT NULL, -- Store as cents to avoid floating point issues
    description TEXT,
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

**Use Cases:**
- System configuration
- User account management
- Emergency data access
- System-wide reporting

#### 2. **staff** (Administrative Staff)
**Permissions:**
- ✅ All instructor permissions
- ✅ Create/update/delete student accounts
- ✅ Manage enrollments
- ✅ View all student data
- ✅ Generate compliance reports
- ❌ Cannot delete programs/modules (admin only)

**Use Cases:**
- Student enrollment processing
- Academic advising
- Student record management
- Compliance tracking

#### 3. **instructor** (Course Instructor)
**Permissions:**
- ✅ Create/update programs and modules
- ✅ View all student progress in assigned modules
- ✅ Manage attendance records
- ✅ Approve skill checkoffs
- ❌ Cannot create/delete student accounts
- ❌ Cannot delete programs/modules (admin only)

**Use Cases:**
- Course content management
- Student progress monitoring
- Skill assessment
- Attendance tracking

#### 4. **finance** (Finance Staff)
**Permissions:**
- ✅ View/manage financial ledgers
- ✅ Process payments and refunds
- ✅ View student enrollment financial data
- ✅ Generate financial reports
- ❌ Cannot create/update programs
- ❌ Cannot manage student accounts

**Use Cases:**
- Payment processing
- Refund management
- Financial reporting
- Tuition tracking

#### 5. **registrar** (Registrar Office)
**Permissions:**
- ✅ Manage student enrollment records
- ✅ Issue credentials and transcripts
- ✅ View compliance reports
- ✅ Manage withdrawals
- ❌ Cannot create/update programs
- ❌ Cannot manage financial records

**Use Cases:**
- Transcript generation
- Credential issuance
- Enrollment verification
- Academic record management

#### 6. **student** (Enrolled Student)
**Permissions:**
- ✅ View own enrolled courses
- ✅ Access course content (H5P modules)
- ✅ View own progress and grades
- ✅ View own transcript
- ❌ Cannot view other students' data
- ❌ Cannot manage programs or users

**Use Cases:**
- Course access
- Progress tracking
- Transcript viewing
- Module completion

### Test Accounts

All test accounts are documented in `/TEST_CREDENTIALS.md`:

| Role | Email | Password |
|------|-------|----------|
| admin | admin@aada.edu | AdminPass!23 |
| staff | staff@aada.edu | StaffPass!23 |
| instructor | instructor@aada.edu | InstructorPass!23 |
| finance | finance@aada.edu | FinancePass!23 |
| registrar | registrar@aada.edu | RegistrarPass!23 |
| student | alice.student@aada.edu | AlicePass!23 |
| student | bob.student@aada.edu | BobLearner!23 |

---

## API Endpoints

### Base URL
```
Development: http://localhost:8000
Production: https://api.aada.edu
```

### Authentication Endpoints

#### POST `/api/auth/login`
**Purpose:** Authenticate user and receive JWT tokens

**Request:**
```json
{
  "email": "admin@aada.edu",
  "password": "AdminPass!23"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Sets Cookies:**
- `access_token` (httpOnly, secure, 15 min)
- `refresh_token` (httpOnly, secure, 7 days)

#### POST `/api/auth/refresh`
**Purpose:** Refresh access token using refresh token

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### GET `/api/auth/me`
**Purpose:** Get current authenticated user details

**Response:**
```json
{
  "id": "uuid-here",
  "email": "admin@aada.edu",
  "first_name": "Ada",
  "last_name": "Administrator",
  "roles": ["admin"],
  "status": "active"
}
```

### Program & Module Endpoints

#### GET `/api/programs`
**Purpose:** List all programs (public endpoint)

**Response:**
```json
[
  {
    "id": "uuid",
    "code": "MA-2025",
    "name": "Medical Assistant Diploma",
    "credential_level": "certificate",
    "total_clock_hours": 480,
    "created_at": "2025-11-05T10:00:00Z"
  }
]
```

#### POST `/api/programs`
**Purpose:** Create new program

**Required Roles:** `admin`, `staff`, `instructor`

**Request:**
```json
{
  "code": "MA-2025",
  "name": "Medical Assistant Diploma",
  "credential_level": "certificate",
  "total_clock_hours": 480
}
```

#### DELETE `/api/programs/{program_id}`
**Purpose:** Delete program

**Required Roles:** `admin` only

#### GET `/api/programs/{program_id}/modules`
**Purpose:** List modules for a program

**Response:**
```json
[
  {
    "id": "uuid",
    "program_id": "uuid",
    "code": "MA-101",
    "title": "Orientation & Professional Foundations",
    "delivery_type": "hybrid",
    "clock_hours": 120,
    "requires_in_person": true,
    "position": 1
  }
]
```

### User Management Endpoints

#### GET `/api/users`
**Purpose:** List all users

**Required Roles:** `admin`, `staff`, `registrar`, `instructor`, `finance`

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "alice.student@aada.edu",
    "first_name": "Alice",
    "last_name": "Student",
    "roles": ["student"],
    "status": "active"
  }
]
```

#### POST `/api/users`
**Purpose:** Create new user

**Required Roles:** `admin`, `staff`

### Enrollment Endpoints

#### GET `/api/enrollments`
**Purpose:** List enrollments (filtered by role)

**Query Parameters:**
- `user_id`: Filter by user (staff can view any, students can only view own)

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "program_id": "uuid",
    "start_date": "2025-09-01",
    "expected_end_date": "2026-06-30",
    "status": "active"
  }
]
```

### Compliance Endpoints

#### GET `/api/transcripts`
**Purpose:** View transcripts

**Required Roles:** `admin`, `staff`, `registrar` (all), `student` (own only)

#### GET `/api/credentials`
**Purpose:** View credentials

**Required Roles:** `admin`, `staff`, `registrar` (all), `student` (own only)

#### GET `/api/finance/ledgers`
**Purpose:** View financial ledgers

**Required Roles:** `admin`, `staff`, `finance`

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

**Logged Information:**
- Timestamp
- User ID and email
- Endpoint accessed
- HTTP method
- IP address
- User agent

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

### RBAC Enforcement

**Implementation:** `app/core/rbac.py`

```python
from app.core.rbac import RBACChecker

# In endpoint handler:
rbac = RBACChecker(current_user)

if not rbac.is_staff():
    raise HTTPException(status_code=403, detail="Staff access required")

if not rbac.can_access(resource_user_id):
    raise HTTPException(status_code=403, detail="Access denied")
```

**Helper Functions:**
- `require_admin()` - Dependency for admin-only endpoints
- `require_staff()` - Dependency for staff-only endpoints
- `require_roles([...])` - Dependency for specific roles
- `can_access_user_data(user_id, current_user)` - Check data access

---

## Testing Strategy

### Backend Testing

**Unit Tests** (`backend/app/tests/`)
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

**Run Tests:**
```bash
docker exec aada_lms-backend-1 sh -c "cd /code && python3 -m pytest app/tests/ -v"
```

### Frontend Testing

**Unit Tests** (Vitest)
- Component rendering
- User interactions
- State management
- API client mocking

**E2E Tests** (Playwright)
- Login flows
- Role-based navigation
- Form submissions
- Data validation

**Run Tests:**
```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e
```

### Test Data

**Database Seeding:**
```bash
docker exec aada_lms-backend-1 sh -c "cd /code && python3 -m app.db.seed"
```

**Creates:**
- 6 role definitions
- 14 test users (7 role-based + 7 generic students)
- 10 programs
- 30 modules
- 14 enrollments
- Sample compliance data

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
  "timestamp": "2025-11-05T14:30:00Z"
}
```

### Future Integration Points

**Planned:**
- ✅ Instructor assignment system (instructor→module→student)
- Payment gateway integration (Stripe/PayPal)
- Email notification system (SendGrid)
- Document storage (AWS S3)
- Video conferencing (Zoom API)
- SMS notifications (Twilio)

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

---

## Change Log

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

**Document Version:** 2.0
**Last Updated:** November 5, 2025
**Next Review:** December 5, 2025
