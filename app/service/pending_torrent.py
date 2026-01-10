"""
待处理种子服务
处理异步元数据获取和过滤逻辑
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db, SessionFactory
from app.db.models.pending_torrent import PendingTorrent, PendingTorrentStatus
from app.service.base import BaseService
from app.service.download_filter import DownloadFilterService
from app.utils.qbittorent import qbittorent
from app.utils.logger import logger


def get_pending_torrent_service(db: Session = Depends(get_db)):
    """获取待处理种子服务实例"""
    return PendingTorrentService(db=db)


class PendingTorrentService(BaseService):
    """待处理种子服务"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.qb = qbittorent
        self.filter_service = DownloadFilterService(db)

    def add_pending_torrent(
        self,
        torrent_hash: str,
        magnet: str,
        savepath: str,
        category: Optional[str],
        num: Optional[str],
        source: str
    ) -> PendingTorrent:
        """
        添加到待处理队列

        Args:
            torrent_hash: 种子哈希值
            magnet: 磁力链接
            savepath: 保存路径
            category: 分类
            num: 番号
            source: 来源 (subscribe/auto_download/manual)

        Returns:
            PendingTorrent: 创建的待处理种子记录
        """
        # 检查是否已存在
        existing = self.get_pending_torrent(torrent_hash)
        if existing:
            logger.info(f"待处理种子已存在: {torrent_hash}")
            return existing

        try:
            pending = PendingTorrent(
                torrent_hash=torrent_hash,
                magnet=magnet,
                savepath=savepath,
                category=category,
                num=num,
                source=source,
                status=PendingTorrentStatus.WAITING_METADATA,
                retry_count=0,
                added_at=datetime.now()
            )
            self.db.add(pending)
            self.db.commit()
            self.db.refresh(pending)

            logger.info(f"添加待处理种子: hash={torrent_hash}, num={num}, source={source}")
            return pending
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加待处理种子失败: {e}")
            raise

    def get_pending_torrent(self, torrent_hash: str) -> Optional[PendingTorrent]:
        """
        根据 hash 获取待处理种子

        Args:
            torrent_hash: 种子哈希值

        Returns:
            PendingTorrent: 待处理种子记录，不存在则返回 None
        """
        return self.db.query(PendingTorrent).filter(
            PendingTorrent.torrent_hash == torrent_hash
        ).first()

    def update_status(
        self,
        torrent_hash: str,
        status: PendingTorrentStatus,
        error_message: Optional[str] = None,
        filter_result: Optional[Dict] = None
    ) -> Optional[PendingTorrent]:
        """
        更新状态

        Args:
            torrent_hash: 种子哈希值
            status: 新状态
            error_message: 错误信息
            filter_result: 过滤结果

        Returns:
            PendingTorrent: 更新后的记录
        """
        pending = self.get_pending_torrent(torrent_hash)
        if not pending:
            logger.warning(f"待处理种子不存在: {torrent_hash}")
            return None

        try:
            pending.status = status
            pending.last_check_at = datetime.now()

            if error_message:
                pending.error_message = error_message

            if filter_result:
                pending.filter_result = json.dumps(filter_result, ensure_ascii=False)
                pending.file_count = filter_result.get('original_files', 0)
                pending.filtered_file_count = filter_result.get('filtered_files', 0)

            if status in (PendingTorrentStatus.COMPLETED, PendingTorrentStatus.FAILED,
                          PendingTorrentStatus.TIMEOUT):
                pending.completed_at = datetime.now()

            self.db.commit()
            self.db.refresh(pending)

            logger.debug(f"更新待处理种子状态: hash={torrent_hash}, status={status.value}")
            return pending
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新待处理种子状态失败: {e}")
            raise

    def _get_torrent_info(self, torrent_hash: str) -> Optional[Dict]:
        """
        从 qBittorrent 获取种子信息

        Args:
            torrent_hash: 种子哈希值

        Returns:
            Dict: 种子信息，不存在则返回 None
        """
        try:
            response = self.qb.get_all_torrents()
            if hasattr(response, 'json'):
                if response.status_code != 200:
                    logger.error(f"获取种子列表失败: HTTP {response.status_code}")
                    return None
                torrents = response.json()
            else:
                torrents = response

            for torrent in torrents:
                if torrent.get('hash', '').lower() == torrent_hash.lower():
                    return torrent

            return None
        except Exception as e:
            logger.error(f"获取种子信息失败: {e}")
            return None

    def _is_metadata_ready(self, torrent_info: Dict) -> bool:
        """
        检查元数据是否就绪

        qBittorrent 中，当元数据就绪时：
        1. content_path 不为空且不等于 save_path
        2. 或者可以获取到文件列表

        Args:
            torrent_info: 种子信息

        Returns:
            bool: 元数据就绪返回 True
        """
        content_path = torrent_info.get('content_path', '')
        save_path = torrent_info.get('save_path', '')
        name = torrent_info.get('name', '')

        # 如果 content_path 存在且不等于 save_path，说明元数据已就绪
        if content_path and content_path != save_path:
            return True

        # 如果有具体的种子名称（不是 hash），也说明元数据已就绪
        torrent_hash = torrent_info.get('hash', '')
        if name and name.lower() != torrent_hash.lower():
            return True

        return False

    def check_metadata_and_filter(self, pending: PendingTorrent) -> bool:
        """
        检查单个种子元数据并过滤

        Args:
            pending: 待处理种子记录

        Returns:
            bool: 处理是否完成（完成/失败/超时都返回 True）
        """
        torrent_hash = pending.torrent_hash

        # 增加重试次数
        pending.retry_count += 1
        pending.last_check_at = datetime.now()
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新重试次数失败: {e}")
            return False

        try:
            # 1. 获取 qBittorrent 中的种子信息
            torrent_info = self._get_torrent_info(torrent_hash)

            if not torrent_info:
                logger.warning(f"种子不存在于 qBittorrent 中: {torrent_hash}")
                self.update_status(
                    torrent_hash,
                    PendingTorrentStatus.FAILED,
                    error_message="种子不存在于下载器中"
                )
                return True

            # 2. 检查元数据是否就绪
            if not self._is_metadata_ready(torrent_info):
                logger.debug(f"种子元数据未就绪: {torrent_hash}, 重试次数: {pending.retry_count}")
                return False

            # 3. 元数据就绪，更新状态为 METADATA_READY
            pending.status = PendingTorrentStatus.METADATA_READY

            # 获取总大小
            total_size = torrent_info.get('total_size', 0)
            pending.total_size_bytes = total_size

            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                logger.error(f"更新元数据状态失败: {e}")
                return False
            logger.info(f"种子元数据已就绪: {torrent_hash}, 大小: {total_size}")

            # 4. 更新状态为 FILTERING 并应用过滤规则
            pending.status = PendingTorrentStatus.FILTERING
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                logger.error(f"更新过滤状态失败: {e}")
                return False

            filter_result = self.filter_service.filter_torrent_files(torrent_hash)

            # 5. 根据过滤结果更新状态
            if filter_result.get('success'):
                # 过滤成功，恢复下载
                self.qb.resume_torrent(torrent_hash)
                self.update_status(
                    torrent_hash,
                    PendingTorrentStatus.COMPLETED,
                    filter_result=filter_result
                )
                logger.info(f"种子过滤完成并开始下载: {torrent_hash}, {filter_result.get('message', '')}")
            else:
                # 过滤失败，删除种子
                logger.warning(f"种子过滤失败: {torrent_hash}, {filter_result.get('message', '')}")
                try:
                    self.qb.delete_torrent(torrent_hash, delete_files=True)
                    logger.info(f"已删除不符合过滤条件的种子: {torrent_hash}")
                except Exception as e:
                    logger.error(f"删除种子失败: {e}")

                self.update_status(
                    torrent_hash,
                    PendingTorrentStatus.FAILED,
                    error_message=filter_result.get('message', '过滤失败'),
                    filter_result=filter_result
                )

            return True

        except Exception as e:
            logger.error(f"处理待处理种子时出错: {torrent_hash}, 错误: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def process_pending_torrents(self) -> Dict:
        """
        批量处理待处理种子（后台任务调用）

        Returns:
            Dict: 处理结果统计
        """
        stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'timeout': 0,
            'still_waiting': 0
        }

        # 查询所有 WAITING_METADATA 状态的种子
        pending_list = self.db.query(PendingTorrent).filter(
            PendingTorrent.status == PendingTorrentStatus.WAITING_METADATA
        ).all()

        stats['total'] = len(pending_list)

        if not pending_list:
            return stats

        logger.info(f"开始处理 {len(pending_list)} 个待处理种子")

        for pending in pending_list:
            # 检查是否超过最大重试次数
            if pending.retry_count >= pending.max_retries:
                logger.warning(f"种子超时: {pending.torrent_hash}, 重试次数: {pending.retry_count}")
                self.update_status(
                    pending.torrent_hash,
                    PendingTorrentStatus.TIMEOUT,
                    error_message=f"元数据获取超时，已重试 {pending.retry_count} 次"
                )
                # 超时后删除种子
                try:
                    self.qb.delete_torrent(pending.torrent_hash, delete_files=True)
                    logger.info(f"已删除超时种子: {pending.torrent_hash}")
                except Exception as e:
                    logger.error(f"删除超时种子失败: {e}")
                stats['timeout'] += 1
                continue

            # 处理单个种子
            completed = self.check_metadata_and_filter(pending)

            if completed:
                # 重新获取状态（可能在 check_metadata_and_filter 中被更新）
                self.db.refresh(pending)
                if pending.status == PendingTorrentStatus.COMPLETED:
                    stats['completed'] += 1
                elif pending.status in (PendingTorrentStatus.FAILED, PendingTorrentStatus.TIMEOUT):
                    stats['failed'] += 1
            else:
                stats['still_waiting'] += 1

        logger.info(f"待处理种子处理完成: {stats}")
        return stats

    def get_pending_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            Dict: 统计信息
        """
        stats = {}

        # 各状态数量统计
        status_counts = self.db.query(
            PendingTorrent.status,
            func.count(PendingTorrent.id)
        ).group_by(PendingTorrent.status).all()

        for status, count in status_counts:
            stats[status.value] = count

        # 确保所有状态都有值
        for status_enum in PendingTorrentStatus:
            if status_enum.value not in stats:
                stats[status_enum.value] = 0

        # 来源统计
        source_counts = self.db.query(
            PendingTorrent.source,
            func.count(PendingTorrent.id)
        ).group_by(PendingTorrent.source).all()

        stats['by_source'] = {source: count for source, count in source_counts if source}

        # 总数
        stats['total'] = self.db.query(func.count(PendingTorrent.id)).scalar() or 0

        # 今日新增
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats['today_added'] = self.db.query(func.count(PendingTorrent.id)).filter(
            PendingTorrent.added_at >= today_start
        ).scalar() or 0

        # 今日完成
        stats['today_completed'] = self.db.query(func.count(PendingTorrent.id)).filter(
            PendingTorrent.completed_at >= today_start,
            PendingTorrent.status == PendingTorrentStatus.COMPLETED
        ).scalar() or 0

        return stats

    def cleanup_old_records(self, days: int = 7) -> int:
        """
        清理旧记录

        Args:
            days: 保留天数，超过这个天数的已完成/失败/超时记录将被删除

        Returns:
            int: 删除的记录数
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            # 只删除已完成、失败、超时的记录
            deleted_count = self.db.query(PendingTorrent).filter(
                PendingTorrent.status.in_([
                    PendingTorrentStatus.COMPLETED,
                    PendingTorrentStatus.FAILED,
                    PendingTorrentStatus.TIMEOUT
                ]),
                PendingTorrent.completed_at < cutoff_date
            ).delete(synchronize_session=False)

            self.db.commit()

            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 条旧的待处理种子记录")

            return deleted_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"清理旧记录失败: {e}")
            raise

    def get_pending_list(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[PendingTorrent], int]:
        """
        获取待处理种子列表

        Args:
            status: 状态过滤
            page: 页码
            page_size: 每页数量

        Returns:
            tuple: (种子列表, 总数)
        """
        query = self.db.query(PendingTorrent)

        # 状态过滤
        if status:
            try:
                status_enum = PendingTorrentStatus(status)
                query = query.filter(PendingTorrent.status == status_enum)
            except ValueError:
                logger.warning(f"无效的状态值: {status}")

        # 获取总数
        total = query.count()

        # 分页并按添加时间倒序
        offset = (page - 1) * page_size
        items = query.order_by(PendingTorrent.added_at.desc()).offset(offset).limit(page_size).all()

        return items, total

    def get_by_hash(self, torrent_hash: str) -> Optional[PendingTorrent]:
        """
        根据hash获取待处理种子（get_pending_torrent 的别名）

        Args:
            torrent_hash: 种子哈希

        Returns:
            PendingTorrent: 待处理种子对象
        """
        return self.get_pending_torrent(torrent_hash)

    def retry_pending(self, torrent_hash: str) -> Optional[PendingTorrent]:
        """
        重试失败的种子

        Args:
            torrent_hash: 种子哈希

        Returns:
            PendingTorrent: 更新后的对象，如果不存在返回None
        """
        pending = self.get_pending_torrent(torrent_hash)
        if not pending:
            return None

        # 只有失败或超时状态才能重试
        if pending.status not in [PendingTorrentStatus.FAILED, PendingTorrentStatus.TIMEOUT]:
            logger.warning(f"种子 {torrent_hash} 状态为 {pending.status.value}，无法重试")
            return None

        try:
            # 重置状态
            pending.status = PendingTorrentStatus.WAITING_METADATA
            pending.retry_count = 0
            pending.error_message = None
            pending.last_check_at = None

            self.db.commit()
            self.db.refresh(pending)

            logger.info(f"重试待处理种子: {torrent_hash}")
            return pending
        except Exception as e:
            self.db.rollback()
            logger.error(f"重试待处理种子失败: {e}")
            raise

    def delete_pending(self, torrent_hash: str) -> bool:
        """
        删除待处理记录

        Args:
            torrent_hash: 种子哈希

        Returns:
            bool: 是否删除成功
        """
        pending = self.get_pending_torrent(torrent_hash)
        if not pending:
            return False

        try:
            self.db.delete(pending)
            self.db.commit()

            logger.info(f"删除待处理种子记录: {torrent_hash}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除待处理种子记录失败: {e}")
            raise

    def pending_to_dict(self, pending: PendingTorrent) -> Dict:
        """
        将PendingTorrent对象转换为字典

        Args:
            pending: PendingTorrent对象

        Returns:
            Dict: 字典表示
        """
        return {
            "id": pending.id,
            "torrent_hash": pending.torrent_hash,
            "magnet": pending.magnet,
            "savepath": pending.savepath,
            "category": pending.category,
            "num": pending.num,
            "source": pending.source,
            "status": pending.status.value,
            "retry_count": pending.retry_count,
            "max_retries": pending.max_retries,
            "filter_result": pending.filter_result,
            "error_message": pending.error_message,
            "added_at": pending.added_at.isoformat() if pending.added_at else None,
            "last_check_at": pending.last_check_at.isoformat() if pending.last_check_at else None,
            "completed_at": pending.completed_at.isoformat() if pending.completed_at else None,
            "file_count": pending.file_count,
            "total_size_bytes": pending.total_size_bytes,
            "filtered_file_count": pending.filtered_file_count,
        }

    @classmethod
    def job_process_pending_torrents(cls) -> dict:
        """
        后台任务入口（类方法）
        处理待处理种子队列
        
        Returns:
            dict: 处理统计信息 {'processed': int, 'completed': int, 'failed': int, 'timeout': int}
        """
        stats = {'processed': 0, 'completed': 0, 'failed': 0, 'timeout': 0}
        try:
            with SessionFactory() as db:
                service = cls(db=db)
                result = service.process_pending_torrents()
                stats = {
                    'processed': result.get('total', 0),
                    'completed': result.get('completed', 0),
                    'failed': result.get('failed', 0),
                    'timeout': result.get('timeout', 0)
                }
                if stats['processed'] > 0:
                    logger.info(f"待处理种子任务完成: {stats}")
        except Exception as e:
            logger.error(f"待处理种子任务执行失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        return stats

    @classmethod
    def job_cleanup_pending_torrents(cls) -> int:
        """
        每日清理任务（类方法）
        清理超过 7 天的旧记录
        
        Returns:
            int: 删除的记录数量
        """
        deleted = 0
        try:
            with SessionFactory() as db:
                service = cls(db=db)
                deleted = service.cleanup_old_records(days=7)
                if deleted > 0:
                    logger.info(f"待处理种子清理任务完成: 删除 {deleted} 条记录")
        except Exception as e:
            logger.error(f"待处理种子清理任务执行失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        return deleted
