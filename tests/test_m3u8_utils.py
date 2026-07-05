from app.utils.m3u8 import fix_m3u8_paths, is_m3u8


def test_fix_m3u8_paths_rewrites_segments_and_uri_attributes():
    content = (
        "#EXTM3U\n"
        "#EXT-X-VERSION:3\n"
        "#EXT-X-KEY:METHOD=AES-128,URI=\"enc.key\"\n"
        "#EXTINF:5.000,\n"
        "segment-1.ts\n"
    )

    result = fix_m3u8_paths(
        content,
        "https://cdn.example.com/video/master.m3u8",
        "https://api.example.com",
    )

    assert "https://api.example.com/common/trailer?url=https%3A%2F%2Fcdn.example.com%2Fvideo%2Fenc.key" in result
    assert "https://api.example.com/common/trailer?url=https%3A%2F%2Fcdn.example.com%2Fvideo%2Fsegment-1.ts" in result


def test_is_m3u8_detects_by_extension_or_content_type():
    assert is_m3u8("https://cdn.example.com/master.m3u8") is True
    assert is_m3u8("https://cdn.example.com/master", "application/vnd.apple.mpegurl") is True
    assert is_m3u8("https://cdn.example.com/master.mp4", "video/mp4") is False
