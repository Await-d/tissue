from app.integrations.notifications.manager import notification_manager
from app.schema import SubscribeNotify, VideoNotify
from app.schema.actor_subscribe import ActorSubscribeNotify
from app.schema.notification import (
    ActorSubscribeStartedPayload,
    SubscribeStartedPayload,
    VideoFailedPayload,
    VideoSavedPayload,
)


def send_video(video: VideoNotify):
    if video.is_success:
        notification_manager.emit_video_saved(
            VideoSavedPayload.model_validate(video.model_dump()),
        )
        return

    notification_manager.emit_video_failed(
        VideoFailedPayload.model_validate(video.model_dump()),
    )


def send_subscribe(subscribe: SubscribeNotify):
    notification_manager.emit_subscribe_started(
        SubscribeStartedPayload.model_validate(subscribe.model_dump()),
    )


def send_actor_subscribe(actor_subscribe: ActorSubscribeNotify):
    notification_manager.emit_actor_subscribe_started(
        ActorSubscribeStartedPayload.model_validate(actor_subscribe.model_dump()),
    )
