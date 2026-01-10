"""add pending_torrent table

Revision ID: fa1714ef03b6
Revises: 20260110_fix_favorites, 6f6b614cff46
Create Date: 2026-01-10 20:58:31.552855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa1714ef03b6'
down_revision: Union[str, None] = ('20260110_fix_favorites', '6f6b614cff46')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
    op.drop_index('ix_pending_torrent_torrent_hash', table_name='pending_torrent')
    op.drop_table('pending_torrent')
    op.execute("DROP TYPE IF EXISTS pendingtorentstatus")
