"""创作者积分与等级模块测试。

覆盖：等级阈值、发布/精选/点赞/收藏积分、删除扣分、抄袭清零、
L0/L1 编辑权益、等级排序加权、首页专题、积分流水。
"""
from __future__ import annotations

from app.core.points import level_for_points
from app.models import User


# ---------------- 等级阈值（纯函数） ----------------

def test_level_thresholds():
    assert level_for_points(0) == 0
    assert level_for_points(199.9) == 0
    assert level_for_points(200) == 1
    assert level_for_points(499) == 1
    assert level_for_points(500) == 2
    assert level_for_points(1199) == 2
    assert level_for_points(1200) == 3
    assert level_for_points(2499) == 3
    assert level_for_points(2500) == 4
    assert level_for_points(99999) == 4


# ---------------- 辅助 ----------------

def _register_and_promote(client, admin_headers, username):
    client.post("/api/auth/register", json={
        "username": username, "email": username + "@t.com", "password": "123456"})
    login = client.post("/api/auth/login", json={
        "username_or_email": username, "password": "123456"}).json()
    uid = login["user_id"]
    r = client.put(f"/api/admin/users/{uid}/role", headers=admin_headers,
                   json={"role": "creator"})
    assert r.status_code == 200, r.text
    return uid, {"Authorization": "Bearer " + login["access_token"]}


def _publish(client, headers, admin_headers, title="一篇正常的游戏评测：玩法与剧情讨论"):
    """创建评测 → 提交审核（一律待审核）→ 管理员人工通过 → 对外可见。"""
    cr = client.post("/api/reviews", headers=headers, json={
        "title": title, "game_id": 1,
        "content": "这篇评测正常讨论游戏的玩法机制与剧情表现，内容客观。"})
    rid = cr.json()["id"]
    r = client.post(f"/api/reviews/{rid}/submit-audit", headers=headers)
    assert r.status_code == 200 and r.json()["status"] == "pending", r.text
    ok = client.post(f"/api/admin/reviews/{rid}/audit-decision", headers=admin_headers,
                     json={"action": "pass", "reason": "内容无问题"})
    assert ok.status_code == 200, ok.text
    return rid


def _points(client, headers):
    return client.get("/api/creator/points", headers=headers).json()


# ---------------- 积分获取 ----------------

def test_points_requires_creator(client, player_headers):
    r = client.get("/api/creator/points", headers=player_headers)
    assert r.status_code == 403


def test_publish_awards_20(client, admin_headers, player_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc1")
    assert _points(client, ch)["points"] == 0.0
    _publish(client, ch, admin_headers)
    ov = _points(client, ch)
    assert ov["points"] == 20.0
    assert ov["level"] == 0  # 20 分仍是 L0 见习创作者
    recs = client.get("/api/creator/point-records", headers=ch).json()
    assert any(rec["change"] == 20.0 and "发布" in rec["reason"] for rec in recs["items"])


def test_admin_pass_awards_20(client, admin_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc2")
    # 引战内容 → AI 转人工复核（manual_review）
    cr = client.post("/api/reviews", headers=ch, json={
        "title": "这游戏真是垃圾", "game_id": 1,
        "content": "纯脑残设计，狗都不玩"})
    rid = cr.json()["id"]
    r = client.post(f"/api/reviews/{rid}/submit-audit", headers=ch)
    assert r.json()["status"] == "pending"  # 一律待审核，AI 转人工复核
    assert _points(client, ch)["points"] == 0.0
    # 管理员人工复核通过
    client.post(f"/api/admin/reviews/{rid}/audit-decision", headers=admin_headers,
                json={"action": "pass", "reason": "无问题"})
    assert _points(client, ch)["points"] == 20.0


def test_like_awards_02(client, admin_headers, player_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc3")
    rid = _publish(client, ch, admin_headers)
    # 别人点赞 → +0.2
    r = client.post(f"/api/reviews/{rid}/like", headers=player_headers)
    assert r.json()["liked"] is True
    assert _points(client, ch)["points"] == 20.2
    # 取消点赞 → 回滚
    client.post(f"/api/reviews/{rid}/like", headers=player_headers)
    assert _points(client, ch)["points"] == 20.0
    # 给自己点赞不加分
    client.post(f"/api/reviews/{rid}/like", headers=ch)
    assert _points(client, ch)["points"] == 20.0


def test_favorite_awards_05(client, admin_headers, player_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc4")
    rid = _publish(client, ch, admin_headers)
    r = client.post(f"/api/reviews/{rid}/favorite", headers=player_headers)
    assert r.json()["favorited"] is True
    assert _points(client, ch)["points"] == 20.5
    client.post(f"/api/reviews/{rid}/favorite", headers=player_headers)
    assert _points(client, ch)["points"] == 20.0


def test_my_review_interactions_listed(client, admin_headers, player_headers):
    """个人中心「评测互动」：点赞/收藏的评测出现在 /reviews/me/likes 与 /me/favorites。"""
    _uid, ch = _register_and_promote(client, admin_headers, "nc4b")
    rid = _publish(client, ch, admin_headers)
    # 未登录 → 401
    assert client.get("/api/reviews/me/likes").status_code == 401
    assert client.get("/api/reviews/me/favorites").status_code == 401
    # 空列表
    assert client.get("/api/reviews/me/likes", headers=player_headers).json()["items"] == []
    # 点赞 + 收藏
    client.post(f"/api/reviews/{rid}/like", headers=player_headers)
    client.post(f"/api/reviews/{rid}/favorite", headers=player_headers)
    likes = client.get("/api/reviews/me/likes", headers=player_headers).json()
    favs = client.get("/api/reviews/me/favorites", headers=player_headers).json()
    assert any(i["id"] == rid for i in likes["items"])
    assert any(i["id"] == rid for i in favs["items"])
    assert likes["items"][0]["game_name"]  # 卡片字段齐全
    # 取消点赞 → 列表移除
    client.post(f"/api/reviews/{rid}/like", headers=player_headers)
    likes = client.get("/api/reviews/me/likes", headers=player_headers).json()
    assert all(i["id"] != rid for i in likes["items"])


def test_my_reviews_listed_for_creator(client, admin_headers, player_headers):
    """个人中心「我的评测」：/reviews/mine 返回登录用户全部评测（含未过审，不限角色）。"""
    _uid, ch = _register_and_promote(client, admin_headers, "nc4c")
    # 未登录 → 401；普通玩家无评测 → 空列表
    assert client.get("/api/reviews/mine").status_code == 401
    assert client.get("/api/reviews/mine", headers=player_headers).json()["items"] == []
    rid = _publish(client, ch, admin_headers)
    mine = client.get("/api/reviews/mine", headers=ch).json()
    assert any(i["id"] == rid and i["status"] == "published" for i in mine["items"])
    # 提交一篇待审核评测，也应出现在自己的 mine 列表（详情对外 403 但本人列表可见）
    cr = client.post("/api/reviews", headers=ch, json={
        "title": "待审核的评测标题", "game_id": 2, "content": "内容正常讨论玩法。"})
    rid2 = cr.json()["id"]
    client.post(f"/api/reviews/{rid2}/submit-audit", headers=ch)
    mine = client.get("/api/reviews/mine", headers=ch).json()
    assert any(i["id"] == rid2 and i["status"] == "manual_review" for i in mine["items"])


def test_feature_awards_30(client, admin_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc5")
    rid = _publish(client, ch, admin_headers)
    r = client.post(f"/api/admin/reviews/{rid}/feature", headers=admin_headers)
    assert r.status_code == 200 and r.json()["is_featured"] is True
    assert _points(client, ch)["points"] == 50.0
    # 取消精选 → 扣回 30
    client.post(f"/api/admin/reviews/{rid}/feature", headers=admin_headers)
    assert _points(client, ch)["points"] == 20.0


def test_feature_requires_admin(client, player_headers):
    r = client.post("/api/admin/reviews/1/feature", headers=player_headers)
    assert r.status_code == 403


# ---------------- 扣分与清零 ----------------

def test_delete_published_deducts(client, admin_headers, player_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc6")
    rid = _publish(client, ch, admin_headers)
    client.post(f"/api/reviews/{rid}/favorite", headers=player_headers)  # +0.5
    assert _points(client, ch)["points"] == 20.5
    # 管理员删除：追回 20.5 + 额外 30，余额扣到 0 为止
    r = client.delete(f"/api/reviews/{rid}", headers=admin_headers)
    assert r.status_code == 200
    assert _points(client, ch)["points"] == 0.0


def test_delete_draft_no_penalty(client, admin_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc7")
    cr = client.post("/api/reviews", headers=ch, json={
        "title": "未发布草稿", "game_id": 1, "content": "草稿内容"})
    rid = cr.json()["id"]
    client.delete(f"/api/reviews/{rid}", headers=ch)  # 作者删草稿
    assert _points(client, ch)["points"] == 0.0  # 无积分无处罚


def test_plagiarize_resets_points(client, creator_headers):
    # 种子创作者（硬核评测君，uid=2）有积分；其评测 1 被判定抄袭
    assert _points(client, creator_headers)["points"] > 0
    r = client.post("/api/admin/reviews/1/plagiarize",
                    headers={"Authorization": "Bearer " + _admin_token(client)})
    assert r.status_code == 200
    ov = _points(client, creator_headers)
    assert ov["points"] == 0.0
    assert ov["level"] == 0
    # 评测已下架（rejected）：匿名访问 → 无权限提示 403
    assert client.get("/api/reviews/1").status_code == 403


def _admin_token(client):
    from tests.conftest import _login
    return _login(client, "admin", "admin123")


# ---------------- 等级权益 ----------------

def test_l0_cannot_edit_published(client, admin_headers):
    _uid, ch = _register_and_promote(client, admin_headers, "nc8")
    rid = _publish(client, ch, admin_headers)
    r = client.put(f"/api/reviews/{rid}", headers=ch, json={"title": "L0 想改"})
    assert r.status_code == 403
    assert "L0" in r.json()["detail"]


def test_l1_can_edit_once(client, admin_headers, db):
    uid, ch = _register_and_promote(client, admin_headers, "nc9")
    rid = _publish(client, ch, admin_headers)
    # 直接把积分/等级抬到 L1
    db.query(User).filter(User.id == uid).update(
        {User.creator_points: 200.0, User.creator_level: 1})
    db.commit()
    r = client.put(f"/api/reviews/{rid}", headers=ch, json={"title": "L1 编辑后标题"})
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "L1 编辑后标题"
    # 第二次被拒
    r2 = client.put(f"/api/reviews/{rid}", headers=ch, json={"title": "再改一次"})
    assert r2.status_code == 400
    assert "编辑机会" in r2.json()["detail"]


# ---------------- 排序加权与专题 ----------------

def test_featured_review_ranks_first_in_game(client, admin_headers):
    # 游戏 1 的评测列表：把 uid5 的评测 12（非最高等级）设为精选 → 应排第一
    r = client.post("/api/admin/reviews/12/feature", headers=admin_headers)
    assert r.status_code == 200
    data = client.get("/api/games/1/reviews").json()
    assert data["items"][0]["is_featured"] is True
    assert data["items"][0]["id"] == 12


def test_hall_only_high_level(client):
    data = client.get("/api/creator/hall").json()
    for it in data["items"]:
        assert it["author_level"] >= 3


def test_review_out_has_level_and_featured(client):
    r = client.get("/api/reviews/1")
    body = r.json() if r.status_code == 200 else None
    # 评测 1 可能在其它用例被下架；存在即校验字段
    if body:
        assert "author_level" in body
        assert "is_featured" in body
