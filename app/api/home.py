import threading
import time
import logging
import traceback
from collections.abc import Iterable as IterableABC
from pathlib import Path
from typing import Any, Dict, List

import tailer
from fastapi import APIRouter, Depends, Response
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


# 按需刷新的进程内节流：避免多个客户端同时打开首页时各自触发一次完整抓取
_REFRESH_LOCK = threading.Lock()
_REFRESH_IN_FLIGHT: set[tuple[str, str, str]] = set()
_REFRESH_LAST_ATTEMPT: Dict[tuple[str, str, str], float] = {}
_REFRESH_COOLDOWN_SECONDS = 120


def _try_acquire_refresh_slot(key: tuple[str, str, str]) -> bool:
    """抢占某个榜单组合的刷新权限。已有刷新在跑或处于冷却期则返回 False。"""
    with _REFRESH_LOCK:
        if key in _REFRESH_IN_FLIGHT:
            return False
        last_attempt = _REFRESH_LAST_ATTEMPT.get(key, 0.0)
        if time.time() - last_attempt < _REFRESH_COOLDOWN_SECONDS:
            return False
        _REFRESH_IN_FLIGHT.add(key)
        _REFRESH_LAST_ATTEMPT[key] = time.time()
        return True


def _release_refresh_slot(key: tuple[str, str, str]) -> None:
    with _REFRESH_LOCK:
        _REFRESH_IN_FLIGHT.discard(key)


@router.get("/ranking")
def get_rankings(
    source: str,
    video_type: str,
    cycle: str,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    获取排行榜数据（优先从缓存读取，缓存不存在时实时爬取）

    取数顺序：新鲜缓存 -> 按需抓取 -> 实时爬取 -> 30 天内旧缓存兜底。
    每一层都独立容错，任意一层异常都不会让接口 500，以免直接跳过后面的兜底。
    返回旧数据时通过响应头 X-Data-Stale / X-Data-Source 告知前端。

    Args:
        source: 数据源（JavDB, JavBus等）
        video_type: 视频类型（censored, uncensored）
        cycle: 周期（daily, weekly, monthly）
        db: 数据库会话
    """
    source = _normalize_source(source)
    logger = logging.getLogger(__name__)

    cache_service = VideoCacheService(db)
    refresh_key = (source, video_type, cycle)

    def _mark(data_source: str, stale: bool = False):
        response.headers["X-Data-Source"] = data_source
        response.headers["X-Data-Stale"] = "true" if stale else "false"

    # 1. 新鲜缓存
    try:
        cached_videos = cache_service.get_ranking_videos(
            source=source, video_type=video_type, cycle=cycle, limit=100
        )
        if cached_videos:
            _mark("cache")
            return _normalize_ranking_fields(cached_videos)
    except Exception as e:
        logger.warning(f"从缓存获取排行榜失败: {e}")

    # 2. 按需抓取并写缓存（同一组合并发去重 + 冷却，避免抓取风暴）
    if _try_acquire_refresh_slot(refresh_key):
        try:
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
                _mark("refresh")
                return _normalize_ranking_fields(cached_videos)
        except Exception as e:
            logger.warning(f"按需刷新排行榜失败: {e}，降级到实时爬取")
            logger.debug(traceback.format_exc())
        finally:
            _release_refresh_slot(refresh_key)
    else:
        logger.info(f"榜单刷新已在进行或处于冷却期，跳过本次抓取: {refresh_key}")

    # 3. 实时爬取（必须容错，否则会跳过下面的旧缓存兜底）
    try:
        if source == "JavDB":
            spider_instance = spider.JavdbSpider()

            detailed_rankings = spider_instance.get_ranking_with_details(
                video_type, cycle, max_pages=1, apply_delay=False
            )
            if detailed_rankings:
                _mark("live")
                return _normalize_ranking_fields(detailed_rankings)

            basic_rankings = spider_instance.get_ranking(video_type, cycle)
            normalized = _normalize_ranking_fields(basic_rankings)
            if normalized:
                _mark("live")
                return normalized
    except Exception as e:
        logger.warning(f"实时爬取排行榜失败: {e}，尝试使用旧缓存兜底")
        logger.debug(traceback.format_exc())

    # 4. 30 天内旧缓存兜底
    try:
        stale_videos = cache_service.query_videos(
            sources=[source], video_types=[video_type], days=30, limit=100
        )
        if stale_videos:
            logger.warning(
                f"使用最近缓存兜底返回首页数据: {source} {video_type} {cycle}, 数量={len(stale_videos)}"
            )
            _mark("stale-cache", stale=True)
            return _normalize_ranking_fields(stale_videos)
    except Exception as e:
        logger.warning(f"读取兜底缓存失败: {e}")

    logger.error(f"首页榜单所有取数途径均失败: {source} {video_type} {cycle}")
    _mark("empty", stale=True)
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
