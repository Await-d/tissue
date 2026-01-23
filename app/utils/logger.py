import inspect
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

import click

# 日志级别颜色
level_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bright_red',
}


class CustomFormatter(logging.Formatter):
    def format(self, record):
        seperator = " " * (8 - len(record.levelname))
        record.leveltext = click.style(record.levelname + ":", fg=level_colors.get(record.levelname, 'white')) + seperator
        return super().format(record)


# 文件 logger - 使用模块级别的单例
_file_logger = None
_logger_manager = None


def _get_file_logger():
    """获取文件 logger（单例）"""
    global _file_logger
    if _file_logger is None:
        log_path = Path(f'{Path(__file__).cwd()}/config/app.log')
        
        _file_logger = logging.getLogger("tissue_file")
        _file_logger.setLevel(logging.INFO)
        _file_logger.propagate = False
        
        # 只在没有 handler 时添加
        if not _file_logger.handlers:
            file_handler = RotatingFileHandler(
                filename=log_path,
                mode='a',
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter("【%(levelname)s】%(asctime)s - %(message)s")
            file_handler.setFormatter(file_formatter)
            _file_logger.addHandler(file_handler)
    
    return _file_logger


class LoggerManager:

    def __init__(self):
        self.file_logger = _get_file_logger()

    def log(self, level: str, msg: str, *args, **kwargs):
        try:
            caller_name = self.__get_caller()
        except Exception:
            caller_name = "app"
        
        full_msg = f"{caller_name} - {msg}"
        
        # 终端输出 - 直接用 print
        level_upper = level.upper()
        color = level_colors.get(level_upper, 'white')
        separator = " " * (8 - len(level_upper))
        colored_level = click.style(f"{level_upper}:", fg=color)
        print(f"{colored_level}{separator}{full_msg}", file=sys.stderr, flush=True)
        
        # 文件输出
        log_method = getattr(self.file_logger, level.lower(), self.file_logger.info)
        log_method(full_msg, *args, **kwargs)

    @staticmethod
    def __get_caller():
        try:
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
            return caller_name or "app"
        except Exception:
            return "app"

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


# 初始化公共日志 - 使用函数确保单例
def get_logger():
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager

logger = get_logger()
