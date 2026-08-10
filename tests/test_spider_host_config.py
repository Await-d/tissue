"""站点镜像域名配置与缓存 key 容错测试

覆盖两类回归：
- parse_host_list：配置了域名就以配置为准，不再追加内置列表
  （否则用户填了可用镜像，仍会继续探测已失效的内置域名，白等首页）
- 缓存 helper 对空 key 的容错：刮削结果可能没有封面/头像地址，
  空 key 不能在 None.encode 上抛 AttributeError 中断调用方流程
"""

from app.utils import cache
from app.utils.spider.spider import parse_host_list

FALLBACK = ["https://www.javbus.com/", "https://www.javbus.one/"]


def test_empty_config_falls_back_to_builtin_list():
    assert parse_host_list(None, FALLBACK) == [
        "https://www.javbus.com",
        "https://www.javbus.one",
    ]
    assert parse_host_list("   ", FALLBACK) == [
        "https://www.javbus.com",
        "https://www.javbus.one",
    ]


def test_configured_hosts_replace_builtin_list():
    result = parse_host_list("javbus9.com, https://mirror.test/", FALLBACK)

    # 关键点：配置项是权威的，内置域名不再被追加到后面
    assert result == ["https://javbus9.com", "https://mirror.test"]
    assert "https://www.javbus.com" not in result


def test_scheme_is_added_and_trailing_slash_stripped():
    assert parse_host_list("example.com/", []) == ["https://example.com"]
    assert parse_host_list("http://plain.test", []) == ["http://plain.test"]


def test_newline_separated_hosts_are_supported():
    assert parse_host_list("a.com\nb.com", []) == [
        "https://a.com",
        "https://b.com",
    ]


def test_duplicates_are_removed_preserving_order():
    assert parse_host_list("b.com, a.com, b.com", []) == [
        "https://b.com",
        "https://a.com",
    ]


def test_blank_entries_are_ignored():
    assert parse_host_list("a.com, , ,b.com,", []) == [
        "https://a.com",
        "https://b.com",
    ]


def test_cache_helpers_tolerate_empty_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "cache_path", tmp_path / "cache")

    # 没有封面地址时这些调用会真实发生（video.cover / actor.thumb 可为 None）
    cache.clean_cache_file("cover", None)
    cache.clean_cache_file("cover", "")
    cache.cache_file("cover", None, b"data")

    assert cache.get_cache_file("cover", None) is None
    assert cache.get_cache_file("cover", "") is None
