"""add module progress tracking fields

Revision ID: 0008_module_progress_tracking
Revises: 0007_crm_schema
Create Date: 2025-11-10 21:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0008_module_progress_tracking'
down_revision: Union[str, None] = '0007_crm_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('module_progress', sa.Column('last_scroll_position', sa.Integer(), server_default='0', nullable=False))
    op.add_column('module_progress', sa.Column('active_time_seconds', sa.Integer(), server_default='0', nullable=False))
    op.add_column('module_progress', sa.Column('sections_viewed', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False))
    op.add_column('module_progress', sa.Column('last_accessed_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.execute("UPDATE module_progress SET last_accessed_at = NOW() WHERE last_accessed_at IS NULL")
    op.alter_column('module_progress', 'last_scroll_position', server_default=None)
    op.alter_column('module_progress', 'active_time_seconds', server_default=None)
    op.alter_column('module_progress', 'sections_viewed', server_default=None)


def downgrade() -> None:
    op.drop_column('module_progress', 'last_accessed_at')
    op.drop_column('module_progress', 'sections_viewed')
    op.drop_column('module_progress', 'active_time_seconds')
    op.drop_column('module_progress', 'last_scroll_position')
