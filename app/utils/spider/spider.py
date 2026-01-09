from abc import abstractmethod
import time
import logging

import requests
import urllib3.util

from app.schema import Setting
from app.utils.spider.spider_exception import SpiderException

logger = logging.getLogger('spider')


class Session(requests.Session):

    def __init__(self, timeout: int = 10):
        super().__init__()
        self.timeout = timeout

    def request(self, *args, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        return super(Session, self).request(*args, **kwargs)


class Spider:
    name = None
    origin_host = None
    downloadable = False

    def __init__(self, alternate_host: str | None = None):
        self.host = alternate_host or self.origin_host

        self.setting = Setting().app
        self.session = Session()
        self.session.headers = {'User-Agent': self.setting.user_agent, 'Referer': self.host}
        self.session.timeout = (5, self.session.timeout)

    def _request_with_retry(self, url: str, method: str = 'get', max_retries: int = 3,
                           timeout: int = 30, retry_delay_base: int = 2, **kwargs) -> requests.Response:
        """
        带重试机制的HTTP请求

        Args:
            url: 请求URL
            method: HTTP方法 (get, post, etc.)
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
            retry_delay_base: 重试延迟基数（秒），实际延迟为 base * attempt
            **kwargs: 传递给requests的其他参数

        Returns:
            requests.Response: 响应对象

        Raises:
            SpiderException: 所有重试都失败时抛出
        """
        last_error = None
        kwargs['timeout'] = timeout

        for attempt in range(max_retries):
            try:
                response = getattr(self.session, method)(url, **kwargs)
                return response
            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} 请求失败 (尝试 {attempt + 1}/{max_retries}): {url} - {e}")
                if attempt < max_retries - 1:
                    delay = retry_delay_base * (attempt + 1)
                    time.sleep(delay)

        logger.error(f"{self.name} 请求失败，已重试 {max_retries} 次: {url} - {last_error}")
        raise SpiderException(f"请求失败: {last_error}")

    @abstractmethod
    def get_info(self, num: str, url: str = None, include_downloads: bool = False, include_previews: bool = False,
                 include_comments=False):
        pass

    @classmethod
    def get_cover(cls, url):
        if cls.origin_host:
            referer = cls.origin_host
        else:
            uri = urllib3.util.parse_url(url)
            referer = f'{uri.scheme}://{uri.host}/'
        response = requests.get(url, headers={'Referer': referer}, timeout=10)
        if response.ok:
            return response.content
        return None

    def testing(self) -> bool:
        try:
            response = self.session.get(self.origin_host)
            return response.ok
        except Exception as e:
            return False
