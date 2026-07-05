---
id: conservative-margin-judging
category: meta
applies-to-phases: '[06,08,09,10]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'any tournament / shadow grader / sprint stop scoring'
indexed-in: conventions/INDEX.md
---

# Conservative margin judging (`conservative-margin-judging`) — 보수적 prior 로 심사하되 측정값 그대로 보고 (sprint-30, 설계 B2 §2.2-5 재작성)

## 한 줄 요약

**모든 내부 judge(plan tournament / impl tournament / shadow grader / sprint stop / phase exit gate)는 보수적 prior 로 채점한다 — 더 개선 여지가 있다고 먼저 가정하고 살핀다. 그러나 채점 결과는 rerun 횟수에 따라 깎거나 올려 성형하지 않고 측정값 그대로 보고한다.**

## 폐지된 것 — rerun-별 score cap

구판은 rerun 횟수별 점수 상한(`rerun=0→cap 0.90`, `1→0.95`, `2→0.99`, `>=3→0.999`)을 강제해, 측정값이 얼마든 낮은 rerun 에서는 무조건 깎아 보고하도록 명령했다. 이는 **반대 방향의 점수 성형 강제**다(설계 B2 §2.2 perverse incentive 진단 (iii)) — 방향이 인플레이션이든 디플레이션이든 부정직은 부정직이다. cap 은 삭제한다. `improvement_axes_remaining` frontmatter 의무, rerun=0 시 강제 ≥1 항목 명시도 함께 폐지 — polishing 동력은 [`budget-saturation-loop.md`](budget-saturation-loop.md) §2 의 delta/plateau 룰이 대체한다.

## 존치 — 보수적 prior + 정직 sentinel

- **보수적 prior**: judge 는 1st pass 낙관 채점을 피하고 weakness ≥1 을 실제로 찾아본 뒤 채점한다(과정의 태도이지 결과의 강제 절삭이 아니다).
- **judge 자신감 sentinel**: "winner clear" / "no further improvement" / "clearly best" / "obvious winner" / "definitive" / "passed on first execution" 류 확신 표현이 **근거 없이** 박히면 재검토 대상 — 단, 실측으로 plateau(개선 정지)가 확인된 경우 "정직한 수렴"을 보고하는 것은 sentinel 위반이 아니다(구분: 근거 없는 확신 vs 실측 기반 수렴 보고).
- **측정값 그대로 보고**: cap 도 인플레이션도 없이, judge 가 관측한 값을 그대로 아티팩트에 남긴다.

## 적용 layer

| Layer | 적용 산출물 |
|---|---|
| plan tournament (phase 06) | `plan/tournament-NN.md` |
| impl tournament (phase 08) | `impl/tournament-impl-NN.md` |
| shadow grader (phase 06/08) | `*/shadow-grade-NN.json` |
| sprint stop judge (phase 10) | `sprints/NN/report.json` |
| phase exit gate (phase 09) | `quality/gate_meta_audit.json` |

## self_lint C-CMJ

컨벤션 파일 존재 + 본문 keyword("보수적 prior" / "측정값 그대로 보고" / "judge 자신감 sentinel" / cap 폐지 서술) — 구 키워드(`0.999 마진`, `rerun-별 score cap`)는 폐지 대상 자체이므로 검증 키워드에서 제거(설계 §4 C-CMJ 동기화).

## 안티 패턴

a- **rerun 횟수에 따라 점수를 인위적으로 깎거나 올림** — 방향 불문 성형 금지. 측정값 그대로.
b- **근거 없는 확신 표현이 rerun=0 산출물에 박힘** — 재검토 대상(구분: 실측 plateau 보고는 예외).
c- **judge 가 weakness 탐색 자체를 생략** — 보수적 prior 위반(첫 인상만으로 확정).

## 호환성

- [`plan-tournament-scoring-strict.md`](plan-tournament-scoring-strict.md) — 6-dim weighted scoring, cap 은 얹지 않는다(본 개정으로 제거).
- [`budget-saturation-loop.md`](budget-saturation-loop.md) — polishing 동력은 stop_policy delta/plateau 룰이 담당.
- [`dacapo-mandatory-rerun.md`](dacapo-mandatory-rerun.md) — rerun 은 advisory(신호 있을 때).
