"""
下载状态检测的Schema定义
"""
from typing import Dict, List

from pydantic import BaseModel, Field


class DownloadStatusBatchRequest(BaseModel):
    """批量检测下载状态请求模型"""
    nums: List[str] = Field(..., description="番号列表")


class DownloadStatusBatchResponse(BaseModel):
    """批量检测下载状态响应模型"""
    data: Dict[str, bool] = Field(..., description="番号与下载状态的映射，True表示已下载，False表示未下载")
