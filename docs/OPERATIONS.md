# AADA LMS - Operations Runbook

## Overview

This runbook provides operational procedures for maintaining and troubleshooting the AADA LMS in production. It covers routine maintenance, incident response, and common operational tasks.

## System Health Monitoring

### Health Check Endpoints

**Backend API Health**:
```bash
curl https://api.aada.edu/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-04T12:34:56Z"
}
```

**Database Health**:
```bash
# Check database connectivity
psql -h <db-host> -U <db-user> -d aada_lms -c "SELECT 1;"

# Check active connections
psql -h <db-host> -U <db-user> -d aada_lms -c "SELECT count(*) FROM pg_stat_activity;"
```

**Application Health Checks**:
- Frontend loading: https://admin.aada.edu, https://learn.aada.edu
- API response time: < 500ms (p95)
- Database query time: < 100ms
- Error rate: < 1%

### Key Metrics to Monitor

| Metric | Threshold | Action if Exceeded |
|--------|-----------|-------------------|
| CPU usage | > 80% | Investigate high-load processes, scale up |
| Memory usage | > 85% | Check for memory leaks, restart services |
| Disk usage | > 80% | Clean up logs, expand storage |
| Database connections | > 80 (of 100) | Check connection leaks, adjust pool size |
| API error rate | > 5% | Check logs, investigate errors |
| Response time (p95) | > 1000ms | Optimize queries, check database |

### Monitoring Tools

**CloudWatch Dashboards** (AWS):
- CPU, memory, disk usage
- Request count, error rate
- Response time distribution
- Database metrics

**Log Aggregation** (CloudWatch Logs, ELK):
- Application logs
- Error logs
- Audit logs
- Access logs

**Alerts**:
- High CPU/memory usage
- Error rate spike
- Database connection failures
- Slow query detection

## Routine Maintenance

### Daily Tasks

**Automated**:
- Database backups (midnight UTC)
- Log rotation
- Certificate renewal check
- Health check monitoring

**Manual** (if needed):
- Review error logs for patterns
- Check alert notifications
- Monitor performance metrics

### Weekly Tasks

- Review system performance reports
- Analyze slow query logs
- Check disk space trends
- Review security audit logs
- Verify backup integrity (sample restore)

### Monthly Tasks

- Security updates (OS, dependencies)
- Database maintenance (VACUUM, ANALYZE)
- Review and archive old logs
- Capacity planning review
- User access audit

### Quarterly Tasks

- Full security audit
- Disaster recovery test
- Performance optimization review
- Dependency updates (major versions)
- Documentation review

## Backup & Recovery

### Backup Schedule

**Database Backups**:
- Full backup: Daily at 2 AM UTC
- Incremental: Every 4 hours
- Retention: 30 days

**Application Code**:
- Git repository (source of truth)
- Docker images tagged by version

**User Uploads** (credentials, documents):
- Continuous sync to S3
- Versioning enabled
- Retention: Permanent

### Backup Verification

**Test restore procedure**:
```bash
# 1. Download backup
aws s3 cp s3://aada-lms-backups/db_backup_20251104.sql.gz .

# 2. Restore to test database
gunzip db_backup_20251104.sql.gz
psql -h test-db-host -U postgres -d aada_lms_test < db_backup_20251104.sql

# 3. Verify data integrity
psql -h test-db-host -U postgres -d aada_lms_test -c "SELECT count(*) FROM users;"

# 4. Clean up
dropdb -h test-db-host -U postgres aada_lms_test
```

### Disaster Recovery

**Recovery Time Objective (RTO)**: 4 hours  
**Recovery Point Objective (RPO)**: 4 hours (last incremental backup)

**Recovery Procedure**:

1. **Assess Situation**:
   - Determine scope of failure (database, application, infrastructure)
   - Identify last known good state

2. **Database Recovery**:
   ```bash
   # Restore from most recent backup
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier aada-lms-recovery \
     --db-snapshot-identifier aada-lms-snapshot-20251104
   
   # Wait for restore to complete
   aws rds wait db-instance-available \
     --db-instance-identifier aada-lms-recovery
   
   # Update application to point to new database
   ```

3. **Application Recovery**:
   ```bash
   # Redeploy application from known good version
   docker pull aada-lms-backend:v1.2.3
   docker-compose up -d
   
   # Or use Kubernetes rollback
   kubectl rollout undo deployment/aada-lms-backend --to-revision=5
   ```

4. **Verification**:
   - Test login functionality
   - Verify data integrity
   - Check recent transactions
   - Monitor for errors

5. **Communication**:
   - Notify stakeholders of recovery status
   - Update status page
   - Document incident and recovery

## Incident Response

### Incident Severity Levels

**P1 - Critical** (Response: Immediate):
- Complete system outage
- Data breach
- Database corruption
- Authentication system failure

**P2 - High** (Response: Within 1 hour):
- Partial system outage (one portal down)
- Performance degradation (> 5s response times)
- Database connection issues
- Payment processing failures

**P3 - Medium** (Response: Within 4 hours):
- Non-critical feature failure
- Slow performance (2-5s response times)
- Intermittent errors affecting < 10% of users

**P4 - Low** (Response: Next business day):
- Minor UI bugs
- Documentation issues
- Non-urgent feature requests

### Incident Response Procedure

1. **Detection & Alerting**:
   - Automated monitoring alerts
   - User-reported issues
   - Health check failures

2. **Triage**:
   - Assess severity
   - Determine impact (how many users affected)
   - Assign responder

3. **Investigation**:
   ```bash
   # Check application logs
   tail -f /var/log/aada-lms/app.log
   
   # Check error rates
   grep "ERROR" /var/log/aada-lms/app.log | wc -l
   
   # Check database
   psql -h db-host -U postgres -d aada_lms -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
   
   # Check system resources
   top
   df -h
   ```

4. **Mitigation**:
   - Apply fix or workaround
   - Restart services if needed
   - Rollback deployment if necessary

5. **Communication**:
   - Update status page
   - Notify affected users (if needed)
   - Provide ETR (estimated time to resolution)

6. **Resolution**:
   - Verify fix
   - Monitor for recurrence
   - Document incident

7. **Post-Mortem**:
   - Root cause analysis
   - Action items to prevent recurrence
   - Update runbook with lessons learned

## Common Issues & Troubleshooting

### Issue: Application Won't Start

**Symptoms**: Service fails to start, error in logs

**Diagnosis**:
```bash
# Check logs
journalctl -u aada-lms -n 50

# Common causes:
# - Database connection refused
# - Missing environment variables
# - Port already in use
```

**Solution**:
```bash
# Check database connectivity
pg_isready -h db-host -p 5432

# Verify environment variables
cat /etc/environment | grep DATABASE_URL

# Check port availability
lsof -i :8000

# Restart service
sudo systemctl restart aada-lms
```

### Issue: High CPU Usage

**Symptoms**: CPU > 80%, slow response times

**Diagnosis**:
```bash
# Identify process
top
ps aux | grep gunicorn

# Check database queries
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
```

**Solution**:
```bash
# Kill long-running queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '5 minutes';

# Restart application workers
sudo systemctl restart aada-lms

# Scale up if persistent
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name aada-lms-asg \
  --desired-capacity 5
```

### Issue: Database Connection Pool Exhausted

**Symptoms**: "too many connections" errors

**Diagnosis**:
```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check connection pool settings
grep pool_size backend/app/db/session.py
```

**Solution**:
```bash
# Kill idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'idle' AND now() - state_change > interval '10 minutes';

# Increase pool size (temporary)
# Edit backend/app/db/session.py
# pool_size=20  →  pool_size=30

# Restart application
sudo systemctl restart aada-lms

# Permanent fix: adjust PostgreSQL max_connections
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

### Issue: Slow Database Queries

**Symptoms**: Response times > 1s, high database CPU

**Diagnosis**:
```bash
# Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  # Log queries > 1s
SELECT pg_reload_conf();

# View slow queries
tail -f /var/log/postgresql/postgresql.log | grep "duration:"

# Analyze query plan
EXPLAIN ANALYZE <slow-query>;
```

**Solution**:
```sql
-- Add missing indexes
CREATE INDEX idx_enrollments_user_id ON enrollments (user_id);

-- Update table statistics
ANALYZE enrollments;

-- Vacuum tables
VACUUM ANALYZE enrollments;
```

### Issue: Memory Leak

**Symptoms**: Gradual memory increase, eventual OOM

**Diagnosis**:
```bash
# Monitor memory over time
watch -n 5 free -m

# Check process memory
ps aux --sort=-%mem | head

# Python memory profiling (if needed)
pip install memory_profiler
python -m memory_profiler backend/app/main.py
```

**Solution**:
```bash
# Restart application (immediate)
sudo systemctl restart aada-lms

# Investigate leak (longer term)
# - Review code for circular references
# - Check for unclosed database connections
# - Profile memory usage

# Temporary mitigation: scheduled restarts
# Add to crontab:
0 3 * * * systemctl restart aada-lms
```

### Issue: SSL Certificate Expiry

**Symptoms**: Browser certificate warnings, HTTPS errors

**Diagnosis**:
```bash
# Check certificate expiry
echo | openssl s_client -connect api.aada.edu:443 2>/dev/null | openssl x509 -noout -dates
```

**Solution**:
```bash
# Let's Encrypt renewal
sudo certbot renew

# Verify renewal
sudo certbot certificates

# Reload nginx
sudo systemctl reload nginx

# Test HTTPS
curl -I https://api.aada.edu
```

## Deployment Procedures

### Standard Deployment

**Pre-deployment checklist**:
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Database migrations tested
- [ ] Rollback plan prepared
- [ ] Stakeholders notified

**Deployment steps**:
```bash
# 1. Pull latest code
git pull origin main

# 2. Run database migrations
cd backend
alembic upgrade head

# 3. Build new Docker image
docker build -t aada-lms-backend:v1.3.0 .

# 4. Tag as latest
docker tag aada-lms-backend:v1.3.0 aada-lms-backend:latest

# 5. Rolling restart (zero downtime)
docker-compose up -d --no-deps --build backend

# 6. Verify deployment
curl https://api.aada.edu/health

# 7. Monitor logs
docker-compose logs -f backend
```

### Hotfix Deployment

**For urgent production fixes**:
```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix main

# 2. Apply fix and test locally

# 3. Fast-track review and merge

# 4. Deploy immediately
git pull origin main
docker-compose up -d --no-deps --build backend

# 5. Monitor closely for 30 minutes

# 6. Document incident and fix
```

### Rollback Procedure

**If deployment fails**:
```bash
# 1. Rollback application
docker tag aada-lms-backend:v1.2.3 aada-lms-backend:latest
docker-compose up -d

# 2. Rollback database (if migrations ran)
cd backend
alembic downgrade -1

# 3. Verify system health
curl https://api.aada.edu/health

# 4. Investigate issue
docker-compose logs backend

# 5. Plan fix and retry deployment
```

## Scaling Operations

### Horizontal Scaling

**Scale up (increase capacity)**:
```bash
# AWS Auto Scaling
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name aada-lms-asg \
  --desired-capacity 5

# Kubernetes
kubectl scale deployment aada-lms-backend --replicas=5
```

**Scale down**:
```bash
# AWS Auto Scaling
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name aada-lms-asg \
  --desired-capacity 2

# Kubernetes
kubectl scale deployment aada-lms-backend --replicas=2
```

### Database Scaling

**Add read replica**:
```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier aada-lms-read-1 \
  --source-db-instance-identifier aada-lms-prod
```

**Update application to use read replica**:
```python
# backend/app/db/session.py
READ_DATABASE_URL = os.getenv("READ_DATABASE_URL")
read_engine = create_engine(READ_DATABASE_URL)

# Use read replica for read-only queries
read_session = sessionmaker(bind=read_engine)
```

## Security Operations

### Rotate Secrets

**Database password rotation**:
```bash
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update database
psql -h db-host -U postgres -c "ALTER USER aada_app WITH PASSWORD '$NEW_PASSWORD';"

# 3. Update application config
aws secretsmanager update-secret \
  --secret-id aada-lms/database-password \
  --secret-string "$NEW_PASSWORD"

# 4. Restart application to pick up new secret
kubectl rollout restart deployment/aada-lms-backend
```

**JWT secret rotation**:
```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Update environment
aws secretsmanager update-secret \
  --secret-id aada-lms/jwt-secret \
  --secret-string "$NEW_SECRET"

# 3. Restart application
# Note: This will invalidate all existing sessions
kubectl rollout restart deployment/aada-lms-backend
```

### Security Audit

**Monthly security checklist**:
- [ ] Review user access logs
- [ ] Check for failed login attempts
- [ ] Verify SSL certificates valid
- [ ] Update security dependencies
- [ ] Review firewall rules
- [ ] Check for exposed secrets in logs
- [ ] Verify backup encryption

## Log Management

### Log Locations

**Application logs**:
- Development: `docker-compose logs backend`
- Production: `/var/log/aada-lms/app.log` or CloudWatch Logs

**Database logs**:
- PostgreSQL: `/var/log/postgresql/postgresql.log`

**Web server logs**:
- Nginx access: `/var/log/nginx/access.log`
- Nginx error: `/var/log/nginx/error.log`

### Log Retention

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Application logs | 90 days | CloudWatch / S3 |
| Audit logs | 3 years | S3 Glacier |
| Access logs | 30 days | CloudWatch / S3 |
| Error logs | 1 year | CloudWatch / S3 |

### Log Analysis

**Find errors in last hour**:
```bash
# CloudWatch Insights query
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

**Analyze API response times**:
```bash
# Parse nginx logs
awk '{print $NF}' /var/log/nginx/access.log | sort -n | tail -n 100
```

## Contact Information

### Escalation Path

**L1 - On-Call Engineer**:
- Initial response
- Basic troubleshooting
- Escalate to L2 if needed

**L2 - Senior Engineer**:
- Complex issues
- Database problems
- Performance optimization

**L3 - Lead Engineer / Architect**:
- Architecture decisions
- Major incidents
- Design changes

### Emergency Contacts

- On-Call Engineer: PagerDuty alerts
- DevOps Lead: [contact info]
- Database Admin: [contact info]
- Security Team: [contact info]
- Management: [contact info]

---

**Last Updated**: 2025-11-04  
**Maintained By**: DevOps Team  
**Review Schedule**: Quarterly
