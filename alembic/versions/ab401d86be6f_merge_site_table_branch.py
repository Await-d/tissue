"""merge_site_table_branch

Revision ID: ab401d86be6f
Revises: 6f6b614cff46, 7c9ba4d939cf
Create Date: 2026-01-09 21:59:31.486145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab401d86be6f'
down_revision: Union[str, None] = ('6f6b614cff46', '7c9ba4d939cf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
