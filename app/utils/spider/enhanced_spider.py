"""
增强的爬虫系统
集成站点管理功能，支持故障转移、负载均衡和性能监控
"""
import time
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Type
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.schema import VideoDetail
from app.db.models.site_management import Site, SiteStatus
from app.services.site_manager import SiteManager
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException
from app.utils.spider.javdb import JavdbSpider
from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.jav321 import Jav321Spider
from app.utils.spider.dmm import DmmSpider
from app.utils.logger import logger


class SpiderRegistry:
    """爬虫注册表"""

    _spiders: Dict[str, Type[Spider]] = {
        'JavdbSpider': JavdbSpider,
        'JavbusSpider': JavbusSpider,
        'Jav321Spider': Jav321Spider,
        'DmmSpider': DmmSpider,
    }

    @classmethod
    def register_spider(cls, name: str, spider_class: Type[Spider]):
        """注册新的爬虫类"""
        cls._spiders[name] = spider_class
        logger.info(f"注册爬虫: {name}")

    @classmethod
    def get_spider(cls, name: str) -> Optional[Type[Spider]]:
        """获取爬虫类"""
        return cls._spiders.get(name)

    @classmethod
    def list_spiders(cls) -> List[str]:
        """列出所有已注册的爬虫"""
        return list(cls._spiders.keys())


class EnhancedSpiderManager:
    """增强的爬虫管理器"""

    def __init__(self, db: Session):
        self.db = db
        self.site_manager = SiteManager(db)
        self._spider_instances: Dict[int, Spider] = {}

    def get_spider_instance(self, site: Site) -> Spider:
        """
        获取或创建爬虫实例

        Args:
            site: 站点配置

        Returns:
            爬虫实例
        """
        if site.id in self._spider_instances:
            return self._spider_instances[site.id]

        spider_class = SpiderRegistry.get_spider(site.spider_class)
        if not spider_class:
            raise SpiderException(f"未找到爬虫类: {site.spider_class}")

        # 创建爬虫实例并配置
        spider = spider_class()
        spider.host = site.current_url
        spider.name = site.name

        # 应用站点特定配置
        if site.config:
            for key, value in site.config.items():
                if hasattr(spider, key):
                    setattr(spider, key, value)

        # 配置请求头
        if site.headers:
            spider.session.headers.update(site.headers)

        # 配置超时和重试
        spider.session.timeout = site.timeout
        spider.session.max_retries = site.max_retries

        self._spider_instances[site.id] = spider
        logger.info(f"创建爬虫实例: {site.name} ({site.spider_class})")

        return spider

    @asynccontextmanager
    async def spider_context(self, operation: str, required_features: Optional[List[str]] = None):
        """
        爬虫上下文管理器，自动处理站点选择和性能监控

        Args:
            operation: 操作类型
            required_features: 必需功能列表

        Yields:
            (spider, site) 元组
        """
        site = self.site_manager.select_best_site(operation, required_features)
        if not site:
            raise SpiderException(f"没有可用站点用于操作: {operation}")

        spider = self.get_spider_instance(site)
        start_time = time.time()
        success = False
        error_details = None

        try:
            logger.info(f"开始操作 '{operation}' 使用站点: {site.name}")
            yield spider, site
            success = True

        except SpiderException as e:
            error_details = {
                'type': 'spider_exception',
                'message': e.message,
                'operation': operation
            }
            logger.error(f"爬虫异常 ({site.name}): {e.message}")
            raise

        except Exception as e:
            error_details = {
                'type': 'unknown_exception',
                'message': str(e),
                'operation': operation
            }
            logger.error(f"未知异常 ({site.name}): {e}")
            raise

        finally:
            response_time = time.time() - start_time

            # 记录性能数据
            self.site_manager.record_site_performance(
                site.id, success, response_time, operation, error_details
            )

            # 添加请求间隔
            if site.rate_limit > 0:
                time.sleep(site.rate_limit)

    async def get_video_info_with_failover(
        self,
        number: str,
        max_attempts: int = 3,
        required_features: Optional[List[str]] = None
    ) -> Optional[VideoDetail]:
        """
        获取视频信息，支持故障转移

        Args:
            number: 视频番号
            max_attempts: 最大尝试次数
            required_features: 必需功能列表

        Returns:
            视频详情或None
        """
        exclude_sites = []

        for attempt in range(max_attempts):
            try:
                async with self.spider_context("get_video_info", required_features) as (spider, site):
                    if site.id in exclude_sites:
                        continue

                    logger.info(f"尝试 {attempt + 1}/{max_attempts}: 使用站点 {site.name} 获取番号 {number}")

                    video_info = spider.get_info(number)
                    if video_info:
                        logger.info(f"成功获取番号 {number} 信息，站点: {site.name}")
                        return video_info
                    else:
                        logger.warning(f"站点 {site.name} 未找到番号 {number}")
                        exclude_sites.append(site.id)

            except SpiderException as e:
                logger.warning(f"站点故障，尝试故障转移: {e.message}")
                if site.id not in exclude_sites:
                    exclude_sites.append(site.id)
                continue

            except Exception as e:
                logger.error(f"获取视频信息时发生未知错误: {e}")
                if site.id not in exclude_sites:
                    exclude_sites.append(site.id)
                continue

        logger.error(f"所有尝试都失败，无法获取番号 {number} 的信息")
        return None

    async def search_with_load_balancing(
        self,
        keyword: str,
        search_type: str = "video",
        load_balancer_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索功能，支持负载均衡

        Args:
            keyword: 搜索关键词
            search_type: 搜索类型 (video, actor)
            load_balancer_id: 负载均衡器ID

        Returns:
            搜索结果列表
        """
        if load_balancer_id:
            site = self.site_manager.get_load_balanced_site(load_balancer_id)
            if not site:
                raise SpiderException("负载均衡器未找到可用站点")
        else:
            site = self.site_manager.select_best_site("search", required_features=["search"])
            if not site:
                raise SpiderException("没有支持搜索的站点")

        async with self.spider_context("search") as (spider, _):
            if search_type == "video":
                return spider.search_videos(keyword) if hasattr(spider, 'search_videos') else []
            elif search_type == "actor":
                return spider.search_actor(keyword) if hasattr(spider, 'search_actor') else []
            else:
                raise SpiderException(f"不支持的搜索类型: {search_type}")

    async def get_downloads_with_redundancy(
        self,
        number: str,
        redundancy_level: int = 2
    ) -> List[Dict[str, Any]]:
        """
        获取下载链接，支持冗余获取

        Args:
            number: 视频番号
            redundancy_level: 冗余级别（使用多少个站点）

        Returns:
            合并的下载链接列表
        """
        sites = self.site_manager.get_available_sites(
            "download",
            required_features=["download"]
        )

        if not sites:
            raise SpiderException("没有支持下载的站点")

        # 选择指定数量的站点
        selected_sites = sites[:redundancy_level]
        all_downloads = []

        for site in selected_sites:
            try:
                async with self.spider_context("get_downloads") as (spider, _):
                    video_info = spider.get_info(number, include_downloads=True)
                    if video_info and video_info.downloads:
                        all_downloads.extend(video_info.downloads)
                        logger.info(f"从站点 {site.name} 获取到 {len(video_info.downloads)} 个下载链接")

            except Exception as e:
                logger.warning(f"从站点 {site.name} 获取下载链接失败: {e}")
                continue

        # 去重
        unique_downloads = []
        seen_urls = set()

        for download in all_downloads:
            if hasattr(download, 'url') and download.url not in seen_urls:
                unique_downloads.append(download)
                seen_urls.add(download.url)

        logger.info(f"总共获取到 {len(unique_downloads)} 个唯一下载链接")
        return unique_downloads

    async def get_actor_info_multi_source(
        self,
        actor_name: str,
        merge_sources: bool = True
    ) -> Dict[str, Any]:
        """
        从多个站点获取演员信息

        Args:
            actor_name: 演员名称
            merge_sources: 是否合并多个数据源

        Returns:
            演员信息字典
        """
        sites = self.site_manager.get_available_sites(
            "actor_info",
            required_features=["actor_info"]
        )

        if not sites:
            raise SpiderException("没有支持演员信息的站点")

        actor_data = {}

        for site in sites:
            try:
                async with self.spider_context("actor_info") as (spider, _):
                    if hasattr(spider, 'get_actor_info'):
                        info = spider.get_actor_info(actor_name)
                        if info:
                            if merge_sources:
                                # 合并数据
                                for key, value in info.items():
                                    if key not in actor_data or not actor_data[key]:
                                        actor_data[key] = value
                                    elif isinstance(value, list):
                                        # 合并列表数据
                                        existing = actor_data.get(key, [])
                                        if isinstance(existing, list):
                                            actor_data[key] = list(set(existing + value))
                            else:
                                # 保持分离的数据源
                                actor_data[site.name] = info

                            logger.info(f"从站点 {site.name} 获取到演员 {actor_name} 的信息")

            except Exception as e:
                logger.warning(f"从站点 {site.name} 获取演员信息失败: {e}")
                continue

        return actor_data

    async def get_trending_videos_aggregated(
        self,
        time_range: str = "week",
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        聚合多个站点的热门视频

        Args:
            time_range: 时间范围 (day, week, month)
            max_results: 最大结果数

        Returns:
            聚合的热门视频列表
        """
        sites = self.site_manager.get_available_sites(
            "trending",
            required_features=["ranking"]
        )

        if not sites:
            logger.warning("没有支持排行榜的站点")
            return []

        all_videos = []

        for site in sites:
            try:
                async with self.spider_context("trending") as (spider, _):
                    if hasattr(spider, 'get_trending_videos'):
                        videos = spider.get_trending_videos(time_range=time_range)
                        if videos:
                            # 为每个视频添加来源信息
                            for video in videos:
                                video['source_site'] = site.name
                                video['source_url'] = site.current_url
                            all_videos.extend(videos)
                            logger.info(f"从站点 {site.name} 获取到 {len(videos)} 个热门视频")

            except Exception as e:
                logger.warning(f"从站点 {site.name} 获取热门视频失败: {e}")
                continue

        # 去重并限制结果数
        unique_videos = []
        seen_numbers = set()

        for video in all_videos:
            video_number = video.get('number') or video.get('code')
            if video_number and video_number not in seen_numbers:
                unique_videos.append(video)
                seen_numbers.add(video_number)

                if len(unique_videos) >= max_results:
                    break

        logger.info(f"聚合获取到 {len(unique_videos)} 个唯一热门视频")
        return unique_videos

    async def health_check_all_spiders(self) -> Dict[str, Any]:
        """
        检查所有爬虫的健康状态

        Returns:
            健康检查结果
        """
        health_results = await self.site_manager.health_check_all_sites()

        spider_health = {}
        for site_id, is_healthy in health_results.items():
            site = self.db.query(Site).filter(Site.id == site_id).first()
            if site:
                spider_health[site.name] = {
                    'site_id': site_id,
                    'spider_class': site.spider_class,
                    'is_healthy': is_healthy,
                    'status': site.status.value,
                    'url': site.current_url
                }

        total_sites = len(spider_health)
        healthy_sites = sum(1 for info in spider_health.values() if info['is_healthy'])

        return {
            'total_sites': total_sites,
            'healthy_sites': healthy_sites,
            'unhealthy_sites': total_sites - healthy_sites,
            'health_rate': (healthy_sites / total_sites * 100) if total_sites > 0 else 0,
            'sites': spider_health,
            'checked_at': datetime.utcnow().isoformat()
        }


# 向后兼容的全局函数
def get_video_info_enhanced(number: str, db: Session) -> Optional[VideoDetail]:
    """
    增强的视频信息获取函数（向后兼容）

    Args:
        number: 视频番号
        db: 数据库会话

    Returns:
        视频详情或None
    """
    manager = EnhancedSpiderManager(db)
    return asyncio.run(manager.get_video_info_with_failover(number))


def get_video_downloads_enhanced(number: str, db: Session) -> List[Dict[str, Any]]:
    """
    增强的视频下载获取函数（向后兼容）

    Args:
        number: 视频番号
        db: 数据库会话

    Returns:
        下载链接列表
    """
    manager = EnhancedSpiderManager(db)
    return asyncio.run(manager.get_downloads_with_redundancy(number))