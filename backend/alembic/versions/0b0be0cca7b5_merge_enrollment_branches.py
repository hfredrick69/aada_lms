"""merge enrollment branches

Revision ID: 0b0be0cca7b5
Revises: 0012_enrollment_agreement_fields, 0012_registration_requests
Create Date: 2025-11-14 23:44:56.277150

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '0b0be0cca7b5'
down_revision: Union[str, None] = ('0012_enrollment_agreement_fields', '0012_registration_requests')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
