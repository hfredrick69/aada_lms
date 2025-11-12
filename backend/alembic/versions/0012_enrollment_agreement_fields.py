"""add course metadata to signed documents

Revision ID: 0012_enrollment_agreement_fields
Revises: 0011_encrypt_phi_fields
Create Date: 2025-11-12 19:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0012_enrollment_agreement_fields"
down_revision: Union[str, None] = "0011_encrypt_phi_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "signed_documents",
        sa.Column("course_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "signed_documents",
        sa.Column("form_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "signed_documents",
        sa.Column("retention_expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("signed_documents", "retention_expires_at")
    op.drop_column("signed_documents", "form_data")
    op.drop_column("signed_documents", "course_type")
