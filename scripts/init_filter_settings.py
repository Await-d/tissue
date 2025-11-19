"""
初始化默认的下载过滤设置
在应用启动时自动创建
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import SessionFactory
from app.db.models.download_filter import DownloadFilterSettings
from app.utils.logger import logger


def init_default_filter_settings():
    """初始化默认的下载过滤设置"""
    db = SessionFactory()
    try:
        # 检查是否已存在激活的设置
        existing = db.query(DownloadFilterSettings).filter_by(is_active=True).first()
        if existing:
            logger.info("下载过滤设置已存在，跳过初始化")
            return

        # 创建默认设置
        default_settings = DownloadFilterSettings(
            min_file_size_mb=300,
            max_file_size_mb=None,
            allowed_extensions=None,
            blocked_extensions=None,
            min_seed_count=1,
            max_total_size_gb=None,
            enable_smart_filter=True,
            skip_sample_files=True,
            skip_subtitle_only=True,
            media_files_only=False,
            include_subtitles=True,
            is_active=True
        )

        db.add(default_settings)
        db.commit()
        logger.info("已自动创建默认的下载过滤设置")

    except Exception as e:
        db.rollback()
        logger.error(f"创建默认过滤设置失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_default_filter_settings()
    print("默认过滤设置初始化完成")
