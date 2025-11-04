"""create compliance schema and tables

Revision ID: 0002_compliance
Revises: 0001_init
Create Date: 2025-10-28 00:15:00

"""
# flake8: noqa: E128, E501
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_compliance'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE SCHEMA IF NOT EXISTS compliance')

    op.create_table('attendance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('modules.id', ondelete="CASCADE")),
        sa.Column('session_type', sa.String(), nullable=False),
        sa.Column('session_ref', sa.String()),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('ended_at', sa.TIMESTAMP(timezone=True), nullable=False),
        schema='compliance'
    )

    op.create_table('skills_checkoffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('modules.id', ondelete="CASCADE")),
        sa.Column('skill_code', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('evaluator_name', sa.String()),
        sa.Column('evaluator_license', sa.String()),
        sa.Column('evidence_url', sa.Text()),
        sa.Column('signed_at', sa.TIMESTAMP(timezone=True)),
        schema='compliance'
    )

    op.create_table('externships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('site_name', sa.String(), nullable=False),
        sa.Column('site_address', sa.Text()),
        sa.Column('supervisor_name', sa.String()),
        sa.Column('supervisor_email', sa.String()),
        sa.Column('total_hours', sa.Integer(), server_default='0'),
        sa.Column('verified', sa.Boolean(), server_default='false'),
        sa.Column('verification_doc_url', sa.Text()),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True)),
        schema='compliance'
    )

    op.create_table('financial_ledgers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id', ondelete="SET NULL")),
        sa.Column('line_type', sa.String(), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        schema='compliance'
    )

    op.create_table('withdrawals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('enrollments.id', ondelete="CASCADE")),
        sa.Column('requested_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('admin_processed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('progress_pct_at_withdrawal', sa.Integer()),
        schema='compliance'
    )

    op.create_table('refunds',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('withdrawal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance.withdrawals.id', ondelete="CASCADE")),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('policy_basis', sa.Text()),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('remitted_at', sa.TIMESTAMP(timezone=True)),
        schema='compliance'
    )

    op.create_table('complaints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="SET NULL")),
        sa.Column('submitted_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('category', sa.String()),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), server_default='open'),
        sa.Column('resolution_notes', sa.Text()),
        sa.Column('resolution_at', sa.TIMESTAMP(timezone=True)),
        schema='compliance'
    )

    op.create_table('credentials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id', ondelete="CASCADE")),
        sa.Column('credential_type', sa.String(), nullable=False),
        sa.Column('issued_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('cert_serial', sa.String(), unique=True, nullable=False),
        schema='compliance'
    )

    op.create_table('transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete="CASCADE")),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id', ondelete="CASCADE")),
        sa.Column('gpa', sa.Numeric(3, 2)),
        sa.Column('generated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('pdf_url', sa.Text()),
        schema='compliance'
    )

    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('details', sa.Text()),
        sa.Column('occurred_at', sa.TIMESTAMP(timezone=True)),
        schema='compliance'
    )


def downgrade():
    op.drop_table('audit_logs', schema='compliance')
    op.drop_table('transcripts', schema='compliance')
    op.drop_table('credentials', schema='compliance')
    op.drop_table('complaints', schema='compliance')
    op.drop_table('refunds', schema='compliance')
    op.drop_table('withdrawals', schema='compliance')
    op.drop_table('financial_ledgers', schema='compliance')
    op.drop_table('externships', schema='compliance')
    op.drop_table('skills_checkoffs', schema='compliance')
    op.drop_table('attendance_logs', schema='compliance')
    op.execute('DROP SCHEMA IF EXISTS compliance CASCADE')
