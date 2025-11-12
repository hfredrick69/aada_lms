import os
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment or use Azure connection
DEFAULT_DATABASE_URL = (
    "postgresql://aadaadmin:SecureDb2024XYZ!@aada-pg-server27841."
    "postgres.database.azure.com:5432/aada_lms?sslmode=require"
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
ENCRYPTION_KEY = (
    "V2t6pyVYNs+yxN+pjh714LUKABt5smISzbCkZF1XRW4="
)

print("Connecting to database...")
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    print("Clearing existing users...")
    conn.execute(text("TRUNCATE TABLE users CASCADE"))

    print("Creating encrypted admin user...")
    result = conn.execute(text("""
        INSERT INTO users (id, email, first_name, last_name, password_hash, status)
        VALUES (
          gen_random_uuid(),
          encode(pgp_sym_encrypt('admin@aada.edu', :key), 'base64'),
          encode(pgp_sym_encrypt('Ada', :key), 'base64'),
          encode(pgp_sym_encrypt('Administrator', :key), 'base64'),
          '$2b$12$LwHw6J8P9R5V6QZ3YGXfJu8p6rY8fTqM4xJm0qQZ3kGx4yM8fTqM8',
          'active'
        )
        RETURNING id
    """), {"key": ENCRYPTION_KEY})

    user_id = result.scalar()
    print(f"✓ Created admin user with ID: {user_id}")
    print()
    print("Login credentials:")
    print("  Email: admin@aada.edu")
    print("  Password: AdminPass!23")

print("✓ Done!")
