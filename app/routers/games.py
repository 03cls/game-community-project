from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_user
from app.db.base import get_db
from app.models import User
from app.schemas import GameCommentCreate, GameRatingReq
from app import services

router = APIRouter(prefix="/api/games", tags=["games"])


@router.get("")
def list_games(
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    sort: str = "hot",
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    return services.list_games(
        db, user, category_id=category_id, keyword=keyword, sort=sort,
        page=page, page_size=page_size,
    )


@router.get("/{game_id}")
def get_game(game_id: int,
             user: Optional[User] = Depends(get_optional_user),
             db: Session = Depends(get_db)):
    return services.get_game(db, user, game_id)


@router.get("/{game_id}/similar")
def similar_games(game_id: int, db: Session = Depends(get_db)):
    """相似游戏推荐：依据分类与标签返回 3-4 款。"""
    return services.list_similar_games(db, game_id)


@router.get("/{game_id}/reviews/count")
def game_reviews_count(game_id: int, db: Session = Depends(get_db)):
    """该游戏公开评测攻略总数（用于详情页按钮展示 N）。"""
    return services.game_reviews_count(db, game_id)


@router.get("/{game_id}/reviews")
def list_game_reviews(game_id: int, page: Optional[int] = None,
                      page_size: Optional[int] = None,
                      keyword: Optional[str] = None,
                      db: Session = Depends(get_db)):
    # mock.js 契约：游戏评测列表默认每页 5 条；keyword 按标题/正文过滤本游戏评测
    return services.list_game_reviews(db, game_id, page=page,
                                      page_size=page_size or 5, keyword=keyword)


@router.get("/{game_id}/comments")
def list_game_comments(game_id: int, page: Optional[int] = None,
                       page_size: Optional[int] = None,
                       user: Optional[User] = Depends(get_optional_user),
                       db: Session = Depends(get_db)):
    """游戏评论区：精选评论置顶 + 普通评论分页。"""
    return services.list_game_comments(db, user, game_id, page=page, page_size=page_size)


@router.post("/{game_id}/comments")
def create_game_comment(game_id: int, body: GameCommentCreate,
                        user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """登录玩家发表游戏短评论。"""
    return services.create_game_comment(db, user, game_id, body)


@router.post("/{game_id}/rating")
def submit_game_rating(game_id: int, body: GameRatingReq,
                       user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """登录用户对游戏提交 1-10 分评分；同一用户仅一条记录，重复提交=修改分数。"""
    return services.submit_game_rating(db, user, game_id, body)
