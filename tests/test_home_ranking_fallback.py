"""首页榜单取数链路测试

覆盖首页"加载失败"的几个根因场景：
- 实时爬取抛异常时不能 500，必须继续走旧缓存兜底
- 返回兜底旧数据时通过响应头告知前端
- 同一榜单组合的按需刷新需要去重 + 冷却，避免抓取风暴
"""

import time

import pytest
from fastapi import Response

import app.api.home as home


@pytest.fixture(autouse=True)
def reset_throttle():
    """每个用例都从干净的节流状态开始。"""
    home._REFRESH_IN_FLIGHT.clear()
    home._REFRESH_LAST_ATTEMPT.clear()
    yield
    home._REFRESH_IN_FLIGHT.clear()
    home._REFRESH_LAST_ATTEMPT.clear()


class FakeCacheService:
    """可编排的 VideoCacheService 替身。"""

    def __init__(self, fresh=None, after_refresh=None, stale=None,
                 fresh_raises=False, refresh_raises=False, stale_raises=False):
        self._fresh = fresh or []
        self._after_refresh = after_refresh or []
        self._stale = stale or []
        self._fresh_raises = fresh_raises
        self._refresh_raises = refresh_raises
        self._stale_raises = stale_raises
        self.refresh_calls = 0
        self._ranking_calls = 0

    def get_ranking_videos(self, **kwargs):
        self._ranking_calls += 1
        if self._fresh_raises:
            raise RuntimeError("db down")
        # 第一次为刷新前，之后为刷新后
        return self._fresh if self._ranking_calls == 1 else self._after_refresh

    def fetch_and_cache_rankings(self, **kwargs):
        self.refresh_calls += 1
        if self._refresh_raises:
            raise RuntimeError("scrape failed")
        return {"total_fetched": len(self._after_refresh), "errors": []}

    def query_videos(self, **kwargs):
        if self._stale_raises:
            raise RuntimeError("stale read failed")
        return self._stale


def _video(num):
    return {"num": num, "title": f"title-{num}", "cover": f"https://x/{num}.jpg", "rank": 4.5}


def _call(monkeypatch, cache_service, spider_factory=None):
    monkeypatch.setattr(home, "VideoCacheService", lambda db: cache_service)
    if spider_factory is not None:
        monkeypatch.setattr(home.spider, "JavdbSpider", spider_factory)
    response = Response()
    data = home.get_rankings(
        source="JavDB", video_type="censored", cycle="daily",
        response=response, db=None,
    )
    return data, response


def test_fresh_cache_is_returned_without_scraping(monkeypatch):
    service = FakeCacheService(fresh=[_video("ABC-001")])

    data, response = _call(monkeypatch, service)

    assert len(data) == 1
    assert data[0]["num"] == "ABC-001"
    assert service.refresh_calls == 0
    assert response.headers["X-Data-Source"] == "cache"
    assert response.headers["X-Data-Stale"] == "false"


def test_on_demand_refresh_populates_cache(monkeypatch):
    service = FakeCacheService(fresh=[], after_refresh=[_video("ABC-002")])

    data, response = _call(monkeypatch, service)

    assert len(data) == 1
    assert service.refresh_calls == 1
    assert response.headers["X-Data-Source"] == "refresh"
    assert response.headers["X-Data-Stale"] == "false"


def test_live_scrape_exception_falls_back_to_stale_cache(monkeypatch):
    """核心回归点：实时爬取抛异常曾导致接口 500，直接跳过旧缓存兜底。"""

    class ExplodingSpider:
        def __init__(self):
            raise RuntimeError("javdb unreachable")

    service = FakeCacheService(
        fresh=[], after_refresh=[], stale=[_video("OLD-001")],
        refresh_raises=True,
    )

    data, response = _call(monkeypatch, service, spider_factory=ExplodingSpider)

    assert len(data) == 1
    assert data[0]["num"] == "OLD-001"
    assert response.headers["X-Data-Source"] == "stale-cache"
    assert response.headers["X-Data-Stale"] == "true"


def test_scrape_method_exception_falls_back_to_stale_cache(monkeypatch):
    """爬虫构造成功但抓取方法抛异常时，同样要走兜底。"""

    class FailingSpider:
        def get_ranking_with_details(self, *a, **k):
            raise RuntimeError("parse error")

        def get_ranking(self, *a, **k):
            raise RuntimeError("parse error")

    service = FakeCacheService(fresh=[], after_refresh=[], stale=[_video("OLD-002")])

    data, response = _call(monkeypatch, service, spider_factory=FailingSpider)

    assert data[0]["num"] == "OLD-002"
    assert response.headers["X-Data-Stale"] == "true"


def test_live_scrape_success_is_returned(monkeypatch):
    class WorkingSpider:
        def get_ranking_with_details(self, *a, **k):
            return [_video("LIVE-001")]

    service = FakeCacheService(fresh=[], after_refresh=[], refresh_raises=True)

    data, response = _call(monkeypatch, service, spider_factory=WorkingSpider)

    assert data[0]["num"] == "LIVE-001"
    assert response.headers["X-Data-Source"] == "live"
    assert response.headers["X-Data-Stale"] == "false"


def test_cache_read_exception_does_not_break_endpoint(monkeypatch):
    """缓存查询本身抛异常也不能让接口 500。"""

    class WorkingSpider:
        def get_ranking_with_details(self, *a, **k):
            return [_video("LIVE-002")]

    service = FakeCacheService(fresh_raises=True)

    data, response = _call(monkeypatch, service, spider_factory=WorkingSpider)

    assert data[0]["num"] == "LIVE-002"


def test_all_sources_failing_returns_empty_list_not_error(monkeypatch):
    class ExplodingSpider:
        def __init__(self):
            raise RuntimeError("down")

    service = FakeCacheService(
        fresh=[], after_refresh=[], stale=[],
        refresh_raises=True, stale_raises=True,
    )

    data, response = _call(monkeypatch, service, spider_factory=ExplodingSpider)

    assert data == []
    assert response.headers["X-Data-Source"] == "empty"
    assert response.headers["X-Data-Stale"] == "true"


def test_refresh_slot_dedupes_concurrent_requests():
    key = ("JavDB", "censored", "daily")

    assert home._try_acquire_refresh_slot(key) is True
    # 同一组合已有刷新在跑
    assert home._try_acquire_refresh_slot(key) is False

    home._release_refresh_slot(key)
    # 释放后仍在冷却期
    assert home._try_acquire_refresh_slot(key) is False


def test_refresh_slot_allows_retry_after_cooldown():
    key = ("JavDB", "uncensored", "weekly")

    assert home._try_acquire_refresh_slot(key) is True
    home._release_refresh_slot(key)

    # 模拟冷却期结束
    home._REFRESH_LAST_ATTEMPT[key] = time.time() - home._REFRESH_COOLDOWN_SECONDS - 1
    assert home._try_acquire_refresh_slot(key) is True


def test_refresh_slots_are_independent_per_combination():
    daily = ("JavDB", "censored", "daily")
    weekly = ("JavDB", "censored", "weekly")

    assert home._try_acquire_refresh_slot(daily) is True
    # 不同榜单组合互不阻塞
    assert home._try_acquire_refresh_slot(weekly) is True


def test_throttled_request_still_falls_through_to_stale_cache(monkeypatch):
    """刷新被节流拦下时，仍要能返回旧数据而不是空页面。"""
    key = ("JavDB", "censored", "daily")
    home._try_acquire_refresh_slot(key)  # 占住刷新槽

    class ExplodingSpider:
        def __init__(self):
            raise RuntimeError("down")

    service = FakeCacheService(fresh=[], stale=[_video("OLD-003")])

    data, response = _call(monkeypatch, service, spider_factory=ExplodingSpider)

    assert service.refresh_calls == 0  # 被节流，没有触发抓取
    assert data[0]["num"] == "OLD-003"
    assert response.headers["X-Data-Stale"] == "true"


def test_source_alias_is_normalized(monkeypatch):
    service = FakeCacheService(fresh=[_video("ABC-003")])
    monkeypatch.setattr(home, "VideoCacheService", lambda db: service)

    response = Response()
    data = home.get_rankings(
        source="javdb", video_type="censored", cycle="daily",
        response=response, db=None,
    )

    assert len(data) == 1


def test_normalize_ranking_fields_fills_aliases():
    normalized = home._normalize_ranking_fields([
        {"num": "A-1", "rating": 4.2, "comments_count": 30, "release_date": "2026-01-01", "isZh": True},
    ])

    item = normalized[0]
    assert item["rank"] == 4.2
    assert item["rank_count"] == 30
    assert item["publish_date"] == "2026-01-01"
    assert item["is_zh"] is True
