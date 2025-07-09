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
    return R.list(downloads)


@router.get('/complete')
def complete_download(torrent_hash: str, service=Depends(get_download_service)):
    service.complete_download(torrent_hash)
    return R.ok()
