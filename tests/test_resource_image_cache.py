"""封面图缓存链路测试

覆盖首页/详情页封面加载失败的几个根因场景：
- 新鲜缓存不重复打上游
- 上游失败时回落到过期副本（而不是直接 502）
- 失效地址写负缓存，避免反复请求
- 风控/错误页（HTML）不会被当成图片缓存下来
"""

import time

import pytest

from app.utils import cache
from app.service.resource import ResourceService

JPEG = b"\xff\xd8\xff" + b"payload" * 20
PNG = b"\x89PNG\r\n\x1a\n" + b"payload" * 20
HTML = b"<html><body>Just a moment...</body></html>"

COVER_URL = "https://img.example.com/cover.jpg"


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """把缓存目录指向临时目录，避免污染真实的 config/cache。"""
    monkeypatch.setattr(cache, "cache_path", tmp_path / "cache")
    yield


@pytest.fixture
def fake_upstream(monkeypatch):
    """替换按 host 分派的抓取通道，返回可编排的响应序列。"""

    calls = []

    def install(*responses):
        queue = list(responses)

        def _fetch(url):
            calls.append(url)
            return queue.pop(0) if len(queue) > 1 else queue[0]

        monkeypatch.setattr(ResourceService, "_fetch_cover_by_host", staticmethod(_fetch))
        return calls

    return install


def _expire_cache(url, image_type="cover"):
    metadata = cache._read_cache_metadata(image_type, url)
    metadata["expire_at"] = time.time() - 10
    cache._write_cache_metadata(image_type, url, metadata)


def test_successful_fetch_is_cached_and_reused(fake_upstream):
    calls = fake_upstream((200, JPEG, "image/jpeg"))

    first = ResourceService.fetch_image_file(COVER_URL)
    second = ResourceService.fetch_image_file(COVER_URL)

    assert first.status_code == 200
    assert first.media_type == "image/jpeg"
    assert first.file_path is not None
    # 第二次必须命中缓存，不再打上游
    assert len(calls) == 1
    assert second.status_code == 200
    # ETag 基于内容摘要，同一份内容应保持稳定，才能让浏览器拿到 304
    assert first.etag == second.etag
    assert first.etag.startswith('"')


def test_etag_differs_for_different_content(fake_upstream):
    fake_upstream((200, JPEG, "image/jpeg"))
    jpeg_result = ResourceService.fetch_image_file(COVER_URL)

    other_url = "https://img.example.com/other.png"
    fake_upstream((200, PNG, "image/png"))
    png_result = ResourceService.fetch_image_file(other_url)

    assert jpeg_result.etag != png_result.etag


def test_stale_cache_serves_image_when_upstream_fails(fake_upstream):
    fake_upstream((200, JPEG, "image/jpeg"))
    ResourceService.fetch_image_file(COVER_URL)

    _expire_cache(COVER_URL)
    fake_upstream((502, None, None))

    result = ResourceService.fetch_image_file(COVER_URL)

    # 关键回归点：上游挂掉时不能返回 502，应继续用本地旧图
    assert result.status_code == 200
    assert result.file_path is not None


def test_stale_fallback_extends_expiry(fake_upstream):
    fake_upstream((200, JPEG, "image/jpeg"))
    ResourceService.fetch_image_file(COVER_URL)

    _expire_cache(COVER_URL)
    fake_upstream((502, None, None))
    ResourceService.fetch_image_file(COVER_URL)

    # 兜底后应延长有效期，避免每次请求都重试已知不可用的上游
    lookup = cache.get_cache_lookup("cover", COVER_URL)
    assert lookup.cache_status == "hit"
    assert lookup.status == "fresh"


def test_negative_cache_prevents_repeated_upstream_calls(fake_upstream):
    calls = fake_upstream((404, None, None))

    first = ResourceService.fetch_image_file(COVER_URL)
    second = ResourceService.fetch_image_file(COVER_URL)

    assert first.status_code == 404
    assert second.status_code == 404
    # 第二次应直接读负缓存
    assert len(calls) == 1


def test_negative_ttl_is_longer_for_not_found_than_transient():
    assert cache.get_negative_ttl_seconds(404) > cache.get_negative_ttl_seconds(502)


def test_html_challenge_page_is_not_cached_as_image(fake_upstream):
    fake_upstream((200, HTML, "image/jpeg"))

    result = ResourceService.fetch_image_file(COVER_URL)

    # 上游用 200 返回 HTML 风控页时必须按失败处理，否则坏内容会被长期缓存
    assert result.file_path is None
    assert result.status_code >= 400
    assert not cache.get_cache_data_path("cover", COVER_URL).exists()


def test_legacy_bad_cache_is_purged_then_refetched(fake_upstream):
    # 模拟历史遗留：缓存里存的是 HTML 而不是图片
    cache.write_success_cache("cover", COVER_URL, HTML, "image/jpeg")
    calls = fake_upstream((200, JPEG, "image/jpeg"))

    result = ResourceService.fetch_image_file(COVER_URL)

    assert result.status_code == 200
    assert result.file_path is not None
    assert len(calls) == 1
    assert ResourceService.fetch_image_bytes(COVER_URL) == JPEG


def test_private_and_invalid_urls_are_blocked(fake_upstream):
    calls = fake_upstream((200, JPEG, "image/jpeg"))

    assert ResourceService.fetch_image_file("http://127.0.0.1/x.jpg").status_code == 403
    assert ResourceService.fetch_image_file("http://192.168.1.5/x.jpg").status_code == 403
    assert ResourceService.fetch_image_file("file:///etc/passwd").status_code == 400
    # 被拦截的请求不应触达上游
    assert len(calls) == 0


def test_protocol_relative_url_is_normalized(fake_upstream):
    fake_upstream((200, JPEG, "image/jpeg"))

    result = ResourceService.fetch_image_file("//img.example.com/relative.jpg")

    assert result.status_code == 200
    assert result.file_path is not None


def test_fetch_image_bytes_returns_none_on_failure(fake_upstream):
    fake_upstream((502, None, None))

    assert ResourceService.fetch_image_bytes(COVER_URL) is None
    assert ResourceService.fetch_image_bytes(None) is None


def test_is_image_binary_recognises_common_formats():
    assert ResourceService.is_image_binary(JPEG)
    assert ResourceService.is_image_binary(PNG)
    assert ResourceService.is_image_binary(b"GIF89a" + b"x" * 10)
    assert ResourceService.is_image_binary(b"RIFF" + b"\x00" * 4 + b"WEBP" + b"x" * 10)
    assert not ResourceService.is_image_binary(HTML)
    assert not ResourceService.is_image_binary(b"")
    assert not ResourceService.is_image_binary(None)


def test_cleanup_expired_cache_removes_negative_but_keeps_stale_image(fake_upstream):
    # 一个成功缓存（随后置为过期）+ 一个负缓存
    fake_upstream((200, JPEG, "image/jpeg"))
    ResourceService.fetch_image_file(COVER_URL)
    _expire_cache(COVER_URL)

    missing_url = "https://img.example.com/missing.jpg"
    cache.write_negative_cache("cover", missing_url, 404, ttl=-1)

    cache.cleanup_expired_cache()

    # 过期但仍可用作兜底的图片数据必须保留
    assert cache.get_cache_data_path("cover", COVER_URL).exists()
    # 过期的负缓存应被清掉，让失效地址有机会重试
    assert cache.get_cache_lookup("cover", missing_url).cache_status == "miss"
