import time
import logging
from collections.abc import Iterable as IterableABC
from pathlib import Path
from typing import Any, Dict, List

import tailer
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi.responses import StreamingResponse
from app.utils import spider
from app.dependencies.security import verify_token
from app.db import get_db
from app.service.video_cache import VideoCacheService

router = APIRouter()


def _normalize_source(source: str) -> str:
    normalized = (source or "").strip().lower()
    mapping = {
        "javdb": "JavDB",
        "javbus": "JavBus",
    }
    return mapping.get(normalized, source)


def _to_plain_dict(video: Any) -> Dict[str, Any]:
    if isinstance(video, dict):
        return dict(video)
    if hasattr(video, "model_dump"):
        return video.model_dump()
    if hasattr(video, "dict"):
        return video.dict()
    return {}


def _normalize_ranking_fields(videos: Any) -> List[Dict[str, Any]]:
    if not isinstance(videos, IterableABC):
        return []

    normalized: List[Dict[str, Any]] = []
    for video in videos:
        item = _to_plain_dict(video)
        if not item:
            continue

        if "is_zh" not in item and "isZh" in item:
            item["is_zh"] = bool(item.get("isZh"))

        if "rank" not in item:
            item["rank"] = item.get("rating")

        if "rank_count" not in item:
            item["rank_count"] = item.get("comments_count", item.get("comments", 0))

        if "publish_date" not in item:
            item["publish_date"] = item.get("release_date")

        normalized.append(item)

    return normalized


@router.get("/ranking")
def get_rankings(
    source: str, video_type: str, cycle: str, db: Session = Depends(get_db)
):
    """
    获取排行榜数据（优先从缓存读取，缓存不存在时实时爬取）

    Args:
        source: 数据源（JavDB, JavBus等）
        video_type: 视频类型（censored, uncensored）
        cycle: 周期（daily, weekly, monthly）
        db: 数据库会话
    """
    source = _normalize_source(source)
    logger = logging.getLogger(__name__)

    cache_service = VideoCacheService(db)

    # 优先从缓存获取
    try:
        cached_videos = cache_service.get_ranking_videos(
            source=source, video_type=video_type, cycle=cycle, limit=100
        )

        # 如果缓存有数据，直接返回
        if cached_videos:
            return _normalize_ranking_fields(cached_videos)

        refresh_stats = cache_service.fetch_and_cache_rankings(
            sources=[source],
            video_types=[video_type],
            cycles=[cycle],
            max_pages=1,
            apply_delay=False,
        )
        logger.info(
            f"首页榜单按需刷新完成: {source} {video_type} {cycle}, "
            f"抓取{refresh_stats['total_fetched']}个, 错误{len(refresh_stats['errors'])}个"
        )

        cached_videos = cache_service.get_ranking_videos(
            source=source, video_type=video_type, cycle=cycle, limit=100
        )
        if cached_videos:
            return _normalize_ranking_fields(cached_videos)
    except Exception as e:
        # 缓存查询失败，记录日志并降级到实时爬取
        logger.warning(f"从缓存获取排行榜失败: {e}，降级到实时爬取")

    # 缓存没有数据或查询失败，降级到实时爬取
    if source == "JavDB":
        spider_instance = spider.JavdbSpider()

        detailed_rankings = spider_instance.get_ranking_with_details(
            video_type, cycle, max_pages=1, apply_delay=False
        )
        if detailed_rankings:
            return _normalize_ranking_fields(detailed_rankings)

        basic_rankings = spider_instance.get_ranking(video_type, cycle)
        normalized = _normalize_ranking_fields(basic_rankings)
        if normalized:
            return normalized
    try:
        stale_videos = cache_service.query_videos(
            sources=[source], video_types=[video_type], days=30, limit=100
        )
        if stale_videos:
            logger.warning(
                f"使用最近缓存兜底返回首页数据: {source} {video_type} {cycle}, 数量={len(stale_videos)}"
            )
            return _normalize_ranking_fields(stale_videos)
    except Exception as e:
        logger.warning(f"读取兜底缓存失败: {e}")

    return []


@router.get("/ranking/detail")
def get_ranking_detail(source: str, num: str, url: str):
    # 根据URL自动修正source参数
    import logging

    logger = logging.getLogger(__name__)

    original_source = source
    # 如果URL包含javbus但source不是JavBus，自动修正
    if "javbus" in url.lower() and source != "JavBus":
        source = "JavBus"
        logger.info(f"根据URL自动修正source: {original_source} -> {source}")
    # 如果URL包含javdb但source不是JavDB，自动修正
    elif "javdb" in url.lower() and source != "JavDB":
        source = "JavDB"
        logger.info(f"根据URL自动修正source: {original_source} -> {source}")

    if source == "JavDB":
        return spider.JavdbSpider().get_info(
            num, url=url, include_downloads=True, include_previews=True
        )
    elif source == "JavBus":
        return spider.JavbusSpider().get_info(
            num, url=url, include_downloads=True, include_previews=True
        )


@router.get("/log", dependencies=[Depends(verify_token)])
async def get_logs():
    log_path = Path(f"{Path(__file__).cwd()}/config/app.log")

    def log_generator():
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[-50:]:
                yield "data: %s\n\n" % line
        while True:
            for t in tailer.follow(open(log_path, "r", encoding="utf-8")):
                yield "data: %s\n\n" % (t or "")
            time.sleep(1)

    return StreamingResponse(log_generator(), media_type="text/event-stream")
