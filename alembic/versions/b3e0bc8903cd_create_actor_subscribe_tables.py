"""create actor subscribe tables

Revision ID: b3e0bc8903cd
Revises: 8f6a88087458
Create Date: 2025-05-26 01:22:26.893318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3e0bc8903cd'
down_revision: Union[str, None] = '8f6a88087458'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('actor_subscribe',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('actor_name', sa.String(), nullable=False),
    sa.Column('actor_url', sa.String(), nullable=True),
    sa.Column('actor_thumb', sa.String(), nullable=True),
    sa.Column('from_date', sa.Date(), nullable=False),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('is_hd', sa.Boolean(), nullable=False),
    sa.Column('is_zh', sa.Boolean(), nullable=False),
    sa.Column('is_uncensored', sa.Boolean(), nullable=False),
    sa.Column('create_by', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('update_by', sa.Integer(), nullable=True),
    sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('actor_subscribe_download',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('actor_subscribe_id', sa.Integer(), nullable=False),
    sa.Column('num', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('cover', sa.String(), nullable=True),
    sa.Column('magnet', sa.String(), nullable=True),
    sa.Column('size', sa.String(), nullable=True),
    sa.Column('download_time', sa.DateTime(), nullable=False),
    sa.Column('is_hd', sa.Boolean(), nullable=False),
    sa.Column('is_zh', sa.Boolean(), nullable=False),
    sa.Column('is_uncensored', sa.Boolean(), nullable=False),
    sa.Column('create_by', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('update_by', sa.Integer(), nullable=True),
    sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('actor_subscribe_download')
    op.drop_table('actor_subscribe')
    # ### end Alembic commands ###
