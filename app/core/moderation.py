"""社区内容风控：敏感词扫描 + 发言频率限制。

全员可发帖/评论（免审），因此必须在发布链路上做硬拦截：
- 敏感词命中 -> 400 拒绝发布，提示命中类别（不回显具体词，避免试探规避）；
- 频率限制 -> 防止刷屏/灌水；
- 举报 + 管理员删除/封禁构成事后治理闭环（见 services / admin 路由）。
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

# 分类敏感词表（教学演示级词库，可按运营需要扩充）
SENSITIVE_WORDS = {
    "辱骂攻击": ["傻逼", "煞笔", "废物", "滚蛋", "狗东西", "脑残", "贱人"],
    "色情低俗": ["约炮", "裸聊", "上门服务", "一夜情", "成人视频", "黄色网站"],
    "赌博诈骗": ["博彩", "六合彩", "赌钱", "开奖直播", "刷单", "稳赚不赔", "代开发票"],
    "违法违规": ["毒品", "枪支买卖", "假证", "洗钱", "代考"],
    "广告引流": ["加微信", "加q群", "加QQ群", "代购代练", "低价充值", "点击链接领取"],
}

# 扁平化一次，避免每次扫描重建
_ALL_WORDS = [(w, cat) for cat, words in SENSITIVE_WORDS.items() for w in words]

# 发言频率限制：两次发帖间隔 >= 30s；两次评论间隔 >= 10s
POST_INTERVAL_SECONDS = 30
COMMENT_INTERVAL_SECONDS = 10


def scan_sensitive(text: str) -> List[str]:
    """返回命中的违规类别列表（去重、保持顺序）。大小写不敏感。"""
    if not text:
        return []
    low = text.lower()
    hits: List[str] = []
    for word, cat in _ALL_WORDS:
        if word.lower() in low and cat not in hits:
            hits.append(cat)
    return hits


def assert_clean(*texts: str) -> None:
    """校验多段文本（标题+正文等），命中即抛 ValueError（service 层转 400）。"""
    hits: List[str] = []
    for t in texts:
        for cat in scan_sensitive(t or ""):
            if cat not in hits:
                hits.append(cat)
    if hits:
        raise ValueError("内容包含违规信息（" + "、".join(hits) + "），请修改后再发布")


def check_frequency(last_time: Optional[datetime], interval: int, what: str) -> None:
    """last_time 为该用户最近一次同类发言时间；过频则抛 ValueError。"""
    if last_time is not None:
        delta = (datetime.utcnow() - last_time).total_seconds()
        if delta < interval:
            wait = int(interval - delta) + 1
            raise ValueError(f"{what}太频繁，请 {wait} 秒后再试")
