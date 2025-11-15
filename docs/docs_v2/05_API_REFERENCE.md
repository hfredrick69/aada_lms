# AADA LMS - API Reference Documentation

**Document Version:** 2.0
**Last Updated:** November 14, 2025
**API Version:** 1.0
**Classification:** Internal Use

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Authentication](#2-authentication)
3. [Core Endpoints](#3-core-endpoints)
4. [Student Management](#4-student-management)
5. [Academic Management](#5-academic-management)
6. [Document Management](#6-document-management)
7. [Financial Management](#7-financial-management)
8. [Compliance & Tracking](#8-compliance--tracking)
9. [CRM & Leads](#9-crm--leads)
10. [Learning Standards](#10-learning-standards)
11. [Error Handling](#11-error-handling)

---

## 1. API Overview

### 1.1 Base URLs

| Environment | Base URL |
|-------------|----------|
| **Development** | `http://localhost:8000` |
| **Staging** | `https://staging-api.aada.edu` |
| **Production** | `https://api.aada.edu` |

### 1.2 API Characteristics

- **Protocol**: HTTPS (TLS 1.2+)
- **Format**: JSON (Content-Type: application/json)
- **Authentication**: JWT Bearer Token
- **Rate Limiting**: Varies by endpoint
- **Versioning**: Path-based (future: `/api/v1/...`)

### 1.3 Common Headers

**Request Headers**:
```http
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
```

**Response Headers**:
```http
Content-Type: application/json
X-Request-ID: <request_uuid>
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699999999
```

### 1.4 HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 OK | Success | GET, PUT, DELETE successful |
| 201 Created | Resource created | POST successful |
| 204 No Content | Success, no response body | DELETE successful (alternative) |
| 400 Bad Request | Invalid input | Validation errors |
| 401 Unauthorized | Authentication required | Missing/invalid token |
| 403 Forbidden | Insufficient permissions | Authorization failure |
| 404 Not Found | Resource not found | Invalid ID or path |
| 409 Conflict | Duplicate resource | Email already exists |
| 422 Unprocessable Entity | Validation error | Pydantic validation failure |
| 429 Too Many Requests | Rate limit exceeded | Slow down requests |
| 500 Internal Server Error | Server error | Unhandled exception |

---

## 2. Authentication

### 2.1 Registration Flow

#### POST /auth/register/step1
**Description**: Initiate user registration

**Public Endpoint**: ✓ No authentication required

**Request**:
```http
POST /auth/register/step1
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "SecurePass123!@#",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response** (200 OK):
```json
{
  "message": "Verification email sent",
  "email": "student@example.com",
  "expires_in_minutes": 30
}
```

**Validation**:
- Email: Valid email format
- Password: Min 12 chars, uppercase, lowercase, digit, special char
- First/Last name: 1-100 characters

#### POST /auth/register/verify
**Description**: Complete registration with email verification token

**Public Endpoint**: ✓ No authentication required

**Request**:
```http
POST /auth/register/verify
Content-Type: application/json

{
  "token": "verification_token_from_email"
}
```

**Response** (200 OK):
```json
{
  "message": "Registration completed successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 2.2 Login

#### POST /auth/login
**Description**: Authenticate user and receive tokens

**Public Endpoint**: ✓ No authentication required

**Request**:
```http
POST /auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "SecurePass123!@#"
}
```

**Response** (200 OK):
```json
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
```

**Set-Cookie** (response header):
```
refresh_token=<token>; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Error Responses**:
- 401: Invalid credentials
- 403: Account locked (too many failed attempts)
- 403: Account not verified

### 2.3 Token Refresh

#### POST /auth/refresh
**Description**: Refresh access token using refresh token

**Public Endpoint**: ✓ No authentication required (uses refresh token)

**Request**:
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "8f3b7c2d1e5a9f6b4c8e2d7a1b5f3c9e"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses**:
- 401: Invalid or expired refresh token
- 401: Revoked refresh token

### 2.4 Logout

#### POST /auth/logout
**Description**: Revoke refresh token and logout

**Authentication**: Required (Bearer token)

**Request**:
```http
POST /auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "8f3b7c2d1e5a9f6b4c8e2d7a1b5f3c9e"
}
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## 3. Core Endpoints

### 3.1 Health Check

#### GET /
**Description**: API health check

**Public Endpoint**: ✓ No authentication required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-14T12:00:00Z"
}
```

### 3.2 API Documentation

#### GET /docs
**Description**: Interactive API documentation (Swagger UI)

**Public Endpoint**: ✓ No authentication required (development only)

**Response**: HTML (Swagger UI interface)

#### GET /redoc
**Description**: Alternative API documentation (ReDoc)

**Public Endpoint**: ✓ No authentication required (development only)

**Response**: HTML (ReDoc interface)

---

## 4. Student Management

### 4.1 List Students

#### GET /students
**Description**: List all students with pagination

**Authentication**: Required
**Roles**: admin, staff, registrar

**Query Parameters**:
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 20, max: 100): Items per page
- `status` (string, optional): Filter by status (active, inactive, withdrawn)
- `search` (string, optional): Search by name or email
- `sort_by` (string, default: created_at): Sort field
- `order` (string, default: desc): Sort order (asc, desc)

**Request**:
```http
GET /students?page=1&limit=20&status=active&search=john
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "total": 156,
  "page": 1,
  "limit": 20,
  "pages": 8,
  "students": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "student@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "enrollment_count": 2,
      "created_at": "2024-01-15T10:30:00Z"
    },
    ...
  ]
}
```

### 4.2 Get Student

#### GET /students/{id}
**Description**: Get student details by ID

**Authentication**: Required
**Roles**: admin, staff, registrar, instructor, finance, student (self-only)

**Path Parameters**:
- `id` (UUID): Student ID

**Request**:
```http
GET /students/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": true,
  "roles": ["student"],
  "enrollments": [
    {
      "id": "enrollment_uuid",
      "program": {
        "id": "program_uuid",
        "name": "Medical Assistant Program"
      },
      "enrollment_date": "2024-01-15",
      "status": "active",
      "payment_status": "paid"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4.3 Student Dashboard

#### GET /students/{id}/dashboard
**Description**: Get student dashboard with progress, courses, and documents

**Authentication**: Required
**Roles**: student (self-only), admin, staff, registrar

**Request**:
```http
GET /students/550e8400-e29b-41d4-a716-446655440000/dashboard
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
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
        "duration_weeks": 36,
        "clock_hours": 720
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
          "last_accessed": "2024-03-10T09:15:00Z",
          "state_data": {
            "current_slide": 15,
            "total_slides": 20
          }
        }
      ]
    }
  ],
  "documents_pending": 1,
  "payment_status": "paid",
  "next_payment_due": null
}
```

---

## 5. Academic Management

### 5.1 List Programs

#### GET /programs
**Description**: List all academic programs

**Authentication**: Required
**Roles**: All authenticated users

**Query Parameters**:
- `is_active` (boolean, optional): Filter by active status
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 20): Items per page

**Request**:
```http
GET /programs?is_active=true
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "total": 15,
  "page": 1,
  "limit": 20,
  "programs": [
    {
      "id": "program_uuid",
      "name": "Medical Assistant Program",
      "description": "Comprehensive medical assistant training...",
      "duration_weeks": 36,
      "clock_hours": 720,
      "tuition": 15000.00,
      "is_active": true,
      "modules_count": 12,
      "created_at": "2023-01-01T00:00:00Z"
    },
    ...
  ]
}
```

### 5.2 Get Program

#### GET /programs/{id}
**Description**: Get program details with modules

**Authentication**: Required
**Roles**: All authenticated users

**Path Parameters**:
- `id` (UUID): Program ID

**Request**:
```http
GET /programs/program_uuid
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": "program_uuid",
  "name": "Medical Assistant Program",
  "description": "Comprehensive medical assistant training...",
  "duration_weeks": 36,
  "clock_hours": 720,
  "tuition": 15000.00,
  "is_active": true,
  "modules": [
    {
      "id": "module_uuid",
      "title": "Anatomy & Physiology",
      "description": "Introduction to human anatomy...",
      "order_index": 1,
      "content_type": "h5p",
      "clock_hours": 60.0,
      "is_required": true
    },
    ...
  ],
  "created_at": "2023-01-01T00:00:00Z"
}
```

### 5.3 Create Enrollment

#### POST /enrollments
**Description**: Enroll student in program

**Authentication**: Required
**Roles**: admin, staff, registrar

**Request**:
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
```

**Response** (201 Created):
```json
{
  "id": "enrollment_uuid",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "program_id": "program_uuid",
  "enrollment_date": "2024-03-15",
  "completion_date": null,
  "status": "active",
  "payment_status": "pending",
  "created_at": "2024-03-15T10:00:00Z"
}
```

### 5.4 Update Module Progress

#### PUT /progress/{module_id}
**Description**: Update student progress for a module

**Authentication**: Required
**Roles**: student (self-only), instructor, admin, staff

**Path Parameters**:
- `module_id` (UUID): Module ID

**Request**:
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
    "quiz_answers": {
      "q1": "A",
      "q2": "C"
    },
    "last_video_position": 245
  }
}
```

**Response** (200 OK):
```json
{
  "id": "progress_uuid",
  "enrollment_id": "enrollment_uuid",
  "module_id": "module_uuid",
  "status": "in_progress",
  "progress_percentage": 75,
  "last_accessed": "2024-03-15T14:30:00Z",
  "completed_at": null,
  "state_data": {
    "current_slide": 15,
    "total_slides": 20
  }
}
```

---

## 6. Document Management

### 6.1 Create Document from Template

#### POST /documents
**Description**: Create signed document instance from template

**Authentication**: Required
**Roles**: admin, staff, registrar

**Request**:
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
    "start_date": "2024-03-15",
    "school_official": "Jane Smith, Registrar"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "document_uuid",
  "template_id": "template_uuid",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "enrollment_id": "enrollment_uuid",
  "status": "created",
  "signing_token": "secure_random_token_32chars",
  "token_expires_at": "2024-03-22T10:00:00Z",
  "sign_url": "https://student-portal.aada.edu/sign/secure_random_token_32chars",
  "requires_countersignature": true,
  "created_at": "2024-03-15T10:00:00Z"
}
```

### 6.2 Public Document Signing (No Auth Required)

#### GET /sign/{token}
**Description**: Get document for public signing

**Public Endpoint**: ✓ No authentication required (token-based access)

**Path Parameters**:
- `token` (string): Signing token from document creation

**Request**:
```http
GET /sign/secure_random_token_32chars
```

**Response** (200 OK):
```json
{
  "document": {
    "id": "document_uuid",
    "template_name": "Enrollment Agreement",
    "student_name": "John Doe",
    "program_name": "Medical Assistant Program",
    "document_data": {
      "tuition": "15000",
      "start_date": "2024-03-15"
    },
    "pdf_url": "/api/documents/document_uuid/preview",
    "requires_countersignature": true
  },
  "expires_at": "2024-03-22T10:00:00Z"
}
```

#### POST /sign/{token}
**Description**: Submit signature for document

**Public Endpoint**: ✓ No authentication required (token-based access)

**Path Parameters**:
- `token` (string): Signing token from document creation

**Request**:
```http
POST /sign/secure_random_token_32chars
Content-Type: application/json

{
  "signer_name": "John Doe",
  "signer_email": "student@example.com",
  "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "signature_type": "student"
}
```

**Response** (200 OK):
```json
{
  "message": "Document signed successfully",
  "document_id": "document_uuid",
  "status": "signed",
  "requires_countersignature": true,
  "signature_id": "signature_uuid",
  "signed_at": "2024-03-15T10:30:00Z"
}
```

---

## 7. Financial Management

### 7.1 Record Payment

#### POST /payments
**Description**: Record payment for enrollment

**Authentication**: Required
**Roles**: admin, staff, finance, student (self-only)

**Request**:
```http
POST /payments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "amount": 15000.00,
  "payment_method": "credit_card",
  "transaction_date": "2024-03-15",
  "reference_number": "PAY_123456",
  "description": "Tuition payment - Medical Assistant Program"
}
```

**Response** (201 Created):
```json
{
  "id": "transaction_uuid",
  "enrollment_id": "enrollment_uuid",
  "transaction_type": "payment",
  "amount": 15000.00,
  "payment_method": "credit_card",
  "transaction_date": "2024-03-15",
  "reference_number": "PAY_123456",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-15T10:00:00Z"
}
```

### 7.2 Request Refund

#### POST /finance/refunds
**Description**: Request refund for enrollment

**Authentication**: Required
**Roles**: admin, staff, finance

**Request**:
```http
POST /finance/refunds
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "reason": "Student unable to continue due to medical reasons",
  "progress_at_withdrawal": 35
}
```

**Response** (201 Created):
```json
{
  "id": "refund_uuid",
  "enrollment_id": "enrollment_uuid",
  "reason": "Student unable to continue due to medical reasons",
  "refund_percentage": 70,
  "refund_amount": 10500.00,
  "progress_at_withdrawal": 35,
  "status": "pending",
  "request_date": "2024-03-15",
  "approval_required": true,
  "approval_date": null,
  "refund_date": null,
  "requested_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-03-15T10:00:00Z"
}
```

**Refund Calculation**:
- 0-15 days: 100% refund
- 16-30 days: 80% refund
- 31-45 days: 60% refund
- >45 days or >50% progress: 0% refund

### 7.3 Get Financial Ledger

#### GET /finance/ledger/{enrollment_id}
**Description**: Get financial ledger for enrollment

**Authentication**: Required
**Roles**: admin, staff, finance, student (self-only)

**Path Parameters**:
- `enrollment_id` (UUID): Enrollment ID

**Request**:
```http
GET /finance/ledger/enrollment_uuid
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "enrollment_id": "enrollment_uuid",
  "student_name": "John Doe",
  "program_name": "Medical Assistant Program",
  "tuition": 15000.00,
  "transactions": [
    {
      "id": "transaction_uuid",
      "transaction_type": "payment",
      "amount": 15000.00,
      "transaction_date": "2024-03-15",
      "payment_method": "credit_card",
      "reference_number": "PAY_123456",
      "description": "Tuition payment"
    },
    {
      "id": "refund_uuid",
      "transaction_type": "refund",
      "amount": -10500.00,
      "transaction_date": "2024-04-01",
      "reference_number": "REFUND_789012",
      "description": "Partial refund - withdrawal"
    }
  ],
  "balance": 4500.00,
  "payment_status": "refunded"
}
```

---

## 8. Compliance & Tracking

### 8.1 Record Attendance

#### POST /attendance
**Description**: Log attendance for enrollment

**Authentication**: Required
**Roles**: admin, staff, registrar, instructor

**Request**:
```http
POST /attendance
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "log_date": "2024-03-15",
  "clock_hours": 8.0,
  "activity_description": "Clinical skills practice session"
}
```

**Response** (201 Created):
```json
{
  "id": "attendance_uuid",
  "enrollment_id": "enrollment_uuid",
  "log_date": "2024-03-15",
  "clock_hours": 8.0,
  "activity_description": "Clinical skills practice session",
  "logged_by": "instructor_uuid",
  "created_at": "2024-03-15T10:00:00Z"
}
```

### 8.2 Record Skills Checkoff

#### POST /skills
**Description**: Record skills competency assessment

**Authentication**: Required
**Roles**: admin, staff, instructor

**Request**:
```http
POST /skills
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "skill_name": "Venipuncture",
  "skill_category": "Clinical Skills",
  "competency_level": "proficient",
  "assessment_date": "2024-03-15",
  "passed": true,
  "notes": "Demonstrated proper technique and safety protocols"
}
```

**Response** (201 Created):
```json
{
  "id": "skill_uuid",
  "enrollment_id": "enrollment_uuid",
  "skill_name": "Venipuncture",
  "skill_category": "Clinical Skills",
  "competency_level": "proficient",
  "assessment_date": "2024-03-15",
  "passed": true,
  "notes": "Demonstrated proper technique and safety protocols",
  "assessed_by": "instructor_uuid",
  "created_at": "2024-03-15T10:00:00Z"
}
```

### 8.3 Generate Transcript

#### POST /transcripts/generate
**Description**: Generate official transcript for enrollment

**Authentication**: Required
**Roles**: admin, staff, registrar

**Request**:
```http
POST /transcripts/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "enrollment_id": "enrollment_uuid",
  "is_official": true
}
```

**Response** (201 Created):
```json
{
  "id": "transcript_uuid",
  "enrollment_id": "enrollment_uuid",
  "transcript_data": {
    "student_name": "John Doe",
    "program_name": "Medical Assistant Program",
    "enrollment_date": "2024-01-15",
    "completion_date": "2024-12-20",
    "modules": [
      {
        "title": "Anatomy & Physiology",
        "clock_hours": 60.0,
        "grade": "A",
        "completed_date": "2024-02-20"
      },
      ...
    ]
  },
  "gpa": 3.85,
  "total_clock_hours": 720.0,
  "generated_date": "2024-12-21",
  "is_official": true,
  "pdf_path": "/documents/transcripts/transcript_uuid.pdf",
  "generated_by": "registrar_uuid",
  "created_at": "2024-12-21T10:00:00Z"
}
```

---

## 9. CRM & Leads

### 9.1 Create Lead

#### POST /leads
**Description**: Create new lead in CRM

**Authentication**: Required
**Roles**: admin, staff

**Request**:
```http
POST /leads
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567890",
  "source_id": "source_uuid",
  "program_interest": "program_uuid",
  "notes": "Interested in evening classes",
  "custom_fields": {
    "referral_source": "Google Ad",
    "preferred_start_date": "2024-06-01"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "lead_uuid",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567890",
  "source_id": "source_uuid",
  "status": "new",
  "lead_score": 50,
  "program_interest": "program_uuid",
  "notes": "Interested in evening classes",
  "custom_fields": {
    "referral_source": "Google Ad",
    "preferred_start_date": "2024-06-01"
  },
  "enrolled_user_id": null,
  "created_at": "2024-03-15T10:00:00Z"
}
```

### 9.2 Convert Lead to Student

#### POST /leads/{id}/convert
**Description**: Convert lead to enrolled student

**Authentication**: Required
**Roles**: admin, staff, registrar

**Path Parameters**:
- `id` (UUID): Lead ID

**Request**:
```http
POST /leads/lead_uuid/convert
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "program_id": "program_uuid",
  "enrollment_date": "2024-06-01",
  "create_user_account": true
}
```

**Response** (200 OK):
```json
{
  "message": "Lead converted to student successfully",
  "lead_id": "lead_uuid",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "enrollment_id": "enrollment_uuid",
  "status": "enrolled"
}
```

---

## 10. Learning Standards

### 10.1 Submit xAPI Statement

#### POST /xapi/statements
**Description**: Submit xAPI (Experience API) statement

**Authentication**: Required
**Roles**: student, instructor, admin

**Request**:
```http
POST /xapi/statements
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "actor": {
    "mbox": "mailto:student@example.com",
    "name": "John Doe"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": {"en-US": "completed"}
  },
  "object": {
    "id": "https://aada.edu/activities/module/anatomy",
    "objectType": "Activity",
    "definition": {
      "name": {"en-US": "Anatomy & Physiology Module"},
      "type": "http://adlnet.gov/expapi/activities/course"
    }
  },
  "result": {
    "completion": true,
    "success": true,
    "score": {
      "scaled": 0.95,
      "raw": 95,
      "min": 0,
      "max": 100
    },
    "duration": "PT2H30M"
  },
  "timestamp": "2024-03-15T14:30:00Z"
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "stored": "2024-03-15T14:30:05Z"
}
```

---

## 11. Error Handling

### 11.1 Error Response Format

**Standard Error Response**:
```json
{
  "detail": "Human-readable error message",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Invalid email format"],
    "password": ["Password must contain uppercase letter"]
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-03-15T14:30:00Z"
}
```

### 11.2 Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400, 422 | Input validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid access token |
| `ACCOUNT_LOCKED` | 403 | Account locked due to failed login attempts |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required role/permission |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource does not exist |
| `DUPLICATE_RESOURCE` | 409 | Resource already exists (e.g., email) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Unhandled server error |

### 11.3 Validation Error Example

**Request**:
```http
POST /auth/register/step1
Content-Type: application/json

{
  "email": "invalid-email",
  "password": "short",
  "first_name": "",
  "last_name": "Doe"
}
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["value is not a valid email address"],
    "password": [
      "Password must be at least 12 characters",
      "Password must contain at least one uppercase letter",
      "Password must contain at least one digit",
      "Password must contain at least one special character"
    ],
    "first_name": ["ensure this value has at least 1 characters"]
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-03-15T14:30:00Z"
}
```

---

**END OF DOCUMENT**

For complete API documentation with interactive testing, visit:
- Development: http://localhost:8000/docs
- Production: https://api.aada.edu/docs
