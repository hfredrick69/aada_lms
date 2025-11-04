# AADA LMS / SIS Monorepo

Unified repository for the **Atlanta Academy of Dental Assisting** platform.  
This monorepo contains the backend (FastAPI), admin portal, student web UI,  
mobile Flutter app, documentation, and AI automation agents.

---

## 📂 Directory Layout
aada_lms/
├── backend/              # FastAPI backend (LMS + SIS API)
├── admin_portal/         # React/Vite Admin UI (existing)
├── frontend/             # Student-facing React/Vite UI (to be generated)
│   └── aada_web/
├── mobile/               # Flutter project(s)
│   └── aada_appv2/
├── docs/                 # Docs, audits, and AI instruction files
├── agents/               # Supervisor + AI automation agents
├── docker-compose.yml    # Unified dev environment
├── .env                  # Shared environment variables
└── README_monorepo.md

---

## 🧰 Prerequisites

| Tool | Version | Purpose |
|------|----------|---------|
| Python | ≥ 3.11 | FastAPI backend |
| Node.js | ≥ 20 | React/Vite frontends |
| npm | ≥ 10 | Frontend package manager |
| Docker / Docker Compose | latest | Unified runtime |
| Flutter | 3.8+ | Mobile app |
| Anthropic & Codex CLIs | latest | AI automation |

---

## ⚙️ Environment Variables (`.env`)

Create a file named `.env` at the repo root:

```bash
API_BASE_URL=http://localhost:8000/api
POSTGRES_USER=aada
POSTGRES_PASSWORD=changeme
POSTGRES_DB=aada_lms
JWT_SECRET=supersecretkey
NODE_ENV=development
