"""创建自动下载表结构完整版本

Revision ID: 16cd43a26d05
Revises: dc133c46bc0e
Create Date: 2025-07-07 20:46:43.987978

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16cd43a26d05'
down_revision: Union[str, None] = '55651a7bffa9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 检查auto_download_rules表是否存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'auto_download_rules' not in tables:
        # 创建自动下载规则表
        op.create_table('auto_download_rules',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('min_rating', sa.DECIMAL(precision=3, scale=1), nullable=True, default=0.0),
            sa.Column('min_comments', sa.Integer(), nullable=True, default=0),
            sa.Column('time_range_type', sa.Enum('day', 'week', 'month', name='timerangetype'), nullable=True, default='week'),
            sa.Column('time_range_value', sa.Integer(), nullable=True, default=1),
            sa.Column('is_hd', sa.Boolean(), nullable=False, default=True),
            sa.Column('is_zh', sa.Boolean(), nullable=False, default=False),
            sa.Column('is_uncensored', sa.Boolean(), nullable=False, default=False),
            sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        
        # 创建索引
        op.create_index('idx_auto_download_rules_enabled', 'auto_download_rules', ['is_enabled'])
    
    if 'auto_download_subscriptions' not in tables:
        # 创建自动下载订阅记录表
        op.create_table('auto_download_subscriptions',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('rule_id', sa.Integer(), nullable=False),
            sa.Column('num', sa.String(length=50), nullable=False),
            sa.Column('title', sa.String(length=500), nullable=True),
            sa.Column('rating', sa.DECIMAL(precision=3, scale=1), nullable=True),
            sa.Column('comments_count', sa.Integer(), nullable=True, default=0),
            sa.Column('cover', sa.String(length=500), nullable=True),
            sa.Column('actors', sa.Text(), nullable=True),
            sa.Column('status', sa.Enum('pending', 'downloading', 'completed', 'failed', name='downloadstatus'), nullable=True, default='pending'),
            sa.Column('download_url', sa.String(length=1000), nullable=True),
            sa.Column('download_time', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['rule_id'], ['auto_download_rules.id'], ondelete='CASCADE')
        )
        
        # 创建索引
        op.create_index('idx_auto_download_subscriptions_rule_id', 'auto_download_subscriptions', ['rule_id'])
        op.create_index('idx_auto_download_subscriptions_status', 'auto_download_subscriptions', ['status'])
        op.create_index('idx_auto_download_subscriptions_num', 'auto_download_subscriptions', ['num'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_auto_download_subscriptions_num', table_name='auto_download_subscriptions')
    op.drop_index('idx_auto_download_subscriptions_status', table_name='auto_download_subscriptions')
    op.drop_index('idx_auto_download_subscriptions_rule_id', table_name='auto_download_subscriptions')
    op.drop_index('idx_auto_download_rules_enabled', table_name='auto_download_rules')
    
    # 删除表
    op.drop_table('auto_download_subscriptions')
    op.drop_table('auto_download_rules')
