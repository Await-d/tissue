"""merge scan_record and other branches

Revision ID: 6ae1b844eb75
Revises: 20260111_scan_record, fa1714ef03b6
Create Date: 2026-01-11 02:16:27.043659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae1b844eb75'
down_revision: Union[str, None] = ('20260111_scan_record', 'fa1714ef03b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
