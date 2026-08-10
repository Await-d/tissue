import io
import os

from PIL import Image
from urllib.parse import urlparse
from . import cutter, badge
from .. import spider
from ..logger import logger
from ...schema import VideoDetail


def save_images(video: VideoDetail, video_path: str):
    path = urlparse(video.cover).path
    file_name = os.path.basename(path)
    extension = os.path.splitext(file_name)[-1]

    fanart_data = spider.get_video_cover(video.cover)
    if not fanart_data:
        # 源站阻断/负缓存命中时抓不到封面。这里必须温和退出：
        # 直接把 None 交给 BytesIO 会抛 TypeError，导致整个入库流程中断，
        # 影片已经移动到媒体库却没有写 NFO。
        logger.warning(f"未能获取封面，跳过封面及水印图片生成: {video.cover}")
        return None

    fanart = Image.open(io.BytesIO(fanart_data))

    poster_image = cutter.cut(fanart)
    poster = badge.tags(poster_image, video.is_zh, video.is_uncensored)
    thumb = badge.tags(fanart, video.is_zh, video.is_uncensored)

    save_path, _ = os.path.splitext(video_path)

    with open(save_path + f"-fanart{extension}", "wb") as f:
        f.write(fanart_data)
    poster.save(save_path + f"-poster{extension}", quality=95, subsampling=0, optimize=True)
    thumb.save(save_path + f"-thumb{extension}", quality=95, subsampling=0, optimize=True)

    return extension
