"""
扫描记录数据模型 - 存储文件扫描历史记录
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from app.db.models.base import Base


class ScanRecord(Base):
    """扫描记录表 - 记录每次文件扫描的结果"""
    __tablename__ = 'scan_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 扫描基本信息
    scan_time = Column(DateTime, nullable=False, default=datetime.now, comment='扫描时间')
    total_files = Column(Integer, nullable=False, default=0, comment='扫描文件总数')
    new_found = Column(Integer, nullable=False, default=0, comment='新发现视频数')
    already_exists = Column(Integer, nullable=False, default=0, comment='已存在视频数')
    scan_duration = Column(Float, nullable=False, default=0.0, comment='扫描耗时(秒)')

    # 扫描状态
    status = Column(String(20), nullable=False, default='success', comment='扫描状态: success/failed')
    error_message = Column(Text, nullable=True, comment='错误信息')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 创建索引优化查询性能
    __table_args__ = (
        Index('idx_scan_time', 'scan_time'),  # 扫描时间索引
        Index('idx_status', 'status'),  # 状态索引
        Index('idx_created_at', 'created_at'),  # 创建时间索引
        {'comment': '扫描记录表 - 存储文件扫描历史记录'}
    )

    def __repr__(self):
        return f"<ScanRecord(id={self.id}, scan_time='{self.scan_time}', status='{self.status}', new_found={self.new_found})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'scan_time': self.scan_time.isoformat() if self.scan_time else None,
            'total_files': self.total_files,
            'new_found': self.new_found,
            'already_exists': self.already_exists,
            'scan_duration': self.scan_duration,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
