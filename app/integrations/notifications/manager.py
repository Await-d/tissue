from pydantic import BaseModel

from app.integrations.notifications.base import NotificationEvent
from app.integrations.notifications.registry import notification_registry
from app.schema.notification import (
    ActorSubscribeStartedPayload,
    CookieInvalidPayload,
    SubscribeStartedPayload,
    VideoFailedPayload,
    VideoSavedPayload,
)
from app.schema.setting import Setting
from app.utils.logger import logger


class NotificationManager:
    def __init__(self) -> None:
        self._provider = None
        self._provider_key: str | None = None
        self._provider_signature: tuple[tuple[str, object], ...] | None = None

    def refresh(self) -> None:
        self._provider = None
        self._provider_key = None
        self._provider_signature = None

    def get_active(self):
        setting = Setting().notify
        provider_key = setting.provider
        provider_cls = notification_registry.get(provider_key)
        if provider_cls is None:
            raise ValueError(f"不支持的通知渠道: {provider_key}")

        provider_config = setting.get_provider_payload(provider_key)
        signature = tuple(sorted(provider_config.items()))
        if (
            self._provider is None
            or self._provider_key != provider_key
            or self._provider_signature != signature
        ):
            self._provider = provider_cls(provider_config)
            self._provider_key = provider_key
            self._provider_signature = signature
        return self._provider

    def emit(self, event: NotificationEvent) -> None:
        try:
            self.get_active().send(event)
        except Exception as exc:
            logger.error(f"消息发送失败: {exc}")

    def emit_event(self, event_name: str, payload: BaseModel) -> None:
        self.emit(NotificationEvent(event=event_name, payload=payload.model_dump()))

    def emit_video_saved(self, payload: VideoSavedPayload) -> None:
        self.emit_event("video.saved", payload)

    def emit_video_failed(self, payload: VideoFailedPayload) -> None:
        self.emit_event("video.failed", payload)

    def emit_subscribe_started(self, payload: SubscribeStartedPayload) -> None:
        self.emit_event("subscribe.started", payload)

    def emit_actor_subscribe_started(self, payload: ActorSubscribeStartedPayload) -> None:
        self.emit_event("actor-subscribe.started", payload)

    def emit_cookie_invalid(self, payload: CookieInvalidPayload) -> None:
        self.emit_event("cookie.invalid", payload)


notification_manager = NotificationManager()
