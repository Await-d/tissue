import time
import traceback
import re
from datetime import datetime
from random import randint

from fastapi import Depends
from sqlalchemy.orm import Session

from app import schema
from app.db import get_db, SessionFactory
from app.db.models.actor_subscribe import ActorSubscribe, ActorSubscribeDownload
from app.db.transaction import transaction
from app.exception import BizException
from app.service.base import BaseService
from app.utils import spider, notify
from app.utils.logger import logger
from app.utils.qbittorent import qbittorent


def get_actor_subscribe_service(db: Session = Depends(get_db)):
    return ActorSubscribeService(db=db)


class ActorSubscribeService(BaseService):

    def get_actor_subscriptions(self):
        return self.db.query(ActorSubscribe).order_by(ActorSubscribe.id.desc()).all()

    def get_actor_subscription_by_name(self, actor_name: str):
        """通过演员名称查找订阅"""
        return self.db.query(ActorSubscribe).filter(ActorSubscribe.actor_name == actor_name).first()

    @transaction
    def add_actor_subscription(self, param: schema.actor_subscribe.ActorSubscribeCreate):
        # 先检查是否已存在该演员的订阅
        exist = self.get_actor_subscription_by_name(param.actor_name)
        if exist:
            # 如果已存在，则更新订阅设置
            exist_data = param.model_dump()
            exist.update(self.db, exist_data)
            return exist
        
        # 不存在则创建新订阅
        subscription = ActorSubscribe(**param.model_dump())
        subscription.add(self.db)
        return subscription

    @transaction
    def update_actor_subscription(self, param: schema.actor_subscribe.ActorSubscribeUpdate):
        exist = ActorSubscribe.get(self.db, param.id)
        if not exist:
            raise BizException("该演员订阅不存在")
        exist.update(self.db, param.model_dump())
        return exist

    @transaction
    def delete_actor_subscription(self, subscription_id: int):
        exist = ActorSubscribe.get(self.db, subscription_id)
        if not exist:
            raise BizException("该演员订阅不存在")
        exist.delete(self.db)

    def get_actor_subscription_downloads(self, subscription_id: int):
        return (
            self.db.query(ActorSubscribeDownload)
            .filter(ActorSubscribeDownload.actor_subscribe_id == subscription_id)
            .order_by(ActorSubscribeDownload.download_time.desc())
            .all()
        )

    def do_actor_subscribe(self):
        """执行演员订阅任务，检查每个演员的新作品并下载"""
        subscriptions = self.get_actor_subscriptions()
        logger.info(f"获取到{len(subscriptions)}个演员订阅")
        
        for subscription in subscriptions:
            try:
                # 获取演员的作品列表
                actor_videos = spider.get_web_actor_videos(subscription.actor_name, "javdb")
                if not actor_videos:
                    logger.error(f"未获取到演员 {subscription.actor_name} 的作品列表")
                    continue
                
                # 获取该演员已下载的作品列表
                downloaded_videos = self.get_actor_subscription_downloads(subscription.id)
                downloaded_nums = {video.num for video in downloaded_videos}
                
                # 筛选出符合条件的新作品
                new_videos = []
                for video in actor_videos:
                    # 检查是否是新作品（发布日期晚于订阅起始日期）
                    if video.get("publish_date"):
                        try:
                            video_date = datetime.strptime(video["publish_date"], "%Y-%m-%d").date()
                            if video_date < subscription.from_date:
                                continue
                        except Exception as e:
                            logger.error(f"解析日期失败: {e}")
                            continue
                    
                    # 检查是否已下载
                    if video["num"] in downloaded_nums:
                        continue
                    
                    new_videos.append(video)
                
                logger.info(f"演员 {subscription.actor_name} 有 {len(new_videos)} 个新作品")
                
                # 处理每个新作品
                for video in new_videos:
                    try:
                        self.process_new_video(subscription, video)
                        # 每个视频处理后随机等待一段时间，避免请求过于频繁
                        time.sleep(randint(10, 30))
                    except Exception as e:
                        logger.error(f"处理视频 {video.get('num', 'unknown')} 失败: {e}")
                        traceback.print_exc()
                
            except Exception as e:
                logger.error(f"处理演员 {subscription.actor_name} 订阅失败: {e}")
                traceback.print_exc()
            
            # 每个演员处理完后随机等待一段时间
            time.sleep(randint(30, 60))
    
    def process_new_video(self, subscription: ActorSubscribe, video_info: dict):
        """处理单个新视频，获取下载链接并选择最佳资源下载"""
        video_num = video_info.get("num")
        if not video_num:
            logger.error("视频缺少番号信息")
            return
        
        logger.info(f"处理新视频: {video_num}")
        
        # 获取视频详情和下载资源
        video_detail = spider.get_video(video_num)
        if not video_detail or not video_detail.downloads:
            logger.error(f"未找到视频 {video_num} 的下载资源")
            return
        
        # 筛选符合条件的资源
        matched_resources = []
        for resource in video_detail.downloads:
            if (not subscription.is_hd or resource.is_hd) and \
               (not subscription.is_zh or resource.is_zh) and \
               (not subscription.is_uncensored or resource.is_uncensored):
                matched_resources.append(resource)
        
        if not matched_resources:
            logger.error(f"视频 {video_num} 没有符合条件的资源")
            return
        
        # 按文件大小排序，选择最大的资源
        largest_resource = self.select_largest_resource(matched_resources)
        
        if not largest_resource:
            logger.error(f"无法确定最佳下载资源")
            return
        
        logger.info(f"选择资源: {largest_resource.name}, 大小: {largest_resource.size}")
        
        # 下载资源
        try:
            self.download_actor_video(subscription, video_detail, largest_resource)
            logger.info(f"成功添加下载任务: {video_num}")
        except Exception as e:
            logger.error(f"添加下载任务失败: {e}")
            raise
    
    def select_largest_resource(self, resources):
        """从资源列表中选择文件大小最大的资源"""
        if not resources:
            return None
        
        def parse_size(size_str):
            if not size_str:
                return 0
            
            # 将大小转换为MB为单位的数值
            try:
                size_str = size_str.upper()
                if 'GB' in size_str:
                    return float(re.sub(r'[^\d.]', '', size_str)) * 1024
                elif 'MB' in size_str:
                    return float(re.sub(r'[^\d.]', '', size_str))
                elif 'KB' in size_str:
                    return float(re.sub(r'[^\d.]', '', size_str)) / 1024
                else:
                    return 0
            except Exception:
                return 0
        
        # 按文件大小排序
        sorted_resources = sorted(resources, key=lambda x: parse_size(x.size), reverse=True)
        return sorted_resources[0] if sorted_resources else None
    
    @transaction
    def download_actor_video(self, subscription, video_detail, resource):
        """下载演员视频并记录"""
        # 添加下载任务
        response = qbittorent.add_magnet(resource.magnet, resource.savepath)
        if response.status_code != 200:
            raise BizException("下载创建失败")
        
        # 记录下载
        download = ActorSubscribeDownload(
            actor_subscribe_id=subscription.id,
            num=video_detail.num,
            title=video_detail.title,
            cover=video_detail.cover,
            magnet=resource.magnet,
            size=resource.size,
            download_time=datetime.now(),
            is_hd=resource.is_hd,
            is_zh=resource.is_zh,
            is_uncensored=resource.is_uncensored
        )
        download.add(self.db)
        
        # 发送通知
        try:
            notify_data = {
                "actor_name": subscription.actor_name,
                "num": video_detail.num,
                "title": video_detail.title,
                "cover": video_detail.cover,
                "magnet": resource.magnet,
                "size": resource.size,
                "is_hd": resource.is_hd,
                "is_zh": resource.is_zh,
                "is_uncensored": resource.is_uncensored
            }
            notify.send_actor_subscribe(notify_data)
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
    
    @classmethod
    def job_actor_subscribe(cls):
        """演员订阅定时任务"""
        with SessionFactory() as db:
            service = ActorSubscribeService(db)
            service.do_actor_subscribe()
            db.commit() 