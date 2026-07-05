import ipaddress
import mimetypes
from hashlib import md5
from typing import Optional
from urllib.parse import urlparse

import httpx
from fastapi import Request, Response
from fastapi.responses import StreamingResponse

from app.schema import Setting
from app.utils import spider
from app.utils.m3u8 import fix_m3u8_paths, is_m3u8


class ResourceService:
    @staticmethod
    def _is_forbidden_ip(address: str) -> bool:
        ip = ipaddress.ip_address(address)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
            or ip.is_reserved
        )

    @classmethod
    def get_remote_url_block_status(cls, url: str) -> int | None:
        component = urlparse(url)
        if component.scheme not in {"http", "https"} or not component.hostname:
            return 400
        try:
            if cls._is_forbidden_ip(component.hostname):
                return 403
        except ValueError:
            return None
        return None

    @staticmethod
    def fetch_image_bytes(url: str | None, image_type: str) -> bytes | None:
        del image_type
        if not url:
            return None

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        if hostname in {"www.javbus.com", "javbus.com", "c0.jdbstatic.com", "jdbstatic.com"}:
            return spider.get_video_cover(url)

        try:
            response = httpx.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                },
                follow_redirects=True,
                timeout=15.0,
            )
            if response.status_code != 200:
                return None
            return response.content
        except Exception:
            return None

    @staticmethod
    def _guess_image_media_type(url: str) -> str:
        mime_type, _ = mimetypes.guess_type(urlparse(url).path)
        if mime_type and mime_type.startswith("image/"):
            return mime_type
        return "image/jpeg"

    @classmethod
    def proxy_cover(cls, url: str) -> Response:
        normalized_url = f"https:{url}" if url.startswith("//") else url
        blocked_status = cls.get_remote_url_block_status(normalized_url)
        if blocked_status is not None:
            return Response(status_code=blocked_status)

        cover = cls.fetch_image_bytes(normalized_url, "cover")
        if not cover:
            return Response(status_code=502)

        return Response(
            content=cover,
            media_type=cls._guess_image_media_type(normalized_url),
            headers={
                "Cache-Control": "public, max-age=31536000",
                "ETag": md5(normalized_url.encode()).hexdigest(),
            },
        )

    @staticmethod
    def _build_proxy_headers(request: Request, url: str) -> dict[str, str]:
        headers: dict[str, str] = {
            "User-Agent": request.headers.get(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            ),
            "Accept": request.headers.get(
                "Accept",
                "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
            ),
            "Accept-Language": request.headers.get("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8"),
        }
        range_header = request.headers.get("Range")
        if range_header:
            headers["Range"] = range_header

        parsed = urlparse(url)
        headers["Referer"] = request.headers.get(
            "Referer",
            f"{parsed.scheme}://{parsed.netloc}/",
        )
        return headers

    @staticmethod
    def _build_cookie_header(url: str) -> str | None:
        parsed = urlparse(url)
        if "javdb" not in (parsed.netloc or ""):
            return None
        setting = Setting().app
        cookies = ["over18=1", "locale=zh"]
        if setting.javdb_cookie:
            cookies.append(setting.javdb_cookie)
        return "; ".join(cookies)

    @classmethod
    async def _proxy_hls_trailer(
        cls,
        url: str,
        headers: dict[str, str],
        request: Request,
        base_url: str | None,
    ) -> Response:
        request_headers = {k: v for k, v in headers.items() if k.lower() != "range"}
        cookie_header = cls._build_cookie_header(url)
        if cookie_header:
            request_headers["Cookie"] = cookie_header

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url, headers=request_headers)
            response.raise_for_status()
            effective_base_url = base_url or str(request.base_url).rstrip("/")
            m3u8_content = fix_m3u8_paths(response.text, url, effective_base_url)
            media_type = response.headers.get("content-type", "application/vnd.apple.mpegurl")
            return Response(content=m3u8_content.encode("utf-8"), media_type=media_type)

    @classmethod
    async def _proxy_binary_trailer(
        cls,
        url: str,
        headers: dict[str, str],
    ) -> Response | StreamingResponse:
        request_headers = dict(headers)
        cookie_header = cls._build_cookie_header(url)
        if cookie_header:
            request_headers["Cookie"] = cookie_header

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            request = client.build_request("GET", url, headers=request_headers)
            response = await client.send(request, stream=True)
            response.raise_for_status()

            excluded_headers = {
                "connection",
                "keep-alive",
                "proxy-authenticate",
                "proxy-authorization",
                "te",
                "trailers",
                "transfer-encoding",
                "upgrade",
                "content-encoding",
            }
            response_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() not in excluded_headers
            }

            async def stream_content():
                async for chunk in response.aiter_bytes(64 * 1024):
                    if chunk:
                        yield chunk

            return StreamingResponse(
                stream_content(),
                status_code=response.status_code,
                headers=response_headers,
            )

    @classmethod
    async def proxy_trailer(
        cls,
        url: str,
        request: Request,
        base_url: Optional[str] = None,
    ) -> Response | StreamingResponse:
        normalized_url = f"https:{url}" if url.startswith("//") else url
        blocked_status = cls.get_remote_url_block_status(normalized_url)
        if blocked_status is not None:
            return Response(status_code=blocked_status)

        headers = cls._build_proxy_headers(request, normalized_url)
        if is_m3u8(normalized_url):
            return await cls._proxy_hls_trailer(normalized_url, headers, request, base_url)
        return await cls._proxy_binary_trailer(normalized_url, headers)
