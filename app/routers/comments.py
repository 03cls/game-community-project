from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_user
from app.db.base import get_db
from app.models import User
from app.schemas import CreateCommentReq
from app import services

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("")
def list_comments(target_type: str = "review",
                  target_id: int = 0,
                  user: Optional[User] = Depends(get_optional_user),
                  db: Session = Depends(get_db)):
    return services.list_comments(db, user, target_type, target_id)


@router.post("")
def create_comment(body: CreateCommentReq,
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return services.create_comment(db, user, body)


@router.get("/mine")
def my_comments(page: Optional[int] = None,
                page_size: Optional[int] = None,
                user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """我发表的全部评论（游戏短评论 + 评测攻略评论，分页）。"""
    return services.my_comments(db, user, page=page, page_size=page_size)


@router.post("/{comment_id}/like")
def like_comment(comment_id: int,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return services.toggle_like(db, user, comment_id)


@router.delete("/{comment_id}")
def delete_comment(comment_id: int,
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """删除自己的评论（含楼中楼回复）。只能删除自己发表的评论。"""
    return services.delete_comment(db, user, comment_id)
