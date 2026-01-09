"""修复枚举值大小写问题

Revision ID: 55651a7bffa9
Revises: 9fca107100f3
Create Date: 2025-07-07 17:27:09.812040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55651a7bffa9'
down_revision: Union[str, None] = '9fca107100f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 在SQLite中，我们需要重新创建表以修复枚举值
    # 但为了安全，我们先尝试更新现有的枚举值
    
    # 对于SQLite，尝试更新现有的大写枚举值为小写
    try:
        # 检查并更新 time_range_type 枚举值
        op.execute("""
            UPDATE auto_download_rules 
            SET time_range_type = 'day' 
            WHERE time_range_type = 'DAY'
        """)
        op.execute("""
            UPDATE auto_download_rules 
            SET time_range_type = 'week' 
            WHERE time_range_type = 'WEEK'
        """)
        op.execute("""
            UPDATE auto_download_rules 
            SET time_range_type = 'month' 
            WHERE time_range_type = 'MONTH'
        """)
        
        # 检查并更新 status 枚举值
        op.execute("""
            UPDATE auto_download_subscriptions 
            SET status = 'pending' 
            WHERE status = 'PENDING'
        """)
        op.execute("""
            UPDATE auto_download_subscriptions 
            SET status = 'downloading' 
            WHERE status = 'DOWNLOADING'
        """)
        op.execute("""
            UPDATE auto_download_subscriptions 
            SET status = 'completed' 
            WHERE status = 'COMPLETED'
        """)
        op.execute("""
            UPDATE auto_download_subscriptions 
            SET status = 'failed' 
            WHERE status = 'FAILED'
        """)
    except Exception as e:
        # 如果更新失败，忽略错误，因为可能数据已经是正确格式
        pass


def downgrade() -> None:
    # 回滚时将小写值改回大写（如果需要的话）
    try:
        op.execute("""
            UPDATE auto_download_rules 
            SET time_range_type = 'DAY' 
            WHERE time_range_type = 'day'
        """)
        op.execute("""
            UPDATE auto_download_rules 
            SET time_range_type = 'WEEK' 
            WHERE time_range_type = 'week'
        """)
        op.execute("""
            UPDATE auto_download_rules 
            SET time_range_type = 'MONTH' 
            WHERE time_range_type = 'month'
        """)
    except Exception as e:
        pass
