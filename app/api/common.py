'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 16:16:27
Description: 请填写简介
'''
import hashlib
import re
import mimetypes
from urllib.parse import urlparse

import httpx
import requests
from cachetools import cached, TTLCache
from fastapi import APIRouter, Response, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.schema.r import R
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
    cover = spider.get_video_cover(normalized_url)
    if not cover:
        raise HTTPException(status_code=502, detail='封面读取失败')

    headers = {
        'Cache-Control': 'public, max-age=31536000',
        'ETag': hashlib.md5(normalized_url.encode()).hexdigest(),
    }
    return Response(content=cover, media_type=_guess_image_media_type(normalized_url), headers=headers)


@router.get("/trailer")
async def proxy_video_trailer(url: str, request: Request):
    headers = {
        "Range": request.headers.get("Range", ""),
        "User-Agent": request.headers.get("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
        "Accept": "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://javdb.com/"
    }
    
    # 为 javdb 相关请求设置必要的 cookies
    cookies = {}
    parsed_url = urlparse(url)
    if 'javdb' in parsed_url.netloc:
        cookies = {
            "over18": "1",
            "locale": "zh"
        }

    async with httpx.AsyncClient(follow_redirects=False, timeout=30.0) as client:
        if url.startswith("//"):
            url = 'https:' + url
        
        try:
            response = await client.get(url, headers=headers, cookies=cookies)
            
            # 处理重定向到登录页面的情况
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_location = response.headers.get("location", "")
                if "login" in redirect_location.lower() or "sign_in" in redirect_location.lower():
                    raise HTTPException(
                        status_code=403,
                        detail="访问视频预览需要认证，请检查 JavDB 配置或稍后重试"
                    )
                # 对于其他重定向，跟随一次
                if redirect_location:
                    if not redirect_location.startswith('http'):
                        redirect_location = f"{parsed_url.scheme}://{parsed_url.netloc}{redirect_location}"
                    response = await client.get(redirect_location, headers=headers, cookies=cookies)
            
            response.raise_for_status()

            async def video_stream():
                async for chunk in response.aiter_bytes(1024 * 1024):
                    yield chunk

            return StreamingResponse(
                video_stream(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.HTTPStatusError as e:
            # 记录错误详情
            raise HTTPException(
                status_code=e.response.status_code if e.response else 500,
                detail=f"无法获取视频预览: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"视频代理错误: {str(e)}"
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
