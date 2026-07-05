# Phase 07 — 계획 재이해 (콜드)

## 한 줄 요약
**계획 자체에 페이즈 03 와 같은 콜드 리딩을 적용한다.** 의도 문서, 비평, 사용자 답을 본 적 없는 fresh 에이전트가 계획만 읽고 무엇을 만들 것인지 거꾸로 추론한다. 의도와 어긋나면 계획이 잘못된 것.

## 입력
- `plan/06-plan.md` 만.

## 서브에이전트
**fresh `Agent(subagent_type="general-purpose")`**, [`../agents/plan-reviewer.md`](../agents/plan-reviewer.md) 의 self-contained 프롬프트.

## 답해야 할 4 질문 + premortem

1- 이 계획만 보면 어떤 기능을 만드는 것인가? (한 문단, 자기 말)
2- 어떤 TODO 부터 시작하겠는가? 이유는?
3- 과소 명세·과대 사이즈·순서 어긋남이 보이는 TODO 는?
4- 누락·잘못된 의존은?
5- **premortem** ([`../conventions/premortem-friction.md`](../conventions/premortem-friction.md), v0.9.7) — "이 플랜이 *수정 0* 으로 페이즈 08 진입 시, sprint 01 의 회귀 발생 위치 ≥ 3 곳?" 격언 prepend (F5 *知之為知之 不知為不知 是知也* / F2 *de omnibus dubitandum est*) + `derived_improvements ≥ 1` 의무. 0 면 C-PM 위반 (미등록).

## 산출물
`plan/07-plan-review.md` — 4 답 + premortem 절 + 판정 (`accept` | `revise` | `reject`).

## 지휘자 후속

a- 1- 답을 `intent/01-intent.md` 의 "무엇을" 과 diff. 의미상 어긋나면 → 계획이 의도를 인코딩하지 못함 → 페이즈 06 재실행.
b- `revise` → 리뷰 첨부해 페이즈 06 재실행. 시도 3 회 캡.
c- `accept` → 페이즈 08.

## Da Capo enforcement gate (HARD-RULE 9.p)

본 페이즈 진입 *전* orchestrator 가 [`../conventions/dacapo-enforcement.md`](../conventions/dacapo-enforcement.md) (bm) 의 `gate_phase06_to_07()` 자동 호출 — 6 조건 검증 :

1- `plan/tournament-NN.md` frontmatter 에 `dacapo_loop_executed: true`
2- `step_d_tournament_pass` + `step_d_shadow_pass` + `step_d_converged` 3종 명시
3- (step_d_converged=true) → CONVERGED OR (rerun_count >= max_rerun OR budget >= 0.95) AND `plan/fallback-reason.md` 본문 ≥ 1 줄 → BUDGET_BOUND
4- rerun_count >= 1 시 `dacapo-rerun-NN.md` 갯수 == rerun_count + `shadow-grade-NN.json` 갯수 == rerun_count+1
5- rerun_count >= 1 시 anonymized previous winner 존재 (ad C-TBR-ANON)
6- `plan/dacapo-flow.md` Mermaid + timeline 의무 (at 가시화)

미달 시 본 페이즈 진입 *자동 거부* + phase 06 Step A 재진입 + `intent/00-violation.md` 기록. 위반 ≥ 3회 시만 페이즈 04 사전 답안 매핑 escalation ([`../conventions/autonomy.md`](../conventions/autonomy.md) 정합 — 자율 회귀 default).

또한 [`../conventions/dacapo-skip-sentinel.md`](../conventions/dacapo-skip-sentinel.md) (bp) 의 3 sentinel (frontmatter 모순 / 디렉터리 카운트 / 로그 패턴) 매치 시도 자동 회귀.

## 왜 필요한가

대부분의 코딩 하네스는 계획 리뷰를 건너뛰고 구현 도중 "당연한" 단계가 사실은 미명세 인프라를 요구한다는 사실을 알게 된다. 여기서 한 번의 에이전트 호출로 잡으면 스프린트 4 회분의 바이섹트 비용을 아낀다.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).


## sprint-38 — phase 07 강화 (3 sub-phase)

phase 07 단순 dispatch → 3 sub-phase 분해:

| sub-phase | 책임 | 산출물 | self_lint |
|---|---|---|---|
| **07.a** Dispatch table | 06.d sub-tree 노드 → agent role 매핑 | `dispatch/07-dispatch-table.md` | C-DPT |
| **07.b** Dispatch trace | agent 실행/산출 추적 manifest | `dispatch/07-dispatch-trace.json` | C-DPS |
| **07.c** Cross-agent invariant | agent 간 산출 정합성 lint | `dispatch/07-cross-agent-lint.md` | C-CAI |

### 07.a Dispatch table

phase 06.d 의 leaf TODO 갯수 == phase 07.a dispatch row 갯수 (1:1 정합).

산출물 — `dispatch/07-dispatch-table.md`:

```markdown
---
phase: "07.a"
prev_fingerprint: "P06D-..."
fingerprint: "P07A-..."
dispatch_row_count: <int>
unmatched_todo: 0          # 의무 0
---

# Phase 07.a Dispatch Table

| TODO ID | Module | Agent role | Subagent type | Inputs | Outputs |
|---|---|---|---|---|---|
| T-001.a.1 | code/<...>/truck.py | implementer | Sonnet | plan/06-plan.md §truck | code/truck.py + tests/ |
| T-001.a.2 | ... | ... | ... | ... | ... |
```

### 07.b Dispatch trace

각 agent 호출의 시작/종료 timestamp + 산출 파일 list. append-only.

산출물 — `dispatch/07-dispatch-trace.json`:

```json
{
  "schema_version": "0.9.43",
  "trace": [
    {
      "todo_id": "T-001.a.1",
      "agent_role": "implementer",
      "subagent_type": "Sonnet",
      "started_at": "<ISO>",
      "ended_at": "<ISO>",
      "duration_seconds": 42,
      "outputs": ["code/truck.py", "code/tests/test_truck.py"],
      "exit_code": 0
    }
  ]
}
```

### 07.c Cross-agent invariant

agent A 의 output 이 agent B 의 input 정합 (interface drift 0). 매 dispatch 후 자동 lint.

산출물 — `dispatch/07-cross-agent-lint.md`:

```markdown
---
phase: "07.c"
fingerprint: "P07C-..."
invariant_checked_count: <int>
invariant_violations: 0       # 의무 0
---

# Phase 07.c Cross-agent Invariant

## Invariants 검사 결과

| Invariant | A → B | 검사 | 결과 |
|---|---|---|---|
| TruckScheduler 인터페이스 시그니처 | T-001.a.1 → T-001.a.2 | dispatch() 시그니처 일치 | ✓ |
| Loader queue capacity | T-001.b.1 → T-001.b.2 | max_capacity 일관 | ✓ |
```

### self_lint C-DPT (C-DPS/C-CAI 미등록)

```python
def check_dispatch_table(skill_root: Path) -> list[str]:
    """C-DPT (sprint-38 PR-I) — phase 07.a dispatch table."""
    issues = []
    p07 = skill_root / "phases" / "07-plan-recursion.md"
    body = p07.read_text(encoding="utf-8")
    for kw in ["07.a Dispatch table", "07.b Dispatch trace", "07.c Cross-agent invariant",
              "dispatch_row_count", "unmatched_todo: 0", "invariant_violations: 0"]:
        if kw not in body:
            issues.append(f"phases/07-plan-recursion.md: '{kw}' 키워드 누락 (sprint-38 PR-I)")
    return issues
```

3 sub-phase 모두 통합 검사 (단일 self_lint 함수, 키워드 매트릭스 검증).

### 안티 패턴

a- **dispatch row != leaf TODO 수** — 06.d 와 1:1 정합 위반.
b- **trace 누락** — dispatch 호출 후 trace 미갱신 = observability 0.
c- **invariant_violations ≥ 1** — agent 간 interface drift. 발견 시 즉시 phase 06 재진입 권고.
d- **unmatched_todo ≥ 1** — dispatch table 에 TODO orphan.
