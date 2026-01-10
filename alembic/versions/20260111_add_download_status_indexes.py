"""添加下载状态查询优化索引

此迁移脚本为 download_status 查询优化添加数据库索引。
这些索引将显著提升批量下载状态检查的性能。

涉及的表：
- torrent: 种子下载记录表
- actor_subscribe_download: 演员订阅下载记录表
- subscribe: 订阅记录表
- history: 历史记录表

索引用途：
1. 单字段索引用于快速查找特定番号
2. 组合索引用于同时过滤番号和状态的查询
3. SQLite 不支持函数索引，但单字段索引仍可加速 func.upper() 查询

Revision ID: 20260111_download_status_indexes
Revises: 20260110_fix_favorites
Create Date: 2026-01-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260111_download_status_indexes'
down_revision: Union[str, None] = '20260110_fix_favorites'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加下载状态查询所需的索引"""

    # 1. torrent 表索引
    # 用途：快速查询番号是否在种子下载记录中
    # 对应查询：func.upper(Torrent.num).in_(upper_nums)
    op.create_index(
        'idx_torrent_num',
        'torrent',
        ['num'],
        unique=False
    )

    # 2. actor_subscribe_download 表索引
    # 用途：快速查询番号是否在演员订阅下载记录中
    # 对应查询：func.upper(ActorSubscribeDownload.num).in_(upper_nums)
    op.create_index(
        'idx_actor_subscribe_download_num',
        'actor_subscribe_download',
        ['num'],
        unique=False
    )

    # 3. subscribe 表索引
    # 3.1 单独的 num 字段索引
    # 用途：加速基于番号的查询
    op.create_index(
        'idx_subscribe_num',
        'subscribe',
        ['num'],
        unique=False
    )

    # 3.2 num + status 组合索引
    # 用途：优化同时过滤番号和状态的查询（status=2 表示已完成）
    # 对应查询：func.upper(Subscribe.num).in_(upper_nums), Subscribe.status == 2
    # 注意：SQLite 中组合索引的顺序很重要，将过滤性强的字段放在前面
    op.create_index(
        'idx_subscribe_num_status',
        'subscribe',
        ['num', 'status'],
        unique=False
    )

    # 3.3 status 字段索引（辅助索引）
    # 用途：当只根据 status 过滤时加速查询
    op.create_index(
        'idx_subscribe_status',
        'subscribe',
        ['status'],
        unique=False
    )

    # 4. history 表索引
    # 4.1 单独的 num 字段索引
    # 用途：加速基于番号的查询（num 可以为 NULL，但索引仍然有效）
    op.create_index(
        'idx_history_num',
        'history',
        ['num'],
        unique=False
    )

    # 4.2 num + status 组合索引
    # 用途：优化同时过滤番号和状态的查询（status=1 表示成功）
    # 对应查询：func.upper(History.num).in_(upper_nums), History.status == 1
    op.create_index(
        'idx_history_num_status',
        'history',
        ['num', 'status'],
        unique=False
    )

    # 4.3 status 字段索引（辅助索引）
    # 用途：当只根据 status 过滤时加速查询
    op.create_index(
        'idx_history_status',
        'history',
        ['status'],
        unique=False
    )


def downgrade() -> None:
    """移除下载状态查询相关的索引"""

    # 删除 history 表索引
    op.drop_index('idx_history_status', table_name='history')
    op.drop_index('idx_history_num_status', table_name='history')
    op.drop_index('idx_history_num', table_name='history')

    # 删除 subscribe 表索引
    op.drop_index('idx_subscribe_status', table_name='subscribe')
    op.drop_index('idx_subscribe_num_status', table_name='subscribe')
    op.drop_index('idx_subscribe_num', table_name='subscribe')

    # 删除 actor_subscribe_download 表索引
    op.drop_index('idx_actor_subscribe_download_num', table_name='actor_subscribe_download')

    # 删除 torrent 表索引
    op.drop_index('idx_torrent_num', table_name='torrent')
