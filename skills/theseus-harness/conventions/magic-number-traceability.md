# Magic number traceability — 코드 literal → 가정 또는 데이터 출처 매핑 (sprint-18, cb, HARD-RULE 9.dd)

## 한 줄 요약

**코드의 모든 숫자 literal (0/1/2/60/100 같은 프로그래밍 상수 제외) 은 (a) `intent/04-autonomy.md` 의 A_i 가정 또는 (b) CSV/YAML/JSON 데이터 파일 출처에 1:1 매핑.** 미매핑 magic number = silent assumption = 컨셉추얼 모델 결손. 외부 cold session 003 의 `loaded_speed_factor 0.85` 가 graph.py 에 하드코딩 + 컨셉추얼 모델 미언급 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| `au polyglot-code-quality.md` 6 메트릭이 cyclomatic / function_length / nesting / duplicate / lint / format 만 검증 | magic number traceability 차원 부재 → silent assumption 통과 |
| 컨셉추얼 모델에 미언급 hardcoded factor | 도메인 외부에서 검증 불가 → grader -2pt Conceptual modelling |

## 트리거

페이즈 09 quality gate. 모든 grade.

## 알고리즘

1. 모든 `*.py` / `*.go` / `*.ts` / `*.js` / `*.rs` 파일 grep — regex `\b[0-9]+(\.[0-9]+)?\b`.
2. 제외 set: `0`, `1`, `2`, `60` (분 ↔ 초), `100` (퍼센트), `1000` (kilo), `3600` (시간 ↔ 초), `1024`, `255` (byte) — programming constants.
3. 남은 literal 마다 다음 중 하나 의무 :
   - (a) `intent/04-autonomy.md` 의 A-N (assumption N) 항목 본문 인용 — A_i 가정 매핑.
   - (b) CSV/YAML/JSON 데이터 파일 path + 셀 위치 인용 (e.g., `data/loaders.csv:loader_id=L_N,rate=...`).
   - (c) 코드 inline comment `# A1 from autonomy.md` 또는 `# from data/X.csv` 표시.
4. 미매핑 literal ≥ 1 → fail. autonomy.md 또는 데이터 파일에 출처 추가 강제.

## frontmatter (09-quality-gate)

```yaml
magic_numbers_total: <int>
magic_numbers_mapped: <int>
magic_numbers_unmapped: 0
unmapped_literal_locations: []
```

## self_lint C-MNT

컨벤션 파일 존재 + 페이즈 09 본문 "magic-number-traceability" + 제외 set 명시 + A_i 가정 또는 CSV/YAML 매핑 명시.

## 안티 패턴

a- "loaded factor = 0.85 because typical industry standard" — 본문 주석에만 있고 autonomy.md / CSV 어디에도 박지 않음. sprint-18 차단.
b- `MAGIC = 0.85` 상수 추출하지만 그 상수의 *출처* 가 어디에도 없음 — naming 만으로 traceability 0.
c- 데이터 파일에 셀 있지만 코드가 *직접* 0.85 박음 (CSV 안 읽음) → mapping (b) 인척 위장. CSV path 인용은 *코드가 그 파일을 실 읽을* 때만 인정.

## cold session 003 검증

`graph.py`: `LOADED_FACTOR = 0.85` 하드코딩.
`intent/04-autonomy.md`: A1-A8 8 가정 어디에도 0.85 언급 없음.
`conceptual_model.md`: loaded_speed_factor 본문 부재.
→ grader -2pt Conceptual modelling. sprint-18 게이트 적용 시 fail → autonomy.md 에 `A9: empty truck speed factor 1.0, loaded 0.85 — typical mining haul (industry default)` 추가 강제.
