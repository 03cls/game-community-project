from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models import User
from app.schemas import CreateFavoriteReq
from app import services

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("")
def list_favorites(user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return services.list_favorites(db, user)


@router.post("")
def add_favorite(body: CreateFavoriteReq,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return services.add_favorite(db, user, body)


@router.delete("/{game_id}")
def remove_favorite(game_id: int,
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    return services.remove_favorite(db, user, game_id)
