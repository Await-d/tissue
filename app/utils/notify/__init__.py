'''
Author: Await
Date: 2025-05-27 04:22:16
LastEditors: Await
LastEditTime: 2025-05-27 04:23:32
Description: 请填写简介
'''
'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 03:00:45
Description: 请填写简介
'''
from app.schema import VideoNotify, Setting, SubscribeNotify
from app.schema.actor_subscribe import ActorSubscribeNotify
from app.utils.logger import logger
from app.utils.notify.base import Base
from app.utils.notify.telegram import Telegram
from app.utils.notify.webhook import Webhook


def match_notification() -> Base:
    setting = Setting().notify

    notification_type = setting.type
    if notification_type == 'telegram':
        return Telegram(setting)
    elif notification_type == 'webhook':
        return Webhook(setting)
    else:
        # 默认返回Webhook或抛出异常
        return Webhook(setting)


def send_video(video: VideoNotify):
    try:
        notification = match_notification()
        notification.send_video(video)
    except:
        logger.error("消息发送失败：视频整理成功")


def send_subscribe(subscribe: SubscribeNotify):
    try:
        notification = match_notification()
        notification.send_subscribe(subscribe)
    except:
        logger.error("消息发送失败：订阅下载成功")


def send_actor_subscribe(actor_subscribe: ActorSubscribeNotify):
    try:
        notification = match_notification()
        notification.send_actor_subscribe(actor_subscribe)
    except Exception as e:
        logger.error(f"消息发送失败：演员订阅通知 - {e}")
