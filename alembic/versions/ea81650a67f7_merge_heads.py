"""merge_heads

Revision ID: ea81650a67f7
Revises: 20250710_add_error_message, 6d698852e9e5
Create Date: 2025-07-10 09:04:49.476890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea81650a67f7'
down_revision: Union[str, None] = ('20250710_add_error_message', '6d698852e9e5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
