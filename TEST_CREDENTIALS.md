# AADA LMS - Test Credentials

**Last Updated:** November 4, 2025
**Security Status:** Phase 1-4 Complete (HIPAA-compliant authentication)

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

### Staff Account
```
Email:    staff@aada.edu
Password: StaffPass!23
Role:     Staff
Name:     Sam Staffer
```

**Access:** Admin Portal (http://localhost:5173)

**Permissions:**
- All instructor permissions
- Create/update/delete students
- Manage all student records
- View and manage compliance reports

---

### Instructor Account
```
Email:    instructor@aada.edu
Password: InstructorPass!23
Role:     Instructor
Name:     Ian Instructor
```

**Access:** Admin Portal (http://localhost:5173)

**Permissions:**
- View and manage programs/modules
- View student progress and grades
- Manage attendance and skill checkoffs
- Cannot create/delete students (staff only)

---

### Finance Account
```
Email:    finance@aada.edu
Password: FinancePass!23
Role:     Finance
Name:     Fiona Finance
```

**Access:** Admin Portal (http://localhost:5173)

**Permissions:**
- View and manage financial ledgers
- Process payments and refunds
- View student enrollment financial data
- Access financial reports

---

### Registrar Account
```
Email:    registrar@aada.edu
Password: RegistrarPass!23
Role:     Registrar
Name:     Rita Registrar
```

**Access:** Admin Portal (http://localhost:5173)

**Permissions:**
- Manage student records
- Issue credentials and transcripts
- View compliance reports
- Manage enrollments and withdrawals

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
Password: BobLearner!23
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
Password: HLARcCjjFCBZQB8IIevlz1EEt8zaR9M9
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

### Reseed Database (Clears all data and creates test accounts)
```bash
docker-compose exec backend sh -c "cd /code && python3 -m app.db.seed"
```

---

## API Testing

### Phase 4 Authentication (httpOnly Cookies)

**Note:** Authentication now uses httpOnly cookies (XSS protection). Tokens are automatically sent via cookies, but Authorization header is still supported for backwards compatibility.

### Login (Cookie-Based Authentication)
```bash
# Login with cookies enabled (-c to save cookies)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice.student@aada.edu","password":"AlicePass!23"}' \
  -c cookies.txt -v

# Use saved cookies for authenticated requests
curl http://localhost:8000/api/auth/me \
  -b cookies.txt
```

### Login (Legacy Authorization Header - Still Supported)
```bash
# Get token from response
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice.student@aada.edu","password":"AlicePass!23"}'

# Use token in Authorization header
TOKEN="<your_token_here>"
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Token Refresh (Automatic via Cookies)
```bash
# Refresh token (rotates both access and refresh tokens)
curl -X POST http://localhost:8000/api/auth/refresh \
  -b cookies.txt -c cookies.txt
```

---

## Notes

### Password Policy (Phase 1 - HIPAA Compliant)
- **Minimum length:** 12 characters
- **Requires:** Uppercase + Lowercase + Digit + Special character
- **Pattern:** All test passwords follow `[Name][Context]!23` format
- **Validation:** Enforced at account creation and password change

### Authentication Security (Phase 3-4)
- **Access tokens:** Expire after 15 minutes (automatic refresh)
- **Refresh tokens:** Expire after 7 days (rotating tokens)
- **Storage:** httpOnly cookies (XSS protection) + Authorization header support
- **Session management:** Token-based with automatic refresh interceptors
- **CORS:** Configured for localhost:5173 and localhost:5174 only

### Database Seeding
- Database includes 10+ records per table
- Sample data: Programs, enrollments, compliance records (attendance, skills, externships, etc.)
- Test accounts: 7 role-based (admin, staff, instructor, finance, registrar, alice, bob) + 7 generic (user1-7@aada.edu)
- All generic accounts use password: `Pass123!Word`

---

## Security Improvements (Phase 1-4)

### Phase 1: Password Policy & Audit Logging
- ✅ HIPAA-compliant password requirements (12+ chars, complexity rules)
- ✅ Comprehensive audit logging for all authentication events
- ✅ Account lockout after 5 failed attempts (30 min lockout)
- ✅ Bcrypt password hashing with salt

### Phase 2: Role-Based Access Control (RBAC)
- ✅ Flexible role system (admin, staff, instructor, finance, registrar, student)
- ✅ Permission-based authorization
- ✅ Multiple roles per user support
- ✅ Staff role hierarchy with inherited permissions
- ✅ Audit logging for role changes

### Phase 3: Token Refresh & Revocation
- ✅ Refresh token system (7-day lifetime)
- ✅ Token rotation on refresh (enhanced security)
- ✅ Database-backed token revocation
- ✅ SHA-256 token hashing in database
- ✅ Automatic cleanup of expired tokens

### Phase 4: httpOnly Cookies & Encryption Infrastructure
- ✅ httpOnly cookie authentication (XSS protection)
- ✅ Automatic token refresh interceptors (both portals)
- ✅ PostgreSQL pgcrypto extension enabled
- ✅ Encryption helper functions for PHI data
- ✅ Backwards compatible with Authorization header

### Security Metrics
- **HIPAA Compliance:** 85% (up from 40%)
- **NIST Authentication:** 75% (up from 11%)
- **XSS Token Theft Risk:** LOW (was HIGH)
- **Critical Security Issues:** 2 remaining (down from 8)

---

## Troubleshooting

### Can't Login
1. **Verify database is seeded:**
   ```bash
   docker-compose exec backend sh -c "cd /code && python3 -m app.db.seed"
   ```
2. **Check password meets requirements:** Min 12 chars, uppercase, lowercase, digit, special
3. **Check backend logs:** `docker-compose logs backend | grep -i "login\|auth"`
4. **Verify cookies in browser:** Check Network tab → Login request → Response Headers → Set-Cookie

### Authentication Issues (Phase 4)
1. **401 Unauthorized errors:**
   - Clear browser cookies
   - Check if access token expired (15 min lifetime)
   - Verify `withCredentials: true` in frontend HTTP client
2. **Token refresh not working:**
   - Check refresh token hasn't expired (7 day lifetime)
   - Verify `/api/auth/refresh` endpoint is accessible
   - Check frontend interceptor logs in browser console

### Database Errors
1. **Run migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```
2. **Enable required extensions:**
   ```bash
   docker-compose exec db psql -U aada -d aada_lms -c "CREATE EXTENSION IF NOT EXISTS citext;"
   docker-compose exec db psql -U aada -d aada_lms -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
   ```
3. **Check database connection:**
   ```bash
   docker-compose exec db psql -U aada -d aada_lms -c "SELECT version();"
   ```

### Frontend Not Loading
1. **Rebuild containers:** `docker-compose up -d --build`
2. **Check environment variables:** Verify `.env` file has all Phase 1-4 variables
3. **Hard refresh browser:** `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
4. **Check CORS configuration:** Backend must allow frontend origins
5. **Clear browser cache and cookies**

### Password Policy Violations
If password doesn't meet requirements during registration/change:
- Check `.env` for `PASSWORD_MIN_LENGTH=12` and other password requirements
- Verify backend is reading environment variables correctly
- Test with compliant password: `TestPassword123!`
