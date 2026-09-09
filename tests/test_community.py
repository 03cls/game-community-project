"""社区模块测试：发帖/列表/点赞/收藏/楼中楼评论/风控/举报治理/个人主页/上传。"""
from __future__ import annotations

import pytest

from app.core import moderation


@pytest.fixture(autouse=True)
def _disable_rate_limit():
    """测试内关闭发帖/评论频率限制（避免连发触发 400）。"""
    old_post, old_comment = moderation.POST_INTERVAL_SECONDS, moderation.COMMENT_INTERVAL_SECONDS
    moderation.POST_INTERVAL_SECONDS = 0
    moderation.COMMENT_INTERVAL_SECONDS = 0
    yield
    moderation.POST_INTERVAL_SECONDS = old_post
    moderation.COMMENT_INTERVAL_SECONDS = old_comment


# ---------------- 列表 / 标签 / 搜索 ----------------

def test_list_posts_hot_and_fields(client):
    r = client.get("/api/community/posts?sort=hot&page_size=20")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 16
    hot_scores = [p["hot_score"] for p in data["items"]]
    assert hot_scores == sorted(hot_scores, reverse=True)
    p = data["items"][0]
    for k in ("id", "title", "tag", "author", "summary", "images", "image_count",
              "like_count", "fav_count", "comment_count", "view_count",
              "created_at", "my_liked", "my_favorited"):
        assert k in p


def test_latest_order_newest_first(client):
    r = client.get("/api/community/posts?sort=latest&page_size=5")
    items = r.json()["items"]
    times = [p["created_at"] for p in items]
    assert times == sorted(times, reverse=True)
    # 当天发布的「入手空洞骑士」帖（种子里 days=0）应排第一
    assert items[0]["title"].startswith("谢谢大家的推荐")


def test_tag_filter(client):
    r = client.get("/api/community/posts?tag=攻略&page_size=20")
    tags = {p["tag"] for p in r.json()["items"]}
    assert tags == {"攻略"}
    assert r.json()["total"] == 5


def test_keyword_filter(client):
    r = client.get("/api/community/posts?keyword=艾尔登法环")
    items = r.json()["items"]
    assert r.json()["total"] >= 1
    assert all("艾尔登法环" in p["title"] or "老头环" in p.get("summary", "")
               or "艾尔登法环" in p.get("summary", "") for p in items)


def test_tags_endpoint(client):
    r = client.get("/api/community/tags")
    assert r.status_code == 200
    assert r.json()["tags"] == ["游戏", "闲聊", "攻略", "吐槽"]


# ---------------- 发帖 ----------------

def test_create_post_requires_login(client):
    r = client.post("/api/community/posts", json={"title": "测试帖", "content": "正文"})
    assert r.status_code == 401


def test_create_post_and_detail_view(client, player_headers):
    payload = {"title": "测试发帖功能", "content": "这是一条测试正文内容。",
               "tag": "闲聊", "images": []}
    r = client.post("/api/community/posts", json=payload, headers=player_headers)
    assert r.status_code == 200, r.text
    post = r.json()["post"]
    assert post["title"] == "测试发帖功能"
    pid = post["id"]

    detail = client.get(f"/api/community/posts/{pid}").json()
    assert detail["content"] == "这是一条测试正文内容。"
    assert detail["view_count"] == post["view_count"] + 1  # 详情浏览量 +1

    lst = client.get("/api/community/posts?keyword=测试发帖功能").json()
    assert any(p["id"] == pid for p in lst["items"])


def test_create_post_validation(client, player_headers):
    r = client.post("/api/community/posts", json={"title": "x", "content": "正文"},
                    headers=player_headers)
    assert r.status_code == 400
    r = client.post("/api/community/posts", json={"title": "合法标题", "content": "", "images": []},
                    headers=player_headers)
    assert r.status_code == 400
    r = client.post("/api/community/posts", json={"title": "合法标题", "content": "正文", "tag": "不存在的标签"},
                    headers=player_headers)
    assert r.status_code == 400


def test_sensitive_content_blocked(client, player_headers):
    r = client.post("/api/community/posts",
                    json={"title": "正常标题", "content": "你就是个傻逼，知道吗", "tag": "闲聊"},
                    headers=player_headers)
    assert r.status_code == 400
    assert "违规" in r.json()["detail"]
    r = client.post("/api/community/posts/1/comments",
                    json={"content": "加微信 vx12345 低价代练"}, headers=player_headers)
    assert r.status_code == 400


def test_post_frequency_limit(client, player_headers, monkeypatch):
    moderation.POST_INTERVAL_SECONDS = 30
    r1 = client.post("/api/community/posts",
                     json={"title": "第一条帖", "content": "正文内容甲", "tag": "闲聊"},
                     headers=player_headers)
    assert r1.status_code == 200
    r2 = client.post("/api/community/posts",
                     json={"title": "第二条帖", "content": "正文内容乙", "tag": "闲聊"},
                     headers=player_headers)
    assert r2.status_code == 400
    assert "频繁" in r2.json()["detail"]


# ---------------- 点赞 / 收藏 ----------------

def test_post_like_toggle(client, player_headers):
    before = client.get("/api/community/posts/2").json()["like_count"]
    r = client.post("/api/community/posts/2/like", headers=player_headers)
    assert r.status_code == 200 and r.json()["liked"] is True
    assert r.json()["like_count"] == before + 1
    # 幂等：再点取消
    r2 = client.post("/api/community/posts/2/like", headers=player_headers)
    assert r2.json()["liked"] is False
    assert r2.json()["like_count"] == before
    detail = client.get("/api/community/posts/2", headers=player_headers).json()
    assert detail["my_liked"] is False


def test_post_favorite_toggle(client, creator_headers):
    before = client.get("/api/community/posts/3").json()["fav_count"]
    r = client.post("/api/community/posts/3/favorite", headers=creator_headers)
    assert r.json()["favorited"] is True
    assert r.json()["fav_count"] == before + 1
    r2 = client.post("/api/community/posts/3/favorite", headers=creator_headers)
    assert r2.json()["favorited"] is False
    assert r2.json()["fav_count"] == before


def test_like_requires_login(client):
    assert client.post("/api/community/posts/1/like").status_code == 401


# ---------------- 评论（楼中楼） ----------------

def test_comment_create_tree_and_count(client, player_headers, creator_headers):
    base = client.get("/api/community/posts/8").json()["comment_count"]
    # 一级评论
    r = client.post("/api/community/posts/8/comments",
                    json={"content": "推荐你试试星露谷"}, headers=player_headers)
    assert r.status_code == 200
    cid = r.json()["comment"]["id"]
    # 楼中楼回复
    r2 = client.post("/api/community/posts/8/comments",
                     json={"content": "同意，星露谷很适合新手", "parent_id": cid},
                     headers=creator_headers)
    assert r2.status_code == 200
    rid = r2.json()["comment"]["id"]
    assert r2.json()["comment"]["parent_id"] == cid

    data = client.get("/api/community/posts/8/comments").json()
    assert data["total"] == base + 2
    # 新评论挂在一级节点下
    top = [c for c in data["items"] if c["id"] == cid]
    assert len(top) == 1
    reply_ids = [x["id"] for x in top[0]["replies"]]
    assert rid in reply_ids
    # 帖子评论计数同步
    assert client.get("/api/community/posts/8").json()["comment_count"] == base + 2


def test_comment_validation(client, player_headers):
    r = client.post("/api/community/posts/1/comments", json={"content": ""},
                    headers=player_headers)
    assert r.status_code == 400
    # 回复不存在的评论
    r = client.post("/api/community/posts/1/comments",
                    json={"content": "测试", "parent_id": 99999}, headers=player_headers)
    assert r.status_code == 400


def test_comment_like_toggle(client, player_headers):
    r = client.post("/api/community/comments/1/like", headers=player_headers)
    assert r.status_code == 200 and r.json()["liked"] is True
    assert r.json()["like_count"] >= 1
    r2 = client.post("/api/community/comments/1/like", headers=player_headers)
    assert r2.json()["liked"] is False


def test_comment_delete_permissions(client, player_headers, creator_headers, admin_headers):
    # player 在帖子 8（作者 uid7）下发评论
    r = client.post("/api/community/posts/8/comments",
                    json={"content": "我是玩家评论"}, headers=player_headers)
    cid = r.json()["comment"]["id"]
    # 其他用户（creator，非帖子作者）不能删
    assert client.delete(f"/api/community/comments/{cid}",
                         headers=creator_headers).status_code == 403
    # 评论作者本人可删
    assert client.delete(f"/api/community/comments/{cid}",
                         headers=player_headers).status_code == 200

    # 帖子作者（uid7=萌新）可删除该帖下任意评论：用 admin 代发→不对，直接测种子帖1作者uid2
    # 种子帖 1 下评论 4（uid7）；帖作者 uid2(creator) 删除它
    assert client.delete("/api/community/comments/4",
                         headers=creator_headers).status_code == 200
    # 管理员可删任意评论
    assert client.delete("/api/community/comments/5",
                         headers=admin_headers).status_code == 200


def test_comment_on_missing_post(client, player_headers):
    r = client.get("/api/community/posts/9999/comments", headers=player_headers)
    assert r.status_code == 404


# ---------------- 删除帖子 ----------------

def test_delete_post_permissions(client, player_headers, creator_headers):
    # player 发帖
    pid = client.post("/api/community/posts",
                      json={"title": "待删除帖", "content": "正文", "tag": "吐槽"},
                      headers=player_headers).json()["post"]["id"]
    # 他人不能删
    assert client.delete(f"/api/community/posts/{pid}",
                         headers=creator_headers).status_code == 403
    # 作者可删
    assert client.delete(f"/api/community/posts/{pid}",
                         headers=player_headers).status_code == 200
    assert client.get(f"/api/community/posts/{pid}").status_code == 404


def test_admin_delete_any_post(client, admin_headers):
    r = client.delete("/api/community/posts/6", headers=admin_headers)
    assert r.status_code == 200
    assert client.get("/api/community/posts/6").status_code == 404


# ---------------- 举报与治理 ----------------

def test_report_requires_validation(client, player_headers):
    r = client.post("/api/community/reports",
                    json={"target_type": "post", "target_id": 1, "reason": "不存在的理由"},
                    headers=player_headers)
    assert r.status_code == 400
    assert client.post("/api/community/reports",
                       json={"target_type": "post", "target_id": 9999, "reason": "其他"},
                       headers=player_headers).status_code == 404
    assert client.post("/api/community/reports",
                       json={"target_type": "post", "target_id": 1, "reason": "垃圾广告"}
                       ).status_code == 401


def test_report_admin_remove_flow(client, player_headers, admin_headers):
    # 玩家举报帖 11
    r = client.post("/api/community/reports",
                    json={"target_type": "post", "target_id": 11,
                          "reason": "辱骂攻击", "detail": "内容引战"},
                    headers=player_headers)
    assert r.status_code == 200
    # 非管理员看不到举报队列
    assert client.get("/api/admin/reports", headers=player_headers).status_code == 403
    # 管理员看到待处理
    pending = client.get("/api/admin/reports?status=pending", headers=admin_headers).json()
    mine = [x for x in pending["items"] if x["target_id"] == 11 and x["target_type"] == "post"]
    assert len(mine) == 1
    rid = mine[0]["id"]
    # 处理：删除违规内容
    h = client.post(f"/api/admin/reports/{rid}/handle",
                    json={"action": "remove"}, headers=admin_headers)
    assert h.status_code == 200
    assert client.get("/api/community/posts/11").status_code == 404
    # 重复处理报错
    assert client.post(f"/api/admin/reports/{rid}/handle",
                       json={"action": "dismiss"}, headers=admin_headers).status_code == 400


def test_report_admin_ban_flow(client, player_headers, admin_headers):
    # 被封用户先登录拿 token（封禁后登录会被拒，用封禁前的 token 验证 403）
    new_man_token = client.post(
        "/api/auth/login",
        json={"username_or_email": "new_man", "password": "123456"}).json()["access_token"]
    new_man_headers = {"Authorization": f"Bearer {new_man_token}"}
    # 玩家举报帖 13（作者 uid7=new_man）
    client.post("/api/community/reports",
                json={"target_type": "post", "target_id": 13, "reason": "违法违规"},
                headers=player_headers)
    rid = [x for x in client.get("/api/admin/reports", headers=admin_headers).json()["items"]
           if x["target_id"] == 13][0]["id"]
    h = client.post(f"/api/admin/reports/{rid}/handle",
                    json={"action": "ban"}, headers=admin_headers)
    assert h.status_code == 200
    # 封禁后该用户的请求被拒（403 账号已封禁）
    r = client.post("/api/community/posts/1/like", headers=new_man_headers)
    assert r.status_code == 403
    # 帖 13 已随封禁删除
    assert client.get("/api/community/posts/13").status_code == 404


def test_report_dismiss_flow(client, player_headers, admin_headers):
    client.post("/api/community/reports",
                json={"target_type": "post", "target_id": 5, "reason": "其他"},
                headers=player_headers)
    rid = [x for x in client.get("/api/admin/reports", headers=admin_headers).json()["items"]
           if x["target_id"] == 5][0]["id"]
    h = client.post(f"/api/admin/reports/{rid}/handle",
                    json={"action": "dismiss"}, headers=admin_headers)
    assert h.status_code == 200 and h.json()["status"] == "dismissed"
    # 帖子仍在
    assert client.get("/api/community/posts/5").status_code == 200


# ---------------- 个人主页 ----------------

def test_profile_posts_public(client, player_headers):
    # uid2（creator）的帖子公开可见
    r = client.get("/api/community/users/2/posts?tab=posts")
    assert r.status_code == 200
    assert r.json()["tab"] == "posts"
    assert all(p["author"]["id"] == 2 for p in r.json()["items"])


def test_profile_favorites_privacy(client, player_headers):
    # 他人收藏列表 403
    r = client.get("/api/community/users/2/posts?tab=favorites", headers=player_headers)
    assert r.status_code == 403
    # 自己收藏可见（帖 6：player 种子里未收藏/点赞过）
    client.post("/api/community/posts/6/favorite", headers=player_headers)
    own = client.get("/api/community/users/3/posts?tab=favorites", headers=player_headers)
    assert own.status_code == 200
    assert any(p["id"] == 6 for p in own.json()["items"])
    # 自己点赞记录（帖 14：player 种子里未点过赞）
    client.post("/api/community/posts/14/like", headers=player_headers)
    likes = client.get("/api/community/users/3/posts?tab=likes", headers=player_headers)
    assert any(p["id"] == 14 for p in likes.json()["items"])


def test_profile_missing_user(client):
    assert client.get("/api/community/users/9999/posts").status_code == 404


# ---------------- 图片上传 ----------------

def test_upload_requires_login(client):
    r = client.post("/api/community/upload",
                    files={"file": ("a.png", b"x", "image/png")})
    assert r.status_code == 401


def test_upload_rejects_bad_ext(client, player_headers):
    r = client.post("/api/community/upload",
                    files={"file": ("virus.exe", b"x", "application/octet-stream")},
                    headers=player_headers)
    assert r.status_code == 400


def test_upload_image_ok(client, player_headers):
    fake_png = b"\x89PNG\r\n\x1a\n" + b"0" * 64
    r = client.post("/api/community/upload",
                    files={"file": ("shot.png", fake_png, "image/png")},
                    headers=player_headers)
    assert r.status_code == 200, r.text
    url = r.json()["url"]
    assert url.startswith("/static/uploads/") and url.endswith(".png")
    # 文件必须落到项目根 static/uploads（而非 app/static），且 URL 可直接访问
    import os
    project_uploads = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "static", "uploads")
    assert os.path.isfile(os.path.join(project_uploads, os.path.basename(url))), \
        "上传图片未落到项目根 static/uploads 目录"
    got = client.get(url)
    assert got.status_code == 200 and got.content == fake_png
    # 发帖可引用上传图
    post = client.post("/api/community/posts",
                       json={"title": "带图帖子", "content": "看图", "tag": "游戏",
                             "images": [url]},
                       headers=player_headers).json()["post"]
    assert post["image_count"] == 1
