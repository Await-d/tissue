"""
自动下载业务逻辑服务
"""
import json
import time
import traceback
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from random import randint
from decimal import Decimal

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app import schema
from app.db import get_db, SessionFactory
from app.db.models.auto_download import AutoDownloadRule, AutoDownloadSubscription, DownloadStatus, TimeRangeType
from app.db.transaction import transaction
from app.exception import BizException
from app.service.base import BaseService
from app.service.subscribe import SubscribeService
from app.utils import spider
from app.utils.video_collector import video_collector
from app.utils.logger import logger


def get_auto_download_service(db: Session = Depends(get_db)):
    return AutoDownloadService(db=db)


class AutoDownloadService(BaseService):
    """自动下载服务"""

    # 规则管理
    def get_rules(self, query: schema.AutoDownloadRuleQuery) -> schema.AutoDownloadListResponse:
        """获取自动下载规则列表"""
        query_filter = []
        
        if query.is_enabled is not None:
            query_filter.append(AutoDownloadRule.is_enabled == query.is_enabled)
        
        if query.name:
            query_filter.append(AutoDownloadRule.name.like(f"%{query.name}%"))
        
        # 基础查询
        base_query = self.db.query(AutoDownloadRule)
        if query_filter:
            base_query = base_query.filter(and_(*query_filter))
        
        # 总数
        total = base_query.count()
        
        # 分页查询
        rules = base_query.offset((query.page - 1) * query.page_size).limit(query.page_size).all()
        
        # 添加统计信息
        rule_data = []
        for rule in rules:
            rule_dict = {
                'id': rule.id,
                'name': rule.name,
                'min_rating': rule.min_rating,
                'min_comments': rule.min_comments,
                'time_range_type': rule.time_range_type,
                'time_range_value': rule.time_range_value,
                'is_hd': rule.is_hd,
                'is_zh': rule.is_zh,
                'is_uncensored': rule.is_uncensored,
                'is_enabled': rule.is_enabled,
                'created_at': rule.created_at,
                'updated_at': rule.updated_at,
            }
            
            # 获取订阅统计
            subscription_count = self.db.query(AutoDownloadSubscription).filter(
                AutoDownloadSubscription.rule_id == rule.id
            ).count()
            
            success_count = self.db.query(AutoDownloadSubscription).filter(
                and_(
                    AutoDownloadSubscription.rule_id == rule.id,
                    AutoDownloadSubscription.status == DownloadStatus.COMPLETED
                )
            ).count()
            
            rule_dict['subscription_count'] = subscription_count
            rule_dict['success_count'] = success_count
            rule_data.append(rule_dict)
        
        return schema.AutoDownloadListResponse(
            items=rule_data,
            total=total,
            page=query.page,
            page_size=query.page_size
        )

    @transaction
    def create_rule(self, rule_data: schema.AutoDownloadRuleCreate) -> AutoDownloadRule:
        """创建自动下载规则"""
        # 检查规则名称是否重复
        existing_rule = self.db.query(AutoDownloadRule).filter(
            AutoDownloadRule.name == rule_data.name
        ).first()
        
        if existing_rule:
            raise BizException(f"规则名称 '{rule_data.name}' 已存在")
        
        # 转换数据
        rule_dict = rule_data.model_dump()
        # 确保枚举值处理正确
        if rule_dict.get('time_range_type') is not None:
            time_range_type = rule_dict['time_range_type']
            # 如果是枚举实例，保持原样
            if not isinstance(time_range_type, TimeRangeType):
                # 如果是字符串，尝试转换
                if isinstance(time_range_type, str):
                    time_range_type = time_range_type.upper()
                    if time_range_type == 'DAY':
                        rule_dict['time_range_type'] = TimeRangeType.DAY
                    elif time_range_type == 'WEEK':
                        rule_dict['time_range_type'] = TimeRangeType.WEEK
                    elif time_range_type == 'MONTH':
                        rule_dict['time_range_type'] = TimeRangeType.MONTH
                    else:
                        raise BizException(f"无效的时间范围类型: {time_range_type}")
        
        rule = AutoDownloadRule(**rule_dict)
        rule.add(self.db)
        
        logger.info(f"创建自动下载规则: {rule.name}")
        return rule

    @transaction
    def update_rule(self, rule_data: schema.AutoDownloadRuleUpdate) -> AutoDownloadRule:
        """更新自动下载规则"""
        rule = AutoDownloadRule.get(self.db, rule_data.id)
        if not rule:
            raise BizException("规则不存在")
        
        # 检查规则名称是否重复（排除自己）
        if rule_data.name and rule_data.name != rule.name:
            existing_rule = self.db.query(AutoDownloadRule).filter(
                and_(
                    AutoDownloadRule.name == rule_data.name,
                    AutoDownloadRule.id != rule_data.id
                )
            ).first()
            
            if existing_rule:
                raise BizException(f"规则名称 '{rule_data.name}' 已存在")
        
        # 更新字段
        update_data = {k: v for k, v in rule_data.model_dump().items() if v is not None and k != 'id'}
        
        # 确保枚举值处理正确
        if update_data.get('time_range_type') is not None:
            time_range_type = update_data['time_range_type']
            # 如果是枚举实例，保持原样
            if not isinstance(time_range_type, TimeRangeType):
                # 如果是字符串，尝试转换
                if isinstance(time_range_type, str):
                    time_range_type = time_range_type.upper()
                    if time_range_type == 'DAY':
                        update_data['time_range_type'] = TimeRangeType.DAY
                    elif time_range_type == 'WEEK':
                        update_data['time_range_type'] = TimeRangeType.WEEK
                    elif time_range_type == 'MONTH':
                        update_data['time_range_type'] = TimeRangeType.MONTH
                    else:
                        raise BizException(f"无效的时间范围类型: {time_range_type}")
        
        rule.update(self.db, update_data)
        
        logger.info(f"更新自动下载规则: {rule.name}")
        return rule

    @transaction
    def delete_rule(self, rule_id: int) -> bool:
        """删除自动下载规则"""
        rule = AutoDownloadRule.get(self.db, rule_id)
        if not rule:
            raise BizException("规则不存在")
        
        rule.delete(self.db)
        logger.info(f"删除自动下载规则: {rule.name}")
        return True

    # 订阅记录管理
    def get_subscriptions(self, query: schema.AutoDownloadSubscriptionQuery) -> schema.AutoDownloadListResponse:
        """获取自动下载订阅记录列表"""
        query_filter = []
        
        if query.rule_id:
            query_filter.append(AutoDownloadSubscription.rule_id == query.rule_id)
        
        if query.status:
            query_filter.append(AutoDownloadSubscription.status == query.status)
        
        if query.num:
            query_filter.append(AutoDownloadSubscription.num.like(f"%{query.num}%"))
        
        if query.start_date:
            query_filter.append(AutoDownloadSubscription.created_at >= query.start_date)
        
        if query.end_date:
            query_filter.append(AutoDownloadSubscription.created_at <= query.end_date + timedelta(days=1))
        
        # 联表查询
        base_query = self.db.query(AutoDownloadSubscription, AutoDownloadRule.name).join(
            AutoDownloadRule, AutoDownloadSubscription.rule_id == AutoDownloadRule.id
        )
        
        if query_filter:
            base_query = base_query.filter(and_(*query_filter))
        
        # 总数
        total = base_query.count()
        
        # 分页查询
        results = base_query.order_by(desc(AutoDownloadSubscription.created_at)).offset(
            (query.page - 1) * query.page_size
        ).limit(query.page_size).all()
        
        # 构造响应数据
        subscription_data = []
        for subscription, rule_name in results:
            subscription_dict = {
                'id': subscription.id,
                'rule_id': subscription.rule_id,
                'rule_name': rule_name,
                'num': subscription.num,
                'title': subscription.title,
                'rating': subscription.rating,
                'comments_count': subscription.comments_count,
                'cover': subscription.cover,
                'actors': subscription.actors,
                'status': subscription.status,
                'download_url': subscription.download_url,
                'download_time': subscription.download_time,
                'created_at': subscription.created_at,
            }
            subscription_data.append(subscription_dict)
        
        return schema.AutoDownloadListResponse(
            items=subscription_data,
            total=total,
            page=query.page,
            page_size=query.page_size
        )

    @transaction
    def delete_subscription(self, subscription_id: int) -> bool:
        """删除订阅记录"""
        subscription = AutoDownloadSubscription.get(self.db, subscription_id)
        if not subscription:
            raise BizException("订阅记录不存在")
        
        subscription.delete(self.db)
        logger.info(f"删除订阅记录: {subscription.num}")
        return True

    @transaction
    def batch_operation(self, operation: schema.AutoDownloadBatchOperation) -> Dict[str, Any]:
        """批量操作"""
        success_count = 0
        failed_count = 0
        error_messages = []
        
        for subscription_id in operation.ids:
            try:
                subscription = AutoDownloadSubscription.get(self.db, subscription_id)
                if not subscription:
                    error_messages.append(f"订阅记录 {subscription_id} 不存在")
                    failed_count += 1
                    continue
                
                if operation.action == 'delete':
                    subscription.delete(self.db)
                elif operation.action == 'retry':
                    subscription.update(self.db, {
                        'status': DownloadStatus.PENDING,
                        'download_time': None
                    })
                else:
                    error_messages.append(f"不支持的操作类型: {operation.action}")
                    failed_count += 1
                    continue
                
                success_count += 1
                
            except Exception as e:
                error_messages.append(f"处理订阅记录 {subscription_id} 时出错: {str(e)}")
                failed_count += 1
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'error_messages': error_messages
        }

    # 统计信息
    def get_statistics(self) -> schema.AutoDownloadStatistics:
        """获取统计信息"""
        # 规则统计
        total_rules = self.db.query(AutoDownloadRule).count()
        active_rules = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.is_enabled == True).count()
        
        # 订阅统计
        total_subscriptions = self.db.query(AutoDownloadSubscription).count()
        pending_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            AutoDownloadSubscription.status == DownloadStatus.PENDING
        ).count()
        downloading_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            AutoDownloadSubscription.status == DownloadStatus.DOWNLOADING
        ).count()
        completed_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            AutoDownloadSubscription.status == DownloadStatus.COMPLETED
        ).count()
        failed_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            AutoDownloadSubscription.status == DownloadStatus.FAILED
        ).count()
        
        # 今日新增
        today = datetime.now().date()
        today_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            func.date(AutoDownloadSubscription.created_at) == today
        ).count()
        
        # 成功率
        success_rate = 0.0
        if total_subscriptions > 0:
            success_rate = (completed_subscriptions / total_subscriptions) * 100
        
        return schema.AutoDownloadStatistics(
            total_rules=total_rules,
            active_rules=active_rules,
            total_subscriptions=total_subscriptions,
            pending_subscriptions=pending_subscriptions,
            downloading_subscriptions=downloading_subscriptions,
            completed_subscriptions=completed_subscriptions,
            failed_subscriptions=failed_subscriptions,
            today_subscriptions=today_subscriptions,
            success_rate=round(success_rate, 2)
        )

    # 核心业务逻辑
    def execute_rules(self, rule_ids: Optional[List[int]] = None, force: bool = False) -> Dict[str, Any]:
        """执行自动下载规则"""
        # 获取要执行的规则
        query = self.db.query(AutoDownloadRule).filter(AutoDownloadRule.is_enabled == True)
        if rule_ids:
            query = query.filter(AutoDownloadRule.id.in_(rule_ids))
        
        rules = query.all()
        
        if not rules:
            return {'message': '没有找到要执行的规则', 'processed_count': 0}
        
        processed_count = 0
        new_subscriptions = 0
        
        for rule in rules:
            try:
                logger.info(f"执行自动下载规则: {rule.name}")
                
                # 获取候选视频列表
                candidate_videos = self._get_candidate_videos(rule, force)
                
                # 筛选符合条件的视频
                filtered_videos = self._filter_videos(rule, candidate_videos)
                
                # 创建订阅记录
                for video in filtered_videos:
                    if self._create_subscription(rule, video):
                        new_subscriptions += 1
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"执行规则 {rule.name} 时出错: {str(e)}")
                traceback.print_exc()
        
        return {
            'message': f'成功执行 {processed_count} 个规则，新增 {new_subscriptions} 个订阅',
            'processed_count': processed_count,
            'new_subscriptions': new_subscriptions
        }

    def _get_candidate_videos(self, rule: AutoDownloadRule, force: bool = False) -> List[Dict[str, Any]]:
        """获取候选视频列表"""
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
        
        candidate_videos = []
        
        try:
            logger.info(f"获取时间范围内的视频: 最近 {time_range_days} 天")
            
            # 使用视频收集器获取符合条件的视频
            videos = video_collector.get_videos_by_criteria(
                min_rating=float(rule.min_rating) if rule.min_rating else None,
                min_comments=rule.min_comments if rule.min_comments else None,
                time_range_days=time_range_days,
                is_hd=rule.is_hd,
                is_zh=rule.is_zh,
                is_uncensored=rule.is_uncensored
            )
            
            candidate_videos = videos
            logger.info(f"获取到 {len(candidate_videos)} 个候选视频")
            
        except Exception as e:
            logger.error(f"获取候选视频时出错: {str(e)}")
            traceback.print_exc()
        
        return candidate_videos

    def _filter_videos(self, rule: AutoDownloadRule, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """筛选符合条件的视频"""
        filtered_videos = []
        
        for video in videos:
            # 检查评分条件
            if rule.min_rating and video.get('rating', 0) < rule.min_rating:
                continue
            
            # 检查评论数条件
            if rule.min_comments and video.get('comments_count', 0) < rule.min_comments:
                continue
            
            # 检查其他条件
            if rule.is_hd and not video.get('is_hd', False):
                continue
            
            if rule.is_zh and not video.get('is_zh', False):
                continue
            
            if rule.is_uncensored and not video.get('is_uncensored', False):
                continue
            
            # 检查是否已经订阅过
            existing_subscription = self.db.query(AutoDownloadSubscription).filter(
                and_(
                    AutoDownloadSubscription.rule_id == rule.id,
                    AutoDownloadSubscription.num == video.get('num')
                )
            ).first()
            
            if existing_subscription:
                continue
            
            filtered_videos.append(video)
        
        return filtered_videos

    @transaction
    def _create_subscription(self, rule: AutoDownloadRule, video: Dict[str, Any]) -> bool:
        """创建订阅记录"""
        try:
            # 构造演员信息JSON
            actors_json = None
            if video.get('actors'):
                actors_json = json.dumps(video['actors'], ensure_ascii=False)
            
            subscription = AutoDownloadSubscription(
                rule_id=rule.id,
                num=video.get('num'),
                title=video.get('title'),
                rating=video.get('rating'),
                comments_count=video.get('comments_count', 0),
                cover=video.get('cover'),
                actors=actors_json,
                status=DownloadStatus.PENDING
            )
            
            subscription.add(self.db)
            
            logger.info(f"创建自动下载订阅: {subscription.num}")
            return True
            
        except Exception as e:
            logger.error(f"创建订阅记录时出错: {str(e)}")
            return False

    @classmethod
    def job_auto_download(cls):
        """定时任务：执行自动下载"""
        logger.info("开始执行自动下载任务")
        
        try:
            with SessionFactory() as db:
                service = cls(db=db)
                result = service.execute_rules()
                logger.info(f"自动下载任务完成: {result['message']}")
                
                # 处理待下载的订阅
                service._process_pending_subscriptions()
                
        except Exception as e:
            logger.error(f"自动下载任务执行失败: {str(e)}")
            traceback.print_exc()

    def _process_pending_subscriptions(self):
        """处理待下载的订阅"""
        # 获取待下载的订阅
        pending_subscriptions = self.db.query(AutoDownloadSubscription).filter(
            AutoDownloadSubscription.status == DownloadStatus.PENDING
        ).limit(10).all()  # 限制数量避免过载
        
        for subscription in pending_subscriptions:
            try:
                # 更新状态为下载中
                subscription.update(self.db, {
                    'status': DownloadStatus.DOWNLOADING,
                    'download_time': datetime.now()
                })
                
                # 获取视频详情和下载链接
                video_detail = spider.get_video(subscription.num)
                if not video_detail or not video_detail.downloads:
                    subscription.update(self.db, {'status': DownloadStatus.FAILED})
                    continue
                
                # 筛选合适的下载链接
                rule = AutoDownloadRule.get(self.db, subscription.rule_id)
                suitable_download = self._find_suitable_download(rule, video_detail.downloads)
                
                if not suitable_download:
                    subscription.update(self.db, {'status': DownloadStatus.FAILED})
                    continue
                
                # 调用现有的下载服务
                subscribe_service = SubscribeService(db=self.db)
                subscribe_data = schema.SubscribeCreate(
                    num=subscription.num,
                    title=subscription.title,
                    is_hd=rule.is_hd,
                    is_zh=rule.is_zh,
                    is_uncensored=rule.is_uncensored
                )
                
                # 执行下载
                subscribe_service.download_video(subscribe_data, suitable_download)
                
                # 更新订阅状态
                subscription.update(self.db, {
                    'status': DownloadStatus.COMPLETED,
                    'download_url': suitable_download.magnet or suitable_download.url
                })
                
                logger.info(f"成功下载: {subscription.num}")
                
            except Exception as e:
                logger.error(f"处理订阅 {subscription.num} 时出错: {str(e)}")
                subscription.update(self.db, {'status': DownloadStatus.FAILED})
            
            # 添加延迟避免过于频繁
            time.sleep(randint(10, 30))

    def _find_suitable_download(self, rule: AutoDownloadRule, downloads: List[Any]) -> Optional[Any]:
        """找到合适的下载链接"""
        def matches_criteria(download):
            if rule.is_hd and not download.is_hd:
                return False
            if rule.is_zh and not download.is_zh:
                return False
            if rule.is_uncensored and not download.is_uncensored:
                return False
            return True
        
        # 筛选符合条件的下载
        suitable_downloads = [d for d in downloads if matches_criteria(d)]
        
        if not suitable_downloads:
            return None
        
        # 返回第一个符合条件的下载
        return suitable_downloads[0]