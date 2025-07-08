"""
异步日志管理器 - 解决日志锁死问题
"""
import asyncio
import inspect
import logging
import queue
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any

import click

# 日志级别颜色
level_name_colors = {
    logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
    logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
    logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
    logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
    logging.CRITICAL: lambda level_name: click.style(
        str(level_name), fg="bright_red"
    ),
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        seperator = " " * (8 - len(record.levelname))
        record.leveltext = level_name_colors[record.levelno](record.levelname + ":") + seperator
        return super().format(record)


class AsyncLoggerManager:
    """异步日志管理器，避免日志锁死"""

    def __init__(self):
        log_path = Path(f'{Path(__file__).cwd()}/config/app.log')
        self.log_queue = queue.Queue()
        self.logger = logging.getLogger(log_path.stem)
        self.logger.setLevel(logging.INFO)
        
        # 清除现有的handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # 终端日志 - 直接输出，不经过队列
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = CustomFormatter(f"%(leveltext)s%(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 文件日志 - 通过异步队列处理
        self.file_handler = RotatingFileHandler(
            filename=log_path,
            mode='a',  # 使用追加模式而不是覆盖模式
            maxBytes=10 * 1024 * 1024,  # 增大文件大小限制
            backupCount=5,
            encoding='utf-8'
        )
        self.file_handler.setLevel(logging.INFO)
        file_formatter = CustomFormatter(f"【%(levelname)s】%(asctime)s - %(message)s")
        self.file_handler.setFormatter(file_formatter)
        
        # 启动异步日志处理线程
        self.stop_event = threading.Event()
        self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.log_thread.start()

    def _log_worker(self):
        """异步日志处理工作线程"""
        while not self.stop_event.is_set():
            try:
                # 从队列获取日志记录，设置超时避免阻塞
                record = self.log_queue.get(timeout=1)
                if record is None:  # 退出信号
                    break
                # 写入文件
                self.file_handler.emit(record)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                # 避免日志系统自身错误导致无限循环
                print(f"日志处理错误: {e}")

    def log(self, method: str, msg: str, *args, **kwargs):
        """记录日志"""
        caller_name = self.__get_caller()
        
        # 创建日志记录
        level = getattr(logging, method.upper())
        record = logging.LogRecord(
            name=self.logger.name,
            level=level,
            pathname="",
            lineno=0,
            msg=f"{caller_name} - {msg}",
            args=args,
            exc_info=None
        )
        
        # 直接处理控制台输出
        if self.logger.isEnabledFor(level):
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                    handler.emit(record)
        
        # 文件日志通过队列异步处理
        if level >= logging.INFO:
            try:
                self.log_queue.put_nowait(record)
            except queue.Full:
                # 队列满了，直接丢弃（避免阻塞）
                pass

    @staticmethod
    def __get_caller():
        """获取调用者信息"""
        caller_name = None
        for i in inspect.stack()[3:]:
            filepath = Path(i.filename)
            parts = filepath.parts
            if not caller_name:
                if parts[-1] == "__init__.py":
                    caller_name = parts[-2]
                else:
                    caller_name = parts[-1]
            if "app" in parts:
                if "main.py" in parts:
                    break
            elif len(parts) != 1:
                break
        if caller_name and caller_name.endswith('.py'):
            caller_name = caller_name[:-3]
        return caller_name or "logger"

    def info(self, msg: str, *args, **kwargs):
        self.log("info", msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self.log("debug", msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.log("warning", msg, *args, **kwargs)

    def warn(self, msg: str, *args, **kwargs):
        self.log("warning", msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.log("error", msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.log("critical", msg, *args, **kwargs)

    def shutdown(self):
        """关闭日志管理器"""
        self.stop_event.set()
        self.log_queue.put(None)  # 发送退出信号
        self.log_thread.join(timeout=5)
        self.file_handler.close()


# 智能下载专用的简化日志记录器
class SmartDownloadLogger:
    """智能下载专用日志记录器，减少日志输出量"""
    
    def __init__(self):
        self.main_logger = AsyncLoggerManager()
        self.batch_logs = []
        self.batch_size = 10
        
    def info(self, msg: str, *args, **kwargs):
        # 对于智能下载，只记录重要信息
        if any(keyword in msg for keyword in ['规则', '执行', '完成', '错误', '失败']):
            self.main_logger.info(msg, *args, **kwargs)
        else:
            # 批量处理次要日志
            self._batch_log("info", msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        # 调试日志只在开发环境输出
        pass
    
    def warning(self, msg: str, *args, **kwargs):
        self.main_logger.warning(msg, *args, **kwargs)
    
    def warn(self, msg: str, *args, **kwargs):
        self.main_logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.main_logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self.main_logger.critical(msg, *args, **kwargs)
    
    def _batch_log(self, level: str, msg: str, *args, **kwargs):
        """批量处理日志"""
        self.batch_logs.append((level, msg, args, kwargs))
        if len(self.batch_logs) >= self.batch_size:
            self._flush_batch()
    
    def _flush_batch(self):
        """刷新批量日志"""
        if self.batch_logs:
            # 只记录批量日志的摘要
            summary = f"批量处理 {len(self.batch_logs)} 条日志记录"
            self.main_logger.info(summary)
            self.batch_logs.clear()
    
    def flush(self):
        """手动刷新批量日志"""
        self._flush_batch()


# 根据上下文选择合适的日志记录器
def get_logger():
    """获取适合当前上下文的日志记录器"""
    # 检查调用栈，如果是智能下载相关，使用专用日志器
    for frame_info in inspect.stack():
        if 'auto_download' in frame_info.filename or 'video_collector' in frame_info.filename:
            return SmartDownloadLogger()
    
    # 默认使用异步日志记录器
    return AsyncLoggerManager()


# 全局日志实例
async_logger = AsyncLoggerManager()