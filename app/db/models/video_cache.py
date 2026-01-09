"""
视频缓存数据模型 - 存储从多个网站预抓取的视频数据
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index, JSON
from app.db.models.base import Base


class VideoCache(Base):
    """视频缓存表 - 系统预抓取的视频数据"""
    __tablename__ = 'video_cache'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 视频基本信息
    num = Column(String(50), nullable=False, comment='视频番号')
    title = Column(String(500), comment='视频标题')
    cover = Column(String(500), comment='封面图片URL')
    url = Column(String(500), comment='视频详情页URL')

    # 视频元数据
    rating = Column(Float, comment='评分 (0-5)')
    comments_count = Column(Integer, default=0, comment='评论数')
    release_date = Column(String(20), comment='发布日期 YYYY-MM-DD')

    # 视频属性标签
    is_hd = Column(Boolean, default=False, comment='是否高清')
    is_zh = Column(Boolean, default=False, comment='是否中文字幕')
    is_uncensored = Column(Boolean, default=False, comment='是否无码')

    # 演员和标签信息 (JSON格式存储)
    actors = Column(JSON, comment='演员列表 [{"id": "xxx", "name": "xxx"}]')
    tags = Column(JSON, comment='标签列表 ["tag1", "tag2"]')

    # 下载信息 (JSON格式存储磁力链接列表)
    magnets = Column(JSON, comment='磁力链接列表 [{"title": "xxx", "link": "magnet:..."}]')

    # 数据源信息
    source = Column(String(50), nullable=False, comment='数据来源: JavDB, JavBus等')
    video_type = Column(String(20), comment='视频类型: censored, uncensored')
    cycle = Column(String(20), comment='榜单周期: daily, weekly, monthly')
    rank_position = Column(Integer, comment='在榜单中的排名位置')

    # 额外元数据
    extra_data = Column(JSON, comment='其他扩展数据')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    fetched_at = Column(DateTime, default=datetime.now, comment='抓取时间')

    # 创建索引优化查询性能
    __table_args__ = (
        Index('idx_num', 'num'),  # 番号索引
        Index('idx_source_type_cycle', 'source', 'video_type', 'cycle'),  # 数据源组合索引
        Index('idx_rating', 'rating'),  # 评分索引
        Index('idx_comments', 'comments_count'),  # 评论数索引
        Index('idx_fetched_at', 'fetched_at'),  # 抓取时间索引
        Index('idx_release_date', 'release_date'),  # 发布日期索引
        {'comment': '视频缓存表 - 存储预抓取的排行榜视频数据'}
    )

    def __repr__(self):
        return f"<VideoCache(num='{self.num}', title='{self.title}', source='{self.source}', rating={self.rating})>"

    def to_dict(self):
        """转换为字典格式，兼容现有的视频数据结构"""
        return {
            'num': self.num,
            'title': self.title,
            'cover': self.cover,
            'url': self.url,
            'rating': self.rating,
            'comments': self.comments_count,  # 兼容旧字段名
            'comments_count': self.comments_count,
            'release_date': self.release_date,
            'is_hd': self.is_hd,
            'is_zh': self.is_zh,
            'is_uncensored': self.is_uncensored,
            'actors': self.actors or [],
            'tags': self.tags or [],
            'magnets': self.magnets or [],
            'source': self.source,
            'video_type': self.video_type,
            'cycle': self.cycle,
            'rank_position': self.rank_position,
            'extra_data': self.extra_data,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
        }
