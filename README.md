---
title: GameReview AI
emoji: 🎮
colorFrom: amber
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# 🎮 GameReview AI — AI 游戏社区评测分享平台

以 **Ollama 本地大模型**为智能内核的游戏社区评测分享平台：游戏库浏览、四维评分雷达、PGC 评测攻略（AI 风控审核）、UGC 社区、评论楼中楼互动、实时消息通知、AI 推荐助手。

## ✨ 功能一览

- **游戏库**：30 款游戏 · 7 大分类 · Steam CDN 封面 · 四维雷达评分
- **评测攻略（PGC）**：创作者撰写 · AI 风控审核 · 积分等级体系（L0-L4）
- **社区（UGC）**：发帖（≤9 图）· 点赞收藏 · 楼中楼评论回复 · 频率限制
- **消息通知**：评论/点赞/收藏/审核/申请全埋点 · 10 秒轮询 · 点击直达
- **AI 助手**：游戏推荐 / 游戏百科 / 高分榜单 / 卡关求助，三级降级架构
- **多账号登录**：同一浏览器可登录多个账号一键切换
- **管理后台**：审核队列 · 举报处理 · 数据仪表盘 · 7 大模块

## 🤖 AI 智能内核（三级降级）

```
① Ollama 本地模型 qwen2.5:3b（localhost:11434）
        ↓ 不可用时降级
② DeepSeek 云端 API（配置 DEEPSEEK_API_KEY 后启用）
        ↓ 不可用时降级
③ 内置规则引擎（意图识别 + 游戏知识库 + 实时数据查询）
```

云端部署时自动使用规则引擎，**零外部依赖全部功能可用**。

## 🧑‍💻 演示账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | admin123 |
| 创作者 | creator | creator123 |
| 玩家 | player | player123 |

## 🛠 技术栈

FastAPI · SQLAlchemy ORM · SQLite · JWT 认证 · 原生 HTML/CSS/JS（暗色琥珀金主题）

## 🚀 本地运行

```bash
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
# 打开 http://127.0.0.1:8000/static/index.html
# 本地启用 AI：安装 Ollama 后执行 ollama pull qwen2.5:3b
```

## 📦 部署

- **Hugging Face Spaces（Docker SDK）**：本仓库已含 Dockerfile，新建 Space 选 Docker 直接部署
- **Render**：使用 render.yaml Blueprint 一键部署（需绑卡验证）

详见 [DEPLOY.md](./DEPLOY.md)。
