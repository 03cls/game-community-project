# CLAUDE.md — AI 游戏社区评测分享平台

本文件为 AI 编程助手提供项目上下文（由 `/init` 流程生成）。

## 项目简介

AI 游戏社区评测分享平台：PC 端 Web 游戏社区，三类角色（普通玩家 player / 评测创作者 creator / 平台管理员 admin），
集成 DeepSeek 大模型提供 **AI 游戏推荐、AI 攻略创作、AI 内容审核** 三项能力。

完整需求见 [PRD.md](PRD.md)。

## 技术栈

- **后端**：Python 3.9+ / FastAPI / SQLAlchemy 2.x / Pydantic v2
- **数据库**：MySQL 8.0（生产目标）；开发默认 SQLite 零配置运行，通过 `.env` 的 `DATABASE_URL` 切换
- **认证**：JWT（python-jose），密码 passlib + bcrypt
- **AI**：httpx 直连 DeepSeek API；未配置 `DEEPSEEK_API_KEY` 时自动降级为 Mock 响应
- **前端**：原生 HTML + CSS + JavaScript（ES6+）+ fetch，无构建工具、无框架
- **测试**：pytest + FastAPI TestClient
- **安全**：bleach 做富文本 XSS 过滤

## 目录结构

```
.
├── PRD.md                  # 产品需求文档
├── CLAUDE.md               # 本文件（AI 助手上下文）
├── requirements.txt        # Python 依赖
├── .env / .env.example     # 环境变量（数据库、JWT 密钥、DeepSeek Key）
├── main.py                 # FastAPI 入口（uvicorn main:app --port 8000）
├── app/                    # 后端应用包
│   ├── core/               # 配置 config、安全 security、依赖注入 deps
│   ├── db/                 # 数据库会话 session、Base、初始化 init_db
│   ├── models/             # SQLAlchemy ORM 模型（一模块一文件）
│   ├── schemas/            # Pydantic 模型（请求/响应 DTO）
│   ├── routers/            # 路由层（controller），只做参数校验与转发
│   ├── services/           # 业务逻辑层，事务边界
│   ├── repositories/       # 数据访问层，只做 CRUD
│   └── ai/                 # DeepSeek 客户端 + Mock 兜底
├── sql/script.sql          # MySQL 建库建表脚本（阶段4 交付）
├── static/                 # 前端工程（FastAPI 挂载到 /static）
│   ├── index.html / login.html / ...  # 12 个页面
│   ├── css/  js/  images/
│   └── 前端分析设计报告.md   # 阶段3 交付物
├── prototype/              # 阶段2 UI 原型（低保真线框图）
├── tests/                  # pytest 单元测试（按模块组织）
├── docs/implements/        # 后端各模块技术实现报告 *.md
└── data/                   # SQLite 数据库文件与种子数据（运行时生成）
```

## 架构约定（严格分层）

```
router（HTTP 入参/出参、权限校验）
  └─ service（业务规则、事务、AI 调用编排）
       └─ repository（SQLAlchemy 查询，无业务逻辑）
            └─ model（ORM）
```

- 一个业务模块一个包/文件组：`auth / users / games / reviews / favorites / play_record / comments / creator_apply / admin / ai`
- router 不直接操作 ORM；service 不直接处理 HTTP；repository 不返回 Pydantic 对象
- 所有 API 必须有单元测试（pytest + TestClient + SQLite 内存库）
- 每个后端模块完成后在 `docs/implements/<模块>.md` 输出技术实现报告

## 开发命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端（自动建表 + 种子数据）
uvicorn main:app --reload --port 8000
# 访问：http://localhost:8000/static/index.html
# API 文档：http://localhost:8000/docs

# 前端独立预览（无需后端，自动走 Mock）
cd static && python -m http.server 8080

# 运行全部单元测试
pytest -v
```

## 环境变量（.env）

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DATABASE_URL` | 数据库连接串 | `sqlite:///./data/game_community.db` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 开发内置值 |
| `JWT_EXPIRE_DAYS` | Token 有效期（天） | `7` |
| `DEEPSEEK_API_KEY` | DeepSeek 密钥，留空则 AI 走 Mock | 空 |
| `DEEPSEEK_BASE_URL` | DeepSeek 接口地址 | `https://api.deepseek.com` |

## 种子账号（开发测试用）

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | `admin` | `admin123` |
| 创作者 | `creator` | `creator123` |
| 玩家 | `player` | `player123` |

## 编码规范

- Python：类型注解齐全；snake_case；模块内按 router → service → repository 分层
- 前端：原生 JS，`js/api.js` 封装 fetch（自动带 token、401 跳登录）；`js/mock.js` 为 Mock 数据层
- API 路径统一 `/api/` 前缀，RESTful 风格，与 PRD 第 6 节完全一致
- 富文本入库前经 bleach 白名单清洗；密码一律 bcrypt；敏感信息不入库不入日志
