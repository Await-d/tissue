#!/usr/bin/env python3
"""
数据库Schema自动检查和修复工具
Automatic database schema checker and fixer

此工具会：
1. 从SQLAlchemy models中读取所有表和字段定义
2. 从实际数据库中读取当前schema
3. 自动检测缺失的表和字段
4. 自动添加缺失的字段（安全的操作）

使用方法:
python db_schema_checker.py --check  # 只检查，不修复
python db_schema_checker.py --fix    # 检查并修复
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from sqlalchemy import inspect, create_engine, text
from sqlalchemy.engine.reflection import Inspector

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import Base, engine
from app.db import models  # 导入所有models

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseSchemaChecker:
    """数据库Schema检查器"""

    def __init__(self, db_url: str = None):
        """
        初始化检查器

        Args:
            db_url: 数据库URL，如果为None则使用默认engine
        """
        if db_url:
            self.engine = create_engine(db_url)
        else:
            self.engine = engine

        self.inspector = inspect(self.engine)
        self.issues = []
        self.fixes = []

    def get_model_schema(self) -> Dict[str, Dict[str, any]]:
        """
        从SQLAlchemy models获取预期的schema

        Returns:
            {table_name: {column_name: column_obj}}
        """
        model_schema = {}

        for table_name, table in Base.metadata.tables.items():
            model_schema[table_name] = {}
            for column in table.columns:
                model_schema[table_name][column.name] = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'default': column.default,
                    'server_default': column.server_default,
                    'primary_key': column.primary_key,
                    'autoincrement': column.autoincrement,
                    'comment': column.comment,
                    'column_obj': column  # 保存原始列对象以便后续使用
                }

        return model_schema

    def get_database_schema(self) -> Dict[str, Set[str]]:
        """
        从实际数据库获取当前schema

        Returns:
            {table_name: set(column_names)}
        """
        db_schema = {}

        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            db_schema[table_name] = {col['name'] for col in columns}

        return db_schema

    def check_schema(self) -> Tuple[Dict, Dict]:
        """
        检查schema差异

        Returns:
            (missing_tables, missing_columns)
            missing_tables: {table_name: columns_dict}
            missing_columns: {table_name: [column_names]}
        """
        model_schema = self.get_model_schema()
        db_schema = self.get_database_schema()

        missing_tables = {}
        missing_columns = {}

        # 检查缺失的表
        for table_name in model_schema:
            if table_name not in db_schema:
                missing_tables[table_name] = model_schema[table_name]
                logger.warning(f"⚠️ 缺失表: {table_name}")
                self.issues.append(f"缺失表: {table_name}")
            else:
                # 检查缺失的列
                model_columns = set(model_schema[table_name].keys())
                db_columns = db_schema[table_name]
                missing_cols = model_columns - db_columns

                if missing_cols:
                    missing_columns[table_name] = list(missing_cols)
                    logger.warning(f"⚠️ 表 {table_name} 缺失列: {missing_cols}")
                    self.issues.append(f"表 {table_name} 缺失列: {missing_cols}")

        return missing_tables, missing_columns

    def fix_missing_columns(self, missing_columns: Dict[str, List[str]], dry_run: bool = False) -> bool:
        """
        修复缺失的列

        Args:
            missing_columns: {table_name: [column_names]}
            dry_run: 如果为True，只打印SQL不执行

        Returns:
            是否成功
        """
        model_schema = self.get_model_schema()
        success = True

        with self.engine.begin() as conn:
            for table_name, columns in missing_columns.items():
                for column_name in columns:
                    try:
                        column_info = model_schema[table_name][column_name]
                        column_obj = column_info['column_obj']

                        # 构建ALTER TABLE语句
                        sql = self._build_add_column_sql(table_name, column_name, column_info)

                        if dry_run:
                            logger.info(f"[DRY RUN] Would execute: {sql}")
                        else:
                            logger.info(f"🔧 添加列: {table_name}.{column_name}")
                            logger.info(f"   SQL: {sql}")
                            conn.execute(text(sql))
                            self.fixes.append(f"添加列: {table_name}.{column_name}")

                    except Exception as e:
                        logger.error(f"❌ 添加列失败 {table_name}.{column_name}: {e}")
                        success = False

        return success

    def _build_add_column_sql(self, table_name: str, column_name: str, column_info: dict) -> str:
        """
        构建ADD COLUMN SQL语句

        Args:
            table_name: 表名
            column_name: 列名
            column_info: 列信息

        Returns:
            SQL语句
        """
        sql_parts = [f"ALTER TABLE {table_name} ADD COLUMN {column_name}"]

        # 类型
        col_type = column_info['type']
        sql_parts.append(col_type)

        # NULL/NOT NULL
        if not column_info['nullable']:
            # 对于NOT NULL列，必须提供默认值
            sql_parts.append("NOT NULL")
            # 尝试添加默认值
            if column_info.get('server_default'):
                sql_parts.append(f"DEFAULT {column_info['server_default'].arg}")
            else:
                # 为NOT NULL列提供合理的默认值
                default_value = self._get_default_value_for_type(col_type)
                if default_value:
                    sql_parts.append(f"DEFAULT {default_value}")

        return " ".join(sql_parts)

    def _get_default_value_for_type(self, col_type: str) -> str:
        """
        根据列类型获取合理的默认值

        Args:
            col_type: 列类型字符串

        Returns:
            默认值字符串
        """
        col_type_upper = col_type.upper()

        if 'INT' in col_type_upper:
            return '0'
        elif 'BOOL' in col_type_upper:
            return '0'
        elif 'FLOAT' in col_type_upper or 'DECIMAL' in col_type_upper or 'NUMERIC' in col_type_upper:
            return '0.0'
        elif 'TEXT' in col_type_upper or 'VARCHAR' in col_type_upper or 'CHAR' in col_type_upper:
            return "''"
        elif 'DATE' in col_type_upper or 'TIME' in col_type_upper:
            return "CURRENT_TIMESTAMP"
        else:
            return "NULL"

    def run_check(self, fix: bool = False, dry_run: bool = False) -> bool:
        """
        运行完整检查

        Args:
            fix: 是否自动修复
            dry_run: 如果为True，只打印SQL不执行

        Returns:
            是否所有检查通过
        """
        logger.info("🔍 开始数据库Schema检查...")

        # 检查schema
        missing_tables, missing_columns = self.check_schema()

        # 报告结果
        if not missing_tables and not missing_columns:
            logger.info("✅ 数据库Schema完整，所有表和字段都存在")
            return True

        # 报告缺失的表
        if missing_tables:
            logger.warning(f"⚠️ 发现 {len(missing_tables)} 个缺失的表")
            logger.warning("   这些表需要通过Alembic迁移来创建")
            logger.warning("   运行: alembic upgrade head")

        # 报告和修复缺失的列
        if missing_columns:
            total_missing_cols = sum(len(cols) for cols in missing_columns.values())
            logger.warning(f"⚠️ 发现 {total_missing_cols} 个缺失的列")

            if fix:
                if dry_run:
                    logger.info("🔧 [DRY RUN] 将执行以下修复:")
                else:
                    logger.info("🔧 开始自动修复缺失的列...")

                success = self.fix_missing_columns(missing_columns, dry_run=dry_run)

                if success:
                    logger.info("✅ 所有缺失的列已成功添加")
                    return True
                else:
                    logger.error("❌ 部分列添加失败，请检查日志")
                    return False
            else:
                logger.info("💡 提示: 使用 --fix 参数自动修复缺失的列")
                return False

        return not (missing_tables or missing_columns)

    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("=" * 60)
        report.append("数据库Schema检查报告")
        report.append("=" * 60)

        if self.issues:
            report.append("\n⚠️ 发现的问题:")
            for issue in self.issues:
                report.append(f"  - {issue}")

        if self.fixes:
            report.append("\n🔧 应用的修复:")
            for fix in self.fixes:
                report.append(f"  - {fix}")

        if not self.issues and not self.fixes:
            report.append("\n✅ 数据库Schema完整，无需修复")

        return "\n".join(report)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据库Schema自动检查和修复工具')
    parser.add_argument('--check', action='store_true', help='只检查，不修复')
    parser.add_argument('--fix', action='store_true', help='检查并自动修复')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，只显示将要执行的SQL')
    parser.add_argument('--db-url', type=str, help='数据库URL（可选）')

    args = parser.parse_args()

    # 如果没有指定任何参数，默认为--check
    if not args.check and not args.fix:
        args.check = True

    try:
        checker = DatabaseSchemaChecker(db_url=args.db_url)

        if args.fix or args.dry_run:
            success = checker.run_check(fix=True, dry_run=args.dry_run)
        else:
            success = checker.run_check(fix=False)

        # 生成并显示报告
        report = checker.generate_report()
        print("\n" + report)

        # 保存报告
        with open("db_schema_check_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        logger.info("📄 检查报告已保存到 db_schema_check_report.txt")

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"❌ 检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
