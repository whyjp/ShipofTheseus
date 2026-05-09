---
id: pre-cold-session-bootup
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'phase 00 enter 직전'
indexed-in: conventions/INDEX.md
---

# Pre-Cold-Session Bootup — phase 00 이전 viewer 부팅 + 빈 골격 JSON

## 한 줄 요약

**cold session 시작 *전* 에 lineage / webview / interactive 3 viewer 가 이미 떠 있도록.** orchestrator 가 phase 00 enter 직전 `pre_bootup.py bootstrap` 호출 → 3 viewer dist 복사 + 의무 키 모두 박힌 빈 골격 JSON emit + viewer-runtime HTTP server 시작. 사용자는 cold session 시작과 동시에 viewer 띄워두고 phase 별 진행을 5초 polling 으로 자동 추적. observability 본질적 상승.

## 1. 동기 — sprint-36 변경 + sprint-40 PR-D 강화

**v0.9.40 까지의 문제**:

a- **lineage / webview / interactive viewer 가 cold session *종료 후* 에만 존재** — 진행 중에는 사용자가 볼 곳 없음.
b- **사용자가 phase 12 / 13 종료까지 기다려야** viewer 첫 등장. phase 06 dacapo 진행 중 상태 추적 불가.
c- **viewer 부팅이 cold session 결과 산출에 결합** — 산출 fail 시 viewer 도 fail.

**v0.9.45 (sprint-40 PR-D) 강화**:

d- **HARD-RULE 9.pp — orchestrator 자동 호출 의무**: phase 00 진입 *직전* `python skills/theseus-harness/scoring/pre_bootup.py bootstrap --root <project>` 호출 강제. 미호출 시 phase 09 §V8 viewer-readiness 게이트 fail → phase 00 재실행.
e- **증거 회피 사례** (v0.9.44 g4-v2): pre-bootup 자동 호출 0 → `webview/`, `interactive-viewer/` 디렉터리 통째 부재. 본 9.pp + §V8 게이트 양쪽 압력으로 차단.

**v0.9.46 (sprint-41 PR-F) 강화 — sprint-40 13 산출물 골격 자동 emit**:

f- **`generate_sprint40_artefacts.py` 자동 호출**: pre_bootup.py bootstrap 직후 `python skills/theseus-harness/scoring/generate_sprint40_artefacts.py --project-root <root>` 호출. 13 sprint-40 의무 산출물 (gate_v6/v8/readme_summary/methodology/4 패턴/modeling_shortcuts/cascaded_subq/webview_exit/iv_exit/iv_dashboard) 의 *빈 골격* (`verdict: pending`) 자동 emit.
g- **cold session 의 책임** = phase 진행 중 `verdict: pending` → `verdict: pass` 갱신. cold session 이 *발견* (생성 X) 패러다임 — 본 PR-F 의 핵심 기여.
h- **0510 회차 회피 패턴 직접 차단**: 13 산출물 모두 부재 → `cold_session_artefacts.py` (sprint-41 PR-C) 가 phase 09 진입 차단 → orchestrator 가 PR-F 골격 자동 emit → cold session 이 verdict 갱신 → phase 09 통과.

**v0.9.41 변경**:

a- **phase 00 *이전* 에 viewer 부팅** — cold session 시작과 viewer 부팅 분리.
b- **빈 골격 JSON** — viewer 가 "대기 중" 상태로 떠 있음. phase 진행에 따라 JSON 갱신 → 자동 polling 으로 반영.
c- **lifecycle 명확화** — `pre_bootup.py bootstrap` (시작) ↔ `pre_bootup.py teardown` (종료). PID/port lock file.

## 2. 산출물 — pre-bootup 후 디렉토리 구조

```
.ShipofTheseus/<proj>/
├── lineage.html               # ← templates/lineage-viewer/dist/index.html (rename)
├── lineage.json               # 빈 골격 — phase 진행에 따라 갱신
├── assets/                    # 공유 (mermaid + styles)
├── webview/
│   ├── index.html
│   ├── data/webview.json      # 빈 골격
│   └── assets/
├── interactive-viewer/
│   ├── index.html
│   ├── dashboard.json         # 빈 골격 (skip=false, status="waiting")
│   └── assets/
└── viewer-runtime/
    ├── viewer-up.{sh,ps1}     # 라이프사이클 시작
    ├── viewer-down.{sh,ps1}   # 종료
    ├── viewer.lock.json       # PID/port — viewer-up 시 자동 생성
    └── server.log             # HTTP server 로그
```

## 3. 빈 골격 JSON — emit_fidelity skeleton 모드 통과

각 viewer 의 골격 JSON 은 *의무 키 모두* 박힘 + 값은 null/empty/placeholder. `emit_fidelity.py check --mode skeleton` 통과 의무.

### 3.1 lineage skeleton (필수 키)

- `schema_version` = "0.9.41"
- `project_id`, `project_run` = "pending"
- `started_at_iso` = pre-bootup 시각 (ISO)
- `ended_at_iso` = null
- `phases_completed` = 0
- `final_outcome` = "IN_PROGRESS"
- `mermaid_flowchart` = `flowchart TB\n  Empty["cold session 미시작"]` (코드 펜스 의무)
- `mermaid_gantt` = `gantt\n  title Phase Lineage — pending\n  dateFormat YYYY-MM-DD HH:mm` (코드 펜스 의무)
- `fingerprint_chain`, `dacapo_summary`, `phase04_answers`, `sentinel_events` = `[]`

### 3.2 webview skeleton (8 탭 키 모두)

- `schema_version` = "0.9.41"
- `state.status` = "waiting", `current_phase` = null
- `timing.started_at_iso` = pre-bootup 시각
- `plan`, `intent`, `impl`, `quality`, `tests.unit`, `tests.e2e`, `sprints`, `runtime.prereq`, `runtime.boot_result` = 모두 빈 / null

### 3.3 dashboard skeleton

- `schema_version` = "0.9.41"
- `current_phase` = "pre-bootup", `status` = "waiting"
- `domain` = null, `matched` = false, `skip` = false
- `summary_kpis`, `scenarios`, `widgets`, `raw_artifacts` = `[]`
- `narrative` = "# 대기 중\n\ncold session 이 시작되면 ..."

## 4. orchestrator 호출 시점

```
[orchestrator]
  ↓
pre_bootup.py bootstrap --root <proj> [--port 18080]
  → 3 viewer dist 복사
  → 빈 골격 JSON emit
  → viewer_runtime.py up (HTTP server + lock file)
  ↓
  사용자에게 viewer URL 출력 :
    http://127.0.0.1:18080/lineage.html
    http://127.0.0.1:18080/webview/
    http://127.0.0.1:18080/interactive-viewer/
  ↓
[phase 00 ~ phase 14 진행]
  → 매 phase exit 시 lineage.json / webview.json / dashboard.json 갱신
  → 사용자 viewer 가 5 초 polling 으로 자동 반영
  ↓
[phase 14 핸드오프 완료]
  ↓
pre_bootup.py teardown --root <proj>
  → viewer_runtime down (PID kill + lock 정리)
```

cold session 비정상 종료 시 (Ctrl+C / 시스템 reboot) 도 lock 파일이 남으므로 다음 `bootstrap` 호출 시 stale 감지 + 재시작 가능.

## 5. self_lint C-PCB

```python
def check_pre_cold_session_bootup(skill_root: Path) -> list[str]:
    issues = []
    conv = skill_root / 'conventions' / 'pre-cold-session-bootup.md'
    if not conv.exists():
        return ['pre-cold-session-bootup.md 부재 (sprint-36)']
    cli = skill_root / 'scoring' / 'pre_bootup.py'
    if not cli.exists():
        issues.append('scoring/pre_bootup.py 부재 (sprint-36 신규)')
    body = _read(cli) if cli.exists() else ''
    for fn in ['cmd_bootstrap', 'cmd_teardown', 'cmd_emit_skeleton',
               'lineage_skeleton', 'webview_skeleton', 'interactive_skeleton']:
        if f'def {fn}' not in body:
            issues.append(f'pre_bootup.py 함수 {fn} 부재')
    return issues
```

## 6. 안티 패턴

a- **viewer 부팅을 phase 12 / 13 종료 후로 미룸** — 진행 중 추적 불가능. pre-bootup 의무.
b- **빈 골격에 의무 키 enumeration 안 함** — viewer 가 키 부재 시 `undefined` 처리. 의무 키 모두 박혀야 함.
c- **bootstrap 후 teardown 안 호출** — PID 누수. orchestrator phase 14 종료 시 의무.
d- **빈 골격 JSON 에 dummy filler ("TODO")** — 실제 빈 array / null 만 허용. dummy 박으면 emit_fidelity skeleton 통과해도 *진짜 데이터* 와 구분 안 됨.

## 7. 호환성

- [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) — 본 컨벤션이 phase 00 이전 시점을 추가. emit 프로토콜 정합.
- [`viewer-runtime.md`](viewer-runtime.md) §3 (sprint-37 PR-AC 통합) — bootstrap 의 step 5 = lifecycle up. §2 (frontend) — 빈 골격이 polling 으로 자동 갱신되는 메커니즘.
- [`phase-lineage-viewer.md`](phase-lineage-viewer.md) §15 — emit fidelity 룰. skeleton 모드 추가.
