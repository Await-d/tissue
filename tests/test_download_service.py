from types import SimpleNamespace

from requests import Response

from app.service import download as download_module


class FakeDownloadFilterService:
    def __init__(self, _db):
        pass

    def filter_torrent_files_readonly(self, _torrent_hash, _files):
        return {"success": True, "files": []}


class FakeQBittorrent:
    def test_connection(self):
        return {"status": True}

    def get_all_torrents(self):
        return [
            {
                "hash": "torrent-hash",
                "name": "example",
                "total_size": 1024,
                "save_path": "/downloads",
                "content_path": "/downloads/example",
                "tags": "整理成功",
            }
        ]

    def get_torrent_files(self, _torrent_hash):
        response = Response()
        response.status_code = 200
        response._content = b""
        return response


def test_get_downloads_skips_torrent_when_files_response_is_not_json(monkeypatch):
    setting = SimpleNamespace(
        download=SimpleNamespace(
            host="http://qbittorrent:8080",
            username="admin",
            category="",
            download_path="/downloads",
            mapping_path="/downloads",
        ),
        app=SimpleNamespace(video_format=".mp4,.mkv,.mov"),
    )
    monkeypatch.setattr(download_module, "Setting", lambda: setting)
    monkeypatch.setattr(
        download_module, "DownloadFilterService", FakeDownloadFilterService
    )

    service = download_module.DownloadService(db=None)
    service.qb = FakeQBittorrent()

    assert service.get_downloads(include_success=True, include_failed=False) == []
