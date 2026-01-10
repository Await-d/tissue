"""
下载状态检测服务的单元测试
"""
import pytest
from datetime import datetime, date

from app.service.download_status import DownloadStatusService
from app.db.models import Torrent, Subscribe, History
from app.db.models.actor_subscribe import ActorSubscribe, ActorSubscribeDownload
from app.db.models.enums import SubscribeStatus, HistoryStatus


class TestDownloadStatusService:
    """测试下载状态检测服务"""

    def test_check_status_returns_downloaded_for_torrent(self, db_session):
        """测试种子表中的番号返回 downloaded"""
        # 创建种子记录
        torrent = Torrent(
            hash='test_hash_001',
            num='TEST-001',
            is_zh=True,
            is_hd=True,
            is_uncensored=False
        )
        db_session.add(torrent)
        db_session.commit()

        # 检查状态
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['TEST-001'])

        assert result['TEST-001'] == 'downloaded'

    def test_check_status_returns_downloaded_for_actor_subscribe(self, db_session):
        """测试演员订阅下载表中的番号返回 downloaded"""
        # 创建演员订阅记录
        actor_subscribe = ActorSubscribe(
            actor_name='测试演员',
            from_date=date.today(),
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(actor_subscribe)
        db_session.flush()

        # 创建下载记录
        download = ActorSubscribeDownload(
            actor_subscribe_id=actor_subscribe.id,
            num='TEST-002',
            title='测试标题',
            download_time=datetime.now(),
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(download)
        db_session.commit()

        # 检查状态
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['TEST-002'])

        assert result['TEST-002'] == 'downloaded'

    def test_check_status_returns_downloaded_for_completed_subscribe(self, db_session):
        """测试订阅表中已完成的番号返回 downloaded"""
        subscribe = Subscribe(
            num='TEST-003',
            title='测试订阅',
            status=SubscribeStatus.COMPLETED,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(subscribe)
        db_session.commit()

        # 检查状态
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['TEST-003'])

        assert result['TEST-003'] == 'downloaded'

    def test_check_status_returns_downloading_for_pending_subscribe(self, db_session):
        """测试订阅表中待处理的番号返回 downloading"""
        subscribe = Subscribe(
            num='TEST-004',
            title='测试订阅',
            status=SubscribeStatus.PENDING,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(subscribe)
        db_session.commit()

        # 检查状态
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['TEST-004'])

        assert result['TEST-004'] == 'downloading'

    def test_check_status_returns_downloaded_for_history_success(self, db_session):
        """测试历史记录表中成功的番号返回 downloaded"""
        history = History(
            num='TEST-005',
            status=HistoryStatus.SUCCESS,
            source_path='/test/source',
            trans_method='move',
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(history)
        db_session.commit()

        # 检查状态
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['TEST-005'])

        assert result['TEST-005'] == 'downloaded'

    def test_check_status_returns_none_for_not_found(self, db_session):
        """测试不存在的番号返回 none"""
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['NOT-EXISTS'])

        assert result['NOT-EXISTS'] == 'none'

    def test_check_status_priority_downloaded_over_downloading(self, db_session):
        """测试状态优先级：downloaded 高于 downloading"""
        # 同时添加到 pending 和 completed 订阅
        subscribe_pending = Subscribe(
            num='TEST-006',
            title='测试订阅 - Pending',
            status=SubscribeStatus.PENDING,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        subscribe_completed = Subscribe(
            num='TEST-006',
            title='测试订阅 - Completed',
            status=SubscribeStatus.COMPLETED,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add_all([subscribe_pending, subscribe_completed])
        db_session.commit()

        # 检查状态
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['TEST-006'])

        # 应该返回 downloaded（优先级更高）
        assert result['TEST-006'] == 'downloaded'

    def test_check_status_case_insensitive(self, db_session):
        """测试番号大小写不敏感"""
        torrent = Torrent(
            hash='test_hash_007',
            num='TEST-007',
            is_zh=True,
            is_hd=True,
            is_uncensored=False
        )
        db_session.add(torrent)
        db_session.commit()

        # 使用小写查询
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['test-007'])

        assert result['test-007'] == 'downloaded'

    def test_check_batch_handles_empty_list(self, db_session):
        """测试空列表返回空字典"""
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch([])

        assert result == {}

    def test_check_batch_handles_multiple_nums(self, db_session):
        """测试批量检查多个番号"""
        # 创建多个记录
        torrent = Torrent(hash='hash1', num='MULTI-001', is_zh=True, is_hd=True, is_uncensored=False)
        subscribe = Subscribe(
            num='MULTI-002',
            title='订阅',
            status=SubscribeStatus.PENDING,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add_all([torrent, subscribe])
        db_session.commit()

        # 批量检查
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(['MULTI-001', 'MULTI-002', 'MULTI-003'])

        assert result['MULTI-001'] == 'downloaded'
        assert result['MULTI-002'] == 'downloading'
        assert result['MULTI-003'] == 'none'

    def test_check_batch_splits_large_batches(self, db_session):
        """测试大批量查询会自动分批"""
        # 创建超过限制数量的番号
        nums = [f'BATCH-{i:03d}' for i in range(150)]

        # 添加部分记录
        for i in range(0, 50):
            torrent = Torrent(
                hash=f'hash_{i}',
                num=nums[i],
                is_zh=True,
                is_hd=True,
                is_uncensored=False
            )
            db_session.add(torrent)
        db_session.commit()

        # 批量检查
        service = DownloadStatusService(db=db_session)
        result = service.check_download_status_batch(nums)

        # 验证返回了所有番号的状态
        assert len(result) == 150
        # 前50个应该是 downloaded
        for i in range(0, 50):
            assert result[nums[i]] == 'downloaded'
        # 后100个应该是 none
        for i in range(50, 150):
            assert result[nums[i]] == 'none'

    def test_check_download_status_single_returns_bool(self, db_session):
        """测试单个番号检查返回布尔值（向后兼容）"""
        torrent = Torrent(hash='hash', num='SINGLE-001', is_zh=True, is_hd=True, is_uncensored=False)
        db_session.add(torrent)
        db_session.commit()

        service = DownloadStatusService(db=db_session)

        # downloaded 应该返回 True
        assert service.check_download_status('SINGLE-001') is True
        # none 应该返回 False
        assert service.check_download_status('NOT-EXISTS') is False

    def test_check_download_status_single_downloading_returns_true(self, db_session):
        """测试单个番号检查 downloading 状态也返回 True"""
        subscribe = Subscribe(
            num='SINGLE-002',
            title='测试',
            status=SubscribeStatus.PENDING,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(subscribe)
        db_session.commit()

        service = DownloadStatusService(db=db_session)

        # downloading 应该返回 True（向后兼容）
        assert service.check_download_status('SINGLE-002') is True

    def test_check_download_status_detailed_returns_status(self, db_session):
        """测试详细状态检查返回具体状态字符串"""
        torrent = Torrent(hash='hash', num='DETAIL-001', is_zh=True, is_hd=True, is_uncensored=False)
        db_session.add(torrent)
        db_session.commit()

        service = DownloadStatusService(db=db_session)

        # 应该返回具体状态
        assert service.check_download_status_detailed('DETAIL-001') == 'downloaded'
        assert service.check_download_status_detailed('NOT-EXISTS') == 'none'

    def test_get_downloaded_nums_from_list(self, db_session):
        """测试筛选已下载的番号"""
        # 创建混合状态的记录
        torrent = Torrent(hash='hash1', num='FILTER-001', is_zh=True, is_hd=True, is_uncensored=False)
        subscribe = Subscribe(
            num='FILTER-002',
            title='订阅',
            status=SubscribeStatus.PENDING,
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add_all([torrent, subscribe])
        db_session.commit()

        service = DownloadStatusService(db=db_session)
        nums = ['FILTER-001', 'FILTER-002', 'FILTER-003']
        downloaded = service.get_downloaded_nums_from_list(nums)

        # downloaded 和 downloading 都应该被包含（向后兼容）
        assert 'FILTER-001' in downloaded
        assert 'FILTER-002' in downloaded
        assert 'FILTER-003' not in downloaded

    def test_get_not_downloaded_nums_from_list(self, db_session):
        """测试筛选未下载的番号"""
        torrent = Torrent(hash='hash1', num='NOTDOWN-001', is_zh=True, is_hd=True, is_uncensored=False)
        db_session.add(torrent)
        db_session.commit()

        service = DownloadStatusService(db=db_session)
        nums = ['NOTDOWN-001', 'NOTDOWN-002']
        not_downloaded = service.get_not_downloaded_nums_from_list(nums)

        assert 'NOTDOWN-001' not in not_downloaded
        assert 'NOTDOWN-002' in not_downloaded


class TestDownloadStatusServicePerformance:
    """性能测试"""

    def test_batch_query_performance(self, db_session):
        """测试批量查询的性能（确保使用 UNION 优化）"""
        # 创建大量记录
        torrents = []
        for i in range(100):
            torrents.append(Torrent(
                hash=f'perf_hash_{i}',
                num=f'PERF-{i:03d}',
                is_zh=True,
                is_hd=True,
                is_uncensored=False
            ))
        db_session.add_all(torrents)
        db_session.commit()

        # 批量查询
        service = DownloadStatusService(db=db_session)
        nums = [f'PERF-{i:03d}' for i in range(100)]

        import time
        start = time.time()
        result = service.check_download_status_batch(nums)
        elapsed = time.time() - start

        # 验证结果正确
        assert len(result) == 100
        for num in nums:
            assert result[num] == 'downloaded'

        # 性能断言（批量查询应该很快，小于 1 秒）
        assert elapsed < 1.0, f"Batch query took {elapsed:.2f}s, expected < 1.0s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
