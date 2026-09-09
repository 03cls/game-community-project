from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_optional_user, require_role
from app.db.base import get_db
from app.models import User
from app.schemas import AIChatReq, AICreatorReq, AIGameRecommendReq
from app import services

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat")
async def chat(body: AIChatReq,
               user: Optional[User] = Depends(get_optional_user),
               db: Session = Depends(get_db)):
    """AI 对话助手：意图识别 + 推荐/评分/攻略/平台答疑（匿名可用）。"""
    return await services.ai_chat(db, user, body)


@router.post("/game-recommend")
async def game_recommend(body: AIGameRecommendReq,
                         user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    return await services.ai_game_recommend(db, user, body)


@router.post("/creator-assistant")
async def creator_assistant(body: AICreatorReq,
                             user: User = Depends(require_role("creator")),
                             db: Session = Depends(get_db)):
    return await services.ai_creator_assistant(db, user, body)
