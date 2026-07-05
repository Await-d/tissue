import json
from typing import Any

from sqlalchemy.exc import OperationalError

from app.db import SessionFactory
from app.db.models import SettingEntry
from app.schema.setting import (
    SettingApp,
    SettingAutoDownload,
    SettingCookieCloud,
    SettingDownload,
    SettingFile,
    SettingNotify,
    config_path,
)
from app.settings.migrations import NAMESPACE_ORDER, get_upgrade, latest_version
from app.utils.logger import logger


class SettingsManager:
    namespace_models = {
        "app": SettingApp,
        "file": SettingFile,
        "download": SettingDownload,
        "notify": SettingNotify,
        "auto_download": SettingAutoDownload,
        "cookiecloud": SettingCookieCloud,
    }

    def bootstrap(self) -> None:
        imported_from_ini = False
        with SessionFactory() as db:
            try:
                entries = db.query(SettingEntry).all()
            except OperationalError:
                logger.warning("settings 表尚未准备完成，跳过配置 bootstrap")
                return

            if not entries:
                imported_from_ini = self._seed_settings(db)
                entries = db.query(SettingEntry).all()

            existing_namespaces = {entry.namespace for entry in entries}
            for namespace in NAMESPACE_ORDER:
                if namespace in existing_namespaces:
                    continue
                self._upsert_namespace(
                    db=db,
                    namespace=namespace,
                    payload=self._default_payload(namespace),
                    version=latest_version(namespace),
                )

            for entry in db.query(SettingEntry).all():
                self._migrate_entry(db, entry)

            db.commit()

        if imported_from_ini and config_path.exists():
            config_path.unlink()
            logger.info("旧配置文件迁移成功，已删除 config/app.conf")

    def load(self) -> dict[str, Any]:
        payloads = {
            namespace: self._default_payload(namespace) for namespace in NAMESPACE_ORDER
        }
        with SessionFactory() as db:
            try:
                entries = db.query(SettingEntry).all()
            except OperationalError:
                return payloads

            for entry in entries:
                entry_namespace = str(getattr(entry, "namespace"))
                if entry_namespace not in self.namespace_models:
                    continue
                payloads[entry_namespace] = self._normalize_namespace_payload(
                    entry_namespace,
                    self._decode_payload(str(getattr(entry, "payload"))),
                )
        return payloads

    def save_section(self, section: str, payload: dict[str, Any]) -> None:
        with SessionFactory() as db:
            if section not in self.namespace_models:
                raise ValueError(f"不支持的配置分组: {section}")

            normalized = self._normalize_namespace_payload(section, payload)
            self._upsert_namespace(
                db=db,
                namespace=section,
                payload=normalized,
                version=latest_version(section),
            )
            db.commit()

    def _seed_settings(self, db: Any) -> bool:
        payloads = self._build_seed_payloads()
        for namespace, payload in payloads.items():
            self._upsert_namespace(db, namespace, payload, 1)
        return config_path.exists()

    def _build_seed_payloads(self) -> dict[str, dict[str, Any]]:
        from app.schema.setting import Setting

        if not config_path.exists():
            return {namespace: self._default_payload(namespace) for namespace in NAMESPACE_ORDER}

        legacy_sections = Setting.read_ini()
        return {
            "app": SettingApp(**legacy_sections.get("app", {})).model_dump(),
            "file": SettingFile(**legacy_sections.get("file", {})).model_dump(),
            "download": SettingDownload(**legacy_sections.get("download", {})).model_dump(),
            "notify": SettingNotify(**legacy_sections.get("notify", {})).model_dump(),
            "auto_download": SettingAutoDownload(**legacy_sections.get("auto_download", {})).model_dump(),
            "cookiecloud": SettingCookieCloud(**legacy_sections.get("cookiecloud", {})).model_dump(),
        }

    def _migrate_entry(self, db: Any, entry: Any) -> None:
        entry_namespace = str(getattr(entry, "namespace"))
        if entry_namespace not in self.namespace_models:
            return

        payload = self._decode_payload(str(getattr(entry, "payload")))
        version = int(getattr(entry, "version"))
        target_version = latest_version(entry_namespace)

        while version < target_version:
            upgrade = get_upgrade(entry_namespace, version)
            if upgrade is None:
                raise RuntimeError(
                    f"缺少配置迁移脚本: {entry_namespace} v{version} -> v{version + 1}",
                )
            payload = upgrade(payload)
            version += 1

        normalized = self._normalize_namespace_payload(entry_namespace, payload)
        entry.payload = self._encode_payload(normalized)
        entry.version = target_version
        db.add(entry)

    def _normalize_namespace_payload(
        self,
        namespace: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        model = self.namespace_models[namespace]
        return model(**payload).model_dump()

    def _default_payload(self, namespace: str) -> dict[str, Any]:
        model = self.namespace_models[namespace]
        return model().model_dump()

    @staticmethod
    def _decode_payload(payload: str) -> dict[str, Any]:
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _encode_payload(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    def _upsert_namespace(
        self,
        db: Any,
        namespace: str,
        payload: dict[str, Any],
        version: int,
    ) -> None:
        entry = db.query(SettingEntry).filter(SettingEntry.namespace == namespace).one_or_none()
        encoded = self._encode_payload(payload)
        if entry is None:
            entry = SettingEntry()
            new_entry: Any = entry
            new_entry.namespace = namespace
            new_entry.version = version
            new_entry.payload = encoded
            db.add(new_entry)
            return

        entry.payload = encoded
        entry.version = version
        db.add(entry)


settings_manager = SettingsManager()
