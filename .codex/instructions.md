# AADA_LMS Project – Codex Instructions

## Overview
The **Atlanta Academy of Dental Assisting LMS** provides backend APIs (FastAPI), React/TypeScript front-end, and an admin portal.  
Codex should assume full-stack production context.

---

## Backend (FastAPI / Python)
- Python 3.11
- Framework: FastAPI
- Tests: pytest 8.3.3 (run from root)
- Path: backend/app/
- Test Path: backend/app/tests/
- Command: `pytest`
- Config: `pytest.ini`
- Style: PEP8 + type hints
- Secrets: `.env` (never inline)
- CI: if requested, create minimal GitHub Actions YAML
- PostGreSQL

---

## Frontend (React / TypeScript)
- Framework: React + TypeScript
- Tests: Vitest 4.0.6 + jsdom
- Testing Library: @testing-library/react 16.3.0
- HTTP Mocking: MSW 2.11.6
- Config: frontend/aada_web/vite.config.ts
- Run:
  - `npm test`
  - `npm run test:watch`
  - `npm run test:coverage`

---

## Admin Portal (React / JS)
- Framework: React (JS)
- Tests: Vitest 4.0.8 + jsdom
- Mocking: axios-mock-adapter 2.1.0
- Config: admin_portal/vitest.config.js
- Run commands same as frontend.

---

## Behavior
- Generate **production-ready** code only.
- Use proper folder structure (`api/`, `db/`, `core/`, `tests/`).
- Always add concise docstrings.
- Ensure >90 % test coverage.
- When editing Docker or deployment scripts, verify Azure compatibility.

---

## Deployment Notes
- Azure Container Apps + Container Registry.
- Deployment scripts: `azure-deploy*.sh`
- No CI/CD pipeline yet; create one if asked.

---

## Documentation
- Update `README.md` for new commands or environment variables.
- Prefer clear examples over theory.
