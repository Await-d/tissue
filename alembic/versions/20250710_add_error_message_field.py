"""添加error_message字段到auto_download_subscriptions表

Revision ID: 20250710_add_error_message
Revises: 20250710_add_resource_hash
Create Date: 2025-07-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250710_add_error_message'
down_revision: Union[str, None] = '20250710_add_resource_hash'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 检查auto_download_subscriptions表是否存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'auto_download_subscriptions' in tables:
        # 检查error_message字段是否已经存在
        columns = [col['name'] for col in inspector.get_columns('auto_download_subscriptions')]
        if 'error_message' not in columns:
            # 添加error_message字段
            op.add_column('auto_download_subscriptions', 
                         sa.Column('error_message', sa.String(1000), nullable=True, 
                                   comment="错误信息"))


def downgrade() -> None:
    # 检查auto_download_subscriptions表是否存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'auto_download_subscriptions' in tables:
        # 检查error_message字段是否存在
        columns = [col['name'] for col in inspector.get_columns('auto_download_subscriptions')]
        if 'error_message' in columns:
            # 删除字段
            op.drop_column('auto_download_subscriptions', 'error_message')