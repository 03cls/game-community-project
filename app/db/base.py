"""数据库会话与 Base。

开发默认 SQLite（零配置），生产可通过 .env 切换 MySQL。
SQLite 需开启外键约束。
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# SQLite 需要多线程访问（FastAPI 跑在多线程中执行同步路由）
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# SQLite 默认不强制外键约束，这里显式开启
@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_conn, _):  # pragma: no cover - 仅 SQLite 生效
    try:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass


def get_db():
    """FastAPI 依赖：提供数据库会话并在请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
