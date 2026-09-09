"""站内消息通知接口：列表 / 未读数 / 标记已读 / 全部已读。"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models import Notification, User

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Tab 分组：interact=互动消息（回复/点赞/收藏），system=系统通知（审核/申请/系统）
_SCOPES = {
    "interact": ("reply", "like", "favorite"),
    "system": ("audit", "apply", "system"),
}


def _out(n: Notification) -> dict:
    return {
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "content": n.content,
        "actor_name": n.actor_name,
        "target_type": n.target_type,
        "target_id": n.target_id,
        "is_read": bool(n.is_read),
        "created_at": n.created_at.isoformat() + "Z" if n.created_at else None,
    }


def _base_query(db: Session, user: User, scope: str, ntype: str, unread: int):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if ntype in ("reply", "like", "favorite", "audit", "apply", "system"):
        q = q.filter(Notification.type == ntype)
    elif scope in _SCOPES:
        q = q.filter(Notification.type.in_(_SCOPES[scope]))
    if unread == 1:
        q = q.filter(Notification.is_read.is_(False))
    return q


@router.get("")
def list_notifications(scope: str = "all",
                       type: str = "all",
                       unread: int = 0,
                       page: int = 1,
                       page_size: int = 10,
                       user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """我的消息列表：scope=all/interact/system，type=具体类型，unread=1 仅未读。"""
    try:
        page = max(1, int(page or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = max(1, min(50, int(page_size or 10)))
    except (TypeError, ValueError):
        page_size = 10
    q = _base_query(db, user, scope, type, unread)
    total = q.count()
    unread_total = (db.query(Notification)
                    .filter(Notification.user_id == user.id,
                            Notification.is_read.is_(False)).count())
    rows = (q.order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset((page - 1) * page_size).limit(page_size).all())
    return {
        "items": [_out(n) for n in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "unread_total": unread_total,
    }


@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """未读消息数（导航铃铛轮询）。"""
    count = (db.query(Notification)
             .filter(Notification.user_id == user.id,
                     Notification.is_read.is_(False)).count())
    return {"count": count}


@router.post("/{notification_id}/read")
def mark_read(notification_id: int,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id).first()
    if n is None:
        raise HTTPException(status_code=404, detail="消息不存在")
    n.is_read = True
    db.commit()
    return {"message": "已读"}


@router.post("/read-all")
def mark_all_read(user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """全部标记已读。"""
    changed = (db.query(Notification)
               .filter(Notification.user_id == user.id,
                       Notification.is_read.is_(False))
               .update({"is_read": True}, synchronize_session=False))
    db.commit()
    return {"message": "全部已读", "changed": changed}
