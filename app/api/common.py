'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 16:16:27
Description: 请填写简介
'''
import hashlib
import re

import httpx
import requests
from cachetools import cached, TTLCache
from fastapi import APIRouter, Response, Request
from fastapi.responses import StreamingResponse

from app.schema.r import R
from app.utils import spider
from version import APP_VERSION

router = APIRouter()


@router.get("/cover")
def proxy_video_cover(url: str):
    cover = spider.get_video_cover(url)
    headers = {
        'Cache-Control': 'public, max-age=31536000',
        'ETag': hashlib.md5(url.encode()).hexdigest(),
    }
    return Response(content=cover, media_type="image", headers=headers)


@router.get("/trailer")
async def proxy_video_trailer(url: str, request: Request):
    headers = {
        "Range": request.headers.get("Range", ""),
        "User-Agent": request.headers.get("User-Agent")
    }

    async with httpx.AsyncClient() as client:
        if url.startswith("//"):
            url = 'http:' + url
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        async def video_stream():
            async for chunk in response.aiter_bytes(1024 * 1024):
                yield chunk

        return StreamingResponse(
            video_stream(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )


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
