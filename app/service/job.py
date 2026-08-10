import hashlib
import os

from app.db import SessionFactory
from app.schema import Setting
from app.service.subscribe import SubscribeService
from app.utils import cache as cache_utils
from app.utils import nfo
from app.utils.cache import cache_path
from app.utils.logger import logger

META_SUFFIX = '.meta.json'


def clean_cache():
    """清理封面缓存中不再被引用的条目。

    图片缓存现在是「数据文件 + <hash>.meta.json 元数据」成对存在，
    清理时必须把两者当作一个整体：只删数据不删元数据会留下孤儿元数据，
    只删元数据则会让仍在使用的图片全部退化成「过期」状态而被反复重抓。
    """
    urls = set()
    setting = Setting().app
    with SessionFactory() as db:
        subscribes = SubscribeService(db=db).get_subscribes()
        for subscribe in subscribes:
            urls.add(subscribe.cover)

    for root, _, files in os.walk(setting.video_path):
        for file in files:
            if file.endswith('.nfo'):
                info = nfo.get_full(str(os.path.join(root, file)))
                urls.add(info.cover)
                for actor in info.actors:
                    urls.add(actor.thumb)

    hashed_urls = set()
    for url in urls:
        # 订阅/NFO 里可能没有封面地址，跳过以免 encode 抛错中断整个清理任务
        if not url:
            continue
        md = hashlib.md5()
        md.update(url.encode("utf-8"))
        hashed_urls.add(md.hexdigest())

    cache_save_path = os.path.join(cache_path, 'cover')
    if not os.path.isdir(cache_save_path):
        return

    removed = 0
    for name in os.listdir(cache_save_path):
        # 用数据文件名（去掉 .meta.json 后缀）判断归属，元数据随数据一起去留
        base_name = name[: -len(META_SUFFIX)] if name.endswith(META_SUFFIX) else name
        if base_name in hashed_urls:
            continue
        try:
            os.remove(os.path.join(cache_save_path, name))
            removed += 1
        except OSError as e:
            logger.warning(f"清理封面缓存失败 {name}: {e}")

    # 清掉过期的负缓存与孤儿元数据，让失效地址有机会重新尝试
    expired = cache_utils.cleanup_expired_cache()
    logger.info(
        f"封面缓存清理完成: 删除{removed}个未引用文件, "
        f"清理过期元数据{expired['removed_metadata']}个"
    )
