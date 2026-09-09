/* ============================================================
   auth.js — 会话 / 导航 / 权限守卫（阶段3 产物）
   ============================================================ */

(function () {
  'use strict';

  var ROLE_NAME = { player: '玩家', creator: '创作者', admin: '管理员' };
  var ROLE_BADGE = { player: 'badge-blue', creator: 'badge-green', admin: 'badge-red' };
  var AVATAR_COLORS = ['#7c5cff', '#4f8cff', '#34d399', '#fbbf24', '#f87171', '#ec4899'];

  /* 创作者等级（与后端 app/core/points.py LEVELS 保持一致） */
  var LEVELS = [
    { lv: 0, code: 'L0', name: '见习创作者', cls: 'lv0', icon: '🏷️' },
    { lv: 1, code: 'L1', name: '普通创作者', cls: 'lv1', icon: '🥉' },
    { lv: 2, code: 'L2', name: '优质创作者', cls: 'lv2', icon: '💜' },
    { lv: 3, code: 'L3', name: '资深创作者', cls: 'lv3', icon: '👑' },
    { lv: 4, code: 'L4', name: '核心创作者', cls: 'lv4', icon: '🌈' }
  ];

  function levelInfo(level) {
    var n = Math.max(0, Math.min(4, parseInt(level, 10) || 0));
    return LEVELS[n];
  }

  /* 等级徽章 HTML。opts.short=true 时只显示 L0-L4（卡片等紧凑场景） */
  function levelBadge(level, opts) {
    var info = levelInfo(level);
    opts = opts || {};
    var text = opts.short ? info.code : info.code + ' ' + info.name;
    var title = '创作者等级 ' + info.code + ' ' + info.name;
    return '<span class="level-badge ' + info.cls + '" title="' + title + '">'
      + (opts.icon === false ? '' : info.icon + ' ') + U.esc(text) + '</span>';
  }

  function user() { return Api.getUser(); }

  /* 重新拉取当前用户最新身份（角色/积分/等级）并写回本地会话。
     场景：管理员审批通过创作者申请后，用户无需重新登录即可获得创作者身份。 */
  function refreshUser() {
    return Api.get('/users/me').then(function (u) {
      Api.setSession(Api.getToken(), u);
      return u;
    });
  }

  function avatarColor(name) {
    var hash = 0;
    for (var i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
  }

  function avatarHtml(u, size) {
    if (u && u.profile && u.profile.avatar) {
      return '<img class="avatar" style="width:' + (size || 32) + 'px;height:' + (size || 32) + 'px" src="' + U.esc(u.profile.avatar) + '">';
    }
    var name = (u && (u.profile && u.profile.nickname || u.username) || '?').slice(0, 1);
    return '<span class="avatar" style="background:' + avatarColor(name) + '">' + U.esc(name) + '</span>';
  }

  /* 根据当前页面深度计算链接前缀（admin 子目录用 ../） */
  function base() { return /\/admin\//.test(location.pathname) ? '../' : ''; }
  function adminHref() { return /\/admin\//.test(location.pathname) ? 'index.html' : 'admin/index.html'; }

  /* 渲染顶部导航。active: home | games | creator | admin */
  function renderNav(active) {
    var b = base();
    var u = user();
    var html = '';
    html += '<div class="topbar"><div class="topbar-inner">';
    html += '<span class="logo" onclick="location.href=\'' + b + 'index.html\'">'
      + '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
      + '<path d="M12 2.5l2.4 2.1 3.2-.4 1 3 2.9 1.4-1.2 3 1.2 3-2.9 1.4-1 3-3.2-.4L12 21.5l-2.4-2.1-3.2.4-1-3L2.5 15l1.2-3-1.2-3 2.9-1.4 1-3 3.2.4L12 2.5z" stroke="#E8A33D" stroke-width="1.5" stroke-linejoin="round"/>'
      + '<path d="M12 7.5l1.2 2.6 2.8.4-2 2 .5 2.8L12 13.9l-2.5 1.4.5-2.8-2-2 2.8-.4L12 7.5z" fill="#E8A33D"/></svg>'
      + 'GameReview <b>AI</b></span>';
    html += '<nav class="nav">'
      + '<a href="' + b + 'index.html" class="' + (active === 'home' ? 'active' : '') + '">首页</a>'
      + '<a href="' + b + 'community.html" class="' + (active === 'community' ? 'active' : '') + '">社区</a>'
      + '<a href="' + b + 'game-list.html" class="' + (active === 'games' ? 'active' : '') + '">游戏库</a>'
      + (u && (u.role === 'creator' || u.role === 'admin')
        ? '<a href="' + b + 'creator-work.html" class="' + (active === 'creator' ? 'active' : '') + '">创作者中心</a>'
        : '')
      + (u && u.role === 'admin'
        ? '<a href="' + adminHref() + '" class="' + (active === 'admin' ? 'active' : '') + '">管理后台</a>'
        : '')
      + '</nav>';
    html += '<div class="nav-search" onclick="document.getElementById(\'navSearch\').focus()">🔍 <input id="navSearch" placeholder="搜索游戏名称 / 标签…" '
      + 'onkeydown="if(event.key===\'Enter\')location.href=\'' + b + 'game-list.html?keyword=\'+encodeURIComponent(this.value)"></div>';
    html += '<div class="topbar-right">';
    if (u) {
      html += '<a class="nav-bell" href="' + b + 'messages.html" title="消息中心">'
        + '🔔<span class="bell-badge" id="bellBadge" style="display:none">0</span></a>';
      html += '<span class="badge ' + (ROLE_BADGE[u.role] || 'badge-gray') + '">' + (ROLE_NAME[u.role] || u.role) + '</span>';
      html += '<div class="user-menu">'
        + '<div class="user-chip" onclick="Auth.toggleMenu(event)">' + avatarHtml(u)
        + '<span style="font-size:13px">' + U.esc(u.profile && u.profile.nickname || u.username) + '</span> ▾</div>'
        + '<div class="dropdown" id="userDropdown">'
        + '<a href="' + b + 'messages.html">🔔 消息中心</a>'
        + '<a href="' + b + 'my-profile.html">👤 个人中心</a>';
      if (u.role === 'creator' || u.role === 'admin') {
        html += '<a href="' + b + 'creator-work.html">✍️ 创作者工作台</a>';
      } else {
        html += '<a href="' + b + 'my-profile.html?tab=apply">📝 申请成为创作者</a>';
      }
      if (u.role === 'admin') html += '<a href="' + adminHref() + '">⚙️ 管理后台</a>';
      /* ===== 多账号切换 ===== */
      var accts = Api.listAccounts();
      if (accts.length > 1 || (accts.length === 1 && accts[0].user.id !== u.id)) {
        html += '<div class="sep"></div>';
        for (var ai = 0; ai < accts.length; ai++) {
          var a = accts[ai].user;
          var isActive = a.id === u.id;
          html += '<a href="javascript:Auth.switchTo(' + ai + ')" class="acct-row ' + (isActive ? 'active' : '') + '">'
            + avatarHtml(a, 22) + '<span>' + U.esc(a.profile && a.profile.nickname || a.username)
            + '</span><span class="badge ' + (ROLE_BADGE[a.role] || 'badge-gray') + '" style="font-size:10px;">' + (ROLE_NAME[a.role] || a.role) + '</span>'
            + (isActive ? '<span style="color:var(--green)">✓</span>' : '')
            + '</a>';
        }
      }
      html += '<div class="sep"></div>';
      html += '<a href="' + b + 'login.html?add=1" style="color:var(--accent-2)">➕ 添加账号</a>';
      html += '<a href="javascript:Auth.logout()">🚪 退出当前账号</a>';
      /* 退出全部：仅当有多个账号时显示 */
      if (accts.length > 1) {
        html += '<a href="javascript:Auth.logoutAll()" style="color:var(--red)">🚪 退出全部账号</a>';
      }
      html += '</div></div>';
    } else {
      html += '<a class="btn btn-sm" href="' + b + 'login.html">登录</a>'
        + '<a class="btn btn-primary btn-sm" href="' + b + 'register.html">注册</a>';
    }
    html += '</div></div></div>';
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.user-menu')) {
        var dd = document.getElementById('userDropdown');
        if (dd) dd.classList.remove('open');
      }
    });
    return html;
  }

  /* ===== 消息中心：导航铃铛未读角标（10 秒轮询，登录后开启） ===== */
  var bellTimer = null;
  function refreshBell() {
    if (!user()) return;
    Api.get('/notifications/unread-count').then(function (d) {
      var el = document.getElementById('bellBadge');
      if (!el) return;
      var n = (d && d.count) || 0;
      if (n > 0) {
        el.style.display = '';
        el.textContent = n > 99 ? '99+' : String(n);
      } else {
        el.style.display = 'none';
      }
    }).catch(function () { /* mock 模式或未登录时静默 */ });
  }
  function startBellPoll() {
    if (!user() || bellTimer) return;
    refreshBell();
    bellTimer = setInterval(refreshBell, 10000);
  }

  function mountNav(active) {
    var el = document.getElementById('navbar');
    if (el) el.innerHTML = renderNav(active);
    startBellPoll();
  }

  function toggleMenu(e) {
    e.stopPropagation();
    document.getElementById('userDropdown').classList.toggle('open');
  }

  /* 切换到指定索引的账号 */
  function switchTo(index) {
    if (Api.switchAccount(index)) {
      var u = Api.getUser();
      U.toast('已切换到 ' + (u.profile && u.profile.nickname || u.username), 'success');
      setTimeout(function () { location.reload(); }, 500);
    }
  }

  /* 退出当前账号：如果有其他账号自动切换 */
  function logout() {
    Api.clearSession();
    var u = Api.getUser();
    if (u) {
      U.toast('已切换到 ' + (u.profile && u.profile.nickname || u.username), 'info');
      setTimeout(function () { location.reload(); }, 600);
    } else {
      U.toast('已退出登录', 'info');
      setTimeout(function () { location.href = base() + 'index.html'; }, 600);
    }
  }

  /* 退出全部账号 */
  function logoutAll() {
    localStorage.removeItem('gc_accounts');
    localStorage.removeItem('gc_token');
    localStorage.removeItem('gc_user');
    U.toast('已退出全部账号', 'info');
    setTimeout(function () { location.href = base() + 'index.html'; }, 600);
  }

  /* 守卫：需登录 */
  function requireLogin() {
    if (!user()) {
      var inAdmin = /\/admin\//.test(location.pathname);
      var b = inAdmin ? '../' : '';
      var file = location.pathname.split('/').pop() + location.search;
      var redirect = encodeURIComponent(inAdmin ? 'admin/' + file : file);
      location.href = b + 'login.html?redirect=' + redirect;
      return false;
    }
    return true;
  }

  /* 守卫：需角色（player/creator/admin 为最低角色） */
  function requireRole(role) {
    if (!requireLogin()) return false;
    var order = { player: 1, creator: 2, admin: 3 };
    var u = user();
    if (order[u.role] < order[role]) {
      U.toast('权限不足，需要' + ROLE_NAME[role] + '身份', 'error');
      setTimeout(function () { location.href = base() + 'index.html'; }, 800);
      return false;
    }
    return true;
  }

  /* 后台侧边栏 */
  function mountAdmin(active) {
    mountNav('admin');
    if (!requireRole('admin')) return false;
    var side = document.getElementById('adminSide');
    if (!side) return true;
    var items = [
      { key: 'dashboard', href: 'index.html', icon: '📊', text: '数据仪表盘' },
      { key: 'users', href: 'user.html', icon: '👥', text: '用户与申请管理' },
      { key: 'audit', href: 'audit-queue.html', icon: '⚖️', text: '审核队列 / 日志' },
      { key: 'games', href: 'game-manage.html', icon: '🎮', text: '游戏 & 分类管理' },
      { key: 'comments', href: 'comments.html', icon: '💬', text: '评论管理' },
      { key: 'community', href: 'community.html', icon: '📢', text: '社区与举报' },
      { key: 'home', href: '../index.html', icon: '🏠', text: '返回前台' }
    ];
    side.innerHTML = '<div class="side-title">后台管理</div>' + items.map(function (i) {
      return '<a href="' + i.href + '" class="' + (active === i.key ? 'active' : '') + '">' + i.icon + ' ' + i.text + '</a>';
    }).join('');
    return true;
  }

  window.Auth = {
    user: user, refreshUser: refreshUser, mountNav: mountNav, mountAdmin: mountAdmin, toggleMenu: toggleMenu, logout: logout,
    requireLogin: requireLogin, requireRole: requireRole,
    avatarHtml: avatarHtml, roleName: ROLE_NAME, roleBadge: ROLE_BADGE, base: base,
    levelBadge: levelBadge, levelInfo: levelInfo, refreshBell: refreshBell,
    switchTo: switchTo, logoutAll: logoutAll
  };
})();
