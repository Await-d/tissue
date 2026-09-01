from types import SimpleNamespace

import pytest

from app.schema import VideoDetail, VideoDownload
from app.service import actor_subscribe as actor_subscribe_module
from app.service import base_download as base_download_module
from app.schema import setting as setting_module


class FakeDatabase:
    def flush(self):
        return None

    def commit(self):
        return None

    def rollback(self):
        return None


class CapturingBaseDownloadService:
    calls = []

    def __init__(self, _db):
        pass

    def download_with_filter(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "success": True,
            "pending": False,
            "torrent_hash": None,
            "message": "accepted",
            "filtered_files": 0,
            "total_files": 0,
        }


class FakeActorSubscribeDownload:
    def __init__(self, **_kwargs):
        pass

    def add(self, _db):
        return None


def run_actor_download_with_savepath(monkeypatch, link_savepath: str | None):
    setting = SimpleNamespace(download=setting_module.SettingDownload(category=""))
    CapturingBaseDownloadService.calls = []
    monkeypatch.setattr(setting_module, "Setting", lambda: setting)
    monkeypatch.setattr(
        base_download_module, "BaseDownloadService", CapturingBaseDownloadService
    )
    monkeypatch.setattr(
        actor_subscribe_module,
        "ActorSubscribeDownload",
        FakeActorSubscribeDownload,
    )
    monkeypatch.setattr(
        actor_subscribe_module.notify, "send_actor_subscribe", lambda _: None
    )

    service = actor_subscribe_module.ActorSubscribeService(FakeDatabase())
    service.download_actor_video(
        {"id": 1, "actor_name": "actor"},
        VideoDetail(num="TEST-001", title="Test"),
        VideoDownload(
            magnet="magnet:?xt=urn:btih:0123456789abcdef", savepath=link_savepath
        ),
    )

    return CapturingBaseDownloadService.calls[0]["savepath"]


@pytest.mark.parametrize("link_savepath", [None, ""])
def test_actor_download_uses_default_path_when_resource_savepath_is_empty(
    monkeypatch, link_savepath
):
    assert run_actor_download_with_savepath(monkeypatch, link_savepath) == "/downloads"


def test_actor_download_uses_resource_savepath_when_provided(monkeypatch):
    assert (
        run_actor_download_with_savepath(monkeypatch, "/custom/downloads")
        == "/custom/downloads"
    )
