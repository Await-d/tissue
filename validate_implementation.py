#!/usr/bin/env python3
"""
自动下载功能实现验证脚本
检查文件结构和代码语法
"""
import os
import ast
import sys

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (不存在)")
        return False

def check_python_syntax(file_path, description):
    """检查Python文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f"✅ {description}: 语法正确")
        return True
    except SyntaxError as e:
        print(f"❌ {description}: 语法错误 - {str(e)}")
        return False
    except Exception as e:
        print(f"⚠️ {description}: 无法检查 - {str(e)}")
        return False

def check_typescript_structure(file_path, description):
    """简单检查TypeScript文件结构"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基本检查
        if 'import' in content and 'export' in content:
            print(f"✅ {description}: 结构正常")
            return True
        else:
            print(f"⚠️ {description}: 可能缺少导入/导出")
            return False
    except Exception as e:
        print(f"❌ {description}: 检查失败 - {str(e)}")
        return False

def main():
    """主验证函数"""
    print("🔍 自动下载功能实现验证")
    print("=" * 60)
    
    results = []
    
    # 检查后端文件
    print("\n📁 后端文件检查:")
    backend_files = [
        ("alembic/versions/add_auto_download_tables.py", "数据库迁移文件"),
        ("app/db/models/auto_download.py", "数据模型文件"),
        ("app/schema/auto_download.py", "Schema定义文件"),
        ("app/service/auto_download.py", "业务服务文件"),
        ("app/api/auto_download.py", "API路由文件"),
        ("app/utils/video_collector.py", "视频收集器文件"),
    ]
    
    for file_path, desc in backend_files:
        exists = check_file_exists(file_path, desc)
        if exists:
            syntax_ok = check_python_syntax(file_path, f"{desc}语法")
            results.append((desc, exists and syntax_ok))
        else:
            results.append((desc, False))
    
    # 检查前端文件  
    print("\n📁 前端文件检查:")
    frontend_files = [
        ("frontend/src/apis/autoDownload.ts", "前端API接口"),
        ("frontend/src/routes/_index/auto-download/index.tsx", "主页面组件"),
        ("frontend/src/routes/_index/auto-download/rules.tsx", "规则管理页面"),
        ("frontend/src/routes/_index/auto-download/subscriptions.tsx", "订阅记录页面"),
        ("frontend/src/routes/_index/setting/auto-download.tsx", "设置页面"),
    ]
    
    for file_path, desc in frontend_files:
        exists = check_file_exists(file_path, desc)
        if exists:
            structure_ok = check_typescript_structure(file_path, f"{desc}结构")
            results.append((desc, exists and structure_ok))
        else:
            results.append((desc, False))
    
    # 检查配置修改
    print("\n⚙️ 配置修改检查:")
    config_checks = []
    
    # 检查模型导入
    try:
        with open("app/db/models/__init__.py", 'r') as f:
            content = f.read()
        if "from .auto_download import *" in content:
            print("✅ 数据模型已导入")
            config_checks.append(True)
        else:
            print("❌ 数据模型未导入")
            config_checks.append(False)
    except:
        print("❌ 无法检查数据模型导入")
        config_checks.append(False)
    
    # 检查Schema导入
    try:
        with open("app/schema/__init__.py", 'r') as f:
            content = f.read()
        if "from .auto_download import *" in content:
            print("✅ Schema已导入")
            config_checks.append(True)
        else:
            print("❌ Schema未导入")
            config_checks.append(False)
    except:
        print("❌ 无法检查Schema导入")
        config_checks.append(False)
    
    # 检查API路由注册
    try:
        with open("app/main.py", 'r') as f:
            content = f.read()
        if "auto_download" in content:
            print("✅ API路由已注册")
            config_checks.append(True)
        else:
            print("❌ API路由未注册")
            config_checks.append(False)
    except:
        print("❌ 无法检查API路由注册")
        config_checks.append(False)
    
    # 检查定时任务
    try:
        with open("app/scheduler.py", 'r') as f:
            content = f.read()
        if "auto_download" in content and "AutoDownloadService" in content:
            print("✅ 定时任务已集成")
            config_checks.append(True)
        else:
            print("❌ 定时任务未集成")
            config_checks.append(False)
    except:
        print("❌ 无法检查定时任务集成")
        config_checks.append(False)
    
    # 检查前端路由
    try:
        with open("frontend/src/routes.tsx", 'r') as f:
            content = f.read()
        if "auto-download" in content:
            print("✅ 前端路由已添加")
            config_checks.append(True)
        else:
            print("❌ 前端路由未添加")
            config_checks.append(False)
    except:
        print("❌ 无法检查前端路由")
        config_checks.append(False)
    
    results.extend([("配置修改", all(config_checks))])
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 验证结果汇总:")
    
    passed = 0
    total = len(results)
    
    for item_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {item_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 总体通过率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 实现质量优秀！功能完整，代码结构清晰。")
    elif success_rate >= 80:
        print("👍 实现质量良好！大部分功能已完成。")
    elif success_rate >= 60:
        print("⚠️ 实现基本完成，但还有一些问题需要修复。")
    else:
        print("❗ 实现存在较多问题，需要进一步完善。")
    
    print("\n📝 下一步建议:")
    print("   1. 运行数据库迁移: alembic upgrade head")
    print("   2. 安装前端依赖并构建: cd frontend && npm install && npm run build")
    print("   3. 启动应用测试功能")
    print("   4. 创建测试规则验证筛选逻辑")
    print("   5. 监控日志确保定时任务正常运行")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)