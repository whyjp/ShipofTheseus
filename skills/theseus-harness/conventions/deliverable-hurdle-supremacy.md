---
id: deliverable-hurdle-supremacy
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'standalone'
indexed-in: conventions/INDEX.md
---

# Deliverable Hurdle Supremacy — 결과물 허들 > 메모리 > 컨벤션

## 한 줄 요약

**본 하네스의 *결과물 허들* 은 메모리 / 컨벤션 / 사용자 사전 위임 *어느 것도 override 불가* 인 supremacy gate.** *실행 가능한 제품 + 코드 + 테스트 구동 값* 까지 검증 의무. 실패 시 *자동 retry sprint* (graceful skip / design-only handoff 금지). v0913_cold01 의 design-only 종료 차단 + 003 / v091_cold01 의 코드 + 실행 결과 generalize.

## 1. 결손 진단

v0913_cold01 (v0.9.13 cold session) :
- self-internal aggregate 0.999 ✅
- Plan tree 4 universes ✅
- Sprint loop 3 회 ✅
- 64 invariants 설계 ✅
- **`code/` 디렉터리 부재** ❌
- **5 bench 의무 산출물 0** ❌
- **실 실행 0** ❌
- **외부 채점 effective 0** ❌

원인 = agent 가 메모리 [`feedback_harness_scope.md`](../../../C:/Users/cxx/.claude/projects/D--github-ShipofTheseus/memory/feedback_harness_scope.md) 룰 ("코드 = 외부 repo only") 을 *literal* 적용. *bench 강제 산출물* 을 메모리 룰이 *우회*.

→ **메모리 / 컨벤션 룰이 *결과물 의무* 를 우회 가능** 했던 것이 본 하네스의 결손.

## 2. Rule precedence — 3 layer

본 컨벤션 도입 후 본 하네스의 *룰 우선순위* :

```
Layer 1 (가장 약함):  메모리 feedback (사용자 사전 위임 / 관찰)
Layer 2 (중간):       하네스 컨벤션 (페이즈 룰 / 게이트 / multiverse / etc.)
Layer 3 (가장 강함):  결과물 허들 (본 컨벤션) — 실행 가능 제품 + 코드 + 테스트 구동 값
```

**Layer 3 가 Layer 1/2 무조건 override**. 메모리 룰이 "코드 안 됨" 이어도, 본 하네스가 standalone 컨텍스트면 코드 강제. 사용자가 phase 04 Q-D 에서 "design-only" 명시한 경우만 *예외* (즉 사용자 *명시 ack* 만 허들 면제).

## 3. 결과물 허들 — 5 hard check

페이즈 09 quality gate 의 *Gate 0* (zero, 정적 7 게이트보다 *상위*) 박힘 :

### Hurdle H1 — Code Existence

`code/`, `src/`, 또는 도메인 default 디렉터리 (`mine_sim/`, `cmd/`, `internal/` 등) 안에 *.py / *.go / *.ts 등 *실행 가능 코드 파일* ≥ N (N = 페이즈 06 plan 의 module count, 보통 ≥ 5).

### Hurdle H2 — Code Execution

페이즈 04 Q-D8 verification command 1 회 실행 + exit 0 검증. mock 모드 강제 시 mock 부팅도 OK.

### Hurdle H3 — Test Suite

`pytest`, `go test`, `bun test` 등 — *N 개 통과* (N ≥ 1, 일반적으로 페이즈 06 plan 의 invariants/scenarios 수). 실 측정 값 박힘 (count, not 0).

### Hurdle H4 — Bench-Required Outputs

페이즈 04 답안 (또는 bench prompt) 에 명시된 *외부 evaluator 강제 산출물* (5 개 / 7 개 등) 모두 :
- file existence
- size > 0
- schema 정합 (validate_outputs.py 또는 동등 검증 PASS)

### Hurdle H5 — Executed Values Recording

산출물의 *측정 수치* 가 *실 실행에서 도출됨* — placeholder / 0 / null 금지 :
- baseline throughput / latency / accuracy 등 *primary metric* 이 *non-zero, finite, in expected range* (analytical-bound-cross-validation 정합)
- CI95 width 가 mean 의 % 단위 (placeholder 0 또는 문자열 "TBD" 금지)
- run_metrics.json 의 wall_clock_seconds > 0

## 4. 허들 실패 처리 — *자동 retry*

5 hurdle 중 1+ 실패 :

```
- Phase 09 quality gate 의 final_status = "HURDLE_FAIL"
- Sprint loop 자동 재호출 (sprint NN+1 진입)
- Sprint NN+1 의 inputs.json 에 `hurdle_retry_target: [H1, H2, H3, H4, H5]` 명시
- 페이즈 06/08 부분 재진입 (hurdle 실패 차원에 따라):
  H1/H4 fail → 페이즈 06 module/output 강화 + 페이즈 08 fan-out 재호출
  H2/H3 fail → 페이즈 08 코드 디버깅 / 테스트 추가
  H5 fail → 페이즈 08 실 실행 + 측정값 박기
- Retry budget cap = 페이즈 04 Q-D6 (시간 budget) 의 50% 또는 5 sprint cap 중 작은 값
- Budget 소진 시: 페이즈 14 handoff *반드시* 다음 명시:
  - status: INCOMPLETE
  - hurdle_failed: [H1, H2, ...]
  - reason: <budget exhausted | hard error>
  - 사용자 ack 필요 — 다음 회차 코드 implement 의무
```

graceful skip / design-only handoff 금지. self-internal aggregate 0.999 같은 *uppgraded score* 보고 차단.

## 5. 사용자 명시 ack 예외

페이즈 04 Q-D 답안에 *명시적* "design-only 모드" 답 시 H1-H5 면제 가능 :

```
Q-D-DELIVERABLE-MODE:
1. Standalone production (default — H1-H5 의무)
2. Integration mode (기존 repo 에 patch — H1 만 의무, H4-H5 면제)
3. Design-only research (사용자 *명시 ack* — H1-H5 모두 면제)
```

답 3 = 사용자 *명시 ack* 의무 — 페이즈 04 frontmatter 의 `user_explicit_confirmation: true` + `design_only_acked_at: <timestamp>`. 명시 없음 = 답 1 default.

v0913_cold01 retro 적용 시 = 답 1 default 였음에도 H1/H2/H3/H4/H5 모두 0 → 본 컨벤션이라면 hard-fail + retry sprint 강제.

## 6. 메모리 룰의 정정 (`feedback_harness_scope.md`)

본 컨벤션이 메모리 룰의 *override 권한* 명시 :

```
~~~ 본 하네스 = 설계 + 가이드 문서. 실 코드 = 외부 repo only. ~~~

(정정, v0.9.14)
하네스의 *침습 가드* :
  - 사용자 *기존* repo 의 *무관 코드* 침습 금지
  - 그러나 *결과물 허들* 은 supremacy: standalone 컨텍스트 시 코드 + 실행 + 측정값 의무
  - 메모리 룰이 결과물 허들 override 불가 (페이즈 04 Q-D 답 3 명시 ack 만 예외)
```

본 정정 후 :
- 003 / cold / v091_cold01 / v099 = 정합 (standalone 컨텍스트, 코드 + 실행 ✅)
- v0913_cold01 = **위반** (standalone 인데 코드 0)

## 7. self_lint C-DHS (deliverable hurdle supremacy)

```python
def lint_deliverable_hurdle(project_dir: Path) -> list[str]:
    errors = []
    handoff = read_yaml(project_dir / "handoff" / "14-handoff.md")

    # Q-D-DELIVERABLE-MODE 확인
    q_d_mode = handoff.get("q_d_deliverable_mode", 1)  # default = standalone

    if q_d_mode == 1:  # standalone production
        # H1
        code_files = list((project_dir / "code").rglob("*.py")) + list((project_dir / "src").rglob("*.go"))
        if len(code_files) < 5:
            errors.append(f"H1 fail: code files {len(code_files)} < 5")
        # H2/H3 — sprint report 의 evidence
        if not handoff.get("execution_evidence"):
            errors.append("H2 fail: no execution evidence")
        # H4
        outputs = list((project_dir / "code" / "outputs").iterdir())
        for required in handoff.get("bench_required_outputs", []):
            p = project_dir / "code" / "outputs" / required
            if not p.exists() or p.stat().st_size == 0:
                errors.append(f"H4 fail: {required} missing or empty")
        # H5
        if not handoff.get("measured_values_evidence"):
            errors.append("H5 fail: no measured values recorded")
    elif q_d_mode == 3:  # design-only — user ack 검증
        if not handoff.get("design_only_acked_at"):
            errors.append("design-only mode without explicit user ack")
    return errors
```

self_lint C-DHS = supremacy gate. handoff 의 final_status 가 "PASS" 인데 H1-H5 fail 시 *handoff 자체가 invalid*.

## 8. 그레이드별 활성

| Grade | 결과물 허들 활성 | 비고 |
|---|:-:|---|
| G1 Trivial | n/a | mini_harness_tbd |
| G2 Simple | optional | small feature, hurdle 약화 OK |
| G3 Standard | **의무** | standalone default |
| G4 Complex | **의무 + retry budget tighter** | bench / external evaluator |
| G5 Critical | 의무 + 사용자 명시 ack 강제 (Q-D-DELIVERABLE-MODE = 1 만 OK) | mission critical |

## 9. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- H1-H5 = *측정 메트릭* 단위 (count / size / non-zero), 도메인 X
b- retry sprint = regression.md §2 sprint loop 의 일반 메커니즘 활용
c- 사용자 ack = 페이즈 04 Q-D 의 generic 패턴
d- 메모리 override 룰 = generic supremacy 메커니즘

## 10. 자기 검증 (메타)

본 컨벤션 자체에 적용 — 본 컨벤션 = single artifact (Markdown). standalone 컨텍스트 X (메타 룰). 따라서 H1-H5 면제 (Q-D-DELIVERABLE-MODE = 3 implicit). 단 본 컨벤션이 *자기 자신의 supremacy* 를 명시하는 자기 적용 = self-bootstrap 정합.

## 11. 안티 패턴

a- **메모리 룰 인용 후 hurdle 면제** — v0913_cold01 패턴. 본 컨벤션 핵심 위반.
b- **handoff status="PASS" 인데 H1-H5 evidence 0** — handoff 정직성 위반. self_lint C-DHS auto-fail.
c- **retry budget 무시 후 design-only handoff** — sprint loop 우회. 본 컨벤션 §4 의 "graceful skip 금지" 위반.
d- **사용자 ack 없이 design-only 종료** — Q-D 답 1/2 default 인데 H1-H5 fail → "사용자 명시 ack 누락" 으로 hard-fail.
e- **self-internal aggregate 만 보고** — bench effective score 별도 보고 의무. v0913_cold01 의 0.999 보고 = 본 컨벤션이라면 *handoff 의 invalid status* 자동 박힘.

## 12. 호환성

- v0.9.5 [`runtime-prereq.md`](runtime-prereq.md) 의 게이트 7 (env-satisfied + 실 실행 1회) = 본 컨벤션 H2/H3 의 *원형*. 본 컨벤션이 H1/H4/H5 추가 + supremacy 메커니즘 명시.
- v0.9.6-13 의 모든 컨벤션 = Layer 2. 본 컨벤션 = Layer 3. 충돌 시 Layer 3 우선.
- 메모리 [`feedback_executable_state.md`](../../../C:/Users/cxx/.claude/projects/D--github-ShipofTheseus/memory/feedback_executable_state.md) = 본 컨벤션의 *원본 의도*. 본 컨벤션이 Layer 3 supremacy 로 강화.
