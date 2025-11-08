# AADA LMS - API Documentation

## Overview

The AADA LMS provides a RESTful API built with FastAPI. This document supplements the auto-generated OpenAPI documentation available at `/docs`.

**API Base URL**: 
- Development: `http://localhost:8000`
- Production: `https://api.aada.edu`

**Interactive Documentation**:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Authentication

### Login

**Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "email": "alice.student@aada.edu",
  "password": "AlicePass!23"
}
```

**Response**: `200 OK`
```json
{
  "message": "Login successful"
}
```

**Cookies Set**:
- `access_token` - JWT access token (httpOnly, secure, sameSite)
- `refresh_token` - JWT refresh token (httpOnly, secure, sameSite)

**Error Responses**:
- `401 Unauthorized` - Invalid credentials
- `422 Unprocessable Entity` - Validation error

### Logout

**Endpoint**: `POST /api/auth/logout`

**Response**: `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

**Effect**: Clears authentication cookies

### Refresh Token

**Endpoint**: `POST /api/auth/refresh`

**Request**: No body (uses refresh_token cookie)

**Response**: `200 OK` (sets new access_token cookie)

**Error**: `401 Unauthorized` - Invalid or expired refresh token

### Get Current User

**Endpoint**: `GET /api/auth/me`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 1,
  "email": "alice.student@aada.edu",
  "full_name": "Alice Student",
  "role": "student",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Users

### List Users

**Endpoint**: `GET /api/users/`

**Authentication**: Required (admin only)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "email": "alice.student@aada.edu",
    "full_name": "Alice Student",
    "role": "student",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "email": "bob.instructor@aada.edu",
    "full_name": "Bob Instructor",
    "role": "instructor",
    "created_at": "2024-01-20T14:00:00Z"
  }
]
```

### Get User by ID

**Endpoint**: `GET /api/users/{user_id}`

**Authentication**: Required (admin or own user_id)

**Response**: `200 OK`
```json
{
  "id": 1,
  "email": "alice.student@aada.edu",
  "full_name": "Alice Student",
  "role": "student",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Create User

**Endpoint**: `POST /api/users/`

**Authentication**: Required (admin only)

**Request**:
```json
{
  "email": "newstudent@aada.edu",
  "password": "SecurePass!23",
  "full_name": "New Student",
  "role": "student"
}
```

**Response**: `201 Created`
```json
{
  "id": 10,
  "email": "newstudent@aada.edu",
  "full_name": "New Student",
  "role": "student",
  "created_at": "2025-11-04T12:34:56Z"
}
```

### Update User

**Endpoint**: `PUT /api/users/{user_id}`

**Authentication**: Required (admin or own user_id)

**Request**:
```json
{
  "full_name": "Alice M. Student",
  "email": "alice.student@aada.edu"
}
```

**Response**: `200 OK` (returns updated user)

## Programs

### List Programs

**Endpoint**: `GET /api/programs/`

**Authentication**: Required

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Dental Assistant Professional",
    "description": "Comprehensive dental assistant training program...",
    "total_credits": 60.0,
    "duration_weeks": 52,
    "tuition_amount_cents": 1200000,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Get Program by ID

**Endpoint**: `GET /api/programs/{program_id}`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Dental Assistant Professional",
  "description": "Comprehensive dental assistant training program...",
  "total_credits": 60.0,
  "duration_weeks": 52,
  "tuition_amount_cents": 1200000,
  "modules": [
    {
      "id": 1,
      "name": "Module 1: Introduction to Dental Assisting",
      "order_num": 1,
      "description": "Foundational concepts..."
    }
  ]
}
```

## Modules

### List Modules

**Endpoint**: `GET /api/modules/?program_id={program_id}`

**Authentication**: Required

**Query Parameters**:
- `program_id` (optional) - Filter by program

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "program_id": 1,
    "name": "Module 1: Introduction to Dental Assisting",
    "order_num": 1,
    "description": "Foundational concepts and terminology",
    "lessons": [
      {
        "id": 1,
        "title": "Welcome to AADA",
        "content_type": "h5p",
        "content_url": "/static/modules/module1/M1_H5P_WelcomeCarousel",
        "order_num": 1
      }
    ]
  }
]
```

### Get Module by ID

**Endpoint**: `GET /api/modules/{module_id}`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": 1,
  "program_id": 1,
  "name": "Module 1: Introduction to Dental Assisting",
  "order_num": 1,
  "description": "Foundational concepts and terminology",
  "lessons": [
    {
      "id": 1,
      "title": "Welcome to AADA",
      "content_type": "h5p",
      "content_url": "/static/modules/module1/M1_H5P_WelcomeCarousel",
      "order_num": 1
    },
    {
      "id": 2,
      "title": "Ethics in Dental Practice",
      "content_type": "h5p",
      "content_url": "/static/modules/module1/M1_H5P_EthicsBranching",
      "order_num": 2
    }
  ]
}
```

## Enrollments

### List Enrollments

**Endpoint**: `GET /api/enrollments/`

**Authentication**: Required (students see own, admins see all)

**Query Parameters**:
- `user_id` (optional) - Filter by user
- `program_id` (optional) - Filter by program
- `status` (optional) - Filter by status (active, completed, withdrawn)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "program_id": 1,
    "status": "active",
    "enrolled_at": "2024-01-15",
    "completed_at": null,
    "progress_pct": 45
  }
]
```

### Create Enrollment

**Endpoint**: `POST /api/enrollments/`

**Authentication**: Required (admin only)

**Request**:
```json
{
  "user_id": 1,
  "program_id": 1,
  "enrolled_at": "2024-01-15"
}
```

**Response**: `201 Created`
```json
{
  "id": 5,
  "user_id": 1,
  "program_id": 1,
  "status": "active",
  "enrolled_at": "2024-01-15",
  "progress_pct": 0
}
```

## Attendance

### List Attendance Records

**Endpoint**: `GET /api/attendance/`

**Authentication**: Required (students see own, admins see all)

**Query Parameters**:
- `user_id` (optional)
- `enrollment_id` (optional)
- `start_date` (optional) - ISO date string
- `end_date` (optional) - ISO date string

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "enrollment_id": 1,
    "clock_in": "2024-11-04T09:00:00Z",
    "clock_out": "2024-11-04T11:30:00Z",
    "total_minutes": 150,
    "notes": "Module 1 study session"
  }
]
```

### Create Attendance Record

**Endpoint**: `POST /api/attendance/`

**Authentication**: Required

**Request**:
```json
{
  "enrollment_id": 1,
  "clock_in": "2024-11-04T09:00:00Z",
  "clock_out": "2024-11-04T11:30:00Z",
  "notes": "Module 1 study session"
}
```

**Response**: `201 Created` (returns created record)

## Transcripts

### List Transcripts

**Endpoint**: `GET /api/transcripts/`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "program_id": 1,
    "gpa": 3.85,
    "total_credits": 60.0,
    "generated_at": "2024-12-15T10:00:00Z",
    "pdf_url": "/static/transcripts/transcript_001.pdf"
  }
]
```

### Generate Transcript

**Endpoint**: `POST /api/transcripts/`

**Authentication**: Required (admin only)

**Request**:
```json
{
  "user_id": 1,
  "program_id": 1
}
```

**Response**: `201 Created`
```json
{
  "id": 5,
  "user_id": 1,
  "program_id": 1,
  "gpa": 3.85,
  "total_credits": 60.0,
  "generated_at": "2025-11-04T12:34:56Z",
  "pdf_url": "/static/transcripts/transcript_005.pdf"
}
```

## Credentials

### List Credentials

**Endpoint**: `GET /api/credentials/`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "program_id": 1,
    "credential_type": "Dental Assistant Certification",
    "cert_serial": "DAC-2024-001",
    "issued_at": "2024-05-15",
    "created_at": "2024-05-15T14:00:00Z"
  }
]
```

### Create Credential

**Endpoint**: `POST /api/credentials/`

**Authentication**: Required

**Request**:
```json
{
  "user_id": 1,
  "program_id": 1,
  "credential_type": "CPR Certification",
  "cert_serial": "CPR-2024-123",
  "issued_at": "2024-08-20"
}
```

**Response**: `201 Created` (returns created credential)

## Externships

### List Externships

**Endpoint**: `GET /api/externships/`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "site_name": "Community Dental Clinic",
    "site_address": "123 Main St, Atlanta, GA 30301",
    "supervisor_name": "Dr. Jane Smith",
    "supervisor_email": "jsmith@communitydental.org",
    "total_hours": 120,
    "verified": true,
    "verified_at": "2024-09-01T10:00:00Z",
    "verification_doc_url": "/static/externships/verification_001.pdf"
  }
]
```

### Create Externship

**Endpoint**: `POST /api/externships/`

**Authentication**: Required

**Request**:
```json
{
  "user_id": 1,
  "site_name": "Community Dental Clinic",
  "site_address": "123 Main St, Atlanta, GA 30301",
  "supervisor_name": "Dr. Jane Smith",
  "supervisor_email": "jsmith@communitydental.org",
  "total_hours": 120
}
```

**Response**: `201 Created` (returns created externship)

### Verify Externship

**Endpoint**: `PUT /api/externships/{externship_id}/verify`

**Authentication**: Required (admin only)

**Response**: `200 OK`
```json
{
  "id": 1,
  "verified": true,
  "verified_at": "2025-11-04T12:34:56Z"
}
```

## Finance

### List Withdrawals

**Endpoint**: `GET /api/finance/withdrawals`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "enrollment_id": 1,
    "requested_at": "2024-10-01T14:00:00Z",
    "progress_pct_at_withdrawal": 35,
    "reason": "Medical reasons",
    "admin_processed_at": "2024-10-05T10:00:00Z"
  }
]
```

### List Refunds

**Endpoint**: `GET /api/finance/refunds`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "withdrawal_id": 1,
    "amount_cents": 600000,
    "policy_basis": "50% refund per GNPEC policy (< 40% completion)",
    "approved_at": "2024-10-05T10:00:00Z",
    "remitted_at": "2024-10-10T09:00:00Z"
  }
]
```

## Documents & E-Signatures

### List Document Templates

**Endpoint**: `GET /api/documents/templates`

**Authentication**: Required

**Query Parameters**:
- `active_only` (optional, default: true) - Show only active templates

**Response**: `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Enrollment Agreement",
    "version": "2024.1",
    "description": "Standard enrollment agreement for all programs",
    "requires_counter_signature": true,
    "is_active": true,
    "file_path": "/app/static/documents/templates/550e8400-e29b-41d4-a716-446655440000_enrollment.pdf",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### Get Document Template

**Endpoint**: `GET /api/documents/templates/{template_id}`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Enrollment Agreement",
  "version": "2024.1",
  "description": "Standard enrollment agreement for all programs",
  "requires_counter_signature": true,
  "is_active": true,
  "file_path": "/app/static/documents/templates/550e8400-e29b-41d4-a716-446655440000_enrollment.pdf",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Create Document Template

**Endpoint**: `POST /api/documents/templates`

**Authentication**: Required (admin only)

**Content-Type**: `multipart/form-data`

**Form Fields**:
- `name` (string, required) - Template name
- `version` (string, required) - Version identifier
- `description` (string, optional) - Template description
- `requires_counter_signature` (boolean, default: false) - Requires counter-signature
- `file` (file, required) - PDF file (max 10MB)

**Security Validation** (multi-layered):
1. **Extension check** - Only `.pdf` allowed
2. **Size limit** - 10MB maximum
3. **Magic bytes** - Verifies file starts with `%PDF-`
4. **PDF structure** - PyPDF2 validates PDF integrity (pages, metadata, readability)
5. **Duplicate check** - Rejects same name+version

**Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Enrollment Agreement",
  "version": "2024.1",
  "description": "Standard enrollment agreement for all programs",
  "requires_counter_signature": true,
  "is_active": true,
  "file_path": "/app/static/documents/templates/550e8400-e29b-41d4-a716-446655440000_enrollment.pdf",
  "created_at": "2025-11-04T12:34:56Z"
}
```

**Error Responses**:
- `400 Bad Request` - Duplicate template, invalid PDF, or file too large
- `422 Unprocessable Entity` - Validation error

### Toggle Template Active Status

**Endpoint**: `PATCH /api/documents/templates/{template_id}/toggle-active`

**Authentication**: Required (admin only)

**Description**: Soft delete/restore a template (toggles is_active flag)

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Enrollment Agreement",
  "version": "2024.1",
  "is_active": false
}
```

### Delete Document Template

**Endpoint**: `DELETE /api/documents/templates/{template_id}`

**Authentication**: Required (admin only)

**Description**: Permanently delete a template (hard delete). Protected - cannot delete templates referenced by signed documents.

**Response**: `200 OK`
```json
{
  "message": "Template deleted successfully"
}
```

**Error Responses**:
- `400 Bad Request` - Template is in use (referenced by signed documents)
- `404 Not Found` - Template not found

### Upload Student Document

**Endpoint**: `POST /api/documents/upload`

**Authentication**: Required (students and admins)

**Content-Type**: `multipart/form-data`

**Description**: Upload student documents (ID, transcripts, certifications, etc.)

**Form Fields**:
- `document_type` (string, required) - Type of document (e.g., "identification", "transcript", "certification")
- `file` (file, required) - PDF, PNG, JPG, or JPEG file (max 10MB)
- `description` (string, optional) - Document description

**Security Validation** (multi-layered):
1. **Extension check** - `.pdf`, `.png`, `.jpg`, `.jpeg` only
2. **Size limit** - 10MB maximum
3. **Magic bytes** - Verifies file type matches extension
4. **Structure validation**:
   - **PDFs**: PyPDF2 validates PDF integrity
   - **Images**: Pillow validates image structure, format, and dimensions

**Response**: `200 OK`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "document_type": "identification",
  "filename": "drivers_license.jpg",
  "file_type": "image",
  "file_path": "documents/student_uploads/1/770e8400-e29b-41d4-a716-446655440003_identification.jpg",
  "size_bytes": 245678,
  "uploaded_at": "2025-11-08T14:30:00Z",
  "uploaded_by": 1
}
```

**Error Responses**:
- `400 Bad Request` - Invalid file type, corrupted file, or file too large
- `422 Unprocessable Entity` - Validation error

**Supported File Types**:
- **PDF** - Enrollment documents, transcripts, certifications
- **PNG** - Screenshots, ID cards, certificates
- **JPG/JPEG** - Photos, scanned documents, ID cards

### Send Document

**Endpoint**: `POST /api/documents/send`

**Authentication**: Required (admin only)

**Description**: Send a document to a user or lead for signing

**Request** (to user):
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1
}
```

**Request** (to lead):
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "lead_id": 2
}
```

**Response**: `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "lead_id": null,
  "status": "sent",
  "signing_token": "abc123...",
  "sent_at": "2025-11-04T12:34:56Z",
  "public_signing_url": "http://localhost:8000/api/public/sign/abc123..."
}
```

### Get User Documents

**Endpoint**: `GET /api/documents/user/{user_id}`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK`
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "template_id": "550e8400-e29b-41d4-a716-446655440000",
    "template_name": "Enrollment Agreement",
    "user_id": 1,
    "status": "signed",
    "sent_at": "2024-11-01T10:00:00Z",
    "signed_at": "2024-11-01T14:30:00Z"
  }
]
```

### Get Lead Documents

**Endpoint**: `GET /api/documents/lead/{lead_id}`

**Authentication**: Required (admin only)

**Response**: `200 OK`
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "template_id": "550e8400-e29b-41d4-a716-446655440000",
    "template_name": "Enrollment Agreement",
    "lead_id": 2,
    "status": "sent",
    "sent_at": "2024-11-04T10:00:00Z"
  }
]
```

### Get Document Audit Trail

**Endpoint**: `GET /api/documents/{document_id}/audit-trail`

**Authentication**: Required (students see own, admins see all)

**Description**: Get complete audit trail for a document (ESIGN Act compliance)

**Response**: `200 OK`
```json
{
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "audit_logs": [
    {
      "id": 1,
      "event_type": "sent",
      "occurred_at": "2024-11-01T10:00:00Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "event_details": "{\"recipient_email\": \"alice.student@aada.edu\"}"
    },
    {
      "id": 2,
      "event_type": "viewed",
      "occurred_at": "2024-11-01T14:15:00Z",
      "ip_address": "192.168.1.101",
      "user_agent": "Mozilla/5.0...",
      "event_details": null
    },
    {
      "id": 3,
      "event_type": "document_signed",
      "occurred_at": "2024-11-01T14:30:00Z",
      "ip_address": "192.168.1.101",
      "user_agent": "Mozilla/5.0...",
      "event_details": "{\"signature_text\": \"Alice Student\", \"consent_given\": true}"
    }
  ]
}
```

### Download Document

**Endpoint**: `GET /api/documents/{document_id}/download`

**Authentication**: Required (students see own, admins see all)

**Response**: `200 OK` (binary PDF file)
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="enrollment-agreement.pdf"`

### Public Signing Endpoint

**Endpoint**: `GET /api/public/sign/{token}`

**Authentication**: Not required (uses one-time token)

**Description**: Public endpoint for document signing via unique token

**Response**: `200 OK`
```json
{
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "template_name": "Enrollment Agreement",
  "recipient_email": "alice.student@aada.edu",
  "requires_counter_signature": true,
  "pdf_url": "/static/documents/templates/550e8400-e29b-41d4-a716-446655440000_enrollment.pdf"
}
```

### Sign Document

**Endpoint**: `POST /api/public/sign/{token}`

**Authentication**: Not required (uses one-time token)

**Content-Type**: `multipart/form-data`

**Form Fields**:
- `signature_text` (string, required) - Typed signature
- `consent_given` (boolean, required) - Must be true
- `signature_image` (file, optional) - Drawn signature image

**Rate Limiting**: 5 requests per minute per IP address

**Response**: `200 OK`
```json
{
  "message": "Document signed successfully",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "signed_at": "2025-11-04T12:34:56Z"
}
```

**Error Responses**:
- `400 Bad Request` - Invalid token, already signed, or consent not given
- `429 Too Many Requests` - Rate limit exceeded

## xAPI

### Record xAPI Statement

**Endpoint**: `POST /api/xapi/statements`

**Authentication**: Required

**Request**:
```json
{
  "actor": {
    "name": "Alice Student",
    "mbox": "mailto:alice.student@aada.edu",
    "objectType": "Agent"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": { "en-US": "completed" }
  },
  "object": {
    "id": "http://aada.edu/modules/1/lessons/1",
    "objectType": "Activity",
    "definition": {
      "name": { "en-US": "Welcome to AADA" },
      "type": "http://adlnet.gov/expapi/activities/module"
    }
  },
  "result": {
    "score": { "scaled": 1.0 },
    "success": true,
    "completion": true
  },
  "timestamp": "2025-11-04T12:34:56.789Z"
}
```

**Response**: `201 Created`
```json
{
  "success": true,
  "id": 123
}
```

## SCORM

### Get SCORM Data

**Endpoint**: `GET /api/scorm/{lesson_id}`

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "cmi.core.lesson_status": "incomplete",
  "cmi.core.score.raw": 75,
  "cmi.core.score.max": 100,
  "cmi.suspend_data": "{\"currentPage\": 5}"
}
```

### Commit SCORM Data

**Endpoint**: `POST /api/scorm/commit`

**Authentication**: Required

**Request**:
```json
{
  "lesson_id": 1,
  "cmi.core.lesson_status": "completed",
  "cmi.core.score.raw": 85,
  "cmi.core.score.max": 100,
  "cmi.suspend_data": "{\"currentPage\": 10}"
}
```

**Response**: `200 OK`
```json
{
  "success": true
}
```

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |

### Example Error Responses

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**:
```json
{
  "detail": "Admin access required"
}
```

**404 Not Found**:
```json
{
  "detail": "User not found"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

**Current**: No rate limiting (development)

**Planned** (production):
- 100 requests per minute per IP
- 1000 requests per hour per user
- Exceeded limit returns `429 Too Many Requests`

## Pagination

**For endpoints returning lists**:

Query parameters (future):
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 50, max: 100)

Response format (future):
```json
{
  "total": 250,
  "page": 1,
  "page_size": 50,
  "pages": 5,
  "data": [...]
}
```

## Filtering & Sorting

**Query Parameters** (planned):
- `sort_by` - Field to sort by
- `order` - `asc` or `desc`
- Field-specific filters (e.g., `status=active`)

Example:
```
GET /api/enrollments/?status=active&sort_by=enrolled_at&order=desc
```

## Webhooks (Future)

**Planned events**:
- `enrollment.created`
- `enrollment.completed`
- `transcript.generated`
- `externship.verified`

**Payload**:
```json
{
  "event": "enrollment.created",
  "timestamp": "2025-11-04T12:34:56Z",
  "data": {
    "enrollment_id": 5,
    "user_id": 1,
    "program_id": 1
  }
}
```

## API Versioning

**Current**: No versioning (v1 implicit)

**Future**: Version prefix in URL
- `/api/v1/users/`
- `/api/v2/users/`

**Policy**: v1 supported for 12 months after v2 release

## SDK / Client Libraries

**Generated TypeScript client** (Student Portal):
```typescript
import { useUsersQuery } from '@/api/hooks';

const { data: users, isLoading } = useUsersQuery();
```

**Python client** (future):
```python
from aada_lms import Client

client = Client(base_url="https://api.aada.edu")
client.login(email="admin@aada.edu", password="...")
users = client.users.list()
```

---

**Last Updated**: 2025-11-04  
**Maintained By**: Backend Team  
**Interactive Docs**: https://api.aada.edu/docs
