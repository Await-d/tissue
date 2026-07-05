from typing import Any

from app.utils.qbittorent import QBittorent


class QBittorrentDownloader:
    key = "qbittorrent"
    label = "qBittorrent"

    def __init__(self, config: dict[str, Any]):
        self.client = QBittorent(config=config)

    def test_connection(self) -> dict[str, Any]:
        return self.client.test_connection()

    def get_torrents(
        self,
        category: str | None = None,
        include_failed: bool = True,
        include_success: bool = True,
    ):
        return self.client.get_torrents(
            category=category,
            include_failed=include_failed,
            include_success=include_success,
        )

    def get_torrent_files(self, torrent_hash: str):
        return self.client.get_torrent_files(torrent_hash)

    def add_magnet(
        self,
        magnet: str,
        save_path: str | None = None,
        category: str | None = None,
        paused: bool = False,
    ):
        return self.client.add_magnet(
            magnet,
            savepath=save_path,
            category=category,
            paused=paused,
        )

    def add_torrent_tags(self, torrent_hash: str, tags: list[str]):
        self.client.add_torrent_tags(torrent_hash, tags)

    def remove_torrent_tags(self, torrent_hash: str, tags: list[str]):
        self.client.remove_torrent_tags(torrent_hash, tags)

    def delete_torrent(self, torrent_hash: str, delete_files: bool = True):
        return self.client.delete_torrent(torrent_hash, delete_files=delete_files)

    def stop_torrent(self, torrent_hash: str):
        return self.client.stop_torrent(torrent_hash)

    def resume_torrent(self, torrent_hash: str):
        return self.client.resume_torrent(torrent_hash)

    def recheck_torrent(self, torrent_hash: str):
        return self.client.recheck_torrent(torrent_hash)

    def get_torrent_properties(self, torrent_hash: str):
        return self.client.get_torrent_properties(torrent_hash)

    def set_file_priority(self, torrent_hash: str, file_ids: list[int], priority: int):
        return self.client.set_file_priority(torrent_hash, file_ids, priority)

    def get_all_torrents(self):
        return self.client.get_all_torrents()

    def extract_hash_from_magnet(self, magnet: str) -> str | None:
        return self.client.extract_hash_from_magnet(magnet)

    def is_magnet_exists(self, magnet: str) -> bool:
        return self.client.is_magnet_exists(magnet)
