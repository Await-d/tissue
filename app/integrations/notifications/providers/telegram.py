import os

import requests

from app.integrations.notifications.base import NotificationEvent, NotificationProvider
from app.schema.notification import (
    ActorSubscribeStartedPayload,
    CookieInvalidPayload,
    SubscribeStartedPayload,
    VideoFailedPayload,
    VideoSavedPayload,
)
from app.service.resource import ResourceService


class TelegramNotificationProvider(NotificationProvider):
    key = "telegram"
    label = "Telegram"

    def send(self, event: NotificationEvent) -> None:
        if event.event == "video.saved":
            self._send_video_saved(VideoSavedPayload.model_validate(event.payload))
            return
        if event.event == "video.failed":
            self._send_video_failed(VideoFailedPayload.model_validate(event.payload))
            return
        if event.event == "subscribe.started":
            self._send_subscribe_started(SubscribeStartedPayload.model_validate(event.payload))
            return
        if event.event == "actor-subscribe.started":
            self._send_actor_subscribe_started(ActorSubscribeStartedPayload.model_validate(event.payload))
            return
        if event.event == "cookie.invalid":
            self._send_cookie_invalid(CookieInvalidPayload.model_validate(event.payload))

    def _send_video_saved(self, video: VideoSavedPayload) -> None:
        actors = ", ".join(actor.name or "" for actor in video.actors if actor.name)
        tags: list[str] = []
        if video.is_zh:
            tags.append("中文")
        if video.is_uncensored:
            tags.append("无码")
        content = (
            f"\n<b><tg-spoiler>{video.num or '-'}</tg-spoiler>整理成功</b>\n"
            f"演员：<tg-spoiler>{actors or '-'}</tg-spoiler>\n"
            f"大小：{video.size or '-'}\n"
            f"文件：<tg-spoiler>{video.path or '-'}</tg-spoiler>\n"
            f"标签：<tg-spoiler>{', '.join(tags) if tags else '-'}</tg-spoiler>\n"
        )
        self._send_message_with_cover(content, video.cover)

    def _send_video_failed(self, video: VideoFailedPayload) -> None:
        content = (
            "\n<b>影片整理失败</b>\n"
            f"文件：<tg-spoiler>{video.path or '-'}</tg-spoiler>\n"
            f"大小：{video.size or '-'}\n"
            f"消息：<tg-spoiler>{video.message or '-'}</tg-spoiler>\n"
        )
        self._send_message_with_cover(content, video.cover)

    def _send_subscribe_started(self, subscribe: SubscribeStartedPayload) -> None:
        tags: list[str] = []
        if subscribe.is_hd:
            tags.append("高清")
        if subscribe.is_zh:
            tags.append("中文")
        if subscribe.is_uncensored:
            tags.append("无码")
        link = f"<a href='{subscribe.url}'>点击</a>" if subscribe.url else "-"
        content = (
            f"\n<b><tg-spoiler>{subscribe.num}</tg-spoiler>开始下载</b>\n"
            f"演员：<tg-spoiler>{subscribe.actors or '-'}</tg-spoiler>\n"
            f"大小：{subscribe.size or '-'}\n"
            f"名称：<tg-spoiler>{subscribe.name or '-'}</tg-spoiler>\n"
            f"站点：<tg-spoiler>{subscribe.website or '-'}</tg-spoiler>\n"
            f"链接：{link}\n"
            f"日期：{subscribe.publish_date or '-'}\n"
            f"标签：<tg-spoiler>{', '.join(tags) if tags else '-'}</tg-spoiler>\n"
        )
        self._send_message_with_cover(content, subscribe.cover)

    def _send_actor_subscribe_started(self, actor_subscribe: ActorSubscribeStartedPayload) -> None:
        tags: list[str] = []
        if actor_subscribe.is_hd:
            tags.append("高清")
        if actor_subscribe.is_zh:
            tags.append("中文")
        if actor_subscribe.is_uncensored:
            tags.append("无码")
        content = (
            f"\n<b>演员订阅: <tg-spoiler>{actor_subscribe.actor_name}</tg-spoiler>新作品</b>\n"
            f"番号：<tg-spoiler>{actor_subscribe.num}</tg-spoiler>\n"
            f"标题：<tg-spoiler>{actor_subscribe.title or '-'}</tg-spoiler>\n"
            f"大小：{actor_subscribe.size or '-'}\n"
            f"标签：<tg-spoiler>{', '.join(tags) if tags else '-'}</tg-spoiler>\n"
        )
        self._send_message_with_cover(content, actor_subscribe.cover)

    def _send_cookie_invalid(self, cookie: CookieInvalidPayload) -> None:
        content = (
            "\n<b>Cookie 已失效</b>\n"
            f"站点：{cookie.site_name}\n"
            f"域名：{cookie.domain}\n"
            f"消息：{cookie.message}\n"
        )
        self._send_message(content)

    def _send_message_with_cover(self, content: str, cover_url: str | None) -> None:
        picture = None
        picture_name = None
        if cover_url:
            picture = ResourceService.fetch_image_bytes(cover_url, "cover")
            _, ext_name = os.path.splitext(cover_url)
            picture_name = f"cover{ext_name}"
        self._send_message(content, picture=picture, picture_name=picture_name)

    def _send_message(self, content: str, picture: bytes | None = None, picture_name: str | None = None) -> None:
        token = self.config.get("token")
        chat_id = self.config.get("chat_id")
        if not token or not chat_id:
            return

        if picture:
            requests.post(
                url=f"https://api.telegram.org/bot{token}/sendPhoto",
                data={
                    "chat_id": chat_id,
                    "parse_mode": "HTML",
                    "caption": content,
                    "has_spoiler": True,
                },
                files={"photo": (picture_name, picture)},
                timeout=10,
            )
            return

        requests.post(
            url=f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "parse_mode": "HTML",
                "text": content,
            },
            timeout=10,
        )
