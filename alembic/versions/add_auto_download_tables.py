"""添加自动下载表

Revision ID: add_auto_download_tables
Revises: 0eb776dce68b
Create Date: 2025-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_auto_download_tables'
down_revision = '0eb776dce68b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 检查表是否已存在，避免重复创建
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # 只在表不存在时创建 auto_download_rules
    if 'auto_download_rules' not in existing_tables:
        op.create_table('auto_download_rules',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('min_rating', sa.DECIMAL(precision=3, scale=1), nullable=True, default=0.0),
            sa.Column('min_comments', sa.Integer(), nullable=True, default=0),
            sa.Column('time_range_type', sa.Enum('day', 'week', 'month', name='time_range_type'), nullable=True, default='week'),
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
        
        # 只在表创建后才创建索引
        op.create_index('idx_auto_download_rules_enabled', 'auto_download_rules', ['is_enabled'])
    
    # 只在表不存在时创建 auto_download_subscriptions
    if 'auto_download_subscriptions' not in existing_tables:
        op.create_table('auto_download_subscriptions',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('rule_id', sa.Integer(), nullable=False),
            sa.Column('num', sa.String(length=50), nullable=False),
            sa.Column('title', sa.String(length=500), nullable=True),
            sa.Column('rating', sa.DECIMAL(precision=3, scale=1), nullable=True),
            sa.Column('comments_count', sa.Integer(), nullable=True, default=0),
            sa.Column('cover', sa.String(length=500), nullable=True),
            sa.Column('actors', sa.Text(), nullable=True),
            sa.Column('status', sa.Enum('pending', 'downloading', 'completed', 'failed', name='download_status'), nullable=True, default='pending'),
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
        
        # 只在表创建后才创建索引
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
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS download_status')
    op.execute('DROP TYPE IF EXISTS time_range_type')