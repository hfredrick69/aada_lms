"""add_login_rate_limiting

Revision ID: a30190520a19
Revises: e25aca18efbb
Create Date: 2025-11-15 13:18:32.089312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a30190520a19'
down_revision: Union[str, None] = 'e25aca18efbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add login_attempts table for brute-force protection"""
    op.create_table(
        'login_attempts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email_hash', sa.String(length=64), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('attempted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Index for fast lookups by email hash and time
    op.create_index(
        'idx_login_attempts_email_time',
        'login_attempts',
        ['email_hash', 'attempted_at'],
        if_not_exists=True
    )

    # Index for cleanup queries
    op.create_index(
        'idx_login_attempts_time',
        'login_attempts',
        ['attempted_at'],
        if_not_exists=True
    )


def downgrade() -> None:
    """Remove login_attempts table"""
    op.drop_index('idx_login_attempts_time', 'login_attempts', if_exists=True)
    op.drop_index('idx_login_attempts_email_time', 'login_attempts', if_exists=True)
    op.drop_table('login_attempts')
