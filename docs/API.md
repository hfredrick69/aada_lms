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
