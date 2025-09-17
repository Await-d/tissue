"""
搜索功能API路由
提供统一的搜索接口，支持多数据源、搜索历史、搜索建议等功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse

from app.dependencies.security import verify_token
from app.service.search import SearchService, get_search_service
from app.schema.r import R
from app.schema.search import (
    SearchRequest, SearchResponse, QuickSearchRequest, QuickSearchResponse,
    SearchSuggestionRequest, SearchSuggestionResponse,
    SearchHistoryRequest, SearchHistoryResponse,
    HotSearchResponse, SearchStatisticsResponse
)
from app.utils.logger import logger

router = APIRouter()


@router.post('/unified', dependencies=[Depends(verify_token)])
def unified_search(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service)
) -> R[SearchResponse]:
    """
    统一搜索接口
    支持本地和网络多数据源搜索
    """
    try:
        # 构建过滤条件
        filters = {}
        if request.is_hd is not None:
            filters['is_hd'] = request.is_hd
        if request.is_zh is not None:
            filters['is_zh'] = request.is_zh
        if request.is_uncensored is not None:
            filters['is_uncensored'] = request.is_uncensored
        if request.date_from:
            filters['date_from'] = request.date_from
        if request.date_to:
            filters['date_to'] = request.date_to
        if request.min_rating is not None:
            filters['min_rating'] = request.min_rating
        if request.max_rating is not None:
            filters['max_rating'] = request.max_rating

        # 执行搜索
        result = search_service.unified_search(
            query=request.query,
            search_type=request.search_type,
            sources=request.sources,
            filters=filters,
            page=request.page,
            page_size=request.page_size
        )

        response = SearchResponse(**result)
        return R.ok(response)

    except Exception as e:
        logger.error(f"统一搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post('/quick', dependencies=[Depends(verify_token)])
def quick_search(
    request: QuickSearchRequest,
    search_service: SearchService = Depends(get_search_service)
) -> R[QuickSearchResponse]:
    """
    快速搜索接口（仅本地搜索）
    用于搜索建议和自动补全
    """
    try:
        # 仅进行本地搜索
        result = search_service.unified_search(
            query=request.query,
            search_type=request.search_type,
            sources=["local"],
            filters={},
            page=1,
            page_size=request.limit
        )

        # 合并本地结果
        quick_results = []
        quick_results.extend(result["results"]["local_videos"])
        quick_results.extend(result["results"]["local_actors"])

        response = QuickSearchResponse(
            query=request.query,
            results=quick_results[:request.limit],
            search_time=result["search_time"]
        )
        return R.ok(response)

    except Exception as e:
        logger.error(f"快速搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"快速搜索失败: {str(e)}")


@router.get('/suggestions', dependencies=[Depends(verify_token)])
def get_search_suggestions(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(default=10, description="建议数量"),
    search_service: SearchService = Depends(get_search_service)
) -> R[List[str]]:
    """
    获取搜索建议
    """
    try:
        suggestions = search_service._get_search_suggestions(query)
        return R.list(suggestions[:limit])

    except Exception as e:
        logger.error(f"获取搜索建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取搜索建议失败: {str(e)}")


@router.get('/history', dependencies=[Depends(verify_token)])
def get_search_history(
    limit: int = Query(default=50, description="历史记录数量"),
    search_type: Optional[str] = Query(default=None, description="搜索类型过滤"),
    search_service: SearchService = Depends(get_search_service)
) -> R[List[dict]]:
    """
    获取搜索历史
    """
    try:
        histories = search_service.get_search_history(limit)
        return R.list(histories)

    except Exception as e:
        logger.error(f"获取搜索历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取搜索历史失败: {str(e)}")


@router.delete('/history', dependencies=[Depends(verify_token)])
def clear_search_history(
    search_service: SearchService = Depends(get_search_service)
) -> R[None]:
    """
    清除搜索历史
    """
    try:
        search_service.clear_search_history()
        return R.ok()

    except Exception as e:
        logger.error(f"清除搜索历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除搜索历史失败: {str(e)}")


@router.get('/hot')  # 无需token验证
def get_hot_searches(
    limit: int = Query(default=10, description="热门搜索数量"),
    search_service: SearchService = Depends(get_search_service)
) -> R[List[dict]]:
    """
    获取热门搜索
    """
    try:
        hot_searches = search_service.get_hot_searches(limit)
        return R.list(hot_searches)

    except Exception as e:
        logger.error(f"获取热门搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取热门搜索失败: {str(e)}")


@router.get('/statistics', dependencies=[Depends(verify_token)])
def get_search_statistics(
    search_service: SearchService = Depends(get_search_service)
) -> R[dict]:
    """
    获取搜索统计信息
    """
    try:
        statistics = search_service.get_search_statistics()
        return R.ok(statistics)

    except Exception as e:
        logger.error(f"获取搜索统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取搜索统计失败: {str(e)}")


# 兼容性接口：保持与现有前端的兼容性
@router.get('/actor', dependencies=[Depends(verify_token)])
def search_actor_compat(
    actor_name: str = Query(..., description="演员名称"),
    force: Optional[bool] = Query(default=True, description="强制刷新"),
    search_service: SearchService = Depends(get_search_service)
) -> R[List[dict]]:
    """
    演员搜索兼容性接口
    保持与现有前端的兼容性
    """
    try:
        result = search_service.unified_search(
            query=actor_name,
            search_type="actor",
            sources=["local"],
            filters={},
            page=1,
            page_size=100
        )

        # 返回本地视频结果，保持兼容性
        videos = result["results"]["local_videos"]
        return R.list(videos)

    except Exception as e:
        logger.error(f"演员搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"演员搜索失败: {str(e)}")


@router.get('/video', dependencies=[Depends(verify_token)])
def search_video_compat(
    num: str = Query(..., description="番号"),
    search_service: SearchService = Depends(get_search_service)
) -> R[dict]:
    """
    视频搜索兼容性接口
    保持与现有前端的兼容性
    """
    try:
        result = search_service.unified_search(
            query=num,
            search_type="num",
            sources=["local", "javdb", "javbus"],
            filters={},
            page=1,
            page_size=1
        )

        # 优先返回本地结果，然后是网络结果
        all_videos = []
        all_videos.extend(result["results"]["local_videos"])
        all_videos.extend(result["results"]["web_videos"])

        if all_videos:
            return R.ok(all_videos[0])
        else:
            raise HTTPException(status_code=404, detail="未找到该视频")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"视频搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"视频搜索失败: {str(e)}")


# 缓存管理接口
@router.get('/cache/info', dependencies=[Depends(verify_token)])
def get_cache_info(
    search_service: SearchService = Depends(get_search_service)
) -> R[dict]:
    """
    获取搜索缓存信息
    """
    try:
        # TODO: 实现缓存信息获取
        cache_info = {
            "total_caches": 0,
            "active_caches": 0,
            "cache_hit_rate": 0.0,
            "caches": []
        }
        return R.ok(cache_info)

    except Exception as e:
        logger.error(f"获取缓存信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存信息失败: {str(e)}")


@router.delete('/cache', dependencies=[Depends(verify_token)])
def clear_search_cache(
    cache_type: Optional[str] = Query(default=None, description="缓存类型"),
    search_service: SearchService = Depends(get_search_service)
) -> R[None]:
    """
    清除搜索缓存
    """
    try:
        # TODO: 实现缓存清除
        logger.info(f"清除搜索缓存: {cache_type}")
        return R.ok()

    except Exception as e:
        logger.error(f"清除搜索缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除搜索缓存失败: {str(e)}")


# 演员相关搜索（扩展原有功能）
@router.get('/actors/all', dependencies=[Depends(verify_token)])
def get_all_actors_enhanced(
    force: Optional[bool] = Query(default=False, description="强制刷新"),
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=50, description="每页大小"),
    search_service: SearchService = Depends(get_search_service)
) -> R[dict]:
    """
    获取所有演员列表（增强版）
    支持分页和搜索功能
    """
    try:
        # 使用视频服务获取演员列表
        actors = search_service.video_service.get_all_actors()

        # 分页处理
        total = len(actors)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_actors = actors[start:end]

        # 转换为字典格式
        actor_dicts = [actor.model_dump() for actor in paginated_actors]

        result = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "actors": actor_dicts
        }

        return R.ok(result)

    except Exception as e:
        logger.error(f"获取演员列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取演员列表失败: {str(e)}")


@router.get('/actors/search', dependencies=[Depends(verify_token)])
def search_actors_enhanced(
    query: str = Query(..., description="演员名称"),
    source: str = Query(default="local", description="搜索源: local, web, all"),
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=20, description="每页大小"),
    search_service: SearchService = Depends(get_search_service)
) -> R[dict]:
    """
    演员搜索（增强版）
    支持本地和网络搜索
    """
    try:
        sources = []
        if source == "local":
            sources = ["local"]
        elif source == "web":
            sources = ["javdb", "javbus"]
        else:  # all
            sources = ["local", "javdb", "javbus"]

        result = search_service.unified_search(
            query=query,
            search_type="actor",
            sources=sources,
            filters={},
            page=page,
            page_size=page_size
        )

        return R.ok(result)

    except Exception as e:
        logger.error(f"演员搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"演员搜索失败: {str(e)}")