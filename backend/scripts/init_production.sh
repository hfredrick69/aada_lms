#!/bin/bash
# Production Database Initialization Script
# Run this once when setting up a new production environment

set -e  # Exit on any error

echo "🚀 AADA LMS - Production Database Initialization"
echo "================================================"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable not set"
    exit 1
fi

echo ""
echo "📊 Step 1: Running database migrations (includes all optimizations)..."
cd /code
PYTHONPATH=/code alembic upgrade head

echo ""
echo "✅ All migrations applied successfully!"
echo ""
echo "📋 Step 2: Verifying performance indexes..."
PYTHONPATH=/code python3 << 'PYTHON'
from app.db.session import engine
from sqlalchemy import text

# Count performance indexes
result = engine.connect().execute(text("""
    SELECT COUNT(*) FROM pg_indexes
    WHERE indexname LIKE 'idx_%'
    AND (schemaname = 'public' OR schemaname = 'crm' OR schemaname = 'compliance')
"""))
count = result.fetchone()[0]

if count >= 50:
    print(f"✅ Performance indexes verified: {count} indexes found")
else:
    print(f"⚠️  WARNING: Only {count} indexes found (expected 50+)")
    exit(1)
PYTHON

echo ""
echo "📋 Step 3: Verifying database schema..."
PYTHONPATH=/code python3 << 'PYTHON'
from app.db.session import engine
from sqlalchemy import text

# Check critical tables exist
tables = ['users', 'enrollments', 'module_progress', 'user_roles']
conn = engine.connect()

for table in tables:
    result = conn.execute(text(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = '{table}'
        )
    """))
    exists = result.fetchone()[0]
    if exists:
        print(f"✅ Table '{table}' exists")
    else:
        print(f"❌ ERROR: Table '{table}' missing")
        exit(1)
PYTHON

echo ""
echo "🎉 Production database initialization complete!"
echo ""
echo "Next steps:"
echo "  1. Run seed script if needed: python3 app/db/seed.py"
echo "  2. Start the application"
echo "  3. Verify health check endpoint"
