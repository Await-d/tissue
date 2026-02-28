"""
视频缓存服务 - 管理预抓取的视频数据
"""

import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from app.db.models.video_cache import VideoCache
from app.schema.setting import Setting
from app.service.base import BaseService
from app.utils import spider
from app.utils.async_logger import get_logger

logger = get_logger()


class VideoCacheService(BaseService):
    """视频缓存服务 - 提供统一的视频数据访问接口"""

    def fetch_and_cache_rankings(
        self,
        sources: List[str] = None,
        video_types: List[str] = None,
        cycles: List[str] = None,
        max_pages: int = 3,
        apply_delay: bool = True,
    ) -> Dict[str, Any]:
        """
        从多个网站抓取排行榜数据并缓存到数据库

        Args:
            sources: 数据源列表，默认 ['JavDB', 'JavBus']
            video_types: 视频类型列表，默认 ['censored', 'uncensored']
            cycles: 周期列表，默认 ['daily', 'weekly', 'monthly']
            max_pages: 每个榜单抓取的最大页数

        Returns:
            统计信息字典
        """
        if sources is None:
            sources = ["JavDB"]  # 目前只支持 JavDB
        if video_types is None:
            video_types = ["censored", "uncensored"]
        if cycles is None:
            cycles = ["daily", "weekly", "monthly"]

        stats = {"total_fetched": 0, "total_new": 0, "total_updated": 0, "errors": []}

        for source in sources:
            for video_type in video_types:
                for cycle in cycles:
                    try:
                        count = self._fetch_and_cache_single_ranking(
                            source, video_type, cycle, max_pages, apply_delay
                        )
                        stats["total_fetched"] += count["fetched"]
                        stats["total_new"] += count["new"]
                        stats["total_updated"] += count["updated"]

                        logger.info(
                            f"缓存完成: {source} {video_type} {cycle} - "
                            f"抓取{count['fetched']}个, 新增{count['new']}个, 更新{count['updated']}个"
                        )
                    except Exception as e:
                        error_msg = f"抓取失败 {source} {video_type} {cycle}: {str(e)}"
                        logger.error(error_msg)
                        logger.debug(traceback.format_exc())
                        stats["errors"].append(error_msg)

        logger.info(
            f"视频缓存更新完成: 总计抓取{stats['total_fetched']}个, "
            f"新增{stats['total_new']}个, 更新{stats['total_updated']}个"
        )

        return stats

    def _fetch_and_cache_single_ranking(
        self,
        source: str,
        video_type: str,
        cycle: str,
        max_pages: int,
        apply_delay: bool = True,
    ) -> Dict[str, int]:
        """抓取单个排行榜并缓存"""
        spider_instance = self._get_spider(source)
        if not spider_instance:
            raise ValueError(f"不支持的数据源: {source}")

        # 获取排行榜数据（包含详细信息）
        if hasattr(spider_instance, "get_ranking_with_details"):
            videos = spider_instance.get_ranking_with_details(
                video_type, cycle, max_pages, apply_delay=apply_delay
            )
        else:
            # 降级方案：获取基础排行榜
            videos = spider_instance.get_ranking(video_type, cycle)
            if not isinstance(videos, list):
                videos = []

        new_count = 0
        updated_count = 0

        for idx, video in enumerate(videos, 1):
            try:
                # 检查是否已存在
                existing = (
                    self.db.query(VideoCache)
                    .filter(
                        and_(
                            VideoCache.num == video.get("num"),
                            VideoCache.source == source,
                            VideoCache.video_type == video_type,
                            VideoCache.cycle == cycle,
                        )
                    )
                    .first()
                )

                if existing:
                    # 更新现有记录
                    self._update_video_cache(existing, video, idx)
                    updated_count += 1
                else:
                    # 创建新记录
                    cache_entry = self._create_video_cache(
                        video, source, video_type, cycle, idx
                    )
                    self.db.add(cache_entry)
                    new_count += 1

            except Exception as e:
                logger.error(f"缓存视频失败 {video.get('num')}: {str(e)}")
                logger.debug(traceback.format_exc())

        self.db.commit()

        return {"fetched": len(videos), "new": new_count, "updated": updated_count}

    def _create_video_cache(
        self, video: Dict, source: str, video_type: str, cycle: str, rank_position: int
    ) -> VideoCache:
        """创建视频缓存记录"""
        # 数据验证
        if not video.get("num"):
            raise ValueError(f"视频番号不能为空: {video}")

        # 评分验证
        rating = video.get("rating")
        if rating is not None:
            try:
                rating_float = float(rating)
                if not (0 <= rating_float <= 5):
                    logger.warning(
                        f"视频 {video.get('num')} 评分异常: {rating}，将设置为None"
                    )
                    rating = None
            except (ValueError, TypeError):
                logger.warning(
                    f"视频 {video.get('num')} 评分格式错误: {rating}，将设置为None"
                )
                rating = None

        # 评论数验证
        comments_count = video.get("comments") or video.get("comments_count", 0)
        if comments_count:
            try:
                comments_count = int(comments_count)
                if comments_count < 0:
                    logger.warning(
                        f"视频 {video.get('num')} 评论数为负数: {comments_count}，将设置为0"
                    )
                    comments_count = 0
            except (ValueError, TypeError):
                logger.warning(
                    f"视频 {video.get('num')} 评论数格式错误: {comments_count}，将设置为0"
                )
                comments_count = 0

        return VideoCache(
            num=video.get("num"),
            title=video.get("title"),
            cover=video.get("cover"),
            url=video.get("url"),
            rating=rating,
            comments_count=comments_count,
            release_date=video.get("release_date"),
            is_hd=video.get("is_hd", False),
            is_zh=video.get("is_zh", False),
            is_uncensored=video_type == "uncensored",
            actors=video.get("actors", []),
            tags=video.get("tags", []),
            magnets=video.get("magnets", []),
            source=source,
            video_type=video_type,
            cycle=cycle,
            rank_position=rank_position,
            extra_data=video.get("extra_data"),
            fetched_at=datetime.now(),
        )

    def _update_video_cache(
        self, existing: VideoCache, video: Dict, rank_position: int
    ):
        """更新视频缓存记录"""
        existing.title = video.get("title", existing.title)
        existing.cover = video.get("cover", existing.cover)
        existing.url = video.get("url", existing.url)
        existing.rating = video.get("rating", existing.rating)
        existing.comments_count = video.get("comments") or video.get(
            "comments_count", existing.comments_count
        )
        existing.release_date = video.get("release_date", existing.release_date)
        existing.is_hd = video.get("is_hd", existing.is_hd)
        existing.is_zh = video.get("is_zh", existing.is_zh)
        existing.actors = video.get("actors", existing.actors)
        existing.tags = video.get("tags", existing.tags)
        existing.magnets = video.get("magnets", existing.magnets)
        existing.rank_position = rank_position
        existing.extra_data = video.get("extra_data", existing.extra_data)
        existing.updated_at = datetime.now()
        existing.fetched_at = datetime.now()

    def query_videos(
        self,
        min_rating: Optional[float] = None,
        min_comments: Optional[int] = None,
        is_hd: Optional[bool] = None,
        is_zh: Optional[bool] = None,
        is_uncensored: Optional[bool] = None,
        sources: Optional[List[str]] = None,
        video_types: Optional[List[str]] = None,
        cycles: Optional[List[str]] = None,
        days: int = 7,
        limit: int = 100,
        offset: int = 0,
        required_actor_id: Optional[str] = None,
        required_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        从缓存中查询视频数据

        Args:
            min_rating: 最低评分
            min_comments: 最低评论数
            is_hd: 是否高清
            is_zh: 是否中文字幕
            is_uncensored: 是否无码
            sources: 数据源列表
            video_types: 视频类型列表
            cycles: 周期列表
            days: 只查询最近N天抓取的数据
            limit: 返回数量限制
            offset: 偏移量
            required_actor_id: 必须包含的演员ID
            required_tags: 必须包含的标签列表
            exclude_tags: 需要排除的标签列表

        Returns:
            ���频列表
        """
        query = self.db.query(VideoCache)

        normalized_required_actor_id = (
            str(required_actor_id).strip() if required_actor_id is not None else ""
        )

        def _normalize_tag_value(tag: Any) -> str:
            if isinstance(tag, dict):
                raw_value = (
                    tag.get("name")
                    or tag.get("tag")
                    or tag.get("value")
                    or tag.get("label")
                )
            else:
                raw_value = tag
            return str(raw_value).strip().lower() if raw_value is not None else ""

        normalized_required_tags = {
            _normalize_tag_value(tag)
            for tag in (required_tags or [])
            if _normalize_tag_value(tag)
        }
        normalized_exclude_tags = {
            _normalize_tag_value(tag)
            for tag in (exclude_tags or [])
            if _normalize_tag_value(tag)
        }

        has_memory_filters = bool(
            normalized_required_actor_id
            or normalized_required_tags
            or normalized_exclude_tags
        )

        # 时间范围过滤
        if days > 0:
            release_cutoff = (datetime.now() - timedelta(days=days)).strftime(
                "%Y-%m-%d"
            )
            fallback_fetched_cutoff = datetime.now() - timedelta(days=days)
            query = query.filter(
                or_(
                    and_(
                        VideoCache.release_date.isnot(None),
                        VideoCache.release_date != "",
                        VideoCache.release_date >= release_cutoff,
                    ),
                    and_(
                        or_(
                            VideoCache.release_date.is_(None),
                            VideoCache.release_date == "",
                        ),
                        VideoCache.fetched_at >= fallback_fetched_cutoff,
                    ),
                )
            )

        # 评分过滤
        if min_rating is not None and min_rating > 0:
            query = query.filter(VideoCache.rating >= min_rating)

        # 评论数过滤
        if min_comments is not None and min_comments > 0:
            query = query.filter(VideoCache.comments_count >= min_comments)

        # 属性过滤
        if is_hd:
            query = query.filter(VideoCache.is_hd.is_(True))
        if is_zh:
            query = query.filter(VideoCache.is_zh.is_(True))
        if is_uncensored is not None:
            query = query.filter(VideoCache.is_uncensored == is_uncensored)

        # 数据源过滤
        if sources:
            query = query.filter(VideoCache.source.in_(sources))
        if video_types:
            query = query.filter(VideoCache.video_type.in_(video_types))
        if cycles:
            query = query.filter(VideoCache.cycle.in_(cycles))

        # 排序：优先按评分和评论数排序
        query = query.order_by(
            desc(VideoCache.rating),
            desc(VideoCache.comments_count),
            desc(VideoCache.fetched_at),
        )

        # 分页
        if has_memory_filters:
            prefetch_limit = max(limit + max(offset, 0), 1000)
            query = query.limit(prefetch_limit)
        else:
            query = query.limit(limit).offset(offset)

        results = query.all()
        videos = [video.to_dict() for video in results]

        # 演员和标签过滤（在内存中进行，因为JSON字段不支持高效的数据库查询）
        filtered_videos = videos

        # 过滤：必须包含指定演员
        if normalized_required_actor_id:
            filtered_videos = [
                v
                for v in filtered_videos
                if v.get("actors")
                and any(
                    str(actor.get("id", "")).strip() == normalized_required_actor_id
                    for actor in v.get("actors", [])
                )
            ]
            logger.info(
                f"演员过滤后剩余 {len(filtered_videos)} 个视频（要求演员ID: {normalized_required_actor_id}）"
            )

        # 过滤：必须包含所有指定标签
        if normalized_required_tags:
            filtered_videos = [
                v
                for v in filtered_videos
                if v.get("tags")
                and normalized_required_tags.issubset(
                    {
                        _normalize_tag_value(tag)
                        for tag in v.get("tags", [])
                        if _normalize_tag_value(tag)
                    }
                )
            ]
            logger.info(
                f"标签过滤后剩余 {len(filtered_videos)} 个视频（要求标签: {sorted(normalized_required_tags)}）"
            )

        # 过滤：排除包含指定标签的视频
        if normalized_exclude_tags:
            filtered_videos = [
                v
                for v in filtered_videos
                if not v.get("tags")
                or not (
                    {
                        _normalize_tag_value(tag)
                        for tag in v.get("tags", [])
                        if _normalize_tag_value(tag)
                    }
                    & normalized_exclude_tags
                )
            ]
            logger.info(
                f"排除标签后剩余 {len(filtered_videos)} 个视频（排除标签: {sorted(normalized_exclude_tags)}）"
            )

        if has_memory_filters:
            safe_offset = max(offset, 0)
            filtered_videos = filtered_videos[safe_offset : safe_offset + limit]

        return filtered_videos

    def get_ranking_videos(
        self,
        source: str = "JavDB",
        video_type: str = "censored",
        cycle: str = "daily",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        获取特定排行榜的缓存数据

        Args:
            source: 数据源
            video_type: 视频类型
            cycle: 周期
            limit: 返回数量

        Returns:
            排行榜视频列表（按排名排序）
        """
        results = (
            self.db.query(VideoCache)
            .filter(
                and_(
                    VideoCache.source == source,
                    VideoCache.video_type == video_type,
                    VideoCache.cycle == cycle,
                )
            )
            .order_by(VideoCache.rank_position)
            .limit(limit)
            .all()
        )

        return [video.to_dict() for video in results]

    def clean_old_cache(self, days: int = 7) -> int:
        """
        清理过期的缓存数据

        Args:
            days: 保留最近N天的数据

        Returns:
            删除的记录数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = (
            self.db.query(VideoCache)
            .filter(VideoCache.fetched_at < cutoff_date)
            .delete()
        )
        self.db.commit()

        logger.info(f"清理了 {deleted} 条过期视频缓存记录（超过{days}天）")
        return deleted

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self.db.query(func.count(VideoCache.id)).scalar()

        # 按数据源统计
        by_source = (
            self.db.query(VideoCache.source, func.count(VideoCache.id))
            .group_by(VideoCache.source)
            .all()
        )

        # 按周期统计
        by_cycle = (
            self.db.query(VideoCache.cycle, func.count(VideoCache.id))
            .group_by(VideoCache.cycle)
            .all()
        )

        # 最新更新时间
        latest_fetch = self.db.query(func.max(VideoCache.fetched_at)).scalar()

        return {
            "total_videos": total,
            "by_source": dict(by_source),
            "by_cycle": dict(by_cycle),
            "latest_fetch": latest_fetch.isoformat() if latest_fetch else None,
        }

    def _get_spider(self, source: str):
        """获取对应的爬虫实例"""
        if source == "JavDB":
            return spider.JavdbSpider()
        elif source == "JavBus":
            return spider.JavbusSpider()
        return None

    @staticmethod
    def job_refresh_video_cache():
        """定时任务：刷新视频缓存"""
        from app.db import SessionFactory

        try:
            with SessionFactory() as db:
                service = VideoCacheService(db)

                logger.info("开始定时刷新视频缓存...")
                stats = service.fetch_and_cache_rankings(
                    sources=["JavDB"],
                    video_types=["censored", "uncensored"],
                    cycles=["daily", "weekly", "monthly"],
                    max_pages=3,
                )

                logger.info(
                    f"视频缓存刷新完成: 抓取{stats['total_fetched']}个, "
                    f"新增{stats['total_new']}个, 更新{stats['total_updated']}个"
                )

                if stats["errors"]:
                    logger.warning(f"刷新过程中发生 {len(stats['errors'])} 个错误")

                setting = Setting()
                cleanup_days = max(
                    1,
                    int(
                        getattr(
                            setting.auto_download,
                            "auto_cleanup_days",
                            7,
                        )
                        or 7
                    ),
                )
                deleted = service.clean_old_cache(days=cleanup_days)

        except Exception as e:
            logger.error(f"视频缓存刷新失败: {str(e)}")
            logger.debug(traceback.format_exc())
