"""
搜索相关的Schema模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """搜索请求参数"""
    query: str = Field(..., description="搜索关键词", min_length=1)
    search_type: str = Field(default="all", description="搜索类型: all, local, web, actor, num")
    sources: Optional[List[str]] = Field(default=None, description="数据源列表: local, javdb, javbus")
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页大小", ge=1, le=100)

    # 过滤条件
    is_hd: Optional[bool] = Field(default=None, description="是否高清")
    is_zh: Optional[bool] = Field(default=None, description="是否中文")
    is_uncensored: Optional[bool] = Field(default=None, description="是否无码")
    date_from: Optional[str] = Field(default=None, description="开始日期")
    date_to: Optional[str] = Field(default=None, description="结束日期")
    min_rating: Optional[float] = Field(default=None, description="最低评分")
    max_rating: Optional[float] = Field(default=None, description="最高评分")

    # 排序条件
    sort_by: str = Field(default="relevance", description="排序字段: relevance, date, rating, title")
    sort_order: str = Field(default="desc", description="排序方向: asc, desc")


class SearchResultItem(BaseModel):
    """搜索结果项"""
    result_type: str = Field(..., description="结果类型: local_video, local_actor, web_video, web_actor")
    source: Optional[str] = Field(default=None, description="数据源")

    # 通用字段
    title: Optional[str] = Field(default=None, description="标题")
    num: Optional[str] = Field(default=None, description="番号")
    cover: Optional[str] = Field(default=None, description="封面图片")
    url: Optional[str] = Field(default=None, description="详情链接")

    # 视频特有字段
    actors: Optional[List[str]] = Field(default=None, description="演员列表")
    studio: Optional[str] = Field(default=None, description="制作商")
    publisher: Optional[str] = Field(default=None, description="发行商")
    rating: Optional[float] = Field(default=None, description="评分")
    premiered: Optional[str] = Field(default=None, description="发布日期")
    runtime: Optional[str] = Field(default=None, description="时长")
    tags: Optional[List[str]] = Field(default=None, description="标签")
    is_hd: Optional[bool] = Field(default=None, description="是否高清")
    is_zh: Optional[bool] = Field(default=None, description="是否中文")
    is_uncensored: Optional[bool] = Field(default=None, description="是否无码")

    # 演员特有字段
    name: Optional[str] = Field(default=None, description="演员姓名")
    thumb: Optional[str] = Field(default=None, description="演员头像")

    # 额外数据
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="额外数据")


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str = Field(..., description="搜索关键词")
    total: int = Field(..., description="总结果数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    search_time: float = Field(..., description="搜索耗时(秒)")

    results: Dict[str, List[SearchResultItem]] = Field(..., description="搜索结果")
    suggestions: List[str] = Field(default=[], description="搜索建议")


class SearchSuggestionRequest(BaseModel):
    """搜索建议请求"""
    query: str = Field(..., description="部分搜索关键词", min_length=1)
    limit: int = Field(default=10, description="建议数量", ge=1, le=50)
    suggestion_types: Optional[List[str]] = Field(default=None, description="建议类型: actor, num, title, tag")


class SearchSuggestionResponse(BaseModel):
    """搜索建议响应"""
    query: str = Field(..., description="搜索关键词")
    suggestions: List[Dict[str, Any]] = Field(..., description="建议列表")


class SearchHistoryRequest(BaseModel):
    """搜索历史请求"""
    limit: int = Field(default=50, description="历史记录数量", ge=1, le=100)
    search_type: Optional[str] = Field(default=None, description="搜索类型过滤")


class SearchHistoryItem(BaseModel):
    """搜索历史项"""
    id: int = Field(..., description="历史记录ID")
    query: str = Field(..., description="搜索关键词")
    search_type: str = Field(..., description="搜索类型")
    result_count: int = Field(..., description="搜索结果数量")
    created_at: datetime = Field(..., description="搜索时间")


class SearchHistoryResponse(BaseModel):
    """搜索历史响应"""
    total: int = Field(..., description="总历史记录数")
    histories: List[SearchHistoryItem] = Field(..., description="历史记录列表")


class HotSearchItem(BaseModel):
    """热门搜索项"""
    query: str = Field(..., description="搜索关键词")
    search_count: int = Field(..., description="搜索次数")
    daily_count: int = Field(..., description="今日搜索次数")
    weekly_count: int = Field(..., description="本周搜索次数")
    trend_score: float = Field(..., description="趋势得分")


class HotSearchResponse(BaseModel):
    """热门搜索响应"""
    hot_searches: List[HotSearchItem] = Field(..., description="热门搜索列表")
    updated_at: datetime = Field(..., description="更新时间")


class SearchStatisticsResponse(BaseModel):
    """搜索统计响应"""
    total_searches: int = Field(..., description="总搜索次数")
    unique_queries: int = Field(..., description="唯一搜索词数量")
    avg_response_time: float = Field(..., description="平均响应时间")
    top_searches: List[HotSearchItem] = Field(..., description="TOP搜索")
    search_trends: List[Dict[str, Any]] = Field(..., description="搜索趋势")


class SearchFilter(BaseModel):
    """搜索过滤器"""
    is_hd: Optional[bool] = None
    is_zh: Optional[bool] = None
    is_uncensored: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    studios: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class QuickSearchRequest(BaseModel):
    """快速搜索请求（仅本地搜索）"""
    query: str = Field(..., description="搜索关键词", min_length=1)
    search_type: str = Field(default="all", description="搜索类型: all, actor, num, title")
    limit: int = Field(default=10, description="结果数量", ge=1, le=50)


class QuickSearchResponse(BaseModel):
    """快速搜索响应"""
    query: str = Field(..., description="搜索关键词")
    results: List[SearchResultItem] = Field(..., description="搜索结果")
    search_time: float = Field(..., description="搜索耗时(秒)")


class SearchCacheInfo(BaseModel):
    """搜索缓存信息"""
    cache_key: str = Field(..., description="缓存键")
    hit_count: int = Field(..., description="命中次数")
    expires_at: datetime = Field(..., description="过期时间")
    result_count: int = Field(..., description="结果数量")


class SearchCacheResponse(BaseModel):
    """搜索缓存响应"""
    total_caches: int = Field(..., description="总缓存数")
    active_caches: int = Field(..., description="活跃缓存数")
    cache_hit_rate: float = Field(..., description="缓存命中率")
    caches: List[SearchCacheInfo] = Field(..., description="缓存列表")