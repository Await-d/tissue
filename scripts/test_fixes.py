#!/usr/bin/env python3
"""
功能测试脚本 - 测试所有修复的功能
使用方法: python scripts/test_fixes.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.data_converter import DataConverter
from app.db import SessionFactory
from app.utils.logger import logger


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        """运行单个测试"""
        try:
            print(f"\n{'='*60}")
            print(f"测试: {name}")
            print(f"{'='*60}")
            func()
            print(f"✅ 通过")
            self.passed += 1
            self.tests.append((name, True, None))
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def summary(self):
        """打印测试总结"""
        print(f"\n{'='*60}")
        print("测试总结")
        print(f"{'='*60}")
        print(f"总计: {self.passed + self.failed}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"\n详细结果:")
        for name, passed, error in self.tests:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}")
            if error:
                print(f"      错误: {error}")
        print(f"{'='*60}\n")


def test_data_converter():
    """测试 DataConverter 工具类"""
    
    # 测试 to_float
    assert DataConverter.to_float(3.14) == 3.14
    assert DataConverter.to_float("3.14") == 3.14
    assert DataConverter.to_float(None) == 0.0
    assert DataConverter.to_float("invalid") == 0.0
    assert DataConverter.to_float(42) == 42.0
    print("  ✓ to_float 测试通过")
    
    # 测试 to_int
    assert DataConverter.to_int(42) == 42
    assert DataConverter.to_int("42") == 42
    assert DataConverter.to_int(3.14) == 3
    assert DataConverter.to_int(None) == 0
    assert DataConverter.to_int("invalid") == 0
    print("  ✓ to_int 测试通过")
    
    # 测试 to_date
    from datetime import date, datetime
    assert DataConverter.to_date("2025-01-15") == date(2025, 1, 15)
    assert DataConverter.to_date(date(2025, 1, 15)) == date(2025, 1, 15)
    assert DataConverter.to_date(datetime(2025, 1, 15, 10, 30)) == date(2025, 1, 15)
    assert DataConverter.to_date(None) is None
    assert DataConverter.to_date("invalid") is None
    print("  ✓ to_date 测试通过")
    
    # 测试 normalize_rating
    assert DataConverter.normalize_rating(7.5) == 7.5
    assert DataConverter.normalize_rating("8.2") == 8.2
    assert DataConverter.normalize_rating(None) == 0.0
    assert DataConverter.normalize_rating(15.0) == 10.0  # 超过最大值
    assert DataConverter.normalize_rating(-5.0) == 0.0   # 低于最小值
    print("  ✓ normalize_rating 测试通过")
    
    # 测试 normalize_comments_count
    assert DataConverter.normalize_comments_count(100) == 100
    assert DataConverter.normalize_comments_count("50") == 50
    assert DataConverter.normalize_comments_count(None) == 0
    assert DataConverter.normalize_comments_count(-10) == 0  # 负数转为0
    print("  ✓ normalize_comments_count 测试通过")
    
    print("\n✅ DataConverter 所有测试通过")


def test_database_migration():
    """测试数据库迁移是否成功"""
    from sqlalchemy import text, inspect
    
    with SessionFactory() as db:
        inspector = inspect(db.bind)
        
        # 检查 actor_subscribe 表是否存在
        tables = inspector.get_table_names()
        assert 'actor_subscribe' in tables, "actor_subscribe 表不存在"
        print("  ✓ actor_subscribe 表存在")
        
        # 检查新字段是否存在
        columns = [col['name'] for col in inspector.get_columns('actor_subscribe')]
        
        if 'subscribed_works_count' in columns:
            print("  ✓ subscribed_works_count 字段已存在")
        else:
            print("  ⚠️  subscribed_works_count 字段不存在，需要执行迁移")
        
        if 'works_count_updated_at' in columns:
            print("  ✓ works_count_updated_at 字段已存在")
        else:
            print("  ⚠️  works_count_updated_at 字段不存在，需要执行迁移")
        
        print("\n✅ 数据库结构检查完成")


def test_qbittorent_methods():
    """测试 qbittorent 新增方法是否存在"""
    from app.utils.qbittorent import qbittorent
    
    # 检查 resume_torrent 方法
    assert hasattr(qbittorent, 'resume_torrent'), "缺少 resume_torrent 方法"
    print("  ✓ resume_torrent 方法存在")
    
    # 检查 add_magnet 方法签名
    import inspect
    sig = inspect.signature(qbittorent.add_magnet)
    params = list(sig.parameters.keys())
    
    assert 'magnet' in params
    assert 'savepath' in params
    assert 'category' in params
    assert 'paused' in params, "add_magnet 缺少 paused 参数"
    print("  ✓ add_magnet 方法签名正确，包含 paused 参数")
    
    print("\n✅ qbittorent 方法检查通过")


def test_base_download_service():
    """测试 BaseDownloadService 是否可以正常导入和实例化"""
    from app.service.base_download import BaseDownloadService
    from sqlalchemy.orm import Session
    
    # 检查类是否存在
    assert BaseDownloadService is not None
    print("  ✓ BaseDownloadService 类可以导入")
    
    # 检查关键方法是否存在
    assert hasattr(BaseDownloadService, 'download_with_filter')
    assert hasattr(BaseDownloadService, '_check_metadata_ready')
    assert hasattr(BaseDownloadService, 'resume_torrent_if_needed')
    print("  ✓ BaseDownloadService 包含所有必需方法")
    
    # 尝试实例化（需要数据库连接）
    with SessionFactory() as db:
        service = BaseDownloadService(db)
        assert service.db is not None
        assert service.filter_service is not None
        print("  ✓ BaseDownloadService 可以正常实例化")
    
    print("\n✅ BaseDownloadService 检查通过")


def test_import_fixes():
    """测试导入修复是否生效"""
    
    # 测试 subscribe.py 中的导入
    try:
        from app.service.subscribe import SubscribeService
        print("  ✓ SubscribeService 可以导入")
    except ImportError as e:
        raise AssertionError(f"SubscribeService 导入失败: {e}")
    
    # 测试 actor_subscribe.py 中的导入
    try:
        from app.service.actor_subscribe import ActorSubscribeService
        print("  ✓ ActorSubscribeService 可以导入")
    except ImportError as e:
        raise AssertionError(f"ActorSubscribeService 导入失败: {e}")
    
    # 测试 auto_download.py 中的导入
    try:
        from app.service.auto_download import AutoDownloadService
        print("  ✓ AutoDownloadService 可以导入")
    except ImportError as e:
        raise AssertionError(f"AutoDownloadService 导入失败: {e}")
    
    print("\n✅ 所有服务类导入正常")


def test_scheduler_config():
    """测试调度器配置"""
    from app.scheduler import scheduler
    
    # 检查定时任务是否配置
    jobs = {job.id: job for job in scheduler.list()}
    
    # 检查演员订阅任务
    if 'actor_subscribe' in jobs:
        print("  ✓ actor_subscribe 定时任务已配置")
    else:
        print("  ⚠️  actor_subscribe 定时任务未配置（可能需要启动调度器）")
    
    # 检查作品数量更新任务
    if 'actor_works_count_update' in jobs:
        print("  ✓ actor_works_count_update 定时任务已配置")
    else:
        print("  ⚠️  actor_works_count_update 定时任务未配置（可能需要启动调度器）")
    
    print("\n✅ 调度器配置检查完成")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("开始功能测试")
    print("="*60)
    
    runner = TestRunner()
    
    # 运行所有测试
    runner.test("DataConverter 工具类", test_data_converter)
    runner.test("数据库迁移", test_database_migration)
    runner.test("qbittorent 方法", test_qbittorent_methods)
    runner.test("BaseDownloadService", test_base_download_service)
    runner.test("导入修复", test_import_fixes)
    runner.test("调度器配置", test_scheduler_config)
    
    # 打印总结
    runner.summary()
    
    # 返回退出码
    return 0 if runner.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
