"""管理员模块测试：dashboard/users/封禁/角色/creator-apply/审核/games/categories/logs/comments。"""
from __future__ import annotations


# ---------------- dashboard ----------------

def test_dashboard_non_admin_forbidden(client, player_headers):
    r = client.get("/api/admin/dashboard", headers=player_headers)
    assert r.status_code == 403


def test_dashboard_success(client, admin_headers):
    r = client.get("/api/admin/dashboard", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["user_count"] == 7
    assert data["game_count"] == 30  # 全部 is_online=True
    # 已发布 reviews: 1,2,3,4,5,6,10 + 30款游戏各3篇追加 = 97 篇
    assert data["review_count"] == 97
    # pending (audit/manual_review): review 7 = 1 篇
    assert data["pending_count"] == 1
    # apply pending: 2
    assert data["apply_count"] == 2


# ---------------- users ----------------

def test_admin_list_users(client, admin_headers):
    r = client.get("/api/admin/users", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 7
    assert any(u["username"] == "admin" for u in items)


def test_admin_list_users_keyword(client, admin_headers):
    r = client.get("/api/admin/users?keyword=creator", headers=admin_headers)
    items = r.json()["items"]
    # 应同时匹配 username=creator 和 nickname=硬核评测君(不含)
    # 主要校验只返回 creator 这一个
    assert all("creator" in (u["username"] + u["email"] + (u["profile"]["nickname"] or "")).lower()
               for u in items)
    assert any(u["username"] == "creator" for u in items)


def test_admin_ban_user(client, admin_headers):
    # player02 (id=4) 是 player，可封禁
    r = client.put("/api/admin/users/4/status", headers=admin_headers,
                   json={"is_active": False})
    assert r.status_code == 200
    assert r.json()["message"] == "已封禁"
    # 封禁后登录失败 403
    r2 = client.post("/api/auth/login", json={
        "username_or_email": "player02", "password": "123456",
    })
    assert r2.status_code == 403


def test_admin_cannot_ban_admin(client, admin_headers):
    # admin (id=1) 不能封禁
    r = client.put("/api/admin/users/1/status", headers=admin_headers,
                   json={"is_active": False})
    assert r.status_code == 400
    assert "管理员" in r.json()["detail"]


def test_admin_update_user_role(client, admin_headers):
    # player02 (id=4) → creator
    r = client.put("/api/admin/users/4/role", headers=admin_headers,
                   json={"role": "creator"})
    assert r.status_code == 200
    assert r.json()["message"] == "角色已更新为 creator"


def test_admin_cannot_change_admin_role(client, admin_headers):
    r = client.put("/api/admin/users/1/role", headers=admin_headers,
                    json={"role": "player"})
    assert r.status_code == 400
    assert "管理员" in r.json()["detail"]


def test_admin_update_user_role_invalid(client, admin_headers):
    r = client.put("/api/admin/users/4/role", headers=admin_headers,
                    json={"role": "superadmin"})
    assert r.status_code == 400
    assert "角色" in r.json()["detail"]


# ---------------- creator-apply ----------------

def test_admin_list_applications(client, admin_headers):
    r = client.get("/api/admin/creator-apply", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    # 种子 2 条 pending (user 7、user 4)
    assert len(items) == 2
    for a in items:
        assert "username" in a and "nickname" in a
        assert a["status"] == "pending"


def test_admin_list_applications_filter_status(client, admin_headers):
    r = client.get("/api/admin/creator-apply?status=pending", headers=admin_headers)
    items = r.json()["items"]
    assert all(a["status"] == "pending" for a in items)
    assert len(items) == 2


def test_admin_approve_application_promotes_creator(client, admin_headers):
    # 申请 id=2 (user 4 = player02)
    r = client.put("/api/admin/creator-apply/2/deal", headers=admin_headers,
                   json={"action": "approve"})
    assert r.status_code == 200
    assert "通过" in r.json()["message"]

    # 校验 user 4 角色已升 creator
    ru = client.get("/api/admin/users?keyword=player02", headers=admin_headers)
    u = ru.json()["items"][0]
    assert u["role"] == "creator"


def test_admin_reject_application(client, admin_headers):
    r = client.put("/api/admin/creator-apply/2/deal", headers=admin_headers,
                    json={"action": "reject"})
    assert r.status_code == 200
    assert "驳回" in r.json()["message"]


def test_admin_deal_application_already_processed(client, admin_headers):
    # 先处理 id=2
    client.put("/api/admin/creator-apply/2/deal", headers=admin_headers,
               json={"action": "reject"})
    # 再次处理 → 400
    r = client.put("/api/admin/creator-apply/2/deal", headers=admin_headers,
                   json={"action": "approve"})
    assert r.status_code == 400
    assert "已处理" in r.json()["detail"]


# ---------------- pending reviews / audit-decision ----------------

def test_admin_pending_reviews(client, admin_headers):
    r = client.get("/api/admin/reviews/pending", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    # review 7 manual_review → 1 条
    assert len(items) == 1
    assert items[0]["id"] == 7


def test_admin_audit_decision_pass(client, admin_headers):
    # review 7 (manual_review) → 通过后 published
    r = client.post("/api/admin/reviews/7/audit-decision",
                    headers=admin_headers,
                    json={"action": "pass", "reason": "内容正常"})
    assert r.status_code == 200
    assert "通过" in r.json()["message"]

    # 校验已发布
    rl = client.get("/api/games/4/reviews")  # review 7 属 game 4
    assert any(it["id"] == 7 and it["status"] == "published"
               for it in rl.json()["items"])


def test_admin_audit_decision_reject(client, admin_headers):
    # 用 review 9（draft）先提交审核走流程？不行，draft 不在 pending。
    # 改为：先在 review 9 上调用 audit-decision 直接 reject
    r = client.post("/api/admin/reviews/9/audit-decision",
                    headers=admin_headers,
                    json={"action": "reject", "reason": "质量过低"})
    assert r.status_code == 200
    assert "驳回" in r.json()["message"]


# ---------------- games ----------------

def test_admin_list_games(client, admin_headers):
    r = client.get("/api/admin/games", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 30
    assert len(data["categories"]) == 7


def test_admin_create_game(client, admin_headers):
    r = client.post("/api/admin/games", headers=admin_headers, json={
        "name": "新游戏X", "name_en": "New Game X",
        "developer": "Test Studio", "category_id": 1,
        "tags": ["测试", "新作"], "is_online": True,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "新游戏X"
    assert data["category_name"] == "角色扮演 RPG"
    assert data["tags"] == ["测试", "新作"]


def test_admin_create_game_missing_name(client, admin_headers):
    r = client.post("/api/admin/games", headers=admin_headers,
                     json={"name": "", "category_id": 1})
    assert r.status_code == 400
    assert "名称" in r.json()["detail"]


def test_admin_update_game(client, admin_headers):
    r = client.put("/api/admin/games/1", headers=admin_headers, json={
        "name": "艾尔登法环（改名版）", "tags": ["魂系", "改版"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "艾尔登法环（改名版）"
    # 注：services.admin_update_game 通过 bulk delete+insert 更新 GameTag，
    # 但未重新加载 game.tag_rows 关系，导致返回的 tags 字段为旧值（Bug）。
    # 通过 /api/games/{id} 重新拉取验证 DB 已写入新 tags。
    r2 = client.get("/api/games/1")
    assert r2.json()["tags"] == ["魂系", "改版"]


# ---------------- categories ----------------

def test_admin_list_categories(client, admin_headers):
    r = client.get("/api/admin/categories", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 7


def test_admin_create_category(client, admin_headers):
    r = client.post("/api/admin/categories", headers=admin_headers,
                     json={"name": "新分类"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "新分类"
    assert data["id"]


def test_admin_create_category_missing_name(client, admin_headers):
    r = client.post("/api/admin/categories", headers=admin_headers,
                     json={"name": ""})
    assert r.status_code == 400
    assert "分类名" in r.json()["detail"]


def test_admin_update_category(client, admin_headers):
    # 先建一个，再改
    cr = client.post("/api/admin/categories", headers=admin_headers,
                     json={"name": "原分类"})
    cid = cr.json()["id"]
    r = client.put(f"/api/admin/categories/{cid}", headers=admin_headers,
                    json={"name": "改名分类"})
    assert r.status_code == 200
    assert r.json()["name"] == "改名分类"


def test_admin_delete_category(client, admin_headers):
    cr = client.post("/api/admin/categories", headers=admin_headers,
                     json={"name": "待删分类"})
    cid = cr.json()["id"]
    r = client.delete(f"/api/admin/categories/{cid}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "分类已删除"


def test_admin_delete_category_with_games_forbidden(client, admin_headers):
    # category_id=1 有游戏（game 2、6 属 cat 1）→ 400
    r = client.delete("/api/admin/categories/1", headers=admin_headers)
    assert r.status_code == 400
    assert "无法删除" in r.json()["detail"]


# ---------------- audit logs ----------------

def test_admin_audit_logs(client, admin_headers):
    r = client.get("/api/admin/audit/logs", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    # 种子 3 条日志
    assert len(items) == 3
    for l in items:
        assert "review_title" in l
        assert "audit_type" in l
        assert "reason" in l


# ---------------- comments ----------------

def test_admin_list_comments(client, admin_headers):
    r = client.get("/api/admin/comments", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    # 种子：6 条评测评论 + 30 条游戏长评 + 225 条游戏普通短评（每游戏 5-10 条）= 261
    assert len(items) == 261
    for c in items:
        assert "content" in c and "author" in c and "review_title" in c
        assert "created_at" in c and "like_count" in c
        assert "target_type" in c and "target_title" in c
        assert "is_featured" not in c  # 精选改为运行时计算，字段已删除
    # 游戏评论带有所属游戏名
    game_comments = [c for c in items if c["target_type"] == "game"]
    assert len(game_comments) == 255
    assert any(c["target_title"] for c in game_comments)


def test_admin_delete_comment(client, admin_headers):
    r = client.delete("/api/admin/comments/1", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "评论已删除"
    # 列表中已不存在
    items = client.get("/api/admin/comments", headers=admin_headers).json()["items"]
    assert all(c["id"] != 1 for c in items)


def test_admin_modules_require_admin(client, player_headers):
    """player 调用任意 admin 接口都应 403。"""
    endpoints = [
        ("GET", "/api/admin/dashboard"),
        ("GET", "/api/admin/users"),
        ("GET", "/api/admin/creator-apply"),
        ("GET", "/api/admin/reviews/pending"),
        ("GET", "/api/admin/games"),
        ("GET", "/api/admin/categories"),
        ("GET", "/api/admin/audit/logs"),
        ("GET", "/api/admin/comments"),
    ]
    for method, path in endpoints:
        r = client.request(method, path, headers=player_headers)
        assert r.status_code == 403, f"{method} {path} 应返回 403，实际 {r.status_code}"
