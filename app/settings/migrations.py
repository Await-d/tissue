from collections.abc import Callable


UpgradeFunc = Callable[[dict], dict]

NAMESPACE_ORDER = (
    "app",
    "file",
    "download",
    "notify",
    "auto_download",
    "cookiecloud",
)

LATEST_VERSIONS: dict[str, int] = {
    namespace: 1 for namespace in NAMESPACE_ORDER
}

MIGRATIONS: dict[str, dict[int, UpgradeFunc]] = {
    namespace: {} for namespace in NAMESPACE_ORDER
}


def latest_version(namespace: str) -> int:
    return LATEST_VERSIONS[namespace]


def get_upgrade(namespace: str, version: int) -> UpgradeFunc | None:
    return MIGRATIONS.get(namespace, {}).get(version)
