from sqlalchemy import Column, Integer, String, Boolean

from app.db.models.base import Base


class Torrent(Base):
    __tablename__ = 'torrent'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String(50), nullable=False)
    num = Column(String, nullable=False)
    is_zh = Column(Boolean, nullable=False, default=False)
    is_hd = Column(Boolean, nullable=False, default=False)
    is_uncensored = Column(Boolean, nullable=False, default=False)
