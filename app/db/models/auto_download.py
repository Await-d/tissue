"""
自动下载相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.models.base import Base


class TimeRangeType(enum.Enum):
    """时间范围类型枚举"""
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class DownloadStatus(enum.Enum):
    """下载状态枚举"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


class AutoDownloadRule(Base):
    """自动下载规则模型"""
    __tablename__ = 'auto_download_rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="规则名称")
    min_rating = Column(DECIMAL(3, 1), nullable=True, default=0.0, comment="最低评分")
    min_comments = Column(Integer, nullable=True, default=0, comment="最低评论数")
    time_range_type = Column(Enum(TimeRangeType), nullable=True, default=TimeRangeType.WEEK, comment="时间范围类型")
    time_range_value = Column(Integer, nullable=True, default=1, comment="时间范围值")
    is_hd = Column(Boolean, nullable=False, default=True, comment="是否高清")
    is_zh = Column(Boolean, nullable=False, default=False, comment="是否中文")
    is_uncensored = Column(Boolean, nullable=False, default=False, comment="是否无码")
    is_enabled = Column(Boolean, nullable=False, default=True, comment="是否启用")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联订阅记录
    subscriptions = relationship("AutoDownloadSubscription", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AutoDownloadRule(id={self.id}, name='{self.name}', enabled={self.is_enabled})>"


class AutoDownloadSubscription(Base):
    """自动下载订阅记录模型"""
    __tablename__ = 'auto_download_subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey('auto_download_rules.id', ondelete='CASCADE'), nullable=False, comment="关联规则ID")
    num = Column(String(50), nullable=False, comment="番号")
    title = Column(String(500), nullable=True, comment="标题")
    rating = Column(DECIMAL(3, 1), nullable=True, comment="评分")
    comments_count = Column(Integer, nullable=True, default=0, comment="评论数")
    cover = Column(String(500), nullable=True, comment="封面URL")
    actors = Column(Text, nullable=True, comment="演员信息(JSON格式)")
    status = Column(Enum(DownloadStatus), nullable=True, default=DownloadStatus.PENDING, comment="下载状态")
    download_url = Column(String(1000), nullable=True, comment="下载链接")
    download_time = Column(DateTime, nullable=True, comment="下载时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")

    # 关联规则
    rule = relationship("AutoDownloadRule", back_populates="subscriptions")

    def __repr__(self):
        return f"<AutoDownloadSubscription(id={self.id}, num='{self.num}', status={self.status})>"