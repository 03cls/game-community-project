from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models import User
from app.schemas import ApplyCreatorReq, ChangePasswordReq, UpdateProfileReq
from app import services

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return services.get_me(user)


@router.put("/me")
def update_me(body: UpdateProfileReq,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return services.update_me(db, user, body)


@router.put("/me/password")
def change_password(body: ChangePasswordReq,
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    return services.change_password(db, user, body)


@router.get("/me/creator-application")
def my_creator_application(user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """我最近一次创作者申请状态（个人中心展示）。"""
    return services.my_creator_application(db, user)


@router.post("/apply-creator")
def apply_creator(body: ApplyCreatorReq,
                  user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return services.apply_creator(db, user, body)
