#!/bin/bash
set -e

echo "=== Seeding Azure Database ==="

# Build a temporary Docker image with the seed script
cd /Users/herbert/Projects/AADA/OnlineCourse/aada_lms/backend

# Get the DATABASE_URL from the backend container app
DATABASE_URL=$(az containerapp show --name aada-backend --resource-group aada-backend-rg --query "properties.template.containers[0].env[?name=='DATABASE_URL'].value" -o tsv)

echo "Running seed script against Azure database..."

# Run the seed script directly with the Azure DATABASE_URL
DATABASE_URL="$DATABASE_URL" PYTHONPATH=/Users/herbert/Projects/AADA/OnlineCourse/aada_lms/backend python3 app/db/seed.py

echo "=== Database seeded successfully! ==="
echo ""
echo "You can now login with:"
echo "  Email: admin@aada.edu"
echo "  Password: AdminPass!23"
