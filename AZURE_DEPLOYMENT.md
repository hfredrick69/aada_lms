# Azure Deployment Guide

## Current Azure Infrastructure

✓ Resource Group: `aada-backend-rg` (East US)
✓ Container Registry: `aadaregistry12345.azurecr.io`
✓ PostgreSQL Server: `aada-pg-server27841` (PostgreSQL 14 - will create new v16)
✓ Existing database: `aada_local`

## Deployment Plan

We'll create:
- New PostgreSQL 16 Flexible Server (`aada-pg16-server`)
- Container App Environment (`aada-lms-env`)
- 3 Container Apps: backend, admin portal, student portal

## Prerequisites

1. Azure CLI installed and logged in
2. Docker installed locally
3. Generate strong encryption keys:

```bash
# Generate 32-character encryption key
openssl rand -base64 32

# Generate JWT secret key
openssl rand -base64 64
```

## Deployment Steps

### 1. Update the deployment script

Edit `azure-deploy.sh`:
- Line 12: Replace `YourSecurePassword123!` with a strong password
- Line 65: Replace `your-32-char-encryption-key-here` with generated key
- Line 66: Replace `your-secret-key-here` with generated JWT secret

### 2. Make script executable

```bash
chmod +x azure-deploy.sh
```

### 3. Run deployment

```bash
./azure-deploy.sh
```

This will:
1. Register Microsoft.App provider
2. Create PostgreSQL 16 server with database
3. Enable pgcrypto extension
4. Create Container App Environment
5. Build and push 3 Docker images to your Container Registry
6. Deploy 3 Container Apps with proper networking
7. Run database migrations
8. Display URLs for all services

## Expected Output

After successful deployment, you'll get 3 URLs:
- Admin Portal: `https://aada-admin.<unique-id>.eastus.azurecontainerapps.io`
- Student Portal: `https://aada-student.<unique-id>.eastus.azurecontainerapps.io`
- Backend API: `https://aada-backend.<unique-id>.eastus.azurecontainerapps.io`

## After Deployment

1. Test the admin portal login
2. Verify API health: `https://aada-backend.../api/` (should return `{"status":"running"}`)
3. Update CORS if needed via Azure Portal or CLI

## Estimated Costs

- PostgreSQL B2s: ~$30/month
- Container Apps (3 apps): ~$25-40/month
- Container Registry Basic: ~$5/month

**Total: ~$60-75/month**

## Cleanup Old Resources (Optional)

If you want to delete the old infrastructure:

```bash
# Delete old PostgreSQL server
az postgres flexible-server delete --resource-group aada-backend-rg --name aada-pg-server27841

# Delete old App Services
az webapp delete --resource-group aada-backend-rg --name aada-backend-app12345
az staticwebapp delete --resource-group aada-backend-rg --name aada-web-app
```

## Troubleshooting

### Container build fails
```bash
# Check Docker is running
docker ps

# Try logging in to registry again
az acr login --name aadaregistry12345
```

### Database connection fails
```bash
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group aada-backend-rg \
  --name aada-pg16-server
```

### Container App won't start
```bash
# Check logs
az containerapp logs show \
  --name aada-backend \
  --resource-group aada-backend-rg \
  --follow
```
