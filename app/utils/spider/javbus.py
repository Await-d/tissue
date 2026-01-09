import random
import re
import logging
import time
from datetime import datetime

import requests
from lxml import etree
from urllib.parse import urljoin, urlparse

from app.schema import VideoDetail, VideoActor, VideoDownload, VideoPreviewItem, VideoPreview
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException

logger = logging.getLogger(__name__)


def _request_with_retry(session, method: str, url: str, max_retries: int = 3, **kwargs):
    """带重试机制的请求方法"""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = session.request(method, url, **kwargs)
            return response
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避: 1s, 2s, 4s
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}，{wait_time}秒后重试")
                time.sleep(wait_time)
            else:
                logger.error(f"所有重试都失败了: {url}")
    raise last_error


class JavBusSpider(Spider):
    name = 'JavBus'
    origin_host = "https://www.javbus.com/"
    downloadable = True

    def __init__(self, alternate_host: str | None = None):
        # 设置 host（支持备用域名）
        self.host = alternate_host or self.origin_host
        
        # 不使用父类的自定义 Session，改用标准 requests.Session（为了更好地处理年龄验证）
        import requests as standard_requests

        # 初始化基础属性
        from app.schema import Setting
        self.setting = Setting().app
        self.session = standard_requests.Session()

        # 配置 session
        user_agent = getattr(self.setting, 'user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.session.headers = {
            'User-Agent': user_agent,
            'Referer': self.host,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session.verify = False
        self.session.timeout = 10

        logger.info(f"初始化爬虫: {self.name}, 域名: {self.host} (使用标准 requests.Session)")

        # 先访问首页建立正常的浏览会话
        self._initialize_session()

    def _initialize_session(self):
        """初始化 session，模拟正常浏览器访问"""
        try:
            # 先访问首页，建立正常session（带重试）
            logger.info("初始化 JavBus session，访问首页...")
            _request_with_retry(self.session, 'GET', self.host, allow_redirects=True, timeout=15)

            # 设置年龄验证 Cookie
            self._set_age_verification_cookies()

            # 等待一小段时间，模拟人类行为
            time.sleep(0.5)

            logger.info(f"Session 初始化完成，Cookie: {dict(self.session.cookies)}")
        except Exception as e:
            logger.warning(f"Session 初始化失败: {e}，将继续尝试")
            # 即使初始化失败，也设置 Cookie，后续请求可能会成功
            self._set_age_verification_cookies()

    def _cookie_domain(self) -> str:
        """获取 Cookie 域名"""
        netloc = urlparse(self.host).netloc
        return f".{netloc}"

    def _set_age_verification_cookies(self):
        """设置年龄验证 Cookie 以绕过年龄确认页面"""
        try:
            dom = self._cookie_domain()
            # JavBus 使用 age=verified Cookie来标记用户已通过年龄验证
            self.session.cookies.set('age', 'verified', domain=dom)
            self.session.cookies.set('locale', 'zh', domain=dom)
            logger.info(f"已为 {dom} 设置年龄验证 Cookie")
        except Exception as e:
            logger.warning(f"设置年龄验证 Cookie 失败: {e}")

    def _check_and_bypass_verification(self, url: str):
        """检查是否遇到年龄验证页面，如果是则尝试绕过"""
        try:
            # 使用带重试的请求
            response = _request_with_retry(self.session, 'GET', url, allow_redirects=True, timeout=15)

            # 检查是否被重定向到验证页面
            if 'driver-verify' in response.url or 'Age Verification' in response.text:
                logger.warning("检测到年龄验证页面，尝试重新初始化 session")

                # 清空现有 cookies 并重新设置
                self.session.cookies.clear()
                self._set_age_verification_cookies()

                # 重试请求，不跟随重定向以避免陷入循环
                response = _request_with_retry(self.session, 'GET', url, allow_redirects=False, timeout=15)

                # 如果仍然重定向，尝试更激进的方法：创建全新session
                if response.status_code in (301, 302, 303, 307, 308):
                    logger.warning("Cookie方法失败，创建新session重试")

                    # 使用标准 requests.Session 而不是自定义 Session
                    new_session = requests.Session()
                    new_session.headers = self.session.headers.copy()
                    new_session.verify = False
                    new_session.cookies.set('age', 'verified', domain=self._cookie_domain())

                    self.session = new_session
                    response = _request_with_retry(self.session, 'GET', url, allow_redirects=True, timeout=15)

            return response
        except Exception as e:
            logger.error(f"绕过验证时出错: {e}")
            raise SpiderException(f"连接 JavBus 失败: {e}")

    def get_info(self, num: str, url: str = None, include_downloads=False, include_previews=False,
                 include_comments=False):

        if url is None:
            url = urljoin(self.host, num)
        else:
            # 确保URL是完整的绝对URL
            if not url.startswith('http'):
                url = urljoin(self.host, url)

        # 使用新的验证绕过方法获取页面
        try:
            response = self._check_and_bypass_verification(url)
            
            # 检查响应状态码
            if response.status_code != 200:
                raise SpiderException(f'请求失败，状态码: {response.status_code}')
                
            html = etree.HTML(response.text)
            
            # 检查是否是有效的番号页面
            # 方法1: 检查是否有番号标题
            title_element = html.xpath("//h3")
            
            # 方法2: 检查页面title，如果包含404或者找不到，说明是无效页面
            page_title = html.xpath("//title/text()")
            if page_title:
                title_lower = page_title[0].lower()
                if '404' in title_lower or 'not found' in title_lower or '找不到' in title_lower:
                    raise SpiderException(f'番号 {num} 不存在')
            
            # 方法3: 检查是否有作品信息容器
            info_container = html.xpath("//div[@class='container']")
            
            # 如果三个关键元素都找不到，说明页面无效
            if not title_element and not info_container:
                # 尝试检查是否重定向到首页
                if response.url.rstrip('/') == self.host.rstrip('/'):
                    raise SpiderException(f'番号 {num} 不存在（重定向到首页）')
                raise SpiderException('未找到番号或页面结构已变化')

            # 确保title_element不为空
            if not title_element:
                raise SpiderException('未找到标题元素，页面结构可能已变化')

        except SpiderException:
            raise
        except Exception as e:
            raise SpiderException(f'获取页面失败: {e}')

        meta = VideoDetail()
        meta.num = num

        if title_element:
            title = title_element[0].text
            meta.title = title
        else:
            raise SpiderException('未找到番号')

        premiered_element = html.xpath("//span[text()='發行日期:']")
        if premiered_element:
            meta.premiered = premiered_element[0].tail.strip()

        runtime_element = html.xpath("//span[text()='長度:']")
        if runtime_element:
            runtime = runtime_element[0].tail.strip()
            runtime = runtime.replace("分鐘", "")
            meta.runtime = runtime

        director_element = html.xpath("//span[text()='導演:']/../a")
        if director_element:
            director = director_element[0].text
            meta.director = director

        studio_element = html.xpath("//span[text()='製作商:']/../a")
        if studio_element:
            studio = studio_element[0].text
            meta.studio = studio

        publisher_element = html.xpath("//span[text()='發行商:']/../a")
        if publisher_element:
            publisher = publisher_element[0].text
            meta.publisher = publisher

        series_element = html.xpath("//span[text()='系列:']/../a")
        if series_element:
            series = series_element[0].text
            meta.series = series

        tag_elements = html.xpath("//span[@class='genre']//a[contains(@href,'genre')]")
        if tag_elements:
            tags = [tag.text for tag in tag_elements]
            meta.tags = tags

        actor_elements = html.xpath("//span[@class='genre']//a[contains(@href,'star')]")
        if actor_elements:
            actors = []
            for element in actor_elements:
                actor_url = element.get('href')
                actor_code = actor_url.split("/")[-1]
                actor_avatar = urljoin(self.host, f'/pics/actress/{actor_code}_a.jpg')
                actor = VideoActor(name=element.text, thumb=actor_avatar)
                actors.append(actor)
            meta.actors = actors

        cover_element = html.xpath("//a[@class='bigImage']")
        if cover_element:
            cover = cover_element[0].get("href")
            meta.cover = urljoin(self.host, cover)

        meta.website.append(url)

        if include_downloads:
            meta.downloads = self.get_downloads(url, response.text)

        if include_downloads:
            meta.previews = self.get_previews(html)

        return meta

    def get_previews(self, html: etree.HTML):
        result = []

        images = html.xpath("//a[@class='sample-box']")
        for image in images:
            thumb = image.xpath("./div/img")[0]
            preview = VideoPreviewItem(type='image', thumb=urljoin(self.host, thumb.get('src')), url=image.get('href'))
            result.append(preview)

        return [VideoPreview(website=self.name, items=result)]

    def get_downloads(self, url: str, response: str):
        params = {'lang': 'zh', 'floor': random.Random().randint(100, 1000)}

        gid = re.search(r'var gid = (\w+);', response)
        params['gid'] = gid.group(1)

        uc = re.search(r'var uc = (\w+);', response)
        params['uc'] = uc.group(1)

        img = re.search(r'var img = \'(.+)\';', response)
        params['img'] = img.group(1)

        response = self.session.get(urljoin(self.host, '/ajax/uncledatoolsbyajax.php'), params=params,
                                    allow_redirects=True, headers={'Referer': self.host})
        html = etree.HTML(f'<table>{response.text}</table>', parser=etree.HTMLParser(encoding='utf-8'))

        result = []
        table = html.xpath("//tr")
        for item in table:
            parts = item.xpath("./td[1]/a")
            if not parts:
                continue

            download = VideoDownload()
            download.website = self.name
            download.url = url
            download.name = parts[0].text.strip()
            download.magnet = parts[0].get('href')

            title = parts[0].text.strip()
            if '无码' in title or '破解' in title or 'uncensored' in title:
                download.is_uncensored = True

            for tag in parts[1:]:
                if tag.text == '高清':
                    download.is_hd = True
                if tag.text == '字幕':
                    download.is_zh = True

            size_element = item.xpath("./td[2]/a")[0]
            download.size = size_element.text.strip()

            publish_date_element = item.xpath("./td[3]/a")[0]
            download.publish_date = datetime.strptime(publish_date_element.text.strip(), "%Y-%m-%d").date()

            result.append(download)
        return result
