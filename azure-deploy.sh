#!/bin/bash
# Azure deployment script for AADA LMS

set -e  # Exit on error

# Ensure Docker builds linux/amd64 images compatible with Azure Container Apps
export DOCKER_DEFAULT_PLATFORM=${DOCKER_DEFAULT_PLATFORM:-linux/amd64}

# Load Azure Communication Services secrets if available
if [ -f "./acs_info.sh" ]; then
  # shellcheck disable=SC1091
  source ./acs_info.sh
fi

# Variables
RG="${RG:-aada-backend-rg}"
LOCATION="${LOCATION:-eastus2}"
ACR_NAME="${ACR_NAME:-aadaregistry12345}"
DB_NAME="${DB_NAME:-aada-lms-db}"
DB_SERVER="${DB_SERVER:-aada-pg16-server}"
DB_ADMIN_USER="${DB_ADMIN_USER:-aadadmin}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:-bg6HJ8VEaQCHJ1kC12ykiCtF!A1}"
ENV_NAME="${ENV_NAME:-aada-lms-env}"

# Existing DB override (set USE_EXISTING_DB=true and provide the values below)
USE_EXISTING_DB="${USE_EXISTING_DB:-false}"
EXISTING_DB_SERVER="${EXISTING_DB_SERVER:-}"
EXISTING_DB_NAME="${EXISTING_DB_NAME:-$DB_NAME}"
EXISTING_DB_ADMIN_USER="${EXISTING_DB_ADMIN_USER:-$DB_ADMIN_USER}"
EXISTING_DB_ADMIN_PASSWORD="${EXISTING_DB_ADMIN_PASSWORD:-}"

# Registration / email defaults
EMAIL_PROVIDER="${EMAIL_PROVIDER:-acs}"
ACS_CONNECTION_STRING="${ACS_CONNECTION_STRING:-}"
ACS_SENDER_EMAIL="${ACS_SENDER_EMAIL:-no-reply@aada.edu}"
FRONTEND_BASE_URL="${FRONTEND_BASE_URL:-https://pending-student-url}"

if [ "$EMAIL_PROVIDER" = "acs" ] && [ -z "$ACS_CONNECTION_STRING" ]; then
  echo "ERROR: EMAIL_PROVIDER is set to 'acs' but ACS_CONNECTION_STRING is missing."
  exit 1
fi

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RG --query loginServer -o tsv)

echo "=== Step 1: Register Container App provider ==="
az provider register -n Microsoft.App --wait

if [ "$USE_EXISTING_DB" = "true" ]; then
  if [ -z "$EXISTING_DB_SERVER" ] || [ -z "$EXISTING_DB_ADMIN_PASSWORD" ]; then
    echo "ERROR: USE_EXISTING_DB=true but EXISTING_DB_SERVER or EXISTING_DB_ADMIN_PASSWORD not provided."
    exit 1
  fi
  DB_SERVER="$EXISTING_DB_SERVER"
  DB_NAME="$EXISTING_DB_NAME"
  DB_ADMIN_USER="$EXISTING_DB_ADMIN_USER"
  DB_ADMIN_PASSWORD="$EXISTING_DB_ADMIN_PASSWORD"
  echo "=== Using existing PostgreSQL server: $DB_SERVER ==="
else
  echo "=== Step 2: Create PostgreSQL 16 Flexible Server ==="
  az postgres flexible-server create \
    --resource-group $RG \
    --name $DB_SERVER \
    --location $LOCATION \
    --admin-user $DB_ADMIN_USER \
    --admin-password "$DB_ADMIN_PASSWORD" \
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
    --admin-user $DB_ADMIN_USER \
    --admin-password "$DB_ADMIN_PASSWORD" \
    --database-name $DB_NAME \
    --querytext "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
fi

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

echo "=== Step 8: Get DB connection string ==="
DB_HOST="${DB_SERVER}.postgres.database.azure.com"
DB_CONNECTION_STRING="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:5432/${DB_NAME}"

echo "=== Step 9: Deploy backend container app ==="
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
    ENVIRONMENT="production" \
    EMAIL_PROVIDER="$EMAIL_PROVIDER" \
    ACS_CONNECTION_STRING="$ACS_CONNECTION_STRING" \
    ACS_SENDER_EMAIL="$ACS_SENDER_EMAIL" \
    FRONTEND_BASE_URL="$FRONTEND_BASE_URL"

# Get backend URL
BACKEND_URL=$(az containerapp show --name aada-backend --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)
API_BASE_URL="https://$BACKEND_URL"

echo "=== Step 10: Build and push admin portal image ==="
cd admin_portal
docker build -f Dockerfile.prod --build-arg VITE_API_BASE_URL="$API_BASE_URL" -t ${ACR_LOGIN_SERVER}/aada-admin:latest .
docker push ${ACR_LOGIN_SERVER}/aada-admin:latest
cd ..

echo "=== Step 11: Build and push student portal image ==="
cd frontend/aada_web
docker build -f Dockerfile.prod --build-arg VITE_API_BASE_URL="$API_BASE_URL" -t ${ACR_LOGIN_SERVER}/aada-student:latest .
docker push ${ACR_LOGIN_SERVER}/aada-student:latest
cd ../..

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
STUDENT_FQDN=$(az containerapp show --name aada-student --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)
echo "Student Portal: https://$STUDENT_FQDN"
echo "Backend API: https://$BACKEND_URL"

if [ -n "$STUDENT_FQDN" ]; then
  echo "=== Updating backend with student portal URL ==="
  az containerapp update \
    --name aada-backend \
    --resource-group $RG \
    --set-env-vars \
      DATABASE_URL="$DB_CONNECTION_STRING" \
      ENCRYPTION_KEY="V2t6pyVYNs+yxN+pjh714LUKABt5smISzbCkZF1XRW4=" \
      SECRET_KEY="wxb+6mnsgdAu1Wx4jdjmQ2NO8bPW8/oyuKN8U9j8RweGeFnFXnIRdDVq7Gc+x/aXPjCGmwbNAXckQ3VTNOT12g==" \
      REFRESH_SECRET_KEY="ox+y0hZgDR6znM4shhbGLb8s3cSbZF8gB2a0l3B0Ohh/Z9/VbGXKGVuPtvqxmxbbfw/evyh4C0W7ZK+5A6ktIw==" \
      ENVIRONMENT="production" \
      EMAIL_PROVIDER="$EMAIL_PROVIDER" \
      ACS_CONNECTION_STRING="$ACS_CONNECTION_STRING" \
      ACS_SENDER_EMAIL="$ACS_SENDER_EMAIL" \
      FRONTEND_BASE_URL="https://$STUDENT_FQDN"
fi
