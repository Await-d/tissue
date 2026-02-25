from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class SettingApp(BaseModel):
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    timeout: int = 60

    video_path: str = "/data/media"

    video_size_minimum: int = 100
    video_format: str = ".mp4,.mkv,.mov"

    # 并发刮削配置
    concurrent_scraping: bool = True
    max_concurrent_spiders: int = 4

    # JavDB登录Cookie（排行榜等页面需要登录才能访问）
    javdb_cookie: Optional[str] = None

    # HTTP代理配置（格式: http://host:port 或 socks5://host:port）
    # 服务器IP被目标站点屏蔽时，可通过代理访问
    proxy: Optional[str] = None
    preview_trace: bool = False
    # 定时扫描配置
    enable_scheduled_scan: bool = False


class SettingFile(BaseModel):
    path: str = "/data/file"
    trans_mode: str = "copy"


class SettingDownload(BaseModel):
    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    trans_mode: str = "copy"
    download_path: str = "/downloads"
    mapping_path: str = "/downloads"
    savepath: Optional[str] = None
    trans_auto: bool = False
    delete_auto: bool = False
    category: Optional[str] = ""
    tracker_subscribe: Optional[str] = ""
    stop_seeding: bool = True


class SettingNotify(BaseModel):
    type: str = "telegram"

    webhook_url: Optional[str] = None

    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class SettingAutoDownload(BaseModel):
    enabled: bool = True
    check_interval: int = 60
    max_daily_downloads: int = 10
    auto_cleanup_days: int = 30
    notification_enabled: bool = True


config_path = Path(f"{Path(__file__).cwd()}/config/app.conf")


class Setting(BaseModel):
    app: SettingApp = SettingApp()
    file: SettingFile = SettingFile()
    download: SettingDownload = SettingDownload()
    notify: SettingNotify = SettingNotify()
    auto_download: SettingAutoDownload = SettingAutoDownload()

    def __init__(self):
        settings = Setting.read()
        super().__init__(**settings)

    @staticmethod
    def read():
        parser = ConfigParser()
        parser.read(config_path)
        sections = parser.sections()
        setting = {}
        for section in sections:
            setting[section] = dict(parser.items(section))

        return setting

    @staticmethod
    def write_section(section: str, setting: dict):
        parser = ConfigParser()
        parser.read(config_path)
        # configparser 要求所有值必须是字符串类型
        string_setting = {k: "" if v is None else str(v) for k, v in setting.items()}
        parser[section] = string_setting
        with open(config_path, "w") as file:
            parser.write(file)
