'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 16:16:27
Description: 请填写简介
'''
import hashlib
import mimetypes
import re
from urllib.parse import urlparse

import requests
from cachetools import cached, TTLCache
from fastapi import APIRouter, Response, Request, HTTPException

from app.schema.r import R
from app.service.resource import ResourceService
from app.utils import spider
from version import APP_VERSION

router = APIRouter()


def _normalize_cover_url(url: str):
    normalized = (url or '').strip()
    if not normalized:
        raise HTTPException(status_code=422, detail='封面地址为空')

    if normalized.startswith('//'):
        normalized = 'https:' + normalized

    parsed = urlparse(normalized)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise HTTPException(status_code=422, detail='封面地址格式无效，仅支持 http/https')

    return normalized


def _guess_image_media_type(url: str):
    mime_type, _ = mimetypes.guess_type(urlparse(url).path)
    if mime_type and mime_type.startswith('image/'):
        return mime_type
    return 'image/jpeg'


@router.get("/cover")
def proxy_video_cover(url: str):
    normalized_url = _normalize_cover_url(url)
    response = ResourceService.proxy_cover(normalized_url)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail='封面读取失败')
    return response


@router.get("/trailer")
async def proxy_video_trailer(
    url: str,
    request: Request,
    base_url: str | None = None,
):
    return await ResourceService.proxy_trailer(url, request, base_url=base_url)

@router.get("/version")
@cached(cache=TTLCache(maxsize=1, ttl=3600))
def get_versions():
    current = APP_VERSION[1:]
    latest = current  # 默认值为当前版本

    try:
        response = requests.get("https://raw.githubusercontent.com/Await-d/tissue/master/version.py", timeout=10)
        if response.status_code == 200:
            # 使用更灵活的正则表达式匹配
            match = re.search(r"APP_VERSION\s*=\s*['\"]v?(.+?)['\"]", response.text)
            if match:
                latest = match.group(1)
            else:
                print("未能从响应中匹配到版本号")
    except Exception as e:
        # 捕获所有异常，包括网络错误、超时等
        print(f"获取最新版本失败: {e}")

    return R.ok({
        "current": current,
        "latest": latest,
    })
