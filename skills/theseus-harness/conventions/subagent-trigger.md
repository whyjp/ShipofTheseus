---
id: subagent-trigger
category: core
applies-to-phases: '[06,08]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'phase 06 exit / phase 08 enter'
indexed-in: conventions/INDEX.md
---

# Subagent Trigger — sub-todo level 병렬 자동 판별 (sprint-34 / v0.9.39)

## 한 줄 요약

**phase 06 exit (plan/06-plan.md 확정) 시점 + phase 08 enter 시점에 `scoring/sub_agent_dispatch.py analyze-todos` 의무 호출 — TODO DAG 를 위상 정렬해 병렬 가능 그룹 + 디스패치 모드 자동 도출.** [`sub-agents.md`](sub-agents.md) (b) 가 *모듈 단위* 분해 트리거를 한다면, 본 컨벤션은 *TODO 단위* (T-NNN) fine-grained 트리거 — 두 layer 가 직교.

## 1. 결손 진단

기존 자산:
- [`sub-agents.md`](sub-agents.md) — 모듈 단위 `should_subdivide()` (LOC 임계 / 복합 책임 / 다중 스택 / explicit / rewrite_streak)
- [`multiverse-impl-fan-out.md`](multiverse-impl-fan-out.md) — universe 단위 fan-out
- [`per-module-diagram-fan-out.md`](per-module-diagram-fan-out.md) — 모듈별 다이어그램
- HARD-RULE 9.a item 3 — `plan/06-plan.md` 의 TODO DAG (T-NNN ID + 의존 + 완료 조건) 본문 의무

**갭** — TODO DAG 가 *작성되어 있어도* implementer 가 그것을 *순차* 처리. 의존 chain 이 분기되어 병렬 가능한데도 1-by-1 dispatch. v0.9.19 mindmap A + per-module fan-out 은 "모듈" 입자이지 "TODO" 입자가 아님.

→ TODO DAG 를 *Kahn 위상 정렬* (의존 없는 노드부터 level 단위) 해 *level 단위 병렬 그룹* 을 자동 도출하고 implementer 가 그 그룹을 한 번에 fan-out 하는 layer 가 필요.

## 2. 입력 / 출력

**입력** — `plan/06-plan.md` 의 TODO 항목. 각 항목은 [`plan.template.md`](../templates/plan.template.md) 형식 :

```markdown
- **T-001 — title**
  - 의존: [T-XXX, T-YYY]    # 또는 []
  - 완료 조건: ...
```

**출력** — JSON :

```json
{
  "total_todos": 5,
  "groups": [["T-001", "T-010"], ["T-020", "T-021"], ["T-080"]],
  "max_parallel": 2,
  "levels": 3,
  "cyclic": [],
  "recommended_mode": "parallel",
  "fan_out_recommendation": "level 3 단계, 최대 2 병렬 — parallel 모드 dispatch 권장"
}
```

같은 sublist (level) = 의존 만족 후 *동시 dispatch 가능*. 다음 level 은 직전 level 종료 후.

## 3. orchestrator 호출 인터페이스

```bash
# phase 06 exit 직후 — plan/06-plan.md 확정 시점
python skills/theseus-harness/scoring/sub_agent_dispatch.py analyze-todos \
    --plan-md .ShipofTheseus/<proj>/plan/06-plan.md --grade 4

# 출력을 plan/06-todo-fan-out.json 으로 저장 (선택)
python ... > .ShipofTheseus/<proj>/plan/06-todo-fan-out.json
```

phase 08 enter 시 implementer agent 가 본 JSON 을 입력으로 받아 :
1. `groups[0]` 의 TODO 들을 *동시 fan-out* (parallel/competition 모드 시)
2. 모두 종료 후 `groups[1]` fan-out
3. 반복

cyclic 검출 시 phase 06 회귀 (재계획) — `intent/00-violation.md` 기록.

## 4. 트리거 신호 + abort vs warn

| 신호 | 처리 |
|---|---|
| `total_todos == 0` | **WARN** — TODO DAG 부재. HARD-RULE 9.a item 3 fail (별 layer 에서 reject) |
| `cyclic ≠ []` | **ABORT** — 의존 cycle 검출, phase 06 회귀 강제 |
| `max_parallel == 1` | INFO — 병렬 가능 분기 부재 (chain), 순차 dispatch |
| `max_parallel > 5` | WARN — `PARALLEL_FAN_OUT_LIMIT` 초과, chunk 분할 권장 |
| `max_parallel ≥ 2 AND mode = sequential` | WARN — 병렬 기회 놓침 (G3+ 에서 mode 권장값 따라야) |

## 5. 그레이드별 모드 추천 알고리즘

```python
if grade <= 2:
    mode = "sequential"
elif grade == 3:
    mode = "sequential" if max_parallel <= 2 else "parallel"
elif grade == 4:
    mode = "parallel" if max_parallel >= 2 else "sequential"
else:   # G5
    mode = "competition" if max_parallel >= 3 else "parallel"
```

G5 에서 max_parallel ≥ 3 시 competition 권장 — 같은 level 내 TODO 들을 *경쟁* universe 로 분기해 best winner 선택 ([`competition.md`](competition.md) 알고리즘).

## 6. self_lint C-SAT 룰 (구 C-STT)

```python
def lint_subagent_trigger(skill_root: Path) -> list[str]:
    issues = []
    conv = (skill_root / "conventions" / "subagent-trigger.md").read_text(encoding="utf-8")
    py = (skill_root / "scoring" / "sub_agent_dispatch.py").read_text(encoding="utf-8")

    for kw in ["analyze-todos", "TODO DAG", "위상 정렬", "병렬 그룹", "max_parallel", "cyclic"]:
        if kw not in conv:
            issues.append(f"subagent-trigger.md: '{kw}' 키워드 누락")

    for fn in ["parse_todos", "topological_levels", "analyze_todos", "cmd_analyze_todos"]:
        if f"def {fn}" not in py:
            issues.append(f"sub_agent_dispatch.py: 함수 {fn} 부재")

    return issues
```

CHECKS 등록 — `("C-SAT", "subagent-trigger TODO DAG analyze-todos (sprint-34 / v0.9.39)", check_subagent_trigger)`.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 위상 정렬 = 일반 그래프 알고리즘, 도메인 X.
b- TODO ID + 의존 = HARD-RULE 9.a item 3 의 일반 골격, 도메인 X.
c- max_parallel 임계 (5) = `PARALLEL_FAN_OUT_LIMIT` (sub-agents.md §"비용 가드"), 도메인 X.

## 8. 안티 패턴

a- **TODO DAG 본문 작성 후 analyze-todos 미호출** — phase 08 implementer 가 순차 dispatch. 본 컨벤션 이행 0. orchestrator 가 phase 06 exit 시 의무 호출.
b- **cyclic 검출 무시** — `cyclic ≠ []` 인데 phase 08 진입. 무한 회귀 또는 데드락. ABORT 의무.
c- **max_parallel > 5 chunk 분할 안 함** — 한 번에 10 sub-agent fan-out → RAM/Opus 한도 초과. `sub-agents.md` 비용 가드 정합 chunk 분할 의무.
d- **G5 max_parallel ≥ 3 인데 parallel 만 사용** — competition 기회 놓침. G5 는 *경쟁* 이 default — 본 컨벤션 §5 모드 추천 따라야.
e- **TODO 형식 비정합** — `**T-NNN — title**` 형식 깨짐 (예: `T1 - title`, `[T001] title`). parse_todos 0 매치 → analyze-todos WARN 처리.

## 9. sub-agents.md 와의 layer 분리

| Layer | 컨벤션 | 입자 | 트리거 |
|---|---|---|---|
| **모듈 단위** | [`sub-agents.md`](sub-agents.md) (b) | Module / TODO bundle | LOC > 200 / 복합 책임 / 다중 스택 / rewrite_streak ≥ 3 |
| **TODO 단위** (sprint-34) | **본 컨벤션** | T-NNN | TODO DAG 위상 정렬 → max_parallel ≥ 2 |

**모듈 분해 후 그 안의 TODO 도 분해 가능** — 두 layer 가 *직교*. 예: 모듈 A 가 should_subdivide=True 로 sub-agent 1/2/3 으로 분해된 후, 각 sub-agent 의 TODO 들이 다시 본 컨벤션의 위상 정렬 대상.

## 10. 그레이드 활성

- G1 / G2 — 비활성 (TODO DAG 자체가 단순, 병렬 의미 약).
- **G3+ — 의무** (TODO ≥ 5 시 analyze-todos 호출).
- G5 — competition 모드 강제 (max_parallel ≥ 3 시).

## 11. 호환성

- [`sub-agents.md`](sub-agents.md) — 모듈 단위 분해 (직교 layer).
- [`competition.md`](competition.md) — G5 competition 모드 머지 알고리즘.
- [`build-and-config.md`](build-and-config.md) §7 — 같은 파일 직렬 가드 (병렬 dispatch 시 머지 가드).
- [`phase-lineage-viewer.md`](phase-lineage-viewer.md) — lineage.md 의 phase 08 노드에 fan-out 정보 기록.
- HARD-RULE 9.a item 3 — TODO DAG 본문 의무 (본 컨벤션의 *입력*).
