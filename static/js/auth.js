/* ============================================================
   auth.js — 会话 / 导航 / 权限守卫（阶段3 产物）
   ============================================================ */

(function () {
  'use strict';

  var ROLE_NAME = { player: '玩家', creator: '创作者', admin: '管理员' };
  var ROLE_BADGE = { player: 'badge-blue', creator: 'badge-green', admin: 'badge-red' };
  var AVATAR_COLORS = ['#7c5cff', '#4f8cff', '#34d399', '#fbbf24', '#f87171', '#ec4899'];

  function user() { return Api.getUser(); }

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
    html += '<span class="logo" onclick="location.href=\'' + b + 'index.html\'">🎮 GameReview AI</span>';
    html += '<nav class="nav">'
      + '<a href="' + b + 'index.html" class="' + (active === 'home' ? 'active' : '') + '">首页</a>'
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
      html += '<span class="badge ' + (ROLE_BADGE[u.role] || 'badge-gray') + '">' + (ROLE_NAME[u.role] || u.role) + '</span>';
      html += '<div class="user-menu">'
        + '<div class="user-chip" onclick="Auth.toggleMenu(event)">' + avatarHtml(u)
        + '<span style="font-size:13px">' + U.esc(u.profile && u.profile.nickname || u.username) + '</span> ▾</div>'
        + '<div class="dropdown" id="userDropdown">'
        + '<a href="' + b + 'my-profile.html">👤 个人中心</a>';
      if (u.role === 'creator' || u.role === 'admin') {
        html += '<a href="' + b + 'creator-work.html">✍️ 创作者工作台</a>';
      } else {
        html += '<a href="' + b + 'my-profile.html?tab=apply">📝 申请成为创作者</a>';
      }
      if (u.role === 'admin') html += '<a href="' + adminHref() + '">⚙️ 管理后台</a>';
      html += '<div class="sep"></div><a href="javascript:Auth.logout()">🚪 退出登录</a>'
        + '</div></div>';
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

  function mountNav(active) {
    var el = document.getElementById('navbar');
    if (el) el.innerHTML = renderNav(active);
  }

  function toggleMenu(e) {
    e.stopPropagation();
    document.getElementById('userDropdown').classList.toggle('open');
  }

  function logout() {
    Api.clearSession();
    U.toast('已退出登录', 'info');
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
      { key: 'home', href: '../index.html', icon: '🏠', text: '返回前台' }
    ];
    side.innerHTML = '<div class="side-title">后台管理</div>' + items.map(function (i) {
      return '<a href="' + i.href + '" class="' + (active === i.key ? 'active' : '') + '">' + i.icon + ' ' + i.text + '</a>';
    }).join('');
    return true;
  }

  window.Auth = {
    user: user, mountNav: mountNav, mountAdmin: mountAdmin, toggleMenu: toggleMenu, logout: logout,
    requireLogin: requireLogin, requireRole: requireRole,
    avatarHtml: avatarHtml, roleName: ROLE_NAME, roleBadge: ROLE_BADGE, base: base
  };
})();
