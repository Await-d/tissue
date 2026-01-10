"""
示例测试 - 展示如何正确使用数据库 fixtures

这个测试文件演示了如何避免 "table already exists" 错误
"""

import pytest
from datetime import datetime, date

from app.db.models import Torrent, Subscribe, History
from app.db.models.actor_subscribe import ActorSubscribe, ActorSubscribeDownload
from app.db.models.enums import SubscribeStatus, HistoryStatus


class TestDatabaseFixtures:
    """数据库 fixture 使用示例"""

    def test_basic_insert(self, db_session):
        """测试基本的插入操作"""
        # 创建一个 Torrent 记录
        torrent = Torrent(
            hash='test_hash_1',
            num='TEST-001',
            is_zh=True,
            is_hd=True,
            is_uncensored=False
        )
        db_session.add(torrent)
        db_session.commit()

        # 验证插入成功
        result = db_session.query(Torrent).filter_by(num='TEST-001').first()
        assert result is not None
        assert result.hash == 'test_hash_1'

    def test_actor_subscribe(self, db_session):
        """测试 actor_subscribe 表操作"""
        # 创建演员订阅记录
        actor_subscribe = ActorSubscribe(
            actor_name='测试演员',
            from_date=date.today(),
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(actor_subscribe)
        db_session.flush()  # 获取 ID

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

        # 验证
        result = db_session.query(ActorSubscribeDownload).filter_by(num='TEST-002').first()
        assert result is not None
        assert result.title == '测试标题'

    def test_subscribe_with_enum(self, db_session):
        """测试 Subscribe 表和枚举"""
        subscribe = Subscribe(
            num='TEST-003',
            title='测试订阅',
            status=SubscribeStatus.COMPLETED,  # 使用枚举
            is_hd=True,
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(subscribe)
        db_session.commit()

        # 验证
        result = db_session.query(Subscribe).filter_by(num='TEST-003').first()
        assert result is not None
        assert result.status == SubscribeStatus.COMPLETED
        assert result.status == 2  # 枚举值

    def test_history_with_enum(self, db_session):
        """测试 History 表和枚举"""
        history = History(
            num='TEST-004',
            status=HistoryStatus.SUCCESS,  # 使用枚举
            source_path='/test/source',
            trans_method='move',
            is_zh=True,
            is_uncensored=False
        )
        db_session.add(history)
        db_session.commit()

        # 验证
        result = db_session.query(History).filter_by(num='TEST-004').first()
        assert result is not None
        assert result.status == HistoryStatus.SUCCESS
        assert result.status == 1  # 枚举值

    def test_multiple_operations(self, db_session):
        """测试多个表的操作"""
        # 添加多个表的记录
        torrent = Torrent(hash='hash1', num='MULTI-001', is_zh=True, is_hd=True, is_uncensored=False)
        subscribe = Subscribe(num='MULTI-002', title='订阅', status=SubscribeStatus.PENDING, is_hd=True, is_zh=True, is_uncensored=False)
        history = History(
            num='MULTI-003',
            status=HistoryStatus.SUCCESS,
            source_path='/test',
            trans_method='move',
            is_zh=True,
            is_uncensored=False
        )

        db_session.add_all([torrent, subscribe, history])
        db_session.commit()

        # 验证
        assert db_session.query(Torrent).count() == 1
        assert db_session.query(Subscribe).count() == 1
        assert db_session.query(History).count() == 1


class TestIsolation:
    """测试每个测试之间的隔离性"""

    def test_first(self, db_session):
        """第一个测试"""
        torrent = Torrent(hash='iso1', num='ISO-001', is_zh=True, is_hd=True, is_uncensored=False)
        db_session.add(torrent)
        db_session.commit()

        assert db_session.query(Torrent).count() == 1

    def test_second(self, db_session):
        """
        第二个测试

        如果 fixture 配置正确，这个测试应该看到空数据库
        而不是上一个测试的数据
        """
        count = db_session.query(Torrent).count()
        assert count == 0, f"数据库应该是空的，但有 {count} 条记录"

    def test_third(self, db_session):
        """第三个测试 - 再次验证隔离性"""
        assert db_session.query(Torrent).count() == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
