#!/usr/bin/env python3
"""
Documentation Agent
-------------------
Generates comprehensive API documentation.
"""

import datetime
from pathlib import Path

LOG_DIR = Path("/tmp/agent_logs")
LOG_DIR.mkdir(exist_ok=True)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[Documentation] {ts} | {msg}"
    print(entry)
    with open(LOG_DIR / "documentation.log", "a") as f:
        f.write(entry + "\n")


def create_api_documentation():
    """Create comprehensive API documentation"""
    log("Creating API documentation...")

    doc_content = '''# AADA LMS API Documentation

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

Generated: ''' + datetime.datetime.now().strftime("%Y-%m-%d") + '''
'''

    doc_path = PROJECT_ROOT / "API_DOCUMENTATION.md"
    doc_path.write_text(doc_content)
    log(f"✅ Created {doc_path}")


def create_testing_documentation():
    """Create testing guide"""
    log("Creating testing documentation...")

    test_doc = '''# AADA LMS Testing Guide

## Overview

This guide covers testing procedures for the AADA Learning Management System.

## Test Environment Setup

### Database Reset
```bash
cd backend
python3 -c "from app.db.seed import reset_and_seed; reset_and_seed()"
```

### Run All Tests
```bash
cd backend/app
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_users_api.py -v
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

## Test Data

Seed data creates:
- 10 users (user1@aada.edu through user10@aada.edu)
- 10 programs with 30 modules
- 10 enrollments
- Sample attendance, skills, externships, credentials, etc.

**Test Credentials:**
- Email: user1@aada.edu
- Password: password123

## Test Categories

### 1. Authentication Tests
- Login flow
- Token validation
- Role-based access control

### 2. CRUD Tests
- User management
- Role management
- Attendance tracking
- Skills checkoffs
- Externships
- Credentials
- Transcripts

### 3. Workflow Tests
- Complaint submission → review → resolution
- Withdrawal → refund processing
- Skill checkoff approval
- Transcript generation with GPA

### 4. Compliance Tests
- Refund policy calculations
- 45-day remittance validation
- GNPEC reporting

### 5. Integration Tests
- xAPI statement tracking
- H5P content delivery
- PDF generation

## Running Automated Tests via Agents

```bash
# Run QA agent (includes all tests)
python3 agents/qa_agent.py

# Run full agent cycle
python3 agents/supervisor_agent.py
```

## Manual Testing Checklist

- [ ] Login as admin
- [ ] Create new user
- [ ] Enroll student in program
- [ ] Log attendance
- [ ] Submit skill checkoff
- [ ] Generate transcript
- [ ] Process withdrawal and refund
- [ ] Submit and resolve complaint
- [ ] Issue credential
- [ ] Generate compliance reports

## CI/CD Integration

Tests run automatically via:
- Pre-commit hooks (flake8 linting)
- QA Agent (pytest suite)
- GitHub Actions (if configured)

---

Generated: ''' + datetime.datetime.now().strftime("%Y-%m-%d") + '''
'''

    test_doc_path = PROJECT_ROOT / "TESTING_GUIDE.md"
    test_doc_path.write_text(test_doc)
    log(f"✅ Created {test_doc_path}")


def create_seed_documentation():
    """Create seed data documentation"""
    log("Creating seed data documentation...")

    seed_doc = '''# AADA LMS Seed Data Documentation

## Overview

Seed data provides comprehensive test records for development and testing.

## Seed Data Contents

### Users (10)
- user1@aada.edu through user10@aada.edu
- Password: `password123`
- user1 has Admin role
- All users have Student role

### Programs (10)
- PROG-001 through PROG-010
- Clock hours: 480-570
- All certificate level

### Modules (30)
- 3 modules per program
- Online delivery type
- 40 clock hours each

### Enrollments (10)
- 8 active enrollments
- 2 withdrawn enrollments

### Attendance Logs (20)
- 2 logs per user (live + lab sessions)

### Skills Checkoffs (10)
- 7 approved
- 3 pending

### Externships (10)
- 6 verified
- 4 unverified
- 80-170 hours each

### Financial Ledgers (10)
- Tuition entries for all users
- $8,500-$8,600 range

### Withdrawals (2)
- Users 9 and 10
- Progress: 30-45%

### Refunds (2)
- Prorated refunds for withdrawn students
- $3,000 each

### Complaints (10)
- 6 resolved
- 4 in review
- Mixed academic/administrative categories

### Credentials (7)
- Issued to completed students
- Serial numbers: CERT-2025-0001 through CERT-2025-0007

### Transcripts (7)
- GPA range: 3.5-3.8
- PDF URLs generated

### xAPI Statements (10)
- Completion statements for each user

## Running Seed Data

### Via Python
```bash
cd backend
python3 -c "from app.db.seed import reset_and_seed; reset_and_seed()"
```

### Via Agent
```bash
python3 agents/seed_expansion_agent.py
```

## Customizing Seed Data

Edit `/backend/app/db/seed.py` to:
- Add more records
- Change user credentials
- Modify program content
- Adjust enrollment statuses

## Database Reset

**WARNING:** Seed script uses `TRUNCATE CASCADE` to clear all data before seeding.

Affected schemas:
- `public` (users, programs, modules, enrollments)
- `compliance` (all compliance tables)

---

Generated: ''' + datetime.datetime.now().strftime("%Y-%m-%d") + '''
'''

    seed_doc_path = PROJECT_ROOT / "SEED_DATA_GUIDE.md"
    seed_doc_path.write_text(seed_doc)
    log(f"✅ Created {seed_doc_path}")


def main():
    log("===== Documentation Agent Starting =====")

    try:
        create_api_documentation()
        create_testing_documentation()
        create_seed_documentation()

        log("✅ All documentation generated")

    except Exception as e:
        log(f"❌ Error: {e}")
        raise

    log("===== Documentation Agent Complete =====")


if __name__ == "__main__":
    main()
