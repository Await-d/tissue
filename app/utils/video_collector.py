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

    def get_ranking_videos(self, video_type: str = 'censored', cycle: str = 'daily', max_pages: int = 3) -> List[Dict[str, Any]]:
        """获取排行榜视频，包含评分和评论信息，优化智能下载规则性能"""
        # 检查缓存
        cache_key = f"ranking_{video_type}_{cycle}_{max_pages}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"从缓存获取排行榜视频数据，共 {len(cached_data)} 个")
            return cached_data
        
        all_videos = []
        unique_nums = set()
        
        for spider_instance in self.spiders:
            try:
                # 使用新的获取排行榜方法，直接包含评分和评论信息
                if hasattr(spider_instance, 'get_ranking_with_details'):
                    videos = spider_instance.get_ranking_with_details(video_type, cycle, max_pages)
                    
                    for video in videos:
                        # 避免重复
                        if video['num'] not in unique_nums:
                            all_videos.append(video)
                            unique_nums.add(video['num'])
                else:
                    # 降级到原有方法
                    logger.warning(f"爬虫 {spider_instance.name} 不支持get_ranking_with_details方法，使用降级方案")
                    videos = spider_instance.get_latest_videos(max_pages)
                    for video in videos:
                        if video['num'] not in unique_nums:
                            all_videos.append(video)
                            unique_nums.add(video['num'])
                    
            except Exception as e:
                logger.error(f"获取排行榜视频出错: {str(e)}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"收集到 {len(all_videos)} 个独特的排行榜视频，包含评分和评论信息")
        
        # 输出前5个视频的详细信息用于调试
        for i, video in enumerate(all_videos[:5]):
            logger.info(f"排行榜视频 {i+1}: {video.get('num')} - 评分: {video.get('rating')} - 评论: {video.get('comments')} - 评论数: {video.get('comments_count')}")
        
        # 统计有效评分和评论数据
        valid_ratings = [v for v in all_videos if v.get('rating') is not None]
        valid_comments = [v for v in all_videos if v.get('comments') is not None and v.get('comments') > 0]
        valid_comments_count = [v for v in all_videos if v.get('comments_count') is not None and v.get('comments_count') > 0]
        logger.info(f"有效评分数据: {len(valid_ratings)}/{len(all_videos)}, 有效评论数据: {len(valid_comments)}/{len(all_videos)}, 有效评论数数据: {len(valid_comments_count)}/{len(all_videos)}")
        
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
        """根据条件筛选视频，优化性能：优先使用排行榜数据避免单独访问详情页"""
        # 构建缓存键
        cache_params = f"{min_rating}_{min_comments}_{is_uncensored}_{is_hd}_{is_zh}_{required_actor_id}_{exclude_actor_id}_{required_tags}_{exclude_tags}_{max_pages}_{days}"
        cache_key = f"criteria_{hash(cache_params)}"
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"从缓存获取筛选视频数据，共 {len(cached_data)} 个")
            return cached_data
        
        # 优化策略：优先使用排行榜数据（已包含评分、评论、质量标签）
        filtered_videos = []
        
        # 1. 先从排行榜获取有评分和评论的视频（有码和无码）
        logger.info("开始从排行榜获取视频数据，避免访问详情页...")
        
        # 获取有码排行榜
        if is_uncensored is None or is_uncensored is False:
            censored_videos = self.get_ranking_videos('censored', 'daily', max_pages)
            filtered_videos.extend(censored_videos)
        
        # 获取无码排行榜
        if is_uncensored is None or is_uncensored is True:
            uncensored_videos = self.get_ranking_videos('uncensored', 'daily', max_pages)
            filtered_videos.extend(uncensored_videos)
        
        logger.info(f"从排行榜获取到 {len(filtered_videos)} 个视频，开始基础筛选...")
        
        # 2. 对排行榜视频进行基础筛选（这些视频已经包含评分和评论信息）
        basic_filtered = []
        for video in filtered_videos:
            # 添加详细的日志输出，显示每个视频的评分和评论数据
            video_rating = video.get('rating')
            video_comments = video.get('comments', 0)
            video_comments_count = video.get('comments_count', 0)
            logger.info(f"视频 {video.get('num')} - 评分: {video_rating} (类型: {type(video_rating)}), 评论: {video_comments} (类型: {type(video_comments)}), 评论数: {video_comments_count} (类型: {type(video_comments_count)})")
            
            # 尝试从多个字段获取评论数
            if video_comments == 0 and video_comments_count != 0:
                video_comments = video_comments_count
                logger.info(f"视频 {video.get('num')} 使用 comments_count 字段: {video_comments}")
            
            # 评分筛选
            if min_rating is not None and min_rating > 0 and video_rating is not None:
                try:
                    rating_float = float(video_rating)
                    min_rating_float = float(min_rating)
                    logger.info(f"视频 {video.get('num')} 评分比较: {rating_float} >= {min_rating_float} ? {rating_float >= min_rating_float}")
                    if rating_float < min_rating_float:
                        logger.info(f"视频 {video.get('num')} 评分 {rating_float} 低于要求 {min_rating_float}，跳过")
                        continue
                except (ValueError, TypeError) as e:
                    logger.warning(f"视频 {video.get('num')} 评分转换失败: {video_rating} (类型: {type(video_rating)}), 错误: {e}")
                    continue
                
            # 评论数筛选
            if min_comments is not None and min_comments > 0 and video_comments is not None:
                try:
                    comments_int = int(video_comments)
                    min_comments_int = int(min_comments)
                    logger.info(f"视频 {video.get('num')} 评论数比较: {comments_int} >= {min_comments_int} ? {comments_int >= min_comments_int}")
                    if comments_int < min_comments_int:
                        logger.info(f"视频 {video.get('num')} 评论数 {comments_int} 低于要求 {min_comments_int}，跳过")
                        continue
                except (ValueError, TypeError) as e:
                    logger.warning(f"视频 {video.get('num')} 评论数转换失败: {video_comments} (类型: {type(video_comments)}), 错误: {e}")
                    continue
            elif min_comments is not None and min_comments > 0 and video_comments == 0:
                logger.info(f"视频 {video.get('num')} 评论数为0，低于要求 {min_comments}，跳过")
                continue
            
            # 质量要求筛选（排行榜数据已包含这些信息）
            if is_uncensored is not None and video.get('is_uncensored', False) != is_uncensored:
                continue
                
            if is_hd is not None and video.get('is_hd', False) != is_hd:
                continue
                
            if is_zh is not None and video.get('is_zh', False) != is_zh:
                continue
            
            basic_filtered.append(video)
        
        logger.info(f"基础筛选后剩余 {len(basic_filtered)} 个视频")
        
        # 3. 对于需要演员或标签信息的筛选，才访问详情页（仅在必要时）
        final_filtered = []
        need_detail_check = bool(required_actor_id or exclude_actor_id or required_tags or exclude_tags)
        
        for video in basic_filtered:
            if need_detail_check:
                # 只有在需要演员或标签信息时才获取详情
                video_detail = self._get_video_detail(video['num'])
                
                if not video_detail:
                    # 如果获取详情失败，但已经通过基础筛选，仍然保留
                    video['detail_missing'] = True
                    final_filtered.append(video)
                    continue
                
                # 合并详情信息
                video.update(video_detail)
                
                # 检查演员
                if required_actor_id:
                    actors = video.get('actors', [])
                    actor_ids = [a.get('id') for a in actors]
                    if required_actor_id not in actor_ids:
                        continue
                
                if exclude_actor_id:
                    actors = video.get('actors', [])
                    actor_ids = [a.get('id') for a in actors]
                    if exclude_actor_id in actor_ids:
                        continue
                
                # 检查标签
                if required_tags:
                    tags = video.get('tags', [])
                    tag_names = [t.get('name').lower() for t in tags]
                    if not all(tag.lower() in tag_names for tag in required_tags):
                        continue
                
                if exclude_tags:
                    tags = video.get('tags', [])
                    tag_names = [t.get('name').lower() for t in tags]
                    if any(tag.lower() in tag_names for tag in exclude_tags):
                        continue
            
            # 通过所有筛选条件
            final_filtered.append(video)
        
        # 4. 如果排行榜数据不足，补充最新视频数据
        if len(final_filtered) < 20:  # 如果结果太少，补充一些最新视频
            logger.info(f"排行榜筛选结果较少({len(final_filtered)}个)，补充最新视频数据...")
            
            latest_videos = self.get_latest_videos(max_pages, days)
            existing_nums = {v['num'] for v in final_filtered}
            
            for video in latest_videos:
                if video['num'] in existing_nums:
                    continue  # 避免重复
                
                # 对补充的视频进行同样的筛选逻辑
                video_rating = video.get('rating')
                if min_rating is not None and min_rating > 0 and video_rating is not None and float(video_rating) < float(min_rating):
                    continue
                video_comments = video.get('comments', 0)
                if min_comments is not None and min_comments > 0 and video_comments is not None and int(video_comments) < int(min_comments):
                    continue
                
                # 需要详情信息的筛选
                if need_detail_check or is_uncensored is not None or is_hd is not None or is_zh is not None:
                    video_detail = self._get_video_detail(video['num'])
                    if video_detail:
                        video.update(video_detail)
                        
                        if is_uncensored is not None and video.get('is_uncensored', False) != is_uncensored:
                            continue
                        if is_hd is not None and video.get('is_hd', False) != is_hd:
                            continue
                        if is_zh is not None and video.get('is_zh', False) != is_zh:
                            continue
                        
                        # 演员和标签检查（同上）
                        if required_actor_id:
                            actors = video.get('actors', [])
                            actor_ids = [a.get('id') for a in actors]
                            if required_actor_id not in actor_ids:
                                continue
                        
                        if exclude_actor_id:
                            actors = video.get('actors', [])
                            actor_ids = [a.get('id') for a in actors]
                            if exclude_actor_id in actor_ids:
                                continue
                        
                        if required_tags:
                            tags = video.get('tags', [])
                            tag_names = [t.get('name').lower() for t in tags]
                            if not all(tag.lower() in tag_names for tag in required_tags):
                                continue
                        
                        if exclude_tags:
                            tags = video.get('tags', [])
                            tag_names = [t.get('name').lower() for t in tags]
                            if any(tag.lower() in tag_names for tag in exclude_tags):
                                continue
                    else:
                        video['detail_missing'] = True
                
                final_filtered.append(video)
                
                # 限制补充数量
                if len(final_filtered) >= 50:
                    break
        
        logger.info(f"最终筛选得到 {len(final_filtered)} 个符合条件的视频")
        
        # 保存到缓存
        self._save_to_cache(cache_key, final_filtered)
        return final_filtered
    
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