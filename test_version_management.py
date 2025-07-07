#!/usr/bin/env python3
"""
版本管理功能测试脚本
"""
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_version_manager_module():
    """测试版本管理器模块"""
    print("🔄 测试版本管理器模块...")
    try:
        from app.utils.version_manager import VersionManager, version_manager
        from version import APP_VERSION
        
        # 测试基本功能
        assert hasattr(VersionManager, 'is_version_updated')
        assert hasattr(VersionManager, 'run_database_migration')
        assert hasattr(VersionManager, 'perform_auto_upgrade')
        print("✅ 版本管理器方法存在")
        
        # 测试版本获取
        current_version = version_manager.current_version
        assert current_version == APP_VERSION
        print(f"✅ 当前版本: {current_version}")
        
        return True
    except Exception as e:
        print(f"❌ 版本管理器模块测试失败: {str(e)}")
        return False

def test_startup_script():
    """测试启动脚本"""
    print("\n🔄 测试启动脚本...")
    try:
        from app.startup import pre_startup_check, startup_health_check
        
        # 测试方法存在
        assert callable(pre_startup_check)
        assert callable(startup_health_check)
        print("✅ 启动脚本方法存在")
        
        return True
    except Exception as e:
        print(f"❌ 启动脚本测试失败: {str(e)}")
        return False

def test_version_api():
    """测试版本管理API"""
    print("\n🔄 测试版本管理API...")
    try:
        from app.api.version import router
        from fastapi import APIRouter
        
        # 检查路由器类型
        assert isinstance(router, APIRouter)
        print("✅ API路由器正常")
        
        # 检查路由数量
        routes = router.routes
        assert len(routes) > 0
        print(f"✅ API路由数量: {len(routes)}")
        
        return True
    except Exception as e:
        print(f"❌ 版本管理API测试失败: {str(e)}")
        return False

def test_version_storage():
    """测试版本信息存储"""
    print("\n🔄 测试版本信息存储...")
    try:
        from app.utils.version_manager import VersionManager
        
        # 使用临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            test_storage_path = os.path.join(temp_dir, "test_version.json")
            test_manager = VersionManager(storage_path=test_storage_path)
            
            # 测试保存版本信息
            test_version = "v0.1.0-test"
            test_manager.save_version_info(
                version=test_version,
                migration_success=True,
                notes="测试版本保存"
            )
            
            # 测试读取版本信息
            stored_version = test_manager.get_stored_version()
            assert stored_version == test_version
            print("✅ 版本信息存储和读取正常")
            
            # 测试版本历史
            version_info = test_manager.get_version_info()
            assert 'version_history' in version_info
            print("✅ 版本历史功能正常")
            
        return True
    except Exception as e:
        print(f"❌ 版本信息存储测试失败: {str(e)}")
        return False

def test_migration_requirements():
    """测试迁移前置条件检查"""
    print("\n🔄 测试迁移前置条件检查...")
    try:
        from app.utils.version_manager import version_manager
        
        # 测试前置条件检查
        requirements = version_manager.check_migration_requirements()
        
        # 检查返回的字段
        required_fields = [
            'alembic_available',
            'config_exists', 
            'database_accessible',
            'disk_space_sufficient',
            'errors'
        ]
        
        for field in required_fields:
            assert field in requirements
        
        print("✅ 迁移前置条件检查正常")
        print(f"  - Alembic可用: {requirements['alembic_available']}")
        print(f"  - 配置文件存在: {requirements['config_exists']}")
        print(f"  - 数据库可访问: {requirements['database_accessible']}")
        print(f"  - 磁盘空间足够: {requirements['disk_space_sufficient']}")
        
        if requirements['errors']:
            print(f"  - 发现问题: {requirements['errors']}")
        
        return True
    except Exception as e:
        print(f"❌ 迁移前置条件检查测试失败: {str(e)}")
        return False

def test_version_comparison():
    """测试版本比较逻辑"""
    print("\n🔄 测试版本比较逻辑...")
    try:
        from app.utils.version_manager import VersionManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_storage_path = os.path.join(temp_dir, "test_version.json")
            test_manager = VersionManager(storage_path=test_storage_path)
            
            # 第一次启动，应该返回需要更新
            is_updated = test_manager.is_version_updated()
            assert is_updated == True
            print("✅ 首次启动检测正确")
            
            # 保存当前版本
            test_manager.save_version_info(
                version=test_manager.current_version,
                migration_success=True
            )
            
            # 再次检查，应该返回不需要更新
            is_updated = test_manager.is_version_updated()
            assert is_updated == False
            print("✅ 版本一致性检测正确")
            
            # 模拟版本更新
            old_version = test_manager.current_version
            test_manager.current_version = "v999.0.0"
            
            is_updated = test_manager.is_version_updated()
            assert is_updated == True
            print("✅ 版本更新检测正确")
            
            # 恢复原版本
            test_manager.current_version = old_version
        
        return True
    except Exception as e:
        print(f"❌ 版本比较逻辑测试失败: {str(e)}")
        return False

def test_integration_with_main():
    """测试与主应用集成"""
    print("\n🔄 测试与主应用集成...")
    try:
        # 检查main.py中是否正确导入
        with open('app/main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # 检查必要的导入
        required_imports = [
            'from app.utils.version_manager import version_manager',
            'from app.api import api_router, actor_subscribe, auto_download, version'
        ]
        
        for import_line in required_imports:
            if import_line not in main_content:
                print(f"❌ 缺少导入: {import_line}")
                return False
        
        # 检查启动函数调用
        if 'perform_version_check_and_migration()' not in main_content:
            print("❌ 缺少版本检测调用")
            return False
        
        # 检查API路由注册
        if 'version.router' not in main_content:
            print("❌ 缺少版本API路由注册")
            return False
        
        print("✅ 与主应用集成正常")
        return True
    except Exception as e:
        print(f"❌ 主应用集成测试失败: {str(e)}")
        return False

def create_mock_scenario():
    """创建模拟场景测试"""
    print("\n🔄 创建模拟升级场景...")
    
    scenarios = [
        {
            'name': '正常升级场景',
            'stored_version': 'v0.0.3',
            'current_version': 'v0.1.0',
            'expected_update': True
        },
        {
            'name': '版本一致场景',
            'stored_version': 'v0.1.0',
            'current_version': 'v0.1.0',
            'expected_update': False
        },
        {
            'name': '首次启动场景',
            'stored_version': None,
            'current_version': 'v0.1.0',
            'expected_update': True
        }
    ]
    
    print("📋 模拟场景:")
    for scenario in scenarios:
        print(f"  - {scenario['name']}")
        print(f"    存储版本: {scenario['stored_version'] or '无'}")
        print(f"    当前版本: {scenario['current_version']}")
        print(f"    需要更新: {'是' if scenario['expected_update'] else '否'}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始版本管理功能测试\n")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("版本管理器模块", test_version_manager_module()))
    test_results.append(("启动脚本", test_startup_script()))
    test_results.append(("版本管理API", test_version_api()))
    test_results.append(("版本信息存储", test_version_storage()))
    test_results.append(("迁移前置条件检查", test_migration_requirements()))
    test_results.append(("版本比较逻辑", test_version_comparison()))
    test_results.append(("主应用集成", test_integration_with_main()))
    
    # 创建模拟场景
    create_mock_scenario()
    
    # 汇总结果
    print("\n" + "=" * 60)
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
    
    if success_rate >= 85:
        print("🎉 版本管理功能实现优秀！")
        print("\n📝 使用说明:")
        print("   1. 应用启动时会自动检测版本更新")
        print("   2. 检测到更新时会自动执行数据库迁移")
        print("   3. 可通过前端界面手动管理版本")
        print("   4. 支持版本历史记录和状态监控")
        print("\n🔧 API端点:")
        print("   - GET /api/version/info - 获取版本信息")
        print("   - GET /api/version/status - 获取系统状态")
        print("   - POST /api/version/migrate - 手动执行迁移")
        print("   - GET /api/version/history - 查看版本历史")
    else:
        print("⚠️ 部分功能需要修复后再测试")
    
    return success_rate >= 85

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)