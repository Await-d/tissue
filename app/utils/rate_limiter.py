"""
Author: Await
Date: 2026-01-11
Description: 速率限制工具 - 基于内存的简单实现

提供线程安全的速率限制功能，用于限制 API 请求频率。
使用滑动窗口算法跟踪请求时间戳。
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Deque, Optional
from functools import wraps

from fastapi import Request, HTTPException, status


class RateLimiter:
    """
    基于内存的速率限制器

    使用滑动窗口算法，为每个 IP 地址维护一个请求时间戳队列。
    线程安全实现，支持并发访问。

    Attributes:
        max_requests: 时间窗口内允许的最大请求数
        window_seconds: 时间窗口大小（秒）
        _requests: 存储每个 IP 的请求时间戳队列
        _lock: 线程锁，确保并发安全
    """

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        """
        初始化速率限制器

        Args:
            max_requests: 时间窗口内允许的最大请求数，默认 30
            window_seconds: 时间窗口大小（秒），默认 60
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # 使用 defaultdict 自动创建新 IP 的队列
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)
        # 使用 RLock 支持重入锁
        self._lock = threading.RLock()

        # 用于定期清理的计数器
        self._cleanup_counter = 0
        self._cleanup_threshold = 1000  # 每 1000 次请求执行一次清理

    def is_allowed(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        检查指定客户端是否允许发送请求

        Args:
            client_id: 客户端标识（通常是 IP 地址）

        Returns:
            tuple[bool, Optional[int]]: (是否允许, 剩余秒数)
                - 允许时返回 (True, None)
                - 拒绝时返回 (False, 需要等待的秒数)
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        with self._lock:
            # 获取该客户端的请求队列
            request_queue = self._requests[client_id]

            # 移除时间窗口外的旧请求
            while request_queue and request_queue[0] < cutoff_time:
                request_queue.popleft()

            # 检查是否超过限制
            if len(request_queue) >= self.max_requests:
                # 计算需要等待的时间（最早请求过期的时间）
                oldest_request = request_queue[0]
                retry_after = int(oldest_request + self.window_seconds - current_time) + 1
                return False, retry_after

            # 记录当前请求
            request_queue.append(current_time)

            # 定期清理空闲的客户端记录
            self._cleanup_counter += 1
            if self._cleanup_counter >= self._cleanup_threshold:
                self._cleanup_idle_clients(cutoff_time)
                self._cleanup_counter = 0

            return True, None

    def _cleanup_idle_clients(self, cutoff_time: float) -> None:
        """
        清理空闲的客户端记录（时间窗口外无请求的客户端）

        Args:
            cutoff_time: 截止时间，早于此时间的请求将被清理
        """
        clients_to_remove = []

        for client_id, request_queue in self._requests.items():
            # 清理该客户端的过期请求
            while request_queue and request_queue[0] < cutoff_time:
                request_queue.popleft()

            # 如果队列为空，标记为待删除
            if not request_queue:
                clients_to_remove.append(client_id)

        # 删除空闲客户端
        for client_id in clients_to_remove:
            del self._requests[client_id]

    def reset(self, client_id: Optional[str] = None) -> None:
        """
        重置速率限制记录

        Args:
            client_id: 要重置的客户端标识，为 None 时重置所有记录
        """
        with self._lock:
            if client_id:
                if client_id in self._requests:
                    del self._requests[client_id]
            else:
                self._requests.clear()

    def get_stats(self, client_id: str) -> Dict[str, int]:
        """
        获取指定客户端的统计信息

        Args:
            client_id: 客户端标识

        Returns:
            Dict[str, int]: 包含以下键的字典：
                - current_requests: 当前时间窗口内的请求数
                - remaining_requests: 剩余可用请求数
                - max_requests: 最大允许请求数
                - window_seconds: 时间窗口大小（秒）
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        with self._lock:
            request_queue = self._requests[client_id]

            # 清理过期请求
            while request_queue and request_queue[0] < cutoff_time:
                request_queue.popleft()

            current_requests = len(request_queue)
            remaining = max(0, self.max_requests - current_requests)

            return {
                "current_requests": current_requests,
                "remaining_requests": remaining,
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds
            }


# 全局速率限制器实例
# 默认配置：每个 IP 每分钟最多 30 次请求
_default_limiter = RateLimiter(max_requests=30, window_seconds=60)


def get_client_ip(request: Request) -> str:
    """
    从请求中获取客户端 IP 地址

    优先从 X-Forwarded-For 头获取，其次从 X-Real-IP，最后从直连 IP。

    Args:
        request: FastAPI 请求对象

    Returns:
        str: 客户端 IP 地址
    """
    # 尝试从代理头获取真实 IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For 可能包含多个 IP，取第一个
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 获取直连 IP
    if request.client:
        return request.client.host

    return "unknown"


def rate_limit(
    max_requests: int = 30,
    window_seconds: int = 60,
    limiter: Optional[RateLimiter] = None
):
    """
    速率限制装饰器

    用于限制 API 端点的请求频率。超过限制时返回 429 错误。

    Args:
        max_requests: 时间窗口内允许的最大请求数
        window_seconds: 时间窗口大小（秒）
        limiter: 自定义速率限制器实例，为 None 时使用默认实例

    Returns:
        装饰器函数

    Example:
        @router.get("/api/example")
        @rate_limit(max_requests=30, window_seconds=60)
        async def example_endpoint(request: Request):
            return {"message": "success"}
    """
    # 使用提供的限制器或默认限制器
    rate_limiter = limiter or _default_limiter

    # 如果使用默认限制器但指定了不同的参数，创建新的限制器
    if limiter is None and (
        max_requests != _default_limiter.max_requests or
        window_seconds != _default_limiter.window_seconds
    ):
        rate_limiter = RateLimiter(max_requests, window_seconds)

    def decorator(func):
        @wraps(func)
        async def async_wrapper(request: Request, *args, **kwargs):
            # 获取客户端 IP
            client_ip = get_client_ip(request)

            # 检查是否允许请求
            allowed, retry_after = rate_limiter.is_allowed(client_ip)

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "请求过于频繁，请稍后再试",
                        "message": f"您已超过速率限制（{max_requests} 次请求 / {window_seconds} 秒）",
                        "retry_after": retry_after,
                        "client_ip": client_ip
                    },
                    headers={"Retry-After": str(retry_after)}
                )

            # 执行原函数
            return await func(request=request, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(request: Request, *args, **kwargs):
            # 获取客户端 IP
            client_ip = get_client_ip(request)

            # 检查是否允许请求
            allowed, retry_after = rate_limiter.is_allowed(client_ip)

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "请求过于频繁，请稍后再试",
                        "message": f"您已超过速率限制（{max_requests} 次请求 / {window_seconds} 秒）",
                        "retry_after": retry_after,
                        "client_ip": client_ip
                    },
                    headers={"Retry-After": str(retry_after)}
                )

            # 执行原函数
            return func(request=request, *args, **kwargs)

        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def get_default_limiter() -> RateLimiter:
    """
    获取默认的速率限制器实例

    Returns:
        RateLimiter: 默认速率限制器
    """
    return _default_limiter
