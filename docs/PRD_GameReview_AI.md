# GameReview AI — 产品需求文档（PRD）

> **版本**：v1.0（反向梳理版）  
> **日期**：2026-09-07  
> **方法**：基于项目实际代码反向梳理，非前瞻性设计文档  
> **状态**：已交付

---

## 一、产品概述

### 1.1 产品定位
GameReview AI 是一个以本地大模型驱动的游戏社区评测分享平台。AI 智能内核采用 Ollama 本地部署的轻量中文模型（qwen2.5:3b），融合游戏评分、评测攻略创作、社区互动和 AI 智能推荐，以暗色琥珀金主题（《黑神话：悟空》视觉风格）为设计基准。

### 1.2 核心价值
- **玩家**：发现好游戏、参与社区互动、获取真实评测
- **创作者**：发布专业评测攻略、AI 风控审核、积分等级体系、AI 创作辅助
- **管理员**：高效审核管理、维护社区秩序、数据仪表盘监控

### 1.3 技术栈
| 层级 | 技术选型 | 版本要求 |
|------|---------|---------|
| 后端框架 | Python FastAPI | ≥0.110 |
| ASGI 服务器 | uvicorn[standard] | ≥0.27 |
| ORM | SQLAlchemy | ≥1.4, <2.0 |
| 数据库 | SQLite（零配置） / MySQL（pymysql 可选） | — |
| 前端 | 原生 HTML/CSS/JavaScript（无框架） | — |
| AI 智能内核 | Ollama 本地模型（qwen2.5:3b） | localhost:11434 |
| AI 备选 | DeepSeek API（云端，DEEPSEEK_API_KEY 为空时自动跳过） | api.deepseek.com |
| HTTP 客户端 | httpx（异步） | ≥0.27 |
| 认证 | python-jose JWT + bcrypt 密码哈希 | — |
| 内容清洗 | bleach | ≥6.0 |
| 测试 | pytest | ≥8.0 |

### 1.4 AI 三级降级策略
```
用户消息
  │
  ├─ 标签专题（推荐巡礼/百科10讲/高分榜单等关键词）？
  │    └─ 强制规则引擎（确定性回答 + 全库覆盖）
  │
  ├─ Ollama 本地模型可用？（OLLAMA_ENABLED=1）
  │    └─ 调用 qwen2.5:3b（注入平台数据快照 + 游戏库目录）
  │         └─ 从自然语言回复中提取游戏名 → 推荐卡片
  │
  ├─ DeepSeek API 可用？（DEEPSEEK_API_KEY 非空）
  │    └─ 调用 deepseek-chat（JSON response format）
  │
  └─ 兜底：规则引擎
       └─ 意图识别 → 关键词匹配 → 知识库 + 数据库查询
```

**设计原则**：本地模型优先（隐私 + 零成本），云端 API 备选，规则引擎兜底保证可用性。

---

## 二、用户角色与权限

### 2.1 角色定义
| 角色 | 权限范围 | 种子账号 |
|------|---------|---------|
| 游客 | 浏览游戏库、评测、社区帖子；不可发帖/评论/评分 | — |
| 玩家 (player) | 全部浏览 + 社区互动 + 游戏评分 + 短评论 + 申请创作者 | player / player123 |
| 创作者 (creator) | 玩家权限 + 发布评测攻略 + AI 创作助手 + 创作者工作台 | creator / creator123 |
| 管理员 (admin) | 创作者权限 + 后台管理全部模块 | admin / admin123 |

### 2.2 多账号支持
- `gc_accounts` localStorage 存储已登录账号列表 `[{token, user}]`
- `setSession(token, user)` 自动去重写入（按 user.id 去重）
- 导航栏下拉菜单展示全部已登录账号，当前账号 ✓ 标记
- 一键切换账号（`switchAccount` → reload），无需退出重登
- 退出当前账号自动切换到其他已登录账号（`clearSession` 过滤当前 token 后回写）
- 添加账号入口：`login.html?add=1`（标题改为「添加账号」，按钮文字「➕ 添加并切换」）
- 401 处理：移除失效账号 token，有其他账号自动切换 + reload，否则跳转登录页

### 2.3 创作者等级体系
| 等级 | 积分阈值 | 权益 |
|------|---------|------|
| L0 见习 | 0 | 可提交评测待审核，不可编辑已发布评测 |
| L1 普通 | 100 | 已发布评测可编辑 1 次 |
| L2 优质 | 300 | 同 L1 |
| L3 资深 | 600 | 同 L1 |
| L4 核心 | 1000 | 同 L1 |

### 2.4 积分规则
| 行为 | 积分变化 |
|------|---------|
| 发布评测 | +20 |
| 评测入选精选 | +30 |
| 评测获赞 | +0.2/赞（取消扣回） |
| 评测被收藏 | +0.5/次 |
| 删除评测 | 扣回该评测所得积分 + 额外 30 分 |
| 抄袭评测 | 积分清零 + 降级 L0 |

---

## 三、功能模块

### 3.1 首页
- **Hero 区域**：左侧游戏封面（Steam CDN 原始比例 460:215 完整显示），右侧 AI 推荐助手面板（高度与封面一致，内容内部滚动）
- **AI 游戏推荐助手**：
  - 4 个 Tab：推荐游戏 / 高分游戏 / 游戏百科 / 卡关
  - 每个 Tab 至少 10 条响应，覆盖全库 30 款游戏
  - 标签轮换机制：`data-qs="q1|q2|q3"` 竖线分隔候选，按序轮换发送
  - 匿名用户可对话（`get_optional_user` 不强制登录）
- **热门游戏区**：横向卡片滚动
- **评测攻略区**：8-10 秒轮询拉取已通过评测
- **全站暗色琥珀金主题**：双径向渐变光晕背景 + Noto Serif SC 衬线标题

### 3.2 游戏库
- 游戏列表：分类筛选 + 关键词搜索 + 分页
- 游戏详情页三栏 Hero 布局：
  - **左栏**：封面 + 缩略图条（Steam CDN 四图：library_600x900 / header / capsule_616x353 / library_hero，onerror 兜底 SVG）
  - **中栏**：meta-grid 信息、标签、描述展开/收起、Steam 购买按钮（`steam_url` 非空时显示，新标签页打开）
  - **右栏**：评分栏（综合评分 + 四维雷达 SVG + dim-chips + 我的评分 + 热门短评）
- 下方：横向滚动截图画廊（lightbox 大图）、评测攻略区、相似推荐 similar-grid（无数据时隐藏）

### 3.3 游戏评分系统
- `game_ratings` 表：(game_id, user_id) 唯一约束，score 为 int 1-10
- 同一用户对同一游戏仅保留一条评分记录（重复提交 = 更新）
- 评分提交需登录（401 否则），游戏详情返回 `my_rating`（null 表示匿名/未评分）
- 综合评分聚合公式（`recalc_game_scores`）：
  - `rating_count` = 已发布评测的四维评分数 + 用户评分记录数
  - `average_score` = 评测四维均值与用户分数的加权合并
  - 四维雷达评分仅从评测聚合（用户评分不影响四维）
- 两个不同的 keyword 过滤器：
  - `GET /api/reviews?keyword=` — 按游戏名过滤（首页评测区）
  - `GET /api/games/{id}/reviews?keyword=` — 按评测标题/内容过滤（游戏详情评测列表）

### 3.4 评测攻略系统（创作者 PGC）
- **评测结构**：标题 + 关联游戏 + 正文 + 标签 + 四维评分（剧情/画面/玩法/优化）
- **AI 风控审核**（`ai_audit`）：
  - 提交后 AI 对标题+正文进行风险扫描
  - 检测维度：广告引流词（加群/微信/vx/代购/http://等）、辱骂引战词（傻逼/垃圾游戏/废物等）
  - 判定逻辑：命中广告+辱骂 → rejected(85+分)；仅辱骂 → manual_review(55+分)；未命中 → passed(2-9分)
  - 审核模式：Ollama 未参与审核，使用 DeepSeek API 或规则引擎（`_mock_audit`）降级
- **状态流转**：draft → audit（待审核）→ published（已通过）/ rejected（已驳回）/ manual_review（待人工）
- **权限**：
  - 仅 creator/admin 角色可发布评测（`require_role("creator")`）
  - 已通过评测全部用户可见；待审核/已驳回仅作者本人可见（他人访问 403）
  - L0 不可编辑已发布评测；L1+ 每篇 1 次编辑机会（`edit_used` 字段）
- **排序**：精选（`is_featured`）→ 创作者等级 → 发布时间
- **管理**：创作者工作台 + 个人中心均支持 5 个状态分类标签 + 分页

### 3.5 社区系统（UGC）
- **帖子结构**：标题（2-100 字）+ 正文 + 图片（最多 9 张，单张 ≤5MB）+ 标签（单选：游戏/闲聊/攻略/吐槽）
- **排序**：推荐（热度）/ 最新（时间倒序）/ 标签筛选
- **互动**：点赞、收藏、评论（楼中楼回复 `parent_id`）、删除自己的帖子/评论
- **频率限制**：发帖 30s/次，评论 10s/次
- **图片上传**：FormData → `/api/community/upload`，保存到项目根 `static/uploads`
- **隐私**：我的收藏/点赞仅本人可见，他人访问 403
- **权限**：所有登录用户可发帖（无需审核权限）；帖主可删除其下所有评论；管理员可删除违规帖+封禁用户

### 3.6 评论系统
- **统一模型**：`Comment` 表，`target_type` 区分归属（game=游戏短评 / review=评测评论）
- **楼中楼回复**：`parent_id` 字段支持嵌套回复
- **操作**：发表、回复（`POST /comments` 带 `parent_id`）、点赞（`POST /comments/{id}/like`）、删除（`DELETE /comments/{id}`）
- **删除权限**：仅本人（`user_id == comment.user_id`）或管理员可删，级联删除子回复
- **`can_delete` 字段**：`comment_out` 返回 `can_delete = (current_user_id == comment.user_id)`，前端据此渲染删除按钮
- **游戏短评**：
  - 自动精选评论：最高赞 + 最早创建（`is_selected` 字段已废弃）
  - 分页：普通评论每页 5-10 条（page_size clamp 1-10）
  - 显示顺序：精选 → 普通分页（时间倒序）
- **评测评论**：顶层评论 + 嵌套回复，支持回复/删除/点赞
- **「我的评论」**：`GET /comments/mine` 聚合游戏短评 + 评测评论，分页返回 `target_name/target_cover`，点击跳转 `#comment-{id}` 锚点

### 3.7 消息通知系统
- **通知模型**：`Notification` 表（id/user_id/type/title/content/actor_id/target_type/target_id/is_read/created_at）
- **通知类型**：reply（评论回复）/ like（点赞）/ favorite（收藏）/ audit（审核结果）/ apply（创作者申请）/ system（系统）
- **通知推送**：
  - `notify.push(db, user_id, ...)` — 单用户，自己不通知自己（`actor_id == user_id` 时跳过）
  - `notify.push_to_admins(db, ...)` — 全部管理员（如收到新创作者申请）
- **埋点位置**：
  - 评论回复 → 通知被回复者（target_type=review/game）
  - 评测/评论点赞 → 通知作者
  - 评测被收藏 → 通知作者
  - 管理员审核通过/驳回 → 通知创作者
  - 创作者申请提交 → 通知全部管理员；申请通过/驳回 → 通知申请人
- **实时性**：导航栏铃铛 10 秒轮询未读数（`GET /notifications/unread-count`），消息中心 10 秒轮询列表
- **消息中心**（`messages.html`）：5 个 Tab（全部/评论回复/点赞/收藏/系统通知）+ 只看未读 + 全部已读 + 分页
- **跳转**：点击消息 → 标记已读（`POST /notifications/{id}/read`）+ 直达对应页面

### 3.8 AI 模块
#### 3.8.1 三层架构
| 层 | 文件 | 职责 |
|----|------|------|
| 前端 | `mock.js` + `index.html` / `creator-edit.html` | 事件委托标签 `data-qs` / `data-action` + `busy` 防重复 + Mock 模式 |
| 后端 | `ai_client.py` | 规则意图识别 + 游戏知识库 + Ollama/DeepSeek 调用 + 平台数据快照 |
| API | `routers/ai.py` | `POST /api/ai/chat`（匿名可用）/ `POST /api/ai/game-recommend`（需登录）/ `POST /api/ai/creator-assistant`（需 creator 角色） |

#### 3.8.2 Ollama 本地模型
- **模型**：qwen2.5:3b（轻量中文模型，通过 `OLLAMA_MODEL` 环境变量配置）
- **端点**：`http://localhost:11434/api/chat`（通过 `OLLAMA_BASE_URL` 配置）
- **调用方式**：`httpx.AsyncClient` 异步 POST，`timeout=60s`
- **参数**：`temperature=0.6`, `num_predict=600`, `stream=False`
- **System Prompt 注入**：
  - 平台项目背景（核心模块/积分规则/审核流程/社区规则）
  - 平台实时数据快照（游戏数/分类/用户/评测/社区/评分统计）
  - 游戏库目录（每款游戏的名称/分类/标签/评分/评分人数/热度）
  - 对话历史（最近 6 条，每条截断 500 字）
  - 回答要求（简体中文、口语化、≤250 字、推荐时写出完整游戏名）
- **推荐提取**：`_extract_games_from_text()` 从自然语言回复中按四层匹配提取游戏名 → 生成推荐卡片

#### 3.8.3 DeepSeek 云端备选
- **模型**：deepseek-chat
- **端点**：`DEEPSEEK_BASE_URL/chat/completions`
- **调用方式**：`httpx.AsyncClient` 异步 POST，JSON response format
- **触发条件**：`DEEPSEEK_API_KEY` 非空且 Ollama 不可用时

#### 3.8.4 规则引擎兜底
- **意图识别关键词**：
  - 评分查询：评分/多少分/分数
  - 排行榜：最高/排行/榜单/top/高分/前十
  - 攻略求助：攻略/怎么打/卡关/通关/打法/技巧
  - 游戏推荐：推荐/有什么/想玩/好玩的
  - 类型匹配：rpg/射击/开放世界/剧情/动作/冒险/策略/模拟/恐怖/魂/像素/国产/独立/合作/竞速/沙盒/二次元/奇幻/科幻/生存/解谜
  - 平台问答：平台功能/评分规则
  - 闲聊/笑话：笑话/段子/逗我/好笑
- **游戏名四层匹配**：`_GAME_ALIASES` 别名表 → 中文全名包含 → 英文名包含 → `_norm_name` 归一化（去空格/中英文标点+lower）
- **游戏知识库**：`_GAME_KNOWLEDGE` 为每款游戏提供 intro/facts/tips，冷知识随机抽取
- **强制规则引擎场景**：标签专题（推荐巡礼/百科10讲/高分榜单/TGA/年度游戏/热度最高/独立游戏等关键词）要求确定性回答 + 全库覆盖

#### 3.8.5 平台数据快照
- **函数**：`_build_platform_digest(db)` — 聚合游戏/分类/评测/社区/用户/评分数据
- **缓存**：30 秒 TTL（`_PLATFORM_DIGEST` 模块级变量），避免每次 AI 调用重复查聚合 SQL
- **快照内容**：
  - 游戏库总数 + 分类数 + 分类分布
  - 用户数 + 创作者/管理员数
  - 评测数 + 状态分布（已发布/待审核/待人工/已驳回）
  - 社区帖子数 + 评论数
  - 评分记录数
  - Top 5 评分最高 + Top 5 热度最高
  - 游戏元数据（名称/分类/标签/评分/评分人数/热度）

#### 3.8.6 AI 评测审核
- **函数**：`ai_audit(title, content)` → `{status, risk_score, reasons}`
- **降级链**：DeepSeek API（JSON response）→ `_mock_audit` 规则引擎兜底
- **注意**：Ollama 不参与审核，审核仅用 DeepSeek 或规则引擎

#### 3.8.7 创作者 AI 助手
- **端点**：`POST /api/ai/creator-assistant`（需 creator 角色）
- **快捷按钮**：写开头/写结尾/标题建议/评分推荐 + 自由对话
- **前端**：`creator-edit.html` 事件委托 `data-qs` / `data-action` + `busy` 防重复

### 3.9 管理员后台
| 模块 | 文件 | 功能 | 特色 |
|------|------|------|------|
| 数据仪表盘 | `admin/index.html` | 平台概览统计 | 实时数据 |
| 用户与申请管理 | `admin/user.html` | 用户列表 + 创作者申请审批 | 5-8s 轮询申请列表，离开销毁定时器 |
| 审核队列 | `admin/audit-queue.html` | 待审核评测 + 通过/驳回 + AI 日志 | 5-8s 轮询，离开销毁定时器 |
| 游戏 & 分类管理 | `admin/game-manage.html` | 游戏 CRUD + 分类管理 | 10 条/页分页 |
| 评论管理 | `admin/comments.html` | 全站评论列表 + 删除违规 | 10 条/页分页 |
| 社区与举报 | `admin/community.html` | 举报队列 + 帖子管理 | 关键词搜索 + 查看跳转 |
| 已发布评测 | — | 已通过评测列表 | 分页浏览 |

### 3.10 个人中心
- **锚点快捷导航**：收藏/评测互动/我的评测/我的评论/社区/游玩档案
- **我的评测**：5 个状态分类标签（全部/已发布/草稿/待审核/已驳回）+ 分页（5 条/页）
- **我的评论**：`GET /comments/mine` 聚合游戏短评 + 评测评论，分页，点击跳转 `#comment-{id}` + 删除
- **评测互动**：我赞过的 / 我收藏的评测
- **社区**：我的帖子 / 我的收藏 / 我的点赞（三 Tab，仅本人可见）
- **游玩档案**：游戏游玩状态（想玩/在玩/已通关）
- **创作者申请**：apply_reason（10-200 字）+ good_at（≤100 字）+ experience（≤200 字）
  - 玩家入口：`my-profile.html?tab=apply`（卡片 flash 高亮）
  - 创作者/管理员入口：`creator-work.html`

### 3.11 创作者工作台
- 评测管理表格：5 个状态分类标签 + 分页（10 条/页）+ 操作（查看/编辑/提交审核/删除）
- AI 攻略创作助手：快捷按钮 + 自由对话
- 创作者统计数据
- 轮询防抖签名纳入 `page+status`，切换分类时强制重绘

### 3.12 智能返回功能
- **函数**：`U.goBack(fallback)` — 统一智能返回
- **策略**：
  1. 同标签页导航（`history.length > 1 && !window.opener`）→ `history.back()`
  2. 新标签页（`target=_blank` 打开，如管理员从审核队列点「查看」）→ `document.referrer` 同源则跳转
  3. 兜底 → fallback URL
- **覆盖页面**：game-detail / review-detail / review-list / community-post / community-new / creator-edit

---

## 四、非功能需求

### 4.1 UI 主题规范
- 暗色琥珀金主题：`--accent #E8A33D` / `--accent-2 #F2C879`
- Noto Serif SC 衬线标题 + Noto Sans SC 正文
- 双径向渐变光晕背景
- CSS 变量重映射保留旧类名兼容（`--surface`/`--card`/`--line`/`--text-2` 映射到新色板）

### 4.2 响应式设计
- ≤960px 收紧 gap/字号、隐藏角色徽标
- ≤840px 隐藏 nav-search、nav 字号 12.5px、user-chip 文本 max-width 88px
- ≤1100px 详情页 score-col `grid-column: 1 / -1` + CSS columns:2 自动均衡
- ≤768px 回落 columns:1
- 顶栏溢出排查方法：`browser_evaluate` 遍历 `getBoundingClientRect().right > documentElement.clientWidth`

### 4.3 缓存对策
- CSS/JS 引用带版本参数（当前 CSS `style.css?v=proto12` / JS `js/auth.js?v=cmnt1`）
- 每次修改 CSS 必须整体 bump 版本号
- 数据库种子数据使用 DB_KEY 版本控制缓存

### 4.4 服务部署
- **按需一键启动**（非开机自启）
- `start-platform.bat`：检测端口 8000 → 未运行则启动 uvicorn + 健康检查（最长 60 秒）→ 打开 `http://127.0.0.1:8000/static/index.html`
- 已运行则直接打开首页
- 启动入口：`python -m uvicorn main:app --port 8000`（不是 `app.main:app`）

### 4.5 AI 模型部署
- **Ollama 本地部署**：用户需提前安装 Ollama 并拉取模型 `ollama pull qwen2.5:3b`
- **默认配置**：`OLLAMA_BASE_URL=http://localhost:11434`，`OLLAMA_MODEL=qwen2.5:3b`，`OLLAMA_ENABLED=1`
- **DeepSeek 备选**：`.env` 中填写 `DEEPSEEK_API_KEY` 即可启用云端 AI（Ollama 不可用时自动降级）
- **零 AI 也可运行**：Ollama 和 DeepSeek 均不可用时，规则引擎兜底保证全部功能可用

---

## 五、数据模型

### 5.1 核心表
| 表名 | 关键字段 | 说明 |
|------|---------|------|
| users | id, username, email, password, role, is_active, nickname, avatar, bio, creator_points, creator_level | 用户 |
| games | id, name, name_en, developer, publisher, cover_url, description, release_date, category_id, average_score, rating_count, steam_url, score_story, score_graphics, score_gameplay, score_optimization, is_online, hot | 游戏 |
| categories | id, name, slug | 游戏分类 |
| game_tags | id, game_id, tag | 游戏标签 |
| reviews | id, title, user_id, game_id, status, audit_score, audit_reason, is_featured, edit_used, body, score_story, score_graphics, score_gameplay, score_optimization, view_count, like_count, fav_count | 评测 |
| comments | id, user_id, target_type, target_id, parent_id, content, like_count, created_at | 评论 |
| comment_likes | comment_id, user_id | 评论点赞 |
| game_ratings | game_id, user_id, score | 游戏评分（唯一约束） |
| notifications | id, user_id, type, title, content, actor_id, target_type, target_id, is_read, created_at | 消息通知 |
| community_posts | id, title, content, user_id, tag, like_count, fav_count, comment_count | 社区帖子 |
| community_comments | id, post_id, user_id, content, parent_id | 社区评论 |
| point_records | id, user_id, change, description, related_type, related_id | 创作者积分流水 |
| creator_applications | id, user_id, apply_reason, good_at, experience, status | 创作者申请 |
| favorites | id, user_id, target_type, target_id | 收藏 |
| play_records | id, user_id, game_id, status | 游玩记录 |

---

## 六、API 设计

### 6.1 路由前缀
| 前缀 | 文件 | 主要端点 |
|------|------|---------|
| /api/auth | auth.py | 注册、登录 |
| /api/users | users.py | 用户资料、修改密码、创作者申请 |
| /api/games | games.py | 游戏列表、详情、相似推荐、评分 |
| /api/comments | comments.py | 评论 CRUD（含 mine / like / delete） |
| /api/reviews | reviews.py | 评测 CRUD、点赞、收藏、提交审核 |
| /api/community | community.py | 帖子 CRUD、评论、举报、图片上传 |
| /api/creator | creator.py | 创作者工作台、评测管理 |
| /api/ai | ai.py | AI 对话、推荐、创作助手 |
| /api/notifications | notifications.py | 通知列表、未读数、已读 |
| /api/favorites | favorites.py | 收藏管理 |
| /api/play_records | play_records.py | 游玩记录 |
| /api/admin | admin.py | 后台管理全部模块 |

### 6.2 AI 端点详解
| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| /api/ai/chat | POST | 匿名可用（`get_optional_user`） | AI 对话助手，三级降级 |
| /api/ai/game-recommend | POST | 需登录 | 基于偏好推荐游戏 |
| /api/ai/creator-assistant | POST | 需 creator 角色 | 创作者 AI 创作助手 |

---

## 七、种子数据

| 类型 | 数量 | 说明 |
|------|------|------|
| 用户 | 7 | admin / creator / player + 4 个种子用户 |
| 游戏 | 30 | Steam 真实数据（封面 CDN），覆盖 7 个分类 |
| 分类 | 7 | 动作/RPG/策略/冒险/模拟/独立/体育 |
| 评测 | ~67 | 状态分布：published / draft / manual_review / rejected |
| 评论 | 多条 | 游戏短评 + 评测评论（含楼中楼回复） |
| 评分 | 多条 | 用户对游戏的 1-10 分评分（玩家 id=3 / 创作者 id=2 等有预置评分） |
| 社区 | 多条 | 帖子 + 评论 + 点赞 + 收藏 |

种子初始化流程：`init_db()` → `seed_if_empty()` → 写入种子数据 → `recalc_game_scores()` 聚合评分 → 按积分规则计算创作者等级 + 积分流水

---

## 八、项目文件结构

```
├── main.py                        # FastAPI 入口（非 app/main.py）
├── start-platform.bat             # 一键启动脚本
├── .env                           # 环境变量配置
├── requirements.txt               # Python 依赖
├── app/
│   ├── models.py                  # 数据模型（15+ 表）
│   ├── schemas.py                 # 请求/响应 Schema
│   ├── services.py                # 业务逻辑层
│   ├── repositories.py            # 数据访问层
│   ├── ai_client.py               # AI 模块（Ollama + DeepSeek + 规则引擎）
│   ├── notify.py                  # 消息通知推送
│   ├── core/
│   │   ├── config.py              # 全局配置（Ollama/DeepSeek/JWT/DB）
│   │   ├── deps.py                # 依赖注入（认证/数据库会话）
│   │   └── points.py              # 积分规则常量
│   ├── routers/
│   │   ├── auth.py                # /api/auth
│   │   ├── users.py               # /api/users
│   │   ├── games.py               # /api/games
│   │   ├── comments.py            # /api/comments
│   │   ├── reviews.py             # /api/reviews
│   │   ├── community.py           # /api/community
│   │   ├── creator.py             # /api/creator
│   │   ├── ai.py                  # /api/ai
│   │   ├── notifications.py       # /api/notifications
│   │   ├── favorites.py           # /api/favorites
│   │   ├── play_records.py        # /api/play_records
│   │   └── admin.py               # /api/admin
│   └── db/
│       ├── base.py                # SessionLocal / get_db
│       └── init_db.py             # 种子数据初始化
├── static/
│   ├── css/style.css              # 全站样式（proto12）
│   ├── js/
│   │   ├── api.js                 # 请求层 + 多账号会话管理
│   │   ├── common.js              # 工具函数 + U.goBack
│   │   ├── auth.js                # 会话/导航/权限/铃铛轮询
│   │   └── mock.js                # Mock 数据层（离线可用）
│   ├── index.html                 # 首页
│   ├── game-list.html             # 游戏库
│   ├── game-detail.html           # 游戏详情
│   ├── review-list.html           # 评测列表
│   ├── review-detail.html         # 评测详情
│   ├── community.html             # 社区
│   ├── community-post.html         # 帖子详情
│   ├── community-new.html         # 发帖
│   ├── creator-work.html          # 创作者工作台
│   ├── creator-edit.html          # 评测编辑
│   ├── my-profile.html            # 个人中心
│   ├── messages.html              # 消息中心
│   ├── login.html                 # 登录（支持 add=1 追加账号）
│   ├── register.html              # 注册
│   ├── presentation.html          # 项目介绍 PPT
│   └── admin/
│       ├── index.html             # 仪表盘
│       ├── user.html              # 用户与申请管理
│       ├── audit-queue.html       # 审核队列
│       ├── game-manage.html       # 游戏管理
│       ├── comments.html          # 评论管理
│       └── community.html         # 社区管理
└── docs/
    └── PRD_GameReview_AI.md       # 本文档
```

---

## 九、环境配置

### 9.1 .env 文件
```env
DATABASE_URL=sqlite:///./data/game_community.db
JWT_SECRET_KEY=game-community-dev-secret-change-me
JWT_EXPIRE_DAYS=7
DEEPSEEK_API_KEY=              # 留空则不启用云端 AI
DEEPSEEK_BASE_URL=https://api.deepseek.com
# 以下通过 config.py 默认值，也可在 .env 中覆盖
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen2.5:3b
# OLLAMA_ENABLED=1
```

### 9.2 Python 依赖
```
fastapi>=0.110
uvicorn[standard]>=0.27
SQLAlchemy>=1.4,<2.0
pymysql>=1.1
python-jose[cryptography]>=3.3
bcrypt>=4.0
httpx>=0.27
python-dotenv>=1.0
bleach>=6.0
pytest>=8.0
```

### 9.3 Ollama 安装与模型拉取
```bash
# 安装 Ollama（参考 ollama.com）
# 拉取轻量中文模型
ollama pull qwen2.5:3b
# 验证服务
curl http://localhost:11434/api/tags
```

---

## 十、迭代记录

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| v0.1 | 2026-09-07 | 基础平台搭建（游戏库/评测/社区/认证） |
| v0.2 | 2026-09-07 | UI 改版暗色琥珀金主题（黑神话原型基准） |
| v0.3 | 2026-09-07 | AI 对话（Ollama qwen2.5:3b + DeepSeek 备选 + 规则引擎兜底）+ 实时数据快照 |
| v0.4 | 2026-09-07 | 消息通知系统（全埋点 + 10 秒轮询 + 消息中心） |
| v0.5 | 2026-09-07 | 评测分页 + 状态分类标签 |
| v0.6 | 2026-09-07 | 智能返回 + 多账号登录 + 消息跳转 |
| v1.0 | 2026-09-07 | 评论回复/删除 + 个人中心跳转锚点 + PRD 反向梳理（当前版本） |
