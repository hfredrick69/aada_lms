#!/bin/bash
set -e

ACR_NAME="aadaregistry12345"
BACKEND_URL="https://aada-backend.nicedune-8fdc50bb.eastus2.azurecontainerapps.io"

echo "=== Building Admin Portal ==="
az acr login --name $ACR_NAME

cd admin_portal
docker buildx build --platform linux/amd64 \
  -f Dockerfile.prod \
  --build-arg VITE_API_BASE_URL="$BACKEND_URL" \
  -t aadaregistry12345.azurecr.io/aada-admin:latest \
  --push .

cd ../frontend/aada_web
docker buildx build --platform linux/amd64 \
  -f Dockerfile.prod \
  --build-arg VITE_API_BASE_URL="$BACKEND_URL" \
  -t aadaregistry12345.azurecr.io/aada-student:latest \
  --push .

echo "=== Redeploying Containers ==="
cd ../..
az containerapp revision copy --name aada-admin --resource-group aada-backend-rg
az containerapp revision copy --name aada-student --resource-group aada-backend-rg

echo "=== Done! ==="
