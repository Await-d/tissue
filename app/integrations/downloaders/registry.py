from app.integrations.downloaders.providers.qbittorrent import QBittorrentDownloader


class DownloaderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, type[QBittorrentDownloader]] = {}

    def register(self, provider_cls) -> None:
        self._providers[provider_cls.key] = provider_cls

    def get(self, key: str):
        return self._providers.get(key)


downloader_registry = DownloaderRegistry()
downloader_registry.register(QBittorrentDownloader)
