"""添加actor_subscribe作品数量缓存字段

Revision ID: 6c0e6afce80e
Revises: 023d19661374
Create Date: 2025-11-13 19:34:17.089052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '6c0e6afce80e'
down_revision: Union[str, None] = '023d19661374'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 获取数据库连接和检查器
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # 检查表是否存在
    if 'actor_subscribe' in inspector.get_table_names():
        # 获取现有列
        existing_columns = [col['name'] for col in inspector.get_columns('actor_subscribe')]

        # 只在列不存在时添加
        if 'subscribed_works_count' not in existing_columns:
            op.add_column('actor_subscribe',
                sa.Column('subscribed_works_count', sa.Integer(), nullable=True, server_default='0', comment='订阅作品总数（缓存）'))

        if 'works_count_updated_at' not in existing_columns:
            op.add_column('actor_subscribe',
                sa.Column('works_count_updated_at', sa.DateTime(), nullable=True, comment='作品数量更新时间'))


def downgrade() -> None:
    # 删除添加的列
    op.drop_column('actor_subscribe', 'works_count_updated_at')
    op.drop_column('actor_subscribe', 'subscribed_works_count')
