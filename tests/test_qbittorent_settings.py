from types import SimpleNamespace
from urllib.parse import urljoin

import requests

from app.utils import qbittorent as qbmod


class FakeResponse:
    def __init__(self, status_code: int, text: str = "", cookies=None, json_data=None):
        self.status_code = status_code
        self.text = text
        self.cookies = cookies or {}
        self._json_data = json_data

    def json(self):
        return self._json_data


class FakeSession:
    def __init__(self):
        self.post_urls = []
        self.get_urls = []

    def post(self, url, data=None, headers=None, timeout=None, **kwargs):
        self.post_urls.append(url)
        return FakeResponse(204, cookies={"QBT_SID_8996": "sid"})

    def get(self, url, timeout=None, **kwargs):
        self.get_urls.append(url)
        if url.endswith("/api/v2/app/version"):
            return FakeResponse(200, text="v5.2.2")
        return FakeResponse(200, json_data=[])


def download_setting(host: str, password: str):
    setting = SimpleNamespace(
        host=host,
        username="admin",
        password=password,
        tracker_subscribe="",
        savepath="",
        category="私自2",
    )
    setting.get_provider_payload = lambda provider: {}
    return setting


def patch_qb_dependencies(monkeypatch, settings):
    calls = SimpleNamespace(count=0)
    latest_setting = settings[-1]

    class FakeSetting:
        def __init__(self):
            if calls.count < len(settings):
                self.download = settings[calls.count]
            else:
                self.download = latest_setting
            calls.count += 1

    sessions = []

    def session_factory():
        session = FakeSession()
        sessions.append(session)
        return session

    monkeypatch.setattr(qbmod, "Setting", FakeSetting)
    monkeypatch.setattr(qbmod.requests, "Session", session_factory)
    return sessions


def test_connection_uses_latest_download_host(monkeypatch):
    sessions = patch_qb_dependencies(
        monkeypatch,
        [
            download_setting("http://old-qb:8996", "old-password"),
            download_setting("http://new-qb:8996", "new-password"),
        ],
    )

    qb = qbmod.QBittorent()

    result = qb.test_connection()

    assert result["status"] is True
    assert len(sessions) == 2
    assert sessions[-1].post_urls == [
        urljoin("http://new-qb:8996", "/api/v2/auth/login")
    ]


def test_connection_resets_session_when_password_changes(monkeypatch):
    sessions = patch_qb_dependencies(
        monkeypatch,
        [
            download_setting("http://same-qb:8996", "old-password"),
            download_setting("http://same-qb:8996", "new-password"),
        ],
    )

    qb = qbmod.QBittorent()

    result = qb.test_connection()

    assert result["status"] is True
    assert len(sessions) == 2


def test_connection_uses_fresh_session_for_repeated_checks(monkeypatch):
    sessions = patch_qb_dependencies(
        monkeypatch,
        [download_setting("http://same-qb:8996", "password")],
    )

    qb = qbmod.QBittorent()

    first_result = qb.test_connection()
    second_result = qb.test_connection()

    assert first_result["status"] is True
    assert second_result["status"] is True
    assert len(sessions) == 3
    assert sessions[1].post_urls == [
        urljoin("http://same-qb:8996", "/api/v2/auth/login")
    ]
    assert sessions[2].post_urls == [
        urljoin("http://same-qb:8996", "/api/v2/auth/login")
    ]
    assert sessions[1] is not sessions[2]


def test_authenticated_methods_use_latest_download_host(monkeypatch):
    sessions = patch_qb_dependencies(
        monkeypatch,
        [
            download_setting("http://old-qb:8996", "old-password"),
            download_setting("http://new-qb:8996", "new-password"),
        ],
    )

    qb = qbmod.QBittorent()

    response = qb.get_all_torrents()

    assert response.status_code == 200
    assert len(sessions) == 2
    assert sessions[-1].get_urls == [
        urljoin("http://new-qb:8996", "/api/v2/torrents/info")
    ]


def test_connection_reports_timeout_before_generic_connection_error(monkeypatch):
    class TimeoutSession:
        def post(self, url, data=None, headers=None, timeout=None, **kwargs):
            raise requests.exceptions.ConnectTimeout("connect timed out")

    class FakeSetting:
        def __init__(self):
            self.download = download_setting("http://slow-qb:8996", "password")

    monkeypatch.setattr(qbmod, "Setting", FakeSetting)
    monkeypatch.setattr(qbmod.requests, "Session", TimeoutSession)

    qb = qbmod.QBittorent()

    result = qb.test_connection()

    assert result == {"status": False, "message": "连接超时，请检查下载器是否在线"}
