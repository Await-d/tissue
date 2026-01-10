"""
待处理种子数据模型
"""
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Enum as SQLEnum
from sqlalchemy.sql import func

from app.db.models.base import Base


class PendingTorrentStatus(str, Enum):
    """待处理种子状态枚举"""
    WAITING_METADATA = "waiting_metadata"  # 等待元数据
    METADATA_READY = "metadata_ready"      # 元数据已就绪
    FILTERING = "filtering"                # 正在过滤
    COMPLETED = "completed"                # 完成
    FAILED = "failed"                      # 失败
    TIMEOUT = "timeout"                    # 超时


class PendingTorrent(Base):
    """待处理种子模型"""
    __tablename__ = 'pending_torrent'

    id = Column(Integer, primary_key=True, autoincrement=True)
    torrent_hash = Column(String(64), unique=True, index=True, nullable=False, comment="种子哈希")
    magnet = Column(Text, nullable=True, comment="磁力链接")
    savepath = Column(String(500), nullable=True, comment="保存路径")
    category = Column(String(100), nullable=True, comment="分类")
    num = Column(String(50), nullable=True, comment="番号")
    source = Column(String(50), nullable=True, comment="来源: subscribe/auto_download/manual")
    status = Column(
        SQLEnum(PendingTorrentStatus),
        nullable=False,
        default=PendingTorrentStatus.WAITING_METADATA,
        comment="状态"
    )
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")
    max_retries = Column(Integer, nullable=False, default=30, comment="最大重试次数")
    filter_result = Column(Text, nullable=True, comment="过滤结果, JSON格式")
    error_message = Column(Text, nullable=True, comment="错误信息")
    added_at = Column(DateTime, nullable=False, server_default=func.now(), comment="添加时间")
    last_check_at = Column(DateTime, nullable=True, comment="最后检查时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    file_count = Column(Integer, nullable=True, comment="文件数量")
    total_size_bytes = Column(BigInteger, nullable=True, comment="总大小(字节)")
    filtered_file_count = Column(Integer, nullable=True, comment="过滤后文件数量")

    def __repr__(self):
        return f"<PendingTorrent(id={self.id}, hash={self.torrent_hash}, status={self.status.value})>"
