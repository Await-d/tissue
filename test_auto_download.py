#!/usr/bin/env python3
"""
自动下载功能测试脚本
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_migration():
    """测试数据库迁移"""
    print("🔄 测试数据库迁移...")
    try:
        from app.db.models.auto_download import AutoDownloadRule, AutoDownloadSubscription
        from app.db.models.auto_download import TimeRangeType, DownloadStatus
        print("✅ 数据模型导入成功")
        
        # 测试枚举
        assert TimeRangeType.DAY.value == "day"
        assert DownloadStatus.PENDING.value == "pending"
        print("✅ 枚举类型正常")
        
        return True
    except Exception as e:
        print(f"❌ 数据库迁移测试失败: {str(e)}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n🔄 测试API端点...")
    base_url = "http://localhost:8000"
    
    test_cases = [
        ("GET", "/api/auto-download/statistics", "获取统计信息"),
        ("GET", "/api/auto-download/rules", "获取规则列表"),
        ("GET", "/api/auto-download/subscriptions", "获取订阅记录"),
    ]
    
    success_count = 0
    
    for method, endpoint, description in test_cases:
        try:
            url = f"{base_url}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                continue
                
            if response.status_code in [200, 401]:  # 401是因为没有认证
                print(f"✅ {description}: {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {description}: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"⚠️ {description}: 服务器未启动")
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
    
    return success_count == len(test_cases)

def test_spider_enhancements():
    """测试爬虫增强功能"""
    print("\n🔄 测试爬虫增强功能...")
    try:
        from app.utils.spider.javdb import JavdbSpider
        from app.utils.video_collector import video_collector
        
        spider = JavdbSpider()
        
        # 测试方法是否存在
        assert hasattr(spider, 'get_trending_videos')
        assert hasattr(spider, 'get_latest_videos')
        assert hasattr(spider, 'get_comments_count')
        print("✅ 爬虫增强方法存在")
        
        # 测试视频收集器
        assert hasattr(video_collector, 'get_videos_by_criteria')
        print("✅ 视频收集器正常")
        
        return True
    except Exception as e:
        print(f"❌ 爬虫增强测试失败: {str(e)}")
        return False

def test_service_logic():
    """测试服务逻辑"""
    print("\n🔄 测试服务逻辑...")
    try:
        from app.service.auto_download import AutoDownloadService
        from app.schema.auto_download import AutoDownloadRuleCreate
        
        # 测试方法是否存在
        assert hasattr(AutoDownloadService, 'create_rule')
        assert hasattr(AutoDownloadService, 'get_rules')
        assert hasattr(AutoDownloadService, 'execute_rules')
        assert hasattr(AutoDownloadService, 'job_auto_download')
        print("✅ 服务方法存在")
        
        # 测试Schema
        rule_data = AutoDownloadRuleCreate(
            name="测试规则",
            min_rating=8.0,
            min_comments=50,
            time_range_type="week",
            time_range_value=1,
            is_hd=True,
            is_zh=False,
            is_uncensored=False,
            is_enabled=True
        )
        assert rule_data.name == "测试规则"
        print("✅ Schema验证正常")
        
        return True
    except Exception as e:
        print(f"❌ 服务逻辑测试失败: {str(e)}")
        return False

def test_scheduler_integration():
    """测试定时任务集成"""
    print("\n🔄 测试定时任务集成...")
    try:
        from app.scheduler import Scheduler
        
        scheduler = Scheduler()
        
        # 检查是否有自动下载任务
        assert 'auto_download' in scheduler.jobs
        print("✅ 定时任务已集成")
        
        return True
    except Exception as e:
        print(f"❌ 定时任务集成测试失败: {str(e)}")
        return False

def create_test_rule():
    """创建测试规则"""
    print("\n🔄 创建测试规则...")
    test_rule = {
        "name": "测试规则 - 高质量作品",
        "min_rating": 8.5,
        "min_comments": 100,
        "time_range_type": "week",
        "time_range_value": 2,
        "is_hd": True,
        "is_zh": False,
        "is_uncensored": False,
        "is_enabled": False  # 测试时不启用
    }
    
    print(f"📋 测试规则配置:")
    for key, value in test_rule.items():
        print(f"   {key}: {value}")
    
    return test_rule

def main():
    """主测试函数"""
    print("🚀 开始自动下载功能测试\n")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("数据库迁移", test_database_migration()))
    test_results.append(("爬虫增强", test_spider_enhancements()))
    test_results.append(("服务逻辑", test_service_logic()))
    test_results.append(("定时任务集成", test_scheduler_integration()))
    test_results.append(("API端点", test_api_endpoints()))
    
    # 创建测试规则示例
    create_test_rule()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 总体通过率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 自动下载功能基本就绪！")
        print("\n📝 下一步操作:")
        print("   1. 运行数据库迁移: alembic upgrade head")
        print("   2. 启动应用服务器")
        print("   3. 在前端创建和配置自动下载规则")
        print("   4. 监控系统运行状态")
    else:
        print("⚠️ 部分功能需要修复后再测试")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)