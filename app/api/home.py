import time
from pathlib import Path

import tailer
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi.responses import StreamingResponse
from app.utils import spider
from app.dependencies.security import verify_token
from app.db import get_db
from app.service.video_cache import VideoCacheService

router = APIRouter()


@router.get('/ranking')
def get_rankings(source: str, video_type: str, cycle: str, db: Session = Depends(get_db)):
    """
    获取排行榜数据（优先从缓存读取，缓存不存在时实时爬取）

    Args:
        source: 数据源（JavDB, JavBus等）
        video_type: 视频类型（censored, uncensored）
        cycle: 周期（daily, weekly, monthly）
        db: 数据库会话
    """
    # 优先从缓存获取
    try:
        cache_service = VideoCacheService(db)
        cached_videos = cache_service.get_ranking_videos(
            source=source,
            video_type=video_type,
            cycle=cycle,
            limit=100
        )

        # 如果缓存有数据，直接返回
        if cached_videos:
            return cached_videos
    except Exception as e:
        # 缓存查询失败，记录日志并降级到实时爬取
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"从缓存获取排行榜失败: {e}，降级到实时爬取")

    # 缓存没有数据或查询失败，降级到实时爬取
    if source == 'JavDB':
        return spider.JavdbSpider().get_ranking(video_type, cycle)

    return []


@router.get('/ranking/detail')
def get_ranking_detail(source: str, num: str, url: str):
    # 根据URL自动修正source参数
    import logging
    logger = logging.getLogger(__name__)
    
    original_source = source
    # 如果URL包含javbus但source不是JavBus，自动修正
    if 'javbus' in url.lower() and source != 'JavBus':
        source = 'JavBus'
        logger.info(f"根据URL自动修正source: {original_source} -> {source}")
    # 如果URL包含javdb但source不是JavDB，自动修正
    elif 'javdb' in url.lower() and source != 'JavDB':
        source = 'JavDB'
        logger.info(f"根据URL自动修正source: {original_source} -> {source}")
    
    if source == 'JavDB':
        return spider.JavdbSpider().get_info(num, url=url, include_downloads=True, include_previews=True)
    elif source == 'JavBus':
        return spider.JavbusSpider().get_info(num, url=url, include_downloads=True, include_previews=True)


@router.get('/log', dependencies=[Depends(verify_token)])
async def get_logs():
    log_path = Path(f'{Path(__file__).cwd()}/config/app.log')

    def log_generator():
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-50:]:
                yield 'data: %s\n\n' % line
        while True:
            for t in tailer.follow(open(log_path, 'r', encoding='utf-8')):
                yield 'data: %s\n\n' % (t or '')
            time.sleep(1)

    return StreamingResponse(log_generator(), media_type="text/event-stream")
