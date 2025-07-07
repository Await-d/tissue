"""
视频收集器 - 聚合各个爬虫网站的视频数据
"""
import time
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from random import randint

from app.utils import spider
from app.utils.logger import logger


class VideoCollector:
    """视频收集器"""
    
    def __init__(self):
        self.spiders = [
            spider.JavdbSpider(),
            # 可以添加其他爬虫
        ]
    
    def get_trending_videos(self, time_range: str = "week", max_pages: int = 3) -> List[Dict[str, Any]]:
        """获取热门视频"""
        all_videos = []
        
        for spider_instance in self.spiders:
            try:
                logger.info(f"从 {spider_instance.name} 获取热门视频")
                
                for page in range(1, max_pages + 1):
                    videos = spider_instance.get_trending_videos(page=page, time_range=time_range)
                    
                    if not videos:
                        break
                    
                    # 为每个视频添加额外信息
                    for video in videos:
                        video['source_website'] = spider_instance.name
                        video['collected_at'] = datetime.now()
                        
                        # 尝试获取详细信息（评论数等）
                        try:
                            if video.get('url'):
                                comments_count = spider_instance.get_comments_count(video['url'])
                                video['comments_count'] = comments_count
                        except Exception as e:
                            logger.warning(f"获取评论数失败: {str(e)}")
                            video['comments_count'] = 0
                    
                    all_videos.extend(videos)
                    
                    # 添加延迟避免过于频繁的请求
                    time.sleep(randint(2, 5))
                
            except Exception as e:
                logger.error(f"从 {spider_instance.name} 获取热门视频时出错: {str(e)}")
                traceback.print_exc()
        
        # 去重（根据番号）
        unique_videos = self._deduplicate_videos(all_videos)
        
        # 按评分排序
        unique_videos.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        logger.info(f"收集到 {len(unique_videos)} 个独特的热门视频")
        return unique_videos
    
    def get_latest_videos(self, date_range: int = 7, max_pages: int = 5) -> List[Dict[str, Any]]:
        """获取最新视频"""
        all_videos = []
        
        for spider_instance in self.spiders:
            try:
                logger.info(f"从 {spider_instance.name} 获取最新视频")
                
                for page in range(1, max_pages + 1):
                    videos = spider_instance.get_latest_videos(page=page, date_range=date_range)
                    
                    if not videos:
                        break
                    
                    # 为每个视频添加额外信息
                    for video in videos:
                        video['source_website'] = spider_instance.name
                        video['collected_at'] = datetime.now()
                        
                        # 尝试获取详细信息
                        try:
                            if video.get('url'):
                                comments_count = spider_instance.get_comments_count(video['url'])
                                video['comments_count'] = comments_count
                        except Exception as e:
                            logger.warning(f"获取评论数失败: {str(e)}")
                            video['comments_count'] = 0
                    
                    all_videos.extend(videos)
                    
                    # 添加延迟
                    time.sleep(randint(2, 5))
                
            except Exception as e:
                logger.error(f"从 {spider_instance.name} 获取最新视频时出错: {str(e)}")
                traceback.print_exc()
        
        # 去重
        unique_videos = self._deduplicate_videos(all_videos)
        
        # 按发布日期排序
        unique_videos.sort(key=lambda x: x.get('publish_date') or datetime.min.date(), reverse=True)
        
        logger.info(f"收集到 {len(unique_videos)} 个独特的最新视频")
        return unique_videos
    
    def get_videos_by_criteria(self, 
                              min_rating: Optional[float] = None,
                              min_comments: Optional[int] = None,
                              time_range_days: int = 7,
                              is_hd: bool = False,
                              is_zh: bool = False,
                              is_uncensored: bool = False) -> List[Dict[str, Any]]:
        """根据条件获取视频"""
        
        # 首先获取最新视频
        latest_videos = self.get_latest_videos(date_range=time_range_days)
        
        # 应用筛选条件
        filtered_videos = []
        
        for video in latest_videos:
            # 检查评分条件
            if min_rating and (not video.get('rating') or video['rating'] < min_rating):
                continue
            
            # 检查评论数条件
            if min_comments and (not video.get('comments_count') or video['comments_count'] < min_comments):
                continue
            
            # 检查其他条件（这些需要获取详细信息）
            if is_hd or is_zh or is_uncensored:
                try:
                    # 获取视频详细信息
                    video_detail = self._get_video_detail(video['num'])
                    if not video_detail:
                        continue
                    
                    if is_hd and not video_detail.get('is_hd', False):
                        continue
                    
                    if is_zh and not video_detail.get('is_zh', False):
                        continue
                    
                    if is_uncensored and not video_detail.get('is_uncensored', False):
                        continue
                    
                    # 合并详细信息
                    video.update({
                        'is_hd': video_detail.get('is_hd', False),
                        'is_zh': video_detail.get('is_zh', False),
                        'is_uncensored': video_detail.get('is_uncensored', False),
                        'actors': video_detail.get('actors', []),
                        'tags': video_detail.get('tags', []),
                    })
                    
                except Exception as e:
                    logger.warning(f"获取视频 {video['num']} 详细信息失败: {str(e)}")
                    continue
            
            filtered_videos.append(video)
        
        logger.info(f"筛选后得到 {len(filtered_videos)} 个符合条件的视频")
        return filtered_videos
    
    def _deduplicate_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重视频列表（根据番号）"""
        seen_nums = set()
        unique_videos = []
        
        for video in videos:
            num = video.get('num')
            if num and num not in seen_nums:
                seen_nums.add(num)
                unique_videos.append(video)
        
        return unique_videos
    
    def _get_video_detail(self, num: str) -> Optional[Dict[str, Any]]:
        """获取视频详细信息"""
        try:
            # 使用现有的spider.get_video方法
            video_detail = spider.get_video(num)
            if video_detail:
                return {
                    'is_hd': getattr(video_detail, 'is_hd', False),
                    'is_zh': getattr(video_detail, 'is_zh', False),  
                    'is_uncensored': getattr(video_detail, 'is_uncensored', False),
                    'actors': getattr(video_detail, 'actors', []),
                    'tags': getattr(video_detail, 'tags', []),
                    'downloads': getattr(video_detail, 'downloads', []),
                }
            return None
        except Exception as e:
            logger.error(f"获取视频 {num} 详细信息时出错: {str(e)}")
            return None


# 全局实例
video_collector = VideoCollector()