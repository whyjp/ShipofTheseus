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
    var btn = ev.target.closest && ev.target.closest('[data-action="toggle-theme"]');
    if (!btn) return;
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  });

  // ── data load ──────────────────────────────────────────────────
  function loadData() {
    if (window.__LINEAGE__ && typeof window.__LINEAGE__ === 'object') {
      return Promise.resolve(window.__LINEAGE__);
    }
    if (typeof fetch !== 'function') {
      return Promise.reject(new Error('no fetch + no window.__LINEAGE__'));
    }
    return fetch('./lineage.json', { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) throw new Error('lineage.json fetch failed: ' + r.status);
        return r.json();
      });
  }

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
      window.mermaid.initialize({
        startOnLoad: false,
        theme: root.getAttribute('data-theme') === 'dark' ? 'dark' : 'default',
        securityLevel: 'loose',
        flowchart: { useMaxWidth: true, htmlLabels: true },
        gantt:     { useMaxWidth: true, fontSize: 12 }
      });
      // mermaid 9~11 모두 지원: run 우선, contentLoaded fallback
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
      var tr = el('tr', r.bypass ? { className: 'lv-row-bypass' } : null, [
        el('td', { className: 'lv-cell-num', text: String(i + 1) }),
        el('td', null, [
          el('span', { className: 'lv-mono', text: 'P' + (r.phase || '??') }),
          el('span', { text: ' · ' + (r.name || '—') })
        ]),
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
      var tr = el('tr', null, [
        el('td', null, [el('span', { className: 'lv-mono', text: r.phase || '—' })]),
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
        el('td', null, [el('span', { className: 'lv-mono', text: r.question || '—' })]),
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

  // ── boot ───────────────────────────────────────────────────────
  initTheme();

  loadData()
    .then(function (d) {
      window.__lineageData__ = d;
      renderHeader(d);
      renderFingerprintChain(d.fingerprint_chain);
      renderDacapo(d.dacapo_summary);
      renderPhase04(d.phase04_answers);
      renderSentinel(d.sentinel_events);
      renderMermaid(d);
    })
    .catch(function (err) {
      console.error('[lineage-viewer]', err);
      renderError((err && err.message) || String(err));
    });
})();
