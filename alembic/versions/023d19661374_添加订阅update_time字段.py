"""添加订阅update_time字段

Revision ID: 023d19661374
Revises: 05d731c03662
Create Date: 2025-11-13 18:31:06.764284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '023d19661374'
down_revision: Union[str, None] = '05d731c03662'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('subscribe', sa.Column('update_time', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('subscribe', 'update_time')
