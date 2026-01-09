"""添加订阅状态字段

Revision ID: 9135e6d48625
Revises: 296fa8c2261d
Create Date: 2025-06-21 23:12:32.519524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = '9135e6d48625'
down_revision: Union[str, None] = '296fa8c2261d'
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
        if 'status' not in existing_columns:
            op.add_column('subscribe', sa.Column('status', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    # 获取数据库连接和检查器
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # 检查表和列是否存在
    if 'subscribe' in inspector.get_table_names():
        existing_columns = [col['name'] for col in inspector.get_columns('subscribe')]
        if 'status' in existing_columns:
            op.drop_column('subscribe', 'status')
