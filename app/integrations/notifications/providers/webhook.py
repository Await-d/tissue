import requests

from app.integrations.notifications.base import NotificationEvent, NotificationProvider


class WebhookNotificationProvider(NotificationProvider):
    key = "webhook"
    label = "Webhook"

    def send(self, event: NotificationEvent) -> None:
        url = self.config.get("url")
        if not url:
            return
        requests.post(url, json=event.model_dump(mode="json"), timeout=10)
