"""
并发刮削服务 - 基于Agent-1分析报告的技术方案
提供3-4倍性能提升的异步并发刮削能力
"""
import asyncio
import time
from typing import List, Optional
from starlette.concurrency import run_in_threadpool

from app.utils.spider import get_spiders
from app.utils.logger import logger
from app.schema.video import VideoDetail


class SpiderService:
    """并发刮削服务"""

    def __init__(self, max_concurrent: Optional[int] = None):
        # 从配置中读取并发数，如果未提供则使用配置默认值
        if max_concurrent is None:
            from app.schema.setting import Setting
            setting = Setting()
            max_concurrent = setting.app.max_concurrent_spiders

        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    def _get_spiders(self):
        """获取所有可用的爬虫"""
        return get_spiders()

    async def _get_video_by_spider_async(self, spider, number: str,
                                       include_downloads: bool = True,
                                       include_previews: bool = True,
                                       include_comments: bool = True):
        """异步版本的单个爬虫刮削"""
        async with self.semaphore:  # 控制并发数
            def __get_video_by_spider():
                try:
                    start_time = time.time()
                    result = spider.get_info(number,
                                           include_downloads=include_downloads,
                                           include_previews=include_previews,
                                           include_comments=include_comments)
                    execution_time = time.time() - start_time
                    logger.info(f"{spider.name} 刮削完成，耗时: {execution_time:.2f}秒")
                    return result
                except Exception as e:
                    logger.error(f"{spider.name} 刮削失败: {str(e)}")
                    return None

            return await run_in_threadpool(__get_video_by_spider)

    async def get_video_info_async(self, number: str,
                                 include_downloads: bool = True,
                                 include_previews: bool = True,
                                 include_comments: bool = True) -> Optional[VideoDetail]:
        """异步版本的视频信息获取"""
        logger.info(f"开始并发刮削番号: {number}")
        start_time = time.time()

        spiders = self._get_spiders()
        logger.info(f"准备使用 {len(spiders)} 个爬虫进行并发刮削")

        # 创建并发任务
        tasks = [
            self._get_video_by_spider_async(
                spider, number, include_downloads, include_previews, include_comments
            )
            for spider in spiders
        ]

        # 并发执行所有爬虫任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤成功的结果
        valid_results = []
        for i, result in enumerate(results):
            if result is not None and not isinstance(result, Exception):
                valid_results.append(result)
                logger.info(f"爬虫 {spiders[i].name} 成功获取数据")
            elif isinstance(result, Exception):
                logger.error(f"爬虫 {spiders[i].name} 执行异常: {str(result)}")
            else:
                logger.warning(f"爬虫 {spiders[i].name} 未获取到数据")

        total_time = time.time() - start_time
        logger.info(f"并发刮削完成，总耗时: {total_time:.2f}秒，成功: {len(valid_results)}/{len(spiders)}")

        if not valid_results:
            logger.error(f"所有爬虫都未能获取到番号 {number} 的信息")
            return None

        # 合并多个数据源的信息（使用现有的合并逻辑）
        merged_result = self._merge_video_info(valid_results)
        logger.info(f"数据合并完成，最终结果包含 {len(merged_result.downloads or [])} 个下载链接")

        return merged_result

    def _merge_video_info(self, video_infos: List[VideoDetail]) -> VideoDetail:
        """合并多个数据源的视频信息"""
        if not video_infos:
            return None

        # 使用第一个结果作为基础
        merged = video_infos[0]

        # 合并其他数据源的信息
        for video_info in video_infos[1:]:
            # 字段补全：优先使用非空字段
            for field_name in video_info.__dict__:
                if hasattr(merged, field_name):
                    current_value = getattr(merged, field_name)
                    new_value = getattr(video_info, field_name)

                    # 如果当前字段为空且新值非空，则使用新值
                    if not current_value and new_value:
                        setattr(merged, field_name, new_value)
                    # 特殊处理列表字段（如downloads, actors等）
                    elif isinstance(current_value, list) and isinstance(new_value, list):
                        # 合并列表，去重
                        combined = current_value + [item for item in new_value if item not in current_value]
                        setattr(merged, field_name, combined)

        return merged


# 全局服务实例
spider_service = SpiderService()


async def get_video_info_async(number: str,
                             include_downloads: bool = True,
                             include_previews: bool = True,
                             include_comments: bool = True) -> Optional[VideoDetail]:
    """异步版本的视频信息获取 - 公共接口"""
    return await spider_service.get_video_info_async(
        number, include_downloads, include_previews, include_comments
    )


def get_video_info_sync(number: str,
                       include_downloads: bool = True,
                       include_previews: bool = True,
                       include_comments: bool = True) -> Optional[VideoDetail]:
    """同步版本的视频信息获取 - 保持向后兼容"""
    try:
        # 尝试获取当前事件循环
        loop = asyncio.get_running_loop()
        # 如果在异步环境中，创建新的线程来运行
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                get_video_info_async(number, include_downloads, include_previews, include_comments)
            )
            return future.result()
    except RuntimeError:
        # 如果没有运行的事件循环，直接创建新的
        return asyncio.run(
            get_video_info_async(number, include_downloads, include_previews, include_comments)
        )


# 配置开关：允许在配置中控制是否启用并发模式
def get_video_info_with_config(number: str,
                              include_downloads: bool = True,
                              include_previews: bool = True,
                              include_comments: bool = True) -> Optional[VideoDetail]:
    """带配置开关的视频信息获取"""
    from app.schema.setting import Setting
    setting = Setting()

    # 检查是否启用并发刮削（假设添加了配置项）
    concurrent_enabled = getattr(setting.app, 'concurrent_scraping', True)

    if concurrent_enabled:
        logger.info("使用并发刮削模式")
        return get_video_info_sync(number, include_downloads, include_previews, include_comments)
    else:
        logger.info("使用传统串行刮削模式")
        # 回退到原有的同步方法
        from app.utils.spider import get_video_info as original_get_video_info
        return original_get_video_info(number)