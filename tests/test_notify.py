from datetime import date

from app.schema import SubscribeNotify
from app.utils import notify


def test_send_subscribe_serializes_publish_date_for_notification_payload(monkeypatch):
    subscribe = SubscribeNotify(num="MIDA-732")
    subscribe = subscribe.model_copy(update={"publish_date": date(2026, 8, 25)})
    received = []

    monkeypatch.setattr(
        notify.notification_manager,
        "emit_subscribe_started",
        received.append,
    )

    notify.send_subscribe(subscribe)

    assert len(received) == 1
    assert received[0].publish_date == "2026-08-25"
