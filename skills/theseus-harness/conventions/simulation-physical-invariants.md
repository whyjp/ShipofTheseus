# Simulation Physical Invariants — Sim correctness 만점 push (sprint-16 / v0.9.22)

## 한 줄 요약

**Sim correctness 18→20 (-2pt) 정정.** [`analytical-bound-cross-validation.md`](analytical-bound-cross-validation.md) (af, v0.9.12) 의 closed-form 상한 검증 위에 *런타임 invariant 자동 검증* 추가 — mass conservation / resource exclusivity / monotonic time / bounded queue / no-deadlock 5 종 시뮬 invariant 을 매 시뮬 실행 *런타임에* 자동 assert.

## 1. 5 시뮬 physical invariant 자동 검증

af 가 *분석적 상한* (예: throughput ≤ N×capacity/T) 을 검증한다면, 본 컨벤션은 *시뮬 진행 중* 에 위반 detect.

```python
class SimulationInvariantChecker:
    """
    매 event 처리 후 5 invariant 자동 assert.
    위반 시 RuntimeError + dump frame + last 100 events.

    bs domain-model-completeness §D4 invariant 와 1:1 매핑 의무 —
    domain 차원 invariant 가 sim 차원으로 자동 변환.
    """

    def __init__(self, scenario: Scenario, domain_invariants: list[Invariant]):
        self.scenario = scenario
        self.domain_invariants = domain_invariants

    def check_after_event(self, event: Event, state: SimState) -> None:
        # I1 mass conservation
        if state.total_loaded != state.total_dumped + state.in_transit:
            raise InvariantViolation(
                f'mass conservation: loaded={state.total_loaded} '
                f'!= dumped={state.total_dumped} + in_transit={state.in_transit}',
                event=event,
            )

        # I2 resource exclusivity
        for loader in state.loaders:
            if len(loader.assigned_trucks) > 1:
                raise InvariantViolation(
                    f'resource exclusivity: loader={loader.id} has {len(loader.assigned_trucks)} trucks',
                )

        # I3 monotonic time
        if event.time < state.last_event_time:
            raise InvariantViolation(
                f'monotonic time: event.time={event.time} < last={state.last_event_time}',
            )

        # I4 bounded queue
        for q in state.queues.values():
            if len(q) > self.scenario.max_queue_bound():
                raise InvariantViolation(
                    f'bounded queue: |{q.name}|={len(q)} > bound={self.scenario.max_queue_bound()}',
                )

        # I5 no-deadlock — every WAITING truck must have a future event scheduled
        for truck in state.trucks:
            if truck.state == TruckState.WAITING:
                if not state.event_queue.has_future_event_for(truck.id):
                    raise InvariantViolation(
                        f'no-deadlock: truck={truck.id} WAITING with no future event',
                    )
```

## 2. invariant 5 종 의무 본문 (페이즈 06 plan)

```markdown
## Simulation Physical Invariants (bu v0.9.22 의무)

매 시뮬 실행 시 다음 5 invariant 가 매 event 처리 후 *런타임 assert* 의무. 위반 시 시뮬 즉시 중단 + dump frame + last 100 events.

| ID | Invariant | 위반 의미 | 위반 빈도 (cold session) |
|---|---|---|:-:|
| I1 | mass conservation | loaded == dumped + in_transit ± 1 | 0 (의무) |
| I2 | resource exclusivity | 1 loader ≤ 1 truck (LOADING) | 0 |
| I3 | monotonic time | event.time strictly increasing | 0 |
| I4 | bounded queue | \|queue\| ≤ scenario.max_queue_bound | 0 |
| I5 | no-deadlock | WAITING truck has future event scheduled | 0 |

bs §D4 의 도메인 invariant 와 1:1 매핑 — domain truth 가 sim runtime 으로 *자동 변환* 되어 시뮬 진행 중 검증.
```

## 3. frontmatter sync

```yaml
---
simulation_invariants:
  count: 5
  runtime_assert_enabled: true
  domain_mapping_ratio: 1.00              # bs §D4 invariant 와 1:1 매핑
  cold_run_violations: 0                  # 본 시뮬 실행 중 위반 0
  cold_run_event_count: 18432             # 검증된 event 수
sim_correctness_grade: A                  # A (모두 PASS) / B (1 violation, 자동 회복) / C (≥2)
---
```

## 4. self_lint C-SPI 룰

```python
def check_simulation_physical_invariants(artifact_dir: Path) -> list[str]:
    plan = artifact_dir / 'plan' / '06-plan.md'
    impl_log = artifact_dir / 'impl' / '08-impl-log.md'
    errors = []

    if plan.exists():
        body = plan.read_text()
        if 'Simulation Physical Invariants' not in body:
            errors.append('plan/06-plan.md: § Simulation Physical Invariants 부재')
        for inv_id in ['I1', 'I2', 'I3', 'I4', 'I5']:
            if inv_id not in body:
                errors.append(f'plan: invariant {inv_id} 명시 부재')
        fm = parse_frontmatter(plan)
        si = fm.get('simulation_invariants', {})
        if si.get('runtime_assert_enabled') != True:
            errors.append('runtime_assert_enabled != true')
        if si.get('domain_mapping_ratio', 0) < 1.0:
            errors.append('domain_mapping_ratio < 1.0 (bs §D4 매핑 의무)')
        if si.get('cold_run_violations', -1) != 0:
            errors.append(f'cold_run_violations != 0')
        if fm.get('sim_correctness_grade') not in ['A', 'B']:
            errors.append('sim_correctness_grade ∉ {A, B}')

    if impl_log.exists():
        body = impl_log.read_text()
        if 'SimulationInvariantChecker' not in body and 'invariant_checker' not in body:
            errors.append('impl-log: SimulationInvariantChecker 구현 명시 부재')

    return errors
```

## 5. cold session 적용 — Sim correctness 18→20 push

af (분석 상한) + 본 컨벤션 (런타임 invariant) 두 layer :
- af = 결과 *상한* 검증 (예: throughput ≤ N/T)
- bu = 진행 *과정* 검증 (mass / resource / time / queue / deadlock)

bench rubric 의 *Sim correctness* 차원 +2pt 회수 가능 :
- 런타임 invariant 명시 + 검증 로그 → +1pt
- bs §D4 도메인 invariant 와 1:1 매핑 → +1pt

## 6. 안티 패턴

a- **invariant 가 *post-hoc 분석*** — 시뮬 종료 후 검증 X. *매 event 후* 런타임 assert 의무.
b- **violation 시 *log + continue*** — 위반 = 즉시 중단 + dump frame. silent skip 금지.
c- **5 invariant 미커버** — I1~I5 모두 의무. domain-specific invariant 추가는 OK 이지만 5 는 base.
d- **bs §D4 매핑 누락** — domain invariant ≠ sim invariant 분리 → drift. 1:1 매핑 ratio 1.0 의무.

## 7. 호환성

- [`analytical-bound-cross-validation.md`](analytical-bound-cross-validation.md) (af) — closed-form 상한 검증 + 본 컨벤션 런타임 invariant = 두 layer.
- [`domain-model-completeness.md`](domain-model-completeness.md) (bs) — §D4 도메인 invariant 가 본 컨벤션의 입력.
- [`data-structure-invariants.md`](data-structure-invariants.md) (bt) — 데이터 구조 invariant + 본 컨벤션 시뮬 invariant = 정적 vs 동적.
- [`test-invariants.md`](test-invariants.md) (n) — 테스트 invariant + 본 컨벤션 = 테스트 시점 vs 시뮬 런타임.
