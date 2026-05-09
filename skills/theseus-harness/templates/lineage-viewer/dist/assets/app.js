/* phase-lineage-viewer · prebuilt shell · v0.9.40
 *
 * 데이터 우선순위:
 *   1. window.__LINEAGE__   (cold session 이 emit 시 inline 주입)
 *   2. fetch('./lineage.json')  (별도 파일 fallback)
 *
 * 파일 시스템 ($file://) 에서 fetch 가 차단되면 lineage.json 을
 *   <script>window.__LINEAGE__={...}</script>
 * 형태로 index.html 에 inline 주입할 것.
 */
(function () {
  'use strict';

  var THEME_KEY = 'theseus-lineage-theme';
  var POLL_INTERVAL_MS = 5000;
  var root = document.documentElement;

  // ── theme ──────────────────────────────────────────────────────
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* no-op */ }
    // mermaid 재렌더 (theme variable 변경 반영)
    if (window.__lineageRendered__ && window.mermaid) renderMermaid(window.__lineageData__ || {});
  }
  function initTheme() {
    var stored = null;
    try { stored = localStorage.getItem(THEME_KEY); } catch (e) {}
    if (!stored && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      stored = 'dark';
    }
    applyTheme(stored || 'light');
  }
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (t.closest && t.closest('[data-action="toggle-theme"]')) {
      applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    }
    if (t.closest && t.closest('[data-action="manual-refresh"]')) {
      manualRefresh();
    }
  });

  // ── refresh status pill (sprint-36) ────────────────────────────
  var refreshState = {
    mode: 'idle',
    lastEtag: null,
    lastModified: null,
    pollTimer: null,
    fetchInFlight: false,
  };

  function setStatus(state, label) {
    var pill = document.querySelector('[data-bind="refresh_status"]');
    if (pill) {
      pill.setAttribute('data-state', state);
      var t = pill.querySelector('.lv-status-text');
      if (t) t.textContent = label;
    }
    var btn = document.querySelector('.lv-btn-refresh');
    if (btn) btn.setAttribute('data-state', state);
    refreshState.mode = state;
  }

  // ── data load ──────────────────────────────────────────────────
  function loadInline() {
    if (window.__LINEAGE__ && typeof window.__LINEAGE__ === 'object') {
      return Promise.resolve({ data: window.__LINEAGE__, source: 'inline' });
    }
    return Promise.reject(new Error('no inline'));
  }
  function loadHttp() {
    if (typeof fetch !== 'function') return Promise.reject(new Error('no fetch'));
    var headers = {};
    if (refreshState.lastEtag)     headers['If-None-Match']     = refreshState.lastEtag;
    if (refreshState.lastModified) headers['If-Modified-Since'] = refreshState.lastModified;
    return fetch('./lineage.json?_t=' + Date.now(), { cache: 'no-store', headers: headers })
      .then(function (r) {
        if (r.status === 304) return { data: null, source: 'http-304' };
        if (!r.ok) throw new Error('lineage.json fetch failed: ' + r.status);
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
    if (!opts.skipInline && window.__LINEAGE__) return loadInline();
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
          window.__lineageData__ = res.data;
          renderAll(res.data);
          setStatus('live', 'live · updated');
        }
      })
      .catch(function (err) {
        console.warn('[lineage-viewer] poll fail', err && err.message);
        setStatus('offline', 'offline · F5');
      })
      .finally(function () { refreshState.fetchInFlight = false; });
  }
  function manualRefresh() {
    if (refreshState.fetchInFlight) return;
    setStatus('updating', '수동 갱신');
    loadData({ skipInline: true })
      .then(function (res) {
        if (res.data) {
          window.__lineageData__ = res.data;
          renderAll(res.data);
          setStatus(refreshState.pollTimer ? 'live' : 'manual', refreshState.pollTimer ? 'live · manual' : 'manual');
        }
      })
      .catch(function (err) { setStatus('offline', 'fetch 차단 — F5'); });
  }
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && refreshState.pollTimer) pollOnce();
  });

  // ── rendering helpers ──────────────────────────────────────────
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
    var sec = s % 60;
    if (h > 0) return h + 'h ' + (m < 10 ? '0' + m : m) + 'm';
    if (m > 0) return m + 'm ' + (sec < 10 ? '0' + sec : sec) + 's';
    return sec + 's';
  }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === 'className') n.className = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    if (children) for (var i = 0; i < children.length; i++) {
      var c = children[i];
      if (c == null) continue;
      n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return n;
  }

  function renderHeader(d) {
    setText('[data-bind="project_id"]',       d.project_id);
    setText('[data-bind="project_run"]',      d.project_run);
    setText('[data-bind="grade"]',            d.grade);
    setText('[data-bind="started_at_iso"]',   d.started_at_iso);
    setText('[data-bind="ended_at_iso"]',     d.ended_at_iso);
    setText('[data-bind="duration_human"]',   fmtDuration(d.duration_seconds));
    setText('[data-bind="phases_completed"]', typeof d.phases_completed === 'number' ? d.phases_completed : '—');
    setText('[data-bind="dacapo_count"]',     typeof d.dacapo_count    === 'number' ? d.dacapo_count    : '—');
    setText('[data-bind="violations_count"]', typeof d.violations_count === 'number' ? d.violations_count : '—');

    var badge = document.querySelector('[data-bind="final_outcome"]');
    if (badge) {
      var oc = d.final_outcome || '—';
      badge.textContent = oc;
      badge.setAttribute('data-state', oc);
    }
  }

  function renderMermaid(d) {
    var fc = document.querySelector('[data-mermaid-target="flowchart"]');
    var gt = document.querySelector('[data-mermaid-target="gantt"]');
    if (!fc || !gt) return;

    if (d.mermaid_flowchart) {
      fc.classList.remove('lv-mermaid-error');
      fc.removeAttribute('data-processed');
      fc.textContent = d.mermaid_flowchart;
    }
    if (d.mermaid_gantt) {
      gt.classList.remove('lv-mermaid-error');
      gt.removeAttribute('data-processed');
      gt.textContent = d.mermaid_gantt;
    }

    if (!window.mermaid) {
      [fc, gt].forEach(function (n) {
        n.classList.add('lv-mermaid-error');
        n.textContent = 'mermaid.min.js 미로드 — assets/mermaid.min.js 벤더링 필요';
      });
      return;
    }

    try {
      // Linear/Stripe theme — indigo/violet
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
        flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
        gantt:     { useMaxWidth: true, fontSize: 12, gridLineStartPadding: 35 }
      });
      var run = window.mermaid.run || function () { window.mermaid.contentLoaded(); };
      run.call(window.mermaid, { querySelector: '.lv-mermaid-target' });
      window.__lineageRendered__ = true;
    } catch (err) {
      [fc, gt].forEach(function (n) {
        n.classList.add('lv-mermaid-error');
        n.textContent = 'Mermaid 렌더 실패: ' + (err && err.message || err);
      });
    }
  }

  function renderFingerprintChain(rows) {
    var tbody = document.querySelector('[data-table="fingerprint_chain"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 6, className: 'lv-empty', text: '데이터 없음' })]));
      return;
    }
    rows.forEach(function (r, i) {
      var matchCls, matchText;
      if (r.bypass)        { matchCls = 'lv-match-bypass'; matchText = 'bypass'; }
      else if (r.match)    { matchCls = 'lv-match-ok';     matchText = '✓'; }
      else                 { matchCls = 'lv-match-fail';   matchText = '✗'; }
      var phaseCell = el('span', { className: 'lv-phase-cell' }, [
        el('span', { className: 'lv-phase-num', text: r.phase || '—' }),
        el('span', { className: 'lv-phase-name', text: r.name || '—' })
      ]);
      var tr = el('tr', r.bypass ? { className: 'lv-row-bypass' } : null, [
        el('td', { className: 'lv-cell-num', text: String(i + 1) }),
        el('td', null, [phaseCell]),
        el('td', { className: 'lv-cell-mono', text: r.start || '—' }),
        el('td', { className: 'lv-cell-mono', text: r.end || '—' }),
        el('td', { className: 'lv-cell-mono', text: r.fingerprint || '—' }),
        el('td', { className: matchCls, text: matchText })
      ]);
      tbody.appendChild(tr);
    });
  }

  function renderDacapo(rows) {
    var tbody = document.querySelector('[data-table="dacapo"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 7, className: 'lv-empty', text: 'Da Capo 미발생 (정상)' })]));
      return;
    }
    rows.forEach(function (r) {
      // phase: "06 plan" → split into num + name
      var phaseStr = r.phase || '';
      var phaseM = /^(\S+)\s+(.*)$/.exec(phaseStr);
      var phaseCell = phaseM
        ? el('span', { className: 'lv-phase-cell' }, [
            el('span', { className: 'lv-phase-num', text: phaseM[1] }),
            el('span', { className: 'lv-phase-name', text: phaseM[2] })
          ])
        : el('span', { className: 'lv-phase-name', text: phaseStr || '—' });
      var tr = el('tr', null, [
        el('td', null, [phaseCell]),
        el('td', { className: 'lv-cell-num', text: String(r.rerun_count != null ? r.rerun_count : '—') }),
        el('td', { className: 'lv-cell-mono', text: r.final_winner || '—' }),
        el('td', { className: 'lv-cell-num', text: r.final_score != null ? r.final_score.toFixed(3) : '—' }),
        el('td', { className: 'lv-cell-num', text: r.shadow != null ? String(r.shadow) : '—' }),
        el('td', { text: r.outcome || '—' }),
        el('td', { className: 'lv-cell-num', text: r.budget != null ? r.budget.toFixed(2) : '—' })
      ]);
      tbody.appendChild(tr);
    });
  }

  function renderPhase04(rows) {
    var tbody = document.querySelector('[data-table="phase04_answers"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 4, className: 'lv-empty', text: '데이터 없음' })]));
      return;
    }
    rows.forEach(function (r) {
      var tr = el('tr', null, [
        el('td', { className: 'lv-cell-q', text: r.question || '—' }),
        el('td', { text: r.label || '—' }),
        el('td', { text: r.answer || '—' }),
        el('td', { text: r.phase_impact || '—' })
      ]);
      tbody.appendChild(tr);
    });
  }

  function renderSentinel(rows) {
    var tbody = document.querySelector('[data-table="sentinel_events"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!rows || !rows.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 5, className: 'lv-empty', text: '정상 — 0 건' })]));
      return;
    }
    rows.forEach(function (r) {
      var tr = el('tr', null, [
        el('td', { className: 'lv-cell-mono', text: r.time || '—' }),
        el('td', { className: 'lv-cell-mono', text: r.phase || '—' }),
        el('td', { className: 'lv-match-fail', text: r.sentinel || '—' }),
        el('td', { text: r.match || '—' }),
        el('td', { text: r.recovery || '—' })
      ]);
      tbody.appendChild(tr);
    });
  }

  function renderError(message) {
    var main = document.querySelector('.lv-main');
    if (!main) return;
    main.innerHTML = '';
    main.appendChild(el('section', { className: 'lv-section' }, [
      el('header', { className: 'lv-section-head' }, [
        el('h2', { className: 'lv-section-title', text: '데이터 로드 실패' }),
        el('p',  { className: 'lv-section-note', text: message })
      ]),
      el('pre', { className: 'lv-mermaid-target lv-mermaid-error' }, [
        document.createTextNode(
          'window.__LINEAGE__ 가 주입되지 않았고 ./lineage.json 도 로드 실패.\n' +
          'cold session emit 측에서 둘 중 하나를 보장해야 합니다.'
        )
      ])
    ]));
  }

  function renderAll(d) {
    renderHeader(d);
    renderFingerprintChain(d.fingerprint_chain);
    renderDacapo(d.dacapo_summary);
    renderPhase04(d.phase04_answers);
    renderSentinel(d.sentinel_events);
    renderMermaid(d);
  }

  // ── boot ───────────────────────────────────────────────────────
  initTheme();

  loadData()
    .then(function (res) {
      window.__lineageData__ = res.data;
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
      console.error('[lineage-viewer]', err);
      renderError((err && err.message) || String(err));
      setStatus('offline', 'offline');
    });
})();
