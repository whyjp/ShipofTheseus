/* interactive-viewer · prebuilt shell · v0.9.41
 *
 * 데이터 우선순위:
 *   1. window.__DASHBOARD__   (cold session inline 주입)
 *   2. fetch('./dashboard.json')  (별도 파일 fallback)
 *
 * 자동 새로고침 (sprint-36):
 *   - HTTP server 환경 (fetch 가능): polling 5초 + ETag/Last-Modified 비교 → 변경 시 reload
 *   - Page Visibility focus 시 즉시 fetch
 *   - file:// 환경: polling fail → 수동 새로고침 button 강조 + F5 안내
 *
 * Widget 타입:
 *   - kpi_grid       — { items: [{label, value, trend, direction}] }
 *   - topology       — { mermaid: "flowchart ..." }
 *   - metric_chart   — { kind: "bar"|"line", data: [{label, value}] }
 *   - table          — { columns: [...], rows: [[...]] }
 *   - markdown       — { body: "# ..." }
 */
(function () {
  'use strict';

  var THEME_KEY = 'theseus-iv-theme';
  var POLL_INTERVAL_MS = 5000;
  var root = document.documentElement;

  // ── theme ───────────────────────────────────────────────────────
  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* no-op */ }
    if (window.__ivData__) renderAll(window.__ivData__);
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

  // ── refresh status pill ───────────────────────────────────────
  var refreshState = {
    mode: 'idle',           // 'idle'|'live'|'updating'|'offline'|'manual'
    lastUpdate: null,       // ISO string
    lastEtag: null,
    lastModified: null,
    pollTimer: null,
    fetchInFlight: false,
  };

  function setStatus(state, label) {
    var pill = document.querySelector('[data-bind="refresh_status"]');
    if (pill) {
      pill.setAttribute('data-state', state);
      var t = pill.querySelector('.iv-status-text');
      if (t) t.textContent = label;
    }
    var btn = document.querySelector('.iv-btn-refresh');
    if (btn) btn.setAttribute('data-state', state);
    var modeBind = document.querySelector('[data-bind="refresh_mode"]');
    if (modeBind) {
      modeBind.textContent = (
        state === 'live'    ? 'polling 5s' :
        state === 'manual'  ? 'manual only (file://)' :
        state === 'offline' ? 'offline' :
        state === 'updating'? '갱신 중' : '대기'
      );
    }
    refreshState.mode = state;
  }

  function setLastUpdate(d) {
    refreshState.lastUpdate = d ? d.toISOString() : null;
    var el = document.querySelector('[data-bind="last_update"]');
    if (!el) return;
    if (!d) { el.textContent = '—'; return; }
    var hh = String(d.getHours()).padStart(2, '0');
    var mm = String(d.getMinutes()).padStart(2, '0');
    var ss = String(d.getSeconds()).padStart(2, '0');
    el.textContent = hh + ':' + mm + ':' + ss;
  }

  // ── data load ───────────────────────────────────────────────
  function loadInline() {
    if (window.__DASHBOARD__ && typeof window.__DASHBOARD__ === 'object') {
      return Promise.resolve({ data: window.__DASHBOARD__, etag: null, lastMod: null, source: 'inline' });
    }
    return Promise.reject(new Error('no inline'));
  }

  function loadHttp() {
    if (typeof fetch !== 'function') return Promise.reject(new Error('no fetch'));
    var headers = {};
    if (refreshState.lastEtag)     headers['If-None-Match']     = refreshState.lastEtag;
    if (refreshState.lastModified) headers['If-Modified-Since'] = refreshState.lastModified;
    return fetch('./dashboard.json?_t=' + Date.now(), { cache: 'no-store', headers: headers })
      .then(function (r) {
        if (r.status === 304) return { data: null, etag: refreshState.lastEtag, lastMod: refreshState.lastModified, source: 'http-304' };
        if (!r.ok) throw new Error('dashboard.json fetch failed: ' + r.status);
        var et = r.headers.get('ETag');
        var lm = r.headers.get('Last-Modified');
        return r.json().then(function (j) { return { data: j, etag: et, lastMod: lm, source: 'http' }; });
      });
  }

  function loadData(opts) {
    opts = opts || {};
    if (!opts.skipInline && window.__DASHBOARD__) return loadInline();
    return loadHttp();
  }

  // ── polling ─────────────────────────────────────────────────
  function startPolling() {
    if (refreshState.pollTimer) clearInterval(refreshState.pollTimer);
    refreshState.pollTimer = setInterval(function () {
      if (document.hidden) return;        // 탭 보이지 않으면 skip
      pollOnce();
    }, POLL_INTERVAL_MS);
  }

  function pollOnce() {
    if (refreshState.fetchInFlight) return;
    refreshState.fetchInFlight = true;
    setStatus('updating', '갱신 중');
    return loadHttp()
      .then(function (res) {
        if (res.source === 'http-304') {
          setStatus('live', 'live · no change');
          return;
        }
        if (res.data) {
          window.__ivData__ = res.data;
          refreshState.lastEtag = res.etag;
          refreshState.lastModified = res.lastMod;
          setLastUpdate(new Date());
          renderAll(res.data);
          setStatus('live', 'live · updated');
        }
      })
      .catch(function (err) {
        console.warn('[iv] poll fail', err && err.message);
        setStatus('offline', 'offline · F5');
      })
      .finally(function () {
        refreshState.fetchInFlight = false;
      });
  }

  function manualRefresh() {
    if (refreshState.fetchInFlight) return;
    setStatus('updating', '수동 갱신');
    loadData({ skipInline: true })
      .then(function (res) {
        if (res.data) {
          window.__ivData__ = res.data;
          if (res.etag)    refreshState.lastEtag = res.etag;
          if (res.lastMod) refreshState.lastModified = res.lastMod;
          setLastUpdate(new Date());
          renderAll(res.data);
          setStatus(refreshState.pollTimer ? 'live' : 'manual', refreshState.pollTimer ? 'live · manual' : 'manual');
        }
      })
      .catch(function (err) {
        console.warn('[iv] manual fail', err && err.message);
        setStatus('offline', 'fetch 차단 — F5');
      });
  }

  // Page Visibility — focus 시 즉시 fetch
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && refreshState.pollTimer) pollOnce();
  });

  // ── helpers ─────────────────────────────────────────────────
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === 'className') n.className = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else if (k === 'html') n.innerHTML   = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    if (children) for (var i = 0; i < children.length; i++) {
      var c = children[i];
      if (c == null) continue;
      n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    }
    return n;
  }

  function setText(selector, value, fallback) {
    var nodes = document.querySelectorAll(selector);
    var v = (value === null || value === undefined || value === '') ? (fallback || '—') : value;
    for (var i = 0; i < nodes.length; i++) nodes[i].textContent = v;
  }

  function clearTarget(name) {
    var n = document.querySelector('[data-target="' + name + '"]');
    if (n) n.innerHTML = '';
    return n;
  }

  // ── render: header ────────────────────────────────────────
  function renderHeader(d) {
    setText('[data-bind="project_id"]', d.project_id);
    setText('[data-bind="schema_version"]', d.schema_version);
    setText('[data-bind="current_phase"]', d.current_phase != null ? d.current_phase : (d.final_phase != null ? 'final ' + d.final_phase : '—'));
    setText('[data-bind="status"]', d.status || (d.skip ? 'skipped' : '—'));

    var dom = document.querySelector('[data-bind="domain_label"]');
    if (dom) {
      dom.textContent = d.domain_label || d.domain || '도메인 미매칭';
      dom.setAttribute('data-state', d.skip ? 'skip' : (d.matched === false ? 'skip' : 'matched'));
    }
  }

  // ── render: skip banner ───────────────────────────────────
  function renderSkip(d) {
    var sec = document.querySelector('[data-section="skip"]');
    if (!sec) return;
    if (d.skip) {
      sec.hidden = false;
      var note = sec.querySelector('[data-bind="skip_reason"]');
      if (note) note.textContent = d.skip_reason || '도메인 미매칭 — phase 13 skip';
    } else {
      sec.hidden = true;
    }
  }

  // ── render: KPI grid ──────────────────────────────────────
  function renderKpis(items) {
    var target = clearTarget('kpi_grid');
    if (!target) return;
    if (!items || !items.length) {
      target.appendChild(el('div', { className: 'iv-empty', text: '데이터 미주입' }));
      return;
    }
    items.forEach(function (it) {
      var card = el('div', { className: 'iv-kpi-card' }, [
        el('span', { className: 'iv-kpi-label', text: it.label || '—' }),
        el('span', { className: 'iv-kpi-value', text: it.value != null ? String(it.value) : '—' }),
        it.trend ? el('span', {
          className: 'iv-kpi-trend',
          'data-direction': it.direction || '',
          text: it.trend
        }) : null
      ]);
      target.appendChild(card);
    });
  }

  // ── render: widgets (schema-driven) ───────────────────────
  function renderWidgets(widgets) {
    var target = clearTarget('widget_stack');
    if (!target) return;
    if (!widgets || !widgets.length) {
      target.appendChild(el('div', { className: 'iv-empty', text: '데이터 미주입' }));
      return;
    }
    widgets.forEach(function (w, idx) {
      var widgetEl = el('div', { className: 'iv-widget', 'data-widget-id': w.id || ('w' + idx), 'data-widget-type': w.type || 'unknown' }, [
        el('header', { className: 'iv-widget-head' }, [
          el('h3',   { className: 'iv-widget-title', text: w.title || (w.type || 'widget') }),
          el('span', { className: 'iv-widget-type', text: w.type || 'unknown' })
        ]),
        el('div', { className: 'iv-widget-body' })
      ]);
      target.appendChild(widgetEl);
      var body = widgetEl.querySelector('.iv-widget-body');
      try {
        switch (w.type) {
          case 'topology':     renderTopology(body, w); break;
          case 'metric_chart': renderChart(body, w); break;
          case 'table':        renderTable(body, w); break;
          case 'markdown':     renderMarkdown(body, w.body); break;
          default:
            body.appendChild(el('div', { className: 'iv-empty', text: 'unknown widget type: ' + (w.type || '?') }));
        }
      } catch (err) {
        body.appendChild(el('div', { className: 'iv-mermaid-error', text: 'render fail: ' + (err && err.message || err) }));
      }
    });
  }

  function renderTopology(container, w) {
    var pre = el('pre', { className: 'iv-mermaid-target', 'data-mermaid-src': w.mermaid || '' }, [w.mermaid || '']);
    container.appendChild(pre);
    if (!window.mermaid) {
      pre.classList.add('iv-mermaid-error');
      pre.textContent = 'mermaid.min.js 미로드';
      return;
    }
    try {
      var isDark = root.getAttribute('data-theme') === 'dark';
      window.mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        themeVariables: isDark ? {
          background:'#0a0a14', primaryColor:'#1e1b4b', primaryBorderColor:'#818cf8',
          primaryTextColor:'#fafafa', lineColor:'#71717a', textColor:'#fafafa',
          fontFamily:'"Inter Variable","Inter","Pretendard",system-ui,sans-serif'
        } : {
          background:'#fafbff', primaryColor:'#eef2ff', primaryBorderColor:'#4f46e5',
          primaryTextColor:'#09090b', lineColor:'#71717a', textColor:'#09090b',
          fontFamily:'"Inter Variable","Inter","Pretendard",system-ui,sans-serif'
        },
        securityLevel: 'loose',
        flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' }
      });
      var run = window.mermaid.run || function () { window.mermaid.contentLoaded(); };
      run.call(window.mermaid, { nodes: [pre] });
    } catch (err) {
      pre.classList.add('iv-mermaid-error');
      pre.textContent = 'Mermaid 렌더 실패: ' + (err && err.message || err);
    }
  }

  function renderChart(container, w) {
    var data = w.data || [];
    if (!data.length) {
      container.appendChild(el('div', { className: 'iv-empty', text: '데이터 0' }));
      return;
    }
    var kind = w.kind || 'bar';
    var W = 760, H = 300, padX = 56, padY = 36;
    var innerW = W - padX * 2, innerH = H - padY * 2;
    var maxV = Math.max.apply(null, data.map(function (d) { return Number(d.value) || 0; }));
    var minV = Math.min.apply(null, data.map(function (d) { return Number(d.value) || 0; }));
    if (minV > 0) minV = 0;
    var scale = (maxV - minV) || 1;

    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'iv-chart-svg');
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

    // gradient defs
    var defs = document.createElementNS(ns, 'defs');
    defs.innerHTML =
      '<linearGradient id="iv-grad-bar" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0%"  stop-color="#4f46e5"/>' +
        '<stop offset="100%" stop-color="#a855f7"/>' +
      '</linearGradient>' +
      '<linearGradient id="iv-grad-line" x1="0" y1="0" x2="1" y2="0">' +
        '<stop offset="0%"  stop-color="#4f46e5"/>' +
        '<stop offset="100%" stop-color="#a855f7"/>' +
      '</linearGradient>';
    svg.appendChild(defs);

    // grid + axes
    for (var i = 0; i <= 4; i++) {
      var y = padY + (innerH * i) / 4;
      var line = document.createElementNS(ns, 'line');
      line.setAttribute('class', 'iv-chart-grid');
      line.setAttribute('x1', padX); line.setAttribute('x2', W - padX);
      line.setAttribute('y1', y);    line.setAttribute('y2', y);
      svg.appendChild(line);
      var lbl = document.createElementNS(ns, 'text');
      lbl.setAttribute('class', 'iv-chart-y-label');
      lbl.setAttribute('x', padX - 8); lbl.setAttribute('y', y + 4);
      lbl.setAttribute('text-anchor', 'end');
      var v = maxV - ((maxV - minV) * i) / 4;
      lbl.textContent = (Math.round(v * 100) / 100).toString();
      svg.appendChild(lbl);
    }

    if (kind === 'bar') {
      var slot = innerW / data.length;
      var barW = Math.min(48, slot * 0.7);
      data.forEach(function (d, idx) {
        var v = Number(d.value) || 0;
        var x = padX + slot * idx + (slot - barW) / 2;
        var h = ((v - minV) / scale) * innerH;
        var y = H - padY - h;
        var bar = document.createElementNS(ns, 'rect');
        bar.setAttribute('class', 'iv-chart-bar');
        bar.setAttribute('x', x); bar.setAttribute('y', y);
        bar.setAttribute('width', barW); bar.setAttribute('height', Math.max(1, h));
        bar.setAttribute('rx', 4);
        svg.appendChild(bar);

        var vlbl = document.createElementNS(ns, 'text');
        vlbl.setAttribute('class', 'iv-chart-bar-label');
        vlbl.setAttribute('x', padX + slot * idx + slot / 2);
        vlbl.setAttribute('y', y - 6);
        vlbl.textContent = String(d.value);
        svg.appendChild(vlbl);

        var xlbl = document.createElementNS(ns, 'text');
        xlbl.setAttribute('class', 'iv-chart-x-label');
        xlbl.setAttribute('x', padX + slot * idx + slot / 2);
        xlbl.setAttribute('y', H - padY + 18);
        xlbl.setAttribute('text-anchor', 'middle');
        xlbl.textContent = d.label || ('#' + (idx + 1));
        svg.appendChild(xlbl);
      });
    } else if (kind === 'line') {
      var step = data.length > 1 ? innerW / (data.length - 1) : 0;
      var pts = data.map(function (d, idx) {
        var v = Number(d.value) || 0;
        var x = padX + step * idx;
        var y = H - padY - ((v - minV) / scale) * innerH;
        return [x, y, d];
      });
      var path = 'M ' + pts.map(function (p) { return p[0] + ' ' + p[1]; }).join(' L ');
      var pathEl = document.createElementNS(ns, 'path');
      pathEl.setAttribute('class', 'iv-chart-line');
      pathEl.setAttribute('d', path);
      svg.appendChild(pathEl);
      pts.forEach(function (p) {
        var c = document.createElementNS(ns, 'circle');
        c.setAttribute('class', 'iv-chart-point');
        c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', 4);
        svg.appendChild(c);
        var lbl = document.createElementNS(ns, 'text');
        lbl.setAttribute('class', 'iv-chart-x-label');
        lbl.setAttribute('x', p[0]);
        lbl.setAttribute('y', H - padY + 18);
        lbl.setAttribute('text-anchor', 'middle');
        lbl.textContent = p[2].label || '';
        svg.appendChild(lbl);
      });
    }
    container.appendChild(svg);
    if (w.x_label || w.y_label) {
      var meta = el('div', { className: 'iv-chart-meta', style: 'display:flex;gap:18px;margin-top:8px;font-size:11px;color:var(--fg-3);' });
      if (w.x_label) meta.appendChild(el('span', { text: 'x: ' + w.x_label }));
      if (w.y_label) meta.appendChild(el('span', { text: 'y: ' + w.y_label }));
      container.appendChild(meta);
    }
  }

  function renderTable(container, w) {
    var cols = w.columns || [];
    var rows = w.rows || [];
    var table = el('table', { className: 'iv-table' }, [
      el('thead', null, [el('tr', null, cols.map(function (c) { return el('th', { text: String(c) }); }))]),
      el('tbody', null, rows.length === 0
        ? [el('tr', null, [el('td', { colspan: cols.length || 1, className: 'iv-empty', text: '데이터 0' })])]
        : rows.map(function (r) {
            return el('tr', null, r.map(function (cell) {
              return el('td', { text: cell == null ? '—' : String(cell) });
            }));
          })
      )
    ]);
    container.appendChild(table);
  }

  function renderMarkdown(container, body) {
    if (!body) {
      container.appendChild(el('div', { className: 'iv-empty', text: '데이터 미주입' }));
      return;
    }
    if (window.marked && typeof window.marked.parse === 'function') {
      container.innerHTML = window.marked.parse(body);
    } else {
      container.appendChild(el('pre', { text: body }));
    }
  }

  // ── render: scenarios table ──────────────────────────────
  function renderScenarios(scenarios) {
    var tbody = document.querySelector('[data-table="scenarios"] tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!scenarios || !scenarios.length) {
      tbody.appendChild(el('tr', null, [el('td', { colspan: 4, className: 'iv-empty', text: '데이터 미주입' })]));
      return;
    }
    scenarios.forEach(function (s) {
      var tr = el('tr', null, [
        el('td', { text: s.name || '—' }),
        el('td', null, [el('span', { className: 'iv-cell-status', 'data-status': s.status || 'skip', text: s.status || '—' })]),
        el('td', { className: 'iv-cell-num', text: s.key_metric != null ? String(s.key_metric) : '—' }),
        el('td', { text: s.note || '—' })
      ]);
      tbody.appendChild(tr);
    });
  }

  // ── render: artifacts ────────────────────────────────────
  function renderArtifacts(items) {
    var target = clearTarget('artifact_grid');
    if (!target) return;
    if (!items || !items.length) {
      target.appendChild(el('div', { className: 'iv-empty', text: '정적 산출물 없음' }));
      return;
    }
    items.forEach(function (a) {
      var thumb;
      if (a.type === 'image' && a.path) {
        thumb = el('div', { className: 'iv-artifact-thumb' }, [el('img', { src: a.path, alt: a.name || '' })]);
      } else if (a.type === 'html' && a.path) {
        thumb = el('div', { className: 'iv-artifact-thumb' }, [el('iframe', { src: a.path, sandbox: 'allow-scripts' })]);
      } else {
        thumb = el('div', { className: 'iv-artifact-thumb', text: a.type || 'file' });
      }
      target.appendChild(el('div', { className: 'iv-artifact-card' }, [
        thumb,
        el('div', { className: 'iv-artifact-meta' }, [
          el('span', { className: 'iv-artifact-name', text: a.name || a.path || '—' }),
          a.path ? el('span', { className: 'iv-artifact-path', text: a.path }) : null
        ])
      ]));
    });
  }

  // ── render: narrative ───────────────────────────────────
  function renderNarrative(body) {
    var target = document.querySelector('[data-target="narrative_body"]');
    if (!target) return;
    target.innerHTML = '';
    if (!body) {
      target.appendChild(el('div', { className: 'iv-empty', text: '데이터 미주입' }));
      return;
    }
    if (window.marked && typeof window.marked.parse === 'function') {
      target.innerHTML = window.marked.parse(body);
    } else {
      target.appendChild(el('pre', { text: body }));
    }
  }

  // ── orchestrate ─────────────────────────────────────────
  function renderAll(d) {
    renderHeader(d);
    renderSkip(d);
    renderKpis(d.summary_kpis);
    renderWidgets(d.widgets);
    renderScenarios(d.scenarios);
    renderArtifacts(d.raw_artifacts);
    renderNarrative(d.narrative);
  }

  // ── boot ──────────────────────────────────────────────
  initTheme();

  loadData()
    .then(function (res) {
      window.__ivData__ = res.data;
      if (res.etag)    refreshState.lastEtag = res.etag;
      if (res.lastMod) refreshState.lastModified = res.lastMod;
      setLastUpdate(new Date());
      renderAll(res.data);
      if (res.source === 'inline') {
        // inline 주입 시 — fetch 가능하면 polling 시작 (HTTP server 환경)
        if (typeof fetch === 'function' && location.protocol !== 'file:') {
          startPolling();
          setStatus('live', 'live · polling');
        } else {
          setStatus('manual', 'manual only');
        }
      } else {
        startPolling();
        setStatus('live', 'live · polling');
      }
    })
    .catch(function (err) {
      console.error('[iv] boot fail', err);
      var main = document.querySelector('.iv-main');
      if (main) {
        main.innerHTML = '';
        main.appendChild(el('section', { className: 'iv-section' }, [
          el('header', { className: 'iv-section-head' }, [
            el('span', { className: 'iv-section-num', text: '!' }),
            el('div', { className: 'iv-section-text' }, [
              el('h2', { className: 'iv-section-title', text: '데이터 로드 실패' }),
              el('p',  { className: 'iv-section-note', text: (err && err.message) || String(err) })
            ])
          ]),
          el('pre', { className: 'iv-mermaid-target iv-mermaid-error', text:
            'window.__DASHBOARD__ 가 주입되지 않았고 ./dashboard.json 도 fetch 실패.\n' +
            '· file:// 환경: HTML 안에 <script>window.__DASHBOARD__ = {...};</script> inline 주입\n' +
            '· HTTP server: cold session 이 dashboard.json 을 emit 했는지 확인'
          })
        ]));
      }
      setStatus('offline', 'offline');
    });

})();
