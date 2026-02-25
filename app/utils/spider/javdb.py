import logging
import re
import time
from datetime import datetime
from random import randint
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from lxml import etree

from app.schema import (
    VideoDetail,
    VideoActor,
    VideoDownload,
    VideoPreviewItem,
    VideoPreview,
    VideoCommentItem,
    VideoComment,
    VideoSiteActor,
)
from app.schema.home import JavDBRanking
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException

# 获取logger
logger = logging.getLogger("spider")


class JavdbSpider(Spider):
    host = "https://javdb.com"
    name = "JavDB"
    downloadable = True
    avatar_host = "https://c0.jdbstatic.com/avatars/"

    # 候选镜像域名列表（可扩展/与站点管理配置配合使用）
    mirror_hosts = [
        "https://javdb.com",
        "https://javdb36.com",
        "https://javdb37.com",
        "https://javdb47.com",
    ]

    def __init__(self):
        # 初始化基础会话配置
        super().__init__()
        # 设置更完整的请求头，模拟真实浏览器
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "Referer": self.host,
            }
        )

        # 动态选择可用域名（被封或不可达时自动切换）
        try:
            self._select_best_host()
        except Exception as e:
            logger.warning(f"选择JavDB可用域名失败，使用默认 {self.host}: {e}")

        # 设置年龄验证Cookie（over18=1表示已确认年满18岁）
        # 需要在选择域名后设置，确保domain正确
        self.session.cookies.set("over18", "1", domain=self._cookie_domain())

        # 从设置中读取并应用JavDB登录Cookie
        self._apply_login_cookie()

    def _cookie_domain(self) -> str:
        netloc = urlparse(self.host).netloc
        return f".{netloc}"

    def _set_age_cookies(self):
        """为当前host设置18+与语言Cookie"""
        try:
            dom = self._cookie_domain()
            self.session.cookies.set("over18", "1", domain=dom)
            self.session.cookies.set("locale", "zh", domain=dom)
        except Exception as e:
            logger.debug(f"设置年龄验证Cookie失败: {e}")

    def _parse_score_text(self, score_text: str) -> tuple:
        """解析评分文本，支持新旧两种格式

        支持格式:
        - 新格式: "4.55, by 754 users" 或 "4.55 by 754 users"
        - 旧格式: "4.55分, 由754人評價"

        Args:
            score_text: 评分文本字符串

        Returns:
            tuple: (rank, rank_count) 元组，解析失败时返回 (None, 0)
        """
        if not score_text:
            return (None, 0)

        score_text = score_text.strip()

        # 尝试新格式: "4.55, by 754 users" 或 "4.55 by 754 users"
        rank_matched = re.search(r"([\d.]+),?\s*by\s*([\d,]+)\s*users?", score_text)
        if rank_matched:
            try:
                rank = float(rank_matched.group(1))
                rank_count = int(rank_matched.group(2).replace(",", ""))
                return (rank, rank_count)
            except (ValueError, TypeError):
                pass

        # 尝试旧格式: "4.55分, 由754人評價"
        rank_matched = re.match(r"(.+?)分,\s*由(.+?)人評價", score_text)
        if rank_matched:
            try:
                rank = float(rank_matched.group(1))
                rank_count = int(rank_matched.group(2))
                return (rank, rank_count)
            except (ValueError, TypeError):
                pass

        # 尝试仅有评分的旧格式: "4.55分"
        rank_matched = re.search(r"(\d+\.?\d*)分", score_text)
        if rank_matched:
            try:
                rank = float(rank_matched.group(1))
                # 单独解析评论数
                count_match = re.search(r"由(\d+)人評價", score_text)
                rank_count = int(count_match.group(1)) if count_match else 0
                return (rank, rank_count)
            except (ValueError, TypeError):
                pass

        return (None, 0)

    def _parse_date(self, date_str: str):
        """解析日期字符串，支持多种格式

        支持格式:
        - MM/DD/YYYY (如 01/15/2024)
        - YYYY-MM-DD (如 2024-01-15)

        Args:
            date_str: 日期字符串

        Returns:
            date: 解析成功返回 date 对象，失败返回 None
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # 尝试 MM/DD/YYYY 格式
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            pass

        # 尝试 YYYY-MM-DD 格式
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

        return None

    def _extract_text(self, element) -> str:
        if element is None:
            return ""
        return "".join(element.itertext()).strip()

    def _clean_label(self, text: str) -> str:
        if not text:
            return ""
        cleaned = re.sub(r"\s+", " ", text).strip().rstrip(":：")
        return cleaned.lower()

    def _extract_info_value(self, html: etree.HTML, labels: List[str]) -> Optional[str]:
        wanted = {self._clean_label(label) for label in labels}
        blocks = html.xpath("//strong")
        for strong in blocks:
            label = self._clean_label(self._extract_text(strong))
            if label not in wanted:
                continue

            sibling_values = strong.xpath(
                "./following-sibling::span[contains(@class,'value')][1]"
            )
            if sibling_values:
                value = self._extract_text(sibling_values[0])
                if value:
                    return value

            sibling_links = strong.xpath("./following-sibling::a[1]")
            if sibling_links:
                value = self._extract_text(sibling_links[0])
                if value:
                    return value

            sibling_nodes = strong.xpath("./following-sibling::*[1]")
            if sibling_nodes:
                value = self._extract_text(sibling_nodes[0])
                if value:
                    return value

        return None

    def _absolutize(self, maybe_url: str) -> str:
        url = (maybe_url or "").strip()
        if not url:
            return ""
        if url.startswith("//"):
            return "https:" + url
        if not url.startswith("http"):
            return urljoin(self.host, url)
        return url

    def _apply_login_cookie(self):
        """从设置中读取并应用JavDB登录Cookie"""
        try:
            from app.schema.setting import Setting

            javdb_cookie = self.setting.javdb_cookie
            if javdb_cookie:
                logger.info("检测到JavDB登录Cookie配置，正在应用...")
                # 解析cookie字符串并设置到session
                # 支持格式: "key1=value1; key2=value2"
                dom = self._cookie_domain()
                for cookie_pair in javdb_cookie.split(";"):
                    cookie_pair = cookie_pair.strip()
                    if "=" in cookie_pair:
                        key, value = cookie_pair.split("=", 1)
                        self.session.cookies.set(key.strip(), value.strip(), domain=dom)
                logger.info(f"已应用JavDB登录Cookie到域名: {dom}")
        except Exception as e:
            logger.debug(f"应用JavDB登录Cookie失败: {e}")

    def _select_best_host(self):
        """尝试镜像域名，选择可用的host"""
        # 去重并保持顺序：优先使用内置镜像列表，再包含当前默认host
        candidates = list(dict.fromkeys(self.mirror_hosts + [self.host]))
        test_paths = ["/videos", "/rankings/movies?p=weekly&t=censored", "/"]

        for base in candidates:
            for path in test_paths:
                try:
                    # 使用已配置的完整请求头
                    resp = self.session.get(urljoin(base, path))
                    # 状态码为200且不是封禁页面即认为可用
                    if resp.status_code == 200 and not self._is_banned_response(resp):
                        self.host = base
                        # 同步更新Referer，避免部分页面校验失败
                        self.session.headers["Referer"] = self.host
                        self._set_age_cookies()
                        logger.info(f"JavDB可用域名: {self.host}")
                        return
                except Exception:
                    continue

        # 若都不可用，仍设置基于现有host的cookie
        logger.warning("未能自动确认JavDB可用域名，将继续使用默认host")
        self._set_age_cookies()

    def _rebuild_url_for_current_host(self, absolute_or_relative_url: str) -> str:
        try:
            parsed = urlparse(absolute_or_relative_url)
            if not parsed.scheme:
                return urljoin(self.host, absolute_or_relative_url)
            current = urlparse(self.host)
            if parsed.netloc != current.netloc:
                path_with_query = parsed.path
                if parsed.query:
                    path_with_query += f"?{parsed.query}"
                return urljoin(self.host, path_with_query)
            return absolute_or_relative_url
        except Exception:
            return urljoin(self.host, absolute_or_relative_url)

    def _is_banned_response(self, resp) -> bool:
        try:
            if resp.status_code in (401, 403, 429, 503):
                return True
            # 如果是登录页面重定向，不算被封禁（可能只是需要登录）
            if "/login" in str(resp.url):
                return False
            content_lower = (
                resp.content.lower()
                if isinstance(resp.content, (bytes, bytearray))
                else b""
            )
            # 注意：移除了captcha检查，因为登录页面会包含验证码但不代表被封禁
            markers = [
                b"banned your access",
                b"access denied",
                b"forbidden",
                b"just a moment",
            ]
            return any(m in content_lower for m in markers)
        except Exception:
            return False

    def _get(self, url: str, headers=None):
        target = self._rebuild_url_for_current_host(url)
        resp = (
            self.session.get(target, headers=headers)
            if headers
            else self.session.get(target)
        )
        if self._is_banned_response(resp):
            logger.warning("检测到被封禁/风控，尝试切换镜像域名后重试")
            try:
                self._select_best_host()
            except Exception:
                pass
            target = self._rebuild_url_for_current_host(url)
            resp = (
                self.session.get(target, headers=headers)
                if headers
                else self.session.get(target)
            )
        return resp

    def get_info(
        self,
        num: str,
        url: Optional[str] = None,
        include_downloads=False,
        include_previews=False,
        include_comments: bool = False,
    ):
        searched = False

        if url is None:
            url = self.search(num)
            searched = True
        else:
            # 确保URL是完整的绝对URL
            if not url.startswith("http"):
                url = urljoin(self.host, url)

        if not url:
            raise SpiderException("未找到番号")
        else:
            if searched:
                time.sleep(randint(1, 3))

        meta = VideoDetail()
        meta.num = num

        if not isinstance(url, str):
            raise SpiderException("未找到番号")

        response = self._get(url)
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding="utf-8"))

        title_element = html.xpath(
            "//strong[contains(@class,'current-title')] | //h2[contains(@class,'title')]"
        )
        if title_element:
            title = self._extract_text(title_element[0])
            meta.title = f"{num.upper()} {title}"

        premiered = self._extract_info_value(
            html, ["日期", "released date", "release date"]
        )
        if premiered:
            meta.premiered = premiered

        runtime = self._extract_info_value(html, ["時長", "时长", "duration"])
        if runtime:
            runtime = re.sub(
                r"\s*(minute\(s\)|minutes?|分鍾|分钟|min)\s*",
                "",
                runtime,
                flags=re.IGNORECASE,
            )
            meta.runtime = runtime.strip()

        director = self._extract_info_value(html, ["導演", "导演", "director"])
        if director:
            meta.director = director

        studio = self._extract_info_value(html, ["片商", "maker", "studio"])
        if studio:
            meta.studio = studio

        publisher = self._extract_info_value(html, ["發行", "发行", "publisher"])
        if publisher:
            meta.publisher = publisher

        series = self._extract_info_value(html, ["系列", "series"])
        if series:
            meta.series = series

        # 标签 - Tags (过滤掉导航类标签如 '類別', 'Tags')
        tag_elements = html.xpath("//a[contains(@href,'/tags?')]")
        if tag_elements:
            skip_tags = ["類別", "Tags", "标签"]
            tags = [
                tag.text
                for tag in tag_elements
                if tag.text and tag.text not in skip_tags
            ]
            meta.tags = tags

        # 演员 - 支持中英文标签，female symbol 或 Actor(s) 标签
        actor_elements = html.xpath(
            "//strong[contains(@class,'symbol') and contains(@class,'female')]"
        )
        if actor_elements:
            actors = []
            for element in actor_elements:
                links = element.xpath("./preceding-sibling::a[1]")
                if not links:
                    continue
                actor_element = links[0]
                actor_url = actor_element.get("href")
                if not actor_url:
                    continue
                actor_code = actor_url.split("/")[-1]
                actor_avatar = urljoin(
                    self.avatar_host, f"{actor_code[0:2].lower()}/{actor_code}.jpg"
                )
                actor = VideoActor(
                    name=actor_element.text, thumb=actor_avatar, code=actor_code
                )
                actors.append(actor)
            meta.actors = actors
            meta.site_actors = [VideoSiteActor(website=self.name, items=actors)]
        else:
            actors = []
            actor_links = html.xpath("//a[contains(@href,'/actors/') and .//strong]")
            for actor_link in actor_links:
                actor_name = (
                    self._extract_text(actor_link.xpath(".//strong")[0])
                    if actor_link.xpath(".//strong")
                    else ""
                )
                actor_url = actor_link.get("href") or ""
                if not actor_name or not actor_url:
                    continue
                actor_code = actor_url.rstrip("/").split("/")[-1]
                actor_avatar = urljoin(
                    self.avatar_host, f"{actor_code[0:2].lower()}/{actor_code}.jpg"
                )
                actors.append(
                    VideoActor(name=actor_name, thumb=actor_avatar, code=actor_code)
                )
            if actors:
                meta.actors = actors
                meta.site_actors = [VideoSiteActor(website=self.name, items=actors)]

        cover_element = html.xpath(
            "//img[contains(@class,'video-cover')] | //div[contains(@class,'cover')]//img[1]"
        )
        if cover_element:
            meta.cover = self._absolutize(cover_element[0].get("src") or "")
        if not meta.cover:
            og_cover = html.xpath("//meta[@property='og:image']/@content")
            if og_cover:
                meta.cover = self._absolutize(og_cover[0])

        # 评分和评论数 - 支持新格式 "4.56, by 1575 users" 和旧格式 "4.56分, 由1575人評價"
        # 新结构: strong[text()='Rating:']/following-sibling::span[@class='value']
        rating_element = html.xpath(
            "//strong[contains(normalize-space(),'Rating') or contains(normalize-space(),'評分')]/following-sibling::span[contains(@class,'value')][1]"
        )
        if rating_element:
            # 获取所有文本内容
            rating_text = "".join(rating_element[0].itertext()).strip()

            # 尝试新格式: "4.56, by 1575 users"
            new_format_match = re.search(
                r"([\d.]+),?\s*by\s*([\d,]+)\s*users?", rating_text
            )
            if new_format_match:
                meta.rating = new_format_match.group(1)
                meta.comments_count = int(new_format_match.group(2).replace(",", ""))
            else:
                # 旧格式: "4.56分, 由1575人評價"
                score_match = re.search(r"(\d+\.?\d*)分?", rating_text)
                if score_match:
                    meta.rating = score_match.group(1)
                count_match = re.search(r"由(\d+)人評價", rating_text)
                if count_match:
                    meta.comments_count = int(count_match.group(1))
        else:
            # 回退：旧的XPath方式
            score_elements = html.xpath(
                "//span[contains(@class,'score-stars')]/../text()"
            )
            if score_elements:
                score_text = str(score_elements[0])
                pattern_result = re.search(r"(\d+\.?\d*)", score_text)
                if pattern_result:
                    meta.rating = pattern_result.group(1)

        # 如果上面没有获取到评论数，从tabs获取
        if not meta.comments_count:
            comments_elements = html.xpath("//div[contains(@class, 'tabs')]//a")
            for el in comments_elements:
                text = "".join(el.itertext()).strip()
                if "短評" in text or "Reviews" in text:
                    comments_match = re.search(r"\((\d+)\)", text)
                    if comments_match:
                        meta.comments_count = int(comments_match.group(1))
                        break

        websites = meta.website or []
        websites.append(url)
        meta.website = websites

        if include_downloads:
            meta.downloads = self.get_downloads(url, html)

        if include_previews:
            meta.previews = self.get_previews(html)

        return meta

    def search(self, num: str):
        url = urljoin(self.host, f"/search?q={num}&f=all")
        response = self._get(url)

        html = etree.HTML(response.content)
        matched_elements = html.xpath("//div[contains(@class,'video-title')]/strong")
        if not matched_elements:
            matched_elements = html.xpath(
                "//a[contains(@href,'/v/') and .//strong]//strong"
            )
        # 记录搜索结果用于调试
        logger.debug(f"搜索 {num} 找到 {len(matched_elements)} 个结果")

        # 精确匹配
        for matched_element in matched_elements:
            element_text = matched_element.text
            if element_text and element_text.strip().lower() == num.lower():
                parent_links = matched_element.xpath(
                    './ancestor::a[contains(@href,"/v/")][1]'
                )
                if not parent_links:
                    continue
                code = parent_links[0].get("href")
                logger.info(f"找到精确匹配的番号: {element_text} -> {code}")
                return urljoin(self.host, code)

        # 如果精确匹配失败，尝试模糊匹配（去掉横杠等）
        num_normalized = num.lower().replace("-", "").replace("_", "")
        for matched_element in matched_elements:
            element_text = matched_element.text
            if element_text:
                element_normalized = (
                    element_text.strip().lower().replace("-", "").replace("_", "")
                )
                if element_normalized == num_normalized:
                    parent_links = matched_element.xpath(
                        './ancestor::a[contains(@href,"/v/")][1]'
                    )
                    if not parent_links:
                        continue
                    code = parent_links[0].get("href")
                    logger.info(f"找到模糊匹配的番号: {element_text} -> {code}")
                    return urljoin(self.host, code)

        # 记录前几个搜索结果用于调试
        if matched_elements:
            logger.debug(f"搜索结果前5个番号:")
            for i, elem in enumerate(matched_elements[:5]):
                if elem.text:
                    logger.debug(f"  {i + 1}. {elem.text}")
        else:
            logger.warning(f"搜索 {num} 未找到任何结果")

        return None

    def get_previews(self, html: etree.HTML):
        result = []

        videos = html.xpath(
            "//div[contains(@class,'preview-images')]/a[contains(@class,'preview-video-container')]"
        )
        for video in videos:
            href = video.get("href")
            # 跳过指向登录页面的链接（未登录用户）
            if not href or href == "/login":
                continue
            thumb_elements = video.xpath("./img")
            if not thumb_elements:
                continue
            thumb = thumb_elements[0]
            video_sources = []
            if href.startswith("#"):
                video_sources = html.xpath(f"//video[@id='{href[1:]}']/source")
            if not video_sources:
                video_sources = video.xpath(".//source")

            if video_sources:
                thumb_src = thumb.get("src") or ""
                video_src = video_sources[0].get("src") or ""
                if not video_src and href and not href.startswith("#"):
                    video_src = href
                # 确保 URL 是绝对路径
                thumb_src = self._absolutize(thumb_src)
                video_src = self._absolutize(video_src)
                if video_src:
                    preview = VideoPreviewItem(
                        type="video", thumb=thumb_src, url=video_src
                    )
                    result.append(preview)

        images = html.xpath(
            "//div[contains(@class,'preview-images')]/a[contains(@class,'tile-item')]"
        )
        for image in images:
            thumb_elements = image.xpath("./img")
            if not thumb_elements:
                continue
            thumb = thumb_elements[0]
            thumb_src = thumb.get("src") or ""
            image_href = image.get("href") or ""
            # 确保 URL 是绝对路径
            thumb_src = self._absolutize(thumb_src)
            image_href = self._absolutize(image_href)
            if image_href:
                preview = VideoPreviewItem(
                    type="image", thumb=thumb_src, url=image_href
                )
                result.append(preview)

        return [VideoPreview(website=self.name, items=result)]

    def get_trending_videos(self, page: int = 1, time_range: str = "week"):
        """获取热门视频列表"""
        try:
            # 添加随机延迟，避免被识别为爬虫
            delay = randint(3, 8)
            logger.info(f"获取热门视频列表前等待 {delay} 秒...")
            time.sleep(delay)

            # 构造热门页面URL
            url = urljoin(self.host, f"/rankings/videos?t={time_range}&page={page}")
            logger.info(f"获取热门视频列表: {url}")

            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host,
            }

            response = self._get(url, headers=headers)
            html = etree.HTML(
                response.content, parser=etree.HTMLParser(encoding="utf-8")
            )

            videos = []
            video_elements = html.xpath("//div[contains(@class, 'item')]")

            for element in video_elements:
                try:
                    # 获取番号
                    title_element = element.xpath(
                        ".//div[contains(@class, 'video-title')]/strong"
                    )
                    if not title_element:
                        continue

                    num = title_element[0].text.strip()

                    # 获取链接
                    link_element = element.xpath(
                        ".//a[contains(@class, 'box') and contains(@href, '/v/')]"
                    )
                    if not link_element:
                        link_element = element.xpath(".//a[contains(@href, '/v/')]")
                    if not link_element:
                        continue

                    video_url = self._absolutize(link_element[0].get("href") or "")

                    # 获取封面
                    cover_element = element.xpath(".//img")
                    cover = (
                        self._absolutize(cover_element[0].get("src") or "")
                        if cover_element
                        else None
                    )

                    # 获取评分
                    rating_element = element.xpath(".//span[contains(@class, 'score')]")
                    rating = None
                    if rating_element:
                        rating_text = rating_element[0].text
                        rating_match = re.search(r"(\d+\.\d+)", rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))

                    video_info = {
                        "num": num,
                        "title": f"{num} {title_element[0].tail or ''}".strip(),
                        "url": video_url,
                        "cover": cover,
                        "rating": rating,
                        "website": self.name,
                    }

                    videos.append(video_info)

                except Exception as e:
                    logger.warning(f"解析视频信息时出错: {str(e)}")
                    continue

            return videos

        except Exception as e:
            logger.error(f"获取热门视频列表时出错: {str(e)}")
            return []

    def get_latest_videos(self, page: int = 1, date_range: int = 7):
        """获取最新视频列表"""
        try:
            # 添加随机延迟，避免被识别为爬虫
            delay = randint(3, 8)
            logger.info(f"获取最新视频列表前等待 {delay} 秒...")
            time.sleep(delay)

            # 构造最新页面URL
            url = urljoin(self.host, f"/videos?page={page}")
            logger.info(f"获取最新视频列表: {url}")

            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host,
            }

            response = self._get(url, headers=headers)
            html = etree.HTML(
                response.content, parser=etree.HTMLParser(encoding="utf-8")
            )

            videos = []
            video_elements = html.xpath("//div[contains(@class, 'item')]")

            for element in video_elements:
                try:
                    # 获取番号
                    title_element = element.xpath(
                        ".//div[contains(@class, 'video-title')]/strong"
                    )
                    if not title_element:
                        continue

                    num = title_element[0].text.strip()

                    # 获取链接
                    link_element = element.xpath(
                        ".//a[contains(@class, 'box') and contains(@href, '/v/')]"
                    )
                    if not link_element:
                        link_element = element.xpath(".//a[contains(@href, '/v/')]")
                    if not link_element:
                        continue

                    video_url = self._absolutize(link_element[0].get("href") or "")

                    # 获取发布日期
                    date_element = element.xpath(
                        ".//div[contains(@class, 'meta')]/text()"
                    )
                    publish_date = None
                    if date_element:
                        date_text = date_element[0].strip()
                        try:
                            publish_date = datetime.strptime(
                                date_text, "%Y-%m-%d"
                            ).date()
                        except:
                            pass

                    # 检查是否在指定日期范围内
                    if publish_date and date_range > 0:
                        days_ago = (datetime.now().date() - publish_date).days
                        if days_ago > date_range:
                            continue

                    # 获取封面
                    cover_element = element.xpath(".//img")
                    cover = (
                        self._absolutize(cover_element[0].get("src") or "")
                        if cover_element
                        else None
                    )

                    # 获取评分（如果有）
                    rating_element = element.xpath(".//span[contains(@class, 'score')]")
                    rating = None
                    if rating_element:
                        rating_text = rating_element[0].text
                        rating_match = re.search(r"(\d+\.\d+)", rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))

                    video_info = {
                        "num": num,
                        "title": f"{num} {title_element[0].tail or ''}".strip(),
                        "url": video_url,
                        "cover": cover,
                        "rating": rating,
                        "comments": 0,  # 最新视频页面没有评论数信息，设置为0
                        "comments_count": 0,  # 最新视频页面没有评论数信息，设置为0
                        "publish_date": publish_date,
                        "website": self.name,
                    }

                    videos.append(video_info)

                except Exception as e:
                    logger.warning(f"解析视频信息时出错: {str(e)}")
                    continue

            return videos

        except Exception as e:
            logger.error(f"获取最新视频列表时出错: {str(e)}")
            return []

    def get_comments_count(self, url: str):
        """获取视频评论数"""
        try:
            # 添加随机延迟，避免被识别为爬虫
            delay = randint(2, 5)
            logger.debug(f"获取评论数前等待 {delay} 秒...")
            time.sleep(delay)

            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host,
            }

            response = self._get(url, headers=headers)
            html = etree.HTML(
                response.content, parser=etree.HTMLParser(encoding="utf-8")
            )

            # 尝试多种XPath匹配评论数
            # 新格式: 短評(44) 或 Reviews(44)
            comments_elements = html.xpath("//div[contains(@class, 'tabs')]//a")
            for el in comments_elements:
                text = "".join(el.itertext()).strip()
                if "短評" in text or "Reviews" in text:
                    comments_match = re.search(r"\((\d+)\)", text)
                    if comments_match:
                        return int(comments_match.group(1))

            # 回退: 旧格式
            comments_elements = html.xpath("//a[contains(@href,'/reviews?')]/text()")
            if comments_elements:
                comments_text = comments_elements[0]
                comments_match = re.search(r"(\d+)", comments_text)
                if comments_match:
                    return int(comments_match.group(1))

            return 0

        except Exception as e:
            logger.error(f"获取评论数时出错: {str(e)}")
            return 0

    def get_downloads(self, url: str, html: etree.HTML):
        result = []
        # 新结构: div.item.columns > div.magnet-name > a
        table = html.xpath("//div[@id='magnets-content']/div[contains(@class, 'item')]")

        for item in table:
            download = VideoDownload()

            # 获取磁力链接元素
            magnet_link = item.xpath(".//div[contains(@class, 'magnet-name')]/a")
            if not magnet_link:
                magnet_link = item.xpath("./div[1]/a")
            if not magnet_link:
                continue

            parts = magnet_link[0]
            download.website = self.name
            download.url = url
            download.magnet = parts.get("href")

            # 获取名称 - 新结构使用 span.name
            name_el = parts.xpath("./span[@class='name']")
            if name_el:
                download.name = name_el[0].text.strip()
            else:
                # 旧结构回退
                first_text = parts.xpath("./text()")
                if first_text:
                    download.name = first_text[0].strip()
                else:
                    download.name = parts.text.strip() if parts.text else ""

            # 检查无码/破解标签
            name_text = download.name or ""
            if "无码" in name_text or "破解" in name_text or "UC" in name_text:
                download.is_uncensored = True

            # 获取文件大小 - 新结构使用 span.meta
            size_el = parts.xpath("./span[@class='meta']")
            if size_el:
                download.size = size_el[0].text.strip().split(",")[0].strip()
            else:
                # 旧结构回退
                size = parts.xpath("./span[2]")
                if size:
                    download.size = (
                        size[0].text.split(",")[0].strip() if size[0].text else ""
                    )

            # 获取标签 (HD, 字幕等) - 新结构使用 span.tag
            # 先尝试 div.tags 内的 span，再尝试直接的 span.tag
            tag_elements = parts.xpath('.//div[@class="tags"]/span') or parts.xpath(
                './/span[contains(@class, "tag")]'
            )
            for tag in tag_elements:
                tag_text = tag.text.strip() if tag.text else ""
                if tag_text in ["高清", "HD"]:
                    download.is_hd = True
                if tag_text in ["字幕", "Subtitle"]:
                    download.is_zh = True

            # 获取发布日期 - 新结构使用不同的元素
            publish_date = (
                item.xpath(".//span[@class='time']")
                or item.xpath(".//div[contains(@class, 'date')]")
                or item.xpath("./div[last()]")
            )
            if publish_date:
                date_text = publish_date[0].text
                if date_text:
                    date_text = date_text.strip()
                    try:
                        download.publish_date = datetime.strptime(
                            date_text, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        pass

            result.append(download)
        return result

    def get_ranking(self, video_type: str, cycle: str):
        url = urljoin(self.host, f"/rankings/movies?p={cycle}&t={video_type}")
        response = self._get(url)

        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding="utf-8"))

        result = []

        videos = html.xpath(
            "//div[contains(@class, 'movie-list')]//a[contains(@href, '/v/')]"
        )

        # 如果没有找到视频，检测是否需要登录并尝试fallback
        if not videos:
            needs_login = (
                "/login" in str(response.url)
                or b"requires login" in response.content.lower()
            )

            if needs_login:
                logger.warning("排行榜页面需要登录，尝试使用首页列表作为替代...")
                # 使用首页带过滤器的URL作为fallback
                fallback_url = urljoin(self.host, f"/?vft=1&t={video_type}")
                return self._parse_homepage_videos(fallback_url, video_type)
            else:
                logger.warning(f"排行榜页面未找到视频列表，URL: {response.url}")

        for video in videos:
            try:
                ranking = JavDBRanking()

                # 封面图片
                card = video.xpath("./ancestor::div[contains(@class, 'item')][1]")
                card = card[0] if card else video
                cover_imgs = card.xpath(".//div[contains(@class, 'cover')]//img")
                if cover_imgs:
                    ranking.cover = self._absolutize(cover_imgs[0].get("src") or "")

                # 标题
                ranking.title = video.get("title")
                if not ranking.title:
                    title_nodes = card.xpath(".//div[contains(@class, 'video-title')]")
                    if title_nodes:
                        ranking.title = self._extract_text(title_nodes[0])

                # 番号
                num_elements = card.xpath(
                    ".//div[contains(@class, 'video-title')]/strong"
                )
                if num_elements:
                    ranking.num = self._extract_text(num_elements[0])

                # 发布日期 - 使用公共方法解析
                meta_elements = card.xpath(".//div[contains(@class, 'meta')]")
                if meta_elements:
                    date_str = self._extract_text(meta_elements[0])
                    if date_str:
                        ranking.publish_date = self._parse_date(date_str)

                # 评分 - 使用公共方法解析
                score_elements = card.xpath(
                    ".//div[contains(@class, 'score')]//span[contains(@class, 'value')]"
                )
                if not score_elements:
                    score_elements = card.xpath(
                        ".//div[contains(@class, 'score')]/span"
                    )

                if score_elements:
                    score_text = "".join(score_elements[0].itertext()).strip()
                    ranking.rank, ranking.rank_count = self._parse_score_text(
                        score_text
                    )

                ranking.url = self._absolutize(video.get("href") or "")

                # 标签 - 检查是否有中文字幕
                tag_elements = card.xpath(
                    ".//div[contains(@class, 'tags')]/span/text()"
                )
                if tag_elements:
                    tag_str = " ".join(tag_elements)
                    ranking.is_zh = "中字" in tag_str or "CnSub" in tag_str
                else:
                    ranking.is_zh = False

                result.append(ranking)
            except Exception as e:
                logger.warning(f"解析排行榜项目失败: {e}")
                continue

        return result

    def _parse_homepage_videos(self, url: str, video_type: str):
        """解析首页视频列表 - 作为排行榜页面的fallback"""
        try:
            logger.info(f"使用首页列表作为fallback: {url}")
            response = self._get(url)
            html = etree.HTML(
                response.content, parser=etree.HTMLParser(encoding="utf-8")
            )

            result = []

            # 优化XPath选择器 - 限定在 movie-list 或 video-list 容器内查找
            # 避免匹配页面其他区域的链接
            video_links = html.xpath(
                '//div[contains(@class, "movie-list") or contains(@class, "video-list")]//a[contains(@href, "/v/")]'
            )

            # 如果没找到，尝试使用备用选择器
            if not video_links:
                video_links = html.xpath(
                    '//div[@class="grid-item"]//a[contains(@href, "/v/")]'
                )

            # 最后再使用更宽松的选择器
            if not video_links:
                video_links = html.xpath('//a[contains(@href, "/v/")]')

            logger.info(f"首页找到 {len(video_links)} 个视频链接")

            for video in video_links:
                try:
                    ranking = JavDBRanking()

                    # 获取视频URL
                    href = video.get("href")
                    if not href or "/v/" not in href:
                        continue
                    ranking.url = urljoin(self.host, href)

                    # 获取标题属性
                    ranking.title = video.get("title")

                    # 番号 - 从 video-title/strong 或直接的 strong 元素获取
                    num_elements = video.xpath(
                        './/div[contains(@class, "video-title")]/strong'
                    )
                    if not num_elements:
                        num_elements = video.xpath(".//strong")
                    if num_elements and num_elements[0].text:
                        ranking.num = num_elements[0].text.strip()
                    else:
                        continue  # 没有番号则跳过

                    # 封面图片
                    cover_imgs = video.xpath(".//img")
                    if cover_imgs:
                        cover_src = cover_imgs[0].get("src")
                        if cover_src:
                            if cover_src.startswith("//"):
                                cover_src = "https:" + cover_src
                            elif not cover_src.startswith("http"):
                                cover_src = urljoin(self.host, cover_src)
                            ranking.cover = cover_src

                    # 评分和评论数 - 使用公共方法解析
                    score_elements = video.xpath(
                        './/div[contains(@class, "score")]//span[@class="value"]'
                    )
                    if not score_elements:
                        score_elements = video.xpath(
                            './/div[contains(@class, "score")]/span'
                        )

                    if score_elements:
                        score_text = "".join(score_elements[0].itertext()).strip()
                        ranking.rank, ranking.rank_count = self._parse_score_text(
                            score_text
                        )

                    # 发布日期 - 使用公共方法解析
                    meta_elements = video.xpath('.//div[contains(@class, "meta")]')
                    if meta_elements:
                        date_text = meta_elements[0].text
                        if date_text:
                            ranking.publish_date = self._parse_date(date_text)

                    # 标签 - 检查是否有中文字幕
                    tag_elements = video.xpath(
                        './/div[contains(@class, "tags")]/span/text()'
                    )
                    if tag_elements:
                        tag_str = " ".join(tag_elements)
                        ranking.is_zh = "中字" in tag_str or "CnSub" in tag_str
                    else:
                        ranking.is_zh = False

                    # 使用 video_type 参数设置是否无码
                    ranking.is_uncensored = video_type == "uncensored"

                    result.append(ranking)

                except Exception as e:
                    logger.debug(f"解析首页视频项目失败: {e}")
                    continue

            # 按评分排序（降序），模拟排行榜效果
            result.sort(key=lambda x: (x.rank or 0, x.rank_count or 0), reverse=True)

            logger.info(f"首页fallback成功解析 {len(result)} 个视频")
            return result

        except Exception as e:
            logger.error(f"解析首页视频列表失败: {e}")
            return []

    def get_ranking_with_details(self, video_type: str, cycle: str, max_pages: int = 1):
        """获取排行榜数据，包含评分和评论信息，用于智能下载规则"""
        try:
            # 构造排行榜URL - 排行榜页面不需要分页，一次返回全部数据
            if video_type == "uncensored":
                # 无码排行榜使用movies路径，通过t参数指定uncensored
                url = urljoin(self.host, f"/rankings/movies?p={cycle}&t=uncensored")
                page_type = "uncensored_ranking"
            else:
                # 有码排行榜同样使用movies路径，通过t参数指定censored
                url = urljoin(self.host, f"/rankings/movies?p={cycle}&t=censored")
                page_type = "censored_ranking"

            logger.info(f"获取排行榜页面: {url} (类型: {page_type})")

            # 添加随机延迟，避免被识别为爬虫
            delay = randint(3, 8)
            logger.info(f"等待 {delay} 秒...")
            time.sleep(delay)

            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host,
            }

            # 设置年龄验证Cookie绕过成人内容确认（根据当前host动态设置）
            self._set_age_cookies()

            response = self._get(url, headers=headers)
            # 检测是否被重定向到登录页（无码排行榜需要登录）
            if (
                "/login" in str(response.url)
                or b"\xe7\x99\xbb\xe5\x85\xa5" in response.content[:1000]
            ):
                logger.warning(
                    f"排行榜页面需要登录 ({video_type} {cycle})，请在设置中配置JavDB登录Cookie才能获取无码排行榜数据"
                )
                return []
            html = etree.HTML(
                response.content, parser=etree.HTMLParser(encoding="utf-8")
            )

            # 仅在 DEBUG 级别日志启用时写入调试文件，避免生产环境磁盘写入
            if logger.isEnabledFor(10):  # logging.DEBUG == 10
                debug_filename = f"javdb_{page_type}_debug.html"
                try:
                    with open(debug_filename, "wb") as f:
                        f.write(response.content)
                    logger.debug(f"已保存调试页面到 {debug_filename}")
                except Exception:
                    pass

            # 根据页面类型使用不同的解析策略
            if page_type == "uncensored_ranking":
                videos = self._parse_uncensored_ranking_page(html, 1)
            else:
                videos = self._parse_censored_ranking_page(html, 1)

            if not videos:
                logger.warning(f"未解析到视频数据")
                return []

            logger.info(f"排行榜解析完成，获取到 {len(videos)} 个视频")

            # 输出前3个视频的详细信息用于调试
            for i, video in enumerate(videos[:3]):
                logger.info(
                    f"视频 {i + 1}: {video.get('num')} - 评分: {video.get('rating')} - 评论: {video.get('comments')} - 页面类型: {video.get('page_type')}"
                )

            return videos

        except Exception as e:
            logger.error(f"获取排行榜数据时出错: {str(e)}")
            import traceback

            logger.debug(traceback.format_exc())
            return []

    def _parse_censored_ranking_page(self, html, page):
        """解析有码排行榜页面"""
        return self._parse_ranking_page(html, page, "censored_ranking")

    def _parse_ranking_page(self, html, page, page_type):
        """统一的排行榜页面解析方法 - 根据实际HTML结构"""
        videos = []

        # 排行榜页面使用movie-list结构
        video_elements = html.xpath(
            "//div[contains(@class, 'movie-list')]//div[contains(@class, 'item')]"
        )
        logger.info(f"{page_type}第 {page} 页找到 {len(video_elements)} 个视频元素")

        # 如果没找到，尝试其他可能的选择器
        if not video_elements:
            alternative_selectors = [
                "//div[@class='item']",  # 直接查找item
                "//div[contains(@class, 'movie-list')]//div[contains(@class, 'item')]",  # 更宽松的匹配
                "//div[@class='grid-item']",  # 可能的替代class名
                "//div[contains(@class, 'video-item')]",  # 其他可能的video item class
            ]

            for selector in alternative_selectors:
                video_elements = html.xpath(selector)
                if video_elements:
                    logger.info(
                        f"使用备用选择器找到 {len(video_elements)} 个视频元素: {selector}"
                    )
                    break
                else:
                    logger.debug(f"备用选择器无结果: {selector}")

        if not video_elements:
            # 输出页面的一些基本信息用于调试
            page_title = html.xpath("//title/text()")
            if page_title:
                logger.warning(f"页面标题: {page_title[0]}")

            # 检查是否有年龄验证模态框
            modal_elements = html.xpath("//div[contains(@class, 'modal')]")
            if modal_elements:
                logger.warning(
                    f"检测到 {len(modal_elements)} 个模态框元素，可能需要年龄验证"
                )

            logger.warning(f"未找到任何视频元素，页面可能结构已变化或需要额外验证")

        for element in video_elements:
            try:
                video_info = {}

                # 获取番号 - 从video-title下的strong元素
                title_element = element.xpath(
                    ".//div[contains(@class, 'video-title')]/strong"
                )
                if not title_element or not title_element[0].text:
                    continue
                num = title_element[0].text.strip()
                video_info["num"] = num
                video_info["page_type"] = page_type

                # 获取链接 - 从a.box元素
                link_element = element.xpath(
                    ".//a[contains(@class, 'box') and contains(@href, '/v/')]"
                )
                if not link_element:
                    link_element = element.xpath(".//a[contains(@href, '/v/')]")
                if link_element:
                    video_url = self._absolutize(link_element[0].get("href") or "")
                    video_info["url"] = video_url

                # 获取标题 - video-title的完整文本
                title_div = element.xpath(".//div[contains(@class, 'video-title')]")
                if title_div:
                    # 提取完整标题文本
                    full_title = "".join(title_div[0].itertext()).strip()
                    video_info["title"] = full_title
                else:
                    video_info["title"] = num

                # 获取封面
                cover_element = element.xpath(".//img")
                if cover_element:
                    video_info["cover"] = self._absolutize(
                        cover_element[0].get("src") or ""
                    )

                # 获取评分和评论数 - 使用公共方法解析
                score_element = element.xpath(
                    ".//div[contains(@class, 'score')]//span[contains(@class, 'value')]"
                )
                if not score_element:
                    score_element = element.xpath(
                        ".//div[contains(@class, 'score')]/span"
                    )
                rating = None
                comments = 0

                if score_element:
                    score_text = "".join(score_element[0].itertext()).strip()
                    logger.debug(f"原始评分文本: '{score_text}'")
                    rating, comments = self._parse_score_text(score_text)
                    if rating is not None:
                        logger.debug(f"成功提取评分: {rating}, 评论数: {comments}")

                video_info["rating"] = rating
                video_info["comments"] = comments
                video_info["comments_count"] = comments

                # 获取发布日期
                meta_elements = element.xpath(".//div[contains(@class, 'meta')]")
                if meta_elements:
                    date_text = "".join(meta_elements[0].itertext()).strip()
                    if date_text:
                        parsed_date = self._parse_date(date_text)
                        video_info["release_date"] = (
                            parsed_date.strftime("%Y-%m-%d") if parsed_date else None
                        )

                # 设置质量标签
                video_info["is_uncensored"] = page_type == "uncensored_ranking"
                video_info["is_hd"] = False  # 排行榜数据默认不标记为高清，避免影响筛选

                # 检查中文字幕: cnsub标签（封面区域）或含中字的tags
                cnsub_elements = element.xpath(".//span[contains(@class, 'cnsub')]")
                tag_texts = " ".join(
                    element.xpath(".//div[contains(@class, 'tags')]//span/text()")
                )
                video_info["is_zh"] = (
                    bool(cnsub_elements) or "中字" in tag_texts or "CnSub" in tag_texts
                )

                video_info["website"] = self.name

                videos.append(video_info)
                logger.debug(f"成功解析视频: {num} - 评分: {rating} - 评论: {comments}")

            except Exception as e:
                logger.warning(f"解析{page_type}视频信息时出错: {str(e)}")
                continue

        logger.info(
            f"{page_type}第{page}页解析完成: 总数{len(videos)}个, 有评分{sum(1 for v in videos if v.get('rating'))}个, 有评论{sum(1 for v in videos if v.get('comments', 0) > 0)}个"
        )
        return videos

    def _parse_uncensored_ranking_page(self, html, page):
        """解析无码排行榜页面"""
        return self._parse_ranking_page(html, page, "uncensored_ranking")

    def get_actors(self):
        """获取JavDB网站上的热门演员列表"""
        url = urljoin(self.host, "/actors")
        response = self._get(url)
        html_content = response.content

        # 保存HTML用于调试
        try:
            with open("javdb_actors_debug.html", "wb") as f:
                f.write(html_content)
            logger.info(
                f"已保存演员列表页面到javdb_actors_debug.html，页面大小: {len(html_content)}字节"
            )
        except Exception as e:
            logger.error(f"保存调试HTML失败: {str(e)}")

        html = etree.HTML(html_content, parser=etree.HTMLParser(encoding="utf-8"))

        # 网站结构：div.actors > div.actor-box > a
        actors_container = html.xpath('//div[contains(@class, "actors")]')
        logger.info(f"找到actors容器元素: {len(actors_container)}个")

        if not actors_container:
            logger.warning("未找到actors容器元素，尝试查找其他可能的演员元素")

            alt_actors = html.xpath('//a[contains(@href, "/actors/")]')
            logger.info(f"尝试替代方式找到演员元素: {len(alt_actors)}个")

            if not alt_actors:
                logger.error("无法找到任何演员元素，可能需要登录或网站结构已更改")
                title = html.xpath("//title/text()")
                logger.info(f"页面标题: {title}")

                login_form = html.xpath(
                    '//form[contains(@action, "login") or contains(@action, "sign_in")]'
                )
                if login_form:
                    logger.error("检测到登录表单，网站可能需要登录才能访问演员列表")

                return []

        result = []
        # 使用 //a 来穿透中间的 div.actor-box 层
        actors = html.xpath(
            '//div[contains(@class, "actors")]//a[contains(@href, "/actors/")]'
        )

        if not actors:
            actors = html.xpath('//a[contains(@href, "/actors/") and .//strong]')
            logger.info(f"使用替代XPath找到演员: {len(actors)}个")

        logger.info(f"找到演员元素: {len(actors)}个")

        for actor in actors:
            try:
                actor_url = actor.get("href")
                if not actor_url or "/actors/" not in actor_url:
                    continue

                actor_code = actor_url.split("/")[-1]
                # 排除分类页面链接
                if not actor_code or actor_code in [
                    "",
                    "censored",
                    "uncensored",
                    "western",
                ]:
                    continue

                # 优先从 title 属性获取演员名称
                actor_name = actor.get("title")

                if not actor_name:
                    # 从 strong 标签获取名称
                    name_el = actor.xpath("./strong/text()")
                    if name_el:
                        actor_name = name_el[0].strip()
                    else:
                        continue

                actor_name = actor_name.strip()
                if not actor_name:
                    continue

                logger.info(f"找到演员: {actor_name}, URL: {actor_url}")

                actor_avatar = urljoin(
                    self.avatar_host, f"{actor_code[0:2].lower()}/{actor_code}.jpg"
                )

                actor_info = VideoActor(name=actor_name, thumb=actor_avatar)
                result.append(actor_info)
            except Exception as e:
                logger.error(f"处理演员元素时出错: {str(e)}")
                continue

        logger.info(f"总共找到 {len(result)} 个演员")
        return result

    def search_actor(self, actor_name: str):
        """搜索JavDB网站上的演员"""
        url = urljoin(self.host, f"/search?q={actor_name}&f=actor")
        response = self._get(url)
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding="utf-8"))

        result = []

        # 尝试不同的XPath表达式找到演员列表
        actors = html.xpath('//a[contains(@href, "/actors/")]')

        for actor in actors:
            try:
                actor_url = actor.get("href")
                if not actor_url or "actors" not in actor_url:
                    continue

                actor_code = actor_url.split("/")[-1]

                # 查找演员名称
                name = None
                name_el = actor.xpath("./strong") or actor.xpath(".//strong")
                if name_el:
                    name = name_el[0].text.strip()
                else:
                    # 如果找不到标签，尝试使用元素自身的文本
                    name = actor.text.strip() if actor.text else None

                if not name:
                    # 如果还找不到名称，可能演员名称在title属性中
                    name = actor.get("title")
                    if name:
                        # 如果title包含多个名称（逗号分隔），取第一个
                        name = name.split(",")[0].strip()

                if not name:
                    continue

                # 构造头像URL
                actor_avatar = urljoin(
                    self.avatar_host, f"{actor_code[0:2].lower()}/{actor_code}.jpg"
                )

                actor_info = VideoActor(name=name, thumb=actor_avatar)
                result.append(actor_info)
            except Exception as e:
                continue

        return result

    def get_actor_videos(self, actor_url: str):
        """获取演员的所有视频 - 优化版本，直接从演员页面提取所有信息"""
        # 处理不同格式的actor_url输入
        if not actor_url.startswith(self.host):
            if not actor_url.startswith("http"):
                # 如果提供的是演员名称而不是URL，先搜索获取演员信息
                actors = self.search_actor(actor_url)
                if not actors:
                    logger.info(f"未找到演员: {actor_url}")
                    return []

                # 找到最匹配的演员
                actor_match = None
                for actor in actors:
                    if (
                        actor.name.lower() == actor_url.lower()
                        or actor_url.lower() in actor.name.lower()
                    ):
                        actor_match = actor
                        break

                if not actor_match:
                    # 排除掉有碼、無碼、歐美等类别标签
                    filtered_actors = [
                        a for a in actors if a.name not in ["有碼", "無碼", "歐美"]
                    ]
                    if filtered_actors:
                        actor_match = filtered_actors[0]
                    elif actors:
                        actor_match = actors[0]
                    else:
                        logger.error(f"没有找到任何匹配的演员: {actor_url}")
                        return []

                logger.info(f"选择演员: {actor_match.name}")

                # 从thumb中提取actor_id
                thumb_url = actor_match.thumb
                actor_code = thumb_url.split("/")[-1].split(".")[0]
                actor_url = urljoin(self.host, f"/actors/{actor_code}")
            elif "/actors/" not in actor_url:
                return []
            else:
                actor_url = urljoin(self.host, actor_url)

        logger.info(f"访问演员作品页: {actor_url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": self.host,
        }

        original_headers = self.session.headers.copy()
        self.session.headers.update(headers)

        try:
            # 访问演员页面
            response = self._get(actor_url)
            html = etree.HTML(
                response.content, parser=etree.HTMLParser(encoding="utf-8")
            )

            result = []

            # 从演员页面直接提取作品信息（包含评分、评论数、日期等）
            movie_boxes = html.xpath('//a[@class="box"]')
            logger.info(f"从演员页面找到 {len(movie_boxes)} 个作品")

            for box in movie_boxes:
                try:
                    item = JavDBRanking()

                    # 提取视频URL
                    video_url = box.get("href")
                    if not video_url.startswith("http"):
                        video_url = urljoin(self.host, video_url)
                    item.url = video_url

                    # 提取番号和标题
                    title_element = box.xpath('.//div[contains(@class, "video-title")]')
                    if title_element:
                        # 提取番号
                        num_element = title_element[0].xpath("./strong/text()")
                        if num_element:
                            item.num = num_element[0].strip()

                        # 提取完整标题
                        full_title = title_element[0].xpath("string(.)")
                        if full_title:
                            item.title = full_title.strip()

                    # 提取封面
                    cover_element = box.xpath('.//img[@loading="lazy"]')
                    if cover_element:
                        cover_url = cover_element[0].get("src")
                        if cover_url and not cover_url.startswith("http"):
                            cover_url = (
                                "https:" + cover_url
                                if cover_url.startswith("//")
                                else urljoin(self.host, cover_url)
                            )
                        item.cover = cover_url

                    # 使用公共方法提取评分和评论数
                    score_element = box.xpath(
                        './/div[contains(@class, "score")]//span[@class="value"]'
                    )
                    if score_element:
                        score_text = "".join(score_element[0].itertext()).strip()
                        rank, rank_count = self._parse_score_text(score_text)
                        if rank is not None:
                            item.rank = rank  # 前端使用
                            item.rating = str(rank)  # 演员订阅使用
                        if rank_count:
                            item.rank_count = rank_count

                    # 检查中文字幕和无码标签
                    cnsub_element = box.xpath('.//span[contains(@class, "cnsub")]')
                    item.is_zh = len(cnsub_element) > 0

                    uncensored_element = box.xpath(
                        './/span[contains(@class, "uncensored")]'
                    )
                    item.is_uncensored = len(uncensored_element) > 0

                    # 使用公共方法解析发布日期
                    date_element = box.xpath('.//div[contains(@class, "meta")]/text()')
                    if date_element and len(date_element) > 0:
                        date_text = date_element[0].strip()
                        item.publish_date = self._parse_date(date_text)

                    # 只有有番号的条目才添加到结果中
                    if item.num:
                        result.append(item)

                except Exception as e:
                    logger.error(f"处理作品条目时出错: {str(e)}")
                    continue

            logger.info(
                f"成功提取到 {len(result)} 个作品信息，包含评分、评论数、日期等完整信息"
            )

            # 输出前3个作品的详细信息用于调试
            for i, item in enumerate(result[:3]):
                logger.info(
                    f"作品 {i + 1}: {item.num} - 评分: {item.rank}/{item.rating} - 评论: {item.rank_count} - 日期: {item.publish_date}"
                )

            return result

        finally:
            # 恢复原始头信息
            self.session.headers = original_headers
