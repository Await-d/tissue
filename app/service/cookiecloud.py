from typing import Any
from importlib import import_module
from urllib.parse import urljoin

from app.schema import Setting
from app.settings import settings_manager
from app.utils.cookies import (
    cookiecloud_items_to_cookies,
    cookies_to_cookiecloud_items,
    parse_cookie_header,
    to_cookie_header,
)
from app.utils.logger import logger
from app.utils.spider.javdb import JavdbSpider

class CookieCloudService:
    def sync(self) -> bool:
        setting = Setting().cookiecloud
        if not setting.enabled:
            return False

        client = self._create_client(setting)
        if client is None:
            return False

        try:
            decrypted_data = client.get_decrypted_data()
        except Exception as exc:
            logger.error(f"CookieCloud 同步失败: {exc}")
            return False

        if not decrypted_data:
            logger.warning("CookieCloud 返回数据为空")
            return False

        matched_entries = self._find_matching_javdb_entries(decrypted_data)
        if not matched_entries:
            logger.info("CookieCloud 中未找到 JavDB 相关 Cookie")
            return False

        cookie_header = to_cookie_header(cookiecloud_items_to_cookies(matched_entries))
        if not cookie_header:
            return False

        if not self._validate_javdb_cookie(cookie_header):
            logger.warning("CookieCloud 中的 JavDB Cookie 无效，跳过写入")
            return False

        self._save_javdb_cookie(cookie_header)
        logger.info("CookieCloud 已同步 JavDB Cookie 到应用设置")
        return True

    def push_javdb_cookie(self, cookie_header: str | None) -> bool:
        setting = Setting().cookiecloud
        if not setting.enabled:
            return False

        client = self._create_client(setting)
        if client is None:
            return False

        try:
            decrypted_data = client.get_decrypted_data() or {}
            if not cookie_header:
                self._remove_cookie_domains(decrypted_data)
            else:
                decrypted_data["javdb.com"] = cookies_to_cookiecloud_items(
                    parse_cookie_header(cookie_header),
                )

            if client.update_cookie(decrypted_data):
                logger.info("应用中的 JavDB Cookie 已推送到 CookieCloud")
                return True
        except Exception as exc:
            logger.error(f"CookieCloud 推送失败: {exc}")

        return False

    def _create_client(self, setting: Any):
        try:
            pycookiecloud_cls = import_module("PyCookieCloud").PyCookieCloud
        except ImportError:
            logger.warning("PyCookieCloud 未安装，CookieCloud 功能不可用")
            return None
        if not setting.host or not setting.uuid or not setting.password:
            logger.warning("CookieCloud 配置不完整")
            return None
        return pycookiecloud_cls(setting.host, setting.uuid, setting.password)

    @staticmethod
    def _find_matching_javdb_entries(cookie_dict: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        matched: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()
        for domain, cookies in cookie_dict.items():
            normalized = domain.lower().lstrip(".")
            if "javdb" not in normalized:
                continue
            for item in cookies:
                key = (
                    str(item.get("name", "")),
                    str(item.get("value", "")),
                    str(item.get("domain", "") or domain),
                    str(item.get("path", "") or "/"),
                )
                if key in seen:
                    continue
                seen.add(key)
                matched.append(item)
        return matched

    @staticmethod
    def _remove_cookie_domains(cookie_dict: dict[str, list[dict[str, Any]]]) -> None:
        keys_to_remove = [domain for domain in cookie_dict.keys() if "javdb" in domain.lower()]
        for domain in keys_to_remove:
            del cookie_dict[domain]

    @staticmethod
    def _save_javdb_cookie(cookie_header: str) -> None:
        settings_payload = Setting.read()
        app_payload = dict(settings_payload.get("app", {}))
        app_payload["javdb_cookie"] = cookie_header
        settings_manager.save_section("app", app_payload)

    @staticmethod
    def _validate_javdb_cookie(cookie_header: str) -> bool:
        spider = JavdbSpider()
        spider.session.cookies.clear()
        spider._set_age_cookies()
        cookie_domain = spider._cookie_domain()
        for cookie in parse_cookie_header(cookie_header):
            spider.session.cookies.set(
                cookie.name,
                cookie.value,
                domain=cookie.domain or cookie_domain,
                path=cookie.path,
            )

        try:
            response = spider.session.get(urljoin(spider.host, "/users"))
            if response.status_code != 200:
                return False
            return "/login" not in str(response.url).lower()
        except Exception as exc:
            logger.warning(f"校验 JavDB Cookie 时出错: {exc}")
            return False


cookiecloud_service = CookieCloudService()
