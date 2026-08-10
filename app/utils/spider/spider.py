'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-24 20:08:46
Description: 请填写简介
'''
'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-24 17:53:27
Description: 请填写简介
'''
'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-24 17:48:42
Description: 请填写简介
'''
from abc import abstractmethod
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from curl_cffi import requests as cffi_requests
    from curl_cffi.requests import Session as CffiSession
    HAS_CURL_CFFI = True
except ImportError:
    import requests as cffi_requests
    from requests import Session as CffiSession
    HAS_CURL_CFFI = False

import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from app.schema import Setting
from app.schema.setting import SettingApp

# 禁用SSL警告
disable_warnings(InsecureRequestWarning)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('spider')

# curl_cffi 使用的 Chrome 版本（与 UA 对齐）
_IMPERSONATE = "chrome120"

_DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)


def _get_app_setting():
    """读取应用设置。配置库未就绪时返回默认值，避免图片链路被配置问题拖死。"""
    try:
        return Setting().app
    except Exception:
        return SettingApp()


def _normalize_host(value: str) -> str:
    host = value.strip().rstrip('/')
    if not host:
        return ''
    if not host.startswith(('http://', 'https://')):
        host = f'https://{host}'
    return host


def parse_host_list(raw: str | None, fallback: list[str]) -> list[str]:
    """解析逗号/换行分隔的域名列表，去重并保持顺序。

    配置了域名就以配置为准，不再追加内置列表：用户显式指定镜像时，
    继续探测已失效的内置域名只会白白增加首页等待时间。
    需要回到内置列表时把配置项留空即可。
    """
    configured = [
        normalized
        for normalized in (_normalize_host(chunk) for chunk in str(raw or '').replace('\n', ',').split(','))
        if normalized
    ]
    if configured:
        return list(dict.fromkeys(configured))

    return list(dict.fromkeys(_normalize_host(host) for host in fallback if _normalize_host(host)))


class Session(CffiSession if HAS_CURL_CFFI else requests.Session):

    def __init__(self, timeout: int = 10):
        if HAS_CURL_CFFI:
            super().__init__(impersonate=_IMPERSONATE)
        else:
            super().__init__()
        self.timeout = timeout
        # curl_cffi 不需要禁用SSL验证，它自带了对Cloudflare的支持
        if not HAS_CURL_CFFI:
            self.verify = False

    def request(self, *args, **kwargs):
        method = args[0] if args else kwargs.get('method')
        url = args[1] if len(args) > 1 else kwargs.get('url')
        logger.info(f"请求: {method} {url}")

        # max_retries 是本封装自有参数，不能透传给底层 http 库
        max_retries = max(1, int(kwargs.pop('max_retries', 3)))

        kwargs.setdefault('timeout', self.timeout)
        if not HAS_CURL_CFFI:
            kwargs.setdefault('verify', False)
        else:
            # curl_cffi 用 impersonate 排试指纹，不需要额外verify参数
            kwargs.setdefault('impersonate', _IMPERSONATE)

        for attempt in range(max_retries):
            try:
                response = super(Session, self).request(*args, **kwargs)
                logger.info(f"响应: {response.status_code} - {url}")
                if response.status_code != 200:
                    logger.error(f"请求失败: {response.status_code} - {url}")
                    logger.error(f"响应内容: {response.text[:200]}")
                return response
            except Exception as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"所有重试都失败了: {url}")
                    raise

class Spider:
    name = None
    host = None
    downloadable = False

    # 用户配置的站点 Cookie 所在的设置项名（子类覆盖，如 'javdb_cookie'）。
    # 过 Cloudflare 质询拿到的 cf_clearance 就填在这里，图片抓取也需要带上。
    cookie_setting_key: str | None = None

    def __init__(self):
        self.setting = Setting().app
        self.session = Session()
        user_agent = getattr(self.setting, 'user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        self.session.headers = {'User-Agent': user_agent, 'Referer': self.host}
        self.session.timeout = (5, self.session.timeout)

        # 应用HTTP代理（设置了proxy时，所有请求包括选择内容阵时的请求均会经过代理）
        proxy = getattr(self.setting, 'proxy', None) or ''
        if proxy.strip():
            self.session.proxies = {
                'http': proxy.strip(),
                'https': proxy.strip(),
            }
            logger.info(f"应用HTTP代理: {proxy.strip()}")
        logger.info(f"初始化爬虫: {self.name}, 域名: {self.host}")

    @abstractmethod
    def get_info(self, num: str, url: str = None, include_downloads: bool = False, include_previews: bool = False,
                include_comments: bool = False):
        pass

    # 获取网站演员列表
    def get_actors(self):
        """获取网站上的热门演员列表，子类可以选择性实现"""
        logger.info(f"获取{self.name}网站演员列表")
        return []
        
    # 搜索演员
    def search_actor(self, actor_name: str):
        """搜索网站上的演员，子类可以选择性实现"""
        logger.info(f"在{self.name}搜索演员: {actor_name}")
        return []
        
    # 获取演员视频列表
    def get_actor_videos(self, actor_url: str):
        """获取演员的视频列表，子类可以选择性实现"""
        logger.info(f"获取{self.name}演员视频列表: {actor_url}")
        return []
    
    # 获取热门视频列表
    def get_trending_videos(self, page: int = 1, time_range: str = "week"):
        """获取热门视频列表，子类可以选择性实现"""
        logger.info(f"获取{self.name}热门视频列表: page={page}, time_range={time_range}")
        return []
    
    # 获取最新视频列表
    def get_latest_videos(self, page: int = 1, date_range: int = 7):
        """获取最新视频列表，子类可以选择性实现"""
        logger.info(f"获取{self.name}最新视频列表: page={page}, date_range={date_range}")
        return []
    
    # 获取评论数
    def get_comments_count(self, url: str):
        """获取视频评论数，子类可以选择性实现"""
        logger.info(f"获取{self.name}视频评论数: {url}")
        return 0

    # 图片抓取时附加的站点专属 Cookie，由子类覆盖（如 over18=1 / age=verified）
    cover_cookies: dict[str, str] = {}

    @classmethod
    def _configured_cookies(cls) -> dict[str, str]:
        """解析用户在设置里填的站点 Cookie（形如 "k1=v1; k2=v2"）。

        这条链路是必需的：被 Cloudflare 质询时唯一可行的绕过办法，就是在浏览器
        过掉质询、把含 cf_clearance 的 Cookie 填进设置。若图片抓取不读这份配置，
        页面能抓到但封面仍然 403，表现为"有数据没有图"。
        """
        if not cls.cookie_setting_key:
            return {}

        raw = getattr(_get_app_setting(), cls.cookie_setting_key, None)
        if not raw:
            return {}

        cookies: dict[str, str] = {}
        for chunk in str(raw).split(';'):
            chunk = chunk.strip()
            if '=' not in chunk:
                continue
            key, _, value = chunk.partition('=')
            key = key.strip()
            if key:
                cookies[key] = value.strip()
        return cookies

    @classmethod
    def _cover_cookie_jar(cls) -> dict[str, str]:
        """站点内置 Cookie + 用户配置 Cookie，后者优先。

        用户配置优先是有意的：cf_clearance 之类的凭据必须能覆盖内置默认值。
        """
        jar = dict(cls.cover_cookies)
        jar.update(cls._configured_cookies())
        return jar

    def _probe_host_isolated(self, base: str) -> bool:
        """用独立 Session 探测单个域名是否可用。

        做域名探测的子类必须覆盖此方法。基类返回 False（不做探测）。

        必须自建 Session：curl_cffi 的 Session 内部包着 libcurl easy handle，
        多线程共用同一个 Session 会出问题。
        """
        return False

    def _probe_hosts_concurrently(self, candidates: list[str]) -> str | None:
        """并发探测全部候选域名，返回优先级最高的可用者。

        返回候选列表里最靠前的可用域名，而不是最先响应的那个——
        否则用户在设置里排的优先级会被网络抖动打乱。
        串行探测时每个不可达域名都要等一次超时，三个镜像就是 15 秒；
        并发后最坏情况约等于单次超时。
        """
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0] if self._probe_host_isolated(candidates[0]) else None

        reachable = set()
        try:
            with ThreadPoolExecutor(max_workers=min(len(candidates), 4)) as pool:
                futures = {pool.submit(self._probe_host_isolated, base): base for base in candidates}
                for future in as_completed(futures):
                    try:
                        if future.result():
                            reachable.add(futures[future])
                    except Exception:
                        continue
        except Exception as e:
            # 线程池不可用时退回串行，功能不能因并发失败而丢失
            logger.warning(f"并发探测{self.name}域名失败，回退串行: {e}")
            for base in candidates:
                if self._probe_host_isolated(base):
                    return base
            return None

        for base in candidates:
            if base in reachable:
                return base
        return None

    @classmethod
    def _cover_headers(cls) -> dict[str, str]:
        """构造图片请求头。Referer 用站点首页，多数图床靠它做防盗链校验。"""
        setting = _get_app_setting()
        user_agent = getattr(setting, 'user_agent', None) or _DEFAULT_USER_AGENT
        headers = {
            'User-Agent': user_agent,
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        if cls.host:
            headers['Referer'] = cls.host
        return headers

    @classmethod
    def fetch_cover(cls, url: str) -> tuple[int, bytes | None, str | None]:
        """抓取图片，返回 (状态码, 内容, content-type)。

        始终走 curl_cffi + impersonate，让所有图源（不只是 javbus/jdbstatic）
        都具备 TLS 指纹伪装能力，避免被 Cloudflare 之类的风控直接拦下。
        失败时返回的状态码交由上层决定是兜底旧缓存还是写负缓存。
        """
        setting = _get_app_setting()
        retries = max(1, int(getattr(setting, 'cover_fetch_retries', 2) or 2))
        proxy = (getattr(setting, 'proxy', None) or '').strip()
        proxies = {'http': proxy, 'https': proxy} if proxy else None

        last_status = 502
        for attempt in range(retries):
            try:
                kwargs: dict = {
                    'headers': cls._cover_headers(),
                    'timeout': 15,
                    'allow_redirects': True,
                }
                cookie_jar = cls._cover_cookie_jar()
                if cookie_jar:
                    kwargs['cookies'] = cookie_jar
                if proxies:
                    kwargs['proxies'] = proxies

                if HAS_CURL_CFFI:
                    kwargs['impersonate'] = _IMPERSONATE
                else:
                    kwargs['verify'] = False

                response = cffi_requests.get(url, **kwargs)
                last_status = response.status_code

                if response.ok and response.content:
                    content_type = response.headers.get('content-type')
                    if content_type:
                        content_type = content_type.split(';', 1)[0].strip()
                    return response.status_code, response.content, content_type

                logger.warning(f"获取封面失败: {response.status_code} - {url}")
                # 4xx 是确定性拒绝，重试无意义
                if 400 <= response.status_code < 500:
                    return response.status_code, None, None
            except Exception as e:
                logger.warning(f"获取封面异常 (尝试 {attempt + 1}/{retries}): {e} - {url}")
                last_status = 502

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

        return last_status, None, None

    @classmethod
    def get_cover(cls, url):
        """向后兼容封装：只返回图片字节。"""
        _, content, _ = cls.fetch_cover(url)
        return content
