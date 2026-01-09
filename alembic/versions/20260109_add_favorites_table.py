"""add_favorites_table

Revision ID: 20260109_favorites
Revises: ab401d86be6f
Create Date: 2026-01-09 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260109_favorites'
down_revision: Union[str, None] = 'ab401d86be6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 favorites 表
    op.create_table('favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('video_num', sa.String(length=50), nullable=False),
        sa.Column('video_title', sa.String(length=500), nullable=True),
        sa.Column('video_cover', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'video_num', name='uix_user_video')
    )
    op.create_index('ix_favorites_user_id', 'favorites', ['user_id'], unique=False)
    op.create_index('ix_favorites_video_num', 'favorites', ['video_num'], unique=False)


def downgrade() -> None:
    # 删除 favorites 表
    op.drop_index('ix_favorites_video_num', table_name='favorites')
    op.drop_index('ix_favorites_user_id', table_name='favorites')
    op.drop_table('favorites')
