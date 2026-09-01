from types import SimpleNamespace

import pytest

from app import schema
from app.schema import setting as setting_module
from app.service import base_download as base_download_module
from app.service import subscribe as subscribe_module


class FakeDatabase:
    def commit(self):
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


def run_download_with_savepath(monkeypatch, link_savepath: str | None):
    setting = SimpleNamespace(download=setting_module.SettingDownload(category=""))
    CapturingBaseDownloadService.calls = []
    monkeypatch.setattr(setting_module, "Setting", lambda: setting)
    monkeypatch.setattr(
        base_download_module, "BaseDownloadService", CapturingBaseDownloadService
    )
    monkeypatch.setattr(
        subscribe_module.SubscribeService,
        "_check_and_record_actor_subscribe_download",
        lambda *_args: None,
    )

    service = subscribe_module.SubscribeService(FakeDatabase())
    service.download_video(
        schema.SubscribeCreate(num="TEST-001"),
        schema.VideoDownload(
            magnet="magnet:?xt=urn:btih:0123456789abcdef", savepath=link_savepath
        ),
        send_notification=False,
    )

    return CapturingBaseDownloadService.calls[0]["savepath"]


@pytest.mark.parametrize("link_savepath", [None, ""])
def test_download_uses_default_path_when_link_savepath_is_empty(
    monkeypatch, link_savepath
):
    assert run_download_with_savepath(monkeypatch, link_savepath) == "/downloads"


def test_download_uses_link_savepath_when_provided(monkeypatch):
    assert (
        run_download_with_savepath(monkeypatch, "/custom/downloads")
        == "/custom/downloads"
    )
