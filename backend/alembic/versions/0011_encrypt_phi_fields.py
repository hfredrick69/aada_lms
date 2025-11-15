"""placeholder for removed migration

Revision ID: 0011_encrypt_phi_fields
Revises: 0008_module_progress_tracking
Create Date: 2025-11-11 00:00:00
"""

from alembic import op  # noqa
import sqlalchemy as sa  # noqa


revision = '0011_encrypt_phi_fields'
down_revision = '0008_module_progress_tracking'
branch_labels = None
depends_on = None


def upgrade():
    """Legacy migration removed - placeholder keeps revision chain intact."""
    pass


def downgrade():
    """Legacy migration removed - placeholder keeps revision chain intact."""
    pass
