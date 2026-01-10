"""add_audit_fields_to_scan_record

为 scan_record 表添加缺失的审计字段（create_by, create_time, update_by, update_time）

这些字段是 Base 模型的标准字段，所有继承自 Base 的模型都应包含这些字段。
原始迁移脚本 20260111_add_scan_record_table 中遗漏了这些字段，导致模型定义与数据库表结构不匹配。

Revision ID: 8b895bf9e393
Revises: 6ae1b844eb75
Create Date: 2026-01-11 02:54:17.332512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b895bf9e393'
down_revision: Union[str, None] = '6ae1b844eb75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加审计字段到 scan_record 表"""
    # 添加 create_by 字段
    op.add_column('scan_record', sa.Column('create_by', sa.Integer(), nullable=True))

    # 添加 create_time 字段
    op.add_column('scan_record', sa.Column('create_time', sa.DateTime(timezone=True), nullable=True))

    # 添加 update_by 字段
    op.add_column('scan_record', sa.Column('update_by', sa.Integer(), nullable=True))

    # 添加 update_time 字段
    op.add_column('scan_record', sa.Column('update_time', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """移除审计字段"""
    op.drop_column('scan_record', 'update_time')
    op.drop_column('scan_record', 'update_by')
    op.drop_column('scan_record', 'create_time')
    op.drop_column('scan_record', 'create_by')
