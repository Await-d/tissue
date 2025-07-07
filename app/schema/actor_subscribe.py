'''
Author: Await
Date: 2025-05-26 01:10:25
LastEditors: Await
LastEditTime: 2025-05-27 02:59:10
Description: 请填写简介
'''
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ActorSubscribeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    actor_name: str
    actor_url: Optional[str] = None
    actor_thumb: Optional[str] = None
    from_date: date
    is_hd: bool = True
    is_zh: bool = False
    is_uncensored: bool = False
    is_paused: bool = False


class ActorSubscribeUpdate(ActorSubscribeCreate):
    id: int


class ActorSubscribe(ActorSubscribeUpdate):
    last_updated: Optional[datetime] = None
    download_count: Optional[int] = 0  # 添加下载数量统计字段
    subscribed_works_count: Optional[int] = 0  # 添加订阅作品总数统计字段


class ActorSubscribeStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_paused: bool


class ActorSubscribeDeleteRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    subscription_id: int
    delete_downloads: bool = False  # 是否删除已下载的资源


class ActorSubscribeNotify(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    actor_name: str
    num: str
    title: Optional[str] = None
    cover: Optional[str] = None
    magnet: Optional[str] = None
    size: Optional[str] = None
    is_hd: bool = True
    is_zh: bool = False
    is_uncensored: bool = False


class ActorSubscribeDownloadCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    actor_subscribe_id: int
    num: str
    title: Optional[str] = None
    cover: Optional[str] = None
    magnet: Optional[str] = None
    size: Optional[str] = None
    is_hd: bool = True
    is_zh: bool = False
    is_uncensored: bool = False


class ActorSubscribeDownload(ActorSubscribeDownloadCreate):
    id: int
    download_time: datetime 


class ActorSubscribeDownloadWithActor(ActorSubscribeDownload):
    """带有演员信息的下载记录"""
    actor_name: str
    actor_thumb: Optional[str] = None 