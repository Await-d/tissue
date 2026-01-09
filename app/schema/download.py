from typing import List, Optional

from pydantic import BaseModel


class TorrentFile(BaseModel):
    name: str
    size: str
    path: str
    progress: float = 1.0  # 默认为1.0表示完成
    num: Optional[str] = None  # 视频番号，用于跳转到详细页面
    actors: Optional[List[str]] = None  # 演员列表，用于跳转到演员页面


class Torrent(BaseModel):
    hash: str
    name: str
    size: str
    path: str
    tags: List[str]
    files: List[TorrentFile] = []
