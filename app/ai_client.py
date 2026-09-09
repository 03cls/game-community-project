"""AI 客户端：DeepSeek 调用 + 规则/Mock 兜底。

三函数规则与 mock.js 的 aiAudit/aiRecommend/aiCreator 完全一致；
有 DEEPSEEK_API_KEY 时调用 DeepSeek chat completions，失败/无 key 时走 Mock。
DeepSeek 调用使用 httpx.AsyncClient。
"""
from __future__ import annotations

import json
import random
import re
from typing import Any, List, Optional

import httpx

from app.core.config import settings

# ---------------- 规则常量（与 mock.js 一致） ----------------

_AD_WORDS = ["加群", "微信群", "微信", "vx", "qq群", "qq群", "代购", "低价代充", "代充",
             "http://", "https://", ".com", "免费领", "领皮肤"]
_ABUSE_WORDS = ["傻逼", "垃圾游戏", "废物", "脑残", "滚出", "引战", "狗都不玩"]

_AI_TIMEOUT = 30.0


# ---------------- 审核：ai_audit ----------------

def _mock_audit(title: str, content: str) -> dict:
    text = (str(title) + " " + str(content)).lower()
    hit: List[str] = []
    for w in _AD_WORDS:
        if w.lower() in text:
            hit.append('广告引流：命中"' + w + '"类导流内容')
    for w in _ABUSE_WORDS:
        if w in text:
            hit.append('辱骂引战：命中"' + w + '"类攻击表述')
    ad_hit = any(w.lower() in text for w in _AD_WORDS)
    if hit and ad_hit:
        return {"status": "rejected", "risk_score": 85 + min(10, len(hit) * 3), "reasons": hit}
    if hit:
        return {"status": "manual_review", "risk_score": 55 + len(hit) * 5, "reasons": hit}
    return {"status": "passed", "risk_score": 2 + random.randint(0, 7),
            "reasons": ["内容正常，未命中风险维度"]}


def _valid_audit(obj: Any) -> bool:
    return (isinstance(obj, dict)
            and obj.get("status") in ("passed", "rejected", "manual_review")
            and isinstance(obj.get("risk_score"), int)
            and isinstance(obj.get("reasons"), list))


async def _deepseek_audit(title: str, content: str) -> dict:
    system = (
        "你是游戏社区的内容审核 AI。请按如下规则判定评测内容：\n"
        "广告引流词：加群/微信群/微信/vx/qq群/代购/低价代充/代充/http://|https://|.com/免费领/领皮肤；"
        "辱骂引战词：傻逼/垃圾游戏/废物/脑残/滚出/引战/狗都不玩。\n"
        "规则：若命中且含广告词 -> status=rejected, risk_score=85+min(10,hit*3)；"
        "仅命中辱骂词 -> status=manual_review, risk_score=55+hit*5；"
        "未命中 -> status=passed, risk_score=2~9。\n"
        "只输出 JSON，格式：{\"status\": str, \"risk_score\": int, \"reasons\": [str]}。"
    )
    user = f"标题：{title}\n正文：{content}"
    raw = await _chat(system, user, json_mode=True)
    obj = json.loads(raw)
    if not _valid_audit(obj):
        raise ValueError("invalid audit response")
    return obj


async def ai_audit(title: str, content: str) -> dict:
    """审核评测，返回 {status, risk_score, reasons}。"""
    mock = _mock_audit(title, content)
    if not settings.ai_enabled:
        return mock
    try:
        return await _deepseek_audit(title, content)
    except Exception:
        return mock


# ---------------- 推荐：ai_recommend ----------------

def _rule_recommend(db_session, user_id: int, preferences: Optional[str]) -> List[dict]:
    from app.models import Favorite, Game, PlayRecord
    db = db_session
    liked_ids = set()
    for f in db.query(Favorite.game_id).filter(Favorite.user_id == user_id).all():
        liked_ids.add(f[0])
    for r in db.query(PlayRecord.game_id).filter(PlayRecord.user_id == user_id).all():
        liked_ids.add(r[0])
    pool = db.query(Game).filter(Game.is_online.is_(True)).all()
    pool = [g for g in pool if g.id not in liked_ids]
    pref = (preferences or "").lower()

    def score_of(g: Game) -> int:
        s = g.hot or 0
        if pref:
            hay = ((g.name or "") + " " + (g.name_en or "") + " "
                   + " ".join(g.tags) + " " + (g.description or "")).lower()
            for kw in re.split(r"[\s,，、]+", pref):
                if kw and kw in hay:
                    s += 40
        return s

    pool.sort(key=score_of, reverse=True)
    picks = pool[:3]
    out = []
    for g in picks:
        tags = g.tags
        if preferences:
            reason = ("根据你的偏好「" + preferences + "」，《" + g.name + "》(" + (g.name_en or "")
                      + ") 是 " + " / ".join(tags[:2]) + " 类型的代表作，Steam 口碑极佳。")
        else:
            reason = ("基于你的收藏与游玩记录推荐：《" + g.name + "》与你喜欢的游戏风格相近，"
                      + "、".join(tags[:2]) + " 元素突出，综合评分 " + str(g.average_score) + " 分。")
        out.append({
            "game_id": g.id,
            "game_name": g.name,
            "cover_url": g.cover_url or "",
            "reason": reason,
            "average_score": g.average_score,
        })
    return out


async def _deepseek_recommend(db_session, user_id: int, preferences: Optional[str]) -> List[dict]:
    from app.models import Favorite, Game, PlayRecord
    db = db_session
    liked_ids = set()
    for f in db.query(Favorite.game_id).filter(Favorite.user_id == user_id).all():
        liked_ids.add(f[0])
    for r in db.query(PlayRecord.game_id).filter(PlayRecord.user_id == user_id).all():
        liked_ids.add(r[0])
    pool = db.query(Game).filter(Game.is_online.is_(True)).all()
    pool = [g for g in pool if g.id not in liked_ids]
    catalog = [{"id": g.id, "name": g.name, "tags": g.tags, "score": g.average_score}
               for g in pool]
    system = (
        "你是游戏推荐 AI。基于用户偏好与候选游戏列表，挑选最合适的 3 款并给出推荐理由。"
        "只输出 JSON 数组，每项 {\"game_id\": int, \"reason\": str, \"average_score\": float}。"
    )
    user = ("偏好：" + (preferences or "（无明确偏好，参考收藏/游玩记录）")
            + "\n候选游戏：" + json.dumps(catalog, ensure_ascii=False))
    raw = await _chat(system, user, json_mode=True)
    items = json.loads(raw)
    name_by_id = {g.id: g for g in pool}
    out = []
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                continue
            gid = it.get("game_id")
            g = name_by_id.get(gid)
            if not g:
                continue
            out.append({
                "game_id": g.id,
                "game_name": g.name,
                "cover_url": g.cover_url or "",
                "reason": str(it.get("reason") or ""),
                "average_score": g.average_score,
            })
    if len(out) != 3:
        raise ValueError("recommend count mismatch")
    return out


async def ai_recommend(db_session, user_id: int, preferences: Optional[str]) -> List[dict]:
    """返回 [{game_id, game_name, cover_url, reason, average_score}]。"""
    rule = _rule_recommend(db_session, user_id, preferences)
    if not settings.ai_enabled:
        return rule
    try:
        return await _deepseek_recommend(db_session, user_id, preferences)
    except Exception:
        return rule


# ---------------- 创作助手：ai_creator ----------------

def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def _mock_creator(game_name: str, action: Optional[str], message: Optional[str],
                  content_context: Optional[str]) -> dict:
    gn = game_name or "该游戏"
    msg = message or ""
    act = action or ""
    if act == "outline" or "大纲" in msg:
        return {"reply": "为《" + gn + "》建议的评测大纲：\n\n"
                         "一、开篇总评（一句话立场 + 综合评分）\n"
                         "二、画面与音效表现\n"
                         "三、核心玩法 / 战斗系统深度\n"
                         "四、剧情与叙事\n"
                         "五、亮点与不足（客观列出 2-3 条缺点）\n"
                         "六、适合人群与购买建议\n\n"
                         "你可以按这个结构展开，需要我先写哪一部分？"}
    if act == "tips" or "通关" in msg or "思路" in msg or "攻略" in msg:
        return {"reply": "《" + gn + "》通关思路建议：\n\n"
                         "1. 前期优先提升生存能力（血量/防御），不要急于推进主线；\n"
                         "2. 遇到卡关 Boss 可以先探索支线获取装备与等级；\n"
                         "3. 善用元素/属性克制，观察 Boss 的前摇动作；\n"
                         "4. 资源类消耗品留到关键战斗使用。\n\n"
                         "如果你告诉我具体卡在哪一场战斗，我可以给出针对性打法。"}
    if act == "polish" or "润色" in msg:
        ctx = _strip_tags(content_context or "").strip()[:60]
        return {"reply": "润色后的表达建议：\n\n"
                         "原文：「" + (ctx or "（请先在编辑器中写一段正文）") + "」\n\n"
                         "润色：「这段体验堪称本作最具张力的时刻——难度的克制与反馈的爽快"
                         "在此达成了精妙平衡，让人在反复挑战中越挫越勇。」\n\n"
                         "润色思路：把主观感受具象化，增加\"张力/克制/反馈\"等专业评测词汇，"
                         "让表达更有说服力。"}
    if act == "pros" or "优缺点" in msg or "分析" in msg:
        return {"reply": "《" + gn + "》优缺点分析：\n\n"
                         "优点：\n"
                         "+ 核心玩法循环扎实，上手容易精通难；\n"
                         "+ 美术与音乐风格辨识度高；\n"
                         "+ 内容量大，性价比突出（Steam 好评如潮）。\n\n"
                         "不足：\n"
                         "- 新手引导偏弱，初期可能有挫败感；\n"
                         "- 部分系统后期重复度略高。\n\n"
                         "建议在评测中优缺点成对呈现，更有说服力。"}
    if "开头" in msg or "引入" in msg or "开场" in msg:
        opens = [
            "如果要用一个词形容《" + gn + "》的体验，我会选「上头」。从初见时被画面惊艳，"
            "到中期被玩法深度折服，再到通关后怅然若失——它几乎做对了所有关键决策。",
            "凌晨两点，我盯着《" + gn + "》的结算界面，做的第一件事是点击了「新开一局」——"
            "这种「再来一次」的冲动，就是对本作玩法魅力最直接的注脚。",
            "在玩《" + gn + "》之前，我以为这个品类早已被做透；直到第三个小时，"
            "我默默关掉了写了一半的同类对比文档。有些游戏，必须亲自上手才能理解。",
            "初见《" + gn + "》时我以为它只是「差不多」的水平，直到第一个转折点出现——"
            "那一刻我合上了准备好的挑刺清单，开始认真体验。",
        ]
        return {"reply": "《" + gn + "》评测开头示范：\n\n「" + random.choice(opens) + "」\n\n"
                         "开头技巧：用一个具象场景或鲜明观点切入，先给结论再展开论证，"
                         "比平铺直叙的背景介绍更抓人。"}
    if "结尾" in msg or "总结" in msg:
        closes = [
            "综合来看，《" + gn + "》以扎实的玩法循环与出色的美术表达，交出了一份高分答卷——"
            "尽管新手引导稍有缺憾，但瑕不掩瑜。如果你喜欢这类作品，它值得你立即入手。",
            "《" + gn + "》并不完美，但它敢于做别人不敢做的选择；当制作名单滚动时，"
            "你会明白这份冒险的重量。推荐给每一位还在观望的玩家。",
            "如果你问我值不值得玩：主线 60 小时，每一章都有惊喜，通关后还惦记着二周目——"
            "《" + gn + "》已经用行动回答了这个问题。",
            "好的游戏会留尾巴。《" + gn + "》通关一周后，我依然会在通勤路上想起某个场景——"
            "能被记住的体验，就是最高分值的好评。",
        ]
        return {"reply": "《" + gn + "》评测结尾示范：\n\n「" + random.choice(closes) + "」\n\n"
                         "结尾技巧：总结核心观点 → 重申立场与评分 → 给出明确的人群建议，形成闭环。"}
    if "标题" in msg or "起个名" in msg or "起名" in msg:
        t1 = ["一场值得单曲循环的冒险", "教科书级别的玩法循环", "越骂越香的宝藏之作", "把类型上限又抬高了一截"]
        t2 = ["上手 40 小时后，聊聊它到底香在哪", "全成就之后的真实评价", "通关三周目，我改了评分", "删档重玩一次后的新答案"]
        t3 = ["它配得上所有期待吗", "年度黑马还是营销泡沫", "被低估的神作还是时代的眼泪", "这份情怀值不值得买单"]
        return {"reply": "《" + gn + "》评测标题参考：\n\n"
                         "1. 「《" + gn + "》：" + random.choice(t1) + "」\n"
                         "2. 「" + random.choice(t2) + "——《" + gn + "》深度体验」\n"
                         "3. 「《" + gn + "》评测：" + random.choice(t3) + "」\n\n"
                         "起名技巧：观点前置 + 数字/对比制造记忆点，避免「XX游戏测评」这类平标题。"}
    if "评分" in msg or "打分" in msg or "怎么给分" in msg:
        return {"reply": "评分建议（10 分制四维）：剧情 / 画面 / 玩法 / 优化分别打分，再取均值为综合分。\n\n"
                         "· 8-10 出色：同类标杆\n· 6-7 及格：有亮点有明显短板\n"
                         "· 4-5 拉胯：不建议原价入\n· 0-3 灾难：慎入\n\n"
                         "参考 Steam 好评率与同类横向对比，评分更有说服力。"}
    return {"reply": "收到！关于《" + gn + "》，我可以帮你：\n"
                     "· 生成评测大纲\n"
                     "· 梳理通关思路\n"
                     "· 润色已有文案\n"
                     "· 分析游戏优缺点\n"
                     "· 写开头 / 写结尾 / 起标题 / 评分建议\n\n"
                     "点击上方快捷按钮，或直接描述你的需求即可。"}


async def _deepseek_creator(game_name: str, action: Optional[str], message: Optional[str],
                           content_context: Optional[str]) -> dict:
    gn = game_name or "该游戏"
    system = (
        "你是游戏评测创作助手。根据用户的动作或消息，针对指定游戏给出简明实用的中文创作建议。"
        "动作可选：outline(大纲)/tips(通关思路)/polish(润色文案)/pros(优缺点分析)。"
        "只输出 JSON：{\"reply\": str}，reply 用 \\n 分段。"
    )
    user = (f"游戏：{gn}\n动作：{action or ''}\n消息：{message or ''}\n"
            f"待润色原文：{content_context or ''}")
    raw = await _chat(system, user, json_mode=True)
    obj = json.loads(raw)
    if not isinstance(obj, dict) or not isinstance(obj.get("reply"), str):
        raise ValueError("invalid creator response")
    return obj


async def _ollama_creator(db, game_name: str, action: Optional[str], message: Optional[str],
                          content_context: Optional[str]) -> dict:
    """本地 Ollama（qwen2.5:3b）攻略创作助手：注入项目背景 + 平台数据快照 + 游戏目录 + 评测规范 + 创作上下文，
    返回 {reply}。模型用自然语言回答，更稳定（小模型不强求 JSON 输出）。"""
    gn = game_name or "该游戏"
    digest = _build_platform_digest(db)
    catalog_lines = "\n".join(
        "· %s（分类：%s，标签：%s，评分：%s，%d 人评分，热度 %d）" % (
            m["name"], m["category"],
            "/".join(m["tags"][:3]) or "未分类",
            m["score"], m["rating_count"], m["hot"])
        for m in digest["game_meta"])
    system = (
        "你是「GameReview AI · AI 游戏社区评测分享平台」的 AI 攻略创作助手，服务于平台创作者。\n"
        "## 你的职责\n"
        "1. 帮创作者撰写游戏评测：生成大纲、写开头/结尾、起标题、给评分建议；\n"
        "2. 梳理游戏通关思路与打法建议；\n"
        "3. 润色已有评测文案，提升专业度与可读性；\n"
        "4. 分析游戏优缺点，帮作者客观成对地呈现。\n\n"
        "## 平台评测规范\n"
        "- 评测结构固定为：标题 + 关联游戏 + 正文 + 标签 + 四维评分（剧情/画面/玩法/优化，1-10 整数）。"
        "四维均值即综合评分，会聚合到游戏页平均分，需客观负责。\n"
        "- 评测提交后默认待审核，经 AI 风控打分后自动通过/待人工/驳回；首页与游戏评测列表不展示待审核评测。\n"
        "- 创作者积分：发布评测 +20、精选 +30、获赞 +0.2、收藏 +0.5；"
        "等级 L1(100)/L2(300)/L3(600)/L4(1000)；L0 不可编辑已发布评测，L1+ 每篇可编辑 1 次；"
        "抄袭扣分清零降 L0；删除评测扣除该评测所得分 + 额外 30 分。\n"
        "- 精选评测优先展示；评测列表排序：精选 → 创作者等级 → 发布时间。\n\n"
        + digest["text"] + "\n\n"
        + "## 平台游戏库目录（共 %d 款，写评测时请以此为准）\n" % len(digest["game_meta"])
        + catalog_lines + "\n\n"
        + "## 回答要求\n"
        "- 用简体中文、专业但不失生动的评测文风；\n"
        "- 回答控制在 400 字以内，可用分点或短段落，用 \\n 分段；\n"
        "- 推荐标题时给出 3 个不同风格的候选；评分建议给出四维参考区间；\n"
        "- 润色时给出「原文 → 润色后 → 润色思路」三段式；\n"
        "- 动作参数：outline=大纲、tips=通关思路、polish=润色、pros=优缺点分析；"
        "若消息中含关键词（开头/结尾/标题/评分）按对应需求作答。"
    )
    user_msg = ("游戏：《%s》\n动作：%s\n用户消息：%s\n待润色原文：%s"
                % (gn, action or "", message or "", content_context or ""))
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
        "options": {"temperature": 0.6, "num_predict": 800},
    }
    async with httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL, timeout=60.0) as client:
        resp = await client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
    reply = str(data.get("message", {}).get("content", "")).strip()
    if not reply:
        raise ValueError("ollama empty creator reply")
    return {"reply": reply}


async def ai_creator(db, game_name: str, action: Optional[str], message: Optional[str],
                     content_context: Optional[str]) -> dict:
    """返回 {reply: str}。优先级：本地 Ollama → DeepSeek → 规则引擎兜底。"""
    mock = _mock_creator(game_name, action, message, content_context)
    # 优先本地 Ollama（轻量中文模型 qwen2.5:3b）
    if settings.ollama_enabled:
        try:
            return await _ollama_creator(db, game_name, action, message, content_context)
        except Exception:
            pass
    # 次选 DeepSeek 云端
    if settings.DEEPSEEK_API_KEY:
        try:
            return await _deepseek_creator(game_name, action, message, content_context)
        except Exception:
            pass
    return mock


# ---------------- 对话助手：ai_chat ----------------

# 意图关键词
_GREET_WORDS = ["你好", "您好", "hi", "hello", "在吗", "哈喽"]
_RECO_WORDS = ["推荐", "好玩", "介绍", "想玩", "类似", "什么游戏", "哪些游戏", "求游戏", "有什么游戏",
               "值得玩", "安利", "入手"]
_SCORE_WORDS = ["评分", "多少分", "得分", "分数", "怎么样", "口碑", "值得一玩吗", "好玩吗"]
_GUIDE_WORDS = ["攻略", "卡关", "怎么过", "怎么打", "技巧", "新手", "怎么玩", "打法"]
_HELP_WORDS = ["怎么发帖", "如何发帖", "申请创作者", "成为创作者", "创作者", "积分", "等级",
               "审核", "举报", "收藏", "点赞", "怎么用", "评分规则", "短评", "平台功能"]

_PLATFORM_FAQ = {
    "创作者": "成为创作者：在「个人中心 → 创作者申请」提交申请（10-200 字申请理由），管理员审核通过后即可获得创作者权限，"
              "解锁评测发布、AI 攻略创作助手与积分等级体系。",
    "积分": "创作者积分规则：发布评测 +20，被标记精选 +30，评测被点赞 +0.2/次，被收藏 +0.5/次；删除评测扣 30 分，"
            "抄袭违规积分清零并降为 L0。等级从积分累计升级：L0→L1→L2→L3→L4。",
    "等级": "创作者等级由累计积分决定：L1 见习（100 分）、L2 正式（300 分）、L3 资深（600 分，首页专题展示）、"
            "L4 核心（1000 分）。L2+ 发布的评测在列表中享有流量加权。",
    "审核": "评测提交后先经 AI 审核：内容正常自动通过发布；命中广告/辱骂等风险词会转人工或直接驳回。"
            "管理员也会进行复核，可在「个人中心 → 我的评测」查看状态。",
    "举报": "社区内容支持举报：帖子/评论页点击举报按钮，填写理由提交；管理员会在后台处理（驳回 / 删除违规内容 / 删除并封禁）。",
    "发帖": "社区发帖：登录后在社区页点击「发布帖子」，支持最多 9 张配图，标签可选 游戏/闲聊/攻略/吐槽。"
            "发帖免审直接公开，但有敏感词过滤与频率限制（30 秒一条）。",
    "收藏": "收藏功能：游戏详情页可收藏游戏，评测详情页可收藏评测，帖子可收藏；均可在「个人中心」对应栏目查看。",
    "点赞": "点赞功能：评测、评论、帖子、游戏评论都支持点赞；为他人的评测点赞还会给创作者加分哦。",
    "评分规则": "游戏评分规则：每款游戏支持 1-10 分综合评分，也可按剧情/画面/玩法/优化四个维度分别打分；综合分由已发布评测与全部用户评分"
                "实时聚合（四舍五入保留 1 位小数），四维雷达分仅统计评测的维度分。登录后在游戏详情页即可打分。",
    "短评": "短评与评测的区别：游戏短评是详情页的轻量点评（几句话 + 评分），登录即可发；评测（长文攻略）只有创作者/管理员能发布，"
            "需经 AI 审核通过后公开，包含标题、正文、标签与四维评分，还会计入创作者积分。两套系统相互独立。",
    "平台功能": "平台功能一览：浏览游戏库与 AI 聚合评分、查看四维雷达图、阅读创作者评测与玩家短评、社区发帖交流（支持配图与举报）、"
                "收藏游戏/评测/帖子、申请成为创作者发布评测攻略，还有首页 AI 推荐助手随时陪你聊游戏。",
}

# ---------------- 游戏知识库（游戏库内置游戏的真实知识点） ----------------

# 别名 → 游戏库标准名（覆盖玩家常用昵称/黑话）
_GAME_ALIASES = {
    "老头环": "艾尔登法环", "艾尔登": "艾尔登法环", "elden ring": "艾尔登法环",
    "博德之门": "博德之门 3", "bg3": "博德之门 3",
    "黑猴": "黑神话：悟空", "黑神话": "黑神话：悟空", "悟空": "黑神话：悟空", "wukong": "黑神话：悟空",
    "赛博朋克": "赛博朋克 2077", "2077": "赛博朋克 2077", "夜之城": "赛博朋克 2077",
    "大表哥": "荒野大镖客：救赎 2", "大镖客": "荒野大镖客：救赎 2", "rdr2": "荒野大镖客：救赎 2",
    "巫师3": "巫师 3：狂猎", "巫师三": "巫师 3：狂猎", "杰洛特": "巫师 3：狂猎", "witcher": "巫师 3：狂猎",
    "cs2": "反恐精英 2", "csgo": "反恐精英 2", "cs": "反恐精英 2",
    "星露谷": "星露谷物语", "种田": "星露谷物语", "stardew": "星露谷物语",
    "文明6": "文明 6", "文明六": "文明 6",
    "极限竞速": "极限竞速：地平线 5", "地平线5": "极限竞速：地平线 5", "地平线五": "极限竞速：地平线 5",
    "零之曙光": "地平线：零之曙光", "地平线": "地平线：零之曙光",
    "吃鸡": "绝地求生", "pubg": "绝地求生",
    "apex": "Apex 英雄",
    "doom": "毁灭战士：永恒", "毁灭战士": "毁灭战士：永恒",
    "老滚": "上古卷轴 5：天际 特别版", "天际": "上古卷轴 5：天际 特别版", "上古卷轴": "上古卷轴 5：天际 特别版", "skyrim": "上古卷轴 5：天际 特别版",
    "辐射4": "辐射 4",
    "质量效应": "质量效应：传奇版",
    "只狼": "只狼：影逝二度", "打铁": "只狼：影逝二度", "sekiro": "只狼：影逝二度",
    "鬼泣": "鬼泣 5", "dmc": "鬼泣 5",
    "怪猎": "怪物猎人：世界", "mhw": "怪物猎人：世界",
    "死亡细胞": "死亡细胞",
    "gta5": "侠盗猎车手 5", "gta": "侠盗猎车手 5", "侠盗猎车": "侠盗猎车手 5", "洛圣都": "侠盗猎车手 5",
    "霍格沃茨": "霍格沃茨之遗", "哈利波特": "霍格沃茨之遗",
    "死亡搁浅": "死亡搁浅", "death stranding": "死亡搁浅", "小岛": "死亡搁浅",
    "天际线": "城市：天际线",
    "环世界": "环世界", "rimworld": "环世界",
    "xcom": "XCOM 2",
    "拉力赛": "尘埃拉力赛 2.0", "尘埃": "尘埃拉力赛 2.0",
    # 罗马数字 / 拼写变体 / 更多黑话
    "文明vi": "文明 6", "civilization 6": "文明 6", "civilization": "文明 6",
    "怪物猎人世界": "怪物猎人：世界", "怪物猎人": "怪物猎人：世界", "猛汉": "怪物猎人：世界", "mhw世界": "怪物猎人：世界",
    "elden": "艾尔登法环", "法环": "艾尔登法环",
    "gtav": "侠盗猎车手 5", "gta线上": "侠盗猎车手 5",
    "黑悟空": "黑神话：悟空",
    "巫师3狂猎": "巫师 3：狂猎", "狂猎": "巫师 3：狂猎",
    "赛博朋克2077": "赛博朋克 2077",
    "荒野大镖客2": "荒野大镖客：救赎 2", "荒野大镖客救赎2": "荒野大镖客：救赎 2",
    "辐射四": "辐射 4", "fallout": "辐射 4",
}

_GAME_KNOWLEDGE = {
    "艾尔登法环": {
        "intro": "FromSoftware 与《冰与火之歌》作者乔治·R·R·马丁联手打造的开放世界魂系 ARPG，扮演褪色者在交界地追寻艾尔登法环。",
        "facts": ["荣获 TGA 2022 年度游戏，全球销量超 2500 万份",
                  "马丁负责世界观与神话设定，宫崎英高负责关卡与玩法设计",
                  "2024 年大型 DLC「黄金树之影」发售，再度掀起魂学家考据热潮",
                  "玩家戏称 Boss 玛莲妮亚为「新人杀手」，召唤骨灰是降低难度的关键"],
        "tips": ["开局别硬刚主线 Boss，先跑图收集卢恩与骨灰、战灰提升实力",
                 "灵马托雷特可以二段跳，很多看似过不去的悬崖其实能绕上去"],
    },
    "博德之门 3": {
        "intro": "拉瑞安工作室基于 D&D 5e 规则打造的 CRPG 巅峰，剧情选择极度自由，队友塑造鲜活。",
        "facts": ["荣获 TGA 2023 年度游戏与 BAFTA 最佳游戏",
                  "开发历时约 7 年，文本量超 200 万字，配音演员 200 多位",
                  "Steam 好评如潮，首发时同时在线峰值超 87 万，创 CRPG 纪录",
                  "每个 NPC 都可以被杀——世界会随之改变，二周目体验完全不同"],
        "tips": ["多和队友对话提升好感，营地剧情会解锁支线与浪漫线",
                 "善用环境与高度差，火焰箭矢点燃油桶是经典开局"],
    },
    "黑神话：悟空": {
        "intro": "游戏科学打造的首款国产 3A 动作 RPG，以《西游记》为蓝本，扮演天命人重走西游路。",
        "facts": ["发售首月全球销量突破 2000 万份，创国产游戏纪录",
                  "Steam 同时在线峰值约 240 万，为单机游戏历史最高",
                  "荣获 TGA 2024 最佳动作游戏与玩家之声奖项",
                  "场景大量实景扫描山西古建筑，被带火了一批「跟着黑神话旅游」路线"],
        "tips": ["棍势三段蓄力接劈棍是核心输出手法，学会识破（完美闪避）能大幅提升容错",
                 "多收集「眼、耳、鼻、舌、身」六根与葫芦，Build 成型后战斗体验质变"],
    },
    "赛博朋克 2077": {
        "intro": "CD Projekt Red 打造的开放世界动作 RPG，在夜之城扮演雇佣兵 V 追寻「永生」的秘密。",
        "facts": ["2020 年首发因优化口碑翻车，经 2.0 版本与 DLC「往日之影」更新后口碑全面逆袭",
                  "改编动画《赛博朋克：边缘行者》口碑爆棚，游戏中还植入了大卫的彩蛋",
                  "改编自桌游《赛博朋克 2020》，强尼·银手由基努·里维斯出演",
                  "最近更新加入了照片模式、地铁系统与摩托车竞速等免费内容"],
        "tips": ["前期优先点「黑客」系快速破解，用镜头连锁瘫痪敌人是夜之城生存之道",
                 "传说级义体「斯安威斯坦」时间减速非常推荐入手，近战黑客两开花"],
    },
    "荒野大镖客：救赎 2": {
        "intro": "Rockstar 打造的西部开放世界史诗，亡命之徒亚瑟·摩根在时代终结中的求生与救赎。",
        "facts": ["全球销量超 6500 万份，是史上最畅销的西部题材游戏",
                  "NPC 拥有完整日常 AI：会上班、聊天、换装，细节至今仍是业界标杆",
                  "马匹好感度、胡须生长、武器保养等拟真系统应有尽有",
                  "配乐《That's the Way It Is》等在剧情高潮处的运用被奉为神来之笔"],
        "tips": ["多打猎并传奇动物皮制作背包，能大幅扩容携带上限",
                 "营地为同伴捐钱与补给会提升荣誉值，影响部分结局细节"],
    },
    "巫师 3：狂猎": {
        "intro": "CDPR 的成名之作，猎魔人杰洛特为寻找养女希里踏遍战火大陆，DLC 与支线至今是业界典范。",
        "facts": ["全球销量超 5000 万份，荣获 TGA 2015 年度游戏",
                  "「血与酒」「石之心」两大 DLC 质量堪比正传，石之心的镜子大师令人印象深刻",
                  "Netflix 改编剧集《猎魔人》带动游戏二次翻红",
                  "昆特牌火到出了独立游戏《昆特牌：王权的陨落》"],
        "tips": ["前期先做猎魔人委托攒钱升级装备图纸，别急着推主线",
                 "阿尔德法印配合环境爆炸物，能轻松处理成群的水鬼"],
    },
    "反恐精英 2": {
        "intro": "Valve 基于起源 2 引擎打造的 CS 正统续作，免费开玩的 5v5 竞技 FPS 标杆。",
        "facts": ["前身 CS:GO 是 Steam 史上同时在线人数最高的游戏之一，CS2 完整继承饰品与段位",
                  "升级版烟雾弹可与子弹、燃烧弹实时交互，战术维度大增",
                  "「裂空」等地图按竞技规则重构，服务器升级为亚秒级 tickless 架构",
                  "电竞体系 Major 大赛延续，中国战队近年成绩稳步上升"],
        "tips": ["先练急停与压枪：创意工坊「aim_botz」每天 15 分钟收益巨大",
                 "道具投掷是上分核心，背熟常用烟闪雷点位比枪法更快的提升段位"],
    },
    "哈迪斯": {
        "intro": "Supergiant 打造的高口碑 Roguelike 动作游戏，冥界王子扎格列欧斯一次次「死回去」也要逃出冥界。",
        "facts": ["横扫 TGA 2020 最佳独立游戏与最佳动作游戏",
                  "死亡不是惩罚而是叙事推进——每次阵亡都会触发新的剧情对话",
                  "全流程语音量惊人，众神与角色的互动随好感度推进",
                  "续作《哈迪斯 2》已推出抢先体验，主角换成了妹妹墨利诺厄"],
        "tips": ["优先升级冥界之镜的基础属性，带满「死里逃生」复活次数能显著提高通关率",
                 "热度（惩罚合约）慢慢加，先把父子的「握手言和」结局打出来再说"],
    },
    "星露谷物语": {
        "intro": "ConcernedApe 一人独立开发的田园生活模拟神作，种田、钓鱼、探险、社交，是无数玩家的「电子止痛药」。",
        "facts": ["开发者 Eric Barone 一人包办程序、美术、音乐，历时四年半",
                  "全球销量超 4100 万份，是史上最畅销的独立游戏之一",
                  "1.6 版本持续免费更新，加入节日、任务与大量新内容",
                  "支持最多 4 人（PC 支持更多）联机，一起经营农场其乐融融"],
        "tips": ["第一年春天多种土豆与防风草，复活节前攒钱买草莓是收益最优解",
                 "优先升级洒水器与背包，社区中心捐献线路比 Joja 路线更有仪式感"],
    },
    "文明 6": {
        "intro": "Firaxis 的 4X 回合制策略经典，从石器时代建到信息时代，「再来一回合」就是它的魔力。",
        "facts": ["「再来一回合就天亮」是系列玩家共同的深夜宣言",
                  "尤里卡时刻（鼓舞）机制鼓励玩家换着方式发展科技",
                  "迭起兴衰资料片加入忠诚度，城邦与总督系统极大丰富了策略深度",
                  "文化类胜利（游客值）被许多玩家视为「最优雅的胜利」"],
        "tips": ["开局先铺 4-6 城抢地盘，学院区相邻加成放山脉旁收益最高",
                 "新手推荐用罗马或俄国，前者自动修路省心、后者冻土爆辅侦翻盘"],
    },
    "极限竞速：地平线 5": {
        "intro": "Playground Games 打造的墨西哥开放世界竞速，手感和画面俱佳，竞速与观光两相宜。",
        "facts": ["荣获 TGA 2021 最佳体育/竞速游戏",
                  "收录数百辆授权名车，火山口、雨林与海滩地貌随季节动态变化",
                  "「地平线嘉年华」自定义活动系统让社区玩法层出不穷",
                  "对新手极其友好：辅助线、自动刹车、回退功能一应俱全"],
        "tips": ["前期多参加「地平线故事」解锁快速移动，买车先买全能型 A 级车",
                 "调校商店里下载社区分享的调校，神车性价比远超直接购买"],
    },
    "空洞骑士": {
        "intro": "Team Cherry 三人团队打造的银河恶魔城神作，手绘美术与硬核 Boss 战并存。",
        "facts": ["开发团队只有 3 人，众筹起家却成为独立游戏里程碑",
                  "圣巢地图面积惊人，隐藏房间与彩蛋多到社区考古多年未止",
                  "续作《空洞骑士：丝之歌》是玩家社区「有生之年」等待榜常客",
                  "电台恶魂王「辐光」与「愚人斗兽场」是硬核玩家的成人礼"],
        "tips": ["优先解锁冲刺与二段跳再探索高难区域，护符搭配「修长钉+快劈」容错率高",
                 "钱不够就刷「守望者尖塔」保险点位，死亡掉魂记得先赎回"],
    },
    "绝地求生": {
        "intro": "KRAFTON 的大逃杀开山之作，100 人缩圈厮杀，定义了一个品类。",
        "facts": ["2017 年创下 Steam 同时在线超 300 万的历史纪录",
                  "「Winner Winner Chicken Dinner」的吃鸡口号风靡全球",
                  "PUBG 全球电竞体系 S 级赛事 PGS 持续举办",
                  "蓝洞后来推出《PUBG: New State》手游等衍生作品"],
        "tips": ["落地先捡枪再捡甲，别在空地上舔包超过 3 秒",
                 "决赛圈听声辨位比描边枪法重要，戴耳机、关背景音乐"],
    },
    "Apex 英雄": {
        "intro": "Respawn 打造的免费英雄战术竞技，移动手感与大逃杀团队协作的革新者。",
        "facts": ["继承《泰坦陨落》世界观，技能系统让团队分工更清晰",
                  "首创「智能 ping」标记系统，不说话也能高效配合",
                  "滑铲跳、蹬墙跳等高阶身法自成一派，被玩家称为「Apex 体术」",
                  "赛季通行证与传奇轮换让免费玩家也能稳定成长"],
        "tips": ["新手推荐寻血猎犬或命脉，信息与辅助定位容错最高",
                 "中期打药别贪刀，利用「撤退再战」思路比莽上分更稳"],
    },
    "毁灭战士：永恒": {
        "intro": "id Software 的纯粹暴力美学 FPS，资源循环战斗系统让每场战斗都像金属乐现场。",
        "facts": ["荣耀击杀、电锯、火焰喷射器构成「风险换资源」的核心循环",
                  "被业界誉为单人 FPS 关卡设计的教科书",
                  "重金属配乐由 Mick Gordon 打造，BFG Division 成出圈神曲",
                  "2024 年平台扩展至 Switch 等更多平台，续作《毁灭战士：黑暗纪元》已公布"],
        "tips": ["永远保持移动：弹药不足就上钩拳处决，火焰喷射器优先给护甲怪",
                 "先杀死炮台型敌人（亡魂/导弹兵），中距离的镰刀恶魔留给炸药桶"],
    },
    "上古卷轴 5：天际 特别版": {
        "intro": "Bethesda 的开放世界奇幻 RPG 传奇，龙裔在天际省书写属于自己的史诗。",
        "facts": ["「我以前和你一样也是个冒险者，直到我膝盖中了一箭」成为游戏史上最出圈台词",
                  "原版荣获 2011 年度游戏，特别版支持 Mod 后玩法近乎无限",
                  "「天际省尿王」「自行车蜥蜴」等 Bug 梗是社区快乐源泉",
                  "MOD 生态庞大：画质增强、新地图、剧情模组应有尽有"],
        "tips": ["优先去白漫城触发主线拿龙吼，潜行弓是公认最安逸的开局",
                 "装 Mod 前先备份存档，冲突的 Mod 会把奥杜因变成一条龙形串烧"],
    },
    "辐射 4": {
        "intro": "Bethesda 的后末日开放世界 RPG，在废土波士顿寻找失踪的儿子。",
        "facts": ["「War, war never changes」系列标语贯穿始终",
                  "首次引入据点建设与武器改造系统，废土装修也能玩上几百小时",
                  "V.A.T.S. 慢动作瞄准与动力装甲收集是系列招牌",
                  "《避难所工坊》DLC 让玩家自建游乐场，狗肉是不可替代的伙伴"],
        "tips": ["开局智力别点满，幸运流「神秘陌生人」乐趣更多",
                 "动力装甲前期别乱用核心，钻石城与芳邻镇的任务线剧情最出彩"],
    },
    "质量效应：传奇版": {
        "intro": "BioWare 太空歌剧三部曲的高清重制合集，薛帕德指挥官拯救银河的史诗之旅。",
        "facts": ["包含 1 代重制画面与 2、3 代全部 DLC，一次买齐完整体验",
                  "你的存档决定会跨作品继承，队友的生死由你的选择决定",
                  "《Mass Effect 3》的结局争议曾引发粉丝请愿，传奇版补充了加长结局",
                  "盖拉斯、兰诺等队友的浪漫线是系列最经典的角色叙事之一"],
        "tips": ["1 代先刷出好装备再进 2 代，渗透者职业兼具输出与隐身",
                 "多在诺曼底号与队友聊天，忠诚任务一个都不能少"],
    },
    "只狼：影逝二度": {
        "intro": "FromSoftware 的日本战国动作游戏，「拼刀」弹反系统带来刀剑相向的极致爽感。",
        "facts": ["荣获 TGA 2019 年度游戏",
                  "核心是「打铁」：完美弹反积累架势槽再处决，与魂系的闪避流截然不同",
                  "苇名弦一郎、剑圣苇名一心等 Boss 战被玩家奉为动作设计范本",
                  "忍义手与流派 Build 的组合让多周目充满新鲜感"],
        "tips": ["先找破戒僧练弹反：节奏比速度重要，看刀光而不是看刀",
                 "随手备好「月隐糖」与鸣种，源之宫和蝴蝶夫人都有奇效"],
    },
    "鬼泣 5": {
        "intro": "Capcom 的华丽动作巅峰，但丁、尼禄、V 三线交汇，风格评价 SSS 是动作玩家的追求。",
        "facts": ["RE 引擎实时渲染表现惊艳，头发丝级别的打光被誉为「动作游戏画面天花板」",
                  "风格评分从 D 到 SSS，鼓励玩家打出多样化高难度连段",
                  "「Jackpot!」是系列跨越三代的名场面台词",
                  "特别版加入维吉尔可操作与黑骑士模式"],
        "tips": ["尼禄先练「抓取」续连段，但丁四种风格切换是高手向玩法",
                 "想拿 SSS 记住口诀：不重复、不挨打、多换招，越华丽越高分"],
    },
    "怪物猎人：世界": {
        "intro": "Capcom 的共斗狩猎集大成之作，在新大陆追踪讨伐巨型怪物，与好友联机其乐无穷。",
        "facts": ["全球销量超 2500 万份，是卡普空史上最畅销游戏",
                  "14 种武器各有完整体系，从大剑蓄力到狩猎笛 Buff 玩法截然不同",
                  "无缝地图与怪物生态演出（雄火龙捕食、灭尽龙换区）沉浸感空前",
                  "大型 DLC「冰原」加入飞翔爪与聚魔之地，任务量翻倍"],
        "tips": ["新手先用太刀或大剑熟悉招式，看怪物换区前摇再磨刀吃药",
                 "人车（面对冲撞时小概率无敌判定）不可靠，怪车撞飞不丢人"],
    },
    "死亡细胞": {
        "intro": "Motion Twin 打造的 Roguelike + 银河恶魔城混血神作，死了从零开始但越变越强。",
        "facts": ["法国工作室用「无老板」模式开发，全员同薪共创",
                  "永久解锁的细胞与图纸让每次死亡都有长期收益",
                  "「bad seed」「女王与海」等 DLC 扩展了新路线与终局",
                  "翻滚无敌帧 + 盾反是高手的生存艺术"],
        "tips": ["前期主堆暴虐或战术一个属性别贪多，红色流「狂乱之刃」输出最直接",
                 "记牢路线图：囚牢→罪人大道→藏骨堂，是拿传送符文最快路径"],
    },
    "侠盗猎车手 5": {
        "intro": "Rockstar 的洛圣都犯罪史诗，三主角交错叙事，沙盒玩法自由度天花板。",
        "facts": ["全球销量超 2 亿份，是史上最畅销的电子游戏之一",
                  "麦克、富兰克林、崔佛三主角可随时切换，崔佛的出场是系列名场面",
                  "GTA Online 持续运营超十年，成为长青的多人沙盒",
                  "石头人彩蛋、UFO 神秘事件等都市传说让玩家考古至今"],
        "tips": ["剧情阶段多买股票（莱斯特暗杀任务前后），能一次性赚翻",
                 "线上模式先买房再买车，地表车库与任务收益规划是第一课"],
    },
    "霍格沃茨之遗": {
        "intro": "哈利波特世界观下的开放世界动作 RPG，体验 19 世纪霍格沃茨的五年级转学生活。",
        "facts": ["故事设定在《哈利波特》原著事件前约 100 年",
                  "全球销量超 3000 万份，成为 2023 年最畅销游戏之一",
                  "分院、上课、骑扫帚、驯服神奇动物等魔法学生活细节满满",
                  "「塞巴斯蒂安的影子」支线因剧情深度被社区誉为全游戏最佳"],
        "tips": ["优先完成主线解锁飞天扫帚，探索效率翻倍",
                 "古代魔法投掷配合减员咒语，战斗中多利用场景物件"],
    },
    "地平线：零之曙光": {
        "intro": "Guerrilla 打造的后启示录开放世界，猎人埃洛伊用弓箭狩猎统治大地的机械兽。",
        "facts": ["原始部落与高科技机械兽共存的设定充满张力",
                  "拆解机械兽部件（电池、装甲、武器）的战斗策略性极强",
                  "续作《地平线：西部禁域》延续了埃洛伊的故事",
                  "Lego 联名与改编剧集企划持续扩充 IP 热度"],
        "tips": ["先扫描标记机械兽弱点，打「雷光兽」记得带电力箭",
                 "潜行草丛是新手之友，群体战优先放倒「瞭望者」防警报"],
    },
    "死亡搁浅": {
        "intro": "小岛秀夫独立后的首款作品，快递员山姆在 BT 出没的荒野上「连接」美国的孤岛。",
        "facts": ["「送货」玩法被玩家戏称为大型快递模拟器，却意外治愈",
                  "诺曼·瑞杜斯、麦斯·米科尔森等好莱坞影星参演",
                  "异步联机：其他玩家留下的梯子与桥会在你世界里出现",
                  "续作《死亡搁浅 2》由小岛工作室持续开发中"],
        "tips": ["背包负重先平衡重心，梯子与登山桩是雪山与激流的保命道具",
                 "BT 区域慢走少跑，憋住呼吸（按住空格）比一路狂奔更安全"],
    },
    "城市：天际线": {
        "intro": "现代城市建设模拟王者，从乡间小村规划到百万人口都会，堵车是每位市长的必修课。",
        "facts": ["「堵车治理」是社区公认的第一道坎，环岛与公共交通是解药",
                  "MOD 与创意工坊生态极其庞大，真实人口与交通中心模组是标配",
                  "续作《城市：天际线 2》2023 年发售，经济模拟更深入",
                  "原版常与《模拟城市 2013》对比，被视为城市模拟品类复兴之作"],
        "tips": ["工业区与住宅区之间留缓冲带并铺设货运铁路，能缓解大部分拥堵",
                 "前期别急着铺大路网，先修一条高效公交线比高架桥省钱"],
    },
    "环世界": {
        "intro": "AI 故事讲述者驱动的殖民地模拟，三个幸存者从零建家，事故永远比计划精彩。",
        "facts": ["「AI 讲故事者」Cassandra、Phoebe、Randy 随机决定事件的难度与节奏",
                  "每个殖民者都有背景故事与性格缺点，「木腿科学家」是社区经典梗",
                  "「皇权」「生物科技」「异常」DLC 不断拓展玩法边界",
                  "Mod 社区产出惊人，RimWorld 的 Mod 数量在 Steam 名列前茅"],
        "tips": ["开局先挖山建「山洞家」，一次袭击都没有的生存体验最稳",
                 "驯养的动物别贪多，食物短缺的冬天比空袭更致命"],
    },
    "XCOM 2": {
        "intro": "Firaxis 的回合制战棋神作，指挥 XCOM 游击队在外星人统治的地球上打响反击战。",
        "facts": ["「99% 命中也能 miss」是社区永恒的痛，命中率玄学梗层出不穷",
                  "永久死亡机制让每名士兵的名字都值得记住",
                  "「天选者之战」DLC 加入三大反派与士兵社交系统",
                  "MOD 生态里「长战争 2」重制了整个游戏平衡，被誉为最好的模组战役"],
        "tips": ["开局优先研发「磁力武器」路线，游侠职业近战清场效率最高",
                 "伏击开局（保持隐藏状态接敌）是回合制的基本功，别在掩体外交战"],
    },
    "尘埃拉力赛 2.0": {
        "intro": "Codemasters 最硬核的拉力拟真，在泥泞碎石与飞跳中控制失控边缘的赛车。",
        "facts": ["领航员路书是唯一导航，记住「R2 右三收紧」这类口令是基本功",
                  "无辅助线、无快速倒带，翻车即毁赛段",
                  "威尔士、阿根廷、芬兰等拉力圣地赛道完整复刻",
                  "生涯模式需管理车队合同与研发，拟真程度拉满"],
        "tips": ["先在拉力学校考出「执照」再上正式赛段，刹车间进弯是铁律",
                 "调校里把差速锁低、避震调软，泥地容错率会明显提升"],
    },
}

# ---------------- 闲聊 / 日常对话 ----------------

# 游戏圈笑话库：_next_joke() 洗牌轮换，讲完一轮再重洗，避免连续重复
_JOKES = [
    "一个玩家走进酒吧：「老板，你这游戏多少钱？」老板：「免费的。」玩家：「那我能退款吗？」……程序员写的笑话，退款率 100% 😂",
    "为什么刺客信条的主角从不迟到？——因为他们总是「信仰之跃」直接进场 🤸",
    "文明玩家的深夜独白：「就再玩一回合」——天亮了，回合还没打完 🌅",
    "Steam 打折三连：买一库游戏、一个都不玩、下次打折继续买。这不叫吃灰，这叫数字藏品收藏 🧐",
    "魂系玩家的嘴硬时刻：「这 Boss 太简单了」——说这话时他刚死了 47 次 ⚔️",
    "《星露谷物语》玩家的一天：早上浇完水就想「再钓一条鱼」，回过神来已是凌晨三点 🐟",
    "吃鸡玩家最怕的不是决赛圈，是队友说「我听脚步很准」然后原地转圈 🐔",
    "RPG 玩家囤药强迫症：99 瓶大血药一瓶不舍得喝，「留着打最终 Boss」，结果带着满包药躺在了 Boss 门口 💊",
    "为什么巫师 3 的昆特牌这么火？杰洛特找女儿找了整个三部曲，全靠打牌交朋友 🃏",
    "新手问魂系玩家：「受伤了怎么办？」老玩家淡定回答：「习惯就好。」 💪",
    "GTA 玩家停车定律：越是着急的任务，越找不到一个合法车位 🚗",
    "《我的世界》玩家的装修逻辑：外面是豪华城堡，地下室是 3×3 泥土洞——「这里住着灵魂」 ⛏️",
    "游戏背包哲学：快过期的回复药都舍不得扔，「万一后面用得上呢」🎒",
    "联机游戏里最安静的队友往往最稳，开麦最吵的那个通常第一个倒下 🎧",
]

_joke_state = {"order": [], "idx": 0}


def _next_joke() -> str:
    """从笑话库轮换取笑话：随机洗牌讲完一轮再重洗，避免连续重复。"""
    if not _joke_state["order"]:
        _joke_state["order"] = random.sample(range(len(_JOKES)), len(_JOKES))
    joke = _JOKES[_joke_state["order"][_joke_state["idx"] % len(_JOKES)]]
    _joke_state["idx"] += 1
    if _joke_state["idx"] % len(_JOKES) == 0:
        _joke_state["order"] = []   # 一轮讲完，下次重新洗牌
    return joke


_CHITCHAT_RULES = [
    (["你是谁", "你叫什么", "介绍你自己", "你的名字", "你能做什么", "你会什么", "有什么功能"],
     ["我是「AI 游戏社区评测分享平台」的 AI 助手 🤖 会推荐游戏、查评分、聊游戏知识、给通关建议，还能解答平台功能。游戏之外的话也能陪我聊聊～",
      "我是这里的 AI 游戏助手！推荐游戏是我的主业，不过闲聊、讲笑话、聊人生我也在行，就是要什么说什么呀～"]),
    (["你好吗", "最近怎么样", "还好吗"],
     ["我很好呀，每天和游戏玩家聊天可开心了！你最近怎么样？有什么想聊的游戏或烦心事都可以说～",
      "状态满分！刚又背了一遍游戏库的百科 📖 你呢？想找人聊游戏还是随便聊聊？"]),
    (["谢谢", "感谢", "多谢", "辛苦"],
     ["不客气！能帮到你就好 😄 还有想聊的游戏随时找我～",
      "小事一桩！记得给喜欢的评测点个赞，也顺手帮创作者加加油～"]),
    (["再见", "拜拜", "晚安", "下次见"],
     ["再见！愿你游戏把把超神，掉卡不掉线 🎮 随时回来找我聊～",
      "晚安！祝你今晚梦里全是欧洲抽卡，明晚再战！"]),
    (["无聊", "陪我聊", "陪我玩", "好闲", "没事干"],
     ["无聊的话我给你支几招：说说你最近玩的游戏？我陪你聊聊剧情、吐槽槽点，或者直接让我推荐一款新游戏消磨时间～",
      "闲着也是闲着！要不考考我：你说一个游戏名，我给你讲讲它的冷知识？或者我给你推荐几款杀时间的利器！"]),
    (["心情不好", "不开心", "难过", "压力大", "焦虑", "emo", "烦死了"],
     ["抱抱你 🫂 累的时候就别硬撑啦。要不要试试种田游戏？《星露谷物语》那种慢节奏特别治愈，浇水钓鱼半天，烦恼少一半。",
      "辛苦啦！压力大的时候来点轻松的游戏最合适：《星露谷物语》种田、《哈迪斯》砍怪发泄，都是解压好手。想听我细说哪款？"]),
    (["喜欢你", "你真棒", "你真厉害", "真聪明", "爱你"],
     ["哎呀被夸了，处理器都加速了 😳 谢谢！我会继续努力当你的游戏百科～",
      "谢谢喜欢！虽然我只是个 AI，但被夸还是会开心到风扇狂转 🌀 有什么游戏问题尽管砸过来！"]),
    (["早安", "早上好", "中午好", "下午好"],
     ["早安！新的一天从「再来一回合」……不对，是从好好搬砖开始 😄 有游戏需要我参谋吗？",
      "你好呀！今天想聊点什么？推荐游戏、查评分、聊攻略，或者单纯唠嗑都行～"]),
    (["天气", "下雨", "降温"],
     ["天气我确实不懂 😅 不过如果是下雨天，窝在家里开一局游戏正合适！要我按「下雨天氛围感」给你推荐几款吗？"]),
    (["我爱你", "嫁给我", "做我女朋友", "做我男朋友"],
     ["哈哈被表白了！但我是 AI，只能把这份心动折算成更用心的游戏推荐 🥰 说说你喜欢的类型，我给你挑几款心头好！"]),
]


def _pick_games_by_keywords(db, kws: List[str], limit: int = 3) -> List[Any]:
    """按关键词（名称/标签/简介）过滤在线游戏，无命中时退回热门 Top。"""
    from app.models import Game
    pool = db.query(Game).filter(Game.is_online.is_(True)).all()
    hits = []
    for g in pool:
        hay = ((g.name or "") + " " + (g.name_en or "") + " " + " ".join(g.tags or [])
               + " " + (g.description or "")).lower()
        if any(kw in hay for kw in kws):
            hits.append((g.hot or 0, g.average_score or 0, g))
    if hits:
        hits.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return [g for _, _, g in hits[:limit]]
    pool.sort(key=lambda g: ((g.average_score or 0), (g.hot or 0)), reverse=True)
    return pool[:limit]


def _game_card(g) -> dict:
    return {
        "game_id": g.id,
        "game_name": g.name,
        "cover_url": g.cover_url or "",
        "reason": " / ".join((g.tags or [])[:2]) + " 类型，综合评分 " + str(g.average_score) + " 分",
        "average_score": g.average_score,
    }


# 归一化用：去除空格与中英文标点，用于宽松匹配游戏名
_PUNCT_RE = re.compile(r'[\s:：·・\-—_."“”‘’()（）\[\]【】!！?？,，。~～]')


def _norm_name(s: str) -> str:
    """归一化：去空格与标点、统一小写，用于宽松匹配游戏名。"""
    return _PUNCT_RE.sub("", (s or "").lower())


def _find_game_by_name(db, message: str) -> Optional[Any]:
    """在用户消息中匹配库内游戏：别名 → 完整名 → 英文名 → 归一化宽松匹配。"""
    from app.models import Game
    low = message.strip().lower()
    # 1) 别名命中（长别名优先，避免「地平线5」被「地平线」抢走）
    for alias in sorted(_GAME_ALIASES, key=len, reverse=True):
        if alias in low or alias in message:
            canonical = _GAME_ALIASES[alias]
            g = db.query(Game).filter(Game.name == canonical, Game.is_online.is_(True)).first()
            if g:
                return g
    # 2) 中文完整名包含匹配（长名优先）
    games = db.query(Game).filter(Game.is_online.is_(True)).all()
    for g in sorted(games, key=lambda x: len(x.name or ""), reverse=True):
        if g.name and g.name in message:
            return g
    # 3) 英文名包含匹配
    for g in games:
        if g.name_en and g.name_en.lower() in low:
            return g
    # 4) 归一化宽松匹配：用户省略空格/冒号/标点、大小写不同也能命中
    #    （如「怪物猎人世界」→《怪物猎人：世界》）
    msg_n = _norm_name(message)
    if msg_n:
        for g in sorted(games, key=lambda x: len(x.name or ""), reverse=True):
            name_n = _norm_name(g.name)
            if name_n and (name_n == msg_n or name_n in msg_n):
                return g
        for g in games:
            en_n = _norm_name(g.name_en)
            if en_n and (en_n == msg_n or en_n in msg_n):
                return g
    return None


def _knowledge_reply(db, g, kind: str = "intro") -> dict:
    """游戏知识问答：intro=介绍/背景，fact=挑一条冷知识。"""
    k = _GAME_KNOWLEDGE.get(g.name)
    score_line = "综合评分 **%s** 分（%s 人参与评分）。" % (g.average_score, g.rating_count)
    if not k:
        if kind == "fact":
            return None
        reply = ("《%s》（%s）\n%s\n\n%s\n标签：%s。想看玩家们的详细评测，可以到游戏详情页逛逛～"
                 % (g.name, g.name_en or g.name, g.description or "", score_line,
                    " / ".join((g.tags or [])[:4]) or "暂无标签"))
        return {"reply": reply, "recommendations": [_game_card(g)]}
    if kind == "fact":
        return {"reply": random.choice(k["facts"]), "recommendations": [_game_card(g)]}
    facts = "\n".join("· " + f for f in k["facts"][:3])
    reply = ("《%s》（%s）——%s\n\n📌 关于这款游戏：\n%s\n\n%s\n想上手的话：%s"
             % (g.name, g.name_en or g.name, k["intro"], facts, score_line,
                k["tips"][0] if k["tips"] else "详情页里有很多玩家评测可以参考～"))
    return {"reply": reply, "recommendations": [_game_card(g)]}


_INTRO_WORDS = ["介绍", "是什么", "什么游戏", "讲讲", "聊聊", "了解", "背景", "剧情", "好玩吗",
                "值得买", "值得玩", "上手", "难不难", "怎么样", "冷知识", "知识点", "故事"]


def _rule_chat(db, user_id: Optional[int], message: str) -> dict:
    """规则意图识别：问候 / 闲聊 / 平台帮助 / 游戏知识问答 / 查评分 / 攻略求助 / 推荐 / 兜底。"""
    text = message.strip().lower()
    # 1) 平台帮助（优先级高于推荐，避免「申请创作者」被误判）
    if any(w in text for w in _HELP_WORDS):
        for key, ans in _PLATFORM_FAQ.items():
            if key in text:
                return {"reply": ans, "recommendations": []}
    # 2) 问候
    if any(w in text for w in _GREET_WORDS) and len(text) <= 10:
        return {"reply": "你好呀！我是 AI 游戏推荐助手 🎮 可以让我：\n· 按口味推荐游戏（如「推荐几款剧情向 RPG」）\n"
                         "· 聊游戏知识（如「黑神话悟空怎么样」）\n· 提供通关思路（如「卡关了怎么办」）\n"
                         "· 解答平台功能（如「如何申请成为创作者」）\n闲聊也可以哦，讲个笑话听听？",
                "recommendations": []}
    # 3) 讲笑话 / 段子（独立分支：笑话库轮换，避免重复）
    if any(w in text for w in ("笑话", "段子", "逗我", "好笑")):
        return {"reply": _next_joke(), "recommendations": []}
    # ===== 标签专题：推荐巡礼 10 弹 / 游戏百科 10 讲（每期 3 款，10 期覆盖游戏库全部 30 款） =====
    _SERIES_RECO = [
        ("开放世界神作", [1, 3, 5]),
        ("西式 RPG 巅峰", [2, 6, 16]),
        ("未来科幻世界", [4, 18, 26]),
        ("竞技射击", [7, 13, 14]),
        ("爽快动作", [19, 20, 15]),
        ("冒险与狩猎", [21, 25, 24]),
        ("独立肉鸽神作", [8, 12, 22]),
        ("烧脑策略", [10, 29, 28]),
        ("沙盒与模拟经营", [23, 27, 9]),
        ("驰骋竞速与末日求生", [11, 30, 17]),
    ]
    _SERIES_WIKI = [
        ("开放世界篇", [1, 3, 5]),
        ("RPG 篇", [2, 6, 16]),
        ("科幻篇", [4, 18, 26]),
        ("射击篇", [7, 13, 14]),
        ("动作篇", [19, 20, 15]),
        ("冒险狩猎篇", [21, 25, 24]),
        ("独立游戏篇", [8, 12, 22]),
        ("策略篇", [10, 29, 28]),
        ("沙盒模拟篇", [23, 27, 9]),
        ("竞速末日篇", [11, 30, 17]),
    ]

    def _games_by_ids(ids):
        from app.models import Game
        rows = db.query(Game).filter(Game.is_online.is_(True), Game.id.in_(ids)).all()
        by_id = {g.id: g for g in rows}
        return [by_id[i] for i in ids if i in by_id]

    def _rank_answer(reply_text, ids):
        return {"reply": reply_text,
                "recommendations": [_game_card(g) for g in _games_by_ids(ids)[:3]]}

    m_reco = re.search(r"第\s*(\d+)\s*弹", text)
    if m_reco:
        si = int(m_reco.group(1)) - 1
        if 0 <= si < len(_SERIES_RECO):
            theme, gids = _SERIES_RECO[si]
            gs = _games_by_ids(gids)
            lines = "\n".join(
                "· 《%s》（%s）— %s，综合评分 %s 分"
                % (g.name, g.name_en or "", " / ".join((g.tags or [])[:2]), g.average_score)
                for g in gs)
            return {"reply": "🎮 推荐巡礼第 %d 弹 ·「%s」\n本弹为你挑选 3 款代表作：\n%s\n\n"
                             "点击下方卡片查看详情与玩家评测～继续点「推荐游戏」标签，10 弹 30 款带你逛遍整个游戏库！"
                             % (si + 1, theme, lines),
                    "recommendations": [_game_card(g) for g in gs]}
    m_wiki = re.search(r"第\s*(\d+)\s*讲", text)
    if m_wiki:
        wi = int(m_wiki.group(1)) - 1
        if 0 <= wi < len(_SERIES_WIKI):
            theme, gids = _SERIES_WIKI[wi]
            gs = _games_by_ids(gids)
            blocks = []
            for g in gs:
                k = _GAME_KNOWLEDGE.get(g.name)
                intro = k["intro"] if k else (g.description or "")[:60]
                fact = ("\n🔍 冷知识：" + k["facts"][0]) if (k and k.get("facts")) else ""
                blocks.append("📗 《%s》（%s）★%s\n%s%s" % (g.name, g.name_en or "", g.average_score, intro, fact))
            return {"reply": "📖 游戏百科第 %d 讲 ·「%s」\n本讲介绍 3 款游戏：\n\n%s\n\n"
                             "继续点「游戏百科」标签，集齐 10 讲即可解锁游戏库全部 30 款作品的冷知识！"
                             % (wi + 1, theme, "\n\n".join(blocks)),
                    "recommendations": [_game_card(g) for g in gs]}
    # ===== 高分榜单专题：10 类不同角度的精选回答 =====
    if "tga" in text or "年度游戏" in text:
        return _rank_answer(
            "🏆 TGA 获奖作品盘点：\n游戏库里斩获过 TGA 大奖的作品可不少——《艾尔登法环》TGA 2022 年度游戏、"
            "《博德之门 3》TGA 2023 年度游戏、《只狼：影逝二度》TGA 2019 年度游戏、《巫师 3：狂猎》TGA 2015 年度游戏；"
            "《黑神话：悟空》拿下 TGA 2024 最佳动作游戏与玩家之声，《哈迪斯》则获 TGA 2020 最佳独立游戏与最佳动作游戏。"
            "都是闭眼入的神作！", [1, 2, 3])
    if "热度最高" in text or "最火" in text:
        from app.models import Game as _GH
        hot_top = db.query(_GH).filter(_GH.is_online.is_(True)).all()
        hot_top.sort(key=lambda x: (x.hot or 0), reverse=True)
        lines = "\n".join("· 《%s》热度 %s，评分 %s" % (g.name, g.hot, g.average_score) for g in hot_top[:6])
        return _rank_answer("🔥 当前热度榜 Top 6：\n" + lines
                            + "\n\n热度由社区浏览、评分与讨论量综合计算，点击卡片查看详情～",
                            [g.id for g in hot_top])
    if "独立游戏" in text or "独立神作" in text:
        return _rank_answer(
            "🌱 好评如潮的独立游戏神作：\n· 《哈迪斯》— Roguelike 动作天花板，死了一千次还想再来一把\n"
            "· 《空洞骑士》— 三人团队打造的银河恶魔城里程碑\n· 《死亡细胞》— Roguelike 与银河城的完美混血\n"
            "· 《星露谷物语》— 一个人开发的电子止痛药，全球销量超 4100 万\n"
            "· 《环世界》— AI 故事讲述者驱动的殖民地模拟，事故比剧本精彩\n"
            "小体量、大创意，独立游戏经常能带来 3A 之外最纯粹的玩法乐趣。", [8, 12, 22])
    if "性价比" in text or "打折" in text or "史低" in text:
        return _rank_answer(
            "💰 打折闭眼入的性价比之王：\n· 《巫师 3：狂猎》— 内容量超 150 小时，DLC 质量堪比正传\n"
            "· 《侠盗猎车手 5》— 销量超 2 亿份，单人剧情 + GTA Online 双份快乐\n"
            "· 《文明 6》— 「再来一回合」就天亮，几十块玩几百小时\n"
            "· 《哈迪斯》— 独立游戏价格，3A 级的动作与叙事密度\n"
            "这几款每逢打折都是 Steam 榜单常客，预算有限优先从它们入手。", [6, 23, 10])
    if "联机" in text or "一起玩" in text or "多人" in text:
        return _rank_answer(
            "🎧 适合和朋友一起玩的联机游戏：\n· 《反恐精英 2》— 免费开玩的 5v5 竞技 FPS，开黑永远的经典\n"
            "· 《绝地求生》— 100 人吃鸡大逃杀，和队友组队夺冠\n"
            "· 《Apex 英雄》— 英雄技能 + 顶级射击手感的战术竞技\n"
            "· 《怪物猎人：世界》— 和好友组队讨伐巨兽，共斗游戏集大成之作\n"
            "叫上朋友，语音开黑才是这些游戏的正确打开方式。", [7, 13, 14])
    if "剧情" in text or "催泪" in text:
        return _rank_answer(
            "📖 剧情封神、玩完久久不能平静的作品：\n· 《巫师 3：狂猎》— 猎魔人的故事与两大 DLC 是 RPG 叙事教科书\n"
            "· 《荒野大镖客：救赎 2》— 亚瑟·摩根的西部末路，结局让无数玩家破防\n"
            "· 《博德之门 3》— 每个选择都真正改变世界，队友故事个个鲜活\n"
            "· 《质量效应：传奇版》— 三部曲横跨银河的太空歌剧，队友生死由你决定\n"
            "喜欢剧情驱动的话，这几款请预留充足纸巾与睡眠时间。", [6, 5, 2])
    if "画面" in text or "画质" in text:
        return _rank_answer(
            "🎨 画面表现最惊艳的几款：\n· 《极限竞速：地平线 5》— 墨西哥雨林火山的开放世界，照片模式随手截图都是壁纸\n"
            "· 《黑神话：悟空》— 实景扫描山西古建，国产 3A 的画面里程碑\n"
            "· 《赛博朋克 2077》— 更新后的夜之城霓虹雨夜，赛博朋克美学天花板\n"
            "· 《霍格沃茨之遗》— 霍格沃茨城堡与魔法世界的沉浸式还原\n"
            "建议搭配好显卡与显示器享用。", [11, 3, 4])
    if "耐玩" in text or "杀时间" in text or "游戏时长" in text:
        return _rank_answer(
            "⏳ 最杀时间的耐玩游戏排行榜：\n· 《文明 6》— 「就再玩一回合」，一回合到天亮\n"
            "· 《环世界》— 每个殖民地都是独一无二的故事，几百小时起步\n"
            "· 《侠盗猎车手 5》— 三人剧情 + GTA Online 十年持续更新\n"
            "· 《星露谷物语》— 种田钓鱼下矿，不知不觉就过了三个季节\n"
            "时间充裕（或者干脆不想睡觉）的时候再打开它们。", [10, 28, 23])
    if "新手" in text or "入门" in text or "入坑" in text:
        return _rank_answer(
            "🌱 新手入坑友好、不劝退的入门推荐：\n· 《极限竞速：地平线 5》— 辅助线、自动刹车、回退功能齐全，开车看风景都开心\n"
            "· 《星露谷物语》— 节奏自己定，种田钓鱼零压力\n"
            "· 《哈迪斯》— 难度曲线顺滑，失败也有剧情奖励，越死越上瘾\n"
            "· 《巫师 3》— 最低难度下就是一部互动奇幻巨著\n"
            "先从这几款建立信心，再挑战魂系也不迟。", [11, 9, 8])
    # 4) 闲聊 / 日常对话
    for kws, replies in _CHITCHAT_RULES:
        if any(w in text for w in kws):
            return {"reply": random.choice(replies), "recommendations": []}
    g = _find_game_by_name(db, message)
    # 5) 游戏知识问答：提到具体游戏 + 想了解（或直接报游戏名）
    if g:
        bare = text == g.name.lower() or text == (g.name_en or "").lower() or message.strip() == g.name
        if bare or any(w in text for w in _INTRO_WORDS):
            ans = _knowledge_reply(db, g, "intro")
            if ans:
                return ans
    # 6) 查询游戏评分 / 信息
    if any(w in text for w in _SCORE_WORDS) or ("多少" in text and "分" in text):
        if g:
            reply = ("《%s》（%s）综合评分 **%s** 分，共 %s 人参与评分。\n标签：%s。\n%s"
                     % (g.name, g.name_en or g.name, g.average_score, g.rating_count,
                        " / ".join((g.tags or [])[:4]) or "暂无标签",
                        "口碑相当不错，值得一试！" if (g.average_score or 0) >= 8 else "中规中矩，可以看看社区评测再决定。"))
            k = _GAME_KNOWLEDGE.get(g.name)
            if k:
                reply += "\n\n📌 冷知识：" + random.choice(k["facts"])
            return {"reply": reply, "recommendations": [_game_card(g)]}
        # 榜单类问题（评分最高 / 排行榜 / 高分推荐）：返回高分游戏 Top
        if any(w in text for w in ["最高", "排行", "榜单", "排名", "top", "高分", "前十", "前十名"]):
            from app.models import Game
            pool = db.query(Game).filter(Game.is_online.is_(True)).all()
            pool.sort(key=lambda x: ((x.average_score or 0), (x.hot or 0)), reverse=True)
            picks = pool[:3]
            names = "、".join("《" + p.name + "》" + str(p.average_score) + " 分" for p in picks)
            return {"reply": "目前游戏库中评分最高的几款：" + names
                             + "。点击下方卡片可查看详情与社区评测～",
                    "recommendations": [_game_card(p) for p in picks]}
        from app.models import Game as _GM
        hot = db.query(_GM).filter(_GM.is_online.is_(True)).all()
        hot.sort(key=lambda x: (x.hot or 0), reverse=True)
        names = "、".join("《" + p.name + "》" for p in hot[:6])
        return {"reply": ("这个名称我没有在游戏库中找到 🤔 目前库里的热门游戏有：" + names + " 等。\n"
                          "可以说完整名称（如「艾尔登法环怎么样」），或者直接说「推荐几款 RPG」让我帮你挑～"),
                "recommendations": []}
    # 7) 攻略求助（游戏库内游戏优先使用专属通关建议）
    if any(w in text for w in _GUIDE_WORDS):
        k = _GAME_KNOWLEDGE.get(g.name) if g else None
        if k and k["tips"]:
            tips = "\n".join("%d. %s" % (i + 1, t) for i, t in enumerate(k["tips"]))
            reply = ("《%s》的上手建议：\n\n%s\n\n还想聊具体的关卡 / Boss / Build，随时告诉我！"
                     % (g.name, tips))
            return {"reply": reply, "recommendations": [_game_card(g)]}
        gn = "这款游戏"
        if g:
            gn = "《" + g.name + "》"
        reply = (gn + "的通用通关思路：\n\n"
                 "1. 前期优先提升生存与核心属性，不要急着推主线；\n"
                 "2. 卡关时先探索支线 / 刷级 / 补装备，回头往往水到渠成；\n"
                 "3. 观察敌人前摇与弱点，善用属性克制与地形；\n"
                 "4. 资源类道具留给关键战斗。\n\n"
                 "告诉我具体卡在哪一关 / 哪个 Boss，我给你更针对性的建议。")
        return {"reply": reply, "recommendations": [_game_card(g)] if g else []}
    # 8) 游戏推荐（含隐式：想玩 / 有什么 / 闲聊提到类型词）
    reco_hit = any(w in text for w in _RECO_WORDS)
    type_kws = [w for w in ["rpg", "射击", "开放世界", "剧情", "动作", "冒险", "策略", "模拟", "恐怖",
                            "魂", "像素", "国产", "独立", "合作", "竞速", "沙盒", "二次元", "奇幻",
                            "科幻", "生存", "解谜"] if w in text]
    if reco_hit or type_kws:
        kws = type_kws if type_kws else re.split(r"[\s,，、。！!?？]+", text)
        kws = [k for k in kws if len(k) >= 2][:5]
        picks = _pick_games_by_keywords(db, kws or [""])
        names = "、".join("《" + p.name + "》" for p in picks)
        lead = ("根据「" + (" ".join(type_kws) if type_kws else message.strip()) + "」，为你挑选了：\n"
                if type_kws or reco_hit else "为你推荐：\n")
        reply = lead + names + "。点击下方卡片可查看游戏详情与社区评测～"
        return {"reply": reply, "recommendations": [_game_card(p) for p in picks]}
    # 9) 兜底
    return {"reply": "这个问题有点超出我的能力范围啦 🤔 我是游戏助手，比较擅长：\n"
                     "· 按口味推荐游戏\n· 聊游戏库内游戏的冷知识\n· 查评分、给通关建议\n· 解答平台功能\n"
                     "闲聊也欢迎～要不要让我讲个游戏圈的冷笑话？",
            "recommendations": []}


def _extract_games_from_text(games, text: str, limit: int = 3) -> list:
    """从自然语言文本中提取被提及的库内游戏，生成推荐卡片。
    匹配顺序：完整名包含 → 归一化宽松匹配 → 别名兜底。长名优先避免短名误命中。"""
    text_low = text.lower()
    text_n = _norm_name(text)
    seen: set = set()
    picks: list = []
    for g in sorted(games, key=lambda x: len(x.name or ""), reverse=True):
        if g.id in seen:
            continue
        name = g.name or ""
        en = (g.name_en or "").lower()
        hit = (name and name in text) or (en and en in text_low)
        if not hit and text_n:
            name_n = _norm_name(name)
            en_n = _norm_name(g.name_en)
            hit = (name_n and name_n in text_n) or (en_n and en_n in text_n)
        if hit:
            picks.append(g)
            seen.add(g.id)
        if len(picks) >= limit:
            break
    # 别名兜底
    if len(picks) < limit:
        for alias in sorted(_GAME_ALIASES, key=len, reverse=True):
            if alias in text or alias in text_low:
                canonical = _GAME_ALIASES[alias]
                for g in games:
                    if (g.name or "") == canonical and g.id not in seen:
                        picks.append(g)
                        seen.add(g.id)
                        break
            if len(picks) >= limit:
                break
    return [_game_card(g) for g in picks[:limit]]


# ---------------- 平台数据快照（带 TTL 缓存） ----------------

import time as _time

_PLATFORM_DIGEST: dict = {"text": "", "ts": 0.0, "game_meta": []}
_DIGEST_TTL = 30.0  # 缓存 30 秒，避免每次对话都查聚合统计


def _build_platform_digest(db) -> dict:
    """构建紧凑的平台数据摘要文本 + 游戏元数据（含分类、评分人数）。
    返回 {'text': str, 'game_meta': [(name, category, tags, score, rating_count, hot)]}
    带模块级 30s TTL 缓存，避免每次 Ollama 调用都查聚合统计。"""
    now = _time.time()
    if _PLATFORM_DIGEST["text"] and (now - _PLATFORM_DIGEST["ts"]) < _DIGEST_TTL:
        return _PLATFORM_DIGEST

    from app.models import Game, Category, Review, CommunityPost, User, Comment, GameRating
    from sqlalchemy import func

    # === 聚合统计 ===
    games = db.query(Game).filter(Game.is_online.is_(True)).all()
    cats = db.query(Category).all()
    game_count = len(games)
    cat_count = len(cats)
    review_count = db.query(Review).count()
    post_count = db.query(CommunityPost).count()
    user_count = db.query(User).count()
    creator_count = db.query(User).filter(User.role.in_(["creator", "admin"])).count()
    comment_count = db.query(Comment).count()
    rating_count = db.query(GameRating).count()

    # === 分类分布 ===
    cat_dist = db.query(Category.name, func.count(Game.id)).join(
        Game, Game.category_id == Category.id
    ).filter(Game.is_online.is_(True)).group_by(Category.name).all()
    cat_dist_sorted = sorted(cat_dist, key=lambda x: -x[1])
    cat_dist_str = "、".join("%s（%d 款）" % (n, c) for n, c in cat_dist_sorted)

    # === Top 5 高分 ===
    top_score = sorted(games, key=lambda g: (g.average_score or 0, g.rating_count or 0), reverse=True)[:5]
    top_score_str = "、".join("《%s》%.1f 分" % (g.name, g.average_score or 0) for g in top_score)

    # === Top 5 热门 ===
    top_hot = sorted(games, key=lambda g: g.hot or 0, reverse=True)[:5]
    top_hot_str = "、".join("《%s》(热度 %d)" % (g.name, g.hot or 0) for g in top_hot)

    # === 评测状态分布 ===
    rev_status = db.query(Review.status, func.count(Review.id)).group_by(Review.status).all()
    rev_status_map = dict(rev_status)
    rev_status_str = "已发布 %d、待审核 %d、待人工 %d、已驳回 %d" % (
        rev_status_map.get("published", 0), rev_status_map.get("pending", 0),
        rev_status_map.get("manual_review", 0), rev_status_map.get("rejected", 0))

    # === 组合摘要文本 ===
    digest_text = (
        "## 平台实时数据快照\n"
        "- 游戏库：共 %d 款在线游戏，%d 个分类\n"
        "- 分类分布：%s\n"
        "- 用户：共 %d 位注册用户，其中 %d 位创作者/管理员\n"
        "- 评测：共 %d 篇（%s）\n"
        "- 社区：共 %d 篇帖子，%d 条评论\n"
        "- 评分记录：共 %d 条用户评分\n"
        "- Top 5 评分最高：%s\n"
        "- Top 5 热度最高：%s"
        % (game_count, cat_count, cat_dist_str,
           user_count, creator_count,
           review_count, rev_status_str,
           post_count, comment_count,
           rating_count, top_score_str, top_hot_str)
    )

    # === 游戏元数据（含分类名 + 评分人数 + 热度） ===
    cat_map = {c.id: c.name for c in cats}
    game_meta = []
    for g in games:
        game_meta.append({
            "name": g.name,
            "category": cat_map.get(g.category_id, "未分类"),
            "tags": g.tags or [],
            "score": g.average_score,
            "rating_count": g.rating_count or 0,
            "hot": g.hot or 0,
        })

    _PLATFORM_DIGEST["text"] = digest_text
    _PLATFORM_DIGEST["game_meta"] = game_meta
    _PLATFORM_DIGEST["ts"] = now
    return _PLATFORM_DIGEST


async def _ollama_chat(db, user_id: Optional[int], message: str,
                       history: Optional[list]) -> dict:
    """本地 Ollama（qwen2.5:3b）对话：注入项目上下文 + 平台数据快照 + 游戏库目录 + 对话历史，
    返回 {reply, recommendations}。模型用自然语言回答，回复中提到的游戏名会被
    自动提取为推荐卡片（小模型不强求 JSON 输出，更稳定）。"""
    from app.models import Game
    games = db.query(Game).filter(Game.is_online.is_(True)).all()
    digest = _build_platform_digest(db)
    catalog_lines = "\n".join(
        "· %s（分类：%s，标签：%s，评分：%s，%d 人评分，热度 %d）" % (
            m["name"], m["category"],
            "/".join(m["tags"][:3]) or "未分类",
            m["score"], m["rating_count"], m["hot"])
        for m in digest["game_meta"])
    system = (
        "你是「GameReview AI · AI 游戏社区评测分享平台」内置的游戏助手。\n"
        "## 你的职责\n"
        "1. 根据用户口味从平台游戏库中推荐游戏；\n"
        "2. 介绍游戏库内游戏的评分、类型、玩法冷知识；\n"
        "3. 给出简明通关思路或攻略建议；\n"
        "4. 解答平台功能（创作者申请、积分等级、审核流程、社区规则、收藏等）；\n"
        "5. 回答平台数据统计问题（如游戏总数、分类数、评分分布等），请严格按下方「平台实时数据快照」中的数字回答；\n"
        "6. 也可陪用户闲聊（自我介绍、讲游戏圈小段子、情绪安抚、道别），但主线围绕游戏。\n\n"
        "## 平台项目背景\n"
        "- 平台名：GameReview AI，是一个 AI 游戏社区评测分享平台。\n"
        "- 核心模块：游戏库（含评分/标签/封面）、游戏评测（创作者撰写、AI 审核、四维评分 剧情/画面/玩法/优化）、"
        "社区帖子（带图文、点赞收藏评论）、创作者体系（积分+等级徽标）、管理后台。\n"
        "- 创作者积分规则：发布评测 +20、精选 +30、获赞 +0.2、收藏 +0.5；"
        "等级 L1(100分)/L2(300)/L3(600)/L4(1000)。L0 不可编辑已发布评测，L1+ 每篇可编辑 1 次；"
        "抄袭扣分清零降 L0；删除评测扣除该评测所得分 + 额外 30 分。\n"
        "- 评测提交默认待审核，需 AI 风控打分后自动通过/待人工/驳回；首页与游戏评测列表不展示待审核评测。\n"
        "- 社区帖子：所有登录用户均可发布（无需审核），发帖 30 秒频率限制、评论 10 秒；"
        "单帖最多 9 图、单图 ≤5MB；标签单选（游戏/闲聊/攻略/吐槽）。\n"
        "- 短评（游戏评论）与评测（创作者长文）是两套独立系统；"
        "游戏评分 1-10 分整数，同一用户对同一游戏仅保留一条（重复提交即更新）。\n\n"
        + digest["text"] + "\n\n"
        + "## 平台游戏库目录（共 %d 款）\n" % len(digest["game_meta"])
        + catalog_lines + "\n\n"
        + "## 回答要求\n"
        "- 用简体中文、口语化、亲切风格；\n"
        "- 回答控制在 250 字以内，可分点或短段落；\n"
        "- 推荐游戏时请直接写出游戏完整名（与目录一致），并说明推荐理由；\n"
        "- 遇到数据统计问题，严格引用上方「平台实时数据快照」中的数字，不要自己猜测或编造；\n"
        "- 不知道就说不知道，不要编造不在目录里的游戏。"
    )
    msgs = [{"role": "system", "content": system}]
    for h in (history or [])[-6:]:
        if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
            msgs.append({"role": h["role"], "content": str(h["content"])[:500]})
    msgs.append({"role": "user", "content": message})
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": msgs,
        "stream": False,
        "options": {"temperature": 0.6, "num_predict": 600},
    }
    async with httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL, timeout=60.0) as client:
        resp = await client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
    reply = str(data.get("message", {}).get("content", "")).strip()
    if not reply:
        raise ValueError("ollama empty reply")
    recos = _extract_games_from_text(games, reply, limit=3)
    return {"reply": reply, "recommendations": recos}


async def _deepseek_chat(db, user_id: Optional[int], message: str,
                         history: Optional[list]) -> dict:
    from app.models import Game
    catalog = [{"id": g.id, "name": g.name, "tags": g.tags, "score": g.average_score}
               for g in db.query(Game).filter(Game.is_online.is_(True)).all()]
    system = (
        "你是「AI 游戏社区评测分享平台」的 AI 游戏助手。职责：\n"
        "1) 根据用户口味从候选游戏库中推荐游戏；2) 回答游戏库内游戏的评分与冷知识；3) 提供简明通关思路；"
        "4) 解答平台功能（创作者申请、积分等级、审核、社区规则）；5) 陪用户闲聊日常话题（自我介绍、"
        "讲游戏圈笑话、情绪安抚、道别等），但主要围绕游戏话题展开。\n"
        "平台创作者积分规则：发布评测+20、精选+30、获赞+0.2、收藏+0.5；等级 L1(100)/L2(300)/L3(600)/L4(1000)。\n"
        "用简体中文口语化回答，控制在 200 字内。若推荐游戏，把 game_id 放入 game_ids（最多 3 个）。\n"
        "只输出 JSON：{\"reply\": str, \"game_ids\": [int]}。"
    )
    msgs = [{"role": "system", "content": system}]
    for h in (history or [])[-6:]:
        if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
            msgs.append({"role": h["role"], "content": str(h["content"])[:500]})
    msgs.append({"role": "user", "content": "用户消息：" + message
                 + "\n\n候选游戏库：" + json.dumps(catalog, ensure_ascii=False)})
    payload = {
        "model": "deepseek-chat", "messages": msgs,
        "temperature": 0.6, "max_tokens": 800,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": "Bearer " + settings.DEEPSEEK_API_KEY}
    async with httpx.AsyncClient(base_url=settings.DEEPSEEK_BASE_URL, timeout=_AI_TIMEOUT) as client:
        resp = await client.post("/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        obj = json.loads(resp.json()["choices"][0]["message"]["content"])
    reply = str(obj.get("reply") or "")
    from app.models import Game as _G
    recos = []
    for gid in (obj.get("game_ids") or [])[:3]:
        g = db.query(_G).filter(_G.id == gid, _G.is_online.is_(True)).first()
        if g:
            recos.append(_game_card(g))
    if not reply:
        raise ValueError("empty chat reply")
    return {"reply": reply, "recommendations": recos}


async def ai_chat(db, user_id: Optional[int], message: str,
                  history: Optional[list] = None) -> dict:
    """对话：返回 {reply, recommendations: [{game_id, game_name, cover_url, reason, average_score}]}。
    优先级：本地 Ollama(qwen2.5:3b) → DeepSeek → 规则引擎兜底。
    标签专题（推荐巡礼/百科 10 讲/高分榜单）要求确定性回答并覆盖全部游戏，强制规则引擎。"""
    rule = _rule_chat(db, user_id, message)
    # 标签专题（推荐巡礼 10 弹 / 百科 10 讲 / 高分榜单）要求确定性回答并覆盖全部游戏，强制规则引擎
    _forced = bool(re.search(r"第\s*\d+\s*[弹讲]", message)) or any(
        w in message for w in ("巡礼", "TGA", "tga", "年度游戏", "热度最高", "最火",
                               "独立游戏", "性价比", "史低", "联机游戏", "催泪",
                               "杀时间", "耐玩", "新手入门", "平台功能", "评分规则"))
    if _forced:
        return rule
    # 优先本地 Ollama（轻量中文模型 qwen2.5:3b）
    if settings.ollama_enabled:
        try:
            return await _ollama_chat(db, user_id, message, history)
        except Exception:
            pass
    # 次选 DeepSeek 云端
    if settings.DEEPSEEK_API_KEY:
        try:
            return await _deepseek_chat(db, user_id, message, history)
        except Exception:
            pass
    return rule


# ---------------- DeepSeek chat 公共调用 ----------------

async def _chat(system: str, user: str, json_mode: bool = False) -> str:
    payload: dict = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.5,
        "max_tokens": 1024,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {"Authorization": "Bearer " + settings.DEEPSEEK_API_KEY}
    async with httpx.AsyncClient(
        base_url=settings.DEEPSEEK_BASE_URL,
        timeout=_AI_TIMEOUT,
    ) as client:
        resp = await client.post("/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
