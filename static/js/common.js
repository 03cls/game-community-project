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
    manual_review: { text: '人工复核中', cls: 'badge-blue' },
    published: { text: '已发布', cls: 'badge-green' },
    rejected: { text: 'AI 驳回', cls: 'badge-red' }
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

  /* ---------- 游戏卡片 ---------- */
  function gameCard(g) {
    var tags = (g.tags || []).slice(0, 3).map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('');
    return '<div class="card card-hover game-card" onclick="location.href=\'game-detail.html?id=' + g.id + '\'">'
      + '<img class="cover" src="' + esc(g.cover_url) + '" alt="' + esc(g.name) + '" loading="lazy">'
      + '<div class="body"><div class="name">' + esc(g.name) + '</div>'
      + '<div class="meta">' + esc(g.name_en || '') + '</div>'
      + tags
      + '<div class="foot"><span class="score">★ ' + Number(g.average_score).toFixed(1) + '</span>'
      + '<span class="dim">' + fmtDate(g.release_date) + '</span></div>'
      + '</div></div>';
  }

  /* ---------- 分页 ---------- */
  function pagination(totalPages, current, onGo) {
    if (totalPages <= 1) return '';
    var html = '<div class="pagination">';
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
      $all('.pagination button[data-p]').forEach(function (btn) {
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
    return '<div class="footer">🎮 AI 游戏社区评测分享平台 · 课程项目 · 数据为 Mock 模拟（游戏信息来源于 Steam 公开资料）</div>';
  }

  window.U = {
    $: $, $all: $all, esc: esc, qs: qs, fmtDate: fmtDate, fmtNum: fmtNum,
    toast: toast, reviewBadge: reviewBadge, playBadge: playBadge,
    gameCard: gameCard, pagination: pagination,
    openModal: openModal, closeModal: closeModal, footer: footer
  };
})();
