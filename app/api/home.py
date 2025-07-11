import time
from pathlib import Path

import tailer
from fastapi import APIRouter, Depends

from fastapi.responses import StreamingResponse
from app.utils import spider
from app.dependencies.security import verify_token

router = APIRouter()


@router.get('/ranking')
def get_rankings(source: str, video_type: str, cycle: str):
    if source == 'JavDB':
        return spider.JavdbSpider().get_ranking(video_type, cycle)


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
