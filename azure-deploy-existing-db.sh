#!/bin/bash
# Azure deployment script for AADA LMS (using existing PostgreSQL server)

set -e  # Exit on error

# Variables
RG="aada-backend-rg"
LOCATION="eastus2"
ACR_NAME="aadaregistry12345"
DB_NAME="aada_lms"
DB_SERVER="aada-pg-server27841"
DB_ADMIN_USER="aadadmin"
DB_ADMIN_PASSWORD="bg6HJ8VEaQCHJ1kC12ykiCtF!A1"
ENV_NAME="aada-lms-env"

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RG --query loginServer -o tsv)

echo "=== Step 1: Register Container App provider ==="
az provider register -n Microsoft.App --wait

echo "=== Step 2: Create database on existing PostgreSQL server ==="
az postgres flexible-server db create \
  --resource-group $RG \
  --server-name $DB_SERVER \
  --database-name $DB_NAME

echo "=== Step 3: Enable pgcrypto extension ==="
PGPASSWORD="$DB_ADMIN_PASSWORD" psql \
  -h ${DB_SERVER}.postgres.database.azure.com \
  -U $DB_ADMIN_USER \
  -d $DB_NAME \
  -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

echo "=== Step 4: Create Container App Environment ==="
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RG \
  --location $LOCATION

echo "=== Step 5: Log in to Container Registry ==="
az acr login --name $ACR_NAME

echo "=== Step 6: Build and push backend image ==="
cd backend
docker build -f Dockerfile.prod -t ${ACR_LOGIN_SERVER}/aada-backend:latest .
docker push ${ACR_LOGIN_SERVER}/aada-backend:latest
cd ..

echo "=== Step 7: Build and push admin portal image ==="
cd admin_portal
docker build -f Dockerfile.prod -t ${ACR_LOGIN_SERVER}/aada-admin:latest .
docker push ${ACR_LOGIN_SERVER}/aada-admin:latest
cd ..

echo "=== Step 8: Build and push student portal image ==="
cd frontend/aada_web
docker build -f Dockerfile.prod -t ${ACR_LOGIN_SERVER}/aada-student:latest .
docker push ${ACR_LOGIN_SERVER}/aada-student:latest
cd ../..

echo "=== Step 9: Get DB connection string ==="
DB_HOST="${DB_SERVER}.postgres.database.azure.com"
DB_CONNECTION_STRING="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"

echo "=== Step 10: Deploy backend container app ==="
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
    ENCRYPTION_KEY="V2t6pyVYNs+yxN+pjh714LUKABt5smISzbCkZF1XRW4=" \
    SECRET_KEY="wxb+6mnsgdAu1Wx4jdjmQ2NO8bPW8/oyuKN8U9j8RweGeFnFXnIRdDVq7Gc+x/aXPjCGmwbNAXckQ3VTNOT12g==" \
    REFRESH_SECRET_KEY="ox+y0hZgDR6znM4shhbGLb8s3cSbZF8gB2a0l3B0Ohh/Z9/VbGXKGVuPtvqxmxbbfw/evyh4C0W7ZK+5A6ktIw==" \
    ENVIRONMENT="production"

# Get backend URL
BACKEND_URL=$(az containerapp show --name aada-backend --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)

echo "=== Step 11: Deploy admin portal container app ==="
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

echo "=== Step 12: Deploy student portal container app ==="
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
