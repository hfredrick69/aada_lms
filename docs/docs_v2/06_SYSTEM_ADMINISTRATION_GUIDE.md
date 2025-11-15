# AADA LMS - System Administration Guide

**Document Version:** 2.0
**Last Updated:** November 14, 2025
**Classification:** Confidential
**Audience:** System Administrators, DevOps Engineers

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Environment Setup](#2-environment-setup)
3. [Deployment Procedures](#3-deployment-procedures)
4. [Database Management](#4-database-management)
5. [User Management](#5-user-management)
6. [Security Operations](#6-security-operations)
7. [Monitoring & Logging](#7-monitoring--logging)
8. [Backup & Recovery](#8-backup--recovery)
9. [Troubleshooting](#9-troubleshooting)
10. [Maintenance Procedures](#10-maintenance-procedures)

---

## 1. System Overview

### 1.1 Architecture Summary

**Components**:
- Backend API (FastAPI, Python 3.11)
- Student Portal (React + TypeScript + Vite)
- Admin Portal (React + Material-UI + Vite)
- PostgreSQL 16 Database
- Azure Cloud Services (App Service, PostgreSQL, Blob Storage, Key Vault)

**Deployment**:
- Development: Docker Compose (local)
- Production: Azure App Service (containerized)

### 1.2 Access Requirements

**Required Access**:
- Azure Portal (subscription owner/contributor)
- Azure Key Vault (secrets access)
- PostgreSQL database (admin credentials)
- GitHub repository (code access)
- Docker Hub/Azure Container Registry (image access)

**Security Clearance**:
- Background check required
- HIPAA training completion
- Security awareness training
- Admin access approval process

### 1.3 Support Contacts

| Role | Contact | Responsibilities |
|------|---------|------------------|
| **Lead Developer** | dev-lead@aada.edu | Architecture, code issues |
| **DevOps Lead** | devops@aada.edu | Deployment, infrastructure |
| **Security Officer** | security@aada.edu | Security incidents, access |
| **Database Admin** | dba@aada.edu | Database management |
| **Compliance Officer** | compliance@aada.edu | HIPAA, audit logs |

---

## 2. Environment Setup

### 2.1 Development Environment

#### Prerequisites

```bash
# Required software
- Docker Desktop (latest)
- Docker Compose (latest)
- Git
- Text editor (VS Code recommended)
- Azure CLI (for production deployment)
```

#### Clone Repository

```bash
git clone https://github.com/aada/aada_lms.git
cd aada_lms
```

#### Environment Configuration

**Create `.env` file** (copy from `.env.example`):

```bash
cp .env.example .env
```

**Edit `.env`** with development values:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://aada:changeme@db:5432/aada_lms
ENCRYPTION_KEY=dev_encryption_key_32_bytes_long_12345

# JWT
JWT_SECRET_KEY=dev_jwt_secret_key_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (development - console logging)
EMAIL_PROVIDER=console

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174

# URLs
BACKEND_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5174
```

#### Start Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

**Services**:
- Backend API: http://localhost:8000
- Student Portal: http://localhost:5173
- Admin Portal: http://localhost:5174
- PostgreSQL: localhost:5432
- API Docs: http://localhost:8000/docs

### 2.2 Production Environment

**Azure Resources Required**:
- Resource Group
- App Service Plan (Linux, B1 or higher)
- App Service (3 instances: backend, student-portal, admin-portal)
- Azure Database for PostgreSQL (Flexible Server)
- Azure Blob Storage Account
- Azure Container Registry
- Azure Key Vault
- Azure Application Insights (optional but recommended)

**Environment Variables** (stored in Azure Key Vault):

```bash
# Database
DATABASE_URL=postgresql+psycopg2://aadaadmin:{password}@aada-pg-server.postgres.database.azure.com:5432/aada_lms?sslmode=require
ENCRYPTION_KEY={32-byte-key-from-key-vault}

# JWT
JWT_SECRET_KEY={64-byte-key-from-key-vault}
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (production - Azure Communication Services)
EMAIL_PROVIDER=acs
ACS_CONNECTION_STRING={from-key-vault}
ACS_SENDER_EMAIL=no-reply@aada.edu

# CORS
ALLOWED_ORIGINS=https://student.aada.edu,https://admin.aada.edu

# URLs
BACKEND_BASE_URL=https://api.aada.edu
FRONTEND_BASE_URL=https://student.aada.edu
```

---

## 3. Deployment Procedures

### 3.1 Local Development Deployment

**Quick Start**:

```bash
# 1. Start services
docker-compose up -d

# 2. Wait for database initialization
docker-compose logs db | grep "ready to accept connections"

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. (Optional) Seed database
docker-compose exec backend python app/db/seed.py

# 5. Access application
open http://localhost:5174  # Admin portal
open http://localhost:5173  # Student portal
open http://localhost:8000/docs  # API docs
```

**Stop Services**:

```bash
docker-compose down  # Stop and remove containers
docker-compose down -v  # Also remove volumes (DATABASE WILL BE DELETED)
```

### 3.2 Production Deployment

**Automated Deployment Script** (`azure-deploy.sh`):

```bash
#!/bin/bash
set -e

# Configuration
RESOURCE_GROUP="aada-lms-prod"
LOCATION="eastus"
ACR_NAME="aadalms"
APP_SERVICE_PLAN="aada-lms-plan"

# Build Docker images
echo "Building Docker images..."
docker build -t $ACR_NAME.azurecr.io/backend:latest -f backend/Dockerfile.prod backend/
docker build -t $ACR_NAME.azurecr.io/student-portal:latest student_portal/
docker build -t $ACR_NAME.azurecr.io/admin-portal:latest admin_portal/

# Push to Azure Container Registry
echo "Pushing images to ACR..."
az acr login --name $ACR_NAME
docker push $ACR_NAME.azurecr.io/backend:latest
docker push $ACR_NAME.azurecr.io/student-portal:latest
docker push $ACR_NAME.azurecr.io/admin-portal:latest

# Deploy backend to App Service
echo "Deploying backend..."
az webapp config container set \
  --name aada-lms-backend \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_NAME.azurecr.io/backend:latest \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io

# Run database migrations
echo "Running database migrations..."
az webapp ssh --name aada-lms-backend --resource-group $RESOURCE_GROUP \
  --command "cd /app && alembic upgrade head"

echo "Deployment completed successfully!"
```

**Run Deployment**:

```bash
chmod +x azure-deploy.sh
./azure-deploy.sh
```

### 3.3 Database Migration Deployment

**Apply Migrations**:

```bash
# Development (local)
docker-compose exec backend alembic upgrade head

# Production (Azure)
az webapp ssh --name aada-lms-backend --resource-group aada-lms-prod \
  --command "cd /app && alembic upgrade head"
```

**Rollback Migration**:

```bash
# Downgrade one migration
docker-compose exec backend alembic downgrade -1

# Downgrade to specific revision
docker-compose exec backend alembic downgrade <revision_id>
```

**Create New Migration**:

```bash
# 1. Modify models in backend/app/db/models/
# 2. Generate migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# 3. Review migration file in backend/alembic/versions/
# 4. Test migration
docker-compose exec backend alembic upgrade head

# 5. Commit migration file
git add backend/alembic/versions/*
git commit -m "Add migration: description"
```

---

## 4. Database Management

### 4.1 Database Access

**Development (Docker Compose)**:

```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U aada -d aada_lms

# Alternative: Connect from host
psql -h localhost -U aada -d aada_lms
```

**Production (Azure PostgreSQL)**:

```bash
# Install Azure CLI and login
az login

# Get connection string from Key Vault
az keyvault secret show --name database-url --vault-name aada-key-vault --query value -o tsv

# Connect using psql
psql "postgresql://aadaadmin:{password}@aada-pg-server.postgres.database.azure.com:5432/aada_lms?sslmode=require"
```

### 4.2 Common Database Operations

**View Database Size**:

```sql
SELECT pg_size_pretty(pg_database_size('aada_lms'));
```

**View Table Sizes**:

```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**View Active Connections**:

```sql
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'aada_lms';
```

**Terminate Idle Connections**:

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'aada_lms'
  AND state = 'idle'
  AND state_change < NOW() - INTERVAL '1 hour';
```

### 4.3 Database Backup

**Manual Backup** (Development):

```bash
# Backup database
docker-compose exec db pg_dump -U aada aada_lms > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
cat backup_20250314_120000.sql | docker-compose exec -T db psql -U aada aada_lms
```

**Manual Backup** (Production):

```bash
# Backup (use Azure CLI or pg_dump)
pg_dump "postgresql://aadaadmin:{password}@aada-pg-server.postgres.database.azure.com:5432/aada_lms?sslmode=require" \
  > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql "postgresql://aadaadmin:{password}@aada-pg-server.postgres.database.azure.com:5432/aada_lms?sslmode=require" \
  < backup_20250314_120000.sql
```

**Automated Backups** (Production):
- Azure PostgreSQL automatic backups enabled (7-day retention)
- Geo-redundant storage
- Point-in-time restore capability

### 4.4 Database Maintenance

**Vacuum and Analyze**:

```sql
-- Vacuum all tables (reclaim storage)
VACUUM VERBOSE ANALYZE;

-- Vacuum specific table
VACUUM VERBOSE ANALYZE users;
```

**Reindex**:

```sql
-- Reindex all tables
REINDEX DATABASE aada_lms;

-- Reindex specific table
REINDEX TABLE users;
```

**Update Statistics**:

```sql
ANALYZE;
```

---

## 5. User Management

### 5.1 Create Admin User

**Using Python Script**:

```python
# create_admin.py
import sys
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.role import Role
from app.core.security import hash_password
import uuid

db = SessionLocal()

# Create user
user = User(
    id=uuid.uuid4(),
    email="admin@aada.edu",
    password_hash=hash_password("SecureAdminPassword123!"),
    first_name="Admin",
    last_name="User",
    is_active=True,
    is_verified=True
)
db.add(user)

# Assign admin role
admin_role = db.query(Role).filter(Role.name == "admin").first()
user.roles.append(admin_role)

db.commit()
print(f"Admin user created: {user.email}")
```

**Run Script**:

```bash
docker-compose exec backend python create_admin.py
```

### 5.2 Reset User Password

**Using Database**:

```sql
-- Generate password hash (use Python bcrypt)
-- Then update user record

UPDATE users
SET password_hash = '$2b$12$...'  -- bcrypt hash
WHERE email = 'user@example.com';
```

**Using Python**:

```python
# reset_password.py
from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import hash_password

db = SessionLocal()

user = db.query(User).filter(User.email == "user@example.com").first()
user.password_hash = hash_password("NewSecurePassword123!")
db.commit()
print(f"Password reset for: {user.email}")
```

### 5.3 Unlock User Account

**Using Database**:

```sql
UPDATE users
SET failed_login_attempts = 0,
    locked_until = NULL
WHERE email = 'user@example.com';
```

### 5.4 Revoke User Sessions

**Using Database**:

```sql
-- Revoke all refresh tokens for user
UPDATE refresh_tokens
SET is_revoked = TRUE
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000';
```

**Note**: Access tokens cannot be revoked (stateless JWT). User must wait for token expiration (15 minutes) or clear client-side token.

---

## 6. Security Operations

### 6.1 Security Key Management

**Generate New Encryption Key**:

```python
import secrets

# Generate 32-byte key for AES-256
encryption_key = secrets.token_bytes(32)
print(encryption_key.hex())
```

**Rotate Encryption Key** (Complex - requires re-encryption):

```python
# 1. Generate new key
new_key = secrets.token_bytes(32)

# 2. Store in Azure Key Vault with new version
az keyvault secret set \
  --vault-name aada-key-vault \
  --name encryption-key \
  --value $(echo -n $new_key | base64)

# 3. Update application configuration
# 4. Re-encrypt all encrypted fields (scripted migration)
# 5. Verify decryption with new key
# 6. Deactivate old key version
```

### 6.2 Audit Log Review

**Recent PHI Access**:

```sql
SELECT
    al.created_at,
    u.email AS user_email,
    al.endpoint,
    al.method,
    al.ip_address,
    al.status_code
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.phi_access = TRUE
  AND al.created_at >= NOW() - INTERVAL '7 days'
ORDER BY al.created_at DESC
LIMIT 100;
```

**Failed Login Attempts**:

```sql
SELECT
    user_email,
    COUNT(*) AS failed_attempts,
    MAX(created_at) AS last_attempt,
    ip_address
FROM audit_logs
WHERE endpoint = '/auth/login'
  AND status_code = 401
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY user_email, ip_address
HAVING COUNT(*) >= 3
ORDER BY failed_attempts DESC;
```

**Unusual Access Patterns**:

```sql
-- Access outside business hours
SELECT
    u.email,
    al.endpoint,
    al.created_at,
    al.ip_address
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.phi_access = TRUE
  AND (EXTRACT(HOUR FROM al.created_at) < 6 OR EXTRACT(HOUR FROM al.created_at) > 20)
  AND al.created_at >= NOW() - INTERVAL '7 days'
ORDER BY al.created_at DESC;
```

### 6.3 Security Incident Response

**Immediate Actions** (Security Breach):

1. **Isolate** affected systems
   ```bash
   # Stop compromised service
   docker-compose stop backend
   # OR (Azure)
   az webapp stop --name aada-lms-backend --resource-group aada-lms-prod
   ```

2. **Revoke** all sessions
   ```sql
   UPDATE refresh_tokens SET is_revoked = TRUE;
   ```

3. **Change** critical secrets
   ```bash
   # Generate new JWT secret
   new_jwt_secret=$(python -c "import secrets; print(secrets.token_urlsafe(64))")

   # Update in Key Vault
   az keyvault secret set \
     --vault-name aada-key-vault \
     --name jwt-secret-key \
     --value "$new_jwt_secret"
   ```

4. **Notify** security team
   ```bash
   # Email security officer
   # Escalate to CISO if PHI compromised
   ```

5. **Document** incident (see Incident Response Plan)

---

## 7. Monitoring & Logging

### 7.1 Application Logs

**View Backend Logs** (Development):

```bash
# Real-time logs
docker-compose logs -f backend

# Recent logs (last 100 lines)
docker-compose logs --tail=100 backend

# Logs with timestamps
docker-compose logs -t backend
```

**View Backend Logs** (Production):

```bash
# Azure App Service logs
az webapp log tail --name aada-lms-backend --resource-group aada-lms-prod

# Download logs
az webapp log download \
  --name aada-lms-backend \
  --resource-group aada-lms-prod \
  --log-file logs.zip
```

### 7.2 Database Logs

**PostgreSQL Logs** (Development):

```bash
docker-compose logs db
```

**PostgreSQL Logs** (Production):

```bash
# Azure Portal: Database > Monitoring > Logs
# OR Azure CLI
az postgres flexible-server server-logs list \
  --resource-group aada-lms-prod \
  --server-name aada-pg-server
```

### 7.3 Monitoring Dashboards

**Azure Application Insights** (Production):

- Live metrics: Real-time request rate, response time, failure rate
- Application map: Dependency visualization
- Performance: Slow queries, long API calls
- Failures: Exception tracking, failed requests
- Users: Active users, sessions, page views

**Access**:
```bash
# Azure Portal
https://portal.azure.com → Application Insights → aada-lms-insights
```

### 7.4 Alerts Configuration

**Key Alerts** (Production):

| Alert | Condition | Action |
|-------|-----------|--------|
| **High Error Rate** | >5% failed requests (5 min) | Email DevOps team |
| **Slow Response** | Avg response time >2s (5 min) | Email DevOps team |
| **Database CPU** | >80% CPU (15 min) | Email DBA |
| **Storage Low** | <10% free disk space | Email DevOps team |
| **Failed Login Spike** | >10 failed logins/min | Email Security team |
| **PHI Access Anomaly** | Access outside hours | Email Compliance team |

---

## 8. Backup & Recovery

### 8.1 Backup Schedule

| Component | Frequency | Retention | Method |
|-----------|-----------|-----------|--------|
| **Database** | Daily (automated) | 7 days | Azure PostgreSQL backup |
| **Database** | Weekly (manual) | 90 days | pg_dump to Azure Blob |
| **Documents** | Real-time | Geo-redundant | Azure Blob replication |
| **Application Code** | On commit | Indefinite | Git repository |
| **Docker Images** | On build | Latest + tags | Azure Container Registry |

### 8.2 Restore Database

**Point-in-Time Restore** (Azure PostgreSQL):

```bash
# Restore to specific timestamp
az postgres flexible-server restore \
  --resource-group aada-lms-prod \
  --name aada-pg-server-restored \
  --source-server aada-pg-server \
  --restore-time "2025-03-14T10:00:00Z"
```

**Restore from Backup File**:

```bash
# Download backup from Azure Blob
az storage blob download \
  --account-name aadalmsbackups \
  --container-name database-backups \
  --name backup_20250314.sql \
  --file backup.sql

# Restore
psql "postgresql://..." < backup.sql
```

### 8.3 Disaster Recovery

**Recovery Procedure** (RTO: 4 hours):

1. **Assess** disaster scope (30 min)
2. **Activate** DR team (15 min)
3. **Restore** database from backup (1 hour)
4. **Deploy** application from Docker images (1 hour)
5. **Verify** system integrity (1 hour)
6. **Resume** operations (15 min)
7. **Notify** stakeholders (30 min)

**Annual DR Drill**: Scheduled for Q1 each year

---

## 9. Troubleshooting

### 9.1 Application Won't Start

**Symptoms**: Backend container fails to start

**Diagnosis**:
```bash
# Check container logs
docker-compose logs backend

# Check container status
docker-compose ps
```

**Common Causes**:
1. **Database not ready**: Wait for database initialization
   ```bash
   docker-compose logs db | grep "ready to accept connections"
   ```

2. **Port conflict**: Port 8000 already in use
   ```bash
   lsof -i :8000  # Find process using port
   kill -9 <PID>  # Kill process
   ```

3. **Invalid environment variables**: Check `.env` file
   ```bash
   cat .env | grep -E "(DATABASE_URL|JWT_SECRET|ENCRYPTION_KEY)"
   ```

### 9.2 Database Connection Errors

**Symptoms**: "could not connect to server"

**Diagnosis**:
```bash
# Test database connectivity
docker-compose exec backend python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('Connected!')"
```

**Solutions**:
1. **Database not running**: Start database
   ```bash
   docker-compose up -d db
   ```

2. **Wrong credentials**: Check `DATABASE_URL` in `.env`

3. **Network issues**: Restart Docker network
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### 9.3 Authentication Failures

**Symptoms**: 401 Unauthorized errors

**Diagnosis**:
```bash
# Check JWT secret consistency
docker-compose exec backend python -c "from app.core.config import settings; print(settings.SECRET_KEY)"
```

**Solutions**:
1. **Token expired**: Refresh token
2. **Invalid JWT secret**: Verify `JWT_SECRET_KEY` in environment
3. **Token not sent**: Check Authorization header in request

### 9.4 High Memory Usage

**Symptoms**: Application slow, OOM errors

**Diagnosis**:
```bash
# Check container memory usage
docker stats

# Check application memory
docker-compose exec backend python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

**Solutions**:
1. **Increase container memory**: Edit `docker-compose.yml`
   ```yaml
   backend:
     mem_limit: 2g
   ```

2. **Optimize queries**: Review slow queries, add indexes

3. **Connection pooling**: Adjust pool size in `app/db/session.py`

### 9.5 Slow Performance

**Diagnosis**:
```bash
# Check slow queries
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Solutions**:
1. **Add database indexes**: Analyze slow queries, create indexes
2. **Optimize queries**: Review and optimize N+1 queries
3. **Increase resources**: Scale up Azure App Service plan
4. **Enable caching**: Implement Redis caching (future)

---

## 10. Maintenance Procedures

### 10.1 Regular Maintenance Tasks

**Daily**:
- Monitor application logs for errors
- Check Azure service health
- Review failed login attempts

**Weekly**:
- Review audit logs
- Check database performance metrics
- Review backup success

**Monthly**:
- Security vulnerability scan
- Update dependencies
- Review user access
- Database maintenance (vacuum, analyze)

**Quarterly**:
- Backup restoration test
- Access review (user roles)
- Security assessment
- Performance optimization

**Annually**:
- Disaster recovery drill
- Comprehensive security audit
- HIPAA risk assessment
- Key rotation (encryption, JWT)

### 10.2 Update Dependencies

**Backend Dependencies**:

```bash
# 1. Check for updates
docker-compose exec backend pip list --outdated

# 2. Update requirements.txt
# Edit backend/requirements.txt

# 3. Rebuild container
docker-compose build backend

# 4. Test
docker-compose up -d
docker-compose exec backend pytest

# 5. Commit changes
git add backend/requirements.txt
git commit -m "Update backend dependencies"
```

**Frontend Dependencies**:

```bash
# Student Portal
cd student_portal
npm outdated
npm update
npm run build  # Test build

# Admin Portal
cd admin_portal
npm outdated
npm update
npm run build  # Test build

# Commit
git add student_portal/package*.json admin_portal/package*.json
git commit -m "Update frontend dependencies"
```

### 10.3 SSL Certificate Renewal

**Azure App Service** (Automatic):
- Azure-managed certificates renew automatically
- No manual intervention required
- Monitor expiration in Azure Portal

**Custom Certificates** (Manual):

```bash
# Upload new certificate to Azure
az webapp config ssl upload \
  --resource-group aada-lms-prod \
  --name aada-lms-backend \
  --certificate-file cert.pfx \
  --certificate-password <password>

# Bind certificate
az webapp config ssl bind \
  --resource-group aada-lms-prod \
  --name aada-lms-backend \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

### 10.4 Scale Application

**Vertical Scaling** (Increase resources):

```bash
# Scale up App Service Plan
az appservice plan update \
  --resource-group aada-lms-prod \
  --name aada-lms-plan \
  --sku P1V2  # Or higher tier
```

**Horizontal Scaling** (Add instances):

```bash
# Auto-scale based on CPU
az monitor autoscale create \
  --resource-group aada-lms-prod \
  --resource aada-lms-backend \
  --min-count 2 \
  --max-count 5 \
  --count 2

# Add scale rule
az monitor autoscale rule create \
  --resource-group aada-lms-prod \
  --autoscale-name aada-lms-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

---

**END OF DOCUMENT**

**Classification**: Confidential
**Distribution**: System administrators, DevOps engineers (authorized personnel only)
