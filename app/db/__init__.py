import secrets
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, QueuePool, event
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, SettingEntry, User
from app.middleware.requestvars import g
from app.utils.security import get_password_hash
from app.utils.logger import logger

db_path = Path(f"{Path(__file__).cwd()}/config")
if not db_path.exists():
    db_path.mkdir()

engine = create_engine(
    f"sqlite:///{db_path}/app.db",
    pool_pre_ping=True,
    echo=False,
    poolclass=QueuePool,
    pool_size=5,
    pool_recycle=3600,
    pool_timeout=30,
    max_overflow=5,
    connect_args={"timeout": 60, "check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    对每个新连接设置 SQLite 优化参数：
    - WAL 模式：允许并发读取，显著减少读写争用
    - synchronous=NORMAL：WAL 模式下更安全的性能模式
    - busy_timeout=30000：SQLite 层级 30s 超时（补充 engine timeout）
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


SessionFactory = sessionmaker(bind=engine, autocommit=False)


# Dependency
def get_db():
    # 检查g()中是否已经有数据库会话
    if hasattr(g(), "db"):
        # 如果已经有会话，直接返回它
        yield g().db
    else:
        # 如果没有会话，创建一个新的
        db = SessionFactory()
        g().db = db
        try:
            yield db
        finally:
            # 只有当没有活跃的事务时才关闭会话
            if not hasattr(g(), "transaction_started") or not g().transaction_started:
                try:
                    if hasattr(g(), "db"):
                        delattr(g(), "db")
                    # 安全地关闭会话
                    if db.is_active:
                        db.close()
                except Exception:
                    # 忽略关闭时的错误
                    pass


def init() -> None:
    base_metadata: Any = getattr(Base, "metadata")
    base_metadata.create_all(engine, checkfirst=True)
    setting_entry_table: Any = getattr(SettingEntry, "__table__")
    setting_entry_table.create(engine, checkfirst=True)
    with SessionFactory() as db:
        user = db.query(User).filter_by(username="admin").one_or_none()
        if not user:
            initial_password = secrets.token_urlsafe(12)
            user = User()
            new_user: Any = user
            new_user.username = "admin"
            new_user.password = get_password_hash(initial_password)
            new_user.name = "管理员"
            new_user.is_admin = True
            db.add(new_user)
            db.commit()
            logger.warning(
                f"检测到系统首次初始化，已创建管理员账号 admin，初始密码为【{initial_password}】。请登录后立即修改密码。",
            )

    from app.settings import settings_manager

    settings_manager.bootstrap()
