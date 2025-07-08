"""
视频收集器 - 聚合各个爬虫网站的视频数据
"""
import time
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from random import randint

from app.utils import spider
from app.utils.async_logger import get_logger

# 获取适合智能下载的日志记录器
logger = get_logger()


class VideoCollector:
    """视频收集器"""
    
    def __init__(self):
        self.spiders = [
            spider.JavdbSpider(),
            # 可以添加其他爬虫
        ]
        # 添加缓存存储
        self._cache = {}
        # 缓存有效期（小时）
        self.cache_ttl_hours = 24
    
    def get_trending_videos(self, time_range: str = "week", max_pages: int = 3) -> List[Dict[str, Any]]:
        """获取热门视频"""
        # 检查缓存
        cache_key = f"trending_{time_range}_{max_pages}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"从缓存获取热门视频数据，共 {len(cached_data)} 个")
            return cached_data
        
        all_videos = []
        
        for spider_instance in self.spiders:
            try:
                logger.info(f"从 {spider_instance.name} 获取热门视频")
                
                for page in range(1, max_pages + 1):
                    videos = spider_instance.get_trending_videos(page, time_range)
                    
                    if not videos:
                        break
                    
                    all_videos.extend(videos)
            except Exception as e:
                logger.error(f"获取热门视频出错: {str(e)}")
                logger.debug(traceback.format_exc())
        
        # 保存到缓存
        self._save_to_cache(cache_key, all_videos)
        return all_videos
    
    def get_latest_videos(self, max_pages: int = 3, days: int = 7) -> List[Dict[str, Any]]:
        """获取最新视频"""
        # 检查缓存
        cache_key = f"latest_{max_pages}_{days}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"从缓存获取最新视频数据，共 {len(cached_data)} 个")
            return cached_data
            
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_videos = []
        unique_nums = set()
        
        for spider_instance in self.spiders:
            try:
                for page in range(1, max_pages + 1):
                    videos = spider_instance.get_latest_videos(page)
                    
                    if not videos:
                        break
                    
                    # 检查发布日期
                    for video in videos:
                        try:
                            # 如果没有日期或者日期格式不对，默认添加
                            if 'release_date' not in video or not video['release_date']:
                                all_videos.append(video)
                                unique_nums.add(video['num'])
                                continue
                            
                            # 解析日期
                            release_date = datetime.strptime(video['release_date'], '%Y-%m-%d')
                            
                            # 检查日期范围
                            if start_date <= release_date <= end_date:
                                # 避免重复
                                if video['num'] not in unique_nums:
                                    all_videos.append(video)
                                    unique_nums.add(video['num'])
                        except Exception as e:
                            logger.error(f"解析视频日期出错: {str(e)}, 视频: {video.get('num')}")
                            # 出错时默认添加
                            if video['num'] not in unique_nums:
                                all_videos.append(video)
                                unique_nums.add(video['num'])
            except Exception as e:
                logger.error(f"获取最新视频出错: {str(e)}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"收集到 {len(all_videos)} 个独特的最新视频")
        
        # 保存到缓存
        self._save_to_cache(cache_key, all_videos)
        return all_videos
    
    def get_videos_by_criteria(self, 
                          min_rating: Optional[float] = None, 
                          min_comments: Optional[int] = None,
                          is_uncensored: Optional[bool] = None,
                          is_hd: Optional[bool] = None,
                          is_zh: Optional[bool] = None,
                          required_actor_id: Optional[str] = None,
                          exclude_actor_id: Optional[str] = None,
                          required_tags: Optional[List[str]] = None,
                          exclude_tags: Optional[List[str]] = None,
                          max_pages: int = 3,
                          days: int = 7) -> List[Dict[str, Any]]:
        """根据条件筛选视频"""
        # 构建缓存键
        cache_params = f"{min_rating}_{min_comments}_{is_uncensored}_{is_hd}_{is_zh}_{required_actor_id}_{exclude_actor_id}_{required_tags}_{exclude_tags}_{max_pages}_{days}"
        cache_key = f"criteria_{hash(cache_params)}"
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"从缓存获取筛选视频数据，共 {len(cached_data)} 个")
            return cached_data
        
        # 获取最新视频
        videos = self.get_latest_videos(max_pages, days)
        filtered_videos = []
        
        # 进行基础筛选
        for video in videos:
            if min_rating and video.get('rating', 0) < min_rating:
                # 减少调试日志输出
                pass
                continue
                
            if min_comments and video.get('comments', 0) < min_comments:
                # 减少调试日志输出
                pass
                continue
            
            # 获取视频详细信息
            video_detail = self._get_video_detail(video['num'])
            
            # 如果获取详情失败，标记并暂时保留
            if not video_detail:
                video['detail_missing'] = True
                filtered_videos.append(video)
                continue
                
            # 合并视频详情到视频信息中
            video.update(video_detail)
            
            # 根据详细信息筛选
            if is_uncensored is not None and video.get('is_uncensored', False) != is_uncensored:
                # 减少调试日志输出
            pass
                continue
                
            if is_hd is not None and video.get('is_hd', False) != is_hd:
                # 减少调试日志输出
                pass
                continue
                
            if is_zh is not None and video.get('is_zh', False) != is_zh:
                # 减少调试日志输出
                pass
                continue
            
            # 检查演员
            if required_actor_id:
                actors = video.get('actors', [])
                actor_ids = [a.get('id') for a in actors]
                if required_actor_id not in actor_ids:
                    # 减少调试日志输出
                    pass
                    continue
            
            if exclude_actor_id:
                actors = video.get('actors', [])
                actor_ids = [a.get('id') for a in actors]
                if exclude_actor_id in actor_ids:
                    # 减少调试日志输出
                    pass
                    continue
            
            # 检查标签
            if required_tags:
                tags = video.get('tags', [])
                tag_names = [t.get('name').lower() for t in tags]
                if not all(tag.lower() in tag_names for tag in required_tags):
                    # 减少调试日志输出
                    pass
                    continue
            
            if exclude_tags:
                tags = video.get('tags', [])
                tag_names = [t.get('name').lower() for t in tags]
                if any(tag.lower() in tag_names for tag in exclude_tags):
                    # 减少调试日志输出
                    pass
                    continue
            
            # 通过所有筛选条件，添加到结果列表
            filtered_videos.append(video)
        
        logger.info(f"筛选后得到 {len(filtered_videos)} 个符合条件的视频")
        
        # 保存到缓存
        self._save_to_cache(cache_key, filtered_videos)
        return filtered_videos
    
    def _get_video_detail(self, num: str) -> Optional[Dict[str, Any]]:
        """获取视频详细信息"""
        # 检查缓存
        cache_key = f"detail_{num}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            # 减少调试日志输出
            pass
            return cached_data
            
        try:
            # 添加随机延迟，避免频繁请求
            delay = randint(5, 10)
            # 减少日志输出，只记录关键信息
            if delay > 8:  # 只在延迟较长时记录
                logger.info(f"获取视频 {num} 详情前等待 {delay} 秒...")
            time.sleep(delay)
            
            # 使用现有的spider.get_video方法
            video_detail = spider.get_video(num)
            if video_detail:
                detail_data = {
                    'is_hd': getattr(video_detail, 'is_hd', False),
                    'is_zh': getattr(video_detail, 'is_zh', False),  
                    'is_uncensored': getattr(video_detail, 'is_uncensored', False),
                    'actors': getattr(video_detail, 'actors', []),
                    'tags': getattr(video_detail, 'tags', []),
                    'downloads': getattr(video_detail, 'downloads', []),
                }
                # 保存到缓存
                self._save_to_cache(cache_key, detail_data)
                return detail_data
            return None
        except Exception as e:
            logger.error(f"获取视频详情出错: {str(e)}, 视频: {num}")
            logger.debug(traceback.format_exc())
            return None
            
    def _save_to_cache(self, key: str, data: Any) -> None:
        """保存数据到缓存"""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        # 减少调试日志输出
        pass
        
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据，如果有效返回数据，否则返回None"""
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        cache_time = cache_entry['timestamp']
        now = datetime.now()
        
        # 检查缓存是否过期
        if now - cache_time > timedelta(hours=self.cache_ttl_hours):
            # 减少调试日志输出
            pass
            return None
            
        return cache_entry['data']


# 全局实例
video_collector = VideoCollector()