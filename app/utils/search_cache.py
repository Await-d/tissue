"""
搜索缓存机制
提供多层次的搜索结果缓存，提升搜索性能
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import pickle
import gzip

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.db.models import SearchCache
from app.utils.logger import logger
from app.utils.cache import get_cache_json, cache_json, clean_cache_json


@dataclass
class CacheConfig:
    """缓存配置"""
    # 内存缓存
    memory_cache_size: int = 1000  # 内存缓存最大条数
    memory_cache_ttl: int = 300    # 内存缓存TTL(秒)

    # 数据库缓存
    db_cache_ttl: int = 3600       # 数据库缓存TTL(秒)
    db_cache_max_size: int = 10000 # 数据库缓存最大条数

    # 文件缓存
    file_cache_enabled: bool = True
    file_cache_ttl: int = 86400    # 文件缓存TTL(秒)
    file_cache_compress: bool = True

    # 清理策略
    auto_cleanup_enabled: bool = True
    cleanup_interval: int = 3600   # 清理间隔(秒)
    max_cache_age: int = 604800    # 最大缓存时间(秒)


class SearchCacheManager:
    """搜索缓存管理器"""

    def __init__(self, db: Session, config: CacheConfig = None):
        self.db = db
        self.config = config or CacheConfig()
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._last_cleanup = datetime.now()

    def generate_cache_key(self,
                          query: str,
                          search_type: str = "all",
                          sources: List[str] = None,
                          filters: Dict[str, Any] = None,
                          page: int = 1,
                          page_size: int = 20) -> str:
        """生成缓存键"""
        # 标准化参数
        sources = sources or ["local"]
        filters = filters or {}

        # 创建缓存键组件
        key_data = {
            "query": query.lower().strip(),
            "search_type": search_type,
            "sources": sorted(sources),
            "filters": sorted(filters.items()) if filters else [],
            "page": page,
            "page_size": page_size
        }

        # 生成MD5哈希
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        cache_key = hashlib.md5(key_str.encode('utf-8')).hexdigest()

        return f"search_{cache_key}"

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存"""
        try:
            # 1. 先检查内存缓存
            memory_result = self._get_from_memory(cache_key)
            if memory_result:
                logger.debug(f"搜索缓存命中[内存]: {cache_key}")
                return memory_result

            # 2. 检查文件缓存
            if self.config.file_cache_enabled:
                file_result = self._get_from_file_cache(cache_key)
                if file_result:
                    logger.debug(f"搜索缓存命中[文件]: {cache_key}")
                    # 回写到内存缓存
                    self._set_to_memory(cache_key, file_result)
                    return file_result

            # 3. 检查数据库缓存
            db_result = self._get_from_database(cache_key)
            if db_result:
                logger.debug(f"搜索缓存命中[数据库]: {cache_key}")
                # 回写到内存和文件缓存
                self._set_to_memory(cache_key, db_result)
                if self.config.file_cache_enabled:
                    self._set_to_file_cache(cache_key, db_result)
                return db_result

            logger.debug(f"搜索缓存未命中: {cache_key}")
            return None

        except Exception as e:
            logger.warning(f"获取搜索缓存失败: {e}")
            return None

    def set(self,
            cache_key: str,
            data: Dict[str, Any],
            ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            # 设置到所有缓存层
            success = True

            # 1. 内存缓存
            self._set_to_memory(cache_key, data, ttl or self.config.memory_cache_ttl)

            # 2. 文件缓存
            if self.config.file_cache_enabled:
                if not self._set_to_file_cache(cache_key, data, ttl or self.config.file_cache_ttl):
                    success = False

            # 3. 数据库缓存
            if not self._set_to_database(cache_key, data, ttl or self.config.db_cache_ttl):
                success = False

            if success:
                logger.debug(f"搜索缓存设置成功: {cache_key}")
            else:
                logger.warning(f"搜索缓存部分设置失败: {cache_key}")

            return success

        except Exception as e:
            logger.error(f"设置搜索缓存失败: {e}")
            return False

    def delete(self, cache_key: str) -> bool:
        """删除缓存"""
        try:
            success = True

            # 删除内存缓存
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]

            # 删除文件缓存
            if self.config.file_cache_enabled:
                clean_cache_json('search_file', cache_key)

            # 删除数据库缓存
            cache_record = self.db.query(SearchCache).filter(
                SearchCache.cache_key == cache_key
            ).first()
            if cache_record:
                self.db.delete(cache_record)
                self.db.commit()

            logger.debug(f"搜索缓存删除成功: {cache_key}")
            return success

        except Exception as e:
            logger.error(f"删除搜索缓存失败: {e}")
            return False

    def clear_all(self) -> bool:
        """清除所有缓存"""
        try:
            # 清除内存缓存
            self._memory_cache.clear()

            # 清除文件缓存
            if self.config.file_cache_enabled:
                clean_cache_json('search_file', '')

            # 清除数据库缓存
            self.db.query(SearchCache).delete()
            self.db.commit()

            logger.info("所有搜索缓存已清除")
            return True

        except Exception as e:
            logger.error(f"清除搜索缓存失败: {e}")
            return False

    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        if not self.config.auto_cleanup_enabled:
            return 0

        now = datetime.now()
        if (now - self._last_cleanup).seconds < self.config.cleanup_interval:
            return 0

        try:
            cleanup_count = 0

            # 清理内存缓存
            expired_keys = []
            for key, data in self._memory_cache.items():
                if now > data.get('expires_at', now):
                    expired_keys.append(key)

            for key in expired_keys:
                del self._memory_cache[key]
                cleanup_count += 1

            # 清理数据库缓存
            expired_db_count = self.db.query(SearchCache).filter(
                SearchCache.expires_at < now
            ).count()

            self.db.query(SearchCache).filter(
                SearchCache.expires_at < now
            ).delete()

            cleanup_count += expired_db_count

            # 限制数据库缓存大小
            if self.config.db_cache_max_size > 0:
                total_count = self.db.query(func.count(SearchCache.id)).scalar()
                if total_count > self.config.db_cache_max_size:
                    # 删除最旧的记录
                    oldest_records = self.db.query(SearchCache).order_by(
                        SearchCache.created_at
                    ).limit(total_count - self.config.db_cache_max_size).all()

                    for record in oldest_records:
                        self.db.delete(record)
                        cleanup_count += 1

            self.db.commit()
            self._last_cleanup = now

            if cleanup_count > 0:
                logger.info(f"清理过期搜索缓存: {cleanup_count} 条")

            return cleanup_count

        except Exception as e:
            logger.error(f"清理搜索缓存失败: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            # 内存缓存统计
            memory_count = len(self._memory_cache)

            # 数据库缓存统计
            db_count = self.db.query(func.count(SearchCache.id)).scalar() or 0
            db_active_count = self.db.query(func.count(SearchCache.id)).filter(
                SearchCache.expires_at > datetime.now()
            ).scalar() or 0

            # 计算命中率（这里需要额外的统计数据）
            total_hits = self.db.query(func.sum(SearchCache.hit_count)).scalar() or 0

            return {
                "memory_cache_count": memory_count,
                "db_cache_count": db_count,
                "db_active_cache_count": db_active_count,
                "total_cache_hits": total_hits,
                "cache_hit_rate": 0.0,  # 需要额外统计
                "last_cleanup": self._last_cleanup.isoformat()
            }

        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {}

    def _get_from_memory(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从内存缓存获取"""
        if cache_key not in self._memory_cache:
            return None

        cache_data = self._memory_cache[cache_key]
        if datetime.now() > cache_data.get('expires_at', datetime.now()):
            del self._memory_cache[cache_key]
            return None

        return cache_data.get('data')

    def _set_to_memory(self,
                      cache_key: str,
                      data: Dict[str, Any],
                      ttl: int = None) -> bool:
        """设置到内存缓存"""
        try:
            if len(self._memory_cache) >= self.config.memory_cache_size:
                # 删除最旧的缓存
                oldest_key = min(self._memory_cache.keys(),
                               key=lambda k: self._memory_cache[k].get('created_at', datetime.now()))
                del self._memory_cache[oldest_key]

            expires_at = datetime.now() + timedelta(seconds=ttl or self.config.memory_cache_ttl)

            self._memory_cache[cache_key] = {
                'data': data,
                'created_at': datetime.now(),
                'expires_at': expires_at
            }

            return True

        except Exception as e:
            logger.warning(f"设置内存缓存失败: {e}")
            return False

    def _get_from_file_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从文件缓存获取"""
        try:
            cache_data = get_cache_json('search_file', cache_key)
            if cache_data and isinstance(cache_data, dict):
                expires_at_str = cache_data.get('expires_at')
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if datetime.now() > expires_at:
                        clean_cache_json('search_file', cache_key)
                        return None

                return cache_data.get('data')

            return None

        except Exception as e:
            logger.warning(f"从文件缓存获取失败: {e}")
            return None

    def _set_to_file_cache(self,
                          cache_key: str,
                          data: Dict[str, Any],
                          ttl: int = None) -> bool:
        """设置到文件缓存"""
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.config.file_cache_ttl)

            cache_data = {
                'data': data,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }

            cache_json('search_file', cache_key, cache_data, expire_time=ttl or self.config.file_cache_ttl)
            return True

        except Exception as e:
            logger.warning(f"设置文件缓存失败: {e}")
            return False

    def _get_from_database(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从数据库缓存获取"""
        try:
            cache_record = self.db.query(SearchCache).filter(
                and_(
                    SearchCache.cache_key == cache_key,
                    SearchCache.expires_at > datetime.now()
                )
            ).first()

            if cache_record:
                # 更新命中次数
                cache_record.hit_count += 1
                self.db.commit()

                # 解析缓存数据
                result_data = json.loads(cache_record.result_data)
                return result_data

            return None

        except Exception as e:
            logger.warning(f"从数据库缓存获取失败: {e}")
            return None

    def _set_to_database(self,
                        cache_key: str,
                        data: Dict[str, Any],
                        ttl: int = None) -> bool:
        """设置到数据库缓存"""
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.config.db_cache_ttl)

            # 检查是否已存在
            existing_cache = self.db.query(SearchCache).filter(
                SearchCache.cache_key == cache_key
            ).first()

            if existing_cache:
                # 更新现有缓存
                existing_cache.result_data = json.dumps(data, ensure_ascii=False)
                existing_cache.result_count = data.get('total', 0)
                existing_cache.expires_at = expires_at
                existing_cache.updated_at = datetime.now()
            else:
                # 创建新缓存
                cache_record = SearchCache(
                    cache_key=cache_key,
                    query=data.get('query', ''),
                    search_type=data.get('search_type', 'all'),
                    result_data=json.dumps(data, ensure_ascii=False),
                    result_count=data.get('total', 0),
                    expires_at=expires_at
                )
                self.db.add(cache_record)

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"设置数据库缓存失败: {e}")
            return False


# 全局缓存实例
_cache_manager: Optional[SearchCacheManager] = None


def get_search_cache_manager(db: Session) -> SearchCacheManager:
    """获取搜索缓存管理器"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = SearchCacheManager(db)
    return _cache_manager


def search_cache_decorator(cache_key_func=None, ttl: int = 3600):
    """搜索缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取数据库会话
            db = kwargs.get('db') or args[0].db if args else None
            if not db:
                return func(*args, **kwargs)

            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"

            # 获取缓存管理器
            cache_manager = get_search_cache_manager(db)

            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return cached_result

            # 执行原函数
            result = func(*args, **kwargs)

            # 缓存结果
            if result:
                cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator