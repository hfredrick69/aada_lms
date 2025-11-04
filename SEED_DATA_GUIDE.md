# AADA LMS Seed Data Documentation

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

Generated: 2025-11-03
