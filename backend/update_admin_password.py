import os
from sqlalchemy import create_engine, text

DEFAULT_DATABASE_URL = (
    "postgresql://aadaadmin:SecureDb2024XYZ!@aada-pg-server27841."
    "postgres.database.azure.com:5432/aada_lms?sslmode=require"
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
CORRECT_HASH = (
    "$2b$12$D/j1lpzIC6/dihu9v6MLzuUgyNq6iml1EedfdIm8AhKzWIYzrmMKe"
)

print("Updating admin password...")
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    result = conn.execute(text("""
        UPDATE users
        SET password_hash = :hash
        WHERE pgp_sym_decrypt(decode(email, 'base64'), :key) = 'admin@aada.edu'
        RETURNING id
    """), {"hash": CORRECT_HASH, "key": "V2t6pyVYNs+yxN+pjh714LUKABt5smISzbCkZF1XRW4="})

    user_id = result.scalar()
    if user_id:
        print(f"✓ Updated admin user password (ID: {user_id})")
    else:
        print("✗ No admin user found")

print("Done!")
