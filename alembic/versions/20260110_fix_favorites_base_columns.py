"""fix_favorites_base_columns

Revision ID: 20260110_fix_favorites
Revises: 20260109_favorites
Create Date: 2026-01-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260110_fix_favorites'
down_revision: Union[str, None] = '20260109_favorites'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 检查并添加缺失的 Base 类基础字段
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('favorites')]

    if 'create_by' not in columns:
        op.add_column('favorites', sa.Column('create_by', sa.Integer(), nullable=True))
    if 'create_time' not in columns:
        op.add_column('favorites', sa.Column('create_time', sa.DateTime(timezone=True), nullable=True))
    if 'update_by' not in columns:
        op.add_column('favorites', sa.Column('update_by', sa.Integer(), nullable=True))
    if 'update_time' not in columns:
        op.add_column('favorites', sa.Column('update_time', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # 删除添加的列
    op.drop_column('favorites', 'update_time')
    op.drop_column('favorites', 'update_by')
    op.drop_column('favorites', 'create_time')
    op.drop_column('favorites', 'create_by')
