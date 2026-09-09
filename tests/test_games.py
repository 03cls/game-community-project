"""游戏模块测试：列表分页/筛选/排序、详情、评测列表。"""
from __future__ import annotations


# ---------------- 列表 ----------------

def test_list_games_default(client):
    r = client.get("/api/games")
    assert r.status_code == 200
    data = r.json()
    # 默认 sort=hot, page=1, page_size=9 → items 长度 == min(9, total)
    assert "items" in data and "total" in data
    assert data["page"] == 1
    assert data["page_size"] == 9
    assert "total_pages" in data
    assert "categories" in data
    # 种子 30 个游戏，全部 is_online=True
    assert data["total"] == 30
    assert len(data["items"]) == 9


def test_list_games_pagination(client):
    r = client.get("/api/games?page=2&page_size=5")
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert data["total"] == 30
    assert data["total_pages"] == 6  # ceil(30/5)
    assert len(data["items"]) == 5


def test_list_games_filter_by_category(client):
    # category_id=4 是开放世界：游戏 1/4/5/23/24/25/26 均属此分类
    r = client.get("/api/games?category_id=4")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 7
    for g in data["items"]:
        assert g["category_id"] == 4
        assert g["category_name"] == "开放世界"


def test_list_games_filter_by_keyword(client):
    r = client.get("/api/games?keyword=艾尔登")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "艾尔登法环"


def test_list_games_sort_hot(client):
    r = client.get("/api/games?sort=hot&page_size=30")
    data = r.json()
    hots = [g["hot"] for g in data["items"]]
    assert hots == sorted(hots, reverse=True)
    # 黑神话 hot=99 应是第一
    assert data["items"][0]["name"] == "黑神话：悟空"


def test_list_games_sort_newest(client):
    r = client.get("/api/games?sort=newest&page_size=30")
    data = r.json()
    dates = [g["release_date"] for g in data["items"]]
    assert dates == sorted(dates, reverse=True)


def test_list_games_sort_score(client):
    r = client.get("/api/games?sort=score&page_size=30")
    data = r.json()
    scores = [g["average_score"] for g in data["items"]]
    assert scores == sorted(scores, reverse=True)


# ---------------- 详情 ----------------

def test_get_game_detail_with_login(client, player_headers):
    # player 种子已收藏 game 1、2、3；已玩过 game 6/8/9
    r = client.get("/api/games/1", headers=player_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert data["name"] == "艾尔登法环"
    assert data["is_favorite"] is True
    assert data["play_status"] is None  # 未玩过


def test_get_game_detail_no_login(client):
    r = client.get("/api/games/1")
    assert r.status_code == 200
    data = r.json()
    assert data["is_favorite"] is False
    assert data["play_status"] is None


def test_get_game_play_status(client, player_headers):
    # player 玩过 game 6 (completed)、8 (playing)、9 (want)
    r = client.get("/api/games/6", headers=player_headers)
    data = r.json()
    assert data["is_favorite"] is False
    assert data["play_status"] == "completed"

    r2 = client.get("/api/games/8", headers=player_headers)
    assert r2.json()["play_status"] == "playing"


def test_get_game_not_found(client):
    r = client.get("/api/games/99999")
    assert r.status_code == 404
    assert "不存在" in r.json()["detail"]


# ---------------- 游戏评测列表 ----------------

def test_list_game_reviews_only_published(client):
    # game 1 (艾尔登法环)：种子 review 1 published + 3 篇追加评测（好/中/差评）= 4 篇公开
    r = client.get("/api/games/1/reviews")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 4
    assert all(i["status"] == "published" for i in data["items"])
    assert sum(1 for i in data["items"] if i["title"].startswith("《艾尔登法环》")) == 4
    # 追加评测携带完整四维评分
    for i in data["items"]:
        for k in ("score_story", "score_graphic", "score_gameplay", "score_opt"):
            assert i[k] is None or 1 <= i[k] <= 10


def test_list_game_reviews_default_page_size_5(client):
    data = client.get("/api/games/1/reviews").json()
    assert data["page_size"] == 5  # 路由默认 5，不被 services 默认值覆盖


def test_list_game_reviews_empty(client):
    # 不存在的游戏：公开评测为空（不校验游戏存在性）
    r = client.get("/api/games/99999/reviews")
    assert r.status_code == 200
    assert r.json()["total"] == 0
    assert r.json()["items"] == []


# ---------------- 游戏详情新字段（steam_url / 四维评分） ----------------

def test_game_detail_has_steam_url_and_scores(client):
    r = client.get("/api/games/1")
    assert r.status_code == 200
    data = r.json()
    assert data["steam_url"] == "https://store.steampowered.com/app/1245620/"
    assert 0 < data["score_story"] <= 10
    assert 0 < data["score_graphic"] <= 10
    assert 0 < data["score_gameplay"] <= 10
    assert 0 < data["score_opt"] <= 10
    assert data["rating_count"] >= 1


# ---------------- 相似游戏推荐 ----------------

def test_similar_games_returns_3_to_4(client):
    r = client.get("/api/games/1/similar")
    assert r.status_code == 200
    items = r.json()["items"]
    assert 3 <= len(items) <= 4
    for s in items:
        assert s["id"] != 1  # 排除自身
        for k in ("name", "cover_url", "average_score", "category_name"):
            assert k in s


def test_similar_games_same_category_first(client):
    # 游戏 1 是开放世界(4)：同分类游戏应优先出现
    r = client.get("/api/games/1/similar")
    items = r.json()["items"]
    assert any(s["category_id"] == 4 if "category_id" in s else s["category_name"] == "开放世界"
               for s in items)


def test_similar_games_not_found(client):
    r = client.get("/api/games/99999/similar")
    assert r.status_code == 404


# ---------------- 评测攻略数量 / 详情 / 评测评论 ----------------

def test_game_reviews_count(client):
    r = client.get("/api/games/1/reviews/count")
    assert r.status_code == 200
    data = r.json()
    assert data["game_id"] == 1
    assert data["count"] == 4  # 种子 1 篇 + 追加 3 篇公开评测


def test_game_reviews_count_not_found(client):
    r = client.get("/api/games/99999/reviews/count")
    assert r.status_code == 404


def test_get_review_detail_increments_read_count(client):
    r0 = client.get("/api/reviews/1")
    assert r0.status_code == 200
    data = r0.json()
    assert data["id"] == 1
    assert data["status"] == "published"
    for k in ("score_story", "score_graphic", "score_gameplay", "score_opt"):
        assert k in data
    r1 = client.get("/api/reviews/1")
    assert r1.json()["read_count"] == data["read_count"] + 1  # 阅读量 +1


def test_get_review_detail_unpublished_forbidden(client):
    # review 9 是草稿（未过审）：匿名访问 → 无权限提示 403（工单允许 404 或无权限提示）
    r = client.get("/api/reviews/9")
    assert r.status_code == 403


def test_get_review_detail_not_found(client):
    r = client.get("/api/reviews/99999")
    assert r.status_code == 404


def test_review_comments_isolated_from_game_comments(client):
    """评测专属评论区：target_type=review，与游戏短评论互不干扰。"""
    r = client.get("/api/reviews/1/comments")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 4
    assert all(c["target_type"] == "review" and c["target_id"] == 1 for c in items)


def test_review_comments_review_not_found(client):
    r = client.get("/api/reviews/99999/comments")
    assert r.status_code == 404
