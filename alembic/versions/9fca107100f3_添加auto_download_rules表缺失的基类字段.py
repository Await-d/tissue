"""添加auto_download_rules表缺失的基类字段

Revision ID: 9fca107100f3
Revises: add_auto_download_tables
Create Date: 2025-07-07 16:50:43.639462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fca107100f3'
down_revision: Union[str, None] = 'add_auto_download_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 检查列是否已存在，避免重复添加
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # 获取 auto_download_rules 表的列信息
    rules_columns = [col['name'] for col in inspector.get_columns('auto_download_rules')]
    
    # 为 auto_download_rules 表添加缺失的基类字段
    if 'create_by' not in rules_columns:
        op.add_column('auto_download_rules', sa.Column('create_by', sa.Integer(), nullable=True))
    
    if 'create_time' not in rules_columns:
        op.add_column('auto_download_rules', sa.Column('create_time', sa.DateTime(), nullable=True))
    
    if 'update_by' not in rules_columns:
        op.add_column('auto_download_rules', sa.Column('update_by', sa.Integer(), nullable=True))
    
    if 'update_time' not in rules_columns:
        op.add_column('auto_download_rules', sa.Column('update_time', sa.DateTime(), nullable=True))
    
    # 获取 auto_download_subscriptions 表的列信息
    subscriptions_columns = [col['name'] for col in inspector.get_columns('auto_download_subscriptions')]
    
    # 为 auto_download_subscriptions 表添加缺失的基类字段
    if 'create_by' not in subscriptions_columns:
        op.add_column('auto_download_subscriptions', sa.Column('create_by', sa.Integer(), nullable=True))
    
    if 'create_time' not in subscriptions_columns:
        op.add_column('auto_download_subscriptions', sa.Column('create_time', sa.DateTime(), nullable=True))
    
    if 'update_by' not in subscriptions_columns:
        op.add_column('auto_download_subscriptions', sa.Column('update_by', sa.Integer(), nullable=True))
    
    if 'update_time' not in subscriptions_columns:
        op.add_column('auto_download_subscriptions', sa.Column('update_time', sa.DateTime(), nullable=True))  # 字段可能已存在


def downgrade() -> None:
    # 删除添加的基类字段
    try:
        op.drop_column('auto_download_rules', 'create_by')
        op.drop_column('auto_download_rules', 'create_time')
        op.drop_column('auto_download_rules', 'update_by')
        op.drop_column('auto_download_rules', 'update_time')
    except Exception:
        pass
    
    try:
        op.drop_column('auto_download_subscriptions', 'create_by')
        op.drop_column('auto_download_subscriptions', 'create_time')
        op.drop_column('auto_download_subscriptions', 'update_by')
        op.drop_column('auto_download_subscriptions', 'update_time')
    except Exception:
        pass
