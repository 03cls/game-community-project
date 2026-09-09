/* ============================================================
   common.js — 公共工具（阶段3 产物）
   ============================================================ */

(function () {
  'use strict';

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function esc(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function qs(name) {
    var m = new RegExp('[?&]' + name + '=([^&]*)').exec(location.search);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function fmtDate(iso) {
    if (!iso) return '-';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function fmtNum(n) {
    n = n || 0;
    if (n >= 10000) return (n / 10000).toFixed(1) + 'w';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
    return String(n);
  }

  /* ---------- Toast ---------- */
  function toast(msg, type) {
    var wrap = document.getElementById('toast-wrap');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.id = 'toast-wrap';
      document.body.appendChild(wrap);
    }
    var el = document.createElement('div');
    el.className = 'toast ' + (type || 'info');
    el.textContent = msg;
    wrap.appendChild(el);
    setTimeout(function () { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; }, 2200);
    setTimeout(function () { el.remove(); }, 2600);
  }

  /* ---------- 状态徽标 ---------- */
  var REVIEW_STATUS = {
    draft: { text: '草稿', cls: 'badge-gray' },
    audit: { text: '审核中', cls: 'badge-amber' },
    manual_review: { text: '待审核', cls: 'badge-amber' },
    published: { text: '已发布', cls: 'badge-green' },
    rejected: { text: '已驳回', cls: 'badge-red' }
  };
  function reviewBadge(status) {
    var s = REVIEW_STATUS[status] || { text: status, cls: 'badge-gray' };
    return '<span class="badge ' + s.cls + '">' + s.text + '</span>';
  }
  var PLAY_STATUS = { want: { text: '想玩', cls: 'badge-blue' }, playing: { text: '正在玩', cls: 'badge-amber' }, completed: { text: '已通关', cls: 'badge-green' } };
  function playBadge(s) {
    var p = PLAY_STATUS[s] || { text: s, cls: 'badge-gray' };
    return '<span class="badge ' + p.cls + '">' + p.text + '</span>';
  }

  /* ---------- 封面图容错：Steam CDN 多镜像自动回退 + 占位图兜底 ---------- */
  var COVER_MIRRORS = [
    'https://cdn.akamai.steamstatic.com/steam/apps/',
    'https://steamcdn-a.akamaihd.net/steam/apps/',
    'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/',
    'https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/'
  ];
  var COVER_FALLBACK = 'data:image/svg+xml;utf8,' + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="460" height="215">'
    + '<rect width="460" height="215" fill="#232833"/>'
    + '<rect x="192" y="70" width="76" height="52" rx="12" fill="none" stroke="#5a6478" stroke-width="5"/>'
    + '<circle cx="214" cy="96" r="15" fill="none" stroke="#5a6478" stroke-width="5"/>'
    + '<text x="230" y="158" fill="#7c869c" font-size="16" text-anchor="middle" font-family="sans-serif">封面加载失败</text>'
    + '</svg>'
  );
  window.coverError = function (img) {
    var m = /steam\/apps\/(\d+)\//.exec(img.src || '');
    var step = parseInt(img.getAttribute('data-fb') || '0', 10);
    if (m && step < COVER_MIRRORS.length) {
      img.setAttribute('data-fb', String(step + 1));
      img.src = COVER_MIRRORS[step] + m[1] + '/header.jpg';
    } else {
      img.onerror = null;
      img.src = COVER_FALLBACK;
    }
  };

  /* ---------- 游戏卡片 ---------- */
  function gameCard(g) {
    var tags = (g.tags || []).slice(0, 3).map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('');
    return '<div class="card card-hover game-card" onclick="location.href=\'game-detail.html?id=' + g.id + '\'">'
      + '<img class="cover" src="' + esc(g.cover_url) + '" alt="' + esc(g.name) + '" loading="lazy" onerror="coverError(this)">'
      + '<div class="body"><div class="name">' + esc(g.name) + '</div>'
      + '<div class="meta">' + esc(g.name_en || '') + '</div>'
      + tags
      + '<div class="foot"><span class="score">★ ' + Number(g.average_score).toFixed(1) + '</span>'
      + '<span class="dim">' + (g.rating_count ? g.rating_count + ' 人评分' : '暂无评分') + '</span>'
      + '<span class="dim">' + fmtDate(g.release_date) + '</span></div>'
      + '</div></div>';
  }

  /* ---------- 分页 ----------
     同一页面可能存在多个分页器，用唯一容器 id 限定事件绑定范围，
     避免 setTimeout 全局绑定把其它分页器的回调覆盖掉。 */
  var pgSeq = 0;
  function pagination(totalPages, current, onGo) {
    if (totalPages <= 1) return '';
    var pgId = 'pg_' + (++pgSeq);
    var html = '<div class="pagination" id="' + pgId + '">';
    html += '<button ' + (current <= 1 ? 'disabled' : '') + ' data-p="' + (current - 1) + '">‹</button>';
    var pages = [];
    for (var i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || Math.abs(i - current) <= 1) pages.push(i);
      else if (pages[pages.length - 1] !== '…') pages.push('…');
    }
    pages.forEach(function (p) {
      if (p === '…') html += '<button disabled>…</button>';
      else html += '<button class="' + (p === current ? 'active' : '') + '" data-p="' + p + '">' + p + '</button>';
    });
    html += '<button ' + (current >= totalPages ? 'disabled' : '') + ' data-p="' + (current + 1) + '">›</button></div>';
    setTimeout(function () {
      var scope = document.getElementById(pgId);
      if (!scope) return;
      $all('#' + pgId + ' button[data-p]').forEach(function (btn) {
        btn.onclick = function () { onGo(parseInt(btn.getAttribute('data-p'), 10)); };
      });
    }, 0);
    return html;
  }

  /* ---------- 弹窗 ---------- */
  function openModal(html) {
    var mask = document.getElementById('modal-mask');
    if (!mask) {
      mask = document.createElement('div');
      mask.id = 'modal-mask';
      mask.className = 'modal-mask';
      mask.onclick = function (e) { if (e.target === mask) closeModal(); };
      document.body.appendChild(mask);
    }
    mask.innerHTML = '<div class="modal">' + html + '</div>';
    mask.classList.add('open');
    return mask;
  }
  function closeModal() {
    var mask = document.getElementById('modal-mask');
    if (mask) { mask.classList.remove('open'); mask.innerHTML = ''; }
  }

  /* 页面底部 */
  function footer() {
    return '<div class="footer">'
      + '<div class="foot-brand">GameReview <b>AI</b> · AI 游戏社区评测分享平台</div>'
      + '<div>课程项目 · 数据为 Mock 模拟（游戏信息来源于 Steam 公开资料）</div>'
      + '</div>';
  }

  /* ===== 智能返回：同标签页用 history.back()，新标签页（target=_blank）用 referrer，兜底 fallback ===== */
  function goBack(fallback) {
    fallback = fallback || 'index.html';
    /* 同标签页导航（有历史且非弹出窗口）→ 浏览器后退 */
    if (history.length > 1 && !window.opener) {
      history.back();
      return;
    }
    /* 新标签页（window.opener 存在或无历史）→ 优先 referrer */
    var ref = document.referrer;
    if (ref) {
      try {
        var url = new URL(ref);
        if (url.origin === location.origin && url.pathname !== location.pathname) {
          location.href = url.pathname + url.search;
          return;
        }
      } catch (e) { /* 非法 referrer，走 fallback */ }
    }
    location.href = fallback;
  }

  window.U = {
    $: $, $all: $all, esc: esc, qs: qs, fmtDate: fmtDate, fmtNum: fmtNum,
    toast: toast, reviewBadge: reviewBadge, playBadge: playBadge,
    gameCard: gameCard, pagination: pagination,
    openModal: openModal, closeModal: closeModal, footer: footer,
    goBack: goBack
  };
})();
