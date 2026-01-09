"""
Author: Await
Date: 2026-01-09
Description: 收藏功能API路由
"""
from typing import List

from fastapi import APIRouter, Depends, Query, Path

from app import schema
from app.schema.r import R
from app.schema.favorite import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteListResponse,
    FavoriteBatchRequest,
    FavoriteCheckResponse
)
from app.service.favorite import get_favorite_service
from app.dependencies.security import get_current_user_id

router = APIRouter()


@router.post("/", response_model=R[FavoriteResponse])
def add_favorite(
    data: FavoriteCreate,
    user_id: int = Depends(get_current_user_id),
    service=Depends(get_favorite_service)
):
    """添加收藏

    Args:
        data: 收藏数据
        user_id: 当前用户ID（自动注入）
        service: 收藏服务（自动注入）

    Returns:
        收藏响应
    """
    result = service.add_favorite(user_id, data)
    return R.ok(data=result, message="收藏成功")


@router.delete("/{video_num}")
def remove_favorite(
    video_num: str = Path(..., min_length=1, max_length=50, description="视频番号"),
    user_id: int = Depends(get_current_user_id),
    service=Depends(get_favorite_service)
):
    """取消收藏

    Args:
        video_num: 视频番号
        user_id: 当前用户ID（自动注入）
        service: 收藏服务（自动注入）

    Returns:
        成功响应
    """
    service.remove_favorite(user_id, video_num)
    return R.ok(message="取消收藏成功")


@router.get("/", response_model=R[FavoriteListResponse])
def get_favorites(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    service=Depends(get_favorite_service)
):
    """获取收藏列表

    Args:
        page: 页码
        size: 每页数量
        user_id: 当前用户ID（自动注入）
        service: 收藏服务（自动注入）

    Returns:
        收藏列表响应
    """
    result = service.get_favorites(user_id, page, size)
    return R.ok(data=result)


@router.get("/check", response_model=R[FavoriteCheckResponse])
def check_favorite(
    video_num: str = Query(..., min_length=1, max_length=50, description="视频番号"),
    user_id: int = Depends(get_current_user_id),
    service=Depends(get_favorite_service)
):
    """检查是否已收藏

    Args:
        video_num: 视频番号
        user_id: 当前用户ID（自动注入）
        service: 收藏服务（自动注入）

    Returns:
        收藏状态响应
    """
    is_favorited = service.check_favorite(user_id, video_num)
    return R.ok(data=FavoriteCheckResponse(video_num=video_num, is_favorited=is_favorited))


@router.post("/batch")
def batch_add_favorites(
    data: FavoriteBatchRequest,
    user_id: int = Depends(get_current_user_id),
    service=Depends(get_favorite_service)
):
    """批量添加收藏

    Args:
        data: 批量收藏请求
        user_id: 当前用户ID（自动注入）
        service: 收藏服务（自动注入）

    Returns:
        批量操作结果
    """
    result = service.batch_add_favorites(user_id, data.video_nums)
    return R.ok(data=result, message=f"批量收藏完成，成功{result['success_count']}个，失败{result['failed_count']}个")


@router.delete("/batch")
def batch_remove_favorites(
    data: FavoriteBatchRequest,
    user_id: int = Depends(get_current_user_id),
    service=Depends(get_favorite_service)
):
    """批量取消收藏

    Args:
        data: 批量取消收藏请求
        user_id: 当前用户ID（自动注入）
        service: 收藏服务（自动注入）

    Returns:
        批量操作结果
    """
    result = service.batch_remove_favorites(user_id, data.video_nums)
    return R.ok(data=result, message=f"批量取消收藏完成，成功{result['success_count']}个")
