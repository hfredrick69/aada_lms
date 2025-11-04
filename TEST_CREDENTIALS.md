# AADA LMS - Test Credentials

**Last Updated:** November 3, 2025

## Environment URLs

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Swagger/OpenAPI)
- **Admin Portal:** http://localhost:5173
- **Student Portal:** http://localhost:5174
- **Database:** PostgreSQL on localhost:5432

## Test Accounts

### Administrator Account
```
Email:    admin@aada.edu
Password: AdminPass!23
Role:     Admin
Name:     Ada Administrator
```

**Access:** Admin Portal (http://localhost:5173)

**Permissions:**
- Full access to all admin features
- View/manage students, programs, compliance reports
- Approve externships, credentials, transcripts
- View financial reports

---

### Student Account 1
```
Email:    alice.student@aada.edu
Password: AlicePass!23
Role:     Student
Name:     Alice Student
```

**Access:** Student Portal (http://localhost:5174)

**Permissions:**
- View enrolled courses
- Access Module 1 content (when integrated)
- View personal progress, grades
- Access H5P interactive activities

---

### Student Account 2
```
Email:    bob.student@aada.edu
Password: BobPass!23
Role:     Student
Name:     Bob Learner
```

**Access:** Student Portal (http://localhost:5174)

**Permissions:**
- View enrolled courses
- Access Module 1 content (when integrated)
- View personal progress, grades
- Access H5P interactive activities

---

## Database Access

### PostgreSQL Connection
```
Host:     localhost
Port:     5432
Database: aada_lms
Username: aada
Password: changeme
```

### Docker Command
```bash
docker-compose exec -it db psql -U aada -d aada_lms
```

---

## Quick Start Commands

### Start All Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend        # Backend API logs
docker-compose logs -f admin_portal   # Admin portal logs
docker-compose logs -f frontend       # Student portal logs
```

### Restart Specific Service
```bash
docker-compose restart backend
docker-compose restart admin_portal
docker-compose restart frontend
```

### Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Reseed Database
```bash
docker-compose exec backend python -m app.db.seed
```

---

## API Testing

### Login (Get JWT Token)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice.student@aada.edu","password":"AlicePass!23"}'
```

### Test Authenticated Endpoint
```bash
# First get token, then use it
TOKEN="<your_token_here>"
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Notes

- All passwords use the pattern: `[Name]Pass!23`
- Passwords require minimum 6 characters
- JWT tokens expire after a configured duration (check backend config)
- Database is seeded with sample programs, enrollments, and compliance data
- CORS is configured for localhost:5173 and localhost:5174 only

---

## Troubleshooting

### Can't Login
1. Verify database is seeded: `docker-compose exec backend python -m app.db.seed`
2. Check backend logs: `docker-compose logs backend`
3. Ensure CORS is configured in `backend/app/main.py`

### Database Errors
1. Run migrations: `docker-compose exec backend alembic upgrade head`
2. Enable citext extension: `docker-compose exec db psql -U aada -d aada_lms -c "CREATE EXTENSION IF NOT EXISTS citext;"`

### Frontend Not Loading
1. Rebuild containers: `docker-compose up -d --build`
2. Check environment variables in `docker-compose.yml`
3. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
