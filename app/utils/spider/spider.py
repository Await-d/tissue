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
import requests
import ssl
import time
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from app.schema import Setting

# 禁用SSL警告
disable_warnings(InsecureRequestWarning)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('spider')


class Session(requests.Session):

    def __init__(self, timeout: int = 10):
        super().__init__()
        self.timeout = timeout
        
        # 禁用SSL验证以避免证书问题
        self.verify = False

    def request(self, *args, **kwargs):
        method = args[0] if args else kwargs.get('method')
        url = args[1] if len(args) > 1 else kwargs.get('url')
        logger.info(f"请求: {method} {url}")
        
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', False)  # 禁用SSL验证
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = super(Session, self).request(*args, **kwargs)
                logger.info(f"响应: {response.status_code} - {url}")
                if response.status_code != 200:
                    logger.error(f"请求失败: {response.status_code} - {url}")
                    logger.error(f"响应内容: {response.text[:200]}")
                return response
            except (requests.exceptions.SSLError, 
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
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

    def __init__(self):
        self.setting = Setting().app
        self.session = Session()
        user_agent = getattr(self.setting, 'user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        self.session.headers = {'User-Agent': user_agent, 'Referer': self.host}
        self.session.timeout = (5, self.session.timeout)
        logger.info(f"初始化爬虫: {self.name}, 域名: {self.host}")

    @abstractmethod
    def get_info(self, num: str, url: str = None, include_downloads: bool = False, include_previews: bool = False):
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

    @classmethod
    def get_cover(cls, url):
        logger.info(f"获取封面: {url}")
        try:
            response = requests.get(url, headers={'Referer': cls.host}, verify=False, timeout=10)
            if response.ok:
                return response.content
            else:
                logger.error(f"获取封面失败: {response.status_code} - {url}")
                return None
        except Exception as e:
            logger.error(f"获取封面异常: {e} - {url}")
            return None
