from typing import List, Dict

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.db.models import Torrent, Subscribe, History
from app.db.models.actor_subscribe import ActorSubscribeDownload
from app.db.models.enums import SubscribeStatus, HistoryStatus
from app.service.base import BaseService
from app.utils.logger import logger


def get_download_status_service(db: Session = Depends(get_db)):
    """依赖注入函数，用于获取 DownloadStatusService 实例"""
    return DownloadStatusService(db=db)


class DownloadStatusService(BaseService):
    """下载状态检测服务

    用于批量检查番号是否已经被下载过，支持从以下表中检查：
    1. torrent 表 - 种子下载记录
    2. actor_subscribe_download 表 - 演员订阅下载记录
    3. subscribe 表 - 订阅记录（SubscribeStatus.COMPLETED 表示已完成）
    4. history 表 - 历史记录（HistoryStatus.SUCCESS 表示成功）
    """

    def __init__(self, db: Session):
        """初始化服务
        
        Args:
            db: SQLAlchemy Session 实例
        """
        super().__init__(db)

    # 批量查询的最大数量限制
    MAX_BATCH_SIZE = 100

    def check_download_status_batch(self, nums: List[str]) -> Dict[str, bool]:
        """批量检查番号的下载状态
        
        Args:
            nums: 番号列表
            
        Returns:
            Dict[str, bool]: 番号到下载状态的映射，True 表示已下载，False 表示未下载
            
        Example:
            >>> service.check_download_status_batch(['IPX-001', 'ABW-123'])
            {'IPX-001': True, 'ABW-123': False}
        """
        if not nums:
            return {}

        # 如果数量超过限制，分批处理
        if len(nums) > self.MAX_BATCH_SIZE:
            logger.warning(f"批量查询数量 {len(nums)} 超过限制 {self.MAX_BATCH_SIZE}，将分批处理")
            result = {}
            for i in range(0, len(nums), self.MAX_BATCH_SIZE):
                batch = nums[i:i + self.MAX_BATCH_SIZE]
                batch_result = self._check_batch_internal(batch)
                result.update(batch_result)
            return result
        
        return self._check_batch_internal(nums)

    def _check_batch_internal(self, nums: List[str]) -> Dict[str, bool]:
        """内部批量检查方法（单批次）
        
        Args:
            nums: 番号列表（已确保数量在限制内）
            
        Returns:
            Dict[str, bool]: 番号到下载状态的映射
        """
        # 将所有番号转为大写，用于统一比较
        upper_nums = [num.upper() for num in nums]

        # 创建番号到原始番号列表的映射（保持返回结果的键与输入一致，支持重复的大小写变体）
        from collections import defaultdict
        num_mapping = defaultdict(list)
        for num in nums:
            num_mapping[num.upper()].append(num)

        logger.debug(f"开始批量检查 {len(nums)} 个番号的下载状态")

        # 初始化所有番号的状态为未下载
        result = {num: False for num in nums}
        
        try:
            # 使用 UNION 优化查询，一次性从所有表中获取已下载的番号
            from sqlalchemy import union_all
            
            # 构建 UNION 查询
            queries = [
                # 1. torrent 表
                self.db.query(func.upper(Torrent.num).label('num')).filter(
                    func.upper(Torrent.num).in_(upper_nums)
                ),
                # 2. actor_subscribe_download 表
                self.db.query(func.upper(ActorSubscribeDownload.num).label('num')).filter(
                    func.upper(ActorSubscribeDownload.num).in_(upper_nums)
                ),
                # 3. subscribe 表（SubscribeStatus.COMPLETED 表示已完成）
                self.db.query(func.upper(Subscribe.num).label('num')).filter(
                    func.upper(Subscribe.num).in_(upper_nums),
                    Subscribe.status == SubscribeStatus.COMPLETED
                ),
                # 4. history 表（HistoryStatus.SUCCESS 表示成功）
                self.db.query(func.upper(History.num).label('num')).filter(
                    func.upper(History.num).in_(upper_nums),
                    History.status == HistoryStatus.SUCCESS
                )
            ]
            
            # 合并所有查询
            union_query = union_all(*queries)
            downloaded_nums = set([row.num for row in self.db.execute(union_query)])
            
            logger.debug(f"从数据库查询到 {len(downloaded_nums)} 个已下载番号")
            
            # 更新结果字典
            for upper_num in downloaded_nums:
                if upper_num in num_mapping:
                    # 将所有大小写变体都标记为已下载
                    for original_num in num_mapping[upper_num]:
                        result[original_num] = True

            downloaded_count = sum(result.values())
            logger.debug(f"批量检查完成：{downloaded_count}/{len(nums)} 个番号已下载")
            
        except Exception as e:
            logger.error(f"批量检查下载状态时发生错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # 发生错误时，保持所有状态为 False
        
        return result

    def check_download_status(self, num: str) -> bool:
        """检查单个番号的下载状态
        
        Args:
            num: 番号
            
        Returns:
            bool: True 表示已下载，False 表示未下载
            
        Example:
            >>> service.check_download_status('IPX-001')
            True
        """
        result = self.check_download_status_batch([num])
        return result.get(num, False)

    def get_downloaded_nums_from_list(self, nums: List[str]) -> List[str]:
        """从给定的番号列表中筛选出已下载的番号
        
        Args:
            nums: 番号列表
            
        Returns:
            List[str]: 已下载的番号列表
            
        Example:
            >>> service.get_downloaded_nums_from_list(['IPX-001', 'ABW-123', 'IPX-002'])
            ['IPX-001', 'IPX-002']
        """
        status_dict = self.check_download_status_batch(nums)
        return [num for num, is_downloaded in status_dict.items() if is_downloaded]

    def get_not_downloaded_nums_from_list(self, nums: List[str]) -> List[str]:
        """从给定的番号列表中筛选出未下载的番号
        
        Args:
            nums: 番号列表
            
        Returns:
            List[str]: 未下载的番号列表
            
        Example:
            >>> service.get_not_downloaded_nums_from_list(['IPX-001', 'ABW-123', 'IPX-002'])
            ['ABW-123']
        """
        status_dict = self.check_download_status_batch(nums)
        return [num for num, is_downloaded in status_dict.items() if not is_downloaded]
