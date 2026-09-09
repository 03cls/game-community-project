"""业务逻辑层：权限校验 / 事务编排 / AI 编排。

严格分层 router → service → repository。service 接收 db session + 当前 user + 请求体，
返回字段对齐 mock.js 的 dict。异常用 HTTPException(status_code, message)。
"""
from __future__ import annotations

import re
from typing import Any, List, Optional
from urllib.parse import quote

from fastapi import HTTPException

from app import repositories
from app import notify
from app.ai_client import ai_audit, ai_chat as _ai_chat, ai_creator, ai_recommend
from app.core import moderation
from app.core import points as pts
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Game, GameRating, Review, User
from app.schemas import (
    AIChatReq,
    AICreatorReq,
    AIGameRecommendReq,
    AdminApplyDealReq,
    AdminCategoryReq,
    AdminGameCreateReq,
    AdminGameUpdateReq,
    AdminReportHandleReq,
    AdminReviewAuditReq,
    AdminUserRoleReq,
    AdminUserStatusReq,
    ApplyCreatorReq,
    ChangePasswordReq,
    CommunityPostCommentReq,
    CommunityPostCreateReq,
    CreateCommentReq,
    CreateFavoriteReq,
    CreateReviewReq,
    GameCommentCreate,
    GameRatingReq,
    LoginReq,
    PlayRecordReq,
    RegisterReq,
    ReportCreateReq,
    UpdateProfileReq,
    UpdateReviewReq,
)

ROLE_ORDER = {"player": 1, "creator": 2, "admin": 3}

# ---------------- 工具 ----------------

def _iso(dt) -> Optional[str]:
    return dt.isoformat() if dt else None


def _img(prompt: str) -> str:
    return ("https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt="
            + quote(prompt) + "&image_size=landscape_16_9")


def require_role(user, role: str) -> None:
    if not user or ROLE_ORDER.get(user.role, 0) < ROLE_ORDER[role]:
        raise HTTPException(status_code=403, detail="权限不足")


def _paginate(items: list, page: Any, page_size: Any) -> dict:
    try:
        page = int(page) if page else 1
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(page_size) if page_size else 9
    except (TypeError, ValueError):
        page_size = 9
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 9
    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    return {
        "items": items[start:start + page_size],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------- 响应构造器 ----------------

def public_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "creator_points": round(user.creator_points or 0.0, 1),
        "creator_level": user.creator_level or 0,
        "created_at": _iso(user.created_at),
        "profile": {
            "nickname": user.nickname,
            "avatar": user.avatar or "",
            "bio": user.bio or "",
        },
    }


def game_out(game) -> dict:
    return {
        "id": game.id,
        "name": game.name,
        "name_en": game.name_en or "",
        "developer": game.developer or "",
        "cover_url": game.cover_url or "",
        "description": game.description or "",
        "release_date": game.release_date or "",
        "category_id": game.category_id,
        "tags": list(game.tags),
        "average_score": game.average_score,
        "steam_url": game.steam_url or "",
        "score_story": game.score_story or 0.0,
        "score_graphic": game.score_graphic or 0.0,
        "score_gameplay": game.score_gameplay or 0.0,
        "score_opt": game.score_opt or 0.0,
        "rating_count": game.rating_count or 0,
        "is_online": game.is_online,
        "hot": game.hot,
        "created_at": _iso(game.created_at),
        "category_name": game.category_name,
    }


def review_out(review) -> dict:
    return {
        "id": review.id,
        "game_id": review.game_id,
        "user_id": review.user_id,
        "title": review.title,
        "content": review.content or "",
        "tags": list(review.tags),
        "score_story": review.score_story,
        "score_graphic": review.score_graphic,
        "score_gameplay": review.score_gameplay,
        "score_opt": review.score_opt,
        "status": review.status,
        "audit_status": review.audit_status,
        "audit_score": review.audit_score,
        "audit_reason": review.audit_reason or "",
        "read_count": review.read_count,
        "like_count": review.like_count,
        "fav_count": review.fav_count,
        "is_featured": review.is_featured or False,
        "edit_used": review.edit_used or False,
        "author_level": review.author.creator_level if review.author else 0,
        "created_at": _iso(review.created_at),
        "author_name": review.author_name,
        "author_avatar": review.author_avatar,
        "game_name": review.game_name,
        "game_cover": review.game_cover,
    }


def comment_out(db, comment, current_user_id: Optional[int]) -> dict:
    liked = False
    if current_user_id:
        liked = repositories.get_comment_like(db, comment.id, current_user_id) is not None
    can_delete = bool(current_user_id and comment.user_id == current_user_id)
    return {
        "id": comment.id,
        "user_id": comment.user_id,
        "target_type": comment.target_type,
        "target_id": comment.target_id,
        "parent_id": comment.parent_id,
        "content": comment.content,
        "like_count": comment.like_count,
        "created_at": _iso(comment.created_at),
        "author_name": comment.author_name,
        "liked": liked,
        "can_delete": can_delete,
    }


def category_out(c) -> dict:
    return {"id": c.id, "name": c.name}


# ---------------- 认证 ----------------

def register(db, body: RegisterReq) -> dict:
    if not body.username or not body.email or not body.password:
        raise HTTPException(status_code=400, detail="用户名、邮箱、密码不能为空")
    if repositories.get_user_by_username(db, body.username) is not None:
        raise HTTPException(status_code=400, detail="用户名已存在")
    if repositories.get_user_by_email(db, body.email) is not None:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    repositories.create_user(
        db, username=body.username, email=body.email,
        password=hash_password(body.password), role="player", is_active=True,
        nickname=body.username, avatar="", bio="",
    )
    db.commit()
    return {"message": "注册成功，请登录"}


def login(db, body: LoginReq) -> dict:
    key = (body.username_or_email or "").strip()
    user = repositories.get_user_by_username_or_email(db, key)
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被封禁，请联系管理员")
    token = create_access_token(user.id, user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "user": public_user(user),
    }


# ---------------- 用户 ----------------

def get_me(user: User) -> dict:
    return public_user(user)


def update_me(db, user: User, body: UpdateProfileReq) -> dict:
    data = body.model_dump(exclude_unset=True)
    if "nickname" in data:
        user.nickname = data["nickname"]
    if "avatar" in data:
        user.avatar = data["avatar"]
    if "bio" in data:
        user.bio = data["bio"]
    db.flush()
    result = public_user(user)
    db.commit()
    return result


def change_password(db, user: User, body: ChangePasswordReq) -> dict:
    if not verify_password(body.old_password, user.password):
        raise HTTPException(status_code=400, detail="原密码不正确")
    if not body.new_password or len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少 6 位")
    user.password = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}


def apply_creator(db, user: User, body: ApplyCreatorReq) -> dict:
    if user.role in ("creator", "admin"):
        raise HTTPException(status_code=400, detail="你已经是创作者了")
    reason = (body.apply_reason or "").strip()
    if len(reason) < 10:
        raise HTTPException(status_code=400, detail="申请理由至少 10 个字，请介绍你的写作经验或游戏经历")
    if len(reason) > 200:
        raise HTTPException(status_code=400, detail="申请理由不能超过 200 个字")
    good_at = (body.good_at or "").strip()
    if len(good_at) > 100:
        raise HTTPException(status_code=400, detail="擅长方向不能超过 100 个字")
    experience = (body.experience or "").strip()
    if len(experience) > 200:
        raise HTTPException(status_code=400, detail="游戏经历不能超过 200 个字")
    if repositories.get_pending_application_by_user(db, user.id) is not None:
        raise HTTPException(status_code=400, detail="已有待审核的申请，请耐心等待")
    repositories.create_creator_application(
        db, user_id=user.id, apply_reason=reason,
        good_at=good_at, experience=experience)
    # 消息通知：收到新的创作者申请 → 通知全部管理员
    notify.push_to_admins(
        db, "apply", "收到新的创作者申请",
        "%s 提交了创作者申请，请前往管理后台审核" % (user.nickname or user.username),
        actor_id=user.id, target_type="application")
    db.commit()
    return {"message": "申请已提交，等待管理员审核"}


def my_creator_application(db, user: User) -> dict:
    """我最近一次创作者申请状态（个人中心展示）。"""
    a = repositories.latest_application_by_user(db, user.id)
    if a is None:
        return {"status": "none", "application": None}
    return {
        "status": a.status,
        "application": {
            "id": a.id,
            "apply_reason": a.apply_reason,
            "good_at": a.good_at or "",
            "experience": a.experience or "",
            "created_at": _iso(a.created_at),
        },
    }


# ---------------- 游戏 ----------------

def list_games(db, user_opt, *, category_id: Optional[int] = None,
               keyword: Optional[str] = None, sort: str = "hot",
               page: Any = 1, page_size: Any = 9) -> dict:
    games = repositories.list_games(db, category_id=category_id,
                                    keyword=keyword, sort=sort or "hot")
    items = [game_out(g) for g in games]
    result = _paginate(items, page, page_size)
    result["categories"] = [category_out(c) for c in repositories.list_categories(db)]
    return result


def get_game(db, user_opt, game_id: int) -> dict:
    game = repositories.get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    out = game_out(game)
    is_fav = False
    play_status = None
    my_rating = None
    my_dims = None
    if user_opt:
        is_fav = repositories.get_favorite(db, user_opt.id, game.id) is not None
        rec = repositories.get_play_record(db, user_opt.id, game.id)
        play_status = rec.play_status if rec else None
        my = repositories.get_game_rating(db, user_opt.id, game.id)
        my_rating = my.score if my else None
        if my is not None:
            my_dims = {
                "score_story": my.score_story,
                "score_graphic": my.score_graphic,
                "score_gameplay": my.score_gameplay,
                "score_opt": my.score_opt,
            }
    out["is_favorite"] = is_fav
    out["play_status"] = play_status
    out["my_rating"] = my_rating
    out["my_dims"] = my_dims
    return out


def list_game_reviews(db, game_id: int, page: Any = 1, page_size: Any = 5,
                      keyword: Optional[str] = None) -> dict:
    reviews = repositories.list_reviews_by_game(db, game_id, keyword=keyword)
    items = [review_out(r) for r in reviews]
    return _paginate(items, page, page_size)


# ---------------- 用户游戏评分（1-10 分，支持四维细化） ----------------

def _valid_dim(v) -> bool:
    return not (isinstance(v, bool) or not isinstance(v, int) or v < 1 or v > 10)


def submit_game_rating(db, user: User, game_id: int, body: GameRatingReq) -> dict:
    """登录用户提交/修改评分：同一用户对单款游戏仅一条记录，提交后重算聚合。

    支持四维细化打分（剧情/画面/玩法/优化）：四维齐全时综合分 = 四维均值（四舍五入）；
    否则必须直接给出综合分 score。
    """
    if repositories.get_game_simple(db, game_id) is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    dims = {k: getattr(body, k) for k in SCORE_FIELDS}
    for k, v in dims.items():
        if v is not None and not _valid_dim(v):
            raise HTTPException(status_code=400, detail=f"{k} 必须为 1-10 的整数")
    if all(v is not None for v in dims.values()):
        # 四维均值四舍五入为整数（int(x+0.5) 常规四舍五入，避免 round 的银行家舍入）
        score = int(sum(dims.values()) / 4 + 0.5)
        score = max(1, min(10, score))
    elif body.score is not None:
        score = body.score
        if not _valid_dim(score):
            raise HTTPException(status_code=400, detail="评分必须为 1-10 的整数")
    else:
        raise HTTPException(status_code=400, detail="请为剧情/画面/玩法/优化四个维度打分，或直接给出综合分")
    _, created = repositories.upsert_game_rating(db, user.id, game_id, score, dims)
    game = repositories.recalc_game_scores(db, game_id)
    db.commit()
    return {
        "message": "评分成功" if created else "评分已更新",
        "game_id": game_id,
        "score": score,
        "my_rating": score,
        "my_dims": dims,
        "average_score": game.average_score,
        "rating_count": game.rating_count,
        "score_story": game.score_story,
        "score_graphic": game.score_graphic,
        "score_gameplay": game.score_gameplay,
        "score_opt": game.score_opt,
    }


# ---------------- 首页游戏评测专区 ----------------

def _excerpt(html: str, n: int = 80) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:n] + "…" if len(text) > n else (text or "（暂无正文）")


def public_review_out(review) -> dict:
    dims = (review.score_story, review.score_graphic,
            review.score_gameplay, review.score_opt)
    score = round(sum(dims) / 4, 1) if all(d is not None for d in dims) else None
    return {
        "id": review.id,
        "game_id": review.game_id,
        "title": review.title,
        "game_name": review.game_name,
        "game_cover": review.game_cover,
        "author_name": review.author_name,
        "author_avatar": review.author_avatar,
        "author_level": review.author.creator_level if review.author else 0,
        "is_featured": review.is_featured or False,
        "score": score,
        "summary": _excerpt(review.content),
        "created_at": _iso(review.created_at),
    }


def list_public_reviews(db, keyword: Optional[str] = None,
                        page: Any = 1, page_size: Any = 12) -> dict:
    """全部公开评测，发布时间倒序；keyword 按游戏名称过滤（首页评测专区）。"""
    reviews = repositories.list_public_reviews(db, keyword=keyword)
    items = [public_review_out(r) for r in reviews]
    return _paginate(items, page, page_size)


def game_reviews_count(db, game_id: int) -> dict:
    if repositories.get_game(db, game_id) is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return {"game_id": game_id, "count": repositories.count_published_reviews_by_game(db, game_id)}


def list_similar_games(db, game_id: int) -> dict:
    """相似游戏推荐：依据分类与标签返回 3-4 款。"""
    game = repositories.get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    similar = repositories.find_similar_games(db, game, limit=4)
    return {"items": [{
        "id": s.id,
        "name": s.name,
        "name_en": s.name_en or "",
        "cover_url": s.cover_url or "",
        "average_score": s.average_score,
        "category_name": s.category_name,
    } for s in similar]}


def get_review_detail(db, review_id: int, viewer: Optional[User] = None) -> dict:
    """评测详情：已通过(published)对全部用户可见（阅读量 +1）；
    待审核/已驳回仅作者本人与管理员可预览，其他用户提示无权限。"""
    review = repositories.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    if review.status != "published":
        # 未过审内容：仅作者本人（及管理员）可预览，不增加阅读量
        allowed = viewer is not None and (
            viewer.id == review.user_id or viewer.role == "admin")
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail="无权限查看该评测（未通过审核的内容仅作者本人可见）")
        result = review_out(review)
        result["my_liked"] = False
        result["my_favorited"] = False
        result["can_edit"] = False
        return result
    review.read_count = (review.read_count or 0) + 1
    db.flush()
    result = review_out(review)
    result["my_liked"] = bool(viewer and repositories.get_review_like(db, review.id, viewer.id))
    result["my_favorited"] = bool(viewer and repositories.get_review_fav(db, review.id, viewer.id))
    result["can_edit"] = bool(
        viewer and review.user_id == viewer.id
        and (viewer.creator_level or 0) >= 1 and not review.edit_used)
    db.commit()
    return result


# ---------------- 收藏 ----------------

def list_favorites(db, user: User) -> dict:
    games = repositories.list_favorites_by_user(db, user.id)
    items = [game_out(g) for g in games]
    return {"items": items, "total": len(items)}


# ---------------- 我的评测互动（点赞 / 收藏） ----------------

def my_review_likes(db, user: User) -> dict:
    """我点赞过的评测列表（仅已发布，个人中心展示）。"""
    reviews = repositories.list_reviews_liked_by_user(db, user.id)
    items = [review_out(r) for r in reviews]
    return {"items": items, "total": len(items)}


def my_review_favs(db, user: User) -> dict:
    """我收藏的评测列表（仅已发布，个人中心展示）。"""
    reviews = repositories.list_reviews_faved_by_user(db, user.id)
    items = [review_out(r) for r in reviews]
    return {"items": items, "total": len(items)}


def my_reviews(db, user: User, status: Optional[str] = None,
               page: Any = 1, page_size: Any = 10) -> dict:
    """我发布的全部评测（个人中心展示，含待审核/已驳回/草稿；不限创作者角色）。
    status 可按 published/rejected/draft/audit/manual_review 过滤。"""
    valid = ("published", "rejected", "draft", "audit", "manual_review")
    st = status if status in valid else None
    reviews = repositories.list_reviews_by_user(db, user.id, status=st)
    items = [review_out(r) for r in reviews]
    return _paginate(items, page, page_size)


def add_favorite(db, user: User, body: CreateFavoriteReq) -> dict:
    if repositories.get_game_simple(db, body.game_id) is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    if repositories.get_favorite(db, user.id, body.game_id) is None:
        repositories.add_favorite(db, user.id, body.game_id)
    db.commit()
    return {"message": "收藏成功"}


def remove_favorite(db, user: User, game_id: int) -> dict:
    repositories.remove_favorite(db, user.id, game_id)
    db.commit()
    return {"message": "已取消收藏"}


# ---------------- 游玩记录 ----------------

def list_play_records(db, user: User) -> dict:
    records = repositories.get_play_records(db, user.id)
    items = []
    for r in records:
        d = {
            "id": r.id,
            "user_id": r.user_id,
            "game_id": r.game_id,
            "play_status": r.play_status,
            "created_at": _iso(r.created_at),
            "updated_at": _iso(r.updated_at),
            "game": game_out(r.game) if r.game else None,
        }
        items.append(d)
    return {"items": items}


def upsert_play_record(db, user: User, body: PlayRecordReq) -> dict:
    if body.play_status not in ("want", "playing", "completed"):
        raise HTTPException(status_code=400, detail="状态非法")
    repositories.upsert_play_record(db, user.id, body.game_id, body.play_status)
    db.commit()
    return {"message": "游玩状态已更新", "play_status": body.play_status}


# ---------------- 评论 ----------------

def list_comments(db, user_opt, target_type: str, target_id: int) -> dict:
    ttype = target_type or "review"
    if ttype == "review" and repositories.get_review(db, target_id) is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    comments = repositories.list_comments(db, ttype, target_id)
    uid = user_opt.id if user_opt else None
    items = [comment_out(db, c, uid) for c in comments]
    return {"items": items}


def my_comments(db, user: User, *, page: Any = 1, page_size: Any = 10) -> dict:
    """我发表的全部评论（游戏短评论 + 评测攻略评论），时间倒序，分页。

    每条附带目标信息：game → game_name / cover；review → review_title。"""
    comments = repositories.list_comments_by_user(db, user.id)
    items = []
    for c in comments:
        out = comment_out(db, c, user.id)
        if c.target_type == "game":
            g = repositories.get_game(db, c.target_id)
            out["target_name"] = g.name if g else "已删除游戏"
            out["target_cover"] = g.cover_url if g else ""
        else:
            r = repositories.get_review(db, c.target_id)
            out["target_name"] = r.title if r else "已删除评测"
            out["target_cover"] = r.game_cover if r else ""
        items.append(out)
    result = _paginate(items, page, page_size)
    return result


def create_comment(db, user: User, body: CreateCommentReq) -> dict:
    if not body.content or not body.content.strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")
    target_type = body.target_type or "review"
    target_id = body.target_id
    if body.game_id:  # 契约：POST /api/comments {game_id, content} 发布游戏短评论
        target_type = "game"
        target_id = body.game_id
        if repositories.get_game(db, body.game_id) is None:
            raise HTTPException(status_code=404, detail="游戏不存在")
    c = repositories.create_comment(
        db, user_id=user.id, target_type=target_type,
        target_id=target_id, parent_id=body.parent_id,
        content=body.content.strip())
    db.flush()
    # 消息通知：回复→通知被回复人；评测收到新评论→通知评测作者（游戏短评无归属人，不通知）
    _snippet = (body.content or "").strip()[:30]
    if body.parent_id:
        _parent = repositories.get_comment(db, body.parent_id)
        if _parent is not None and _parent.user_id:
            if target_type == "review":
                _rv = repositories.get_review(db, target_id)
                _ctx = "评测《%s》" % _rv.title if _rv else "评论"
            else:
                _gm = repositories.get_game(db, target_id)
                _ctx = "游戏《%s》短评" % _gm.name if _gm else "短评"
            notify.push(db, _parent.user_id, "reply",
                        "「%s」回复了你的评论" % (user.nickname or user.username),
                        "%s：%s" % (_ctx, _snippet),
                        actor_id=user.id, target_type=target_type,
                        target_id=target_id)
    elif target_type == "review":
        _rv = repositories.get_review(db, target_id)
        if _rv is not None and _rv.author is not None:
            notify.push(db, _rv.author.id, "reply",
                        "「%s」评论了你的评测" % (user.nickname or user.username),
                        "《%s》：%s" % (_rv.title, _snippet),
                        actor_id=user.id, target_type="review",
                        target_id=target_id)
    result = comment_out(db, c, user.id)
    db.commit()
    return result


def toggle_like(db, user: User, comment_id: int) -> dict:
    if repositories.get_comment(db, comment_id) is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    like_count, liked = repositories.toggle_comment_like(db, comment_id, user.id)
    db.commit()
    return {"like_count": like_count, "liked": liked}


def delete_comment(db, user: User, comment_id: int) -> dict:
    """删除评论：只能删自己的；级联删除子回复。"""
    c = repositories.get_comment(db, comment_id)
    if c is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    if c.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="只能删除自己的评论")
    repositories.delete_comment(db, comment_id)
    db.commit()
    return {"message": "评论已删除"}


def _attach_user_scores(db, game_id: int, comments: List[dict]) -> None:
    """为游戏短评批量附带作者的评分（综合分 + 四维）：评论显示打分人的综合评分。"""
    uids = list({c["user_id"] for c in comments if c.get("user_id")})
    if not uids:
        return
    rows = (db.query(GameRating)
            .filter(GameRating.game_id == game_id, GameRating.user_id.in_(uids))
            .all())
    by_user = {r.user_id: r for r in rows}
    for c in comments:
        r = by_user.get(c.get("user_id"))
        c["user_score"] = r.score if r else None
        c["user_dims"] = (
            {"剧情": r.score_story, "画面": r.score_graphic,
             "玩法": r.score_gameplay, "优化": r.score_opt} if r else None
        )


def list_game_comments(db, user_opt, game_id: int, page: Any, page_size: Any) -> dict:
    """游戏短评论区：自动精选置顶 + 普通评论分页（默认每页 5 条）。

    自动精选为运行时计算：取点赞最高的评论（并列取创建时间最早），无字数/内容限制；
    无评论时为 null。精选展示的评论不再重复出现在普通列表。
    """
    if repositories.get_game(db, game_id) is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    try:
        page = max(1, int(page or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(page_size) if page_size else 5
    except (TypeError, ValueError):
        page_size = 5
    page_size = min(max(page_size, 1), 10)  # 契约：每页 5-10 条
    uid = user_opt.id if user_opt else None
    # 自动精选：点赞最高者作唯一候选
    candidate = repositories.list_top_liked_comment(db, "game", game_id)
    auto_selected = None
    exclude_id = None
    if candidate is not None:
        auto_selected = comment_out(db, candidate, uid)
        exclude_id = candidate.id  # 精选展示的评论不再重复出现在普通列表
    normals, total = repositories.list_normal_comments_paginated(
        db, "game", game_id, page, page_size, exclude_id=exclude_id)
    items = [comment_out(db, c, uid) for c in normals]
    all_cmts = ([auto_selected] if auto_selected else []) + items
    _attach_user_scores(db, game_id, all_cmts)
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {
        "auto_selected_comment": auto_selected,
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def create_game_comment(db, user: User, game_id: int, body: GameCommentCreate) -> dict:
    if repositories.get_game(db, game_id) is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    if not body.content or not body.content.strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")
    c = repositories.create_comment(
        db, user_id=user.id, target_type="game", target_id=game_id,
        parent_id=body.parent_id, content=body.content.strip())
    db.flush()
    result = comment_out(db, c, user.id)
    _attach_user_scores(db, game_id, [result])
    db.commit()
    return result


# ---------------- 评测 ----------------

SCORE_FIELDS = ("score_story", "score_graphic", "score_gameplay", "score_opt")


def _validate_scores(data: dict) -> dict:
    """四维评分校验：允许 None（不打分），填写时必须为 1-10 整数。"""
    values = {}
    for k in SCORE_FIELDS:
        if k in data and data[k] is not None:
            v = data[k]
            if not isinstance(v, int) or isinstance(v, bool) or v < 1 or v > 10:
                raise HTTPException(status_code=400, detail=f"{k} 必须为 1-10 的整数")
            values[k] = v
    return values


def create_review(db, user: User, body: CreateReviewReq) -> dict:
    require_role(user, "creator")
    if not body.title or not body.game_id:
        raise HTTPException(status_code=400, detail="标题与关联游戏必填")
    r = repositories.create_review(
        db, game_id=body.game_id, user_id=user.id, title=body.title,
        content=body.content or "", tags=body.tags or [],
        scores=_validate_scores(body.model_dump()))
    db.flush()
    result = review_out(r)
    db.commit()
    return result


def update_review(db, user: User, review_id: int, body: UpdateReviewReq) -> dict:
    review = repositories.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="只能编辑自己的文章")
    if review.status == "published":
        # L1+ 权益：单篇已发布评测可编辑 1 次；L0 不可编辑
        if (user.creator_level or 0) < 1:
            raise HTTPException(
                status_code=403,
                detail="L0 见习创作者的已发布评测不可编辑，升至 L1（200 积分）后每篇可编辑 1 次")
        if review.edit_used:
            raise HTTPException(status_code=400, detail="本篇评测的 1 次编辑机会已用完")
    data = body.model_dump(exclude_unset=True)
    values = {k: v for k, v in data.items() if k != "tags"}
    tags = data.get("tags")
    repositories.update_review(db, review, values, tags)
    if review.status == "published":
        repositories.mark_review_edit_used(db, review)
    db.flush()
    result = review_out(review)
    db.commit()
    return result


def delete_review(db, user: User, review_id: int) -> dict:
    review = repositories.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    if review.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除")
    game_id = review.game_id
    author = review.author
    # 积分规则：已发布评测删除 → 追回该篇全部积分，额外扣 30（草稿/被驳回无积分）
    if review.status == "published" and author is not None:
        earned = repositories.sum_points_of_review(db, author.id, review.id)
        penalty = round(earned + pts.POINT_DELETE_PENALTY, 1)
        repositories.add_point_record(
            db, author, -penalty,
            "评测《%s》被删除：追回积分 %s，额外扣 %s"
            % (review.title, _fmt_points(earned), _fmt_points(pts.POINT_DELETE_PENALTY)),
            related_type="review", related_id=review.id)
    repositories.delete_review(db, review)
    repositories.recalc_game_scores(db, game_id)  # 删除评测后重新计算游戏评分
    db.commit()
    return {"message": "已删除"}


def _fmt_points(v: float) -> str:
    return ("%g" % round(v, 1))


async def submit_audit(db, user: User, review_id: int) -> dict:
    require_role(user, "creator")
    review = repositories.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if review.status == "published":
        raise HTTPException(status_code=400, detail="文章已发布")
    if review.status in ("audit", "manual_review"):
        raise HTTPException(status_code=400, detail="文章正在审核中")
    # 提交后一律进入「待审核」状态，由管理员人工通过/驳回；
    # AI 审核仅计算风险分作为管理员参考，不再自动发布或驳回。
    audit = await ai_audit(review.title, review.content or "")
    reason = "；".join(audit.get("reasons", []))
    repositories.create_audit_log(
        db, review_id=review.id, audit_type="ai",
        risk_score=audit.get("risk_score"), reason=reason, operator_id=1)
    review.audit_score = audit.get("risk_score")
    repositories.update_review_status(
        db, review, status="manual_review", audit_status="manual_review",
        audit_score=audit.get("risk_score"), audit_reason=reason)
    db.commit()
    return {"message": "已提交审核，等待管理员审核", "status": "pending", "audit": audit}


def creator_reviews(db, user: User, status: Optional[str] = None,
                    page: Any = 1, page_size: Any = 10) -> dict:
    require_role(user, "creator")
    valid = ("published", "rejected", "draft", "audit", "manual_review")
    st = status if status in valid else None
    reviews = repositories.list_reviews_by_user(db, user.id, status=st)
    items = [review_out(r) for r in reviews]
    return _paginate(items, page, page_size)


def creator_statistics(db, user: User) -> dict:
    require_role(user, "creator")
    return repositories.statistics_for_creator(db, user.id)


# ---------------- 创作者积分与等级 ----------------

def creator_points_overview(db, user: User) -> dict:
    """工作台积分面板：总积分、当前等级、升级进度与规则说明。"""
    require_role(user, "creator")
    data = pts.overview(user.creator_points or 0.0)
    data["rules"] = [
        "评测审核通过发布 +%s" % _fmt_points(pts.POINT_PUBLISH),
        "管理员标记精选 +%s" % _fmt_points(pts.POINT_FEATURED),
        "评测获赞 +%s / 次" % _fmt_points(pts.POINT_REVIEW_LIKE),
        "评测被收藏 +%s / 次" % _fmt_points(pts.POINT_REVIEW_FAV),
        "评测被删除追回该篇全部积分并额外 -%s" % _fmt_points(pts.POINT_DELETE_PENALTY),
        "抄袭违规下架：积分清零、等级重置 L0",
    ]
    return data


def creator_point_records(db, user: User, page: Any = 1, page_size: Any = 10) -> dict:
    require_role(user, "creator")
    records = repositories.list_point_records(db, user.id)
    items = [{
        "id": r.id,
        "change": round(r.change or 0.0, 1),
        "reason": r.reason,
        "balance_after": round(r.balance_after or 0.0, 1),
        "created_at": _iso(r.created_at),
    } for r in records]
    return _paginate(items, page, page_size)


def creator_hall(db, page: Any = 1, page_size: Any = 6) -> dict:
    """首页专题：L3+ 资深/核心创作者的公开评测。"""
    reviews = repositories.list_hall_reviews(db, limit=30)
    items = [public_review_out(r) for r in reviews]
    return _paginate(items, page, page_size)


def toggle_review_like(db, user: User, review_id: int) -> dict:
    review = repositories.get_review(db, review_id)
    if review is None or review.status != "published":
        raise HTTPException(status_code=404, detail="评测不存在或未公开")
    liked, count = repositories.toggle_review_like(db, review, user.id)
    # 积分：为他人评测点赞 +0.2，取消则回滚；给自己点赞不计分
    if review.author is not None and review.author.id != user.id:
        change = pts.POINT_REVIEW_LIKE if liked else -pts.POINT_REVIEW_LIKE
        repositories.add_point_record(
            db, review.author, change,
            "评测《%s》%s" % (review.title, "获赞" if liked else "点赞被取消"),
            related_type="review", related_id=review.id)
        if liked:
            # 消息通知：评测被点赞 → 通知评测作者
            notify.push(db, review.author.id, "like",
                        "「%s」赞了你的评测" % (user.nickname or user.username),
                        "《%s》" % review.title,
                        actor_id=user.id, target_type="review",
                        target_id=review.id)
    db.commit()
    return {"liked": liked, "like_count": count}


def toggle_review_fav(db, user: User, review_id: int) -> dict:
    review = repositories.get_review(db, review_id)
    if review is None or review.status != "published":
        raise HTTPException(status_code=404, detail="评测不存在或未公开")
    fav, count = repositories.toggle_review_fav(db, review, user.id)
    if review.author is not None and review.author.id != user.id:
        change = pts.POINT_REVIEW_FAV if fav else -pts.POINT_REVIEW_FAV
        repositories.add_point_record(
            db, review.author, change,
            "评测《%s》%s" % (review.title, "被收藏" if fav else "收藏被取消"),
            related_type="review", related_id=review.id)
        if fav:
            # 消息通知：评测被收藏 → 通知评测作者
            notify.push(db, review.author.id, "favorite",
                        "「%s」收藏了你的评测" % (user.nickname or user.username),
                        "《%s》" % review.title,
                        actor_id=user.id, target_type="review",
                        target_id=review.id)
    db.commit()
    return {"favorited": fav, "fav_count": count}


# ---------------- AI ----------------

async def ai_game_recommend(db, user: User, body: AIGameRecommendReq) -> dict:
    recos = await ai_recommend(db, user.id, body.preferences)
    return {"recommendations": recos}


async def ai_chat(db, user: Optional[User], body: AIChatReq) -> dict:
    """AI 对话助手：意图识别（推荐/评分/攻略/平台答疑），匿名可用。"""
    message = (body.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    if len(message) > 500:
        raise HTTPException(status_code=400, detail="消息过长（500 字以内）")
    return await _ai_chat(db, user.id if user else None,
                          message, body.history)


async def ai_creator_assistant(db, user: User, body: AICreatorReq) -> dict:
    require_role(user, "creator")
    game = repositories.get_game_simple(db, body.game_id)
    game_name = game.name if game else "该游戏"
    return await ai_creator(db, game_name, body.action, body.message, body.content_context)


# ---------------- 管理员 ----------------

def admin_dashboard(db, user: User) -> dict:
    require_role(user, "admin")
    return repositories.dashboard_stats(db)


def admin_list_users(db, user: User, keyword: Optional[str] = None) -> dict:
    require_role(user, "admin")
    users = repositories.list_users(db, keyword)
    return {"items": [public_user(u) for u in users]}


def admin_update_user_status(db, user: User, user_id: int, body: AdminUserStatusReq) -> dict:
    require_role(user, "admin")
    target = repositories.get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.role == "admin":
        raise HTTPException(status_code=400, detail="不能封禁管理员")
    repositories.set_user_active(db, target, body.is_active)
    db.commit()
    return {"message": "已解封" if body.is_active else "已封禁"}


def admin_update_user_role(db, user: User, user_id: int, body: AdminUserRoleReq) -> dict:
    require_role(user, "admin")
    target = repositories.get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.role == "admin":
        raise HTTPException(status_code=400, detail="不能修改管理员角色")
    if body.role not in ("player", "creator"):
        raise HTTPException(status_code=400, detail="角色非法")
    repositories.set_user_role(db, target, body.role)
    db.commit()
    return {"message": "角色已更新为 " + body.role}


def admin_list_applications(db, user: User, status: Optional[str] = None) -> dict:
    require_role(user, "admin")
    apps = repositories.list_applications(db, status)
    items = []
    for a in apps:
        u = a.user
        items.append({
            "id": a.id,
            "user_id": a.user_id,
            "apply_reason": a.apply_reason,
            "good_at": a.good_at or "",
            "experience": a.experience or "",
            "status": a.status,
            "audit_user_id": a.audit_user_id,
            "created_at": _iso(a.created_at),
            "username": u.username if u else "",
            "nickname": (u.nickname if u else "") or "",
            "email": (u.email if u else "") or "",
        })
    return {"items": items}


def admin_deal_application(db, user: User, application_id: int, body: AdminApplyDealReq) -> dict:
    require_role(user, "admin")
    app = repositories.get_application(db, application_id)
    if app is None:
        raise HTTPException(status_code=404, detail="申请不存在")
    if app.status != "pending":
        raise HTTPException(status_code=400, detail="该申请已处理")
    if body.action == "approve":
        repositories.update_application(db, app, status="approved", audit_user_id=user.id)
        applicant = repositories.get_user_by_id(db, app.user_id)
        if applicant is not None:
            applicant.role = "creator"
            # 消息通知：申请结果 → 通知申请人（跳转创作者中心）
            notify.push(db, applicant.id, "apply", "创作者申请已通过",
                        "恭喜！你已成为创作者，去发布你的第一篇评测吧",
                        target_type="creator_center")
        db.commit()
        return {"message": "已通过申请，用户已升级为创作者"}
    repositories.update_application(db, app, status="rejected", audit_user_id=user.id)
    notify.push(db, app.user_id, "apply", "创作者申请未通过",
                "很遗憾，本次申请未通过审核，欢迎继续活跃社区后再来申请",
                target_type="profile")
    db.commit()
    return {"message": "已驳回申请"}


def admin_pending_reviews(db, user: User) -> dict:
    require_role(user, "admin")
    reviews = repositories.list_pending_reviews(db)
    return {"items": [review_out(r) for r in reviews]}


def admin_review_audit_decision(db, user: User, review_id: int,
                                body: AdminReviewAuditReq) -> dict:
    require_role(user, "admin")
    review = repositories.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    reason_text = ("人工复核通过：" if body.action == "pass"
                   else "人工复核驳回：") + (body.reason or "无备注")
    repositories.create_audit_log(
        db, review_id=review.id, audit_type="manual", risk_score=None,
        reason=reason_text, operator_id=user.id)
    if body.action == "pass":
        was_published = review.status == "published"
        repositories.update_review_status(
            db, review, status="published", audit_status="passed")
        repositories.recalc_game_scores(db, review.game_id)  # 人工复核通过后聚合评分
        if not was_published and review.author is not None:
            # 积分：人工复核通过发布 +20
            repositories.add_point_record(
                db, review.author, pts.POINT_PUBLISH,
                "评测《%s》人工复核通过发布" % review.title,
                related_type="review", related_id=review.id)
        # 消息通知：审核结果 → 通知评测作者
        if review.author is not None:
            notify.push(db, review.author.id, "audit",
                        "评测审核通过",
                        "《%s》已通过人工复核并发布" % review.title,
                        actor_id=user.id, target_type="review",
                        target_id=review.id)
        db.commit()
        return {"message": "已通过，文章发布"}
    repositories.update_review_status(
        db, review, status="rejected", audit_status="rejected",
        audit_reason="人工驳回：" + (body.reason or "不符合社区规范"))
    # 消息通知：审核驳回 → 通知评测作者（仅本人可见）
    if review.author is not None:
        notify.push(db, review.author.id, "audit", "评测审核未通过",
                    "《%s》被驳回：%s" % (review.title, body.reason or "不符合社区规范"),
                    actor_id=user.id, target_type="review", target_id=review.id)
    db.commit()
    return {"message": "已驳回"}


def admin_toggle_review_feature(db, user: User, review_id: int) -> dict:
    """管理员标记/取消精选：精选 +30 积分，取消则扣回。"""
    require_role(user, "admin")
    review = repositories.get_review(db, review_id)
    if review is None or review.status != "published":
        raise HTTPException(status_code=404, detail="公开评测不存在")
    new_val = not (review.is_featured or False)
    repositories.set_review_featured(db, review, new_val)
    if review.author is not None:
        change = pts.POINT_FEATURED if new_val else -pts.POINT_FEATURED
        repositories.add_point_record(
            db, review.author, change,
            "评测《%s》%s" % (review.title,
                          "被管理员标记精选" if new_val else "被取消精选标记"),
            related_type="review", related_id=review.id)
    db.commit()
    return {"is_featured": new_val,
            "message": "已标记精选，作者 +%s 积分" % _fmt_points(pts.POINT_FEATURED) if new_val
            else "已取消精选标记，作者扣回 %s 积分" % _fmt_points(pts.POINT_FEATURED)}


def admin_review_plagiarize(db, user: User, review_id: int) -> dict:
    """抄袭违规下架：评测下架（rejected）+ 作者积分清零、等级重置 L0。"""
    require_role(user, "admin")
    review = repositories.get_review(db, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    author = review.author
    title = review.title
    game_id = review.game_id
    was_published = review.status == "published"
    repositories.update_review_status(
        db, review, status="rejected", audit_status="rejected",
        audit_reason="抄袭违规，管理员强制下架")
    if was_published:
        repositories.recalc_game_scores(db, game_id)
    if author is not None and (author.creator_points or 0) > 0:
        repositories.reset_creator_points(
            db, author, "评测《%s》判定抄袭违规：积分清零、等级重置 L0" % title)
    db.commit()
    return {"message": "已按抄袭违规下架，作者积分清零并重置为 L0"}


def admin_list_games(db, user: User) -> dict:
    require_role(user, "admin")
    games = repositories.list_all_games(db)
    return {
        "items": [game_out(g) for g in games],
        "categories": [category_out(c) for c in repositories.list_categories(db)],
    }


def admin_create_game(db, user: User, body: AdminGameCreateReq) -> dict:
    require_role(user, "admin")
    if not body.name:
        raise HTTPException(status_code=400, detail="游戏名称必填")
    cover = body.cover_url or _img(
        "generic video game cover art, fantasy adventure, cinematic")
    g = repositories.create_game(
        db, name=body.name, name_en=body.name_en or "", developer=body.developer or "",
        cover_url=cover, description=body.description or "",
        release_date=body.release_date or "2025-01-01", category_id=body.category_id or 1,
        tags=body.tags or [], average_score=0.0, is_online=body.is_online, hot=50)
    db.flush()
    # 重新加载以拿到 tag_rows 与 category
    g = repositories.get_game(db, g.id)
    result = game_out(g)
    db.commit()
    return result


def admin_update_game(db, user: User, game_id: int, body: AdminGameUpdateReq) -> dict:
    require_role(user, "admin")
    game = repositories.get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="游戏不存在")
    data = body.model_dump(exclude_unset=True)
    values = {k: v for k, v in data.items() if k != "tags"}
    tags = data.get("tags")
    repositories.update_game(db, game, values, tags)
    db.flush()
    result = game_out(game)
    db.commit()
    return result


def admin_list_categories(db, user: User) -> dict:
    require_role(user, "admin")
    return {"items": [category_out(c) for c in repositories.list_categories(db)]}


def admin_create_category(db, user: User, body: AdminCategoryReq) -> dict:
    require_role(user, "admin")
    if not body.name:
        raise HTTPException(status_code=400, detail="分类名必填")
    c = repositories.create_category(db, body.name)
    db.commit()
    return {"id": c.id, "name": c.name}


def admin_update_category(db, user: User, category_id: int,
                          body: AdminCategoryReq) -> dict:
    require_role(user, "admin")
    c = repositories.get_category(db, category_id)
    if c is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    repositories.update_category(db, c, body.name or c.name)
    db.commit()
    return {"id": c.id, "name": c.name}


def admin_delete_category(db, user: User, category_id: int) -> dict:
    require_role(user, "admin")
    c = repositories.get_category(db, category_id)
    if c is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    if repositories.has_games_in_category(db, category_id):
        raise HTTPException(status_code=400, detail="该分类下仍有游戏，无法删除")
    repositories.delete_category(db, c)
    db.commit()
    return {"message": "分类已删除"}


def admin_audit_logs(db, user: User) -> dict:
    require_role(user, "admin")
    logs = repositories.list_audit_logs(db)
    items = []
    for l in logs:
        items.append({
            "id": l.id,
            "review_id": l.review_id,
            "audit_type": l.audit_type,
            "risk_score": l.risk_score,
            "reason": l.reason,
            "operator_id": l.operator_id,
            "created_at": _iso(l.created_at),
            "review_title": l.review.title if l.review else "#" + str(l.review_id),
        })
    return {"items": items}


def admin_list_comments(db, user: User) -> dict:
    require_role(user, "admin")
    comments = repositories.list_all_comments(db)
    review_ids = {c.target_id for c in comments if c.target_type == "review"}
    game_ids = {c.target_id for c in comments if c.target_type == "game"}
    reviews_map: dict = {}
    games_map: dict = {}
    if review_ids:
        for r in db.query(Review).filter(Review.id.in_(review_ids)).all():
            reviews_map[r.id] = r.title
    if game_ids:
        for g in db.query(Game).filter(Game.id.in_(game_ids)).all():
            games_map[g.id] = g.name
    items = []
    for c in comments:
        if c.target_type == "review":
            target_title = reviews_map.get(c.target_id, "#" + str(c.target_id))
        else:
            target_title = games_map.get(c.target_id, "#" + str(c.target_id))
        items.append({
            "id": c.id,
            "content": c.content,
            "author": c.author.username if c.author else "",
            "author_id": c.user_id,
            "target_type": c.target_type,
            "target_id": c.target_id,
            "target_title": target_title,
            "review_title": reviews_map.get(c.target_id, "")
            if c.target_type == "review" else "",
            "like_count": c.like_count or 0,
            "created_at": _iso(c.created_at),
        })
    return {"items": items}


def admin_delete_comment(db, user: User, comment_id: int) -> dict:
    """管理员删除违规评论（自动精选为运行时计算，删除后自动重算，无需人工干预）。"""
    require_role(user, "admin")
    c = repositories.get_comment(db, comment_id)
    if c is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    repositories.delete_comment(db, comment_id)
    db.commit()
    return {"message": "评论已删除"}


# ==================== 社区模块 ====================

POST_REPORT_REASONS = ["垃圾广告", "辱骂攻击", "色情低俗", "违法违规", "诈骗引流", "其他"]


def _author_out(post) -> dict:
    return {
        "id": post.user_id,
        "name": post.author_name,
        "avatar": post.author_avatar or "",
    }


def _post_summary(content: str) -> str:
    text = re.sub(r"\s+", " ", (content or "").strip())
    return text[:120] + ("…" if len(text) > 120 else "")


def post_out(db, post, *, viewer_id: Optional[int] = None,
             viewer_role: str = "", full: bool = False, flags: Optional[dict] = None) -> dict:
    """帖子卡片/详情输出。viewer_id 非空时附带 my_liked/my_favorited；
    flags 可传入批量预取的标记字典避免 N+1。"""
    if flags is None:
        flags = (repositories.user_post_flags(db, viewer_id, [post.id])
                 .get(post.id, {"liked": False, "fav": False})) if viewer_id else {"liked": False, "fav": False}
    else:
        flags = flags.get(post.id, {"liked": False, "fav": False})
    data = {
        "id": post.id,
        "title": post.title,
        "tag": post.tag,
        "author": _author_out(post),
        "images": post.image_list if full else post.image_list[:3],
        "image_count": len(post.image_list),
        "view_count": post.view_count or 0,
        "like_count": post.like_count or 0,
        "fav_count": post.fav_count or 0,
        "comment_count": post.comment_count or 0,
        "hot_score": post.hot_score or 0,
        "created_at": _iso(post.created_at),
        "my_liked": flags["liked"],
        "my_favorited": flags["fav"],
        "can_delete": viewer_id is not None and (
            viewer_id == post.user_id or ROLE_ORDER.get(viewer_role, 0) >= 3),
    }
    if full:
        data["content"] = post.content or ""
    else:
        data["summary"] = _post_summary(post.content)
    return data


def community_tags() -> dict:
    return {"tags": repositories.POST_TAGS}


def community_list_posts(db, user: Optional[User], *, sort: str = "hot",
                         tag: Optional[str] = None, keyword: Optional[str] = None,
                         page=None, page_size=None) -> dict:
    if sort not in ("hot", "latest"):
        sort = "hot"
    if tag and tag not in repositories.POST_TAGS:
        tag = None
    posts = repositories.list_posts(db, tag=tag, keyword=keyword, sort=sort)
    paged = _paginate(posts, page, page_size or 10)
    flags = repositories.user_post_flags(db, user.id if user else None,
                                         [p.id for p in paged["items"]])
    paged["items"] = [post_out(db, p, viewer_id=user.id if user else None,
                               viewer_role=user.role if user else "", flags=flags)
                      for p in paged["items"]]
    paged["sort"] = sort
    paged["tag"] = tag or ""
    paged["keyword"] = keyword or ""
    return paged


def community_post_detail(db, user: Optional[User], post_id: int) -> dict:
    post = repositories.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在或已被删除")
    repositories.bump_post_view(db, post)
    db.commit()
    db.refresh(post)
    return post_out(db, post, viewer_id=user.id if user else None,
                    viewer_role=user.role if user else "", full=True)


def _validate_images(images) -> List[str]:
    if not isinstance(images, list):
        raise HTTPException(status_code=400, detail="images 必须为数组")
    urls = []
    for u in images[:9]:
        if not isinstance(u, str):
            continue
        if u.startswith("/static/uploads/") or u.startswith("http://") or u.startswith("https://"):
            urls.append(u)
    return urls


def community_create_post(db, user: User, body: CommunityPostCreateReq) -> dict:
    title = (body.title or "").strip()
    content = (body.content or "").strip()
    if not (2 <= len(title) <= 100):
        raise HTTPException(status_code=400, detail="标题需 2-100 字")
    if not content and not body.images:
        raise HTTPException(status_code=400, detail="正文和图片至少填一项")
    if len(content) > 10000:
        raise HTTPException(status_code=400, detail="正文过长（上限 10000 字）")
    try:
        moderation.assert_clean(title, content)
        moderation.check_frequency(repositories.last_post_time(db, user.id),
                                   moderation.POST_INTERVAL_SECONDS, "发帖")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    images = _validate_images(body.images)
    if body.tag not in repositories.POST_TAGS:
        raise HTTPException(status_code=400, detail="标签不合法")
    post = repositories.create_post(
        db, user_id=user.id, title=title, content=content,
        images=images, tag=body.tag)
    db.commit()
    db.refresh(post)
    return {"message": "发布成功", "post": post_out(db, post, viewer_id=user.id, full=True)}


def community_delete_post(db, user: User, post_id: int) -> dict:
    post = repositories.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在或已被删除")
    if post.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="只能删除自己的帖子")
    repositories.delete_post(db, post)
    db.commit()
    return {"message": "帖子已删除"}


def community_toggle_like(db, user: User, post_id: int) -> dict:
    liked, post = repositories.toggle_post_like(db, user.id, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if liked and post.user_id != user.id:
        # 消息通知：帖子被点赞 → 通知帖子作者
        notify.push(db, post.user_id, "like",
                    "「%s」赞了你的帖子" % (user.nickname or user.username),
                    _post_summary(post.content),
                    actor_id=user.id, target_type="post", target_id=post.id)
    db.commit()
    return {"liked": liked, "like_count": post.like_count}


def community_toggle_favorite(db, user: User, post_id: int) -> dict:
    fav, post = repositories.toggle_post_favorite(db, user.id, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if fav and post.user_id != user.id:
        # 消息通知：帖子被收藏 → 通知帖子作者
        notify.push(db, post.user_id, "favorite",
                    "「%s」收藏了你的帖子" % (user.nickname or user.username),
                    _post_summary(post.content),
                    actor_id=user.id, target_type="post", target_id=post.id)
    db.commit()
    return {"favorited": fav, "fav_count": post.fav_count}


# ---------------- 帖子评论（楼中楼） ----------------

def _post_comment_out(db, c, viewer_id: Optional[int], liked_ids: set) -> dict:
    return {
        "id": c.id,
        "post_id": c.post_id,
        "parent_id": c.parent_id,
        "content": c.content,
        "author": {
            "id": c.user_id,
            "name": c.author_name,
            "avatar": c.author_avatar or "",
        },
        "like_count": c.like_count or 0,
        "my_liked": c.id in liked_ids,
        "created_at": _iso(c.created_at),
        "replies": [],
    }


def community_list_comments(db, user: Optional[User], post_id: int) -> dict:
    post = repositories.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在或已被删除")
    comments = repositories.list_post_comments(db, post_id)
    liked_ids = repositories.liked_comment_ids(
        db, user.id if user else None, [c.id for c in comments])
    by_id = {}
    tops = []
    viewer_id = user.id if user else None
    is_post_author = viewer_id is not None and viewer_id == post.user_id
    is_admin = viewer_id is not None and user.role == "admin"
    for c in comments:
        node = _post_comment_out(db, c, viewer_id, liked_ids)
        node["can_delete"] = (viewer_id is not None and
                              (viewer_id == c.user_id or is_post_author or is_admin))
        by_id[c.id] = node
    for c in comments:
        node = by_id[c.id]
        if c.parent_id and c.parent_id in by_id:
            by_id[c.parent_id]["replies"].append(node)
        else:
            tops.append(node)
    # 楼中楼回复按时间正序（对话顺序）
    for node in by_id.values():
        node["reply_count"] = len(node["replies"])
        node["replies"].sort(key=lambda r: r["created_at"] or "")
    return {"items": tops, "total": len(comments)}


def community_create_comment(db, user: User, post_id: int,
                             body: CommunityPostCommentReq) -> dict:
    post = repositories.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在或已被删除")
    content = (body.content or "").strip()
    if not (1 <= len(content) <= 1000):
        raise HTTPException(status_code=400, detail="评论需 1-1000 字")
    parent_id = body.parent_id
    if parent_id:
        parent = repositories.get_post_comment(db, parent_id)
        if parent is None or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="回复的评论不存在")
        # 统一两层：回复挂在一级评论下
        parent_id = parent.parent_id or parent.id
    try:
        moderation.assert_clean(content)
        moderation.check_frequency(repositories.last_comment_time(db, user.id),
                                   moderation.COMMENT_INTERVAL_SECONDS, "评论")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    c = repositories.create_post_comment(
        db, post_id=post_id, user_id=user.id, content=content, parent_id=parent_id)
    # 消息通知：回复楼中楼 → 通知被回复的评论作者；新评论 → 通知帖子作者
    if parent_id:
        parent = repositories.get_post_comment(db, parent_id)
        if parent is not None and parent.user_id != user.id:
            notify.push(db, parent.user_id, "reply",
                        "「%s」回复了你在帖子的评论" % (user.nickname or user.username),
                        content[:80], actor_id=user.id,
                        target_type="post", target_id=post_id)
    elif post.user_id != user.id:
        notify.push(db, post.user_id, "reply",
                    "「%s」评论了你的帖子" % (user.nickname or user.username),
                    content[:80], actor_id=user.id,
                    target_type="post", target_id=post_id)
    db.commit()
    db.refresh(c)
    return {"message": "评论成功", "comment": {
        "id": c.id, "post_id": c.post_id, "parent_id": c.parent_id,
        "content": c.content, "like_count": 0, "my_liked": False,
        "author": {"id": user.id, "name": user.nickname or user.username,
                   "avatar": user.avatar or ""},
        "created_at": _iso(c.created_at), "replies": [], "reply_count": 0,
        "can_delete": True}}


def community_delete_comment(db, user: User, comment_id: int) -> dict:
    c = repositories.get_post_comment(db, comment_id)
    if c is None:
        raise HTTPException(status_code=404, detail="评论不存在或已被删除")
    post = repositories.get_post(db, c.post_id)
    is_post_author = post is not None and post.user_id == user.id
    if c.user_id != user.id and not is_post_author and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除该评论")
    repositories.delete_post_comment(db, c)
    db.commit()
    return {"message": "评论已删除"}


def community_toggle_comment_like(db, user: User, comment_id: int) -> dict:
    liked, c = repositories.toggle_post_comment_like(db, user.id, comment_id)
    if c is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    if liked:
        # 消息通知：帖子评论被点赞 → 通知评论作者（跳转到帖子页）
        notify.push(db, c.user_id, "like",
                    "「%s」赞了你的评论" % (user.nickname or user.username),
                    (c.content or "")[:40],
                    actor_id=user.id, target_type="post", target_id=c.post_id)
    db.commit()
    return {"liked": liked, "like_count": c.like_count}


# ---------------- 举报 ----------------

def community_create_report(db, user: User, body: ReportCreateReq) -> dict:
    if body.target_type not in ("post", "comment"):
        raise HTTPException(status_code=400, detail="举报对象类型不合法")
    if body.reason not in POST_REPORT_REASONS:
        raise HTTPException(status_code=400, detail="举报理由不合法")
    if body.target_type == "post":
        if repositories.get_post(db, body.target_id) is None:
            raise HTTPException(status_code=404, detail="帖子不存在")
    else:
        if repositories.get_post_comment(db, body.target_id) is None:
            raise HTTPException(status_code=404, detail="评论不存在")
    detail = (body.detail or "").strip()[:500] or None
    repositories.create_report(
        db, reporter_id=user.id, target_type=body.target_type,
        target_id=body.target_id, reason=body.reason, detail=detail)
    db.commit()
    return {"message": "举报已提交，管理员会尽快处理"}


# ---------------- 个人主页：我的帖子/收藏/点赞 ----------------

def community_user_posts(db, viewer: Optional[User], target_user_id: int,
                         tab: str, page=None, page_size=None) -> dict:
    target = repositories.get_user_by_id(db, target_user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if tab == "favorites":
        # 收藏仅本人可见
        if not viewer or viewer.id != target_user_id:
            raise HTTPException(status_code=403, detail="收藏列表仅本人可见")
        posts = repositories.list_favorited_posts(db, target_user_id)
    elif tab == "likes":
        if not viewer or viewer.id != target_user_id:
            raise HTTPException(status_code=403, detail="点赞记录仅本人可见")
        posts = repositories.list_liked_posts(db, target_user_id)
    else:
        tab = "posts"
        posts = repositories.list_posts(db, user_id=target_user_id, sort="latest")
    paged = _paginate(posts, page, page_size or 10)
    flags = repositories.user_post_flags(db, viewer.id if viewer else None,
                                         [p.id for p in paged["items"]])
    paged["items"] = [post_out(db, p, viewer_id=viewer.id if viewer else None,
                               viewer_role=viewer.role if viewer else "", flags=flags)
                      for p in paged["items"]]
    paged["tab"] = tab
    paged["user"] = {"id": target.id, "name": target.nickname or target.username,
                     "avatar": target.avatar or ""}
    return paged


# ---------------- 管理员：帖子治理 + 举报处理 ----------------

def admin_list_community_posts(db, user: User, keyword: Optional[str] = None) -> dict:
    require_role(user, "admin")
    posts = repositories.list_posts(db, keyword=keyword, sort="latest")
    pending_report_ids = {r.target_id for r in repositories.list_reports(db, "pending")
                          if r.target_type == "post"}
    return {"items": [{
        "id": p.id,
        "title": p.title,
        "tag": p.tag,
        "author": p.author_name,
        "author_id": p.user_id,
        "summary": _post_summary(p.content),
        "like_count": p.like_count or 0,
        "fav_count": p.fav_count or 0,
        "comment_count": p.comment_count or 0,
        "view_count": p.view_count or 0,
        "reported": p.id in pending_report_ids,
        "created_at": _iso(p.created_at),
    } for p in posts]}


def admin_delete_community_post(db, user: User, post_id: int) -> dict:
    require_role(user, "admin")
    post = repositories.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    repositories.delete_post(db, post)
    db.commit()
    return {"message": "帖子已删除"}


def _report_out(db, r) -> dict:
    target_title, target_author_id = "", None
    if r.target_type == "post":
        p = repositories.get_post(db, r.target_id)
        if p:
            target_title = p.title
            target_author_id = p.user_id
    else:
        c = repositories.get_post_comment(db, r.target_id)
        if c:
            target_title = _post_summary(c.content)
            target_author_id = c.user_id
    return {
        "id": r.id,
        "target_type": r.target_type,
        "target_id": r.target_id,
        "target_title": target_title,
        "target_exists": bool(target_title) or (
            repositories.get_post(db, r.target_id) is not None
            if r.target_type == "post"
            else repositories.get_post_comment(db, r.target_id) is not None),
        "target_author_id": target_author_id,
        "reason": r.reason,
        "detail": r.detail or "",
        "status": r.status,
        "handle_note": r.handle_note or "",
        "reporter": r.reporter.username if r.reporter else "",
        "created_at": _iso(r.created_at),
        "handled_at": _iso(r.handled_at),
    }


def admin_list_reports(db, user: User, status: Optional[str] = None) -> dict:
    require_role(user, "admin")
    reports = repositories.list_reports(db, status or "pending")
    return {"items": [_report_out(db, r) for r in reports]}


def admin_handle_report(db, user: User, report_id: int,
                        body: AdminReportHandleReq) -> dict:
    """举报处理：dismiss=驳回举报；remove=删除违规内容；ban=删除内容并封禁作者。"""
    require_role(user, "admin")
    if body.action not in ("dismiss", "remove", "ban"):
        raise HTTPException(status_code=400, detail="action 不合法")
    r = repositories.get_report(db, report_id)
    if r is None:
        raise HTTPException(status_code=404, detail="举报不存在")
    if r.status != "pending":
        raise HTTPException(status_code=400, detail="该举报已处理")

    target_author_id = None
    if body.action in ("remove", "ban"):
        if r.target_type == "post":
            target = repositories.get_post(db, r.target_id)
            if target is None:
                raise HTTPException(status_code=404, detail="被举报帖子已不存在")
            target_author_id = target.user_id
            repositories.delete_post(db, target)
        else:
            target = repositories.get_post_comment(db, r.target_id)
            if target is None:
                raise HTTPException(status_code=404, detail="被举报评论已不存在")
            target_author_id = target.user_id
            repositories.delete_post_comment(db, target)
        if body.action == "ban" and target_author_id:
            author = repositories.get_user_by_id(db, target_author_id)
            if author and author.role != "admin":
                author.is_active = False

    note = body.note or {"dismiss": "驳回举报", "remove": "已删除违规内容",
                         "ban": "已删除违规内容并封禁作者"}[body.action]
    repositories.mark_report(db, r, status="handled" if body.action != "dismiss" else "dismissed",
                             handler_id=user.id, note=note)
    db.commit()
    return {"message": "处理完成", "status": r.status}
