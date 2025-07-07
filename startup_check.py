#!/usr/bin/env python3
"""
启动检查脚本 - 用于检测和修复生产环境问题
Startup check script for detecting and fixing production environment issues
"""

import sys
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StartupChecker:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.issues_found = []
        self.fixes_applied = []
        
    def check_database_connection(self) -> bool:
        """检查数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT 1")
            conn.close()
            logger.info("✅ 数据库连接正常")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            self.issues_found.append(f"数据库连接失败: {e}")
            return False
    
    def check_migration_status(self) -> bool:
        """检查数据库迁移状态"""
        try:
            result = subprocess.run(
                ["alembic", "current"], 
                capture_output=True, 
                text=True, 
                cwd="."
            )
            
            current_revision = result.stdout.strip()
            if not current_revision or "head" not in current_revision:
                logger.warning("⚠️ 数据库迁移不是最新版本")
                self.issues_found.append("数据库迁移不是最新版本")
                return False
            
            logger.info("✅ 数据库迁移状态正常")
            return True
        except Exception as e:
            logger.error(f"❌ 检查迁移状态失败: {e}")
            self.issues_found.append(f"检查迁移状态失败: {e}")
            return False
    
    def check_enum_values(self) -> bool:
        """检查枚举值是否正确"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查auto_download_rules表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='auto_download_rules'
            """)
            
            if not cursor.fetchone():
                logger.warning("⚠️ auto_download_rules表不存在")
                self.issues_found.append("auto_download_rules表不存在")
                conn.close()
                return False
            
            # 检查枚举值格式
            cursor.execute("""
                SELECT time_range_type, status 
                FROM auto_download_rules 
                WHERE time_range_type IN ('DAY', 'WEEK', 'MONTH') 
                OR status IN ('ACTIVE', 'INACTIVE')
            """)
            
            old_enum_records = cursor.fetchall()
            if old_enum_records:
                logger.warning(f"⚠️ 发现 {len(old_enum_records)} 条旧格式枚举值记录")
                self.issues_found.append(f"发现 {len(old_enum_records)} 条旧格式枚举值记录")
                conn.close()
                return False
            
            logger.info("✅ 枚举值格式正确")
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 检查枚举值失败: {e}")
            self.issues_found.append(f"检查枚举值失败: {e}")
            return False
    
    def check_required_columns(self) -> bool:
        """检查必需的列是否存在"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查auto_download_rules表结构
            cursor.execute("PRAGMA table_info(auto_download_rules)")
            columns = [row[1] for row in cursor.fetchall()]
            
            required_columns = ['create_by', 'create_time', 'update_by', 'update_time']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                logger.warning(f"⚠️ 缺少必需的列: {missing_columns}")
                self.issues_found.append(f"缺少必需的列: {missing_columns}")
                conn.close()
                return False
            
            logger.info("✅ 表结构完整")
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 检查表结构失败: {e}")
            self.issues_found.append(f"检查表结构失败: {e}")
            return False
    
    def auto_fix_migrations(self) -> bool:
        """自动修复迁移问题"""
        try:
            logger.info("🔧 开始自动修复数据库迁移...")
            
            # 运行数据库迁移
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                logger.info("✅ 数据库迁移修复成功")
                self.fixes_applied.append("数据库迁移修复成功")
                return True
            else:
                logger.error(f"❌ 数据库迁移修复失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 自动修复迁移失败: {e}")
            return False
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        logger.info("🚀 开始启动检查...")
        
        results = {
            "database_connection": self.check_database_connection(),
            "migration_status": self.check_migration_status(),
            "enum_values": self.check_enum_values(),
            "required_columns": self.check_required_columns(),
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied
        }
        
        # 如果发现问题，尝试自动修复
        if self.issues_found:
            logger.info("🔧 发现问题，尝试自动修复...")
            if self.auto_fix_migrations():
                # 重新检查修复后的状态
                logger.info("🔄 重新检查修复后的状态...")
                results["migration_status"] = self.check_migration_status()
                results["enum_values"] = self.check_enum_values()
                results["required_columns"] = self.check_required_columns()
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成检查报告"""
        report = []
        report.append("=" * 50)
        report.append("启动检查报告")
        report.append("=" * 50)
        
        # 检查结果
        report.append("\n📊 检查结果:")
        for check, status in results.items():
            if check not in ["issues_found", "fixes_applied"]:
                status_icon = "✅" if status else "❌"
                report.append(f"  {status_icon} {check}: {'通过' if status else '失败'}")
        
        # 发现的问题
        if results["issues_found"]:
            report.append("\n⚠️ 发现的问题:")
            for issue in results["issues_found"]:
                report.append(f"  - {issue}")
        
        # 应用的修复
        if results["fixes_applied"]:
            report.append("\n🔧 应用的修复:")
            for fix in results["fixes_applied"]:
                report.append(f"  - {fix}")
        
        # 总结
        all_passed = all(results[k] for k in results if k not in ["issues_found", "fixes_applied"])
        report.append(f"\n📋 总结: {'所有检查通过' if all_passed else '存在问题需要手动处理'}")
        
        if not all_passed:
            report.append("\n🔧 建议操作:")
            report.append("  1. 确保在正确的项目目录中运行此脚本")
            report.append("  2. 检查数据库文件权限")
            report.append("  3. 手动运行: alembic upgrade head")
            report.append("  4. 如果问题持续，请检查日志文件")
        
        return "\n".join(report)

def main():
    """主函数"""
    # 检查是否在正确的目录中
    if not os.path.exists("alembic.ini"):
        logger.error("❌ 未找到alembic.ini文件，请确保在正确的项目目录中运行此脚本")
        sys.exit(1)
    
    checker = StartupChecker()
    results = checker.run_all_checks()
    report = checker.generate_report(results)
    
    print(report)
    
    # 保存报告到文件
    with open("startup_check_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("📄 检查报告已保存到 startup_check_report.txt")
    
    # 根据结果设置退出码
    all_passed = all(results[k] for k in results if k not in ["issues_found", "fixes_applied"])
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()