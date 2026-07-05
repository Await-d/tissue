from app.integrations.notifications.providers.telegram import TelegramNotificationProvider
from app.integrations.notifications.providers.webhook import WebhookNotificationProvider


class NotificationRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, type] = {}

    def register(self, provider_cls) -> None:
        self._providers[provider_cls.key] = provider_cls

    def get(self, key: str):
        return self._providers.get(key)


notification_registry = NotificationRegistry()
notification_registry.register(TelegramNotificationProvider)
notification_registry.register(WebhookNotificationProvider)
