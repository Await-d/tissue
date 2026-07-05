from app.integrations.downloaders.manager import downloader_manager
from app.integrations.notifications.manager import notification_manager
from app.service.cookiecloud import cookiecloud_service
from app.scheduler import scheduler
from app.schema import Setting


class SettingService:
    @staticmethod
    def save_section(section: str, payload: dict) -> None:
        Setting.write_section(section, payload)
        latest_setting = Setting()

        if section == "download":
            if latest_setting.download.trans_auto:
                scheduler.add("scrape_download")
            else:
                scheduler.remove("scrape_download")

            if latest_setting.download.delete_auto:
                scheduler.add("delete_complete_download")
            else:
                scheduler.remove("delete_complete_download")

            if latest_setting.download.stop_seeding:
                scheduler.add("stop_seeding_completed")
            else:
                scheduler.remove("stop_seeding_completed")

            downloader_manager.refresh()

        if section == "notify":
            notification_manager.refresh()

        if section == "auto_download":
            scheduler.jobs["auto_download"].interval = max(
                1,
                int(getattr(latest_setting.auto_download, "check_interval", 60) or 60),
            )
            if latest_setting.auto_download.enabled:
                scheduler.add("auto_download")
            else:
                scheduler.remove("auto_download")

        if section == "cookiecloud":
            if latest_setting.cookiecloud.enabled:
                scheduler.add("cookiecloud_sync")
                cookiecloud_service.sync()
            else:
                scheduler.remove("cookiecloud_sync")

        if section == "app":
            cookiecloud_service.push_javdb_cookie(latest_setting.app.javdb_cookie)
