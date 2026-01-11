"""add pending_torrent table

Revision ID: fa1714ef03b6
Revises: 20260110_fix_favorites, 6f6b614cff46
Create Date: 2026-01-10 20:58:31.552855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'fa1714ef03b6'
down_revision: Union[str, None] = ('20260110_fix_favorites', '6f6b614cff46')
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

    if 'pending_torrent' not in existing_tables:
        op.create_table(
            'pending_torrent',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('torrent_hash', sa.String(64), nullable=False),
            sa.Column('magnet', sa.Text(), nullable=True),
            sa.Column('savepath', sa.String(500), nullable=True),
            sa.Column('category', sa.String(100), nullable=True),
            sa.Column('num', sa.String(50), nullable=True),
            sa.Column('source', sa.String(50), nullable=True),
            sa.Column('status', sa.Enum('waiting_metadata', 'metadata_ready', 'filtering', 'completed', 'failed', 'timeout', name='pendingtorentstatus'), nullable=False),
            sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
            sa.Column('max_retries', sa.Integer(), nullable=False, default=30),
            sa.Column('filter_result', sa.Text(), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('added_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('last_check_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('file_count', sa.Integer(), nullable=True),
            sa.Column('total_size_bytes', sa.BigInteger(), nullable=True),
            sa.Column('filtered_file_count', sa.Integer(), nullable=True),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_pending_torrent_torrent_hash', 'pending_torrent', ['torrent_hash'], unique=True)


def downgrade() -> None:
    existing_tables = get_existing_tables()

    if 'pending_torrent' in existing_tables:
        safe_drop_index('ix_pending_torrent_torrent_hash', 'pending_torrent')
        op.drop_table('pending_torrent')
        op.execute("DROP TYPE IF EXISTS pendingtorentstatus")
