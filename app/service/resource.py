import ipaddress
import mimetypes
import os
from dataclasses import dataclass
from typing import Literal, Optional
from urllib.parse import urlparse

import httpx
from fastapi import Request, Response
from fastapi.responses import StreamingResponse

from app.schema import Setting
from app.utils import cache
from app.utils.logger import logger
from app.utils.m3u8 import fix_m3u8_paths, is_m3u8
from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.javdb import JavdbSpider
from app.utils.spider.spider import Spider


ImageCacheType = Literal["cover", "avatar", "preview"]


@dataclass(slots=True)
class ImageResult:
    """图片抓取结果。file_path 为空时表示失败，由 status_code 说明原因。"""

    file_path: Optional[str]
    media_type: Optional[str]
    status_code: int
    etag: Optional[str] = None


class ResourceService:
    # 浏览器端缓存时长
    IMAGE_CLIENT_CACHE_MAX_AGE_SECONDS = 24 * 60 * 60
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
    def _image_cache_ttl() -> int:
        """图片缓存有效期，取自设置项 app.cover_cache_ttl。"""
        try:
            ttl = int(Setting().app.cover_cache_ttl)
            return ttl if ttl > 0 else cache.DEFAULT_CACHE_TTL_SECONDS
        except Exception:
            return cache.DEFAULT_CACHE_TTL_SECONDS

    @staticmethod
    def normalize_image_url(url: str) -> str:
        normalized = (url or "").strip()
        if normalized.startswith("//"):
            normalized = f"https:{normalized}"
        return normalized

    @classmethod
    def is_remote_image(cls, url: str) -> bool:
        component = urlparse(url)
        return component.scheme in {"http", "https"}

    @staticmethod
    def _guess_image_media_type(url: str) -> str:
        mime_type, _ = mimetypes.guess_type(urlparse(url).path)
        if mime_type and mime_type.startswith("image/"):
            return mime_type
        return "image/jpeg"

    @staticmethod
    def _fetch_cover_by_host(url: str) -> tuple[int, bytes | None, str | None]:
        """按图片 host 选择带对应 Referer/Cookie 的抓取通道。

        所有分支都走 curl_cffi + impersonate，不再有裸 httpx 的降级路径。
        """
        hostname = (urlparse(url).hostname or "").lower()
        if hostname in {"c0.jdbstatic.com", "jdbstatic.com"} or hostname.endswith(".jdbstatic.com"):
            return JavdbSpider.fetch_cover(url)
        if hostname in {"www.javbus.com", "javbus.com"} or hostname.endswith(".javbus.com"):
            return JavbusSpider.fetch_cover(url)
        return Spider.fetch_cover(url)

    @staticmethod
    def is_image_binary(content: bytes | None) -> bool:
        """按魔数判断是否为图片。

        风控/年龄验证页面常以 200 返回 HTML，若不校验就会把错误页当图片缓存下来，
        之后即使源站恢复，前端仍会一直读到这份坏缓存。
        """
        if not content:
            return False
        if content.startswith(b"\xff\xd8\xff"):  # jpeg
            return True
        if content.startswith(b"\x89PNG\r\n\x1a\n"):  # png
            return True
        if content.startswith((b"GIF87a", b"GIF89a")):  # gif
            return True
        if content.startswith(b"RIFF") and content[8:12] == b"WEBP":  # webp
            return True
        if (
            len(content) >= 12
            and content[4:8] == b"ftyp"
            and content[8:12] in (b"avif", b"mif1")
        ):  # avif/heif
            return True
        return False

    @classmethod
    def _cached_file_is_valid(cls, file_path, metadata) -> bool:
        """校验磁盘上的缓存文件：既看魔数，也比对尺寸。

        只看魔数会漏掉\"头部完好、内容截断或交错\"的坏文件——那种文件会在
        整个 TTL 内被当成好图持续返回，即使源站早已恢复。
        元数据里已经记了写入时的 size，拿它比对即可，成本仍然很低。
        """
        try:
            with open(file_path, "rb") as file:
                if not cls.is_image_binary(file.read(16)):
                    return False

            expected_size = (metadata or {}).get("size")
            if isinstance(expected_size, int) and expected_size > 0:
                if os.path.getsize(file_path) != expected_size:
                    return False

            return True
        except OSError:
            return False

    @classmethod
    def fetch_image_file(cls, url: str, image_type: ImageCacheType = "cover") -> ImageResult:
        """取图片，优先本地缓存；上游失败时回落到过期副本，全失败才写负缓存。"""
        normalized_url = cls.normalize_image_url(url)
        blocked_status = cls.get_remote_url_block_status(normalized_url)
        if blocked_status is not None:
            return ImageResult(file_path=None, media_type=None, status_code=blocked_status)

        lookup = cache.get_cache_lookup(image_type, normalized_url)

        stale_path: str | None = None
        stale_media_type: str | None = None
        stale_etag: str | None = None

        if lookup.cache_status == "hit" and lookup.file_path is not None:
            if cls._cached_file_is_valid(lookup.file_path, lookup.metadata):
                stale_path = str(lookup.file_path)
                stale_media_type = (
                    lookup.metadata.get("content_type")
                    or cls._guess_image_media_type(normalized_url)
                )
                stale_etag = cache.build_cache_etag(image_type, normalized_url, lookup.metadata)
                if lookup.status == "fresh":
                    return ImageResult(
                        file_path=stale_path,
                        media_type=stale_media_type,
                        status_code=200,
                        etag=stale_etag,
                    )
            else:
                # 历史遗留的坏缓存（HTML 错误页等），清掉后重新抓取
                logger.warning(f"缓存内容非图片，清理后重新抓取: {normalized_url}")
                cache.clean_cache_file(image_type, normalized_url)
        elif lookup.cache_status == "negative" and lookup.status == "fresh":
            error_code = (lookup.metadata or {}).get("error_code") or 502
            return ImageResult(file_path=None, media_type=None, status_code=int(error_code))

        status_code, content, content_type = cls._fetch_cover_by_host(normalized_url)

        # 只有确认是图片才写缓存，避免把风控/验证页当成封面存下来
        if content and not cls.is_image_binary(content):
            logger.warning(f"上游返回内容不是图片，按失败处理: {normalized_url}")
            content = None
            status_code = status_code if status_code and status_code >= 400 else 502

        if content:
            media_type = content_type or cls._guess_image_media_type(normalized_url)
            if not media_type.startswith("image/"):
                media_type = cls._guess_image_media_type(normalized_url)
            metadata = cache.write_success_cache(
                image_type,
                normalized_url,
                content,
                media_type,
                ttl=cls._image_cache_ttl(),
            )
            return ImageResult(
                file_path=str(cache.get_cache_data_path(image_type, normalized_url)),
                media_type=media_type,
                status_code=200,
                etag=cache.build_cache_etag(image_type, normalized_url, metadata),
            )

        # 上游失败但本地有过期副本：继续提供旧图并延长其可用期限
        if stale_path is not None:
            cache.extend_cache_expiry(
                image_type, normalized_url, cache.get_stale_fallback_ttl_seconds()
            )
            logger.warning(f"图片上游不可用({status_code})，使用过期缓存兜底: {normalized_url}")
            return ImageResult(
                file_path=stale_path,
                media_type=stale_media_type,
                status_code=200,
                etag=stale_etag,
            )

        cache.write_negative_cache(
            image_type,
            normalized_url,
            status_code,
            cache.get_negative_ttl_seconds(status_code),
        )
        return ImageResult(file_path=None, media_type=None, status_code=status_code or 502)

    @classmethod
    def fetch_image_bytes(cls, url: str | None, image_type: ImageCacheType = "cover") -> bytes | None:
        """取图片字节（通知模块等在用）。"""
        if not url:
            return None

        image = cls.fetch_image_file(url, image_type)
        if not image.file_path:
            return None

        try:
            with open(image.file_path, "rb") as file:
                return file.read()
        except OSError:
            return None

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
