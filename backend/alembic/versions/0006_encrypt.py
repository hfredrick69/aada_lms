"""Enable encryption infrastructure

Revision ID: 0006_encrypt
Revises: 0005_refresh_tokens
Create Date: 2025-11-04

"""
from alembic import op


# revision identifiers
revision = '0006_encrypt'
down_revision = '0005_refresh_tokens'
branch_labels = None
depends_on = None


def upgrade():
    """
    Enable PostgreSQL pgcrypto extension for HIPAA-compliant encryption at rest.

    This provides the infrastructure for encrypting PHI (Protected Health Information)
    data in the database using AES-256 encryption.
    """
    # Enable pgcrypto extension (idempotent - safe if already exists)
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Note: Actual column encryption will be implemented incrementally
    # to avoid disrupting existing data. This migration establishes
    # the encryption capability.


def downgrade():
    """Disable pgcrypto extension (use with caution in production)."""
    # Note: In production, you may want to keep the extension even on downgrade
    # as removing it will break any encrypted columns
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
