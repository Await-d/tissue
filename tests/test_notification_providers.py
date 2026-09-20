from app.integrations.notifications.providers.telegram import TelegramNotificationProvider
from app.schema.notification import SubscribeStartedPayload, VideoSavedPayload
from app.schema.video import VideoActor


def _capture_content(provider, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        provider,
        "_send_message_with_cover",
        lambda content, cover: captured.setdefault("content", content),
    )
    return captured


def test_video_saved_escapes_actor_names(monkeypatch):
    provider = TelegramNotificationProvider({})
    captured = _capture_content(provider, monkeypatch)

    provider._send_video_saved(
        VideoSavedPayload(
            num="<b>X</b>",
            path="/tmp/<script>.mp4",
            actors=[VideoActor(name="<script>alert(1)</script>")],
        )
    )

    content = captured["content"]
    assert "<script>" not in content
    assert "&lt;script&gt;" in content
    assert "<b>X</b>" not in content


def test_subscribe_started_escapes_url_and_fields(monkeypatch):
    provider = TelegramNotificationProvider({})
    captured = _capture_content(provider, monkeypatch)

    provider._send_subscribe_started(
        SubscribeStartedPayload(
            num="X-1",
            url="https://example.com/'><b>inject</b>",
            name="<i>n</i>",
            actors="<u>a</u>",
        )
    )

    content = captured["content"]
    assert "<b>inject</b>" not in content
    assert "<i>n</i>" not in content
    assert "<u>a</u>" not in content
    assert "&lt;i&gt;n&lt;/i&gt;" in content
    assert "&#x27;" in content


def test_cover_picture_name_is_sanitized(monkeypatch):
    provider = TelegramNotificationProvider({})
    captured = {}

    monkeypatch.setattr(
        "app.integrations.notifications.providers.telegram.ResourceService.fetch_image_bytes",
        lambda _url, _image_type: b"image",
    )
    monkeypatch.setattr(
        provider,
        "_send_message",
        lambda content, picture=None, picture_name=None: captured.update(
            name=picture_name
        ),
    )

    provider._send_message_with_cover(
        "x", "https://example.com/a.jpg\r\nX-Injected: 1"
    )

    assert captured["name"] == "cover.jpg"
