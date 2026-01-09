"""添加订阅update_time字段

Revision ID: 023d19661374
Revises: 05d731c03662
Create Date: 2025-11-13 18:31:06.764284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '023d19661374'
down_revision: Union[str, None] = '05d731c03662'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 获取数据库连接和检查器
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # 检查表是否存在
    if 'subscribe' in inspector.get_table_names():
        # 获取现有列
        existing_columns = [col['name'] for col in inspector.get_columns('subscribe')]

        # 只在列不存在时添加
        if 'update_time' not in existing_columns:
            op.add_column('subscribe', sa.Column('update_time', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # 获取数据库连接和检查器
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # 检查表和列是否存在
    if 'subscribe' in inspector.get_table_names():
        existing_columns = [col['name'] for col in inspector.get_columns('subscribe')]
        if 'update_time' in existing_columns:
            op.drop_column('subscribe', 'update_time')
