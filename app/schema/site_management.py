"""
站点管理相关的Pydantic Schema
用于API请求和响应的数据验证和序列化
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl

from app.db.models.site_management import SiteStatus, SiteType


# ========== 站点管理 Schema ==========

class SiteBase(BaseModel):
    """站点基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="站点名称")
    spider_class: str = Field(..., description="爬虫类名")
    base_url: HttpUrl = Field(..., description="站点基础URL")
    mirror_urls: List[HttpUrl] = Field(default=[], description="镜像URL列表")

    site_type: SiteType = Field(default=SiteType.PRIMARY, description="站点类型")
    priority: int = Field(default=100, ge=1, le=1000, description="优先级")
    weight: float = Field(default=1.0, ge=0.1, le=10.0, description="权重值")

    supports_download: bool = Field(default=False, description="是否支持下载")
    supports_preview: bool = Field(default=False, description="是否支持预览")
    supports_search: bool = Field(default=True, description="是否支持搜索")
    supports_actor_info: bool = Field(default=False, description="是否支持演员信息")
    supports_ranking: bool = Field(default=False, description="是否支持排行榜")

    config: Dict[str, Any] = Field(default={}, description="站点特定配置")
    headers: Dict[str, str] = Field(default={}, description="自定义请求头")
    rate_limit: int = Field(default=1, ge=0, le=60, description="请求间隔(秒)")
    timeout: int = Field(default=30, ge=5, le=300, description="请求超时时间(秒)")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")

    region: Optional[str] = Field(None, max_length=10, description="地理区域")
    language: str = Field(default="zh", max_length=10, description="主要语言")
    description: Optional[str] = Field(None, description="站点描述")
    tags: List[str] = Field(default=[], description="站点标签")


class SiteCreate(SiteBase):
    """创建站点请求"""

    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('站点名称不能为空')
        return v.strip()

    @validator('spider_class')
    def validate_spider_class(cls, v):
        # 检查爬虫类名是否符合Python类名规范
        if not v or not v.isidentifier() or not v[0].isupper():
            raise ValueError('爬虫类名必须是有效的Python类名')
        return v


class SiteUpdate(BaseModel):
    """更新站点请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    spider_class: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    mirror_urls: Optional[List[HttpUrl]] = None

    site_type: Optional[SiteType] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)
    weight: Optional[float] = Field(None, ge=0.1, le=10.0)
    status: Optional[SiteStatus] = None
    is_enabled: Optional[bool] = None

    supports_download: Optional[bool] = None
    supports_preview: Optional[bool] = None
    supports_search: Optional[bool] = None
    supports_actor_info: Optional[bool] = None
    supports_ranking: Optional[bool] = None

    config: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    rate_limit: Optional[int] = Field(None, ge=0, le=60)
    timeout: Optional[int] = Field(None, ge=5, le=300)
    max_retries: Optional[int] = Field(None, ge=0, le=10)

    region: Optional[str] = Field(None, max_length=10)
    language: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class SiteResponse(SiteBase):
    """站点响应"""
    id: int
    status: SiteStatus
    is_enabled: bool
    current_url: str
    is_healthy: bool
    create_time: Optional[datetime]
    update_time: Optional[datetime]

    class Config:
        from_attributes = True


class SiteListResponse(BaseModel):
    """站点列表响应"""
    sites: List[SiteResponse]
    total: int
    skip: int
    limit: int


# ========== 站点统计 Schema ==========

class SiteStatisticsResponse(BaseModel):
    """站点统计响应"""
    id: int
    site_id: int

    total_requests: int
    successful_requests: int
    failed_requests: int

    avg_response_time: float
    max_response_time: float
    min_response_time: float

    videos_scraped: int
    actors_scraped: int
    downloads_provided: int

    timeout_errors: int
    connection_errors: int
    parse_errors: int
    rate_limit_errors: int

    success_rate: float
    error_rate: float

    stat_date: datetime
    last_reset: datetime

    class Config:
        from_attributes = True


# ========== 健康检查 Schema ==========

class SiteHealthResponse(BaseModel):
    """站点健康检查响应"""
    id: int
    site_id: int
    is_healthy: bool
    response_time: Optional[float]
    status_code: Optional[int]
    error_message: Optional[str]
    check_type: str
    check_url: Optional[str]
    checked_at: datetime
    next_check: Optional[datetime]

    class Config:
        from_attributes = True


class HealthCheckResult(BaseModel):
    """健康检查结果"""
    is_healthy: bool
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None


# ========== 错误日志 Schema ==========

class SiteErrorLogResponse(BaseModel):
    """站点错误日志响应"""
    id: int
    site_id: int
    error_type: Optional[str]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]

    request_url: Optional[str]
    request_method: Optional[str]
    request_headers: Optional[Dict[str, Any]]

    response_code: Optional[int]
    response_time: Optional[float]

    operation: Optional[str]
    video_number: Optional[str]
    actor_name: Optional[str]

    is_resolved: bool
    resolution_note: Optional[str]

    occurred_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== 故障转移规则 Schema ==========

class FailoverRuleBase(BaseModel):
    """故障转移规则基础"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = Field(default=True)

    trigger_error_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    trigger_response_time: float = Field(default=30.0, ge=1.0, le=300.0)
    trigger_consecutive_failures: int = Field(default=3, ge=1, le=20)

    fallback_strategy: str = Field(default="priority")
    fallback_sites: List[int] = Field(default=[])

    recovery_success_rate: float = Field(default=0.8, ge=0.5, le=1.0)
    recovery_check_interval: int = Field(default=300, ge=60, le=3600)


class FailoverRuleCreate(FailoverRuleBase):
    """创建故障转移规则请求"""
    pass


class FailoverRuleUpdate(BaseModel):
    """更新故障转移规则请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

    trigger_error_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    trigger_response_time: Optional[float] = Field(None, ge=1.0, le=300.0)
    trigger_consecutive_failures: Optional[int] = Field(None, ge=1, le=20)

    fallback_strategy: Optional[str] = None
    fallback_sites: Optional[List[int]] = None

    recovery_success_rate: Optional[float] = Field(None, ge=0.5, le=1.0)
    recovery_check_interval: Optional[int] = Field(None, ge=60, le=3600)


class FailoverRuleResponse(FailoverRuleBase):
    """故障转移规则响应"""
    id: int
    last_triggered: Optional[datetime]
    last_recovered: Optional[datetime]
    create_time: Optional[datetime]
    update_time: Optional[datetime]

    class Config:
        from_attributes = True


# ========== 负载均衡 Schema ==========

class LoadBalancerBase(BaseModel):
    """负载均衡器基础"""
    name: str = Field(..., min_length=1, max_length=100)
    strategy: str = Field(default="round_robin")
    is_active: bool = Field(default=True)

    site_ids: List[int] = Field(default=[])
    weights: Dict[str, float] = Field(default={})

    health_check_enabled: bool = Field(default=True)
    health_check_interval: int = Field(default=60, ge=30, le=3600)


class LoadBalancerCreate(LoadBalancerBase):
    """创建负载均衡器请求"""

    @validator('site_ids')
    def validate_site_ids(cls, v):
        if len(v) < 2:
            raise ValueError('负载均衡器至少需要2个站点')
        return v


class LoadBalancerUpdate(BaseModel):
    """更新负载均衡器请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    strategy: Optional[str] = None
    is_active: Optional[bool] = None

    site_ids: Optional[List[int]] = None
    weights: Optional[Dict[str, float]] = None

    health_check_enabled: Optional[bool] = None
    health_check_interval: Optional[int] = Field(None, ge=30, le=3600)


class LoadBalancerResponse(LoadBalancerBase):
    """负载均衡器响应"""
    id: int
    total_requests: int
    last_request_time: Optional[datetime]
    current_active_sites: List[int]
    last_rotation_time: Optional[datetime]
    create_time: Optional[datetime]
    update_time: Optional[datetime]

    class Config:
        from_attributes = True


# ========== 站点测试 Schema ==========

class SiteTestResult(BaseModel):
    """站点测试结果"""
    test_name: str
    success: bool
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SiteTestResponse(BaseModel):
    """站点测试响应"""
    site_id: int
    site_name: str
    test_number: str
    overall_success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_results: List[SiteTestResult]
    test_duration: float
    tested_at: datetime


# ========== 批量操作 Schema ==========

class BatchHealthCheckRequest(BaseModel):
    """批量健康检查请求"""
    site_ids: Optional[List[int]] = None
    include_disabled: bool = Field(default=False)


class BatchHealthCheckResponse(BaseModel):
    """批量健康检查响应"""
    total_checked: int
    healthy_sites: int
    unhealthy_sites: int
    results: List[Dict[str, Any]]
    checked_at: datetime


# ========== 仪表板 Schema ==========

class DashboardSiteStats(BaseModel):
    """仪表板站点统计"""
    total: int
    active: int
    disabled: int
    degraded: int
    maintenance: int
    blocked: int


class DashboardErrorStats(BaseModel):
    """仪表板错误统计"""
    total: int
    unresolved: int
    recent_24h: int
    recent_7d: int


class DashboardOverviewResponse(BaseModel):
    """仪表板概览响应"""
    sites: DashboardSiteStats
    errors: DashboardErrorStats
    top_error_sites: List[Dict[str, Any]]
    performance_summary: Dict[str, float]
    timestamp: datetime