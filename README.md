# AADA LMS (xAPI + SCORM + SIS)

Backend system for the Atlanta Academy of Dental Assisting (AADA) Dental Assistant Certificate.

## Quickstart

```bash
cp .env.example .env
docker-compose up --build
open http://localhost:8000/docs
```


## Phase 2: GNPEC Compliance Tables (Separate `compliance` schema)
Run migrations:
```bash
docker-compose exec web alembic upgrade head
```
This creates schema **compliance** and tables: attendance_logs, skills_checkoffs, externships,
financial_ledgers, withdrawals, refunds, complaints, credentials, transcripts, audit_logs.
Routers are stubbed in `app/routers/` for Codex to implement CRUD/business logic.
