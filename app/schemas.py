"""Pydantic v2 请求 DTO：字段对齐 mock.js 的 handle() 入参。

响应模型可选——service 直接返回 dict，字段严格对齐 mock.js 的
publicUser/gameOut/reviewOut/commentOut 等构造函数。
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RegisterReq(BaseModel):
    username: str
    email: str
    password: str


class LoginReq(BaseModel):
    username_or_email: str
    password: str


class UpdateProfileReq(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str


class ApplyCreatorReq(BaseModel):
    apply_reason: str
    good_at: Optional[str] = None    # 擅长方向（逗号分隔标签）
    experience: Optional[str] = None  # 游戏经历（选填）


class CreateFavoriteReq(BaseModel):
    game_id: int


class PlayRecordReq(BaseModel):
    game_id: int
    play_status: str  # want/playing/completed


class CreateCommentReq(BaseModel):
    target_type: str = "review"
    target_id: int = 0
    parent_id: Optional[int] = None
    content: str
    # 游戏短评论快捷入参：POST /api/comments {game_id, content}
    game_id: Optional[int] = None


class GameCommentCreate(BaseModel):
    """游戏详情页发表短评论（target 由路径参数 game_id 决定）。"""
    content: str
    parent_id: Optional[int] = None


class GameRatingReq(BaseModel):
    """用户对游戏的评分（1-10 分）：可直接给综合分，或四维细化打分（剧情/画面/玩法/优化）。"""
    score: Optional[int] = None
    score_story: Optional[int] = None
    score_graphic: Optional[int] = None
    score_gameplay: Optional[int] = None
    score_opt: Optional[int] = None


class CreateReviewReq(BaseModel):
    title: str
    game_id: int
    content: str = ""
    tags: List[str] = Field(default_factory=list)
    # 四维评分 1-10：剧情/画面/玩法/性能优化
    score_story: Optional[int] = None
    score_graphic: Optional[int] = None
    score_gameplay: Optional[int] = None
    score_opt: Optional[int] = None


class UpdateReviewReq(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    game_id: Optional[int] = None
    tags: Optional[List[str]] = None
    score_story: Optional[int] = None
    score_graphic: Optional[int] = None
    score_gameplay: Optional[int] = None
    score_opt: Optional[int] = None


class AIGameRecommendReq(BaseModel):
    preferences: Optional[str] = None


class AIChatReq(BaseModel):
    message: str
    history: Optional[list] = None  # [{role, content}] 简单上下文，DeepSeek 模式使用


class AICreatorReq(BaseModel):
    game_id: int
    action: Optional[str] = None
    message: Optional[str] = None
    content_context: Optional[str] = None


class AdminUserStatusReq(BaseModel):
    is_active: bool


class AdminUserRoleReq(BaseModel):
    role: str  # player/creator


class AdminApplyDealReq(BaseModel):
    action: str  # approve/reject


class AdminReviewAuditReq(BaseModel):
    action: str  # pass/reject
    reason: Optional[str] = None


class AdminGameCreateReq(BaseModel):
    name: str
    name_en: str = ""
    developer: str = ""
    cover_url: str = ""
    description: str = ""
    release_date: str = "2025-01-01"
    category_id: int = 1
    tags: List[str] = Field(default_factory=list)
    is_online: bool = True


class AdminGameUpdateReq(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    developer: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    is_online: Optional[bool] = None


class AdminCategoryReq(BaseModel):
    name: str


# ==================== 社区模块 ====================

class CommunityPostCreateReq(BaseModel):
    """发帖：标题 + 正文 + 多图 URL（图片先走上传接口）+ 单选标签。"""
    title: str
    content: str = ""
    images: List[str] = Field(default_factory=list)
    tag: str = "闲聊"  # 游戏/闲聊/攻略/吐槽


class CommunityPostCommentReq(BaseModel):
    """帖子评论/楼中楼回复。"""
    content: str
    parent_id: Optional[int] = None


class ReportCreateReq(BaseModel):
    """举报帖子或评论。"""
    target_type: str  # post/comment
    target_id: int
    reason: str = "其他"
    detail: Optional[str] = None


class AdminReportHandleReq(BaseModel):
    """管理员处理举报：dismiss=驳回，remove=删除违规内容，ban=删除并封禁作者。"""
    action: str  # dismiss/remove/ban
    note: Optional[str] = None
