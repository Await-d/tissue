import time
import traceback
import re
import os
from datetime import datetime
from random import randint

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

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
        """获取所有演员订阅列表，包含下载统计"""
        try:
            # 使用SQL联表查询获取演员订阅信息和下载数量统计
            sql_str = """
            SELECT a.*, COALESCE(COUNT(d.id), 0) as download_count
            FROM actor_subscribe a
            LEFT JOIN actor_subscribe_download d ON a.id = d.actor_subscribe_id
            GROUP BY a.id
            ORDER BY a.id DESC
            """
            query = text(sql_str)
            result = self.db.execute(query)
            subscriptions = []
            
            for row in result:
                # 将查询结果转换为字典
                subscription_dict = {
                    'id': row.id,
                    'actor_name': row.actor_name,
                    'actor_url': row.actor_url,
                    'actor_thumb': row.actor_thumb,
                    'from_date': row.from_date,
                    'last_updated': row.last_updated,
                    'is_hd': row.is_hd,
                    'is_zh': row.is_zh,
                    'is_uncensored': row.is_uncensored,
                    'is_paused': row.is_paused,
                    'min_rating': getattr(row, 'min_rating', 0.0),
                    'min_comments': getattr(row, 'min_comments', 0),
                    'download_count': row.download_count,
                    'subscribed_works_count': 0  # 默认值，将在下面计算
                }
                
                # 计算订阅作品总数（符合订阅条件的作品数量）
                try:
                    subscribed_works_count = self._calculate_subscribed_works_count(subscription_dict)
                    subscription_dict['subscribed_works_count'] = subscribed_works_count
                except Exception as e:
                    logger.error(f"计算演员 {subscription_dict['actor_name']} 的订阅作品数量失败: {e}")
                    subscription_dict['subscribed_works_count'] = 0
                
                subscriptions.append(subscription_dict)
            
            return subscriptions
        except Exception as e:
            logger.error(f"获取演员订阅列表失败: {e}")
            # 如果查询失败，回退到原来的简单查询
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
    def update_actor_subscription_status(self, param: schema.actor_subscribe.ActorSubscribeStatusUpdate):
        """更新演员订阅状态（暂停/恢复）"""
        exist = ActorSubscribe.get(self.db, param.id)
        if not exist:
            raise BizException("该演员订阅不存在")
        exist.update(self.db, {"is_paused": param.is_paused})
        return exist

    @transaction
    def delete_actor_subscription(self, subscription_id: int, delete_downloads: bool = False):
        """删除演员订阅
        
        Args:
            subscription_id: 订阅ID
            delete_downloads: 是否删除已下载的资源
        """
        exist = ActorSubscribe.get(self.db, subscription_id)
        if not exist:
            raise BizException("该演员订阅不存在")
        
        # 获取该订阅的所有下载记录
        downloads = self.get_actor_subscription_downloads(subscription_id)
        
        if delete_downloads and downloads:
            logger.info(f"开始删除演员 {exist.actor_name} 的 {len(downloads)} 个下载资源")
            
            # 删除qBittorrent中的下载任务
            for download in downloads:
                try:
                    if download.magnet:
                        # 通过magnet获取种子hash，然后删除任务
                        self._delete_torrent_by_magnet(download.magnet)
                        logger.info(f"已删除下载任务: {download.num}")
                except Exception as e:
                    logger.error(f"删除下载任务失败 {download.num}: {e}")
        
        # 删除下载记录（数据库中的记录）
        for download in downloads:
            download.delete(self.db)
        
        # 删除订阅记录
        exist.delete(self.db)
        
        logger.info(f"已删除演员订阅: {exist.actor_name}, 删除下载资源: {delete_downloads}")

    def _delete_torrent_by_magnet(self, magnet: str):
        """通过magnet链接删除qBittorrent中的种子"""
        try:
            # 使用qbittorent的方法从magnet链接中提取hash
            torrent_hash = qbittorent.extract_hash_from_magnet(magnet)
            
            if torrent_hash:
                # 调用qBittorrent API删除种子（包括文件）
                response = qbittorent.delete_torrent(torrent_hash, delete_files=True)
                if response.status_code == 200:
                    logger.info(f"成功删除种子: {torrent_hash}")
                else:
                    logger.warning(f"删除种子失败: {torrent_hash}, 状态码: {response.status_code}")
            else:
                logger.warning(f"无法从magnet链接中提取hash: {magnet}")
        except Exception as e:
            logger.error(f"删除种子时发生错误: {e}")

    def get_actor_subscription_downloads(self, subscription_id: int):
        return (
            self.db.query(ActorSubscribeDownload)
            .filter(ActorSubscribeDownload.actor_subscribe_id == subscription_id)
            .order_by(ActorSubscribeDownload.download_time.desc())
            .all()
        )

    def get_all_subscription_downloads(self):
        """获取所有演员订阅的下载记录，带有演员信息"""
        try:
            # 使用SQL联表查询获取下载记录和对应的演员信息
            sql_str = """
            SELECT d.*, a.actor_name, a.actor_thumb
            FROM actor_subscribe_download d
            JOIN actor_subscribe a ON d.actor_subscribe_id = a.id
            ORDER BY d.download_time DESC
            """
            query = text(sql_str)
            result = self.db.execute(query)
            downloads = []
            
            for row in result:
                # 将查询结果转换为字典
                download_dict = {
                    'id': row.id,
                    'actor_subscribe_id': row.actor_subscribe_id,
                    'num': row.num,
                    'title': row.title,
                    'cover': row.cover,
                    'magnet': row.magnet,
                    'size': row.size,
                    'download_time': row.download_time,
                    'is_hd': row.is_hd,
                    'is_zh': row.is_zh,
                    'is_uncensored': row.is_uncensored,
                    'actor_name': row.actor_name,
                    'actor_thumb': row.actor_thumb
                }
                downloads.append(download_dict)
            
            return downloads
        except Exception as e:
            logger.error(f"actor_subscribe - 获取所有下载记录失败: {e}")
            # 如果查询失败，回退到简单查询
            return []

    @transaction
    def delete_subscription_download(self, download_id: int, delete_files: bool = False):
        """删除单个下载记录
        
        Args:
            download_id: 下载记录ID
            delete_files: 是否同时删除文件
        """
        download = ActorSubscribeDownload.get(self.db, download_id)
        if not download:
            raise BizException("下载记录不存在")
        
        if delete_files and download.magnet:
            # 删除qBittorrent中的下载任务和文件
            self._delete_torrent_by_magnet(download.magnet)
            logger.info(f"已删除下载任务: {download.num}")
        
        # 删除数据库中的记录
        download.delete(self.db)
        logger.info(f"已删除下载记录: {download.num}, 删除文件: {delete_files}")
        
        return True

    def do_actor_subscribe(self):
        """执行演员订阅任务，检查每个演员的新作品并下载"""
        subscriptions = self.get_actor_subscriptions()
        logger.info(f"获取到{len(subscriptions)}个演员订阅")
        
        # 过滤掉已暂停的订阅
        active_subscriptions = [s for s in subscriptions if not s['is_paused']]
        if len(active_subscriptions) < len(subscriptions):
            logger.info(f"跳过{len(subscriptions) - len(active_subscriptions)}个已暂停的订阅")
        
        for subscription in active_subscriptions:
            try:
                # 获取演员的作品列表
                actor_videos = spider.get_web_actor_videos(subscription['actor_name'], "javdb")
                if not actor_videos:
                    logger.error(f"未获取到演员 {subscription['actor_name']} 的作品列表")
                    continue
                
                # 获取该演员已下载的作品列表
                downloaded_videos = self.get_actor_subscription_downloads(subscription['id'])
                downloaded_nums = {video.num for video in downloaded_videos}
                
                # 筛选出符合条件的新作品
                new_videos = []
                for video in actor_videos:
                    # 检查是否是新作品（发布日期晚于订阅起始日期）
                    if video.get("publish_date"):
                        try:
                            # 处理不同格式的日期
                            if isinstance(video["publish_date"], str):
                                video_date = datetime.strptime(video["publish_date"], "%Y-%m-%d").date()
                            else:
                                # 如果已经是日期对象
                                video_date = video["publish_date"]
                            
                            # 确保订阅起始日期也是date对象
                            from_date = subscription['from_date']
                            if isinstance(from_date, str):
                                from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                            elif hasattr(from_date, 'date'):
                                from_date = from_date.date()
                                
                            if video_date < from_date:
                                continue
                        except Exception as e:
                            logger.error(f"解析日期失败: {e}")
                            continue
                    
                    # 检查是否已下载
                    if video["num"] in downloaded_nums:
                        continue
                    
                    # 检查评分筛选条件
                    if subscription.get('min_rating', 0.0) > 0.0:
                        video_rating = video.get('rating', 0.0)
                        if isinstance(video_rating, str):
                            try:
                                video_rating = float(video_rating)
                            except (ValueError, TypeError):
                                video_rating = 0.0
                        if video_rating < subscription['min_rating']:
                            logger.debug(f"视频 {video['num']} 评分 {video_rating} 低于要求的 {subscription['min_rating']}")
                            continue
                    
                    # 检查评论数筛选条件
                    if subscription.get('min_comments', 0) > 0:
                        video_comments = video.get('comments_count', 0)
                        if isinstance(video_comments, str):
                            try:
                                video_comments = int(video_comments)
                            except (ValueError, TypeError):
                                video_comments = 0
                        if video_comments < subscription['min_comments']:
                            logger.debug(f"视频 {video['num']} 评论数 {video_comments} 低于要求的 {subscription['min_comments']}")
                            continue
                    
                    new_videos.append(video)
                
                logger.info(f"演员 {subscription['actor_name']} 有 {len(new_videos)} 个新作品")
                
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
                logger.error(f"处理演员 {subscription['actor_name']} 订阅失败: {e}")
                traceback.print_exc()
            
            # 每个演员处理完后随机等待一段时间
            time.sleep(randint(30, 60))
    
    def process_new_video(self, subscription: dict, video_info: dict):
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
            if (not subscription['is_hd'] or resource.is_hd) and \
               (not subscription['is_zh'] or resource.is_zh) and \
               (not subscription['is_uncensored'] or resource.is_uncensored):
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
    
    def download_actor_video(self, subscription, video_detail, resource):
        """下载演员视频并记录"""
        try:
            # 检查种子是否已存在于qBittorrent中
            if qbittorent.is_magnet_exists(resource.magnet):
                logger.info(f"种子已存在于qBittorrent中，跳过下载，直接记录: {video_detail.num}")
                # 虽然不添加下载任务，但仍然记录为已下载
                download = ActorSubscribeDownload(
                    actor_subscribe_id=subscription['id'],
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
                self.db.flush()
                return
                
            # 添加下载任务
            response = qbittorent.add_magnet(resource.magnet, resource.savepath)
            if response.status_code != 200:
                raise BizException("下载创建失败")
            
            # 记录下载
            download = ActorSubscribeDownload(
                actor_subscribe_id=subscription['id'],
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
            self.db.flush()
            
            # 发送通知
            try:
                from app.schema.actor_subscribe import ActorSubscribeNotify
                notify_data = ActorSubscribeNotify(
                    actor_name=subscription['actor_name'],
                    num=video_detail.num,
                    title=video_detail.title,
                    cover=video_detail.cover,
                    magnet=resource.magnet,
                    size=resource.size,
                    is_hd=resource.is_hd,
                    is_zh=resource.is_zh,
                    is_uncensored=resource.is_uncensored
                )
                notify.send_actor_subscribe(notify_data)
            except Exception as e:
                logger.error(f"发送通知失败: {e}")
        except Exception as e:
            self.db.rollback()
            raise e
    
    @classmethod
    def job_actor_subscribe(cls):
        """演员订阅定时任务"""
        with SessionFactory() as db:
            service = ActorSubscribeService(db)
            service.do_actor_subscribe()
            db.commit()

    def _calculate_subscribed_works_count(self, subscription: dict) -> int:
        """计算订阅作品总数（从订阅开始日期到现在，符合条件的作品数量）"""
        try:
            # 获取演员的作品列表
            actor_videos = spider.get_web_actor_videos(subscription['actor_name'], "javdb")
            if not actor_videos:
                return 0
            
            # 获取订阅起始日期，确保是date对象
            from_date = subscription['from_date']
            if isinstance(from_date, str):
                from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            
            # 筛选出符合订阅条件的作品
            qualified_videos = []
            for video in actor_videos:
                # 检查发布日期是否晚于订阅起始日期
                if video.get("publish_date"):
                    try:
                        # 处理不同格式的日期
                        if isinstance(video["publish_date"], str):
                            video_date = datetime.strptime(video["publish_date"], "%Y-%m-%d").date()
                        else:
                            video_date = video["publish_date"]
                        
                        # 确保订阅起始日期也是date对象
                        if isinstance(from_date, str):
                            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                        elif hasattr(from_date, 'date'):
                            from_date_obj = from_date.date()
                        else:
                            from_date_obj = from_date
                            
                        if video_date >= from_date_obj:
                            qualified_videos.append(video)
                    except Exception as e:
                        logger.error(f"解析日期失败: {e}")
                        continue
            
            return len(qualified_videos)
        except Exception as e:
            logger.error(f"获取演员 {subscription['actor_name']} 作品列表失败: {e}")
            return 0 