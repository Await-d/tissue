"""
自动下载服务
"""
import traceback
from datetime import datetime
import time
from random import randint
from typing import List, Dict, Any, Optional
from sqlalchemy import and_

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db, SessionFactory
from app.db.models.auto_download import AutoDownloadRule, AutoDownloadSubscription, DownloadStatus, TimeRangeType
from app.schema import subscribe as schema
from app.utils.video_collector import VideoCollector
from app.utils.logger import logger
from app.service.download import DownloadService
from app.service.subscribe import SubscribeService
from app.utils import spider


def get_auto_download_service(db: Session = Depends(get_db)):
    """获取自动下载服务实例"""
    return AutoDownloadService(db=db)


class AutoDownloadService:
    """自动下载服务"""

    def __init__(self, db=None):
        """初始化自动下载服务"""
        self.db = db or next(get_db())
        self.download_service = DownloadService()
    
    def execute_rules(self, rule_ids: Optional[List[int]] = None, force: bool = False) -> Dict[str, Any]:
        """执行自动下载规则"""
        # 获取要执行的规则
        query = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.is_enabled == True)
        if rule_ids:
            query = query.filter(AutoDownloadRule.id.in_(rule_ids))
        
        rules = query.all()
        
        if not rules:
            logger.warning("没有找到启用的规则，请确认规则配置")
            return {'message': '没有找到要执行的规则', 'processed_count': 0}
        
        logger.info(f"找到 {len(rules)} 个规则需要执行")
        processed_count = 0
        new_subscriptions = 0
        
        # 创建视频收集器（只创建一次，多个规则共享同一个收集器及其缓存）
        collector = VideoCollector()
        
        for rule in rules:
            try:
                logger.info(f"===== 执行规则 [{rule.name}] ID:{rule.id} =====" )
                logger.info(f"规则条件: 评分>={rule.min_rating or '无限制'}, 评论>={rule.min_comments or '无限制'}")
                logger.info(f"规则条件: 高清={rule.is_hd}, 中文字幕={rule.is_zh}, 无码={rule.is_uncensored}")
                
                # 计算时间范围
                if not force:
                    if rule.time_range_type == TimeRangeType.DAY:
                        time_range_days = rule.time_range_value
                    elif rule.time_range_type == TimeRangeType.WEEK:
                        time_range_days = rule.time_range_value * 7
                    elif rule.time_range_type == TimeRangeType.MONTH:
                        time_range_days = rule.time_range_value * 30
                    else:
                        time_range_days = 7  # 默认一周
                else:
                    time_range_days = 365  # 强制执行时扩大范围
                
                # 获取视频，所有规则共享同一个收集器的缓存
                videos = collector.get_videos_by_criteria(
                    min_rating=rule.min_rating,
                    min_comments=rule.min_comments,
                    is_hd=rule.is_hd,
                    is_zh=rule.is_zh,
                    is_uncensored=rule.is_uncensored,
                    days=time_range_days,
                    required_actor_id=rule.actor_id,
                    required_tags=rule.tags.split(',') if rule.tags and rule.tags.strip() else None,
                    exclude_tags=rule.exclude_tags.split(',') if rule.exclude_tags and rule.exclude_tags.strip() else None
                )
                
                logger.info(f"规则 [{rule.name}] 初步筛选得到 {len(videos)} 个视频")
                
                # 额外筛选（比如排除已订阅的）
                filtered_videos = self._filter_videos(rule, videos)
                logger.info(f"规则 [{rule.name}] 最终筛选得到 {len(filtered_videos)} 个待处理视频")
                
                if not filtered_videos:
                    logger.info(f"规则 [{rule.name}] 没有找到符合条件的新视频")
                    continue
                
                # 处理符合条件的视频
                rule_new_subscriptions = 0
                for video in filtered_videos:
                    try:
                        if self._create_subscription(rule, video):
                            rule_new_subscriptions += 1
                            new_subscriptions += 1
                    except Exception as e:
                        logger.error(f"处理视频 {video.get('num')} 时出错: {str(e)}")
                
                logger.info(f"规则 [{rule.name}] 执行完成，新增 {rule_new_subscriptions} 个订阅")
                processed_count += 1
                
            except Exception as e:
                logger.error(f"执行规则 [{rule.name}] 时出错: {str(e)}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"规则执行完成，共处理 {processed_count} 个规则，新增 {new_subscriptions} 个订阅")
        return {
            'message': f'规则执行完成，共处理 {processed_count} 个规则，新增 {new_subscriptions} 个订阅',
            'processed_count': processed_count,
            'new_subscriptions': new_subscriptions
        }

    def _get_candidate_videos(self, rule: AutoDownloadRule, force: bool = False) -> List[Dict[str, Any]]:
        """获取候选视频"""
        try:
            logger.info(f"获取候选视频 - 规则: {rule.name}")
            
            # 创建视频收集器实例
            collector = VideoCollector()
            
            # 计算时间范围
            if not force:
                if rule.time_range_type == TimeRangeType.DAY:
                    time_range_days = rule.time_range_value
                elif rule.time_range_type == TimeRangeType.WEEK:
                    time_range_days = rule.time_range_value * 7
                elif rule.time_range_type == TimeRangeType.MONTH:
                    time_range_days = rule.time_range_value * 30
                else:
                    time_range_days = 7  # 默认一周
            else:
                time_range_days = 365  # 强制执行时扩大范围
            
            # 使用视频收集器获取符合条件的视频
            videos = collector.get_videos_by_criteria(
                min_rating=float(rule.min_rating) if rule.min_rating else None,
                min_comments=rule.min_comments if rule.min_comments else None,
                is_hd=rule.is_hd,
                is_zh=rule.is_zh,
                is_uncensored=rule.is_uncensored,
                days=time_range_days
            )
            
            logger.info(f"获取到 {len(videos)} 个候选视频")
            return videos
        except Exception as e:
            logger.error(f"获取候选视频出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return []

    def _filter_videos(self, rule: AutoDownloadRule, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """筛选符合条件的视频"""
        filtered_videos = []
        
        for video in videos:
            # 记录视频信息
            logger.debug(f"过滤视频: {video.get('num')}, 标题: {video.get('title')}")
            
            # 如果视频已经被标记为详情获取失败，暂时保留
            if video.get('detail_missing', False):
                logger.warning(f"视频 {video.get('num')} 的详细信息获取失败，暂时保留并稍后重试获取详情")
                filtered_videos.append(video)
                continue
            
            # 视频收集器已经应用了基础过滤条件，此处只检查是否已经订阅
            # 检查是否已经订阅过
            existing_subscription = self.db.query(AutoDownloadSubscription).filter(
                and_(
                    AutoDownloadSubscription.rule_id == rule.id,
                    AutoDownloadSubscription.num == video.get('num')
                )
            ).first()
            
            if existing_subscription:
                logger.debug(f"视频 {video.get('num')} 已经被此规则订阅过，状态: {existing_subscription.status}")
                continue
            
            # 通过所有检查，添加到结果
            filtered_videos.append(video)
        
        return filtered_videos

    def _create_subscription(self, rule: AutoDownloadRule, video: Dict[str, Any]) -> bool:
        """创建订阅记录"""
        try:
            num = video.get('num')
            title = video.get('title')
            logger.info(f"为规则 [{rule.name}] 创建新订阅: {num} - {title}")
            
            # 创建订阅记录
            subscription_data = {
                'rule_id': rule.id,
                'num': num,
                'title': title,
                'cover': video.get('cover'),
                'status': DownloadStatus.PENDING,
                'create_time': datetime.now()
            }
            
            # 查询是否已存在，避免重复
            existing = self.db.query(AutoDownloadSubscription).filter(
                and_(
                    AutoDownloadSubscription.rule_id == rule.id,
                    AutoDownloadSubscription.num == num
                )
            ).first()
            
            if existing:
                logger.warning(f"订阅已存在: {num}, 跳过创建")
                return False
                
            # 创建新订阅
            subscription = AutoDownloadSubscription(**subscription_data)
            self.db.add(subscription)
            self.db.commit()
            
            logger.info(f"成功创建订阅: {num}")
            return True
            
        except Exception as e:
            logger.error(f"创建订阅记录时出错: {str(e)}")
            return False

    @staticmethod
    def job_auto_download():
        """自动下载定时任务"""
        try:
            logger.info("开始执行自动下载任务...")
            service = AutoDownloadService()
            result = service.execute_rules()
            
            # 处理待下载的订阅
            service._process_pending_subscriptions()
            
            logger.info(f"自动下载任务完成: {result.get('message')}")
            return result
        except Exception as e:
            logger.error(f"执行自动下载任务出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return {'message': f'执行出错: {str(e)}', 'processed_count': 0}

    def _process_pending_subscriptions(self):
        """处理待下载的订阅"""
        # 获取待下载的订阅
        pending_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            AutoDownloadSubscription.status == DownloadStatus.PENDING
        ).limit(10).all()  # 限制数量避免过载
        
        for subscription in pending_subscriptions:
            try:
                # 更新状态为下载中
                subscription.status = DownloadStatus.DOWNLOADING
                subscription.download_time = datetime.now()
                self.db.commit()
                
                # 获取视频详情和下载链接
                video_detail = spider.get_video(subscription.num)
                if not video_detail or not getattr(video_detail, 'downloads', []):
                    subscription.status = DownloadStatus.FAILED
                    self.db.commit()
                    continue
                
                # 筛选合适的下载链接
                rule = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.id == subscription.rule_id).first()
                suitable_download = self._find_suitable_download(rule, video_detail.downloads)
                
                if not suitable_download:
                    subscription.status = DownloadStatus.FAILED
                    self.db.commit()
                    continue
                
                # 调用现有的下载服务
                subscribe_service = SubscribeService()
                subscribe_data = schema.SubscribeCreate(
                    num=subscription.num,
                    title=subscription.title,
                    is_hd=rule.is_hd if rule else False,
                    is_zh=rule.is_zh if rule else False,
                    is_uncensored=rule.is_uncensored if rule else False
                )
                
                # 执行下载
                subscribe_service.download_video(subscribe_data, suitable_download)
                
                # 更新订阅状态
                subscription.status = DownloadStatus.COMPLETED
                subscription.download_url = getattr(suitable_download, 'magnet', None) or getattr(suitable_download, 'url', None)
                self.db.commit()
                
                logger.info(f"成功下载: {subscription.num}")
                
            except Exception as e:
                logger.error(f"处理订阅 {subscription.num} 时出错: {str(e)}")
                subscription.status = DownloadStatus.FAILED
                self.db.commit()
            
            # 添加延迟避免过于频繁
            time.sleep(randint(10, 30))

    def _find_suitable_download(self, rule: AutoDownloadRule, downloads: List[Any]) -> Optional[Any]:
        """找到合适的下载链接"""
        def matches_criteria(download):
            if rule and rule.is_hd and not getattr(download, 'is_hd', False):
                return False
            if rule and rule.is_zh and not getattr(download, 'is_zh', False):
                return False
            if rule and rule.is_uncensored and not getattr(download, 'is_uncensored', False):
                return False
            return True
        
        # 筛选符合条件的下载
        suitable_downloads = [d for d in downloads if matches_criteria(d)]
        
        if not suitable_downloads:
            return None
        
        # 返回第一个符合条件的下载
        return suitable_downloads[0]