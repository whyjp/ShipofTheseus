---
id: dacapo-frontmatter-schema
category: tournament
applies-to-phases: '[06,08]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'tournament 산출'
indexed-in: conventions/INDEX.md
---

# Da Capo Frontmatter Schema — tournament/shadow-grade/dacapo-rerun 의무 필드 (sprint-16 / v0.9.22)

## 한 줄 요약

**Da Capo Loop 의 산출물 3종 (tournament-NN.md / shadow-grade-NN.json / dacapo-rerun-NN.md) frontmatter 의 *의무 필드* 정의.** [`dacapo-enforcement.md`](dacapo-enforcement.md) (HARD-RULE 9.o) 의 게이트 5 조건이 본 스키마를 입력으로 검증. 외부 cold session 의 tournament.md 가 winner_score / shadow_grader_predicted_score 만 박고 rerun_count / step_d_pass / dacapo_loop_executed 누락한 회귀 정정.

## 1. tournament-NN.md frontmatter 스키마

```yaml
---
skill_name: theseus-harness
skill_version: 0.9.22
phase: 06-tournament                         # 또는 08-tournament-impl
project_id: <proj>
project_run: <run>
fingerprint: sha256:<...>
prev_fingerprint: sha256:<...>
produced_at: <ISO>
producer_agent: planner|implementer

# ── Da Capo Loop 의무 필드 ──────────────────
dacapo_loop_executed: true                    # 의사코드 Step A~D 실행됨
rerun: 00                                     # 0-padded, 첫 시도 = 00
rerun_count: 0                                # 누적 다카포 횟수
grade: G4
multiverse_width: 7
stop_policy_ref: budget-saturation-loop.md    # 구 threshold: 0.999 대체(설계 B2 §2.3) — 정지 권위는 manifest stop_policy
shadow_target: 95
max_rerun: 3                                  # G3=2/G4=3/G5=5

# ── tournament 결과 ───────────────────────────────────────
winner_id: universe-3
winner_score: 0.892
winner_sub_scores:
  cold_recall: 0.85
  dip_strictness: 0.72
  simplicity: 0.95
  test_topology: 0.80
  fe_be_parity: 0.90
  decision_coverage: 0.78
weakest_dim: dip_strictness
weakest_dim_score: 0.72

# ── Step D 결과 (게이트 입력) ─────────────────────────────
step_d_tournament_pass: false                 # winner_score >= threshold
step_d_shadow_pass: false                     # shadow.predicted >= shadow_target
step_d_converged: false                       # AND of above

# ── Step E 결과 (cap 검사) ────────────────────────────────
step_e_cap_reached: false                     # rerun_count >= max_rerun OR budget >= 0.95
budget_used_total: 0.42                       # 0.0~1.0
budget_cap_status: under                      # under | at | over

# ── 승격 정책 (plan.tournament_winner_argmax 입력, v0.9.57) ─
promotion_policy: copy                        # copy | merge (미기재 → copy 기본; merge 는 선언 의무 예외)
merge_sources: []                             # merge 시만: winner 를 포함한 base universe id 목록 (예: [universe-3, universe-1])

# ── 다음 액션 ─────────────────────────────────────────────
next_action: dacapo_rerun                     # converge | dacapo_rerun | budget_bound
fallback_reason: ""                           # BUDGET_BOUND 시만 본문 채움
---
```

**승격 정책 필드(v0.9.57, [`multiverse.fan_out_width`](../checks/multiverse.fan_out_width.json) 폭 강제의 짝 — 병합 소유)**: `promotion_policy`/`merge_sources` 는 *선택* 필드다(미기재 → `copy` 기본이라 하위호환·비휴면). `plan.tournament_winner_argmax` 게이트가 소비한다. `copy` 면 canonical `plan/06-plan.md` 가 winner 후보 `plan/candidates/<winner_id>/06-plan.md` 와 byte-동일이어야 한다(기계적 복사 — 조용한 재작성 차단). `merge`([`competition.md`](competition.md) Δ<0.05/0.02 자동 머지)면 `merge_sources` 에 winner 를 포함한 base universe id 를 선언한다 — 선언 안 하면 copy 로 간주돼 digest 불일치로 FAIL 된다. REQUIRED_TOURNAMENT 에는 넣지 않는다(기존 run false-FAIL 방지; default-copy 가 비휴면 강제).

## 2. shadow-grade-NN.json 스키마

```json
{
  "skill_name": "theseus-harness",
  "skill_version": "0.9.22",
  "phase": "06-shadow-grade",
  "rerun": 0,
  "context_mode": "zero-context",
  "prior_context_token_count": 0,
  "agent_call_id": "<unique fresh sub-agent call id>",
  "subagent_type": "general-purpose",
  "loaded_artifacts": [
    "plan/candidates/universe-3/06-plan.md",
    "plan/candidates/universe-3/meta.md",
    "plan/candidates/universe-3/code-spike.py"
  ],
  "rubric_used": "generic-bench-rubric",
  "rubric_path": "scoring/rubrics/generic-bench-rubric.md",
  "model": "Sonnet",
  "predicted_score": 92,
  "shadow_target": 95,
  "shadow_pass": false,
  "weakest_category": "results_and_interpretation",
  "category_scores": {
    "design_quality": 95,
    "module_decomposition": 94,
    "test_topology": 91,
    "results_and_interpretation": 88,
    "non_functional_requirements": 92
  },
  "produced_at": "<ISO>"
}
```

[`shadow-grader-zero-context.md`](shadow-grader-zero-context.md) 가 zero-context 무결성 보증.

## 3. dacapo-rerun-NN.md frontmatter 스키마

```yaml
---
skill_name: theseus-harness
skill_version: 0.9.22
phase: 06-dacapo-rerun                       # 또는 08-dacapo-rerun
rerun: 01                                    # 0-padded
prev_rerun: 00
prev_winner_id: universe-3
prev_winner_score: 0.892
prev_shadow_score: 92

# ── Step F lesson ─────────────────────────────────────────
weakest_dim_picked: dip_strictness
shadow_weakest_category: results_and_interpretation
evidence_gaps: ["measurement_contract_method_unclear",
                "decision_coverage_branch_b_not_explored"]
lesson_type: "ae interface-first 인터페이스 정의 ≥ 5 추가"
lesson_candidates_considered: [bg, bi, bb, aa, bf, ae]
lesson_applied: |
  universe-3 의 06-plan.md 에 포트 인터페이스 정의 5개 추가:
  - DispatcherPort, RouterPort, ResourcePort, EventLoggerPort, MetricsPort
  - DIP cap 0.6 위반 정정 (cold-read 시 인터페이스 의존만 노출)

# ── Step G anonymize ─────────────────────────────────────
anonymized_prev_winner_id: universe-anon-rerun-01-a
anonymized_artifact: plan/candidates/universe-anon-rerun-01-a/
fresh_seeds_picked: [adapter-first, minimal-subtraction, tdd-topology,
                     strict-layering, branch-b-routing, branch-b-resource]
fresh_universe_count: 6                       # width - 1

produced_at: <ISO>
---
```

## 4. self_lint C-DCL-FRONTMATTER 신규 룰

```python
def check_dacapo_frontmatter_schema(artifact_dir: Path) -> list[str]:
    """tournament-NN.md / shadow-grade-NN.json / dacapo-rerun-NN.md 의무 필드."""
    errors = []

    REQUIRED_TOURNAMENT = [
        'dacapo_loop_executed', 'rerun', 'rerun_count', 'grade',
        'threshold', 'shadow_target', 'max_rerun',
        'winner_id', 'winner_score',
        'step_d_tournament_pass', 'step_d_shadow_pass', 'step_d_converged',
        'step_e_cap_reached', 'budget_used_total',
        'next_action',
    ]
    for tournament_file in (artifact_dir / 'plan').glob('tournament-*.md'):
        fm = parse_frontmatter(tournament_file)
        for field in REQUIRED_TOURNAMENT:
            if field not in fm:
                errors.append(f'{tournament_file.name} frontmatter 의무 필드 부재: {field}')

    REQUIRED_SHADOW = [
        'context_mode', 'prior_context_token_count', 'loaded_artifacts',
        'rubric_used', 'predicted_score', 'shadow_target', 'shadow_pass',
        'weakest_category', 'category_scores',
    ]
    for shadow_file in (artifact_dir / 'plan').glob('shadow-grade-*.json'):
        data = json.loads(shadow_file.read_text())
        for field in REQUIRED_SHADOW:
            if field not in data:
                errors.append(f'{shadow_file.name} 의무 필드 부재: {field}')

    REQUIRED_RERUN = [
        'rerun', 'prev_rerun', 'prev_winner_id', 'prev_winner_score',
        'weakest_dim_picked', 'lesson_type', 'lesson_applied',
        'anonymized_prev_winner_id', 'fresh_seeds_picked',
    ]
    for rerun_file in (artifact_dir / 'plan').glob('dacapo-rerun-*.md'):
        fm = parse_frontmatter(rerun_file)
        for field in REQUIRED_RERUN:
            if field not in fm:
                errors.append(f'{rerun_file.name} frontmatter 의무 필드 부재: {field}')

    return errors
```

## 5. cross-validation — 거짓 frontmatter 차단

agent 가 검증 우회 위해 `dacapo_loop_executed: true` 거짓 박을 가능. cross-validation :

| 거짓 박힘 | 모순 검출 |
|---|---|
| dacapo_loop_executed=true 인데 rerun_count > 0 + dacapo-rerun-NN.md 부재 | C-DCL-RERUN-LOG fail (미등록) |
| step_d_converged=true 인데 winner_score < threshold | C-DCL-WIN-THRESHOLD 산술 검증 |
| step_d_tournament_pass=true 인데 winner_score < threshold | 직접 산술 모순 |
| step_e_cap_reached=true 인데 rerun_count < max_rerun AND budget < 0.95 | 산술 모순 |
| anonymized_prev_winner_id 박힘 인데 candidates/ 디렉터리 부재 | 파일시스템 검증 |
| promotion_policy: merge 인데 merge_sources 부재/winner_id 제외 | plan.tournament_winner_argmax merge_sources_include_winner 검증 |
| winner_id 선언인데 본문 표 argmax ≠ winner (총점 최대 아님) | plan.tournament_winner_argmax winner_argmax_match 재계산 |

self_lint `check_dacapo_frontmatter_consistency()` 가 5 모순 자동 검증.

## 6. 산출물 위치 표

| Phase | tournament | shadow-grade | dacapo-rerun |
|---|---|---|---|
| 06 plan | `plan/tournament-NN.md` | `plan/shadow-grade-NN.json` | `plan/dacapo-rerun-NN.md` |
| 08 impl | `impl/tournament-impl-NN.md` | `impl/shadow-grade-NN.json` | `impl/dacapo-rerun-NN.md` |

NN = 0-padded 2자리. 첫 시도 = 00, 첫 dacapo rerun = 01.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- frontmatter 필드 = 도메인 X (loop 메타 데이터만).
b- cross-validation = 산술 + 파일시스템 검증, 도메인 X.
c- phase 06 / 08 / 02 / 05 / 11 / 13 (multi-phase 활성 시) 모두 동일 스키마 적용 가능.

## 8. 안티 패턴

a- **`rerun_count` 만 박고 `step_d_*_pass` 누락** — gate 게이트가 검증 못 함. 모든 4 step_d 필드 의무.
b- **`fallback_reason: ""` 빈 값으로 BUDGET_BOUND 위장** — 본문 ≥ 1 줄 의무.
c- **`loaded_artifacts: []` 빈 배열로 zero-context 위장** — shadow grader 가 *어떤 산출물을 봤는지* ≥ 1 의무.
d- **`prior_context_token_count` 누락** — context_mode='zero-context' 의 무결성 증거 누락. shadow-grader-zero-context.md 정합.

## 9. 호환성

- [`dacapo-enforcement.md`](dacapo-enforcement.md) (bm) — 본 스키마 5 조건 검증 의무.
- [`shadow-grader-zero-context.md`](shadow-grader-zero-context.md) (bo) — shadow-grade-NN.json 의 prior_context 무결성.
- [`contracts.md`](contracts.md) — 기본 frontmatter 스키마 + 본 스키마 = phase 06/08 tournament 산출물의 완전 스키마.
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) (ad) — anonymized_prev_winner_id 필드 = ad C-TBR-ANON 정합.
