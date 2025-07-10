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
            return any(col['name'] == column_name for col in columns)
        except Exception as e:
            logger.error(f"检查列是否存在时出错: {e}")
            return False
    
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_definition: str) -> bool:
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
    
    def check_and_add_actor_subscribe_rating_fields(self) -> bool:
        """检查并添加演员订阅表的评分和评论筛选字段"""
        table_name = "actor_subscribe"
        
        try:
            # 检查并添加min_rating字段
            rating_added = self.add_column_if_not_exists(
                table_name, 
                "min_rating", 
                "DECIMAL(3,1) DEFAULT 0.0"
            )
            
            # 检查并添加min_comments字段
            comments_added = self.add_column_if_not_exists(
                table_name, 
                "min_comments", 
                "INTEGER DEFAULT 0"
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
            result = self.add_column_if_not_exists(table_name, column_name, column_definition)
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
    
    def run_schema_checks(self) -> dict:
        """运行所有schema检查"""
        logger.info("开始执行数据库Schema检查...")
        
        results = {
            'success': True,
            'checks_performed': [],
            'errors': []
        }
        
        try:
            # 检查auto_download_subscriptions表是否存在并添加字段
            if self.check_table_exists('auto_download_subscriptions'):
                check_result = self.check_and_add_auto_download_error_message()
                if check_result:
                    results['checks_performed'].append('auto_download_subscriptions.error_message字段检查完成')
                else:
                    results['success'] = False
                    results['errors'].append('auto_download_subscriptions.error_message字段检查失败')
            else:
                logger.warning("auto_download_subscriptions表不存在，跳过error_message字段检查")
                results['checks_performed'].append('auto_download_subscriptions表不存在')
            
            # 检查actor_subscribe表是否存在并添加字段
            if self.check_table_exists('actor_subscribe'):
                check_result = self.check_and_add_actor_subscribe_rating_fields()
                if check_result:
                    results['checks_performed'].append('actor_subscribe筛选字段检查完成')
                else:
                    results['success'] = False
                    results['errors'].append('actor_subscribe筛选字段检查失败')
            else:
                logger.warning("actor_subscribe表不存在，跳过筛选字段检查")
                results['checks_performed'].append('actor_subscribe表不存在')
            
            # 可以在这里添加更多的字段检查
            
        except Exception as e:
            logger.error(f"Schema检查过程中发生错误: {e}")
            results['success'] = False
            results['errors'].append(f"Schema检查异常: {str(e)}")
        
        if results['success']:
            logger.info("数据库Schema检查完成")
        else:
            logger.error("数据库Schema检查失败")
        
        return results


# 创建全局实例
schema_checker = DatabaseSchemaChecker()