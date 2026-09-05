-- ============================================================
-- AI 游戏社区评测分享平台 — MySQL 数据库初始化脚本
-- 阶段4 产物 · 10 张表 + 索引 + 外键 + 种子数据
-- 游戏数据均为真实存在的 Steam 游戏
-- ============================================================

-- 建库
DROP DATABASE IF EXISTS game_community;
CREATE DATABASE game_community DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE game_community;

-- ============================================================
-- 1. 用户表
-- ============================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id          BIGINT       NOT NULL AUTO_INCREMENT,
  username    VARCHAR(50)  NOT NULL,
  email       VARCHAR(100) NOT NULL,
  password    VARCHAR(255) NOT NULL COMMENT 'bcrypt 哈希存储',
  role        ENUM('player','creator','admin') NOT NULL DEFAULT 'player',
  is_active   TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '0=封禁 1=正常',
  nickname    VARCHAR(50)  DEFAULT NULL,
  avatar      VARCHAR(500) DEFAULT NULL,
  bio         TEXT         DEFAULT NULL,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  UNIQUE KEY uk_email (email)
) ENGINE=InnoDB COMMENT='用户表';

-- ============================================================
-- 2. 游戏分类表
-- ============================================================
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
  id          INT          NOT NULL AUTO_INCREMENT,
  name        VARCHAR(50)  NOT NULL,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_cat_name (name)
) ENGINE=InnoDB COMMENT='游戏分类表';

-- ============================================================
-- 3. 游戏表
-- ============================================================
DROP TABLE IF EXISTS games;
CREATE TABLE games (
  id            BIGINT       NOT NULL AUTO_INCREMENT,
  name          VARCHAR(100) NOT NULL,
  name_en       VARCHAR(100) DEFAULT NULL,
  developer     VARCHAR(100) DEFAULT NULL,
  cover_url     VARCHAR(500) DEFAULT NULL,
  description   TEXT         DEFAULT NULL,
  release_date  DATE         DEFAULT NULL,
  category_id   INT          NOT NULL,
  average_score DECIMAL(3,1) NOT NULL DEFAULT 0.0,
  is_online     TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '0=下架 1=上架',
  hot           INT          NOT NULL DEFAULT 0 COMMENT '热度值',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_category (category_id),
  KEY idx_online (is_online),
  KEY idx_release (release_date),
  KEY idx_hot (hot),
  CONSTRAINT fk_game_category FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB COMMENT='游戏表';

-- ============================================================
-- 4. 游戏标签表（多对多）
-- ============================================================
DROP TABLE IF EXISTS game_tags;
CREATE TABLE game_tags (
  id       BIGINT      NOT NULL AUTO_INCREMENT,
  game_id  BIGINT      NOT NULL,
  tag      VARCHAR(50) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_game_tag (game_id, tag),
  KEY idx_tag (tag),
  CONSTRAINT fk_gt_game FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='游戏标签表';

-- ============================================================
-- 5. 评测/攻略表
-- ============================================================
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
  id            BIGINT      NOT NULL AUTO_INCREMENT,
  game_id       BIGINT      NOT NULL,
  user_id       BIGINT      NOT NULL,
  title         VARCHAR(200) NOT NULL,
  content       LONGTEXT    DEFAULT NULL COMMENT '富文本 HTML',
  status        ENUM('draft','audit','manual_review','published','rejected') NOT NULL DEFAULT 'draft',
  audit_status  ENUM('passed','manual_review','rejected') DEFAULT NULL,
  audit_score   INT         DEFAULT NULL COMMENT 'AI 风险分 0-100',
  audit_reason  TEXT        DEFAULT NULL COMMENT '审核原因/驳回理由',
  read_count    INT         NOT NULL DEFAULT 0,
  like_count    INT         NOT NULL DEFAULT 0,
  fav_count     INT         NOT NULL DEFAULT 0,
  created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_review_game (game_id),
  KEY idx_review_user (user_id),
  KEY idx_review_status (status),
  KEY idx_review_created (created_at),
  CONSTRAINT fk_rev_game FOREIGN KEY (game_id) REFERENCES games(id),
  CONSTRAINT fk_rev_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='评测攻略表';

-- ============================================================
-- 6. 评测标签表
-- ============================================================
DROP TABLE IF EXISTS review_tags;
CREATE TABLE review_tags (
  id         BIGINT      NOT NULL AUTO_INCREMENT,
  review_id  BIGINT      NOT NULL,
  tag        VARCHAR(50) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_review_tag (review_id, tag),
  CONSTRAINT fk_rt_review FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='评测标签表';

-- ============================================================
-- 7. 评论表（支持嵌套回复）
-- ============================================================
DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
  id           BIGINT      NOT NULL AUTO_INCREMENT,
  user_id      BIGINT      NOT NULL,
  target_type  ENUM('review') NOT NULL DEFAULT 'review',
  target_id    BIGINT      NOT NULL COMMENT '评测 ID',
  parent_id    BIGINT      DEFAULT NULL COMMENT '父评论 ID（NULL=顶级评论）',
  content      TEXT        NOT NULL,
  like_count   INT         NOT NULL DEFAULT 0,
  created_at   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_comment_target (target_type, target_id),
  KEY idx_comment_user (user_id),
  KEY idx_comment_parent (parent_id),
  CONSTRAINT fk_cmt_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_cmt_parent FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='评论表';

-- ============================================================
-- 8. 评论点赞表
-- ============================================================
DROP TABLE IF EXISTS comment_likes;
CREATE TABLE comment_likes (
  id          BIGINT NOT NULL AUTO_INCREMENT,
  comment_id  BIGINT NOT NULL,
  user_id     BIGINT NOT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_cmt_like (comment_id, user_id),
  CONSTRAINT fk_cl_comment FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
  CONSTRAINT fk_cl_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='评论点赞表';

-- ============================================================
-- 9. 游戏收藏表
-- ============================================================
DROP TABLE IF EXISTS favorites;
CREATE TABLE favorites (
  id          BIGINT NOT NULL AUTO_INCREMENT,
  user_id     BIGINT NOT NULL,
  game_id     BIGINT NOT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_fav (user_id, game_id),
  KEY idx_fav_user (user_id),
  CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_fav_game FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='游戏收藏表';

-- ============================================================
-- 10. 游玩记录表
-- ============================================================
DROP TABLE IF EXISTS play_records;
CREATE TABLE play_records (
  id           BIGINT NOT NULL AUTO_INCREMENT,
  user_id      BIGINT NOT NULL,
  game_id      BIGINT NOT NULL,
  play_status  ENUM('want','playing','completed') NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_play (user_id, game_id),
  KEY idx_play_user (user_id),
  CONSTRAINT fk_play_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_play_game FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='游玩记录表';

-- ============================================================
-- 11. 创作者申请表
-- ============================================================
DROP TABLE IF EXISTS creator_applications;
CREATE TABLE creator_applications (
  id            BIGINT NOT NULL AUTO_INCREMENT,
  user_id       BIGINT NOT NULL,
  apply_reason  TEXT NOT NULL,
  status        ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  audit_user_id BIGINT DEFAULT NULL COMMENT '审核管理员 ID',
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_apply_user (user_id),
  KEY idx_apply_status (status),
  CONSTRAINT fk_apply_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='创作者申请表';

-- ============================================================
-- 12. 审核日志表
-- ============================================================
DROP TABLE IF EXISTS audit_logs;
CREATE TABLE audit_logs (
  id            BIGINT NOT NULL AUTO_INCREMENT,
  review_id     BIGINT NOT NULL,
  audit_type    ENUM('ai','manual') NOT NULL,
  risk_score    INT DEFAULT NULL COMMENT 'AI 风险分 0-100',
  reason        TEXT DEFAULT NULL,
  operator_id   BIGINT DEFAULT NULL COMMENT '操作人（1=system）',
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_log_review (review_id),
  CONSTRAINT fk_log_review FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='审核日志表';

-- ============================================================
-- 种子数据
-- ============================================================

-- 分类
INSERT INTO categories (id, name) VALUES
(1,'角色扮演 RPG'),(2,'射击 FPS'),(3,'动作 ACT'),(4,'开放世界'),
(5,'模拟经营 SIM'),(6,'策略 SLG'),(7,'竞速 RAC');

-- 用户（密码为明文占位，后端用 bcrypt 哈希后替换）
INSERT INTO users (id, username, email, password, role, is_active, nickname, bio, created_at) VALUES
(1,'admin','admin@game.local','$2b$12$placeholder_admin_hash','admin',1,'平台管理员','游戏社区官方管理员账号', DATE_SUB(NOW(), INTERVAL 900 DAY)),
(2,'creator','creator@game.local','$2b$12$placeholder_creator_hash','creator',1,'硬核评测君','十年游戏龄，只写有态度的评测。', DATE_SUB(NOW(), INTERVAL 800 DAY)),
(3,'player','player@game.local','$2b$12$placeholder_player_hash','player',1,'休闲玩家小P','周末打游戏的社畜一枚', DATE_SUB(NOW(), INTERVAL 700 DAY)),
(4,'player02','p02@game.local','$2b$12$placeholder_p02_hash','player',1,'夜行者','单机剧情党', DATE_SUB(NOW(), INTERVAL 300 DAY)),
(5,'writer_lily','lily@game.local','$2b$12$placeholder_lily_hash','creator',1,'莉莉的游戏簿','偏爱独立游戏与叙事作品', DATE_SUB(NOW(), INTERVAL 260 DAY)),
(6,'bad_guy','bad@game.local','$2b$12$placeholder_bad_hash','player',0,'引战小号','', DATE_SUB(NOW(), INTERVAL 120 DAY)),
(7,'new_man','new@game.local','$2b$12$placeholder_new_hash','player',1,'萌新','', DATE_SUB(NOW(), INTERVAL 10 DAY));

-- 游戏（12 款真实 Steam 游戏，封面图占位由后端/前端生成）
INSERT INTO games (id, name, name_en, developer, cover_url, description, release_date, category_id, average_score, is_online, hot, created_at) VALUES
(1,'艾尔登法环','Elden Ring','FromSoftware','','由 FromSoftware 与乔治·R·R·马丁联手打造的开放世界魂系动作 RPG。玩家作为褪色者踏入广袤的交界地，探索六大区域、挑战强敌、收集卢恩，最终成为艾尔登之王。','2022-02-25',4,9.6,1,98, DATE_SUB(NOW(), INTERVAL 400 DAY)),
(2,'博德之门 3','Baldur''s Gate 3','Larian Studios','','拉瑞安工作室出品的 CRPG 巅峰之作，基于龙与地下城 D&D 5e 规则。你的大脑被植入了夺心魔蝌蚪，一场改变费伦大陆命运的冒险由此展开。','2023-08-03',1,9.7,1,95, DATE_SUB(NOW(), INTERVAL 380 DAY)),
(3,'黑神话：悟空','Black Myth: Wukong','游戏科学 Game Science','','游戏科学开发的国产 3A 动作角色扮演游戏。扮演天命人，踏上充满凶险与惊奇的西游路，与各路妖王殊死一战。','2024-08-20',3,9.3,1,99, DATE_SUB(NOW(), INTERVAL 300 DAY)),
(4,'赛博朋克 2077','Cyberpunk 2077','CD Projekt Red','','CD Projekt Red 出品的开放世界动作 RPG。在夜之城这座权力、魅力和义体改造交织的都市里，扮演雇佣兵 V，追寻一种永生不朽的独特植入体。','2020-12-10',4,8.5,1,90, DATE_SUB(NOW(), INTERVAL 500 DAY)),
(5,'荒野大镖客：救赎 2','Red Dead Redemption 2','Rockstar Games','','R 星打造的西部题材开放世界史诗。1899 年的美国，亡命之徒亚瑟·摩根随范德林德帮在时代的终结中挣扎求生。','2018-10-26',4,9.5,1,87, DATE_SUB(NOW(), INTERVAL 600 DAY)),
(6,'巫师 3：狂猎','The Witcher 3: Wild Hunt','CD Projekt Red','','利维亚的杰洛特，一名职业猎魔人，在战火纷飞的大陆上寻找预言之子希里。CDPR 凭借本作一举封神。','2015-05-19',1,9.4,1,88, DATE_SUB(NOW(), INTERVAL 700 DAY)),
(7,'反恐精英 2','Counter-Strike 2','Valve','','Valve 基于起源 2 引擎打造的 CS 系列续作，免费开玩。升级的烟雾弹物理、亚秒级服务器与全新画质。','2023-09-27',2,8.0,1,96, DATE_SUB(NOW(), INTERVAL 360 DAY)),
(8,'哈迪斯','Hades','Supergiant Games','','Supergiant 出品的高口碑 Roguelike。扮演冥界王子扎格列欧斯，在每次死亡都重来的逃亡中杀出冥界。','2020-09-17',3,9.2,1,80, DATE_SUB(NOW(), INTERVAL 450 DAY)),
(9,'星露谷物语','Stardew Valley','ConcernedApe','','一个人历时四年半开发的田园模拟神作。继承爷爷的农场，种地、养殖、钓鱼、挖矿、与村民恋爱结婚。','2016-02-27',5,9.5,1,85, DATE_SUB(NOW(), INTERVAL 800 DAY)),
(10,'文明 6','Sid Meier''s Civilization VI','Firaxis Games','','席德·梅尔的传奇 4X 策略系列。从石器时代到信息时代，建立帝国、发展科技、外交博弈或征服世界。','2016-10-21',6,8.3,1,75, DATE_SUB(NOW(), INTERVAL 750 DAY)),
(11,'极限竞速：地平线 5','Forza Horizon 5','Playground Games','','地平线系列登陆墨西哥。数百辆授权座驾、世界顶级的驾驶手感、随季节变换的开放世界。','2021-11-09',7,9.0,1,78, DATE_SUB(NOW(), INTERVAL 420 DAY)),
(12,'空洞骑士','Hollow Knight','Team Cherry','','澳大利亚三人团队打造的银河恶魔城神作。深入衰败的圣巢，探索 interconnected 的地下王国，挑战硬核 Boss 战。','2017-02-25',3,9.4,1,82, DATE_SUB(NOW(), INTERVAL 650 DAY));

-- 游戏标签
INSERT INTO game_tags (game_id, tag) VALUES
(1,'魂系'),(1,'黑暗幻想'),(1,'开放世界'),(1,'动作RPG'),
(2,'回合制'),(2,'剧情丰富'),(2,'奇幻'),(2,'合作'),
(3,'神话'),(3,'动作RPG'),(3,'单机'),(3,'国风'),
(4,'赛博朋克'),(4,'科幻'),(4,'开放世界'),(4,'剧情丰富'),
(5,'西部'),(5,'剧情丰富'),(5,'开放世界'),(5,'写实'),
(6,'奇幻'),(6,'开放世界'),(6,'剧情丰富'),(6,'选择取向'),
(7,'竞技'),(7,'多人'),(7,'FPS'),(7,'电竞'),
(8,'Roguelike'),(8,'希腊神话'),(8,'独立'),(8,'动作'),
(9,'像素'),(9,'农场'),(9,'休闲'),(9,'联机'),
(10,'回合制'),(10,'历史'),(10,'4X'),(10,'建设'),
(11,'赛车'),(11,'开放世界'),(11,'多人'),(11,'写实'),
(12,'银河恶魔城'),(12,'独立'),(12,'手绘'),(12,'困难');

-- 评测
INSERT INTO reviews (id, game_id, user_id, title, content, status, audit_status, audit_score, audit_reason, read_count, like_count, fav_count, created_at) VALUES
(1,1,2,'《艾尔登法环》深度评测：开放世界与魂系的完美融合','<h2>总评：9.6 分，年度最佳实至名归</h2><p>当 FromSoftware 决定做开放世界，所有人都担心魂系的精雕细琢会被稀释。事实证明，交界地的每一寸土地都藏着惊喜。</p><h2>一、开放世界的新范式</h2><p>没有问号轰炸地图，没有公式化据点。你远远看到一座破屋，走近可能是一段支线；探索的驱动力完全来自好奇心本身。</p>','published','passed',8,'',12350,866,412, DATE_SUB(NOW(), INTERVAL 120 DAY)),
(2,2,5,'《博德之门3》：CRPG 的新黄金标准','<h2>总评：9.7 分</h2><p>拉瑞安用 5e 规则证明了一件事：回合制可以比动作游戏更爽快。第一章的林地攻防战就足以让大多数 RPG 黯然失色。</p>','published','passed',5,'',9820,743,356, DATE_SUB(NOW(), INTERVAL 90 DAY)),
(3,3,2,'《黑神话：悟空》通关评测：国产 3A 的里程碑','<h2>总评：9.3 分</h2><p>天命人走出花果山的那一刻，中国玩家等了很多年。</p><p>战斗系统上，劈棍、立棍、戳棍三架势切换流畅。美术更是无可争议的世界级。</p>','published','passed',6,'',28600,2100,980, DATE_SUB(NOW(), INTERVAL 60 DAY)),
(4,8,5,'《哈迪斯》评测：死了一千次还想再来一把','<h2>总评：9.2 分</h2><p>Roguelike 最爽的节奏被 Supergiant 彻底摸透。15 分钟一局，每局都有新 Build。</p>','published','passed',3,'',6420,521,230, DATE_SUB(NOW(), INTERVAL 80 DAY)),
(5,9,2,'《星露谷物语》：治愈一切的像素田园','<h2>总评：9.5 分</h2><p>春种秋收，养鸡钓鱼，和镇民聊天跳舞。星露谷的厉害之处在于它没有目标。</p>','published','passed',2,'',5310,467,310, DATE_SUB(NOW(), INTERVAL 70 DAY)),
(6,12,5,'《空洞骑士》：圣巢之下，皆是悲歌','<h2>总评：9.4 分</h2><p>手绘的虫子王国里，每一个 NPC 都有令人心碎的故事。</p>','published','passed',4,'',7240,689,401, DATE_SUB(NOW(), INTERVAL 55 DAY)),
(7,4,2,'《赛博朋克2077》：夜之城漫步指南','<h2>从口碑崩盘到涅槃重生</h2><p>2.0 更新与往日之影 DLC 之后，夜之城终于兑现了最初的承诺。</p>','manual_review','manual_review',62,'疑似引战争议表述，需人工复核',0,0,0, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(8,7,2,'CS2 新手必看！加群领皮肤攻略','<p>新手玩家快来，加群 xxx-xxx-xxx 免费领皮肤，还有代购打折游戏！</p>','rejected','rejected',92,'AI 审核驳回：检测到广告引流内容',0,0,0, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(9,6,2,'《巫师3》二周目：猎魔人的自我修养（草稿）','<h2>二周目才懂的细节</h2><p>（草稿，未完待续…）</p>','draft',NULL,NULL,'',0,0,0, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(10,5,5,'《大镖客2》细节考据：R星的西部有多真实','<p>亚瑟的胡子会生长、马会受惊、路过的NPC会记住你……这篇图文整理了 30 个令人发指的细节。</p>','published','passed',7,'',8900,712,388, DATE_SUB(NOW(), INTERVAL 45 DAY));

-- 评测标签
INSERT INTO review_tags (review_id, tag) VALUES
(1,'魂系'),(1,'年度游戏'),
(2,'CRPG'),(2,'剧情'),
(3,'国产'),(3,'3A'),
(4,'Roguelike'),(4,'独立游戏'),
(5,'治愈'),(5,'模拟'),
(6,'银河恶魔城'),(6,'独立游戏'),
(7,'赛博朋克'),(7,'开放世界'),
(10,'考据'),(10,'开放世界');

-- 评论
INSERT INTO comments (id, user_id, target_type, target_id, parent_id, content, like_count, created_at) VALUES
(1,3,'review',1,NULL,'碎星那一战我打了整整一下午，过的时候手都在抖！',45, DATE_SUB(NOW(), INTERVAL 119 DAY)),
(2,4,'review',1,1,'同感！拉塔恩的 BGM 一响直接头皮发麻',12, DATE_SUB(NOW(), INTERVAL 118 DAY)),
(3,7,'review',1,NULL,'请问新手适合玩法师还是近战呀？',3, DATE_SUB(NOW(), INTERVAL 110 DAY)),
(4,2,'review',1,3,'新手强烈推荐观星者，远程法术容错率高~',20, DATE_SUB(NOW(), INTERVAL 109 DAY)),
(5,3,'review',3,NULL,'黑神话首发日我请假在家玩了一整天，值了！',88, DATE_SUB(NOW(), INTERVAL 59 DAY)),
(6,4,'review',2,NULL,'影心是我老婆，不接受反驳。',34, DATE_SUB(NOW(), INTERVAL 88 DAY));

-- 评论点赞（comment_likes 6→user3, 1→user4 等）
INSERT INTO comment_likes (comment_id, user_id) VALUES
(1,4),(1,2),(1,7),
(2,3),(2,2),
(4,3),(4,7),
(5,2),(5,4),(5,7),
(6,3),(6,2);

-- 收藏
INSERT INTO favorites (user_id, game_id, created_at) VALUES
(3,1, DATE_SUB(NOW(), INTERVAL 200 DAY)),
(3,2, DATE_SUB(NOW(), INTERVAL 150 DAY)),
(3,3, DATE_SUB(NOW(), INTERVAL 59 DAY)),
(2,6, DATE_SUB(NOW(), INTERVAL 300 DAY));

-- 游玩记录
INSERT INTO play_records (user_id, game_id, play_status, created_at, updated_at) VALUES
(3,6,'completed', DATE_SUB(NOW(), INTERVAL 180 DAY), DATE_SUB(NOW(), INTERVAL 100 DAY)),
(3,8,'playing', DATE_SUB(NOW(), INTERVAL 90 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3,9,'want', DATE_SUB(NOW(), INTERVAL 30 DAY), DATE_SUB(NOW(), INTERVAL 30 DAY));

-- 创作者申请
INSERT INTO creator_applications (id, user_id, apply_reason, status, audit_user_id, created_at) VALUES
(1,7,'我是游戏媒体撰稿人，想在平台发布 Steam 游戏评测，之前运营过个人游戏公众号。','pending',NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(2,4,'单机游戏通关 200+，想写点东西分享。','pending',NULL, DATE_SUB(NOW(), INTERVAL 1 DAY));

-- 审核日志
INSERT INTO audit_logs (review_id, audit_type, risk_score, reason, operator_id, created_at) VALUES
(8,'ai',92,'命中广告引流：检测到"加群""微信 vx"等联系方式导流片段',1, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(7,'ai',62,'疑似引战争议表述："某游戏就是垃圾"类对比引战，需人工判断',1, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(3,'ai',6,'内容正常，未命中风险维度',1, DATE_SUB(NOW(), INTERVAL 60 DAY));

-- ============================================================
-- 视图：游戏列表（含分类名）
-- ============================================================
CREATE OR REPLACE VIEW v_game_list AS
SELECT g.*, c.name AS category_name
FROM games g
JOIN categories c ON g.category_id = c.id;

-- 视图：评测列表（含作者名和游戏名）
CREATE OR REPLACE VIEW v_review_list AS
SELECT r.*,
       u.username    AS author_name,
       u.nickname    AS author_nickname,
       u.avatar      AS author_avatar,
       g.name        AS game_name,
       g.cover_url   AS game_cover
FROM reviews r
JOIN users u ON r.user_id = u.id
JOIN games g ON r.game_id = g.id;

-- ============================================================
-- 重置自增起始值
-- ============================================================
ALTER TABLE users AUTO_INCREMENT = 100;
ALTER TABLE games AUTO_INCREMENT = 100;
ALTER TABLE reviews AUTO_INCREMENT = 100;
ALTER TABLE comments AUTO_INCREMENT = 100;
