import os

import pytest

from app import utils
from app.schema.video import VideoActor, VideoDetail
from app.service.video import VideoService


@pytest.mark.parametrize(
    "raw",
    [
        "../../etc/passwd",
        "..\\..\\windows\\system32",
        "/absolute/path",
        "a/b",
        "..",
        ".",
        "",
        None,
        "   ",
    ],
)
def test_sanitize_path_component_never_yields_separators_or_traversal(raw):
    result = utils.sanitize_path_component(raw)
    assert "/" not in result
    assert "\\" not in result
    assert result not in (".", "..")
    assert result != ""


def test_sanitize_path_component_keeps_normal_text():
    assert utils.sanitize_path_component("正常演员") == "正常演员"
    assert utils.sanitize_path_component("A.B") == "A.B"
    assert utils.sanitize_path_component("A/B") == "A_B"


def test_sanitize_path_component_falls_back_for_blank():
    assert utils.sanitize_path_component(None) == "未知"
    assert utils.sanitize_path_component("..") == "未知"
    assert utils.sanitize_path_component(". .") == "未知"


def test_trans_keeps_files_inside_library_for_malicious_metadata(
    db_session, monkeypatch, tmp_path
):
    source = tmp_path / "src" / "input.mp4"
    source.parent.mkdir()
    source.write_bytes(b"video")

    library = tmp_path / "library"
    library.mkdir()

    nfo_temp = tmp_path / "temp.nfo"
    nfo_temp.write_text("<movie/>", encoding="utf-8")

    monkeypatch.setattr(
        "app.service.video.nfo.get_nfo_path_by_video", lambda _path: str(nfo_temp)
    )
    monkeypatch.setattr("app.service.video.nfo.save", lambda _path, _video: None)
    monkeypatch.setattr(
        "app.service.video.utils.remove_empty_directory", lambda _path: None
    )

    service = VideoService(db=db_session)
    video = VideoDetail(
        title="../../../../tmp/evil",
        num="../../evil",
        path=str(source),
        actors=[VideoActor(name="../../../../tmp/pwn", code="X")],
    )

    dest = service.trans(video, str(library), "copy")

    library_real = os.path.realpath(str(library))
    dest_real = os.path.realpath(dest)
    assert os.path.commonpath([library_real, dest_real]) == library_real

    rel_parts = os.path.relpath(dest_real, library_real).split(os.sep)
    assert all(part not in (".", "..") for part in rel_parts)
    assert os.path.exists(dest)


def test_trans_allows_symlinked_actor_folder(db_session, monkeypatch, tmp_path):
    source = tmp_path / "src" / "input.mp4"
    source.parent.mkdir()
    source.write_bytes(b"video")

    library = tmp_path / "library"
    library.mkdir()
    external = tmp_path / "external"
    external.mkdir()

    link = library / "ActorX"
    try:
        link.symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("symlink not supported on this platform")

    nfo_temp = tmp_path / "temp.nfo"
    nfo_temp.write_text("<movie/>", encoding="utf-8")
    monkeypatch.setattr(
        "app.service.video.nfo.get_nfo_path_by_video", lambda _path: str(nfo_temp)
    )
    monkeypatch.setattr("app.service.video.nfo.save", lambda _path, _video: None)
    monkeypatch.setattr(
        "app.service.video.utils.remove_empty_directory", lambda _path: None
    )

    service = VideoService(db=db_session)
    video = VideoDetail(
        title="Title",
        num="NUM-1",
        path=str(source),
        actors=[VideoActor(name="ActorX", code="X")],
    )

    dest = service.trans(video, str(library), "copy")

    assert os.path.exists(dest)
    assert os.path.realpath(dest).startswith(os.path.realpath(str(external)) + os.sep)
