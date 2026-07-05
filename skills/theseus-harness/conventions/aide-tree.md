---
id: aide-tree
category: multiverse
applies-to-phases: '[02,05,06,08,11,13]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always (multi-phase) / universe candidate (symmetry)'
indexed-in: conventions/INDEX.md
---

# AIDE-tree — multi-phase multiverse 확장 (breadth) + 대칭 sequenceDiagram (depth)

## 한 줄 요약

**본 하네스의 *유일한 차별 강점* = multiverse competition. 본 컨벤션은 그 강점을 두 axis 로 확장**: ① **breadth** — 페이즈 06 (plan) 뿐 아니라 02/05/08/11/13 까지 N universe 경합 (multi-phase) ② **depth** — 각 universe candidate 의 sequenceDiagram 강제로 대칭 architectural diff (symmetry). 둘 다 G3+ 한정, 페이즈 04 NFR-V 단계에서 활성 여부 사용자 위임.

## 1. 결손 진단

기존 [`plan-tree.md`](plan-tree.md) + [`competition.md`](competition.md) + HARD-RULE 9-c :

- 페이즈 06 만 N universe planner sub-agent 호출 → *plan* axis 만 multiverse, review/critique/impl/regression/visualization axis 는 single-world
- universe-N/06-plan.md "≥ 20 diff lines" 만 enforcement → *분량* 만 검증, *시각적 architectural diff* 자유
- v01_cold 회차 audit 사례: 3 universe 중 1 개만 sequenceDiagram, 나머지 2 개 text-only — *형식적 3 candidate / 실 경합력 1*

→ **breadth 확장** + **depth 대칭** 둘 다 필요.

## 2. Breadth — 페이즈별 multiverse 활성 (multi-phase)

각 페이즈가 *어떤 axis 의 multiverse* 인지 명시:

| 페이즈 | universe 차별 axis | N (G3 / G4 / G5) | 합집합 type |
|---|---|:-:|---|
| 02 doc-review | reviewer 시각 (skeptic / supportive / domain-naive) | 2 / 3 / 4 | tournament merge |
| 05 critique | critic 차원 (structural / behavioral / cost-benefit / risk) | 2 / 3 / 4 | tournament merge + ensemble |
| 06 plan-tree | architecture seed | 2 / 3-4 / 5-6 | tournament merge (기존) |
| 08 impl strategy | implementation 전략 (idiomatic / optimized / minimal) | 2 / 3 / 4 | tournament + integrate |
| 11 regression bisect | hypothesis space (commit / data / config / env) | 2 / 3 / 4 | parallel hypothesis tournament |
| 13 interactive-viewer | UX framing (operator / engineer / executive) | — / 2 / 3 | gallery (no merge — show all) |

각 페이즈의 universe 별 산출물 = `<phase_dir>/candidates/universe-N/<phase_artifact>.md` (페이즈 06 와 동일 패턴).

### 2.1 Tournament resolve 차원 (phase-specific)

- 02 doc-review = 결손 발견 수 + 결손 우선순위 매칭 + remediation 제안 quality
- 05 critique = 대안 다양성 + 비용-효익 정량화 + 우선순위 합리성
- 08 impl strategy = (코드 품질 + 테스트 커버리지 + LOC) × NFR 충족
- 11 regression bisect = hypothesis 의 evidence weight + 검증 가능성
- 13 viewer = decision-support clarity per stakeholder

각 페이즈 별 차원 *재정의* — generic 차원이 아닌 phase-specific. 차원 정의 frontmatter 박힘 검증 의무 (C-AT-MP, 미등록).

### 2.2 페이즈 04 자율 설정 (Q-D10~D14)

페이즈 04 NFR-V 단계에서 *각 페이즈의 multiverse 활성 여부* 사용자 위임:

```
Q-D10 — 페이즈 02 multi-reviewer 활성?
1. 비활성 (single reviewer, default G3)
2. 폭 2 (G4+)
3. 폭 3+
4. N/A (페이즈 02 skip)

Q-D11 — 페이즈 05 multi-critic ?     # 동일 패턴
Q-D12 — 페이즈 08 multi-strategy?
Q-D13 — 페이즈 11 multi-hypothesis?
Q-D14 — 페이즈 13 multi-framing viewer?
```

cold context 의 자동 매핑 = G4 default (페이즈 02/05/08 = 폭 2-3, 페이즈 11/13 = 폭 2). 사용자 명시 시 override.

### 2.3 Blind rerun 활성

각 multiverse 페이즈가 [`tournament-blind-rerun.md`](tournament-blind-rerun.md) 의 임계-미달-재경합 룰 적용 가능. 페이즈 04 Q-D2 답 (auto-fix-trigger) 정합 — fail 시 자동 blind rerun 진입.

## 3. Depth — universe candidate sequenceDiagram 대칭 (symmetry)

페이즈 06 의 N universe candidate 가 *대칭 깊이* 로 elaborated 되어야 진짜 경합 — line count 만 ≥20 diff 가 아니라 *시각적 architectural diff* (sequenceDiagram per-universe) 강제.

### 3.1 운영 룰

각 universe candidate 의 `plan/candidates/universe-N/06-plan.md` 의무:

a- **sequenceDiagram ≥ 1** — Mermaid sequenceDiagram block.
b- **Actors ≥ 3** — diagram 내 `participant` 또는 `actor` 선언 ≥ 3.
c- **Interactions ≥ 5** — `->>`, `-->>`, `--)`, `-)`, `->>+`, `-x` 등 메시지 화살표 ≥ 5.
d- **Universe-specific actor differentiation** — 각 universe 의 actor 이름 또는 dispatch flow 가 *다른 universe 와 visually 구분*. 예: U1 = `dispatcher_per_direction`, U2 = `dispatcher_priority`, U3 = `dispatcher_fifo`. universe 간 actor 이름 / interaction 패턴 차이 ≥ 1 검증 의무 (C-PT-SEQ, 미등록).

### 3.2 검증 스케치 — C-PT-SEQ (미등록)

```python
def lint_universe_sequence_diagram(plan_dir: Path) -> list[str]:
    errors = []
    for uni_dir in (plan_dir / "candidates").glob("universe-*"):
        plan = (uni_dir / "06-plan.md").read_text(encoding="utf-8")
        import re
        seq_blocks = re.findall(r"```mermaid\s*sequenceDiagram(.*?)```", plan, re.DOTALL)
        if not seq_blocks:
            errors.append(f"{uni_dir.name}: no sequenceDiagram block")
            continue
        body = seq_blocks[0]
        actors = re.findall(r"(?:participant|actor)\s+(\w+)", body)
        interactions = re.findall(r"->>|-->>|-?\)|-x", body)
        if len(actors) < 3:
            errors.append(f"{uni_dir.name}: actors={len(actors)} < 3")
        if len(interactions) < 5:
            errors.append(f"{uni_dir.name}: interactions={len(interactions)} < 5")
    # Cross-universe actor differentiation
    actor_sets = {uni: set(...) for uni in candidates}
    if all are subset → fail "no universe-specific actors"
    return errors
```

## 4. Breadth × Depth 시너지

| 축 | 작용 |
|---|---|
| **breadth** (multi-phase) | 5+ 페이즈로 multiverse 확장 |
| **depth** (symmetry) | 각 universe 의 sequenceDiagram 강제 |
| validity (별도) | [`tournament-blind-rerun.md`](tournament-blind-rerun.md) — 임계 미달 시 blind 재경합 |

세 축 시너지 = "deep × broad × validated multiverse" — 본 하네스의 *유일한 차별 강점* 의 풀 발현.

## 5. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 페이즈별 차별 axis = 의미군 (reviewer 시각 / critic 차원 등), 도메인 X.
b- N (G3/G4/G5) = 그레이드별 generic 룰.
c- tournament resolve = 페이즈별 차원 정의만 차이, 알고리즘은 competition.md 동일.
d- sequenceDiagram = Mermaid 표준 (도메인 무관).
e- actors / interactions count 임계 = generic 메트릭, 도메인 X.
f- universe-specific differentiation = naming 룰, 케이스 X.

## 6. 안티 패턴

### 6.1 Breadth 안티 패턴

a- *모든 페이즈* 에 multiverse 활성 — over-engineering. 룰 §2 표의 axis 가 의미 있을 때만.
b- universe N 마다 *동일한 산출물 변형* — 차별 axis 위반 (C-AT-MP-AXIS, 미등록).
c- multi-phase 활성 시 tournament merge 없이 *형식적 N 산출물* 만 — single-world 와 동급. merge 의무.

### 6.2 Depth 안티 패턴

d- sequenceDiagram 1 개 박지만 actors 모두 동일 = 형식적 통과 (룰 §3.1-d 위반).
e- 동일 sequence 를 N universe 모두 carbon-copy = competition 0 (universe 간 diff 0).
f- universe N-1 / N-2 가 N-1 의 1 줄 변형 + actor 이름만 변경 = pseudo-diff. self_lint 가 의미 매칭 검증 (TBD).

## 7. 호환성

- [`competition.md`](competition.md) / [`plan-tree.md`](plan-tree.md) — 페이즈 06 룰은 *불변*. 본 컨벤션은 *추가 페이즈* (multi-phase) + *대칭 강제* (symmetry) 만 정의. backward compatible.
- [`per-module-diagram-fan-out.md`](per-module-diagram-fan-out.md) — universe 별 sequenceDiagram 의무 + 본 컨벤션 = universe 안 *모듈* fan-out (직교).
- [`multiverse-impl-fan-out.md`](multiverse-impl-fan-out.md) — plan 차원 sequenceDiagram per-universe → impl 코드 차원으로 확장.
- phases/06,08,14 §canonical inline (sprint-37 PR-AH, prev: canonical-not-stub.md) — universe candidate sequenceDiagram + canonical inline mode 결합 시 winner sequence 가 canonical 에도 박힘.

## 8. 통합 history (sprint-37 PR-AB)

본 컨벤션은 sprint-37 PR-AB (다이어트) 에서 **`aide-tree-multi-phase`** (breadth) + **`aide-tree-symmetry`** (depth) 두 컨벤션을 단일 컨벤션의 §2/§3 두 축으로 통합. 책임 = "multiverse competition 확장" 단일, 두 축 = breadth (multi-phase) / depth (symmetry). 매핑은 [`MIGRATION.md`](MIGRATION.md) 단일 source.
