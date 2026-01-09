from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

from app.schema.r import R
from app.service.download import get_download_service
from app.utils.logger import logger

router = APIRouter()


class SetFilePriorityRequest(BaseModel):
    """设置文件优先级请求"""
    torrent_hash: str
    file_indices: List[int]  # 文件索引列表
    priority: int  # 0=不下载, 1=正常, 6=高, 7=最高


class ApplyFilterRequest(BaseModel):
    """应用过滤规则请求"""
    torrent_hash: str


@router.get("/")
def get_downloads(
    include_success: bool = True,
    include_failed: bool = True,
    service=Depends(get_download_service)
):
    downloads = service.get_downloads(include_success=include_success, include_failed=include_failed)

    # 如果返回空列表且配置未设置，返回提示信息
    if len(downloads) == 0 and not service.setting.download.host:
        return R.list(downloads, message="请先在设置页面配置qBittorrent连接信息")

    return R.list(downloads)


@router.get('/complete')
def complete_download(torrent_hash: str, service=Depends(get_download_service)):
    service.complete_download(torrent_hash)
    return R.ok()


@router.get('/test-connection')
def test_qbittorrent_connection(service=Depends(get_download_service)):
    """测试qBittorrent连接状态"""
    test_result = service.qb.test_connection()
    return R.ok(test_result)


@router.get('/torrent/{torrent_hash}/files')
def get_torrent_files(torrent_hash: str, service=Depends(get_download_service)):
    """获取种子的文件列表"""
    try:
        files = service.get_torrent_files(torrent_hash)
        return R.ok(files)
    except Exception as e:
        logger.error(f"获取种子文件列表失败: {e}")
        return R.fail(f"获取文件列表失败: {str(e)}")


@router.post('/torrent/files/priority')
def set_files_priority(request: SetFilePriorityRequest, service=Depends(get_download_service)):
    """设置文件下载优先级"""
    try:
        result = service.set_files_priority(
            request.torrent_hash,
            request.file_indices,
            request.priority
        )
        return R.ok(result, message="优先级设置成功")
    except Exception as e:
        logger.error(f"设置文件优先级失败: {e}")
        return R.fail(f"设置优先级失败: {str(e)}")


@router.post('/torrent/apply-filter')
def apply_filter_to_torrent(request: ApplyFilterRequest, service=Depends(get_download_service)):
    """对种子应用全局过滤规则"""
    try:
        result = service.apply_filter_to_torrent(request.torrent_hash)
        if result['success']:
            return R.ok(result, message=result['message'])
        else:
            return R.fail(result['message'], data=result)
    except Exception as e:
        logger.error(f"应用过滤规则失败: {e}")
        return R.fail(f"应用过滤规则失败: {str(e)}")


@router.post('/torrent/{torrent_hash}/pause')
def pause_torrent(torrent_hash: str, service=Depends(get_download_service)):
    """暂停种子下载"""
    try:
        service.pause_torrent(torrent_hash)
        return R.ok(message="已暂停下载")
    except Exception as e:
        logger.error(f"暂停种子失败: {e}")
        return R.fail(f"暂停失败: {str(e)}")


@router.post('/torrent/{torrent_hash}/resume')
def resume_torrent(torrent_hash: str, service=Depends(get_download_service)):
    """恢复种子下载"""
    try:
        service.resume_torrent(torrent_hash)
        return R.ok(message="已恢复下载")
    except Exception as e:
        logger.error(f"恢复种子失败: {e}")
        return R.fail(f"恢复失败: {str(e)}")


@router.delete('/torrent/{torrent_hash}')
def delete_torrent(torrent_hash: str, delete_files: bool = False, service=Depends(get_download_service)):
    """删除种子"""
    try:
        service.delete_torrent(torrent_hash, delete_files)
        return R.ok(message="已删除种子" + ("及文件" if delete_files else ""))
    except Exception as e:
        logger.error(f"删除种子失败: {e}")
        return R.fail(f"删除失败: {str(e)}")
