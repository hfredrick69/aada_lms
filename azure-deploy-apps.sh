#!/bin/bash
# Azure Container Apps deployment (images already pushed)

set -e

# Variables
RG="${RG:-aada-backend-rg}"
LOCATION="${LOCATION:-eastus2}"
ACR_NAME="${ACR_NAME:-aadaregistry12345}"
DB_NAME="${DB_NAME:-aada_lms}"
DB_SERVER="${DB_SERVER:-aada-pg-server27841}"
DB_ADMIN_USER="${DB_ADMIN_USER:-aadadmin}"
DB_ADMIN_PASSWORD="${DB_ADMIN_PASSWORD:-bg6HJ8VEaQCHJ1kC12ykiCtF!A1}"
ENV_NAME="${ENV_NAME:-aada-lms-env}"

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

echo "=== Deploying Backend Container App ==="
DB_HOST="${DB_SERVER}.postgres.database.azure.com"
DB_CONNECTION_STRING="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"

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

echo "=== Getting Backend URL ==="
BACKEND_URL=$(az containerapp show --name aada-backend --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)
echo "Backend URL: https://$BACKEND_URL"

echo "=== Deploying Admin Portal Container App ==="
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

echo "=== Deploying Student Portal Container App ==="
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

echo "=== Deployment Complete! ==="
echo "Admin Portal: https://$(az containerapp show --name aada-admin --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)"
STUDENT_FQDN=$(az containerapp show --name aada-student --resource-group $RG --query properties.configuration.ingress.fqdn -o tsv)
echo "Student Portal: https://$STUDENT_FQDN"
echo "Backend API: https://$BACKEND_URL"

if [ -n "$STUDENT_FQDN" ]; then
  echo "=== Updating backend with student portal URL ==="
  az containerapp update \
    --name aada-backend \
    --resource-group $RG \
    --env-vars \
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
