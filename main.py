"""AI 游戏社区评测分享平台 — 应用入口。

启动：set SQLALCHEMY_SILENCE_UBER_WARNING=1
     uvicorn main:app --port 8000
"""
from __future__ import annotations

# 必须在导入 SQLAlchemy 之前设置，沉默 1.4 的 2.0 迁移 uber warning
import os

os.environ.setdefault("SQLALCHEMY_SILENCE_UBER_WARNING", "1")

import os.path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.init_db import init_db, seed_if_empty
from app.routers import (
    admin_router,
    ai_router,
    auth_router,
    comments_router,
    community_router,
    creator_router,
    favorites_router,
    games_router,
    notifications_router,
    play_records_router,
    reviews_router,
    users_router,
)

app = FastAPI(
    title="AI 游戏社区评测分享平台",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()
    seed_if_empty()


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(games_router)
app.include_router(favorites_router)
app.include_router(play_records_router)
app.include_router(comments_router)
app.include_router(reviews_router)
app.include_router(community_router)
app.include_router(creator_router)
app.include_router(ai_router)
app.include_router(notifications_router)
app.include_router(admin_router)

# 挂载静态资源（前端）
_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")
