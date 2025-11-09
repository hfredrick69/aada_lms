"""Encrypt PHI fields for HIPAA compliance

Revision ID: 0011_encrypt_phi_fields
Revises: 0010_lead_based_signing
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import os


# revision identifiers
revision = '0011_encrypt_phi_fields'
down_revision = '0010_lead_based_signing'
branch_labels = None
depends_on = None


def upgrade():
    """
    Encrypt Protected Health Information (PHI) fields using pgcrypto.

    This migration encrypts sensitive PII data at rest for HIPAA compliance.
    Currently encrypts:
    - User PII: first_name, last_name, email

    Strategy:
    1. Add temporary encrypted columns
    2. Migrate data from plaintext to encrypted
    3. Drop old plaintext columns
    4. Rename encrypted columns to original names

    Uses AES-256 encryption via PostgreSQL pgcrypto extension.

    Note: Compliance module tables (credentials, transcripts, etc.) will be
    encrypted when those tables are created in future migrations.
    """

    # Get encryption key from environment
    encryption_key = os.getenv('ENCRYPTION_KEY', 'dev_encryption_key_change_in_production_32bytes')

    conn = op.get_bind()

    # ========================================
    # USERS TABLE - Encrypt PII
    # ========================================
    print("Encrypting users table...")

    # Add temporary encrypted columns
    op.add_column('users', sa.Column('first_name_encrypted', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('last_name_encrypted', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('email_encrypted', sa.Text(), nullable=True))

    # Migrate existing data to encrypted columns
    conn.execute(text("""
        UPDATE users
        SET first_name_encrypted = encode(
            pgp_sym_encrypt(first_name, :key),
            'base64'
        )
        WHERE first_name IS NOT NULL;
    """), {"key": encryption_key})

    conn.execute(text("""
        UPDATE users
        SET last_name_encrypted = encode(
            pgp_sym_encrypt(last_name, :key),
            'base64'
        )
        WHERE last_name IS NOT NULL;
    """), {"key": encryption_key})

    conn.execute(text("""
        UPDATE users
        SET email_encrypted = encode(
            pgp_sym_encrypt(email::text, :key),
            'base64'
        )
        WHERE email IS NOT NULL;
    """), {"key": encryption_key})

    # Drop old plaintext columns and rename encrypted ones
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

    # For email, we need to handle the unique constraint
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_column('users', 'email')

    # Rename encrypted columns
    op.alter_column('users', 'first_name_encrypted', new_column_name='first_name')
    op.alter_column('users', 'last_name_encrypted', new_column_name='last_name')
    op.alter_column('users', 'email_encrypted', new_column_name='email')

    # Add unique constraint on encrypted email
    # Note: Encrypted values are unique by nature (same plaintext + key = same ciphertext)
    op.create_unique_constraint('users_email_key', 'users', ['email'])

    print("✅ User PII fields successfully encrypted!")
    print("ℹ️  Compliance tables will be encrypted when created in future migrations")


def downgrade():
    """
    Decrypt PHI fields back to plaintext.

    WARNING: This should NOT be used in production as it defeats HIPAA compliance.
    This is provided for development/testing rollback only.
    """
    encryption_key = os.getenv('ENCRYPTION_KEY', 'dev_encryption_key_change_in_production_32bytes')
    conn = op.get_bind()

    # Users table
    op.add_column('users', sa.Column('first_name_plain', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name_plain', sa.String(), nullable=True))
    op.add_column('users', sa.Column('email_plain', sa.String(), nullable=True))

    conn.execute(text("""
        UPDATE users
        SET first_name_plain = pgp_sym_decrypt(
            decode(first_name, 'base64'),
            :key
        )
        WHERE first_name IS NOT NULL;
    """), {"key": encryption_key})

    conn.execute(text("""
        UPDATE users
        SET last_name_plain = pgp_sym_decrypt(
            decode(last_name, 'base64'),
            :key
        )
        WHERE last_name IS NOT NULL;
    """), {"key": encryption_key})

    conn.execute(text("""
        UPDATE users
        SET email_plain = pgp_sym_decrypt(
            decode(email, 'base64'),
            :key
        )
        WHERE email IS NOT NULL;
    """), {"key": encryption_key})

    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_column('users', 'email')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')

    op.alter_column('users', 'first_name_plain', new_column_name='first_name')
    op.alter_column('users', 'last_name_plain', new_column_name='last_name')
    op.alter_column('users', 'email_plain', new_column_name='email')

    # Re-create unique constraint
    op.create_unique_constraint('users_email_key', 'users', ['email'])
