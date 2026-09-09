"""认证依赖：解析 JWT、注入当前用户、角色校验。

- get_current_user：无 token / 无效 token -> 401；封禁用户 -> 403
- get_optional_user：无 token 或无效 token 均返回 None（不抛）
- require_role(role)：依赖工厂，校验当前用户角色 order >= required
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.base import SessionLocal, get_db
from app.models import User

# tokenUrl 仅用于 OpenAPI 文档展示，实际登录走 /api/auth/login 接收 JSON
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _load_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        _unauthorized()
    user_id_raw = payload.get("sub")
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        _unauthorized()
        return None  # unreachable
    user = _load_user(db, user_id)
    if user is None:
        _unauthorized()
    if not user.is_active:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="账号已被封禁")
    return user


def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional),
                      db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        return None
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        return None
    user = _load_user(db, user_id)
    if user is None or not user.is_active:
        return None
    return user


def require_role(role: str):
    """依赖工厂：校验当前用户角色 >= role，否则 403。"""
    from fastapi import HTTPException
    order = {"player": 1, "creator": 2, "admin": 3}

    def _check(user: User = Depends(get_current_user)) -> User:
        if order.get(user.role, 0) < order[role]:
            raise HTTPException(status_code=403, detail="权限不足")
        return user

    return _check


def _unauthorized():
    from fastapi import HTTPException
    raise HTTPException(status_code=401, detail="未登录或登录已过期")
