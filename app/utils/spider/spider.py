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

from app.schema import Setting

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('spider')


class Session(requests.Session):

    def __init__(self, timeout: int = 10):
        super().__init__()
        self.timeout = timeout

    def request(self, *args, **kwargs):
        method = args[0] if args else kwargs.get('method')
        url = args[1] if len(args) > 1 else kwargs.get('url')
        logger.info(f"请求: {method} {url}")
        
        kwargs.setdefault('timeout', self.timeout)
        response = super(Session, self).request(*args, **kwargs)
        
        logger.info(f"响应: {response.status_code} - {url}")
        if response.status_code != 200:
            logger.error(f"请求失败: {response.status_code} - {url}")
            logger.error(f"响应内容: {response.text[:200]}")
        
        return response


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

    @classmethod
    def get_cover(cls, url):
        logger.info(f"获取封面: {url}")
        response = requests.get(url, headers={'Referer': cls.host})
        if response.ok:
            return response.content
        else:
            logger.error(f"获取封面失败: {response.status_code} - {url}")
            return None
