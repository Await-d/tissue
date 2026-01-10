"""
下载过滤API接口
提供下载过滤设置和操作的REST API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.schema.r import R
from app.service.download_filter import get_download_filter_service, DownloadFilterService
from app.utils.logger import logger

router = APIRouter()


class FilterSettingsRequest(BaseModel):
    """过滤设置请求模型"""
    min_file_size_mb: int = Field(default=300, ge=1, le=10000, description="最小文件大小(MB)")
    max_file_size_mb: Optional[int] = Field(default=None, ge=1, le=50000, description="最大文件大小(MB)")
    allowed_extensions: Optional[List[str]] = Field(default=None, description="允许的文件扩展名列表")
    blocked_extensions: Optional[List[str]] = Field(default=None, description="禁止的文件扩展名列表")
    min_seed_count: Optional[int] = Field(default=1, ge=0, description="最小种子数")
    max_total_size_gb: Optional[float] = Field(default=None, ge=0, description="种子总大小限制(GB)")
    enable_smart_filter: bool = Field(default=True, description="启用智能过滤")
    skip_sample_files: bool = Field(default=True, description="跳过样本文件")
    skip_subtitle_only: bool = Field(default=True, description="跳过仅字幕文件")
    media_files_only: bool = Field(default=False, description="只保留媒体文件(视频+字幕)")
    include_subtitles: bool = Field(default=True, description="包含字幕文件")


class MagnetFilterRequest(BaseModel):
    """磁力链接过滤请求模型"""
    magnet_url: str = Field(..., description="磁力链接")


class TorrentFilterRequest(BaseModel):
    """种子过滤请求模型"""
    torrent_hash: str = Field(..., description="种子Hash")


@router.get("/settings")
def get_filter_settings(service: DownloadFilterService = Depends(get_download_filter_service)):
    """
    获取当前的过滤设置
    """
    try:
        settings = service.get_filter_settings()
        
        if not settings:
            # 返回默认设置
            default_settings = service.get_default_filter_settings()
            return R.ok(default_settings, message="使用默认设置")
        
        # 转换为字典格式
        settings_dict = {
            "id": settings.id,
            "min_file_size_mb": settings.min_file_size_mb,
            "max_file_size_mb": settings.max_file_size_mb,
            "allowed_extensions": settings.allowed_extensions,
            "blocked_extensions": settings.blocked_extensions,
            "min_seed_count": settings.min_seed_count,
            "max_total_size_gb": float(settings.max_total_size_gb) if settings.max_total_size_gb else None,
            "enable_smart_filter": settings.enable_smart_filter,
            "skip_sample_files": settings.skip_sample_files,
            "skip_subtitle_only": settings.skip_subtitle_only,
            "media_files_only": getattr(settings, 'media_files_only', False),
            "include_subtitles": getattr(settings, 'include_subtitles', True),
            "is_active": settings.is_active,
            "created_at": settings.created_at.isoformat() if settings.created_at else None,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None,
        }
        
        return R.ok(settings_dict)
        
    except Exception as e:
        logger.error(f"获取过滤设置失败: {e}")
        return R.fail(f"获取设置失败: {str(e)}")


@router.post("/settings")
def save_filter_settings(
    request: FilterSettingsRequest,
    service: DownloadFilterService = Depends(get_download_filter_service)
):
    """
    保存过滤设置
    """
    try:
        # 转换请求数据
        settings_data = request.dict()
        
        # 处理扩展名列表
        if settings_data["allowed_extensions"]:
            import json
            settings_data["allowed_extensions"] = json.dumps(settings_data["allowed_extensions"])
        
        if settings_data["blocked_extensions"]:
            import json
            settings_data["blocked_extensions"] = json.dumps(settings_data["blocked_extensions"])
        
        # 保存设置
        settings = service.create_or_update_filter_settings(settings_data)
        
        return R.ok({
            "id": settings.id,
            "message": "设置保存成功"
        })
        
    except Exception as e:
        logger.error(f"保存过滤设置失败: {e}")
        return R.fail(f"保存设置失败: {str(e)}")


@router.post("/test-magnet")
def test_magnet_filter(
    request: MagnetFilterRequest,
    service: DownloadFilterService = Depends(get_download_filter_service)
):
    """
    测试磁力链接过滤效果
    """
    try:
        result = service.apply_filter_to_magnet(request.magnet_url)
        
        return R.ok(result, message="过滤测试完成")
        
    except Exception as e:
        logger.error(f"测试磁力链接过滤失败: {e}")
        return R.fail(f"测试失败: {str(e)}")


@router.post("/filter-torrent")
def filter_torrent(
    request: TorrentFilterRequest,
    service: DownloadFilterService = Depends(get_download_filter_service)
):
    """
    对已存在的种子应用过滤规则
    """
    try:
        result = service.filter_torrent_files(request.torrent_hash)
        
        if result["success"]:
            return R.ok(result, message=result["message"])
        else:
            return R.fail(result["message"], data=result)
        
    except Exception as e:
        logger.error(f"过滤种子失败: {e}")
        return R.fail(f"过滤失败: {str(e)}")


@router.get("/statistics")
def get_filter_statistics(service: DownloadFilterService = Depends(get_download_filter_service)):
    """
    获取过滤统计信息
    """
    try:
        stats = service.get_filter_statistics()
        return R.ok(stats)
        
    except Exception as e:
        logger.error(f"获取过滤统计失败: {e}")
        return R.fail(f"获取统计失败: {str(e)}")


@router.get("/default-settings")
def get_default_settings(service: DownloadFilterService = Depends(get_download_filter_service)):
    """
    获取默认设置
    """
    try:
        default_settings = service.get_default_filter_settings()
        return R.ok(default_settings)
        
    except Exception as e:
        logger.error(f"获取默认设置失败: {e}")
        return R.fail(f"获取默认设置失败: {str(e)}")


@router.post("/reset-settings")
def reset_to_default_settings(service: DownloadFilterService = Depends(get_download_filter_service)):
    """
    重置为默认设置
    """
    try:
        default_settings = service.get_default_filter_settings()
        settings = service.create_or_update_filter_settings(default_settings)

        return R.ok({
            "id": settings.id,
            "message": "设置已重置为默认值"
        })

    except Exception as e:
        logger.error(f"重置设置失败: {e}")
        return R.fail(f"重置失败: {str(e)}")


@router.post("/cleanup-torrent/{torrent_hash}")
def cleanup_torrent(
    torrent_hash: str,
    dry_run: bool = True,
    service: DownloadFilterService = Depends(get_download_filter_service)
):
    """
    清理指定种子中不需要的文件

    Args:
        torrent_hash: 种子hash
        dry_run: 是否为模拟运行模式，True时仅返回将被删除的文件列表，不实际删除
    """
    try:
        result = service.cleanup_torrent_files(torrent_hash, dry_run=dry_run)

        if result["success"]:
            return R.ok(result, message=result["message"])
        else:
            return R.fail(result["message"], data=result)

    except Exception as e:
        logger.error(f"清理种子文件失败: {e}")
        return R.fail(f"清理失败: {str(e)}")


@router.post("/cleanup-all")
def cleanup_all_torrents(
    category: str = None,
    dry_run: bool = True,
    service: DownloadFilterService = Depends(get_download_filter_service)
):
    """
    批量清理所有种子（或指定分类）中不需要的文件

    Args:
        category: 种子分类，如果为None则处理所有种子
        dry_run: 是否为模拟运行模式，True时仅返回将被删除的文件列表，不实际删除
    """
    try:
        result = service.cleanup_all_torrents(category=category, dry_run=dry_run)

        if result["success"]:
            return R.ok(result, message=result["message"])
        else:
            return R.fail(result["message"], data=result)

    except Exception as e:
        logger.error(f"批量清理种子文件失败: {e}")
        return R.fail(f"批量清理失败: {str(e)}")


@router.get("/preview-cleanup/{torrent_hash}")
def preview_cleanup(
    torrent_hash: str,
    service: DownloadFilterService = Depends(get_download_filter_service)
):
    """
    预览指定种子的清理结果（仅返回将被删除的文件列表，不实际删除）

    Args:
        torrent_hash: 种子hash
    """
    try:
        result = service.cleanup_torrent_files(torrent_hash, dry_run=True)

        if result["success"]:
            return R.ok(result, message=result["message"])
        else:
            return R.fail(result["message"], data=result)

    except Exception as e:
        logger.error(f"预览清理结果失败: {e}")
        return R.fail(f"预览失败: {str(e)}")