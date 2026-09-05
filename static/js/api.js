/* ============================================================
   api.js — 请求层（阶段3 产物）
   - 自动探测后端：/api/health 可达 → 真实 FastAPI；否则 → Mock
   - 自动携带 JWT（Authorization: Bearer）
   - 401 统一处理：清除 token 跳转登录页
   ============================================================ */

(function () {
  'use strict';

  var TOKEN_KEY = 'gc_token';
  var USER_KEY = 'gc_user';
  var mode = 'unknown'; // 'real' | 'mock'

  function getToken() { return localStorage.getItem(TOKEN_KEY) || ''; }
  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
  function getUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); }
    catch (e) { return null; }
  }

  /* 探测后端是否在线（1.5s 超时） */
  function detectBackend() {
    return new Promise(function (resolve) {
      if (location.protocol === 'file:') { mode = 'mock'; return resolve(mode); }
      var ctrl = new AbortController();
      var timer = setTimeout(function () { ctrl.abort(); }, 1500);
      fetch('/api/health', { signal: ctrl.signal })
        .then(function (r) { clearTimeout(timer); mode = r.ok ? 'real' : 'mock'; resolve(mode); })
        .catch(function () { clearTimeout(timer); mode = 'mock'; resolve(mode); });
    });
  }

  function delay(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  async function request(method, path, body) {
    if (mode === 'unknown') await detectBackend();

    /* ---- Mock 模式 ---- */
    if (mode === 'mock') {
      await delay(180 + Math.random() * 220); // 模拟网络延迟
      var headers = { Authorization: 'Bearer ' + getToken() };
      try {
        return window.MockApi.handle(method, '/api' + path, body, headers);
      } catch (e) {
        if (e.status === 401) { handle401(); }
        var err = new Error(e.message || '请求失败');
        err.status = e.status || 500;
        throw err;
      }
    }

    /* ---- 真实后端模式 ---- */
    var opts = { method: method, headers: { 'Content-Type': 'application/json' } };
    var token = getToken();
    if (token) opts.headers.Authorization = 'Bearer ' + token;
    if (body !== undefined && body !== null) opts.body = JSON.stringify(body);

    var res = await fetch('/api' + path, opts);
    if (res.status === 401) { handle401(); throw Object.assign(new Error('未登录或登录已过期'), { status: 401 }); }
    var data = null;
    try { data = await res.json(); } catch (e) { data = {}; }
    if (!res.ok) {
      var msg = (data && (data.detail || data.message)) || '请求失败 (' + res.status + ')';
      throw Object.assign(new Error(typeof msg === 'string' ? msg : JSON.stringify(msg)), { status: res.status });
    }
    return data;
  }

  function handle401() {
    clearSession();
    if (!/login\.html/.test(location.pathname)) {
      var inAdmin = /\/admin\//.test(location.pathname);
      var prefix = inAdmin ? '../' : '';
      var file = location.pathname.split('/').pop() + location.search;
      var redirect = encodeURIComponent(inAdmin ? 'admin/' + file : file);
      location.href = prefix + 'login.html?redirect=' + redirect;
    }
  }

  window.Api = {
    request: request,
    get: function (p) { return request('GET', p); },
    post: function (p, b) { return request('POST', p, b || {}); },
    put: function (p, b) { return request('PUT', p, b || {}); },
    del: function (p) { return request('DELETE', p); },
    detectBackend: detectBackend,
    getMode: function () { return mode; },
    getToken: getToken,
    setSession: setSession,
    clearSession: clearSession,
    getUser: getUser
  };
})();
