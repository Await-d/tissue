"""
自动下载功能的Schema定义
"""
from datetime import datetime, date
from typing import Optional, List, Any
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, validator


class TimeRangeType(str, Enum):
    """时间范围类型枚举"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class DownloadStatus(str, Enum):
    """下载状态枚举"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


# 自动下载规则相关Schema
class AutoDownloadRuleBase(BaseModel):
    """自动下载规则基础模型"""
    name: str = Field(..., description="规则名称")
    min_rating: Optional[Decimal] = Field(default=0.0, ge=0, le=10, description="最低评分")
    min_comments: Optional[int] = Field(default=0, ge=0, description="最低评论数")
    time_range_type: Optional[TimeRangeType] = Field(default=TimeRangeType.WEEK, description="时间范围类型")
    time_range_value: Optional[int] = Field(default=1, ge=1, description="时间范围值")
    is_hd: bool = Field(default=True, description="是否高清")
    is_zh: bool = Field(default=False, description="是否中文")
    is_uncensored: bool = Field(default=False, description="是否无码")
    is_enabled: bool = Field(default=True, description="是否启用")

    @validator('time_range_type', pre=True)
    def normalize_time_range_type(cls, v):
        """兼容处理：处理各种形式的枚举值输入"""
        if v is None:
            return v
            
        # 如果是枚举实例，直接返回
        if isinstance(v, TimeRangeType):
            return v
            
        # 如果是字符串，转换为小写并检查有效性
        if isinstance(v, str):
            v = v.lower()
            try:
                return TimeRangeType(v)
            except ValueError:
                # 尝试通过名称匹配
                try:
                    return getattr(TimeRangeType, v.upper())
                except AttributeError:
                    raise ValueError(f"'{v}' 不是有效的时间范围类型。可用值: day, week, month")
                    
        # 其他类型，尝试转换为字符串后处理
        return cls.normalize_time_range_type(str(v))


class AutoDownloadRuleCreate(AutoDownloadRuleBase):
    """创建自动下载规则"""
    pass


class AutoDownloadRuleUpdate(BaseModel):
    """更新自动下载规则"""
    id: Optional[int] = None  # 改为可选字段，API中会自动设置
    name: Optional[str] = None
    min_rating: Optional[Decimal] = None
    min_comments: Optional[int] = None
    time_range_type: Optional[TimeRangeType] = None
    time_range_value: Optional[int] = None
    is_hd: Optional[bool] = None
    is_zh: Optional[bool] = None
    is_uncensored: Optional[bool] = None
    is_enabled: Optional[bool] = None
    
    # 重用相同的验证器
    @validator('time_range_type', pre=True)
    def normalize_time_range_type(cls, v):
        """兼容处理：处理各种形式的枚举值输入"""
        if v is None:
            return v
            
        # 如果是枚举实例，直接返回
        if isinstance(v, TimeRangeType):
            return v
            
        # 如果是字符串，转换为小写并检查有效性
        if isinstance(v, str):
            v = v.lower()
            try:
                return TimeRangeType(v)
            except ValueError:
                # 尝试通过名称匹配
                try:
                    return getattr(TimeRangeType, v.upper())
                except AttributeError:
                    raise ValueError(f"'{v}' 不是有效的时间范围类型。可用值: day, week, month")
                    
        # 其他类型，尝试转换为字符串后处理
        return cls.normalize_time_range_type(str(v))


class AutoDownloadRuleResponse(AutoDownloadRuleBase):
    """自动下载规则响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    subscription_count: Optional[int] = Field(default=0, description="订阅数量")
    success_count: Optional[int] = Field(default=0, description="成功下载数量")

    class Config:
        from_attributes = True


# 自动下载订阅记录相关Schema
class AutoDownloadSubscriptionBase(BaseModel):
    """自动下载订阅记录基础模型"""
    rule_id: int = Field(..., description="关联规则ID")
    num: str = Field(..., description="番号")
    title: Optional[str] = Field(None, description="标题")
    rating: Optional[Decimal] = Field(None, description="评分")
    comments_count: Optional[int] = Field(default=0, description="评论数")
    cover: Optional[str] = Field(None, description="封面URL")
    actors: Optional[str] = Field(None, description="演员信息(JSON格式)")
    status: Optional[str] = Field(default="pending", description="下载状态")
    download_url: Optional[str] = Field(None, description="下载链接")
    download_time: Optional[datetime] = Field(None, description="下载时间")
    resource_hash: Optional[str] = Field(None, description="资源唯一标识（用于重复检测）")
    error_message: Optional[str] = Field(None, description="错误信息")

    @validator('status', pre=True)
    def normalize_status(cls, v):
        """标准化状态，确保枚举值正确"""
        if v is None:
            return v
        if isinstance(v, str):
            # 将输入转换为小写
            v_lower = v.lower()
            if v_lower in ['pending', 'downloading', 'completed', 'failed']:
                return v_lower
            # 处理可能的大写输入
            elif v.upper() in ['PENDING', 'DOWNLOADING', 'COMPLETED', 'FAILED']:
                return v.lower()
        return v


class AutoDownloadSubscriptionCreate(AutoDownloadSubscriptionBase):
    """创建自动下载订阅记录"""
    pass


class AutoDownloadSubscriptionUpdate(BaseModel):
    """更新自动下载订阅记录"""
    id: int
    status: Optional[str] = None
    download_url: Optional[str] = None
    download_time: Optional[datetime] = None
    error_message: Optional[str] = None


class AutoDownloadSubscriptionResponse(AutoDownloadSubscriptionBase):
    """自动下载订阅记录响应模型"""
    id: int
    created_at: datetime
    rule_name: Optional[str] = Field(None, description="关联规则名称")

    class Config:
        from_attributes = True


# 查询参数Schema
class AutoDownloadRuleQuery(BaseModel):
    """自动下载规则查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    name: Optional[str] = Field(None, description="规则名称(模糊搜索)")


class AutoDownloadSubscriptionQuery(BaseModel):
    """自动下载订阅记录查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    rule_id: Optional[int] = Field(None, description="规则ID")
    status: Optional[str] = Field(None, description="下载状态")
    num: Optional[str] = Field(None, description="番号(模糊搜索)")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")


# 批量操作Schema
class AutoDownloadBatchOperation(BaseModel):
    """批量操作"""
    ids: List[int] = Field(..., description="要操作的ID列表")
    action: str = Field(..., description="操作类型(delete/retry/pause/resume)")

    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['delete', 'retry', 'pause', 'resume']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of {allowed_actions}')
        return v


# 统计信息Schema
class AutoDownloadStatistics(BaseModel):
    """自动下载统计信息"""
    total_rules: int = Field(default=0, description="总规则数")
    active_rules: int = Field(default=0, description="活跃规则数")
    total_subscriptions: int = Field(default=0, description="总订阅数")
    pending_subscriptions: int = Field(default=0, description="待处理订阅数")
    downloading_subscriptions: int = Field(default=0, description="下载中订阅数")
    completed_subscriptions: int = Field(default=0, description="已完成订阅数")
    failed_subscriptions: int = Field(default=0, description="失败订阅数")
    today_subscriptions: int = Field(default=0, description="今日新增订阅数")
    success_rate: float = Field(default=0.0, description="成功率")


# 手动触发Schema
class AutoDownloadTrigger(BaseModel):
    """手动触发自动下载"""
    rule_ids: Optional[List[int]] = Field(None, description="指定规则ID列表，为空则执行所有启用的规则")
    force: bool = Field(default=False, description="是否强制执行(忽略时间限制)")


# 响应包装Schema
class AutoDownloadResponse(BaseModel):
    """统一响应格式"""
    success: bool = Field(default=True, description="操作是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class AutoDownloadListResponse(BaseModel):
    """列表响应格式"""
    items: List[Any] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数量")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")

    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        total = values.get('total', 0)
        page_size = values.get('page_size', 20)
        return (total + page_size - 1) // page_size if total > 0 else 0