import traceback
from typing import List
from datetime import datetime
from urllib.parse import urlparse

from app.schema import VideoDetail
from app.schema.setting import Setting
from app.utils import cache
from app.utils.logger import logger
from app.utils.spider.dmm import DmmSpider
from app.utils.spider.jav321 import Jav321Spider
from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.javdb import JavdbSpider
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException


def _normalize_cover_url(url: str):
    normalized = (url or "").strip()
    if normalized.startswith("//"):
        normalized = "https:" + normalized
    return normalized


def _is_image_binary(content: bytes):
    if not content:
        return False

    if content.startswith(b"\xff\xd8\xff"):  # jpeg
        return True
    if content.startswith(b"\x89PNG\r\n\x1a\n"):  # png
        return True
    if content.startswith((b"GIF87a", b"GIF89a")):  # gif
        return True
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":  # webp
        return True
    if (
        len(content) >= 12
        and content[4:8] == b"ftyp"
        and content[8:12] in (b"avif", b"mif1")
    ):  # avif/heif
        return True
    return False


def get_web_actor_videos(actor_name: str, source: str = "javdb"):
    """获取演员的视频列表，这是一个辅助函数，用于避免循环导入"""
    # 延迟导入以避免循环引用
    from app.api.video import _get_web_actor_videos

    return _get_web_actor_videos(actor_name, source)


def get_video_cover(url: str):
    normalized_url = _normalize_cover_url(url)
    component = urlparse(normalized_url)

    if component.scheme not in ("http", "https") or not component.netloc:
        logger.warning(f"封面地址格式无效: {url}")
        return None

    cached = cache.get_cache_file("cover", normalized_url)
    if cached is not None:
        if _is_image_binary(cached):
            return cached
        logger.warning(f"封面缓存内容非图片，清理并重新抓取: {normalized_url}")
        cache.clean_cache_file("cover", normalized_url)

    hostname = component.hostname
    if hostname in ("www.javbus.com", "javbus.com"):
        response = JavbusSpider.get_cover(normalized_url)
    elif hostname in ("c0.jdbstatic.com", "jdbstatic.com"):
        response = JavdbSpider.get_cover(normalized_url)
    else:
        response = Spider.get_cover(normalized_url)

    if not isinstance(response, (bytes, bytearray)):
        logger.warning(f"封面抓取结果类型异常: {normalized_url}")
        return None

    if not _is_image_binary(bytes(response)):
        logger.warning(f"封面抓取结果不是图片内容: {normalized_url}")
        return None

    cover_bytes = bytes(response)
    cache.cache_file("cover", normalized_url, cover_bytes)
    return cover_bytes


def _merge_video_info(metas: List[VideoDetail]) -> VideoDetail:
    meta = metas[0]
    if len(metas) >= 2:
        logger.info("合并多个刮削信息...")
        for key in meta.__dict__:
            if not getattr(meta, key):
                for other_meta in metas[1:]:
                    value = getattr(other_meta, key)
                    if value:
                        setattr(meta, key, value)
                        break
        meta.website = [m.website[0] for m in metas if m.website]
        meta.previews = [m.previews[0] for m in metas if m.previews]
        merged_downloads = []
        for item in metas:
            if item.downloads:
                merged_downloads.extend(item.downloads)
        meta.downloads = merged_downloads
        if meta.downloads:
            meta.downloads.sort(
                key=lambda i: i.publish_date or datetime.now().date(), reverse=True
            )
        logger.info("信息合并成功")
    return meta


def get_video_info(number: str):
    spiders = [JavbusSpider(), JavdbSpider(), Jav321Spider(), DmmSpider()]
    metas = []
    logger.info(f"开始刮削番号《{number}》")
    for spider in spiders:
        try:
            logger.info(f"{spider.name} 开始刮削...")
            meta = spider.get_info(number)
            metas.append(meta)
            logger.info(f"{spider.name} 刮削成功")
        except SpiderException as e:
            logger.info(f"{spider.name} {e.message}")
        except Exception:
            logger.error(f"{spider.name} 未知错误，请检查网站连通性")
            traceback.print_exc()

    if len(metas) == 0:
        return

    meta = _merge_video_info(metas)

    actor_names = [
        actor.name
        for actor in (meta.actors or [])
        if isinstance(actor.name, str) and actor.name
    ]
    logger.info(
        f"番号《{number}》刮削完成，标题：{meta.title}，演员：{'、'.join(actor_names)}"
    )
    return meta


def get_spiders():
    """获取所有可用的爬虫实例"""
    return [JavbusSpider(), JavdbSpider(), Jav321Spider(), DmmSpider()]


def get_video(number: str):
    spiders = [JavbusSpider(), JavdbSpider()]
    metas = []
    preview_trace = bool(getattr(Setting().app, "preview_trace", False))
    logger.info(f"开始刮削番号《{number}》")

    for spider in spiders:
        try:
            if spider.downloadable:
                logger.info(f"{spider.name} 获取下载列表...")
                try:
                    videos = spider.get_info(
                        number, include_downloads=True, include_previews=True
                    )
                    if videos:
                        download_count = len(videos.downloads or [])
                        preview_count = sum(
                            len(p.items or []) for p in (videos.previews or [])
                        )

                        if download_count > 0:
                            logger.info(
                                f"{spider.name} 获取到{download_count}条下载资源"
                            )
                        else:
                            logger.warning(
                                f"{spider.name} 未获取到下载资源，将保留元数据/预览信息"
                            )

                        if preview_count > 0:
                            logger.info(f"{spider.name} 获取到{preview_count}个预览项")
                        elif preview_trace:
                            logger.info(f"{spider.name} 未获取到预览项")

                        if preview_trace:
                            preview_sources = [
                                p.website for p in (videos.previews or [])
                            ]
                            logger.info(
                                f"[PREVIEW_TRACE] {spider.name} -> downloads={download_count}, previews={preview_count}, sources={preview_sources}"
                            )

                        metas.append(videos)
                    else:
                        logger.warning(f"{spider.name} 未获取到影片信息")
                except SpiderException as e:
                    logger.error(f"{spider.name} 获取下载列表失败: {e.message}")
                except Exception as e:
                    logger.error(f"{spider.name} 获取下载列表失败: {str(e)}")
                    traceback.print_exc()
        except Exception as e:
            logger.error(f"{spider.name} 未知错误: {str(e)}")
            traceback.print_exc()
            continue

    if len(metas) == 0:
        logger.warning(f"番号《{number}》没有找到任何下载资源")
        return None

    meta = _merge_video_info(metas)
    if preview_trace:
        merged_preview_count = sum(len(p.items or []) for p in (meta.previews or []))
        logger.info(
            f"[PREVIEW_TRACE] merged number={number}, downloads={len(meta.downloads or [])}, preview_groups={len(meta.previews or [])}, preview_items={merged_preview_count}"
        )
    if not (meta.downloads or []):
        logger.warning(f"番号《{number}》未匹配到下载资源，但已返回可用元数据")
    return meta
