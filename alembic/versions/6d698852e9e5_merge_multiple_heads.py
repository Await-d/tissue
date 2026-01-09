"""merge multiple heads

Revision ID: 6d698852e9e5
Revises: 20250710_add_resource_hash, 20250109_fix_torrent
Create Date: 2025-07-10 12:11:40.537272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d698852e9e5'
down_revision: Union[str, None] = ('20250710_add_resource_hash', '20250109_fix_torrent')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
