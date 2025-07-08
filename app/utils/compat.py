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


def fix_starlette_python312_compatibility():
    """修复Starlette在Python 3.12中的兼容性问题"""
    import sys
    if sys.version_info >= (3, 12):
        # 针对Python 3.12的特殊处理
        try:
            import contextlib
            
            # 如果没有collapse_excgroups，添加一个兼容的实现
            if not hasattr(contextlib, 'collapse_excgroups'):
                # 创建一个兼容的collapse_excgroups函数
                def collapse_excgroups():
                    # 返回一个null context manager
                    return contextlib.nullcontext()
                
                # 将函数添加到contextlib模块中
                contextlib.collapse_excgroups = collapse_excgroups
                
                # 同时为ExceptionGroup提供兼容性支持
                if not hasattr(contextlib, 'ExceptionGroup'):
                    # 如果没有ExceptionGroup，创建一个简单的替代
                    class ExceptionGroup(Exception):
                        def __init__(self, message, exceptions):
                            super().__init__(message)
                            self.exceptions = exceptions
                    
                    contextlib.ExceptionGroup = ExceptionGroup
                    
        except ImportError:
            pass
        except Exception as e:
            # 如果修复失败，记录错误但不影响启动
            print(f"Warning: Failed to apply starlette compatibility fix: {e}")


def fix_exception_group_compatibility():
    """修复ExceptionGroup在Python 3.12中的兼容性问题"""
    import sys
    if sys.version_info >= (3, 12):
        try:
            # 确保ExceptionGroup可用
            import builtins
            if not hasattr(builtins, 'ExceptionGroup'):
                class ExceptionGroup(Exception):
                    def __init__(self, message, exceptions):
                        super().__init__(message)
                        self.exceptions = exceptions
                        
                    def __str__(self):
                        return f"{super().__str__()}: {len(self.exceptions)} exceptions"
                
                builtins.ExceptionGroup = ExceptionGroup
        except Exception as e:
            print(f"Warning: Failed to apply ExceptionGroup compatibility fix: {e}")


def init_compatibility():
    """初始化所有兼容性修复"""
    suppress_bcrypt_warnings()
    fix_exception_group_compatibility()
    fix_starlette_python312_compatibility()