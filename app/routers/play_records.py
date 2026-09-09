from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models import User
from app.schemas import PlayRecordReq
from app import services

router = APIRouter(prefix="/api/play-record", tags=["play-record"])


@router.get("")
def list_play_records(user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    return services.list_play_records(db, user)


@router.post("")
def upsert_play_record(body: PlayRecordReq,
                       user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    return services.upsert_play_record(db, user, body)
