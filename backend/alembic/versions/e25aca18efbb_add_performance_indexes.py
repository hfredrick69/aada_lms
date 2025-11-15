"""add_performance_indexes

Revision ID: e25aca18efbb
Revises: 0b0be0cca7b5
Create Date: 2025-11-15 12:25:29.488790

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e25aca18efbb'
down_revision: Union[str, None] = '0b0be0cca7b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Foreign key indexes for faster joins
    op.create_index(
        'idx_enrollments_user_id',
        'enrollments',
        ['user_id'],
        if_not_exists=True
    )
    op.create_index(
        'idx_enrollments_program_id',
        'enrollments',
        ['program_id'],
        if_not_exists=True
    )
    op.create_index(
        'idx_refresh_tokens_user_id',
        'refresh_tokens',
        ['user_id'],
        if_not_exists=True
    )
    op.create_index(
        'idx_audit_logs_user_id',
        'audit_logs',
        ['user_id'],
        if_not_exists=True
    )
    op.create_index(
        'idx_signed_documents_user_id',
        'signed_documents',
        ['user_id'],
        if_not_exists=True
    )

    # Filtered column indexes for common WHERE clauses
    op.create_index(
        'idx_users_status',
        'users',
        ['status'],
        if_not_exists=True
    )
    op.create_index(
        'idx_enrollments_status',
        'enrollments',
        ['status'],
        if_not_exists=True
    )
    op.create_index(
        'idx_payments_status',
        'payments',
        ['status'],
        if_not_exists=True
    )

    # Composite indexes for common query patterns
    op.create_index(
        'idx_enrollments_user_program',
        'enrollments',
        ['user_id', 'program_id'],
        if_not_exists=True
    )
    op.create_index(
        'idx_audit_logs_user_created',
        'audit_logs',
        ['user_id', 'created_at'],
        if_not_exists=True
    )

    # XAPI JSONB index for faster JSONB queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_xapi_actor_gin
        ON xapi_statements USING gin (actor)
    """)


def downgrade() -> None:
    # Drop all indexes in reverse order
    op.execute("DROP INDEX IF EXISTS idx_xapi_actor_gin")
    op.drop_index('idx_audit_logs_user_created', 'audit_logs')
    op.drop_index('idx_enrollments_user_program', 'enrollments')
    op.drop_index('idx_payments_status', 'payments')
    op.drop_index('idx_enrollments_status', 'enrollments')
    op.drop_index('idx_users_status', 'users')
    op.drop_index('idx_signed_documents_user_id', 'signed_documents')
    op.drop_index('idx_audit_logs_user_id', 'audit_logs')
    op.drop_index('idx_refresh_tokens_user_id', 'refresh_tokens')
    op.drop_index('idx_enrollments_program_id', 'enrollments')
    op.drop_index('idx_enrollments_user_id', 'enrollments')
