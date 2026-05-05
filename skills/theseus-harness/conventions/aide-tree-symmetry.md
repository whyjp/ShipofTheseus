---
id: aide-tree-symmetry
category: multiverse
applies-to-phases: '[06]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'universe candidate'
indexed-in: conventions/INDEX.md
---

# AIDE-tree symmetric depth — 모든 universe candidate 의 sequenceDiagram 강제

## 한 줄 요약

**페이즈 06 의 N universe candidate 가 *대칭 깊이* 로 elaborated 되어야 진짜 경합 — line count 만 ≥20 diff 가 아니라 *시각적 architectural diff* (sequenceDiagram per-universe) 강제.** v01_cold 회차의 audit 에서 발견 (3 universe 중 1 universe 만 sequenceDiagram, 나머지 2 universe 는 text-only — 비대칭 경합).

## 1. 결손 진단

기존 [`plan-tree.md`](plan-tree.md) + HARD-RULE 9-c 가 "universe-N/06-plan.md ≥ 20 diff lines" 만 enforcement. 이 룰은 *분량* 만 검증 — *diagrammatic depth* 는 자유. 실제 cold 검증 (synthetic_mine_throughput_v01_cold) 에서 :

- universe-1/06-plan.md = 66 lines, sequenceDiagram 0
- universe-2/06-plan.md = 186 lines, sequenceDiagram 1
- universe-3/06-plan.md = 72 lines, sequenceDiagram 0

→ U2 만 *시각적으로 elaborated*, U1/U3 는 *text-only architectural description*. tournament 가 *형식적으로 3 candidate* 지만 *실 경합력* 은 U2 우월. 비대칭.

## 2. 운영 룰

각 universe candidate 의 `plan/candidates/universe-N/06-plan.md` 의무 :

a- **sequenceDiagram ≥ 1** — Mermaid sequenceDiagram block.
b- **Actors ≥ 3** — diagram 내 `participant` 또는 `actor` 선언 ≥ 3.
c- **Interactions ≥ 5** — `->>`, `-->>`, `--)`, `-)`, `->>+`, `-x` 등 메시지 화살표 ≥ 5.
d- **Universe-specific actor differentiation** — 각 universe 의 actor 이름 또는 dispatch flow 가 *다른 universe 와 visually 구분*. 예: U1 = `dispatcher_per_direction`, U2 = `dispatcher_priority`, U3 = `dispatcher_fifo`. self_lint C-PT-SEQ 가 universe 간 actor 이름 / interaction 패턴 차이 ≥ 1 검증.

## 3. self_lint 룰

`scoring/self_lint.py` C-PT-SEQ (신규) :

```python
def lint_universe_sequence_diagram(plan_dir: Path) -> list[str]:
    errors = []
    for uni_dir in (plan_dir / "candidates").glob("universe-*"):
        plan = (uni_dir / "06-plan.md").read_text(encoding="utf-8")
        # Detect Mermaid sequenceDiagram blocks
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

## 4. v0.9.9 의 enforcement 갭 (재확인)

v0.9.9 의 [`plan-tree.md`](plan-tree.md) 가 line-count 강제만 — sequenceDiagram 강제 없음. v0.9.10 본 컨벤션 도입으로 *symmetric architectural diff* 강제.

## 5. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- sequenceDiagram = Mermaid 표준 (도메인 무관).
b- actors / interactions count 임계 = generic 메트릭, 도메인 X.
c- universe-specific differentiation = naming 룰, 케이스 X.

## 6. 안티 패턴

a- sequenceDiagram 1 개 박지만 actors 모두 동일 = 형식적 통과 (룰 §2-d 위반).
b- 동일 sequence 를 N universe 모두 carbon-copy = competition 0 (universe 간 diff 0).
c- universe N-1 / N-2 가 N-1 의 1 줄 변형 + actor 이름만 변경 = pseudo-diff. self_lint 가 의미 매칭 검증 (TBD v0.9.11).
