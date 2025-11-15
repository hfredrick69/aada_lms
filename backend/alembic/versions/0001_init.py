"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2025-10-28 00:00:00

"""
# flake8: noqa: E128, E501
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # users
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='active')
    )

    # programs
    op.create_table('programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('credential_level', sa.String(), nullable=False),
        sa.Column('total_clock_hours', sa.Integer(), nullable=False)
    )

    # modules
    op.create_table('modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id', ondelete="CASCADE")),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('delivery_type', sa.String(), nullable=False),
        sa.Column('clock_hours', sa.Integer(), nullable=False),
        sa.Column('requires_in_person', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('position', sa.Integer(), nullable=False)
    )

    # enrollments
    op.create_table('enrollments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id', ondelete="CASCADE")),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('expected_end_date', sa.Date()),
        sa.Column('status', sa.String(), server_default='active')
    )

    # module_progress
    op.create_table('module_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('enrollments.id', ondelete="CASCADE")),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('modules.id', ondelete="CASCADE")),
        sa.Column('scorm_status', sa.String()),
        sa.Column('score', sa.Integer()),
        sa.Column('progress_pct', sa.Integer())
    )

    # xapi statements
    op.create_table('xapi_statements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor', postgresql.JSONB(), nullable=False),
        sa.Column('verb', postgresql.JSONB(), nullable=False),
        sa.Column('object', postgresql.JSONB(), nullable=False),
        sa.Column('result', postgresql.JSONB()),
        sa.Column('context', postgresql.JSONB()),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('stored_at', sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"))
    )

    # scorm_records
    op.create_table('scorm_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('modules.id', ondelete="CASCADE")),
        sa.Column('lesson_status', sa.String()),
        sa.Column('score_scaled', sa.Numeric(4, 3)),
        sa.Column('score_raw', sa.Numeric(6, 2)),
        sa.Column('session_time', sa.String()),
        sa.Column('interactions', postgresql.JSONB())
    )


def downgrade():
    op.drop_table('scorm_records')
    op.drop_table('xapi_statements')
    op.drop_table('module_progress')
    op.drop_table('enrollments')
    op.drop_table('modules')
    op.drop_table('programs')
    op.drop_table('users')
