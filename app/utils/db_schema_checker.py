"""
数据库Schema检查器
用于检查和自动添加缺失的字段
"""

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.db import engine
from app.utils.logger import logger


class DatabaseSchemaChecker:
    """数据库Schema检查器"""

    def __init__(self):
        self.engine = engine

    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """检查表中是否存在指定列"""
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            return any(col["name"] == column_name for col in columns)
        except Exception as e:
            logger.error(f"检查列是否存在时出错: {e}")
            return False

    def add_column_if_not_exists(
        self, table_name: str, column_name: str, column_definition: str
    ) -> bool:
        """如果列不存在则添加列"""
        try:
            if not self.check_column_exists(table_name, column_name):
                logger.info(f"检测到表 {table_name} 缺少列 {column_name}，开始添加...")

                # 构建ALTER TABLE语句
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"

                with self.engine.connect() as connection:
                    connection.execute(text(alter_sql))
                    connection.commit()

                logger.info(f"成功为表 {table_name} 添加列 {column_name}")
                return True
            else:
                logger.debug(f"表 {table_name} 已存在列 {column_name}")
                return False

        except SQLAlchemyError as e:
            logger.error(f"添加列时发生数据库错误: {e}")
            return False
        except Exception as e:
            logger.error(f"添加列时发生未知错误: {e}")
            return False

    def check_and_add_torrent_is_hd_field(self) -> bool:
        """检查并添加torrent表的is_hd字段"""
        table_name = "torrent"
        column_name = "is_hd"
        column_definition = "BOOLEAN DEFAULT 0"

        try:
            result = self.add_column_if_not_exists(
                table_name, column_name, column_definition
            )
            if result:
                logger.info("torrent表is_hd字段添加成功")
            return True
        except Exception as e:
            logger.error(f"检查和添加torrent表is_hd字段时出错: {e}")
            return False

    def check_and_add_actor_subscribe_rating_fields(self) -> bool:
        """检查并添加演员订阅表的评分和评论筛选字段"""
        table_name = "actor_subscribe"

        try:
            # 检查并添加min_rating字段
            rating_added = self.add_column_if_not_exists(
                table_name, "min_rating", "DECIMAL(3,1) DEFAULT 0.0"
            )

            # 检查并添加min_comments字段
            comments_added = self.add_column_if_not_exists(
                table_name, "min_comments", "INTEGER DEFAULT 0"
            )

            if rating_added or comments_added:
                logger.info("演员订阅表评分和评论筛选字段添加成功")

            return True
        except Exception as e:
            logger.error(f"检查和添加演员订阅表筛选字段时出错: {e}")
            return False

    def check_and_add_auto_download_error_message(self) -> bool:
        """检查并添加自动下载订阅表的error_message字段"""
        table_name = "auto_download_subscriptions"
        column_name = "error_message"
        column_definition = "VARCHAR(1000)"

        try:
            result = self.add_column_if_not_exists(
                table_name, column_name, column_definition
            )
            if result:
                logger.info("自动下载订阅表错误信息字段添加成功")
            return True
        except Exception as e:
            logger.error(f"检查和添加自动下载订阅表错误信息字段时出错: {e}")
            return False

    def check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            return table_name in tables
        except Exception as e:
            logger.error(f"检查表是否存在时出错: {e}")
            return False

    def normalize_auto_download_enum_values(self) -> bool:
        """规范化自动下载相关枚举值，修复历史脏数据"""
        try:
            has_subscriptions = self.check_table_exists("auto_download_subscriptions")
            has_rules = self.check_table_exists("auto_download_rules")

            if not has_subscriptions and not has_rules:
                logger.warning("auto_download相关表不存在，跳过枚举值规范化")
                return True

            status_value_map = {
                "PENDING": "pending",
                "DOWNLOADING": "downloading",
                "COMPLETED": "completed",
                "FAILED": "failed",
                "DownloadStatus.PENDING": "pending",
                "DownloadStatus.DOWNLOADING": "downloading",
                "DownloadStatus.COMPLETED": "completed",
                "DownloadStatus.FAILED": "failed",
            }
            time_range_value_map = {
                "DAY": "day",
                "WEEK": "week",
                "MONTH": "month",
                "TimeRangeType.DAY": "day",
                "TimeRangeType.WEEK": "week",
                "TimeRangeType.MONTH": "month",
            }

            with self.engine.connect() as connection:
                if has_subscriptions:
                    for source_value, target_value in status_value_map.items():
                        connection.execute(
                            text(
                                "UPDATE auto_download_subscriptions "
                                "SET status = :target_value "
                                "WHERE status = :source_value"
                            ),
                            {
                                "source_value": source_value,
                                "target_value": target_value,
                            },
                        )

                if has_rules:
                    for source_value, target_value in time_range_value_map.items():
                        connection.execute(
                            text(
                                "UPDATE auto_download_rules "
                                "SET time_range_type = :target_value "
                                "WHERE time_range_type = :source_value"
                            ),
                            {
                                "source_value": source_value,
                                "target_value": target_value,
                            },
                        )

                connection.commit()

            logger.info("auto_download枚举值规范化完成")
            return True
        except SQLAlchemyError as e:
            logger.error(f"规范化auto_download枚举值时发生数据库错误: {e}")
            return False
        except Exception as e:
            logger.error(f"规范化auto_download枚举值时发生未知错误: {e}")
            return False

    def run_schema_checks(self) -> dict:
        """运行所有schema检查"""
        logger.info("开始执行数据库Schema检查...")

        results = {"success": True, "checks_performed": [], "errors": []}

        try:
            # 检查torrent表是否存在并添加is_hd字段
            if self.check_table_exists("torrent"):
                check_result = self.check_and_add_torrent_is_hd_field()
                if check_result:
                    results["checks_performed"].append("torrent.is_hd字段检查完成")
                else:
                    results["success"] = False
                    results["errors"].append("torrent.is_hd字段检查失败")
            else:
                logger.warning("torrent表不存在，跳过is_hd字段检查")
                results["checks_performed"].append("torrent表不存在")

            # 检查auto_download_subscriptions表是否存在并添加字段
            if self.check_table_exists("auto_download_subscriptions"):
                check_result = self.check_and_add_auto_download_error_message()
                if check_result:
                    results["checks_performed"].append(
                        "auto_download_subscriptions.error_message字段检查完成"
                    )
                else:
                    results["success"] = False
                    results["errors"].append(
                        "auto_download_subscriptions.error_message字段检查失败"
                    )
            else:
                logger.warning(
                    "auto_download_subscriptions表不存在，跳过error_message字段检查"
                )
                results["checks_performed"].append(
                    "auto_download_subscriptions表不存在"
                )

            # 检查actor_subscribe表是否存在并添加字段
            if self.check_table_exists("actor_subscribe"):
                check_result = self.check_and_add_actor_subscribe_rating_fields()
                if check_result:
                    results["checks_performed"].append(
                        "actor_subscribe筛选字段检查完成"
                    )
                else:
                    results["success"] = False
                    results["errors"].append("actor_subscribe筛选字段检查失败")
            else:
                logger.warning("actor_subscribe表不存在，跳过筛选字段检查")
                results["checks_performed"].append("actor_subscribe表不存在")

            normalize_result = self.normalize_auto_download_enum_values()
            if normalize_result:
                results["checks_performed"].append("auto_download枚举值规范化完成")
            else:
                results["success"] = False
                results["errors"].append("auto_download枚举值规范化失败")

            # 可以在这里添加更多的字段检查

        except Exception as e:
            logger.error(f"Schema检查过程中发生错误: {e}")
            results["success"] = False
            results["errors"].append(f"Schema检查异常: {str(e)}")

        if results["success"]:
            logger.info("数据库Schema检查完成")
        else:
            logger.error("数据库Schema检查失败")

        return results


# 创建全局实例
schema_checker = DatabaseSchemaChecker()
