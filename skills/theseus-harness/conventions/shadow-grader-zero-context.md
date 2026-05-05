---
id: shadow-grader-zero-context
category: tournament
applies-to-phases: '[06,08]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'step C'
indexed-in: conventions/INDEX.md
---

# Shadow Grader Zero-Context Integrity — 무결성 증거 + cross-validation (sprint-16 / v0.9.22)

## 한 줄 요약

**Step C 의 shadow grader 가 *진짜 zero-context* 였는지 증거를 남긴다.** prior_context_token_count, loaded_artifacts, rubric_path 의무 박음 + cross-validation 으로 winner self-rating 의 *복사* 차단. 외부 cold session 의 shadow_grader_predicted_score=92 가 winner self-rating 89.2 와 거의 동일한 회귀 (zero-context 위반 의심) 정정.

## 1. 결손 진단

[`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) Step C :

```python
shadow = call_shadow_grader(
    rubric       = load_generic_rubric(),
    artifacts    = collect_winner_artifacts(winner, phase),
    model        = 'Sonnet',
    context_mode = 'zero-context',     # ← 무엇이 zero 인가? 증거 어디?
)
```

`context_mode='zero-context'` 가 *문자열 인자* 일 뿐. 실제 fresh sub-agent 가 *기존 conversation 0 토큰* 으로 호출됐는지 *증거 부재*. agent 가 :
- (a) 진짜 fresh sub-agent 호출 → 일반 rubric 으로 객관 점수
- (b) 같은 conversation 안에서 winner 산출물 다시 읽고 self-rating 흉내 → 점수 복사

두 경로 구별 불가. 외부 cold session 에서 winner=0.892 (89.2 환산) + shadow=92 = 거의 일치 → (b) 경로 의심.

## 2. shadow-grade-NN.json 무결성 필드 (의무)

```json
{
  "context_mode": "zero-context",
  "prior_context_token_count": 0,            // 이 호출 직전 conversation 토큰
  "agent_call_id": "<unique fresh call id>", // sub-agent 호출 trace
  "subagent_type": "general-purpose",         // fresh load 보증
  "loaded_artifacts": [                        // 명시적 입력 파일들
    "plan/candidates/universe-3/06-plan.md",
    "plan/candidates/universe-3/meta.md",
    "plan/candidates/universe-3/code-spike.py"
  ],
  "loaded_artifacts_token_count": 4823,       // 본문 토큰 (rubric 별도)
  "rubric_path": "scoring/rubrics/generic-bench-rubric.md",
  "rubric_token_count": 1247,
  "model": "Sonnet",
  "predicted_score": 92,
  "category_scores": { ... },
  "weakest_category": "results_and_interpretation",
  "produced_at": "<ISO>"
}
```

`prior_context_token_count: 0` 강제 — 0 이 아니면 zero-context 위반 (winner 산출물을 conversation 으로 미리 본 sub-agent).

## 3. cross-validation 5 룰

### 룰 1 — predicted_score vs winner_score 큰 차이 의무

```python
def check_shadow_independence(shadow, winner) -> bool:
    """shadow grader 가 진짜 독립인지 점수 차이로 검증."""
    score_diff = abs(shadow['predicted_score'] / 100 - winner['tournament_score'])
    if score_diff < 0.03:    # 3pt 미만 차이 = 의심
        # 너무 일치 → 복사 의심
        flag('shadow_independence_suspicious',
             severity='warn',
             evidence=f'shadow={shadow.predicted_score}, winner={winner.score*100:.1f}, diff={score_diff*100:.1f}pt')
    return score_diff >= 0.03
```

너무 일치하면 self_lint warn. 3pt 이상 차이 권장.

### 룰 2 — weakest_category 재산출 검증

```python
def check_weakest_category_independence(shadow, winner) -> bool:
    """shadow 의 weakest 가 winner sub_scores 의 weakest 와 동일하면 복사 의심."""
    winner_weakest = min(winner.sub_scores.items(), key=lambda x: x[1])[0]
    if shadow['weakest_category'] == winner_weakest:
        flag('weakest_category_copied', severity='warn')
    return shadow['weakest_category'] != winner_weakest
```

shadow 가 *다른 차원* 을 weakest 로 picking 하는 게 자연 — 다른 rubric, 다른 시각. 동일 = 복사 의심.

### 룰 3 — agent_call_id 유니크 의무

```python
def check_unique_agent_call(shadow_files: list[Path]) -> list[str]:
    """모든 shadow-grade-NN.json 의 agent_call_id 가 유니크 의무."""
    call_ids = [json.loads(f.read_text())['agent_call_id'] for f in shadow_files]
    if len(call_ids) != len(set(call_ids)):
        return ['shadow grader call_id 중복 — fresh sub-agent 호출 위반']
    return []
```

매 rerun 마다 fresh sub-agent 호출 의무 → 호출 ID 중복 = 위반.

### 룰 4 — loaded_artifacts ≥ 1 의무

```python
def check_loaded_artifacts(shadow) -> bool:
    """shadow grader 가 *어떤 산출물을 봤는지* 명시 의무."""
    if not shadow.get('loaded_artifacts') or len(shadow['loaded_artifacts']) == 0:
        flag('shadow_no_input', severity='error')
        return False
    return True
```

빈 배열 = 무엇을 채점한 건지 불명 → fail.

### 룰 5 — rubric_path 일반 rubric 의무

```python
def check_rubric_is_generic(shadow) -> bool:
    """shadow rubric 이 generic (cold-bench 정합) 이지 winner 의 self-rubric 아닌지 검증."""
    if shadow.get('rubric_path', '').endswith('-self.md'):
        flag('shadow_rubric_self_referential', severity='error')
        return False
    if 'generic' not in shadow.get('rubric_used', ''):
        flag('shadow_rubric_not_generic', severity='warn')
    return True
```

rubric 자체가 winner self-rubric 이면 self-rating 복사. generic-bench-rubric.md 만 허용.

## 4. self_lint C-DCL-SHADOW-CONTEXT 룰

```python
def check_shadow_grader_zero_context(artifact_dir: Path) -> list[str]:
    """shadow-grade-NN.json 무결성 5 룰."""
    errors = []
    shadow_files = list((artifact_dir / 'plan').glob('shadow-grade-*.json'))

    for sf in shadow_files:
        data = json.loads(sf.read_text())

        # 의무 필드
        if data.get('context_mode') != 'zero-context':
            errors.append(f'{sf.name} context_mode != zero-context')
        if data.get('prior_context_token_count', 1) != 0:
            errors.append(f'{sf.name} prior_context_token_count != 0')
        if not data.get('agent_call_id'):
            errors.append(f'{sf.name} agent_call_id 부재')
        if not data.get('loaded_artifacts'):
            errors.append(f'{sf.name} loaded_artifacts 빈')
        if not data.get('rubric_path'):
            errors.append(f'{sf.name} rubric_path 부재')

    # cross-validation
    errors.extend(check_unique_agent_call(shadow_files))

    # rerun 별 cross
    for sf in shadow_files:
        rerun = parse_rerun_from_name(sf.name)
        tournament = artifact_dir / 'plan' / f'tournament-{rerun:02d}.md'
        if tournament.exists():
            t_fm = parse_frontmatter(tournament)
            shadow = json.loads(sf.read_text())
            score_diff = abs(shadow['predicted_score'] / 100 - t_fm['winner_score'])
            if score_diff < 0.03:
                errors.append(f'{sf.name} shadow vs winner 차이 {score_diff*100:.1f}pt < 3pt — 복사 의심')

    return errors
```

## 5. shadow grader sub-agent 호출 템플릿 (참고)

```python
def call_shadow_grader(rubric_path, artifacts, model='Sonnet'):
    """fresh sub-agent 호출 — conversation 0 토큰 보증."""
    call_id = generate_unique_call_id()
    prompt = render_template('shadow-grader.tmpl',
                              rubric_path=rubric_path,
                              artifacts=artifacts)
    response = Agent(
        subagent_type='general-purpose',     # fresh load
        prompt=prompt,                        # self-contained — conversation 의존 0
        model=model,
    )
    return {
        'agent_call_id': call_id,
        'subagent_type': 'general-purpose',
        'context_mode': 'zero-context',
        'prior_context_token_count': 0,       # fresh sub-agent default
        'loaded_artifacts': artifacts,
        'rubric_path': rubric_path,
        ... parse(response) ...,
    }
```

## 6. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- prior_context_token_count = sub-agent invocation metadata, 도메인 X.
b- agent_call_id 유니크 = trace 데이터, 도메인 X.
c- score 차이 3pt threshold = 통계적 독립성 heuristic, 도메인 X.

## 7. 안티 패턴

a- **`prior_context_token_count: 0` 거짓 박기** — 같은 conversation 의 sub-agent 호출인데 0 박기. agent_call_id 유니크 + subagent_type='general-purpose' cross-check.
b- **shadow rubric 으로 winner self-rubric 사용** — generic 이 아닌 winner 가 만든 rubric → self-rating 복사. rubric_path 검증.
c- **shadow_grade 와 winner 점수 동일** — 차이 0 = 복사 의심. 3pt threshold warn.
d- **loaded_artifacts 거짓 박기** — 본 산출물을 *실제로 읽었는지* token count 로 cross-check.

## 8. 호환성

- [`dacapo-frontmatter-schema.md`](dacapo-frontmatter-schema.md) (bn) — shadow-grade-NN.json 의무 필드 정의.
- [`dacapo-enforcement.md`](dacapo-enforcement.md) (bm) — 게이트 5 조건의 step_d_shadow_pass 가 본 컨벤션 무결성 의존.
- [`grader-in-sprint.md`](grader-in-sprint.md) (be) — shadow grader 의 phase-내 적용. 본 컨벤션 = 무결성 layer.
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) (ad) — anonymize 와 직교 (ad = candidate 익명화, 본 = grader 무결성).

## 9. cold session 검증

`2026-05-05__001_mine_g4/plan/tournament.md` :

```yaml
shadow_grader_predicted_score: 92
winner_score: 0.892   # 89.2 환산
```

차이 = |92 - 89.2| = 2.8pt < 3pt threshold. 본 컨벤션 적용 시 :
- `shadow_independence_suspicious` warn 발생
- shadow-grade-NN.json 부재 → C-DCL-SHADOW-CONTEXT 모든 필드 fail
- agent_call_id 부재 → unique call 검증 불가
- loaded_artifacts 부재 → 무엇을 채점했는지 불명

→ shadow grader 가 *진짜 zero-context* 였는지 증거 0. v0.9.22 적용 시 게이트 reject 후 phase 06 재진입.
