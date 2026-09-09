from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas import LoginReq, RegisterReq
from app import services

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(body: RegisterReq, db: Session = Depends(get_db)):
    return services.register(db, body)


@router.post("/login")
def login(body: LoginReq, db: Session = Depends(get_db)):
    return services.login(db, body)
