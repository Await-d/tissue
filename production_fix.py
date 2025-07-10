#!/usr/bin/env python3
"""
专用于生产环境的数据库修复脚本
直接使用应用的数据库连接配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def fix_production_database():
    """使用应用配置修复生产环境数据库"""
    
    print("=" * 60)
    print("🚀 使用应用配置修复生产环境数据库")
    print("=" * 60)
    
    try:
        # 导入应用的数据库配置
        from app.db import engine, SessionFactory
        from sqlalchemy import text, inspect
        
        print("✅ 成功导入应用数据库配置")
        
        # 获取数据库检查器
        inspector = inspect(engine)
        
        # 检查表是否存在
        tables = inspector.get_table_names()
        if 'auto_download_subscriptions' not in tables:
            print("❌ auto_download_subscriptions表不存在")
            return False
        
        print("✅ auto_download_subscriptions表存在")
        
        # 检查字段
        columns = inspector.get_columns('auto_download_subscriptions')
        column_names = [col['name'] for col in columns]
        
        print(f"📋 当前字段: {column_names}")
        
        if 'resource_hash' in column_names:
            print("✅ resource_hash字段已存在")
            
            # 检查索引
            indexes = inspector.get_indexes('auto_download_subscriptions')
            index_names = [idx['name'] for idx in indexes]
            
            if 'ix_auto_download_subscriptions_resource_hash' in index_names:
                print("✅ resource_hash索引已存在")
            else:
                print("🔧 创建resource_hash索引...")
                with engine.connect() as conn:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_auto_download_subscriptions_resource_hash 
                        ON auto_download_subscriptions (resource_hash)
                    """))
                    conn.commit()
                print("✅ resource_hash索引创建成功")
            
            return True
        
        print("🔧 添加resource_hash字段...")
        
        # 使用应用的数据库连接添加字段
        with engine.connect() as conn:
            # 添加字段
            conn.execute(text("""
                ALTER TABLE auto_download_subscriptions 
                ADD COLUMN resource_hash VARCHAR(64) DEFAULT NULL
            """))
            
            # 创建索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_auto_download_subscriptions_resource_hash 
                ON auto_download_subscriptions (resource_hash)
            """))
            
            conn.commit()
        
        print("✅ resource_hash字段添加成功")
        print("✅ resource_hash索引创建成功")
        
        # 验证
        inspector = inspect(engine)
        columns = inspector.get_columns('auto_download_subscriptions')
        column_names = [col['name'] for col in columns]
        
        if 'resource_hash' in column_names:
            print("✅ 字段添加验证通过")
        else:
            print("❌ 字段添加验证失败")
            return False
        
        # 测试查询
        print("🔍 测试查询...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM auto_download_subscriptions"))
            count = result.scalar()
            print(f"   📊 订阅记录总数: {count}")
            
            if count > 0:
                result = conn.execute(text("SELECT id, resource_hash FROM auto_download_subscriptions LIMIT 3"))
                rows = result.fetchall()
                print("   📊 前3条记录:")
                for row in rows:
                    print(f"      ID: {row[0]}, resource_hash: {row[1]}")
        
        print("\n" + "=" * 60)
        print("✅ 生产环境数据库修复完成!")
        print("🚀 重启应用以清除SQLAlchemy缓存")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入应用模块失败: {e}")
        print("💡 请确认在正确的项目目录中运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 修复过程失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_production_database()
    sys.exit(0 if success else 1)