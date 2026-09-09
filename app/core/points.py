"""创作者积分与等级体系（课设简化版）。

- 仅 PGC 游戏评测可获得积分，普通社区帖子不参与；
- 积分变动全部记录流水（PointRecord），等级由当前积分统一推导；
- 不实现防刷、积分兑换、现金奖励等商业功能。
"""
from __future__ import annotations

from typing import Optional, Tuple

# ---------------- 积分规则 ----------------
POINT_PUBLISH = 20.0        # 评测审核通过发布
POINT_FEATURED = 30.0       # 管理员标记精选
POINT_REVIEW_LIKE = 0.2     # 评测被点赞（每次）
POINT_REVIEW_FAV = 0.5      # 评测被收藏（每次）
POINT_DELETE_PENALTY = 30.0  # 评测被删除的额外扣分（同时追回该篇全部积分）

# ---------------- 等级配置（阈值为该等级最低积分） ----------------
# (等级, 代号, 名称, 阈值, 徽章色, 权益说明)
LEVELS = [
    (0, "L0", "见习创作者", 0, "gray",
     "可发布评测；已发布评测不可编辑"),
    (1, "L1", "普通创作者", 200, "blue",
     "展示等级徽章；单篇已发布评测获得 1 次编辑权限"),
    (2, "L2", "优质创作者", 500, "purple",
     "徽章；评测列表排序加权；工作台查看完整数据"),
    (3, "L3", "资深创作者", 1200, "gold",
     "徽章；首页「资深创作者专题」展示入口"),
    (4, "L4", "核心创作者", 2500, "rainbow",
     "彩虹徽章；全站最高等级展示"),
]

MAX_LEVEL = LEVELS[-1][0]


def level_for_points(points: float) -> int:
    """根据积分推导等级（取满足阈值的最高等级）。"""
    points = points or 0.0
    lvl = 0
    for lv, _code, _name, threshold, _color, _benefit in LEVELS:
        if points >= threshold:
            lvl = lv
    return lvl


def level_info(level: int) -> dict:
    """单个等级的展示信息。"""
    level = max(0, min(MAX_LEVEL, int(level or 0)))
    lv, code, name, threshold, color, benefit = LEVELS[level]
    return {"level": lv, "code": code, "name": name,
            "min_points": threshold, "color": color, "benefit": benefit}


def next_level(points: float) -> Tuple[Optional[dict], float]:
    """返回 (下一等级信息或 None, 距下一等级还差多少分)。"""
    points = points or 0.0
    cur = level_for_points(points)
    if cur >= MAX_LEVEL:
        return None, 0.0
    nxt = level_info(cur + 1)
    return nxt, max(0.0, round(nxt["min_points"] - points, 1))


def overview(points: float) -> dict:
    """积分概览：当前等级 + 升级进度，供工作台/前端直接消费。"""
    points = round(points or 0.0, 1)
    cur = level_for_points(points)
    nxt, needed = next_level(points)
    cur_info = level_info(cur)
    # 当前等级区间进度（进度条用）
    lower = cur_info["min_points"]
    upper = nxt["min_points"] if nxt else lower
    span = (upper - lower) if nxt else 1
    progress = round(min(1.0, max(0.0, (points - lower) / span)) * 100, 1) if nxt else 100.0
    return {
        "points": points,
        "level": cur,
        "level_code": cur_info["code"],
        "level_name": cur_info["name"],
        "level_color": cur_info["color"],
        "benefit": cur_info["benefit"],
        "next_level": nxt,
        "points_to_next": needed,
        "progress": progress,
        "is_max": nxt is None,
    }
