# GameReview AI — 公网部署指南（GitHub + Render）

> 目标：任何人通过一个公网网址即可使用平台全部功能（注册/登录/评测/社区/评分/AI 对话）。
>
> 为什么不能只用 GitHub Pages？GitHub Pages 只能托管静态页面，无法运行 FastAPI 后端
> 和 SQLite 数据库。方案：**GitHub 存放代码 + Render 免费运行服务**。

---

## 方案总览

| 角色 | 平台 | 费用 |
|------|------|------|
| 代码仓库 | GitHub | 免费 |
| 运行服务（FastAPI + SQLite + 静态前端） | Render.com | 免费 |
| AI 内核 | 规则引擎（内置），可选 DeepSeek API | 免费 / 按量 |

项目已具备云端部署条件：
- 前端 api.js 使用相对路径 `/api/...`，同源部署零改动
- 启动时自动建库 + 自动灌入种子数据（30 款游戏 / 67 篇评测 / 7 个账号）
- AI 三级降级：云端设 `OLLAMA_ENABLED=0` 后自动用规则引擎，零外部依赖
- `render.yaml` 已就绪（Render Blueprint）

---

## 第一步：推送代码到 GitHub

1. 在 https://github.com/new 创建仓库（例如 `gamereview-ai`），**不要**勾选 README/.gitignore（本地已有）。
2. 在项目根目录 `c:\Users\ABC\Documents\trae_projects\1` 执行：

```bash
git add .
git commit -m "feat: 完整平台 v1.0（消息通知/评论互动/多账号/AI 内核）+ 部署配置"
git remote add origin https://github.com/<你的用户名>/gamereview-ai.git
git branch -M main
git push -u origin main
```

> `.gitignore` 已排除 `.env`、`data/`（数据库）、日志，密钥不会被上传。

## 第二步：Render 一键部署

1. 注册/登录 https://render.com （可用 GitHub 账号直接登录）。
2. 进入 Dashboard → **New → Blueprint**，选择刚推送的 `gamereview-ai` 仓库。
3. Render 读取 `render.yaml` 自动完成配置，直接点 **Apply**。
4. 等待 3-5 分钟构建完成，得到公网地址，例如：

```
https://gamereview-ai.onrender.com/static/index.html
```

这就是可以发给任何人的使用地址。

### 可选：升级 AI 为云端大模型

Render 项目 → Environment → 编辑 `DEEPSEEK_API_KEY`，填入 https://platform.deepseek.com
申请的 Key。之后 AI 对话由 DeepSeek 大模型接管（审核仍走规则引擎），不填则全部用内置规则引擎。

---

## 免费版注意事项

| 事项 | 说明 |
|------|------|
| 冷启动 | 15 分钟无访问会休眠，下次访问约 30-60 秒唤醒（首次打开稍慢属正常） |
| 数据持久性 | 免费版磁盘是临时的：**重新部署/重启后，运行期注册的用户和发布的内容会重置为种子数据**（演示完全够用；如需持久化可升级付费磁盘或改用外部数据库） |
| 并发 | 免费版 512MB 内存，单人演示 / 小规模访问无压力 |
| 演示账号 | admin/admin123 · creator/creator123 · player/player123 |

---

## 本地运行（对照）

```bash
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
# 打开 http://127.0.0.1:8000/static/index.html
# 本地 AI：先安装 Ollama 并执行 ollama pull qwen2.5:3b
```
