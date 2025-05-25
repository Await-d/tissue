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


class ActorSubscribeUpdate(ActorSubscribeCreate):
    id: int


class ActorSubscribe(ActorSubscribeUpdate):
    last_updated: Optional[datetime] = None


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