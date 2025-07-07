import os.path
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional, Dict, List
from functools import wraps

cache_path = Path(f'{Path(__file__).cwd()}/config/cache')


def get_cache_path(parent: str, path: str):
    md = hashlib.md5()
    md.update(path.encode("utf-8"))
    return os.path.join(cache_path, parent, md.hexdigest())


def cache_file(parent: str, path: str, content: bytes):
    cache_file_path = get_cache_path(parent, path)

    folder = os.path.abspath(os.path.join(cache_file_path, '..'))
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(cache_file_path, 'wb') as file:
        file.write(content)


def get_cache_file(parent: str, path: str):
    cache_file_path = get_cache_path(parent, path)
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'rb') as file:
            return file.read()


def clean_cache_file(parent: str, path: str):
    cache_file_path = get_cache_path(parent, path)
    if os.path.exists(cache_file_path):
        os.remove(cache_file_path)


def cache_json(parent: str, key: str, data: Any, expire_time: int = 3600):
    """
    缓存JSON数据
    
    Args:
        parent: 缓存目录名
        key: 缓存键名
        data: 要缓存的数据（可JSON序列化的对象）
        expire_time: 过期时间（秒），默认1小时
    """
    cache_file_path = get_cache_path(parent, key)
    
    folder = os.path.abspath(os.path.join(cache_file_path, '..'))
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    cache_data = {
        "data": data,
        "expire_at": time.time() + expire_time
    }
    
    with open(cache_file_path, 'w', encoding='utf-8') as file:
        json.dump(cache_data, file, ensure_ascii=False)


def get_cache_json(parent: str, key: str) -> Optional[Any]:
    """
    获取缓存的JSON数据
    
    Args:
        parent: 缓存目录名
        key: 缓存键名
    
    Returns:
        缓存的数据，如果不存在或已过期返回None
    """
    cache_file_path = get_cache_path(parent, key)
    if not os.path.exists(cache_file_path):
        return None
    
    with open(cache_file_path, 'r', encoding='utf-8') as file:
        try:
            cache_data = json.load(file)
            if time.time() > cache_data.get("expire_at", 0):
                # 缓存已过期
                os.remove(cache_file_path)
                return None
            return cache_data.get("data")
        except (json.JSONDecodeError, KeyError):
            # 缓存文件损坏
            os.remove(cache_file_path)
            return None


def clean_cache_json(parent: str, key: str):
    """
    清除JSON缓存
    
    Args:
        parent: 缓存目录名
        key: 缓存键名
    """
    clean_cache_file(parent, key)


def cached(parent: str, key_func=None, expire_time: int = 3600):
    """
    缓存装饰器
    
    Args:
        parent: 缓存目录名
        key_func: 生成缓存键的函数，默认使用函数名和参数
        expire_time: 过期时间（秒）
    
    Example:
        @cached('actors')
        def get_actors():
            # 获取演员列表的代码
            return actors
            
        @cached('actor_videos', key_func=lambda name, source: f"{source}_{name}")
        def get_actor_videos(name, source='javdb'):
            # 获取演员视频的代码
            return videos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果第一个参数是self（方法），不将其用于缓存键
            actual_args = args[1:] if args and hasattr(args[0], func.__name__) else args
            
            # 生成缓存键
            try:
                if key_func:
                    # 确保key_func接收正确的参数个数
                    import inspect
                    sig = inspect.signature(key_func)
                    params = list(sig.parameters.values())
                    
                    # 处理参数
                    call_args = {}
                    for i, param in enumerate(params):
                        if i < len(actual_args):
                            # 如果有对应的位置参数，使用位置参数
                            call_args[param.name] = actual_args[i]
                        elif param.name in kwargs:
                            # 如果在kwargs中，使用kwargs
                            call_args[param.name] = kwargs[param.name]
                        elif param.default != inspect.Parameter.empty:
                            # 如果有默认值，使用默认值
                            call_args[param.name] = param.default
                    
                    # 调用key_func
                    cache_key = key_func(**call_args)
                else:
                    # 默认使用函数名和参数生成缓存键
                    args_str = '_'.join([str(arg) for arg in actual_args])
                    kwargs_str = '_'.join([f"{k}_{v}" for k, v in kwargs.items()])
                    cache_key = f"{func.__name__}_{args_str}_{kwargs_str}"
            except Exception as e:
                import logging
                logging.getLogger('cache').error(f"生成缓存键时出错: {str(e)}")
                # 出错时使用安全的缓存键
                cache_key = f"{func.__name__}_{hash(str(actual_args))}"
            
            # 尝试从缓存获取
            cached_data = get_cache_json(parent, cache_key)
            if cached_data is not None:
                return cached_data
            
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_json(parent, cache_key, result, expire_time)
            
            return result
        return wrapper
    return decorator
