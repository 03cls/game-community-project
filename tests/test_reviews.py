"""评测模块测试：创建/编辑(非作者/已发布)/删除/submit-audit。"""
from __future__ import annotations


# ---------------- 创建 ----------------

def test_create_review_requires_creator(client, player_headers):
    r = client.post("/api/reviews", headers=player_headers, json={
        "title": "test", "game_id": 1, "content": "x",
    })
    assert r.status_code == 403  # require_role(player) 失败


def test_create_review_missing_title(client, creator_headers):
    r = client.post("/api/reviews", headers=creator_headers, json={
        "title": "", "game_id": 1, "content": "x",
    })
    assert r.status_code == 400
    assert "标题" in r.json()["detail"]


def test_create_review_missing_game_id(client, creator_headers):
    r = client.post("/api/reviews", headers=creator_headers, json={
        "title": "无游戏", "game_id": 0, "content": "x",
    })
    assert r.status_code == 400
    assert "标题" in r.json()["detail"]


def test_create_review_success(client, creator_headers):
    r = client.post("/api/reviews", headers=creator_headers, json={
        "title": "我的新评测", "game_id": 1,
        "content": "这是一篇正常评测正文", "tags": ["测试", "新作"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "我的新评测"
    assert data["game_id"] == 1
    assert data["status"] == "draft"
    assert data["audit_status"] is None
    assert data["tags"] == ["测试", "新作"]
    assert data["game_name"] == "艾尔登法环"
    assert data["author_name"] == "硬核评测君"


# ---------------- 编辑 ----------------

def test_update_review_not_author(client, creator_headers):
    # review 2 owned by writer_lily (user_id=5)
    r = client.put("/api/reviews/2", headers=creator_headers, json={
        "title": "改个标题",
    })
    assert r.status_code == 403
    assert "只能编辑" in r.json()["detail"]


def test_update_published_review_l1_edit_once(client, creator_headers):
    # 种子创作者（硬核评测君）等级 ≥ L1：已发布评测可编辑 1 次
    r = client.put("/api/reviews/1", headers=creator_headers, json={
        "title": "L1 权益首次编辑已发布评测",
    })
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "L1 权益首次编辑已发布评测"
    assert r.json()["edit_used"] is True
    # 第 2 次编辑被拒：1 次编辑机会已用完
    r2 = client.put("/api/reviews/1", headers=creator_headers, json={
        "title": "想再改一次",
    })
    assert r2.status_code == 400
    assert "编辑机会" in r2.json()["detail"]


def test_update_review_success(client, creator_headers):
    # 先创建一篇草稿
    cr = client.post("/api/reviews", headers=creator_headers, json={
        "title": "草稿标题", "game_id": 1, "content": "草稿正文",
    })
    rid = cr.json()["id"]

    r = client.put(f"/api/reviews/{rid}", headers=creator_headers, json={
        "title": "改后标题", "content": "改后正文", "tags": ["新标签"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "改后标题"
    assert data["content"] == "改后正文"
    # 注：services.update_review 通过 bulk delete+insert 更新 ReviewTag，
    # 但未重新加载 review.tag_rows 关系，导致返回的 tags 字段为旧值（Bug）。
    # 通过 /api/creator/reviews 重新拉取验证 DB 已写入新 tags。
    r2 = client.get("/api/creator/reviews", headers=creator_headers)
    mine = [rv for rv in r2.json()["items"] if rv["id"] == rid][0]
    assert mine["tags"] == ["新标签"]


# ---------------- 删除 ----------------

def test_delete_review_not_author(client, player_headers):
    # player 删除他人评测 → 403（player 既非作者也非 admin）
    r = client.delete("/api/reviews/1", headers=player_headers)
    assert r.status_code == 403
    assert "无权" in r.json()["detail"]


def test_delete_review_by_author(client, creator_headers):
    # creator 删除自己的草稿 review 9
    r = client.delete("/api/reviews/9", headers=creator_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "已删除"
    # 再删一次 → 404
    r2 = client.delete("/api/reviews/9", headers=creator_headers)
    assert r2.status_code == 404


def test_delete_review_by_admin(client, admin_headers):
    # admin 删除任意评测
    r = client.delete("/api/reviews/2", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "已删除"


# ---------------- submit-audit ----------------

def test_submit_audit_already_published(client, creator_headers):
    # review 1 已 published
    r = client.post("/api/reviews/1/submit-audit", headers=creator_headers)
    assert r.status_code == 400
    assert "已发布" in r.json()["detail"]


def test_submit_audit_in_review(client, creator_headers):
    # review 7 manual_review
    r = client.post("/api/reviews/7/submit-audit", headers=creator_headers)
    assert r.status_code == 400
    assert "审核中" in r.json()["detail"]


def test_submit_audit_normal_pending(client, creator_headers):
    # 新审核流：提交后一律进入「待审核」，由管理员人工通过/驳回
    cr = client.post("/api/reviews", headers=creator_headers, json={
        "title": "正常评测标题", "game_id": 1,
        "content": "这是一篇内容正常的评测，讨论游戏机制与剧情。",
    })
    rid = cr.json()["id"]
    r = client.post(f"/api/reviews/{rid}/submit-audit",
                    headers=creator_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending"
    assert data["audit"]["status"] == "passed"  # AI 风险参考：正常内容
    # 待审核评测对外不可见：匿名访问详情 → 无权限
    assert client.get(f"/api/reviews/{rid}").status_code == 403


def test_submit_audit_ad_pending(client, creator_headers):
    # 广告内容：AI 标记风险，但最终仍进入待审核，由管理员驳回
    cr = client.post("/api/reviews", headers=creator_headers, json={
        "title": "加群领皮肤攻略", "game_id": 1,
        "content": "新手快来加群 xxx-xxx-xxx 免费领皮肤，微信 vx_xxx 联系我",
    })
    rid = cr.json()["id"]
    r = client.post(f"/api/reviews/{rid}/submit-audit",
                    headers=creator_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "pending"
    assert data["audit"]["status"] == "rejected"  # AI 风险参考：广告


def test_submit_audit_abuse_manual_review(client, creator_headers):
    cr = client.post("/api/reviews", headers=creator_headers, json={
        "title": "这游戏真是垃圾游戏", "game_id": 1,
        "content": "纯脑残设计，狗都不玩",
    })
    rid = cr.json()["id"]
    r = client.post(f"/api/reviews/{rid}/submit-audit",
                    headers=creator_headers)
    assert r.status_code == 200
    data = r.json()
    # 新审核流：对外统一返回 pending，AI 仅给出风险参考（manual_review）
    assert data["status"] == "pending"
    assert data["audit"]["status"] == "manual_review"
