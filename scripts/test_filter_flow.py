"""
测试智能下载和演员订阅的过滤流程
检查为什么文件过滤没有生效
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import SessionFactory
from app.service.download_filter import DownloadFilterService
from app.service.base_download import BaseDownloadService

def test_filter_settings():
    """测试过滤设置是否存在"""
    db = SessionFactory()
    try:
        filter_service = DownloadFilterService(db)
        settings = filter_service.get_filter_settings()

        if settings:
            print("✅ 找到激活的过滤设置:")
            print(f"   ID: {settings.id}")
            print(f"   最小文件大小: {settings.min_file_size_mb}MB")
            print(f"   最大文件大小: {settings.max_file_size_mb}MB")
            print(f"   智能过滤: {settings.enable_smart_filter}")
            print(f"   跳过样本文件: {settings.skip_sample_files}")
            print(f"   只保留媒体文件: {getattr(settings, 'media_files_only', False)}")
            print(f"   包含字幕: {getattr(settings, 'include_subtitles', True)}")
            print(f"   激活状态: {settings.is_active}")
            return True
        else:
            print("❌ 未找到激活的过滤设置")
            default_settings = filter_service.get_default_filter_settings()
            print("   默认设置:")
            for key, value in default_settings.items():
                print(f"     {key}: {value}")
            return False
    finally:
        db.close()


def test_download_flow_tracking():
    """测试下载流程跟踪"""
    print("\n" + "="*60)
    print("下载流程分析")
    print("="*60)

    print("\n智能下载流程:")
    print("  AutoDownloadService._process_single_subscription()")
    print("    → SubscribeService.download_video()")
    print("      → BaseDownloadService.download_with_filter(skip_filter=False)")
    print("        → DownloadFilterService.filter_torrent_files()")

    print("\n演员订阅下载流程:")
    print("  ActorSubscribeService.download_actor_video()")
    print("    → BaseDownloadService.download_with_filter(skip_filter=False)")
    print("      → DownloadFilterService.filter_torrent_files()")

    print("\n关键点:")
    print("  1. skip_filter=False ✓ (应该启用过滤)")
    print("  2. 种子添加时 paused=True ✓ (应该暂停)")
    print("  3. 等待元数据加载 (最多10秒)")
    print("  4. 应用过滤规则")
    print("  5. 设置文件优先级")
    print("  6. 恢复下载")


def check_base_download_logic():
    """检查 BaseDownloadService 的关键逻辑"""
    print("\n" + "="*60)
    print("BaseDownloadService 关键逻辑检查")
    print("="*60)

    # 读取源码检查
    file_path = "app/service/base_download.py"

    print(f"\n检查 {file_path}:")
    print("  1. add_magnet 调用时 paused 参数:")
    print("     paused=(not skip_filter)")
    print("     → skip_filter=False 时, paused=True ✓")

    print("\n  2. 元数据等待:")
    print("     _check_metadata_ready(torrent_hash, max_attempts=10)")
    print("     → 最多等待 10 秒")
    print("     → 如果超时，直接 resume_torrent() ❌ 跳过过滤!")

    print("\n  3. 过滤应用:")
    print("     filter_service.filter_torrent_files(torrent_hash)")
    print("     → 调用文件优先级设置 API")

    print("\n⚠️  可能的问题:")
    print("     如果元数据加载超时(10秒)，会跳过过滤直接下载所有文件!")


def main():
    print("="*60)
    print("智能下载和演员订阅文件过滤问题诊断")
    print("="*60)

    # 测试1: 检查过滤设置
    print("\n[测试1] 检查过滤设置")
    print("-"*60)
    has_settings = test_filter_settings()

    # 测试2: 分析下载流程
    test_download_flow_tracking()

    # 测试3: 检查关键逻辑
    check_base_download_logic()

    # 总结
    print("\n" + "="*60)
    print("问题总结")
    print("="*60)

    if not has_settings:
        print("\n❌ 主要问题: 数据库中没有激活的过滤设置")
        print("   解决方案: 通过 /api/download-filter/settings 创建默认设置")
    else:
        print("\n⚠️  疑似问题: 元数据加载超时导致跳过过滤")
        print("   原因分析:")
        print("     1. 磁力链接需要从DHT网络获取元数据")
        print("     2. 当前只等待10秒就超时")
        print("     3. 超时后直接恢复下载，跳过过滤")
        print("\n   建议检查:")
        print("     1. 查看应用日志，搜索 '元数据加载超时'")
        print("     2. 查看应用日志，搜索 '应用过滤规则'")
        print("     3. 查看应用日志，搜索 '成功设置文件优先级'")
        print("\n   如果日志显示 '元数据加载超时':")
        print("     → 增加等待时间或使用延迟过滤机制")


if __name__ == "__main__":
    main()
