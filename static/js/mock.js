/* ============================================================
   mock.js — 前端 Mock 数据层（阶段3 产物）
   - 后端未启动时，api.js 自动把所有 /api 请求路由到本文件
   - 数据持久化到 localStorage（gc_mock_db_v1），刷新不丢失
   - 游戏数据均为真实存在的 Steam 游戏
   ============================================================ */

(function () {
  'use strict';

  var DB_KEY = 'gc_mock_db_v1';

  /* ---------- 封面图：按各游戏风格生成的美术图 ---------- */
  function IMG(prompt) {
    return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=' +
      encodeURIComponent(prompt) + '&image_size=landscape_16_9';
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
      { id: 1, name: '艾尔登法环', name_en: 'Elden Ring', developer: 'FromSoftware',
        cover_url: IMG('dark fantasy epic video game cover art, armored knight facing a colossal glowing golden tree, crumbling castle on horizon, dramatic cinematic lighting, painterly concept art'),
        description: '由 FromSoftware 与乔治·R·R·马丁联手打造的开放世界魂系动作 RPG。玩家作为褪色者踏入广袤的交界地，探索 six 大区域、挑战强敌、收集卢恩，最终成为艾尔登之王。',
        release_date: '2022-02-25', category_id: 4, tags: ['魂系', '黑暗幻想', '开放世界', '动作RPG'],
        average_score: 9.6, is_online: true, hot: 98, created_at: d(400) },
      { id: 2, name: '博德之门 3', name_en: "Baldur's Gate 3", developer: 'Larian Studios',
        cover_url: IMG('high fantasy RPG video game cover art, party of adventurers facing a tentacled mind flayer monster, glowing magic spells, dramatic painted illustration, dungeons and dragons style'),
        description: '拉瑞安工作室出品的 CRPG 巅峰之作，基于龙与地下城 D&D 5e 规则。你的大脑被植入了夺心魔蝌蚪，一场改变费伦大陆命运的冒险由此展开，选择将真正改变世界。',
        release_date: '2023-08-03', category_id: 1, tags: ['回合制', '剧情丰富', '奇幻', '合作'],
        average_score: 9.7, is_online: true, hot: 95, created_at: d(380) },
      { id: 3, name: '黑神话：悟空', name_en: 'Black Myth: Wukong', developer: '游戏科学 Game Science',
        cover_url: IMG('chinese mythology action game cover art, monkey king warrior with golden staff standing on mountain cliff, swirling clouds and epic dark fantasy landscape, cinematic painting'),
        description: '游戏科学开发的国产 3A 动作角色扮演游戏。扮演天命人，踏上充满凶险与惊奇的西游路，与各路妖王殊死一战。每一步都踏足四大部州的神话山河。',
        release_date: '2024-08-20', category_id: 3, tags: ['神话', '动作RPG', '单机', '国风'],
        average_score: 9.3, is_online: true, hot: 99, created_at: d(300) },
      { id: 4, name: '赛博朋克 2077', name_en: 'Cyberpunk 2077', developer: 'CD Projekt Red',
        cover_url: IMG('cyberpunk sci-fi video game cover art, neon lit futuristic city street at night with rain reflections, mercenary with glowing cybernetic arm, yellow and magenta neon, cinematic'),
        description: 'CD Projekt Red 出品的开放世界动作 RPG。在夜之城这座权力、魅力和义体改造交织的都市里，扮演雇佣兵 V，追寻一种永生不朽的独特植入体。历经多次更新后口碑全面逆袭。',
        release_date: '2020-12-10', category_id: 4, tags: ['赛博朋克', '科幻', '开放世界', '剧情丰富'],
        average_score: 8.5, is_online: true, hot: 90, created_at: d(500) },
      { id: 5, name: '荒野大镖客：救赎 2', name_en: 'Red Dead Redemption 2', developer: 'Rockstar Games',
        cover_url: IMG('western open world game cover art, cowboys on horseback at sunset crossing vast prairie, dramatic orange sky and mountains, realistic cinematic style'),
        description: 'R 星打造的西部题材开放世界史诗。1899 年的美国，亡命之徒亚瑟·摩根随范德林德帮在时代的终结中挣扎求生。一个关于忠诚、理想与消逝的西部故事。',
        release_date: '2018-10-26', category_id: 4, tags: ['西部', '剧情丰富', '开放世界', '写实'],
        average_score: 9.5, is_online: true, hot: 87, created_at: d(600) },
      { id: 6, name: '巫师 3：狂猎', name_en: 'The Witcher 3: Wild Hunt', developer: 'CD Projekt Red',
        cover_url: IMG('dark fantasy RPG cover art, white haired monster hunter with silver sword standing on cliff overlooking medieval village, a griffin flying in stormy sky, moody painted illustration'),
        description: '利维亚的杰洛特，一名职业猎魔人，在战火纷飞的大陆上寻找预言之子希里。CDPR 凭借本作一举封神，次世代更新后画面焕然新生。',
        release_date: '2015-05-19', category_id: 1, tags: ['奇幻', '开放世界', '剧情丰富', '选择取向'],
        average_score: 9.4, is_online: true, hot: 88, created_at: d(700) },
      { id: 7, name: '反恐精英 2', name_en: 'Counter-Strike 2', developer: 'Valve',
        cover_url: IMG('tactical FPS shooter game cover art, special forces soldiers with rifles on a dusty middle eastern map, smoke grenades, competitive esports style, cinematic lighting'),
        description: 'Valve 基于起源 2 引擎打造的 CS 系列续作，免费开玩。升级的烟雾弹物理、亚秒级服务器与全新画质，让全球最流行的竞技射击焕然升级。',
        release_date: '2023-09-27', category_id: 2, tags: ['竞技', '多人', 'FPS', '电竞'],
        average_score: 8.0, is_online: true, hot: 96, created_at: d(360) },
      { id: 8, name: '哈迪斯', name_en: 'Hades', developer: 'Supergiant Games',
        cover_url: IMG('greek mythology roguelike game cover art, underworld prince wielding glowing red blade, fiery underworld temple, stylized hand painted art, vibrant colors'),
        description: 'Supergiant 出品的高口碑 Roguelike。扮演冥界王子扎格列欧斯，在每次死亡都重来的逃亡中杀出冥界。流畅的战斗、丰富的 Build 与全程配音的希腊诸神，让人死了一千次还想再来一把。',
        release_date: '2020-09-17', category_id: 3, tags: ['Roguelike', '希腊神话', '独立', '动作'],
        average_score: 9.2, is_online: true, hot: 80, created_at: d(450) },
      { id: 9, name: '星露谷物语', name_en: 'Stardew Valley', developer: 'ConcernedApe',
        cover_url: IMG('cozy pixel art farming simulation game cover art, green farm with crops chickens and farmhouse, cheerful countryside, retro pixel art style, warm colors'),
        description: '一个人历时四年半开发的田园模拟神作。继承爷爷的农场，种地、养殖、钓鱼、挖矿、与村民恋爱结婚。支持多人联机，是无数玩家的电子止痛药。',
        release_date: '2016-02-27', category_id: 5, tags: ['像素', '农场', '休闲', '联机'],
        average_score: 9.5, is_online: true, hot: 85, created_at: d(800) },
      { id: 10, name: '文明 6', name_en: 'Sid Meier’s Civilization VI', developer: 'Firaxis Games',
        cover_url: IMG('turn based strategy game cover art, stylized world map with great historical leaders and ancient monuments across ages, globe and wonders, illustrated historical art style'),
        description: '席德·梅尔的传奇 4X 策略系列。从石器时代到信息时代，建立帝国、发展科技、外交博弈或征服世界。再来一回合就睡觉——然后天就亮了。',
        release_date: '2016-10-21', category_id: 6, tags: ['回合制', '历史', '4X', '建设'],
        average_score: 8.3, is_online: true, hot: 75, created_at: d(750) },
      { id: 11, name: '极限竞速：地平线 5', name_en: 'Forza Horizon 5', developer: 'Playground Games',
        cover_url: IMG('open world racing game cover art, orange sports car drifting through mexican desert with jungle and dust trail, bright sunny sky, dynamic cinematic action'),
        description: '地平线系列登陆墨西哥。数百辆授权座驾、世界顶级的驾驶手感、随季节变换的开放世界，无论是竞速老炮还是观光休闲玩家都能找到乐趣。',
        release_date: '2021-11-09', category_id: 7, tags: ['赛车', '开放世界', '多人', '写实'],
        average_score: 9.0, is_online: true, hot: 78, created_at: d(420) },
      { id: 12, name: '空洞骑士', name_en: 'Hollow Knight', developer: 'Team Cherry',
        cover_url: IMG('hand drawn metroidvania game cover art, small masked knight with nail sword in dark underground insect kingdom, blue and white tones, atmospheric hand drawn art'),
        description: '澳大利亚三人团队打造的银河恶魔城神作。深入衰败的圣巢，探索 interconnected 的地下王国，挑战硬核 Boss 战。手绘美术、凄美配乐与庞大的世界等待着你。',
        release_date: '2017-02-25', category_id: 3, tags: ['银河恶魔城', '独立', '手绘', '困难'],
        average_score: 9.4, is_online: true, hot: 82, created_at: d(650) }
    ];

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

    var comments = [
      { id: 1, user_id: 3, target_type: 'review', target_id: 1, parent_id: null, content: '碎星那一战我打了整整一下午，过的时候手都在抖！', like_count: 45, created_at: d(119), likes: [] },
      { id: 2, user_id: 4, target_type: 'review', target_id: 1, parent_id: 1, content: '同感！拉塔恩的 BGM 一响直接头皮发麻', like_count: 12, created_at: d(118), likes: [] },
      { id: 3, user_id: 7, target_type: 'review', target_id: 1, parent_id: null, content: '请问新手适合玩法师还是近战呀？', like_count: 3, created_at: d(110), likes: [] },
      { id: 4, user_id: 2, target_type: 'review', target_id: 1, parent_id: 3, content: '新手强烈推荐观星者，远程法术容错率高~', like_count: 20, created_at: d(109), likes: [] },
      { id: 5, user_id: 3, target_type: 'review', target_id: 3, content: '黑神话首发日我请假在家玩了一整天，值了！', like_count: 88, created_at: d(59), likes: [] },
      { id: 6, user_id: 4, target_type: 'review', target_id: 2, content: '影心是我老婆，不接受反驳。', like_count: 34, created_at: d(88), likes: [] }
    ];

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

    return {
      seq: { users: 100, games: 100, reviews: 100, comments: 100, favorites: 100, records: 100, applies: 100, logs: 100, categories: 100 },
      users: users, categories: categories, games: games, reviews: reviews,
      comments: comments, favorites: favorites, records: records, applies: applies, auditLogs: auditLogs
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
      created_at: u.created_at, profile: u.profile };
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
      game_name: g ? g.name : '',
      game_cover: g ? g.cover_url : ''
    });
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
    return { reply: '收到！关于《' + gn + '》，我可以帮你：\n· 生成评测大纲\n· 梳理通关思路\n· 润色已有文案\n· 分析游戏优缺点\n\n点击上方快捷按钮，或直接描述你的需求即可。' };
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
    if (method === 'POST' && p === '/api/users/apply-creator') {
      var me3 = authUser(db, headers);
      requireRole(me3, 'player');
      if (me3.role === 'creator' || me3.role === 'admin') fail(400, '你已经是创作者了');
      var pending = db.applies.some(function (a) { return a.user_id === me3.id && a.status === 'pending'; });
      if (pending) fail(400, '已有待审核的申请，请耐心等待');
      db.applies.push({ id: ++db.seq.applies, user_id: me3.id, apply_reason: body.apply_reason || '', status: 'pending', audit_user_id: null, created_at: nowIso() });
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
      return out;
    }
    if ((m = p.match(/^\/api\/games\/(\d+)\/reviews$/)) && method === 'GET') {
      var gid = parseInt(m[1], 10);
      var rl = db.reviews.filter(function (r) { return r.game_id === gid && r.status === 'published'; })
        .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); });
      return paginate(rl.map(function (r) { return reviewOut(r, db); }), query.page, 5);
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
      var nc = { id: ++db.seq.comments, user_id: cu2.id, target_type: body.target_type || 'review',
        target_id: body.target_id, parent_id: body.parent_id || null, content: body.content.trim(),
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
      var nr = { id: ++db.seq.reviews, game_id: body.game_id, user_id: cru.id, title: body.title,
        content: body.content || '', tags: body.tags || [], status: 'draft', audit_status: null,
        audit_score: null, audit_reason: '', read_count: 0, like_count: 0, fav_count: 0, created_at: nowIso() };
      db.reviews.push(nr); save(db);
      return reviewOut(nr, db);
    }
    if ((m = p.match(/^\/api\/reviews\/(\d+)$/)) && method === 'PUT') {
      var cru2 = authUser(db, headers);
      var rv = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv) fail(404, '评测不存在');
      if (rv.user_id !== cru2.id) fail(403, '只能编辑自己的文章');
      if (rv.status === 'published') fail(400, '已发布文章不可编辑');
      rv.title = body.title !== undefined ? body.title : rv.title;
      rv.content = body.content !== undefined ? body.content : rv.content;
      rv.game_id = body.game_id !== undefined ? body.game_id : rv.game_id;
      rv.tags = body.tags !== undefined ? body.tags : rv.tags;
      save(db);
      return reviewOut(rv, db);
    }
    if ((m = p.match(/^\/api\/reviews\/(\d+)$/)) && method === 'DELETE') {
      var cru3 = authUser(db, headers);
      var rv2 = db.reviews.filter(function (x) { return x.id === parseInt(m[1], 10); })[0];
      if (!rv2) fail(404, '评测不存在');
      if (rv2.user_id !== cru3.id && cru3.role !== 'admin') fail(403, '无权删除');
      db.reviews = db.reviews.filter(function (x) { return x.id !== rv2.id; });
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
      /* AI 自动审核 */
      var audit = aiAudit(rv3.title, rv3.content);
      var log = { id: ++db.seq.logs, review_id: rv3.id, audit_type: 'ai', risk_score: audit.risk_score,
        reason: audit.reasons.join('；'), operator_id: 1, created_at: nowIso() };
      db.auditLogs.push(log);
      rv3.audit_score = audit.risk_score;
      if (audit.status === 'passed') {
        rv3.status = 'published'; rv3.audit_status = 'passed'; rv3.audit_reason = audit.reasons.join('；');
        save(db);
        return { message: 'AI 审核通过，文章已发布！', status: 'published', audit: audit };
      }
      if (audit.status === 'rejected') {
        rv3.status = 'rejected'; rv3.audit_status = 'rejected'; rv3.audit_reason = audit.reasons.join('；');
        save(db);
        return { message: 'AI 审核未通过，文章被驳回', status: 'rejected', audit: audit };
      }
      rv3.status = 'manual_review'; rv3.audit_status = 'manual_review'; rv3.audit_reason = audit.reasons.join('；');
      save(db);
      return { message: 'AI 判定存疑，已转入管理员人工复核队列', status: 'manual_review', audit: audit };
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

    /* ===== AI ===== */
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
          return Object.assign({}, a, { username: u ? u.username : '', nickname: u ? u.profile.nickname : '' });
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
      if (body.action === 'pass') { rv4.status = 'published'; rv4.audit_status = 'passed'; }
      else { rv4.status = 'rejected'; rv4.audit_status = 'rejected'; rv4.audit_reason = '人工驳回：' + (body.reason || '不符合社区规范'); }
      save(db);
      return { message: body.action === 'pass' ? '已通过，文章发布' : '已驳回' };
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
        return { id: c.id, content: c.content, author: u ? u.username : '', review_title: rv6 ? rv6.title : '', created_at: c.created_at };
      });
      return { items: cml };
    }
    if ((m = p.match(/^\/api\/admin\/comments\/(\d+)$/)) && method === 'DELETE') {
      var au17 = authUser(db, headers);
      requireRole(au17, 'admin');
      db.comments = db.comments.filter(function (x) { return x.id !== parseInt(m[1], 10); });
      save(db);
      return { message: '评论已删除' };
    }

    fail(404, '接口不存在（Mock）：' + method + ' ' + p);
  }

  window.MockApi = { handle: handle, reset: reset, seed: seed };
})();
