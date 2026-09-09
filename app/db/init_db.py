"""数据库初始化：建表 + 种子数据。

种子数据与前端 mock.js / database/script.sql 保持一致，保证前端切换到真实后端后数据一致。
密码用 bcrypt 哈希后写入（admin/admin123、creator/creator123、player/player123）。
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.core.security import hash_password
from app.db.base import Base, engine, SessionLocal
from app.models import (
    AuditLog,
    Category,
    Comment,
    CommentLike,
    CommunityPost,
    CreatorApplication,
    Favorite,
    Game,
    GameRating,
    GameTag,
    PlayRecord,
    PostComment,
    PostCommentLike,
    PostFavorite,
    PostLike,
    Report,
    Review,
    ReviewTag,
    PointRecord,
    User,
)


def init_db() -> None:
    """建表。"""
    Base.metadata.create_all(bind=engine)


def seed_if_empty() -> None:
    """若 users 表为空，写入种子数据。"""
    db = SessionLocal()
    try:
        if db.query(User).first() is not None:
            return
        _seed(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _seed(db) -> None:
    now = datetime.utcnow()

    def d(days_ago: int) -> datetime:
        return now - timedelta(days=days_ago)

    # ---- 分类 ----
    cats = [
        ("角色扮演 RPG",), ("射击 FPS",), ("动作 ACT",), ("开放世界",),
        ("模拟经营 SIM",), ("策略 SLG",), ("竞速 RAC",),
    ]
    cat_objs = []
    for i, (name,) in enumerate(cats, start=1):
        c = Category(id=i, name=name, created_at=now)
        cat_objs.append(c)
        db.add(c)

    # ---- 用户 ----
    users_seed = [
        (1, "admin", "admin@game.local", "admin123", "admin", True, "平台管理员", "游戏社区官方管理员账号", 900),
        (2, "creator", "creator@game.local", "creator123", "creator", True, "硬核评测君", "十年游戏龄，只写有态度的评测。", 800),
        (3, "player", "player@game.local", "player123", "player", True, "休闲玩家小P", "周末打游戏的社畜一枚", 700),
        (4, "player02", "p02@game.local", "123456", "player", True, "夜行者", "单机剧情党", 300),
        (5, "writer_lily", "lily@game.local", "123456", "creator", True, "莉莉的游戏簿", "偏爱独立游戏与叙事作品", 260),
        (6, "bad_guy", "bad@game.local", "123456", "player", False, "引战小号", "", 120),
        (7, "new_man", "new@game.local", "123456", "player", True, "萌新", "", 10),
    ]
    user_objs = []
    for uid, uname, email, pwd, role, active, nick, bio, days in users_seed:
        u = User(
            id=uid, username=uname, email=email, password=hash_password(pwd),
            role=role, is_active=active, nickname=nick, avatar="", bio=bio,
            created_at=d(days), updated_at=d(days),
        )
        user_objs.append(u)
        db.add(u)

    # ---- 游戏 ----
    # 元组第 5 位为 Steam AppID，封面直接使用 Steam 商店官方 header 图（CDN）
    games_seed = [
        (1, "艾尔登法环", "Elden Ring", "FromSoftware", 1245620,
         "由 FromSoftware 与乔治·R·R·马丁联手打造的开放世界魂系动作 RPG。玩家作为褪色者踏入广袤的交界地，探索六大区域、挑战强敌、收集卢恩，最终成为艾尔登之王。",
         "2022-02-25", 4, 9.6, True, 98, 400,
         ["魂系", "黑暗幻想", "开放世界", "动作RPG"]),
        (2, "博德之门 3", "Baldur's Gate 3", "Larian Studios", 1086940,
         "拉瑞安工作室出品的 CRPG 巅峰之作，基于龙与地下城 D&D 5e 规则。你的大脑被植入了夺心魔蝌蚪，一场改变费伦大陆命运的冒险由此展开，选择将真正改变世界。",
         "2023-08-03", 1, 9.7, True, 95, 380,
         ["回合制", "剧情丰富", "奇幻", "合作"]),
        (3, "黑神话：悟空", "Black Myth: Wukong", "游戏科学 Game Science", 2358720,
         "游戏科学开发的国产 3A 动作角色扮演游戏。扮演天命人，踏上充满凶险与惊奇的西游路，与各路妖王殊死一战。每一步都踏足四大部州的神话山河。",
         "2024-08-20", 3, 9.3, True, 99, 300,
         ["神话", "动作RPG", "单机", "国风"]),
        (4, "赛博朋克 2077", "Cyberpunk 2077", "CD Projekt Red", 1091500,
         "CD Projekt Red 出品的开放世界动作 RPG。在夜之城这座权力、魅力和义体改造交织的都市里，扮演雇佣兵 V，追寻一种永生不朽的独特植入体。历经多次更新后口碑全面逆袭。",
         "2020-12-10", 4, 8.5, True, 90, 500,
         ["赛博朋克", "科幻", "开放世界", "剧情丰富"]),
        (5, "荒野大镖客：救赎 2", "Red Dead Redemption 2", "Rockstar Games", 1174180,
         "R 星打造的西部题材开放世界史诗。1899 年的美国，亡命之徒亚瑟·摩根随范德林德帮在时代的终结中挣扎求生。一个关于忠诚、理想与消逝的西部故事。",
         "2018-10-26", 4, 9.5, True, 87, 600,
         ["西部", "剧情丰富", "开放世界", "写实"]),
        (6, "巫师 3：狂猎", "The Witcher 3: Wild Hunt", "CD Projekt Red", 292030,
         "利维亚的杰洛特，一名职业猎魔人，在战火纷飞的大陆上寻找预言之子希里。CDPR 凭借本作一举封神，次世代更新后画面焕然新生。",
         "2015-05-19", 1, 9.4, True, 88, 700,
         ["奇幻", "开放世界", "剧情丰富", "选择取向"]),
        (7, "反恐精英 2", "Counter-Strike 2", "Valve", 730,
         "Valve 基于起源 2 引擎打造的 CS 系列续作，免费开玩。升级的烟雾弹物理、亚秒级服务器与全新画质，让全球最流行的竞技射击焕然升级。",
         "2023-09-27", 2, 8.0, True, 96, 360,
         ["竞技", "多人", "FPS", "电竞"]),
        (8, "哈迪斯", "Hades", "Supergiant Games", 1145360,
         "Supergiant 出品的高口碑 Roguelike。扮演冥界王子扎格列欧斯，在每次死亡都重来的逃亡中杀出冥界。流畅的战斗、丰富的 Build 与全程配音的希腊诸神，让人死了一千次还想再来一把。",
         "2020-09-17", 3, 9.2, True, 80, 450,
         ["Roguelike", "希腊神话", "独立", "动作"]),
        (9, "星露谷物语", "Stardew Valley", "ConcernedApe", 413150,
         "一个人历时四年半开发的田园模拟神作。继承爷爷的农场，种地、养殖、钓鱼、挖矿、与村民恋爱结婚。支持多人联机，是无数玩家的电子止痛药。",
         "2016-02-27", 5, 9.5, True, 85, 800,
         ["像素", "农场", "休闲", "联机"]),
        (10, "文明 6", "Sid Meier’s Civilization VI", "Firaxis Games", 289070,
         "席德·梅尔的传奇 4X 策略系列。从石器时代到信息时代，建立帝国、发展科技、外交博弈或征服世界。再来一回合就睡觉——然后天就亮了。",
         "2016-10-21", 6, 8.3, True, 75, 750,
         ["回合制", "历史", "4X", "建设"]),
        (11, "极限竞速：地平线 5", "Forza Horizon 5", "Playground Games", 1551360,
         "地平线系列登陆墨西哥。数百辆授权座驾、世界顶级的驾驶手感、随季节变换的开放世界，无论是竞速老炮还是观光休闲玩家都能找到乐趣。",
         "2021-11-09", 7, 9.0, True, 78, 420,
         ["赛车", "开放世界", "多人", "写实"]),
        (12, "空洞骑士", "Hollow Knight", "Team Cherry", 367520,
         "澳大利亚三人团队打造的银河恶魔城神作。深入衰败的圣巢，探索 interconnected 的地下王国，挑战硬核 Boss 战。手绘美术、凄美配乐与庞大的世界等待着你。",
         "2017-02-25", 3, 9.4, True, 82, 650,
         ["银河恶魔城", "独立", "手绘", "困难"]),
        # ---- 13-30：追加的真实 Steam 游戏 ----
        (13, "绝地求生", "PUBG: BATTLEGROUNDS", "KRAFTON", 578080,
         "KRAFTON 出品的现象级大逃杀游戏。100 名玩家空降至荒岛，搜集装备、在不断缩小的安全区中厮杀，最后一人（队）获胜。它定义了一个品类，曾长期占据 Steam 同时在线榜首。",
         "2017-12-21", 2, 8.2, True, 92, 340,
         ["大逃杀", "多人", "FPS", "射击"]),
        (14, "Apex 英雄", "Apex Legends", "Respawn Entertainment", 1172470,
         "Respawn 打造的免费英雄射击大逃杀。拥有独特技能的「传奇」三人组队，在世界边缘等地图高速交战。流畅的移动手感、智能标记系统与团队协作，是大逃杀品类的革新者。",
         "2020-11-05", 2, 8.5, True, 89, 280,
         ["大逃杀", "英雄射击", "多人", "FPS"]),
        (15, "毁灭战士：永恒", "DOOM Eternal", "id Software", 782330,
         "id Software 的纯粹暴力美学 FPS。扮演毁灭战士在地狱大军中撕开血路，荣耀击杀、电锯处决与重金属配乐让每场战斗都肾上腺素飙升，是单人射击关卡设计的教科书。",
         "2020-03-20", 2, 9.0, True, 76, 310,
         ["FPS", "快节奏", "血腥", "单人"]),
        (16, "上古卷轴 5：天际 特别版", "The Elder Scrolls V: Skyrim Special Edition", "Bethesda Game Studios", 489830,
         "Bethesda 的开放世界奇幻 RPG 传奇。龙裔在天际省对抗世界吞噬者奥杜因，四大公会、数十条支线与数不清的地牢。「我以前也是个冒险者，直到我膝盖中了一箭」。",
         "2016-10-28", 1, 9.3, True, 84, 500,
         ["奇幻", "开放世界", "RPG", "龙"]),
        (17, "辐射 4", "Fallout 4", "Bethesda Game Studios", 377160,
         "核战后的废土波士顿，你是 111 号避难所唯一的幸存者，踏上寻找失踪儿子的旅程。动力装甲、据点建设、V.A.T.S. 慢动作射击与黑色幽默，构成最经典的后末日 RPG。",
         "2015-11-10", 1, 8.0, True, 72, 480,
         ["后末日", "开放世界", "RPG", "剧情丰富"]),
        (18, "质量效应：传奇版", "Mass Effect Legendary Edition", "BioWare", 1328670,
         "BioWare 太空歌剧三部曲的高清合集。薛帕德指挥官率诺曼底号船员跨星系对抗收割者、拯救银河系，你的决定会贯穿三部作品。浪漫、忠诚与牺牲，RPG 剧情叙事的巅峰。",
         "2021-05-14", 1, 8.8, True, 70, 260,
         ["科幻", "RPG", "剧情丰富", "太空"]),
        (19, "只狼：影逝二度", "Sekiro: Shadows Die Twice", "FromSoftware", 814380,
         "FromSoftware 的日本战国动作游戏。忍者狼凭借义手忍具与「拼刀」系统，在苇名国与神佛妖魔对决。弹反机制让战斗如刀剑交锋般爽快，荣获 2019 年 TGA 年度游戏。",
         "2019-03-22", 3, 9.2, True, 90, 360,
         ["魂系", "动作", "日本", "困难"]),
        (20, "鬼泣 5", "Devil May Cry 5", "Capcom", 601150,
         "卡普空华丽动作的巅峰。尼禄、但丁与 V 三条线索交汇，风格评分系统鼓励你打出最花哨的连段。RE 引擎画面惊艳，「Jackpot！」——动作游戏玩家的爽感天花板。",
         "2019-03-08", 3, 9.0, True, 74, 350,
         ["动作", "华丽", "砍杀", "单人"]),
        (21, "怪物猎人：世界", "Monster Hunter: World", "Capcom", 582010,
         "卡普空共斗狩猎的集大成之作。在新大陆追踪、讨伐数十种巨型怪物，用素材打造武器装备。14 种武器风格迥异，无缝地图与生态演出让狩猎沉浸感空前，极适合与好友联机。",
         "2018-08-09", 3, 8.9, True, 86, 400,
         ["动作", "合作", "狩猎", "共斗"]),
        (22, "死亡细胞", "Dead Cells", "Motion Twin", 588650,
         "法国独立团队打造的类银河恶魔城 Roguelike。每次死亡都从零开始，但永久解锁的武器与细胞让你越变越强。快节奏的翻滚招架与海量武器 Build，被称为「类 Rogue 与银河恶魔城的完美联姻」。",
         "2018-08-07", 3, 9.0, True, 73, 390,
         ["Roguelike", "像素", "动作", "类银河恶魔城"]),
        (23, "侠盗猎车手 5", "Grand Theft Auto V", "Rockstar Games", 271590,
         "R 星的洛圣都犯罪史诗。麦克、富兰克林、崔佛三主角交错叙事，这座城市本身就是最棒的沙盒游乐场。剧情模式与长青的 GTA Online 让它成为史上销量最高的游戏之一。",
         "2015-04-14", 4, 8.6, True, 93, 550,
         ["开放世界", "犯罪", "多人", "动作"]),
        (24, "霍格沃茨之遗", "Hogwarts Legacy", "Avalanche Software", 990080,
         "哈利波特世界的开放世界动作 RPG。故事设定在 19 世纪的霍格沃茨，你是掌握古代魔法的五年级转学生。分院、上课、骑扫帚、驯服神奇动物，哈迷梦寐以求的魔法学生活。",
         "2023-02-10", 4, 8.2, True, 81, 200,
         ["魔法", "开放世界", "奇幻", "哈利波特"]),
        (25, "地平线：零之曙光", "Horizon Zero Dawn Complete Edition", "Guerrilla Games", 1151640,
         "游击队打造的后启示录开放世界。人类文明退化为部落，巨型机械兽统治大地。红发猎人埃洛伊用弓箭与绊线狩猎机械恐龙，揭开旧世界毁灭的惊人真相。",
         "2020-08-07", 4, 8.5, True, 68, 240,
         ["开放世界", "动作RPG", "科幻", "女主角"]),
        (26, "死亡搁浅", "Death Stranding", "Kojima Productions", 1190460,
         "小岛秀夫独立后的首款作品。在死亡搁浅后的美国，快递员山姆背着货物穿越 BT 出没的荒野，连接孤立的节点。一款关于「送货」与「连接」的奇特游戏，喜欢的人会深深着迷。",
         "2020-07-14", 4, 8.8, True, 77, 220,
         ["开放世界", "剧情", "步行模拟", "科幻"]),
        (27, "城市：天际线", "Cities: Skylines", "Colossal Order", 255710,
         "现代城市建设模拟的王者。规划道路、分区、公共交通与公共服务，看着小村庄成长为百万人口都市。堵车治理是每位市长的必修课，MOD 生态让玩法无限延伸。",
         "2015-03-10", 5, 8.8, True, 71, 520,
         ["城市建设", "模拟", "管理", "沙盒"]),
        (28, "环世界", "RimWorld", "Ludeon Studios", 294100,
         "AI 故事讲述者驱动的殖民地模拟。三个流坠异星的幸存者从零建家、抵御袭击、应对瘟疫与心灵飞船。每个殖民者都有背景故事与情绪，事故永远比计划精彩——「再来一天就睡觉」。",
         "2018-10-17", 5, 9.3, True, 80, 330,
         ["殖民模拟", "生存", "沙盒", "剧情"]),
        (29, "XCOM 2", "XCOM 2", "Firaxis Games", 268500,
         "Firaxis 的回合制战棋神作。外星人统治地球 20 年后，你指挥 XCOM 游击队打响反击战。命中率 99% 也会 miss 的紧张感、永久死亡的队员培养与基地建设，让人又爱又恨。",
         "2016-02-05", 6, 8.6, True, 69, 560,
         ["回合制", "策略", "战棋", "科幻"]),
        (30, "尘埃拉力赛 2.0", "DiRT Rally 2.0", "Codemasters", 690790,
         "Codemasters 最硬核的拉力赛拟真游戏。在威尔士泥泞、阿根廷碎石与芬兰飞跳中控制失控边缘的拉力车，领航员的路书就是你的生命。没有辅助线，没有回头路，献给真正的驾驶爱好者。",
         "2019-02-26", 7, 8.4, True, 62, 300,
         ["拉力赛", "竞速", "拟真", "赛车"]),
    ]
    for gid, name, en, dev, appid, desc, rel, cid, score, online, hot, days, tags in games_seed:
        g = Game(
            id=gid, name=name, name_en=en, developer=dev,
            cover_url="https://cdn.cloudflare.steamstatic.com/steam/apps/%d/header.jpg" % appid,
            steam_url="https://store.steampowered.com/app/%d/" % appid,
            description=desc, release_date=rel, category_id=cid, average_score=score,
            is_online=online, hot=hot, created_at=d(days), updated_at=d(days),
        )
        db.add(g)
        for t in tags:
            db.add(GameTag(game_id=gid, tag=t))

    # ---- 评测 ----
    # 元组末 4 位为四维评分（剧情/画面/玩法/优化，1-10；未公开评测不参与打分则为 None）
    reviews_seed = [
        (1, 1, 2, "《艾尔登法环》深度评测：开放世界与魂系的完美融合",
         "<h2>总评：9.6 分，年度最佳实至名归</h2><p>当 FromSoftware 决定做开放世界，所有人都担心魂系的精雕细琢会被稀释。事实证明，交界地的每一寸土地都藏着惊喜。</p><h2>一、开放世界的新范式</h2><p>没有问号轰炸地图，没有公式化据点。你远远看到一座破屋，走近可能是一段支线；远远看到一棵金色巨树，那就是你几十个小时后的终点。探索的驱动力完全来自好奇心本身。</p><h2>二、战斗与 Build</h2><p>战灰系统让武器构筑空前自由，法师、双刀、大曲剑各有爽点。Boss 战依然是 FS 的看家本领，碎星拉塔恩的演出堪称系列之最。</p><h2>三、缺点</h2><p>后期天空城与圣树的难度曲线陡峭，PC 版初期优化一般。</p><p>总而言之，这是献给所有热爱探索的玩家的一封情书。</p>",
         ["魂系", "年度游戏"], "published", "passed", 8, "", 12350, 866, 412, 120, 10, 9, 9, 8),
        (2, 2, 5, "《博德之门3》：CRPG 的新黄金标准",
         "<h2>总评：9.7 分</h2><p>拉瑞安用 5e 规则证明了一件事：回合制可以比动作游戏更爽快。第一章的林地攻防战就足以让大多数 RPG 黯然失色。</p><p>最惊人的是自由度——你可以和敌人谈判、把 Boss 推下悬崖、甚至和反派谈恋爱。编剧对「玩家想干什么」的回应几乎没有死角。</p><p>如果你只玩一款 2023 年的游戏，就是它。</p>",
         ["CRPG", "剧情"], "published", "passed", 5, "", 9820, 743, 356, 90, 10, 9, 9, 9),
        (3, 3, 2, "《黑神话：悟空》通关评测：国产 3A 的里程碑",
         "<h2>总评：9.3 分</h2><p>天命人走出花果山的那一刻，中国玩家等了很多年。</p><p>战斗系统上，劈棍、立棍、戳棍三架势切换流畅，七十二变与法术让 Boss 战充满解法。美术更是无可争议的世界级——小雷音寺的金顶、紫云山的丹霞，每一帧都能当壁纸。</p><p>短板在于地图引导偏弱、结局叙事见仁见智。但它证明了：中国人做 3A，能成。</p>",
         ["国产", "3A"], "published", "passed", 6, "", 28600, 2100, 980, 60, 9, 10, 9, 8),
        (4, 8, 5, "《哈迪斯》评测：死了一千次还想再来一把",
         "<h2>总评：9.2 分</h2><p>Roguelike 最爽的节奏被 Supergiant 彻底摸透。15 分钟一局，每局都有新 Build，每次死亡都推进剧情。</p><p>众神祝福的组合拳、信物系统、镜子天赋，成长曲线层层嵌套。全程配音的希腊神明个个性格鲜明。</p>",
         ["Roguelike", "独立游戏"], "published", "passed", 3, "", 6420, 521, 230, 80, 9, 9, 10, 9),
        (5, 9, 2, "《星露谷物语》：治愈一切的像素田园",
         "<h2>总评：9.5 分</h2><p>春种秋收，养鸡钓鱼，和镇民聊天跳舞。星露谷的厉害之处在于它没有目标——你想怎么活就怎么活。</p><p>下班之后打开游戏浇浇花，现实里的焦虑就被治愈了。</p>",
         ["治愈", "模拟"], "published", "passed", 2, "", 5310, 467, 310, 70, 9, 8, 9, 10),
        (6, 12, 5, "《空洞骑士》：圣巢之下，皆是悲歌",
         "<h2>总评：9.4 分</h2><p>手绘的虫子王国里，每一个 NPC 都有令人心碎的故事。</p><p>地图设计是教科书级别的 interconnected world，一门之隔常常是两个区域。Boss 战难度硬核但公平，辐辉级等你挑战。</p>",
         ["银河恶魔城", "独立游戏"], "published", "passed", 4, "", 7240, 689, 401, 55, 10, 9, 9, 9),
        (7, 4, 2, "《赛博朋克2077》：夜之城漫步指南",
         "<h2>从口碑崩盘到涅槃重生</h2><p>2.0 更新与往日之影 DLC 之后，夜之城终于兑现了最初的承诺。义体 Build 玩法深度大增，V 的故事依然是 CDPR 最擅长的那杯烈酒。</p><p>建议：一定要做完帕南线和朱迪线。</p>",
         ["赛博朋克", "开放世界"], "manual_review", "manual_review", 62, "AI 判定存在疑似引战表述，建议人工复核", 0, 0, 0, 3, 8, 9, 8, 6),
        (8, 7, 2, "CS2 新手必看！加群领皮肤攻略",
         "<p>新手玩家快来，加群 xxx-xxx-xxx 免费领皮肤，还有代购打折游戏，微信 vx_xxxxxx 联系我！</p>",
         [], "rejected", "rejected", 92, "AI 审核驳回：检测到广告引流内容（加群/联系方式），违反社区内容规范", 0, 0, 0, 6, None, None, None, None),
        (9, 6, 2, "《巫师3》二周目：猎魔人的自我修养（草稿）",
         "<h2>二周目才懂的细节</h2><p>（草稿，未完待续……）血腥男爵线第一次玩只觉得震撼，二周目才发现每个选择都有伏线……</p>",
         ["剧情"], "draft", None, None, "", 0, 0, 0, 2, None, None, None, None),
        (10, 5, 5, "《大镖客2》细节考据：R星的西部有多真实",
         "<p>亚瑟的胡子会生长、马会受惊、路过的NPC会记住你……这篇图文整理了 30 个令人发指的细节。</p>",
         ["考据", "开放世界"], "published", "passed", 7, "", 8900, 712, 388, 45, 9, 10, 9, 8),
    ]
    for rid, gid, uid, title, content, tags, status, a_status, a_score, a_reason, rc, lc, fc, days, s_story, s_graphic, s_gameplay, s_opt in reviews_seed:
        r = Review(
            id=rid, game_id=gid, user_id=uid, title=title, content=content,
            score_story=s_story, score_graphic=s_graphic,
            score_gameplay=s_gameplay, score_opt=s_opt,
            status=status, audit_status=a_status, audit_score=a_score, audit_reason=a_reason,
            read_count=rc, like_count=lc, fav_count=fc, created_at=d(days), updated_at=d(days),
        )
        db.add(r)
        for t in tags:
            db.add(ReviewTag(review_id=rid, tag=t))

    # ---- 追加评测攻略：每款游戏预置 好评/中性/差评 各 1 篇公开评测（带完整四维评分） ----
    # 内容由游戏名+标签组合生成，保证每篇文本互不重复；评分基于游戏种子综合分推导
    gen_tags = {g[0]: g[12] for g in games_seed}
    gen_scores = {g[0]: g[8] for g in games_seed}
    review_variants = [
        ("good", "深度评测", (
            "作为一款主打{tag1}与{tag2}的作品，《{name}》给我的第一印象相当惊艳。"
            "玩法层面核心循环扎实，{tag3}元素的融入让每次决策都有分量；"
            "剧情演出与关卡节奏张弛有度，BOSS 战的机制设计尤其值得反复琢磨。"
            "我花了三十多个小时通关一周目，途中几乎没有遇到劝退的重复劳动，强烈推荐给喜欢{tag1}的玩家。"),
         ("剧情演出在线，关卡设计环环相扣", "画面与美术风格高度统一", "玩法深度足够撑起上百小时", "优化表现稳定")),
        ("mid", "一周目通关心得", (
            "客观聊聊《{name}》。它的{tag1}与{tag2}确实是卖点，{tag3}部分的中规中矩让体验谈不上惊艳但也不失望。"
            "我通关大约花了二十小时，中期有几段任务引导做得模糊，需要自己摸索；"
            "剧情整体工整，缺少让人拍案的反转。如果你是{tag3}爱好者可以入手，纯路人建议先看实况再决定。"),
         ("剧情工整但缺乏记忆点", "画面达标，个别场景贴图一般", "玩法中规中矩，耐玩度一般", "优化尚可，偶有掉帧")),
        ("bad", "劝退实录", (
            "说实话对《{name}》挺失望的。宣传里吹的{tag1}和{tag2}在实际体验里存在感稀薄，"
            "玩法单调重复，任务设计基本是跑腿与刷材料的排列组合，我硬撑了十几个小时还是选择了退款边缘的放弃。"
            "剧情逻辑前后矛盾，{tag3}相关内容更像凑数。除非你对该系列有情怀滤镜，否则不建议原价入手。"),
         ("剧情割裂，人物动机站不住脚", "画面过时，光影表现拉胯", "玩法重复，缺乏正反馈", "优化糟糕，发热与闪退频发")),
    ]
    next_rid = 11
    for g in games_seed:
        gid, name = g[0], g[1]
        base = min(10, max(6, int(round(gen_scores[gid]))))
        tags3 = (gen_tags[gid] + ["剧情", "玩法", "画面", "优化"])
        for vi, (kind, suffix, tpl, dim_words) in enumerate(review_variants):
            tag1, tag2, tag3 = tags3[0], tags3[1 % len(tags3)], tags3[2 % len(tags3)]
            content_html = (
                "<h2>关于《{name}》的{cn_label}</h2><p>{body}</p><h2>分维度小结</h2><p>{d1}；{d2}；{d3}；{d4}。</p>"
            ).format(
                name=name, cn_label=suffix,
                body=tpl.format(name=name, tag1=tag1, tag2=tag2, tag3=tag3),
                d1=dim_words[0], d2=dim_words[1], d3=dim_words[2], d4=dim_words[3])
            if kind == "good":
                dims = (min(10, base + 1), min(10, base), max(1, base - 1), max(1, base - 1))
            elif kind == "mid":
                dims = (max(1, base - 2), max(1, base - 2), max(1, base - 3), max(1, base - 2))
            else:
                dims = (max(1, base - 4), max(1, base - 5), max(1, base - 4), max(1, base - 5))
            uid = 2 if vi % 2 == 0 else 5
            days = 10 + (gid * 3 + vi * 7) % 40
            db.add(Review(
                id=next_rid, game_id=gid, user_id=uid,
                title="《%s》%s：%s向玩家的真实体验" % (name, suffix, {"good": "推荐", "mid": "中性", "bad": "避雷"}[kind]),
                content=content_html,
                score_story=dims[0], score_graphic=dims[1],
                score_gameplay=dims[2], score_opt=dims[3],
                status="published", audit_status="passed", audit_score=3, audit_reason="",
                read_count=800 + (gid * 137 + vi * 61) % 5200,
                like_count=40 + (gid * 29 + vi * 17) % 320,
                fav_count=15 + (gid * 11 + vi * 7) % 130,
                created_at=d(days), updated_at=d(days),
            ))
            next_rid += 1

    # autoflush=False：聚合查询前必须显式 flush，否则 pending 的评测对查询不可见
    db.flush()

    # ---- 用户游戏评分（1-10 分）：每款游戏 2-3 名用户评分，同一用户对单款游戏仅一条 ----
    rating_authors = [3, 4, 7, 2, 5]
    for g in games_seed:
        gid = g[0]
        base = min(10, max(6, int(round(gen_scores[gid]))))
        for k in range(2 + gid % 2):
            uid = rating_authors[(gid * 2 + k) % len(rating_authors)]
            score = min(10, max(1, base + ((gid + k) % 3) - 1))
            rdays = 5 + (gid + k * 3) % 25
            db.add(GameRating(game_id=gid, user_id=uid, score=score,
                              created_at=d(rdays), updated_at=d(rdays)))
    # autoflush=False：聚合查询前必须显式 flush，否则 pending 的评分对查询不可见
    db.flush()

    # ---- 聚合回写：统一调用 repositories.recalc_game_scores（全站唯一评分口径）----
    from app import repositories as _repo
    for g in games_seed:
        _repo.recalc_game_scores(db, g[0])

    # ---- 创作者积分与等级：精选标记 + 按公开评测积分规则回算（含积分流水） ----
    from app.core import points as _pts
    featured_ids = [1, 2, 3]  # 管理员标记的精选评测（+30/篇）
    for fr in db.query(Review).filter(Review.id.in_(featured_ids)).all():
        fr.is_featured = True
    db.flush()
    for cu in db.query(User).filter(User.role.in_(["creator", "admin"])).all():
        balance = 0.0
        records = []  # (created_at, change, reason, review_id)
        pub_reviews = db.query(Review).filter(
            Review.user_id == cu.id, Review.status == "published"
        ).order_by(Review.created_at.asc()).all()
        for rv in pub_reviews:
            base_t = rv.created_at
            entries = [(base_t, _pts.POINT_PUBLISH,
                        "评测《%s》审核通过发布" % rv.title, rv.id)]
            if rv.is_featured:
                entries.append((base_t + timedelta(minutes=1), _pts.POINT_FEATURED,
                                "评测《%s》被管理员标记精选" % rv.title, rv.id))
            if rv.like_count:
                entries.append((base_t + timedelta(minutes=2),
                                round(_pts.POINT_REVIEW_LIKE * rv.like_count, 1),
                                "评测《%s》累计获赞 %d 次" % (rv.title, rv.like_count), rv.id))
            if rv.fav_count:
                entries.append((base_t + timedelta(minutes=3),
                                round(_pts.POINT_REVIEW_FAV * rv.fav_count, 1),
                                "评测《%s》累计被收藏 %d 次" % (rv.title, rv.fav_count), rv.id))
            for t, chg, reason, rid in entries:
                balance = round(balance + chg, 1)
                records.append((t, chg, reason, rid, balance))
        for t, chg, reason, rid, bal in records:
            db.add(PointRecord(user_id=cu.id, change=chg, reason=reason,
                               related_type="review", related_id=rid,
                               balance_after=bal, created_at=t))
        cu.creator_points = balance
        cu.creator_level = _pts.level_for_points(balance)

    # ---- 评论 ----
    comments_seed = [
        (1, 3, "review", 1, None, "碎星那一战我打了整整一下午，过的时候手都在抖！", 45, 119),
        (2, 4, "review", 1, 1, "同感！拉塔恩的 BGM 一响直接头皮发麻", 12, 118),
        (3, 7, "review", 1, None, "请问新手适合玩法师还是近战呀？", 3, 110),
        (4, 2, "review", 1, 3, "新手强烈推荐观星者，远程法术容错率高~", 20, 109),
        (5, 3, "review", 3, None, "黑神话首发日我请假在家玩了一整天，值了！", 88, 59),
        (6, 4, "review", 2, None, "影心是我老婆，不接受反驳。", 34, 88),
    ]
    for cid, uid, ttype, tid, pid, content, lc, days in comments_seed:
        db.add(Comment(
            id=cid, user_id=uid, target_type=ttype, target_id=tid, parent_id=pid,
            content=content, like_count=lc, created_at=d(days),
        ))
    # 评论点赞
    likes_seed = [
        (1, 4), (1, 2), (1, 7), (2, 3), (2, 2), (4, 3), (4, 7),
        (5, 2), (5, 4), (5, 7), (6, 3), (6, 2),
    ]
    for cmt_id, uid in likes_seed:
        db.add(CommentLike(comment_id=cmt_id, user_id=uid, created_at=now))

    # ---- 游戏评论：每款游戏 1 条高质量长评（≥50字，紧扣游戏具体内容+个人游玩感受，点赞最高→自动精选候选）
    # + 5-10 条差异化普通短评。精选不再人工指定，完全由运行时按点赞数自动计算 ----
    # 长评：人工撰写，每条均提及该游戏的玩法/剧情/关卡/BOSS/画面/机制中至少一项，并带个人真实体验
    featured_texts = [
        # 1 艾尔登法环
        "交界地的开放世界设计太妙了，我骑着灵马在宁姆格福闲逛，随便摸进一个地下监牢都能挖出一套新的 build。碎星拉塔恩那场 BOSS 战我打了整整两天，召唤一众 NPC 一起冲锋时热血沸腾，八十小时通关还舍不得进二周目。",
        # 2 博德之门 3
        "拉瑞安把 DND 5e 规则做得一点都不枯燥，我队里游荡者偷袭接战士借机攻击的连招屡试不爽。第一章地精营地是屠村还是谈判让我纠结了半小时，影心的个人剧情一路反转，通关后看队友各奔东西居然有点鼻酸，年度游戏实至名归。",
        # 3 黑神话：悟空
        "国产 3A 能有这个完成度真的感动。金箍棒轻重棍势切换的手感扎实，黄风大圣那关我在风沙里死了十几次才摸清出招节奏，小西天的壁画场景美得舍不得走。三十小时通关，部分关卡锁视角和后期数值是硬伤，但瑕不掩瑜。",
        # 4 赛博朋克 2077
        "更新到 2.0 之后完全是另一个游戏。义体过载配沙鹰暴击的 build 让最高难度也能横着走，夜之城雨夜街头的霓虹画面配上叛逆电台的音乐，代入感直接拉满。杰克葬礼那段剧情我一个老玩家居然红了眼，六十小时主线打完还在满城清问号。",
        # 5 荒野大镖客：救赎 2
        "R 星对细节的偏执到了可怕的程度，马蹄踩在泥地里会留下深浅不一的印子，亚瑟几天不刮胡子就疯长。第六章雪山那场决战配上达奇的台词，剧情后劲大得我通关一周没点开别的游戏。节奏慢是真的，但沉浸感也是真的无人能敌。",
        # 6 巫师 3
        "杰洛特找希里这条主线的叙事节奏太好了，血腥男爵任务里沼泽三女巫的支线我至今记得清清楚楚。次世代更新后威伦的草甸和诺维格瑞的雨天画面焕然新生，昆特牌我打到忘了推进主线，两百小时还没清完问号。",
        # 7 反恐精英 2
        "起源 2 引擎的烟雾弹是真的物理，烟雾会被手雷炸开缺口再慢慢回流，Inferno 香蕉道丢烟抢点的战术深度一下就上来了。亚秒级服务器打起来手感丝滑，我和车队在炙热沙城二排了一整晚，就是偶尔匹配到实力差距大的局，希望 V 社继续打磨反作弊。",
        # 8 哈迪斯
        "Roguelike 最怕重复，但哈迪斯每次死亡回大厅听众神唠嗑都有新台词，扎格列欧斯和冥后的家庭剧我追了五十局。雅典娜反弹盾配海神击飞特效清屏特别爽，信物系统让每局 build 都不一样，OST 好听到我单独买了专辑。",
        # 9 星露谷物语
        "下班回家浇浇地钓钓鱼，星露谷的像素画面配上季节变化的 BGM，比什么解压神器都管用。我第二年秋天娶了潘妮，温室种满上古水果后躺着数钱，和朋友联机四个人分工种地挖矿效率翻倍，不知不觉就肝到凌晨两点。",
        # 10 文明 6
        "「再来一回合就睡觉」是真的，等我打完这把宗教胜利天都亮了。区域相邻加成的机制很讲究，学院靠山、剧院靠奇观的布局我能研究半小时，秦始皇长城流铺城又稳又爽。AI 后期外交有点神经质，但策略深度足够我再玩几百小时。",
        # 11 极限竞速：地平线 5
        "墨西哥这张地图的季节变换做得太美了，雨季丛林里的泥地拉力和旱季火山口的下坡冲刺完全是两种手感。我折腾了一整天改装调校四百多辆车，方向盘打起来手感细腻，周末和朋友联机跑环岛赛吹水，休闲竞速天花板。",
        # 12 空洞骑士
        "等丝之歌等得我把空洞骑士又通了一遍。圣巢的手绘美术配上低沉的钢琴配乐，在泪水之城听雨那段氛围绝了。格林团长的 BOSS 战拼反应拼到手指发酸，苦痛之路我跳了四个小时才过，硬核但每次死亡都觉得是自己菜，不是游戏不公平。",
        # 13 绝地求生
        "最早一批吃鸡玩家，机场 C 字楼落地成盒几十把才学会听声辨位。缩圈机制带来的紧张感至今没有同类能替代，最后一圈趴在草里和对面拼药时肾上腺素飙升，和车队四排连麦喊到嗓子哑。虽然现在外挂问题头疼，但情怀分必须给满。",
        # 14 Apex 英雄
        "Respawn 的射击手感真是行业顶尖，滑铲接绳索转点的机动性一旦习惯就回不去了。我主玩寻血犬，扫描开 Q 突脸的节奏特别上头，世界边缘那张图的碎片东区落地架百玩不腻。新赛季平衡性偶尔翻车，但和队友排位冲分的爽感还是独一档。",
        # 15 毁灭战士：永恒
        "这游戏把 FPS 的战斗节奏推到了极致，荣耀击杀回血、电锯回弹的机制逼你全程贴脸输出，根本没机会蹲掩体。重金属 BGM 一响恶魔再多人也敢冲，地狱关卡的平台跳跃略硬核，但整体爽快感是我玩过所有射击游戏里最纯粹的。",
        # 16 上古卷轴 5：天际
        "十年老滚玩家表示特别版的 64 位稳定性和高清材质让重开体验舒服太多。我这档走潜弓流，蹲在遗迹阴影里一箭秒掉尸鬼大君的爽感百试不厌，盗贼公会和黑暗兄弟会的支线叙事比主线还抓人。膝盖中箭梗玩了十年，天际省还是逛不腻。",
        # 17 辐射 4
        "废土波士顿的黑色幽默太对我胃口了，和狗肉一起在发光海捡垃圾建据点，几百小时就没推过多少主线。穿上动力装甲踩死死亡爪的瞬间值回票价，VATS 慢动作轰掉超变变种人脑袋百看不厌。对话选择比新维加斯浅是遗憾，但建设系统让人上瘾。",
        # 18 质量效应：传奇版
        "薛帕德三部曲的剧情厚度在 RPG 里独一档，从一代救议会到三代结局抉择，盖拉斯的忠诚任务我每次重玩都认真做完。传奇版把一代的操作和画面翻新后流畅多了，诺曼底号上和队友聊天的日常比打仗还让人怀念，太空歌剧巅峰。",
        # 19 只狼：影逝二度
        "拼刀弹反的机制太上头了，叮的一声完美格挡比什么奖励都爽。苇名弦一郎我卡了三个晚上，最后无伤过他第三阶段时手心全是汗。义手忍具爆竹克野兽、伞克雷的克制设计很讲究，苇名城的红叶和雪景像浮世绘，年度游戏不冤。",
        # 20 鬼泣 5
        "卡普空的动作手感从没让人失望，尼禄红刀配机械手的连段越打越花，风格评分从 D 刷到 SSS 的过程就是对玩家最好的奖励。RE 引擎下但丁的建模精细到胡茬，V 召唤魔兽走位输出的玩法很新鲜，二周目上手但丁直接爽到飞起。",
        # 21 怪物猎人：世界
        "十四种武器真的是十四种玩法，我太刀见切斩练了上百小时，砍中灭尽龙白棘倒地的瞬间成就感爆棚。冰原的冰咒龙套配冥赤龙武器刷到天昏地暗，无缝地图里怪物互殴的生态演出像在看纪录片，和好友四人组队狩猎的共斗乐趣无可替代。",
        # 22 死亡细胞
        "快节奏的翻滚招架一旦上头根本停不下来，每局随机的武器组合逼你临场换套路，巨人崛起 DLC 的稻草人 BOSS 我死了快二十次。永久解锁的细胞和锻造所让菜鸡也能慢慢滚雪球，二细胞难度开始才是真正的开始，像素画面配管弦乐意外地带感。",
        # 23 侠盗猎车手 5
        "三主角切换叙事是 R 星最聪明的设计，崔佛疯、麦克怂、富兰克林稳，珠宝店劫案的前置任务我反复玩了三遍。洛圣都的街头细节密度惊人，堵车时听电台、半夜开上山看夜景都能打发时间，线上模式和朋友抢赌场劫案笑到肚子痛，长青不是没道理。",
        # 24 霍格沃茨之遗
        "收到猫头鹰信那一刻哈迷直接泪目，分院帽分我进格兰芬多后，在城堡里爬楼梯找移动教室的还原度满分。古代魔法的终结技演出华丽，骑着扫帚在禁林边打黑巫师边看海格小屋，画面美得像在电影里。后期重复度偏高，但魔法课和有求必应屋养神奇动物够我沉迷很久。",
        # 25 地平线：零之曙光
        "机械兽的设定太有想象力了，用绊线和绳索陷阱狩猎雷霆牙的打法完全是另一个怪物猎人。埃洛伊这个红发女猎人的塑造很有魅力，旧世界毁灭真相的剧情在全息记录里一点点拼出来特别抓人，Decima 引擎的画面在开放世界里绝对第一梯队，坐等续作上 PC。",
        # 26 死亡搁浅
        "一开始以为是走路模拟器，结果背货规划路线的机制意外上瘾，在 BT 区和米尔人之间铺快递网络越铺越有成就感。开罗尔网络连上网、高速公路一段段修通时，真的能体会到小岛想表达的连接。剧情后半段亚美莉的反转后劲很大，和 BB 的互动细节也戳人。",
        # 27 城市：天际线
        "治堵车是每位市长的毕业考，我拆掉高速入口改成单行道加公交分流后，看着全城车流变成绿色畅通，满足感爆棚。公园生活和工业 DLC 的供应链能玩出花来，工坊 MOD 打了六十多个还在加，规划党杀时间神器，新建的城市一不小心就到了后半夜。",
        # 28 环世界
        "三个坠机幸存者开局，我眼睁睁看着厨师精神崩溃把仓库点了，AI 故事讲述者的随机性比编剧还敢写。殖民地防御从木栅栏滚到自动炮塔的过程特别上头，MOD 生态直接把玩法翻倍，冷库供电、小人心情、袭击波次要操心的事太多，再来一天就睡觉。",
        # 29 XCOM 2
        "命中率 99% 贴脸 miss 是 XCOM 玩家的共同创伤，但也正是这种压力让每次战术决策都惊心动魄。我王牌狙击手中毒阵亡后直接读档半小时，兵种搭配和掩体推进的战棋机制堪称教科书，化身计划倒计时逼着你取舍，基地建设加人员养成让人又爱又恨。",
        # 30 尘埃拉力赛 2.0
        "拟真拉力赛的硬核程度超出想象，没有辅助线没有回头路，全靠领航员的路书提前判断弯道。威尔士雨夜里轮胎在泥地上打滑的触感、芬兰飞跳落地时悬挂的反馈，用方向盘玩真的会哭。新手被劝退是常态，但一圈完美跑完赛段的成就感，比任何娱乐向赛车都强。",
    ]
    # 数据契约自检：长评必须 ≥50 字（保证能通过自动精选校验）
    assert len(featured_texts) == 30
    for _t in featured_texts:
        assert len(_t.strip()) >= 50, "长评字数不足 50：" + _t

    # 普通短评：片段池组合生成（参考 Steam/TapTap 短评风格改写），全局去重，禁止复制粘贴
    # 开头池刻意交错取模，杜绝「同一开头刷屏」；并补充中性/吐槽向开头
    nc_openers = [
        "打折入的，", "观望了很久才买，", "朋友安利来的，", "刷实况被种草，",
        "原价入手的，", "玩了三十小时，", "刚通关一周目，", "趁假期肝完了，",
        "作为休闲玩家，", "剧情党路过，", "冲着美术来的，", "上班摸鱼玩的，",
        "等了好久终于打折，", "老粉直接入了，", "退款边缘试探后留下的，", "被主播骗进来的，",
        "半夜睡不着开的，", "地铁上随手玩的，", "年末总结必提的，", "白给之后真香的，",
        "首发当天冲的，", "二周目回来补的，", "被朋友拉进坑的，", "联赛看完热血上头的，",
        "通关纪念一下，", "手残党艰难推进中，", "白金达成来汇报，", "剧情实况二刷的，",
        "出差路上通关的，", "迟到了三年的补票，",
    ]
    nc_middles = [
        "越玩越上头", "战斗手感相当扎实", "剧情演出值回票价", "BOSS 战机制很有创意",
        "美术风格太对味了", "音乐好听到单曲循环", "地图探索处处有惊喜", "配装流派能研究很久",
        "支线质量比主线还高", "优化好到低配也能流畅跑", "节奏紧凑不拖沓", "关卡设计环环相扣",
        "重玩价值很高", "氛围沉浸感拉满", "难度选项对新手友好", "角色塑造个个鲜活",
        "结局反转让人没想到", "技能搭配套路很多", "开放世界内容塞得很满", "解谜部分恰到好处",
        "后期数值有点膨胀", "教程引导略显啰嗦", "联机偶尔掉线有点烦", "地图大但填充略重复",
        "死亡惩罚有点劝退", "前期节奏偏慢热", "偶尔遇到点穿模 BUG", "高难度下比较受苦",
        "DLC 定价偏高", "剧情后半段收得有点仓促",
        "代练都嫌累的肝度", "任务引导基本靠猜", "优化稀烂全靠硬件撑", "剧情注水明显",
        "匹配机制像坐过山车", "手感发涩不像同一团队做的", "付费点吃相略难看", "战斗读盘慢到出戏",
    ]
    nc_endings = [
        "。", "总体推荐。", "个人给好评。", "已经安利给朋友了。", "瑕不掩瑜吧。",
        "会再开二周目。", "期待后续更新。", "比预期好玩。", "通宵警告。",
        "建议打折入手。", "新手记得先调难度。", "玩着玩着天就亮了。", "值这个价。", "欢迎讨论。",
        "先观望后续补丁。", "谨慎入手。", "回本了。", "就写到这吧。",
    ]
    _combo_total = len(nc_openers) * len(nc_middles) * len(nc_endings)
    _used_texts: set = set()

    def _normal_text(seq: int) -> str:
        i = seq % _combo_total
        while i in _used_texts:  # 全局唯一，杜绝重复评论
            i = (i + 1) % _combo_total
        _used_texts.add(i)
        # 交错取模：让相邻评论的开头/中段/结尾都轮转起来，避免同开头连片重复
        o = i % len(nc_openers)
        r = i // len(nc_openers)
        mi = r % len(nc_middles)
        ei = r // len(nc_middles)
        return nc_openers[o] + nc_middles[mi] + nc_endings[ei]

    featured_authors = [2, 5, 4, 3]
    normal_authors = [3, 4, 7, 5, 2, 4, 7, 3]
    next_cid = 7  # 1-6 为评测评论
    nseq = 0
    for gid in range(1, 31):
        # 高质量长评（点赞数显著高于普通短评 → 运行时自动成为精选候选）
        f_author = featured_authors[(gid - 1) % 4]
        f_days = 20 + (gid % 8)
        f_likes = 25 + (gid * 7) % 65
        db.add(Comment(
            id=next_cid, user_id=f_author, target_type="game", target_id=gid,
            parent_id=None, content=featured_texts[gid - 1],
            like_count=f_likes, created_at=d(f_days),
        ))
        # 长评点赞（排除作者本人）
        for liker in [u for u in (7, 4, 3) if u != f_author][:2]:
            db.add(CommentLike(comment_id=next_cid, user_id=liker, created_at=now))
        next_cid += 1
        # 普通评论：每款游戏 5-10 条（确定性数量，便于测试），文本全局不重复
        normal_count = 5 + gid % 6
        for k in range(normal_count):
            n_author = normal_authors[(gid * 3 + k) % len(normal_authors)]
            content = _normal_text(nseq)
            nseq += 1
            n_days = 1 + (gid + k * 2) % 15
            n_likes = (gid + k * 3) % 18
            db.add(Comment(
                id=next_cid, user_id=n_author, target_type="game", target_id=gid,
                parent_id=None, content=content,
                like_count=n_likes, created_at=d(n_days),
            ))
            if k % 3 == 1:
                liker = [u for u in (2, 3, 7) if u != n_author][0]
                db.add(CommentLike(comment_id=next_cid, user_id=liker, created_at=now))
            next_cid += 1
    # 数据契约自检：全部评论文本唯一
    assert len(_used_texts) == nseq

    # ---- 收藏 ----
    fav_seed = [(3, 1, 200), (3, 2, 150), (3, 3, 59), (2, 6, 300)]
    for uid, gid, days in fav_seed:
        db.add(Favorite(user_id=uid, game_id=gid, created_at=d(days)))

    # ---- 游玩记录 ----
    rec_seed = [
        (3, 6, "completed", 180, 100), (3, 8, "playing", 90, 5), (3, 9, "want", 30, 30),
    ]
    for uid, gid, status, cd, ud in rec_seed:
        db.add(PlayRecord(user_id=uid, game_id=gid, play_status=status,
                          created_at=d(cd), updated_at=d(ud)))

    # ---- 创作者申请 ----
    apply_seed = [
        (1, 7, "我是游戏媒体撰稿人，想在平台发布 Steam 游戏评测，之前运营过个人游戏公众号。", "pending", None, 2),
        (2, 4, "单机游戏通关 200+，想写点东西分享。", "pending", None, 1),
    ]
    for aid, uid, reason, status, auid, days in apply_seed:
        db.add(CreatorApplication(id=aid, user_id=uid, apply_reason=reason, status=status,
                                  audit_user_id=auid, created_at=d(days), updated_at=d(days)))

    # ---- 审核日志 ----
    logs_seed = [
        (1, 8, "ai", 92, '命中广告引流：检测到"加群""微信 vx"等联系方式导流片段', 1, 6),
        (2, 7, "ai", 62, '疑似引战争议表述："某游戏就是垃圾"类对比引战，需人工判断', 1, 3),
        (3, 3, "ai", 6, "内容正常，未命中风险维度", 1, 60),
    ]
    for lid, rid, atype, score, reason, opid, days in logs_seed:
        db.add(AuditLog(id=lid, review_id=rid, audit_type=atype, risk_score=score,
                        reason=reason, operator_id=opid, created_at=d(days)))

    # ==================== 社区模块 ====================
    import json as _json
    from app import repositories as _repo

    def _cover(appid: str) -> str:
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"

    # ---- 帖子：(id, 作者uid, 标题, 正文, 标签, 图片列表, 浏览量, 天前) ----
    posts_seed = [
        (1, 2, "艾尔登法环 200 小时通关纪念：交界地值得每个褪色者走一遭",
         "从宁姆格福一步步走到灰烬王城罗德尔，整整 200 小时。老头环最打动我的不是难度，而是那种『翻过这道坡，永远有新的东西在等你』的探索感。\n"
         "新手建议：别急着打主线，先把啜泣半岛和湖区逛完，等级和瓶升级够了再去碰史东薇尔。近战玩家前期推荐直剑+盾，稳扎稳打。\n"
         "最后一张是我打完最终 Boss 时的截图，手抖得不行。",
         "游戏", [_cover("1245620"), _cover("2778580")], 860, 20),
        (2, 3, "社畜打游戏时间不够用？我的碎片时间游戏清单",
         "每天下班到家只剩两三个小时，还经常累得不想动。分享几个适合碎片时间玩的游戏：\n"
         "1. 哈迪斯：每局 30-40 分钟，死了就睡，毫无负担；\n"
         "2. 星露谷物语：一天游戏内时间 15 分钟，随时存档；\n"
         "3. 杀戮尖塔：一局一把，套路多变。\n"
         "开放世界大作虽然香，但现在真的肝不动了，大家有什么同类推荐吗？",
         "闲聊", [], 520, 2),
        (3, 5, "星露谷物语三年农场布局分享（附截图）",
         "终于在第三年完成了完美农场！布局思路：\n"
         "· 温室种远古水果，配蜂房常年收蜜；\n"
         "· 畜棚集中放在南侧，靠近出货箱减少跑路；\n"
         "· 东侧全部留给果树和洒水器阵列。\n"
         "新手最容易踩的坑：第一年冬天之前一定要把锄头升级到金锄头，不然挖冬季根要崩溃。",
         "攻略", [_cover("413150")], 430, 5),
        (4, 4, "黑神话悟空通关了，说说不满的地方",
         "画面和动作确实顶级，国产 3A 的牌面没得说。但通关后还是想吐槽几点：\n"
         "1. 后期地图明显赶工，火焰山和紫云山内容量差太多；\n"
         "2. 棍法系统看着花哨，实际大部分时间蓄力戳戳戳；\n"
         "3. 收集品引导为零，全靠攻略。\n"
         "总体 8 分，鼓励分加一分。",
         "吐槽", [_cover("2358720")], 610, 1),
        (5, 2, "博德之门3 荣誉模式开荒注意事项（无剧透）",
         "荣誉模式只有一个存档，团灭直接删档，准备入坑的务必注意：\n"
         "1. 第一章幽暗地域前务必全员 5 级；\n"
         "2. 荣誉专属 Boss 机制比战术模式多，别用攻略站的老打法；\n"
         "3. 给队伍里的辅助留好卷轴，控制链断了就是团灭。\n"
         "祝各位骰运昌隆。",
         "攻略", [_cover("1086940")], 380, 8),
        (6, 3, "CS2 定级赛连败十把，心态崩了",
         "从完美 C 段一路连输，队友不是挂机就是秒选 AWP 不开枪。最离谱的一把队友在中路买了把霰弹枪蹲了一整局。\n"
         "现在定级到 3000 分，感觉自己根本不是这个水平，V社的段位机制真的没问题吗……",
         "吐槽", [], 350, 3),
        (7, 5, "今年玩过的独立游戏 TOP5 推荐",
         "今年补了不少独立游戏，私心前五：\n"
         "1. 哈迪斯——肉鸽天花板；2. 空洞骑士——地图设计教科书；3. 星露谷物语——电子止痛药；\n"
         "4. 极乐迪斯科——文本量爆炸的 CRPG；5. 传送门 2——永不过时的解谜经典。\n"
         "每一款都是小体量大内容，独立游戏的性价比真的离谱。",
         "游戏", [_cover("1145360")], 290, 12),
        (8, 7, "刚入坑求推荐：手残适合玩什么？",
         "之前只玩过手机上的消消乐，最近想认真试试 PC 游戏，但动作游戏打两下就死，太挫败了。\n"
         "各位大佬有什么对操作要求低、剧情好的游戏推荐吗？预算 200 以内，谢谢大家！",
         "闲聊", [], 210, 1),
        (9, 4, "赛博朋克2077 往日之影 值不值得买",
         "2.0 更新之后本体已经是完全体，往日之影 DLC 体量相当于半个游戏，狗镇的地图密度比夜之城还高。\n"
         "剧情走的是谍战路线，选结局的时候真的纠结了半小时。建议 30 级以上再进 DLC，不然装备会很难受。",
         "游戏", [_cover("1091500")], 340, 6),
        (10, 2, "哈迪斯全武器热度32通关 Build 分享",
         "最后一把过的是盾牌宙斯套路：核心是宙斯普攻+求援雷罚，锤子选爆裂回旋，热度高点投毒+时限。\n"
         "信物：爱神进场换宙斯信物，保证雷海成型。镜子必点死亡抗拒拉满。\n"
         "卡热度 20 的朋友可以试试这套，通关率比弓和拳稳很多。",
         "攻略", [_cover("1145360")], 260, 15),
        (11, 3, "文明6 再来一回合就睡觉……现在早上七点了",
         "昨晚十一点想开一局『随便玩玩』，结果和甘地抢奇观抢到凌晨，最后被蛮族骑射手偷了三座城。\n"
         "最气的是我赢了战争输了外交，全球红脸。这游戏对明天要上班的人极度不友好。",
         "吐槽", [], 410, 4),
        (12, 5, "荒野大镖客2 里我最喜欢的十个细节",
         "R星的细节真的变态：\n"
         "1. 雪地里走久了马的腿上会结冰碴；2. 武器长期不保养会卡壳；3. 胡子真的会慢慢长长，还能选择修剪样式；\n"
         "4. 在镇上开枪，几天后报纸会登出来；5. 温泉里碰到的路人对话每个人都不一样……\n"
         "这游戏 2018 年的，现在看还是没人比得过。",
         "游戏", [_cover("1174180"), _cover("1404210")], 320, 18),
        (13, 7, "谢谢大家的推荐，入手了空洞骑士，痛并快乐着",
         "听了上个帖子大家的建议，先买了空洞骑士。现在游戏时长 12 小时，死了 200 多次，刚打完假骑士和小姐姐。\n"
         "手残表示黄蜂小姐打了一下午，过的时候手都在抖。这个游戏为什么越死越想玩啊！",
         "闲聊", [_cover("367520")], 180, 0),
        (14, 4, "极限竞速地平线5 方向盘玩家的设置心得",
         "用罗技 G29 玩了 100 小时，关键设置：\n"
         "力回馈 70%、路感偏移 50、减速带效果 30；转向线性度 50 最跟手。\n"
         "辅助全关之后，越野赛记得把差速器前加速调到 30%，后驱大马力车起步不甩尾。",
         "攻略", [_cover("1551360")], 150, 10),
        (15, 2, "巫师3 次世代版画面设置优化指南",
         "3060 显卡稳 60 帧的设置：光追开超级性能模式，毛发特效关到中，阴影高、植被距离高，其余全高。\n"
         "次世代版最坑的是光追阴影开关，关掉直接涨 15 帧但画面几乎看不出区别。",
         "攻略", [_cover("292030")], 170, 25),
        (16, 3, "游戏里哪个瞬间让你突然泪目？",
         "我是荒野大镖客2 亚瑟在山顶看日出那次，结合后面的剧情根本绷不住。\n"
         "还有去月球结尾的钢琴曲一响，眼泪完全不受控制。大家玩游戏哭过吗？是哪个瞬间？",
         "闲聊", [], 390, 7),
    ]
    post_objs = []
    for pid, uid, title, content, tag, images, views, days in posts_seed:
        p = CommunityPost(id=pid, user_id=uid, title=title, content=content,
                         images=_json.dumps(images, ensure_ascii=False), tag=tag,
                         view_count=views, created_at=d(days), updated_at=d(days))
        post_objs.append(p)
        db.add(p)
    db.flush()

    # ---- 帖子评论（含楼中楼回复）：(id, post_id, uid, 内容, parent_id, 天前) ----
    pcomments_seed = [
        (1, 1, 3, "同 200 小时玩家，啜泣半岛真的是新手最好的课堂，我当时直接去史东薇尔被噩兆老师教育了三小时。", None, 19),
        (2, 1, 5, "直剑+盾+1，前中期最稳的流派，后期洗成法师就开始起飞了。", None, 18),
        (3, 1, 4, "回复 2 楼：法师确实强，但二周目我还是回去玩近战了，弹反太爽。", 2, 18),
        (4, 1, 7, "马克一下，昨天刚买，还在大树守卫那里反复去世……", None, 2),
        (5, 2, 5, "再加一个《短途徒步旅行》，一个半小时通关，特别治愈，适合下班瘫着玩。", None, 2),
        (6, 2, 4, "杀戮尖塔+1，我每天午休来一把，贼精神（然后下午更累了）。", None, 1),
        (7, 3, 2, "金锄头是真的，第一年冬天我拿铜锄头挖了半天才发现冬天根的数量和锄头等级挂钩。", None, 4),
        (8, 4, 2, "火焰山确实短，但我觉得节奏问题不大，总比灌水强。棍法同感，定身法+戳戳戳万能。", None, 1),
        (9, 4, 3, "8 分不能再多了，章节注水的章节是真的水。", None, 0),
        (10, 5, 3, "荣誉模式第一章团灭两次的人路过，记得打地精营地前先存几个卷轴！", None, 7),
        (11, 6, 4, "CS 的定级本来就和状态关系很大，歇两天再打，别硬刚。", None, 2),
        (12, 7, 2, "前五全部同意！极乐迪斯科建议玩之前先睡个好觉，文本密度真的大。", None, 11),
        (13, 8, 5, "手残首推星露谷物语和博德之门3，BG3 可以开剧情难度，战斗随便打。", None, 1),
        (14, 8, 2, "传送门2 也很适合，解谜为主不考操作，剧情还神。", None, 0),
        (15, 8, 3, "回复 14 楼：传送门真的神作，两个人一起玩合作模式笑到肚子痛。", 14, 0),
        (16, 13, 5, "欢迎入坑！打不过就升级骨钉和回血槽，小姐姐的节奏是三刀一躲。", None, 0),
        (17, 16, 5, "去月球+1，为了这个剧情我还买了原声带。", None, 6),
        (18, 16, 2, "巫师3 凯尔莫罕之战，维瑟米尔那段，老猎魔人真的意难平。", None, 6),
        (19, 12, 3, "报纸那个细节我第一次发现的时候惊了，还专门去买了份报纸看自己的通缉令。", None, 17),
        (20, 11, 7, "所以……这游戏到底多少钱，看你们说的我都不敢买了（笑）。", None, 3),
    ]
    for cid, pid, uid, content, parent, days in pcomments_seed:
        db.add(PostComment(id=cid, post_id=pid, user_id=uid, content=content,
                           parent_id=parent, created_at=d(days)))

    # ---- 帖子点赞：(post_id, uid) 组合，去重 ----
    post_likes_seed = [
        (1, 3), (1, 4), (1, 5), (1, 7),
        (2, 2), (2, 4), (2, 5), (2, 7),
        (3, 2), (3, 3), (3, 4),
        (4, 2), (4, 3), (4, 7),
        (5, 3), (5, 4), (5, 5),
        (6, 4), (6, 7),
        (7, 2), (7, 3), (7, 4),
        (8, 2), (8, 3), (8, 5),
        (9, 2), (9, 3), (9, 5),
        (10, 3), (10, 4), (10, 5),
        (11, 2), (11, 4), (11, 5), (11, 7),
        (12, 2), (12, 3), (12, 4),
        (13, 2), (13, 3), (13, 4), (13, 5),
        (16, 2), (16, 4), (16, 5), (16, 7),
    ]
    for i, (pid, uid) in enumerate(post_likes_seed, start=1):
        db.add(PostLike(id=i, post_id=pid, user_id=uid,
                        created_at=d(1 + (pid + uid) % 20)))

    # ---- 帖子收藏 ----
    post_favs_seed = [
        (3, 3), (3, 4), (5, 3), (5, 7), (10, 3), (10, 4),
        (14, 2), (15, 4), (7, 3), (12, 7), (1, 5), (1, 7),
    ]
    for i, (pid, uid) in enumerate(post_favs_seed, start=1):
        db.add(PostFavorite(id=i, post_id=pid, user_id=uid,
                            created_at=d(1 + (pid * 2 + uid) % 20)))

    # ---- 评论点赞 ----
    comment_likes_seed = [
        (1, 5), (1, 7), (2, 3), (2, 4), (5, 3), (13, 2), (13, 4),
        (14, 7), (16, 7), (18, 3), (18, 5), (8, 3), (19, 5),
    ]
    for i, (cid, uid) in enumerate(comment_likes_seed, start=1):
        db.add(PostCommentLike(id=i, comment_id=cid, user_id=uid, created_at=d(1)))

    # ---- 举报（1 条待处理，供后台演示） ----
    db.add(Report(id=1, reporter_id=3, target_type="post", target_id=4,
                  reason="辱骂攻击", detail="帖子里有对游戏的攻击性表述，看着不舒服",
                  status="pending", created_at=d(0)))

    db.flush()
    # ---- 回写互动计数与热度分（autoflush=False，必须 flush 后再聚合） ----
    for p in db.query(CommunityPost).all():
        p.like_count = db.query(PostLike).filter(PostLike.post_id == p.id).count()
        p.fav_count = db.query(PostFavorite).filter(PostFavorite.post_id == p.id).count()
        p.comment_count = db.query(PostComment).filter(PostComment.post_id == p.id).count()
        _repo.recalc_post_hot(db, p)
    for c in db.query(PostComment).all():
        c.like_count = db.query(PostCommentLike).filter(
            PostCommentLike.comment_id == c.id).count()
    db.flush()
