---
name: Sprint-52
sprint_type: feature
version: 0.9.52
---

# Sprint-52 — v0.9.52 — Viewer Finalization Closure

> 시작: 2026-05-10 (g4-sprint51 99/100 회차 직후 viewer 진단 시점, 사용자 직접 지시)
> 사용자 직접 지시 (요지):
> - g4-sprint51 99 점은 별개. 본 하네스 *기능* 으로서 viewer 들의 구성이 미완성.
> - 하네스가 *스스로* 결과를 올바르게 채울 수 있도록 submission 단계에서 누락된 점을 보강.
> - 추가 증상: 일부 0607 페이즈 gantt 시간이 11:00 으로 잘못 기록 — universe candidate frontmatter `created_at` 누락이 원인.

본 sprint = **Viewer Finalization Closure**. cold session 종료 시 lineage.json / webview/data/webview.json / interactive-viewer/dashboard.json 의 placeholder 잔존을 *구조적으로* 차단.

---

## 0. 진단 — *왜* 본 sprint 인가

### 0-1. 사용자가 본 viewer 의 구체 결함 (g4-sprint51 회차)

| Endpoint | 결함 |
|---|---|
| `lineage.html` | `project_run=pending`, `final_outcome=IN_PROGRESS`, `duration_seconds=4.35` (실험 wall-time 만), 모든 `phases[].fingerprint=PENDING`, `fingerprint_chain=[]`, `mermaid_flowchart="cold session 미시작"`, `mermaid_gantt="대기"`, `winner=null` |
| `interactive-viewer/dashboard.json` | `current_phase="pre-bootup"`, `final_phase=null` (산출은 종료) |
| `webview/data/webview.json` | `final_phase=null`, `timing.duration_seconds=4.35`, `timing.phases_completed=43` (값은 살아있으나 timing 필드 stub) |
| 0607 페이즈 gantt | universe candidate (universe-1~4 × {06-plan-candidate, 07-cold-read} = 8 항목) `created_at` 누락 → fallback timestamp `T11:00:00Z` 으로 잘못 표시 |

### 0-2. 결함의 *기저*

`scoring/pre_bootup.py:68-70` 가 cold session 시작 직전 *빈 골격* emit:

```python
"mermaid_flowchart": "flowchart TB\n  Empty[\"cold session 미시작\"]...",
"mermaid_gantt": "gantt\n  title Phase Lineage — pending...",
"fingerprint_chain": [],
```

**누구도 이 stub 을 실 데이터로 *refresh* 하지 않는다**:
- `scoring/fingerprint.py` 는 *개별 .md frontmatter* compute 만 — lineage.json 으로 aggregate 책임 없음
- `phases/14-handoff.md:28` 는 "fingerprint chain 무결성 *최종 검증*" 만 *서술*. 검증 대상인 lineage.json 을 *refresh* 하는 CLI invoke 0
- `phases/06-plan.md` 의 universe candidate 산출 룰 (line 382) 은 frontmatter `created_at` 의무 명시 누락
- `scoring/placeholder_grep.py` 는 lineage.json / dashboard.json / webview.json 을 sentinel target 에 안 넣음 → cold session 종료 후 placeholder 잔존 catch 불가

이 패턴은 sprint-43 의 *declared = invoked* 위반 + sprint-51 의 *Extension Invoke Closure* 가 finalize 단계를 미커버 한 누락. 즉 *기존 인프라* 의 sink 페이즈 wiring 만 빠진 상태.

---

## 1. 본 sprint 의 단일 의도

> **Viewer Finalization Closure** — phase 14 (handoff) 가 lineage / webview / dashboard 의 placeholder 를 실 데이터로 *집결 refresh* 하고, cold session 종료 시 placeholder 잔존이 자동 차단되도록 enforcement layer 4 닫힘.

---

## 2. 7 PR 매핑

### PR-A — sprint-52 plan (본 문서)

frontmatter `sprint_type: feature` + 결함 진단 + PR-B~G 매핑 + 메모리 cross-link.

### PR-B — `lineage_finalize.py` 신규 CLI

`scoring/lineage_finalize.py`:

입력: `--root <project_dir>` (cold session 의 submission root)

동작:
1. `<root>/.ShipofTheseus/` 재귀 스캔 → 모든 `*.md` 의 frontmatter 추출 (`phase`, `created_at`, `fingerprint`, `prev_fingerprint`, file path)
2. `created_at` None / 정시 stub (`T..:00Z`/`T..:00:00Z`) 감지 → 파일 mtime fallback 적용 + WARN 카운트
3. `fingerprint` PENDING 인 파일 → `fingerprint.py compute` 동등 로직으로 chain 재계산 (`prev_fingerprint` 도 동시 재구성)
4. lineage.json 의 다음 키 모두 실 값으로 *refresh*:
   - `project_run`: "completed"
   - `final_outcome`: "DONE"
   - `phases_completed`: 실제 phase 수
   - `phases[]`: fingerprint chain 정합 + created_at 정정
   - `fingerprint_chain[]`: phase 순서대로 dump
   - `mermaid_flowchart`: phase chain (universe candidate fan-out + dacapo branch 표시)
   - `mermaid_gantt`: created_at 기반 시간축 (정시 stub 잔존 시 mtime fallback)
   - `duration_seconds`: ended - started 실 계산
   - `winner`: tournament-NN.md frontmatter 에서 추출 (winner_id / winner_score / philosophy)
5. `<root>/interactive-viewer/dashboard.json` 의 `current_phase` / `final_phase` 정정
6. `<root>/webview/data/webview.json` 의 `final_phase` / `timing.*` 정정

CLI 명령:
```
lineage_finalize.py refresh --root <project_dir> [--dry-run] [--strict]
```

`--strict`: created_at stub / fingerprint PENDING 잔존 시 exit 1.

테스트: `tests/test_lineage_finalize.py` — 빈 골격 + 부분 산출 + 완전 산출 3 fixture.

### PR-C — phase 14-handoff.md 본문에 literal Bash invoke

`phases/14-handoff.md` 에 `## §자동 CLI 호출 (sprint-52, declared=invoked)` 섹션 추가:

```bash
python skills/theseus-harness/scoring/fingerprint.py chain --dir <project>/.ShipofTheseus
python skills/theseus-harness/scoring/lineage_finalize.py refresh --root <project> --strict
python skills/theseus-harness/scoring/placeholder_grep.py \
    --target-root <project> \
    --include-viewer-json \
    --max-violation-count 0
```

sprint-43 `phases/06,08,09,10,14 §자동 CLI 호출` 패턴 따름. orchestrator 가 phase 14 walkthrough 에서 literal Bash 박힌 명령을 그대로 invoke.

### PR-D — phase 06 universe candidate frontmatter 의무 + self_lint

`phases/06-plan.md` 의 universe candidate 산출 룰 (line 382 부근) 에 frontmatter 의무 박기:

```yaml
---
skill_name: shipoftheseus:theseus-orchestrator
skill_version: <semver>
phase: 06-plan-candidate  # 또는 07-cold-read
universe: universe-N
created_at: "<ISO8601 with seconds>"
fingerprint: PENDING  # phase 14 finalize 시 chain 채움
prev_fingerprint: PENDING_FROM_<source>
---
```

self_lint **C-UNIV-CREATED-AT** 신규: `plan/candidates/universe-*/06-plan.md` + `07-cold-read.md` 의 `created_at` 부재 / 정시 stub (`T..:00:00Z`) 감지 → fail.

### PR-E — `placeholder_grep.py` 확장

`scoring/placeholder_grep.py` 에 `--include-viewer-json` 옵션 추가. 옵션 활성 시 다음 sentinel detection:

| 파일 | key path | sentinel 조건 |
|---|---|---|
| `lineage.json` | `project_run` | != "completed" |
| `lineage.json` | `final_outcome` | == "IN_PROGRESS" / "PENDING" |
| `lineage.json` | `winner` | == null |
| `lineage.json` | `fingerprint_chain` | == [] |
| `lineage.json` | `mermaid_flowchart` / `mermaid_gantt` | "미시작" / "pending" / "Empty" 포함 |
| `lineage.json` | `phases[].fingerprint` | == "PENDING" |
| `lineage.json` | `phases[].created_at` | None / "T..:00:00Z" 정시 stub |
| `interactive-viewer/dashboard.json` | `current_phase` | == "pre-bootup" + final_phase != null 일 때 모순 |
| `interactive-viewer/dashboard.json` | `final_phase` | == null + status == "complete" 일 때 모순 |
| `webview/data/webview.json` | `final_phase` | == null |
| `webview/data/webview.json` | `timing.duration_seconds` | == 0 / 매우 작은 값 (< 60s) + phases_completed > 1 모순 |

탈출구는 sprint-51 placeholder_grep 와 동일 (`# placeholder-ok:` 코멘트 / frontmatter ack).

### PR-F — HARD-RULE 9.nnn~9.ppp 신설

`HARD-CORE.md` 에 다음 추가:

- **9.nnn** Phase 14 finalize CLI invoke 의무: phase 14-handoff 진입 시 `lineage_finalize.py refresh --strict` + `fingerprint.py chain` + `placeholder_grep.py --include-viewer-json` 3 종 literal Bash invoke. 어느 하나 exit ≠ 0 = 페이즈 재진입.
- **9.ooo** Universe candidate frontmatter `created_at` 의무: phase 06 universe candidate 산출 시 `created_at` 부재 = self_lint C-UNIV-CREATED-AT fail = 페이즈 재진입.
- **9.ppp** Cold session 종료 시 viewer JSON placeholder 잔존 = orchestrator fail. lineage.json 의 `project_run != completed` / `winner == null` / `fingerprint_chain == []` 잔존 = exit 1.

### PR-G — sprint 마감 v0.9.52

- `skills/theseus-harness/SKILL.md` version → 0.9.52
- `skills/theseus-orchestrator/SKILL.md` version → 0.9.52 (sprint-49 forward only naming policy 정합, 본 sprint 부터 sync)
- `CHANGELOG.md` 항목 추가
- self_lint all_ok 검증
- *증거 산출* — sprint-51 submission (`D:/github/simulation-bench/submissions/2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-sprint51`) 에 `lineage_finalize.py refresh` 호출 → viewer 3 종 정상화 + `.tmp/viewer_patch.py` 단발 patch 의 .bak 백업으로 변경 회복 가능 입증
- 본 sprint 산출물 메모리 갱신 (`project_sprint52_v0952.md`)

---

## 3. 검증 plan

### 3-1. unit test
`tests/test_lineage_finalize.py` (PR-B) — 3 fixture (빈 골격 / 부분 / 완전) + strict mode + dry-run.

### 3-2. integration proof
sprint-51 submission 에 `lineage_finalize.py refresh --root <sub>` 호출 후 viewer 3 종 endpoint 응답 검증:
- lineage.json `project_run == "completed"` + `fingerprint_chain` non-empty + `mermaid_flowchart` 에 "Empty"/"미시작" 부재
- dashboard.json `current_phase == "14-handoff"` + `final_phase == "14-handoff"`
- webview.json `final_phase == "14-handoff"` + `timing.duration_seconds > 60`

### 3-3. self_lint
신규 C-UNIV-CREATED-AT (PR-D) + viewer JSON placeholder 차단 (PR-E) → self_lint all_ok 의무.

---

## 4. 비-목표 (out of scope)

- **점수 회복 추적 금지** — 본 sprint 는 viewer *기능 무결성* 만. 다음 cold session 점수와 무관 (메모리 `feedback_score_targeting_taboo.md` 정합).
- **도메인 의존 fix 금지** — universe candidate frontmatter 룰은 일반 (mining 무관). lineage_finalize 도 도메인 무관 markdown frontmatter parse (메모리 `feedback_harness_strengthening_methodology.md` 정합).
- **신규 컨벤션 추가 0** — 본 sprint 는 *기존 본체 강화* (메모리 `feedback_convention_diet_paradigm.md` 정합). HARD-RULE 3 건 + self_lint 1 건만 신규.
- **점수 시뮬레이션 / external evaluator 호출 금지** — proof 는 viewer endpoint 응답 자체로 충분.

---

## 5. 메모리 cross-link

- `feedback_dual_pressure_json_schema.md` — lineage/webview JSON 의무 키 = 게이트 + viewer source 양쪽 압력. 본 sprint 가 그 닫힘 단계.
- `feedback_hurdle_as_cli_paradigm.md` — 컨벤션 본문 = 명세, CLI = 집행. lineage_finalize.py 가 페어.
- `project_sprint43_v0948.md` — declared=invoked 패턴. 본 sprint 가 finalize 차원 적용.
- `feedback_intent_recursion_paradigm.md` — sprint-51 이 prompt → harness recursion 닫음. 본 sprint 는 산출 → viewer recursion 닫음.
- `project_sprint51_v0951.md` — Extension Invoke Closure. 본 sprint 가 finalize-side closure (대칭).

---

## 6. 진행 상태

PR-A (본 문서) 부터 PR-G 까지 main 머지 후 v0.9.52 release.
