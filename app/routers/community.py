"""社区模块路由：帖子 / 评论（楼中楼）/ 点赞 / 收藏 / 举报 / 图片上传。"""
from __future__ import annotations

import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_user
from app.db.base import get_db
from app.models import User
from app.schemas import (
    CommunityPostCommentReq,
    CommunityPostCreateReq,
    ReportCreateReq,
)
from app import services

router = APIRouter(prefix="/api/community", tags=["community"])

ALLOWED_IMAGE_EXT = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                     ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("/tags")
def tags():
    """社区标签选项（游戏/闲聊/攻略/吐槽）。"""
    return services.community_tags()


@router.get("/posts")
def list_posts(sort: str = "hot", tag: Optional[str] = None,
               keyword: Optional[str] = None, page: Optional[int] = None,
               page_size: Optional[int] = None,
               user: Optional[User] = Depends(get_optional_user),
               db: Session = Depends(get_db)):
    """帖子列表：推荐(热度)/最新(时间)，标签与关键词筛选。"""
    return services.community_list_posts(
        db, user, sort=sort, tag=tag, keyword=keyword, page=page, page_size=page_size)


@router.post("/posts")
def create_post(body: CommunityPostCreateReq,
                user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """全员可发帖，发布即公开（发布前过内容风控）。"""
    return services.community_create_post(db, user, body)


@router.get("/posts/{post_id}")
def post_detail(post_id: int,
                user: Optional[User] = Depends(get_optional_user),
                db: Session = Depends(get_db)):
    """帖子详情（浏览量 +1）。"""
    return services.community_post_detail(db, user, post_id)


@router.delete("/posts/{post_id}")
def delete_post(post_id: int,
                user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """作者删自己的帖；管理员可删任意帖。"""
    return services.community_delete_post(db, user, post_id)


@router.post("/posts/{post_id}/like")
def like_post(post_id: int,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    """点赞/取消点赞（幂等切换）。"""
    return services.community_toggle_like(db, user, post_id)


@router.post("/posts/{post_id}/favorite")
def favorite_post(post_id: int,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """收藏/取消收藏（幂等切换）。"""
    return services.community_toggle_favorite(db, user, post_id)


@router.get("/posts/{post_id}/comments")
def list_comments(post_id: int,
                  user: Optional[User] = Depends(get_optional_user),
                  db: Session = Depends(get_db)):
    """评论区：一级评论 + 楼中楼回复树。"""
    return services.community_list_comments(db, user, post_id)


@router.post("/posts/{post_id}/comments")
def create_comment(post_id: int, body: CommunityPostCommentReq,
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """发表评论/回复（过内容风控 + 频率限制）。"""
    return services.community_create_comment(db, user, post_id, body)


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int,
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """评论作者、帖子作者、管理员可删。"""
    return services.community_delete_comment(db, user, comment_id)


@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: int,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """评论点赞/取消点赞。"""
    return services.community_toggle_comment_like(db, user, comment_id)


@router.post("/reports")
def create_report(body: ReportCreateReq,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """举报帖子/评论。"""
    return services.community_create_report(db, user, body)


@router.get("/users/{user_id}/posts")
def user_posts(user_id: int, tab: str = "posts",
               page: Optional[int] = None, page_size: Optional[int] = None,
               viewer: Optional[User] = Depends(get_optional_user),
               db: Session = Depends(get_db)):
    """个人主页社区内容：tab=posts(TA的帖子,公开)/favorites(收藏,仅本人)/likes(点赞,仅本人)。"""
    return services.community_user_posts(db, viewer, user_id, tab,
                                         page=page, page_size=page_size)


@router.post("/upload")
def upload_image(file: UploadFile = File(...),
                 user: User = Depends(get_current_user)):
    """发帖图片上传：校验类型/大小，落盘 static/uploads，返回可访问 URL。"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return JSONResponse(status_code=400,
                            content={"detail": "仅支持 jpg/png/gif/webp 图片"})
    data = file.file.read()
    if len(data) > MAX_IMAGE_SIZE:
        return JSONResponse(status_code=400, content={"detail": "图片不能超过 5MB"})
    if not data:
        return JSONResponse(status_code=400, content={"detail": "图片内容为空"})

    # __file__ 位于 app/routers/community.py，需向上三级到项目根，再拼 static/
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    static_dir = os.path.join(project_dir, "static")
    upload_dir = os.path.join(static_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    fname = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(upload_dir, fname), "wb") as f:
        f.write(data)
    return {"url": f"/static/uploads/{fname}", "filename": fname}
