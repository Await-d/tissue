import os
import os.path
import hashlib
import json
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Dict, List
from functools import wraps

cache_path = Path(f'{Path(__file__).cwd()}/config/cache')

# 元数据缓存默认 TTL（秒）
DEFAULT_CACHE_TTL_SECONDS = 24 * 60 * 60
# 上游抓取失败但本地存在过期副本时，延长该副本可用时间
STALE_FALLBACK_TTL_SECONDS = 30 * 60
# 负缓存 TTL：明确的 4xx 缓存久一些，网络/5xx 类错误尽快重试
NEGATIVE_TTL_NOT_FOUND_SECONDS = 6 * 60 * 60
NEGATIVE_TTL_TRANSIENT_SECONDS = 5 * 60


def get_cache_path(parent: str, path: str):
    md = hashlib.md5()
    md.update(path.encode("utf-8"))
    return os.path.join(cache_path, parent, md.hexdigest())


def _write_bytes_atomic(target: str, content: bytes) -> None:
    """先写同目录临时文件再 rename，保证读到的永远是完整内容。

    首页一次渲染几十张封面，用户连续刷新时同一个 URL 很可能被并发写入
    同一个文件；直接 open(...,'wb') 会让两次写入交错，产出头部正常但
    内容损坏的图片，并在整个 TTL 内被当作好图持续返回。
    同目录 os.replace 是原子操作，不会出现半截文件。
    """
    folder = os.path.dirname(target)
    os.makedirs(folder, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=folder, suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp_path, target)
    except BaseException:
        # 失败时不要留下 .tmp 残留
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def cache_file(parent: str, path: str, content: bytes):
    # 封面/头像地址允许为空（刮削结果可能没有图），空 key 直接跳过，
    # 否则 get_cache_path 会在 None.encode 上抛 AttributeError 中断调用方流程
    if not path:
        return

    _write_bytes_atomic(get_cache_path(parent, path), content)


def get_cache_file(parent: str, path: str):
    if not path:
        return None

    cache_file_path = get_cache_path(parent, path)
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'rb') as file:
            return file.read()


def clean_cache_file(parent: str, path: str):
    if not path:
        return

    cache_file_path = get_cache_path(parent, path)
    if os.path.exists(cache_file_path):
        os.remove(cache_file_path)
    meta_file_path = get_cache_meta_path(parent, path)
    if os.path.exists(meta_file_path):
        os.remove(meta_file_path)


# ---------------------------------------------------------------------------
# 带元数据的二进制缓存
#
# 与上面的 cache_file / get_cache_file 共用同一个数据文件路径（保持向后兼容，
# app/service/video.py、app/utils/notify/telegram.py 等旧调用方无需改动），
# 额外在同目录写一个 <hash>.meta.json 记录 content_type / etag / 过期时间。
# 这样上游抓取失败时可以判断\"本地有过期副本\"并继续对外提供服务。
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class CacheLookup:
    """一次缓存查询的结果。

    cache_status: hit=有数据文件, negative=有失败记录, miss=什么都没有
    status: fresh=未过期, stale=已过期（数据仍可用作兜底）
    """

    cache_status: str = 'miss'
    status: str = 'stale'
    file_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def get_cache_data_path(parent: str, path: str) -> Path:
    return Path(get_cache_path(parent, path))


def get_cache_meta_path(parent: str, path: str) -> str:
    return f'{get_cache_path(parent, path)}.meta.json'


def _read_cache_metadata(parent: str, path: str) -> Dict[str, Any]:
    meta_file_path = get_cache_meta_path(parent, path)
    if not os.path.exists(meta_file_path):
        return {}
    try:
        with open(meta_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _write_cache_metadata(parent: str, path: str, metadata: Dict[str, Any]) -> None:
    # 元数据同样会被并发覆盖，走原子写避免读到半截 JSON。
    # 半截 JSON 会被 _read_cache_metadata 当成空元数据，
    # 进而让一张好图退化成"过期"状态被反复重抓。
    payload = json.dumps(metadata, ensure_ascii=False).encode('utf-8')
    _write_bytes_atomic(get_cache_meta_path(parent, path), payload)


def get_cache_lookup(parent: str, path: str) -> CacheLookup:
    """查询缓存状态。数据文件存在但没有元数据时视为过期命中，可用作兜底。"""
    data_path = get_cache_data_path(parent, path)
    metadata = _read_cache_metadata(parent, path)
    now = time.time()
    is_fresh = now <= float(metadata.get('expire_at') or 0)

    if metadata.get('error_code') and not data_path.exists():
        return CacheLookup(
            cache_status='negative',
            status='fresh' if is_fresh else 'stale',
            file_path=None,
            metadata=metadata,
        )

    if data_path.exists():
        return CacheLookup(
            cache_status='hit',
            status='fresh' if is_fresh else 'stale',
            file_path=data_path,
            metadata=metadata,
        )

    return CacheLookup()


def write_success_cache(
    parent: str,
    path: str,
    content: bytes,
    content_type: Optional[str],
    ttl: int = DEFAULT_CACHE_TTL_SECONDS,
) -> Dict[str, Any]:
    """写入数据文件与元数据，返回新元数据。"""
    cache_file(parent, path, content)
    metadata = {
        'content_type': content_type or 'application/octet-stream',
        'content_hash': hashlib.sha256(content).hexdigest(),
        'size': len(content),
        'cached_at': time.time(),
        'expire_at': time.time() + ttl,
    }
    _write_cache_metadata(parent, path, metadata)
    return metadata


def write_negative_cache(parent: str, path: str, status_code: Optional[int], ttl: int) -> None:
    """记录一次抓取失败，避免短时间内反复请求同一个失效地址。"""
    data_path = get_cache_data_path(parent, path)
    if data_path.exists():
        # 仍有可用副本时不写负缓存，交给 stale 兜底逻辑
        return
    _write_cache_metadata(
        parent,
        path,
        {
            'error_code': int(status_code or 502),
            'cached_at': time.time(),
            'expire_at': time.time() + ttl,
        },
    )


def extend_cache_expiry(parent: str, path: str, ttl: int) -> None:
    """上游暂时不可用时，延长既有副本的可用期限。"""
    metadata = _read_cache_metadata(parent, path)
    if not metadata:
        metadata = {'content_type': 'application/octet-stream', 'cached_at': time.time()}
    metadata['expire_at'] = time.time() + ttl
    metadata.pop('error_code', None)
    _write_cache_metadata(parent, path, metadata)


def build_cache_etag(parent: str, path: str, metadata: Dict[str, Any]) -> str:
    """基于内容摘要生成 ETag；缺少摘要时回落到路径+时间戳。"""
    content_hash = metadata.get('content_hash')
    if not content_hash:
        seed = f'{parent}:{path}:{metadata.get("cached_at", "")}:{metadata.get("size", "")}'
        content_hash = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    return f'"{content_hash}"'


def get_negative_ttl_seconds(status_code: Optional[int]) -> int:
    """404/410 这类确定性错误缓存久一些，其余按瞬时故障处理。"""
    if status_code in (404, 410):
        return NEGATIVE_TTL_NOT_FOUND_SECONDS
    return NEGATIVE_TTL_TRANSIENT_SECONDS


def get_stale_fallback_ttl_seconds() -> int:
    return STALE_FALLBACK_TTL_SECONDS


def cleanup_expired_cache(parents: Optional[List[str]] = None) -> Dict[str, int]:
    """清理过期的元数据、负缓存与孤儿数据文件。"""
    result = {'removed_metadata': 0, 'removed_data': 0, 'removed_dirs': 0}
    if not os.path.exists(cache_path):
        return result

    target_parents = parents or [
        name for name in os.listdir(cache_path)
        if os.path.isdir(os.path.join(cache_path, name))
    ]
    now = time.time()

    for parent in target_parents:
        folder = os.path.join(cache_path, parent)
        if not os.path.isdir(folder):
            continue

        for name in os.listdir(folder):
            if not name.endswith('.meta.json'):
                continue

            meta_file_path = os.path.join(folder, name)
            data_file_path = meta_file_path[: -len('.meta.json')]
            try:
                with open(meta_file_path, 'r', encoding='utf-8') as file:
                    metadata = json.load(file)
            except (json.JSONDecodeError, OSError):
                metadata = {}

            expire_at = float(metadata.get('expire_at') or 0)
            if now <= expire_at:
                continue

            # 过期的负缓存直接删掉，让下次请求重新尝试
            if metadata.get('error_code'):
                os.remove(meta_file_path)
                result['removed_metadata'] += 1
                continue

            # 过期但仍有数据文件的保留，作为上游故障时的兜底副本
            if not os.path.exists(data_file_path):
                os.remove(meta_file_path)
                result['removed_metadata'] += 1

        # 清理没有对应数据文件的空目录
        if not os.listdir(folder):
            os.rmdir(folder)
            result['removed_dirs'] += 1

    return result


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
