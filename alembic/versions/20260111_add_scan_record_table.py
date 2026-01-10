"""添加扫描记录表

此迁移脚本创建 scan_record 表，用于存储文件扫描历史记录。

功能说明：
- 记录每次文件扫描的详细信息（时间、文件数、新发现数等）
- 跟踪扫描状态和错误信息
- 提供扫描历史查询和分析

表结构：
- scan_record: 扫描记录表，包含扫描时间、统计信息、状态等字段

索引：
- idx_scan_time: 扫描时间索引（用于按时间查询）
- idx_status: 状态索引（用于按状态过滤）
- idx_created_at: 创建时间索引（用于排序）

Revision ID: 20260111_scan_record
Revises: 20260111_download_status_indexes
Create Date: 2026-01-11 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260111_scan_record'
down_revision: Union[str, None] = '20260111_download_status_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 scan_record 表"""

    op.create_table(
        'scan_record',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, comment='主键ID'),
        sa.Column('scan_time', sa.DateTime(), nullable=False, comment='扫描时间'),
        sa.Column('total_files', sa.Integer(), nullable=False, server_default='0', comment='扫描文件总数'),
        sa.Column('new_found', sa.Integer(), nullable=False, server_default='0', comment='新发现视频数'),
        sa.Column('already_exists', sa.Integer(), nullable=False, server_default='0', comment='已存在视频数'),
        sa.Column('scan_duration', sa.Float(), nullable=False, server_default='0.0', comment='扫描耗时(秒)'),
        sa.Column('status', sa.String(20), nullable=False, server_default='success', comment='扫描状态: success/failed'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        # Base 模型的标准审计字段
        sa.Column('create_by', sa.Integer(), nullable=True),
        sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('update_by', sa.Integer(), nullable=True),
        sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        comment='扫描记录表 - 存储文件扫描历史记录'
    )

    # 创建索引以优化查询性能
    op.create_index('idx_scan_time', 'scan_record', ['scan_time'], unique=False)
    op.create_index('idx_status', 'scan_record', ['status'], unique=False)
    op.create_index('idx_created_at', 'scan_record', ['created_at'], unique=False)


def downgrade() -> None:
    """删除 scan_record 表"""

    # 删除索引
    op.drop_index('idx_created_at', table_name='scan_record')
    op.drop_index('idx_status', table_name='scan_record')
    op.drop_index('idx_scan_time', table_name='scan_record')

    # 删除表
    op.drop_table('scan_record')
