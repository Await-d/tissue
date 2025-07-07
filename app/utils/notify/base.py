from app.schema import VideoNotify, SettingNotify, SubscribeNotify
from app.schema.actor_subscribe import ActorSubscribeNotify


class Base:

    def __init__(self, setting: SettingNotify):
        self.setting = setting

    def send_video(self, video: VideoNotify):
        pass

    def send_subscribe(self, subscribe: SubscribeNotify):
        pass

    def send_actor_subscribe(self, actor_subscribe: ActorSubscribeNotify):
        pass
