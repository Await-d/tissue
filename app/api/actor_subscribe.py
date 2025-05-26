"""
Author: Await
Date: 2025-05-26 00:30:00
LastEditors: Await
LastEditTime: 2025-05-26 00:30:00
Description: 演员订阅API
"""

from typing import List, Optional

from fastapi import APIRouter, Depends

from app import schema
from app.schema.r import R
from app.service.actor_subscribe import get_actor_subscribe_service

router = APIRouter()


@router.get("/", response_model=R[List[schema.actor_subscribe.ActorSubscribe]])
def get_actor_subscriptions(service=Depends(get_actor_subscribe_service)):
    """获取演员订阅列表"""
    subscriptions = service.get_actor_subscriptions()
    return R.list(subscriptions)


@router.post("/")
def add_actor_subscription(
    subscription: schema.actor_subscribe.ActorSubscribeCreate, 
    service=Depends(get_actor_subscribe_service)
):
    """添加演员订阅"""
    result = service.add_actor_subscription(subscription)
    # 返回结果中加入is_update标识，表示是更新还是新增
    is_update = hasattr(result, 'id') and result.id is not None
    return R.ok(data={"is_update": is_update, "id": result.id if is_update else None})


@router.put("/")
def update_actor_subscription(
    subscription: schema.actor_subscribe.ActorSubscribeUpdate, 
    service=Depends(get_actor_subscribe_service)
):
    """更新演员订阅"""
    service.update_actor_subscription(subscription)
    return R.ok()


@router.put("/status")
def update_actor_subscription_status(
    status: schema.actor_subscribe.ActorSubscribeStatusUpdate,
    service=Depends(get_actor_subscribe_service)
):
    """更新演员订阅状态（暂停/恢复）"""
    service.update_actor_subscription_status(status)
    return R.ok()


@router.delete("/")
def delete_actor_subscription(
    delete_request: schema.actor_subscribe.ActorSubscribeDeleteRequest,
    service=Depends(get_actor_subscribe_service)
):
    """删除演员订阅"""
    service.delete_actor_subscription(
        delete_request.subscription_id, 
        delete_request.delete_downloads
    )
    return R.ok()


@router.get("/downloads", response_model=R[List[schema.actor_subscribe.ActorSubscribeDownload]])
def get_actor_subscription_downloads(
    actor_id: int,
    service=Depends(get_actor_subscribe_service)
):
    """获取演员订阅的下载记录"""
    downloads = service.get_actor_subscription_downloads(actor_id)
    return R.list(downloads)


@router.post("/run")
def run_actor_subscribe(service=Depends(get_actor_subscribe_service)):
    """手动执行演员订阅任务"""
    service.do_actor_subscribe()
    return R.ok() 