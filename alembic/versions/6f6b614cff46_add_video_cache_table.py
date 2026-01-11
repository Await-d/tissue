"""add_video_cache_table

Revision ID: 6f6b614cff46
Revises: 6c0e6afce80e
Create Date: 2025-11-14 19:27:32.035204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '6f6b614cff46'
down_revision: Union[str, None] = '6c0e6afce80e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_existing_tables():
    """获取数据库中已存在的表列表"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return inspector.get_table_names()


def get_existing_indexes(table_name):
    """获取指定表的索引列表"""
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        return [idx['name'] for idx in inspector.get_indexes(table_name)]
    except Exception:
        return []


def safe_drop_index(index_name, table_name):
    """安全删除索引（如果存在）"""
    existing_indexes = get_existing_indexes(table_name)
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    existing_tables = get_existing_tables()

    # 只在表不存在时创建 video_cache 表
    if 'video_cache' not in existing_tables:
        op.create_table('video_cache',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
            sa.Column('num', sa.String(length=50), nullable=False, comment='视频番号'),
            sa.Column('title', sa.String(length=500), nullable=True, comment='视频标题'),
            sa.Column('cover', sa.String(length=500), nullable=True, comment='封面图片URL'),
            sa.Column('url', sa.String(length=500), nullable=True, comment='视频详情页URL'),
            sa.Column('rating', sa.Float(), nullable=True, comment='评分 (0-5)'),
            sa.Column('comments_count', sa.Integer(), nullable=True, comment='评论数'),
            sa.Column('release_date', sa.String(length=20), nullable=True, comment='发布日期 YYYY-MM-DD'),
            sa.Column('is_hd', sa.Boolean(), nullable=True, comment='是否高清'),
            sa.Column('is_zh', sa.Boolean(), nullable=True, comment='是否中文字幕'),
            sa.Column('is_uncensored', sa.Boolean(), nullable=True, comment='是否无码'),
            sa.Column('actors', sa.JSON(), nullable=True, comment='演员列表 [{"id": "xxx", "name": "xxx"}]'),
            sa.Column('tags', sa.JSON(), nullable=True, comment='标签列表 ["tag1", "tag2"]'),
            sa.Column('magnets', sa.JSON(), nullable=True, comment='磁力链接列表 [{"title": "xxx", "link": "magnet:..."}]'),
            sa.Column('source', sa.String(length=50), nullable=False, comment='数据来源: JavDB, JavBus等'),
            sa.Column('video_type', sa.String(length=20), nullable=True, comment='视频类型: censored, uncensored'),
            sa.Column('cycle', sa.String(length=20), nullable=True, comment='榜单周期: daily, weekly, monthly'),
            sa.Column('rank_position', sa.Integer(), nullable=True, comment='在榜单中的排名位置'),
            sa.Column('extra_data', sa.JSON(), nullable=True, comment='其他扩展数据'),
            sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
            sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
            sa.Column('fetched_at', sa.DateTime(), nullable=True, comment='抓取时间'),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            comment='视频缓存表 - 存储预抓取的排行榜视频数据'
        )
        op.create_index('idx_comments', 'video_cache', ['comments_count'], unique=False)
        op.create_index('idx_fetched_at', 'video_cache', ['fetched_at'], unique=False)
        op.create_index('idx_num', 'video_cache', ['num'], unique=False)
        op.create_index('idx_rating', 'video_cache', ['rating'], unique=False)
        op.create_index('idx_release_date', 'video_cache', ['release_date'], unique=False)
        op.create_index('idx_source_type_cycle', 'video_cache', ['source', 'video_type', 'cycle'], unique=False)


def downgrade() -> None:
    existing_tables = get_existing_tables()

    # 只在表存在时删除 video_cache 表
    if 'video_cache' in existing_tables:
        safe_drop_index('idx_source_type_cycle', 'video_cache')
        safe_drop_index('idx_release_date', 'video_cache')
        safe_drop_index('idx_rating', 'video_cache')
        safe_drop_index('idx_num', 'video_cache')
        safe_drop_index('idx_fetched_at', 'video_cache')
        safe_drop_index('idx_comments', 'video_cache')
        op.drop_table('video_cache')
