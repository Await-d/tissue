from datetime import datetime, timezone

import jwt

from app.schema.setting import SettingDownload, SettingNotify
from app.utils.security import algorithm, create_access_token, secret_key


def test_create_access_token_uses_short_default_expiry():
    token = create_access_token("123", remember=False)

    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    expire_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

    assert 11 <= (expire_at - issued_at).total_seconds() / 3600 <= 13


def test_create_access_token_uses_long_remember_expiry():
    token = create_access_token("123", remember=True)

    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    expire_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

    assert 360 <= (expire_at - issued_at).days <= 366


def test_download_provider_payload_falls_back_to_legacy_fields():
    setting = SettingDownload(host="http://qb:8080", username="user", password="pass", tracker_subscribe="https://trackers")

    payload = setting.get_provider_payload("qbittorrent")

    assert payload["host"] == "http://qb:8080"
    assert payload["username"] == "user"
    assert payload["password"] == "pass"
    assert payload["tracker_subscribe"] == "https://trackers"


def test_notify_provider_payload_falls_back_to_legacy_fields():
    setting = SettingNotify(
        type="telegram",
        telegram_token="token",
        telegram_chat_id="chat-id",
        webhook_url="https://hook.example.com",
    )

    telegram_payload = setting.get_provider_payload("telegram")
    webhook_payload = setting.get_provider_payload("webhook")

    assert telegram_payload["token"] == "token"
    assert telegram_payload["chat_id"] == "chat-id"
    assert webhook_payload["url"] == "https://hook.example.com"
