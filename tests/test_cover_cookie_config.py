"""封面抓取的 Cookie 配置测试

fetch_cover 是 classmethod，直接走 curl_cffi，不经过 Spider 实例的 session。
而用户在设置里填的站点 Cookie（如过 Cloudflare 质询后拿到的 cf_clearance）
原先只被 _apply_login_cookie 应用到实例级 session，于是出现：
页面能抓到、封面仍然 403，表现为"有数据没有图"。

本文件锁定这条链路：配置里的 Cookie 必须真正到达出站的图片请求。
"""

import pytest

from app.utils.spider import spider as spider_mod
from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.javdb import JavdbSpider


class FakeAppSetting:
    """最小设置替身，避免测试触碰真实配置库。"""

    def __init__(self, javdb_cookie=None):
        self.user_agent = "TestUA/1.0"
        self.proxy = None
        self.cover_fetch_retries = 1
        self.javdb_cookie = javdb_cookie


@pytest.fixture
def fake_setting(monkeypatch):
    setting = FakeAppSetting()
    monkeypatch.setattr(spider_mod, "_get_app_setting", lambda: setting)
    return setting


class FakeImageResponse:
    status_code = 200
    content = b"\xff\xd8\xff" + b"x" * 50
    headers = {"content-type": "image/jpeg"}
    ok = True


@pytest.fixture
def captured_request(monkeypatch):
    """捕获传给 HTTP 层的 kwargs，用于断言 Cookie 真的发出去了。"""
    captured = {}

    def fake_get(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeImageResponse()

    monkeypatch.setattr(spider_mod.cffi_requests, "get", fake_get)
    return captured


def test_builtin_cookies_used_when_nothing_configured(fake_setting):
    assert JavdbSpider._cover_cookie_jar() == {"over18": "1", "locale": "zh"}
    assert JavbusSpider._cover_cookie_jar() == {"age": "verified", "existmag": "all"}


def test_configured_cookie_is_merged_with_builtin(fake_setting):
    fake_setting.javdb_cookie = "cf_clearance=ABCDEF123456; _jdb_session=xyz789"

    jar = JavdbSpider._cover_cookie_jar()

    # 关键回归点：cf_clearance 必须进入图片请求的 Cookie
    assert jar["cf_clearance"] == "ABCDEF123456"
    assert jar["_jdb_session"] == "xyz789"
    # 内置 Cookie 不能被挤掉
    assert jar["over18"] == "1"
    assert jar["locale"] == "zh"


def test_configured_value_overrides_builtin(fake_setting):
    fake_setting.javdb_cookie = "over18=0"

    # 用户配置优先：凭据类 Cookie 必须能覆盖内置默认值
    assert JavdbSpider._cover_cookie_jar()["over18"] == "0"


def test_cookie_does_not_leak_across_sites(fake_setting):
    fake_setting.javdb_cookie = "cf_clearance=SHOULD_NOT_LEAK"

    jar = JavbusSpider._cover_cookie_jar()

    # JavBus 没有配置 cookie_setting_key，不能拿到 JavDB 的凭据
    assert "cf_clearance" not in jar
    assert jar == {"age": "verified", "existmag": "all"}


def test_spider_without_cookie_setting_key_returns_empty(fake_setting):
    assert spider_mod.Spider.cookie_setting_key is None
    assert spider_mod.Spider._configured_cookies() == {}


@pytest.mark.parametrize(
    "raw",
    [None, "", "   ", "novalue", ";;;", "=noname"],
)
def test_malformed_cookie_input_is_tolerated(fake_setting, raw):
    fake_setting.javdb_cookie = raw

    # 畸形输入不能抛异常，也不能污染内置 Cookie
    assert JavdbSpider._cover_cookie_jar() == {"over18": "1", "locale": "zh"}


def test_partially_malformed_input_keeps_valid_pairs(fake_setting):
    fake_setting.javdb_cookie = "=noname; good=1; alsobad; other=2"

    jar = JavdbSpider._cover_cookie_jar()

    assert jar["good"] == "1"
    assert jar["other"] == "2"
    assert "" not in jar


def test_whitespace_around_pairs_is_stripped(fake_setting):
    fake_setting.javdb_cookie = "  cf_clearance = TOKEN123  ;  a=b  "

    jar = JavdbSpider._cover_cookie_jar()

    assert jar["cf_clearance"] == "TOKEN123"
    assert jar["a"] == "b"


def test_cookie_value_containing_equals_is_preserved(fake_setting):
    # base64 风格的值常带 '='，不能被截断
    fake_setting.javdb_cookie = "token=abc==def"

    assert JavdbSpider._cover_cookie_jar()["token"] == "abc==def"


def test_configured_cookie_reaches_outbound_request(fake_setting, captured_request):
    fake_setting.javdb_cookie = "cf_clearance=REALTOKEN"

    status, content, content_type = JavdbSpider.fetch_cover(
        "https://c0.jdbstatic.com/covers/a.jpg"
    )

    assert status == 200
    assert content_type == "image/jpeg"
    assert content

    sent_cookies = captured_request.get("cookies") or {}
    # 这是本次修复的核心断言：配置的凭据真的出现在出站请求上
    assert sent_cookies.get("cf_clearance") == "REALTOKEN"
    assert sent_cookies.get("over18") == "1"


def test_referer_is_still_sent_with_cover_request(fake_setting, captured_request):
    JavdbSpider.fetch_cover("https://c0.jdbstatic.com/covers/a.jpg")

    headers = captured_request.get("headers") or {}
    # 图床靠 Referer 做防盗链，不能因为加 Cookie 而丢掉
    assert headers.get("Referer") == JavdbSpider.host
    assert headers.get("User-Agent") == "TestUA/1.0"


def test_javdb_declares_its_cookie_setting_key():
    # 设置项改名时这条会失败，避免配置静默失效
    assert JavdbSpider.cookie_setting_key == "javdb_cookie"


def test_cookie_setting_key_matches_an_actual_setting_field():
    from app.schema.setting import SettingApp

    assert JavdbSpider.cookie_setting_key in SettingApp.model_fields
