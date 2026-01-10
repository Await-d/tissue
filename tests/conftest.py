"""
测试配置文件 - 共享的 fixtures 和配置

解决 "table already exists" 错误的关键点：
1. 每次测试使用独立的内存数据库
2. 测试后正确清理数据库连接
3. 使用 drop_all 确保表被清理
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models.base import Base


@pytest.fixture(scope='function')
def db_session() -> Session:
    """
    为每个测试函数创建独立的数据库会话

    scope='function' 确保每个测试都有独立的数据库
    这样可以避免 "table already exists" 错误
    """
    # 使用内存数据库，每次测试都是全新的
    engine = create_engine(
        'sqlite:///:memory:',
        echo=False,  # 设置为 True 可以看到 SQL 语句
        connect_args={'check_same_thread': False}  # SQLite 特定配置
    )

    # 创建所有表
    Base.metadata.create_all(engine)

    # 创建会话
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    session = SessionLocal()

    try:
        yield session
    finally:
        # 测试结束后清理
        session.close()
        # 删除所有表，确保下次测试时干净的环境
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope='session')
def shared_db_engine():
    """
    会话级别的数据库引擎（可选）

    如果需要在多个测试间共享数据库，使用此 fixture
    但要注意手动清理测试数据
    """
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope='function')
def db_session_from_shared_engine(shared_db_engine):
    """
    使用共享引擎创建会话

    这种方式可以提高测试速度，但需要手动清理数据
    """
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=shared_db_engine
    )
    session = SessionLocal()

    try:
        yield session
        # 回滚事务，清理测试数据
        session.rollback()
    finally:
        session.close()
