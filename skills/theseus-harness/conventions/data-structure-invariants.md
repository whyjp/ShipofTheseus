---
id: data-structure-invariants
category: planning
applies-to-phases: '[06]'
applies-to-grades: '[all]'
trigger-when: 'data 구조 ≥ 1'
indexed-in: conventions/INDEX.md
---

# Data Structure Invariants — Data & topology 만점 push (sprint-16 / v0.9.22)

## 한 줄 요약

**Data & topology 14→15 (-1pt) 정정.** 페이즈 06 의 `plan/06-plan.md` 데이터 구조 ≥ 2 의무 (sprint-05-e) 위에 *invariant + bounds + topology* 명시 추가. 단순 schema 만 박는 게 아니라 *어떤 시점에도 성립하는 조건* + *크기 한계* + *접근 패턴* 까지.

## 1. 데이터 구조 본문 의무 (페이즈 06 plan 강화)

기존 (sprint-05-e) :
```python
@dataclass
class Truck:
    id: str
    state: TruckState
    cargo: float
```

**v0.9.22 추가 의무** — 각 데이터 구조마다 4 항목 본문 :

```python
@dataclass
class Truck:
    """
    Invariants:
      - cargo >= 0 (never negative)
      - cargo <= max_capacity (bounded)
      - state ∈ TruckState (enum strict)
      - id is unique across pool (UUID v4)

    Topology:
      - 1:N with EventQueue (one truck publishes many events)
      - 1:1 with Loader (when state == LOADING)
      - referenced from Dispatcher.pending_queue
      - referenced from RouteGraph.node_assignments

    Access patterns:
      - read: every tick (~1000Hz simulated)
      - write: state transition only (~10Hz per truck)
      - mutated by: Dispatcher.assign / Loader.complete / DumpSite.complete
      - read by: EventLogger / MetricsCollector / WebView

    Bounds:
      - count: ≤ scenario.fleet_size (default 50)
      - lifetime: full simulation (no GC during run)
    """
    id: str
    state: TruckState
    cargo: float = 0.0
```

## 2. plan 본문 의무 추가 표

```markdown
## Data Structure Invariants & Topology (bt v0.9.22 의무)

| 데이터 구조 | Invariants | Topology | Access | Bounds |
|---|---|---|---|---|
| Truck | cargo ≥ 0, cargo ≤ max_cap, state ∈ enum, id unique | 1:N EventQueue, 1:1 Loader (loading) | r every tick, w on transition | count ≤ fleet_size |
| Loader | queue_len ≥ 0, queue_len ≤ max_queue, state ∈ {FREE,LOADING,BLOCKED} | 1:N TruckPool (queueing) | r/w on truck arrival | count ≤ scenario.loader_count |
| EventQueue | heap invariant (min-heap by time), no duplicate (truck_id, event_type, time) | bridge 모든 actor → all consumers | w on publish, r on next() | size ≤ horizon × max_event_rate |
| RouteGraph | DAG (no cycle), distance ≥ 0, all nodes reachable from depot | nodes = {Loader, DumpSite, Depot} edges = travel_time | read-only after init | nodes ≤ scenario.site_count |
```

## 3. frontmatter sync

```yaml
---
data_structures:
  count: 4
  with_invariants_ratio: 1.00            # 모든 구조에 invariant ≥ 1 명시
  with_topology_ratio: 1.00              # 모든 구조에 topology 명시
  with_bounds_ratio: 1.00                # 모든 구조에 bounds 명시
  total_invariants: 14
  total_topology_edges: 9
data_topology_grade: A                   # A (모두 1.0) / B (≥0.75) / C (<0.75)
---
```

## 4. self_lint C-DSI 룰

```python
def check_data_structure_invariants(artifact_dir: Path) -> list[str]:
    plan = artifact_dir / 'plan' / '06-plan.md'
    if not plan.exists():
        return []
    fm = parse_frontmatter(plan)
    body = plan.read_text()
    errors = []

    ds = fm.get('data_structures', {})
    if ds.get('with_invariants_ratio', 0) < 1.0:
        errors.append(f'with_invariants_ratio {ds.get("with_invariants_ratio")} < 1.0')
    if ds.get('with_topology_ratio', 0) < 1.0:
        errors.append('with_topology_ratio < 1.0')
    if ds.get('with_bounds_ratio', 0) < 1.0:
        errors.append('with_bounds_ratio < 1.0')
    if ds.get('total_invariants', 0) < ds.get('count', 0) * 2:
        errors.append('total_invariants < count × 2 (구조당 평균 2 invariant)')

    if 'Data Structure Invariants & Topology' not in body:
        errors.append('§ Data Structure Invariants & Topology 표 부재')
    if 'Invariants:' not in body and 'invariants:' not in body:
        errors.append('각 데이터 구조에 Invariants: docstring 부재')

    if fm.get('data_topology_grade') not in ['A', 'B']:
        errors.append('data_topology_grade ∉ {A, B}')

    return errors
```

## 5. cold session 적용 — Data & topology 14→15 push

본 컨벤션 적용 후 :
- 모든 데이터 구조에 *4 항목 docstring* + *표 1 행* 의무
- bench rubric 의 *Data & topology* 차원 +1pt 회수 (현재 schema 만 → invariant + topology 명시)

## 6. 안티 패턴

a- **invariant 가 *type hint*** — `cargo: float` 는 type, invariant 는 `cargo >= 0`. 별개.
b- **topology 가 *모듈 import 그래프*** — 모듈 ≠ 데이터 구조 관계. *데이터 흐름* 만.
c- **bounds 가 *추상*** — "큰 N" 금지. 정량 한계 (≤ scenario.fleet_size) 의무.
d- **Access patterns 누락** — read/write 빈도 + 누가 mutate vs read 만 명시. 동시성 가드 필요 시 입력.

## 7. 호환성

- [`measurement-contract.md`](measurement-contract.md) (bi) — bounds 가 metric 의 "max possible value" 입력 (saturation 검증).
- [`domain-model-completeness.md`](domain-model-completeness.md) (bs) — D4 도메인 invariant + 본 컨벤션 데이터 구조 invariant = 두 layer (domain semantic vs data-structural).
- [`interface-first-parallel-impl.md`](interface-first-parallel-impl.md) (ae) — 인터페이스 ≥ 5 정의 + 본 컨벤션의 topology 표 = 외부 인터페이스 + 내부 데이터 관계.
