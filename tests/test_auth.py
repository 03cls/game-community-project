"""认证模块测试：register / login。"""
from __future__ import annotations


# ---------------- register ----------------

def test_register_success(client):
    r = client.post("/api/auth/register", json={
        "username": "newbie01", "email": "newbie01@game.local", "password": "abc123",
    })
    assert r.status_code == 200
    assert r.json()["message"] == "注册成功，请登录"


def test_register_duplicate_username(client):
    r = client.post("/api/auth/register", json={
        "username": "admin", "email": "unique01@game.local", "password": "abc123",
    })
    assert r.status_code == 400
    assert "已存在" in r.json()["detail"]


def test_register_duplicate_email(client):
    r = client.post("/api/auth/register", json={
        "username": "unique_user", "email": "admin@game.local", "password": "abc123",
    })
    assert r.status_code == 400
    assert "邮箱" in r.json()["detail"]


# ---------------- login ----------------

def test_login_by_username_success(client):
    r = client.post("/api/auth/login", json={
        "username_or_email": "admin", "password": "admin123",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert data["user_id"] == 1
    assert data["role"] == "admin"
    assert data["access_token"]
    assert data["user"]["username"] == "admin"


def test_login_by_email_success(client):
    r = client.post("/api/auth/login", json={
        "username_or_email": "creator@game.local", "password": "creator123",
    })
    assert r.status_code == 200
    assert r.json()["role"] == "creator"


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={
        "username_or_email": "admin", "password": "wrong",
    })
    assert r.status_code == 401
    assert "密码" in r.json()["detail"]


def test_login_banned_user(client):
    # bad_guy 是种子封禁用户
    r = client.post("/api/auth/login", json={
        "username_or_email": "bad_guy", "password": "123456",
    })
    assert r.status_code == 403
    assert "封禁" in r.json()["detail"]
