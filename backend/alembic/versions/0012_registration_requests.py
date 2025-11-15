"""registration requests table

Revision ID: 0012_registration_requests
Revises: 0001_init
Create Date: 2025-11-11 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0012_registration_requests'
down_revision = '0011_encrypt_phi_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'registration_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('email_hash', sa.String(length=64), nullable=False),
        sa.Column('token_hash', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('request_ip', sa.String(length=64)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index(
        'ix_registration_requests_email_hash',
        'registration_requests',
        ['email_hash'],
        unique=False
    )


def downgrade():
    op.drop_index('ix_registration_requests_email_hash', table_name='registration_requests')
    op.drop_table('registration_requests')
