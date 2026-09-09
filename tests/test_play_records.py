"""游玩记录测试：列表/更新状态/非法状态。"""
from __future__ import annotations


def test_list_play_records(client, player_headers):
    # player 种子记录：game 6 completed / 8 playing / 9 want
    r = client.get("/api/play-record", headers=player_headers)
    assert r.status_code == 200
    data = r.json()
    ids_status = {item["game_id"]: item["play_status"] for item in data["items"]}
    assert ids_status == {6: "completed", 8: "playing", 9: "want"}
    # 每条带 game 详情
    assert all("game" in item and item["game"] is not None for item in data["items"])


def test_list_play_records_requires_auth(client):
    r = client.get("/api/play-record")
    assert r.status_code == 401


def test_upsert_play_record_new(client, player_headers):
    # player 没玩过 game 1
    r = client.post("/api/play-record", headers=player_headers,
                    json={"game_id": 1, "play_status": "want"})
    assert r.status_code == 200
    assert r.json()["message"] == "游玩状态已更新"
    assert r.json()["play_status"] == "want"

    r2 = client.get("/api/play-record", headers=player_headers)
    ids = {item["game_id"] for item in r2.json()["items"]}
    assert 1 in ids


def test_upsert_play_record_update(client, player_headers):
    # game 6 已是 completed，改为 playing
    r = client.post("/api/play-record", headers=player_headers,
                    json={"game_id": 6, "play_status": "playing"})
    assert r.status_code == 200
    assert r.json()["play_status"] == "playing"

    r2 = client.get("/api/play-record", headers=player_headers)
    for item in r2.json()["items"]:
        if item["game_id"] == 6:
            assert item["play_status"] == "playing"
            return
    assert False, "未找到 game 6 的记录"


def test_upsert_play_record_invalid_status(client, player_headers):
    r = client.post("/api/play-record", headers=player_headers,
                     json={"game_id": 1, "play_status": "invalid_status"})
    assert r.status_code == 400
    assert "非法" in r.json()["detail"]
