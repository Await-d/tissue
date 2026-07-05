from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class NotificationEvent(BaseModel):
    event: str
    version: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any]


class NotificationProvider:
    key: str
    label: str

    def __init__(self, config: dict[str, Any]):
        self.config = config

    def send(self, event: NotificationEvent) -> None:
        raise NotImplementedError
