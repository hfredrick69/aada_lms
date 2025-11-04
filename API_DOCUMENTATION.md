# AADA LMS API Documentation

## Overview

The AADA Learning Management System provides a comprehensive RESTful API for managing:
- User authentication and authorization
- Program and module management
- Student enrollments and progress tracking
- Compliance reporting (attendance, skills, externships)
- Financial transactions (withdrawals, refunds)
- Credentials and transcripts
- xAPI learning analytics

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT authentication via Bearer token.

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@aada.edu",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer {token}
```

---

## Users API

### List Users
```http
GET /users
Authorization: Bearer {admin_token}
```

### Create User
```http
POST /users
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "email": "newuser@aada.edu",
  "password": "securepass",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Get User
```http
GET /users/{user_id}
Authorization: Bearer {token}
```

### Update User
```http
PUT /users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "first_name": "Jane",
  "status": "active"
}
```

### Delete User
```http
DELETE /users/{user_id}
Authorization: Bearer {admin_token}
```

---

## Roles API

### List Roles
```http
GET /roles
```

### Create Role
```http
POST /roles
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Instructor",
  "description": "Teaching staff"
}
```

### Delete Role
```http
DELETE /roles/{role_id}
Authorization: Bearer {admin_token}
```

---

## Programs API

### List Programs
```http
GET /programs
Authorization: Bearer {token}
```

### Get Program Modules
```http
GET /programs/{program_id}/modules
Authorization: Bearer {token}
```

---

## Enrollments API

### List Enrollments
```http
GET /enrollments
Authorization: Bearer {token}
```

---

## Attendance API

### List Attendance Logs
```http
GET /attendance
Authorization: Bearer {token}
```

### Create Attendance Log
```http
POST /attendance
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "uuid",
  "module_id": "uuid",
  "session_type": "live",
  "started_at": "2025-01-15T10:00:00Z",
  "ended_at": "2025-01-15T11:30:00Z"
}
```

### Update Attendance
```http
PUT /attendance/{attendance_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "session_type": "lab"
}
```

### Delete Attendance
```http
DELETE /attendance/{attendance_id}
Authorization: Bearer {token}
```

---

## Skills API

### List Skills Checkoffs
```http
GET /skills
Authorization: Bearer {token}
```

### Create Skill Checkoff
```http
POST /skills
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "uuid",
  "module_id": "uuid",
  "skill_code": "PPE_DON_DOFF",
  "status": "pending"
}
```

### Approve Skill Checkoff
```http
PUT /skills/{checkoff_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "approved",
  "evaluator_name": "Dr. Smith",
  "evaluator_license": "LIC-12345"
}
```

---

## Externships API

### List Externships
```http
GET /externships
Authorization: Bearer {token}
```

### Create Externship
```http
POST /externships
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "uuid",
  "site_name": "Dental Clinic",
  "supervisor_name": "Dr. Johnson",
  "total_hours": 120,
  "verified": true,
  "verification_doc_url": "https://example.com/doc.pdf"
}
```

---

## Finance API

### Withdrawals

#### List Withdrawals
```http
GET /finance/withdrawals
Authorization: Bearer {token}
```

#### Create Withdrawal
```http
POST /finance/withdrawals
Authorization: Bearer {token}
Content-Type: application/json

{
  "enrollment_id": "uuid",
  "reason": "Personal circumstances",
  "progress_pct_at_withdrawal": 45
}
```

### Refunds

#### List Refunds
```http
GET /finance/refunds
Authorization: Bearer {token}
```

#### Create Refund
```http
POST /finance/refunds
Authorization: Bearer {token}
Content-Type: application/json

{
  "withdrawal_id": "uuid",
  "amount_cents": 350000,
  "policy_basis": "GNPEC Standard 12 - Prorated"
}
```

---

## Credentials API

### List Credentials
```http
GET /credentials
Authorization: Bearer {token}
```

### Issue Credential
```http
POST /credentials
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "uuid",
  "program_id": "uuid",
  "credential_type": "certificate"
}
```

---

## Transcripts API

### List Transcripts
```http
GET /transcripts
Authorization: Bearer {token}
```

### Generate Transcript
```http
POST /transcripts
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "uuid",
  "program_id": "uuid"
}
```

### Download Transcript PDF
```http
GET /transcripts/{transcript_id}/pdf
Authorization: Bearer {token}
```

---

## Complaints API

### List Complaints
```http
GET /complaints?status=open
Authorization: Bearer {token}
```

### Create Complaint
```http
POST /complaints
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "uuid",
  "category": "Academic",
  "details": "Complaint details here"
}
```

### Update Complaint Status
```http
PUT /complaints/{complaint_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "resolved",
  "resolution_notes": "Issue addressed"
}
```

---

## xAPI API

### Create xAPI Statement
```http
POST /xapi/statements
Authorization: Bearer {token}
Content-Type: application/json

{
  "actor": {
    "mbox": "mailto:student@aada.edu",
    "name": "John Doe"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed"
  },
  "object": {
    "id": "http://aada.edu/modules/ma-101"
  }
}
```

### Query xAPI Statements
```http
GET /xapi/statements?agent=student@aada.edu&verb=completed&since=2025-01-01
Authorization: Bearer {token}
```

---

## Reports API

### Health Check
```http
GET /reports/health
```

### Compliance Reports
```http
GET /reports/compliance/{resource}?format=csv
Authorization: Bearer {token}
```

**Resources:** attendance, credentials, complaints, externships, skills, withdrawals, refunds, transcripts

**Formats:** csv, pdf

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Rate Limiting

No rate limiting currently enforced.

## Pagination

List endpoints do not currently implement pagination. All results are returned.

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

Generated: 2025-11-03
