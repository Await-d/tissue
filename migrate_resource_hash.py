#!/usr/bin/env python3
"""
生产环境数据库迁移脚本 - 添加resource_hash字段
用于在生产环境中安全地添加resource_hash字段和索引
"""

import sqlite3
import sys
from pathlib import Path

def migrate_resource_hash():
    """安全地添加resource_hash字段和索引"""
    
    # 数据库文件路径
    db_path = Path('config/app.db')
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='auto_download_subscriptions'
        """)
        
        if not cursor.fetchone():
            print("❌ auto_download_subscriptions表不存在")
            return False
        
        # 检查resource_hash字段是否已存在
        cursor.execute("PRAGMA table_info(auto_download_subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'resource_hash' in columns:
            print("✅ resource_hash字段已存在，无需迁移")
            
            # 检查索引是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='ix_auto_download_subscriptions_resource_hash'
            """)
            
            if not cursor.fetchone():
                print("🔧 创建resource_hash索引...")
                cursor.execute("""
                    CREATE INDEX ix_auto_download_subscriptions_resource_hash 
                    ON auto_download_subscriptions (resource_hash)
                """)
                conn.commit()
                print("✅ resource_hash索引创建成功")
            else:
                print("✅ resource_hash索引已存在")
            
            conn.close()
            return True
        
        print("🔧 开始添加resource_hash字段...")
        
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
        
        # 提交更改
        conn.commit()
        
        print("✅ resource_hash字段添加成功")
        print("✅ resource_hash索引创建成功")
        
        # 验证更改
        cursor.execute("PRAGMA table_info(auto_download_subscriptions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'resource_hash' in columns:
            print("✅ 字段验证通过")
        else:
            print("❌ 字段验证失败")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 开始生产环境数据库迁移")
    print("=" * 50)
    
    success = migrate_resource_hash()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 迁移完成! 可以重启应用")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ 迁移失败! 请检查错误信息")
        print("=" * 50)
        sys.exit(1)