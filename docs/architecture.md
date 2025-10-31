# AADA LMS Architecture & Test Guide

## System Overview

The AADA Learning Management System is a FastAPI application backed by PostgreSQL and orchestrated with Docker Compose. The platform handles core LMS needs as well as GNPEC-compliant reporting for refunds, attendance, externships, and credentialing.

```
┌──────────┐      HTTP       ┌────────────┐      SQLAlchemy ORM      ┌────────────┐
│  Client  │ ──────────────▶ │  FastAPI   │ ───────────────────────▶ │ PostgreSQL │
└──────────┘                 │  Routers   │                          │  (Docker)  │
                             └────────────┘                          └────────────┘
                                   │
                                   ├─ app/routers/… (business domains)
                                   ├─ app/schemas/… (Pydantic models)
                                   └─ app/db/… (models, session, seed data)
```

## Application Architecture

- **FastAPI entry point**: `app/main.py` wires routers, exposes `/docs`, and integrates the SQLAlchemy session.
- **Configuration**: `app/core/config.py` loads environment variables for database URI, JWT settings, and compliance policy thresholds (`REFUND_DAYS_LIMIT`, `CANCELLATION_WINDOW_HOURS`, `PROGRESS_REFUND_THRESHOLD`).
- **Persistence**: SQLAlchemy models in `app/db/models/**` map to Postgres schemas (general tables plus `compliance.*` schema).
- **Routers & Business Logic**
  - `app/routers/auth.py`: JWT login + profile endpoints backed by PostgreSQL users/roles.
  - `app/routers/attendance.py`: CRUD for live/lab/externship sessions with duration validation.
  - `app/routers/skills.py`: Skills checkoff workflow with evaluator approvals and status transitions.
  - `app/routers/externships.py`: Externship tracking with verification document enforcement.
  - `app/routers/finance.py`: Withdrawals & refunds honoring cancellation windows, prorated refunds, and 45-day remittance limits.
  - `app/routers/complaints.py`: Complaint intake, review, resolution, and GNPEC appeal messaging.
  - `app/routers/credentials.py`: Certificate issuance gated by program completion checks.
  - `app/routers/transcripts.py`: Transcript generation aggregating module progress, creating PDF artifacts under `generated/transcripts/`.
  - `app/routers/reports.py`: CSV/PDF export endpoints for compliance datasets.
  - `app/routers/xapi.py`: Statement ingestion and analytics filters (`agent`, `verb`, `since`).

### Data Model Highlights

- **Enrollment lifecycle**: `enrollments`, `module_progress`, `programs`, and `modules` underpin attendance, credentials, and transcripts.
- **Compliance schema**: Contains `attendance_logs`, `skills_checkoffs`, `externships`, `withdrawals`, `refunds`, `complaints`, `credentials`, `transcripts`, and `financial_ledgers`.
- **xAPI**: Stored in `xapi_statements` with JSON payloads and timestamp indices suitable for analytics filters.

## Environment Setup

1. **Start services**
   ```bash
   docker-compose up --build -d
   ```
2. **Install Python deps (if running locally)**
   ```bash
   python3 -m pip install -r requirements.txt
   ```
3. **Apply migrations**
   ```bash
   docker-compose exec web alembic upgrade head
   ```
4. **Run API**
   - FastAPI runs on `http://localhost:8000` via the `web` service.
   - Interactive docs available at `http://localhost:8000/docs`.

## Database Seeding

- Run the reusable seeding script after migrations:
  ```bash
  docker-compose exec web python -m app.db.seed
  ```
- The script populates:
  - Users (students/admins), programs, modules, and enrollments.
    * Default admin credential: `admin@aada.edu` / `AdminPass!23`.
  - Module progress, attendance logs, skills checkoffs, externships.
  - Financial ledgers, withdrawals, refunds (prorated and cancellation cases).
  - Complaints at various lifecycle stages.
  - Credentials and transcripts with generated PDFs.
  - xAPI statements for analytics filtering.

## Testing Strategy

### Test Suite

| Test Module | Coverage Summary |
|-------------|------------------|
| `app/tests/test_basic.py` | Verifies API root health. |
| `app/tests/test_complaint_flow.py` | Exercises complaint intake → review → resolution → GNPEC appeal, with DB cleanup between runs. |
| `app/tests/test_refund_policy.py` | Validates refund list, prorated refund (<50% completion), and full cancellation refund (≤72 hours). |
| `app/tests/test_transcript_generation.py` | Seeds enrollment data, triggers transcript creation, verifies PDF output and retrieval. |
| `app/tests/test_xapi_filters.py` | Confirms analytics filters (`agent`, `verb`, `since`) on `/xapi/statements`. |

Each test resets dependent tables using helper utilities in `app/tests/utils.py` to ensure deterministic outcomes.

### Running Tests

```bash
docker-compose exec web env PYTHONPATH=/code pytest -v
```

The command sets `PYTHONPATH=/code` so imports of the `app` package resolve correctly in the container environment.

## Operational Notes

- **Generated assets**: Transcript PDFs land under `generated/transcripts/` (ignored by Git via `.gitignore`).
- **Environment variables**: adjust `.env` as needed; defaults align with docker-compose network names.
- **Reports**: Export compliance data by hitting `/reports/compliance/{resource}?format=csv|pdf`.
- **Analytics**: Query `/xapi/statements` with optional `agent`, `verb`, `since`, and `limit` parameters for LRS-style insights.

This document should serve as the canonical reference for architecture, setup, testing, and lifecycle operations of the AADA LMS platform.
