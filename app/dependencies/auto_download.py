"""
自动下载相关的依赖项
"""
from typing import Optional
from fastapi import Query, HTTPException, status

from app.db.models.auto_download import TimeRangeType


def normalize_time_range_type(time_range_type: Optional[str] = None) -> Optional[TimeRangeType]:
    """
    处理并标准化时间范围类型参数
    
    将时间范围类型参数转换为大写，并验证是否为有效的枚举值
    如果是有效值，返回相应的枚举实例，否则抛出异常
    """
    if time_range_type is None:
        return None
    
    # 转换为大写
    time_range_type = time_range_type.upper()
    
    # 验证是否为有效值
    valid_values = [e.name for e in TimeRangeType]
    if time_range_type not in valid_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{time_range_type}' 不是有效的时间范围类型。可用值: {', '.join(valid_values)}"
        )
    
    # 返回相应的枚举实例
    if time_range_type == "DAY":
        return TimeRangeType.DAY
    elif time_range_type == "WEEK":
        return TimeRangeType.WEEK
    elif time_range_type == "MONTH":
        return TimeRangeType.MONTH
    
    # 以防万一
    return None 