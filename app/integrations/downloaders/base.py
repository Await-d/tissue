from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AddTorrentResult:
    success: bool
    torrent_hash: str | None = None
    message: str | None = None


class DownloaderProvider(Protocol):
    key: str
    label: str

    def test_connection(self) -> dict[str, Any]: ...

    def get_torrents(
        self,
        category: str | None = None,
        include_failed: bool = True,
        include_success: bool = True,
    ) -> Any: ...

    def get_torrent_files(self, torrent_hash: str) -> Any: ...

    def add_magnet(
        self,
        magnet: str,
        save_path: str | None = None,
        category: str | None = None,
        paused: bool = False,
    ) -> Any: ...

    def add_torrent_tags(self, torrent_hash: str, tags: list[str]) -> Any: ...

    def remove_torrent_tags(self, torrent_hash: str, tags: list[str]) -> Any: ...

    def delete_torrent(self, torrent_hash: str, delete_files: bool = True) -> Any: ...

    def stop_torrent(self, torrent_hash: str) -> Any: ...

    def resume_torrent(self, torrent_hash: str) -> Any: ...

    def recheck_torrent(self, torrent_hash: str) -> Any: ...

    def get_torrent_properties(self, torrent_hash: str) -> Any: ...

    def set_file_priority(self, torrent_hash: str, file_ids: list[int], priority: int) -> Any: ...

    def get_all_torrents(self) -> Any: ...

    def extract_hash_from_magnet(self, magnet: str) -> str | None: ...

    def is_magnet_exists(self, magnet: str) -> bool: ...
