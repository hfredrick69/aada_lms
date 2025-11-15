"""Add document e-signature tables

Revision ID: 0009
Revises: 0008
Create Date: 2025-11-07

This migration adds tables for digital document signing (enrollment agreements).
Provides legally compliant e-signature workflow with full audit trail.

Tables added:
- document_templates: Document templates (enrollment agreement, etc.)
- signed_documents: Document instances sent to students
- document_signatures: Individual signatures with audit data
- document_audit_logs: Complete audit trail for legal compliance
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0009_document_esignature'
down_revision = '0008_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Create document e-signature tables"""

    # Document Templates
    op.create_table(
        'document_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('requires_counter_signature', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Signed Documents
    op.create_table(
        'signed_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('unsigned_file_path', sa.String(length=500), nullable=True),
        sa.Column('signed_file_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('student_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('student_signed_at', sa.DateTime(), nullable=True),
        sa.Column('counter_signed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['document_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Document Signatures
    op.create_table(
        'document_signatures',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signature_type', sa.String(length=50), nullable=False),
        sa.Column('signature_data', sa.Text(), nullable=False),
        sa.Column('signed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=False),
        sa.Column('typed_name', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['signed_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signer_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Document Audit Logs
    op.create_table(
        'document_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_details', sa.Text(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['signed_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_signed_documents_template_id', 'signed_documents', ['template_id'])
    op.create_index('idx_signed_documents_user_id', 'signed_documents', ['user_id'])
    op.create_index('idx_signed_documents_status', 'signed_documents', ['status'])
    op.create_index('idx_signed_documents_user_status', 'signed_documents', ['user_id', 'status'])

    op.create_index('idx_document_signatures_document_id', 'document_signatures', ['document_id'])
    op.create_index('idx_document_signatures_signer_id', 'document_signatures', ['signer_id'])

    op.create_index('idx_document_audit_logs_document_id', 'document_audit_logs', ['document_id'])
    op.create_index('idx_document_audit_logs_occurred_at', 'document_audit_logs',
                    ['occurred_at'], postgresql_ops={'occurred_at': 'DESC'})


def downgrade():
    """Drop document e-signature tables"""

    # Drop indexes
    op.drop_index('idx_document_audit_logs_occurred_at', table_name='document_audit_logs')
    op.drop_index('idx_document_audit_logs_document_id', table_name='document_audit_logs')

    op.drop_index('idx_document_signatures_signer_id', table_name='document_signatures')
    op.drop_index('idx_document_signatures_document_id', table_name='document_signatures')

    op.drop_index('idx_signed_documents_user_status', table_name='signed_documents')
    op.drop_index('idx_signed_documents_status', table_name='signed_documents')
    op.drop_index('idx_signed_documents_user_id', table_name='signed_documents')
    op.drop_index('idx_signed_documents_template_id', table_name='signed_documents')

    # Drop tables
    op.drop_table('document_audit_logs')
    op.drop_table('document_signatures')
    op.drop_table('signed_documents')
    op.drop_table('document_templates')
