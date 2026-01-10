"""
数据库迁移工具的单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from sqlalchemy import inspect

from app.utils.db_migration import DatabaseMigration
from app.db.models.download_filter import DownloadFilterSettings
from app.db.models.pending_torrent import PendingTorrent


class TestDatabaseMigration:
    """测试数据库迁移管理器"""

    def test_table_exists_returns_true_when_table_exists(self, db_session):
        """测试表存在时返回 True"""
        # 创建一个测试表
        DownloadFilterSettings.__table__.create(db_session.bind, checkfirst=True)

        migration = DatabaseMigration()
        assert migration._table_exists('download_filter_settings') is True

    def test_table_exists_returns_false_when_table_not_exists(self, db_session):
        """测试表不存在时返回 False"""
        migration = DatabaseMigration()
        assert migration._table_exists('nonexistent_table') is False

    def test_ensure_download_filter_table_creates_if_missing(self, db_session):
        """测试下载过滤表不存在时自动创建"""
        migration = DatabaseMigration()

        # 确保表不存在
        if migration._table_exists('download_filter_settings'):
            DownloadFilterSettings.__table__.drop(db_session.bind)

        # 执行创建
        migration._ensure_download_filter_table()

        # 验证表已创建
        assert migration._table_exists('download_filter_settings') is True

    def test_ensure_download_filter_table_skips_if_exists(self, db_session):
        """测试下载过滤表存在时不重复创建"""
        migration = DatabaseMigration()

        # 先创建表
        DownloadFilterSettings.__table__.create(db_session.bind, checkfirst=True)

        # 再次调用应该跳过
        migration._ensure_download_filter_table()

        # 验证表仍然存在
        assert migration._table_exists('download_filter_settings') is True

    def test_ensure_pending_torrent_table_creates_if_missing(self, db_session):
        """测试待处理种子表不存在时自动创建"""
        migration = DatabaseMigration()

        # 确保表不存在
        if migration._table_exists('pending_torrent'):
            PendingTorrent.__table__.drop(db_session.bind)

        # 执行创建
        migration._ensure_pending_torrent_table()

        # 验证表已创建
        assert migration._table_exists('pending_torrent') is True

    def test_ensure_pending_torrent_table_skips_if_exists(self, db_session):
        """测试待处理种子表存在时不重复创建"""
        migration = DatabaseMigration()

        # 先创建表
        PendingTorrent.__table__.create(db_session.bind, checkfirst=True)

        # 再次调用应该跳过
        migration._ensure_pending_torrent_table()

        # 验证表仍然存在
        assert migration._table_exists('pending_torrent') is True

    def test_column_exists_returns_true_when_column_exists(self, db_session):
        """测试列存在时返回 True"""
        # 创建表
        DownloadFilterSettings.__table__.create(db_session.bind, checkfirst=True)

        migration = DatabaseMigration()
        assert migration._column_exists('download_filter_settings', 'min_file_size_mb') is True

    def test_column_exists_returns_false_when_column_not_exists(self, db_session):
        """测试列不存在时返回 False"""
        # 创建表
        DownloadFilterSettings.__table__.create(db_session.bind, checkfirst=True)

        migration = DatabaseMigration()
        assert migration._column_exists('download_filter_settings', 'nonexistent_column') is False

    @patch('alembic.config.Config')
    @patch('alembic.command.upgrade')
    def test_run_alembic_upgrade_success(self, mock_upgrade, mock_config):
        """测试 Alembic 升级成功"""
        migration = DatabaseMigration()

        # Mock alembic.ini 文件存在
        with patch.object(Path, 'exists', return_value=True):
            migration._run_alembic_upgrade()

        # 验证调用了 upgrade
        mock_upgrade.assert_called_once()

    @patch('alembic.config.Config')
    def test_run_alembic_upgrade_file_not_found(self, mock_config):
        """测试 alembic.ini 文件不存在时的处理"""
        migration = DatabaseMigration()

        # Mock alembic.ini 文件不存在
        with patch.object(Path, 'exists', return_value=False):
            # 应该不抛出异常，只是记录警告
            migration._run_alembic_upgrade()

    @patch('alembic.config.Config')
    @patch('alembic.command.upgrade')
    def test_run_alembic_upgrade_handles_exception(self, mock_upgrade, mock_config):
        """测试 Alembic 升级失败时的异常处理"""
        migration = DatabaseMigration()

        # Mock upgrade 抛出异常
        mock_upgrade.side_effect = Exception("Upgrade failed")

        with patch.object(Path, 'exists', return_value=True):
            # 应该捕获异常并记录警告，不中断程序
            migration._run_alembic_upgrade()

    def test_init_default_filter_settings_creates_if_missing(self, db_session):
        """测试初始化默认过滤设置"""
        # 创建表
        DownloadFilterSettings.__table__.create(db_session.bind, checkfirst=True)

        migration = DatabaseMigration()
        migration._init_default_filter_settings()

        # 验证有默认设置
        from sqlalchemy import text
        with migration.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM download_filter_settings"))
            count = result.scalar()
            assert count > 0

    def test_init_default_filter_settings_skips_if_exists(self, db_session):
        """测试已有设置时跳过初始化"""
        # 创建表并插入数据
        DownloadFilterSettings.__table__.create(db_session.bind, checkfirst=True)

        migration = DatabaseMigration()

        # 第一次初始化
        migration._init_default_filter_settings()

        from sqlalchemy import text
        with migration.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM download_filter_settings"))
            count_before = result.scalar()

        # 第二次初始化
        migration._init_default_filter_settings()

        with migration.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM download_filter_settings"))
            count_after = result.scalar()

        # 数量应该相同，不重复插入
        assert count_before == count_after

    @patch.object(DatabaseMigration, '_run_alembic_upgrade')
    @patch.object(DatabaseMigration, '_ensure_download_filter_table')
    @patch.object(DatabaseMigration, '_ensure_pending_torrent_table')
    @patch.object(DatabaseMigration, '_init_default_filter_settings')
    def test_check_and_migrate_calls_all_methods(
        self,
        mock_init_settings,
        mock_ensure_pending,
        mock_ensure_filter,
        mock_alembic
    ):
        """测试 check_and_migrate 调用所有必要的方法"""
        migration = DatabaseMigration()
        migration.check_and_migrate()

        # 验证所有方法都被调用
        mock_alembic.assert_called_once()
        mock_ensure_filter.assert_called_once()
        mock_ensure_pending.assert_called_once()
        mock_init_settings.assert_called_once()


class TestDatabaseMigrationIntegration:
    """集成测试 - 测试完整迁移流程"""

    def test_full_migration_workflow(self, db_session):
        """测试完整的迁移工作流"""
        from sqlalchemy import text

        migration = DatabaseMigration()

        # 删除所有表（如果存在）
        inspector = inspect(db_session.bind)
        for table_name in inspector.get_table_names():
            if table_name in ['download_filter_settings', 'pending_torrent']:
                db_session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        db_session.commit()

        # 执行迁移（跳过 Alembic）
        with patch.object(DatabaseMigration, '_run_alembic_upgrade'):
            migration.check_and_migrate()

        # 验证所有表都被创建
        assert migration._table_exists('download_filter_settings') is True
        assert migration._table_exists('pending_torrent') is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
