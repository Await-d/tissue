"""
自动下载API路由
"""
import asyncio
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app import schema
from app.dependencies.security import verify_token
from app.service.auto_download import get_auto_download_service, AutoDownloadService
from app.dependencies.auto_download import normalize_time_range_type
from app.db.models.auto_download import TimeRangeType


router = APIRouter(tags=["自动下载"], dependencies=[Depends(verify_token)])

# 任务状态存储（生产环境中应该使用Redis或数据库）
_task_status = {}


# 规则管理API
@router.get("/rules", response_model=schema.AutoDownloadListResponse, summary="获取自动下载规则列表")
async def get_rules(
    page: int = 1,
    page_size: int = 20,
    is_enabled: Optional[bool] = None,
    name: Optional[str] = None,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """获取自动下载规则列表"""
    try:
        query = schema.AutoDownloadRuleQuery(
            page=page,
            page_size=page_size,
            is_enabled=is_enabled,
            name=name
        )
        return service.get_rules(query)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/rules", response_model=schema.AutoDownloadResponse, summary="创建自动下载规则")
async def create_rule(
    rule_data: schema.AutoDownloadRuleCreate,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """创建自动下载规则"""
    try:
        # 确保time_range_type为大写
        if hasattr(rule_data, 'time_range_type') and rule_data.time_range_type and isinstance(rule_data.time_range_type, str):
            rule_data.time_range_type = rule_data.time_range_type.upper()
        
        rule = service.create_rule(rule_data)
        return schema.AutoDownloadResponse(
            success=True,
            message="规则创建成功",
            data={
                "id": rule.id,
                "name": rule.name
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/rules/{rule_id}", response_model=schema.AutoDownloadResponse, summary="更新自动下载规则")
async def update_rule(
    rule_id: int,
    rule_data: schema.AutoDownloadRuleUpdate,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """更新自动下载规则"""
    try:
        rule_data.id = rule_id
        
        # 确保time_range_type为大写
        if hasattr(rule_data, 'time_range_type') and rule_data.time_range_type and isinstance(rule_data.time_range_type, str):
            rule_data.time_range_type = rule_data.time_range_type.upper()
            
        rule = service.update_rule(rule_data)
        return schema.AutoDownloadResponse(
            success=True,
            message="规则更新成功",
            data={
                "id": rule.id,
                "name": rule.name
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/rules/{rule_id}", response_model=schema.AutoDownloadResponse, summary="删除自动下载规则")
async def delete_rule(
    rule_id: int,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """删除自动下载规则"""
    try:
        service.delete_rule(rule_id)
        return schema.AutoDownloadResponse(
            success=True,
            message="规则删除成功"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# 订阅记录管理API
@router.get("/subscriptions", response_model=schema.AutoDownloadListResponse, summary="获取自动下载订阅记录")
async def get_subscriptions(
    page: int = 1,
    page_size: int = 20,
    rule_id: Optional[int] = None,
    download_status: Optional[schema.DownloadStatus] = None,
    num: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """获取自动下载订阅记录"""
    try:
        from datetime import datetime
        
        # 转换日期参数
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        query = schema.AutoDownloadSubscriptionQuery(
            page=page,
            page_size=page_size,
            rule_id=rule_id,
            status=download_status,
            num=num,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        return service.get_subscriptions(query)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"日期格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/subscriptions/{subscription_id}", response_model=schema.AutoDownloadResponse, summary="删除订阅记录")
async def delete_subscription(
    subscription_id: int,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """删除订阅记录"""
    try:
        service.delete_subscription(subscription_id)
        return schema.AutoDownloadResponse(
            success=True,
            message="订阅记录删除成功"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/subscriptions/batch", response_model=schema.AutoDownloadResponse, summary="批量操作订阅记录")
async def batch_operation(
    operation: schema.AutoDownloadBatchOperation,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """批量操作订阅记录"""
    try:
        result = service.batch_operation(operation)
        return schema.AutoDownloadResponse(
            success=True,
            message=f"批量操作完成: 成功 {result['success_count']} 个，失败 {result['failed_count']} 个",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# 统计和管理API
@router.get("/statistics", response_model=schema.AutoDownloadStatistics, summary="获取统计信息")
async def get_statistics(
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """获取自动下载统计信息"""
    try:
        return service.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/trigger", response_model=schema.AutoDownloadResponse, summary="手动触发自动下载")
async def trigger_auto_download(
    trigger_data: schema.AutoDownloadTrigger,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """手动触发自动下载（异步后台执行）"""
    try:
        # 生成任务ID
        task_id = f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 初始化任务状态
        _task_status[task_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "rule_ids": trigger_data.rule_ids,
            "force": trigger_data.force,
            "result": None,
            "error": None
        }
        
        async def background_task():
            """后台执行任务"""
            try:
                # 在新的数据库会话中执行
                from app.db import SessionFactory
                with SessionFactory() as db:
                    task_service = AutoDownloadService(db=db)
                    result = task_service.execute_rules(
                        rule_ids=trigger_data.rule_ids,
                        force=trigger_data.force
                    )
                    db.commit()
                
                # 更新任务状态
                _task_status[task_id].update({
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "result": result
                })
                print(f"智能下载任务 {task_id} 执行完成: {result}")
                
            except Exception as e:
                # 更新任务状态
                _task_status[task_id].update({
                    "status": "failed",
                    "completed_at": datetime.now().isoformat(),
                    "error": str(e)
                })
                print(f"智能下载任务 {task_id} 执行失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # 在后台执行
        asyncio.create_task(background_task())
        
        return schema.AutoDownloadResponse(
            success=True,
            message=f"智能下载任务已启动，任务ID: {task_id}。任务将在后台执行，可通过 /api/auto-download/tasks/{task_id} 查看状态。",
            data={
                "task_id": task_id,
                "status": "started",
                "started_at": datetime.now().isoformat(),
                "rule_ids": trigger_data.rule_ids,
                "force": trigger_data.force
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tasks/{task_id}", response_model=schema.AutoDownloadResponse, summary="查询任务状态")
async def get_task_status(task_id: str):
    """查询智能下载任务状态"""
    if task_id not in _task_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    
    task_info = _task_status[task_id]
    return schema.AutoDownloadResponse(
        success=True,
        message="任务状态查询成功",
        data=task_info
    )


# 规则测试API
@router.post("/rules/{rule_id}/test", response_model=schema.AutoDownloadResponse, summary="测试规则")
async def test_rule(
    rule_id: int,
    limit: int = 10,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """测试自动下载规则，预览符合条件的视频"""
    try:
        # 这里可以实现规则测试逻辑
        # 获取规则，应用筛选条件，返回预览结果
        return schema.AutoDownloadResponse(
            success=True,
            message="测试功能暂未实现",
            data={"preview_videos": []}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# 规则启用/禁用API
@router.patch("/rules/{rule_id}/toggle", response_model=schema.AutoDownloadResponse, summary="切换规则状态")
async def toggle_rule(
    rule_id: int,
    enabled: bool,
    service: AutoDownloadService = Depends(get_auto_download_service)
):
    """启用或禁用自动下载规则"""
    try:
        rule_data = schema.AutoDownloadRuleUpdate(
            id=rule_id,
            is_enabled=enabled
        )
        rule = service.update_rule(rule_data)
        return schema.AutoDownloadResponse(
            success=True,
            message=f"规则已{'启用' if enabled else '禁用'}",
            data={
                "id": rule.id,
                "name": rule.name,
                "is_enabled": rule.is_enabled
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))