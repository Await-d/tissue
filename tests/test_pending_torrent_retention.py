from requests import Response

from app.db.models.pending_torrent import PendingTorrent, PendingTorrentStatus
from app.service import base_download as base_download_module
from app.service.pending_torrent import PendingTorrentService


class FakeQBittorrent:
    def __init__(self, files):
        self.files = files
        self.deleted_hashes = []

    def get_all_torrents(self):
        return [
            {
                "hash": "torrent-hash",
                "name": "display-name-before-metadata",
                "save_path": "/downloads",
                "content_path": "/downloads/display-name-before-metadata",
                "total_size": 0,
            }
        ]

    def get_torrent_files(self, _torrent_hash):
        response = Response()
        response.status_code = 200
        response._content = self.files
        return response

    def delete_torrent(self, torrent_hash, delete_files=True):
        self.deleted_hashes.append((torrent_hash, delete_files))

    def is_magnet_exists(self, _magnet):
        return False

    def add_magnet(self, _magnet, _savepath, category=None, paused=False):
        response = Response()
        response.status_code = 200
        return response

    def extract_hash_from_magnet(self, _magnet):
        return "torrent-hash"


class RejectingFilterService:
    def __init__(self):
        self.calls = 0

    def filter_torrent_files(self, _torrent_hash):
        self.calls += 1
        return {
            "success": False,
            "message": "无法获取种子文件列表",
            "original_files": 0,
            "filtered_files": 0,
        }


def create_pending(db_session):
    pending = PendingTorrent(
        torrent_hash="torrent-hash",
        magnet="magnet:?xt=urn:btih:torrent-hash",
        savepath="/downloads",
        category="category",
        source="manual",
        status=PendingTorrentStatus.WAITING_METADATA,
    )
    db_session.add(pending)
    db_session.commit()
    return pending


def test_pending_task_waits_when_display_name_exists_but_files_are_unavailable(db_session):
    pending = create_pending(db_session)
    qbittorrent = FakeQBittorrent(b"[]")
    filter_service = RejectingFilterService()
    service = PendingTorrentService(db_session)
    service.qb = qbittorrent
    service.filter_service = filter_service

    processed = service.check_metadata_and_filter(pending)

    db_session.refresh(pending)
    assert processed is False
    assert pending.status is PendingTorrentStatus.WAITING_METADATA
    assert pending.retry_count == 1
    assert filter_service.calls == 0
    assert qbittorrent.deleted_hashes == []


def test_pending_filter_failure_retries_when_file_list_is_temporarily_unavailable(db_session):
    pending = create_pending(db_session)
    qbittorrent = FakeQBittorrent(b'[{"index": 0, "name": "video.mp4", "size": 1024}]')
    filter_service = RejectingFilterService()
    service = PendingTorrentService(db_session)
    service.qb = qbittorrent
    service.filter_service = filter_service

    processed = service.check_metadata_and_filter(pending)

    db_session.refresh(pending)
    assert processed is False
    assert pending.status is PendingTorrentStatus.WAITING_METADATA
    assert filter_service.calls == 1
    assert qbittorrent.deleted_hashes == []


def test_initial_filter_failure_keeps_the_paused_task(monkeypatch, db_session):
    qbittorrent = FakeQBittorrent(b'[{"index": 0, "name": "video.mp4", "size": 1024}]')
    filter_service = RejectingFilterService()
    monkeypatch.setattr(base_download_module, "qbittorent", qbittorrent)
    service = base_download_module.BaseDownloadService(db_session)
    service.filter_service = filter_service

    result = service.download_with_filter(
        magnet="magnet:?xt=urn:btih:torrent-hash",
        savepath="/downloads",
        category="category",
    )

    assert result["success"] is True
    assert result["pending"] is True
    assert filter_service.calls == 1
    assert qbittorrent.deleted_hashes == []
    pending = service.pending_service.get_pending_torrent("torrent-hash")
    assert pending is not None
    assert pending.status is PendingTorrentStatus.WAITING_METADATA
