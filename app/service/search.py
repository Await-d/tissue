"""
统一搜索服务类
支持多数据源搜索、搜索历史、搜索建议等功能
"""
import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.db import get_db
from app.db.models import History, SearchHistory, SearchStatistics, HotSearch
from app.service.base import BaseService
from app.service.video import VideoService, get_video_service
from app.schema.video import VideoList, VideoActor
from app.utils.logger import logger
from app.utils.cache import cached, get_cache_json, cache_json, clean_cache_json
from app.utils.search_cache import SearchCacheManager, get_search_cache_manager
from app.utils.search_suggestions import SearchSuggestionService, get_search_suggestion_service
from app.utils.spider.javdb import JavDBSpider
from app.utils.spider.javbus import JavBusSpider


def get_search_service(db: Session = Depends(get_db)):
    return SearchService(db=db)


class SearchService(BaseService):
    """统一搜索服务"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.video_service = VideoService(db)
        self.cache_manager = get_search_cache_manager(db)
        self.suggestion_service = get_search_suggestion_service(db)

    def unified_search(self,
                      query: str,
                      search_type: str = "all",
                      sources: List[str] = None,
                      filters: Dict[str, Any] = None,
                      page: int = 1,
                      page_size: int = 20) -> Dict[str, Any]:
        """
        统一搜索接口（带缓存）

        Args:
            query: 搜索关键词
            search_type: 搜索类型 (all, local, web, actor, num)
            sources: 数据源列表 (local, javdb, javbus)
            filters: 过滤条件
            page: 页码
            page_size: 每页大小

        Returns:
            统一格式的搜索结果
        """
        if not query.strip():
            return {
                "query": query,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "results": {
                    "local_videos": [],
                    "local_actors": [],
                    "web_videos": [],
                    "web_actors": []
                },
                "suggestions": [],
                "search_time": 0
            }

        # 生成缓存键
        cache_key = self.cache_manager.generate_cache_key(
            query=query,
            search_type=search_type,
            sources=sources,
            filters=filters,
            page=page,
            page_size=page_size
        )

        # 尝试从缓存获取
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            logger.info(f"搜索缓存命中: {query}")
            # 记录搜索历史（缓存命中也要记录）
            self._record_search_history(query, search_type)
            return cached_result

        # 执行搜索
        start_time = datetime.now()

        # 记录搜索历史
        self._record_search_history(query, search_type)

        # 默认数据源
        if sources is None:
            sources = ["local", "javdb", "javbus"]

        # 默认过滤条件
        if filters is None:
            filters = {}

        results = {
            "local_videos": [],
            "local_actors": [],
            "web_videos": [],
            "web_actors": []
        }

        total_count = 0

        # 本地搜索
        if "local" in sources and search_type in ["all", "local", "actor", "num"]:
            local_results = self._search_local(query, search_type, filters)
            results["local_videos"] = local_results.get("videos", [])
            results["local_actors"] = local_results.get("actors", [])
            total_count += len(results["local_videos"]) + len(results["local_actors"])

        # 网络搜索
        if search_type in ["all", "web", "actor", "num"]:
            for source in ["javdb", "javbus"]:
                if source in sources:
                    web_results = self._search_web(query, source, search_type, filters)
                    if web_results:
                        results["web_videos"].extend(web_results.get("videos", []))
                        results["web_actors"].extend(web_results.get("actors", []))

        total_count += len(results["web_videos"]) + len(results["web_actors"])

        # 分页处理
        results = self._paginate_results(results, page, page_size)

        # 生成搜索建议
        suggestions = self.suggestion_service.get_suggestions(query, limit=10)

        search_time = (datetime.now() - start_time).total_seconds()

        final_result = {
            "query": query,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "results": results,
            "suggestions": suggestions,
            "search_time": search_time
        }

        # 缓存结果（仅当有结果时才缓存）
        if total_count > 0:
            cache_ttl = 1800 if "web" in str(sources) else 3600  # 网络搜索缓存时间较短
            self.cache_manager.set(cache_key, final_result, cache_ttl)

        # 清理过期缓存
        self.cache_manager.cleanup_expired()

        return final_result

    def _search_local(self, query: str, search_type: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """本地搜索"""
        results = {"videos": [], "actors": []}

        try:
            # 演员搜索
            if search_type in ["all", "actor"]:
                actors = self.video_service.search_videos_by_actor(query)
                results["videos"].extend([video.model_dump() for video in actors])

                # 演员列表搜索
                all_actors = self.video_service.get_all_actors()
                matching_actors = [
                    actor for actor in all_actors
                    if query.lower() in actor.name.lower()
                ]
                results["actors"].extend([actor.model_dump() for actor in matching_actors])

            # 番号搜索
            if search_type in ["all", "num"]:
                videos = self.video_service.get_videos()
                matching_videos = [
                    video for video in videos
                    if (video.num and query.upper() in video.num.upper()) or
                       (video.title and query.lower() in video.title.lower())
                ]
                results["videos"].extend([video.model_dump() for video in matching_videos])

            # 应用过滤条件
            results = self._apply_filters(results, filters)

        except Exception as e:
            logger.error(f"本地搜索失败: {e}")

        return results

    def _search_web(self, query: str, source: str, search_type: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """网络搜索"""
        cache_key = f"web_search_{source}_{search_type}_{query}"

        # 尝试从缓存获取
        cached_result = get_cache_json('web_search', cache_key)
        if cached_result:
            return cached_result

        results = {"videos": [], "actors": []}

        try:
            # 选择爬虫
            if source == "javdb":
                spider = JavDBSpider()
            elif source == "javbus":
                spider = JavBusSpider()
            else:
                return None

            # 演员搜索
            if search_type in ["all", "actor"]:
                actors = spider.search_actor(query)
                results["actors"] = [actor.model_dump() for actor in actors]

                # 获取演员的视频
                for actor in actors[:3]:  # 限制前3个演员，避免请求过多
                    try:
                        actor_videos = spider.get_actor_videos(actor.name)
                        for video in actor_videos:
                            video_dict = video.model_dump()
                            video_dict['source'] = source
                            results["videos"].append(video_dict)
                    except Exception as e:
                        logger.warning(f"获取演员 {actor.name} 视频失败: {e}")

            # 番号/标题搜索
            if search_type in ["all", "num"]:
                try:
                    # 如果看起来像番号，直接搜索
                    if re.match(r'^[A-Za-z]+-?\d+', query):
                        video = spider.search_video(query)
                        if video:
                            video_dict = video.model_dump()
                            video_dict['source'] = source
                            results["videos"].append(video_dict)
                except Exception as e:
                    logger.warning(f"番号搜索失败: {e}")

            # 缓存结果
            cache_json('web_search', cache_key, results, expire_time=1800)  # 30分钟缓存

        except Exception as e:
            logger.error(f"网络搜索失败 {source}: {e}")

        return results

    def _apply_filters(self, results: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """应用过滤条件"""
        if not filters:
            return results

        # 过滤视频
        filtered_videos = []
        for video in results.get("videos", []):
            if self._video_matches_filters(video, filters):
                filtered_videos.append(video)
        results["videos"] = filtered_videos

        return results

    def _video_matches_filters(self, video: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """检查视频是否匹配过滤条件"""
        # HD过滤
        if filters.get("is_hd") and not video.get("is_hd"):
            return False

        # 中文过滤
        if filters.get("is_zh") and not video.get("is_zh"):
            return False

        # 无码过滤
        if filters.get("is_uncensored") and not video.get("is_uncensored"):
            return False

        # 日期范围过滤
        if filters.get("date_from") or filters.get("date_to"):
            video_date = video.get("premiered") or video.get("publish_date")
            if video_date:
                try:
                    if isinstance(video_date, str):
                        video_date = datetime.fromisoformat(video_date.replace('Z', '+00:00'))

                    if filters.get("date_from"):
                        date_from = datetime.fromisoformat(filters["date_from"])
                        if video_date < date_from:
                            return False

                    if filters.get("date_to"):
                        date_to = datetime.fromisoformat(filters["date_to"])
                        if video_date > date_to:
                            return False
                except:
                    pass

        return True

    def _paginate_results(self, results: Dict[str, Any], page: int, page_size: int) -> Dict[str, Any]:
        """分页处理"""
        # 合并所有结果进行统一分页
        all_items = []

        # 添加类型标识
        for video in results["local_videos"]:
            video["result_type"] = "local_video"
            all_items.append(video)

        for actor in results["local_actors"]:
            actor["result_type"] = "local_actor"
            all_items.append(actor)

        for video in results["web_videos"]:
            video["result_type"] = "web_video"
            all_items.append(video)

        for actor in results["web_actors"]:
            actor["result_type"] = "web_actor"
            all_items.append(actor)

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_items = all_items[start:end]

        # 重新分组
        paginated_results = {
            "local_videos": [],
            "local_actors": [],
            "web_videos": [],
            "web_actors": []
        }

        for item in paginated_items:
            result_type = item.pop("result_type")
            paginated_results[result_type].append(item)

        return paginated_results

    def _record_search_history(self, query: str, search_type: str):
        """记录搜索历史"""
        try:
            # 这里可以保存到数据库，暂时先记录日志
            logger.info(f"搜索记录: query={query}, type={search_type}, time={datetime.now()}")

            # TODO: 保存到搜索历史表
            # search_history = SearchHistory(
            #     query=query,
            #     search_type=search_type,
            #     user_ip=get_client_ip(),
            #     created_at=datetime.now()
            # )
            # search_history.add(self.db)
            # self.db.commit()

        except Exception as e:
            logger.warning(f"记录搜索历史失败: {e}")

    def get_quick_suggestions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取快速搜索建议"""
        try:
            suggestions = self.suggestion_service.get_suggestions(
                query=query,
                limit=limit,
                suggestion_types=["actor", "num", "history", "hot"]
            )
            return [{"value": s["value"], "type": s["type"]} for s in suggestions]
        except Exception as e:
            logger.warning(f"获取快速建议失败: {e}")
            return []

    def get_hot_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门搜索词"""
        # TODO: 从搜索历史统计中获取
        # 暂时返回示例数据
        return [
            {"query": "SSIS", "count": 150},
            {"query": "三上悠亚", "count": 120},
            {"query": "SSNI", "count": 100},
            {"query": "明日花", "count": 80},
            {"query": "IPX", "count": 75}
        ]

    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取搜索历史"""
        # TODO: 从数据库获取用户搜索历史
        return []

    def clear_search_history(self):
        """清除搜索历史"""
        # TODO: 清除数据库中的搜索历史
        pass

    def get_search_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        return {
            "total_searches": 0,
            "unique_queries": 0,
            "top_searches": self.get_hot_searches(5),
            "search_trends": []
        }