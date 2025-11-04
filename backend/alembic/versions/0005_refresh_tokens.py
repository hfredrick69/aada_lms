"""Add refresh tokens table

Revision ID: 0005_refresh_tokens
Revises: 0004_audit_logging
Create Date: 2025-11-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '0005_refresh_tokens'
down_revision = '0004_audit_logging'
branch_labels = None
depends_on = None


def upgrade():
    """Create refresh_tokens table for JWT token refresh pattern."""
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoke_reason', sa.String(length=200), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('replaced_by_token_id', sa.String(), nullable=True),
        sa.Column('use_count', sa.String(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token_hash')
    )

    # Create indexes for efficient querying
    op.create_index('idx_refresh_user_active', 'refresh_tokens', ['user_id', 'is_revoked', 'expires_at'])
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'])
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'])
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'])
    op.create_index(op.f('ix_refresh_tokens_is_revoked'), 'refresh_tokens', ['is_revoked'])


def downgrade():
    """Drop refresh_tokens table and indexes."""
    op.drop_index(op.f('ix_refresh_tokens_is_revoked'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index('idx_refresh_user_active', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
