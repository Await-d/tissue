from datetime import date, datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field


class VideoActor(BaseModel):
    name: Optional[str] = None
    thumb: Optional[str] = None


class WebActor(BaseModel):
    """网站演员模型"""
    name: str
    thumb: Optional[str] = None
    url: Optional[str] = None


class VideoList(BaseModel):
    title: str
    path: str
    cover: Optional[str] = None
    is_zh: bool = False
    is_uncensored: bool = False

    actors: List[VideoActor] = []


class VideoDownload(BaseModel):
    website: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    magnet: Optional[str] = None
    size: Optional[str] = None
    savepath: Optional[str] = None
    is_uncensored: bool = False
    is_zh: bool = False
    is_hd: bool = False
    publish_date: Optional[date] = None


class WebVideo(BaseModel):
    """网站视频搜索结果模型"""
    title: str
    cover: Optional[str] = None
    num: str
    url: str
    publish_date: Optional[date] = None
    rank: Optional[float] = None
    is_zh: bool = False
    is_uncensored: bool = False
    actors: List[WebActor] = []


class VideoPreviewItem(BaseModel):
    type: Optional[str] = None
    thumb: Optional[str] = None
    url: Optional[str] = None


class VideoPreview(BaseModel):
    website: Optional[str] = None
    items: List[VideoPreviewItem] = []


class VideoDetail(BaseModel):
    # 标题
    title: Optional[str] = None
    # 番号
    num: Optional[str] = None
    # 评分
    rating: Optional[str] = None
    # 评论数
    comments_count: Optional[int] = None
    # 发行时间
    premiered: Optional[str] = None
    # 大纲
    outline: Optional[str] = None
    # 时长
    runtime: Optional[str] = None
    # 导演
    director: Optional[str] = None
    # 演员
    actors: Optional[List[VideoActor]] = []
    # 制造商
    studio: Optional[str] = None
    # 发行商
    publisher: Optional[str] = None
    # 类别
    tags: Optional[List[str]] = []
    # 系列
    series: Optional[str] = None
    # 封面
    cover: Optional[str] = None
    poster: Optional[str] = None
    fanart: Optional[str] = None
    thumb: Optional[str] = None
    # 页面
    website: Optional[List[str]] = []
    # 路径
    path: Optional[str] = None
    # 是否中文
    is_zh: bool = False
    # 是否无码
    is_uncensored: bool = False

    # 下载列表
    downloads: Optional[List[VideoDownload]] = []
    # 预览列表
    previews: Optional[List[VideoPreview]] = []


class VideoNotify(VideoDetail):
    is_success: bool = True
    mode: Optional[str] = None
    trans_mode: Optional[str] = None
    torrent_hash: Optional[str] = None
    size: Optional[str] = None
    message: Optional[str] = None
