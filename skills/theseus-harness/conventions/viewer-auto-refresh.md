---
id: viewer-auto-refresh
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: '3 viewer 공통'
indexed-in: conventions/INDEX.md
---

# Viewer Auto-Refresh — 페이지 자동 갱신 (3 viewer 공통)

## 한 줄 요약

**3 viewer (lineage / webview / interactive) 가 JSON 파일 변경을 자동 감지 + reload.** HTTP server 환경에선 5초 폴링 + ETag/Last-Modified 비교 + Page Visibility focus 시 즉시 fetch. file:// 환경에선 폴링 fail → 수동 새로고침 button 으로 갱신. observability 본질적 상승.

## 1. 동기 — sprint-36 변경

cold session 진행 중 viewer 가 떠 있어도, JSON 갱신이 화면에 반영되지 않으면 *static viewer* 와 다를 바 없다. polling + manual button 으로 사용자가 갱신을 *체감* 하도록.

## 2. 메커니즘

### 2.1 polling (HTTP server 환경)

```javascript
setInterval(function () {
  if (document.hidden) return;     // 탭 숨김 시 skip
  pollOnce();
}, 5000);

function pollOnce() {
  var headers = {};
  if (lastEtag)     headers['If-None-Match']     = lastEtag;
  if (lastModified) headers['If-Modified-Since'] = lastModified;
  fetch('./<viewer>.json?_t=' + Date.now(), { cache: 'no-store', headers: headers })
    .then(function (r) {
      if (r.status === 304) return;   // 변경 없음
      // ... fetch + render
    });
}
```

핵심:
- **ETag / Last-Modified** — 변경 없을 때 304 반환 → 페이로드 0, 자원 효율.
- **`?_t=<ts>`** — 일부 프록시/브라우저 캐시 우회.
- **`document.hidden` 체크** — 백그라운드 탭에서 폴링 안 함.

### 2.2 Page Visibility API

탭 포커스 돌아올 때 즉시 fetch :

```javascript
document.addEventListener('visibilitychange', function () {
  if (!document.hidden && pollTimer) pollOnce();
});
```

5초 polling 보다 *체감 속도* 향상. 탭 전환 직후 화면 = 최신.

### 2.3 manual refresh button

`[data-action="manual-refresh"]` 클릭 → `loadHttp({ skipInline: true })` → 즉시 fetch + render. 폴링 + 수동 둘 다 같은 파이프라인 사용.

### 2.4 status pill UX

3 viewer 모두 헤더에 `data-state` 4 종 :

| state | 표시 | 의미 |
|---|---|---|
| `idle` | 회색 dot | 부팅 직전 |
| `live` | 초록 dot + pulse | polling 활성 |
| `updating` | 파란 dot | 현재 fetch 중 |
| `offline` | 빨간 dot | fetch 실패 → F5 안내 |

manual refresh button 도 동일 state 반영.

## 3. file:// 환경 fallback

브라우저가 `file://` 에서 fetch 차단 (CORS) → polling 자동 fail → status='offline'. 사용자에게 "F5 또는 새로고침 button" 안내. inline 주입 패턴 (`window.__LINEAGE__` 등) 시 *초기* 로드는 inline 데이터, 갱신은 manual.

## 4. 적용 대상

| viewer | data source | binding |
|---|---|---|
| lineage-viewer | `./lineage.json` | `window.__LINEAGE__` |
| webview | `./data/webview.json` | `window.__WEBVIEW__` |
| interactive-viewer | `./dashboard.json` | `window.__DASHBOARD__` |

3 viewer 모두 동일 *폴링 + visibility + manual* 패턴 박힘.

## 5. self_lint C-VAR

```python
def check_viewer_auto_refresh(skill_root: Path) -> list[str]:
    issues = []
    for viewer, app_path in [
        ('lineage-viewer', 'templates/lineage-viewer/dist/assets/app.js'),
        ('webview',        'templates/webview/dist/assets/app.js'),
        ('interactive-viewer', 'templates/interactive-viewer/dist/assets/app.js'),
    ]:
        body = (skill_root / app_path).read_text(encoding='utf-8')
        for kw in ['POLL_INTERVAL_MS', 'pollOnce', 'visibilitychange',
                   'manual-refresh', 'If-None-Match', 'If-Modified-Since']:
            if kw not in body:
                issues.append(f'{viewer}/app.js: \'{kw}\' 키워드 부재')
    return issues
```

## 6. 안티 패턴

a- **fetch 캐시 미off** — `cache: 'no-store'` 누락 시 브라우저가 stale 반환. 의무.
b- **ETag 무시** — 매 폴링마다 풀 페이로드. 304 활용 의무.
c- **document.hidden 체크 누락** — 백그라운드 탭이 자원 잡아먹음.
d- **status pill 부재** — 사용자가 polling 활성 여부 알 수 없음 → "왜 화면이 안 바뀌지?" 의문.
e- **폴링 5초가 너무 빠름/느림** — 5초 = file 변경 감지 + 자원 균형. 단축 시 부하 / 연장 시 체감 저하.

## 7. 호환성

- [`pre-cold-session-bootup.md`](pre-cold-session-bootup.md) — bootstrap 후 빈 골격이 polling 으로 자동 갱신.
- [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) — emit 프로토콜 정합.
- [`viewer-runtime-lifecycle.md`](viewer-runtime-lifecycle.md) — HTTP server 가 polling 의 전제.
