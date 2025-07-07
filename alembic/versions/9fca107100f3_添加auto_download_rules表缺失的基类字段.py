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
    # 为auto_download_rules表添加缺失的基类字段
    try:
        op.add_column('auto_download_rules', sa.Column('create_by', sa.Integer(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    try:
        op.add_column('auto_download_rules', sa.Column('create_time', sa.DateTime(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    try:
        op.add_column('auto_download_rules', sa.Column('update_by', sa.Integer(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    try:
        op.add_column('auto_download_rules', sa.Column('update_time', sa.DateTime(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    # 为auto_download_subscriptions表添加缺失的基类字段
    try:
        op.add_column('auto_download_subscriptions', sa.Column('create_by', sa.Integer(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    try:
        op.add_column('auto_download_subscriptions', sa.Column('create_time', sa.DateTime(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    try:
        op.add_column('auto_download_subscriptions', sa.Column('update_by', sa.Integer(), nullable=True))
    except Exception:
        pass  # 字段可能已存在
    
    try:
        op.add_column('auto_download_subscriptions', sa.Column('update_time', sa.DateTime(), nullable=True))
    except Exception:
        pass  # 字段可能已存在


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
