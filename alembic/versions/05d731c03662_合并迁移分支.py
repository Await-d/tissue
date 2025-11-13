"""合并迁移分支

Revision ID: 05d731c03662
Revises: 383104710481, dbd2ca9e6501
Create Date: 2025-11-13 18:30:55.220405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05d731c03662'
down_revision: Union[str, None] = ('383104710481', 'dbd2ca9e6501')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
