"""Add audit logging table

Revision ID: 0004_audit_logging
Revises: 0003_auth_roles
Create Date: 2025-01-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '0004_audit_logging'
down_revision = '0003_auth_roles'
branch_labels = None
depends_on = None


def upgrade():
    """Create audit_logs table for HIPAA compliance tracking."""
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('user_email', sa.String(), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column(
            'timestamp',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('request_size', sa.Integer(), nullable=True),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.Column('is_phi_access', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('query_params', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient querying
    op.create_index('idx_audit_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_phi_timestamp', 'audit_logs', ['is_phi_access', 'timestamp'])
    op.create_index('idx_audit_status_timestamp', 'audit_logs', ['status_code', 'timestamp'])
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])
    op.create_index(op.f('ix_audit_logs_path'), 'audit_logs', ['path'])
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'])
    op.create_index(op.f('ix_audit_logs_status_code'), 'audit_logs', ['status_code'])
    op.create_index(op.f('ix_audit_logs_is_phi_access'), 'audit_logs', ['is_phi_access'])


def downgrade():
    """Drop audit_logs table and indexes."""
    op.drop_index(op.f('ix_audit_logs_is_phi_access'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_status_code'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_path'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index('idx_audit_status_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_phi_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_user_timestamp', table_name='audit_logs')
    op.drop_table('audit_logs')
