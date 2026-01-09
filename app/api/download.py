from fastapi import APIRouter, Depends

from app.schema.r import R
from app.service.download import get_download_service

router = APIRouter()


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
