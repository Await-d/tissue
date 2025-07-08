"""
将auto_download_rules表中的time_range_type字段值从小写转换为大写
"""
import sqlite3
import os
from pathlib import Path

def run_migration():
    """执行数据库迁移，将time_range_type字段值从小写转换为大写"""
    # 获取数据库路径
    db_path = Path(f'{Path(__file__).parent.parent.parent.parent}/config/app.db')
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 查询现有记录
        cursor.execute("SELECT id, time_range_type FROM auto_download_rules")
        records = cursor.fetchall()
        
        # 更新记录
        updated_count = 0
        for record_id, time_range_type in records:
            if time_range_type and isinstance(time_range_type, str):
                upper_value = time_range_type.upper()
                cursor.execute(
                    "UPDATE auto_download_rules SET time_range_type = ? WHERE id = ?", 
                    (upper_value, record_id)
                )
                updated_count += 1
        
        # 提交更改
        conn.commit()
        
        print(f"成功更新 {updated_count} 条记录")
        return True
    
    except Exception as e:
        print(f"迁移过程中发生错误: {str(e)}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration() 