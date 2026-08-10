'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 16:16:27
Description: 请填写简介
'''
import re
from urllib.parse import urlparse

import requests
from cachetools import cached, TTLCache
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import FileResponse

from app.schema.r import R
from app.service.resource import ImageCacheType, ResourceService
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


@router.get("/cover")
def proxy_video_cover(url: str, request: Request, image_type: ImageCacheType = 'cover'):
    """代理图片。

    命中缓存时直接从磁盘返回（FileResponse），并带上基于内容摘要的 ETag，
    客户端下次带 If-None-Match 即可拿到 304，不必重传图片字节。
    失败时透传真实状态码，前端可据此区分\"地址无效\"与\"源站阻断\"。
    """
    normalized_url = _normalize_cover_url(url)
    image = ResourceService.fetch_image_file(normalized_url, image_type)

    if image.file_path:
        max_age = ResourceService.IMAGE_CLIENT_CACHE_MAX_AGE_SECONDS
        if image.etag and request.headers.get('if-none-match') == image.etag:
            return Response(
                status_code=304,
                headers={
                    'Cache-Control': f'public, max-age={max_age}',
                    'ETag': image.etag,
                },
            )

        headers = {'Cache-Control': f'public, max-age={max_age}'}
        if image.etag:
            headers['ETag'] = image.etag
        return FileResponse(
            path=image.file_path,
            media_type=image.media_type,
            headers=headers,
        )

    return Response(
        status_code=image.status_code,
        headers={'Cache-Control': 'no-cache'},
    )


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
