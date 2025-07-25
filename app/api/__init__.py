from fastapi import APIRouter, Depends

from app.api import auth, user, setting, video, common, file, download, history, schedule, home, subscribe, auto_download, version, download_filter
from app.dependencies.security import verify_token

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(common.router, prefix="/common")
api_router.include_router(user.router, prefix='/user', dependencies=[Depends(verify_token)])
api_router.include_router(setting.router, prefix='/setting', dependencies=[Depends(verify_token)])

api_router.include_router(video.router, prefix='/video')
api_router.include_router(file.router, prefix='/file', dependencies=[Depends(verify_token)])
api_router.include_router(download.router, prefix='/download', dependencies=[Depends(verify_token)])
api_router.include_router(history.router, prefix='/history', dependencies=[Depends(verify_token)])
api_router.include_router(schedule.router, prefix='/schedule', dependencies=[Depends(verify_token)])
api_router.include_router(home.router, prefix='/home', dependencies=[Depends(verify_token)])
api_router.include_router(subscribe.router, prefix='/subscribe', dependencies=[Depends(verify_token)])
api_router.include_router(auto_download.router, prefix='/auto-download', dependencies=[Depends(verify_token)])
api_router.include_router(version.router, prefix='/version', dependencies=[Depends(verify_token)])
api_router.include_router(download_filter.router, prefix='/download-filter', dependencies=[Depends(verify_token)])
