from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_user
from app.db.base import get_db
from app.models import User
from app.schemas import CreateReviewReq, UpdateReviewReq
from app import services

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("")
def list_public_reviews(keyword: Optional[str] = None,
                        page: Optional[int] = None,
                        page_size: Optional[int] = None,
                        db: Session = Depends(get_db)):
    """全部公开评测列表（首页「游戏评测」专区）：发布时间倒序，keyword 按游戏名称过滤。"""
    return services.list_public_reviews(db, keyword=keyword,
                                        page=page, page_size=page_size)


@router.get("/me/likes")
def my_liked_reviews(user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    """我点赞过的评测列表（个人中心「评测互动」）；需置于 /{review_id} 之前。"""
    return services.my_review_likes(db, user)


@router.get("/me/favorites")
def my_favorited_reviews(user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    """我收藏的评测列表（个人中心「评测互动」）。"""
    return services.my_review_favs(db, user)


@router.get("/mine")
def my_reviews(status: Optional[str] = None,
               page: Optional[int] = None,
               page_size: Optional[int] = None,
               user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """我发布的全部评测（个人中心「我的评测」，含未过审内容；需置于 /{review_id} 之前）。
    status 可按 published/rejected/draft/audit/manual_review 过滤，分页。"""
    return services.my_reviews(db, user, status=status, page=page, page_size=page_size)


@router.get("/{review_id}")
def get_review(review_id: int,
               user: Optional[User] = Depends(get_optional_user),
               db: Session = Depends(get_db)):
    """单篇公开评测攻略完整详情（阅读量 +1）。登录时返回我的点赞/收藏状态。"""
    return services.get_review_detail(db, review_id, viewer=user)


@router.get("/{review_id}/comments")
def list_review_comments(review_id: int,
                         user: Optional[User] = Depends(get_optional_user),
                         db: Session = Depends(get_db)):
    """该评测攻略下的专属评论区（comments 表 target_type="review"）。"""
    return services.list_comments(db, user, "review", review_id)


@router.post("")
def create_review(body: CreateReviewReq,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return services.create_review(db, user, body)


@router.put("/{review_id}")
def update_review(review_id: int,
                  body: UpdateReviewReq,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return services.update_review(db, user, review_id, body)


@router.delete("/{review_id}")
def delete_review(review_id: int,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return services.delete_review(db, user, review_id)


@router.post("/{review_id}/submit-audit")
async def submit_audit(review_id: int,
                       user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    return await services.submit_audit(db, user, review_id)


@router.post("/{review_id}/like")
def like_review(review_id: int,
                user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """点赞/取消点赞评测（幂等切换）；作者获 0.2 积分/赞。"""
    return services.toggle_review_like(db, user, review_id)


@router.post("/{review_id}/favorite")
def favorite_review(review_id: int,
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """收藏/取消收藏评测（幂等切换）；作者获 0.5 积分/收藏。"""
    return services.toggle_review_fav(db, user, review_id)
