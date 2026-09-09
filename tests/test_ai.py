"""AI 模块测试：game-recommend / creator-assistant。"""
from __future__ import annotations


# ---------------- game-recommend ----------------

def test_game_recommend_no_more_than_3(client, player_headers):
    r = client.post("/api/ai/game-recommend", headers=player_headers,
                    json={"preferences": ""})
    assert r.status_code == 200
    data = r.json()
    assert len(data["recommendations"]) <= 3
    # 不少于 1（有可推荐游戏）
    assert len(data["recommendations"]) >= 1
    # 每条带必要字段
    for item in data["recommendations"]:
        assert "game_id" in item
        assert "game_name" in item
        assert "reason" in item
        assert "average_score" in item


def test_game_recommend_excludes_favorited_and_played(client, player_headers):
    # player 收藏 1,2,3；游玩 6,8,9 → 推荐不应包含这些
    r = client.post("/api/ai/game-recommend", headers=player_headers,
                    json={"preferences": ""})
    assert r.status_code == 200
    excluded = {1, 2, 3, 6, 8, 9}
    for item in r.json()["recommendations"]:
        assert item["game_id"] not in excluded


def test_game_recommend_requires_auth(client):
    r = client.post("/api/ai/game-recommend", json={"preferences": ""})
    assert r.status_code == 401


def test_game_recommend_with_preferences(client, player_headers):
    # 给个偏好关键词，确保仍合法返回
    r = client.post("/api/ai/game-recommend", headers=player_headers,
                    json={"preferences": "动作 奇幻"})
    assert r.status_code == 200
    assert isinstance(r.json()["recommendations"], list)
    assert len(r.json()["recommendations"]) <= 3


# ---------------- creator-assistant ----------------

def test_creator_assistant_requires_creator(client, player_headers):
    r = client.post("/api/ai/creator-assistant", headers=player_headers, json={
        "game_id": 1, "action": "outline",
    })
    assert r.status_code == 403


def test_creator_assistant_outline(client, creator_headers):
    r = client.post("/api/ai/creator-assistant", headers=creator_headers,
                     json={"game_id": 1, "action": "outline"})
    assert r.status_code == 200
    reply = r.json()["reply"]
    assert "大纲" in reply
    assert "艾尔登法环" in reply


def test_creator_assistant_tips(client, creator_headers):
    r = client.post("/api/ai/creator-assistant", headers=creator_headers,
                     json={"game_id": 1, "action": "tips"})
    assert r.status_code == 200
    assert "通关" in r.json()["reply"]


def test_creator_assistant_polish(client, creator_headers):
    r = client.post("/api/ai/creator-assistant", headers=creator_headers, json={
        "game_id": 1, "action": "polish",
        "content_context": "<p>战斗手感非常爽快</p>",
    })
    assert r.status_code == 200
    reply = r.json()["reply"]
    assert "润色" in reply


def test_creator_assistant_pros(client, creator_headers):
    r = client.post("/api/ai/creator-assistant", headers=creator_headers,
                     json={"game_id": 1, "action": "pros"})
    assert r.status_code == 200
    assert "优缺点" in r.json()["reply"]


def test_creator_assistant_default_action(client, creator_headers):
    r = client.post("/api/ai/creator-assistant", headers=creator_headers, json={
        "game_id": 1, "action": "", "message": "帮我看看",
    })
    assert r.status_code == 200
    assert "艾尔登法环" in r.json()["reply"]


def test_creator_assistant_unknown_game(client, creator_headers):
    r = client.post("/api/ai/creator-assistant", headers=creator_headers,
                     json={"game_id": 99999, "action": "outline"})
    assert r.status_code == 200
    assert "该游戏" in r.json()["reply"]
