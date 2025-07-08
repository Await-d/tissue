"""
日志系统初始化 - 根据环境选择合适的日志记录器
"""
import os
from app.utils.logger import LoggerManager
from app.utils.async_logger import AsyncLoggerManager


def init_logger():
    """初始化日志系统"""
    # 根据环境变量选择日志记录器
    use_async_logger = os.getenv('USE_ASYNC_LOGGER', 'true').lower() == 'true'
    
    if use_async_logger:
        # 使用异步日志记录器
        return AsyncLoggerManager()
    else:
        # 使用同步日志记录器
        return LoggerManager()


# 全局日志实例
logger = init_logger()