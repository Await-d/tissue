"""
数据库自动迁移工具
用于在程序启动时自动创建缺失的表和字段
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine
from app.db.models.download_filter import DownloadFilterSettings
from app.db.models.pending_torrent import PendingTorrent
from app.utils.logger import logger


class DatabaseMigration:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.engine = engine
    
    def check_and_migrate(self):
        """
        检查并执行必要的数据库迁移
        """
        try:
            logger.info("开始检查数据库结构...")
            
            # 运行 Alembic 升级（若配置文件存在）
            self._run_alembic_upgrade()

            # 检查下载过滤设置表
            self._ensure_download_filter_table()

            # 检查待处理种子表
            self._ensure_pending_torrent_table()
            
            # 初始化默认设置
            self._init_default_filter_settings()
            
            logger.info("数据库迁移检查完成")
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            raise
    
    def _table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 表是否存在
        """
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except Exception as e:
            logger.error(f"检查表是否存在时出错: {e}")
            return False
    
    def _column_exists(self, table_name: str, column_name: str) -> bool:
        """
        检查列是否存在
        
        Args:
            table_name: 表名
            column_name: 列名
            
        Returns:
            bool: 列是否存在
        """
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            return any(col['name'] == column_name for col in columns)
        except Exception as e:
            logger.error(f"检查列是否存在时出错: {e}")
            return False

    def _run_alembic_upgrade(self):
        """
        运行 Alembic 升级，将数据库迁移到最新版本
        """
        try:
            config_path = Path("alembic.ini")
            if not config_path.exists():
                logger.warning("alembic.ini 不存在，跳过 Alembic 升级")
                return

            alembic_cfg = Config(str(config_path))
            command.upgrade(alembic_cfg, "head")
            logger.info("Alembic 升级完成")
        except Exception as e:
            # 不阻塞后续检查，记录警告即可
            logger.warning(f"Alembic 升级失败，继续执行后续检查: {e}")
    
    def _ensure_download_filter_table(self):
        """
        确保下载过滤设置表存在
        """
        table_name = 'download_filter_settings'
        
        if not self._table_exists(table_name):
            logger.info(f"创建表: {table_name}")
            try:
                # 使用SQLAlchemy模型创建表
                DownloadFilterSettings.__table__.create(self.engine)
                logger.info(f"表 {table_name} 创建成功")
            except SQLAlchemyError as e:
                logger.error(f"创建表 {table_name} 失败: {e}")
                raise
        else:
            logger.info(f"表 {table_name} 已存在")
            
            # 检查是否需要添加新字段（这里可以扩展检查逻辑）
            self._check_and_add_columns(table_name)

    def _ensure_pending_torrent_table(self):
        """
        确保待处理种子表存在
        """
        table_name = 'pending_torrent'

        if not self._table_exists(table_name):
            logger.info(f"创建表: {table_name}")
            try:
                PendingTorrent.__table__.create(self.engine, checkfirst=True)
                logger.info(f"表 {table_name} 创建成功")
            except SQLAlchemyError as e:
                logger.error(f"创建表 {table_name} 失败: {e}")
                raise
        else:
            logger.info(f"表 {table_name} 已存在")
    
    def _check_and_add_columns(self, table_name: str):
        """
        检查并添加缺失的列
        
        Args:
            table_name: 表名
        """
        # 定义需要检查的列及其SQL定义（SQLite不支持COMMENT语法）
        required_columns = {
            'min_file_size_mb': "ALTER TABLE download_filter_settings ADD COLUMN min_file_size_mb INTEGER NOT NULL DEFAULT 300",
            'max_file_size_mb': "ALTER TABLE download_filter_settings ADD COLUMN max_file_size_mb INTEGER NULL",
            'allowed_extensions': "ALTER TABLE download_filter_settings ADD COLUMN allowed_extensions TEXT NULL",
            'blocked_extensions': "ALTER TABLE download_filter_settings ADD COLUMN blocked_extensions TEXT NULL",
            'min_seed_count': "ALTER TABLE download_filter_settings ADD COLUMN min_seed_count INTEGER NULL DEFAULT 1",
            'max_total_size_gb': "ALTER TABLE download_filter_settings ADD COLUMN max_total_size_gb DECIMAL(10,2) NULL",
            'enable_smart_filter': "ALTER TABLE download_filter_settings ADD COLUMN enable_smart_filter BOOLEAN NOT NULL DEFAULT 1",
            'skip_sample_files': "ALTER TABLE download_filter_settings ADD COLUMN skip_sample_files BOOLEAN NOT NULL DEFAULT 1",
            'skip_subtitle_only': "ALTER TABLE download_filter_settings ADD COLUMN skip_subtitle_only BOOLEAN NOT NULL DEFAULT 1",
            'media_files_only': "ALTER TABLE download_filter_settings ADD COLUMN media_files_only BOOLEAN NOT NULL DEFAULT 0",
            'include_subtitles': "ALTER TABLE download_filter_settings ADD COLUMN include_subtitles BOOLEAN NOT NULL DEFAULT 1",
            'is_active': "ALTER TABLE download_filter_settings ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1",
            'created_at': "ALTER TABLE download_filter_settings ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            'updated_at': "ALTER TABLE download_filter_settings ADD COLUMN updated_at DATETIME NULL"
        }
        
        for column_name, alter_sql in required_columns.items():
            if not self._column_exists(table_name, column_name):
                try:
                    logger.info(f"添加列: {table_name}.{column_name}")
                    with self.engine.connect() as conn:
                        conn.execute(text(alter_sql))
                        conn.commit()
                    logger.info(f"列 {table_name}.{column_name} 添加成功")
                except SQLAlchemyError as e:
                    logger.warning(f"添加列 {table_name}.{column_name} 失败: {e}")
                    # 对于已存在的列，我们忽略错误
                    if "Duplicate column name" not in str(e):
                        raise
    
    def _init_default_filter_settings(self):
        """
        初始化默认的过滤设置
        """
        try:
            with self.engine.connect() as conn:
                # 检查是否已有设置记录
                result = conn.execute(text("SELECT COUNT(*) as count FROM download_filter_settings WHERE is_active = 1"))
                count = result.fetchone()[0]
                
                if count == 0:
                    logger.info("初始化默认下载过滤设置")
                    
                    # 插入默认设置
                    insert_sql = """
                    INSERT INTO download_filter_settings 
                    (min_file_size_mb, max_file_size_mb, enable_smart_filter, 
                     skip_sample_files, skip_subtitle_only, is_active) 
                    VALUES (300, NULL, 1, 1, 1, 1)
                    """
                    
                    conn.execute(text(insert_sql))
                    conn.commit()
                    logger.info("默认下载过滤设置初始化完成")
                else:
                    logger.info("下载过滤设置已存在，跳过初始化")
                    
        except SQLAlchemyError as e:
            logger.error(f"初始化默认过滤设置失败: {e}")
            # 这不是致命错误，继续执行
    
    def add_filter_setting_to_download_table(self):
        """
        为现有的下载相关表添加过滤设置字段（如果需要的话）
        """
        # 这里可以添加对现有表的扩展，比如在种子表中添加过滤状态字段
        pass


# 全局实例
db_migration = DatabaseMigration()
