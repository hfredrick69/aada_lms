# AADA LMS (xAPI + SCORM + SIS)

**Atlanta Academy of Dental Assisting** - Learning Management System + Student Information System

Complete LMS/SIS platform with GNPEC compliance, H5P interactive content, and dual-portal architecture.

## 🚀 Quick Start

```bash
# 1. Start all services
docker-compose up -d --build

# 2. Enable PostgreSQL extension
docker-compose exec db psql -U aada -d aada_lms -c "CREATE EXTENSION IF NOT EXISTS citext;"

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Seed test data
docker-compose exec backend python -m app.db.seed
```

## 🔗 Access URLs

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Admin Portal:** http://localhost:5173
- **Student Portal:** http://localhost:5174

## 🔑 Test Credentials

See **[TEST_CREDENTIALS.md](TEST_CREDENTIALS.md)** for all test accounts and quick reference commands.

**Quick Login:**
- Admin: `admin@aada.edu` / `AdminPass!23`
- Student: `alice.student@aada.edu` / `AlicePass!23`

## 📚 Documentation

- **[Status & Progress](aada_lms_sis_10312025.md)** - Current state, gaps, and priorities
- **[Test Credentials](TEST_CREDENTIALS.md)** - All login credentials and quick commands
- **[Architecture Guide](docs/architecture.md)** - System design and testing guide
- **[Monorepo Overview](README_monorepo.md)** - Directory structure and setup
- **[H5P Infrastructure](docs/h5p_content_infrastructure.md)** - Complete H5P system documentation
- **[Student Portal Integration](docs/student_portal_integration.md)** - Module player & H5P embedding
- **[H5P Matching Generator](docs/h5p_matching_generator.md)** - Build H5P.Matching packages

## 🏗️ Architecture

```
aada_lms/
├── backend/              # FastAPI backend (port 8000)
├── admin_portal/         # React admin UI (port 5173)
├── frontend/aada_web/    # React student portal (port 5174)
├── mobile/aada_appv2/    # Flutter mobile app
├── docs/                 # Documentation
└── agents/               # AI automation agents
```

## ✅ What's Working

- ✅ JWT authentication for both portals
- ✅ PostgreSQL database with all migrations
- ✅ Admin portal: Dashboard, programs, reports, externships, documents
- ✅ Student portal: Dashboard, authentication
- ✅ GNPEC compliance APIs (withdrawals, refunds, complaints, transcripts)
- ✅ E-signature system: Document templates, public signing, audit trail (ESIGN Act compliant)
- ✅ H5P content delivery system
- ✅ xAPI/Learning Record Store
- ✅ Docker Compose orchestration
