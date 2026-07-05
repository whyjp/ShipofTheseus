# B3 완료 보고 — self_lint 순감 + §11.5(a) 지시질량 재실측 (B3d)

> **작성**: opus (오케스트레이터 실측·검증)
> **일자**: 2026-07-05
> **근거 설계**: `docs/design/2026-07-05-B3-selflint-diet-remeasure-design.md`
> **before-ref**: `d0754f7` (B1 착수 직전 = WP8 dogfood 완료 시점)

---

## 0. 한 줄 요약

B1(커널 배선)·B2(동결 다이어트+임계 재설정)·B3(self_lint 순감+stale 정리) 누적으로
**phase 진입 지시질량이 268,199 → 242,076 bytes (−26,123, −9.7%)** 로 실측 감소했다.
§11.5(a) 성공 지표(지시 질량 감소)는 값으로 충족된다. 커널 게이팅·측정계 무회귀.

---

## 1. §11.5(a) 지시질량 재실측 (before-ref d0754f7 대비)

| 계층 | 파일 | before | after | Δ | % |
|---|---:|---:|---:|---:|---:|
| always-load (HARD-CORE + 양 SKILL) | 3 | 48,919 | 46,823 | −2,096 | −4.3% |
| phases | 16 | 219,280 | 195,253 | −24,027 | **−11.0%** |
| **A+B (진입 지시질량)** | 19 | **268,199** | **242,076** | **−26,123** | **−9.7%** |
| conventions | 90 | 809,152 | 792,816 | −16,336 | −2.0% |
| 전체 (A+B+conventions) | 109 | 1,077,351 | 1,034,892 | −42,459 | −3.9% |

측정 방법(재현): `git show d0754f7:<path>` (before) 와 현재 파일 크기(after) 의 바이트 차.
경로는 posix 정규화(Windows glob 백슬래시 → `/`). 전 계층 순감.

**정직 고지**: B3 설계 투영치(A+B ≤ 241,600, −9.9%) 대비 실측 −9.7% 로 476 bytes 초과.
per-WP 하드 룰("편집 파일 총량 after ≤ before")은 B3a/B3b/B3c 전건 충족했고, A+B 투영치는
게이트가 아닌 예측이었다. B3 자체의 주 순감은 진입질량(−1,380, B1+B2 이후)이 아니라
**측정계**(self_lint −144줄 + 은퇴 스크립트 4파일 −894줄)이며, 이는 A+B 집합 밖이다
(설계가 미리 고지한 대로).

---

## 2. B3 조치 요약 (B3a~B3c)

| WP | 조치 | 값 |
|---|---|---|
| B3a | self_lint 8룰 삭제(각 대체 커널 CheckSpec id 또는 미구현 grep-0 근거 1:1) + 수정존치 2 + ID 리네임 2 + 짝 prose 귀속 정리 | self_lint 3,374→3,230줄, 등록 126→118 |
| B3b | 9.rr stale 은퇴 — phase 09/orchestrator 서술·runtime_guard_chain hook·phase_invoke_audit 맵 정정 + `cold_session_artefacts.py`·`generate_sprint40_artefacts.py`+테스트 4파일 물리삭제(참조 0 확인 후) | 순 −962줄 |
| B3c | 가짜 self_lint 귀속 51개 id 정리(44파일, "미등록" 표기, 내용·화이트리스트 존치) | 순감 −16B, CRLF 0 |

**보수 원칙 준수**: 삭제 self_lint 룰 전건에 대체 커널 체크 또는 미구현 근거 1:1(무게이트
공백 0); `check_cold_session.py` 는 `measure_cold_isolation` 라이브러리 사용처라 존치(호출만
정정); 가짜 귀속은 귀속어만 제거하고 내용 룰 존치.

---

## 3. B3 완료 게이트 (전 조건 값 충족)

| 조건 | 결과 |
|---|---|
| self_lint `all_ok` | ✅ EXIT=0 |
| 등록 룰 수 | ✅ 118 (설계 목표) |
| self_lint.py 줄수 | ✅ 3,230 (≤3,230 목표) |
| pytest scoring 전건 | ✅ 486 passed (은퇴 스크립트 테스트 −13) |
| manifest drift-check | ✅ `{"ok": true, "problems": []}` |
| dogfood verdict 불변 | ✅ clean-tree verdict=fail / PASS=5 / measured_backed=8 |
| B1d 발화 리허설 재실행 | ✅ test_run_gate 포함 486 passed(커널 게이팅 왕복 보존) |
| 편집 md 총량 ≤ before | ✅ per-WP 전건 충족 |
| CRLF 오염 | ✅ 0건 (LF 유지) |

---

## 4. 이 재실측이 증명/미증명하는 것

**증명**: B1~B3 로 phase 진입 지시질량이 값으로 감소(−9.7%)했고, 커널 게이팅·dogfood
verdict·전 테스트가 무회귀다. §11.5(a) 의 두 성공 지표 중 (a) 지시 질량 감소는 충족.

**미증명(가설)**: (b) 외부 벤치 점수 개선은 이 재실측으로 확증되지 않는다 — 외부 evaluator
부재. 지시질량 감소가 외부 점수를 실제로 올리는지는 **B4 드레스 리허설 후 벤치마크로만**
확증된다(개선-여지 평가 §4 명시). 본 문서는 내부 지시질량 감소만 값으로 보고한다.

---

*sufficiency bar: B1 ✅ · B2 ✅ · B3 ✅ · B4(풀 파이프라인 드레스 리허설) 대기 → 그 후 벤치마크.*
