'''
Author: Await
Date: 2025-05-26 01:10:10
LastEditors: Await
LastEditTime: 2025-05-26 23:42:36
Description: 请填写简介
'''
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, DECIMAL

from app.db.models.base import Base


class ActorSubscribe(Base):
    __tablename__ = 'actor_subscribe'

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_name = Column(String, nullable=False)
    actor_url = Column(String, nullable=True)
    actor_thumb = Column(String, nullable=True)
    from_date = Column(Date, nullable=False)  # 订阅起始日期
    last_updated = Column(DateTime, nullable=True)
    is_hd = Column(Boolean, nullable=False, default=True)
    is_zh = Column(Boolean, nullable=False, default=False)
    is_uncensored = Column(Boolean, nullable=False, default=False)
    is_paused = Column(Boolean, nullable=False, default=False)  # 是否暂停订阅
    min_rating = Column(DECIMAL(3, 1), nullable=True, default=0.0, comment="最低评分要求")
    min_comments = Column(Integer, nullable=True, default=0, comment="最低评论数要求")
    subscribed_works_count = Column(Integer, nullable=True, default=0, comment="订阅作品总数（缓存）")
    works_count_updated_at = Column(DateTime, nullable=True, comment="作品数量更新时间")


class ActorSubscribeDownload(Base):
    __tablename__ = 'actor_subscribe_download'

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_subscribe_id = Column(Integer, nullable=False)  # 关联的演员订阅ID
    num = Column(String, nullable=False)  # 番号
    title = Column(String, nullable=True)  # 标题
    cover = Column(String, nullable=True)  # 封面
    magnet = Column(String, nullable=True)  # 磁力链接
    size = Column(String, nullable=True)  # 文件大小
    download_time = Column(DateTime, nullable=False)  # 下载时间
    is_hd = Column(Boolean, nullable=False, default=True)
    is_zh = Column(Boolean, nullable=False, default=False)
    is_uncensored = Column(Boolean, nullable=False, default=False) 