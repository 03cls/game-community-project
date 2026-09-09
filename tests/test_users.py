"""用户模块测试：me / password / apply-creator。"""
from __future__ import annotations


# ---------------- me ----------------

def test_get_me_without_token_401(client):
    r = client.get("/api/users/me")
    assert r.status_code == 401


def test_get_me_success(client, player_headers):
    r = client.get("/api/users/me", headers=player_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "player"
    assert data["role"] == "player"
    assert "profile" in data
    assert data["profile"]["nickname"] == "休闲玩家小P"


def test_update_me_success(client, player_headers):
    r = client.put("/api/users/me", headers=player_headers, json={
        "nickname": "改名后的玩家", "bio": "新简介",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["profile"]["nickname"] == "改名后的玩家"
    assert data["profile"]["bio"] == "新简介"


# ---------------- password ----------------

def test_change_password_wrong_old(client, player_headers):
    r = client.put("/api/users/me/password", headers=player_headers, json={
        "old_password": "wrong", "new_password": "newpass",
    })
    assert r.status_code == 400
    assert "原密码" in r.json()["detail"]


def test_change_password_too_short(client, player_headers):
    r = client.put("/api/users/me/password", headers=player_headers, json={
        "old_password": "player123", "new_password": "123",
    })
    assert r.status_code == 400
    assert "6 位" in r.json()["detail"]


def test_change_password_success(client):
    # 先登录拿 token
    tok = client.post("/api/auth/login", json={
        "username_or_email": "player", "password": "player123",
    }).json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}

    r = client.put("/api/users/me/password", headers=h, json={
        "old_password": "player123", "new_password": "newpass6",
    })
    assert r.status_code == 200
    assert r.json()["message"] == "密码修改成功"

    # 用新密码登录验证
    r2 = client.post("/api/auth/login", json={
        "username_or_email": "player", "password": "newpass6",
    })
    assert r2.status_code == 200

    # 旧密码应失败
    r3 = client.post("/api/auth/login", json={
        "username_or_email": "player", "password": "player123",
    })
    assert r3.status_code == 401


# ---------------- apply-creator ----------------

def test_apply_creator_already_creator(client, creator_headers):
    r = client.post("/api/users/apply-creator", headers=creator_headers, json={
        "apply_reason": "我想做创作者",
    })
    assert r.status_code == 400
    assert "创作者" in r.json()["detail"]


def test_apply_creator_success(client, player_headers):
    r = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "我有 5 年游戏评测经验",
    })
    assert r.status_code == 200
    assert r.json()["message"] == "申请已提交，等待管理员审核"


def test_apply_creator_duplicate_pending(client, player_headers):
    # 第一次申请
    r1 = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "这是我的第一次申请，理由足够长",
    })
    assert r1.status_code == 200
    # 第二次：还有 pending 应失败
    r2 = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "这是我的第二次申请，理由也足够长",
    })
    assert r2.status_code == 400
    assert "待审核" in r2.json()["detail"]


# ---------------- my creator-application ----------------

def test_my_creator_application_requires_auth(client):
    r = client.get("/api/users/me/creator-application")
    assert r.status_code == 401


def test_my_creator_application_none(client, player_headers):
    data = client.get("/api/users/me/creator-application", headers=player_headers).json()
    assert data["status"] == "none"
    assert data["application"] is None


def test_my_creator_application_pending_fields(client, player_headers):
    """申请后可查到 pending 状态与全部字段（个人中心展示）。"""
    r = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "我玩了十年游戏，写过不少攻略，希望加入创作者",
        "good_at": "攻略心得、新游首发评测",
        "experience": "Steam 库存 500+，常写长评",
    })
    assert r.status_code == 200
    data = client.get("/api/users/me/creator-application", headers=player_headers).json()
    assert data["status"] == "pending"
    app = data["application"]
    assert "攻略" in app["apply_reason"]
    assert app["good_at"] == "攻略心得、新游首发评测"
    assert app["experience"] == "Steam 库存 500+，常写长评"
    assert app["created_at"]


def test_apply_creator_reason_too_short(client, player_headers):
    r = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "太短了",
    })
    assert r.status_code == 400
    assert "至少 10" in r.json()["detail"]


def test_apply_creator_good_at_too_long(client, player_headers):
    r = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "我有丰富的游戏评测写作经验，希望加入创作者团队",
        "good_at": "x" * 101,
    })
    assert r.status_code == 400
    assert "擅长方向" in r.json()["detail"]


def test_apply_creator_experience_too_long(client, player_headers):
    r = client.post("/api/users/apply-creator", headers=player_headers, json={
        "apply_reason": "我有丰富的游戏评测写作经验，希望加入创作者团队",
        "experience": "y" * 201,
    })
    assert r.status_code == 400
    assert "游戏经历" in r.json()["detail"]
