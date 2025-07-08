"""
自动下载服务
"""
import traceback
from datetime import datetime, date
import time
from random import randint
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, func

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db, SessionFactory
from app.db.models.auto_download import AutoDownloadRule, AutoDownloadSubscription, DownloadStatus, TimeRangeType
from app.schema import subscribe as schema
from app.schema.auto_download import (
    AutoDownloadRuleQuery, 
    AutoDownloadListResponse, 
    AutoDownloadRuleResponse, 
    AutoDownloadStatistics, 
    AutoDownloadSubscriptionResponse,
    AutoDownloadSubscriptionQuery,
    AutoDownloadBatchOperation
)
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

    def __init__(self, db: Session = None):
        """初始化服务
        
        Args:
            db: 数据库会话，如果为None，则创建新会话
        """
        self.db = db or SessionFactory()
        self.download_service = DownloadService(db=self.db)
        self.subscribe_service = SubscribeService(db=self.db)
    
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
        
    def get_rules(self, query: AutoDownloadRuleQuery):
        """获取自动下载规则列表"""
        try:
            # 构建基本查询
            base_query = self.db.query(AutoDownloadRule)
            
            # 应用过滤条件
            if query.is_enabled is not None:
                base_query = base_query.filter(AutoDownloadRule.is_enabled == query.is_enabled)
                
            if query.name:
                base_query = base_query.filter(AutoDownloadRule.name.like(f"%{query.name}%"))
            
            # 计算总数
            total = base_query.count()
            
            # 应用分页
            rules = base_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
            
            # 计算总页数
            total_pages = (total + query.page_size - 1) // query.page_size if query.page_size > 0 else 0
            
            # 为每个规则添加统计信息
            rule_responses = []
            for rule in rules:
                # 获取订阅数量
                subscription_count = self.db.query(AutoDownloadSubscription).filter(
                    AutoDownloadSubscription.rule_id == rule.id
                ).count()
                
                # 获取成功下载数量
                success_count = self.db.query(AutoDownloadSubscription).filter(
                    AutoDownloadSubscription.rule_id == rule.id,
                    AutoDownloadSubscription.status == DownloadStatus.COMPLETED
                ).count()
                
                # 处理枚举值
                time_range_type_value = rule.time_range_type.value if rule.time_range_type else None
                
                # 构建响应对象
                rule_dict = {
                    "id": rule.id,
                    "name": rule.name,
                    "min_rating": rule.min_rating,
                    "min_comments": rule.min_comments,
                    "time_range_type": time_range_type_value,
                    "time_range_value": rule.time_range_value,
                    "is_hd": rule.is_hd,
                    "is_zh": rule.is_zh,
                    "is_uncensored": rule.is_uncensored,
                    "is_enabled": rule.is_enabled,
                    "created_at": rule.created_at or datetime.now(),
                    "updated_at": rule.updated_at or datetime.now(),
                    "subscription_count": subscription_count,
                    "success_count": success_count
                }
                rule_responses.append(AutoDownloadRuleResponse.model_validate(rule_dict))
            
            # 返回列表响应
            return AutoDownloadListResponse(
                items=rule_responses,
                total=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=total_pages
            )
        except Exception as e:
            logger.error(f"获取自动下载规则列表出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def get_subscriptions(self, query: AutoDownloadSubscriptionQuery):
        """获取自动下载订阅记录"""
        try:
            # 构建基本查询
            from sqlalchemy import func
            
            # 查询订阅记录和关联的规则名称
            base_query = self.db.query(
                AutoDownloadSubscription, 
                AutoDownloadRule.name.label('rule_name')
            ).outerjoin(
                AutoDownloadRule,
                AutoDownloadSubscription.rule_id == AutoDownloadRule.id
            )
            
            # 应用过滤条件
            if query.rule_id:
                base_query = base_query.filter(AutoDownloadSubscription.rule_id == query.rule_id)
                
            if query.status:
                # 将字符串状态转换为枚举值
                try:
                    enum_status = DownloadStatus[query.status.upper()]
                    base_query = base_query.filter(AutoDownloadSubscription.status == enum_status)
                except (KeyError, AttributeError):
                    pass  # 忽略无效状态
                
            if query.num:
                base_query = base_query.filter(AutoDownloadSubscription.num.like(f"%{query.num}%"))
                
            if query.start_date:
                base_query = base_query.filter(func.date(AutoDownloadSubscription.created_at) >= query.start_date)
                
            if query.end_date:
                base_query = base_query.filter(func.date(AutoDownloadSubscription.created_at) <= query.end_date)
            
            # 计算总数
            total = base_query.count()
            
            # 应用分页
            results = base_query.order_by(AutoDownloadSubscription.created_at.desc()).offset(
                (query.page - 1) * query.page_size
            ).limit(query.page_size).all()
            
            # 计算总页数
            total_pages = (total + query.page_size - 1) // query.page_size if query.page_size > 0 else 0
            
            # 构建响应列表
            subscription_responses = []
            for subscription, rule_name in results:
                # 处理枚举值
                status_value = subscription.status.value if subscription.status else None
                
                # 构建响应对象
                subscription_dict = {
                    "id": subscription.id,
                    "rule_id": subscription.rule_id,
                    "num": subscription.num,
                    "title": subscription.title,
                    "rating": subscription.rating,
                    "comments_count": subscription.comments_count,
                    "cover": subscription.cover,
                    "actors": subscription.actors,
                    "status": status_value,
                    "download_url": subscription.download_url,
                    "download_time": subscription.download_time,
                    "created_at": subscription.created_at,
                    "rule_name": rule_name
                }
                subscription_responses.append(AutoDownloadSubscriptionResponse.model_validate(subscription_dict))
            
            # 返回列表响应
            return AutoDownloadListResponse(
                items=subscription_responses,
                total=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=total_pages
            )
        except Exception as e:
            logger.error(f"获取自动下载订阅记录出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def get_statistics(self):
        """获取自动下载统计信息"""
        try:
            # 获取规则统计
            total_rules = self.db.query(AutoDownloadRule).count()
            active_rules = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.is_enabled == True).count()
            
            # 获取订阅统计
            total_subscriptions = self.db.query(AutoDownloadSubscription).count()
            
            # 根据状态统计
            status_counts = {}
            for status in [DownloadStatus.PENDING, DownloadStatus.DOWNLOADING, DownloadStatus.COMPLETED, DownloadStatus.FAILED]:
                count = self.db.query(AutoDownloadSubscription).filter(
                    AutoDownloadSubscription.status == status
                ).count()
                status_counts[status] = count
            
            # 获取今日新增订阅
            today = date.today()
            today_subscriptions = self.db.query(AutoDownloadSubscription).filter(
                func.date(AutoDownloadSubscription.create_time) == today
            ).count()
            
            # 计算成功率
            success_rate = 0.0
            if total_subscriptions > 0:
                success_rate = round(status_counts.get(DownloadStatus.COMPLETED, 0) / total_subscriptions * 100, 2)
            
            # 构建统计响应
            return AutoDownloadStatistics(
                total_rules=total_rules,
                active_rules=active_rules,
                total_subscriptions=total_subscriptions,
                pending_subscriptions=status_counts.get(DownloadStatus.PENDING, 0),
                downloading_subscriptions=status_counts.get(DownloadStatus.DOWNLOADING, 0),
                completed_subscriptions=status_counts.get(DownloadStatus.COMPLETED, 0),
                failed_subscriptions=status_counts.get(DownloadStatus.FAILED, 0),
                today_subscriptions=today_subscriptions,
                success_rate=success_rate
            )
        except Exception as e:
            logger.error(f"获取统计信息出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def delete_rule(self, rule_id: int):
        """删除自动下载规则"""
        try:
            rule = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.id == rule_id).first()
            if not rule:
                raise ValueError(f"规则ID {rule_id} 不存在")
                
            # 删除规则前先删除关联的订阅
            self.db.query(AutoDownloadSubscription).filter(
                AutoDownloadSubscription.rule_id == rule_id
            ).delete()
            
            # 删除规则
            self.db.delete(rule)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除规则出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def delete_subscription(self, subscription_id: int):
        """删除自动下载订阅记录"""
        try:
            subscription = self.db.query(AutoDownloadSubscription).filter(
                AutoDownloadSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                raise ValueError(f"订阅ID {subscription_id} 不存在")
                
            self.db.delete(subscription)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除订阅记录出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def batch_operation(self, operation: AutoDownloadBatchOperation):
        """批量操作订阅记录"""
        result = {
            'success_count': 0,
            'failed_count': 0,
            'failed_ids': []
        }
        
        try:
            for subscription_id in operation.ids:
                try:
                    subscription = self.db.query(AutoDownloadSubscription).filter(
                        AutoDownloadSubscription.id == subscription_id
                    ).first()
                    
                    if not subscription:
                        raise ValueError(f"订阅ID {subscription_id} 不存在")
                    
                    if operation.action == 'delete':
                        # 删除订阅
                        self.db.delete(subscription)
                        result['success_count'] += 1
                    elif operation.action == 'retry':
                        # 重试订阅，将状态设为待处理
                        subscription.status = DownloadStatus.PENDING
                        result['success_count'] += 1
                    elif operation.action == 'pause':
                        # 暂停订阅，暂时没有暂停状态，可以自定义
                        # 这里暂时不做处理
                        result['success_count'] += 1
                    elif operation.action == 'resume':
                        # 恢复订阅，如果是失败状态则恢复为待处理
                        if subscription.status == DownloadStatus.FAILED:
                            subscription.status = DownloadStatus.PENDING
                        result['success_count'] += 1
                except Exception as e:
                    logger.error(f"批量操作订阅记录 {subscription_id} 出错: {str(e)}")
                    result['failed_count'] += 1
                    result['failed_ids'].append(subscription_id)
            
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量操作订阅记录出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def update_rule(self, rule_data):
        """更新自动下载规则"""
        try:
            rule = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.id == rule_data.id).first()
            if not rule:
                raise ValueError(f"规则ID {rule_data.id} 不存在")
            
            # 更新非空字段
            if rule_data.name is not None:
                rule.name = rule_data.name
            if rule_data.min_rating is not None:
                rule.min_rating = rule_data.min_rating
            if rule_data.min_comments is not None:
                rule.min_comments = rule_data.min_comments
            if rule_data.time_range_type is not None:
                rule.time_range_type = rule_data.time_range_type
            if rule_data.time_range_value is not None:
                rule.time_range_value = rule_data.time_range_value
            if rule_data.is_hd is not None:
                rule.is_hd = rule_data.is_hd
            if rule_data.is_zh is not None:
                rule.is_zh = rule_data.is_zh
            if rule_data.is_uncensored is not None:
                rule.is_uncensored = rule_data.is_uncensored
            if rule_data.is_enabled is not None:
                rule.is_enabled = rule_data.is_enabled
                
            rule.updated_at = datetime.now()
            self.db.commit()
            return rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新规则出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
            
    def create_rule(self, rule_data):
        """创建自动下载规则"""
        try:
            # 检查名称是否重复
            existing_rule = self.db.query(AutoDownloadRule).filter(
                AutoDownloadRule.name == rule_data.name
            ).first()
            if existing_rule:
                raise ValueError(f"规则名称 '{rule_data.name}' 已存在")
            
            # 创建规则
            now = datetime.now()
            rule = AutoDownloadRule(
                name=rule_data.name,
                min_rating=rule_data.min_rating,
                min_comments=rule_data.min_comments,
                time_range_type=rule_data.time_range_type,
                time_range_value=rule_data.time_range_value,
                is_hd=rule_data.is_hd,
                is_zh=rule_data.is_zh,
                is_uncensored=rule_data.is_uncensored,
                is_enabled=rule_data.is_enabled,
                created_at=now,
                updated_at=now
            )
            
            self.db.add(rule)
            self.db.commit()
            return rule
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建规则出错: {str(e)}")
            logger.debug(traceback.format_exc())
            raise