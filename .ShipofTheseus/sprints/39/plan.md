# Sprint-39 — 4 패턴 inline (트랙 3)

> 시작: 2026-05-09 (sprint-38 13 PR 마감 직후)
> 직전: sprint-38 트랙 2 마감 (phase 06 6 sub-phase + phase 07 3 sub-phase + phase 08.f + self_lint 125)
> 우선순위: **트랙 3 → 외부 적용 (sprint-40)**

본 sprint = sprint-37 plan.md §3.3 의 **트랙 3 (4 패턴 inline)** 정식 진행.

---

## 0. 배경 — 94 plateau 4 감점 메타 패턴

sprint-37 plan §0 의 4 감점 (simulation-bench 회차) 의 메타 패턴 :

| 패턴 | 사례 | 본질 |
|---|---|---|
| **A. PNC** (Plumbed-Not-Consumed) | warmup_minutes 필드 정의 ✓ / 사용 ✗ | 정의 layer ↔ 실효 사용 layer 비대칭 |
| **B. Mirror** (Workspace ≠ Deliverable) | 내부 ramp_closed 검증 ✓ / 외부 README 부재 | 내부 압력 강함 / 외부 압력 빈약 |
| **C. Primary-Source** (Proxy-as-Primary) | truck_util = 1 − queue/shift | 형제 metric reformulation 을 1차 측정으로 통과 |
| **D. Literal-Forbid** (Letter-by-Fallback) | hardcoded `/mnt/d/...` + fallback | runtime 무해, source rubric 위반 |

본 sprint = 4 패턴을 phase 09 게이트 본문에 *inline* 흡수 (별도 컨벤션 0). cold session 이 매번 4 패턴 검사 의무.

---

## 1. 의도 — 한 줄

phase 09 게이트 본문에 4 패턴 (PNC / Mirror / Primary / Literal) inline → cold session 의 자동 검출 메커니즘.

---

## 2. PR 분할안

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A ★ 본 PR | sprint-39 plan.md | 0 | 0 |
| PR-B | A. PNC inline → phases/09 §PNC | AST 분석 — 정의 ↔ 사용 | C-PNC |
| PR-C | B. Mirror inline → phases/09 §Mirror | internal ↔ deliverable 매니페스트 | C-MIR |
| PR-D | C. Primary-Source inline → phases/09 §Primary | metric source-signal manifest, sibling overlap > 50% warn | C-PRI |
| PR-E | D. Literal-Forbid inline → phases/09 §Literal | forbid directive → regex → deliverable source 검사 | C-LIT |
| PR-F | sprint 마감 v0.9.44 + CHANGELOG | SKILL.md / plugin.json / CHANGELOG | 0 |

self_lint +4 신규 (125 → 129).

---

## 3. 4 패턴 명세

### 3.1 A. PNC (Plumbed-Not-Consumed)

정의: 필드/변수 정의 layer ↔ 실효 사용 layer 의 비대칭.

검사 알고리즘:
- AST 분석 (Python: ast / Go: go/ast / TS: tsc --noEmit + ts-morph)
- dataclass / TypedDict / class field 추출
- 각 field 가 어디서 *읽기* 되는지 (read access) 추적
- read access 0 = PNC 위반 (define-only)

산출: phase 09 게이트 출력 `gate_pnc.json` :

```json
{
  "fields_total": <int>,
  "fields_consumed": <int>,
  "fields_orphan": <int>,
  "violations": [
    {"field": "warmup_minutes", "defined_at": "config.py:L12", "consumed_at": null}
  ]
}
```

게이트: violations 0 의무 (cap_correctness).

### 3.2 B. Mirror (Workspace ≠ Deliverable)

정의: 내부 verification fact ↔ deliverable mirror 의 비대칭.

검사 알고리즘:
- 내부 산출물 (impl/ 안의 verification fact, 예: ramp_closed assert) 수집
- deliverable (handoff/, README.md, 외부 evaluator 입력) 수집
- 매핑 표: 모든 internal fact 가 ≥ 1 deliverable 에 mirror 되어야 함

산출: `gate_mirror.json` :

```json
{
  "internal_facts_total": <int>,
  "mirrored_count": <int>,
  "unmirrored_count": <int>,
  "violations": [
    {"fact": "ramp_closed_after_30min", "internal_loc": "impl/sim.py:L89", "deliverable_mirror": null}
  ]
}
```

게이트: unmirrored_count 0 의무 (cap_results).

### 3.3 C. Primary-Source (Proxy-as-Primary)

정의: 형제 metric reformulation 을 1차 측정으로 통과 (e.g., `truck_util = 1 − queue/shift` — 직접 측정이 아닌 derived).

검사 알고리즘:
- 06.b directives.json 의 `primary` type directive 추출
- 각 primary directive 의 *measurement source* 추적
- sibling metric (formula 안에 다른 metric 인용) 감지
- sibling overlap > 50% 시 warn (proxy 의심)

산출: `gate_primary.json` :

```json
{
  "primary_directives_total": <int>,
  "direct_measured": <int>,
  "proxy_via_sibling": <int>,
  "violations": [
    {"directive": "D-009 (primary)", "metric": "truck_util", "formula": "1 - queue/shift", "sibling_overlap": 0.6}
  ]
}
```

게이트: sibling_overlap > 50% 0 건 의무 (cap_correctness).

### 3.4 D. Literal-Forbid (Letter-by-Fallback)

정의: 06.b directives.json 의 `avoid` type directive 의 *literal* (e.g., hardcoded path / forbidden API) 가 deliverable source 에 등장.

검사 알고리즘:
- avoid directive 추출 (e.g., "no hardcoded paths", "no /mnt/")
- regex 자동 추출 (e.g., `r"/mnt/[a-z]/"`, `r"localhost:[0-9]+"`)
- 모든 deliverable source code grep
- 매치 시 위반

산출: `gate_literal.json` :

```json
{
  "avoid_directives_total": <int>,
  "regex_patterns": [{"directive": "D-005", "pattern": "/mnt/[a-z]/"}],
  "violations": [
    {"directive": "D-005", "pattern": "/mnt/[a-z]/", "match": "/mnt/d/data", "file": "src/loader.py:L42"}
  ]
}
```

게이트: violations 0 의무 (cap_correctness, fallback 무관 — letter-strict).

---

## 4. 산출물 경로 정책 (06.f sanctioned interrupt)

본 plan.md 자체 = 06.f path-policy 정합 (sprint-38 PR-B 적용):
- 후보: `.ShipofTheseus/sprints/39/plan.md` / `skills/theseus-harness/sprints/39/` / mirror 양쪽
- 사용자 결정 (2026-05-09 본 sprint 시작 turn): `.ShipofTheseus/sprints/39/plan.md` (sprint-37/38 동일)

---

## 5. premortem — 사전 부검 (06.e 정합)

| 우려 | 사전 정정 |
|---|---|
| 4 패턴 검사 시 false positive | 각 패턴별 allow_list / skip_pattern frontmatter 의무 (per-project) |
| AST 분석이 언어별 다름 | Python first-class, Go/TS는 sprint-40 외부 적용 시점에 추가. sprint-39 = Python only PoC |
| sibling overlap 50% 임계가 도메인 종속 | 50% = generic default, 어댑터 별 override 가능 |
| Literal-forbid regex 자동 추출 false positive | regex 추출 후 사용자 ack (06.f path-policy 정합) — sprint-39 cold session 시 검증 |

격언:
- **동**: 「過則勿憚改 (과즉물탄개)」 — 잘못된 결과는 *고치는 데 주저 마라*. 4 패턴 검출은 *고침 의무 트리거*.
- **서**: «What gets measured gets managed.» (Drucker) — 4 패턴이 *측정* 되어야 *관리* 가능.

---

## 6. 후속 sprint

| sprint | 트랙 | spec |
|---|---|---|
| sprint-40 | 외부 적용 | simulation-bench 재제출 (94 plateau 극복 검증) — sprint-37/38/39 누적 효과 측정 |
| sprint-41+ | TBD | 외부 검증 결과에 따라 회귀/심화 |

---

## 7. 본 sprint 의 의미 — 메타

3 단계 패러다임 전환의 *3 단계*:
- sprint-37 = 정리 (다이어트, 트랙 1) — 완료
- sprint-38 = 깊이 (본체 강화, 트랙 2) — 완료
- **sprint-39 = 통합 (4 패턴 inline, 트랙 3)** — 진행

3 단계 누적 후 sprint-40 외부 검증으로 본 패러다임 전환 효과 측정.
