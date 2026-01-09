"""
性能监控API - 提供并发刮削性能数据
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schema.setting import Setting
from app.utils.logger import logger

router = APIRouter(prefix="/performance", tags=["性能监控"])

# 全局性能统计
performance_stats = {
    "concurrent_requests": 0,
    "total_requests": 0,
    "average_time": 0.0,
    "success_rate": 0.0,
    "last_reset": time.time()
}


@router.get("/stats")
async def get_performance_stats():
    """获取并发刮削性能统计"""
    setting = Setting()

    return {
        "status": "ok",
        "data": {
            **performance_stats,
            "config": {
                "concurrent_enabled": setting.app.concurrent_scraping,
                "max_concurrent": setting.app.max_concurrent_spiders,
            },
            "uptime": time.time() - performance_stats["last_reset"]
        }
    }


@router.post("/reset")
async def reset_performance_stats():
    """重置性能统计"""
    global performance_stats
    performance_stats = {
        "concurrent_requests": 0,
        "total_requests": 0,
        "average_time": 0.0,
        "success_rate": 0.0,
        "last_reset": time.time()
    }

    logger.info("性能统计已重置")
    return {"status": "ok", "message": "性能统计已重置"}


def record_scraping_performance(execution_time: float, success: bool, concurrent: bool = True):
    """记录刮削性能数据"""
    global performance_stats

    performance_stats["total_requests"] += 1
    if concurrent:
        performance_stats["concurrent_requests"] += 1

    # 更新平均时间（简单的移动平均）
    current_avg = performance_stats["average_time"]
    total = performance_stats["total_requests"]
    performance_stats["average_time"] = (current_avg * (total - 1) + execution_time) / total

    # 更新成功率
    if success:
        current_success_count = performance_stats["success_rate"] * (total - 1)
        performance_stats["success_rate"] = (current_success_count + 1) / total
    else:
        current_success_count = performance_stats["success_rate"] * (total - 1)
        performance_stats["success_rate"] = current_success_count / total


@router.get("/test")
async def test_concurrent_scraping():
    """测试并发刮削性能"""
    from app.service.spider import get_video_info_async

    test_number = "SSIS-001"
    start_time = time.time()

    try:
        result = await get_video_info_async(test_number)
        execution_time = time.time() - start_time
        success = result is not None

        record_scraping_performance(execution_time, success, concurrent=True)

        return {
            "status": "ok",
            "data": {
                "test_number": test_number,
                "execution_time": execution_time,
                "success": success,
                "result_summary": {
                    "title": result.title if result else None,
                    "downloads_count": len(result.downloads or []) if result else 0,
                    "actors_count": len(result.actors or []) if result else 0,
                } if result else None
            }
        }
    except Exception as e:
        execution_time = time.time() - start_time
        record_scraping_performance(execution_time, False, concurrent=True)

        logger.error(f"并发刮削测试失败: {str(e)}")
        return {
            "status": "error",
            "message": f"测试失败: {str(e)}",
            "data": {
                "test_number": test_number,
                "execution_time": execution_time,
                "success": False
            }
        }