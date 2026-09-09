"""站内消息通知：统一推送入口。

规则：
- 不给自己发通知（actor_id == user_id 时静默跳过）；
- actor 为 None 表示系统消息；
- 通知在业务事务内 db.add()，随业务 commit 一起落库，不单独 commit。
"""
from __future__ import annotations

from typing import Optional

from app.models import Notification, User


def push(db, user_id: Optional[int], ntype: str, title: str,
         content: str = "", actor_id: Optional[int] = None,
         target_type: Optional[str] = None,
         target_id: Optional[int] = None) -> None:
    """给单个用户推送通知（自己触发的操作不通知自己）。"""
    if user_id is None:
        return
    if actor_id is not None and actor_id == user_id:
        return
    db.add(Notification(
        user_id=user_id, type=ntype, title=title,
        content=(content or "")[:500], actor_id=actor_id,
        target_type=target_type, target_id=target_id))


def push_to_admins(db, ntype: str, title: str, content: str = "",
                   actor_id: Optional[int] = None,
                   target_type: Optional[str] = None,
                   target_id: Optional[int] = None) -> None:
    """给全部管理员推送通知（如收到新的创作者申请）。"""
    admins = db.query(User).filter(User.role == "admin").all()
    for a in admins:
        push(db, a.id, ntype, title, content, actor_id=actor_id,
             target_type=target_type, target_id=target_id)
