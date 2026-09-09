"""pytest 全局 fixture：SQLite 内存库 + TestClient + 角色 token。

关键策略：
1. 在 import app/* 之前注入环境变量（DATABASE_URL=内存库、关闭 DeepSeek 走 Mock）。
2. 用 StaticPool 让内存库在多线程下共享同一连接（否则每个连接看到空库）。
3. patch app.db.base 的 engine / SessionLocal 指向测试 engine —— 这样
   init_db.py 在 main.py import 时通过 `from app.db.base import engine, SessionLocal`
   拿到的就是 patched 版本，startup 时 init_db()/seed_if_empty() 操作内存库。
4. patch hash_password 用 rounds=4 加速种子用户哈希（不影响 verify 逻辑）。
5. 每个测试函数级 client fixture：drop+create 全新表，再触发 startup 重新 seed。
"""
from __future__ import annotations

import os

# ---- 1) 在 import app 之前设置环境变量 ----
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
os.environ["DEEPSEEK_API_KEY"] = ""  # 强制 AI 走 Mock 规则兜底
os.environ.setdefault("JWT_SECRET_KEY", "game-community-dev-secret-change-me")

# ---- 2) 用快速 bcrypt rounds 加速种子数据 ----
import bcrypt


def _fast_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72],
                         bcrypt.gensalt(rounds=4)).decode("utf-8")


import app.core.security as _sec
_sec.hash_password = _fast_hash

# ---- 3) patch app.db.base 的 engine / SessionLocal ----
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.base as _base

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=False,
)


@event.listens_for(test_engine, "connect")
def _enable_sqlite_fk(dbapi_conn, _):
    try:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()
    except Exception:
        pass


_base.engine = test_engine
_base.SessionLocal = sessionmaker(autocommit=False, autoflush=False,
                                  bind=test_engine)

# ---- 4) 此时导入 main，init_db 拿到的就是 patched engine/hash_password ----
import pytest
from fastapi.testclient import TestClient

import main as _main
from app.db.base import Base


@pytest.fixture
def client():
    """每个测试一个全新 DB：drop → create → TestClient context 触发 startup(init+seed)。"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    with TestClient(_main.app) as c:
        yield c
    # 清理：drop_all 防止表残留（下一轮 fixture 会再 drop+create）


@pytest.fixture
def db():
    """直接拿 SessionLocal 用于断言/造数据。"""
    s = _base.SessionLocal()
    try:
        yield s
    finally:
        s.close()


# ---- token / headers 辅助 ----
def _login(client, username, password):
    r = client.post("/api/auth/login",
                    json={"username_or_email": username, "password": password})
    assert r.status_code == 200, f"login {username} failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def admin_token(client):
    return _login(client, "admin", "admin123")


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def creator_token(client):
    return _login(client, "creator", "creator123")


@pytest.fixture
def creator_headers(creator_token):
    return {"Authorization": f"Bearer {creator_token}"}


@pytest.fixture
def player_token(client):
    return _login(client, "player", "player123")


@pytest.fixture
def player_headers(player_token):
    return {"Authorization": f"Bearer {player_token}"}
