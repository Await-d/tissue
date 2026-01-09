"""添加resource_hash字段到auto_download_subscriptions表

Revision ID: 20250710_add_resource_hash
Revises: 16cd43a26d05
Create Date: 2025-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250710_add_resource_hash'
down_revision: Union[str, None] = '16cd43a26d05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 检查auto_download_subscriptions表是否存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'auto_download_subscriptions' in tables:
        # 检查resource_hash字段是否已经存在
        columns = [col['name'] for col in inspector.get_columns('auto_download_subscriptions')]
        if 'resource_hash' not in columns:
            # 添加resource_hash字段
            op.add_column('auto_download_subscriptions', 
                         sa.Column('resource_hash', sa.String(64), nullable=True, 
                                   comment="资源唯一标识（用于重复检测）"))
            
            # 创建索引
            op.create_index('ix_auto_download_subscriptions_resource_hash', 
                           'auto_download_subscriptions', ['resource_hash'])


def downgrade() -> None:
    # 检查auto_download_subscriptions表是否存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'auto_download_subscriptions' in tables:
        # 检查resource_hash字段是否存在
        columns = [col['name'] for col in inspector.get_columns('auto_download_subscriptions')]
        if 'resource_hash' in columns:
            # 删除索引
            op.drop_index('ix_auto_download_subscriptions_resource_hash', 
                         table_name='auto_download_subscriptions')
            
            # 删除字段
            op.drop_column('auto_download_subscriptions', 'resource_hash')