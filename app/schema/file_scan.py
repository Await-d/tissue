"""
文件扫描相关的Schema定义
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ScanTriggerRequest(BaseModel):
    """手动触发扫描请求模型"""
    force_rescan: Optional[bool] = Field(False, description="是否强制重新扫描，默认False")


class ScanResultResponse(BaseModel):
    """扫描结果响应模型"""
    scan_id: int = Field(..., description="扫描记录ID")
    scan_time: datetime = Field(..., description="扫描时间")
    total_files: int = Field(..., description="扫描文件总数")
    new_found: int = Field(..., description="新发现视频数")
    already_exists: int = Field(..., description="已存在视频数")
    scan_duration: float = Field(..., description="扫描耗时(秒)")
    status: str = Field(..., description="扫描状态: running/success/failed")
    error_message: Optional[str] = Field(None, description="错误信息")

    class Config:
        from_attributes = True


class ScanRecordListResponse(BaseModel):
    """扫描记录列表响应模型"""
    records: List[ScanResultResponse] = Field(..., description="扫描记录列表")
    total: int = Field(..., description="总记录数")

    class Config:
        from_attributes = True
