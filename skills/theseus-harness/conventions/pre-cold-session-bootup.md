---
id: pre-cold-session-bootup
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'frozen(advisory) — 옵션 부팅 시'
indexed-in: conventions/INDEX.md
---

# Pre-Cold-Session Bootup — how-to (§8 동결 advisory, B2-F3)

## 한 줄 요약

**cold session 시작 *전* 에 lineage / webview / interactive 3 viewer 를 미리 띄우는 것이 *가능*하다** — 생산 의무는 §8 동결로 해제됐다(편익 미실증). 실시간 관측이 필요하면 phase 00 enter 직전 `pre_bootup.py bootstrap` 호출 *가능*(옵션). 스크립트·템플릿·lifecycle 은 물리 존치.

## 1. 사용법 (옵션)

```
python skills/theseus-harness/scoring/pre_bootup.py bootstrap --root <project> [--port 18080]
  → 3 viewer dist 복사 + 빈 skeleton JSON emit + viewer-runtime HTTP server 시작
  → viewer URL 출력: lineage.html / webview/ / interactive-viewer/
[phase 00 ~ 14 진행 중 — 부팅했다면 5초 polling 으로 자동 갱신 관측 가능]
python skills/theseus-harness/scoring/pre_bootup.py teardown --root <project>
  → viewer_runtime down (PID kill + lock 정리)
```

## 2. skeleton JSON 키 (부팅하는 경우 emit_fidelity 대상, 능력 참조)

`pre_bootup.py`가 `lineage_skeleton`/`webview_skeleton`/`interactive_skeleton` 3 함수로 각 viewer 의 빈 골격을 emit 한다 — 의무 키 모두 채운 null/empty 값(dummy filler 금지):

- lineage skeleton: `project_run="pending"`, `phases_completed=0`, `final_outcome="IN_PROGRESS"`, `mermaid_flowchart`/`mermaid_gantt` 코드펜스, `fingerprint_chain=[]` 등.
- webview skeleton: `state.status="waiting"`, `plan`/`intent`/`impl`/`quality`/`tests.*`/`sprints`/`runtime.*` 모두 빈.
- interactive skeleton (dashboard): `status="waiting"`, `summary_kpis`/`scenarios`/`widgets`=`[]`.

## 3. 조건부 존치 — teardown (진실성/위생, 부팅한 경우)

**부팅했다면** phase 14 종료 시 `pre_bootup.py teardown` 으로 PID/lock 정리 의무 — 이는 생산 의무가 아니라 *만든 것을 어지르지 않을* 위생 규칙(원칙 2). 부팅하지 않은 run 은 해당 없음. 비정상 종료 시 stale lock 은 다음 `bootstrap` 이 감지·정리.

## 4. 안티 패턴 (부팅하는 경우에 한함)

a- 빈 골격에 의무 키 enumeration 누락 — viewer 가 `undefined` 노출.
b- bootstrap 후 teardown 누락 — PID 누수(§3 조건부 의무 위반).
c- 빈 골격에 dummy filler("TODO") — 실제 빈 array/null 만 허용(진실성).

## 5. 재승격 경로 및 호환성

재승격 = `frozen.viewer_mandatory` CheckSpec A/B 실증. 관련: [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) · [`viewer-runtime.md`](viewer-runtime.md) · [`phase-lineage-viewer.md`](phase-lineage-viewer.md).
