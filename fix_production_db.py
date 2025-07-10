#!/usr/bin/env python3
"""
修复生产环境数据库问题
适用于多种数据库配置情况
"""

import sqlite3
import sys
import os
from pathlib import Path

def find_database_files():
    """查找所有可能的数据库文件"""
    possible_paths = [
        Path('config/app.db'),
        Path('app.db'),
        Path('tissue.db'),
        Path('../config/app.db'),
        Path('/app/config/app.db'),
        Path('/app/app.db'),
    ]
    
    existing_files = []
    for path in possible_paths:
        if path.exists() and path.stat().st_size > 0:
            existing_files.append(path)
    
    return existing_files

def check_and_fix_database(db_path):
    """检查并修复单个数据库文件"""
    print(f"\n📁 检查数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='auto_download_subscriptions'
        """)
        
        if not cursor.fetchone():
            print("   ⚠️  auto_download_subscriptions表不存在，跳过")
            conn.close()
            return False
        
        # 检查记录数
        cursor.execute("SELECT COUNT(*) FROM auto_download_subscriptions")
        count = cursor.fetchone()[0]
        print(f"   📊 订阅记录数: {count}")
        
        # 检查resource_hash字段是否存在
        cursor.execute("PRAGMA table_info(auto_download_subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'resource_hash' in columns:
            print("   ✅ resource_hash字段已存在")
            
            # 检查索引
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='ix_auto_download_subscriptions_resource_hash'
            """)
            
            if cursor.fetchone():
                print("   ✅ resource_hash索引已存在")
            else:
                print("   🔧 创建resource_hash索引...")
                cursor.execute("""
                    CREATE INDEX ix_auto_download_subscriptions_resource_hash 
                    ON auto_download_subscriptions (resource_hash)
                """)
                conn.commit()
                print("   ✅ resource_hash索引创建成功")
            
            conn.close()
            return True
        
        print("   🔧 添加resource_hash字段...")
        
        # 添加resource_hash字段
        cursor.execute("""
            ALTER TABLE auto_download_subscriptions 
            ADD COLUMN resource_hash VARCHAR(64) DEFAULT NULL
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX ix_auto_download_subscriptions_resource_hash 
            ON auto_download_subscriptions (resource_hash)
        """)
        
        conn.commit()
        
        print("   ✅ resource_hash字段添加成功")
        print("   ✅ resource_hash索引创建成功")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"   ❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 查找并修复生产环境数据库")
    print("=" * 60)
    
    # 查找所有数据库文件
    db_files = find_database_files()
    
    if not db_files:
        print("❌ 未找到任何数据库文件")
        print("   请确认应用已正确初始化")
        return False
    
    print(f"📋 找到 {len(db_files)} 个数据库文件:")
    for db_file in db_files:
        print(f"   - {db_file} ({db_file.stat().st_size} bytes)")
    
    # 处理每个数据库文件
    success_count = 0
    for db_file in db_files:
        if check_and_fix_database(db_file):
            success_count += 1
    
    print(f"\n" + "=" * 60)
    if success_count > 0:
        print(f"✅ 成功修复 {success_count} 个数据库文件")
        print("🚀 请重启应用以应用更改")
    else:
        print("❌ 没有数据库文件需要修复或修复失败")
    print("=" * 60)
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)