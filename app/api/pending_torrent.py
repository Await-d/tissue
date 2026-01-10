"""
待处理种子API接口
提供待处理种子管理的REST API
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.schema.r import R
from app.service.pending_torrent import get_pending_torrent_service, PendingTorrentService
from app.utils.logger import logger

router = APIRouter()


@router.get("/list")
def get_pending_list(
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    service: PendingTorrentService = Depends(get_pending_torrent_service)
):
    """
    获取待处理种子列表

    Args:
        status: 状态过滤 (waiting_metadata/metadata_ready/filtering/completed/failed/timeout)
        page: 页码，默认1
        page_size: 每页数量，默认20

    Returns:
        待处理种子列表和总数
    """
    try:
        items, total = service.get_pending_list(status=status, page=page, page_size=page_size)

        # 转换为字典列表
        data = [service.pending_to_dict(item) for item in items]

        return R.list(data, total=total)

    except Exception as e:
        logger.error(f"获取待处理种子列表失败: {e}")
        return R.fail(f"获取列表失败: {str(e)}")


@router.get("/statistics")
def get_statistics(service: PendingTorrentService = Depends(get_pending_torrent_service)):
    """
    获取统计信息

    Returns:
        各状态数量统计
    """
    try:
        statistics = service.get_pending_statistics()
        return R.ok(statistics)

    except Exception as e:
        logger.error(f"获取待处理种子统计失败: {e}")
        return R.fail(f"获取统计失败: {str(e)}")


@router.post("/retry/{torrent_hash}")
def retry_pending(
    torrent_hash: str,
    service: PendingTorrentService = Depends(get_pending_torrent_service)
):
    """
    重试失败的种子

    Args:
        torrent_hash: 种子哈希

    Returns:
        重试结果
    """
    try:
        pending = service.retry_pending(torrent_hash)

        if not pending:
            return R.fail("种子不存在或状态不允许重试")

        return R.ok(service.pending_to_dict(pending), message="重试成功")

    except Exception as e:
        logger.error(f"重试待处理种子失败: {e}")
        return R.fail(f"重试失败: {str(e)}")


@router.delete("/{torrent_hash}")
def delete_pending(
    torrent_hash: str,
    service: PendingTorrentService = Depends(get_pending_torrent_service)
):
    """
    删除待处理记录

    Args:
        torrent_hash: 种子哈希

    Returns:
        删除结果
    """
    try:
        success = service.delete_pending(torrent_hash)

        if not success:
            return R.fail("种子记录不存在")

        return R.ok(message="删除成功")

    except Exception as e:
        logger.error(f"删除待处理种子失败: {e}")
        return R.fail(f"删除失败: {str(e)}")


@router.post("/cleanup")
def cleanup_old_records(
    days: int = Query(default=7, ge=1, le=365, description="保留天数"),
    service: PendingTorrentService = Depends(get_pending_torrent_service)
):
    """
    清理旧记录

    Args:
        days: 保留天数，默认7天，删除早于此天数的已完成/失败/超时记录

    Returns:
        清理结果
    """
    try:
        deleted_count = service.cleanup_old_records(days=days)

        return R.ok({
            "deleted_count": deleted_count,
            "days": days
        }, message=f"成功清理 {deleted_count} 条旧记录")

    except Exception as e:
        logger.error(f"清理待处理种子记录失败: {e}")
        return R.fail(f"清理失败: {str(e)}")
