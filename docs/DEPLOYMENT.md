# AADA LMS - Deployment Guide

## Overview

This guide covers deploying the AADA LMS from development to production environments. The system supports deployment to cloud providers (AWS, Azure, GCP) or on-premises infrastructure.

## Deployment Architecture

### Production Architecture (Recommended)

```
┌─────────────────────────────────────────────┐
│         Load Balancer / CDN                 │
│         (AWS ALB / CloudFront)              │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼─────────┐  ┌──────▼──────────┐
│  Static Assets  │  │   API Gateway   │
│  (S3/CloudFront)│  │     (Nginx)     │
└─────────────────┘  └────────┬─────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
        ┌───────▼────────┐        ┌─────────▼────────┐
        │  Web Servers   │        │  Worker Nodes    │
        │  (Gunicorn)    │        │  (Background)    │
        │  FastAPI App   │        │                  │
        └───────┬────────┘        └──────────────────┘
                │
        ┌───────▼────────┐
        │   Database     │
        │  (RDS Postgres)│
        └────────────────┘
```

## Pre-Deployment Checklist

### Security Review
- [ ] All secrets moved to environment variables
- [ ] No hardcoded passwords in codebase
- [ ] HTTPS enforced (SSL certificates configured)
- [ ] CORS restricted to production domains
- [ ] Security headers configured (see SECURITY_COMPLIANCE.md)
- [ ] Database access restricted to private subnet
- [ ] Admin portal restricted to authorized IPs (optional)

### Code Quality
- [ ] All tests passing (backend, frontend, E2E)
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] No debugging code (console.log, print statements)
- [ ] Production dependencies only (no dev dependencies)

### Database
- [ ] Migrations tested and verified
- [ ] Backup procedures configured
- [ ] Database credentials secured
- [ ] Connection pooling configured
- [ ] Read replicas configured (if needed)

### Infrastructure
- [ ] Monitoring and alerting configured
- [ ] Log aggregation setup
- [ ] Backup/disaster recovery tested
- [ ] Scaling policies defined
- [ ] Domain names configured
- [ ] DNS records updated

## Environment Setup

### Environment Variables

**Backend (Production)**:
```bash
# Database
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/aada_lms

# Security
SECRET_KEY=<256-bit-random-key>  # Generate with: openssl rand -hex 32
ALLOWED_ORIGINS=https://admin.aada.edu,https://learn.aada.edu

# Application
ENV=production
DEBUG=False
LOG_LEVEL=INFO

# Sessions
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
COOKIE_SECURE=True
COOKIE_SAMESITE=strict

# Email (if configured)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>

# Storage (if using S3)
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
S3_BUCKET=aada-lms-uploads
```

**Frontend (Production)**:
```bash
# Build-time variables
VITE_API_URL=https://api.aada.edu
VITE_ENV=production
```

### Secrets Management

**AWS Secrets Manager**:
```bash
# Store secret
aws secretsmanager create-secret \
  --name aada-lms/database-url \
  --secret-string "postgresql://..."

# Retrieve in application
aws secretsmanager get-secret-value --secret-id aada-lms/database-url
```

**Environment Variables from Secrets**:
```python
# backend/app/core/config.py
import os
import boto3

if os.getenv("ENV") == "production":
    # Fetch from AWS Secrets Manager
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId='aada-lms/database-url')
    DATABASE_URL = secret['SecretString']
else:
    DATABASE_URL = os.getenv("DATABASE_URL")
```

## Deployment Methods

### Method 1: Docker Deployment (Simplest)

**Docker Compose (Production)**:
```yaml
version: '3.8'

services:
  backend:
    image: aada-lms-backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    restart: always
    ports:
      - "8000:8000"
    depends_on:
      - db
    command: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

  db:
    image: postgres:17
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

**Build and deploy**:
```bash
# Build backend image
docker build -t aada-lms-backend:latest ./backend

# Build frontend (static files)
cd frontend/aada_web
npm run build
# Upload dist/ to S3 or serve via nginx

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Method 2: AWS Deployment

**Architecture**:
- EC2 instances for backend (or ECS/Fargate)
- RDS PostgreSQL for database
- S3 + CloudFront for frontend static files
- ALB for load balancing
- Route 53 for DNS

**Backend on EC2**:
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip nginx

# Clone repository
git clone <repo-url> /opt/aada_lms
cd /opt/aada_lms/backend

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Install systemd service
sudo cp aada-lms.service /etc/systemd/system/
sudo systemctl enable aada-lms
sudo systemctl start aada-lms
```

**Systemd Service** (`/etc/systemd/system/aada-lms.service`):
```ini
[Unit]
Description=AADA LMS API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/aada_lms/backend
Environment="PATH=/usr/local/bin"
EnvironmentFile=/opt/aada_lms/.env
ExecStart=/usr/local/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend on S3 + CloudFront**:
```bash
# Build frontend
cd frontend/aada_web
npm run build

# Upload to S3
aws s3 sync dist/ s3://aada-lms-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E123456 \
  --paths "/*"
```

### Method 3: Kubernetes Deployment

**Kubernetes manifests**:

**Backend Deployment** (`k8s/backend-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aada-lms-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aada-lms-backend
  template:
    metadata:
      labels:
        app: aada-lms-backend
    spec:
      containers:
      - name: backend
        image: aada-lms-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aada-lms-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: aada-lms-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service** (`k8s/backend-service.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: aada-lms-backend
spec:
  selector:
    app: aada-lms-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy to Kubernetes**:
```bash
# Create secrets
kubectl create secret generic aada-lms-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="..."

# Apply manifests
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Check status
kubectl get pods
kubectl get services
```

## Database Migration

### Pre-Migration

**Backup database**:
```bash
# Production backup
pg_dump -h rds-endpoint -U admin aada_lms > backup_pre_deploy.sql

# Or automated
aws rds create-db-snapshot \
  --db-instance-identifier aada-lms-prod \
  --db-snapshot-identifier pre-deploy-$(date +%Y%m%d-%H%M%S)
```

### Running Migrations

**Manual migration**:
```bash
# SSH to backend server
ssh user@backend-server

# Run migrations
cd /opt/aada_lms/backend
source venv/bin/activate
alembic upgrade head
```

**Automated migration** (in deployment script):
```bash
#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
systemctl restart aada-lms
```

### Rollback Plan

**Rollback migration**:
```bash
alembic downgrade -1  # Rollback one version
```

**Restore from backup** (if needed):
```bash
psql -h rds-endpoint -U admin aada_lms < backup_pre_deploy.sql
```

## Nginx Configuration

**Production nginx.conf**:
```nginx
upstream backend {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.aada.edu admin.aada.edu learn.aada.edu;
    return 301 https://$host$request_uri;
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.aada.edu;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /opt/aada_lms/backend/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Admin Portal (served from S3/CloudFront or local)
server {
    listen 443 ssl http2;
    server_name admin.aada.edu;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    root /var/www/admin;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Student Portal
server {
    listen 443 ssl http2;
    server_name learn.aada.edu;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    root /var/www/student;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## SSL/TLS Configuration

### Let's Encrypt (Free SSL)

**Install Certbot**:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

**Obtain certificate**:
```bash
sudo certbot --nginx -d api.aada.edu -d admin.aada.edu -d learn.aada.edu
```

**Auto-renewal**:
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically adds renewal to cron
```

### AWS Certificate Manager

**Request certificate**:
```bash
aws acm request-certificate \
  --domain-name aada.edu \
  --subject-alternative-names *.aada.edu \
  --validation-method DNS
```

**Attach to ALB**:
- Configure HTTPS listener on ALB
- Select ACM certificate
- Configure target group to backend instances

## Monitoring Setup

### Application Logging

**Backend logging** (`backend/app/core/logging.py`):
```python
import logging
import json_logging

# Configure JSON logging for production
json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# CloudWatch handler (if using AWS)
if os.getenv("ENV") == "production":
    import watchtower
    handler = watchtower.CloudWatchLogHandler(log_group="/aada-lms/backend")
    logger.addHandler(handler)
```

### Health Check Endpoints

**Backend health check**:
```python
# backend/app/main.py
@app.get("/health")
def health_check():
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Monitoring Tools

**CloudWatch Alarms** (AWS):
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name aada-lms-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

**Application Metrics**:
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx responses)
- Request throughput (requests/second)
- Database connection pool utilization
- Queue lengths (if using background jobs)

## Scaling

### Horizontal Scaling

**Auto-scaling (AWS)**:
```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name aada-lms-backend \
  --version-description "Backend server template" \
  --launch-template-data file://launch-template.json

# Create auto-scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name aada-lms-backend-asg \
  --launch-template LaunchTemplateName=aada-lms-backend \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --vpc-zone-identifier subnet-12345,subnet-67890
```

**Scaling policies**:
- Scale up: CPU > 70% for 5 minutes
- Scale down: CPU < 30% for 10 minutes
- Max instances: 10
- Min instances: 2

### Database Scaling

**Read replicas**:
```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier aada-lms-read-replica-1 \
  --source-db-instance-identifier aada-lms-prod
```

**Connection pooling**:
```python
# backend/app/db/session.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Increase for production
    max_overflow=40,
    pool_pre_ping=True
)
```

## Rollback Procedure

### Application Rollback

**Docker deployment**:
```bash
# Tag current version
docker tag aada-lms-backend:latest aada-lms-backend:v1.2.3

# Deploy new version
docker pull aada-lms-backend:v1.3.0
docker-compose up -d

# Rollback if needed
docker-compose down
docker tag aada-lms-backend:v1.2.3 aada-lms-backend:latest
docker-compose up -d
```

**Kubernetes deployment**:
```bash
# Rollback to previous revision
kubectl rollout undo deployment/aada-lms-backend

# Rollback to specific revision
kubectl rollout undo deployment/aada-lms-backend --to-revision=3
```

### Database Rollback

**Alembic rollback**:
```bash
alembic downgrade -1  # Rollback one migration
```

**Full restore**:
```bash
# Stop application
systemctl stop aada-lms

# Restore database
psql -h rds-endpoint -U admin aada_lms < backup_pre_deploy.sql

# Restart application
systemctl start aada-lms
```

## Troubleshooting

### Common Issues

**Issue**: Application won't start
```bash
# Check logs
journalctl -u aada-lms -f

# Common causes:
# - Database connection refused (check DATABASE_URL)
# - Missing environment variables
# - Port already in use
```

**Issue**: Database connection timeout
```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier aada-lms-prod

# Check security group allows inbound on port 5432
# Check database credentials
```

**Issue**: High memory usage
```bash
# Check processes
top
ps aux | grep gunicorn

# Adjust worker count
# workers = (2 * cpu_cores) + 1
```

## Post-Deployment

### Verification Steps

1. **Smoke tests**:
   - [ ] Admin portal loads (https://admin.aada.edu)
   - [ ] Student portal loads (https://learn.aada.edu)
   - [ ] API health check passes (https://api.aada.edu/health)
   - [ ] Login works for admin user
   - [ ] Login works for student user

2. **Functionality tests**:
   - [ ] View student list
   - [ ] Create new enrollment
   - [ ] Upload credential
   - [ ] Generate transcript
   - [ ] Submit externship record

3. **Performance tests**:
   - [ ] Page load times < 2 seconds
   - [ ] API response times < 500ms (p95)
   - [ ] Database queries optimized

4. **Security tests**:
   - [ ] HTTPS enforced
   - [ ] Security headers present
   - [ ] CORS restricted
   - [ ] Authentication required for protected routes

### Monitoring

**First 24 hours**:
- Monitor error logs closely
- Check resource utilization (CPU, memory, disk)
- Verify backups running
- Test alert notifications

**First week**:
- Review performance metrics
- Analyze slow queries
- Check user feedback
- Adjust scaling policies if needed

---

**Last Updated**: 2025-11-04  
**Maintained By**: DevOps Team
