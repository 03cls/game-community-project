"""SQLAlchemy ORM 模型：对应 database/script.sql 的 12 张表。

一模块一文件在小型项目会过度碎片化，这里集中声明以便维护表间关系。
标签以独立表存储（game_tags / review_tags），模型上通过 tags 属性暴露为字符串列表。
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def _pk():
    """跨库主键：SQLite 用 INTEGER（支持 rowid 自增），MySQL 用 BIGINT（匹配 script.sql）。"""
    return Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = "users"

    id = _pk()
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False, comment="bcrypt 哈希")
    role = Column(String(10), nullable=False, default="player")  # player/creator/admin
    is_active = Column(Boolean, nullable=False, default=True)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    # 创作者积分与等级（仅 role=creator/admin 有意义；积分变动见 point_records 流水）
    creator_points = Column(Float, nullable=False, default=0.0)
    creator_level = Column(Integer, nullable=False, default=0)  # L0-L4，由积分自动推导
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = relationship("Review", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    play_records = relationship("PlayRecord", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("CreatorApplication", back_populates="user", cascade="all, delete-orphan")
    game_ratings = relationship("GameRating", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("CommunityPost", back_populates="author", cascade="all, delete-orphan")
    post_comments = relationship("PostComment", back_populates="author", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="reporter", cascade="all, delete-orphan")
    point_records = relationship("PointRecord", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    games = relationship("Game", back_populates="category")


class GameTag(Base):
    __tablename__ = "game_tags"

    id = _pk()
    game_id = Column(BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String(50), nullable=False, index=True)

    game = relationship("Game", back_populates="tag_rows")


class Game(Base):
    __tablename__ = "games"

    id = _pk()
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    developer = Column(String(100), nullable=True)
    cover_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    release_date = Column(String(20), nullable=True)  # ISO 日期串，避免跨库日期类型差异
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    average_score = Column(Float, nullable=False, default=0.0)  # 综合总评分（由公开评测聚合，管理员不可手动修改）
    steam_url = Column(String(255), nullable=False, default="")  # Steam 商店完整地址，空则前端隐藏购买按钮
    # 四维维度平均分（聚合自全部公开评测的打分）
    score_story = Column(Float, nullable=False, default=0.0)    # 剧情
    score_graphic = Column(Float, nullable=False, default=0.0)  # 画面
    score_gameplay = Column(Float, nullable=False, default=0.0)  # 玩法
    score_opt = Column(Float, nullable=False, default=0.0)      # 性能优化
    rating_count = Column(Integer, nullable=False, default=0)   # 参与评分的公开评测数量
    is_online = Column(Boolean, nullable=False, default=True, index=True)
    hot = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="games")
    tag_rows = relationship("GameTag", back_populates="game", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="game")
    ratings = relationship("GameRating", back_populates="game", cascade="all, delete-orphan")

    @property
    def tags(self) -> List[str]:
        return [row.tag for row in (self.tag_rows or [])]

    @property
    def category_name(self) -> str:
        return self.category.name if self.category else ""


class ReviewTag(Base):
    __tablename__ = "review_tags"

    id = _pk()
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String(50), nullable=False)

    review = relationship("Review", back_populates="tag_rows")


class Review(Base):
    __tablename__ = "reviews"

    id = _pk()
    game_id = Column(BigInteger, ForeignKey("games.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    # 创作者提交时的四维评分（1-10），后端聚合公开评测写入 games 表
    score_story = Column(Integer, nullable=True)    # 剧情
    score_graphic = Column(Integer, nullable=True)  # 画面
    score_gameplay = Column(Integer, nullable=True)  # 玩法
    score_opt = Column(Integer, nullable=True)      # 性能优化
    status = Column(String(20), nullable=False, default="draft", index=True)
    # draft/audit/manual_review/published/rejected
    audit_status = Column(String(20), nullable=True)  # passed/manual_review/rejected
    audit_score = Column(Integer, nullable=True)
    audit_reason = Column(Text, nullable=True)
    read_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    fav_count = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False, index=True)  # 管理员标记精选
    edit_used = Column(Boolean, nullable=False, default=False)  # L1 权益：每篇已发布评测可编辑 1 次
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    game = relationship("Game", back_populates="reviews")
    author = relationship("User", back_populates="reviews")
    tag_rows = relationship("ReviewTag", back_populates="review", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="review", cascade="all, delete-orphan")
    likes = relationship("ReviewLike", back_populates="review", cascade="all, delete-orphan")
    favs = relationship("ReviewFavorite", back_populates="review", cascade="all, delete-orphan")

    @property
    def tags(self) -> List[str]:
        return [row.tag for row in (self.tag_rows or [])]

    @property
    def author_name(self) -> str:
        if self.author and self.author.nickname:
            return self.author.nickname
        return self.author.username if self.author else "未知"

    @property
    def author_avatar(self) -> str:
        return self.author.avatar if self.author else ""

    @property
    def game_name(self) -> str:
        return self.game.name if self.game else ""

    @property
    def game_cover(self) -> str:
        return self.game.cover_url if self.game else ""


class Comment(Base):
    __tablename__ = "comments"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(20), nullable=False, default="review")
    target_id = Column(BigInteger, nullable=False, index=True)
    parent_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    author = relationship("User", back_populates="comments")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")
    parent = relationship("Comment", remote_side=[id], backref="children")

    @property
    def author_name(self) -> str:
        if self.author and self.author.nickname:
            return self.author.nickname
        return self.author.username if self.author else "未知"


class CommentLike(Base):
    __tablename__ = "comment_likes"
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_comment_user_like"),
    )

    id = _pk()
    comment_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    comment = relationship("Comment", back_populates="likes")


class ReviewLike(Base):
    """用户对评测攻略的点赞（联合唯一，幂等切换）。"""
    __tablename__ = "review_likes"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_user_like"),
    )

    id = _pk()
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    review = relationship("Review", back_populates="likes")


class ReviewFavorite(Base):
    """用户对评测攻略的收藏（联合唯一，幂等切换）。"""
    __tablename__ = "review_favorites"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_user_fav"),
    )

    id = _pk()
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    review = relationship("Review", back_populates="favs")


class PointRecord(Base):
    """创作者积分流水：每次积分变动一条记录，余额扣减/清零都可追溯。"""
    __tablename__ = "point_records"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    change = Column(Float, nullable=False)  # 正为加分、负为扣分
    reason = Column(String(200), nullable=False)
    related_type = Column(String(20), nullable=False, default="")  # review / system
    related_id = Column(BigInteger, nullable=True)
    balance_after = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="point_records")


class GameRating(Base):
    """用户对游戏的 1-10 分数字评分。同一用户对单款游戏仅一条（联合唯一），支持改分。"""
    __tablename__ = "game_ratings"
    __table_args__ = (
        UniqueConstraint("game_id", "user_id", name="uq_game_user_rating"),
    )

    id = _pk()
    game_id = Column(BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # 1-10 综合分（四维均值或直填）
    # 四维细化评分（1-10，可空：兼容旧数据/仅综合分）
    score_story = Column(Integer, nullable=True)    # 剧情
    score_graphic = Column(Integer, nullable=True)  # 画面
    score_gameplay = Column(Integer, nullable=True)  # 玩法
    score_opt = Column(Integer, nullable=True)      # 优化
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    game = relationship("Game", back_populates="ratings")
    user = relationship("User", back_populates="game_ratings")


class Favorite(Base):
    __tablename__ = "favorites"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_id = Column(BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    game = relationship("Game")


class PlayRecord(Base):
    __tablename__ = "play_records"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_id = Column(BigInteger, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    play_status = Column(String(12), nullable=False)  # want/playing/completed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="play_records")
    game = relationship("Game")


class CreatorApplication(Base):
    __tablename__ = "creator_applications"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    apply_reason = Column(Text, nullable=False)
    good_at = Column(String(100), default="")    # 擅长方向（逗号分隔标签）
    experience = Column(Text, default="")        # 游戏经历（选填）
    status = Column(String(10), nullable=False, default="pending", index=True)  # pending/approved/rejected
    audit_user_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = _pk()
    review_id = Column(BigInteger, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    audit_type = Column(String(10), nullable=False)  # ai/manual
    risk_score = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    operator_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    review = relationship("Review", back_populates="audit_logs")


# ==================== 社区模块（帖子/评论/点赞/收藏/举报） ====================

class CommunityPost(Base):
    """社区帖子：全员可发、免审即公开。tag 取 游戏/闲聊/攻略/吐槽 等单选标签。
    images 以 JSON 数组字符串存储多图 URL；互动计数冗余在帖子行上，热度分由 recalc 维护。"""
    __tablename__ = "community_posts"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False, default="")
    images = Column(Text, nullable=False, default="[]")  # JSON 数组：多图 URL
    tag = Column(String(20), nullable=False, default="闲聊", index=True)
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    fav_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    hot_score = Column(Float, nullable=False, default=0.0, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    favorites = relationship("PostFavorite", back_populates="post", cascade="all, delete-orphan")

    @property
    def image_list(self) -> List[str]:
        try:
            data = json.loads(self.images or "[]")
            return [u for u in data if isinstance(u, str)]
        except (ValueError, TypeError):
            return []

    @property
    def author_name(self) -> str:
        if self.author and self.author.nickname:
            return self.author.nickname
        return self.author.username if self.author else "未知"

    @property
    def author_avatar(self) -> str:
        return self.author.avatar if self.author else ""


class PostComment(Base):
    """帖子评论：parent_id 非空即楼中楼回复（统一两层，回复挂在一级评论下）。"""
    __tablename__ = "post_comments"

    id = _pk()
    post_id = Column(BigInteger, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(BigInteger, ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    post = relationship("CommunityPost", back_populates="comments")
    author = relationship("User", back_populates="post_comments")
    likes = relationship("PostCommentLike", back_populates="comment", cascade="all, delete-orphan")
    parent = relationship("PostComment", remote_side=[id], backref="children")

    @property
    def author_name(self) -> str:
        if self.author and self.author.nickname:
            return self.author.nickname
        return self.author.username if self.author else "未知"

    @property
    def author_avatar(self) -> str:
        return self.author.avatar if self.author else ""


class PostLike(Base):
    __tablename__ = "post_likes"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_user_like"),
    )

    id = _pk()
    post_id = Column(BigInteger, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    post = relationship("CommunityPost", back_populates="likes")


class PostFavorite(Base):
    __tablename__ = "post_favorites"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_user_fav"),
    )

    id = _pk()
    post_id = Column(BigInteger, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    post = relationship("CommunityPost", back_populates="favorites")


class PostCommentLike(Base):
    __tablename__ = "post_comment_likes"
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_pcomment_user_like"),
    )

    id = _pk()
    comment_id = Column(BigInteger, ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    comment = relationship("PostComment", back_populates="likes")


class Report(Base):
    """举报：target_type=post/comment；status=pending/handled/dismissed。"""
    __tablename__ = "reports"

    id = _pk()
    reporter_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(10), nullable=False, index=True)  # post/comment
    target_id = Column(BigInteger, nullable=False, index=True)
    reason = Column(String(50), nullable=False, default="其他")
    detail = Column(Text, nullable=True)
    status = Column(String(10), nullable=False, default="pending", index=True)  # pending/handled/dismissed
    handler_id = Column(BigInteger, nullable=True)
    handle_note = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    handled_at = Column(DateTime, nullable=True)

    reporter = relationship("User", back_populates="reports")


class Notification(Base):
    """站内消息通知：type 区分类型（reply/like/favorite/audit/apply/system）；
    target_type + target_id 决定点击跳转位置；actor 为触发者（None=系统消息）。
    通知在业务事务内 db.add()，随业务 commit 一起落库。"""
    __tablename__ = "notifications"

    id = _pk()
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    type = Column(String(20), nullable=False, default="system", index=True)
    title = Column(String(200), nullable=False, default="")
    content = Column(Text, nullable=False, default="")
    actor_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
                      nullable=True)
    target_type = Column(String(20), nullable=True)   # post/review/game/comment
    target_id = Column(BigInteger, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    actor = relationship("User", foreign_keys=[actor_id])

    @property
    def actor_name(self) -> str:
        if self.actor is None:
            return "系统"
        return self.actor.nickname or self.actor.username
