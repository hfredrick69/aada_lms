# AADA LMS Testing Guide

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

Generated: 2025-11-03
