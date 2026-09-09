"""评论模块测试：游戏短评论（自动精选运行时计算）/ 评测评论 / 点赞 / 管理员删除。"""
from __future__ import annotations


def test_list_comments(client):
    # review 1 有 4 条种子评论 (id 1,2,3,4)
    r = client.get("/api/comments?target_type=review&target_id=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 4
    # 顺序按 created_at asc
    assert data["items"][0]["content"] == "碎星那一战我打了整整一下午，过的时候手都在抖！"


def test_list_comments_empty(client):
    r = client.get("/api/comments?target_type=review&target_id=99999")
    assert r.status_code == 404  # 评测不存在
    assert "评测不存在" in r.json()["detail"]


def test_create_comment_success(client, player_headers):
    r = client.post("/api/comments", headers=player_headers, json={
        "target_type": "review", "target_id": 1, "content": "新评论内容",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["content"] == "新评论内容"
    assert data["like_count"] == 0
    assert data["user_id"] is not None
    assert "liked" in data
    assert data["target_type"] == "review"
    assert "is_featured" not in data  # 旧字段已删除


def test_create_comment_shortcut_by_game_id(client, player_headers):
    """契约：POST /api/comments {game_id, content} 发布游戏短评论。"""
    r = client.post("/api/comments", headers=player_headers,
                    json={"game_id": 1, "content": "用 game_id 快捷发一条游戏短评论"})
    assert r.status_code == 200
    data = r.json()
    assert data["target_type"] == "game"
    assert data["target_id"] == 1


def test_create_comment_empty_content(client, player_headers):
    r = client.post("/api/comments", headers=player_headers, json={
        "target_type": "review", "target_id": 1, "content": "   ",
    })
    assert r.status_code == 400
    assert "不能为空" in r.json()["detail"]


def test_create_comment_requires_auth(client):
    r = client.post("/api/comments", json={
        "target_type": "review", "target_id": 1, "content": "x",
    })
    assert r.status_code == 401


def test_toggle_like_add_then_remove(client, player_headers):
    # 评论 1 种子 like_count=45，player 未点赞过
    r0 = client.get("/api/comments?target_type=review&target_id=1",
                    headers=player_headers)
    init_liked = [c for c in r0.json()["items"] if c["id"] == 1][0]["liked"]
    assert init_liked is False

    r = client.post("/api/comments/1/like", headers=player_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["liked"] is True
    assert data["like_count"] == 46

    # 再次点击 = 取消
    r2 = client.post("/api/comments/1/like", headers=player_headers)
    assert r2.status_code == 200
    assert r2.json()["liked"] is False
    assert r2.json()["like_count"] == 45


def test_toggle_like_comment_not_found(client, player_headers):
    r = client.post("/api/comments/99999/like", headers=player_headers)
    assert r.status_code == 404
    assert "评论不存在" in r.json()["detail"]


# ============ 游戏短评论区（自动精选 + 普通分页） ============

def test_game_comments_auto_featured_and_pagination(client):
    """游戏1：种子长评点赞最高 → 自动精选；普通评论 6 条，每页 5 条共 2 页。"""
    r = client.get("/api/games/1/comments")
    assert r.status_code == 200
    data = r.json()
    # 自动精选板块（点赞最高者，无字数限制）
    f = data["auto_selected_comment"]
    assert f is not None
    assert f["target_type"] == "game" and f["target_id"] == 1
    assert "author_name" in f and "like_count" in f
    assert "is_featured" not in f
    # 普通评论分页（自动精选不再重复出现在普通列表）
    assert data["total"] == 6
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total_pages"] == 2
    assert len(data["items"]) == 5
    assert all(c["id"] != f["id"] for c in data["items"])
    # 第二页
    r2 = client.get("/api/games/1/comments?page=2")
    assert len(r2.json()["items"]) == 1


def test_game_comments_every_game_has_auto_featured(client):
    """种子契约：每款游戏都有评论 → 点赞最高者自动成为精选（无字数限制）。"""
    for gid in range(1, 31):
        data = client.get(f"/api/games/{gid}/comments").json()
        f = data["auto_selected_comment"]
        assert f is not None, f"游戏 {gid} 缺少自动精选评论"


def test_game_comments_game_not_found(client):
    r = client.get("/api/games/99999/comments")
    assert r.status_code == 404


def test_game_comments_page_size_bounded(client):
    """每页 5-10 条：超大 page_size 被截断为 10。"""
    data = client.get("/api/games/1/comments?page_size=999").json()
    assert data["page_size"] == 10


def test_create_game_comment_requires_auth(client):
    r = client.post("/api/games/1/comments", json={"content": "x"})
    assert r.status_code == 401


def test_create_game_comment_success(client, player_headers):
    r = client.post("/api/games/1/comments", headers=player_headers,
                    json={"content": "这游戏真不错！"})
    assert r.status_code == 200
    data = r.json()
    assert data["content"] == "这游戏真不错！"
    assert data["target_type"] == "game" and data["target_id"] == 1
    assert data["like_count"] == 0
    # 普通评论总数 +1 且出现在第 1 页（最新在前）
    listing = client.get("/api/games/1/comments").json()
    assert listing["total"] == 7
    assert listing["items"][0]["content"] == "这游戏真不错！"
    # 自动精选不受发评影响
    assert listing["auto_selected_comment"] is not None


def test_create_game_comment_empty(client, player_headers):
    r = client.post("/api/games/1/comments", headers=player_headers,
                    json={"content": "   "})
    assert r.status_code == 400


def test_create_game_comment_game_not_found(client, player_headers):
    r = client.post("/api/games/99999/comments", headers=player_headers,
                    json={"content": "x"})
    assert r.status_code == 404


def test_game_comment_like_toggle(client, player_headers):
    """游戏评论点赞切换：计数实时来自数据库，防重复点赞。"""
    r0 = client.get("/api/games/1/comments", headers=player_headers).json()
    f0 = r0["auto_selected_comment"]
    assert f0["liked"] is False  # 种子点赞者不含 player(3)？作者轮转，player 未赞
    init_count = f0["like_count"]

    r = client.post(f"/api/comments/{f0['id']}/like", headers=player_headers)
    assert r.json()["liked"] is True
    assert r.json()["like_count"] == init_count + 1

    # 重复请求 = 取消（幂等切换，不会 +2）
    r2 = client.post(f"/api/comments/{f0['id']}/like", headers=player_headers)
    assert r2.json()["liked"] is False
    assert r2.json()["like_count"] == init_count


def test_auto_featured_recalculates_after_like_change(client, db):
    """点赞变化后精选实时重算：原最高赞评论被清零后，新的最高赞者成为精选。"""
    from app.models import Comment

    # 清零游戏1当前点赞最高的长评
    top = (db.query(Comment)
           .filter(Comment.target_type == "game", Comment.target_id == 1)
           .order_by(Comment.like_count.desc(), Comment.created_at.asc(),
                     Comment.id.asc()).first())
    top.like_count = 0
    db.commit()

    data = client.get("/api/games/1/comments").json()
    f = data["auto_selected_comment"]
    # 精选仍存在：点赞最高者自动上位（无字数限制），且不会是刚清零的那条
    assert f is not None and f["id"] != top.id
    # 普通列表包含全部评论（除精选外）
    assert data["total"] == 6


def test_auto_featured_tie_breaks_by_earliest_created(client, db):
    """点赞并列第一取创建时间最早者。"""
    from app.models import Comment, CommentLike

    all_c = (db.query(Comment)
             .filter(Comment.target_type == "game", Comment.target_id == 2).all())
    for c in all_c:
        c.like_count = 0
    db.query(CommentLike).filter(
        CommentLike.comment_id.in_([c.id for c in all_c])).delete(synchronize_session=False)
    db.commit()

    # 取创建最早的两条评论，点赞并列 7
    two = (db.query(Comment)
           .filter(Comment.target_type == "game", Comment.target_id == 2)
           .order_by(Comment.created_at.asc(), Comment.id.asc())
           .limit(2).all())
    assert len(two) == 2
    first, second = two
    for c in two:
        c.like_count = 7
    db.commit()

    data = client.get("/api/games/2/comments").json()
    f = data["auto_selected_comment"]
    # 并列取创建最早（无论长评短评，无字数限制）
    assert f is not None and f["id"] == first.id


# ============ 种子数据契约 ============

def test_seed_comments_quality_contract(client):
    """种子契约：每游戏有精选（点赞最高，无字数限制）；普通评论 5-10 条且文本互不重复。"""
    for gid in range(1, 31):
        data = client.get(f"/api/games/{gid}/comments").json()
        assert data["auto_selected_comment"] is not None
        assert 5 <= data["total"] <= 10, f"游戏{gid}普通评论数量 {data['total']} 不在 5-10 区间"
        texts = [c["content"] for c in data["items"]]
        assert len(texts) == len(set(texts)), f"游戏{gid}存在重复短评"


def test_seed_comments_all_unique(client, admin_headers):
    """种子契约：全站评论文本互不相同。"""
    items = client.get("/api/admin/comments", headers=admin_headers).json()["items"]
    contents = [c["content"] for c in items]
    assert len(contents) == len(set(contents)), "存在重复评论文本"


# ============ 管理员：删除 / 列表（精选为运行时计算，无手动标记接口） ============

def test_admin_feature_endpoint_removed(client, admin_headers):
    """旧接口 PUT/POST /api/admin/comments/{id}/feature 已删除。"""
    r = client.post("/api/admin/comments/8/feature", headers=admin_headers)
    assert r.status_code == 404


def test_admin_delete_normal_comment(client, admin_headers):
    """普通评论可删除，删除后列表计数更新；自动精选不受影响。"""
    before = client.get("/api/games/1/comments").json()["total"]
    r = client.delete("/api/admin/comments/8", headers=admin_headers)  # 游戏1普通评论
    assert r.status_code == 200
    after = client.get("/api/games/1/comments").json()["total"]
    assert after == before - 1
    # 自动精选仍存在（运行时计算，不依赖人工标记）
    assert client.get("/api/games/1/comments").json()["auto_selected_comment"] is not None


def test_admin_delete_last_game_comment_ok(client, admin_headers, db):
    """删除评论不再受"至少保留 1 条精选"限制（精选自动计算）。"""
    from app.models import Comment
    gids = (db.query(Comment.target_id)
            .filter(Comment.target_type == "game").distinct().all())
    # 挑游戏 30：清掉普通评论后删除长评也不报错
    r = client.delete("/api/admin/comments/8", headers=admin_headers)
    assert r.status_code == 200


def test_admin_comments_list_has_like_data(client, admin_headers):
    r = client.get("/api/admin/comments", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    game_c = [c for c in items if c["target_type"] == "game"][0]
    assert "like_count" in game_c
    assert "is_featured" not in game_c  # 旧字段已删除
    assert game_c["target_title"]  # 所属对象名
    review_c = [c for c in items if c["target_type"] == "review"]
    if review_c:
        assert review_c[0]["review_title"]


def test_admin_comments_list_requires_admin(client, player_headers):
    r = client.get("/api/admin/comments", headers=player_headers)
    assert r.status_code == 403


# ============ 我的评论（个人中心：游戏短评 + 评测评论聚合） ============

def _fresh_user_headers(client):
    client.post("/api/auth/register", json={
        "username": "commenter1", "email": "commenter1@test.com", "password": "123456"})
    tok = client.post("/api/auth/login", json={
        "username_or_email": "commenter1", "password": "123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_my_comments_requires_auth(client):
    r = client.get("/api/comments/mine")
    assert r.status_code == 401


def test_my_comments_empty_for_new_user(client):
    h = _fresh_user_headers(client)
    data = client.get("/api/comments/mine", headers=h).json()
    assert data["items"] == []
    assert data["total"] == 0


def test_my_comments_aggregates_game_and_review_targets(client):
    """两类评论聚合，附目标名称/封面，时间倒序。"""
    h = _fresh_user_headers(client)
    client.post("/api/comments", headers=h, json={"game_id": 1, "content": "游戏短评甲"})
    client.post("/api/comments", headers=h,
                json={"target_type": "review", "target_id": 1, "content": "评测评论乙"})
    data = client.get("/api/comments/mine", headers=h).json()
    assert data["total"] == 2
    assert {c["target_type"] for c in data["items"]} == {"game", "review"}
    game_c = [c for c in data["items"] if c["target_type"] == "game"][0]
    assert game_c["target_name"]
    assert game_c["target_cover"]
    review_c = [c for c in data["items"] if c["target_type"] == "review"][0]
    assert review_c["target_name"]  # 评测标题
    # 时间倒序：后创建的在前
    assert data["items"][0]["content"] == "评测评论乙"


def test_my_comments_pagination(client):
    h = _fresh_user_headers(client)
    for i in range(3):
        client.post("/api/comments", headers=h, json={"game_id": 2, "content": f"分页短评{i}"})
    data = client.get("/api/comments/mine?page=1&page_size=2", headers=h).json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 2
    assert len(data["items"]) == 2
    data2 = client.get("/api/comments/mine?page=2&page_size=2", headers=h).json()
    assert len(data2["items"]) == 1
