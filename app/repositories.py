"""纯 SQLAlchemy CRUD：只做数据访问，返回 ORM 对象，不含业务逻辑。

业务校验/事务编排放在 services.py。标签以独立表存储，创建/更新时同步 GameTag/ReviewTag。
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased, joinedload, selectinload

from app.models import (
    AuditLog,
    Category,
    Comment,
    CommentLike,
    CommunityPost,
    CreatorApplication,
    Favorite,
    Game,
    GameRating,
    GameTag,
    PlayRecord,
    PostComment,
    PostCommentLike,
    PostFavorite,
    PostLike,
    PointRecord,
    Report,
    Review,
    ReviewFavorite,
    ReviewLike,
    ReviewTag,
    User,
)


# ---------------- 用户 ----------------

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username_or_email(db: Session, key: str) -> Optional[User]:
    return db.query(User).filter(or_(User.username == key, User.email == key)).first()


def create_user(db: Session, *, username: str, email: str, password: str,
                role: str = "player", is_active: bool = True,
                nickname: Optional[str] = None, avatar: str = "",
                bio: str = "") -> User:
    u = User(username=username, email=email, password=password, role=role,
             is_active=is_active, nickname=nickname or username, avatar=avatar, bio=bio)
    db.add(u)
    db.flush()
    return u


def list_users(db: Session, keyword: Optional[str] = None) -> List[User]:
    q = db.query(User)
    if keyword:
        kw = "%" + keyword.lower() + "%"
        q = q.filter(or_(
            User.username.ilike(kw),
            User.email.ilike(kw),
            User.nickname.ilike(kw),
        ))
    return q.order_by(User.id.asc()).all()


def set_user_active(db: Session, user: User, is_active: bool) -> User:
    user.is_active = is_active
    db.flush()
    return user


def set_user_role(db: Session, user: User, role: str) -> User:
    user.role = role
    db.flush()
    return user


# ---------------- 分类 ----------------

def list_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.id.asc()).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, name: str) -> Category:
    c = Category(name=name)
    db.add(c)
    db.flush()
    return c


def update_category(db: Session, category: Category, name: str) -> Category:
    category.name = name
    db.flush()
    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.flush()


def has_games_in_category(db: Session, category_id: int) -> bool:
    return db.query(Game.id).filter(Game.category_id == category_id).first() is not None


# ---------------- 游戏 ----------------

def list_games(db: Session, category_id: Optional[int] = None,
               keyword: Optional[str] = None, sort: str = "hot") -> List[Game]:
    q = db.query(Game).filter(Game.is_online.is_(True))
    if category_id:
        q = q.filter(Game.category_id == category_id)
    if keyword:
        kw = "%" + keyword.lower() + "%"
        tag_game_ids = db.query(GameTag.game_id).filter(GameTag.tag.ilike(kw)).subquery()
        q = q.filter(or_(
            Game.name.ilike(kw),
            Game.name_en.ilike(kw),
            Game.description.ilike(kw),
            Game.id.in_(tag_game_ids),
        ))
    if sort == "newest":
        q = q.order_by(Game.release_date.desc())
    elif sort == "score":
        q = q.order_by(Game.average_score.desc())
    else:
        q = q.order_by(Game.hot.desc())
    return q.all()


def get_game(db: Session, game_id: int) -> Optional[Game]:
    return (db.query(Game)
            .options(selectinload(Game.tag_rows), joinedload(Game.category))
            .filter(Game.id == game_id).first())


def get_game_simple(db: Session, game_id: int) -> Optional[Game]:
    return db.query(Game).filter(Game.id == game_id).first()


def list_all_games(db: Session) -> List[Game]:
    return (db.query(Game).options(selectinload(Game.tag_rows), joinedload(Game.category))
            .order_by(Game.id.asc()).all())


def create_game(db: Session, *, name: str, name_en: str = "", developer: str = "",
                cover_url: str = "", description: str = "",
                release_date: str = "2025-01-01", category_id: int = 1,
                tags: Optional[List[str]] = None, average_score: float = 0.0,
                is_online: bool = True, hot: int = 50) -> Game:
    g = Game(name=name, name_en=name_en, developer=developer, cover_url=cover_url,
             description=description, release_date=release_date, category_id=category_id,
             average_score=average_score, is_online=is_online, hot=hot)
    db.add(g)
    db.flush()
    for t in (tags or []):
        db.add(GameTag(game_id=g.id, tag=t))
    db.flush()
    return g


def update_game(db: Session, game: Game, values: dict,
                tags: Optional[List[str]] = None) -> Game:
    for k, v in values.items():
        setattr(game, k, v)
    if tags is not None:
        # 通过 ORM 关系集合整体替换：cascade="all, delete-orphan" 负责删旧增新，
        # 保证 game.tag_rows 内存集合立即与数据库一致（bulk delete+insert 会导致关系过期不刷新）
        game.tag_rows = [GameTag(tag=t) for t in tags]
    db.flush()
    return game


def find_similar_games(db: Session, game: Game, limit: int = 4) -> List[Game]:
    """相似游戏：同分类 + 标签重合度加权，取前 limit 款（在线、排除自身）。"""
    tags = set(game.tags or [])
    candidates = (db.query(Game)
                  .options(selectinload(Game.tag_rows), joinedload(Game.category))
                  .filter(Game.is_online.is_(True), Game.id != game.id).all())
    scored = []
    for c in candidates:
        s = 0
        if c.category_id == game.category_id:
            s += 2
        s += len(tags & set(c.tags or []))
        if s > 0:
            scored.append((s, c.hot or 0, c.id, c))
    scored.sort(key=lambda x: (x[0], x[1], -x[2]), reverse=True)
    return [c for _, _, _, c in scored[:limit]]


# ---------------- 评测 ----------------

def list_reviews_by_game(db: Session, game_id: int,
                         keyword: Optional[str] = None) -> List[Review]:
    q = (db.query(Review)
         .options(selectinload(Review.tag_rows), joinedload(Review.author),
                  joinedload(Review.game))
         .filter(Review.game_id == game_id, Review.status == "published"))
    if keyword:
        kw = "%" + keyword.lower() + "%"
        q = q.filter(or_(Review.title.ilike(kw), Review.content.ilike(kw)))
    # 排序加权：精选 > 作者等级（L2+ 流量倾斜）> 最新
    return (q.join(User, Review.user_id == User.id)
            .order_by(Review.is_featured.desc(), User.creator_level.desc(),
                      Review.created_at.desc()).all())


def list_public_reviews(db: Session, keyword: Optional[str] = None) -> List[Review]:
    """全部公开评测；精选与高等级创作者加权在前，同级内最新优先。keyword 按游戏名称过滤。"""
    q = (db.query(Review)
         .options(selectinload(Review.tag_rows), joinedload(Review.author),
                  joinedload(Review.game))
         .filter(Review.status == "published"))
    if keyword:
        kw = "%" + keyword.lower() + "%"
        q = q.join(Game, Review.game_id == Game.id).filter(
            or_(Game.name.ilike(kw), Game.name_en.ilike(kw)))
    return (q.join(User, Review.user_id == User.id)
            .order_by(Review.is_featured.desc(), User.creator_level.desc(),
                      Review.created_at.desc(), Review.id.desc()).all())


def count_published_reviews_by_game(db: Session, game_id: int) -> int:
    return (db.query(Review)
            .filter(Review.game_id == game_id, Review.status == "published").count())


def list_reviews_by_user(db: Session, user_id: int, status: Optional[str] = None) -> List[Review]:
    q = (db.query(Review)
         .options(selectinload(Review.tag_rows), joinedload(Review.author),
                  joinedload(Review.game))
         .filter(Review.user_id == user_id))
    if status:
        q = q.filter(Review.status == status)
    return q.order_by(Review.created_at.desc()).all()


def list_pending_reviews(db: Session) -> List[Review]:
    return (db.query(Review)
            .options(selectinload(Review.tag_rows), joinedload(Review.author),
                     joinedload(Review.game))
            .filter(Review.status.in_(["audit", "manual_review"]))
            .order_by(Review.created_at.desc()).all())


def get_review(db: Session, review_id: int) -> Optional[Review]:
    return (db.query(Review)
            .options(selectinload(Review.tag_rows), joinedload(Review.author),
                     joinedload(Review.game))
            .filter(Review.id == review_id).first())


def create_review(db: Session, *, game_id: int, user_id: int, title: str,
                  content: str = "", tags: Optional[List[str]] = None,
                  scores: Optional[dict] = None) -> Review:
    scores = scores or {}
    r = Review(game_id=game_id, user_id=user_id, title=title, content=content,
               score_story=scores.get("score_story"),
               score_graphic=scores.get("score_graphic"),
               score_gameplay=scores.get("score_gameplay"),
               score_opt=scores.get("score_opt"),
               status="draft", audit_status=None, audit_score=None, audit_reason="",
               read_count=0, like_count=0, fav_count=0)
    db.add(r)
    db.flush()
    for t in (tags or []):
        db.add(ReviewTag(review_id=r.id, tag=t))
    db.flush()
    return r


def update_review(db: Session, review: Review, values: dict,
                  tags: Optional[List[str]] = None) -> Review:
    for k, v in values.items():
        setattr(review, k, v)
    if tags is not None:
        # 同 update_game：通过关系集合替换，保证 review.tag_rows 立即刷新
        review.tag_rows = [ReviewTag(tag=t) for t in tags]
    db.flush()
    return review


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.flush()


def update_review_status(db: Session, review: Review, *, status: str,
                         audit_status: Optional[str] = None,
                         audit_score: Optional[int] = None,
                         audit_reason: Optional[str] = None) -> Review:
    review.status = status
    if audit_status is not None:
        review.audit_status = audit_status
    if audit_score is not None:
        review.audit_score = audit_score
    if audit_reason is not None:
        review.audit_reason = audit_reason
    db.flush()
    return review


def set_review_featured(db: Session, review: Review, featured: bool) -> Review:
    review.is_featured = featured
    db.flush()
    return review


def mark_review_edit_used(db: Session, review: Review) -> Review:
    review.edit_used = True
    db.flush()
    return review


# -------- 评测点赞 / 收藏（幂等切换） --------

def get_review_like(db: Session, review_id: int, user_id: int) -> Optional[ReviewLike]:
    return db.query(ReviewLike).filter(
        ReviewLike.review_id == review_id, ReviewLike.user_id == user_id).first()


def get_review_fav(db: Session, review_id: int, user_id: int) -> Optional[ReviewFavorite]:
    return db.query(ReviewFavorite).filter(
        ReviewFavorite.review_id == review_id, ReviewFavorite.user_id == user_id).first()


def list_reviews_liked_by_user(db: Session, user_id: int) -> List[Review]:
    """我点赞过的评测（仅已发布，按点赞时间倒序）。"""
    return db.query(Review).join(
        ReviewLike, ReviewLike.review_id == Review.id
    ).filter(
        ReviewLike.user_id == user_id, Review.status == "published"
    ).order_by(ReviewLike.created_at.desc()).all()


def list_reviews_faved_by_user(db: Session, user_id: int) -> List[Review]:
    """我收藏的评测（仅已发布，按收藏时间倒序）。"""
    return db.query(Review).join(
        ReviewFavorite, ReviewFavorite.review_id == Review.id
    ).filter(
        ReviewFavorite.user_id == user_id, Review.status == "published"
    ).order_by(ReviewFavorite.created_at.desc()).all()


def toggle_review_like(db: Session, review: Review, user_id: int) -> Tuple[bool, int]:
    existing = get_review_like(db, review.id, user_id)
    if existing:
        db.delete(existing)
        review.like_count = max(0, (review.like_count or 1) - 1)
        db.flush()
        return False, review.like_count
    db.add(ReviewLike(review_id=review.id, user_id=user_id))
    review.like_count = (review.like_count or 0) + 1
    db.flush()
    return True, review.like_count


def toggle_review_fav(db: Session, review: Review, user_id: int) -> Tuple[bool, int]:
    existing = get_review_fav(db, review.id, user_id)
    if existing:
        db.delete(existing)
        review.fav_count = max(0, (review.fav_count or 1) - 1)
        db.flush()
        return False, review.fav_count
    db.add(ReviewFavorite(review_id=review.id, user_id=user_id))
    review.fav_count = (review.fav_count or 0) + 1
    db.flush()
    return True, review.fav_count


def list_hall_reviews(db: Session, limit: int = 6) -> List[Review]:
    """首页专题：L3+ 资深/核心创作者的公开评测，等级高在前、热度（阅读量）辅助。"""
    return (db.query(Review)
            .options(selectinload(Review.tag_rows), joinedload(Review.author),
                     joinedload(Review.game))
            .join(User, Review.user_id == User.id)
            .filter(Review.status == "published", User.creator_level >= 3)
            .order_by(User.creator_level.desc(), Review.is_featured.desc(),
                      Review.read_count.desc())
            .limit(limit).all())


# ---------------- 创作者积分流水 ----------------

def add_point_record(db: Session, user: User, change: float, reason: str,
                     related_type: str = "", related_id: Optional[int] = None) -> PointRecord:
    """记录一笔积分变动并自动重算等级。余额扣减时不低于 0。"""
    from app.core import points as pts
    new_balance = max(0.0, round((user.creator_points or 0.0) + round(change, 1), 1))
    user.creator_points = new_balance
    user.creator_level = pts.level_for_points(new_balance)
    rec = PointRecord(
        user_id=user.id, change=round(change, 1), reason=reason,
        related_type=related_type, related_id=related_id,
        balance_after=new_balance)
    db.add(rec)
    db.flush()
    return rec


def reset_creator_points(db: Session, user: User, reason: str) -> PointRecord:
    """积分清零、等级重置 L0（抄袭违规下架）。"""
    change = -(user.creator_points or 0.0)
    return add_point_record(db, user, change, reason)


def sum_points_of_review(db: Session, user_id: int, review_id: int) -> float:
    """汇总某篇评测已发放的全部积分（正反向轧差），用于删帖追回。"""
    total = (db.query(PointRecord)
             .filter(PointRecord.user_id == user_id,
                     PointRecord.related_type == "review",
                     PointRecord.related_id == review_id)
             .all())
    return round(sum((r.change or 0.0) for r in total), 1)


def list_point_records(db: Session, user_id: int) -> List[PointRecord]:
    return (db.query(PointRecord)
            .filter(PointRecord.user_id == user_id)
            .order_by(PointRecord.created_at.desc(), PointRecord.id.desc()).all())


def _round1(x: float) -> float:
    """四舍五入保留 1 位小数（int(x*10+0.5)，避免 Python round 的银行家舍入）。"""
    return int(x * 10 + 0.5) / 10


def recalc_game_scores(db: Session, game_id: int) -> Optional[Game]:
    """聚合写回 games 表（全站唯一评分聚合口径）。

    - 每篇「已发布且带四维评分」的评测贡献 1 人，综合分取其四维均值；
    - 每条用户评分贡献 1 人，综合分取 score（四维齐全时已由四维均值四舍五入得到）；
    - 游戏综合总分 = 所有贡献者综合分的平均值，四舍五入保留 1 位小数；
    - 四维雷达分 = 所有带四维分的贡献者（评测 + 用户评分）按维度平均，保留 1 位小数；
    - 无任何打分时全部归零。
    """
    game = get_game_simple(db, game_id)
    if game is None:
        return None
    rows = (db.query(Review.score_story, Review.score_graphic,
                     Review.score_gameplay, Review.score_opt)
            .filter(Review.game_id == game_id, Review.status == "published",
                    Review.score_story.isnot(None),
                    Review.score_graphic.isnot(None),
                    Review.score_gameplay.isnot(None),
                    Review.score_opt.isnot(None))
            .all())
    user_rows = (db.query(GameRating.score, GameRating.score_story,
                          GameRating.score_graphic, GameRating.score_gameplay,
                          GameRating.score_opt)
                 .filter(GameRating.game_id == game_id).all())
    n_total = len(rows) + len(user_rows)
    total = 0.0
    d_sum = [0.0, 0.0, 0.0, 0.0]  # 剧情/画面/玩法/优化 分子
    d_cnt = [0, 0, 0, 0]           # 各维度参与人数
    for r in rows:
        total += (r[0] + r[1] + r[2] + r[3]) / 4
        for i in range(4):
            d_sum[i] += r[i]
            d_cnt[i] += 1
    for u in user_rows:
        total += u[0]
        for i in range(4):
            v = u[i + 1]
            if v is not None:
                d_sum[i] += v
                d_cnt[i] += 1
    game.score_story = _round1(d_sum[0] / d_cnt[0]) if d_cnt[0] else 0.0
    game.score_graphic = _round1(d_sum[1] / d_cnt[1]) if d_cnt[1] else 0.0
    game.score_gameplay = _round1(d_sum[2] / d_cnt[2]) if d_cnt[2] else 0.0
    game.score_opt = _round1(d_sum[3] / d_cnt[3]) if d_cnt[3] else 0.0
    game.rating_count = n_total
    game.average_score = _round1(total / n_total) if n_total else 0.0
    db.flush()
    return game


# ---------------- 用户游戏评分 ----------------

def get_game_rating(db: Session, user_id: int, game_id: int) -> Optional[GameRating]:
    return (db.query(GameRating)
            .filter(GameRating.user_id == user_id, GameRating.game_id == game_id)
            .first())


def upsert_game_rating(db: Session, user_id: int, game_id: int, score: int,
                       dims: Optional[dict] = None) -> Tuple[GameRating, bool]:
    """同一用户对单款游戏仅保留一条评分；存在则改分，不存在则新建。dims 为四维权（可空）。"""
    rating = get_game_rating(db, user_id, game_id)
    created = rating is None
    if rating is None:
        rating = GameRating(user_id=user_id, game_id=game_id, score=score)
        db.add(rating)
    else:
        rating.score = score
    if dims:
        for k, v in dims.items():
            setattr(rating, k, v)
    db.flush()
    return rating, created


# ---------------- 评论 ----------------

def list_comments(db: Session, target_type: str, target_id: int) -> List[Comment]:
    return (db.query(Comment).options(joinedload(Comment.author))
            .filter(Comment.target_type == target_type, Comment.target_id == target_id)
            .order_by(Comment.created_at.asc()).all())


def list_comments_by_user(db: Session, user_id: int) -> List[Comment]:
    """某用户发表的全部评论（游戏短评论 + 评测评论），时间倒序。"""
    return (db.query(Comment).options(joinedload(Comment.author))
            .filter(Comment.user_id == user_id)
            .order_by(Comment.created_at.desc()).all())


def list_all_comments(db: Session) -> List[Comment]:
    return (db.query(Comment).options(joinedload(Comment.author))
            .order_by(Comment.created_at.desc()).all())


def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    return (db.query(Comment).options(joinedload(Comment.author))
            .filter(Comment.id == comment_id).first())


def create_comment(db: Session, *, user_id: int, target_type: str, target_id: int,
                   parent_id: Optional[int], content: str) -> Comment:
    c = Comment(user_id=user_id, target_type=target_type, target_id=target_id,
                parent_id=parent_id, content=content, like_count=0)
    db.add(c)
    db.flush()
    return c


def delete_comment(db: Session, comment_id: int) -> None:
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if c is not None:
        db.delete(c)
        db.flush()


def toggle_comment_like(db: Session, comment_id: int, user_id: int) -> Tuple[int, bool]:
    existing = (db.query(CommentLike)
                .filter(CommentLike.comment_id == comment_id,
                        CommentLike.user_id == user_id).first())
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if existing is not None:
        db.delete(existing)
        if comment is not None:
            comment.like_count = max(0, (comment.like_count or 0) - 1)
        db.flush()
        return (comment.like_count if comment is not None else 0), False
    db.add(CommentLike(comment_id=comment_id, user_id=user_id))
    if comment is not None:
        comment.like_count = (comment.like_count or 0) + 1
    db.flush()
    return (comment.like_count if comment is not None else 0), True


def get_comment_like(db: Session, comment_id: int, user_id: int) -> Optional[CommentLike]:
    return (db.query(CommentLike)
            .filter(CommentLike.comment_id == comment_id,
                    CommentLike.user_id == user_id).first())


def list_top_liked_comment(db: Session, target_type: str, target_id: int) -> Optional[Comment]:
    """点赞数量最高的评论（并列取创建时间最早），作为自动精选候选。"""
    return (db.query(Comment).options(joinedload(Comment.author))
            .filter(Comment.target_type == target_type, Comment.target_id == target_id)
            .order_by(Comment.like_count.desc(), Comment.created_at.asc(), Comment.id.asc())
            .first())


def list_normal_comments_paginated(db: Session, target_type: str, target_id: int,
                                   page: int, page_size: int,
                                   exclude_id: Optional[int] = None) -> Tuple[List[Comment], int]:
    """普通评论分页：按时间倒序；exclude_id 用于排除自动精选展示的那条。"""
    base = (db.query(Comment)
            .filter(Comment.target_type == target_type, Comment.target_id == target_id))
    if exclude_id is not None:
        base = base.filter(Comment.id != exclude_id)
    total = base.count()
    items = (base.options(joinedload(Comment.author))
             .order_by(Comment.created_at.desc())
             .offset((page - 1) * page_size).limit(page_size).all())
    return items, total


# ---------------- 收藏 ----------------

def list_favorites_by_user(db: Session, user_id: int) -> List[Game]:
    return (db.query(Game).join(Favorite, Favorite.game_id == Game.id)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.id.asc()).all())


def get_favorite(db: Session, user_id: int, game_id: int) -> Optional[Favorite]:
    return (db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.game_id == game_id).first())


def add_favorite(db: Session, user_id: int, game_id: int) -> Favorite:
    f = Favorite(user_id=user_id, game_id=game_id)
    db.add(f)
    db.flush()
    return f


def remove_favorite(db: Session, user_id: int, game_id: int) -> None:
    db.query(Favorite).filter(Favorite.user_id == user_id,
                              Favorite.game_id == game_id).delete()
    db.flush()


# ---------------- 游玩记录 ----------------

def get_play_records(db: Session, user_id: int) -> List[PlayRecord]:
    return (db.query(PlayRecord).options(joinedload(PlayRecord.game))
            .filter(PlayRecord.user_id == user_id)
            .order_by(PlayRecord.id.asc()).all())


def get_play_record(db: Session, user_id: int, game_id: int) -> Optional[PlayRecord]:
    return (db.query(PlayRecord)
            .filter(PlayRecord.user_id == user_id, PlayRecord.game_id == game_id).first())


def upsert_play_record(db: Session, user_id: int, game_id: int, status: str) -> PlayRecord:
    rec = get_play_record(db, user_id, game_id)
    if rec is not None:
        rec.play_status = status
        rec.updated_at = datetime.utcnow()
        db.flush()
        return rec
    rec = PlayRecord(user_id=user_id, game_id=game_id, play_status=status)
    db.add(rec)
    db.flush()
    return rec


# ---------------- 创作者申请 ----------------

def create_creator_application(db: Session, *, user_id: int, apply_reason: str,
                               good_at: str = "", experience: str = "") -> CreatorApplication:
    a = CreatorApplication(user_id=user_id, apply_reason=apply_reason,
                           good_at=good_at or "", experience=experience or "",
                           status="pending", audit_user_id=None)
    db.add(a)
    db.flush()
    return a


def list_applications(db: Session, status: Optional[str] = None) -> List[CreatorApplication]:
    q = db.query(CreatorApplication)
    if status:
        q = q.filter(CreatorApplication.status == status)
    return q.order_by(CreatorApplication.created_at.desc()).all()


def get_pending_application_by_user(db: Session, user_id: int) -> Optional[CreatorApplication]:
    return (db.query(CreatorApplication)
            .filter(CreatorApplication.user_id == user_id,
                    CreatorApplication.status == "pending").first())


def latest_application_by_user(db: Session, user_id: int) -> Optional[CreatorApplication]:
    """用户最近一次申请（个人中心状态展示）。"""
    return (db.query(CreatorApplication)
            .filter(CreatorApplication.user_id == user_id)
            .order_by(CreatorApplication.created_at.desc()).first())


def get_application(db: Session, application_id: int) -> Optional[CreatorApplication]:
    return db.query(CreatorApplication).filter(CreatorApplication.id == application_id).first()


def update_application(db: Session, application: CreatorApplication, *,
                      status: str, audit_user_id: int) -> CreatorApplication:
    application.status = status
    application.audit_user_id = audit_user_id
    db.flush()
    return application


# ---------------- 审核日志 ----------------

def create_audit_log(db: Session, *, review_id: int, audit_type: str,
                     risk_score: Optional[int], reason: str,
                     operator_id: int) -> AuditLog:
    log = AuditLog(review_id=review_id, audit_type=audit_type, risk_score=risk_score,
                   reason=reason, operator_id=operator_id)
    db.add(log)
    db.flush()
    return log


def list_audit_logs(db: Session) -> List[AuditLog]:
    return (db.query(AuditLog).options(joinedload(AuditLog.review))
            .order_by(AuditLog.created_at.desc()).all())


# ---------------- 统计 ----------------

def statistics_for_creator(db: Session, user_id: int) -> dict:
    reviews = db.query(Review).filter(Review.user_id == user_id).all()
    published = [r for r in reviews if r.status == "published"]
    draft = [r for r in reviews if r.status in ("draft", "rejected")]
    return {
        "published_count": len(published),
        "draft_count": len(draft),
        "total_read": sum((r.read_count or 0) for r in published),
        "total_like": sum((r.like_count or 0) for r in published),
        "total_favorite": sum((r.fav_count or 0) for r in published),
    }


def dashboard_stats(db: Session) -> dict:
    user_count = db.query(User).count()
    game_count = db.query(Game).filter(Game.is_online.is_(True)).count()
    review_count = db.query(Review).filter(Review.status == "published").count()
    pending_count = db.query(Review).filter(Review.status.in_(["audit", "manual_review"])).count()
    apply_count = db.query(CreatorApplication).filter(
        CreatorApplication.status == "pending").count()
    return {
        "user_count": user_count,
        "game_count": game_count,
        "review_count": review_count,
        "pending_count": pending_count,
        "apply_count": apply_count,
    }


# ==================== 社区模块 ====================

POST_TAGS = ["游戏", "闲聊", "攻略", "吐槽"]


def get_post(db: Session, post_id: int) -> Optional[CommunityPost]:
    return db.query(CommunityPost).filter(CommunityPost.id == post_id).first()


def list_posts(db: Session, *, tag: Optional[str] = None,
               keyword: Optional[str] = None, sort: str = "hot",
               user_id: Optional[int] = None) -> List[CommunityPost]:
    """帖子列表：hot=热度倒序，latest=发布时间倒序；可按标签/关键词/作者过滤。"""
    q = db.query(CommunityPost)
    if tag:
        q = q.filter(CommunityPost.tag == tag)
    if user_id is not None:
        q = q.filter(CommunityPost.user_id == user_id)
    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.filter(or_(CommunityPost.title.like(like), CommunityPost.content.like(like)))
    if sort == "latest":
        q = q.order_by(CommunityPost.created_at.desc())
    else:
        q = q.order_by(CommunityPost.hot_score.desc(), CommunityPost.created_at.desc())
    return q.all()


def list_favorited_posts(db: Session, user_id: int) -> List[CommunityPost]:
    """用户收藏的帖子（按收藏时间倒序）。"""
    rows = (db.query(CommunityPost, PostFavorite.created_at)
            .join(PostFavorite, PostFavorite.post_id == CommunityPost.id)
            .filter(PostFavorite.user_id == user_id)
            .order_by(PostFavorite.created_at.desc()).all())
    return [r[0] for r in rows]


def list_liked_posts(db: Session, user_id: int) -> List[CommunityPost]:
    """用户点赞过的帖子（按点赞时间倒序）。"""
    rows = (db.query(CommunityPost, PostLike.created_at)
            .join(PostLike, PostLike.post_id == CommunityPost.id)
            .filter(PostLike.user_id == user_id)
            .order_by(PostLike.created_at.desc()).all())
    return [r[0] for r in rows]


def create_post(db: Session, *, user_id: int, title: str, content: str,
                images: List[str], tag: str) -> CommunityPost:
    import json as _json
    post = CommunityPost(
        user_id=user_id, title=title, content=content,
        images=_json.dumps(images, ensure_ascii=False),
        tag=tag if tag in POST_TAGS else "闲聊",
    )
    db.add(post)
    db.flush()
    recalc_post_hot(db, post)
    return post


def delete_post(db: Session, post: CommunityPost) -> None:
    db.delete(post)
    db.flush()


def bump_post_view(db: Session, post: CommunityPost) -> None:
    post.view_count = (post.view_count or 0) + 1
    recalc_post_hot(db, post)
    db.flush()


def toggle_post_like(db: Session, user_id: int, post_id: int) -> Tuple[bool, CommunityPost]:
    """点赞/取消点赞，返回 (当前是否已赞, 帖子)。"""
    post = get_post(db, post_id)
    if post is None:
        return False, None
    row = (db.query(PostLike)
           .filter(PostLike.post_id == post_id, PostLike.user_id == user_id).first())
    if row:
        db.delete(row)
        post.like_count = max(0, (post.like_count or 1) - 1)
        liked = False
    else:
        db.add(PostLike(post_id=post_id, user_id=user_id))
        post.like_count = (post.like_count or 0) + 1
        liked = True
    recalc_post_hot(db, post)
    db.flush()
    return liked, post


def toggle_post_favorite(db: Session, user_id: int, post_id: int) -> Tuple[bool, CommunityPost]:
    post = get_post(db, post_id)
    if post is None:
        return False, None
    row = (db.query(PostFavorite)
           .filter(PostFavorite.post_id == post_id, PostFavorite.user_id == user_id).first())
    if row:
        db.delete(row)
        post.fav_count = max(0, (post.fav_count or 1) - 1)
        fav = False
    else:
        db.add(PostFavorite(post_id=post_id, user_id=user_id))
        post.fav_count = (post.fav_count or 0) + 1
        fav = True
    recalc_post_hot(db, post)
    db.flush()
    return fav, post


def user_post_flags(db: Session, user_id: Optional[int], post_ids: List[int]) -> dict:
    """批量返回某用户对这些帖子的点赞/收藏标记：{post_id: {"liked": bool, "fav": bool}}。"""
    flags = {pid: {"liked": False, "fav": False} for pid in post_ids}
    if not user_id or not post_ids:
        return flags
    for r in db.query(PostLike.post_id).filter(
            PostLike.user_id == user_id, PostLike.post_id.in_(post_ids)).all():
        flags[r[0]]["liked"] = True
    for r in db.query(PostFavorite.post_id).filter(
            PostFavorite.user_id == user_id, PostFavorite.post_id.in_(post_ids)).all():
        flags[r[0]]["fav"] = True
    return flags


def recalc_post_hot(db: Session, post: CommunityPost) -> None:
    """热度分（小黑盒思路：互动权重 + 时间重力衰减）。
    权重：评论 4 > 收藏 3 > 点赞 2 > 浏览 0.05；发布越久分越低。"""
    base = ((post.like_count or 0) * 2
            + (post.fav_count or 0) * 3
            + (post.comment_count or 0) * 4
            + (post.view_count or 0) * 0.05)
    age_hours = max(0.0, (datetime.utcnow() - post.created_at).total_seconds() / 3600.0)
    post.hot_score = round(base / ((age_hours + 2.0) ** 1.5), 4)


def recalc_all_post_hot(db: Session) -> None:
    for post in db.query(CommunityPost).all():
        recalc_post_hot(db, post)
    db.flush()


# ---------------- 帖子评论（楼中楼） ----------------

def list_post_comments(db: Session, post_id: int) -> List[PostComment]:
    return (db.query(PostComment)
            .filter(PostComment.post_id == post_id)
            .order_by(PostComment.like_count.desc(), PostComment.created_at.asc())
            .all())


def get_post_comment(db: Session, comment_id: int) -> Optional[PostComment]:
    return db.query(PostComment).filter(PostComment.id == comment_id).first()


def create_post_comment(db: Session, *, post_id: int, user_id: int,
                        content: str, parent_id: Optional[int]) -> PostComment:
    c = PostComment(post_id=post_id, user_id=user_id,
                    content=content, parent_id=parent_id)
    db.add(c)
    post = get_post(db, post_id)
    if post:
        post.comment_count = (post.comment_count or 0) + 1
        recalc_post_hot(db, post)
    db.flush()
    return c


def delete_post_comment(db: Session, comment: PostComment) -> None:
    """删除评论（楼中楼回复随父评论级联删除），并重算帖子评论数与热度。"""
    post_id = comment.post_id
    db.delete(comment)
    db.flush()
    post = get_post(db, post_id)
    if post:
        post.comment_count = db.query(PostComment).filter(
            PostComment.post_id == post_id).count()
        recalc_post_hot(db, post)
        db.flush()


def toggle_post_comment_like(db: Session, user_id: int, comment_id: int) -> Tuple[bool, PostComment]:
    c = get_post_comment(db, comment_id)
    if c is None:
        return False, None
    row = (db.query(PostCommentLike)
           .filter(PostCommentLike.comment_id == comment_id,
                   PostCommentLike.user_id == user_id).first())
    if row:
        db.delete(row)
        c.like_count = max(0, (c.like_count or 1) - 1)
        liked = False
    else:
        db.add(PostCommentLike(comment_id=comment_id, user_id=user_id))
        c.like_count = (c.like_count or 0) + 1
        liked = True
    db.flush()
    return liked, c


def liked_comment_ids(db: Session, user_id: Optional[int], comment_ids: List[int]) -> set:
    if not user_id or not comment_ids:
        return set()
    rows = (db.query(PostCommentLike.comment_id)
            .filter(PostCommentLike.user_id == user_id,
                    PostCommentLike.comment_id.in_(comment_ids)).all())
    return {r[0] for r in rows}


def last_post_time(db: Session, user_id: int) -> Optional[datetime]:
    row = (db.query(CommunityPost.created_at)
           .filter(CommunityPost.user_id == user_id)
           .order_by(CommunityPost.created_at.desc()).first())
    return row[0] if row else None


def last_comment_time(db: Session, user_id: int) -> Optional[datetime]:
    row = (db.query(PostComment.created_at)
           .filter(PostComment.user_id == user_id)
           .order_by(PostComment.created_at.desc()).first())
    return row[0] if row else None


# ---------------- 举报 ----------------

def create_report(db: Session, *, reporter_id: int, target_type: str,
                  target_id: int, reason: str, detail: Optional[str]) -> Report:
    r = Report(reporter_id=reporter_id, target_type=target_type,
               target_id=target_id, reason=reason, detail=detail)
    db.add(r)
    db.flush()
    return r


def get_report(db: Session, report_id: int) -> Optional[Report]:
    return db.query(Report).filter(Report.id == report_id).first()


def list_reports(db: Session, status: Optional[str] = None) -> List[Report]:
    q = db.query(Report)
    if status:
        q = q.filter(Report.status == status)
    return q.order_by(Report.created_at.desc()).all()


def mark_report(db: Session, report: Report, *, status: str,
                handler_id: int, note: str) -> Report:
    report.status = status
    report.handler_id = handler_id
    report.handle_note = note
    report.handled_at = datetime.utcnow()
    db.flush()
    return report
