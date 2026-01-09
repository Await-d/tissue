from pathlib import Path
from sqlalchemy import create_engine, QueuePool
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, User
from app.middleware.requestvars import g
from app.utils.security import get_password_hash

db_path = Path(f'{Path(__file__).cwd()}/config')
if not db_path.exists():
    db_path.mkdir()

engine = create_engine(f'sqlite:///{db_path}/app.db',
                       pool_pre_ping=True,
                       echo=False,
                       poolclass=QueuePool,
                       pool_size=1024,
                       pool_recycle=3600,
                       pool_timeout=180,
                       max_overflow=10,
                       connect_args={"timeout": 60},
                       )

SessionFactory = sessionmaker(bind=engine, autocommit=False)


# Dependency
def get_db():
    # 检查g()中是否已经有数据库会话
    if hasattr(g(), 'db'):
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
            if not hasattr(g(), 'transaction_started') or not g().transaction_started:
                try:
                    if hasattr(g(), 'db'):
                        delattr(g(), 'db')
                    # 安全地关闭会话
                    if db.is_active:
                        db.close()
                except Exception:
                    # 忽略关闭时的错误
                    pass


def init() -> None:
    with SessionFactory() as db:
        user = db.query(User).filter_by(username='admin').one_or_none()
        if not user:
            user = User()
            user.username = 'admin'
            user.password = get_password_hash("password")
            user.name = "管理员"
            user.is_admin = True
            db.add(user)
            db.commit()
