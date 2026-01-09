"""
Author: Await
Date: 2026-01-09
Description: 收藏功能数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint

from app.db.models.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    video_num = Column(String(50), nullable=False, index=True)
    video_title = Column(String(500), nullable=True)
    video_cover = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'video_num', name='uix_user_video'),
    )
