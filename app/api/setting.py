from fastapi import APIRouter
from pydantic import BaseModel

from app.scheduler import scheduler
from app.schema import Setting
from app.schema.r import R
from app.utils.qbittorent import qbittorent
from app.utils.logger import logger

router = APIRouter()


@router.get("/")
def get_settings():
    settings = Setting()
    return R.ok(settings)


@router.post('/')
def save_setting(section: str, setting: dict):
    Setting.write_section(section, setting)
    if section == 'download':
        trans_auto = setting.get('trans_auto')
        if trans_auto:
            scheduler.add('scrape_download')
        else:
            scheduler.remove('scrape_download')

        delete_auto = setting.get('delete_auto')
        if delete_auto:
            scheduler.add('delete_complete_download')
        else:
            scheduler.remove('delete_complete_download')

        qbittorent.host = setting.get('host')
        qbittorent.tracker_subscribe = setting.get('tracker_subscribe')
        qbittorent.savepath = setting.get('savepath')

    return R.ok()


@router.get("/test-qbittorrent")
def test_qbittorrent_connection():
    """
    测试qBittorrent下载器连接
    """
    try:
        result = qbittorent.test_connection()
        if result["status"]:
            return R.ok(result)
        else:
            return R.fail(result["message"], data=result)
    except Exception as e:
        logger.error(f"测试qBittorrent连接时出错: {str(e)}")
        return R.fail(f"测试连接时发生错误: {str(e)}")
