"""
站点管理数据模型
用于管理多个视频站点的配置、状态和优先级
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.db.models.base import Base


class SiteStatus(str, Enum):
    """站点状态枚举"""
    ACTIVE = "active"           # 正常激活
    DISABLED = "disabled"       # 手动禁用
    DEGRADED = "degraded"       # 降级状态
    MAINTENANCE = "maintenance"  # 维护状态
    BLOCKED = "blocked"         # 被封锁


class SiteType(str, Enum):
    """站点类型枚举"""
    PRIMARY = "primary"         # 主要站点
    SECONDARY = "secondary"     # 次要站点
    BACKUP = "backup"          # 备用站点
    MIRROR = "mirror"          # 镜像站点


class ManagedSite(Base):
    """站点基础信息表（站点管理功能）"""
    __tablename__ = 'managed_sites'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="站点名称")
    spider_class = Column(String(100), nullable=False, comment="爬虫类名")
    base_url = Column(String(500), nullable=False, comment="站点基础URL")
    mirror_urls = Column(JSON, default=list, comment="镜像URL列表")

    # 站点分类和优先级
    site_type = Column(String(20), default=SiteType.PRIMARY, comment="站点类型")
    priority = Column(Integer, default=100, comment="优先级(数值越低优先级越高)")
    weight = Column(Float, default=1.0, comment="权重值用于负载均衡")

    # 状态管理
    status = Column(String(20), default=SiteStatus.ACTIVE, comment="站点状态")
    is_enabled = Column(Boolean, default=True, comment="是否启用")

    # 功能支持
    supports_download = Column(Boolean, default=False, comment="是否支持下载")
    supports_preview = Column(Boolean, default=False, comment="是否支持预览")
    supports_search = Column(Boolean, default=True, comment="是否支持搜索")
    supports_actor_info = Column(Boolean, default=False, comment="是否支持演员信息")
    supports_ranking = Column(Boolean, default=False, comment="是否支持排行榜")

    # 配置信息
    config = Column(JSON, default=dict, comment="站点特定配置")
    headers = Column(JSON, default=dict, comment="自定义请求头")
    rate_limit = Column(Integer, default=1, comment="请求间隔(秒)")
    timeout = Column(Integer, default=30, comment="请求超时时间(秒)")
    max_retries = Column(Integer, default=3, comment="最大重试次数")

    # 地理位置和语言
    region = Column(String(10), comment="地理区域")
    language = Column(String(10), default="zh", comment="主要语言")

    # 描述信息
    description = Column(Text, comment="站点描述")
    tags = Column(JSON, default=list, comment="站点标签")

    # 关联关系
    statistics = relationship("SiteStatistics", back_populates="managed_site", uselist=False, cascade="all, delete-orphan")
    health_checks = relationship("SiteHealthCheck", back_populates="managed_site", cascade="all, delete-orphan")
    error_logs = relationship("SiteErrorLog", back_populates="managed_site", cascade="all, delete-orphan")

    @hybrid_property
    def current_url(self) -> str:
        """获取当前可用的URL"""
        if self.status == SiteStatus.ACTIVE:
            return self.base_url
        elif self.mirror_urls:
            return self.mirror_urls[0]
        return self.base_url

    @hybrid_property
    def is_healthy(self) -> bool:
        """判断站点是否健康"""
        return self.status in [SiteStatus.ACTIVE, SiteStatus.DEGRADED] and self.is_enabled

    def get_next_mirror_url(self) -> Optional[str]:
        """获取下一个镜像URL"""
        if not self.mirror_urls:
            return None
        # 简单轮询策略
        current_index = self.mirror_urls.index(self.base_url) if self.base_url in self.mirror_urls else -1
        next_index = (current_index + 1) % len(self.mirror_urls)
        return self.mirror_urls[next_index]


class SiteStatistics(Base):
    """站点统计信息表"""
    __tablename__ = 'site_statistics'

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey('managed_sites.id'), nullable=False)

    # 请求统计
    total_requests = Column(Integer, default=0, comment="总请求数")
    successful_requests = Column(Integer, default=0, comment="成功请求数")
    failed_requests = Column(Integer, default=0, comment="失败请求数")

    # 性能统计
    avg_response_time = Column(Float, default=0.0, comment="平均响应时间(秒)")
    max_response_time = Column(Float, default=0.0, comment="最大响应时间(秒)")
    min_response_time = Column(Float, default=0.0, comment="最小响应时间(秒)")

    # 数据统计
    videos_scraped = Column(Integer, default=0, comment="抓取的视频数量")
    actors_scraped = Column(Integer, default=0, comment="抓取的演员数量")
    downloads_provided = Column(Integer, default=0, comment="提供的下载数量")

    # 错误统计
    timeout_errors = Column(Integer, default=0, comment="超时错误数")
    connection_errors = Column(Integer, default=0, comment="连接错误数")
    parse_errors = Column(Integer, default=0, comment="解析错误数")
    rate_limit_errors = Column(Integer, default=0, comment="频率限制错误数")

    # 时间范围
    stat_date = Column(DateTime, default=datetime.utcnow, comment="统计日期")
    last_reset = Column(DateTime, default=datetime.utcnow, comment="上次重置时间")

    # 关联关系
    managed_site = relationship("ManagedSite", back_populates="statistics")

    @hybrid_property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @hybrid_property
    def error_rate(self) -> float:
        """错误率"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100


class SiteHealthCheck(Base):
    """站点健康检查表"""
    __tablename__ = 'site_health_checks'

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey('managed_sites.id'), nullable=False)

    # 检查结果
    is_healthy = Column(Boolean, default=True, comment="是否健康")
    response_time = Column(Float, comment="响应时间(毫秒)")
    status_code = Column(Integer, comment="HTTP状态码")
    error_message = Column(Text, comment="错误信息")

    # 检查详情
    check_type = Column(String(50), default="ping", comment="检查类型")
    check_url = Column(String(500), comment="检查的URL")

    # 时间信息
    checked_at = Column(DateTime, default=datetime.utcnow, comment="检查时间")
    next_check = Column(DateTime, comment="下次检查时间")

    # 关联关系
    managed_site = relationship("ManagedSite", back_populates="health_checks")


class SiteErrorLog(Base):
    """站点错误日志表"""
    __tablename__ = 'site_error_logs'

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey('managed_sites.id'), nullable=False)

    # 错误信息
    error_type = Column(String(100), comment="错误类型")
    error_message = Column(Text, comment="错误消息")
    error_details = Column(JSON, comment="错误详情")

    # 请求信息
    request_url = Column(String(500), comment="请求URL")
    request_method = Column(String(10), comment="请求方法")
    request_headers = Column(JSON, comment="请求头")

    # 响应信息
    response_code = Column(Integer, comment="响应状态码")
    response_time = Column(Float, comment="响应时间")

    # 上下文信息
    operation = Column(String(100), comment="操作类型")
    video_number = Column(String(50), comment="相关视频番号")
    actor_name = Column(String(100), comment="相关演员名称")

    # 处理状态
    is_resolved = Column(Boolean, default=False, comment="是否已解决")
    resolution_note = Column(Text, comment="解决方案说明")

    # 时间信息
    occurred_at = Column(DateTime, default=datetime.utcnow, comment="发生时间")
    resolved_at = Column(DateTime, comment="解决时间")

    # 关联关系
    managed_site = relationship("ManagedSite", back_populates="error_logs")


class SiteFailoverRule(Base):
    """站点故障转移规则表"""
    __tablename__ = 'site_failover_rules'

    id = Column(Integer, primary_key=True, index=True)

    # 规则基础信息
    name = Column(String(100), nullable=False, comment="规则名称")
    description = Column(Text, comment="规则描述")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 触发条件
    trigger_error_rate = Column(Float, default=0.5, comment="触发的错误率阈值")
    trigger_response_time = Column(Float, default=30.0, comment="触发的响应时间阈值(秒)")
    trigger_consecutive_failures = Column(Integer, default=3, comment="连续失败次数阈值")

    # 故障转移策略
    fallback_strategy = Column(String(50), default="priority", comment="故障转移策略")
    fallback_sites = Column(JSON, default=list, comment="备用站点ID列表")

    # 恢复条件
    recovery_success_rate = Column(Float, default=0.8, comment="恢复的成功率阈值")
    recovery_check_interval = Column(Integer, default=300, comment="恢复检查间隔(秒)")

    # 时间信息
    last_triggered = Column(DateTime, comment="上次触发时间")
    last_recovered = Column(DateTime, comment="上次恢复时间")


class SiteLoadBalancer(Base):
    """站点负载均衡表"""
    __tablename__ = 'site_load_balancers'

    id = Column(Integer, primary_key=True, index=True)

    # 负载均衡配置
    name = Column(String(100), nullable=False, comment="负载均衡器名称")
    strategy = Column(String(50), default="round_robin", comment="负载均衡策略")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 站点组
    site_ids = Column(JSON, default=list, comment="参与负载均衡的站点ID列表")
    weights = Column(JSON, default=dict, comment="站点权重配置")

    # 健康检查
    health_check_enabled = Column(Boolean, default=True, comment="是否启用健康检查")
    health_check_interval = Column(Integer, default=60, comment="健康检查间隔(秒)")

    # 统计信息
    total_requests = Column(Integer, default=0, comment="总分发请求数")
    last_request_time = Column(DateTime, comment="上次请求时间")

    # 当前状态
    current_active_sites = Column(JSON, default=list, comment="当前活跃站点列表")
    last_rotation_time = Column(DateTime, comment="上次轮换时间")