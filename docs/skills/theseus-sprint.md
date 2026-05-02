# theseus-sprint 가이드

## 한 줄 요약

**페이즈 10–11 — 무한 스프린트 루프 (그레이드별 임계 0.95~0.99999) + 회귀 바이섹트 + 정체 감지 + 천정 자동 조정 + 멀티버스.**

본 하네스의 *심장*. 임계 도달까지 자동으로 회귀하며, 사용자 인터럽트 0 을 약속한다.

## 언제 호출하는가

ⓐ orchestrator 가 자동 위임 (quality 직후).
ⓑ 외부에서 받은 quality 산출물로 *스프린트만 다시 돌리고* 싶을 때 — 단독 호출.
ⓒ 회귀 바이섹트만 따로 돌리고 싶을 때 (sprint NN 의 `bisect.md` 만 갱신).

## 호출 형식

```
/theseus-sprint <요구사항>
```

단, *quality 산출물* (`quality/09-quality-gate.md`) 이 존재해야 한다. frontmatter 검증 실패 시 진입 거부.

## 페이즈별 산출물

| 페이즈 | 파일 | 내용 |
| ----- | ---- | --- |
| 10 | `sprints/NN/report.md` | 스프린트 NN 보고서 (점수 + 변경 요약 + 다음 스프린트 계획) |
| 10 | `sprints/NN/inputs.json` | 채점 입력 (score.py 의 입력) |
| 10 | `sprints/NN/score.json` | 채점 결과 (score.py --out) |
| 10 | `sprints/NN/lesson_pack.json` | 정체 감지 시 다음 루프 전달 레슨 |
| 10 | `sprints/NN/unit.json` | 단위 테스트 결과 |
| 10 | `sprints/NN/e2e.json` | E2E 테스트 결과 |
| 11 | `sprints/NN/bisect.md?` | 회귀 바이섹트 결과 (회귀 발견 시만) |
| 11 | `sprints/NN/snapshot/?` | 멀티버스 우주별 스냅샷 (사용 시) |

## 무한 루프의 정지 조건

ⓐ **임계 도달** — 그레이드별 임계 (G3=0.95, G4=0.99, G5=0.999) 를 6 차원 가중평균이 도달.
ⓑ **회귀 발견** — 점수가 *전 스프린트 대비 하락* — 자동 바이섹트 후 사용자 ack 1 회.
ⓒ **정체 감지** — score Δ < 0.005 가 3 스프린트 연속 — `lesson_pack.json` 다음 루프 전달.
ⓓ **천정 도달** — 리소스 천정의 80% 도달 시 Q-D3 사전 위임 자동 매핑 (천정 조정 또는 NFR 재조정).
ⓔ **재구축 트리거** — DIP 단독 cap 위반 또는 깊은 품질 위반 6 차원 중 하나 → `re-architect` 로 페이즈 06 부터 재진입.

## 회귀 바이섹트 (페이즈 11)

스프린트 NN 의 점수가 NN-1 대비 하락하면:

ⓐ NN 의 변경 단위(commit, 모듈, TODO) 를 자동 그룹화.
ⓑ 그룹별로 격리 적용 → 각 그룹 단독으로 점수 측정.
ⓒ 점수 하락의 원인 그룹을 식별 → `bisect.md` 에 기록.
ⓓ 사용자 ack 1 회 (롤백 또는 보완).

자세한 알고리즘은 [`../../skills/theseus-harness/agents/regression-analyst.md`](../../skills/theseus-harness/agents/regression-analyst.md).

## 멀티버스 (닥터 스트레인지 모드)

대형 변경에서 후보가 N 개 동등하게 합리일 때, 격리 병렬 우주를 만들어 동시 진행 — 각 우주에서 점수 측정 후 최고 우주를 본선으로 선정. 자세한 절차는 [`../../skills/theseus-harness/conventions/checkpoints.md`](../../skills/theseus-harness/conventions/checkpoints.md) + [`../../skills/theseus-harness/conventions/competition.md`](../../skills/theseus-harness/conventions/competition.md).

페이즈 04 에서 Q-D6 으로 멀티버스 사용 여부를 확정 — G5 에서 default true.

## 정체 극복 (lessons.md)

같은 류의 실패가 반복되면 (정체 감지) 다음 루프에 `lesson_pack.json` 이 전달된다:

```json
{
  "forbidden_strategies": ["DI 컨테이너 직접 import", "전역 변수로 상태 공유"],
  "rewrite_rule": "auth 모듈 통째 폐기 후 페이즈 06 부터 재진입",
  "stagnation_trigger": "score Δ < 0.005 for 3 sprints",
  "carryover_count": 2
}
```

자세한 룰은 [`../../skills/theseus-harness/conventions/lessons.md`](../../skills/theseus-harness/conventions/lessons.md).

## 천정 자동 조정 (resources.md)

리소스 프로파일 (로컬/K8s/EC2/서버리스) 별로 RPS·latency 천정이 자동 매핑된다. 천정의 80% 도달 시 Q-D3 위임:

ⓐ 천정 상향 (인스턴스 추가, 인프라 변경).
ⓑ NFR 하향 (목표 RPS 낮춤).
ⓒ 아키텍처 변경 (캐시 도입 등).

자세한 룰은 [`../../skills/theseus-harness/conventions/resources.md`](../../skills/theseus-harness/conventions/resources.md).

## 입출력 (단독 호출)

- **입력**: `quality/09-quality-gate.md` (frontmatter 검증 통과 필수).
- **출력**: `sprints/NN/{report,inputs,score,lesson_pack,unit,e2e}.*` + 임계 도달 시 다음 스킬 (`theseus-webview`) 진입.

## 자주 묻는 질문

**Q. 무한 루프가 정말 무한히 도는가?**
A. 아니다. 정지 조건 5 가지 + 그레이드별 최대 스프린트 수 (G5 는 50, G3 는 20). 도달하지 못하면 페이즈 11 이 `re-architect` 트리거.

**Q. 회귀가 발견되면 자동 롤백되는가?**
A. 아니다. `bisect.md` 가 원인을 짚고 사용자 ack 를 1 회 받는다 — 롤백 또는 보완을 사용자가 결정. 자율 권한 4 단계 중 G5 의 일부 케이스에서만 자동 롤백.

**Q. 멀티버스가 디스크/시간을 너무 먹지 않는가?**
A. Q-D6 에서 사용자가 우주 수를 확정 (default G5 에서 3 개, 기타 grade 는 1). 디스크는 `sprints/NN/snapshot/<universe>/` 로 격리.

## 더 읽을거리

- [`../../skills/theseus-sprint/SKILL.md`](../../skills/theseus-sprint/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/agents/regression-analyst.md`](../../skills/theseus-harness/agents/regression-analyst.md) — 회귀 바이섹트 에이전트.
- [`../../skills/theseus-harness/conventions/lessons.md`](../../skills/theseus-harness/conventions/lessons.md) — 정체 극복.
- [`../../skills/theseus-harness/conventions/resources.md`](../../skills/theseus-harness/conventions/resources.md) — 리소스 천정.
- [`../../skills/theseus-harness/conventions/checkpoints.md`](../../skills/theseus-harness/conventions/checkpoints.md) — 체크포인트·멀티버스.
