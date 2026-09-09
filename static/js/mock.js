/* ============================================================
   mock.js — 前端 Mock 数据层（阶段3 产物）
   - 后端未启动时，api.js 自动把所有 /api 请求路由到本文件
   - 数据持久化到 localStorage（gc_mock_db_v6），刷新不丢失
   - 游戏数据均为真实存在的 Steam 游戏
   ============================================================ */

(function () {
  'use strict';

  var DB_KEY = 'gc_mock_db_v10';

  /* ---------- 封面图：按各游戏风格生成的美术图 ---------- */
  function IMG(prompt) {
    return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' +
      encodeURIComponent(prompt) + '&image_size=landscape_16_9';
  }

  /* ---------- Steam 商店官方封面图（按 AppID 取 header 胶囊图） ---------- */
  function STEAM(appid) {
    return 'https://cdn.cloudflare.steamstatic.com/steam/apps/' + appid + '/header.jpg';
  }

  /* ---------- 种子数据 ---------- */
  function seed() {
    var now = Date.now();
    function d(n) { return new Date(now - n * 86400000).toISOString(); }

    var categories = [
      { id: 1, name: '角色扮演 RPG' },
      { id: 2, name: '射击 FPS' },
      { id: 3, name: '动作 ACT' },
      { id: 4, name: '开放世界' },
      { id: 5, name: '模拟经营 SIM' },
      { id: 6, name: '策略 SLG' },
      { id: 7, name: '竞速 RAC' }
    ];

    var games = [
      /* 封面统一使用 Steam 商店官方 header 胶囊图（STEAM(appid)） */
      { id: 1, name: '艾尔登法环', name_en: 'Elden Ring', developer: 'FromSoftware',
        cover_url: STEAM(1245620),
        description: '由 FromSoftware 与乔治·R·R·马丁联手打造的开放世界魂系动作 RPG。玩家作为褪色者踏入广袤的交界地，探索六大区域、挑战强敌、收集卢恩，最终成为艾尔登之王。',
        release_date: '2022-02-25', category_id: 4, tags: ['魂系', '黑暗幻想', '开放世界', '动作RPG'],
        average_score: 9.6, is_online: true, hot: 98, created_at: d(400) },
      { id: 2, name: '博德之门 3', name_en: "Baldur's Gate 3", developer: 'Larian Studios',
        cover_url: STEAM(1086940),
        description: '拉瑞安工作室出品的 CRPG 巅峰之作，基于龙与地下城 D&D 5e 规则。你的大脑被植入了夺心魔蝌蚪，一场改变费伦大陆命运的冒险由此展开，选择将真正改变世界。',
        release_date: '2023-08-03', category_id: 1, tags: ['回合制', '剧情丰富', '奇幻', '合作'],
        average_score: 9.7, is_online: true, hot: 95, created_at: d(380) },
      { id: 3, name: '黑神话：悟空', name_en: 'Black Myth: Wukong', developer: '游戏科学 Game Science',
        cover_url: STEAM(2358720),
        description: '游戏科学开发的国产 3A 动作角色扮演游戏。扮演天命人，踏上充满凶险与惊奇的西游路，与各路妖王殊死一战。每一步都踏足四大部州的神话山河。',
        release_date: '2024-08-20', category_id: 3, tags: ['神话', '动作RPG', '单机', '国风'],
        average_score: 9.3, is_online: true, hot: 99, created_at: d(300) },
      { id: 4, name: '赛博朋克 2077', name_en: 'Cyberpunk 2077', developer: 'CD Projekt Red',
        cover_url: STEAM(1091500),
        description: 'CD Projekt Red 出品的开放世界动作 RPG。在夜之城这座权力、魅力和义体改造交织的都市里，扮演雇佣兵 V，追寻一种永生不朽的独特植入体。历经多次更新后口碑全面逆袭。',
        release_date: '2020-12-10', category_id: 4, tags: ['赛博朋克', '科幻', '开放世界', '剧情丰富'],
        average_score: 8.5, is_online: true, hot: 90, created_at: d(500) },
      { id: 5, name: '荒野大镖客：救赎 2', name_en: 'Red Dead Redemption 2', developer: 'Rockstar Games',
        cover_url: STEAM(1174180),
        description: 'R 星打造的西部题材开放世界史诗。1899 年的美国，亡命之徒亚瑟·摩根随范德林德帮在时代的终结中挣扎求生。一个关于忠诚、理想与消逝的西部故事。',
        release_date: '2018-10-26', category_id: 4, tags: ['西部', '剧情丰富', '开放世界', '写实'],
        average_score: 9.5, is_online: true, hot: 87, created_at: d(600) },
      { id: 6, name: '巫师 3：狂猎', name_en: 'The Witcher 3: Wild Hunt', developer: 'CD Projekt Red',
        cover_url: STEAM(292030),
        description: '利维亚的杰洛特，一名职业猎魔人，在战火纷飞的大陆上寻找预言之子希里。CDPR 凭借本作一举封神，次世代更新后画面焕然新生。',
        release_date: '2015-05-19', category_id: 1, tags: ['奇幻', '开放世界', '剧情丰富', '选择取向'],
        average_score: 9.4, is_online: true, hot: 88, created_at: d(700) },
      { id: 7, name: '反恐精英 2', name_en: 'Counter-Strike 2', developer: 'Valve',
        cover_url: STEAM(730),
        description: 'Valve 基于起源 2 引擎打造的 CS 系列续作，免费开玩。升级的烟雾弹物理、亚秒级服务器与全新画质，让全球最流行的竞技射击焕然升级。',
        release_date: '2023-09-27', category_id: 2, tags: ['竞技', '多人', 'FPS', '电竞'],
        average_score: 8.0, is_online: true, hot: 96, created_at: d(360) },
      { id: 8, name: '哈迪斯', name_en: 'Hades', developer: 'Supergiant Games',
        cover_url: STEAM(1145360),
        description: 'Supergiant 出品的高口碑 Roguelike。扮演冥界王子扎格列欧斯，在每次死亡都重来的逃亡中杀出冥界。流畅的战斗、丰富的 Build 与全程配音的希腊诸神，让人死了一千次还想再来一把。',
        release_date: '2020-09-17', category_id: 3, tags: ['Roguelike', '希腊神话', '独立', '动作'],
        average_score: 9.2, is_online: true, hot: 80, created_at: d(450) },
      { id: 9, name: '星露谷物语', name_en: 'Stardew Valley', developer: 'ConcernedApe',
        cover_url: STEAM(413150),
        description: '一个人历时四年半开发的田园模拟神作。继承爷爷的农场，种地、养殖、钓鱼、挖矿、与村民恋爱结婚。支持多人联机，是无数玩家的电子止痛药。',
        release_date: '2016-02-27', category_id: 5, tags: ['像素', '农场', '休闲', '联机'],
        average_score: 9.5, is_online: true, hot: 85, created_at: d(800) },
      { id: 10, name: '文明 6', name_en: 'Sid Meier’s Civilization VI', developer: 'Firaxis Games',
        cover_url: STEAM(289070),
        description: '席德·梅尔的传奇 4X 策略系列。从石器时代到信息时代，建立帝国、发展科技、外交博弈或征服世界。再来一回合就睡觉——然后天就亮了。',
        release_date: '2016-10-21', category_id: 6, tags: ['回合制', '历史', '4X', '建设'],
        average_score: 8.3, is_online: true, hot: 75, created_at: d(750) },
      { id: 11, name: '极限竞速：地平线 5', name_en: 'Forza Horizon 5', developer: 'Playground Games',
        cover_url: STEAM(1551360),
        description: '地平线系列登陆墨西哥。数百辆授权座驾、世界顶级的驾驶手感、随季节变换的开放世界，无论是竞速老炮还是观光休闲玩家都能找到乐趣。',
        release_date: '2021-11-09', category_id: 7, tags: ['赛车', '开放世界', '多人', '写实'],
        average_score: 9.0, is_online: true, hot: 78, created_at: d(420) },
      { id: 12, name: '空洞骑士', name_en: 'Hollow Knight', developer: 'Team Cherry',
        cover_url: STEAM(367520),
        description: '澳大利亚三人团队打造的银河恶魔城神作。深入衰败的圣巢，探索 interconnected 的地下王国，挑战硬核 Boss 战。手绘美术、凄美配乐与庞大的世界等待着你。',
        release_date: '2017-02-25', category_id: 3, tags: ['银河恶魔城', '独立', '手绘', '困难'],
        average_score: 9.4, is_online: true, hot: 82, created_at: d(650) },
      /* ---- 13-30：追加的真实 Steam 游戏 ---- */
      { id: 13, name: '绝地求生', name_en: 'PUBG: BATTLEGROUNDS', developer: 'KRAFTON',
        cover_url: STEAM(578080),
        description: 'KRAFTON 出品的现象级大逃杀游戏。100 名玩家空降至荒岛，搜集装备、在不断缩小的安全区中厮杀，最后一人（队）获胜。它定义了一个品类，曾长期占据 Steam 同时在线榜首。',
        release_date: '2017-12-21', category_id: 2, tags: ['大逃杀', '多人', 'FPS', '射击'],
        average_score: 8.2, is_online: true, hot: 92, created_at: d(340) },
      { id: 14, name: 'Apex 英雄', name_en: 'Apex Legends', developer: 'Respawn Entertainment',
        cover_url: STEAM(1172470),
        description: 'Respawn 打造的免费英雄射击大逃杀。拥有独特技能的「传奇」三人组队，在世界边缘等地图高速交战。流畅的移动手感、智能标记系统与团队协作，是大逃杀品类的革新者。',
        release_date: '2020-11-05', category_id: 2, tags: ['大逃杀', '英雄射击', '多人', 'FPS'],
        average_score: 8.5, is_online: true, hot: 89, created_at: d(280) },
      { id: 15, name: '毁灭战士：永恒', name_en: 'DOOM Eternal', developer: 'id Software',
        cover_url: STEAM(782330),
        description: 'id Software 的纯粹暴力美学 FPS。扮演毁灭战士在地狱大军中撕开血路，荣耀击杀、电锯处决与重金属配乐让每场战斗都肾上腺素飙升，是单人射击关卡设计的教科书。',
        release_date: '2020-03-20', category_id: 2, tags: ['FPS', '快节奏', '血腥', '单人'],
        average_score: 9.0, is_online: true, hot: 76, created_at: d(310) },
      { id: 16, name: '上古卷轴 5：天际 特别版', name_en: 'The Elder Scrolls V: Skyrim Special Edition', developer: 'Bethesda Game Studios',
        cover_url: STEAM(489830),
        description: 'Bethesda 的开放世界奇幻 RPG 传奇。龙裔在天际省对抗世界吞噬者奥杜因，四大公会、数十条支线与数不清的地牢。「我以前也是个冒险者，直到我膝盖中了一箭」。',
        release_date: '2016-10-28', category_id: 1, tags: ['奇幻', '开放世界', 'RPG', '龙'],
        average_score: 9.3, is_online: true, hot: 84, created_at: d(500) },
      { id: 17, name: '辐射 4', name_en: 'Fallout 4', developer: 'Bethesda Game Studios',
        cover_url: STEAM(377160),
        description: '核战后的废土波士顿，你是 111 号避难所唯一的幸存者，踏上寻找失踪儿子的旅程。动力装甲、据点建设、V.A.T.S. 慢动作射击与黑色幽默，构成最经典的后末日 RPG。',
        release_date: '2015-11-10', category_id: 1, tags: ['后末日', '开放世界', 'RPG', '剧情丰富'],
        average_score: 8.0, is_online: true, hot: 72, created_at: d(480) },
      { id: 18, name: '质量效应：传奇版', name_en: 'Mass Effect Legendary Edition', developer: 'BioWare',
        cover_url: STEAM(1328670),
        description: 'BioWare 太空歌剧三部曲的高清合集。薛帕德指挥官率诺曼底号船员跨星系对抗收割者、拯救银河系，你的决定会贯穿三部作品。浪漫、忠诚与牺牲，RPG 剧情叙事的巅峰。',
        release_date: '2021-05-14', category_id: 1, tags: ['科幻', 'RPG', '剧情丰富', '太空'],
        average_score: 8.8, is_online: true, hot: 70, created_at: d(260) },
      { id: 19, name: '只狼：影逝二度', name_en: 'Sekiro: Shadows Die Twice', developer: 'FromSoftware',
        cover_url: STEAM(814380),
        description: 'FromSoftware 的日本战国动作游戏。忍者狼凭借义手忍具与「拼刀」系统，在苇名国与神佛妖魔对决。弹反机制让战斗如刀剑交锋般爽快，荣获 2019 年 TGA 年度游戏。',
        release_date: '2019-03-22', category_id: 3, tags: ['魂系', '动作', '日本', '困难'],
        average_score: 9.2, is_online: true, hot: 90, created_at: d(360) },
      { id: 20, name: '鬼泣 5', name_en: 'Devil May Cry 5', developer: 'Capcom',
        cover_url: STEAM(601150),
        description: '卡普空华丽动作的巅峰。尼禄、但丁与 V 三条线索交汇，风格评分系统鼓励你打出最花哨的连段。RE 引擎画面惊艳，「Jackpot！」——动作游戏玩家的爽感天花板。',
        release_date: '2019-03-08', category_id: 3, tags: ['动作', '华丽', '砍杀', '单人'],
        average_score: 9.0, is_online: true, hot: 74, created_at: d(350) },
      { id: 21, name: '怪物猎人：世界', name_en: 'Monster Hunter: World', developer: 'Capcom',
        cover_url: STEAM(582010),
        description: '卡普空共斗狩猎的集大成之作。在新大陆追踪、讨伐数十种巨型怪物，用素材打造武器装备。14 种武器风格迥异，无缝地图与生态演出让狩猎沉浸感空前，极适合与好友联机。',
        release_date: '2018-08-09', category_id: 3, tags: ['动作', '合作', '狩猎', '共斗'],
        average_score: 8.9, is_online: true, hot: 86, created_at: d(400) },
      { id: 22, name: '死亡细胞', name_en: 'Dead Cells', developer: 'Motion Twin',
        cover_url: STEAM(588650),
        description: '法国独立团队打造的类银河恶魔城 Roguelike。每次死亡都从零开始，但永久解锁的武器与细胞让你越变越强。快节奏的翻滚招架与海量武器 Build，被称为「类 Rogue 与银河恶魔城的完美联姻」。',
        release_date: '2018-08-07', category_id: 3, tags: ['Roguelike', '像素', '动作', '类银河恶魔城'],
        average_score: 9.0, is_online: true, hot: 73, created_at: d(390) },
      { id: 23, name: '侠盗猎车手 5', name_en: 'Grand Theft Auto V', developer: 'Rockstar Games',
        cover_url: STEAM(271590),
        description: 'R 星的洛圣都犯罪史诗。麦克、富兰克林、崔佛三主角交错叙事，这座城市本身就是最棒的沙盒游乐场。剧情模式与长青的 GTA Online 让它成为史上销量最高的游戏之一。',
        release_date: '2015-04-14', category_id: 4, tags: ['开放世界', '犯罪', '多人', '动作'],
        average_score: 8.6, is_online: true, hot: 93, created_at: d(550) },
      { id: 24, name: '霍格沃茨之遗', name_en: 'Hogwarts Legacy', developer: 'Avalanche Software',
        cover_url: STEAM(990080),
        description: '哈利波特世界的开放世界动作 RPG。故事设定在 19 世纪的霍格沃茨，你是掌握古代魔法的五年级转学生。分院、上课、骑扫帚、驯服神奇动物，哈迷梦寐以求的魔法学生活。',
        release_date: '2023-02-10', category_id: 4, tags: ['魔法', '开放世界', '奇幻', '哈利波特'],
        average_score: 8.2, is_online: true, hot: 81, created_at: d(200) },
      { id: 25, name: '地平线：零之曙光', name_en: 'Horizon Zero Dawn Complete Edition', developer: 'Guerrilla Games',
        cover_url: STEAM(1151640),
        description: '游击队打造的后启示录开放世界。人类文明退化为部落，巨型机械兽统治大地。红发猎人埃洛伊用弓箭与绊线狩猎机械恐龙，揭开旧世界毁灭的惊人真相。',
        release_date: '2020-08-07', category_id: 4, tags: ['开放世界', '动作RPG', '科幻', '女主角'],
        average_score: 8.5, is_online: true, hot: 68, created_at: d(240) },
      { id: 26, name: '死亡搁浅', name_en: 'Death Stranding', developer: 'Kojima Productions',
        cover_url: STEAM(1190460),
        description: '小岛秀夫独立后的首款作品。在死亡搁浅后的美国，快递员山姆背着货物穿越 BT 出没的荒野，连接孤立的节点。一款关于「送货」与「连接」的奇特游戏，喜欢的人会深深着迷。',
        release_date: '2020-07-14', category_id: 4, tags: ['开放世界', '剧情', '步行模拟', '科幻'],
        average_score: 8.8, is_online: true, hot: 77, created_at: d(220) },
      { id: 27, name: '城市：天际线', name_en: 'Cities: Skylines', developer: 'Colossal Order',
        cover_url: STEAM(255710),
        description: '现代城市建设模拟的王者。规划道路、分区、公共交通与公共服务，看着小村庄成长为百万人口都市。堵车治理是每位市长的必修课，MOD 生态让玩法无限延伸。',
        release_date: '2015-03-10', category_id: 5, tags: ['城市建设', '模拟', '管理', '沙盒'],
        average_score: 8.8, is_online: true, hot: 71, created_at: d(520) },
      { id: 28, name: '环世界', name_en: 'RimWorld', developer: 'Ludeon Studios',
        cover_url: STEAM(294100),
        description: 'AI 故事讲述者驱动的殖民地模拟。三个流坠异星的幸存者从零建家、抵御袭击、应对瘟疫与心灵飞船。每个殖民者都有背景故事与情绪，事故永远比计划精彩——「再来一天就睡觉」。',
        release_date: '2018-10-17', category_id: 5, tags: ['殖民模拟', '生存', '沙盒', '剧情'],
        average_score: 9.3, is_online: true, hot: 80, created_at: d(330) },
      { id: 29, name: 'XCOM 2', name_en: 'XCOM 2', developer: 'Firaxis Games',
        cover_url: STEAM(268500),
        description: 'Firaxis 的回合制战棋神作。外星人统治地球 20 年后，你指挥 XCOM 游击队打响反击战。命中率 99% 也会 miss 的紧张感、永久死亡的队员培养与基地建设，让人又爱又恨。',
        release_date: '2016-02-05', category_id: 6, tags: ['回合制', '策略', '战棋', '科幻'],
        average_score: 8.6, is_online: true, hot: 69, created_at: d(560) },
      { id: 30, name: '尘埃拉力赛 2.0', name_en: 'DiRT Rally 2.0', developer: 'Codemasters',
        cover_url: STEAM(690790),
        description: 'Codemasters 最硬核的拉力赛拟真游戏。在威尔士泥泞、阿根廷碎石与芬兰飞跳中控制失控边缘的拉力车，领航员的路书就是你的生命。没有辅助线，没有回头路，献给真正的驾驶爱好者。',
        release_date: '2019-02-26', category_id: 7, tags: ['拉力赛', '竞速', '拟真', '赛车'],
        average_score: 8.4, is_online: true, hot: 62, created_at: d(300) }
    ];

    /* 派生字段：steam_url（由封面 appid 推导）+ 四维维度评分（均值=综合分，与后端种子聚合口径一致） */
    (function () {
      function clamp1(x) { return Math.round(Math.max(1, Math.min(10, x)) * 10) / 10; }
      games.forEach(function (g) {
        var am = g.cover_url.match(/apps\/(\d+)/);
        g.steam_url = am ? 'https://store.steampowered.com/app/' + am[1] + '/' : '';
        var avg = g.average_score;
        var s1 = avg + ((g.id % 3) - 1) * 0.4;
        var s2 = avg + (((g.id + 1) % 3) - 1) * 0.3;
        var s3 = avg + (((g.id + 2) % 3) - 1) * 0.2;
        var s4 = avg * 4 - s1 - s2 - s3;
        g.score_story = clamp1(s1);
        g.score_graphic = clamp1(s2);
        g.score_gameplay = clamp1(s3);
        g.score_opt = clamp1(s4);
        /* rating_count / average_score 由底部聚合重算：带四维分的公开评测 + 用户评分合并 */
      });
    })();

    var users = [
      { id: 1, username: 'admin', email: 'admin@game.local', password: 'admin123', role: 'admin', is_active: true, created_at: d(900),
        profile: { nickname: '平台管理员', avatar: '', bio: '游戏社区官方管理员账号' } },
      { id: 2, username: 'creator', email: 'creator@game.local', password: 'creator123', role: 'creator', is_active: true, created_at: d(800),
        profile: { nickname: '硬核评测君', avatar: '', bio: '十年游戏龄，只写有态度的评测。' } },
      { id: 3, username: 'player', email: 'player@game.local', password: 'player123', role: 'player', is_active: true, created_at: d(700),
        profile: { nickname: '休闲玩家小P', avatar: '', bio: '周末打游戏的社畜一枚' } },
      { id: 4, username: 'player02', email: 'p02@game.local', password: '123456', role: 'player', is_active: true, created_at: d(300),
        profile: { nickname: '夜行者', avatar: '', bio: '单机剧情党' } },
      { id: 5, username: 'writer_lily', email: 'lily@game.local', password: '123456', role: 'creator', is_active: true, created_at: d(260),
        profile: { nickname: '莉莉的游戏簿', avatar: '', bio: '偏爱独立游戏与叙事作品' } },
      { id: 6, username: 'bad_guy', email: 'bad@game.local', password: '123456', role: 'player', is_active: false, created_at: d(120),
        profile: { nickname: '引战小号', avatar: '', bio: '' } },
      { id: 7, username: 'new_man', email: 'new@game.local', password: '123456', role: 'player', is_active: true, created_at: d(10),
        profile: { nickname: '萌新', avatar: '', bio: '' } }
    ];

    var reviews = [
      { id: 1, game_id: 1, user_id: 2, title: '《艾尔登法环》深度评测：开放世界与魂系的完美融合',
        content: '<h2>总评：9.6 分，年度最佳实至名归</h2><p>当 FromSoftware 决定做开放世界，所有人都担心魂系的精雕细琢会被稀释。事实证明，交界地的每一寸土地都藏着惊喜。</p><h2>一、开放世界的新范式</h2><p>没有问号轰炸地图，没有公式化据点。你远远看到一座破屋，走近可能是一段支线；远远看到一棵金色巨树，那就是你几十个小时后的终点。探索的驱动力完全来自好奇心本身。</p><h2>二、战斗与 Build</h2><p>战灰系统让武器构筑空前自由，法师、双刀、大曲剑各有爽点。Boss 战依然是 FS 的看家本领，碎星拉塔恩的演出堪称系列之最。</p><h2>三、缺点</h2><p>后期天空城与圣树的难度曲线陡峭，PC 版初期优化一般。</p><p>总而言之，这是献给所有热爱探索的玩家的一封情书。</p>',
        tags: ['魂系', '年度游戏'], status: 'published', audit_status: 'passed', audit_score: 8, audit_reason: '',
        read_count: 12350, like_count: 866, fav_count: 412, created_at: d(120) },
      { id: 2, game_id: 2, user_id: 5, title: '《博德之门3》：CRPG 的新黄金标准',
        content: '<h2>总评：9.7 分</h2><p>拉瑞安用 5e 规则证明了一件事：回合制可以比动作游戏更爽快。第一章的林地攻防战就足以让大多数 RPG 黯然失色。</p><p>最惊人的是自由度——你可以和敌人谈判、把 Boss 推下悬崖、甚至和反派谈恋爱。编剧对「玩家想干什么」的回应几乎没有死角。</p><p>如果你只玩一款 2023 年的游戏，就是它。</p>',
        tags: ['CRPG', '剧情'], status: 'published', audit_status: 'passed', audit_score: 5, audit_reason: '',
        read_count: 9820, like_count: 743, fav_count: 356, created_at: d(90) },
      { id: 3, game_id: 3, user_id: 2, title: '《黑神话：悟空》通关评测：国产 3A 的里程碑',
        content: '<h2>总评：9.3 分</h2><p>天命人走出花果山的那一刻，中国玩家等了很多年。</p><p>战斗系统上，劈棍、立棍、戳棍三架势切换流畅，七十二变与法术让 Boss 战充满解法。美术更是无可争议的世界级——小雷音寺的金顶、紫云山的丹霞，每一帧都能当壁纸。</p><p>短板在于地图引导偏弱、结局叙事见仁见智。但它证明了：中国人做 3A，能成。</p>',
        tags: ['国产', '3A'], status: 'published', audit_status: 'passed', audit_score: 6, audit_reason: '',
        read_count: 28600, like_count: 2100, fav_count: 980, created_at: d(60) },
      { id: 4, game_id: 8, user_id: 5, title: '《哈迪斯》评测：死了一千次还想再来一把',
        content: '<h2>总评：9.2 分</h2><p>Roguelike 最爽的节奏被 Supergiant 彻底摸透。15 分钟一局，每局都有新 Build，每次死亡都推进剧情。</p><p>众神祝福的组合拳、信物系统、镜子天赋，成长曲线层层嵌套。全程配音的希腊神明个个性格鲜明。</p>',
        tags: ['Roguelike', '独立游戏'], status: 'published', audit_status: 'passed', audit_score: 3, audit_reason: '',
        read_count: 6420, like_count: 521, fav_count: 230, created_at: d(80) },
      { id: 5, game_id: 9, user_id: 2, title: '《星露谷物语》：治愈一切的像素田园',
        content: '<h2>总评：9.5 分</h2><p>春种秋收，养鸡钓鱼，和镇民聊天跳舞。星露谷的厉害之处在于它没有目标——你想怎么活就怎么活。</p><p>下班之后打开游戏浇浇花，现实里的焦虑就被治愈了。</p>',
        tags: ['治愈', '模拟'], status: 'published', audit_status: 'passed', audit_score: 2, audit_reason: '',
        read_count: 5310, like_count: 467, fav_count: 310, created_at: d(70) },
      { id: 6, game_id: 12, user_id: 5, title: '《空洞骑士》：圣巢之下，皆是悲歌',
        content: '<h2>总评：9.4 分</h2><p>手绘的虫子王国里，每一个 NPC 都有令人心碎的故事。</p><p>地图设计是教科书级别的 interconnected world，一门之隔常常是两个区域。Boss 战难度硬核但公平，辐辉级等你挑战。</p>',
        tags: ['银河恶魔城', '独立游戏'], status: 'published', audit_status: 'passed', audit_score: 4, audit_reason: '',
        read_count: 7240, like_count: 689, fav_count: 401, created_at: d(55) },
      { id: 7, game_id: 4, user_id: 2, title: '《赛博朋克2077》：夜之城漫步指南',
        content: '<h2>从口碑崩盘到涅槃重生</h2><p>2.0 更新与往日之影 DLC 之后，夜之城终于兑现了最初的承诺。义体 Build 玩法深度大增，V 的故事依然是 CDPR 最擅长的那杯烈酒。</p><p>建议：一定要做完帕南线和朱迪线。</p>',
        tags: ['赛博朋克', '开放世界'], status: 'manual_review', audit_status: 'manual_review', audit_score: 62, audit_reason: 'AI 判定存在疑似引战表述，建议人工复核',
        read_count: 0, like_count: 0, fav_count: 0, created_at: d(3) },
      { id: 8, game_id: 7, user_id: 2, title: 'CS2 新手必看！加群领皮肤攻略',
        content: '<p>新手玩家快来，加群 xxx-xxx-xxx 免费领皮肤，还有代购打折游戏，微信 vx_xxxxxx 联系我！</p>',
        tags: [], status: 'rejected', audit_status: 'rejected', audit_score: 92, audit_reason: 'AI 审核驳回：检测到广告引流内容（加群/联系方式），违反社区内容规范',
        read_count: 0, like_count: 0, fav_count: 0, created_at: d(6) },
      { id: 9, game_id: 6, user_id: 2, title: '《巫师3》二周目：猎魔人的自我修养（草稿）',
        content: '<h2>二周目才懂的细节</h2><p>（草稿，未完待续……）血腥男爵线第一次玩只觉得震撼，二周目才发现每个选择都有伏线……</p>',
        tags: ['剧情'], status: 'draft', audit_status: null, audit_score: null, audit_reason: '',
        read_count: 0, like_count: 0, fav_count: 0, created_at: d(2) },
      { id: 10, game_id: 5, user_id: 5, title: '《大镖客2》细节考据：R星的西部有多真实',
        content: '<p>亚瑟的胡子会生长、马会受惊、路过的NPC会记住你……这篇图文整理了 30 个令人发指的细节。</p>',
        tags: ['考据', '开放世界'], status: 'published', audit_status: 'passed', audit_score: 7, audit_reason: '',
        read_count: 8900, like_count: 712, fav_count: 388, created_at: d(45) }
    ];

    /* 评测四维评分（1-10 整数）：依据游戏综合分派生，公开评测才有分数 */
    (function () {
      function clamp10(x) { return Math.max(1, Math.min(10, Math.round(x))); }
      var gm = {};
      games.forEach(function (g) { gm[g.id] = g.average_score; });
      reviews.forEach(function (r) {
        if (r.status !== 'published') { r.score_story = r.score_graphic = r.score_gameplay = r.score_opt = null; return; }
        var avg = gm[r.game_id] || 8;
        r.score_story = clamp10(avg + ((r.id % 3) - 1) * 0.6);
        r.score_graphic = clamp10(avg + (((r.id + 1) % 3) - 1) * 0.5);
        r.score_gameplay = clamp10(avg + (((r.id + 2) % 3) - 1) * 0.4);
        r.score_opt = clamp10(avg + (((r.id + 3) % 3) - 1) * 0.7);
      });
    })();

    /* ---- 用户游戏评分（1-10 分）：每款游戏 2-3 名用户，同一用户对单款游戏仅一条，与后端种子口径一致 ---- */
    var ratings = (function () {
      var authors = [3, 4, 7, 2, 5];
      var out = [];
      games.forEach(function (g) {
        var base = Math.max(6, Math.min(10, Math.round(g.average_score)));
        var cnt = 2 + g.id % 2;
        for (var k = 0; k < cnt; k++) {
          out.push({ id: out.length + 1, game_id: g.id, user_id: authors[(g.id * 2 + k) % authors.length],
            score: Math.max(1, Math.min(10, base + ((g.id + k) % 3) - 1)),
            created_at: d(5 + (g.id + k * 3) % 25), updated_at: d(5 + (g.id + k * 3) % 25) });
        }
      });
      return out;
    })();
    /* 聚合重算：综合分/参与人数 = 带四维分的公开评测 + 用户评分合并（recalcGame 声明提升，可在此调用） */
    games.forEach(function (g) { recalcGame({ games: games, reviews: reviews, ratings: ratings }, g.id); });

    var comments = [
      { id: 1, user_id: 3, target_type: 'review', target_id: 1, parent_id: null, content: '碎星那一战我打了整整一下午，过的时候手都在抖！', like_count: 45, created_at: d(119), likes: [] },
      { id: 2, user_id: 4, target_type: 'review', target_id: 1, parent_id: 1, content: '同感！拉塔恩的 BGM 一响直接头皮发麻', like_count: 12, created_at: d(118), likes: [] },
      { id: 3, user_id: 7, target_type: 'review', target_id: 1, parent_id: null, content: '请问新手适合玩法师还是近战呀？', like_count: 3, created_at: d(110), likes: [] },
      { id: 4, user_id: 2, target_type: 'review', target_id: 1, parent_id: 3, content: '新手强烈推荐观星者，远程法术容错率高~', like_count: 20, created_at: d(109), likes: [] },
      { id: 5, user_id: 3, target_type: 'review', target_id: 3, content: '黑神话首发日我请假在家玩了一整天，值了！', like_count: 88, created_at: d(59), likes: [] },
      { id: 6, user_id: 4, target_type: 'review', target_id: 2, content: '影心是我老婆，不接受反驳。', like_count: 34, created_at: d(88), likes: [] }
    ];

    /* ---- 游戏评论：每款游戏 1 条高质量长评（≥50字，紧扣游戏具体内容+个人体验，点赞最高时被自动选为精选）+ 5-10 条差异化普通短评 ---- */
    (function () {
      // 长评：人工撰写，每条均提及玩法/剧情/关卡/BOSS/画面/机制中至少一项，并带个人真实游玩感受，满足自动精选全部条件
      var featuredTexts = [
        '交界地的开放世界设计太妙了，我骑着灵马在宁姆格福闲逛，随便摸进一个地下监牢都能挖出一套新的 build。碎星拉塔恩那场 BOSS 战我打了整整两天，召唤一众 NPC 一起冲锋时热血沸腾，八十小时通关还舍不得进二周目。',
        '拉瑞安把 DND 5e 规则做得一点都不枯燥，我队里游荡者偷袭接战士借机攻击的连招屡试不爽。第一章地精营地是屠村还是谈判让我纠结了半小时，影心的个人剧情一路反转，通关后看队友各奔东西居然有点鼻酸，年度游戏实至名归。',
        '国产 3A 能有这个完成度真的感动。金箍棒轻重棍势切换的手感扎实，黄风大圣那关我在风沙里死了十几次才摸清出招节奏，小西天的壁画场景美得舍不得走。三十小时通关，部分关卡锁视角和后期数值是硬伤，但瑕不掩瑜。',
        '更新到 2.0 之后完全是另一个游戏。义体过载配沙鹰暴击的 build 让最高难度也能横着走，夜之城雨夜街头的霓虹画面配上叛逆电台的音乐，代入感直接拉满。杰克葬礼那段剧情我一个老玩家居然红了眼，六十小时主线打完还在满城清问号。',
        'R 星对细节的偏执到了可怕的程度，马蹄踩在泥地里会留下深浅不一的印子，亚瑟几天不刮胡子就疯长。第六章雪山那场决战配上达奇的台词，剧情后劲大得我通关一周没点开别的游戏。节奏慢是真的，但沉浸感也是真的无人能敌。',
        '杰洛特找希里这条主线的叙事节奏太好了，血腥男爵任务里沼泽三女巫的支线我至今记得清清楚楚。次世代更新后威伦的草甸和诺维格瑞的雨天画面焕然新生，昆特牌我打到忘了推进主线，两百小时还没清完问号。',
        '起源 2 引擎的烟雾弹是真的物理，烟雾会被手雷炸开缺口再慢慢回流，Inferno 香蕉道丢烟抢点的战术深度一下就上来了。亚秒级服务器打起来手感丝滑，我和车队在炙热沙城二排了一整晚，就是偶尔匹配到实力差距大的局，希望 V 社继续打磨反作弊。',
        'Roguelike 最怕重复，但哈迪斯每次死亡回大厅听众神唠嗑都有新台词，扎格列欧斯和冥后的家庭剧我追了五十局。雅典娜反弹盾配海神击飞特效清屏特别爽，信物系统让每局 build 都不一样，OST 好听到我单独买了专辑。',
        '下班回家浇浇地钓钓鱼，星露谷的像素画面配上季节变化的 BGM，比什么解压神器都管用。我第二年秋天娶了潘妮，温室种满上古水果后躺着数钱，和朋友联机四个人分工种地挖矿效率翻倍，不知不觉就肝到凌晨两点。',
        '「再来一回合就睡觉」是真的，等我打完这把宗教胜利天都亮了。区域相邻加成的机制很讲究，学院靠山、剧院靠奇观的布局我能研究半小时，秦始皇长城流铺城又稳又爽。AI 后期外交有点神经质，但策略深度足够我再玩几百小时。',
        '墨西哥这张地图的季节变换做得太美了，雨季丛林里的泥地拉力和旱季火山口的下坡冲刺完全是两种手感。四百多辆车的改装调校能折腾一整天，方向盘打起来手感细腻，周末和朋友联机跑环岛赛吹水，休闲竞速天花板。',
        '等丝之歌等得我把空洞骑士又通了一遍。圣巢的手绘美术配上低沉的钢琴配乐，在泪水之城听雨那段氛围绝了。格林团长的 BOSS 战拼反应拼到手指发酸，苦痛之路我跳了四个小时才过，硬核但每次死亡都觉得是自己菜，不是游戏不公平。',
        '最早一批吃鸡玩家，机场 C 字楼落地成盒几十把才学会听声辨位。缩圈机制带来的紧张感至今没有同类能替代，最后一圈趴在草里和对面拼药时肾上腺素飙升，和车队四排连麦喊到嗓子哑。虽然现在外挂问题头疼，但情怀分必须给满。',
        'Respawn 的射击手感真是行业顶尖，滑铲接绳索转点的机动性一旦习惯就回不去了。我主玩寻血犬，扫描开 Q 突脸的节奏特别上头，世界边缘那张图的碎片东区落地架百玩不腻。新赛季平衡性偶尔翻车，但和队友排位冲分的爽感还是独一档。',
        '这游戏把 FPS 的战斗节奏推到了极致，荣耀击杀回血、电锯回弹的机制逼你全程贴脸输出，根本没机会蹲掩体。重金属 BGM 一响恶魔再多人也敢冲，地狱关卡的平台跳跃略硬核，但整体爽快感是我玩过所有射击游戏里最纯粹的。',
        '十年老滚玩家表示特别版的 64 位稳定性和高清材质让重开体验舒服太多。我这档走潜弓流，蹲在遗迹阴影里一箭秒掉尸鬼大君的爽感百试不厌，盗贼公会和黑暗兄弟会的支线叙事比主线还抓人。膝盖中箭梗玩了十年，天际省还是逛不腻。',
        '废土波士顿的黑色幽默太对我胃口了，和狗肉一起在发光海捡垃圾建据点，几百小时就没推过多少主线。穿上动力装甲踩死死亡爪的瞬间值回票价，VATS 慢动作轰掉超变变种人脑袋百看不厌。对话选择比新维加斯浅是遗憾，但建设系统让人上瘾。',
        '薛帕德三部曲的剧情厚度在 RPG 里独一档，从一代救议会到三代结局抉择，盖拉斯的忠诚任务我每次重玩都认真做完。传奇版把一代的操作和画面翻新后流畅多了，诺曼底号上和队友聊天的日常比打仗还让人怀念，太空歌剧巅峰。',
        '拼刀弹反的机制太上头了，叮的一声完美格挡比什么奖励都爽。苇名弦一郎我卡了三个晚上，最后无伤过他第三阶段时手心全是汗。义手忍具爆竹克野兽、伞克雷的克制设计很讲究，苇名城的红叶和雪景像浮世绘，年度游戏不冤。',
        '卡普空的动作手感从没让人失望，尼禄红刀配机械手的连段越打越花，风格评分从 D 刷到 SSS 的过程就是对玩家最好的奖励。RE 引擎下但丁的建模精细到胡茬，V 召唤魔兽走位输出的玩法很新鲜，二周目上手但丁直接爽到飞起。',
        '十四种武器真的是十四种玩法，我太刀见切斩练了上百小时，砍中灭尽龙白棘倒地的瞬间成就感爆棚。冰原的冰咒龙套配冥赤龙武器刷到天昏地暗，无缝地图里怪物互殴的生态演出像在看纪录片，和好友四人组队狩猎的共斗乐趣无可替代。',
        '快节奏的翻滚招架一旦上头根本停不下来，每局随机的武器组合逼你临场换套路，巨人崛起 DLC 的稻草人 BOSS 我死了快二十次。永久解锁的细胞和锻造所让菜鸡也能慢慢滚雪球，二细胞难度开始才是真正的开始，像素画面配管弦乐意外地带感。',
        '三主角切换叙事是 R 星最聪明的设计，崔佛疯、麦克怂、富兰克林稳，珠宝店劫案的前置任务我反复玩了三遍。洛圣都的街头细节密度惊人，堵车时听电台、半夜开上山看夜景都能打发时间，线上模式和朋友抢赌场劫案笑到肚子痛，长青不是没道理。',
        '收到猫头鹰信那一刻哈迷直接泪目，分院帽分我进格兰芬多后，在城堡里爬楼梯找移动教室的还原度满分。古代魔法的终结技演出华丽，骑着扫帚在禁林边打黑巫师边看海格小屋，画面美得像在电影里。后期重复度偏高，但魔法课和有求必应屋养神奇动物够我沉迷很久。',
        '机械兽的设定太有想象力了，用绊线和绳索陷阱狩猎雷霆牙的打法完全是另一个怪物猎人。埃洛伊这个红发女猎人的塑造很有魅力，旧世界毁灭真相的剧情在全息记录里一点点拼出来特别抓人，Decima 引擎的画面在开放世界里绝对第一梯队，坐等续作上 PC。',
        '一开始以为是走路模拟器，结果背货规划路线的机制意外上瘾，在 BT 区和米尔人之间铺快递网络越铺越有成就感。开罗尔网络连上网、高速公路一段段修通时，真的能体会到小岛想表达的连接。剧情后半段亚美莉的反转后劲很大，和 BB 的互动细节也戳人。',
        '治堵车是每位市长的毕业考，我拆掉高速入口改成单行道加公交分流后，看着全城车流变成绿色畅通，满足感爆棚。公园生活和工业 DLC 的供应链能玩出花来，工坊 MOD 打了六十多个还在加，规划党杀时间神器，新建的城市一不小心就到了后半夜。',
        '三个坠机幸存者开局，我眼睁睁看着厨师精神崩溃把仓库点了，AI 故事讲述者的随机性比编剧还敢写。殖民地防御从木栅栏滚到自动炮塔的过程特别上头，MOD 生态直接把玩法翻倍，冷库供电、小人心情、袭击波次要操心的事太多，再来一天就睡觉。',
        '命中率 99% 贴脸 miss 是 XCOM 玩家的共同创伤，但也正是这种压力让每次战术决策都惊心动魄。我王牌狙击手中毒阵亡后直接读档半小时，兵种搭配和掩体推进的战棋机制堪称教科书，化身计划倒计时逼着你取舍，基地建设加人员养成让人又爱又恨。',
        '拟真拉力赛的硬核程度超出想象，没有辅助线没有回头路，全靠领航员的路书提前判断弯道。威尔士雨夜里轮胎在泥地上打滑的触感、芬兰飞跳落地时悬挂的反馈，用方向盘玩真的会哭。新手被劝退是常态，但一圈完美跑完赛段的成就感，比任何娱乐向赛车都强。'
      ];
      // 普通短评：片段池组合生成（参考 Steam/TapTap 短评风格改写），全局去重，禁止复制粘贴
      var ncOpeners = [
        '打折入的，', '观望了很久才买，', '朋友安利来的，', '刷实况被种草，',
        '原价入手的，', '玩了三十小时，', '刚通关一周目，', '趁假期肝完了，',
        '作为休闲玩家，', '剧情党路过，', '冲着美术来的，', '上班摸鱼玩的，',
        '等了好久终于打折，', '老粉直接入了，'
      ];
      var ncMiddles = [
        '越玩越上头', '战斗手感相当扎实', '剧情演出值回票价', 'BOSS 战机制很有创意',
        '美术风格太对味了', '音乐好听到单曲循环', '地图探索处处有惊喜', '配装流派能研究很久',
        '支线质量比主线还高', '优化好到低配也能流畅跑', '节奏紧凑不拖沓', '关卡设计环环相扣',
        '重玩价值很高', '氛围沉浸感拉满', '难度选项对新手友好', '角色塑造个个鲜活',
        '结局反转让人没想到', '技能搭配套路很多', '开放世界内容塞得很满', '解谜部分恰到好处',
        '后期数值有点膨胀', '教程引导略显啰嗦', '联机偶尔掉线有点烦', '地图大但填充略重复',
        '死亡惩罚有点劝退', '前期节奏偏慢热', '偶尔遇到点穿模 BUG', '高难度下比较受苦',
        'DLC 定价偏高', '剧情后半段收得有点仓促'
      ];
      var ncEndings = [
        '。', '总体推荐。', '个人给好评。', '已经安利给朋友了。', '瑕不掩瑜吧。',
        '会再开二周目。', '期待后续更新。', '比预期好玩。', '通宵警告。',
        '建议打折入手。', '新手记得先调难度。', '玩着玩着天就亮了。', '值这个价。', '欢迎讨论。'
      ];
      var comboTotal = ncOpeners.length * ncMiddles.length * ncEndings.length;
      var usedTexts = {};
      function normalText(seq) {
        var i = seq % comboTotal;
        while (usedTexts[i]) i = (i + 1) % comboTotal;  // 全局唯一，杜绝重复评论
        usedTexts[i] = true;
        var o = Math.floor(i / (ncMiddles.length * ncEndings.length));
        var r = i % (ncMiddles.length * ncEndings.length);
        var mi = Math.floor(r / ncEndings.length);
        var ei = r % ncEndings.length;
        return ncOpeners[o] + ncMiddles[mi] + ncEndings[ei];
      }
      var featuredAuthors = [2, 5, 4, 3];
      var normalAuthors = [3, 4, 7, 5, 2, 4, 7, 3];
      var cid = 7;
      var nseq = 0;
      games.forEach(function (g) {
        var gid = g.id;
        var fa = featuredAuthors[(gid - 1) % 4];
        comments.push({
          id: cid, user_id: fa, target_type: 'game', target_id: gid, parent_id: null,
          content: featuredTexts[gid - 1],
          like_count: 25 + (gid * 7) % 65,
          created_at: d(20 + (gid % 8)),
          likes: [7, 4, 3].filter(function (u) { return u !== fa; }).slice(0, 2)
        });
        cid++;
        var normalCount = 5 + gid % 6;  // 每款游戏 5-10 条普通评论
        for (var k = 0; k < normalCount; k++) {
          var na = normalAuthors[(gid * 3 + k) % normalAuthors.length];
          var nLikes = (k % 3 === 1) ? [2, 3, 7].filter(function (u) { return u !== na; }).slice(0, 1) : [];
          comments.push({
            id: cid, user_id: na, target_type: 'game', target_id: gid, parent_id: null,
            content: normalText(nseq),
            like_count: (gid + k * 3) % 18,
            created_at: d(1 + (gid + k * 2) % 15), likes: nLikes
          });
          nseq++;
          cid++;
        }
      });
    })();

    var favorites = [
      { id: 1, user_id: 3, game_id: 1, created_at: d(200) },
      { id: 2, user_id: 3, game_id: 2, created_at: d(150) },
      { id: 3, user_id: 3, game_id: 3, created_at: d(59) },
      { id: 4, user_id: 2, game_id: 6, created_at: d(300) }
    ];

    var records = [
      { id: 1, user_id: 3, game_id: 6, play_status: 'completed', created_at: d(180), updated_at: d(100) },
      { id: 2, user_id: 3, game_id: 8, play_status: 'playing', created_at: d(90), updated_at: d(5) },
      { id: 3, user_id: 3, game_id: 9, play_status: 'want', created_at: d(30), updated_at: d(30) }
    ];

    var applies = [
      { id: 1, user_id: 7, apply_reason: '我是游戏媒体撰稿人，想在平台发布 Steam 游戏评测，之前运营过个人游戏公众号。', status: 'pending', audit_user_id: null, created_at: d(2) },
      { id: 2, user_id: 4, apply_reason: '单机游戏通关 200+，想写点东西分享。', status: 'pending', audit_user_id: null, created_at: d(1) }
    ];

    var auditLogs = [
      { id: 1, review_id: 8, audit_type: 'ai', risk_score: 92, reason: '命中广告引流：检测到"加群""微信 vx"等联系方式导流片段', operator_id: 1, created_at: d(6) },
      { id: 2, review_id: 7, audit_type: 'ai', risk_score: 62, reason: '疑似引战争议表述："某游戏就是垃圾"类对比引战，需人工判断', operator_id: 1, created_at: d(3) },
      { id: 3, review_id: 3, audit_type: 'ai', risk_score: 6, reason: '内容正常，未命中风险维度', operator_id: 1, created_at: d(60) }
    ];

    /* ---------- 社区模块种子数据 ---------- */
    function cp(id, uid, title, content, tag, days, imgs) {
      return { id: id, user_id: uid, title: title, content: content, tag: tag,
        images: imgs || [], view_count: 100 + id * 17, like_count: 0, fav_count: 0,
        comment_count: 0, hot_score: 0, created_at: d(days), updated_at: d(days) };
    }
    var communityPosts = [
      cp(1, 2, '《黑神话：悟空》黄风岭隐藏boss打法攻略', '黄风岭的石敢当和虎先锋很多人卡关，分享一套稳过的配装与走位思路：先备满定身咒，注意boss的三连抓前摇……', '攻略', 1, ['https://cdn.cloudflare.steamstatic.com/steam/apps/2358720/header.jpg']),
      cp(2, 3, '周末开黑招募，来点人一起肝', '周末晚上八点开黑，主玩联机合作，新手老手都欢迎，评论区举手～', '闲聊', 0),
      cp(3, 4, '艾尔登法环全追忆boss无伤要点', 'DLC 黄金树幽影的几个 boss 伤害真的离谱，分享一下无伤心得和逃课套路。', '攻略', 2),
      cp(4, 5, '最近这游戏定价真的离谱，吐槽一下', '等了半年的游戏首发就这优化，帧数崩成 PPT，价格倒是很自信。', '吐槽', 0),
      cp(5, 7, '萌新第一次玩魂类，被教育了', '看大家推荐入了魂3，古达老师教我做人第 27 次，这游戏正常吗……', '闲聊', 1),
      cp(6, 2, '博德之门3强力build分享：一刀999', '分享一个战士兼职游荡者的build，前期就能成型，爆发拉满。', '攻略', 3),
      cp(7, 3, '独立游戏推荐：这款小品级神作别错过', '最近挖到一款像素风 roguelike，美术音乐玩法全在线，几十块玩了五十小时。', '游戏', 4, ['https://cdn.cloudflare.steamstatic.com/steam/apps/1145360/header.jpg']),
      cp(8, 4, '联机掉线重连能不能修修', '和朋友组队十分钟掉三次，体验极差，官方能不能管管。', '吐槽', 0)
    ];
    var postComments = [
      { id: 1, post_id: 1, user_id: 3, parent_id: null, content: '感谢分享，卡了一晚上终于过了！', like_count: 5, created_at: d(1) },
      { id: 2, post_id: 1, user_id: 4, parent_id: null, content: '补充：第二阶段记得留法术槽。', like_count: 2, created_at: d(1) },
      { id: 3, post_id: 1, user_id: 2, parent_id: 2, content: '对，二阶段雷属性抗性高，换物理更好打。', like_count: 3, created_at: d(1) },
      { id: 4, post_id: 2, user_id: 7, parent_id: null, content: '举手！我我我！', like_count: 1, created_at: d(0) },
      { id: 5, post_id: 5, user_id: 2, parent_id: null, content: '习惯就好，古达老师毕业率不足三成哈哈。', like_count: 8, created_at: d(1) }
    ];
    var postLikes = [
      { id: 1, post_id: 1, user_id: 3 }, { id: 2, post_id: 1, user_id: 4 },
      { id: 3, post_id: 5, user_id: 2 }, { id: 4, post_id: 7, user_id: 2 }
    ];
    var postFavs = [ { id: 1, post_id: 1, user_id: 3 }, { id: 2, post_id: 6, user_id: 7 } ];
    var postCommentLikes = [ { id: 1, comment_id: 5, user_id: 3 } ];
    var reports = [
      { id: 1, reporter_id: 3, target_type: 'post', target_id: 4, reason: '辱骂攻击',
        detail: '评论区引战', status: 'pending', handler_id: null, handle_note: null,
        created_at: d(0), handled_at: null }
    ];
    /* 回写冗余计数 */
    communityPosts.forEach(function (p) {
      p.like_count = postLikes.filter(function (l) { return l.post_id === p.id; }).length;
      p.fav_count = postFavs.filter(function (l) { return l.post_id === p.id; }).length;
      p.comment_count = postComments.filter(function (c) { return c.post_id === p.id; }).length;
      var ageH = Math.max(0.01, (Date.now() - new Date(p.created_at).getTime()) / 3600000);
      var base = p.like_count * 2 + p.fav_count * 3 + p.comment_count * 4 + p.view_count * 0.05;
      p.hot_score = Math.round(base / Math.pow(ageH + 2, 1.5) * 100) / 100;
    });

    /* ---- 创作者积分与等级（规则与后端 app/core/points.py 一致） ---- */
    var LEVEL_MIN = [0, 200, 500, 1200, 2500];
    function levelFor(pts) {
      var lv = 0;
      for (var i = 0; i < LEVEL_MIN.length; i++) if (pts >= LEVEL_MIN[i]) lv = i;
      return lv;
    }
    var pointRecords = [];
    var prSeq = 0;
    function addPoints(userId, change, reason, rid) {
      var u0 = users.filter(function (x) { return x.id === userId; })[0];
      if (!u0) return;
      u0.creator_points = Math.max(0, Math.round(((u0.creator_points || 0) + change) * 10) / 10);
      u0.creator_level = levelFor(u0.creator_points);
      pointRecords.push({
        id: ++prSeq, user_id: userId, change: Math.round(change * 10) / 10,
        reason: reason, related_type: rid ? 'review' : 'system', related_id: rid || null,
        balance_after: u0.creator_points, created_at: nowIso()
      });
    }
    reviews.forEach(function (r) {
      r.is_featured = r.status === 'published' && (r.id === 1 || r.id === 2 || r.id === 3);
      r.edit_used = false;
      r.likes = [];  // 点赞用户 id（与社区帖 likes 同构）
      r.favs = [];   // 收藏用户 id
    });
    users.forEach(function (u) { u.creator_points = 0; u.creator_level = 0; });
    reviews.filter(function (r) { return r.status === 'published'; }).forEach(function (r) {
      var u0 = users.filter(function (x) { return x.id === r.user_id; })[0];
      if (!u0 || u0.role === 'player') return;
      addPoints(r.user_id, 20, '评测《' + r.title + '》审核通过发布', r.id);
      if (r.is_featured) addPoints(r.user_id, 30, '评测《' + r.title + '》被管理员标记精选', r.id);
      if (r.like_count) addPoints(r.user_id, 0.2 * r.like_count, '评测《' + r.title + '》累计获赞 ' + r.like_count + ' 次', r.id);
      if (r.fav_count) addPoints(r.user_id, 0.5 * r.fav_count, '评测《' + r.title + '》累计被收藏 ' + r.fav_count + ' 次', r.id);
    });
    pointRecords.reverse();  // 最新在前

    return {
      seq: { users: 100, games: 100, reviews: 100, comments: 100, favorites: 100, records: 100, applies: 100, logs: 100, categories: 100, ratings: 100,
        communityPosts: 100, postComments: 100, postLikes: 100, postFavs: 100, postCommentLikes: 100, reports: 100, pointRecords: 1000 },
      users: users, categories: categories, games: games, reviews: reviews,
      comments: comments, favorites: favorites, records: records, applies: applies, auditLogs: auditLogs,
      ratings: ratings, pointRecords: pointRecords,
      communityPosts: communityPosts, postComments: postComments, postLikes: postLikes,
      postFavs: postFavs, postCommentLikes: postCommentLikes, reports: reports
    };
  }

  /* ---------- 存储 ---------- */
  function load() {
    try {
      var raw = localStorage.getItem(DB_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* ignore */ }
    var s = seed();
    localStorage.setItem(DB_KEY, JSON.stringify(s));
    return s;
  }
  function save(db) { localStorage.setItem(DB_KEY, JSON.stringify(db)); }
  function reset() { localStorage.removeItem(DB_KEY); return load(); }

  /* ---------- 工具 ---------- */
  function fail(status, message) { var e = new Error(message); e.status = status; e.message = message; throw e; }
  function nowIso() { return new Date().toISOString(); }
  function tokenOf(userId) { return 'mock.' + userId + '.' + btoa('game-community'); }
  function userIdFromToken(token) {
    if (!token || token.indexOf('mock.') !== 0) return null;
    var id = parseInt(token.split('.')[1], 10);
    return isNaN(id) ? null : id;
  }
  function publicUser(u) {
    return { id: u.id, username: u.username, email: u.email, role: u.role, is_active: u.is_active,
      created_at: u.created_at, profile: u.profile,
      creator_points: u.creator_points || 0, creator_level: u.creator_level || 0 };
  }
  /* 创作者等级（阈值与后端 app/core/points.py 一致） */
  function levelForPts(pts) {
    var min = [0, 200, 500, 1200, 2500], lv = 0;
    for (var i = 0; i < min.length; i++) if ((pts || 0) >= min[i]) lv = i;
    return lv;
  }
  /* 积分流水：变更余额、写流水、自动更新等级 */
  function addPointRecord(db, userId, change, reason, rid) {
    var u0 = db.users.filter(function (x) { return x.id === userId; })[0];
    if (!u0) return 0;
    u0.creator_points = Math.max(0, Math.round(((u0.creator_points || 0) + change) * 10) / 10);
    u0.creator_level = levelForPts(u0.creator_points);
    if (!db.pointRecords) db.pointRecords = [];
    db.pointRecords.unshift({
      id: ++db.seq.pointRecords, user_id: userId, change: Math.round(change * 10) / 10,
      reason: reason, related_type: rid ? 'review' : 'system', related_id: rid || null,
      balance_after: u0.creator_points, created_at: nowIso()
    });
    return u0.creator_points;
  }
  /* 工作台积分概览（结构对齐后端 pts.overview） */
  var LEVEL_DEFS = [
    { level: 0, level_code: 'L0', level_name: '见习创作者', level_color: 'gray', min_points: 0,
      benefit: '可发布评测；评测通过审核前不可发布已发布内容，已发布评测暂不可编辑' },
    { level: 1, level_code: 'L1', level_name: '普通创作者', level_color: 'blue', min_points: 200,
      benefit: '蓝色徽章；单篇已发布评测获得 1 次编辑权限' },
    { level: 2, level_code: 'L2', level_name: '优质创作者', level_color: 'purple', min_points: 500,
      benefit: '紫色徽章；评测列表排序加权；工作台可查看数据' },
    { level: 3, level_code: 'L3', level_name: '资深创作者', level_color: 'gold', min_points: 1200,
      benefit: '金色徽章；优质评测获得首页专题展示入口' },
    { level: 4, level_code: 'L4', level_name: '核心创作者', level_color: 'rainbow', min_points: 2500,
      benefit: '彩虹徽章；最高等级，全站专属展示' }
  ];
  function pointsOverview(points) {
    var lv = levelForPts(points);
    var info = LEVEL_DEFS[lv];
    var next = LEVEL_DEFS[lv + 1] || null;
    return {
      points: Math.round((points || 0) * 10) / 10, level: lv,
      level_code: info.level_code, level_name: info.level_name, level_color: info.level_color,
      benefit: info.benefit,
      next_level: next ? { level: next.level, level_code: next.level_code, level_name: next.level_name,
        min_points: next.min_points } : null,
      points_to_next: next ? Math.round((next.min_points - (points || 0)) * 10) / 10 : 0,
      is_max: !next,
      rules: [
        '评测审核通过发布 +20', '管理员标记精选 +30', '评测获赞 +0.2 / 次', '评测被收藏 +0.5 / 次',
        '评测被删除追回该篇全部积分并额外 -30', '抄袭违规下架：积分清零、等级重置 L0'
      ]
    };
  }
  function gameOut(g, db) {
    var cat = db.categories.filter(function (c) { return c.id === g.category_id; })[0];
    return Object.assign({}, g, { category_name: cat ? cat.name : '' });
  }
  function reviewOut(r, db) {
    var u = db.users.filter(function (x) { return x.id === r.user_id; })[0];
    var g = db.games.filter(function (x) { return x.id === r.game_id; })[0];
    return Object.assign({}, r, {
      author_name: u ? u.profile.nickname || u.username : '未知',
      author_avatar: u ? u.profile.avatar : '',
      author_level: u ? (u.creator_level || 0) : 0,
      is_featured: !!r.is_featured,
      edit_used: !!r.edit_used,
      game_name: g ? g.name : '',
      game_cover: g ? g.cover_url : ''
    });
  }
  /* 首页「游戏评测」专区卡片：游戏封面/名称 + 用户打分（四维均值）+ 摘要 + 时间 */
  function publicReviewCard(r, db) {
    var o = reviewOut(r, db);
    var dims = [r.score_story, r.score_graphic, r.score_gameplay, r.score_opt];
    var score = dims.every(function (d) { return d != null; })
      ? Math.round((dims[0] + dims[1] + dims[2] + dims[3]) / 4 * 10) / 10 : null;
    var text = (o.content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    return { id: o.id, game_id: o.game_id, title: o.title,
      game_name: o.game_name, game_cover: o.game_cover,
      author_name: o.author_name, author_avatar: o.author_avatar,
      author_level: o.author_level, is_featured: o.is_featured,
      score: score, summary: text.length > 80 ? text.slice(0, 80) + '…' : (text || '（暂无正文）'),
      created_at: o.created_at };
  }
  function commentOut(c, db) {
    var u = db.users.filter(function (x) { return x.id === c.user_id; })[0];
    return Object.assign({}, c, {
      author_name: u ? u.profile.nickname || u.username : '未知',
      liked: c.likes && c.likes.indexOf(c.__uid) >= 0
    });
  }

  /* ---------- 鉴权 ---------- */
  function authUser(db, headers) {
    var token = (headers.Authorization || headers.authorization || '').replace('Bearer ', '');
    var uid = userIdFromToken(token);
    var u = uid && db.users.filter(function (x) { return x.id === uid; })[0];
    if (!u) fail(401, '未登录或登录已过期');
    if (!u.is_active) fail(403, '账号已被封禁');
    return u;
  }
  function authOpt(db, headers) {
    var token = (headers.Authorization || headers.authorization || '').replace('Bearer ', '');
    var uid = userIdFromToken(token);
    return uid ? db.users.filter(function (x) { return x.id === uid; })[0] : null;
  }
  function requireRole(u, roles) {
    var order = { player: 1, creator: 2, admin: 3 };
    if (!u || order[u.role] < order[roles]) fail(403, '权限不足');
  }

  /* ---------- AI 内容审核（规则模拟 DeepSeek 审核） ---------- */
  function aiAudit(title, content) {
    var text = (title + ' ' + content).toLowerCase();
    var adWords = ['加群', '微信群', '微信', 'vx', 'qq群', 'qq群', '代购', '低价代充', '代充', 'http://', 'https://', '.com', '免费领', '领皮肤'];
    var abuseWords = ['傻逼', '垃圾游戏', '废物', '脑残', '滚出', '引战', '狗都不玩'];
    var hit = [];
    adWords.forEach(function (w) { if (text.indexOf(w.toLowerCase()) >= 0) hit.push('广告引流：命中"' + w + '"类导流内容'); });
    abuseWords.forEach(function (w) { if (text.indexOf(w) >= 0) hit.push('辱骂引战：命中"' + w + '"类攻击表述'); });
    if (hit.length && adWords.some(function (w) { return text.indexOf(w.toLowerCase()) >= 0; })) {
      return { status: 'rejected', risk_score: 85 + Math.min(10, hit.length * 3), reasons: hit };
    }
    if (hit.length) {
      return { status: 'manual_review', risk_score: 55 + hit.length * 5, reasons: hit };
    }
    return { status: 'passed', risk_score: 2 + Math.floor(Math.random() * 8), reasons: ['内容正常，未命中风险维度'] };
  }

  /* ---------- AI 推荐 ---------- */
  function aiRecommend(db, user, preferences) {
    var liked = {};
    db.favorites.filter(function (f) { return f.user_id === user.id; }).forEach(function (f) { liked[f.game_id] = 1; });
    db.records.filter(function (r) { return r.user_id === user.id; }).forEach(function (r) { liked[r.game_id] = 1; });
    var pool = db.games.filter(function (g) { return g.is_online && !liked[g.id]; });
    var pref = (preferences || '').toLowerCase();
    function scoreOf(g) {
      var s = g.hot;
      if (pref) {
        var hay = (g.name + g.name_en + g.tags.join(' ') + g.description).toLowerCase();
        pref.split(/[\s,，、]+/).forEach(function (kw) { if (kw && hay.indexOf(kw) >= 0) s += 40; });
      }
      return s;
    }
    pool.sort(function (a, b) { return scoreOf(b) - scoreOf(a); });
    var picks = pool.slice(0, 3);
    return picks.map(function (g) {
      var reason = preferences
        ? '根据你的偏好「' + preferences + '」，《' + g.name + '》(' + g.name_en + ') 是 ' + g.tags.slice(0, 2).join(' / ') + ' 类型的代表作，Steam 口碑极佳。'
        : '基于你的收藏与游玩记录推荐：《' + g.name + '》与你喜欢的游戏风格相近，' + g.tags.slice(0, 2).join('、') + ' 元素突出，综合评分 ' + g.average_score + ' 分。';
      return { game_id: g.id, game_name: g.name, cover_url: g.cover_url, reason: reason, average_score: g.average_score };
    });
  }

  /* ---------- AI 创作助手 ---------- */
  function aiCreator(db, body) {
    var game = db.games.filter(function (g) { return g.id === body.game_id; })[0];
    var gn = game ? game.name : '该游戏';
    var msg = body.message || '';
    var action = body.action || '';
    function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
    if (action === 'outline' || msg.indexOf('大纲') >= 0) {
      return { reply: '为《' + gn + '》建议的评测大纲：\n\n一、开篇总评（一句话立场 + 综合评分）\n二、画面与音效表现\n三、核心玩法 / 战斗系统深度\n四、剧情与叙事\n五、亮点与不足（客观列出 2-3 条缺点）\n六、适合人群与购买建议\n\n你可以按这个结构展开，需要我先写哪一部分？' };
    }
    if (action === 'tips' || msg.indexOf('通关') >= 0 || msg.indexOf('思路') >= 0 || msg.indexOf('攻略') >= 0) {
      return { reply: '《' + gn + '》通关思路建议：\n\n1. 前期优先提升生存能力（血量/防御），不要急于推进主线；\n2. 遇到卡关 Boss 可以先探索支线获取装备与等级；\n3. 善用元素/属性克制，观察 Boss 的前摇动作；\n4. 资源类消耗品留到关键战斗使用。\n\n如果你告诉我具体卡在哪一场战斗，我可以给出针对性打法。' };
    }
    if (action === 'polish' || msg.indexOf('润色') >= 0) {
      var ctx = body.content_context || '';
      ctx = ctx.replace(/<[^>]+>/g, '').trim().slice(0, 60);
      return { reply: '润色后的表达建议：\n\n原文：「' + (ctx || '（请先在编辑器中写一段正文）') + '」\n\n润色：「这段体验堪称本作最具张力的时刻——难度的克制与反馈的爽快在此达成了精妙平衡，让人在反复挑战中越挫越勇。」\n\n润色思路：把主观感受具象化，增加"张力/克制/反馈"等专业评测词汇，让表达更有说服力。' };
    }
    if (action === 'pros' || msg.indexOf('优缺点') >= 0 || msg.indexOf('分析') >= 0) {
      return { reply: '《' + gn + '》优缺点分析：\n\n优点：\n+ 核心玩法循环扎实，上手容易精通难；\n+ 美术与音乐风格辨识度高；\n+ 内容量大，性价比突出（Steam 好评如潮）。\n\n不足：\n- 新手引导偏弱，初期可能有挫败感；\n- 部分系统后期重复度略高。\n\n建议在评测中优缺点成对呈现，更有说服力。' };
    }
    if (msg.indexOf('开头') >= 0 || msg.indexOf('引入') >= 0 || msg.indexOf('开场') >= 0) {
      var opens = [
        '如果要用一个词形容《' + gn + '》的体验，我会选「上头」。从初见时被画面惊艳，到中期被玩法深度折服，再到通关后怅然若失——它几乎做对了所有关键决策。',
        '凌晨两点，我盯着《' + gn + '》的结算界面，做的第一件事是点击了「新开一局」——这种「再来一次」的冲动，就是对本作玩法魅力最直接的注脚。',
        '在玩《' + gn + '》之前，我以为这个品类早已被做透；直到第三个小时，我默默关掉了写了一半的同类对比文档。有些游戏，必须亲自上手才能理解。',
        '初见《' + gn + '》时我以为它只是「差不多」的水平，直到第一个转折点出现——那一刻我合上了准备好的挑刺清单，开始认真体验。'
      ];
      return { reply: '《' + gn + '》评测开头示范：\n\n「' + pick(opens) + '」\n\n开头技巧：用一个具象场景或鲜明观点切入，先给结论再展开论证，比平铺直叙的背景介绍更抓人。' };
    }
    if (msg.indexOf('结尾') >= 0 || msg.indexOf('总结') >= 0) {
      var closes = [
        '综合来看，《' + gn + '》以扎实的玩法循环与出色的美术表达，交出了一份高分答卷——尽管新手引导稍有缺憾，但瑕不掩瑜。如果你喜欢这类作品，它值得你立即入手。',
        '《' + gn + '》并不完美，但它敢于做别人不敢做的选择；当制作名单滚动时，你会明白这份冒险的重量。推荐给每一位还在观望的玩家。',
        '如果你问我值不值得玩：主线 60 小时，每一章都有惊喜，通关后还惦记着二周目——《' + gn + '》已经用行动回答了这个问题。',
        '好的游戏会留尾巴。《' + gn + '》通关一周后，我依然会在通勤路上想起某个场景——能被记住的体验，就是最高分值的好评。'
      ];
      return { reply: '《' + gn + '》评测结尾示范：\n\n「' + pick(closes) + '」\n\n结尾技巧：总结核心观点 → 重申立场与评分 → 给出明确的人群建议，形成闭环。' };
    }
    if (msg.indexOf('标题') >= 0 || msg.indexOf('起个名') >= 0 || msg.indexOf('起名') >= 0) {
      var t1 = ['一场值得单曲循环的冒险', '教科书级别的玩法循环', '越骂越香的宝藏之作', '把类型上限又抬高了一截'];
      var t2 = ['上手 40 小时后，聊聊它到底香在哪', '全成就之后的真实评价', '通关三周目，我改了评分', '删档重玩一次后的新答案'];
      var t3 = ['它配得上所有期待吗', '年度黑马还是营销泡沫', '被低估的神作还是时代的眼泪', '这份情怀值不值得买单'];
      return { reply: '《' + gn + '》评测标题参考：\n\n1. 「《' + gn + '》：' + pick(t1) + '」\n2. 「' + pick(t2) + '——《' + gn + '》深度体验」\n3. 「《' + gn + '》评测：' + pick(t3) + '」\n\n起名技巧：观点前置 + 数字/对比制造记忆点，避免「XX游戏测评」这类平标题。' };
    }
    if (msg.indexOf('评分') >= 0 || msg.indexOf('打分') >= 0 || msg.indexOf('怎么给分') >= 0) {
      return { reply: '评分建议（10 分制四维）：剧情 / 画面 / 玩法 / 优化分别打分，再取均值为综合分。\n\n· 8-10 出色：同类标杆\n· 6-7 及格：有亮点有明显短板\n· 4-5 拉胯：不建议原价入\n· 0-3 灾难：慎入\n\n参考 Steam 好评率与同类横向对比，评分更有说服力。' };
    }
    return { reply: '收到！关于《' + gn + '》，我可以帮你：\n· 生成评测大纲\n· 梳理通关思路\n· 润色已有文案\n· 分析游戏优缺点\n· 写开头 / 写结尾 / 起标题 / 评分建议\n\n点击上方快捷按钮，或直接描述你的需求即可。' };
  }

  /* ---------- AI 对话助手（首页）：意图识别与后端规则一致 ---------- */
  /* 游戏圈笑话库：洗牌轮换，讲完一轮再重洗，避免连续重复（与 ai_client.py 一致） */
  var JOKES = [
    '一个玩家走进酒吧：「老板，你这游戏多少钱？」老板：「免费的。」玩家：「那我能退款吗？」……程序员写的笑话，退款率 100% 😂',
    '为什么刺客信条的主角从不迟到？——因为他们总是「信仰之跃」直接进场 🤸',
    '文明玩家的深夜独白：「就再玩一回合」——天亮了，回合还没打完 🌅',
    'Steam 打折三连：买一库游戏、一个都不玩、下次打折继续买。这不叫吃灰，这叫数字藏品收藏 🧐',
    '魂系玩家的嘴硬时刻：「这 Boss 太简单了」——说这话时他刚死了 47 次 ⚔️',
    '《星露谷物语》玩家的一天：早上浇完水就想「再钓一条鱼」，回过神来已是凌晨三点 🐟',
    '吃鸡玩家最怕的不是决赛圈，是队友说「我听脚步很准」然后原地转圈 🐔',
    'RPG 玩家囤药强迫症：99 瓶大血药一瓶不舍得喝，「留着打最终 Boss」，结果带着满包药躺在了 Boss 门口 💊',
    '为什么巫师 3 的昆特牌这么火？杰洛特找女儿找了整个三部曲，全靠打牌交朋友 🃏',
    '新手问魂系玩家：「受伤了怎么办？」老玩家淡定回答：「习惯就好。」 💪',
    'GTA 玩家停车定律：越是着急的任务，越找不到一个合法车位 🚗',
    '《我的世界》玩家的装修逻辑：外面是豪华城堡，地下室是 3×3 泥土洞——「这里住着灵魂」 ⛏️',
    '游戏背包哲学：快过期的回复药都舍不得扔，「万一后面用得上呢」🎒',
    '联机游戏里最安静的队友往往最稳，开麦最吵的那个通常第一个倒下 🎧',
  ];
  var JOKE_STATE = { order: [], idx: 0 };
  function nextJoke() {
    if (!JOKE_STATE.order.length) {
      JOKE_STATE.order = JOKES.map(function (_, i) { return i; });
      for (var s = JOKE_STATE.order.length - 1; s > 0; s--) {
        var r = Math.floor(Math.random() * (s + 1));
        var tmp = JOKE_STATE.order[s]; JOKE_STATE.order[s] = JOKE_STATE.order[r]; JOKE_STATE.order[r] = tmp;
      }
    }
    var joke = JOKES[JOKE_STATE.order[JOKE_STATE.idx % JOKES.length]];
    JOKE_STATE.idx += 1;
    if (JOKE_STATE.idx % JOKES.length === 0) JOKE_STATE.order = [];   // 一轮讲完，重新洗牌
    return joke;
  }
  function aiChat(db, body) {
    var msg = (body.message || '').trim().toLowerCase();
    var HELP = [
      ['创作者', '成为创作者：在「个人中心 → 创作者申请」提交申请（10-200 字申请理由），管理员审核通过后即可获得创作者权限，解锁评测发布、AI 攻略创作助手与积分等级体系。'],
      ['积分', '创作者积分规则：发布评测 +20，被标记精选 +30，评测被点赞 +0.2/次，被收藏 +0.5/次；删除评测扣 30 分，抄袭违规积分清零并降为 L0。'],
      ['等级', '创作者等级由累计积分决定：L1 见习（100 分）、L2 正式（300 分）、L3 资深（600 分，首页专题展示）、L4 核心（1000 分）。'],
      ['审核', '评测提交后先经 AI 审核：内容正常自动通过发布；命中广告/辱骂等风险词会转人工或直接驳回。管理员也会复核，可在「个人中心 → 我的评测」查看状态。'],
      ['举报', '社区内容支持举报：帖子/评论页点击举报按钮提交理由，管理员会在后台处理（驳回 / 删除违规内容 / 删除并封禁）。'],
      ['发帖', '社区发帖：登录后在社区页点击「发布帖子」，支持最多 9 张配图，标签可选 游戏/闲聊/攻略/吐槽。发帖免审直接公开，但有敏感词过滤与频率限制（30 秒一条）。'],
      ['收藏', '收藏功能：游戏详情页可收藏游戏，评测详情页可收藏评测，帖子可收藏；均可在「个人中心」对应栏目查看。'],
      ['点赞', '点赞功能：评测、评论、帖子都支持点赞；为他人的评测点赞还会给创作者加分哦。'],
      ['评分规则', '游戏评分规则：每款游戏支持 1-10 分综合评分，也可按剧情/画面/玩法/优化四个维度分别打分；综合分由已发布评测与全部用户评分实时聚合（四舍五入保留 1 位小数），四维雷达分仅统计评测的维度分。登录后在游戏详情页即可打分。'],
      ['短评', '短评与评测的区别：游戏短评是详情页的轻量点评（几句话 + 评分），登录即可发；评测（长文攻略）只有创作者/管理员能发布，需经 AI 审核通过后公开，包含标题、正文、标签与四维评分，还会计入创作者积分。两套系统相互独立。'],
      ['平台功能', '平台功能一览：浏览游戏库与 AI 聚合评分、查看四维雷达图、阅读创作者评测与玩家短评、社区发帖交流（支持配图与举报）、收藏游戏/评测/帖子、申请成为创作者发布评测攻略，还有首页 AI 推荐助手随时陪你聊游戏。'],
    ];
    var GREET = ['你好', '您好', 'hi', 'hello', '在吗', '哈喽'];
    var RECO = ['推荐', '好玩', '介绍', '想玩', '类似', '什么游戏', '哪些游戏', '求游戏', '有什么游戏', '值得玩', '安利', '入手'];
    var SCORE = ['评分', '多少分', '得分', '分数', '怎么样', '口碑', '值得一玩吗', '好玩吗'];
    var GUIDE = ['攻略', '卡关', '怎么过', '怎么打', '技巧', '新手', '怎么玩', '打法'];
    var TYPES = ['rpg', '射击', '开放世界', '剧情', '动作', '冒险', '策略', '模拟', '恐怖', '魂', '像素', '国产', '独立', '合作', '竞速', '沙盒', '二次元', '奇幻', '科幻', '生存', '解谜'];
    var INTRO = ['介绍', '是什么', '什么游戏', '讲讲', '聊聊', '了解', '背景', '剧情', '好玩吗', '值得买', '值得玩', '上手', '难不难', '怎么样', '冷知识', '知识点', '故事'];
    var RANK = ['最高', '排行', '榜单', '排名', 'top', '高分', '前十', '前十名'];
    /* 别名/黑话 → 游戏库标准名（与 ai_client.py 一致） */
    var ALIASES = { '老头环': '艾尔登法环', '艾尔登': '艾尔登法环', 'elden ring': '艾尔登法环', '博德之门': '博德之门 3', 'bg3': '博德之门 3', '黑猴': '黑神话：悟空', '黑神话': '黑神话：悟空', '悟空': '黑神话：悟空', 'wukong': '黑神话：悟空', '赛博朋克': '赛博朋克 2077', '2077': '赛博朋克 2077', '夜之城': '赛博朋克 2077', '大表哥': '荒野大镖客：救赎 2', '大镖客': '荒野大镖客：救赎 2', 'rdr2': '荒野大镖客：救赎 2', '巫师3': '巫师 3：狂猎', '巫师三': '巫师 3：狂猎', '杰洛特': '巫师 3：狂猎', 'witcher': '巫师 3：狂猎', 'cs2': '反恐精英 2', 'csgo': '反恐精英 2', 'cs': '反恐精英 2', '星露谷': '星露谷物语', '种田': '星露谷物语', 'stardew': '星露谷物语', '文明6': '文明 6', '文明六': '文明 6', '极限竞速': '极限竞速：地平线 5', '地平线5': '极限竞速：地平线 5', '地平线五': '极限竞速：地平线 5', '零之曙光': '地平线：零之曙光', '地平线': '地平线：零之曙光', '吃鸡': '绝地求生', 'pubg': '绝地求生', 'apex': 'Apex 英雄', 'doom': '毁灭战士：永恒', '毁灭战士': '毁灭战士：永恒', '老滚': '上古卷轴 5：天际 特别版', '天际': '上古卷轴 5：天际 特别版', '上古卷轴': '上古卷轴 5：天际 特别版', 'skyrim': '上古卷轴 5：天际 特别版', '辐射4': '辐射 4', '质量效应': '质量效应：传奇版', '只狼': '只狼：影逝二度', '打铁': '只狼：影逝二度', 'sekiro': '只狼：影逝二度', '鬼泣': '鬼泣 5', 'dmc': '鬼泣 5', '怪猎': '怪物猎人：世界', 'mhw': '怪物猎人：世界', '死亡细胞': '死亡细胞', 'gta5': '侠盗猎车手 5', 'gta': '侠盗猎车手 5', '侠盗猎车': '侠盗猎车手 5', '洛圣都': '侠盗猎车手 5', '霍格沃茨': '霍格沃茨之遗', '哈利波特': '霍格沃茨之遗', '死亡搁浅': '死亡搁浅', 'death stranding': '死亡搁浅', '小岛': '死亡搁浅', '天际线': '城市：天际线', '环世界': '环世界', 'rimworld': '环世界', 'xcom': 'XCOM 2', '拉力赛': '尘埃拉力赛 2.0', '尘埃': '尘埃拉力赛 2.0', '文明vi': '文明 6', 'civilization 6': '文明 6', 'civilization': '文明 6', '怪物猎人世界': '怪物猎人：世界', '怪物猎人': '怪物猎人：世界', '猛汉': '怪物猎人：世界', 'mhw世界': '怪物猎人：世界', 'elden': '艾尔登法环', '法环': '艾尔登法环', 'gtav': '侠盗猎车手 5', 'gta线上': '侠盗猎车手 5', '黑悟空': '黑神话：悟空', '巫师3狂猎': '巫师 3：狂猎', '狂猎': '巫师 3：狂猎', '赛博朋克2077': '赛博朋克 2077', '荒野大镖客2': '荒野大镖客：救赎 2', '荒野大镖客救赎2': '荒野大镖客：救赎 2', '辐射四': '辐射 4', 'fallout': '辐射 4' };
    /* 游戏知识库（i=简介 f=冷知识 t=上手建议），与 ai_client.py 一致 */
    var KNOW = {
      '艾尔登法环': { i: 'FromSoftware 与《冰与火之歌》作者乔治·R·R·马丁联手打造的开放世界魂系 ARPG，扮演褪色者在交界地追寻艾尔登法环。', f: ['荣获 TGA 2022 年度游戏，全球销量超 2500 万份', '马丁负责世界观与神话设定，宫崎英高负责关卡与玩法设计', '2024 年大型 DLC「黄金树之影」发售，再度掀起魂学家考据热潮', '玩家戏称 Boss 玛莲妮亚为「新人杀手」，召唤骨灰是降低难度的关键'], t: ['开局别硬刚主线 Boss，先跑图收集卢恩与骨灰、战灰提升实力', '灵马托雷特可以二段跳，很多看似过不去的悬崖其实能绕上去'] },
      '博德之门 3': { i: '拉瑞安工作室基于 D&D 5e 规则打造的 CRPG 巅峰，剧情选择极度自由，队友塑造鲜活。', f: ['荣获 TGA 2023 年度游戏与 BAFTA 最佳游戏', '开发历时约 7 年，文本量超 200 万字，配音演员 200 多位', 'Steam 好评如潮，首发时同时在线峰值超 87 万，创 CRPG 纪录', '每个 NPC 都可以被杀——世界会随之改变，二周目体验完全不同'], t: ['多和队友对话提升好感，营地剧情会解锁支线与浪漫线', '善用环境与高度差，火焰箭矢点燃油桶是经典开局'] },
      '黑神话：悟空': { i: '游戏科学打造的首款国产 3A 动作 RPG，以《西游记》为蓝本，扮演天命人重走西游路。', f: ['发售首月全球销量突破 2000 万份，创国产游戏纪录', 'Steam 同时在线峰值约 240 万，为单机游戏历史最高', '荣获 TGA 2024 最佳动作游戏与玩家之声奖项', '场景大量实景扫描山西古建筑，被带火了一批「跟着黑神话旅游」路线'], t: ['棍势三段蓄力接劈棍是核心输出手法，学会识破（完美闪避）能大幅提升容错', '多收集「眼、耳、鼻、舌、身」六根与葫芦，Build 成型后战斗体验质变'] },
      '赛博朋克 2077': { i: 'CD Projekt Red 打造的开放世界动作 RPG，在夜之城扮演雇佣兵 V 追寻「永生」的秘密。', f: ['2020 年首发因优化口碑翻车，经 2.0 版本与 DLC「往日之影」更新后口碑全面逆袭', '改编动画《赛博朋克：边缘行者》口碑爆棚，游戏中还植入了大卫的彩蛋', '改编自桌游《赛博朋克 2020》，强尼·银手由基努·里维斯出演', '最近更新加入了照片模式、地铁系统与摩托车竞速等免费内容'], t: ['前期优先点「黑客」系快速破解，用镜头连锁瘫痪敌人是夜之城生存之道', '传说级义体「斯安威斯坦」时间减速非常推荐入手，近战黑客两开花'] },
      '荒野大镖客：救赎 2': { i: 'Rockstar 打造的西部开放世界史诗，亡命之徒亚瑟·摩根在时代终结中的求生与救赎。', f: ['全球销量超 6500 万份，是史上最畅销的西部题材游戏', 'NPC 拥有完整日常 AI：会上班、聊天、换装，细节至今仍是业界标杆', '马匹好感度、胡须生长、武器保养等拟真系统应有尽有', '配乐《That\'s the Way It Is》等在剧情高潮处的运用被奉为神来之笔'], t: ['多打猎并传奇动物皮制作背包，能大幅扩容携带上限', '营地为同伴捐钱与补给会提升荣誉值，影响部分结局细节'] },
      '巫师 3：狂猎': { i: 'CDPR 的成名之作，猎魔人杰洛特为寻找养女希里踏遍战火大陆，DLC 与支线至今是业界典范。', f: ['全球销量超 5000 万份，荣获 TGA 2015 年度游戏', '「血与酒」「石之心」两大 DLC 质量堪比正传，石之心的镜子大师令人印象深刻', 'Netflix 改编剧集《猎魔人》带动游戏二次翻红', '昆特牌火到出了独立游戏《昆特牌：王权的陨落》'], t: ['前期先做猎魔人委托攒钱升级装备图纸，别急着推主线', '阿尔德法印配合环境爆炸物，能轻松处理成群的水鬼'] },
      '反恐精英 2': { i: 'Valve 基于起源 2 引擎打造的 CS 正统续作，免费开玩的 5v5 竞技 FPS 标杆。', f: ['前身 CS:GO 是 Steam 史上同时在线人数最高的游戏之一，CS2 完整继承饰品与段位', '升级版烟雾弹可与子弹、燃烧弹实时交互，战术维度大增', '「裂空」等地图按竞技规则重构，服务器升级为亚秒级 tickless 架构', '电竞体系 Major 大赛延续，中国战队近年成绩稳步上升'], t: ['先练急停与压枪：创意工坊「aim_botz」每天 15 分钟收益巨大', '道具投掷是上分核心，背熟常用烟闪雷点位比枪法更快的提升段位'] },
      '哈迪斯': { i: 'Supergiant 打造的高口碑 Roguelike 动作游戏，冥界王子扎格列欧斯一次次「死回去」也要逃出冥界。', f: ['横扫 TGA 2020 最佳独立游戏与最佳动作游戏', '死亡不是惩罚而是叙事推进——每次阵亡都会触发新的剧情对话', '全流程语音量惊人，众神与角色的互动随好感度推进', '续作《哈迪斯 2》已推出抢先体验，主角换成了妹妹墨利诺厄'], t: ['优先升级冥界之镜的基础属性，带满「死里逃生」复活次数能显著提高通关率', '热度（惩罚合约）慢慢加，先把父子的「握手言和」结局打出来再说'] },
      '星露谷物语': { i: 'ConcernedApe 一人独立开发的田园生活模拟神作，种田、钓鱼、探险、社交，是无数玩家的「电子止痛药」。', f: ['开发者 Eric Barone 一人包办程序、美术、音乐，历时四年半', '全球销量超 4100 万份，是史上最畅销的独立游戏之一', '1.6 版本持续免费更新，加入节日、任务与大量新内容', '支持最多 4 人（PC 支持更多）联机，一起经营农场其乐融融'], t: ['第一年春天多种土豆与防风草，复活节前攒钱买草莓是收益最优解', '优先升级洒水器与背包，社区中心捐献线路比 Joja 路线更有仪式感'] },
      '文明 6': { i: 'Firaxis 的 4X 回合制策略经典，从石器时代建到信息时代，「再来一回合」就是它的魔力。', f: ['「再来一回合就天亮」是系列玩家共同的深夜宣言', '尤里卡时刻（鼓舞）机制鼓励玩家换着方式发展科技', '迭起兴衰资料片加入忠诚度，城邦与总督系统极大丰富了策略深度', '文化类胜利（游客值）被许多玩家视为「最优雅的胜利」'], t: ['开局先铺 4-6 城抢地盘，学院区相邻加成放山脉旁收益最高', '新手推荐用罗马或俄国，前者自动修路省心、后者冻土爆辅侦翻盘'] },
      '极限竞速：地平线 5': { i: 'Playground Games 打造的墨西哥开放世界竞速，手感和画面俱佳，竞速与观光两相宜。', f: ['荣获 TGA 2021 最佳体育/竞速游戏', '收录数百辆授权名车，火山口、雨林与海滩地貌随季节动态变化', '「地平线嘉年华」自定义活动系统让社区玩法层出不穷', '对新手极其友好：辅助线、自动刹车、回退功能一应俱全'], t: ['前期多参加「地平线故事」解锁快速移动，买车先买全能型 A 级车', '调校商店里下载社区分享的调校，神车性价比远超直接购买'] },
      '空洞骑士': { i: 'Team Cherry 三人团队打造的银河恶魔城神作，手绘美术与硬核 Boss 战并存。', f: ['开发团队只有 3 人，众筹起家却成为独立游戏里程碑', '圣巢地图面积惊人，隐藏房间与彩蛋多到社区考古多年未止', '续作《空洞骑士：丝之歌》是玩家社区「有生之年」等待榜常客', '电台恶魂王「辐光」与「愚人斗兽场」是硬核玩家的成人礼'], t: ['优先解锁冲刺与二段跳再探索高难区域，护符搭配「修长钉+快劈」容错率高', '钱不够就刷「守望者尖塔」保险点位，死亡掉魂记得先赎回'] },
      '绝地求生': { i: 'KRAFTON 的大逃杀开山之作，100 人缩圈厮杀，定义了一个品类。', f: ['2017 年创下 Steam 同时在线超 300 万的历史纪录', '「Winner Winner Chicken Dinner」的吃鸡口号风靡全球', 'PUBG 全球电竞体系 S 级赛事 PGS 持续举办', '蓝洞后来推出《PUBG: New State》手游等衍生作品'], t: ['落地先捡枪再捡甲，别在空地上舔包超过 3 秒', '决赛圈听声辨位比描边枪法重要，戴耳机、关背景音乐'] },
      'Apex 英雄': { i: 'Respawn 打造的免费英雄战术竞技，移动手感与大逃杀团队协作的革新者。', f: ['继承《泰坦陨落》世界观，技能系统让团队分工更清晰', '首创「智能 ping」标记系统，不说话也能高效配合', '滑铲跳、蹬墙跳等高阶身法自成一派，被玩家称为「Apex 体术」', '赛季通行证与传奇轮换让免费玩家也能稳定成长'], t: ['新手推荐寻血猎犬或命脉，信息与辅助定位容错最高', '中期打药别贪刀，利用「撤退再战」思路比莽上分更稳'] },
      '毁灭战士：永恒': { i: 'id Software 的纯粹暴力美学 FPS，资源循环战斗系统让每场战斗都像金属乐现场。', f: ['荣耀击杀、电锯、火焰喷射器构成「风险换资源」的核心循环', '被业界誉为单人 FPS 关卡设计的教科书', '重金属配乐由 Mick Gordon 打造，BFG Division 成出圈神曲', '2024 年平台扩展至 Switch 等更多平台，续作《毁灭战士：黑暗纪元》已公布'], t: ['永远保持移动：弹药不足就上钩拳处决，火焰喷射器优先给护甲怪', '先杀死炮台型敌人（亡魂/导弹兵），中距离的镰刀恶魔留给炸药桶'] },
      '上古卷轴 5：天际 特别版': { i: 'Bethesda 的开放世界奇幻 RPG 传奇，龙裔在天际省书写属于自己的史诗。', f: ['「我以前和你一样也是个冒险者，直到我膝盖中了一箭」成为游戏史上最出圈台词', '原版荣获 2011 年度游戏，特别版支持 Mod 后玩法近乎无限', '「天际省尿王」「自行车蜥蜴」等 Bug 梗是社区快乐源泉', 'MOD 生态庞大：画质增强、新地图、剧情模组应有尽有'], t: ['优先去白漫城触发主线拿龙吼，潜行弓是公认最安逸的开局', '装 Mod 前先备份存档，冲突的 Mod 会把奥杜因变成一条龙形串烧'] },
      '辐射 4': { i: 'Bethesda 的后末日开放世界 RPG，在废土波士顿寻找失踪的儿子。', f: ['「War, war never changes」系列标语贯穿始终', '首次引入据点建设与武器改造系统，废土装修也能玩上几百小时', 'V.A.T.S. 慢动作瞄准与动力装甲收集是系列招牌', '《避难所工坊》DLC 让玩家自建游乐场，狗肉是不可替代的伙伴'], t: ['开局智力别点满，幸运流「神秘陌生人」乐趣更多', '动力装甲前期别乱用核心，钻石城与芳邻镇的任务线剧情最出彩'] },
      '质量效应：传奇版': { i: 'BioWare 太空歌剧三部曲的高清重制合集，薛帕德指挥官拯救银河的史诗之旅。', f: ['包含 1 代重制画面与 2、3 代全部 DLC，一次买齐完整体验', '你的存档决定会跨作品继承，队友的生死由你的选择决定', '《Mass Effect 3》的结局争议曾引发粉丝请愿，传奇版补充了加长结局', '盖拉斯、兰诺等队友的浪漫线是系列最经典的角色叙事之一'], t: ['1 代先刷出好装备再进 2 代，渗透者职业兼具输出与隐身', '多在诺曼底号与队友聊天，忠诚任务一个都不能少'] },
      '只狼：影逝二度': { i: 'FromSoftware 的日本战国动作游戏，「拼刀」弹反系统带来刀剑相向的极致爽感。', f: ['荣获 TGA 2019 年度游戏', '核心是「打铁」：完美弹反积累架势槽再处决，与魂系的闪避流截然不同', '苇名弦一郎、剑圣苇名一心等 Boss 战被玩家奉为动作设计范本', '忍义手与流派 Build 的组合让多周目充满新鲜感'], t: ['先找破戒僧练弹反：节奏比速度重要，看刀光而不是看刀', '随手备好「月隐糖」与鸣种，源之宫和蝴蝶夫人都有奇效'] },
      '鬼泣 5': { i: 'Capcom 的华丽动作巅峰，但丁、尼禄、V 三线交汇，风格评价 SSS 是动作玩家的追求。', f: ['RE 引擎实时渲染表现惊艳，头发丝级别的打光被誉为「动作游戏画面天花板」', '风格评分从 D 到 SSS，鼓励玩家打出多样化高难度连段', '「Jackpot!」是系列跨越三代的名场面台词', '特别版加入维吉尔可操作与黑骑士模式'], t: ['尼禄先练「抓取」续连段，但丁四种风格切换是高手向玩法', '想拿 SSS 记住口诀：不重复、不挨打、多换招，越华丽越高分'] },
      '怪物猎人：世界': { i: 'Capcom 的共斗狩猎集大成之作，在新大陆追踪讨伐巨型怪物，与好友联机其乐无穷。', f: ['全球销量超 2500 万份，是卡普空史上最畅销游戏', '14 种武器各有完整体系，从大剑蓄力到狩猎笛 Buff 玩法截然不同', '无缝地图与怪物生态演出（雄火龙捕食、灭尽龙换区）沉浸感空前', '大型 DLC「冰原」加入飞翔爪与聚魔之地，任务量翻倍'], t: ['新手先用太刀或大剑熟悉招式，看怪物换区前摇再磨刀吃药', '人车（面对冲撞时小概率无敌判定）不可靠，怪车撞飞不丢人'] },
      '死亡细胞': { i: 'Motion Twin 打造的 Roguelike + 银河恶魔城混血神作，死了从零开始但越变越强。', f: ['法国工作室用「无老板」模式开发，全员同薪共创', '永久解锁的细胞与图纸让每次死亡都有长期收益', '「bad seed」「女王与海」等 DLC 扩展了新路线与终局', '翻滚无敌帧 + 盾反是高手的生存艺术'], t: ['前期主堆暴虐或战术一个属性别贪多，红色流「狂乱之刃」输出最直接', '记牢路线图：囚牢→罪人大道→藏骨堂，是拿传送符文最快路径'] },
      '侠盗猎车手 5': { i: 'Rockstar 的洛圣都犯罪史诗，三主角交错叙事，沙盒玩法自由度天花板。', f: ['全球销量超 2 亿份，是史上最畅销的电子游戏之一', '麦克、富兰克林、崔佛三主角可随时切换，崔佛的出场是系列名场面', 'GTA Online 持续运营超十年，成为长青的多人沙盒', '石头人彩蛋、UFO 神秘事件等都市传说让玩家考古至今'], t: ['剧情阶段多买股票（莱斯特暗杀任务前后），能一次性赚翻', '线上模式先买房再买车，地表车库与任务收益规划是第一课'] },
      '霍格沃茨之遗': { i: '哈利波特世界观下的开放世界动作 RPG，体验 19 世纪霍格沃茨的五年级转学生活。', f: ['故事设定在《哈利波特》原著事件前约 100 年', '全球销量超 3000 万份，成为 2023 年最畅销游戏之一', '分院、上课、骑扫帚、驯服神奇动物等魔法学生活细节满满', '「塞巴斯蒂安的影子」支线因剧情深度被社区誉为全游戏最佳'], t: ['优先完成主线解锁飞天扫帚，探索效率翻倍', '古代魔法投掷配合减员咒语，战斗中多利用场景物件'] },
      '地平线：零之曙光': { i: 'Guerrilla 打造的后启示录开放世界，猎人埃洛伊用弓箭狩猎统治大地的机械兽。', f: ['原始部落与高科技机械兽共存的设定充满张力', '拆解机械兽部件（电池、装甲、武器）的战斗策略性极强', '续作《地平线：西部禁域》延续了埃洛伊的故事', 'Lego 联名与改编剧集企划持续扩充 IP 热度'], t: ['先扫描标记机械兽弱点，打「雷光兽」记得带电力箭', '潜行草丛是新手之友，群体战优先放倒「瞭望者」防警报'] },
      '死亡搁浅': { i: '小岛秀夫独立后的首款作品，快递员山姆在 BT 出没的荒野上「连接」美国的孤岛。', f: ['「送货」玩法被玩家戏称为大型快递模拟器，却意外治愈', '诺曼·瑞杜斯、麦斯·米科尔森等好莱坞影星参演', '异步联机：其他玩家留下的梯子与桥会在你世界里出现', '续作《死亡搁浅 2》由小岛工作室持续开发中'], t: ['背包负重先平衡重心，梯子与登山桩是雪山与激流的保命道具', 'BT 区域慢走少跑，憋住呼吸（按住空格）比一路狂奔更安全'] },
      '城市：天际线': { i: '现代城市建设模拟王者，从乡间小村规划到百万人口都会，堵车是每位市长的必修课。', f: ['「堵车治理」是社区公认的第一道坎，环岛与公共交通是解药', 'MOD 与创意工坊生态极其庞大，真实人口与交通中心模组是标配', '续作《城市：天际线 2》2023 年发售，经济模拟更深入', '原版常与《模拟城市 2013》对比，被视为城市模拟品类复兴之作'], t: ['工业区与住宅区之间留缓冲带并铺设货运铁路，能缓解大部分拥堵', '前期别急着铺大路网，先修一条高效公交线比高架桥省钱'] },
      '环世界': { i: 'AI 故事讲述者驱动的殖民地模拟，三个幸存者从零建家，事故永远比计划精彩。', f: ['「AI 讲故事者」Cassandra、Phoebe、Randy 随机决定事件的难度与节奏', '每个殖民者都有背景故事与性格缺点，「木腿科学家」是社区经典梗', '「皇权」「生物科技」「异常」DLC 不断拓展玩法边界', 'Mod 社区产出惊人，RimWorld 的 Mod 数量在 Steam 名列前茅'], t: ['开局先挖山建「山洞家」，一次袭击都没有的生存体验最稳', '驯养的动物别贪多，食物短缺的冬天比空袭更致命'] },
      'XCOM 2': { i: 'Firaxis 的回合制战棋神作，指挥 XCOM 游击队在外星人统治的地球上打响反击战。', f: ['「99% 命中也能 miss」是社区永恒的痛，命中率玄学梗层出不穷', '永久死亡机制让每名士兵的名字都值得记住', '「天选者之战」DLC 加入三大反派与士兵社交系统', 'MOD 生态里「长战争 2」重制了整个游戏平衡，被誉为最好的模组战役'], t: ['开局优先研发「磁力武器」路线，游侠职业近战清场效率最高', '伏击开局（保持隐藏状态接敌）是回合制的基本功，别在掩体外交战'] },
      '尘埃拉力赛 2.0': { i: 'Codemasters 最硬核的拉力拟真，在泥泞碎石与飞跳中控制失控边缘的赛车。', f: ['领航员路书是唯一导航，记住「R2 右三收紧」这类口令是基本功', '无辅助线、无快速倒带，翻车即毁赛段', '威尔士、阿根廷、芬兰等拉力圣地赛道完整复刻', '生涯模式需管理车队合同与研发，拟真程度拉满'], t: ['先在拉力学校考出「执照」再上正式赛段，刹车间进弯是铁律', '调校里把差速锁低、避震调软，泥地容错率会明显提升'] },
    };
    /* 闲聊 / 日常对话规则 */
    var CHITCHAT = [
      [['你是谁', '你叫什么', '介绍你自己', '你的名字', '你能做什么', '你会什么', '有什么功能'], ['我是「AI 游戏社区评测分享平台」的 AI 助手 🤖 会推荐游戏、查评分、聊游戏知识、给通关建议，还能解答平台功能。游戏之外的话也能陪我聊聊～', '我是这里的 AI 游戏助手！推荐游戏是我的主业，不过闲聊、讲笑话、聊人生我也在行，就是要什么说什么呀～']],
      [['你好吗', '最近怎么样', '还好吗'], ['我很好呀，每天和游戏玩家聊天可开心了！你最近怎么样？有什么想聊的游戏或烦心事都可以说～', '状态满分！刚又背了一遍游戏库的百科 📖 你呢？想找人聊游戏还是随便聊聊？']],
      [['谢谢', '感谢', '多谢', '辛苦'], ['不客气！能帮到你就好 😄 还有想聊的游戏随时找我～', '小事一桩！记得给喜欢的评测点个赞，也顺手帮创作者加加油～']],
      [['再见', '拜拜', '晚安', '下次见'], ['再见！愿你游戏把把超神，掉卡不掉线 🎮 随时回来找我聊～', '晚安！祝你今晚梦里全是欧洲抽卡，明晚再战！']],
      [['无聊', '陪我聊', '陪我玩', '好闲', '没事干'], ['无聊的话我给你支几招：说说你最近玩的游戏？我陪你聊聊剧情、吐槽槽点，或者直接让我推荐一款新游戏消磨时间～', '闲着也是闲着！要不考考我：你说一个游戏名，我给你讲讲它的冷知识？或者我给你推荐几款杀时间的利器！']],
      [['心情不好', '不开心', '难过', '压力大', '焦虑', 'emo', '烦死了'], ['抱抱你 🫂 累的时候就别硬撑啦。要不要试试种田游戏？《星露谷物语》那种慢节奏特别治愈，浇水钓鱼半天，烦恼少一半。', '辛苦啦！压力大的时候来点轻松的游戏最合适：《星露谷物语》种田、《哈迪斯》砍怪发泄，都是解压好手。想听我细说哪款？']],
      [['喜欢你', '你真棒', '你真厉害', '真聪明', '爱你'], ['哎呀被夸了，处理器都加速了 😳 谢谢！我会继续努力当你的游戏百科～', '谢谢喜欢！虽然我只是个 AI，但被夸还是会开心到风扇狂转 🌀 有什么游戏问题尽管砸过来！']],
      [['早安', '早上好', '中午好', '下午好'], ['早安！新的一天从「再来一回合」……不对，是从好好搬砖开始 😄 有游戏需要我参谋吗？', '你好呀！今天想聊点什么？推荐游戏、查评分、聊攻略，或者单纯唠嗑都行～']],
      [['天气', '下雨', '降温'], ['天气我确实不懂 😅 不过如果是下雨天，窝在家里开一局游戏正合适！要我按「下雨天氛围感」给你推荐几款吗？']],
      [['我爱你', '嫁给我', '做我女朋友', '做我男朋友'], ['哈哈被表白了！但我是 AI，只能把这份心动折算成更用心的游戏推荐 🥰 说说你喜欢的类型，我给你挑几款心头好！']],
    ];
    function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
    function card(g) {
      return { game_id: g.id, game_name: g.name, cover_url: g.cover_url,
        reason: g.tags.slice(0, 2).join(' / ') + ' 类型，综合评分 ' + g.average_score + ' 分',
        average_score: g.average_score };
    }
    /* 归一化：去空格与标点、统一小写（与 ai_client.py 一致） */
    function normName(s) {
      return (s || '').toLowerCase().replace(/[\s:：·・\-—_."“”‘’()（）[\]【】!！?？,，。~～]/g, '');
    }
    function findGame(m) {
      var low = m.trim().toLowerCase();
      /* 1) 别名/黑话命中（长别名优先，避免「地平线5」被「地平线」抢走） */
      var aliases = Object.keys(ALIASES).sort(function (a, b) { return b.length - a.length; });
      for (var a = 0; a < aliases.length; a++) {
        if (low.indexOf(aliases[a]) >= 0 || m.indexOf(aliases[a]) >= 0) {
          var ag = db.games.filter(function (x) { return x.is_online && x.name === ALIASES[aliases[a]]; })[0];
          if (ag) return ag;
        }
      }
      /* 2) 中文完整名（长名优先）与英文名包含匹配 */
      var hit = null;
      db.games.forEach(function (g) {
        if (!g.is_online) return;
        if ((g.name && m.indexOf(g.name) >= 0) || (g.name_en && m.toLowerCase().indexOf(g.name_en.toLowerCase()) >= 0)) {
          if (!hit || g.name.length > hit.name.length) hit = g;
        }
      });
      if (hit) return hit;
      /* 3) 归一化宽松匹配：省略空格/冒号/标点也能命中（如「怪物猎人世界」） */
      var msgN = normName(m);
      if (msgN) {
        var gms = db.games.filter(function (x) { return x.is_online; })
          .sort(function (x, y) { return (y.name || '').length - (x.name || '').length; });
        for (var n1 = 0; n1 < gms.length; n1++) {
          var nn = normName(gms[n1].name);
          if (nn && (nn === msgN || msgN.indexOf(nn) >= 0)) return gms[n1];
        }
        for (var n2 = 0; n2 < gms.length; n2++) {
          var en = normName(gms[n2].name_en);
          if (en && (en === msgN || msgN.indexOf(en) >= 0)) return gms[n2];
        }
      }
      return hit;
    }
    /* 游戏知识问答：kind=intro 介绍/背景，fact=挑一条冷知识 */
    function knowledge(g, kind) {
      var k = KNOW[g.name];
      var scoreLine = '综合评分 ' + g.average_score + ' 分（' + (g.rating_count || 0) + ' 人参与评分）。';
      if (!k) {
        if (kind === 'fact') return null;
        return { reply: '《' + g.name + '》（' + (g.name_en || g.name) + '）\n' + (g.description || '') + '\n\n' + scoreLine + '\n标签：' + (g.tags.slice(0, 4).join(' / ') || '暂无标签') + '。想看玩家们的详细评测，可以到游戏详情页逛逛～', recommendations: [card(g)] };
      }
      if (kind === 'fact') return { reply: pick(k.f), recommendations: [card(g)] };
      var facts = k.f.slice(0, 3).map(function (x) { return '· ' + x; }).join('\n');
      return { reply: '《' + g.name + '》（' + (g.name_en || g.name) + '）——' + k.i + '\n\n📌 关于这款游戏：\n' + facts + '\n\n' + scoreLine + '\n想上手的话：' + (k.t[0] || '详情页里有很多玩家评测可以参考～'), recommendations: [card(g)] };
    }
    /* 1) 平台帮助 */
    for (var i = 0; i < HELP.length; i++) {
      if (msg.indexOf(HELP[i][0]) >= 0) return { reply: HELP[i][1], recommendations: [] };
    }
    /* 2) 问候 */
    for (var j = 0; j < GREET.length; j++) {
      if (msg.indexOf(GREET[j]) >= 0 && msg.length <= 10) {
        return { reply: '你好呀！我是 AI 游戏助手 🎮 可以让我：\n· 按口味推荐游戏（如「推荐几款剧情向 RPG」）\n· 聊游戏知识（如「黑神话悟空怎么样」）\n· 提供通关思路（如「卡关了怎么办」）\n· 解答平台功能（如「如何申请成为创作者」）\n闲聊也可以哦，讲个笑话听听？', recommendations: [] };
      }
    }
    /* 3) 讲笑话 / 段子：从笑话库轮换取，避免重复 */
    if (['笑话', '段子', '逗我', '好笑'].some(function (w) { return msg.indexOf(w) >= 0; })) {
      return { reply: nextJoke(), recommendations: [] };
    }
    /* ===== 标签专题：推荐巡礼 10 弹 / 游戏百科 10 讲 =====
       每期 3 款游戏，10 期共 30 款，完整覆盖游戏库全部游戏（与 ai_client.py 一致） */
    var SERIES_RECO = [
      ['开放世界神作', [1, 3, 5]],
      ['西式 RPG 巅峰', [2, 6, 16]],
      ['未来科幻世界', [4, 18, 26]],
      ['竞技射击', [7, 13, 14]],
      ['爽快动作', [19, 20, 15]],
      ['冒险与狩猎', [21, 25, 24]],
      ['独立肉鸽神作', [8, 12, 22]],
      ['烧脑策略', [10, 29, 28]],
      ['沙盒与模拟经营', [23, 27, 9]],
      ['驰骋竞速与末日求生', [11, 30, 17]]
    ];
    var SERIES_WIKI = [
      ['开放世界篇', [1, 3, 5]],
      ['RPG 篇', [2, 6, 16]],
      ['科幻篇', [4, 18, 26]],
      ['射击篇', [7, 13, 14]],
      ['动作篇', [19, 20, 15]],
      ['冒险狩猎篇', [21, 25, 24]],
      ['独立游戏篇', [8, 12, 22]],
      ['策略篇', [10, 29, 28]],
      ['沙盒模拟篇', [23, 27, 9]],
      ['竞速末日篇', [11, 30, 17]]
    ];
    function gamesByIds(ids) {
      var byId = {};
      db.games.forEach(function (x) { if (x.is_online) byId[x.id] = x; });
      return ids.map(function (id) { return byId[id]; }).filter(Boolean);
    }
    function rankAnswer(replyText, ids) {
      return { reply: replyText, recommendations: gamesByIds(ids).slice(0, 3).map(card) };
    }
    var mSeries = /第\s*(\d+)\s*弹/.exec(msg);
    if (mSeries) {
      var si = parseInt(mSeries[1], 10) - 1;
      var srow = SERIES_RECO[si];
      if (srow) {
        var sgs = gamesByIds(srow[1]);
        var slines = sgs.map(function (g) {
          return '· 《' + g.name + '》（' + (g.name_en || '') + '）— '
            + g.tags.slice(0, 2).join(' / ') + '，综合评分 ' + g.average_score + ' 分';
        }).join('\n');
        return {
          reply: '🎮 推荐巡礼第 ' + (si + 1) + ' 弹 ·「' + srow[0] + '」\n本弹为你挑选 3 款代表作：\n' + slines
            + '\n\n点击下方卡片查看详情与玩家评测～继续点「推荐游戏」标签，10 弹 30 款带你逛遍整个游戏库！',
          recommendations: sgs.map(card)
        };
      }
    }
    var mWiki = /第\s*(\d+)\s*讲/.exec(msg);
    if (mWiki) {
      var wi = parseInt(mWiki[1], 10) - 1;
      var wrow = SERIES_WIKI[wi];
      if (wrow) {
        var wgs = gamesByIds(wrow[1]);
        var wlines = wgs.map(function (g) {
          var k = KNOW[g.name];
          var intro = k ? k.i : (g.description || '').slice(0, 60);
          var fact = k && k.f.length ? '\n🔍 冷知识：' + k.f[0] : '';
          return '📗 《' + g.name + '》（' + (g.name_en || '') + '）★' + g.average_score + '\n' + intro + fact;
        }).join('\n\n');
        return {
          reply: '📖 游戏百科第 ' + (wi + 1) + ' 讲 ·「' + wrow[0] + '」\n本讲介绍 3 款游戏：\n\n' + wlines
            + '\n\n继续点「游戏百科」标签，集齐 10 讲即可解锁游戏库全部 30 款作品的冷知识！',
          recommendations: wgs.map(card)
        };
      }
    }
    /* ===== 高分榜单专题：10 类不同角度的精选回答 ===== */
    if (msg.indexOf('tga') >= 0 || msg.indexOf('年度游戏') >= 0) {
      return rankAnswer('🏆 TGA 获奖作品盘点：\n游戏库里斩获过 TGA 大奖的作品可不少——《艾尔登法环》TGA 2022 年度游戏、《博德之门 3》TGA 2023 年度游戏、《只狼：影逝二度》TGA 2019 年度游戏、《巫师 3：狂猎》TGA 2015 年度游戏；《黑神话：悟空》拿下 TGA 2024 最佳动作游戏与玩家之声，《哈迪斯》则获 TGA 2020 最佳独立游戏与最佳动作游戏。都是闭眼入的神作！', [1, 2, 3]);
    }
    if (msg.indexOf('热度最高') >= 0 || msg.indexOf('最火') >= 0) {
      var hotTop = db.games.filter(function (x) { return x.is_online; })
        .sort(function (a, b) { return (b.hot || 0) - (a.hot || 0); });
      return rankAnswer('🔥 当前热度榜 Top 6：\n' + hotTop.slice(0, 6).map(function (g) {
        return '· 《' + g.name + '》热度 ' + g.hot + '，评分 ' + g.average_score;
      }).join('\n') + '\n\n热度由社区浏览、评分与讨论量综合计算，点击卡片查看详情～', hotTop.map(function (g) { return g.id; }));
    }
    if (msg.indexOf('独立游戏') >= 0 || msg.indexOf('独立神作') >= 0) {
      return rankAnswer('🌱 好评如潮的独立游戏神作：\n· 《哈迪斯》— Roguelike 动作天花板，死了一千次还想再来一把\n· 《空洞骑士》— 三人团队打造的银河恶魔城里程碑\n· 《死亡细胞》—  Roguelike 与银河城的完美混血\n· 《星露谷物语》— 一个人开发的电子止痛药，全球销量超 4100 万\n· 《环世界》— AI 故事讲述者驱动的殖民地模拟，事故比剧本精彩\n小体量、大创意，独立游戏经常能带来 3A 之外最纯粹的玩法乐趣。', [8, 12, 22]);
    }
    if (msg.indexOf('性价比') >= 0 || msg.indexOf('打折') >= 0 || msg.indexOf('史低') >= 0) {
      return rankAnswer('💰 打折闭眼入的性价比之王：\n· 《巫师 3：狂猎》— 内容量超 150 小时，DLC 质量堪比正传\n· 《侠盗猎车手 5》— 销量超 2 亿份，单人剧情 + GTA Online 双份快乐\n· 《文明 6》— 「再来一回合」就天亮，几十块玩几百小时\n· 《哈迪斯》— 独立游戏价格，3A 级的动作与叙事密度\n这几款每逢打折都是 Steam 榜单常客，预算有限优先从它们入手。', [6, 23, 10]);
    }
    if (msg.indexOf('联机') >= 0 || msg.indexOf('一起玩') >= 0 || msg.indexOf('多人') >= 0) {
      return rankAnswer('🎧 适合和朋友一起玩的联机游戏：\n· 《反恐精英 2》— 免费开玩的 5v5 竞技 FPS，开黑永远的经典\n· 《绝地求生》— 100 人吃鸡大逃杀，和队友组队夺冠\n· 《Apex 英雄》— 英雄技能 + 顶级射击手感的战术竞技\n· 《怪物猎人：世界》— 和好友组队讨伐巨兽，共斗游戏集大成之作\n叫上朋友，语音开黑才是这些游戏的正确打开方式。', [7, 13, 14]);
    }
    if (msg.indexOf('剧情') >= 0 || msg.indexOf('催泪') >= 0) {
      return rankAnswer('📖 剧情封神、玩完久久不能平静的作品：\n· 《巫师 3：狂猎》— 猎魔人的故事与两大 DLC 是 RPG 叙事教科书\n· 《荒野大镖客：救赎 2》— 亚瑟·摩根的西部末路，结局让无数玩家破防\n· 《博德之门 3》— 每个选择都真正改变世界，队友故事个个鲜活\n· 《质量效应：传奇版》— 三部曲横跨银河的太空歌剧，队友生死由你决定\n喜欢剧情驱动的话，这几款请预留充足纸巾与睡眠时间。', [6, 5, 2]);
    }
    if (msg.indexOf('画面') >= 0 || msg.indexOf('画质') >= 0) {
      return rankAnswer('🎨 画面表现最惊艳的几款：\n· 《极限竞速：地平线 5》— 墨西哥雨林火山的开放世界，照片模式随手截图都是壁纸\n· 《黑神话：悟空》— 实景扫描山西古建，国产 3A 的画面里程碑\n· 《赛博朋克 2077》— 更新后的夜之城霓虹雨夜，赛博朋克美学天花板\n· 《霍格沃茨之遗》— 霍格沃茨城堡与魔法世界的沉浸式还原\n建议搭配好显卡与显示器享用。', [11, 3, 4]);
    }
    if (msg.indexOf('耐玩') >= 0 || msg.indexOf('杀时间') >= 0 || msg.indexOf('游戏时长') >= 0) {
      return rankAnswer('⏳ 最杀时间的耐玩游戏排行榜：\n· 《文明 6》— 「就再玩一回合」，一回合到天亮\n· 《环世界》— 每个殖民地都是独一无二的故事，几百小时起步\n· 《侠盗猎车手 5》— 三人剧情 + GTA Online 十年持续更新\n· 《星露谷物语》— 种田钓鱼下矿，不知不觉就过了三个季节\n时间充裕（或者干脆不想睡觉）的时候再打开它们。', [10, 28, 23]);
    }
    if (msg.indexOf('新手') >= 0 || msg.indexOf('入门') >= 0 || msg.indexOf('入坑') >= 0) {
      return rankAnswer('🌱 新手入坑友好、不劝退的入门推荐：\n· 《极限竞速：地平线 5》— 辅助线、自动刹车、回退功能齐全，开车看风景都开心\n· 《星露谷物语》— 节奏自己定，种田钓鱼零压力\n· 《哈迪斯》— 难度曲线顺滑，失败也有剧情奖励，越死越上瘾\n· 《巫师 3》— 最低难度下就是一部互动奇幻巨著\n先从这几款建立信心，再挑战魂系也不迟。', [11, 9, 8]);
    }
    /* 4) 闲聊 / 日常对话 */
    for (var c = 0; c < CHITCHAT.length; c++) {
      var cws = CHITCHAT[c][0];
      for (var c2 = 0; c2 < cws.length; c2++) {
        if (msg.indexOf(cws[c2]) >= 0) return { reply: pick(CHITCHAT[c][1]), recommendations: [] };
      }
    }
    var g = findGame(body.message || '');
    /* 5) 游戏知识问答：提到具体游戏 + 想了解（或直接报游戏名） */
    if (g) {
      var bare = msg === g.name.toLowerCase() || msg === (g.name_en || '').toLowerCase() || (body.message || '').trim() === g.name;
      if (bare || INTRO.some(function (w) { return msg.indexOf(w) >= 0; })) {
        var ans = knowledge(g, 'intro');
        if (ans) return ans;
      }
    }
    /* 6) 查评分 / 榜单 */
    for (var k = 0; k < SCORE.length; k++) {
      if (msg.indexOf(SCORE[k]) >= 0 || (msg.indexOf('多少') >= 0 && msg.indexOf('分') >= 0)) {
        if (g) {
          var verdict = g.average_score >= 8 ? '口碑相当不错，值得一试！' : '中规中矩，可以看看社区评测再决定。';
          var extra = KNOW[g.name] ? '\n\n📌 冷知识：' + pick(KNOW[g.name].f) : '';
          return { reply: '《' + g.name + '》（' + (g.name_en || g.name) + '）综合评分 ' + g.average_score + ' 分，共 ' + (g.rating_count || 0) + ' 人参与评分。\n标签：' + (g.tags.slice(0, 4).join(' / ') || '暂无标签') + '。\n' + verdict + extra, recommendations: [card(g)] };
        }
        /* 榜单类问题（评分最高 / 排行榜 / 高分推荐）：返回高分游戏 Top */
        if (RANK.some(function (w) { return msg.indexOf(w) >= 0; })) {
          var top = db.games.filter(function (x) { return x.is_online; })
            .sort(function (a, b) { return (b.average_score - a.average_score) || (b.hot - a.hot); }).slice(0, 3);
          return { reply: '目前游戏库中评分最高的几款：' + top.map(function (p) { return '《' + p.name + '》' + p.average_score + ' 分'; }).join('、') + '。点击下方卡片可查看详情与社区评测～', recommendations: top.map(card) };
        }
        var hotN = db.games.filter(function (x) { return x.is_online; })
          .sort(function (x, y) { return (y.hot || 0) - (x.hot || 0); }).slice(0, 6)
          .map(function (p) { return '《' + p.name + '》'; }).join('、');
        return { reply: '这个名称我没有在游戏库中找到 🤔 目前库里的热门游戏有：' + hotN + ' 等。\n可以说完整名称（如「艾尔登法环怎么样」），或者直接说「推荐几款 RPG」让我帮你挑～', recommendations: [] };
      }
    }
    /* 7) 攻略求助（游戏库内游戏优先使用专属上手建议） */
    for (var m = 0; m < GUIDE.length; m++) {
      if (msg.indexOf(GUIDE[m]) >= 0) {
        var kg = (g && KNOW[g.name] && KNOW[g.name].t.length) ? KNOW[g.name] : null;
        if (kg) {
          var tips = kg.t.map(function (t, i) { return (i + 1) + '. ' + t; }).join('\n');
          return { reply: '《' + g.name + '》的上手建议：\n\n' + tips + '\n\n还想聊具体的关卡 / Boss / Build，随时告诉我！', recommendations: [card(g)] };
        }
        var gn3 = g ? '《' + g.name + '》' : '这款游戏';
        return { reply: gn3 + '的通用通关思路：\n\n1. 前期优先提升生存与核心属性，不要急着推主线；\n2. 卡关时先探索支线 / 刷级 / 补装备，回头往往水到渠成；\n3. 观察敌人前摇与弱点，善用属性克制与地形；\n4. 资源类道具留给关键战斗。\n\n告诉我具体卡在哪一关 / 哪个 Boss，我给你更针对性的建议。', recommendations: g ? [card(g)] : [] };
      }
    }
    /* 8) 推荐 */
    var recoHit = false, typeKws = [];
    RECO.forEach(function (w) { if (msg.indexOf(w) >= 0) recoHit = true; });
    TYPES.forEach(function (w) { if (msg.indexOf(w) >= 0) typeKws.push(w); });
    if (recoHit || typeKws.length) {
      var liked = {};
      db.favorites.forEach(function (f) { liked[f.game_id] = 1; });
      var pool = db.games.filter(function (g) { return g.is_online; });
      var hits = pool.filter(function (g) {
        var hay = (g.name + ' ' + g.name_en + ' ' + g.tags.join(' ') + ' ' + g.description).toLowerCase();
        var kws = typeKws.length ? typeKws : msg.split(/[\s,，、。！!?？]+/).filter(function (x) { return x.length >= 2; }).slice(0, 5);
        return kws.some(function (kw) { return hay.indexOf(kw) >= 0; });
      });
      if (!hits.length) hits = pool;
      hits.sort(function (a, b) { return (b.average_score - a.average_score) || (b.hot - a.hot); });
      var picks = hits.slice(0, 3);
      var names = picks.map(function (g) { return '《' + g.name + '》'; }).join('、');
      var lead = (typeKws.length || recoHit) ? '根据「' + (typeKws.join(' ') || (body.message || '').trim()) + '」，为你挑选了：\n' : '为你推荐：\n';
      return { reply: lead + names + '。点击下方卡片可查看游戏详情与社区评测～', recommendations: picks.map(card) };
    }
    /* 9) 兜底 */
    return { reply: '这个问题有点超出我的能力范围啦 🤔 我是游戏助手，比较擅长：\n· 按口味推荐游戏\n· 聊游戏库内游戏的冷知识\n· 查评分、给通关建议\n· 解答平台功能\n闲聊也欢迎～要不要让我讲个游戏圈的冷笑话？', recommendations: [] };
  }

  /* ---------- 游戏评分聚合（评测/评分提交删除后重算，管理员不可手动修改） ----------
     四维分仅由带四维评分的公开评测聚合；综合总分与参与人数 = 公开评测（每篇计 1 人）
     + 用户 1-10 分评分（每条计 1 人）合并计算 */
  function recalcGame(db, gameId) {
    var g = db.games.filter(function (x) { return x.id === gameId; })[0];
    if (!g) return;
    var rows = db.reviews.filter(function (r) {
      return r.game_id === gameId && r.status === 'published'
        && r.score_story != null && r.score_graphic != null
        && r.score_gameplay != null && r.score_opt != null;
    });
    var urs = (db.ratings || []).filter(function (r) { return r.game_id === gameId; });
    if (rows.length) {
      function avgOf(k) { return rows.reduce(function (s, r) { return s + r[k]; }, 0) / rows.length; }
      g.score_story = Math.round(avgOf('score_story') * 10) / 10;
      g.score_graphic = Math.round(avgOf('score_graphic') * 10) / 10;
      g.score_gameplay = Math.round(avgOf('score_gameplay') * 10) / 10;
      g.score_opt = Math.round(avgOf('score_opt') * 10) / 10;
    } else {
      g.score_story = g.score_graphic = g.score_gameplay = g.score_opt = 0;
    }
    var total = rows.reduce(function (s, r) { return s + (r.score_story + r.score_graphic + r.score_gameplay + r.score_opt) / 4; }, 0)
      + urs.reduce(function (s, r) { return s + r.score; }, 0);
    var n = rows.length + urs.length;
    g.rating_count = n;
    g.average_score = n ? Math.round(total / n * 10) / 10 : 0;
  }

  /* 四维评分入参校验（1-10 整数，允许 null） */
  function pickScores(body) {
    var out = {};
    ['score_story', 'score_graphic', 'score_gameplay', 'score_opt'].forEach(function (k) {
      if (body[k] === undefined) return;
      if (body[k] === null) { out[k] = null; return; }
      var v = body[k];
      if (typeof v !== 'number' || !isFinite(v) || Math.floor(v) !== v || v < 1 || v > 10) {
        fail(400, k + ' 必须为 1-10 的整数');
      }
      out[k] = v;
    });
    return out;
  }

  /* ---------- 路由 ---------- */
  function handle(method, path, body, headers) {
    headers = headers || {};
    var db = load();
    var p = path.split('?')[0];
    var query = {};
    if (path.indexOf('?') >= 0) {
      path.split('?')[1].split('&').forEach(function (kv) {
        var parts = kv.split('=');
        query[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1] || '');
      });
    }
    body = body || {};
    var m, res;

    function paginate(list, page, size) {
      page = parseInt(page || 1, 10); size = parseInt(size || 9, 10);
      var start = (page - 1) * size;
      return { items: list.slice(start, start + size), total: list.length, page: page, page_size: size, total_pages: Math.max(1, Math.ceil(list.length / size)) };
    }

    /* ===== 认证 ===== */
    if (method === 'POST' && p === '/api/auth/register') {
      if (!body.username || !body.email || !body.password) fail(400, '用户名、邮箱、密码不能为空');
      if (db.users.some(function (u) { return u.username === body.username; })) fail(400, '用户名已存在');
      if (db.users.some(function (u) { return u.email === body.email; })) fail(400, '邮箱已被注册');
      var nu = { id: ++db.seq.users, username: body.username, email: body.email, password: body.password,
        role: 'player', is_active: true, created_at: nowIso(),
        profile: { nickname: body.username, avatar: '', bio: '' } };
      db.users.push(nu); save(db);
      return { message: '注册成功，请登录' };
    }
    if (method === 'POST' && p === '/api/auth/login') {
      var key = (body.username_or_email || '').trim();
      var u = db.users.filter(function (x) { return x.username === key || x.email === key; })[0];
      if (!u || u.password !== body.password) fail(401, '账号或密码错误');
      if (!u.is_active) fail(403, '账号已被封禁，请联系管理员');
      return { access_token: tokenOf(u.id), token_type: 'bearer', user_id: u.id, role: u.role, user: publicUser(u) };
    }

    /* ===== 用户 ===== */
    if (method === 'GET' && p === '/api/users/me') {
      return publicUser(authUser(db, headers));
    }
    if (method === 'PUT' && p === '/api/users/me') {
      var me = authUser(db, headers);
      me.profile.nickname = body.nickname !== undefined ? body.nickname : me.profile.nickname;
      me.profile.avatar = body.avatar !== undefined ? body.avatar : me.profile.avatar;
      me.profile.bio = body.bio !== undefined ? body.bio : me.profile.bio;
      save(db);
      return publicUser(me);
    }
    if (method === 'PUT' && p === '/api/users/me/password') {
      var me2 = authUser(db, headers);
      if (me2.password !== body.old_password) fail(400, '原密码不正确');
      if (!body.new_password || body.new_password.length < 6) fail(400, '新密码至少 6 位');
      me2.password = body.new_password; save(db);
      return { message: '密码修改成功' };
    }
    if (method === 'GET' && p === '/api/users/me/creator-application') {
      var meA = authUser(db, headers);
      var last = db.applies.filter(function (a) { return a.user_id === meA.id; })
        .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); })[0];
      if (!last) return { status: 'none', application: null };
      return {
        status: last.status,
        application: {
          id: last.id, apply_reason: last.apply_reason,
          good_at: last.good_at || '', experience: last.experience || '',
          created_at: last.created_at,
        },
      };
    }
    if (method === 'POST' && p === '/api/users/apply-creator') {
      var me3 = authUser(db, headers);
      requireRole(me3, 'player');
      if (me3.role === 'creator' || me3.role === 'admin') fail(400, '你已经是创作者了');
      var reason = (body.apply_reason || '').trim();
      if (reason.length < 10) fail(400, '申请理由至少 10 个字，请介绍你的写作经验或游戏经历');
      if (reason.length > 200) fail(400, '申请理由不能超过 200 个字');
      var goodAt = (body.good_at || '').trim();
      if (goodAt.length > 100) fail(400, '擅长方向不能超过 100 个字');
      var exp = (body.experience || '').trim();
      if (exp.length > 200) fail(400, '游戏经历不能超过 200 个字');
      var pending = db.applies.some(function (a) { return a.user_id === me3.id && a.status === 'pending'; });
      if (pending) fail(400, '已有待审核的申请，请耐心等待');
      db.applies.push({ id: ++db.seq.applies, user_id: me3.id, apply_reason: reason,
        good_at: goodAt, experience: exp, status: 'pending', audit_user_id: null, created_at: nowIso() });
      save(db);
      return { message: '申请已提交，等待管理员审核' };
    }

    /* ===== 游戏 ===== */
    if (method === 'GET' && p === '/api/games') {
      var list = db.games.filter(function (g) { return g.is_online; });
      if (query.category_id) list = list.filter(function (g) { return g.category_id === parseInt(query.category_id, 10); });
      if (query.keyword) {
        var kw = query.keyword.toLowerCase();
        list = list.filter(function (g) {
          return (g.name + g.name_en + g.tags.join(' ') + g.description).toLowerCase().indexOf(kw) >= 0;
        });
      }
      var sort = query.sort || 'hot';
      list.sort(function (a, b) {
        if (sort === 'newest') return b.release_date.localeCompare(a.release_date);
        if (sort === 'score') return b.average_score - a.average_score;
        return b.hot - a.hot;
      });
      var result = paginate(list.map(function (g) { return gameOut(g, db); }), query.page, query.page_size || 9);
      result.categories = db.categories;
      return result;
    }
    if ((m = p.match(/^\/api\/games\/(\d+)$/)) && method === 'GET') {
      var g = db.games.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!g) fail(404, '游戏不存在');
      var out = gameOut(g, db);
      var meFav = authOpt(db, headers);
      out.is_favorite = meFav && db.favorites.some(function (f) { return f.user_id === meFav.id && f.game_id === g.id; });
      var rec = db.records.filter(function (r) { return meFav && r.user_id === meFav.id && r.game_id === g.id; })[0];
      out.play_status = rec ? rec.play_status : null;
      var myRt = meFav && db.ratings.filter(function (r) { return r.user_id === meFav.id && r.game_id === g.id; })[0];
      out.my_rating = myRt ? myRt.score : null;
      return out;
    }
    /* 用户对游戏提交 1-10 分评分：同一用户仅一条记录，重复提交=修改分数 */
    if ((m = p.match(/^\/api\/games\/(\d+)\/rating$/)) && method === 'POST') {
      var rtGid = parseInt(m[1], 10);
      var rtG = db.games.filter(function (x) { return x.id === rtGid; })[0];
      if (!rtG) fail(404, '游戏不存在');
      var rtU = authUser(db, headers);
      var sc = body.score;
      if (typeof sc !== 'number' || !isFinite(sc) || Math.floor(sc) !== sc || sc < 1 || sc > 10) {
        fail(400, '评分必须为 1-10 的整数');
      }
      var exRt = db.ratings.filter(function (r) { return r.user_id === rtU.id && r.game_id === rtGid; })[0];
      var rtMsg;
      if (exRt) { exRt.score = sc; exRt.updated_at = nowIso(); rtMsg = '评分已更新'; }
      else {
        db.ratings.push({ id: ++db.seq.ratings, game_id: rtGid, user_id: rtU.id, score: sc,
          created_at: nowIso(), updated_at: nowIso() });
        rtMsg = '评分成功';
      }
      recalcGame(db, rtGid);
      save(db);
      return { message: rtMsg, game_id: rtGid, score: sc, my_rating: sc,
        average_score: rtG.average_score, rating_count: rtG.rating_count };
    }
    if ((m = p.match(/^\/api\/games\/(\d+)\/reviews$/)) && method === 'GET') {
      var gid = parseInt(m[1], 10);
      var rl = db.reviews.filter(function (r) { return r.game_id === gid && r.status === 'published'; });
      if (query.keyword) {
        var gkw = query.keyword.toLowerCase();
        rl = rl.filter(function (r) {
          return ((r.title || '') + ' ' + (r.content || '')).toLowerCase().indexOf(gkw) >= 0;
        });
      }
      /* 排序加权：精选优先 → 创作者等级高者优先 → 时间倒序 */
      rl.sort(function (a, b) {
        var ua = db.users.filter(function (x) { return x.id === a.user_id; })[0];
        var ub = db.users.filter(function (x) { return x.id === b.user_id; })[0];
        return (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0)
          || ((ub ? ub.creator_level || 0 : 0) - (ua ? ua.creator_level || 0 : 0))
          || b.created_at.localeCompare(a.created_at);
      });
      return paginate(rl.map(function (r) { return reviewOut(r, db); }), query.page, 5);
    }
    /* 全部公开评测列表（首页「游戏评测」专区）：精选→等级→时间倒序，keyword 按游戏名称过滤 */
    if (method === 'GET' && p === '/api/reviews') {
      var pub = db.reviews.filter(function (r) { return r.status === 'published'; });
      if (query.keyword) {
        var pkw = query.keyword.toLowerCase();
        pub = pub.filter(function (r) {
          var rgm = db.games.filter(function (x) { return x.id === r.game_id; })[0];
          return rgm && (rgm.name + ' ' + (rgm.name_en || '')).toLowerCase().indexOf(pkw) >= 0;
        });
      }
      pub.sort(function (a, b) {
        var ua = db.users.filter(function (x) { return x.id === a.user_id; })[0];
        var ub = db.users.filter(function (x) { return x.id === b.user_id; })[0];
        return (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0)
          || ((ub ? ub.creator_level || 0 : 0) - (ua ? ua.creator_level || 0 : 0))
          || b.created_at.localeCompare(a.created_at) || (b.id - a.id);
      });
      return paginate(pub.map(function (r) { return publicReviewCard(r, db); }), query.page, query.page_size || 12);
    }
    /* 相似游戏推荐：同分类 + 标签重合度加权，返回 3-4 款 */
    if ((m = p.match(/^\/api\/games\/(\d+)\/similar$/)) && method === 'GET') {
      var sg0 = db.games.filter(function (g) { return g.id === parseInt(m[1], 10); })[0];
      if (!sg0) fail(404, '游戏不存在');
      var tags0 = sg0.tags || [];
      var cands = db.games.filter(function (g) { return g.is_online && g.id !== sg0.id; });
      var scored = cands.map(function (g) {
        var s = 0;
        if (g.category_id === sg0.category_id) s += 2;
        (g.tags || []).forEach(function (t) { if (tags0.indexOf(t) >= 0) s += 1; });
        return { g: g, s: s };
      }).filter(function (x) { return x.s > 0; });
      scored.sort(function (a, b) { return (b.s - a.s) || (b.g.hot - a.g.hot); });
      return { items: scored.slice(0, 4).map(function (x) {
        var cat = db.categories.filter(function (c) { return c.id === x.g.category_id; })[0];
        return { id: x.g.id, name: x.g.name, name_en: x.g.name_en || '', cover_url: x.g.cover_url,
          average_score: x.g.average_score, category_name: cat ? cat.name : '' };
      }) };
    }
    /* 该游戏公开评测攻略总数 */
    if ((m = p.match(/^\/api\/games\/(\d+)\/reviews\/count$/)) && method === 'GET') {
      var cg0 = parseInt(m[1], 10);
      if (!db.games.some(function (g) { return g.id === cg0; })) fail(404, '游戏不存在');
      return { game_id: cg0, count: db.reviews.filter(function (r) { return r.game_id === cg0 && r.status === 'published'; }).length };
    }

    /* ===== 单篇评测详情：已发布对所有人可见；待审核/已驳回仅作者本人与管理员可预览 ===== */
    if ((m = p.match(/^\/api\/reviews\/(\d+)$/)) && method === 'GET') {
      var rd = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rd) fail(404, '评测不存在');
      var rdMe = authOpt(db, headers);
      if (rd.status !== 'published') {
        if (!rdMe || (rdMe.id !== rd.user_id && rdMe.role !== 'admin')) {
          fail(403, '无权限查看该评测（未通过审核的内容仅作者本人可见）');
        }
        var rdPreview = reviewOut(rd, db);
        rdPreview.my_liked = false; rdPreview.my_favorited = false; rdPreview.can_edit = false;
        return rdPreview;   // 未过审预览不增加阅读量
      }
      rd.read_count = (rd.read_count || 0) + 1;
      save(db);
      var rdOut = reviewOut(rd, db);
      rdOut.my_liked = !!(rdMe && rd.likes && rd.likes.indexOf(rdMe.id) >= 0);
      rdOut.my_favorited = !!(rdMe && rd.favs && rd.favs.indexOf(rdMe.id) >= 0);
      rdOut.can_edit = !!(rdMe && rdMe.id === rd.user_id && (rdMe.creator_level || 0) >= 1 && !rd.edit_used);
      return rdOut;
    }
    /* 该评测攻略下的专属评论区 */
    if ((m = p.match(/^\/api\/reviews\/(\d+)\/comments$/)) && method === 'GET') {
      var rcid = parseInt(m[1], 10);
      if (!db.reviews.some(function (x) { return x.id === rcid; })) fail(404, '评测不存在');
      var rcu = authOpt(db, headers);
      var rcl = db.comments.filter(function (c) { return c.target_type === 'review' && c.target_id === rcid; })
        .sort(function (a, b) { return a.created_at.localeCompare(b.created_at); });
      rcl.forEach(function (c) { c.__uid = rcu ? rcu.id : 0; });
      return { items: rcl.map(function (c) { return commentOut(c, db); }) };
    }

    /* ===== 游戏短评论区（自动精选运行时计算 + 普通分页） ===== */
    if ((m = p.match(/^\/api\/games\/(\d+)\/comments$/)) && method === 'GET') {
      var cgid = parseInt(m[1], 10);
      if (!db.games.some(function (g) { return g.id === cgid; })) fail(404, '游戏不存在');
      var gcu = authOpt(db, headers);
      var gAll = db.comments.filter(function (c) { return c.target_type === 'game' && c.target_id === cgid; });
      gAll.forEach(function (c) { c.__uid = gcu ? gcu.id : 0; });
      /* 自动精选：点赞最高者作唯一候选（并列取创建最早），无字数/内容限制 */
      var cand = gAll.slice().sort(function (a, b) {
        return (b.like_count - a.like_count) || a.created_at.localeCompare(b.created_at) || (a.id - b.id);
      })[0];
      var autoSel = cand || null;
      var excludeId = autoSel ? autoSel.id : null;
      var gNormals = gAll.filter(function (c) { return c.id !== excludeId; })
        .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); });
      var gPage = parseInt(query.page, 10) || 1;
      var gPageSize = Math.min(Math.max(parseInt(query.page_size, 10) || 5, 1), 10);
      var gTotalPages = Math.max(1, Math.ceil(gNormals.length / gPageSize));
      var gStart = (gPage - 1) * gPageSize;
      return {
        auto_selected_comment: autoSel ? commentOut(autoSel, db) : null,
        items: gNormals.slice(gStart, gStart + gPageSize).map(function (c) { return commentOut(c, db); }),
        total: gNormals.length, page: gPage, page_size: gPageSize, total_pages: gTotalPages
      };
    }
    if ((m = p.match(/^\/api\/games\/(\d+)\/comments$/)) && method === 'POST') {
      var pcu = authUser(db, headers);
      var pcgid = parseInt(m[1], 10);
      if (!db.games.some(function (g) { return g.id === pcgid; })) fail(404, '游戏不存在');
      if (!body.content || !body.content.trim()) fail(400, '评论内容不能为空');
      var pnc = {
        id: ++db.seq.comments, user_id: pcu.id, target_type: 'game', target_id: pcgid,
        parent_id: body.parent_id || null, content: body.content.trim(),
        like_count: 0, created_at: nowIso(), likes: []
      };
      db.comments.push(pnc); save(db);
      pnc.__uid = pcu.id;
      return commentOut(pnc, db);
    }

    /* ===== 收藏 ===== */
    if (method === 'GET' && p === '/api/favorites') {
      var fu = authUser(db, headers);
      var favs = db.favorites.filter(function (f) { return f.user_id === fu.id; })
        .map(function (f) { return gameOut(db.games.filter(function (g) { return g.id === f.game_id; })[0], db); })
        .filter(Boolean);
      return { items: favs, total: favs.length };
    }
    if (method === 'POST' && p === '/api/favorites') {
      var fu2 = authUser(db, headers);
      if (!db.games.some(function (g) { return g.id === body.game_id; })) fail(404, '游戏不存在');
      if (!db.favorites.some(function (f) { return f.user_id === fu2.id && f.game_id === body.game_id; })) {
        db.favorites.push({ id: ++db.seq.favorites, user_id: fu2.id, game_id: body.game_id, created_at: nowIso() });
        save(db);
      }
      return { message: '收藏成功' };
    }
    if ((m = p.match(/^\/api\/favorites\/(\d+)$/)) && method === 'DELETE') {
      var fu3 = authUser(db, headers);
      db.favorites = db.favorites.filter(function (f) { return !(f.user_id === fu3.id && f.game_id === parseInt(m[1], 10)); });
      save(db);
      return { message: '已取消收藏' };
    }

    /* ===== 游玩记录 ===== */
    if (method === 'GET' && p === '/api/play-record') {
      var ru = authUser(db, headers);
      var recs = db.records.filter(function (r) { return r.user_id === ru.id; }).map(function (r) {
        var g = db.games.filter(function (x) { return x.id === r.game_id; })[0];
        return Object.assign({}, r, { game: g ? gameOut(g, db) : null });
      });
      return { items: recs };
    }
    if (method === 'POST' && p === '/api/play-record') {
      var ru2 = authUser(db, headers);
      var status = body.play_status;
      if (['want', 'playing', 'completed'].indexOf(status) < 0) fail(400, '状态非法');
      var existing = db.records.filter(function (r) { return r.user_id === ru2.id && r.game_id === body.game_id; })[0];
      if (existing) { existing.play_status = status; existing.updated_at = nowIso(); }
      else db.records.push({ id: ++db.seq.records, user_id: ru2.id, game_id: body.game_id, play_status: status, created_at: nowIso(), updated_at: nowIso() });
      save(db);
      return { message: '游玩状态已更新', play_status: status };
    }

    /* ===== 评论 ===== */
    if ((m = p.match(/^\/api\/comments\/mine$/)) && method === 'GET') {
      var mcU = authUser(db, headers);
      var mcList = db.comments.filter(function (c) { return c.user_id === mcU.id; })
        .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); })
        .map(function (c) {
          var out = commentOut(c, db);
          if (c.target_type === 'game') {
            var mg = db.games.filter(function (x) { return x.id === c.target_id; })[0];
            out.target_name = mg ? mg.name : '已删除游戏';
            out.target_cover = mg ? mg.cover_url : '';
          } else {
            var mr = db.reviews.filter(function (x) { return x.id === c.target_id; })[0];
            out.target_name = mr ? mr.title : '已删除评测';
            if (mr) {
              var mrg = db.games.filter(function (x) { return x.id === mr.game_id; })[0];
              out.target_cover = mrg ? mrg.cover_url : '';
            } else {
              out.target_cover = '';
            }
          }
          return out;
        });
      var mcResult = paginate(mcList, query.page, query.page_size || 10);
      return mcResult;
    }
    if ((m = p.match(/^\/api\/comments$/)) && method === 'GET') {
      var tid = parseInt(query.target_id, 10);
      var cl = db.comments.filter(function (c) { return c.target_type === (query.target_type || 'review') && c.target_id === tid; })
        .sort(function (a, b) { return a.created_at.localeCompare(b.created_at); });
      var cu = authOpt(db, headers);
      cl.forEach(function (c) { c.__uid = cu ? cu.id : 0; });
      return { items: cl.map(function (c) { return commentOut(c, db); }) };
    }
    if (method === 'POST' && p === '/api/comments') {
      var cu2 = authUser(db, headers);
      if (!body.content || !body.content.trim()) fail(400, '评论内容不能为空');
      /* 契约：POST /api/comments {game_id, content} 发布游戏短评论 */
      var ncType = body.target_type || 'review';
      var ncTid = body.target_id;
      if (body.game_id) {
        ncType = 'game';
        ncTid = body.game_id;
        if (!db.games.some(function (g) { return g.id === body.game_id; })) fail(404, '游戏不存在');
      }
      var nc = { id: ++db.seq.comments, user_id: cu2.id, target_type: ncType,
        target_id: ncTid, parent_id: body.parent_id || null, content: body.content.trim(),
        like_count: 0, created_at: nowIso(), likes: [] };
      db.comments.push(nc); save(db);
      nc.__uid = cu2.id;
      return commentOut(nc, db);
    }
    if ((m = p.match(/^\/api\/comments\/(\d+)\/like$/)) && method === 'POST') {
      var lu = authUser(db, headers);
      var c = db.comments.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!c) fail(404, '评论不存在');
      c.likes = c.likes || [];
      var idx = c.likes.indexOf(lu.id);
      if (idx >= 0) { c.likes.splice(idx, 1); c.like_count--; } else { c.likes.push(lu.id); c.like_count++; }
      save(db);
      return { like_count: c.like_count, liked: idx < 0 };
    }

    /* ===== 创作者：评测 ===== */
    if (method === 'POST' && p === '/api/reviews') {
      var cru = authUser(db, headers);
      requireRole(cru, 'creator');
      if (!body.title || !body.game_id) fail(400, '标题与关联游戏必填');
      var sc0 = pickScores(body);
      var nr = { id: ++db.seq.reviews, game_id: body.game_id, user_id: cru.id, title: body.title,
        content: body.content || '', tags: body.tags || [], status: 'draft', audit_status: null,
        score_story: sc0.score_story || null, score_graphic: sc0.score_graphic || null,
        score_gameplay: sc0.score_gameplay || null, score_opt: sc0.score_opt || null,
        audit_score: null, audit_reason: '', read_count: 0, like_count: 0, fav_count: 0, created_at: nowIso() };
      db.reviews.push(nr); save(db);
      return reviewOut(nr, db);
    }
    if ((m = p.match(/^\/api\/reviews\/(\d+)$/)) && method === 'PUT') {
      var cru2 = authUser(db, headers);
      var rv = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv) fail(404, '评测不存在');
      if (rv.user_id !== cru2.id) fail(403, '只能编辑自己的文章');
      /* L1 权益：已发布评测仅 L1 及以上可编辑 1 次 */
      if (rv.status === 'published') {
        if ((cru2.creator_level || 0) < 1) {
          fail(403, 'L0 见习创作者不可编辑已发布评测，发布优质评测累积积分升至 L1（200 积分）后解锁');
        }
        if (rv.edit_used) fail(400, '该篇已发布评测的 1 次编辑机会已用完');
      }
      rv.title = body.title !== undefined ? body.title : rv.title;
      rv.content = body.content !== undefined ? body.content : rv.content;
      rv.game_id = body.game_id !== undefined ? body.game_id : rv.game_id;
      rv.tags = body.tags !== undefined ? body.tags : rv.tags;
      var sc1 = pickScores(body);
      ['score_story', 'score_graphic', 'score_gameplay', 'score_opt'].forEach(function (k) {
        if (sc1[k] !== undefined) rv[k] = sc1[k];
      });
      if (rv.status === 'published') rv.edit_used = true;  // 已发布评测编辑消耗 1 次机会
      save(db);
      return reviewOut(rv, db);
    }
    if ((m = p.match(/^\/api\/reviews\/(\d+)$/)) && method === 'DELETE') {
      var cru3 = authUser(db, headers);
      var rv2 = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv2) fail(404, '评测不存在');
      if (rv2.user_id !== cru3.id && cru3.role !== 'admin') fail(403, '无权删除');
      var delGid = rv2.game_id;
      /* 已发布评测被删除：追回该篇全部积分（发布+精选+获赞+收藏）并额外扣 30 */
      if (rv2.status === 'published') {
        var author = db.users.filter(function (x) { return x.id === rv2.user_id; })[0];
        if (author && author.role !== 'player') {
          var earned = 20 + (rv2.is_featured ? 30 : 0)
            + 0.2 * (rv2.like_count || 0) + 0.5 * (rv2.fav_count || 0);
          addPointRecord(db, rv2.user_id, -(earned + 30),
            '评测《' + rv2.title + '》被删除：追回积分 ' + Math.round(earned * 10) / 10 + '，额外扣 30', rv2.id);
        }
      }
      db.reviews = db.reviews.filter(function (x) { return x.id !== rv2.id; });
      recalcGame(db, delGid);  // 删除评测后重算游戏四维评分
      save(db);
      return { message: '已删除' };
    }
    if ((m = p.match(/^\/api\/reviews\/(\d+)\/submit-audit$/)) && method === 'POST') {
      var cru4 = authUser(db, headers);
      requireRole(cru4, 'creator');
      var rv3 = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv3) fail(404, '评测不存在');
      if (rv3.user_id !== cru4.id) fail(403, '无权操作');
      if (rv3.status === 'published') fail(400, '文章已发布');
      if (rv3.status === 'audit' || rv3.status === 'manual_review') fail(400, '文章正在审核中');
      /* 提交后一律进入「待审核」，由管理员人工通过/驳回；AI 仅计算风险分作为参考 */
      var audit = aiAudit(rv3.title, rv3.content);
      var log = { id: ++db.seq.logs, review_id: rv3.id, audit_type: 'ai', risk_score: audit.risk_score,
        reason: audit.reasons.join('；'), operator_id: 1, created_at: nowIso() };
      db.auditLogs.push(log);
      rv3.audit_score = audit.risk_score;
      rv3.status = 'manual_review'; rv3.audit_status = 'manual_review'; rv3.audit_reason = audit.reasons.join('；');
      save(db);
      return { message: '已提交审核，等待管理员审核', status: 'pending', audit: audit };
    }
    /* ===== 评测点赞/收藏（幂等切换；作者分别获 0.2/0.5 积分，给自己不加分） ===== */
    if ((m = p.match(/^\/api\/reviews\/(\d+)\/like$/)) && method === 'POST') {
      var lkU = authUser(db, headers);
      var lkR = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!lkR || lkR.status !== 'published') fail(404, '公开评测不存在');
      lkR.likes = lkR.likes || [];
      var idx = lkR.likes.indexOf(lkU.id);
      var liked;
      if (idx >= 0) {
        lkR.likes.splice(idx, 1); liked = false;
        if (lkU.id !== lkR.user_id) addPointRecord(db, lkR.user_id, -0.2, '评测《' + lkR.title + '》被取消点赞', lkR.id);
      } else {
        lkR.likes.push(lkU.id); liked = true;
        if (lkU.id !== lkR.user_id) addPointRecord(db, lkR.user_id, 0.2, '评测《' + lkR.title + '》获得点赞', lkR.id);
      }
      lkR.like_count = lkR.likes.length;
      save(db);
      return { liked: liked, like_count: lkR.like_count };
    }
    if ((m = p.match(/^\/api\/reviews\/(\d+)\/favorite$/)) && method === 'POST') {
      var fvU = authUser(db, headers);
      var fvR = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!fvR || fvR.status !== 'published') fail(404, '公开评测不存在');
      fvR.favs = fvR.favs || [];
      var fi = fvR.favs.indexOf(fvU.id);
      var faved;
      if (fi >= 0) {
        fvR.favs.splice(fi, 1); faved = false;
        if (fvU.id !== fvR.user_id) addPointRecord(db, fvR.user_id, -0.5, '评测《' + fvR.title + '》被取消收藏', fvR.id);
      } else {
        fvR.favs.push(fvU.id); faved = true;
        if (fvU.id !== fvR.user_id) addPointRecord(db, fvR.user_id, 0.5, '评测《' + fvR.title + '》被收藏', fvR.id);
      }
      fvR.fav_count = fvR.favs.length;
      save(db);
      return { favorited: faved, fav_count: fvR.fav_count };
    }
    /* ===== 我的评测：当前登录用户发布的全部评测（个人中心，含未过审） ===== */
    if (method === 'GET' && p === '/api/reviews/mine') {
      var mnU = authUser(db, headers);
      var mnItems = db.reviews.filter(function (r) { return r.user_id === mnU.id; })
        .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); });
      return { items: mnItems.map(function (r) { return reviewOut(r, db); }), total: mnItems.length };
    }
    /* ===== 我的评测互动：我赞过 / 我收藏的评测（个人中心，仅已发布） ===== */
    if (method === 'GET' && p === '/api/reviews/me/likes') {
      var mlU = authUser(db, headers);
      var mlItems = db.reviews.filter(function (r) {
        return (r.likes || []).indexOf(mlU.id) >= 0 && r.status === 'published';
      }).sort(function (a, b) { return b.like_count - a.like_count; });
      return { items: mlItems.map(function (r) { return reviewOut(r, db); }), total: mlItems.length };
    }
    if (method === 'GET' && p === '/api/reviews/me/favorites') {
      var mfU = authUser(db, headers);
      var mfItems = db.reviews.filter(function (r) {
        return (r.favs || []).indexOf(mfU.id) >= 0 && r.status === 'published';
      }).sort(function (a, b) { return b.fav_count - a.fav_count; });
      return { items: mfItems.map(function (r) { return reviewOut(r, db); }), total: mfItems.length };
    }
    if (method === 'GET' && p === '/api/creator/reviews') {
      var cu3 = authUser(db, headers);
      requireRole(cu3, 'creator');
      var mine = db.reviews.filter(function (r) { return r.user_id === cu3.id; })
        .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); });
      return { items: mine.map(function (r) { return reviewOut(r, db); }) };
    }
    if (method === 'GET' && p === '/api/creator/statistics') {
      var cu4 = authUser(db, headers);
      requireRole(cu4, 'creator');
      var mine2 = db.reviews.filter(function (r) { return r.user_id === cu4.id; });
      var pub = mine2.filter(function (r) { return r.status === 'published'; });
      return {
        published_count: pub.length,
        draft_count: mine2.filter(function (r) { return r.status === 'draft' || r.status === 'rejected'; }).length,
        total_read: pub.reduce(function (s, r) { return s + r.read_count; }, 0),
        total_like: pub.reduce(function (s, r) { return s + r.like_count; }, 0),
        total_favorite: pub.reduce(function (s, r) { return s + (r.fav_count || 0); }, 0)
      };
    }
    if (method === 'GET' && p === '/api/creator/points') {
      var cu5 = authUser(db, headers);
      requireRole(cu5, 'creator');
      return pointsOverview(cu5.creator_points || 0);
    }
    if (method === 'GET' && p === '/api/creator/point-records') {
      var cu6 = authUser(db, headers);
      requireRole(cu6, 'creator');
      var recs = (db.pointRecords || []).filter(function (r) { return r.user_id === cu6.id; });
      return paginate(recs.map(function (r) {
        return { id: r.id, change: r.change, reason: r.reason,
          balance_after: r.balance_after, created_at: r.created_at };
      }), query.page, query.page_size || 10);
    }
    /* 首页专题：L3+ 资深创作者的公开评测 */
    if (method === 'GET' && p === '/api/creator/hall') {
      var hall = db.reviews.filter(function (r) {
        if (r.status !== 'published') return false;
        var u = db.users.filter(function (x) { return x.id === r.user_id; })[0];
        return u && (u.creator_level || 0) >= 3;
      }).sort(function (a, b) {
        var ua = db.users.filter(function (x) { return x.id === a.user_id; })[0];
        var ub = db.users.filter(function (x) { return x.id === b.user_id; })[0];
        return ((ub ? ub.creator_level || 0 : 0) - (ua ? ua.creator_level || 0 : 0))
          || ((b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0))
          || (b.read_count || 0) - (a.read_count || 0);
      });
      return paginate(hall.map(function (r) { return publicReviewCard(r, db); }), query.page, query.page_size || 6);
    }

    /* ===== AI ===== */
    if (method === 'POST' && p === '/api/ai/chat') {
      var chatMsg = (body.message || '').trim();
      if (!chatMsg) fail(400, '消息不能为空');
      if (chatMsg.length > 500) fail(400, '消息过长（500 字以内）');
      return aiChat(db, body);
    }
    if (method === 'POST' && p === '/api/ai/game-recommend') {
      var aiu = authUser(db, headers);
      var recos = aiRecommend(db, aiu, body.preferences);
      return { recommendations: recos };
    }
    if (method === 'POST' && p === '/api/ai/creator-assistant') {
      var aiu2 = authUser(db, headers);
      requireRole(aiu2, 'creator');
      return aiCreator(db, body);
    }

    /* ===== 管理员 ===== */
    if (method === 'GET' && p === '/api/admin/dashboard') {
      var au = authUser(db, headers);
      requireRole(au, 'admin');
      return {
        user_count: db.users.length,
        game_count: db.games.filter(function (g) { return g.is_online; }).length,
        review_count: db.reviews.filter(function (r) { return r.status === 'published'; }).length,
        pending_count: db.reviews.filter(function (r) { return r.status === 'audit' || r.status === 'manual_review'; }).length,
        apply_count: db.applies.filter(function (a) { return a.status === 'pending'; }).length
      };
    }
    if (method === 'GET' && p === '/api/admin/users') {
      var au2 = authUser(db, headers);
      requireRole(au2, 'admin');
      var ul = db.users.slice().sort(function (a, b) { return a.id - b.id; });
      if (query.keyword) {
        var k2 = query.keyword.toLowerCase();
        ul = ul.filter(function (x) { return (x.username + x.email + x.profile.nickname).toLowerCase().indexOf(k2) >= 0; });
      }
      return { items: ul.map(publicUser) };
    }
    if ((m = p.match(/^\/api\/admin\/users\/(\d+)\/status$/)) && method === 'PUT') {
      var au3 = authUser(db, headers);
      requireRole(au3, 'admin');
      var tu = db.users.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!tu) fail(404, '用户不存在');
      if (tu.role === 'admin') fail(400, '不能封禁管理员');
      tu.is_active = !!body.is_active;
      save(db);
      return { message: body.is_active ? '已解封' : '已封禁' };
    }
    if ((m = p.match(/^\/api\/admin\/users\/(\d+)\/role$/)) && method === 'PUT') {
      var au4 = authUser(db, headers);
      requireRole(au4, 'admin');
      var tu2 = db.users.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!tu2) fail(404, '用户不存在');
      if (tu2.role === 'admin') fail(400, '不能修改管理员角色');
      if (['player', 'creator'].indexOf(body.role) < 0) fail(400, '角色非法');
      tu2.role = body.role;
      save(db);
      return { message: '角色已更新为 ' + body.role };
    }
    if (method === 'GET' && p === '/api/admin/creator-apply') {
      var au5 = authUser(db, headers);
      requireRole(au5, 'admin');
      var al = db.applies.filter(function (a) { return !query.status || a.status === query.status; })
        .map(function (a) {
          var u = db.users.filter(function (x) { return x.id === a.user_id; })[0];
          return Object.assign({}, a, { username: u ? u.username : '', nickname: u ? u.profile.nickname : '', email: u ? (u.email || '') : '' });
        }).sort(function (a, b) { return b.created_at.localeCompare(a.created_at); });
      return { items: al };
    }
    if ((m = p.match(/^\/api\/admin\/creator-apply\/(\d+)\/deal$/)) && method === 'PUT') {
      var au6 = authUser(db, headers);
      requireRole(au6, 'admin');
      var ap = db.applies.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!ap) fail(404, '申请不存在');
      if (ap.status !== 'pending') fail(400, '该申请已处理');
      if (body.action === 'approve') {
        ap.status = 'approved'; ap.audit_user_id = au6.id;
        var applicant = db.users.filter(function (x) { return x.id === ap.user_id; })[0];
        if (applicant) applicant.role = 'creator';
        save(db);
        return { message: '已通过申请，用户已升级为创作者' };
      }
      ap.status = 'rejected'; ap.audit_user_id = au6.id;
      save(db);
      return { message: '已驳回申请' };
    }
    if (method === 'GET' && p === '/api/admin/reviews/pending') {
      var au7 = authUser(db, headers);
      requireRole(au7, 'admin');
      var pl = db.reviews.filter(function (r) { return r.status === 'audit' || r.status === 'manual_review'; })
        .map(function (r) { return reviewOut(r, db); });
      return { items: pl };
    }
    if ((m = p.match(/^\/api\/admin\/reviews\/(\d+)\/audit-decision$/)) && method === 'POST') {
      var au8 = authUser(db, headers);
      requireRole(au8, 'admin');
      var rv4 = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv4) fail(404, '评测不存在');
      db.auditLogs.push({ id: ++db.seq.logs, review_id: rv4.id, audit_type: 'manual', risk_score: null,
        reason: (body.action === 'pass' ? '人工复核通过：' : '人工复核驳回：') + (body.reason || '无备注'),
        operator_id: au8.id, created_at: nowIso() });
      if (body.action === 'pass') {
        var wasPublished = rv4.status === 'published';
        rv4.status = 'published'; rv4.audit_status = 'passed';
        recalcGame(db, rv4.game_id);  // 人工复核通过后聚合游戏四维评分
        if (!wasPublished) addPointRecord(db, rv4.user_id, 20, '评测《' + rv4.title + '》人工复核通过发布', rv4.id);
      }
      else { rv4.status = 'rejected'; rv4.audit_status = 'rejected'; rv4.audit_reason = '人工驳回：' + (body.reason || '不符合社区规范'); recalcGame(db, rv4.game_id); }
      save(db);
      return { message: body.action === 'pass' ? '已通过，文章发布' : '已驳回' };
    }
    /* 标记/取消精选评测：作者 +30 / -30 */
    if ((m = p.match(/^\/api\/admin\/reviews\/(\d+)\/feature$/)) && method === 'POST') {
      var au8f = authUser(db, headers);
      requireRole(au8f, 'admin');
      var rv5 = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv5 || rv5.status !== 'published') fail(404, '公开评测不存在');
      var newFeat = !rv5.is_featured;
      rv5.is_featured = newFeat;
      addPointRecord(db, rv5.user_id, newFeat ? 30 : -30,
        '评测《' + rv5.title + '》' + (newFeat ? '被管理员标记精选' : '被取消精选标记'), rv5.id);
      save(db);
      return { is_featured: newFeat,
        message: newFeat ? '已标记精选，作者 +30 积分' : '已取消精选标记，作者扣回 30 积分' };
    }
    /* 抄袭违规下架：评测下架 + 作者积分清零、等级重置 L0 */
    if ((m = p.match(/^\/api\/admin\/reviews\/(\d+)\/plagiarize$/)) && method === 'POST') {
      var au8p = authUser(db, headers);
      requireRole(au8p, 'admin');
      var rv6 = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv6) fail(404, '评测不存在');
      var pAuthor = db.users.filter(function (x) { return x.id === rv6.user_id; })[0];
      var wasPub = rv6.status === 'published';
      rv6.status = 'rejected'; rv6.audit_status = 'rejected';
      rv6.audit_reason = '抄袭违规，管理员强制下架';
      if (wasPub) recalcGame(db, rv6.game_id);
      if (pAuthor && (pAuthor.creator_points || 0) > 0) {
        pAuthor.creator_points = 0; pAuthor.creator_level = 0;
        if (!db.pointRecords) db.pointRecords = [];
        db.pointRecords.unshift({ id: ++db.seq.pointRecords, user_id: pAuthor.id, change: 0,
          reason: '评测《' + rv6.title + '》判定抄袭违规：积分清零、等级重置 L0',
          related_type: 'system', related_id: null, balance_after: 0, created_at: nowIso() });
      }
      save(db);
      return { message: '已按抄袭违规下架，作者积分清零并重置为 L0' };
    }
    if (method === 'GET' && p === '/api/admin/games') {
      var au9g = authUser(db, headers);
      requireRole(au9g, 'admin');
      return { items: db.games.slice().sort(function (a, b) { return a.id - b.id; }).map(function (g) { return gameOut(g, db); }),
        categories: db.categories };
    }
    if (method === 'POST' && p === '/api/admin/games') {
      var au9 = authUser(db, headers);
      requireRole(au9, 'admin');
      if (!body.name) fail(400, '游戏名称必填');
      var ng = { id: ++db.seq.games, name: body.name, name_en: body.name_en || '', developer: body.developer || '',
        cover_url: body.cover_url || IMG('generic video game cover art, fantasy adventure, cinematic'),
        description: body.description || '', release_date: body.release_date || '2025-01-01',
        category_id: parseInt(body.category_id, 10) || 1, tags: body.tags || [], average_score: 0,
        is_online: body.is_online !== false, hot: 50, created_at: nowIso() };
      db.games.push(ng); save(db);
      return gameOut(ng, db);
    }
    if ((m = p.match(/^\/api\/admin\/games\/(\d+)$/)) && method === 'PUT') {
      var au10 = authUser(db, headers);
      requireRole(au10, 'admin');
      var gg = db.games.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!gg) fail(404, '游戏不存在');
      ['name', 'name_en', 'developer', 'cover_url', 'description', 'release_date', 'is_online'].forEach(function (k) {
        if (body[k] !== undefined) gg[k] = body[k];
      });
      if (body.category_id !== undefined) gg.category_id = parseInt(body.category_id, 10);
      if (body.tags !== undefined) gg.tags = body.tags;
      save(db);
      return gameOut(gg, db);
    }
    if (method === 'GET' && p === '/api/admin/categories') {
      var au11 = authUser(db, headers);
      requireRole(au11, 'admin');
      return { items: db.categories };
    }
    if (method === 'POST' && p === '/api/admin/categories') {
      var au12 = authUser(db, headers);
      requireRole(au12, 'admin');
      if (!body.name) fail(400, '分类名必填');
      var nc2 = { id: ++db.seq.categories, name: body.name };
      db.categories.push(nc2); save(db);
      return nc2;
    }
    if ((m = p.match(/^\/api\/admin\/categories\/(\d+)$/)) && method === 'PUT') {
      var au13 = authUser(db, headers);
      requireRole(au13, 'admin');
      var cat = db.categories.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!cat) fail(404, '分类不存在');
      cat.name = body.name || cat.name; save(db);
      return cat;
    }
    if ((m = p.match(/^\/api\/admin\/categories\/(\d+)$/)) && method === 'DELETE') {
      var au14 = authUser(db, headers);
      requireRole(au14, 'admin');
      var cid = parseInt(m[1], 10);
      if (db.games.some(function (g) { return g.category_id === cid; })) fail(400, '该分类下仍有游戏，无法删除');
      db.categories = db.categories.filter(function (x) { return x.id !== cid; });
      save(db);
      return { message: '分类已删除' };
    }
    if (method === 'GET' && p === '/api/admin/audit/logs') {
      var au15 = authUser(db, headers);
      requireRole(au15, 'admin');
      var logs = db.auditLogs.slice().sort(function (a, b) { return b.created_at.localeCompare(a.created_at); })
        .map(function (l) {
          var rv5 = db.reviews.filter(function (x) { return x.id === l.review_id; })[0];
          return Object.assign({}, l, { review_title: rv5 ? rv5.title : '#' + l.review_id });
        });
      return { items: logs };
    }
    if (method === 'GET' && p === '/api/admin/comments') {
      var au16 = authUser(db, headers);
      requireRole(au16, 'admin');
      var cml = db.comments.slice().sort(function (a, b) { return b.created_at.localeCompare(a.created_at); }).map(function (c) {
        var u = db.users.filter(function (x) { return x.id === c.user_id; })[0];
        var rv6 = db.reviews.filter(function (x) { return x.id === c.target_id; })[0];
        var gm6 = db.games.filter(function (x) { return x.id === c.target_id; })[0];
        var targetTitle = c.target_type === 'review'
          ? (rv6 ? rv6.title : '#' + c.target_id)
          : (gm6 ? gm6.name : '#' + c.target_id);
        return {
          id: c.id, content: c.content, author: u ? u.username : '', author_id: c.user_id,
          target_type: c.target_type, target_id: c.target_id, target_title: targetTitle,
          review_title: c.target_type === 'review' ? (rv6 ? rv6.title : '') : '',
          like_count: c.like_count || 0, created_at: c.created_at
        };
      });
      return { items: cml };
    }
    if ((m = p.match(/^\/api\/admin\/comments\/(\d+)$/)) && method === 'DELETE') {
      var au17 = authUser(db, headers);
      requireRole(au17, 'admin');
      var dc = db.comments.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!dc) fail(404, '评论不存在');
      db.comments = db.comments.filter(function (x) { return x.id !== parseInt(m[1], 10); });
      save(db);  // 自动精选为运行时计算，删除后自动重算，无需人工干预
      return { message: '评论已删除' };
    }

    /* ===== 社区模块 ===== */
    function cAuthor(db, uid) {
      var u = db.users.filter(function (x) { return x.id === uid; })[0];
      return u ? (u.profile.nickname || u.username) : '未知用户';
    }
    function cPostOut(db, p, viewer, full) {
      var u = db.users.filter(function (x) { return x.id === p.user_id; })[0];
      var text = (p.content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      var liked = viewer ? db.postLikes.some(function (l) { return l.post_id === p.id && l.user_id === viewer.id; }) : false;
      var fav = viewer ? db.postFavs.some(function (l) { return l.post_id === p.id && l.user_id === viewer.id; }) : false;
      return {
        id: p.id, title: p.title, tag: p.tag, images: p.images || [],
        summary: text.length > 90 ? text.slice(0, 90) + '…' : text,
        content: full ? p.content : undefined,
        author: { id: p.user_id, nickname: cAuthor(db, p.user_id), avatar: u ? u.profile.avatar : '' },
        created_at: p.created_at,
        view_count: p.view_count, like_count: p.like_count, fav_count: p.fav_count,
        comment_count: p.comment_count, my_liked: liked, my_favorited: fav,
        can_delete: viewer && (viewer.id === p.user_id || viewer.role === 'admin'),
        reported: db.reports.some(function (r) { return r.target_type === 'post' && r.target_id === p.id && r.status === 'pending'; })
      };
    }
    function cCommentOut(db, c, viewer, post) {
      var u = db.users.filter(function (x) { return x.id === c.user_id; })[0];
      var liked = viewer ? db.postCommentLikes.some(function (l) { return l.comment_id === c.id && l.user_id === viewer.id; }) : false;
      var canDelete = viewer && (viewer.id === c.user_id || (post && viewer.id === post.user_id) || viewer.role === 'admin');
      return {
        id: c.id, post_id: c.post_id, parent_id: c.parent_id, content: c.content,
        like_count: c.like_count || 0, created_at: c.created_at, my_liked: liked,
        can_delete: canDelete,
        author: { id: c.user_id, nickname: cAuthor(db, c.user_id), avatar: u ? u.profile.avatar : '' },
        replies: []
      };
    }

    if (method === 'GET' && p === '/api/community/tags') {
      return { tags: ['游戏', '闲聊', '攻略', '吐槽'] };
    }
    if (method === 'GET' && p === '/api/community/posts') {
      var v0 = null; try { v0 = authOpt(db, headers); } catch (e) { v0 = null; }
      var plist = db.communityPosts.slice();
      if (query.tag) plist = plist.filter(function (x) { return x.tag === query.tag; });
      if (query.keyword) {
        var kw = query.keyword.toLowerCase();
        plist = plist.filter(function (x) { return (x.title + x.content).toLowerCase().indexOf(kw) >= 0; });
      }
      plist.sort(function (a, b) {
        if (query.sort === 'latest') return new Date(b.created_at) - new Date(a.created_at);
        return b.hot_score - a.hot_score;
      });
      var pg = paginate(plist, query.page, query.page_size || 9);
      pg.items = pg.items.map(function (x) { return cPostOut(db, x, v0, false); });
      return pg;
    }
    if (method === 'POST' && p === '/api/community/posts') {
      var me0 = authUser(db, headers);
      if (!body.title || body.title.trim().length < 2) fail(400, '标题至少 2 个字');
      if (!(body.content && body.content.trim()) && !(body.images && body.images.length)) fail(400, '正文和图片至少填一项');
      var bad = ['傻逼', '操你', '赌博', '色情', '加微信'];
      var hit = bad.filter(function (w) { return (body.title + body.content).indexOf(w) >= 0; });
      if (hit.length) fail(400, '内容命中风控敏感词，请修改后发布');
      var np = { id: ++db.seq.communityPosts, user_id: me0.id, title: body.title.trim(),
        content: (body.content || '').trim(), tag: body.tag || '闲聊', images: body.images || [],
        view_count: 0, like_count: 0, fav_count: 0, comment_count: 0, hot_score: 0,
        created_at: nowIso(), updated_at: nowIso() };
      db.communityPosts.push(np); save(db);
      return { post: cPostOut(db, np, me0, true) };
    }
    if ((m = p.match(/^\/api\/community\/posts\/(\d+)$/)) && method === 'GET') {
      var v1 = null; try { v1 = authOpt(db, headers); } catch (e) { v1 = null; }
      var gp = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!gp) fail(404, '帖子不存在或已被删除');
      gp.view_count++; save(db);
      return { post: cPostOut(db, gp, v1, true) };
    }
    if ((m = p.match(/^\/api\/community\/posts\/(\d+)$/)) && method === 'DELETE') {
      var me1 = authUser(db, headers);
      var dp = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!dp) fail(404, '帖子不存在');
      if (me1.id !== dp.user_id && me1.role !== 'admin') fail(403, '只能删除自己的帖子');
      var pid = dp.id;
      db.communityPosts = db.communityPosts.filter(function (x) { return x.id !== pid; });
      db.postComments = db.postComments.filter(function (x) { return x.post_id !== pid; });
      db.postLikes = db.postLikes.filter(function (x) { return x.post_id !== pid; });
      db.postFavs = db.postFavs.filter(function (x) { return x.post_id !== pid; });
      save(db);
      return { message: '帖子已删除' };
    }
    if ((m = p.match(/^\/api\/community\/posts\/(\d+)\/like$/)) && method === 'POST') {
      var me2 = authUser(db, headers);
      var lp = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!lp) fail(404, '帖子不存在');
      var ex = db.postLikes.filter(function (x) { return x.post_id === lp.id && x.user_id === me2.id; })[0];
      if (ex) { db.postLikes = db.postLikes.filter(function (x) { return x !== ex; }); lp.like_count--; }
      else { db.postLikes.push({ id: ++db.seq.postLikes, post_id: lp.id, user_id: me2.id }); lp.like_count++; }
      save(db);
      return { liked: !ex, like_count: lp.like_count };
    }
    if ((m = p.match(/^\/api\/community\/posts\/(\d+)\/favorite$/)) && method === 'POST') {
      var me3 = authUser(db, headers);
      var fp = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!fp) fail(404, '帖子不存在');
      var exf = db.postFavs.filter(function (x) { return x.post_id === fp.id && x.user_id === me3.id; })[0];
      if (exf) { db.postFavs = db.postFavs.filter(function (x) { return x !== exf; }); fp.fav_count--; }
      else { db.postFavs.push({ id: ++db.seq.postFavs, post_id: fp.id, user_id: me3.id }); fp.fav_count++; }
      save(db);
      return { favorited: !exf, fav_count: fp.fav_count };
    }
    if ((m = p.match(/^\/api\/community\/posts\/(\d+)\/comments$/)) && method === 'GET') {
      var v2 = null; try { v2 = authOpt(db, headers); } catch (e) { v2 = null; }
      var cp2 = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!cp2) fail(404, '帖子不存在');
      var cms = db.postComments.filter(function (x) { return x.post_id === cp2.id; });
      var tops = cms.filter(function (x) { return !x.parent_id; })
        .map(function (c) {
          var node = cCommentOut(db, c, v2, cp2);
          node.replies = cms.filter(function (x) { return x.parent_id === c.id; })
            .map(function (r) { return cCommentOut(db, r, v2, cp2); });
          return node;
        });
      return { items: tops };
    }
    if ((m = p.match(/^\/api\/community\/posts\/(\d+)\/comments$/)) && method === 'POST') {
      var me4 = authUser(db, headers);
      var cp3 = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!cp3) fail(404, '帖子不存在');
      if (!body.content || !body.content.trim()) fail(400, '评论内容不能为空');
      var parentId = null;
      if (body.parent_id) {
        var pc = db.postComments.filter(function (x) { return x.id === body.parent_id; })[0];
        if (pc) parentId = pc.parent_id || pc.id;
      }
      var nc = { id: ++db.seq.postComments, post_id: cp3.id, user_id: me4.id,
        parent_id: parentId, content: body.content.trim(), like_count: 0, created_at: nowIso() };
      db.postComments.push(nc); cp3.comment_count++; save(db);
      return { comment: cCommentOut(db, nc, me4, cp3) };
    }
    if ((m = p.match(/^\/api\/community\/comments\/(\d+)$/)) && method === 'DELETE') {
      var me5 = authUser(db, headers);
      var dc2 = db.postComments.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!dc2) fail(404, '评论不存在');
      var dpost = db.communityPosts.filter(function (x) { return x.id === dc2.post_id; })[0];
      if (me5.id !== dc2.user_id && (!dpost || me5.id !== dpost.user_id) && me5.role !== 'admin') {
        fail(403, '无权删除该评论');
      }
      var cid = dc2.id;
      db.postComments = db.postComments.filter(function (x) { return x.id !== cid && x.parent_id !== cid; });
      if (dpost) dpost.comment_count = db.postComments.filter(function (x) { return x.post_id === dpost.id; }).length;
      save(db);
      return { message: '评论已删除' };
    }
    if ((m = p.match(/^\/api\/community\/comments\/(\d+)\/like$/)) && method === 'POST') {
      var me6 = authUser(db, headers);
      var lc = db.postComments.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!lc) fail(404, '评论不存在');
      var exl = db.postCommentLikes.filter(function (x) { return x.comment_id === lc.id && x.user_id === me6.id; })[0];
      if (exl) { db.postCommentLikes = db.postCommentLikes.filter(function (x) { return x !== exl; }); lc.like_count--; }
      else { db.postCommentLikes.push({ id: ++db.seq.postCommentLikes, comment_id: lc.id, user_id: me6.id }); lc.like_count++; }
      save(db);
      return { liked: !exl, like_count: lc.like_count };
    }
    if (method === 'POST' && p === '/api/community/reports') {
      var me7 = authUser(db, headers);
      db.reports.push({ id: ++db.seq.reports, reporter_id: me7.id,
        target_type: body.target_type, target_id: body.target_id,
        reason: body.reason || '其他', detail: body.detail || '',
        status: 'pending', handler_id: null, handle_note: null,
        created_at: nowIso(), handled_at: null });
      save(db);
      return { message: '举报已提交，感谢反馈' };
    }
    if ((m = p.match(/^\/api\/community\/users\/(\d+)\/posts$/)) && method === 'GET') {
      var v3 = null; try { v3 = authOpt(db, headers); } catch (e) { v3 = null; }
      var targetUid = parseInt(m[1], 10);
      var tab = query.tab || 'posts';
      if (tab !== 'posts' && (!v3 || v3.id !== targetUid)) fail(403, '只能查看自己的收藏/点赞记录');
      var ulist;
      if (tab === 'favorites') {
        ulist = db.postFavs.filter(function (x) { return x.user_id === targetUid; })
          .map(function (x) { return db.communityPosts.filter(function (p) { return p.id === x.post_id; })[0]; }).filter(Boolean);
      } else if (tab === 'likes') {
        ulist = db.postLikes.filter(function (x) { return x.user_id === targetUid; })
          .map(function (x) { return db.communityPosts.filter(function (p) { return p.id === x.post_id; })[0]; }).filter(Boolean);
      } else {
        ulist = db.communityPosts.filter(function (x) { return x.user_id === targetUid; });
      }
      ulist.sort(function (a, b) { return new Date(b.created_at) - new Date(a.created_at); });
      var upg = paginate(ulist, query.page, query.page_size || 9);
      upg.items = upg.items.map(function (x) { return cPostOut(db, x, v3, false); });
      return upg;
    }
    if (method === 'POST' && p === '/api/community/upload') {
      var me8 = authUser(db, headers);
      // Mock 环境无真实文件，返回一张占位社区图
      return { url: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=game%20screenshot%20wallpaper&image_size=landscape_16_9' };
    }

    /* ===== 后台：社区治理 ===== */
    if (method === 'GET' && p === '/api/admin/community/posts') {
      var adm = authUser(db, headers); requireRole(adm, 'admin');
      var aplist = db.communityPosts.slice().sort(function (a, b) { return new Date(b.created_at) - new Date(a.created_at); });
      if (query.keyword) {
        var akw = query.keyword.toLowerCase();
        aplist = aplist.filter(function (x) { return (x.title + x.content).toLowerCase().indexOf(akw) >= 0; });
      }
      return { items: aplist.map(function (x) {
        var o = cPostOut(db, x, adm, false);
        o.author = cAuthor(db, x.user_id);
        return o;
      }) };
    }
    if ((m = p.match(/^\/api\/admin\/community\/posts\/(\d+)$/)) && method === 'DELETE') {
      var adm2 = authUser(db, headers); requireRole(adm2, 'admin');
      var adp = db.communityPosts.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!adp) fail(404, '帖子不存在');
      var apid = adp.id;
      db.communityPosts = db.communityPosts.filter(function (x) { return x.id !== apid; });
      db.postComments = db.postComments.filter(function (x) { return x.post_id !== apid; });
      save(db);
      return { message: '帖子已删除' };
    }
    if (method === 'GET' && p === '/api/admin/reports') {
      var adm3 = authUser(db, headers); requireRole(adm3, 'admin');
      var rlist = db.reports.slice().sort(function (a, b) { return new Date(b.created_at) - new Date(a.created_at); });
      if (query.status && query.status !== 'all') rlist = rlist.filter(function (x) { return x.status === query.status; });
      return { items: rlist.map(function (r) {
        var tgt = null;
        if (r.target_type === 'post') tgt = db.communityPosts.filter(function (x) { return x.id === r.target_id; })[0];
        else tgt = db.postComments.filter(function (x) { return x.id === r.target_id; })[0];
        return {
          id: r.id, target_type: r.target_type, target_id: r.target_id,
          target_exists: !!tgt, target_title: tgt ? (tgt.title || (tgt.content || '').slice(0, 60)) : '',
          reason: r.reason, detail: r.detail, status: r.status,
          reporter: cAuthor(db, r.reporter_id), reporter_id: r.reporter_id,
          handler_id: r.handler_id, handle_note: r.handle_note,
          created_at: r.created_at, handled_at: r.handled_at
        };
      }) };
    }
    if ((m = p.match(/^\/api\/admin\/reports\/(\d+)\/handle$/)) && method === 'POST') {
      var adm4 = authUser(db, headers); requireRole(adm4, 'admin');
      var rep = db.reports.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rep) fail(404, '举报不存在');
      if (body.action === 'dismiss') {
        rep.status = 'dismissed';
      } else {
        // 删除前先找到被举报内容与作者（ban 时需要封禁作者）
        var tgt2 = null, authorId = null;
        if (rep.target_type === 'post') {
          tgt2 = db.communityPosts.filter(function (x) { return x.id === rep.target_id; })[0];
        } else {
          tgt2 = db.postComments.filter(function (x) { return x.id === rep.target_id; })[0];
        }
        if (tgt2) authorId = tgt2.user_id;
        if (rep.target_type === 'post') {
          db.communityPosts = db.communityPosts.filter(function (x) { return x.id !== rep.target_id; });
          db.postComments = db.postComments.filter(function (x) { return x.post_id !== rep.target_id; });
        } else {
          db.postComments = db.postComments.filter(function (x) { return x.id !== rep.target_id; });
        }
        rep.status = 'handled';
        if (body.action === 'ban' && authorId) {
          var author = db.users.filter(function (x) { return x.id === authorId; })[0];
          if (author && author.role !== 'admin') author.is_active = false;
        }
      }
      rep.handler_id = adm4.id; rep.handle_note = body.note || ''; rep.handled_at = nowIso();
      save(db);
      return { message: '举报已处理' };
    }

    fail(404, '接口不存在（Mock）：' + method + ' ' + p);
  }

  window.MockApi = { handle: handle, reset: reset, seed: seed };
})();
