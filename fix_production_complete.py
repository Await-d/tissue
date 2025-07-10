#!/usr/bin/env python3
"""
完整的生产环境数据库修复脚本
直接添加缺失的resource_hash字段和索引
"""

import sqlite3
import sys
import os
from pathlib import Path

def find_production_database():
    """查找生产环境数据库文件"""
    # 常见的生产环境数据库路径
    possible_paths = [
        Path('config/app.db'),
        Path('app.db'),
        Path('/app/config/app.db'),
        Path('/app/app.db'),
        Path('../config/app.db'),
        Path('tissue.db'),
    ]
    
    print("🔍 查找生产环境数据库文件...")
    for path in possible_paths:
        if path.exists():
            size = path.stat().st_size
            print(f"   📁 找到: {path} ({size} bytes)")
            
            # 检查是否包含auto_download_subscriptions表
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='auto_download_subscriptions'
                """)
                
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM auto_download_subscriptions")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ 包含订阅表，记录数: {count}")
                    conn.close()
                    return path
                else:
                    print(f"   ⚠️  不包含订阅表，跳过")
                    
                conn.close()
            except Exception as e:
                print(f"   ❌ 检查失败: {e}")
                
    return None

def backup_database(db_path):
    """备份数据库"""
    backup_path = db_path.with_suffix(f'{db_path.suffix}.backup')
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"   ✅ 数据库已备份到: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"   ❌ 备份失败: {e}")
        return None

def add_resource_hash_field(db_path):
    """添加resource_hash字段和索引"""
    print(f"🔧 开始修复数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(auto_download_subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'resource_hash' in columns:
            print("   ✅ resource_hash字段已存在，无需添加")
            conn.close()
            return True
        
        print("   🔧 添加resource_hash字段...")
        
        # 添加字段
        cursor.execute("""
            ALTER TABLE auto_download_subscriptions 
            ADD COLUMN resource_hash VARCHAR(64) DEFAULT NULL
        """)
        
        print("   ✅ resource_hash字段添加成功")
        
        # 创建索引
        print("   🔧 创建resource_hash索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_auto_download_subscriptions_resource_hash 
            ON auto_download_subscriptions (resource_hash)
        """)
        
        print("   ✅ resource_hash索引创建成功")
        
        # 提交更改
        conn.commit()
        
        # 验证更改
        cursor.execute("PRAGMA table_info(auto_download_subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'resource_hash' in columns:
            print("   ✅ 字段添加验证通过")
        else:
            print("   ❌ 字段添加验证失败")
            conn.close()
            return False
        
        # 检查索引
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='ix_auto_download_subscriptions_resource_hash'
        """)
        
        if cursor.fetchone():
            print("   ✅ 索引创建验证通过")
        else:
            print("   ❌ 索引创建验证失败")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"   ❌ 数据库操作失败: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")
        return False

def verify_fix(db_path):
    """验证修复结果"""
    print("🔍 验证修复结果...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(auto_download_subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"   📋 当前字段: {columns}")
        
        if 'resource_hash' in columns:
            print("   ✅ resource_hash字段存在")
        else:
            print("   ❌ resource_hash字段不存在")
            conn.close()
            return False
        
        # 检查索引
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='auto_download_subscriptions'
        """)
        
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"   📋 现有索引: {indexes}")
        
        if 'ix_auto_download_subscriptions_resource_hash' in indexes:
            print("   ✅ resource_hash索引存在")
        else:
            print("   ❌ resource_hash索引不存在")
            conn.close()
            return False
        
        # 测试查询
        cursor.execute("SELECT id, resource_hash FROM auto_download_subscriptions LIMIT 3")
        results = cursor.fetchall()
        
        print(f"   📊 测试查询结果 (前3条):")
        for row in results:
            print(f"      ID: {row[0]}, resource_hash: {row[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 生产环境数据库完整修复工具")
    print("=" * 60)
    
    # 查找数据库
    db_path = find_production_database()
    if not db_path:
        print("❌ 未找到生产环境数据库文件")
        print("💡 请确认数据库文件路径或应用已正确初始化")
        return False
    
    print(f"\n📁 使用数据库: {db_path}")
    
    # 备份数据库
    print("\n💾 备份数据库...")
    backup_path = backup_database(db_path)
    if not backup_path:
        print("⚠️  备份失败，但继续执行修复")
    
    # 添加字段
    print("\n🔧 修复数据库...")
    if not add_resource_hash_field(db_path):
        print("\n❌ 数据库修复失败!")
        return False
    
    # 验证修复
    print("\n🔍 验证修复...")
    if not verify_fix(db_path):
        print("\n❌ 修复验证失败!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 生产环境数据库修复完成!")
    print("🚀 请重启应用以应用更改")
    if backup_path:
        print(f"💾 备份文件: {backup_path}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)