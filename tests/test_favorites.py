"""收藏模块测试：列表/添加/重复添加幂等/取消/游戏不存在。"""
from __future__ import annotations


def test_list_favorites(client, player_headers):
    # player 种子收藏了 game 1/2/3
    r = client.get("/api/favorites", headers=player_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    ids = {g["id"] for g in data["items"]}
    assert ids == {1, 2, 3}


def test_list_favorites_requires_auth(client):
    r = client.get("/api/favorites")
    assert r.status_code == 401


def test_add_favorite_success(client, player_headers):
    # player 未收藏 game 5
    r = client.post("/api/favorites", headers=player_headers, json={"game_id": 5})
    assert r.status_code == 200
    assert r.json()["message"] == "收藏成功"

    # 列表里能看到
    r2 = client.get("/api/favorites", headers=player_headers)
    assert r2.json()["total"] == 4
    assert any(g["id"] == 5 for g in r2.json()["items"])


def test_add_favorite_idempotent(client, player_headers):
    # player 已收藏 game 1，再添加应幂等返回 200
    r = client.post("/api/favorites", headers=player_headers, json={"game_id": 1})
    assert r.status_code == 200
    # 总数仍为 3
    r2 = client.get("/api/favorites", headers=player_headers)
    assert r2.json()["total"] == 3


def test_add_favorite_game_not_found(client, player_headers):
    r = client.post("/api/favorites", headers=player_headers,
                     json={"game_id": 99999})
    assert r.status_code == 404
    assert "游戏不存在" in r.json()["detail"]


def test_remove_favorite(client, player_headers):
    # 取消收藏 game 1
    r = client.delete("/api/favorites/1", headers=player_headers)
    assert r.status_code == 200
    assert r.json()["message"] == "已取消收藏"

    r2 = client.get("/api/favorites", headers=player_headers)
    assert r2.json()["total"] == 2
    assert all(g["id"] != 1 for g in r2.json()["items"])


def test_remove_favorite_not_collected(client, player_headers):
    # player 未收藏 game 5，删除仍返回 200（幂等）
    r = client.delete("/api/favorites/5", headers=player_headers)
    assert r.status_code == 200
