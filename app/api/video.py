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
from app.utils.cache import cached, get_cache_json, cache_json, clean_cache_json

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


@cached('web_actors', key_func=lambda source: f"actors_{source.lower()}", expire_time=3600)
def _get_web_actors(source: str = 'javdb'):
    """从网站获取热门演员列表（带缓存）"""
    logger.info(f"从{source}获取热门演员列表")
    try:
        if source.lower() == 'javdb':
            spider = JavdbSpider()
        elif source.lower() == 'javbus':
            spider = JavbusSpider()
        else:
            return []
            
        actors = spider.get_actors()
        
        # 转换为WebActor类型
        web_actors = []
        for actor in actors:
            web_actor = WebActor(
                name=actor.name,
                thumb=actor.thumb,
                url=f"/actors/{actor.name}"  # 简化URL，前端会处理
            )
            # 转换为字典，使其可以被JSON序列化
            web_actors.append(web_actor.model_dump())
            
        return web_actors
    except Exception as e:
        logger.error(f"获取演员列表失败: {str(e)}")
        return []


@router.get('/web/actors')  # 无需token验证的API
def get_web_actors(source: str = 'javdb', force: bool = True):
    """从网站获取热门演员列表"""
    logger.info(f"尝试获取演员列表，源：{source}，强制刷新：{force}")
    cache_key = f"actors_{source.lower()}"
    
    # 如果强制刷新，则清除缓存
    if force:
        clean_cache_json('web_actors', cache_key)
        logger.info(f"强制刷新{source}演员列表")
    
    # 获取演员列表（内部有缓存机制）
    web_actors = _get_web_actors(source)
    return R.list(web_actors)


@cached('web_actor_search', key_func=lambda name, source: f"search_{source.lower()}_{name}", expire_time=3600)
def _search_web_actor(actor_name: str, source: str = 'javdb'):
    """从网站搜索演员（带缓存）"""
    logger.info(f"从{source}搜索演员: {actor_name}")
    try:
        if source.lower() == 'javdb':
            spider = JavdbSpider()
        elif source.lower() == 'javbus':
            spider = JavbusSpider()
        else:
            return []
            
        actors = spider.search_actor(actor_name)
        
        # 转换为WebActor类型
        web_actors = []
        for actor in actors:
            web_actor = WebActor(
                name=actor.name,
                thumb=actor.thumb,
                url=f"/actors/{actor.name}"  # 简化URL，前端会处理
            )
            # 转换为字典，使其可以被JSON序列化
            web_actors.append(web_actor.model_dump())
            
        return web_actors
    except Exception as e:
        logger.error(f"搜索演员失败: {str(e)}")
        return []


@router.get('/web/search/actor')
def search_web_actor(actor_name: str, source: str = 'javdb', force: bool = False):
    """从网站搜索演员"""
    cache_key = f"search_{source.lower()}_{actor_name}"
    
    # 如果强制刷新，则清除缓存
    if force:
        clean_cache_json('web_actor_search', cache_key)
        logger.info(f"强制刷新{source}演员搜索: {actor_name}")
    
    # 搜索演员（内部有缓存机制）
    web_actors = _search_web_actor(actor_name, source)
    return R.list(web_actors)


@cached('web_actor_videos', key_func=lambda name, source: f"videos_{source.lower()}_{name}", expire_time=3600)
def _get_web_actor_videos(actor_name: str, source: str = 'javdb'):
    """获取演员的所有视频（带缓存）"""
    logger.info(f"从{source}获取演员的视频: {actor_name}")
    
    try:
        # 选择爬虫
        if source.lower() == 'javdb':
            spider = JavdbSpider()
        elif source.lower() == 'javbus':
            spider = JavbusSpider()
        else:
            return []
        
        # 获取演员视频
        videos = spider.get_actor_videos(actor_name)
        
        # 处理结果，确保可以被JSON序列化
        result_videos = []
        for video in videos:
            video_dict = video.model_dump()
            
            # 处理日期：如果是日期对象，转换为字符串
            if video.publish_date:
                video_dict['publish_date'] = video.publish_date.isoformat()
            
            # 为演员订阅兼容性添加comments_count字段
            if 'rank_count' in video_dict and video_dict['rank_count'] is not None:
                video_dict['comments_count'] = video_dict['rank_count']
                
            result_videos.append(video_dict)
            
        return result_videos
    except Exception as e:
        logger.error(f"获取演员视频失败: {str(e)}")
        return []


@router.get('/web/actor/videos')  # 无需token验证的API
def get_web_actor_videos(actor_name: str, source: str = 'javdb', force: bool = False):
    """获取演员的所有视频"""
    cache_key = f"videos_{source.lower()}_{actor_name}"
    
    # 如果强制刷新，则清除缓存
    if force:
        clean_cache_json('web_actor_videos', cache_key)
        logger.info(f"强制刷新{source}演员视频: {actor_name}")
    
    # 获取演员视频（内部有缓存机制）
    web_videos = _get_web_actor_videos(actor_name, source)
    return R.list(web_videos)
