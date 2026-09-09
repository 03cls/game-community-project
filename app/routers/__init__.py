"""路由聚合：所有 router 在此汇总，供 main.py include。"""
from __future__ import annotations

from .admin import router as admin_router
from .ai import router as ai_router
from .auth import router as auth_router
from .comments import router as comments_router
from .community import router as community_router
from .creator import router as creator_router
from .favorites import router as favorites_router
from .games import router as games_router
from .notifications import router as notifications_router
from .play_records import router as play_records_router
from .reviews import router as reviews_router
from .users import router as users_router

__all__ = [
    "admin_router",
    "ai_router",
    "auth_router",
    "comments_router",
    "community_router",
    "creator_router",
    "favorites_router",
    "games_router",
    "notifications_router",
    "play_records_router",
    "reviews_router",
    "users_router",
]
