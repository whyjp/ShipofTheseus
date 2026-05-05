# Dead code zero (`dead-code-zero`) — ruff F,ARG,SIM 또는 vulture 위반 0 (sprint-18, cc, HARD-RULE 9.ee)

## 한 줄 요약

**페이즈 09 가 `ruff check --select F,ARG,SIM` 또는 `vulture` 실행, 위반 0 강제.** dead import / dead arg / unreachable / unused-loop-control / 정의됐지만 미사용 함수 모두 차단. 외부 cold session 003 의 `precompute_paths` 정의됐지만 미사용 + `g_data` 파라미터 dead 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| `au polyglot-code-quality.md` 의 lint 메트릭이 ruff 기본 룰만 강제, F/ARG/SIM strict 는 옵셔널 | dead code 가 lint clean 인 채 통과 |
| dead arg 가 grader 의 Sim correctness 직접 -2pt | precompute_paths 정의 + 미사용 = 의도 불명 |

## 트리거

페이즈 09 quality gate. Python 코드 ≥ 1 파일.

## 알고리즘

1. 외부 repo 의 entry directory 에서 `ruff check --select F,ARG,SIM <src_dir>` 실행.
   - **F** rules : F401 (unused import), F811 (redefined), F841 (unused variable), F901 (raise NotImplemented).
   - **ARG** rules : ARG001 (unused function argument), ARG002 (unused method argument), ARG003 (unused class method argument).
   - **SIM** rules : SIM103 (return-condition), SIM118 (key in dict), SIM910 (dict-get-default).
2. 또는 보조: `vulture <src_dir>` (confidence ≥ 80%).
3. 위반 ≥ 1 → fail. 코드 정리 (제거 또는 사용) 강제.
4. 의도적 unused 시 `# noqa: ARGNNN` 명시 + autonomy.md 정당화 의무.

## frontmatter (09-quality-gate)

```yaml
ruff_F_violations: 0
ruff_ARG_violations: 0
ruff_SIM_violations: 0
vulture_high_conf_violations: 0
intentional_unused_with_justification: []
```

## self_lint C-DCZ

컨벤션 파일 존재 + 페이즈 09 본문에 "ruff" + "F,ARG,SIM" + "vulture" + "위반 0" 명시.

## 안티 패턴

a- "이 함수는 future use" — 사용처 없는 코드 스파게티화. sprint-18 차단 — 사용 시점에 추가, 그 전엔 제거.
b- `# pylint: disable` 무차별 — F/ARG/SIM 별 명시 noqa 만 인정.
c- `g_data` 같은 dead arg 가 인터페이스 정의 일관성 위해 필요 — 다른 모듈 시그니처 정합 시에도 ARG noqa + 정당화 의무.
d- `precompute_paths()` 정의 + 어디서도 호출 안 함 — F401/F841 류 detect.

## cold session 003 검증

`graph.py`: `def precompute_paths(graph, scenario): ... return paths` — 정의 후 호출처 0.
`truck.py`: `def truck_proc(env, truck_id, scenario, registry, recorder, rng, g_data):` — `g_data` 본문 사용 0.
→ grader -2pt Sim correctness. sprint-18 게이트 적용 시 ruff F/ARG fail → 정리 또는 noqa+정당화 강제.
