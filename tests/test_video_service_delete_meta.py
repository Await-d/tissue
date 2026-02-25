from types import SimpleNamespace

from app.service.video import VideoService


def test_delete_video_meta_skips_none_image_fields(db_session, monkeypatch):
    service = VideoService(db=db_session)

    monkeypatch.setattr(
        "app.service.video.nfo.get_nfo_path_by_video", lambda _path: "/tmp/video.nfo"
    )
    monkeypatch.setattr(
        "app.service.video.nfo.get_full",
        lambda _path: SimpleNamespace(poster=None, thumb="thumb.jpg", fanart=None),
    )

    removed_paths = []

    def fake_exists(path):
        return path in {"/tmp/video.nfo", "/tmp/movie.nfo", "/tmp/thumb.jpg"}

    def fake_remove(path):
        removed_paths.append(path)

    monkeypatch.setattr("app.service.video.os.path.exists", fake_exists)
    monkeypatch.setattr("app.service.video.os.remove", fake_remove)

    service.delete_video_meta("/tmp/video.mp4")

    assert removed_paths == ["/tmp/video.nfo", "/tmp/movie.nfo", "/tmp/thumb.jpg"]
