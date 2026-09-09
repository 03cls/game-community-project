/* ============================================================
   api.js — 请求层（阶段3 产物 + 多账号支持）
   - 自动探测后端：/api/health 可达 → 真实 FastAPI；否则 → Mock
   - 自动携带 JWT（Authorization: Bearer）
   - 401 统一处理：移除失效账号，有其他账号则自动切换，否则跳转登录页
   - 多账号：gc_accounts 存储已登录账号列表，gc_token/gc_user 为当前活跃账号
   ============================================================ */

(function () {
  'use strict';

  var TOKEN_KEY = 'gc_token';
  var USER_KEY = 'gc_user';
  var ACCOUNTS_KEY = 'gc_accounts'; /* [{token, user}] */
  var mode = 'unknown'; // 'real' | 'mock'

  /* ===== 多账号存储 ===== */
  function getAccounts() {
    try { return JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || '[]'); }
    catch (e) { return []; }
  }
  function saveAccounts(list) {
    localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(list));
  }

  function getToken() { return localStorage.getItem(TOKEN_KEY) || ''; }
  function getUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); }
    catch (e) { return null; }
  }

  /* 设置当前会话，同时写入账号列表（去重：同 user.id 覆盖） */
  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    var accounts = getAccounts();
    var idx = -1;
    for (var i = 0; i < accounts.length; i++) {
      if (accounts[i].user && user && accounts[i].user.id === user.id) { idx = i; break; }
    }
    if (idx >= 0) { accounts[idx].token = token; accounts[idx].user = user; }
    else { accounts.push({ token: token, user: user }); }
    saveAccounts(accounts);
  }

  /* 退出当前账号：从列表移除；有其他账号则自动切换到第一个 */
  function clearSession() {
    var token = getToken();
    var accounts = getAccounts().filter(function (a) { return a.token !== token; });
    saveAccounts(accounts);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    if (accounts.length > 0) {
      localStorage.setItem(TOKEN_KEY, accounts[0].token);
      localStorage.setItem(USER_KEY, JSON.stringify(accounts[0].user));
    }
  }

  /* 切换到指定索引的账号 */
  function switchAccount(index) {
    var accounts = getAccounts();
    if (index < 0 || index >= accounts.length) return false;
    var a = accounts[index];
    localStorage.setItem(TOKEN_KEY, a.token);
    localStorage.setItem(USER_KEY, JSON.stringify(a.user));
    return true;
  }

  /* 移除指定索引的账号（不退出当前登录，仅从列表删除） */
  function removeAccount(index) {
    var accounts = getAccounts();
    if (index < 0 || index >= accounts.length) return;
    var removed = accounts.splice(index, 1)[0];
    saveAccounts(accounts);
    /* 如果删的是当前活跃账号，切到第一个 */
    if (removed.token === getToken()) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      if (accounts.length > 0) {
        localStorage.setItem(TOKEN_KEY, accounts[0].token);
        localStorage.setItem(USER_KEY, JSON.stringify(accounts[0].user));
      }
    }
  }

  function listAccounts() { return getAccounts(); }

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

  /* 401 处理：移除失效账号，有其他账号则自动切换并刷新，否则跳登录页 */
  function handle401() {
    var token = getToken();
    var accounts = getAccounts().filter(function (a) { return a.token !== token; });
    saveAccounts(accounts);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    if (accounts.length > 0) {
      /* 切到另一个账号，刷新当前页 */
      localStorage.setItem(TOKEN_KEY, accounts[0].token);
      localStorage.setItem(USER_KEY, JSON.stringify(accounts[0].user));
      location.reload();
      return;
    }
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
    getUser: getUser,
    listAccounts: listAccounts,
    switchAccount: switchAccount,
    removeAccount: removeAccount
  };
})();
