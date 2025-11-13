import re
import time
import traceback
from datetime import datetime
from random import randint

from fastapi import Depends
from sqlalchemy.orm import Session

from app import schema
from app.db import get_db, SessionFactory
from app.db.models import Subscribe, Torrent
from app.db.transaction import transaction
from app.exception import BizException
from app.service.base import BaseService
from app.service.download_filter import DownloadFilterService
from app.utils import spider, notify
from app.utils.logger import logger
from app.utils.qbittorent import qbittorent
from app.utils.spider import JavdbSpider


def get_subscribe_service(db: Session = Depends(get_db)):
    return SubscribeService(db=db)


class SubscribeService(BaseService):

    def __init__(self, db: Session):
        super().__init__(db)
        self.filter_service = DownloadFilterService(db)

    def get_subscribes(self):
        return self.db.query(Subscribe).filter(Subscribe.status != 2).order_by(Subscribe.id.desc()).all()

    def get_subscribe_histories(self):
        return self.db.query(Subscribe).filter(Subscribe.status == 2).order_by(Subscribe.update_time.desc()).all()

    @transaction
    def add_subscribe(self, param: schema.SubscribeCreate):
        exists = self.get_subscribes()

        if [exist for exist in exists if
            exist.num.upper() == param.num.upper() and exist.is_hd == param.is_hd and exist.is_zh == param.is_zh and exist.is_uncensored == param.is_uncensored]:
            raise BizException('存在相同订阅，无需重复添加')

        subscribe = Subscribe(**param.model_dump())
        subscribe.add(self.db)

    @transaction
    def update_subscribe(self, param: schema.SubscribeUpdate):
        exist = Subscribe.get(self.db, param.id)
        if not exist:
            raise BizException("该订阅不存在")

        exist.update(self.db, param.model_dump())

    @transaction
    def re_subscribe(self, subscribe_id: int):
        exist = Subscribe.get(self.db, subscribe_id)
        param = schema.SubscribeCreate(**exist.__dict__)
        param.status = 1
        self.add_subscribe(param)

    @transaction
    def delete_subscribe(self, subscribe_id: int):
        exist = Subscribe.get(self.db, subscribe_id)
        exist.delete(self.db)

    def search_video(self, num: str):
        video = spider.get_video(num)
        if not video:
            raise BizException("未找到影片")
        return video

    @transaction
    def download_video_manual(
        self, video: schema.SubscribeCreate, link: schema.VideoDownload
    ):
        self.download_video(video, link)

    def do_subscribe(self):
        subscribes = self.get_subscribes()
        logger.info(f"获取到{len(subscribes)}个订阅")
        for subscribe in subscribes:
            time.sleep(randint(30, 60))

            result = spider.get_video(subscribe.num)
            if not result:
                logger.error("所有站点均未获取到影片")
                continue

            def get_matched(item):
                if subscribe.is_hd and not item.is_hd:
                    logger.error(f"{item.name} 不匹配高清，已跳过")
                    return False
                if subscribe.is_zh and not item.is_zh:
                    logger.error(f"{item.name} 不匹配中文，已跳过")
                    return False
                if subscribe.is_uncensored and not item.is_uncensored:
                    logger.error(f"{item.name} 不匹配无码，已跳过")
                    return False

                if subscribe.include_keyword and not re.search(subscribe.include_keyword, item.name, re.IGNORECASE):
                    logger.error(f"{item.name} 不匹配包含关键字，已跳过")
                    return False

                if subscribe.exclude_keyword and re.search(subscribe.exclude_keyword, item.name, re.IGNORECASE):
                    logger.error(f"{item.name} 匹配排除关键字，已跳过")
                    return False

                return True

            result = list(filter(get_matched, result.downloads))
            if not result:
                logger.error(f"未匹配到符合条件的影片")
                continue

            logger.info(f"匹配到符合条件的影片{len(result)}部，将选择最新发布的影片")
            matched = result[0]
            if matched:
                try:
                    self.download_video(
                        schema.SubscribeCreate.model_validate(subscribe), matched
                    )
                    logger.info(f"订阅《{subscribe.num}》已完成")
                    subscribe.update(self.db, {'status': 2})
                    self.db.commit()
                except Exception as e:
                    logger.error("下载任务创建失败")
                    traceback.print_exc()
                    continue

    def download_video(self, video: schema.SubscribeCreate, link: schema.VideoDownload):
        from app.service.base_download import BaseDownloadService
        
        # 获取下载设置中的分类
        from app.schema.setting import Setting
        setting = Setting()
        category = setting.download.category if setting.download.category else None
        
        # 确保使用正确的下载路径
        download_path = link.savepath if link.savepath else setting.download.download_path
        
        # 使用基础下载服务进行下载（包含过滤规则）
        base_download_service = BaseDownloadService(self.db)
        download_result = base_download_service.download_with_filter(
            magnet=link.magnet,
            savepath=download_path,
            category=category,
            skip_filter=False  # 启用过滤规则
        )
        
        if not download_result['success']:
            error_msg = download_result['message']
            logger.warning(f"视频 {video.num} 下载被拒绝: {error_msg}")
            raise BizException(f"下载失败: {error_msg}")
        
        logger.info(f"视频 {video.num} 下载成功: {download_result['message']}")
        logger.info(f"过滤结果: 保留 {download_result['filtered_files']}/{download_result['total_files']} 个文件")
        
        # 记录种子信息到数据库
        torrent_hash = download_result['torrent_hash']
        if torrent_hash:
            torrent = Torrent()
            torrent.hash = torrent_hash
            torrent.num = video.num
            torrent.is_zh = link.is_zh
            torrent.is_hd = getattr(link, 'is_hd', False)
            torrent.is_uncensored = link.is_uncensored
            self.db.add(torrent)
            self.db.flush()

        # 检查是否属于演员订阅，如果是则记录到演员订阅下载表
        self._check_and_record_actor_subscribe_download(video, link)

        # 发送订阅通知
        subscribe_notify = schema.SubscribeNotify.model_validate(video)
        subscribe_notify = subscribe_notify.model_copy(update=link.model_dump())
        notify.send_subscribe(subscribe_notify)

    def _check_and_record_actor_subscribe_download(self, video: schema.SubscribeCreate, link: schema.VideoDownload):
        """检查并记录演员订阅下载"""
        try:
            logger.info(f"[智能下载] 开始检查演员订阅下载记录: {video.num}")
            from app.db.models.actor_subscribe import ActorSubscribe, ActorSubscribeDownload
            from app.utils import spider
            
            # 获取视频详情以获取演员信息
            video_detail = spider.get_video(video.num)
            if not video_detail:
                logger.info(f"[智能下载] 未能获取视频详情: {video.num}")
                return
            
            if not video_detail.actors:
                logger.info(f"视频无演员信息: {video.num}")
                return
            
            logger.info(f"视频 {video.num} 包含 {len(video_detail.actors)} 个演员")
            
            # 检查是否有对应的演员订阅
            for actor in video_detail.actors:
                logger.info(f"检查演员订阅: {actor.name}")
                actor_subscription = self.db.query(ActorSubscribe).filter(
                    ActorSubscribe.actor_name == actor.name
                ).first()
                
                if actor_subscription:
                    logger.info(f"找到演员订阅: {actor.name} (ID: {actor_subscription.id})")
                    # 检查是否已经记录过这个下载
                    existing_download = self.db.query(ActorSubscribeDownload).filter(
                        ActorSubscribeDownload.actor_subscribe_id == actor_subscription.id,
                        ActorSubscribeDownload.num == video.num
                    ).first()
                    
                    if existing_download:
                        logger.info(f"下载记录已存在: {actor.name} - {video.num}")
                    else:
                        # 记录到演员订阅下载表
                        download = ActorSubscribeDownload(
                            actor_subscribe_id=actor_subscription.id,
                            num=video.num,
                            title=video_detail.title,
                            cover=video_detail.cover,
                            magnet=link.magnet,
                            size=link.size if hasattr(link, 'size') else None,
                            download_time=datetime.now(),
                            is_hd=getattr(link, 'is_hd', False),
                            is_zh=link.is_zh,
                            is_uncensored=link.is_uncensored
                        )
                        download.add(self.db)
                        self.db.commit()  # 立即提交以确保记录被保存
                        logger.info(f"[智能下载] 成功记录演员订阅下载: {actor.name} - {video.num}")
                else:
                    logger.info(f"未找到演员订阅: {actor.name}")
                    
        except Exception as e:
            logger.error(f"记录演员订阅下载失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # 不影响主要下载流程，只记录错误

    def do_subscribe_meta_update(self):
        subscribes = self.get_subscribes()
        logger.info(f"获取到{len(subscribes)}个订阅")
        for subscribe in subscribes:
            info = spider.get_video_info(subscribe.num)
            if info:
                subscribe.cover = info.cover or subscribe.cover
                subscribe.title = info.title or subscribe.title
                subscribe.premiered = (
                    datetime.strptime(info.premiered, "%Y-%m-%d").date()
                    if info.premiered
                    else subscribe.premiered
                )
                subscribe.actors = (
                    ", ".join([i.name for i in info.actors])
                    if info.actors
                    else subscribe.actors
                )
                logger.info(f"已更新订阅《{subscribe.num}》元数据")
                self.db.add(subscribe)
            else:
                logger.error(f"未找到订阅《{subscribe.num}》元数据")

            time.sleep(randint(30, 60))

    @classmethod
    def job_subscribe(cls):
        with SessionFactory() as db:
            SubscribeService(db=db).do_subscribe()
            db.commit()

    @classmethod
    def job_subscribe_meta_update(cls):
        with SessionFactory() as db:
            SubscribeService(db=db).do_subscribe_meta_update()
            db.commit()
