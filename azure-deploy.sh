#!/bin/bash
# Azure deployment script for AADA LMS

set -e  # Exit on error

# Variables
RG="aada-backend-rg"
LOCATION="eastus"
ACR_NAME="aadaregistry12345"
DB_NAME="aada-lms-db"
DB_SERVER="aada-pg16-server"
ENV_NAME="aada-lms-env"

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RG --query loginServer -o tsv)

echo "=== Step 1: Register Container App provider ==="
az provider register -n Microsoft.App --wait

echo "=== Step 2: Create PostgreSQL 16 Flexible Server ==="
az postgres flexible-server create \
  --resource-group $RG \
  --name $DB_SERVER \
  --location $LOCATION \
  --admin-user aadadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B2s \
  --tier Burstable \
  --version 16 \
  --storage-size 32 \
  --public-access 0.0.0.0-255.255.255.255

echo "=== Step 3: Create database ==="
az postgres flexible-server db create \
  --resource-group $RG \
  --server-name $DB_SERVER \
  --database-name $DB_NAME

echo "=== Step 4: Enable pgcrypto extension ==="
az postgres flexible-server execute \
  --name $DB_SERVER \
  --admin-user aadadmin \
  --admin-password "YourSecurePassword123!" \
  --database-name $DB_NAME \
  --querytext "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

echo "=== Step 5: Create Container App Environment ==="
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RG \
  --location $LOCATION

echo "=== Step 6: Log in to Container Registry ==="
az acr login --name $ACR_NAME

echo "=== Step 7: Build and push backend image ==="
cd backend
docker build -f Dockerfile.prod -t ${ACR_LOGIN_SERVER}/aada-backend:latest .
docker push ${ACR_LOGIN_SERVER}/aada-backend:latest
cd ..

echo "=== Step 8: Build and push admin portal image ==="
cd admin_portal
docker build -f Dockerfile.prod -t ${ACR_LOGIN_SERVER}/aada-admin:latest .
docker push ${ACR_LOGIN_SERVER}/aada-admin:latest
cd ..

echo "=== Step 9: Build and push student portal image ==="
cd frontend/aada_web
docker build -f Dockerfile.prod -t ${ACR_LOGIN_SERVER}/aada-student:latest .
docker push ${ACR_LOGIN_SERVER}/aada-student:latest
cd ../..

echo "=== Step 10: Get DB connection string ==="
DB_HOST="${DB_SERVER}.postgres.database.azure.com"
DB_CONNECTION_STRING="postgresql://aadadmin:YourSecurePassword123!@${DB_HOST}:5432/${DB_NAME}"

echo "=== Step 11: Deploy backend container app ==="
az containerapp create \
  --name aada-backend \
  --resource-group $RG \
  --environment $ENV_NAME \
  --image ${ACR_LOGIN_SERVER}/aada-backend:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv) \
  --env-vars \
    DATABASE_URL="$DB_CONNECTION_STRING" \
    ENCRYPTION_KEY="your-32-char-encryption-key-here" \
    SECRET_KEY="your-secret-key-here" \
    ENVIRONMENT="production"

# Get backend URL
BACKEND_URL=$(az containerapp show --name aada-backend --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)

echo "=== Step 12: Deploy admin portal container app ==="
az containerapp create \
  --name aada-admin \
  --resource-group $RG \
  --environment $ENV_NAME \
  --image ${ACR_LOGIN_SERVER}/aada-admin:latest \
  --target-port 80 \
  --ingress external \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv) \
  --env-vars \
    VITE_API_URL="https://$BACKEND_URL"

echo "=== Step 13: Deploy student portal container app ==="
az containerapp create \
  --name aada-student \
  --resource-group $RG \
  --environment $ENV_NAME \
  --image ${ACR_LOGIN_SERVER}/aada-student:latest \
  --target-port 80 \
  --ingress external \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv) \
  --env-vars \
    VITE_API_URL="https://$BACKEND_URL"

echo "=== Deployment complete! ==="
echo "Admin Portal: https://$(az containerapp show --name aada-admin --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)"
echo "Student Portal: https://$(az containerapp show --name aada-student --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)"
echo "Backend API: https://$BACKEND_URL"
