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
    service.add_actor_subscription(subscription)
    return R.ok()


@router.put("/")
def update_actor_subscription(
    subscription: schema.actor_subscribe.ActorSubscribeUpdate, 
    service=Depends(get_actor_subscribe_service)
):
    """更新演员订阅"""
    service.update_actor_subscription(subscription)
    return R.ok()


@router.delete("/")
def delete_actor_subscription(
    subscribe_id: int, 
    service=Depends(get_actor_subscribe_service)
):
    """删除演员订阅"""
    service.delete_actor_subscription(subscribe_id)
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