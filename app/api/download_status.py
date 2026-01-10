"""
Author: Await
Date: 2026-01-11
Description: 下载状态检测 API 路由

已实现速率限制功能：
- 使用自定义的基于内存的速率限制器
- 配置: 每个 IP 每分钟最多 30 次请求
- 超过限制返回 429 错误，包含重试时间
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app import schema
from app.schema.r import R
from app.service.download_status import get_download_status_service, DownloadStatusService
from app.utils.rate_limiter import rate_limit

router = APIRouter()


@router.post("/check-batch", response_model=R[dict])
@rate_limit(max_requests=30, window_seconds=60)
def check_download_status_batch(
    request: Request,
    batch_request: schema.DownloadStatusBatchRequest,
    service: DownloadStatusService = Depends(get_download_status_service)
):
    """
    批量检测番号的下载状态

    已应用速率限制：每个 IP 每分钟最多 30 次请求

    Args:
        request: FastAPI 请求对象（用于速率限制）
        batch_request: 包含番号列表的请求对象
        service: 下载状态服务实例（通过依赖注入获取）

    Returns:
        R[dict]: 包含番号与下载状态映射的响应对象
            - success: True
            - data: {"番号1": True/False, "番号2": True/False, ...}

    Raises:
        HTTPException:
            - 429: 请求过于频繁，超过速率限制
            - 500: 服务器内部错误
    """
    try:
        result = service.check_download_status_batch(batch_request.nums)
        return R.ok(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测下载状态失败: {str(e)}"
        )
