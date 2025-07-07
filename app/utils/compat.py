"""
兼容性处理模块
用于处理第三方库的兼容性问题和警告
"""
import warnings
import logging


def suppress_bcrypt_warnings():
    """抑制bcrypt版本兼容性警告"""
    # 抑制passlib的bcrypt版本检查警告
    warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")
    warnings.filterwarnings("ignore", category=UserWarning, module="passlib")
    
    # 设置passlib日志级别
    passlib_logger = logging.getLogger("passlib")
    passlib_logger.setLevel(logging.ERROR)
    
    # 尝试monkey patch修复bcrypt版本检查
    try:
        import bcrypt
        if not hasattr(bcrypt, '__about__'):
            # 为bcrypt模块添加缺失的__about__属性
            class About:
                __version__ = getattr(bcrypt, '__version__', '4.2.1')
            
            bcrypt.__about__ = About()
    except ImportError:
        pass


def init_compatibility():
    """初始化所有兼容性修复"""
    suppress_bcrypt_warnings()