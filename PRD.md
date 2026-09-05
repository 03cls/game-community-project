# AI 游戏社区评测分享平台 — 产品需求文档（PRD）

> 完整版需求文档，可直接作为项目需求依据，用于需求分析、前端开发、后端开发整套流程。
>
> - 运行环境：本地开发，浏览器访问 `http://localhost:8000`，仅 PC 端，无需移动端适配
> - AI：后端直接调用 DeepSeek API，不使用 Dify，简化部署

---

## 1. 项目概述

开发一个 PC 端 Web 游戏社区平台，面向游戏爱好者。平台包含三类角色：**普通玩家、评测创作者、平台管理员**。

- 普通玩家：浏览游戏库、查看评测攻略、收藏游戏、标记游玩记录；
- 评测创作者：发布游戏评测与攻略，借助 AI 辅助创作文案，提交内容进入审核流程；
- 平台管理员：用户管理、内容管理、处理 AI 审核存疑内容、维护游戏库与分类。

平台集成 **DeepSeek 大模型**，提供三项 AI 能力：

1. **AI 游戏推荐助手**（面向普通玩家）
2. **AI 攻略创作助手**（面向评测创作者）
3. **AI 内容审核助手**（自动审核用户提交的评测、攻略内容）

### 开发技术栈

| 项 | 选型 |
|---|---|
| 后端 | FastAPI + SQLAlchemy + MySQL（开发环境可用 SQLite 免装切换） |
| 前端 | HTML + CSS + JavaScript（原生）+ AJAX (fetch) |
| 认证 | JWT（JSON Web Token） |
| AI 集成 | 后端直接 HTTP 调用 DeepSeek API（无 Key 时 Mock 兜底） |
| 架构 | 严格分层 `router / service / repository`，按模块分包；每个 API 编写单元测试；模块技术文档输出到 `docs/implements` |
| 运行环境 | 本地电脑，访问地址 `http://localhost:8000` |

---

## 2. 用户角色与功能模块

### 2.1 通用功能（所有角色）

- 注册、登录、登出，JWT 维护会话状态
- 修改个人资料：昵称、头像、个人简介
- 修改登录密码
- 获取当前用户角色与权限信息
- 未登录用户：可以浏览游戏库、游戏详情、公开评测攻略；不能收藏、标记游玩记录、发布内容、使用 AI 功能；需要登录的页面跳转登录页。

### 2.2 普通玩家功能

| 功能点 | 描述 |
|---|---|
| 游戏库浏览 | 按游戏分类、热度、发布时间筛选；分页展示游戏列表 |
| 游戏搜索 | 按游戏名称、标签关键字搜索游戏，支持分页 |
| 游戏详情页 | 展示游戏封面、简介、发行时间、标签、综合评分、评测攻略列表 |
| 游戏收藏 | 添加 / 取消收藏游戏；个人中心查看我的收藏列表 |
| 游玩记录 | 标记游戏状态：想玩 / 正在玩 / 已通关；个人中心查看全部游玩档案 |
| 评测交互 | 阅读评测攻略；对文章发表评论、回复评论；点赞评论 |
| AI 游戏推荐助手 | 基于游玩记录、收藏记录，或者手动输入游戏偏好，获取个性化游戏推荐，附带推荐理由 |

### 2.3 评测创作者功能

> 获取方式：普通玩家提交创作者申请，管理员审核通过后获得创作者权限。

| 功能点 | 描述 |
|---|---|
| 评测攻略管理 | 新建、编辑、删除评测 / 攻略；支持草稿保存；填写标题、正文、关联游戏、标签 |
| 提交审核 | 完成评测 / 攻略编辑后提交审核；提交后状态变为审核中，审核通过才对外公开 |
| 查看审核状态 | 查看状态：审核中、AI 通过、AI 驳回、人工复核中；AI 驳回展示具体驳回原因 |
| 作品数据统计 | 查看自己文章的阅读量、点赞数、收藏数统计 |
| AI 攻略创作助手 | 写作页面 AI 对话框；支持生成评测大纲、通关思路；润色已有文案；分析游戏优缺点；AI 结合当前写作上下文输出内容；生成内容可一键复制到编辑器 |

### 2.4 平台管理员功能

| 功能点 | 描述 |
|---|---|
| 控制台仪表盘 | 统计总用户数、游戏总数、评测攻略总数、待审核内容数量 |
| 用户管理 | 查询用户列表；封禁 / 解封用户账号；授予 / 撤销评测创作者权限；重置用户密码 |
| 创作者申请处理 | 查看玩家提交的创作者申请，同意或驳回申请 |
| 审核队列 | 查看全部审核中、AI 驳回待人工复核的评测攻略 |
| 人工最终决策 | 对 AI 标记存疑内容手动通过 / 驳回，填写处理理由 |
| 游戏库管理 | 新增、编辑、下架游戏条目；维护游戏封面、简介、标签 |
| 游戏分类管理 | 新增、修改、删除游戏分类（RPG、射击、开放世界、模拟等） |
| 评论管理 | 查看评论，删除违规评论内容 |
| AI 审核日志 | 查看每一条内容 AI 审核详情：风险分数、命中风险、违规片段 |

---

## 3. AI 模块详细设计（DeepSeek）

### 3.1 AI 游戏推荐助手

- **触发**：玩家页面点击 AI 推荐按钮
- **输入**：可选用户手动填写偏好描述；自动读取用户游玩记录、收藏记录
- **处理**：后端把用户历史 + 偏好传给 DeepSeek；模型基于平台游戏库数据返回推荐结果
- **输出 JSON**：`[{game_id, game_name, reason}]`
- **前端**：卡片列表展示推荐游戏，点击跳转游戏详情。

### 3.2 AI 攻略创作助手

- **触发**：创作者在写作页面打开 AI 助手对话框
- **输入上下文**：关联的游戏 ID、用户已经写好的部分文本；用户提问消息
- **支持能力**：生成评测大纲、通关思路、润色文本、分析游戏优缺点
- **输出**：文本结果，前端展示，支持复制到编辑器。

### 3.3 AI 内容审核助手

- **触发**：创作者提交评测 / 攻略审核时后端自动调用
- **输入**：评测标题、正文内容
- **审核维度**：识别辱骂引战、广告引流、违法违规敏感内容
- **大模型输出字段**：
  - `status`：`passed / rejected / manual_review`
  - `risk_score`：0-100 风险分数
  - `reasons`：数组，违规片段与原因
- **业务流转**：
  - `passed` + 低分：内容自动发布公开
  - `rejected` + 高分：状态 AI 驳回，返回作者驳回理由
  - `manual_review`：进入管理员人工复核队列。

---

## 4. 认证与权限设计（JWT）

### 4.1 JWT 认证流程

- 用户注册成功不返回 token。
- 登录提交账号密码，验证成功返回 JWT；前端存储在 `localStorage`。
- 需要认证接口请求头携带 `Authorization: Bearer <token>`。
- FastAPI `Depends` 依赖解析 token，拿到 `user_id`、`role` 角色。
- Token 有效期 7 天。

### 4.2 角色权限

- **player（普通玩家）**：浏览游戏、收藏、游玩记录、评论、使用 AI 推荐助手。
- **creator（评测创作者）**：拥有玩家全部权限；可发布管理评测攻略、使用 AI 攻略创作助手。
- **admin（管理员）**：全部权限，后台管理、审核、游戏库维护。

### 4.3 安全

- 密码使用 `passlib + bcrypt` 哈希存储，不存明文。
- 用户输入后端校验；富文本内容做 XSS 过滤（bleach）。
- 未认证请求返回 401，前端清除 token 跳转登录页面。

---

## 5. 数据库设计（核心表）

使用 SQLAlchemy ORM；生成 MySQL `script.sql` 脚本。

| 表名 | 关键字段 |
|---|---|
| `users` | id, username, email, password_hash, role, is_active, created_at |
| `user_profiles` | user_id, avatar, nickname, bio |
| `game_categories` | id, category_name |
| `games` | id, name, cover_url, description, release_date, category_id, tags, average_score, is_online, created_at |
| `game_reviews` | id, game_id, user_id, title, content, status(draft/audit/published/rejected), audit_status, audit_score, audit_reason, read_count, like_count, created_at |
| `user_game_favorite` | id, user_id, game_id, created_at |
| `user_game_record` | id, user_id, game_id, play_status(want/playing/completed), created_at |
| `creator_apply` | id, user_id, apply_reason, status, audit_user_id, created_at |
| `comments` | id, user_id, target_type(review), target_id, parent_id, content, like_count, created_at |
| `audit_logs` | id, review_id, audit_type(ai/manual), risk_score, reason, operator_id, created_at |

---

## 6. API 接口约定（RESTful + JWT）

需要认证接口请求头携带 `Authorization: Bearer <token>`。

### 6.1 认证接口（无需 token）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/register` | 注册 `{username, email, password}` |
| POST | `/api/auth/login` | 登录 `{username_or_email, password}`，返回 `access_token`、`token_type`、`user_id`、`role` |

### 6.2 用户接口（需要 token）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/users/me` | 获取当前用户信息 |
| PUT | `/api/users/me` | 修改个人资料 |
| PUT | `/api/users/me/password` | 修改密码 |
| POST | `/api/users/apply-creator` | 提交创作者申请 |

### 6.3 游戏模块（部分无需 token）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/games` | 游戏列表分页筛选搜索 |
| GET | `/api/games/{id}` | 游戏详情 |
| GET | `/api/games/{id}/reviews` | 获取该游戏评测列表 |

### 6.4 玩家操作（需要 token，player+）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/favorites` | 添加游戏收藏 |
| DELETE | `/api/favorites/{game_id}` | 取消收藏 |
| GET | `/api/favorites` | 我的收藏 |
| POST | `/api/play-record` | 保存游玩状态 `{game_id, play_status}` |
| GET | `/api/play-record` | 获取我的游玩记录 |
| POST | `/api/comments` | 发表评论 |
| POST | `/api/comments/{id}/like` | 点赞评论 |

### 6.5 创作者接口（需要 token，creator+）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/reviews` | 创建评测攻略（草稿） |
| PUT | `/api/reviews/{id}` | 修改评测 |
| DELETE | `/api/reviews/{id}` | 删除评测 |
| POST | `/api/reviews/{id}/submit-audit` | 提交审核 |
| GET | `/api/creator/statistics` | 获取作品统计 |
| POST | `/api/ai/creator-assistant` | AI 攻略创作助手 |

### 6.6 管理员接口（需要 token，admin）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/users` | 用户列表 |
| PUT | `/api/admin/users/{id}/status` | 封禁解封 |
| PUT | `/api/admin/users/{id}/role` | 修改用户角色 |
| GET | `/api/admin/creator-apply` | 获取创作者申请列表 |
| PUT | `/api/admin/creator-apply/{id}/deal` | 处理申请 |
| GET | `/api/admin/reviews/pending` | 待审核评测队列 |
| POST | `/api/admin/reviews/{id}/audit-decision` | 人工审核决策 |
| POST | `/api/admin/games` | 新增游戏 |
| PUT | `/api/admin/games/{id}` | 修改游戏信息 |
| GET | `/api/admin/audit/logs` | AI 审核日志 |
| POST | `/api/admin/categories` | 分类 CRUD（含 PUT/DELETE） |
| DELETE | `/api/admin/comments/{id}` | 删除评论 |

### 6.7 AI 玩家接口（需要 token，player+）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/ai/game-recommend` | AI 游戏推荐；入参 `{preferences?: string}` |

---

## 7. 前端页面结构（PC 端）

| 页面路径 | 页面名称 | 说明 |
|---|---|---|
| `/index.html` | 首页 | 游戏推荐展示、热门游戏列表入口 |
| `/login.html` | 登录页 | 账号密码登录 |
| `/register.html` | 注册页 | 新用户注册 |
| `/game-list.html` | 游戏库列表页 | 筛选搜索游戏 |
| `/game-detail.html?id=xx` | 游戏详情页 | 游戏信息、评测攻略列表 |
| `/my-profile.html` | 个人中心 | 修改资料、我的收藏、游玩记录、提交创作者申请 |
| `/creator-work.html` | 创作者工作台 | 我的评测列表、草稿管理 |
| `/creator-edit.html?id=xx` | 评测编辑页面 | 编辑器 + AI 创作助手对话框 |
| `/admin/index.html` | 管理员控制台 | 数据仪表盘 |
| `/admin/user.html` | 用户管理页面 | 用户查询、封禁、角色授予 |
| `/admin/audit-queue.html` | 审核队列页面 | 处理评测、查看 AI 审核日志 |
| `/admin/game-manage.html` | 游戏 & 分类管理页面 | 维护游戏库数据 |

**前端要求：**

- 使用原生 `fetch` 做 AJAX 请求；封装请求拦截器自动带上 token
- 捕获 401 响应：清除 `localStorage` token，跳转到登录页面
- 评测编辑使用轻量富文本编辑器
- 使用模拟静态图片作为游戏封面测试素材
- 前端内置 Mock 数据层，后端未启动时也可独立打开页面进行测试

---

## 8. 本地开发环境

**依赖：**

- Python 3.10+（实际开发环境 Python 3.9 兼容）
- MySQL 8.0（未安装时可用 SQLite 免装运行，通过 `.env` 的 `DATABASE_URL` 切换）
- 依赖包：`fastapi uvicorn sqlalchemy pymysql python-jose passlib bcrypt httpx python-dotenv bleach pytest`

**启动步骤：**

1. 创建 python 虚拟环境，安装依赖：`pip install -r requirements.txt`
2. MySQL 创建数据库：`game_community`（或使用 SQLite，零配置）
3. `.env` 配置数据库连接信息、DeepSeek API Key
4. SQLAlchemy 模型生成数据表，导出 `script.sql` 脚本
5. `uvicorn main:app --reload --port 8000` 启动后端
6. 前端静态文件放置在 `static` 目录，FastAPI 挂载 static 静态资源；浏览器访问 `http://localhost:8000/static/index.html`

---

## 9. 非功能性需求

- 普通页面加载小于 2 秒；AI 接口允许 3-8 秒响应。
- 安全：密码 bcrypt 哈希；XSS 过滤用户富文本；JWT 鉴权；后端参数校验。
- 浏览器：Chrome、Edge、Firefox 最新版本，只做 PC 端。
- 后端分层架构 `router / service / repository`；每个模块 API 编写单元测试；模块技术实现文档输出到 `docs/implements/*.md`。

---

## 10. 暂不实现（扩展方向）

- 用户等级、积分系统
- 文件上传图片服务器（本项目使用本地静态图片模拟）
- WebSocket 实时通知
- 第三方登录

---

*（注：部分内容可能由 AI 生成）*
