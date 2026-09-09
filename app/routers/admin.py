from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.base import get_db
from app.models import User
from app.schemas import (
    AdminApplyDealReq,
    AdminCategoryReq,
    AdminGameCreateReq,
    AdminGameUpdateReq,
    AdminReportHandleReq,
    AdminReviewAuditReq,
    AdminUserRoleReq,
    AdminUserStatusReq,
)
from app import services

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard")
def dashboard(user: User = Depends(require_role("admin")),
              db: Session = Depends(get_db)):
    return services.admin_dashboard(db, user)


@router.get("/users")
def list_users(keyword: Optional[str] = None,
               user: User = Depends(require_role("admin")),
               db: Session = Depends(get_db)):
    return services.admin_list_users(db, user, keyword)


@router.put("/users/{user_id}/status")
def update_user_status(user_id: int, body: AdminUserStatusReq,
                       user: User = Depends(require_role("admin")),
                       db: Session = Depends(get_db)):
    return services.admin_update_user_status(db, user, user_id, body)


@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, body: AdminUserRoleReq,
                     user: User = Depends(require_role("admin")),
                     db: Session = Depends(get_db)):
    return services.admin_update_user_role(db, user, user_id, body)


@router.get("/creator-apply")
def list_applications(status: Optional[str] = None,
                      user: User = Depends(require_role("admin")),
                      db: Session = Depends(get_db)):
    return services.admin_list_applications(db, user, status)


@router.put("/creator-apply/{application_id}/deal")
def deal_application(application_id: int, body: AdminApplyDealReq,
                     user: User = Depends(require_role("admin")),
                     db: Session = Depends(get_db)):
    return services.admin_deal_application(db, user, application_id, body)


@router.get("/reviews/pending")
def pending_reviews(user: User = Depends(require_role("admin")),
                    db: Session = Depends(get_db)):
    return services.admin_pending_reviews(db, user)


@router.post("/reviews/{review_id}/audit-decision")
def review_audit_decision(review_id: int, body: AdminReviewAuditReq,
                          user: User = Depends(require_role("admin")),
                          db: Session = Depends(get_db)):
    return services.admin_review_audit_decision(db, user, review_id, body)


@router.post("/reviews/{review_id}/feature")
def toggle_review_feature(review_id: int,
                          user: User = Depends(require_role("admin")),
                          db: Session = Depends(get_db)):
    """标记/取消精选评测：作者积分 +30/-30。"""
    return services.admin_toggle_review_feature(db, user, review_id)


@router.post("/reviews/{review_id}/plagiarize")
def review_plagiarize(review_id: int,
                      user: User = Depends(require_role("admin")),
                      db: Session = Depends(get_db)):
    """抄袭违规下架：评测下架 + 作者积分清零、等级重置 L0。"""
    return services.admin_review_plagiarize(db, user, review_id)


@router.get("/games")
def list_games(user: User = Depends(require_role("admin")),
               db: Session = Depends(get_db)):
    return services.admin_list_games(db, user)


@router.post("/games")
def create_game(body: AdminGameCreateReq,
                user: User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    return services.admin_create_game(db, user, body)


@router.put("/games/{game_id}")
def update_game(game_id: int, body: AdminGameUpdateReq,
                user: User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    return services.admin_update_game(db, user, game_id, body)


@router.get("/categories")
def list_categories(user: User = Depends(require_role("admin")),
                     db: Session = Depends(get_db)):
    return services.admin_list_categories(db, user)


@router.post("/categories")
def create_category(body: AdminCategoryReq,
                    user: User = Depends(require_role("admin")),
                    db: Session = Depends(get_db)):
    return services.admin_create_category(db, user, body)


@router.put("/categories/{category_id}")
def update_category(category_id: int, body: AdminCategoryReq,
                    user: User = Depends(require_role("admin")),
                    db: Session = Depends(get_db)):
    return services.admin_update_category(db, user, category_id, body)


@router.delete("/categories/{category_id}")
def delete_category(category_id: int,
                    user: User = Depends(require_role("admin")),
                    db: Session = Depends(get_db)):
    return services.admin_delete_category(db, user, category_id)


@router.get("/audit/logs")
def audit_logs(user: User = Depends(require_role("admin")),
              db: Session = Depends(get_db)):
    return services.admin_audit_logs(db, user)


@router.get("/comments")
def list_comments(user: User = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    return services.admin_list_comments(db, user)


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int,
                   user: User = Depends(require_role("admin")),
                   db: Session = Depends(get_db)):
    """管理员删除违规评论（精选由系统自动计算，管理员只管删除与查看点赞数据）。"""
    return services.admin_delete_comment(db, user, comment_id)


# ---------------- 社区治理 ----------------

@router.get("/community/posts")
def list_community_posts(keyword: Optional[str] = None,
                         user: User = Depends(require_role("admin")),
                         db: Session = Depends(get_db)):
    """社区帖子管理列表（含被举报标记）。"""
    return services.admin_list_community_posts(db, user, keyword)


@router.delete("/community/posts/{post_id}")
def delete_community_post(post_id: int,
                          user: User = Depends(require_role("admin")),
                          db: Session = Depends(get_db)):
    """管理员删除违规帖子。"""
    return services.admin_delete_community_post(db, user, post_id)


@router.get("/reports")
def list_reports(status: Optional[str] = None,
                 user: User = Depends(require_role("admin")),
                 db: Session = Depends(get_db)):
    """举报队列：默认待处理，可传 status=handled/dismissed/all。"""
    status_arg = None if status == "all" else status
    return services.admin_list_reports(db, user, status_arg)


@router.post("/reports/{report_id}/handle")
def handle_report(report_id: int, body: AdminReportHandleReq,
                  user: User = Depends(require_role("admin")),
                  db: Session = Depends(get_db)):
    """处理举报：dismiss=驳回 / remove=删除违规内容 / ban=删除并封禁作者。"""
    return services.admin_handle_report(db, user, report_id, body)
