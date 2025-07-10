#!/usr/bin/env python3
"""
强制刷新SQLAlchemy模型架构
解决生产环境中模型与数据库不一致的问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def force_schema_refresh():
    """强制刷新数据库架构"""
    print("🔄 强制刷新SQLAlchemy模型架构...")
    
    try:
        # 导入必要的模块
        from app.db import engine, SessionFactory
        from app.db.models.auto_download import AutoDownloadSubscription
        from sqlalchemy import inspect
        
        # 创建数据库会话
        session = SessionFactory()
        
        # 获取数据库检查器
        inspector = inspect(engine)
        
        # 检查表结构
        print("📋 检查当前表结构...")
        table_columns = inspector.get_columns('auto_download_subscriptions')
        column_names = [col['name'] for col in table_columns]
        
        print(f"   当前字段: {column_names}")
        
        if 'resource_hash' in column_names:
            print("✅ resource_hash字段在数据库中存在")
        else:
            print("❌ resource_hash字段在数据库中不存在")
            return False
        
        # 测试模型查询
        print("🔍 测试模型查询...")
        try:
            # 尝试查询第一条记录
            subscription = session.query(AutoDownloadSubscription).first()
            if subscription:
                print(f"   ✅ 成功查询到记录 ID: {subscription.id}")
                print(f"   📊 resource_hash值: {subscription.resource_hash}")
            else:
                print("   ⚠️  表中没有记录")
            
            # 尝试计数查询
            count = session.query(AutoDownloadSubscription).count()
            print(f"   📊 总记录数: {count}")
            
        except Exception as e:
            print(f"   ❌ 查询失败: {e}")
            return False
        finally:
            session.close()
        
        print("✅ 模型架构检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 架构刷新失败: {e}")
        return False

def clear_sqlalchemy_cache():
    """清除SQLAlchemy相关缓存"""
    print("🧹 清除SQLAlchemy缓存...")
    
    try:
        # 删除可能的缓存文件
        cache_patterns = [
            "**/*.pyc",
            "**/__pycache__",
            ".serena/cache/**/*",
        ]
        
        import glob
        for pattern in cache_patterns:
            for cache_file in glob.glob(pattern, recursive=True):
                cache_path = Path(cache_file)
                if cache_path.exists():
                    if cache_path.is_file():
                        cache_path.unlink()
                        print(f"   🗑️  删除文件: {cache_file}")
                    elif cache_path.is_dir() and not any(cache_path.iterdir()):
                        cache_path.rmdir()
                        print(f"   🗑️  删除空目录: {cache_file}")
        
        print("✅ 缓存清除完成")
        return True
        
    except Exception as e:
        print(f"❌ 缓存清除失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 强制刷新生产环境数据库架构")
    print("=" * 60)
    
    # 清除缓存
    clear_sqlalchemy_cache()
    
    # 强制刷新架构
    if force_schema_refresh():
        print("\n" + "=" * 60)
        print("✅ 架构刷新完成!")
        print("🚀 建议重启应用以确保更改生效")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ 架构刷新失败!")
        print("💡 请检查数据库连接和权限")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)