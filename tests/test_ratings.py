"""游戏评分（1-10 分）与公开评测列表接口测试。

覆盖契约：
- 登录用户对游戏提交 1-10 分评分；同一用户仅一条记录，重复提交=修改分数；
- 未登录提交评分 401；非法分数 400；游戏不存在 404；
- 聚合统计：rating_count = 带四维评分的公开评测数 + 用户评分数，average_score 合并计算；
- 游戏详情返回 my_rating（未评分为 null）；
- GET /api/reviews 公开评测列表：时间倒序、keyword 按游戏名过滤、卡片字段齐全；
- GET /api/games/{id}/reviews 支持 keyword 过滤。
"""
from __future__ import annotations


# ---------------- 提交评分 ----------------

def test_rating_requires_login(client):
    r = client.post("/api/games/1/rating", json={"score": 8})
    assert r.status_code == 401


def test_rating_submit_and_reflect_in_detail(client, player_headers):
    # 未评分时 my_rating 为 null
    detail = client.get("/api/games/1", headers=player_headers).json()
    assert detail["my_rating"] is None
    before_count = detail["rating_count"]

    r = client.post("/api/games/1/rating", json={"score": 8}, headers=player_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "评分成功"
    assert data["my_rating"] == 8
    assert data["rating_count"] == before_count + 1  # 新增 1 名评分用户

    # 详情页可见我的评分，参与人数同步 +1
    detail = client.get("/api/games/1", headers=player_headers).json()
    assert detail["my_rating"] == 8
    assert detail["rating_count"] == before_count + 1


def test_rating_update_keeps_single_record(client, player_headers, db):
    from app.models import GameRating
    first = client.post("/api/games/1/rating", json={"score": 8}, headers=player_headers).json()
    second = client.post("/api/games/1/rating", json={"score": 10}, headers=player_headers).json()
    assert second["message"] == "评分已更新"
    assert second["my_rating"] == 10
    # 人数不因重复提交增加，仍是同一记录
    assert second["rating_count"] == first["rating_count"]
    me = client.get("/api/users/me", headers=player_headers).json()
    rows = db.query(GameRating).filter_by(game_id=1, user_id=me["id"]).all()
    assert len(rows) == 1 and rows[0].score == 10
    detail = client.get("/api/games/1", headers=player_headers).json()
    assert detail["my_rating"] == 10


def test_rating_invalid_score(client, player_headers):
    for bad in (0, 11, -3):
        r = client.post("/api/games/1/rating", json={"score": bad}, headers=player_headers)
        assert r.status_code == 400
        assert "1-10" in r.json()["detail"]


def test_rating_game_not_found(client, player_headers):
    r = client.post("/api/games/9999/rating", json={"score": 8}, headers=player_headers)
    assert r.status_code == 404


def test_rating_isolated_per_user(client, player_headers, creator_headers):
    a = client.post("/api/games/2/rating", json={"score": 9}, headers=player_headers).json()
    b = client.post("/api/games/2/rating", json={"score": 6}, headers=creator_headers).json()
    assert a["rating_count"] + 1 == b["rating_count"]  # 两个用户各计 1 人
    assert client.get("/api/games/2", headers=player_headers).json()["my_rating"] == 9
    assert client.get("/api/games/2", headers=creator_headers).json()["my_rating"] == 6
    # 未登录只可查看，无 my_rating 值
    assert client.get("/api/games/2").json()["my_rating"] is None


# ---------------- 聚合合并口径 ----------------

def test_aggregate_merges_user_scores_with_reviews(client, player_headers):
    """综合平均分 = 评测四维均值与用户评分合并平均；四维分仍仅由评测聚合。"""
    before = client.get("/api/games/1").json()
    # 种子中游戏 1 有带四维评分的公开评测；记录四维分不应被用户评分改变
    dims_before = (before["score_story"], before["score_graphic"],
                   before["score_gameplay"], before["score_opt"])
    assert before["rating_count"] >= 3  # 至少包含 3 篇带四维评分的公开评测

    client.post("/api/games/1/rating", json={"score": 1}, headers=player_headers)
    after = client.get("/api/games/1").json()
    assert after["rating_count"] == before["rating_count"] + 1
    assert after["average_score"] < before["average_score"]  # 打 1 分拉低综合分
    dims_after = (after["score_story"], after["score_graphic"],
                  after["score_gameplay"], after["score_opt"])
    assert dims_after == dims_before


# ---------------- 公开评测列表（首页评测专区） ----------------

def test_public_reviews_list_default_order_and_fields(client):
    r = client.get("/api/reviews?page=1&page_size=8")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 97  # 种子公开评测总数
    items = data["items"]
    assert 0 < len(items) <= 8
    for it in items:
        for k in ("id", "game_id", "title", "game_name", "game_cover",
                  "author_name", "score", "summary", "created_at"):
            assert k in it
        assert it["score"] is not None
        assert it["summary"]
    # 排序加权：精选优先 → 创作者等级高者优先 → 时间倒序
    keys = [(bool(it.get("is_featured")), it.get("author_level") or 0,
             it["created_at"]) for it in items]
    assert keys == sorted(keys, key=lambda k: (k[0], k[1], k[2]), reverse=True)


def test_public_reviews_keyword_filters_by_game_name(client):
    r = client.get("/api/reviews", params={"keyword": "艾尔登法环"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert all(it["game_name"] == "艾尔登法环" for it in data["items"])
    # 英文名也可命中
    r2 = client.get("/api/reviews", params={"keyword": "Elden"})
    assert r2.status_code == 200
    assert r2.json()["total"] >= 1


# ---------------- 游戏评测列表 keyword ----------------

def test_game_reviews_keyword_filter(client):
    base = client.get("/api/games/1/reviews?page=1&page_size=20").json()
    assert base["total"] >= 4
    hit = client.get("/api/games/1/reviews?page=1&page_size=20",
                     params={"keyword": "深度评测"}).json()
    assert 1 <= hit["total"] <= base["total"]
    assert all("深度评测" in it["title"] or "深度评测" in it["content"] for it in hit["items"])
    miss = client.get("/api/games/1/reviews", params={"keyword": "不存在的关键词XYZ"}).json()
    assert miss["total"] == 0
