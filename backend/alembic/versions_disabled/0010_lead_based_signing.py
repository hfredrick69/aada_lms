"""Lead-based signing support

Revision ID: 0010_lead_based_signing
Revises: 0009_document_esignature
Create Date: 2025-01-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0010_lead_based_signing'
down_revision = '0009_document_esignature'
branch_labels = None
depends_on = None


def upgrade():
    # Alter signed_documents table
    op.alter_column('signed_documents', 'user_id',
                    existing_type=postgresql.UUID(),
                    nullable=True)

    op.add_column('signed_documents', sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('signed_documents', sa.Column('signer_name', sa.String(length=255), nullable=True))
    op.add_column('signed_documents', sa.Column('signer_email', sa.String(length=255), nullable=True))
    op.add_column('signed_documents', sa.Column('signing_token', sa.String(length=255), nullable=True))
    op.add_column('signed_documents', sa.Column('token_expires_at', sa.DateTime(), nullable=True))

    # Add foreign key to leads
    op.create_foreign_key(
        'fk_signed_documents_lead_id',
        'signed_documents', 'leads',
        ['lead_id'], ['id'],
        source_schema=None,
        referent_schema='crm'
    )

    # Add unique constraint and index on signing_token for performance
    op.create_index('ix_signed_documents_signing_token', 'signed_documents', ['signing_token'], unique=True)

    # Add check constraint to ensure either user_id OR lead_id is set
    op.execute("""
        ALTER TABLE signed_documents
        ADD CONSTRAINT chk_signed_documents_user_or_lead
        CHECK (
            (user_id IS NOT NULL AND lead_id IS NULL) OR
            (user_id IS NULL AND lead_id IS NOT NULL)
        )
    """)

    # Alter document_signatures table
    op.alter_column('document_signatures', 'signer_id',
                    existing_type=postgresql.UUID(),
                    nullable=True)

    op.alter_column('document_signatures', 'typed_name',
                    existing_type=sa.String(length=255),
                    nullable=False)

    op.add_column('document_signatures', sa.Column('signer_email', sa.String(length=255), nullable=True))


def downgrade():
    # Remove columns from document_signatures
    op.drop_column('document_signatures', 'signer_email')

    op.alter_column('document_signatures', 'typed_name',
                    existing_type=sa.String(length=255),
                    nullable=True)

    op.alter_column('document_signatures', 'signer_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)

    # Remove check constraint
    op.execute("ALTER TABLE signed_documents DROP CONSTRAINT IF EXISTS chk_signed_documents_user_or_lead")

    # Remove index and columns from signed_documents
    op.drop_index('ix_signed_documents_signing_token', table_name='signed_documents')

    op.drop_constraint('fk_signed_documents_lead_id', 'signed_documents', type_='foreignkey')

    op.drop_column('signed_documents', 'token_expires_at')
    op.drop_column('signed_documents', 'signing_token')
    op.drop_column('signed_documents', 'signer_email')
    op.drop_column('signed_documents', 'signer_name')
    op.drop_column('signed_documents', 'lead_id')

    op.alter_column('signed_documents', 'user_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
