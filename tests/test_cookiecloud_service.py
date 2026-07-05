from types import SimpleNamespace

from app.service.cookiecloud import CookieCloudService


def test_cookiecloud_sync_updates_javdb_cookie(monkeypatch):
    saved_sections: list[tuple[str, dict]] = []

    monkeypatch.setattr(
        "app.settings.settings_manager.load",
        lambda: {
            "app": {"javdb_cookie": None},
            "cookiecloud": {
                "enabled": True,
                "host": "https://cookiecloud.example.com",
                "uuid": "uuid",
                "password": "password",
            },
        },
    )
    monkeypatch.setattr(
        "app.settings.settings_manager.save_section",
        lambda section, payload: saved_sections.append((section, payload)),
    )
    monkeypatch.setattr(
        CookieCloudService,
        "_validate_javdb_cookie",
        staticmethod(lambda cookie_header: cookie_header.startswith("_jdb_session=")),
    )

    class FakeClient:
        def get_decrypted_data(self):
            return {
                "javdb.com": [
                    {"name": "_jdb_session", "value": "session-token", "domain": "javdb.com", "path": "/"},
                    {"name": "remember_me_token", "value": "remember-token", "domain": "javdb.com", "path": "/"},
                ],
            }

    monkeypatch.setattr(
        CookieCloudService,
        "_create_client",
        lambda self, setting: FakeClient(),
    )

    synced = CookieCloudService().sync()

    assert synced is True
    assert saved_sections == [
        (
            "app",
            {"javdb_cookie": "_jdb_session=session-token; remember_me_token=remember-token"},
        ),
    ]


def test_cookiecloud_push_updates_remote_payload(monkeypatch):
    updated_payloads: list[dict] = []

    monkeypatch.setattr(
        "app.settings.settings_manager.load",
        lambda: {
            "cookiecloud": {
                "enabled": True,
                "host": "https://cookiecloud.example.com",
                "uuid": "uuid",
                "password": "password",
            },
        },
    )

    class FakeClient:
        def __init__(self):
            self.payload = {"other.com": [{"name": "a", "value": "1"}]}

        def get_decrypted_data(self):
            return dict(self.payload)

        def update_cookie(self, payload):
            updated_payloads.append(payload)
            return True

    monkeypatch.setattr(
        CookieCloudService,
        "_create_client",
        lambda self, setting: FakeClient(),
    )

    pushed = CookieCloudService().push_javdb_cookie("_jdb_session=session-token; remember_me_token=remember-token")

    assert pushed is True
    assert updated_payloads[0]["other.com"] == [{"name": "a", "value": "1"}]
    assert updated_payloads[0]["javdb.com"][0]["name"] == "_jdb_session"


def test_db_init_creates_metadata_before_bootstrap(monkeypatch):
    create_all_called: list[bool] = []
    table_create_called: list[bool] = []
    bootstrap_called: list[bool] = []

    class FakeQuery:
        def filter_by(self, **kwargs):
            return self

        def one_or_none(self):
            return SimpleNamespace(username="admin")

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def query(self, model):
            return FakeQuery()

    class FakeTable:
        def create(self, engine, checkfirst=True):
            table_create_called.append(checkfirst)

    monkeypatch.setattr("app.db.Base.metadata.create_all", lambda engine, checkfirst=True: create_all_called.append(checkfirst))
    monkeypatch.setattr("app.db.SettingEntry.__table__", FakeTable())
    monkeypatch.setattr("app.db.SessionFactory", lambda: FakeSession())
    monkeypatch.setattr("app.settings.settings_manager.bootstrap", lambda: bootstrap_called.append(True))

    from app import db

    db.init()

    assert create_all_called == [True]
    assert table_create_called == [True]
    assert bootstrap_called == [True]
