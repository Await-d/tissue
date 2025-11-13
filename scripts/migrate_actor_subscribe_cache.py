"""
数据库迁移脚本 - 添加演员订阅作品数量缓存字段
执行方式: python scripts/migrate_actor_subscribe_cache.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db import SessionFactory
from app.utils.logger import logger


def migrate():
    """执行数据库迁移"""
    with SessionFactory() as db:
        try:
            logger.info("开始数据库迁移: 添加演员订阅作品数量缓存字段")
            
            # 检查字段是否已存在
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='actor_subscribe' 
                AND column_name='subscribed_works_count'
            """)
            
            result = db.execute(check_sql).fetchone()
            
            if result:
                logger.info("字段 subscribed_works_count 已存在，跳过迁移")
                return
            
            # 添加新字段
            logger.info("添加字段 subscribed_works_count...")
            db.execute(text("""
                ALTER TABLE actor_subscribe 
                ADD COLUMN subscribed_works_count INTEGER DEFAULT 0 
                COMMENT '订阅作品总数（缓存）'
            """))
            
            logger.info("添加字段 works_count_updated_at...")
            db.execute(text("""
                ALTER TABLE actor_subscribe 
                ADD COLUMN works_count_updated_at DATETIME 
                COMMENT '作品数量更新时间'
            """))
            
            db.commit()
            logger.info("数据库迁移完成！")
            
            # 可选：立即更新所有订阅的作品数量
            logger.info("\n是否立即更新所有订阅的作品数量？(y/n)")
            logger.info("注意：这可能需要较长时间，建议在业务低峰期执行")
            
        except Exception as e:
            db.rollback()
            logger.error(f"数据库迁移失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


if __name__ == "__main__":
    migrate()
