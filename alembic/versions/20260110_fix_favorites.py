"""修复收藏夹（空迁移，用于解决版本不匹配问题）

Revision ID: 20260110_fix_favorites
Revises: 7c9ba4d939cf
Create Date: 2026-01-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260110_fix_favorites'
down_revision: Union[str, None] = '7c9ba4d939cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
