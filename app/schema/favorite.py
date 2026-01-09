"""
Author: Await
Date: 2026-01-09
Description: 收藏功能数据结构
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class FavoriteCreate(BaseModel):
    """创建收藏请求"""
    model_config = ConfigDict(from_attributes=True)

    video_num: str = Field(..., min_length=1, max_length=50, description="视频番号")
    video_title: Optional[str] = Field(None, max_length=500, description="视频标题")
    video_cover: Optional[str] = Field(None, max_length=500, description="视频封面URL")


class FavoriteResponse(BaseModel):
    """收藏响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    video_num: str
    video_title: Optional[str] = None
    video_cover: Optional[str] = None
    created_at: datetime


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    model_config = ConfigDict(from_attributes=True)

    items: List[FavoriteResponse]
    total: int
    page: int
    size: int


class FavoriteBatchRequest(BaseModel):
    """批量收藏请求"""
    model_config = ConfigDict(from_attributes=True)

    video_nums: List[str] = Field(..., min_length=1, max_length=100, description="视频番号列表")


class FavoriteCheckResponse(BaseModel):
    """检查收藏状态响应"""
    model_config = ConfigDict(from_attributes=True)

    video_num: str
    is_favorited: bool
