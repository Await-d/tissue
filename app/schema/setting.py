from configparser import ConfigParser
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


config_path = Path(f"{Path(__file__).cwd()}/config/app.conf")


class SettingApp(BaseModel):
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    timeout: int = 60
    video_path: str = "/data/media"
    video_size_minimum: int = 100
    video_format: str = ".mp4,.mkv,.mov"
    concurrent_scraping: bool = True
    max_concurrent_spiders: int = 4
    javdb_cookie: str | None = None
    proxy: str | None = None
    preview_trace: bool = False
    enable_scheduled_scan: bool = False


class SettingFile(BaseModel):
    path: str = "/data/file"
    trans_mode: str = "copy"


class DownloaderQbittorrentConfig(BaseModel):
    host: str | None = None
    username: str | None = None
    password: str | None = None
    tracker_subscribe: str | None = ""


class SettingDownload(BaseModel):
    host: str | None = None
    username: str | None = None
    password: str | None = None
    trans_mode: str = "copy"
    download_path: str = "/downloads"
    mapping_path: str = "/downloads"
    savepath: str | None = None
    trans_auto: bool = False
    delete_auto: bool = False
    category: str | None = ""
    tracker_subscribe: str | None = ""
    stop_seeding: bool = True
    provider: str = "qbittorrent"
    providers: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        provider_payload = DownloaderQbittorrentConfig(
            host=self.host,
            username=self.username,
            password=self.password,
            tracker_subscribe=self.tracker_subscribe,
        ).model_dump()
        merged_payload = {
            **provider_payload,
            **self.providers.get("qbittorrent", {}),
        }
        self.providers["qbittorrent"] = DownloaderQbittorrentConfig(
            **merged_payload,
        ).model_dump()

    def get_provider_payload(self, provider: str | None = None) -> dict[str, Any]:
        key = provider or self.provider
        provider_payload = dict(self.providers.get(key, {}))
        if key == "qbittorrent":
            provider_payload.setdefault("host", self.host)
            provider_payload.setdefault("username", self.username)
            provider_payload.setdefault("password", self.password)
            provider_payload.setdefault(
                "tracker_subscribe",
                self.tracker_subscribe,
            )
        return provider_payload


class NotifyTelegramConfig(BaseModel):
    token: str | None = None
    chat_id: str | None = None


class NotifyWebhookConfig(BaseModel):
    url: str | None = None


class SettingNotify(BaseModel):
    type: str = "telegram"
    webhook_url: str | None = None
    telegram_token: str | None = None
    telegram_chat_id: str | None = None
    provider: str = "telegram"
    providers: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        self.provider = self.provider or self.type or "telegram"
        self.type = self.provider
        telegram_payload = NotifyTelegramConfig(
            token=self.telegram_token,
            chat_id=self.telegram_chat_id,
        ).model_dump()
        webhook_payload = NotifyWebhookConfig(url=self.webhook_url).model_dump()
        self.providers["telegram"] = NotifyTelegramConfig(
            **{**telegram_payload, **self.providers.get("telegram", {})},
        ).model_dump()
        self.providers["webhook"] = NotifyWebhookConfig(
            **{**webhook_payload, **self.providers.get("webhook", {})},
        ).model_dump()

    def get_provider_payload(self, provider: str | None = None) -> dict[str, Any]:
        key = provider or self.provider
        provider_payload = dict(self.providers.get(key, {}))
        if key == "telegram":
            provider_payload.setdefault("token", self.telegram_token)
            provider_payload.setdefault("chat_id", self.telegram_chat_id)
        if key == "webhook":
            provider_payload.setdefault("url", self.webhook_url)
        return provider_payload


class SettingAutoDownload(BaseModel):
    enabled: bool = True
    check_interval: int = 60
    max_daily_downloads: int = 10
    auto_cleanup_days: int = 30
    notification_enabled: bool = True


class SettingCookieCloud(BaseModel):
    enabled: bool = False
    host: str | None = None
    uuid: str | None = None
    password: str | None = None


class Setting(BaseModel):
    app: SettingApp = Field(default_factory=SettingApp)
    file: SettingFile = Field(default_factory=SettingFile)
    download: SettingDownload = Field(default_factory=SettingDownload)
    notify: SettingNotify = Field(default_factory=SettingNotify)
    auto_download: SettingAutoDownload = Field(default_factory=SettingAutoDownload)
    cookiecloud: SettingCookieCloud = Field(default_factory=SettingCookieCloud)

    def __init__(self, **data: Any):
        if not data:
            from app.settings import settings_manager

            data = settings_manager.load()
        super().__init__(**data)

    @staticmethod
    def read() -> dict[str, Any]:
        from app.settings import settings_manager

        return settings_manager.load()

    @staticmethod
    def read_ini() -> dict[str, dict[str, Any]]:
        parser = ConfigParser()
        parser.read(config_path)
        sections = parser.sections()
        setting: dict[str, dict[str, Any]] = {}
        for section in sections:
            setting[section] = dict(parser.items(section))
        return setting

    @staticmethod
    def write_section(section: str, setting: dict[str, Any]) -> None:
        from app.settings import settings_manager

        settings_manager.save_section(section, setting)
