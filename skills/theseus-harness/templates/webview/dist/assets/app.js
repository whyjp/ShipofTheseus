/* theseus-view · phase 12 prebuilt shell · v0.9.40
 *
 * 데이터 우선순위:
 *   1. window.__WEBVIEW__       (cold session emit 시 inline 주입)
 *   2. fetch('./data/webview.json')   (별도 파일 fallback)
 *
 * 라이브 폴링이 필요하면 dev mode 사용 (server.ts + bun run dev) — prebuilt shell 의 책임 X.
 */
(function () {
  'use strict';

  var THEME_KEY = 'theseus-view-theme';
  var ACTIVE_TAB_KEY = 'theseus-view-active-tab';
  var root = document.documentElement;

  // ── theme ──────────────────────────────────────────────────────
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    if (window.__webviewRendered__ && window.mermaid) renderModuleGraph(window.__webviewData__ || {});
  }
  function initTheme() {
    var stored = null;
    try { stored = localStorage.getItem(THEME_KEY); } catch (e) {}
    if (!stored && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) stored = 'dark';
    applyTheme(stored || 'light');
  }
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest && ev.target.closest('[data-action="toggle-theme"]');
    if (!btn) return;
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  });

  // ── tabs ───────────────────────────────────────────────────────
  function activateTab(name) {
    var tabs = document.querySelectorAll('.tv-tab');
    var panels = document.querySelectorAll('.tv-panel');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.toggle('active', tabs[i].getAttribute('data-tab') === name);
    }
    for (var j = 0; j < panels.length; j++) {
      panels[j].classList.toggle('active', panels[j].getAttribute('data-panel') === name);
    }
    try { localStorage.setItem(ACTIVE_TAB_KEY, name); } catch (e) {}
    // mermaid 는 hidden 시 16px placeholder 만 — 활성 탭 진입 시 재렌더
    if (name === 'modules' && window.__webviewData__) renderModuleGraph(window.__webviewData__);
    if (name === 'sprints' && window.__webviewData__) drawSprintChart(window.__webviewData__.sprints || []);
    if (name === 'design' || name === 'impl') reflowMermaidIn(name);
  }
  function reflowMermaidIn(panelName) {
    if (!window.mermaid) return;
    var panel = document.querySelector('[data-panel="' + panelName + '"]');
    if (!panel) return;
    var nodes = panel.querySelectorAll('pre.mermaid');
    var pending = [];
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      // 이미 렌더된 SVG 가 16px placeholder 인지 검사
      var svg = n.querySelector('svg');
      if (!svg) { pending.push(n); continue; }
      var w = svg.getBoundingClientRect().width;
      if (w < 32) {
        // re-render
        var src = n.getAttribute('data-mermaid-src');
        if (!src) continue;
        n.removeAttribute('data-processed');
        n.textContent = src;
        pending.push(n);
      }
    }
    if (pending.length) {
      try {
        var run = window.mermaid.run || function () { window.mermaid.contentLoaded(); };
        run.call(window.mermaid, { nodes: pending });
      } catch (e) {}
    }
  }
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest && ev.target.closest('.tv-tab');
    if (!btn) return;
    activateTab(btn.getAttribute('data-tab'));
  });
  function restoreTab() {
    var saved;
    try { saved = localStorage.getItem(ACTIVE_TAB_KEY); } catch (e) {}
    if (saved) activateTab(saved);
  }

  // ── data load + auto-refresh (sprint-36) ──────────────────────
  var POLL_INTERVAL_MS = 5000;
  var refreshState = { mode: 'idle', lastEtag: null, lastModified: null, pollTimer: null, fetchInFlight: false };

  function setStatus(state, label) {
    var pill = document.querySelector('[data-bind="refresh_status"]');
    if (pill) {
      pill.setAttribute('data-state', state);
      var t = pill.querySelector('.tv-status-text');
      if (t) t.textContent = label;
    }
    var btn = document.querySelector('.tv-btn-refresh');
    if (btn) btn.setAttribute('data-state', state);
    refreshState.mode = state;
  }
  function loadInline() {
    if (window.__WEBVIEW__ && typeof window.__WEBVIEW__ === 'object') {
      return Promise.resolve({ data: window.__WEBVIEW__, source: 'inline' });
    }
    return Promise.reject(new Error('no inline'));
  }
  function loadHttp() {
    if (typeof fetch !== 'function') return Promise.reject(new Error('no fetch'));
    var headers = {};
    if (refreshState.lastEtag)     headers['If-None-Match']     = refreshState.lastEtag;
    if (refreshState.lastModified) headers['If-Modified-Since'] = refreshState.lastModified;
    return fetch('./data/webview.json?_t=' + Date.now(), { cache: 'no-store', headers: headers })
      .then(function (r) {
        if (r.status === 304) return { data: null, source: 'http-304' };
        if (!r.ok) throw new Error('webview.json fetch failed: ' + r.status);
        var et = r.headers.get('ETag');
        var lm = r.headers.get('Last-Modified');
        return r.json().then(function (j) {
          if (et) refreshState.lastEtag     = et;
          if (lm) refreshState.lastModified = lm;
          return { data: j, source: 'http' };
        });
      });
  }
  function loadData(opts) {
    opts = opts || {};
    if (!opts.skipInline && window.__WEBVIEW__) return loadInline();
    return loadHttp();
  }
  function startPolling() {
    if (refreshState.pollTimer) clearInterval(refreshState.pollTimer);
    refreshState.pollTimer = setInterval(function () {
      if (document.hidden) return;
      pollOnce();
    }, POLL_INTERVAL_MS);
  }
  function pollOnce() {
    if (refreshState.fetchInFlight) return;
    refreshState.fetchInFlight = true;
    setStatus('updating', '갱신 중');
    return loadHttp()
      .then(function (res) {
        if (res.source === 'http-304') { setStatus('live', 'live'); return; }
        if (res.data) {
          window.__webviewData__ = res.data;
          renderAll(res.data);
          setStatus('live', 'live · updated');
        }
      })
      .catch(function () { setStatus('offline', 'offline · F5'); })
      .finally(function () { refreshState.fetchInFlight = false; });
  }
  function manualRefresh() {
    if (refreshState.fetchInFlight) return;
    setStatus('updating', '수동 갱신');
    loadData({ skipInline: true })
      .then(function (res) {
        if (res.data) {
          window.__webviewData__ = res.data;
          renderAll(res.data);
          setStatus(refreshState.pollTimer ? 'live' : 'manual', refreshState.pollTimer ? 'live · manual' : 'manual');
        }
      })
      .catch(function () { setStatus('offline', 'fetch 차단 — F5'); });
  }
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && refreshState.pollTimer) pollOnce();
  });
  document.addEventListener('click', function (ev) {
    if (ev.target.closest && ev.target.closest('[data-action="manual-refresh"]')) manualRefresh();
  });

  // ── helpers ────────────────────────────────────────────────────
  function setText(selector, value, fallback) {
    var nodes = document.querySelectorAll(selector);
    var v = (value === null || value === undefined || value === '') ? (fallback || '—') : value;
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = v;
  }
  function fmtDuration(seconds) {
    if (typeof seconds !== 'number' || !isFinite(seconds)) return '—';
    var s = Math.max(0, Math.floor(seconds));
    var h = Math.floor(s / 3600);
    var m = Math.floor((s % 3600) / 60);
    if (h > 0) return h + 'h ' + (m < 10 ? '0' + m : m) + 'm';
    if (m > 0) return m + 'm ' + (s % 60) + 's';
    return s + 's';
  }
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === 'className') n.className = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else if (k === 'html') n.innerHTML = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    if (children) for (var i = 0; i < children.length; i++) {
      var c = children[i];
      if (c == null) continue;
      n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return n;
  }
  function renderMd(src) {
    if (!window.marked) return '<pre>' + escapeHtml(src) + '</pre>';
    try {
      window.marked.setOptions({ breaks: false, gfm: true });
      return window.marked.parse(src);
    } catch (err) {
      return '<pre>' + escapeHtml(src) + '</pre>';
    }
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function processMermaidInBody(container) {
    if (!window.mermaid) return;
    // Convert ```mermaid 코드 펜스 → <pre class="mermaid">
    var codeBlocks = container.querySelectorAll('pre > code.language-mermaid, pre > code.language-Mermaid');
    for (var i = 0; i < codeBlocks.length; i++) {
      var pre = codeBlocks[i].parentNode;
      var src = codeBlocks[i].textContent;
      var newPre = document.createElement('pre');
      newPre.className = 'mermaid';
      newPre.setAttribute('data-mermaid-src', src);   // reflow 시 재렌더용
      newPre.textContent = src;
      pre.parentNode.replaceChild(newPre, pre);
    }
    // 이미 변환된 노드 중 src 미저장 분도 보충
    var allMermaid = container.querySelectorAll('pre.mermaid');
    for (var k = 0; k < allMermaid.length; k++) {
      if (!allMermaid[k].getAttribute('data-mermaid-src')) {
        allMermaid[k].setAttribute('data-mermaid-src', allMermaid[k].textContent);
      }
    }
    var run = window.mermaid.run || function () { window.mermaid.contentLoaded(); };
    try { run.call(window.mermaid, { nodes: container.querySelectorAll('pre.mermaid:not([data-processed])') }); }
    catch (e) { /* no-op */ }
  }

  // ── renderers ──────────────────────────────────────────────────
  function renderHeader(d) {
    var t = d.timing || {};
    setText('[data-bind="project_id"]',     d.project_id);
    setText('[data-bind="started_at_iso"]', t.started_at_iso);
    setText('[data-bind="duration_human"]', fmtDuration(t.duration_seconds));
    setText('[data-bind="final_phase"]',    d.final_phase || (d.state && d.state.last_completed_phase) || '—');
    setText('[data-bind="emit_mode"]',      d.emit_mode || 'prebuilt');
    var s = d.state || {};
    var statusBadges = document.querySelectorAll('[data-bind="status"]');
    for (var i = 0; i < statusBadges.length; i++) {
      statusBadges[i].textContent = s.status || '—';
      statusBadges[i].setAttribute('data-state', s.status || '—');
    }
  }

  function renderProgress(d) {
    var s = d.state || {};
    setText('[data-panel="progress"] [data-bind="current_phase"]',         s.current_phase);
    setText('[data-panel="progress"] [data-bind="active_skill"]',          s.active_skill);
    setText('[data-panel="progress"] [data-bind="active_agent"]',          s.active_agent);
    setText('[data-panel="progress"] [data-bind="current_universe"]',      s.current_universe);
    setText('[data-panel="progress"] [data-bind="current_module"]',
      s.current_module ? s.current_module + ' (depth ' + (s.current_sub_depth || 0) + ')' : '—');
    setText('[data-panel="progress"] [data-bind="last_completed_phase"]',  s.last_completed_phase);
    var pct = (s.completed_count != null && s.total_estimated)
      ? s.completed_count + ' / ' + s.total_estimated +
        ' (' + Math.round((s.completed_count / s.total_estimated) * 100) + '%)'
      : '—';
    setText('[data-panel="progress"] [data-bind="progress_pct"]', pct);

    var ul = document.querySelector('[data-list="pending_artifacts"]');
    if (ul) {
      ul.innerHTML = '';
      var arts = s.pending_artifacts || [];
      if (!arts.length) {
        ul.appendChild(el('li', { className: 'tv-empty', text: '없음' }));
      } else {
        arts.forEach(function (p) { ul.appendChild(el('li', { text: p })); });
      }
    }
  }

  function renderModuleGraph(d) {
    var target = document.querySelector('[data-mermaid-target="modules"]');
    if (!target) return;
    var src = (d.plan && d.plan.module_graph_mermaid) || (d.module_graph_mermaid) || '';
    if (!src) return;
    target.classList.remove('tv-mermaid-error');
    target.removeAttribute('data-processed');
    target.textContent = src;

    if (!window.mermaid) {
      target.classList.add('tv-mermaid-error');
      target.textContent = 'mermaid.min.js 미로드';
      return;
    }
    try {
      var isDark = root.getAttribute('data-theme') === 'dark';
      var themeVars = isDark ? {
        background:        '#0a0a14',
        primaryColor:      '#1e1b4b',
        primaryBorderColor:'#818cf8',
        primaryTextColor:  '#fafafa',
        lineColor:         '#71717a',
        secondaryColor:    '#11111c',
        tertiaryColor:     '#1c1c2a',
        textColor:         '#fafafa',
        fontFamily:        '"Inter Variable", "Inter", "Pretendard", system-ui, sans-serif'
      } : {
        background:        '#fafbff',
        primaryColor:      '#eef2ff',
        primaryBorderColor:'#4f46e5',
        primaryTextColor:  '#09090b',
        lineColor:         '#71717a',
        secondaryColor:    '#f4f4f7',
        tertiaryColor:     '#ffffff',
        textColor:         '#09090b',
        fontFamily:        '"Inter Variable", "Inter", "Pretendard", system-ui, sans-serif'
      };
      window.mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        themeVariables: themeVars,
        securityLevel: 'loose',
        flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' }
      });
      var run = window.mermaid.run || function () { window.mermaid.contentLoaded(); };
      run.call(window.mermaid, { querySelector: '[data-mermaid-target="modules"]' });
      window.__webviewRendered__ = true;
    } catch (err) {
      target.classList.add('tv-mermaid-error');
      target.textContent = 'Mermaid 렌더 실패: ' + (err && err.message || err);
    }
  }

  function renderMdList(panel, files) {
    var container = document.querySelector('[data-md-list="' + panel + '"]');
    if (!container) return;
    container.innerHTML = '';
    var entries = Object.keys(files || {});
    if (!entries.length) {
      container.appendChild(el('div', { className: 'tv-empty', text: '데이터 없음' }));
      return;
    }
    entries.sort().forEach(function (name) {
      var src = files[name] || '';
      var card = el('article', { className: 'tv-md-card' }, [
        el('header', { className: 'tv-md-card-head', text: name }),
        el('div', { className: 'tv-md-card-body', html: renderMd(src) })
      ]);
      container.appendChild(card);
      processMermaidInBody(card);
    });
  }

  function renderUnitTests(rows) {
    var tbody = document.querySelector('[data-table="unit_tests"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 6, className: 'tv-empty', text: '데이터 없음' })]));
      return;
    }
    rows.forEach(function (r) {
      var pass = r.pass || 0, fail = r.fail || 0, total = r.total || (pass + fail);
      var rate = total > 0 ? Math.round((pass / total) * 100) : 0;
      var failures = (r.failures || []).slice(0, 3).join(', ');
      if ((r.failures || []).length > 3) failures += ', …';
      var tr = el('tr', null, [
        el('td', { className: 'tv-cell-mono', text: r.sprint || '—' }),
        el('td', { className: 'tv-cell-num', text: String(total) }),
        el('td', { className: 'tv-cell-num tv-cell-pass', text: String(pass) }),
        el('td', { className: 'tv-cell-num ' + (fail > 0 ? 'tv-cell-fail' : ''), text: String(fail) }),
        el('td', { className: 'tv-cell-num', text: rate + '%' }),
        el('td', { className: 'tv-cell-mono', text: failures || '—' })
      ]);
      tbody.appendChild(tr);
    });
  }

  function renderE2E(rows) {
    var tbody = document.querySelector('[data-table="e2e_tests"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    var flat = [];
    (rows || []).forEach(function (entry) {
      (entry.scenarios || []).forEach(function (sc) {
        flat.push({ sprint: entry.sprint, scenario: sc.name, status: sc.status, steps: sc.steps, note: sc.note });
      });
    });
    if (!flat.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 5, className: 'tv-empty', text: '데이터 없음' })]));
      return;
    }
    flat.forEach(function (r) {
      var statusCls = r.status === 'pass' ? 'tv-cell-pass' :
                      r.status === 'fail' ? 'tv-cell-fail' :
                      r.status === 'skip' ? 'tv-cell-skip' : '';
      var tr = el('tr', null, [
        el('td', { className: 'tv-cell-mono', text: r.sprint || '—' }),
        el('td', { text: r.scenario || '—' }),
        el('td', { className: statusCls, text: r.status || '—' }),
        el('td', { className: 'tv-cell-num', text: r.steps != null ? String(r.steps) : '—' }),
        el('td', { text: r.note || '' })
      ]);
      tbody.appendChild(tr);
    });
  }

  function renderSprints(rows) {
    var tbody = document.querySelector('[data-table="sprints"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 4, className: 'tv-empty', text: '데이터 없음' })]));
      return;
    }
    rows.forEach(function (r) {
      var tr = el('tr', null, [
        el('td', { className: 'tv-cell-mono', text: r.sprint || '—' }),
        el('td', { className: 'tv-cell-num', text: r.score != null ? r.score.toFixed(3) : '—' }),
        el('td', { text: r.outcome || '—' }),
        el('td', { className: 'tv-cell-mono', text: r.bisect || '—' })
      ]);
      tbody.appendChild(tr);
    });

    drawSprintChart(rows);
  }

  function drawSprintChart(rows) {
    var svg = document.querySelector('[data-chart="sprint-score"]');
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (!rows || !rows.length) return;

    var W = 800, H = 240, padL = 50, padR = 20, padT = 20, padB = 30;
    var n = rows.length;
    var xs = function (i) { return padL + (i * (W - padL - padR) / Math.max(n - 1, 1)); };
    var ys = function (v) { return padT + (1 - v) * (H - padT - padB); };

    var ns = 'http://www.w3.org/2000/svg';
    function svgEl(tag, attrs) {
      var n = document.createElementNS(ns, tag);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      return n;
    }

    // gradient defs for line stroke
    var defs = svgEl('defs', {});
    var grad = svgEl('linearGradient', { id: 'tv-grad', x1: '0%', y1: '0%', x2: '100%', y2: '0%' });
    var s1 = svgEl('stop', { offset: '0%', 'stop-color': '#4f46e5' });
    var s2 = svgEl('stop', { offset: '50%', 'stop-color': '#7c3aed' });
    var s3 = svgEl('stop', { offset: '100%', 'stop-color': '#a855f7' });
    grad.appendChild(s1); grad.appendChild(s2); grad.appendChild(s3);
    defs.appendChild(grad);
    svg.appendChild(defs);

    // grid + y-axis labels (0.0, 0.5, 1.0)
    var grid = svgEl('g', { class: 'grid' });
    var axis = svgEl('g', { class: 'axis' });
    [0.0, 0.5, 0.999, 1.0].forEach(function (v) {
      var y = ys(v);
      grid.appendChild(svgEl('line', { x1: padL, x2: W - padR, y1: y, y2: y }));
      var lbl = svgEl('text', { x: padL - 6, y: y + 3, 'text-anchor': 'end' });
      lbl.textContent = v.toFixed(3);
      axis.appendChild(lbl);
    });
    svg.appendChild(grid);
    svg.appendChild(axis);

    // 0.999 임계 점선
    svg.appendChild(svgEl('path', {
      class: 'threshold',
      d: 'M' + padL + ',' + ys(0.999) + ' L' + (W - padR) + ',' + ys(0.999)
    }));
    var thrLabel = svgEl('text', { class: 'label', x: W - padR - 4, y: ys(0.999) - 4, 'text-anchor': 'end' });
    thrLabel.textContent = '임계 0.999';
    svg.appendChild(thrLabel);

    // 라인
    var dParts = [];
    rows.forEach(function (r, i) {
      var v = (r.score != null && isFinite(r.score)) ? Math.max(0, Math.min(1, r.score)) : 0;
      dParts.push((i === 0 ? 'M' : 'L') + xs(i) + ',' + ys(v));
    });
    svg.appendChild(svgEl('path', { class: 'line', d: dParts.join(' ') }));

    // 점 + sprint label
    rows.forEach(function (r, i) {
      var v = (r.score != null && isFinite(r.score)) ? Math.max(0, Math.min(1, r.score)) : 0;
      svg.appendChild(svgEl('circle', { class: 'point', cx: xs(i), cy: ys(v), r: 4 }));
      var lab = svgEl('text', { class: 'label', x: xs(i), y: H - padB + 16, 'text-anchor': 'middle' });
      lab.textContent = r.sprint || ('s' + (i + 1));
      svg.appendChild(lab);
    });
  }

  function renderRuntime(d) {
    var rt = d.runtime || {};
    var pq = rt.prereq || {};
    var br = rt.boot_result || {};
    setText('[data-bind="rt_mode"]',           pq.mode);
    setText('[data-bind="rt_secrets_count"]',  pq.secrets_count != null ? String(pq.secrets_count) : '—');
    setText('[data-bind="rt_boot_command"]',   pq.boot_command);
    setText('[data-bind="rt_env_hash"]',       pq.env_hash);
    setText('[data-bind="rt_boot_exit"]',      br.boot_exit != null ? String(br.boot_exit) : '—');
    setText('[data-bind="rt_healthz_status"]', br.healthz_status != null ? String(br.healthz_status) : '—');
    setText('[data-bind="rt_elapsed_ms"]',     br.elapsed_ms != null ? String(br.elapsed_ms) : '—');

    var outcome = (br.boot_exit === 0 && br.healthz_status >= 200 && br.healthz_status < 300) ? 'OK' :
                  (br.boot_exit == null ? 'SKIP' : 'FAIL');
    var badge = document.querySelector('[data-bind="rt_outcome"]');
    if (badge) {
      badge.textContent = outcome;
      badge.setAttribute('data-state', outcome);
    }
  }

  function renderError(message) {
    var main = document.querySelector('.tv-main');
    if (!main) return;
    main.innerHTML = '';
    main.appendChild(el('section', { className: 'tv-panel active' }, [
      el('h2', { className: 'tv-panel-title', text: '데이터 로드 실패' }),
      el('p',  { className: 'tv-panel-note', text: message }),
      el('pre', { className: 'tv-mermaid-target tv-mermaid-error' }, [
        document.createTextNode(
          'window.__WEBVIEW__ 가 주입되지 않았고 ./data/webview.json 도 로드 실패.\n' +
          'cold session emit 측에서 둘 중 하나를 보장해야 합니다.'
        )
      ])
    ]));
  }

  function renderAll(d) {
    renderHeader(d);
    renderProgress(d);
    renderModuleGraph(d);
    renderMdList('design', (d.intent || {}));
    renderMdList('impl', Object.assign({}, d.impl || {}, d.quality ? { 'quality.md': d.quality } : {}));
    renderUnitTests(d.tests && d.tests.unit);
    renderE2E(d.tests && d.tests.e2e);
    renderSprints(d.sprints);
    renderRuntime(d);
  }

  // ── boot ───────────────────────────────────────────────────────
  initTheme();
  restoreTab();

  loadData()
    .then(function (res) {
      window.__webviewData__ = res.data;
      renderAll(res.data);
      if (res.source === 'inline') {
        if (typeof fetch === 'function' && location.protocol !== 'file:') {
          startPolling();
          setStatus('live', 'live');
        } else {
          setStatus('manual', 'manual only');
        }
      } else {
        startPolling();
        setStatus('live', 'live');
      }
    })
    .catch(function (err) {
      console.error('[theseus-view]', err);
      renderError((err && err.message) || String(err));
      setStatus('offline', 'offline');
    });
})();
