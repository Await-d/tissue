"""
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 14:27:14
Description: 请填写简介
"""

from fastapi import APIRouter

from app.integrations.downloaders.manager import downloader_manager
from app.schema import Setting
from app.schema.r import R
from app.service.setting import SettingService

router = APIRouter()


@router.get("/")
def get_settings():
    settings = Setting()
    return R.ok(settings)


@router.post("/")
def save_setting(section: str, setting: dict):
    SettingService.save_section(section, setting)
    return R.ok()


@router.get("/test-qbittorrent")
def test_qbittorrent_connection():
    result = downloader_manager.get_active().test_connection()
    if result["status"]:
        return R.ok(result)
    return R.fail(result["message"], data=result)
