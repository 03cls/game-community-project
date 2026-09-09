"""安全模块：bcrypt 密码哈希 + JWT 签发/校验。

说明：直接调用 bcrypt 库（不依赖 passlib），避免 passlib 1.7 与 bcrypt 5 的兼容问题。
bcrypt 对超过 72 字节的密码会抛错，这里统一截断到前 72 字节。
"""
from __future__ import annotations

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from .config import settings

# bcrypt 限制：密码最大 72 字节
_BCRYPT_MAX_BYTES = 72


def _b(pw: str) -> bytes:
    """编码并截断到 72 字节，规避 bcrypt 长度上限。"""
    return pw.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """bcrypt 哈希，返回字符串存储。"""
    return bcrypt.hashpw(_b(password), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文与哈希是否匹配。"""
    try:
        return bcrypt.checkpw(_b(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, role: str, extra: dict[str, Any] | None = None) -> str:
    """签发 JWT：payload 含 sub(user_id)、role、exp。"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any] | None:
    """校验并解码 JWT，失败返回 None。"""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
