"""
下载过滤配置数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, Text
from sqlalchemy.sql import func

from app.db.models.base import Base


class DownloadFilterSettings(Base):
    """下载过滤设置模型"""
    __tablename__ = 'download_filter_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 文件大小过滤
    min_file_size_mb = Column(Integer, nullable=False, default=300, comment="最小文件大小(MB)")
    max_file_size_mb = Column(Integer, nullable=True, comment="最大文件大小(MB), null表示无限制")
    
    # 文件类型过滤
    allowed_extensions = Column(Text, nullable=True, comment="允许的文件扩展名，JSON格式")
    blocked_extensions = Column(Text, nullable=True, comment="禁止的文件扩展名，JSON格式")
    
    # 种子过滤
    min_seed_count = Column(Integer, nullable=True, default=1, comment="最小种子数")
    max_total_size_gb = Column(DECIMAL(10, 2), nullable=True, comment="种子总大小限制(GB)")
    
    # 智能过滤
    enable_smart_filter = Column(Boolean, nullable=False, default=True, comment="启用智能过滤")
    skip_sample_files = Column(Boolean, nullable=False, default=True, comment="跳过样本文件")
    skip_subtitle_only = Column(Boolean, nullable=False, default=True, comment="跳过仅字幕文件")
    media_files_only = Column(Boolean, nullable=False, default=False, comment="只保留媒体文件(视频+字幕)")
    include_subtitles = Column(Boolean, nullable=False, default=True, comment="包含字幕文件")
    
    # 系统字段
    is_active = Column(Boolean, nullable=False, default=True, comment="是否激活")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<DownloadFilterSettings(id={self.id}, min_file_size_mb={self.min_file_size_mb})>"