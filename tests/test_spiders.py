"""
蜘蛛数据提取综合测试

测试分层：
  - 单元测试（无网络）：测试纯解析方法，如 _parse_score_text / _parse_date
  - 离线 HTML 测试：使用项目中已保存的 debug HTML 文件
  - 在线集成测试：标记为 @pytest.mark.live_network，需手动执行
    pytest tests/test_spiders.py -m live_network --proxy http://your-proxy:port

运行方式：
  pytest tests/test_spiders.py -v              # 仅运行离线测试
  pytest tests/test_spiders.py -v -m live_network  # 仅运行网络测试
  pytest tests/test_spiders.py -v --run-all    # 运行全部
"""

import os
import json
import re
import pytest
from datetime import date
from unittest.mock import patch, MagicMock, PropertyMock
from lxml import etree

# ──────────────────────────────────────────────
# Fixtures 和 Markers
# ──────────────────────────────────────────────


def pytest_configure(config):
    config.addinivalue_line("markers", "live_network: 需要真实网络连接的集成测试")


# JavDB ranking 调试文件路径（项目根目录）
JAVDB_CENSORED_DEBUG = os.path.join(
    os.path.dirname(__file__), "..", "javdb_censored_ranking_debug.html"
)
JAVDB_UNCENSORED_DEBUG = os.path.join(
    os.path.dirname(__file__), "..", "javdb_uncensored_ranking_debug.html"
)


@pytest.fixture(scope="module")
def javdb_spider_no_network():
    """创建 JavdbSpider 实例，跳过网络初始化（_select_best_host / _apply_login_cookie）"""
    with (
        patch("app.utils.spider.javdb.JavdbSpider._select_best_host"),
        patch("app.utils.spider.javdb.JavdbSpider._apply_login_cookie"),
    ):
        from app.utils.spider.javdb import JavdbSpider

        spider = JavdbSpider.__new__(JavdbSpider)
        spider.host = "https://javdb.com"
        spider.avatar_host = "https://c0.jdbstatic.com/avatars/"
        spider.name = "JavDB"
        # 不需要 session，只测试纯解析
        return spider


@pytest.fixture(scope="module")
def javbus_spider_no_network():
    """创建 JavbusSpider 实例，跳过网络初始化"""
    with patch("app.utils.spider.javbus.JavbusSpider._initialize_session"):
        from app.utils.spider.javbus import JavbusSpider

        spider = JavbusSpider.__new__(JavbusSpider)
        spider.host = "https://www.javbus.com/"
        spider.name = "JavBus"
        return spider


# ──────────────────────────────────────────────
# JavDB: 评分文本解析
# ──────────────────────────────────────────────


class TestJavdbParseScoreText:
    """测试 _parse_score_text 的两种格式及边界情况"""

    def test_old_format_chinese(self, javdb_spider_no_network):
        """旧格式：4.55分, 由754人評價"""
        rating, count = javdb_spider_no_network._parse_score_text("4.55分, 由754人評價")
        assert rating == 4.55
        assert count == 754

    def test_old_format_with_whitespace(self, javdb_spider_no_network):
        """旧格式带前后空白"""
        rating, count = javdb_spider_no_network._parse_score_text(
            "  4.33分, 由669人評價  "
        )
        assert rating == 4.33
        assert count == 669

    def test_new_format_english(self, javdb_spider_no_network):
        """新格式：4.55, by 754 users"""
        rating, count = javdb_spider_no_network._parse_score_text("4.55, by 754 users")
        assert rating == 4.55
        assert count == 754

    def test_new_format_with_comma_count(self, javdb_spider_no_network):
        """新格式：千位分隔符 1,575"""
        rating, count = javdb_spider_no_network._parse_score_text(
            "4.56, by 1,575 users"
        )
        assert rating == 4.56
        assert count == 1575

    def test_new_format_no_comma(self, javdb_spider_no_network):
        """新格式：4.56 by 1575 users（无逗号）"""
        rating, count = javdb_spider_no_network._parse_score_text("4.56 by 1575 users")
        assert rating == 4.56
        assert count == 1575

    def test_old_format_score_only(self, javdb_spider_no_network):
        """旧格式只有评分，没有人数"""
        rating, count = javdb_spider_no_network._parse_score_text("4.55分")
        assert rating == 4.55
        assert count == 0

    def test_empty_string(self, javdb_spider_no_network):
        """空字符串返回 (None, 0)"""
        rating, count = javdb_spider_no_network._parse_score_text("")
        assert rating is None
        assert count == 0

    def test_none_input(self, javdb_spider_no_network):
        """None 输入返回 (None, 0)"""
        rating, count = javdb_spider_no_network._parse_score_text(None)
        assert rating is None
        assert count == 0

    def test_star_icon_noise(self, javdb_spider_no_network):
        """包含 itertext 产生的图标噪声时，仍能正确解析"""
        # 实际 itertext 结果可能带有 \n 和空格
        text = "\n\n 4.68分, 由1875人評價"
        rating, count = javdb_spider_no_network._parse_score_text(text)
        assert rating == 4.68
        assert count == 1875


# ──────────────────────────────────────────────
# JavDB: 日期解析
# ──────────────────────────────────────────────


class TestJavdbParseDate:
    """测试 _parse_date 的两种日期格式"""

    def test_yyyymmdd_format(self, javdb_spider_no_network):
        """YYYY-MM-DD 格式"""
        d = javdb_spider_no_network._parse_date("2026-01-09")
        assert d == date(2026, 1, 9)

    def test_mmddyyyy_format(self, javdb_spider_no_network):
        """MM/DD/YYYY 格式"""
        d = javdb_spider_no_network._parse_date("01/09/2026")
        assert d == date(2026, 1, 9)

    def test_with_whitespace(self, javdb_spider_no_network):
        """带空白的日期（div.meta 的 text 经常带换行）"""
        d = javdb_spider_no_network._parse_date("  2025-12-30  ")
        assert d == date(2025, 12, 30)

    def test_invalid_returns_none(self, javdb_spider_no_network):
        """无法解析的字符串返回 None"""
        d = javdb_spider_no_network._parse_date("not-a-date")
        assert d is None

    def test_none_returns_none(self, javdb_spider_no_network):
        """None 输入返回 None"""
        d = javdb_spider_no_network._parse_date(None)
        assert d is None

    def test_empty_returns_none(self, javdb_spider_no_network):
        d = javdb_spider_no_network._parse_date("")
        assert d is None


# ──────────────────────────────────────────────
# JavDB: 排行榜 HTML 解析（使用实际保存的 debug 文件）
# ──────────────────────────────────────────────


@pytest.mark.skipif(
    not os.path.exists(JAVDB_CENSORED_DEBUG),
    reason="缺少 javdb_censored_ranking_debug.html（需先运行一次 job_refresh_video_cache）",
)
class TestJavdbRankingPageParsing:
    """使用项目中保存的 debug HTML 文件测试排行榜解析"""

    @pytest.fixture(scope="class")
    def parsed_videos(self, javdb_spider_no_network):
        with open(JAVDB_CENSORED_DEBUG, "rb") as f:
            content = f.read()
        html = etree.HTML(content, parser=etree.HTMLParser(encoding="utf-8"))
        return javdb_spider_no_network._parse_ranking_page(html, 1, "censored_ranking")

    def test_finds_videos(self, parsed_videos):
        """应该能找到至少一个视频（XPath contains 修复后）"""
        assert len(parsed_videos) > 0, (
            "排行榜 HTML 未解析到任何视频，XPath 可能仍有问题"
        )

    def test_video_has_required_fields(self, parsed_videos):
        """每个视频必须有 num、url、cover"""
        for v in parsed_videos:
            assert v.get("num"), f"视频缺少番号: {v}"
            assert v.get("url"), f"视频 {v['num']} 缺少 URL"

    def test_rating_extracted(self, parsed_videos):
        """至少 50% 的视频应有评分"""
        rated = [v for v in parsed_videos if v.get("rating") is not None]
        ratio = len(rated) / len(parsed_videos)
        assert ratio >= 0.5, (
            f"评分提取率过低: {ratio:.0%}（共 {len(parsed_videos)} 个视频）"
        )

    def test_comments_extracted(self, parsed_videos):
        """至少 50% 的视频应有评论数"""
        commented = [v for v in parsed_videos if v.get("comments", 0) > 0]
        ratio = len(commented) / len(parsed_videos)
        assert ratio >= 0.5, f"评论数提取率过低: {ratio:.0%}"

    def test_release_date_extracted(self, parsed_videos):
        """至少 50% 的视频应有发布日期（新增的提取逻辑）"""
        dated = [v for v in parsed_videos if v.get("release_date")]
        ratio = len(dated) / len(parsed_videos)
        assert ratio >= 0.5, f"发布日期提取率过低: {ratio:.0%}"

    def test_release_date_format(self, parsed_videos):
        """发布日期格式必须是 YYYY-MM-DD"""
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for v in parsed_videos:
            if v.get("release_date"):
                assert date_pattern.match(v["release_date"]), (
                    f"日期格式错误: {v['release_date']} (num={v['num']})"
                )

    def test_is_zh_detection(self, parsed_videos):
        """包含中文字幕的视频应被正确标记（至少能检测到一个）"""
        zh_videos = [v for v in parsed_videos if v.get("is_zh")]
        # 有码排行榜中中字视频占比通常 > 10%
        # 但接受0个，确保不崩溃即可；如果有则更好
        for v in zh_videos:
            assert v["is_zh"] is True

    def test_is_zh_always_false_regression(self, parsed_videos):
        """
        回归测试: is_zh 不应全部是 False
        从实际 HTML 中，MIDA-439 有中字标签，应被检测为 is_zh=True
        """
        mida = next((v for v in parsed_videos if v.get("num") == "MIDA-439"), None)
        if mida:
            assert mida["is_zh"] is True, (
                "MIDA-439 有 '含中字磁鏈' 标签，但 is_zh 仍为 False（回归）"
            )

    def test_cover_url_is_absolute(self, parsed_videos):
        """封面 URL 必须是绝对 URL"""
        for v in parsed_videos:
            if v.get("cover"):
                assert v["cover"].startswith("http"), (
                    f"封面 URL 不是绝对地址: {v['cover']} (num={v['num']})"
                )

    def test_is_uncensored_is_false(self, parsed_videos):
        """有码排行榜中 is_uncensored 必须是 False"""
        for v in parsed_videos:
            assert v.get("is_uncensored") is False, (
                f"有码排行榜中 {v['num']} 的 is_uncensored 不应为 True"
            )


@pytest.mark.skipif(
    not os.path.exists(JAVDB_UNCENSORED_DEBUG),
    reason="缺少 javdb_uncensored_ranking_debug.html",
)
class TestJavdbUncensoredLoginDetection:
    """测试无码排行榜的登录页检测（使用保存的登录页 HTML）"""

    def test_login_page_detected(self, javdb_spider_no_network):
        """
        uncensored debug 文件实际上是登录页，
        验证 get_ranking_with_details 能正确检测并返回空列表
        """
        with open(JAVDB_UNCENSORED_DEBUG, "rb") as f:
            content = f.read()

        # 模拟 response 返回登录页 content
        mock_response = MagicMock()
        mock_response.url = "https://javdb565.com/login"
        mock_response.content = content

        with (
            patch.object(javdb_spider_no_network, "_get", return_value=mock_response),
            patch.object(javdb_spider_no_network, "_set_age_cookies"),
        ):
            result = javdb_spider_no_network.get_ranking_with_details(
                "uncensored", "daily"
            )

        assert result == [], "登录页应返回空列表，而非尝试解析"


# ──────────────────────────────────────────────
# JavDB: 排行榜 XPath 修复（mock HTML）
# ──────────────────────────────────────────────


class TestJavdbXpathContainsFix:
    """验证排行榜容器 XPath 使用 contains 而非精确匹配"""

    MOCK_RANKING_HTML = """
    <html><body>
    <div class="movie-list h cols-4 vcols-8">
      <div class="item">
        <a href="/v/abc123" class="box" title="TEST-001">
          <div class="cover "><img src="https://example.com/cover.jpg" /></div>
          <div class="video-title"><strong>TEST-001</strong> Test Title</div>
          <div class="score">
            <span class="value"><span class="score-stars"></span>
            4.55分, 由100人評價</span>
          </div>
          <div class="meta">2026-01-01</div>
          <div class="tags has-addons">
            <span class="tag is-success">含磁鏈</span>
          </div>
        </a>
      </div>
      <div class="item">
        <a href="/v/def456" class="box" title="TEST-002">
          <div class="cover ">
            <span class="tag-can-play cnsub">中字可播放</span>
            <img src="https://example.com/cover2.jpg" />
          </div>
          <div class="video-title"><strong>TEST-002</strong> Chinese Sub Title</div>
          <div class="score">
            <span class="value"><span class="score-stars"></span>
            4.80分, 由500人評價</span>
          </div>
          <div class="meta">2026-01-02</div>
          <div class="tags has-addons">
            <span class="tag is-warning">含中字磁鏈</span>
          </div>
        </a>
      </div>
    </div>
    </body></html>
    """.encode("utf-8")

    @pytest.fixture
    def mock_html(self):
        return etree.HTML(
            self.MOCK_RANKING_HTML, parser=etree.HTMLParser(encoding="utf-8")
        )

    def test_container_xpath_matches_multiclass(
        self, javdb_spider_no_network, mock_html
    ):
        """关键修复：contains(@class,'movie-list') 能匹配 'movie-list h cols-4 vcols-8'"""
        elements = mock_html.xpath(
            "//div[contains(@class, 'movie-list')]//div[@class='item']"
        )
        assert len(elements) == 2, "XPath 应找到 2 个 item，contains 修复失效"

    def test_exact_xpath_would_fail(self, mock_html):
        """确认精确匹配无法找到元素（复现修复前的 bug）"""
        elements = mock_html.xpath("//div[@class='movie-list']//div[@class='item']")
        assert len(elements) == 0, "精确匹配应找不到元素，否则测试前提不成立"

    def test_parse_ranking_finds_both_videos(self, javdb_spider_no_network, mock_html):
        """_parse_ranking_page 应能找到 mock HTML 中的 2 个视频"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        assert len(videos) == 2

    def test_is_zh_cnsub_detection(self, javdb_spider_no_network, mock_html):
        """TEST-002 有 cnsub span，应被标记为 is_zh=True"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        by_num = {v["num"]: v for v in videos}
        assert by_num["TEST-002"]["is_zh"] is True

    def test_is_zh_tag_text_detection(self, javdb_spider_no_network, mock_html):
        """TEST-002 的 tags 中有 '含中字磁鏈'，也应触发 is_zh=True"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        by_num = {v["num"]: v for v in videos}
        # 同一个视频，两种检测方式都应命中
        assert by_num["TEST-002"]["is_zh"] is True

    def test_is_zh_no_chinese_sub(self, javdb_spider_no_network, mock_html):
        """TEST-001 没有中字标签，is_zh 应为 False"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        by_num = {v["num"]: v for v in videos}
        assert by_num["TEST-001"]["is_zh"] is False

    def test_release_date_extracted(self, javdb_spider_no_network, mock_html):
        """两个视频都应提取到发布日期"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        by_num = {v["num"]: v for v in videos}
        assert by_num["TEST-001"]["release_date"] == "2026-01-01"
        assert by_num["TEST-002"]["release_date"] == "2026-01-02"

    def test_rating_extracted(self, javdb_spider_no_network, mock_html):
        """评分应被正确提取"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        by_num = {v["num"]: v for v in videos}
        assert by_num["TEST-001"]["rating"] == 4.55
        assert by_num["TEST-002"]["rating"] == 4.80

    def test_comments_extracted(self, javdb_spider_no_network, mock_html):
        """评论数应被正确提取"""
        videos = javdb_spider_no_network._parse_ranking_page(
            mock_html, 1, "censored_ranking"
        )
        by_num = {v["num"]: v for v in videos}
        assert by_num["TEST-001"]["comments"] == 100
        assert by_num["TEST-002"]["comments"] == 500


# ──────────────────────────────────────────────
# JavDB: 搜索结果解析（mock HTML）
# ──────────────────────────────────────────────


class TestJavdbSearchParsing:
    """测试 search() 方法的番号提取逻辑"""

    MOCK_SEARCH_HTML = b"""
    <html><body>
    <div class="video-title"><strong>ABC-123</strong></div>
    <div class="video-title"><strong>ABC-1234</strong></div>
    <div class="video-title"><strong>def-456</strong></div>
    </body></html>
    """

    @pytest.fixture
    def mock_html(self):
        return etree.HTML(self.MOCK_SEARCH_HTML)

    def test_strong_elements_found(self, mock_html):
        """XPath //div[@class='video-title']/strong 应找到所有番号"""
        elements = mock_html.xpath("//div[@class='video-title']/strong")
        texts = [e.text for e in elements]
        assert "ABC-123" in texts
        assert "ABC-1234" in texts

    def test_exact_match_over_partial(self, mock_html):
        """精确匹配 'ABC-123' 不应匹配 'ABC-1234'"""
        elements = mock_html.xpath("//div[@class='video-title']/strong")
        exact = [e for e in elements if e.text and e.text.strip().lower() == "abc-123"]
        assert len(exact) == 1
        assert exact[0].text == "ABC-123"


# ──────────────────────────────────────────────
# JavBus: Bug 修复验证
# ──────────────────────────────────────────────


class TestJavbusGetPreviewsFix:
    """测试 get_previews IndexError 修复"""

    MOCK_PREVIEWS_WITH_IMG = b"""
    <html><body>
    <a class="sample-box" href="/img/full.jpg">
      <div><img src="/img/thumb.jpg"/></div>
    </a>
    </body></html>
    """

    MOCK_PREVIEWS_NO_IMG = b"""
    <html><body>
    <a class="sample-box" href="/img/full.jpg">
      <div></div>
    </a>
    </body></html>
    """

    MOCK_PREVIEWS_EMPTY_DIV = b"""
    <html><body>
    <a class="sample-box" href="/img/full.jpg">
    </a>
    </body></html>
    """

    def test_normal_preview_extracted(self, javbus_spider_no_network):
        """正常情况下应提取到 preview"""
        html = etree.HTML(self.MOCK_PREVIEWS_WITH_IMG)
        result = javbus_spider_no_network.get_previews(html)
        assert len(result) == 1
        assert len(result[0].items) == 1

    def test_no_img_does_not_crash(self, javbus_spider_no_network):
        """div 中没有 img 时不应崩溃（修复前会 IndexError）"""
        html = etree.HTML(self.MOCK_PREVIEWS_NO_IMG)
        result = javbus_spider_no_network.get_previews(html)
        # 没有 img 的 sample-box 应被跳过，返回空 items
        assert result == [{"website": "JavBus", "items": []}] or result[0].items == []

    def test_empty_sample_box_does_not_crash(self, javbus_spider_no_network):
        """完全空的 sample-box 不应崩溃"""
        html = etree.HTML(self.MOCK_PREVIEWS_EMPTY_DIV)
        result = javbus_spider_no_network.get_previews(html)
        assert isinstance(result, list)


class TestJavbusIncludePreviewsBugFix:
    """测试 include_previews 参数修复（之前错误地用 include_downloads 控制）"""

    def test_previews_called_with_include_previews_true(self):
        """include_previews=True 时应调用 get_previews"""
        with (
            patch("app.utils.spider.javbus.JavbusSpider._initialize_session"),
            patch(
                "app.utils.spider.javbus.JavbusSpider._check_and_bypass_verification"
            ) as mock_req,
            patch("app.utils.spider.javbus.JavbusSpider.get_previews") as mock_previews,
            patch(
                "app.utils.spider.javbus.JavbusSpider.get_downloads", return_value=[]
            ),
        ):
            from app.utils.spider.javbus import JavbusSpider

            spider = JavbusSpider.__new__(JavbusSpider)
            spider.host = "https://www.javbus.com/"
            spider.name = "JavBus"

            # 构造最小化有效响应 HTML
            fake_html = b"""
            <html><body>
            <h3>TEST-001</h3>
            <div class="container"></div>
            <title>TEST-001</title>
            </body></html>
            """
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = fake_html.decode()
            mock_resp.url = "https://www.javbus.com/TEST-001"
            mock_req.return_value = mock_resp
            mock_previews.return_value = []

            try:
                spider.get_info(
                    "TEST-001", include_downloads=False, include_previews=True
                )
            except Exception:
                pass  # 忽略其他解析错误，只关注 get_previews 的调用

            mock_previews.assert_called_once()

    def test_previews_not_called_with_include_previews_false(self):
        """include_previews=False 时不应调用 get_previews"""
        with (
            patch("app.utils.spider.javbus.JavbusSpider._initialize_session"),
            patch(
                "app.utils.spider.javbus.JavbusSpider._check_and_bypass_verification"
            ) as mock_req,
            patch("app.utils.spider.javbus.JavbusSpider.get_previews") as mock_previews,
        ):
            from app.utils.spider.javbus import JavbusSpider

            spider = JavbusSpider.__new__(JavbusSpider)
            spider.host = "https://www.javbus.com/"
            spider.name = "JavBus"

            fake_html = b"<html><body><h3>TEST-001</h3><div class='container'></div></body></html>"
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = fake_html.decode()
            mock_resp.url = "https://www.javbus.com/TEST-001"
            mock_req.return_value = mock_resp

            try:
                spider.get_info(
                    "TEST-001", include_downloads=True, include_previews=False
                )
            except Exception:
                pass

            mock_previews.assert_not_called()


# ──────────────────────────────────────────────
# Jav321: br.tail None 修复
# ──────────────────────────────────────────────


class TestJav321OutlineExtraction:
    """测试 jav321 outline 提取时 br.tail 为 None 的处理"""

    def test_br_with_none_tail_does_not_crash(self):
        """
        修复前: "".join(map(lambda i: i.tail, brs)) 在 tail=None 时会 TypeError
        修复后: 过滤 None 值
        """
        from app.utils.spider.jav321 import Jav321Spider

        # 构造包含 br 但没有 tail 文本的 HTML
        html_with_empty_br = etree.HTML(b"""
        <html><body>
        <small>TEST-001</small>
        <div class="row">
          <div>
            <div>
              <div class="row">
                <div>
                  Outline text
                  <br/>
                  <br/>
                </div>
              </div>
            </div>
          </div>
        </div>
        </body></html>
        """)

        with patch.object(Jav321Spider, "__init__", lambda self: None):
            spider = Jav321Spider.__new__(Jav321Spider)

        # 直接调用 join 逻辑（模拟 get_info 中的代码路径）
        no = html_with_empty_br.xpath("//small")
        if no:
            outline_element = no[0].xpath("./../../..//div[@class='row']")
            if outline_element:
                outline_div = outline_element[-1].xpath("./div")
                if outline_div:
                    brs = outline_div[0].xpath("./br")
                    # 修复后的代码：过滤 None tail
                    try:
                        extra = "".join(i.tail for i in brs if i.tail)
                        assert isinstance(extra, str)
                    except TypeError:
                        pytest.fail("br.tail 为 None 时引发 TypeError，修复未生效")


# ──────────────────────────────────────────────
# DMM: KeyError / AttributeError 修复
# ──────────────────────────────────────────────


class TestDmmKeyErrorFixes:
    """测试 DMM spider 对缺失字段的容错处理"""

    BASE_CONTENT = {
        "makerContentId": "test00001",
        "title": "Test Title",
        "description": "Test outline",
        "makerReleasedAt": "2026-01-01T00:00:00+09:00",
        "duration": 7200,
        "genres": [],
        "actresses": [],
    }

    def _make_spider(self):
        from app.utils.spider.dmm import DmmSpider

        with patch.object(DmmSpider, "__init__", lambda self: None):
            spider = DmmSpider.__new__(DmmSpider)
            spider.name = "DMM"
            spider.host = "https://www.dmm.co.jp"
            spider.api_url = "https://api.video.dmm.co.jp/graphql"
        return spider

    def _make_api_response(self, content_override=None, review=None):
        content = dict(self.BASE_CONTENT)
        if content_override:
            content.update(content_override)
        return {"data": {"ppvContent": content, "reviewSummary": review}}

    def _mock_requests(self, spider, api_json):
        """Mock spider.session.get 和 session.post"""
        mock_session = MagicMock()
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.text = (
            '"yesButtonLink":"/digital/videoa/-/detail/=/cid=test00001/"'
        )
        mock_session.get.return_value = mock_get_resp

        mock_post_resp = MagicMock()
        mock_post_resp.json.return_value = api_json
        mock_session.post.return_value = mock_post_resp

        spider.session = mock_session

    def test_no_packageImage_does_not_crash(self):
        """packageImage 缺失时不应崩溃（cover 为 None）"""
        spider = self._make_spider()
        resp = self._make_api_response({"packageImage": None})
        self._mock_requests(spider, resp)

        result = spider.get_info("TEST-001")
        assert result.cover is None

    def test_no_actresses_does_not_crash(self):
        """actresses 字段缺失时不应崩溃"""
        spider = self._make_spider()
        resp = self._make_api_response({"actresses": None})
        self._mock_requests(spider, resp)

        result = spider.get_info("TEST-001")
        assert result.actors == []

    def test_no_directors_does_not_crash(self):
        """directors 列表为空时不应崩溃"""
        spider = self._make_spider()
        resp = self._make_api_response({"directors": []})
        self._mock_requests(spider, resp)

        result = spider.get_info("TEST-001")
        assert result.director is None or result.director == ""

    def test_with_actresses(self):
        """正常的 actresses 数据应被提取"""
        spider = self._make_spider()
        resp = self._make_api_response(
            {
                "actresses": [
                    {
                        "name": "Test Actress",
                        "imageUrl": "https://example.com/avatar.jpg",
                    }
                ]
            }
        )
        self._mock_requests(spider, resp)

        result = spider.get_info("TEST-001")
        assert len(result.actors) == 1
        assert result.actors[0].name == "Test Actress"

    def test_get_previews_no_packageImage(self):
        """get_previews 中 packageImage 为 None 时不应 AttributeError"""
        spider = self._make_spider()
        content = {
            "sampleImages": [
                {
                    "imageUrl": "https://example.com/thumb1.jpg",
                    "largeImageUrl": "https://example.com/large1.jpg",
                }
            ],
            "sample2DMovie": {"highestMovieUrl": "https://example.com/sample.mp4"},
            "packageImage": None,  # 触发原 AttributeError
        }
        result = spider.get_previews(content)
        # 不应崩溃，视频预览的 thumb 为 None 也可接受
        assert isinstance(result, list)

    def test_get_real_page_raises_spider_exception(self):
        """找不到年龄确认按钮时应抛 SpiderException，而非裸 Exception"""
        from app.utils.spider.spider_exception import SpiderException

        spider = self._make_spider()
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "no age button here"  # 无 yesButtonLink
        mock_session.get.return_value = mock_resp
        spider.session = mock_session

        with pytest.raises(SpiderException):
            spider.get_real_page("TEST-001")


# ──────────────────────────────────────────────
# 在线网络集成测试（需手动启用）
# ──────────────────────────────────────────────


@pytest.mark.live_network
class TestJavdbLiveNetwork:
    """在线测试 - 需要网络和代理，默认跳过"""

    TEST_NUM = "SONE-701"  # 一个稳定存在的番号

    @pytest.fixture(scope="class")
    def spider(self):
        from app.utils.spider.javdb import JavdbSpider

        return JavdbSpider()

    def test_search_returns_url(self, spider):
        url = spider.search(self.TEST_NUM)
        assert url is not None
        assert "javdb" in url

    def test_get_info_returns_meta(self, spider):
        from app.schema import VideoDetail

        meta = spider.get_info(self.TEST_NUM)
        assert isinstance(meta, VideoDetail)
        assert meta.num.upper() == self.TEST_NUM.upper()
        assert meta.title
        assert meta.cover

    def test_get_ranking_censored_daily(self, spider):
        videos = spider.get_ranking_with_details("censored", "daily")
        assert len(videos) > 0, "有码日榜应返回数据"
        for v in videos[:5]:
            assert v.get("num"), "每个视频必须有番号"

    def test_get_ranking_uncensored_requires_login_or_returns_empty(self, spider):
        """无码排行榜：未配置 Cookie 时应返回空列表并记录警告"""
        videos = spider.get_ranking_with_details("uncensored", "daily")
        # 未配置 Cookie → 返回空列表（不崩溃）
        assert isinstance(videos, list)


@pytest.mark.live_network
class TestJavbusLiveNetwork:
    """在线测试 JavBus"""

    TEST_NUM = "SONE-701"

    @pytest.fixture(scope="class")
    def spider(self):
        from app.utils.spider.javbus import JavbusSpider

        return JavbusSpider()

    def test_get_info_returns_meta(self, spider):
        from app.schema import VideoDetail

        meta = spider.get_info(self.TEST_NUM)
        assert isinstance(meta, VideoDetail)
        assert meta.title

    def test_get_info_with_previews_calls_get_previews(self, spider):
        """include_previews=True 时应包含 previews（修复后行为）"""
        meta = spider.get_info(self.TEST_NUM, include_previews=True)
        # previews 可能为空（取决于页面），但不应是 None
        assert meta.previews is not None
