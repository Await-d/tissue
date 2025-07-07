import requests

from app.schema import VideoNotify, SubscribeNotify
from app.schema.actor_subscribe import ActorSubscribeNotify
from app.utils.notify.base import Base


class Webhook(Base):

    def send_video(self, video: VideoNotify):
        self.send('video', video.model_dump())

    def send_subscribe(self, subscribe: SubscribeNotify):
        self.send('subscribe', subscribe.model_dump())

    def send_actor_subscribe(self, actor_subscribe: ActorSubscribeNotify):
        self.send('actor_subscribe', actor_subscribe.model_dump())

    def send(self, event: str, payload: dict):
        requests.post(self.setting.webhook_url, json={
            'event': event,
            'payload': payload
        })
