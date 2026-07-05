---
id: phase-lineage-viewer
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'phase exit (advisory, §8 동결 — 산출 시)'
indexed-in: conventions/INDEX.md
---

# Phase Lineage Viewer — 프로젝트 전체 페이즈 흐름 + Gantt (how-to, 생산 의무 §8 동결 B2-F3)

## 한 줄 요약

**프로젝트 전체 (페이즈 00 → 14) 흐름을 단일 마크다운 (`.ShipofTheseus/<프로젝트>/lineage.md`) 에 *Mermaid flowchart + Mermaid gantt* 두 view 로 누적 가시화 *가능*(생산 의무는 §8 동결로 해제 — 산출하는 경우의 how-to).** [`dacapo-flow-trace.md`](dacapo-flow-trace.md) (bq) 가 *phase 06 / 08 per-phase* 만 가시화 — 본 컨벤션은 *프로젝트 전체* 페이즈 lineage + universe 분기 + dacapo loop + sentinel 회귀 + 산출물 fingerprint chain + 핸드오프 결정을 한 view 로 통합. 디버깅 시 "이 프로젝트가 어떤 결정의 흐름을 거쳐 최종 산출물에 도달했는지" 한 파일에서 즉시 재구성. **sprint-34 / v0.9.39 — Mermaid `gantt` chart 추가 (timeline view), 산출하는 경우 전 그레이드 권장**. 산출한 경우 거짓 백필/위조 차단은 조건부 존치 — gantt timeline 이 [`phase_state.py`](../scoring/phase_state.py) 의 entered_at/exited_at 직접 시각화.

## 1. bq vs br 책임 분리

| Layer | 컨벤션 | 가시화 범위 | 산출물 |
|---|---|---|---|
| **per-phase** | bq dacapo-flow-trace | phase 06 *또는* 08 의 Step A~G + universe 노드 + dacapo loop | `plan/dacapo-flow.md` + `impl/dacapo-flow.md` |
| **project-wide** (신규) | **br phase-lineage-viewer** | phase 00 → 14 전체 흐름 + 페이즈 간 핸드오프 + dacapo loop 요약 + sentinel 위반 이벤트 | **`lineage.md`** (프로젝트 루트) |

br 는 bq 의 *상위 view* — bq 가 phase 06/08 의 *내부* 다카포 흐름을 자세히, br 은 *모든 페이즈* 의 *외부* 흐름을 압축적으로 보여줌.

## 1.5. Mermaid Gantt — timeline view (sprint-34 / v0.9.39 신규)

flowchart 가 *논리 흐름* 을 보여준다면, gantt 는 *시간 분포* 를 보여준다. 두 view 의 *결합* 으로 (a) 어떤 phase 가 오래 걸렸는지 (b) dacapo loop 가 시간상 어디서 시작/종료됐는지 (c) sentinel 위반이 어느 시점에 발생했는지 즉시 식별. 데이터 source = [`phase_state.py`](../scoring/phase_state.py) 의 `state/phase_state.json` (entered_at/exited_at) — 별도 입력 없음.

```mermaid
gantt
  title Phase Lineage — synthetic_mine_throughput_001
  dateFormat YYYY-MM-DD HH:mm
  axisFormat %H:%M

  section Setup
  P00 naming           :p0, 2026-05-09 13:00, 2m
  P01 intent + 마인드맵 :p1, after p0, 6m

  section Review
  P02 의도 리뷰 :p2, after p1, 3m
  P03 콜드 재이해 :p3, after p2, 3m
  P04 사용자 질의 :p4, after p3, 3m
  P05 비평 :p5, after p4, 4m

  section Plan
  P06 plan-tree :p6, after p5, 7m
  P06 dacapo R1 :crit, dc6_r1, 13:32, 26m
  P06 dacapo R2 :crit, dc6_r2, 13:58, 25m
  P07 plan 재이해 :p7, 14:23, 7m

  section Impl
  P08 impl 5 sub × 7 universe :p8, 14:30, 1h42m
  P08 dacapo R1 (impl) :crit, dc8_r1, 16:12, 1h
  P09 게이트 :p9, 17:12, 8m

  section Sprint
  P10 sprint trinity :p10, 17:20, 1h22m
  P11 회귀 바이섹트 (bypass) :crit, p11, 18:42, 1m

  section Output
  P12 theseus-view :p12, 18:42, 26m
  P13 interactive-viewer :p13, 19:08, 22m
  P14 핸드오프 :milestone, p14, 19:35, 0
```

**의무 항목**:
- `dateFormat` / `axisFormat` 명시 — Mermaid 표준 (시간 축 정합)
- section ≥ 3 (Setup / Plan / Impl 등 — 그레이드 별 활성 phase 그룹)
- 모든 활성 phase 가 노드로 (G1: P01 + P14 만 / G2: P01 + P04 + P06 + P08 + P09 + P14 / G3+: 풀)
- dacapo loop 가 발생한 phase 는 *별도 task* 로 (`crit` 클래스 + dacapo R1/R2 라벨)
- sentinel 위반은 `crit` 클래스 + `★` 라벨 prefix (예: "★ B universe_skip")
- **hotspot 마커 (sprint-35-extra)** — 누적 소요시간이 *동급 phase 중앙값 × 1.5* 초과 시 `★` 라벨 prefix 추가. crit 와 *직교* — Da Capo + hotspot 모두 시 "★ P08 dacapo R1 (hotspot)" 처럼 둘 다 표기.
- **병렬 서브에이전트 (sprint-35-extra)** — phase 08 multiverse / phase 11 회귀 멀티 candidate 처럼 *동시* 다수 task 가 도는 경우, *각 universe 별 row 분해* 의무. 동일 시작 시각으로 정렬되어 시각적 동시성이 보임. 단일 task 로 합쳐 표시 = 병렬성 은폐로 fail.
- bypass phase = 일반 task (no class) 또는 `:done` (gray). `:crit` 사용 금지 — bypass 는 정상 lineage.
- phase 14 = `milestone` task (0 분 길이)
- 시각 = phase_state.json 의 entered_at (start) + duration_seconds → end (자동 산출)

**자동 갱신** — `update_phase_lineage(event='exit', ...)` 호출 시 gantt block 도 함께 갱신. 수동 편집 금지.

### 1.5.a 색상 의미 표 (legend)

| 표시 | 의미 | 트리거 |
|---|---|---|
| 일반 (default fill) | 정상 phase 진행 | 첫 실행 통과, sentinel 0 |
| **빨강 `:crit`** | Da Capo rerun · sentinel 위반 | winner 임계 미달 → 폴리싱 / 또는 universe_skip / log pattern / forgery 감지 |
| **★ 라벨 prefix** | hotspot — 시간 1.5× 초과 또는 sentinel 박힘 | task 라벨 본문에 `★` 접두 |
| **dashed (no fill)** | bypass | 회귀 미발생으로 phase 11 skip 등 |
| **milestone (0 분)** | phase 14 핸드오프 | `:milestone` 클래스 |

view 가독성: 빨강 + ★ 두 신호로 *어디 시간 많이 썼는지* + *어디 무결성 깨졌는지* 가 즉시 식별. 병렬 서브에이전트는 *동일 start 의 다수 row* 로 시각적 동시성 표현.

## 2. lineage.md 구조

```markdown
---
skill_name: theseus-harness
skill_version: 0.9.22
phase: project-lineage
project_id: <proj>
project_run: <run>
fingerprint: sha256:<...>
prev_fingerprint: null                       # 프로젝트 루트 산출물 (체인 시작)
produced_at: <ISO>
producer_agent: orchestrator
last_updated_at: <ISO>
total_phases_completed: 9                    # 진행된 페이즈 갯수
final_phase: 14                              # 최종 도달 페이즈
total_violations: 0                          # 누적 sentinel 위반
total_dacapo_reruns: 2                       # phase 06+08 누적 dacapo 횟수
final_outcome: HANDOFF | IN_PROGRESS | BUDGET_BOUND
---

# Project Lineage Viewer

> 프로젝트: <project_id>
> 시작: <ISO> · 종료: <ISO> · 총 소요: <시간>
> 최종 outcome: **HANDOFF** (페이즈 14 완료, winner=universe-3, score=0.967)

## 1. 한눈 lineage 다이어그램

```mermaid
flowchart TB
  classDef done fill:#c8e6c9,stroke:#2e7d32
  classDef bypass fill:#e0e0e0,stroke:#757575,stroke-dasharray: 5 5
  classDef sentinel fill:#fff59d,stroke:#f57f17
  classDef dacapo fill:#bbdefb,stroke:#1565c0
  classDef budget fill:#ffe0b2,stroke:#ef6c00

  P00["Phase 00 — naming<br/>2026-05-05 13:00"]:::done
  P00 --> P01["Phase 01 — intent + 마인드맵<br/>13:02 · grade=G4"]:::done
  P01 --> P02["Phase 02 — 의도 리뷰<br/>13:08"]:::done
  P02 --> P03["Phase 03 — 콜드 재이해<br/>13:11 · 4 답변 일치"]:::done
  P03 --> P04["Phase 04 — 사용자 질의<br/>13:14 · Q-G1=G4 / Q-D1~D9 사전답안"]:::done
  P04 --> P05["Phase 05 — 비평<br/>13:18 · simplification 표 6 row"]:::done
  P05 --> P06["Phase 06 — plan-tree<br/>13:25 · width=7"]:::dacapo

  subgraph DC06 ["Phase 06 Da Capo Loop"]
    direction LR
    R0["Rerun 00<br/>winner=U3 0.892"]:::dacapo
    R1["Rerun 01<br/>winner=U-anon-r1-a 0.945"]:::dacapo
    R2["Rerun 02<br/>winner=U-anon-r2-a 0.967 ✓"]:::done
    R0 -->|"lesson: ae interface"| R1
    R1 -->|"lesson: bi measurement"| R2
  end

  P06 --> DC06
  DC06 --> P07["Phase 07 — plan 재이해<br/>14:23 · accept"]:::done
  P07 --> P08["Phase 08 — impl 5 sub × 7 universe<br/>14:30"]:::dacapo

  subgraph DC08 ["Phase 08 Da Capo Loop"]
    R0_8["Rerun 00<br/>winner=U3-impl 0.93"]:::dacapo
    R1_8["Rerun 01<br/>winner=U-anon-impl 0.97 ✓"]:::done
    R0_8 -->|"lesson: DIP refactor"| R1_8
  end

  P08 --> DC08
  DC08 --> P09["Phase 09 — 게이트 9<br/>17:12 · proceed"]:::done
  P09 --> P10["Phase 10 — sprint trinity<br/>17:20 · 6 sprint × 3 axis"]:::done
  P10 --> P11["Phase 11 — 회귀 바이섹트<br/>미발생"]:::bypass
  P11 --> P12["Phase 12 — theseus-view<br/>18:42"]:::done
  P12 --> P13["Phase 13 — interactive-viewer<br/>19:08"]:::done
  P13 --> P14["Phase 14 — 핸드오프<br/>19:35 · winner promote"]:::done

  P14 --> Done(["HANDOFF<br/>19:35 · 6h 35m 총 소요"])
```

## 2. 페이즈별 진입/종료 시각 + 핸드오프 fingerprint

| # | 페이즈 | 시작 | 종료 | 산출 fingerprint | 다음 페이즈 prev_fingerprint | 일치 |
|:-:|---|---|---|---|---|:-:|
| 00 | naming | 13:00 | 13:02 | sha256:7a9c... | sha256:7a9c... (01 prev) | ✓ |
| 01 | intent | 13:02 | 13:08 | sha256:1f2e... | sha256:1f2e... (02 prev) | ✓ |
| 02 | doc-review | 13:08 | 13:11 | sha256:8d3b... | sha256:8d3b... (03 prev) | ✓ |
| ... | ... | ... | ... | ... | ... | ... |
| 06 | plan-tree | 13:25 | 14:23 | sha256:c4f8... (rerun 02 winner) | sha256:c4f8... (07 prev) | ✓ |
| 07 | plan-recursion | 14:23 | 14:30 | sha256:5b21... | sha256:5b21... (08 prev) | ✓ |
| 08 | implement | 14:30 | 17:12 | sha256:9e74... (impl rerun 01) | sha256:9e74... (09 prev) | ✓ |
| ... | ... | ... | ... | ... | ... | ... |
| 14 | handoff | 19:30 | 19:35 | sha256:f8a2... | (체인 종료) | — |

체인 무결성 = 모든 행 ✓ 의무. 하나라도 mismatch 면 sentinel ★ 노드 추가 + intent/00-violation.md 기록.

## 3. Da Capo loop 요약 (per-phase 상세는 bq dacapo-flow.md 참조)

| Phase | rerun count | final winner | final score | shadow | outcome | budget |
|:-:|:-:|---|:-:|:-:|---|:-:|
| 06 plan | 2 | universe-anon-r2-a | 0.967 | 96 | CONVERGED (partial — shadow PASS) | 0.89 |
| 08 impl | 1 | universe-anon-impl | 0.97 | 95 | CONVERGED | 0.78 |

drill-down :
- Phase 06 다카포 자세히 → [`plan/dacapo-flow.md`](plan/dacapo-flow.md)
- Phase 08 다카포 자세히 → [`impl/dacapo-flow.md`](impl/dacapo-flow.md)

## 4. Sentinel 위반 이벤트 (해당 시 추가)

> 본 프로젝트 sentinel 0회 위반. 정상 lineage.

위반 발생 시 row 추가 :

| 시각 | 페이즈 | sentinel | 매치 | 회귀 |
|---|:-:|---|---|---|
| (예시) 13:42 | 06 | B universe_skip | width=7, candidates=3 | phase 06 Step A 재진입 |
| (예시) 14:08 | 06 | C log pattern | "Winner clear → phase 07" | phase 06 Step A 재진입 |

## 5. 페이즈 04 사용자 답안 매핑 (autonomy 정합)

| Q | 답 | 페이즈 영향 |
|---|---|---|
| Q-G1 grade | G4 | 모든 페이즈 활성 |
| Q-D1 stack | Python (default) | 페이즈 04-stack |
| Q-D2 budget | 80% | 페이즈 10 sprint cap |
| Q-D3 resources | 로컬 | 페이즈 04-runtime-prereq |
| Q-D7 checkpoints | 모든 phase | 페이즈 06/08 dacapo + sprint |
| Q-D8 verification | pytest + invariants | 페이즈 09 게이트 |
| Q-D9 runtime-prereq | OK | 페이즈 04-verification |
| Q-D-AUDIENCE | external-reviewer | 페이즈 08 docstring density |

페이즈 05~14 자율 결정은 `intent/04-autonomy.md` 박힘. 본 표는 사후 lineage 회수용.

## 6. orchestrator 자동 갱신 인터페이스

```python
def update_phase_lineage(
    project_dir: Path,
    phase: int,
    event: str,                   # 'enter' | 'exit' | 'dacapo_loop' | 'sentinel' | 'handoff'
    details: dict,
):
    """매 페이즈 진입/종료 시점에 호출 — lineage.md 누적 갱신."""

    lineage_md = project_dir / 'lineage.md'

    # 1. timeline 행 추가
    if event == 'enter':
        append_phase_row(lineage_md, phase, start_time=now_iso())
    elif event == 'exit':
        update_phase_row(lineage_md, phase,
                         end_time=now_iso(),
                         fingerprint=details['fingerprint'],
                         outcome=details['outcome'])
        verify_fingerprint_chain(lineage_md, phase)   # mismatch → sentinel

    # 2. Mermaid 다이어그램 갱신
    if event == 'enter':
        append_mermaid_phase_node(lineage_md, phase)
    elif event == 'dacapo_loop':
        append_mermaid_dacapo_subgraph(lineage_md, phase, **details)
    elif event == 'sentinel':
        append_mermaid_sentinel_node(lineage_md, **details)
    elif event == 'handoff':
        append_mermaid_done_node(lineage_md, **details)

    # 3. frontmatter 갱신
    update_frontmatter(lineage_md, {
        'last_updated_at': now_iso(),
        'total_phases_completed': count_completed_phases(lineage_md),
        'final_phase': phase if event == 'exit' else fm.get('final_phase'),
        'total_violations': count_violations(project_dir),
        'total_dacapo_reruns': sum_dacapo_reruns(project_dir),
        'final_outcome': details.get('final_outcome', 'IN_PROGRESS'),
    })

    # 4. fingerprint 재계산
    recompute_fingerprint(lineage_md)
```

매 페이즈 진입/종료 + dacapo loop 진행 + sentinel 매치 + 핸드오프 시점에 호출. 수동 편집 금지.

## 7. lineage.md 무결성 검증 함수 (참고 구현)

```python
def check_phase_lineage_viewer(artifact_dir: Path) -> list[str]:
    """프로젝트 종료 시 lineage.md 무결성."""
    errors = []
    lineage = artifact_dir / 'lineage.md'

    # 의무 산출 (G3+)
    if not lineage.exists():
        errors.append('lineage.md 부재 (br v0.9.22 의무)')
        return errors

    text = lineage.read_text(encoding='utf-8')
    fm = parse_frontmatter(lineage)

    # mermaid flowchart ≥ 1 의무
    if '```mermaid' not in text or 'flowchart' not in text:
        errors.append('lineage.md mermaid flowchart 부재')

    # mermaid gantt ≥ 1 의무 (sprint-34 / v0.9.39 신규 — 모든 그레이드)
    if 'gantt' not in text or 'dateFormat' not in text:
        errors.append('lineage.md mermaid gantt + dateFormat 부재 (sprint-34 / v0.9.39 의무)')

    # phase 노드 의무 — 그레이드 별 minimal set (sprint-34 / v0.9.39)
    grade = (fm.get('grade') or 'G4').upper()
    required_phases = {
        'G1': [1, 14],
        'G2': [1, 4, 6, 8, 9, 14],
    }.get(grade, list(range(0, 15)))   # G3+ 풀
    for p in required_phases:
        if f'P{p:02d}' not in text and f'Phase {p:02d}' not in text:
            # bypass (회귀 미발생) 도 표시 의무 — bypass 노드
            errors.append(f'lineage.md Phase {p:02d} 노드 부재 (grade={grade} 필수)')

    # fingerprint chain 의무 — 표에 모든 페이즈 행
    if '| # | 페이즈 |' not in text:
        errors.append('lineage.md fingerprint chain 표 부재')

    # 페이즈 04 답안 매핑 표 의무 (autonomy 정합 lineage 회수)
    if 'Q-G1' not in text or 'Q-D1' not in text:
        errors.append('lineage.md 페이즈 04 답안 매핑 표 부재')

    # final_outcome ∈ {HANDOFF, IN_PROGRESS, BUDGET_BOUND}
    if fm.get('final_outcome') not in ['HANDOFF', 'IN_PROGRESS', 'BUDGET_BOUND']:
        errors.append('lineage.md final_outcome 값 invalid')

    # bq dacapo-flow.md 와 cross-link
    if 'plan/dacapo-flow.md' not in text and (artifact_dir / 'plan/dacapo-flow.md').exists():
        errors.append('lineage.md 가 plan/dacapo-flow.md cross-link 부재')

    return errors
```

## 8. 사람 사용 예 — 디버깅 시나리오

> "이 프로젝트 phase 09 에서 왜 proceed 결정이 났나?"

`lineage.md` 한 파일 열어 :

1. Mermaid 다이어그램 → P09 노드 (게이트 9 · proceed) 강조
2. fingerprint chain 표 → P09 행의 sha256 + P10 prev_fingerprint 일치 확인
3. (필요 시 drill-down) → `quality/09-quality-gate.md` 직접 확인

> "phase 06 의 winner 가 0.967 인데 왜 0.999 미달에도 promote 됐나?"

1. Mermaid → DC06 subgraph 확인 → R2 (Rerun 02) 우승 + ✓ 표시
2. Da Capo 요약 표 → Phase 06 outcome=CONVERGED (partial — shadow PASS), budget=0.89
3. drill-down → [`plan/dacapo-flow.md`](plan/dacapo-flow.md) 의 timeline `step=D event=check pass=PARTIAL_PASS`

→ 프로젝트 전체 흐름 + per-phase 다카포 흐름 두 layer 동시 사용.

## 9. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- phase 0~14 표 + Mermaid 노드 = 일반 라이프사이클 가시화, 도메인 X.
b- fingerprint chain = contracts.md 의 일반 무결성 검증, 도메인 X.
c- Da Capo 요약 표 = bq 의 final 결과 누적, 도메인 X.

## 10. 안티 패턴

a- **lineage.md 가 *개별 산출물 링크 모음만***  — Mermaid 다이어그램 부재. 흐름 재구성 불가. flowchart ≥ 1 의무.
b- **bypass 페이즈 누락** — 회귀 미발생으로 phase 11 skip → bypass 노드도 의무 (bypass 클래스 + dashed 엣지).
c- **fingerprint chain 표 mismatch 무시** — sentinel ★ 노드 추가 안 함 → 무결성 우회. 본 컨벤션 §7 강제.
d- **dacapo flow 와 lineage 의 cross-link 부재** — drill-down 불가능. plan/dacapo-flow.md cross-link 의무.
e- **수동 편집** — 사람이 손으로 행 추가 → orchestrator 자동 갱신과 drift. fingerprint mismatch 로 검출.
f- **Mermaid 노드 라벨에 unquoted parens** (sprint-35 v0.9.40 회귀 정정) — `[Phase 11 — 회귀 바이섹트<br/>(미발생)]` 형태는 Mermaid 가 `(` 를 stadium shape 으로 오해, parse error. **노드 라벨에 parens / `=` / 한글 + 특수문자 혼용 시 반드시 `["..."]` 인용 의무**. 예: `P11["Phase 11 — 회귀 바이섹트<br/>미발생"]:::bypass`. subgraph / edge 라벨 / Done(\[...\]) stadium 도 동일.

## 11. 호환성

- [`dacapo-flow-trace.md`](dacapo-flow-trace.md) (bq) — per-phase 가시화. 본 컨벤션 = 그 상위 project-wide view.
- [`contracts.md`](contracts.md) — fingerprint chain 무결성 룰 = 본 lineage 의 검증 입력.
- [`indexing.md`](indexing.md) — INDEX.md 가 lineage.md 를 별도 섹션 ("Project Lineage") 로 노출.
- [`autonomy.md`](autonomy.md) — 페이즈 04 답안 매핑 표가 본 lineage 의 §5 로 흡수, 자율 결정 사후 회수 정합.
- [`dacapo-skip-sentinel.md`](dacapo-skip-sentinel.md) (bp) — sentinel 매치 시 lineage.md §4 행 + Mermaid ★ 노드 동시 추가.
- [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) — `lineage.html` + `lineage.json` 이중 emit 프로토콜. 본 컨벤션 §14 가 trigger 매핑.

## 12. 그레이드 활성 (sprint-34 / v0.9.39 — 모든 그레이드 의무)

| Grade | flowchart | gantt | fingerprint chain | dacapo summary | sentinel events | phase 04 답안 매핑 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| **G1** Trivial | ✅ minimal (P01 + P14 만) | ✅ minimal | ✅ (2 행) | n/a (dacapo 없음) | optional | optional |
| **G2** Simple | ✅ (P01 + P04 + P06 + P08 + P09 + P14) | ✅ | ✅ (6 행) | n/a | optional | ✅ |
| **G3** Standard | ✅ (P00~P14 전체) | ✅ | ✅ (15 행) | ✅ | ✅ | ✅ |
| **G4** Complex | G3 + universe 분기 노드 + dacapo R1/R2 | ✅ + critical task | ✅ + universe fingerprint | ✅ | ✅ | ✅ |
| **G5** Critical | G4 + 빡빡 (fingerprint mismatch 0 / sentinel 위반 ≥ 1 시 즉시 ack) | ✅ + sentinel critical | ✅ | ✅ | 0 의무 | ✅ |

**왜 G1/G2 도 의무인가** (sprint-34 변경 동기) :
- v0.9.22 사고 — 백필/위조는 *간단한 프로젝트* 일수록 발견 안 됨 (lineage 비교 없으니까)
- gantt timeline 이 [`phase_state.py`](../scoring/phase_state.py) 의 entered_at/exited_at 직접 시각화 → 수동 frontmatter 위조 시 즉시 detect
- 모든 그레이드에서 동일 운영 — 하네스 일관성

minimal 모드 (G1/G2) 는 *flowchart + gantt + fingerprint chain 표 + 페이즈 04 답안 매핑* 만, dacapo summary / sentinel events 는 phase 06/08 활성 시 (G2+) 자동 추가.

## 13. 페이즈별 갱신 트리거 — phase 00 → phase 14 매핑

| Phase | 트리거 시점 | 갱신 대상 |
|:-:|---|---|
| phase 00 (naming) | 종료 | P00 노드 + fingerprint chain 첫 행 |
| phase 01 (intent) | 종료 | P01 노드 + grade frontmatter 박음 |
| phase 02 (doc-review) | 종료 | P02 노드 |
| phase 03 (cold-comprehension) | 종료 | P03 노드 + cold-read diff 결과 박음 |
| phase 04 (clarify) | 종료 | P04 노드 + 페이즈 04 답안 매핑 표 §5 갱신 |
| phase 05 (critique) | 종료 | P05 노드 |
| phase 06 (plan-tree) | dacapo loop 진행 / 종료 | DC06 subgraph + Da Capo 요약 표 §3 행 |
| phase 07 (plan-recursion) | 종료 | P07 노드 |
| phase 08 (implement) | dacapo loop 진행 / 종료 | DC08 subgraph + Da Capo 요약 표 §3 행 |
| phase 09 (gates) | 종료 | P09 노드 + gate proceed/halt outcome |
| phase 10 (sprint) | 매 sprint + 종료 | P10 노드 + sprint trinity outcome |
| phase 11 (regression-bisect) | bypass 또는 진행 | P11 노드 (bypass 시 dashed 엣지) |
| phase 12 (theseus-view) | 종료 | P12 노드 |
| phase 13 (interactive-viewer) | 종료 | P13 노드 |
| **phase 14** (handoff) | 종료 | P14 노드 + final_outcome=HANDOFF + lineage.md 최종 fingerprint chain 무결성 검증 |

phase 14 핸드오프 시점에 본 lineage.md 가 *최종 산출물의 일부* — handoff/14-handoff.md 본문에 cross-link 의무.

## 14. HTML viewer 동시 emit (sprint-35 / v0.9.40 신규)

`lineage.md` (마크다운, 누적 갱신) 와 함께 **standalone HTML viewer 도 동시 emit** 의무 (G3+, G1/G2 옵션). markdown viewer 의존 없이 즉시 디버깅 가능.

### 14.1 산출물

```
.ShipofTheseus/<proj>/
├── lineage.md          # 기존 — 마크다운 (Mermaid flowchart + gantt + 표)
├── lineage.html        # 신규 — standalone HTML viewer (prebuilt shell 복사)
├── lineage.json        # 신규 — viewer 가 fetch (또는 inline 주입 시 생략 가능)
└── assets/             # shell 의존 파일 (mermaid.min.js + styles.css + app.js)
    ├── styles.css
    ├── app.js
    └── mermaid.min.js
```

### 14.2 emit 흐름 (orchestrator 자동, 수동 편집 금지)

매 phase exit 시 [`§6 update_phase_lineage`](#6-orchestrator-자동-갱신-인터페이스) 호출 *직후* :

a- `lineage.md` 가 누적 갱신된 그 데이터를 JSON 으로 직렬화 — `mermaid_flowchart` / `mermaid_gantt` 는 마크다운에 박힌 Mermaid 코드 펜스 본문 그대로, `fingerprint_chain` / `dacapo_summary` / `phase04_answers` / `sentinel_events` 는 표 → JSON list 변환.
b- 초회 호출 시 `templates/lineage-viewer/dist/*` 를 `<project>/` 로 복사 (`index.html` → `lineage.html` rename).
c- inline 주입 패턴 채택 시 `lineage.html` 의 `<script src="./assets/app.js">` 직전에 `<script>window.__LINEAGE__ = <JSON>;</script>` 박아 갱신. fetch 패턴 채택 시 `lineage.json` 갱신.

스키마 + 패턴 A/B 상세는 [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) §3.1.

### 14.3 lineage.html 검증 확장

§7 의 기존 검증 함수에 다음 항목 추가 :

```python
# G3+ 의무 (sprint-35 / v0.9.40)
grade = (fm.get('grade') or 'G4').upper()
if grade in ('G3', 'G4', 'G5'):
    lineage_html = artifact_dir / 'lineage.html'
    if not lineage_html.exists():
        errors.append('lineage.html 부재 (sprint-35 / v0.9.40 의무, G3+)')
    else:
        text = lineage_html.read_text(encoding='utf-8')
        has_inline = 'window.__LINEAGE__' in text
        has_json   = (artifact_dir / 'lineage.json').exists()
        if not (has_inline or has_json):
            errors.append('lineage.html 데이터 채널 부재 (window.__LINEAGE__ inline 또는 lineage.json fetch 중 하나 필수)')
```

C-PSR (prebuilt-shell-runtime-json) 와 cross-validate — 두 룰이 같은 결함을 양쪽에서 검출.

### 14.4 G1/G2 옵션

G1 / G2 (의무 산출 수가 적은 그레이드) 는 `lineage.html` 옵션. `lineage.md` 단일이어도 통과 — 단 contributor 가 직접 viewer 를 띄우려면 [`templates/lineage-viewer/dist/`](../templates/lineage-viewer/dist/) shell 을 수동 복사 + JSON 주입 가능.

## 15. emit fidelity — 채워야 비로소 게이트 통과 (sprint-35-extra)

§14 가 `lineage.html` + `lineage.json` *생성* 만 다뤘다면, 본 §15 는 *완전성* 의 게이트. 빈 list / null / dummy filler 박아두면 (a) `emit_fidelity.py check` fail (b) viewer 가 빈 화면 — *이중 압력* 으로 cold session 이 키를 채우도록 강제.

### 15.1 의무 키 (cold session 이 채워야 진행 가능)

[`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) §3.3 의 enumeration 그대로. 본 컨벤션이 *어디서 가져오는지* 매핑 :

| 키 | 출처 phase / 산출물 | 빈값 시 |
|---|---|---|
| `mermaid_flowchart` | 본 컨벤션 §1 의 lineage.md flowchart 코드 펜스 | G4+ subgraph ≥ 2 의무 (multiverse + dacapo) |
| `mermaid_gantt` | §1.5 gantt 코드 펜스 | G4+ ★ ≥ 1 (hotspot) + 동일 start row ≥ 3 (parallel) 의무 |
| `fingerprint_chain` | scoring/phase_state.py 의 entered_at/fingerprint | 길이 = phases_completed |
| `dacapo_summary` | §3 표 → JSON list 변환 | dacapo 발생 phase 별 1 row |
| `phase04_answers` | intent/04-questions.md + 04-autonomy.md | Q-G1 + Q-D1~D9 |
| `sentinel_events` | dacapo-skip-sentinel + log pattern + forgery 감지 | 0 건 시 `[]` 허용 |
| `winner` | phase 06/08 final winner | dacapo 발생 시 의무 |

### 15.2 sprint-35-extra 룰 (gantt 본문)

§1.5 의 hotspot ★ / parallel rows / bypass `:done` 룰을 본 §15 가 **runnable 게이트** 로 승격. `emit_fidelity.py check --root <proj>` 가 :

a- `★` 마커 0 → G4+ 시 fail (hotspot 표기 누락)
b- 동일 start 시각의 task 가 < 3 → G4+ 시 fail (병렬 sub-agent 은폐)
c- bypass 행에 `:crit` 사용 → fail (정상 lineage 인데 빨강으로 표시)
d- multiverse subgraph 부재 (flowchart `subgraph` < 2) → G4+ 시 fail

### 15.3 dummy filler 금지

빈 배열 + null 은 *그 키가 정말 비어있을 때* (sentinel_events 0 건 등) 만 허용. 진짜 채워야 할 자리에 `"데이터 미주입"` / `"TODO"` / `"-"` / `"FIXME"` 박는 것 fail. shell 측이 *키 부재 시* fallback 으로 표시하는 건 OK — 하지만 *키가 있으면서 dummy 값* 은 fail.

### 15.4 호출 시점

```
# phase 12 exit / phase 14 진입 시 orchestrator 가 자동 호출
python skills/theseus-harness/scoring/emit_fidelity.py check --root .ShipofTheseus/<proj>

# 디버깅 — 모든 키 fill 상태 JSON 덤프
python skills/theseus-harness/scoring/emit_fidelity.py report --root .ShipofTheseus/<proj>
```

cold session 이 본 게이트 fail 하면 phase exit 차단 — emit step 다시 (sentinel: emit_incomplete).

### 15.5 안티 패턴

a- **의무 키 enumeration 만 박고 *값* 안 채움** — 빈 list/null 배열로 schema-conform 만 시킴. `emit_fidelity.py` 가 fill 검증.
b- **dummy filler 로 임시 통과** — `"TODO"` 박고 다음 phase 로 진행. fail.
c- **gantt 에서 multiverse 를 단일 row 로 압축** — phase 08 의 7 universe 를 "P08 impl 7 universe ∥, 102m" 하나로 표시. 병렬성 은폐로 fail. universe 별 row 분해 의무.
d- **bypass phase 를 `:crit` 으로 표기** — 회귀 미발생인데 빨강. lineage 의미 왜곡, `:done` 사용.

## 16. 호환 — emit_fidelity CLI 와 self_lint 매핑

| 검증 layer | 도구 | 시점 |
|---|---|---|
| static skill self-check | `self_lint.py` C-EFS | 하네스 contributor PR 시 |
| sample 자체 검증 | `emit_fidelity.py samples` | 위와 동일 (CI) |
| cold session 산출 검증 | `emit_fidelity.py check --root <proj>` | phase 12 exit + phase 14 진입 |
| 디버깅 dump | `emit_fidelity.py report --root <proj>` | 사람이 직접 |

같은 fidelity 스키마가 4 위치에서 검증 — single source, multiple gates.
