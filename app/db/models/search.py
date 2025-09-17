"""
搜索相关数据库模型
包括搜索历史、搜索统计、热门搜索等
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index, Boolean, Float
from sqlalchemy.sql import func

from app.db.models.base import Base


class SearchHistory(Base):
    """搜索历史表"""
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(255), nullable=False, comment='搜索关键词')
    search_type = Column(String(50), default='all', comment='搜索类型: all, local, web, actor, num')
    result_count = Column(Integer, default=0, comment='搜索结果数量')
    user_ip = Column(String(45), comment='用户IP地址')
    user_agent = Column(Text, comment='用户代理信息')
    response_time = Column(Float, comment='响应时间(秒)')
    sources = Column(String(255), comment='搜索数据源，逗号分隔')
    filters_applied = Column(Text, comment='应用的过滤条件(JSON)')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')

    # 创建索引以优化查询性能
    __table_args__ = (
        Index('idx_search_query', 'query'),
        Index('idx_search_type', 'search_type'),
        Index('idx_search_created_at', 'created_at'),
        Index('idx_search_query_type', 'query', 'search_type'),
    )


class SearchStatistics(Base):
    """搜索统计表（按日统计）"""
    __tablename__ = 'search_statistics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, comment='统计日期')
    query = Column(String(255), nullable=False, comment='搜索关键词')
    search_count = Column(Integer, default=1, comment='搜索次数')
    unique_users = Column(Integer, default=1, comment='唯一用户数')
    avg_response_time = Column(Float, comment='平均响应时间')
    success_rate = Column(Float, comment='成功率')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')

    # 创建唯一索引和其他索引
    __table_args__ = (
        Index('idx_stats_date_query', 'date', 'query', unique=True),
        Index('idx_stats_date', 'date'),
        Index('idx_stats_query', 'query'),
        Index('idx_stats_count', 'search_count'),
    )


class SearchSuggestion(Base):
    """搜索建议表"""
    __tablename__ = 'search_suggestions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(255), nullable=False, comment='原始搜索词')
    suggestion = Column(String(255), nullable=False, comment='建议搜索词')
    suggestion_type = Column(String(50), comment='建议类型: actor, num, title, tag')
    priority = Column(Integer, default=1, comment='优先级，数字越大优先级越高')
    click_count = Column(Integer, default=0, comment='点击次数')
    is_active = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_suggestion_query', 'query'),
        Index('idx_suggestion_type', 'suggestion_type'),
        Index('idx_suggestion_priority', 'priority'),
        Index('idx_suggestion_active', 'is_active'),
    )


class HotSearch(Base):
    """热门搜索表"""
    __tablename__ = 'hot_searches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(255), nullable=False, unique=True, comment='搜索关键词')
    search_count = Column(Integer, default=1, comment='总搜索次数')
    daily_count = Column(Integer, default=0, comment='今日搜索次数')
    weekly_count = Column(Integer, default=0, comment='本周搜索次数')
    monthly_count = Column(Integer, default=0, comment='本月搜索次数')
    trend_score = Column(Float, default=0.0, comment='趋势得分')
    last_search_at = Column(DateTime, default=func.now(), comment='最后搜索时间')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_hot_search_count', 'search_count'),
        Index('idx_hot_daily_count', 'daily_count'),
        Index('idx_hot_weekly_count', 'weekly_count'),
        Index('idx_hot_monthly_count', 'monthly_count'),
        Index('idx_hot_trend_score', 'trend_score'),
        Index('idx_hot_last_search', 'last_search_at'),
    )


class SearchCache(Base):
    """搜索缓存表"""
    __tablename__ = 'search_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), nullable=False, unique=True, comment='缓存键')
    query = Column(String(255), nullable=False, comment='搜索关键词')
    search_type = Column(String(50), comment='搜索类型')
    sources = Column(String(255), comment='数据源')
    result_data = Column(Text, comment='搜索结果数据(JSON)')
    result_count = Column(Integer, default=0, comment='结果数量')
    hit_count = Column(Integer, default=0, comment='缓存命中次数')
    expires_at = Column(DateTime, nullable=False, comment='过期时间')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_cache_query', 'query'),
        Index('idx_cache_expires', 'expires_at'),
        Index('idx_cache_created', 'created_at'),
    )