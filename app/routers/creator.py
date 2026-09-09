from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.base import get_db
from app.models import User
from app import services

router = APIRouter(prefix="/api/creator", tags=["creator"])


@router.get("/reviews")
def creator_reviews(status: Optional[str] = None,
                    page: Optional[int] = None,
                    page_size: Optional[int] = None,
                    user: User = Depends(require_role("creator")),
                    db: Session = Depends(get_db)):
    """创作者评测管理：可按 status 过滤 + 分页。"""
    return services.creator_reviews(db, user, status=status,
                                    page=page, page_size=page_size)


@router.get("/statistics")
def creator_statistics(user: User = Depends(require_role("creator")),
                       db: Session = Depends(get_db)):
    return services.creator_statistics(db, user)


@router.get("/points")
def creator_points(user: User = Depends(require_role("creator")),
                   db: Session = Depends(get_db)):
    """创作者积分与等级概览（工作台）。"""
    return services.creator_points_overview(db, user)


@router.get("/point-records")
def creator_point_records(page: Optional[int] = None,
                          page_size: Optional[int] = None,
                          user: User = Depends(require_role("creator")),
                          db: Session = Depends(get_db)):
    """积分流水记录（分页）。"""
    return services.creator_point_records(db, user, page=page, page_size=page_size)


@router.get("/hall")
def creator_hall(page: Optional[int] = None,
                 page_size: Optional[int] = None,
                 db: Session = Depends(get_db)):
    """首页专题：L3+ 资深创作者的公开评测（公开接口）。"""
    return services.creator_hall(db, page=page, page_size=page_size)
