from typing import Optional, List

from fastapi import APIRouter, Depends

from app.schema import VideoDetail
from app.schema.r import R
from app.schema.video import WebActor, WebVideo
from app.service.video import get_video_service
from app.utils.logger import logger
from app.utils.spider.javdb import JavdbSpider
from app.utils.spider.javbus import JavbusSpider
from app.dependencies.security import verify_token

router = APIRouter()


@router.get('/', dependencies=[Depends(verify_token)])
def get_videos(force: Optional[bool] = False, service=Depends(get_video_service)):
    if force:
        video = service.get_videos_force()
    else:
        video = service.get_videos()
    return R.list(video)


@router.get('/detail', dependencies=[Depends(verify_token)])
def get_video(path: str, service=Depends(get_video_service)):
    video = service.get_video(path)
    return R.ok(video)


@router.get('/parse', dependencies=[Depends(verify_token)])
def parse_video(path: str, service=Depends(get_video_service)):
    video = service.parse_video(path)
    return R.ok(video)


@router.get('/scrape', dependencies=[Depends(verify_token)])
def scrape_video(num: str, service=Depends(get_video_service)):
    video = service.scrape_video(num)
    return R.ok(video)


@router.post('/', dependencies=[Depends(verify_token)])
def save_video(video: VideoDetail,
               mode: Optional[str] = None,
               trans_mode: Optional[str] = None,
               service=Depends(get_video_service)):
    service.save_video(video, mode, trans_mode)
    return R.ok()


@router.delete('/', dependencies=[Depends(verify_token)])
def delete_video(path: str, service=Depends(get_video_service)):
    service.delete_video(path)
    return R.ok()


@router.get('/actors', dependencies=[Depends(verify_token)])
def get_all_actors(force: Optional[bool] = True, service=Depends(get_video_service)):
    """获取所有演员列表"""
    if force:
        # 强制刷新视频缓存
        logger.info("强制刷新视频缓存，获取演员列表")
        service.get_videos_force()
    else:
        logger.info("从缓存获取演员列表")
    actors = service.get_all_actors()
    return R.list(actors)


@router.get('/search/actor', dependencies=[Depends(verify_token)])
def search_videos_by_actor(actor_name: str, force: Optional[bool] = True, service=Depends(get_video_service)):
    """根据演员名称搜索视频"""
    if force:
        # 强制刷新视频缓存
        logger.info(f"强制刷新视频缓存，搜索演员：{actor_name}")
        service.get_videos_force()
    else:
        logger.info(f"从缓存搜索演员：{actor_name}")
    videos = service.search_videos_by_actor(actor_name)
    return R.list(videos)


@router.get('/web/actors')
def get_web_actors(source: str = 'javdb'):
    """从网站获取热门演员列表"""
    logger.info(f"从{source}获取热门演员列表")
    try:
        if source.lower() == 'javdb':
            spider = JavdbSpider()
        elif source.lower() == 'javbus':
            spider = JavbusSpider()
        else:
            return R.list([])
            
        actors = spider.get_actors()
        
        # 转换为WebActor类型
        web_actors = []
        for actor in actors:
            web_actor = WebActor(
                name=actor.name,
                thumb=actor.thumb,
                url=f"/actors/{actor.name}"  # 简化URL，前端会处理
            )
            web_actors.append(web_actor)
            
        return R.list(web_actors)
    except Exception as e:
        logger.error(f"获取演员列表失败: {str(e)}")
        return R.list([])


@router.get('/web/search/actor', dependencies=[Depends(verify_token)])
def search_web_actor(actor_name: str, source: str = 'javdb'):
    """从网站搜索演员"""
    logger.info(f"从{source}搜索演员: {actor_name}")
    try:
        if source.lower() == 'javdb':
            spider = JavdbSpider()
        elif source.lower() == 'javbus':
            spider = JavbusSpider()
        else:
            return R.list([])
            
        actors = spider.search_actor(actor_name)
        
        # 转换为WebActor类型
        web_actors = []
        for actor in actors:
            web_actor = WebActor(
                name=actor.name,
                thumb=actor.thumb,
                url=f"/actors/{actor.name}"  # 简化URL，前端会处理
            )
            web_actors.append(web_actor)
            
        return R.list(web_actors)
    except Exception as e:
        logger.error(f"搜索演员失败: {str(e)}")
        return R.list([])


@router.get('/web/actor/videos')
def get_web_actor_videos(actor_name: str, source: str = 'javdb'):
    """获取演员的所有视频"""
    logger.info(f"从{source}获取演员的视频: {actor_name}")
    try:
        if source.lower() == 'javdb':
            spider = JavdbSpider()
        elif source.lower() == 'javbus':
            spider = JavbusSpider()
        else:
            return R.list([])
            
        # 直接传入演员名称，不构造URL
        videos = spider.get_actor_videos(actor_name)
        
        # 转换为WebVideo类型
        web_videos: List[WebVideo] = []
        for video in videos:
            web_video = WebVideo(
                title=video.title or video.num,
                cover=video.cover,
                num=video.num,
                url=video.url,
                publish_date=getattr(video, "publish_date", None),
                rank=getattr(video, "rank", None),
                is_zh=getattr(video, "isZh", False),
                is_uncensored=getattr(video, "is_uncensored", False)
            )
            web_videos.append(web_video)
            
        return R.list(web_videos)
    except Exception as e:
        logger.error(f"获取演员视频失败: {str(e)}")
        return R.list([])
