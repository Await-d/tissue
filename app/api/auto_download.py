"""
自动下载API路由
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app import schema
from app.dependencies.security import verify_token
from app.service.auto_download import get_auto_download_service, AutoDownloadService
from app.dependencies.auto_download import normalize_time_range_type
from app.db.models.auto_download import TimeRangeType


router = APIRouter(tags=["自动下载"], dependencies=[Depends(verify_token)])


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
    """手动触发自动下载"""
    try:
        result = service.execute_rules(
            rule_ids=trigger_data.rule_ids,
            force=trigger_data.force
        )
        return schema.AutoDownloadResponse(
            success=True,
            message="触发成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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