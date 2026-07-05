import re
from urllib.parse import urlencode, urljoin, urlparse


URI_ATTRIBUTE_PATTERN = re.compile(r'URI="([^"]+)"')
URI_ATTRIBUTE_TAGS = (
    "#EXT-X-KEY",
    "#EXT-X-MAP",
    "#EXT-X-I-FRAME-STREAM-INF",
    "#EXT-X-MEDIA",
)


def _build_proxy_url(resource_url: str, base_path: str, proxy_path: str, base_url: str) -> str:
    absolute_url = urljoin(base_path, resource_url) if not resource_url.startswith("http") else resource_url
    return f"{proxy_path}?{urlencode({'url': absolute_url, 'base_url': base_url})}"


def _rewrite_uri_attribute_line(line: str, base_path: str, proxy_path: str, base_url: str) -> str:
    if not line.startswith(URI_ATTRIBUTE_TAGS):
        return line

    def replace_uri(match: re.Match[str]) -> str:
        proxied_url = _build_proxy_url(match.group(1), base_path, proxy_path, base_url)
        return f'URI="{proxied_url}"'

    return URI_ATTRIBUTE_PATTERN.sub(replace_uri, line, count=1)


def fix_m3u8_paths(m3u8_content: str, video_url: str, base_url: str) -> str:
    parsed = urlparse(video_url)
    base_path = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"
    proxy_path = urljoin(base_url + "/", "common/trailer")

    fixed_lines: list[str] = []
    for line in m3u8_content.splitlines():
        if line.startswith("#"):
            line = _rewrite_uri_attribute_line(line, base_path, proxy_path, base_url)
        elif line:
            line = _build_proxy_url(line, base_path, proxy_path, base_url)
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


def is_m3u8(url: str, content_type: str | None = None) -> bool:
    parsed = urlparse(url)
    if parsed.path.lower().endswith(".m3u8"):
        return True
    if content_type and "mpegurl" in content_type.lower():
        return True
    return False
