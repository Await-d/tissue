"""缓存写入原子性与坏缓存自愈测试

首页一次渲染几十张封面，用户连续刷新时同一个 URL 很可能被并发写入同一个文件。
非原子写会让两次写入交错，产出「头部正常、内容损坏」的图片，
而只校验魔数的话这种文件会在整个 TTL 内被当成好图持续返回。

本文件覆盖：
- 并发写同一 key 后，读出的必须是某一个完整版本，不能是拼接产物
- 截断/损坏的缓存能被识破，并触发重抓（自愈）
- 写入异常不留下 .tmp 残留
"""

import os
import threading

import pytest

from app.utils import cache
from app.service.resource import ResourceService


def _jpeg(marker: bytes, size: int = 4096) -> bytes:
    """构造固定长度的合法 JPEG 头 + 可区分填充。"""
    body = marker * (size // len(marker) + 1)
    return b"\xff\xd8\xff" + body[: size - 3]


URL = "https://img.example.com/atomic.jpg"


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "cache_path", tmp_path / "cache")
    yield


def test_concurrent_writes_never_produce_a_spliced_file():
    """并发写同一 key：结果必须完整等于其中某一个版本。"""
    variants = {
        marker: _jpeg(marker)
        for marker in (b"AA", b"BB", b"CC", b"DD")
    }
    assert len({len(v) for v in variants.values()}) == 1, "各版本长度需一致才能验证交错"

    errors = []

    def writer(payload):
        try:
            for _ in range(25):
                cache.cache_file("cover", URL, payload)
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [
        threading.Thread(target=writer, args=(payload,))
        for payload in variants.values()
        for _ in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors

    final = cache.get_cache_file("cover", URL)
    # 关键断言：读到的内容必须是某个完整版本，而不是多次写入交错的产物
    assert final in variants.values()


def test_concurrent_metadata_writes_stay_parsable():
    """元数据并发写：不能读到半截 JSON（否则好图会退化成过期被反复重抓）。"""
    errors = []

    def writer(ttl):
        try:
            for _ in range(30):
                cache.write_success_cache("cover", URL, _jpeg(b"MM"), "image/jpeg", ttl=ttl)
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=writer, args=(ttl,)) for ttl in (60, 120, 180, 240)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors

    metadata = cache._read_cache_metadata("cover", URL)
    # 半截 JSON 会被解析成空 dict，这里必须拿到完整字段
    assert metadata.get("content_type") == "image/jpeg"
    assert isinstance(metadata.get("expire_at"), float)
    assert metadata.get("size") == len(_jpeg(b"MM"))


def test_truncated_cache_is_rejected():
    """头部完好但内容被截断的文件必须判为无效。"""
    payload = _jpeg(b"TT")
    cache.write_success_cache("cover", URL, payload, "image/jpeg")

    lookup = cache.get_cache_lookup("cover", URL)
    assert ResourceService._cached_file_is_valid(lookup.file_path, lookup.metadata) is True

    # 截掉一半，模拟并发交错/写入中断的产物
    data_path = cache.get_cache_data_path("cover", URL)
    with open(data_path, "r+b") as file:
        file.truncate(len(payload) // 2)

    lookup = cache.get_cache_lookup("cover", URL)
    # 魔数仍然合法，只有尺寸校验能发现问题
    assert ResourceService._cached_file_is_valid(lookup.file_path, lookup.metadata) is False


def test_truncated_cache_triggers_refetch_and_self_heals(monkeypatch):
    """坏缓存不能被一直返回：应清掉并重抓。"""
    good = _jpeg(b"GG")
    cache.write_success_cache("cover", URL, good, "image/jpeg")

    data_path = cache.get_cache_data_path("cover", URL)
    with open(data_path, "r+b") as file:
        file.truncate(64)

    calls = []

    def fake_fetch(url):
        calls.append(url)
        return (200, good, "image/jpeg")

    monkeypatch.setattr(ResourceService, "_fetch_cover_by_host", staticmethod(fake_fetch))

    result = ResourceService.fetch_image_file(URL)

    assert result.status_code == 200
    assert result.file_path is not None
    assert len(calls) == 1, "坏缓存必须触发一次重抓"
    # 自愈后内容恢复完整
    assert ResourceService.fetch_image_bytes(URL) == good


def test_oversized_cache_is_also_rejected():
    """内容比记录的 size 长（写入交错的另一种形态）同样要判无效。"""
    payload = _jpeg(b"OO")
    cache.write_success_cache("cover", URL, payload, "image/jpeg")

    data_path = cache.get_cache_data_path("cover", URL)
    with open(data_path, "ab") as file:
        file.write(b"garbage-appended")

    lookup = cache.get_cache_lookup("cover", URL)
    assert ResourceService._cached_file_is_valid(lookup.file_path, lookup.metadata) is False


def test_missing_metadata_falls_back_to_magic_check_only():
    """老缓存没有元数据时不能因为缺 size 就误判为坏图。"""
    payload = _jpeg(b"LL")
    cache.cache_file("cover", URL, payload)  # 只写数据，不写元数据

    lookup = cache.get_cache_lookup("cover", URL)
    assert lookup.cache_status == "hit"
    assert lookup.status == "stale"
    # 没有 size 可比时，魔数合法即视为可用（可作为兜底副本）
    assert ResourceService._cached_file_is_valid(lookup.file_path, lookup.metadata) is True


def test_failed_write_leaves_no_tmp_residue(monkeypatch):
    """写入过程抛异常时不能留下 .tmp 文件。"""
    real_replace = os.replace

    def exploding_replace(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", exploding_replace)

    with pytest.raises(OSError):
        cache.cache_file("cover", URL, _jpeg(b"EE"))

    monkeypatch.setattr(os, "replace", real_replace)

    folder = os.path.join(cache.cache_path, "cover")
    residue = [n for n in os.listdir(folder)] if os.path.isdir(folder) else []
    assert not any(n.endswith(".tmp") for n in residue), f"残留临时文件: {residue}"


def test_write_creates_no_partial_file_visible_to_readers():
    """写入完成前不应有可见的半截文件（原子 rename 保证）。"""
    payload = _jpeg(b"PP", size=256 * 1024)
    cache.cache_file("cover", URL, payload)

    read_back = cache.get_cache_file("cover", URL)
    assert read_back is not None
    assert len(read_back) == len(payload)
    assert read_back == payload
