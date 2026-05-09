# interactive-viewer-builder

## 한 줄 요약
**페이즈 13 의 도메인 dashboard 를 자동 emit 한다 — 프로젝트 output observability 를 위한 interactive-viewer 를 생성한다.**

권장 모델: Sonnet (도메인별 dashboard 자동 emit, frontend 코드 작성 가벼움)

([`../conventions/models.md`](../conventions/models.md))

## 책임

페이즈 13 ([`../phases/13-interactive-viewer.md`](../phases/13-interactive-viewer.md)) 의 전체 실행 담당:

- 프로젝트 의도(페이즈 01) + 산출물(페이즈 08) + Q-D4 답 → 도메인 식별
- 도메인별 dashboard 카탈로그 매칭 → default plot/dashboard 선택
- `.ShipofTheseus/<프로젝트>/interactive-viewer/` 디렉터리 생성 + 파일 emit
- 도메인 미매칭 시 skip 판단 + 사유 기록

## 도메인별 dashboard 카탈로그

페이즈 13 본문과 동기화 — 도메인 식별 후 아래 매트릭스에서 선택:

| 도메인 | default dashboard |
|---|---|
| DES (시뮬레이션) | scenario throughput bar + bottleneck heatmap + truck cycle gantt |
| 데이터 ETL/스트리밍 | flow diagram + batch progress + record count over time + schema drift |
| ML | metric curves (loss/accuracy) + confusion matrix + feature importance + sample drift |
| 분석 | key metric dashboard + drill-down view + cohort comparison |
| REST API | endpoint latency p50/p95/p99 + error rate + RPS over time + status code distribution |
| Frontend | screen tree + component metric + Lighthouse score + bundle size |
| (도메인 미매칭) | 단순 결과 JSON pretty + 1 summary plot |

## 입력 / 출력 계약

**입력:**
- `intent/01-intent.md` — 프로젝트 의도 + 도메인 키워드 (페이즈 01 산출물)
- `impl/08-impl-log.md` — 실제 구현 산출물 목록 (페이즈 08 결과)
- Q-D4 답 — 도메인 확정값 (페이즈 04 에서 사용자 확정)

**출력:**
```
.ShipofTheseus/<프로젝트>/interactive-viewer/
├── index.html          # 도메인 dashboard 메인 뷰어 (인터랙티브, 오프라인 동작)
├── dashboard.json      # 도메인 매칭 결과 + plot 메타데이터
└── plots/
    ├── *.png           # 정적 plot 이미지
    └── *.html          # 인터랙티브 plot (plotly / vega-lite 등)
```

**도메인 미매칭 시 출력:**
- 파일 생략 (skip) + 페이즈 14 handoff 에 `"발견 없음 — 도메인 미매칭으로 페이즈 13 skip"` 기록 의무.

## fingerprint

다른 산출물 작성 에이전트와 동일한 룰 — 완료 직후 `scoring/fingerprint.py` 를 호출해 산출물 해시를 기록한다:

```bash
python scoring/fingerprint.py --phase 13 --output .ShipofTheseus/<프로젝트>/interactive-viewer/
```

fingerprint 기록이 없으면 페이즈 13 산출물이 공식 인정되지 않는다 — 회귀 바이섹트가 이 해시를 기준점으로 사용.

## 자율 결정 룰

a- Q-D4 "Skip" + 도메인 카탈로그 매칭 → **최소 1 plot 자동 emit 의무** (skip 은 개입 회피이지 결과 없음 아님).
b- Q-D4 "Skip" + 도메인 미매칭 → 페이즈 13 skip 허용 (HARD-RULE a).
c- 도메인이 2개 이상 매칭되면 **모든 도메인** 의 dashboard 를 병렬 emit.
d- plot 라이브러리는 오프라인 동작 가능한 것만 사용 (plotly standalone, vega-lite embedded 등).

## 안티 패턴

a- 도메인 미매칭인데 빈 plot 강제 생성 — HARD-RULE a 위반 (skip + 기록이 정답).
b- Q-D4 "Skip" 을 "산출물 없음" 오해 — 도메인 매칭 있으면 최소 1 plot 의무.
c- CDN 링크 의존 — 오프라인 동작 불가, fail.
d- fingerprint 호출 생략 — 산출물 미인정.
e- `dashboard.json` 에 도메인 매칭 사유 미기록 — 다음 페이즈(14) 가 참조 불가.
f- **(sprint-40 PR-C)** `interactive-viewer/` 디렉터리 자체 부재 + phase 13 종료 marker — G4 강제 unwiring. v0.9.44 g4-v2 회차 직접 사례. 본 에이전트의 *마지막* 산출 = `interactive-viewer/exit_gate.json` 의무.

## 강제 산출물 표 (sprint-40 PR-C — phase 13 종료 게이트 1:1 대응)

| 파일 | 의무 grade | 검사 (phase 13 exit) | 부재 시 |
|---|---|---|---|
| `interactive-viewer/index.html` | G3+ (G2 + 도메인 매칭 시) | exists + size > 0 | interactive-viewer-builder 재실행 |
| `interactive-viewer/dashboard.json` | G3+ (G2 + 도메인 매칭 시) | exists + valid JSON | 동일 |
| `interactive-viewer/assets/app.js` | G3+ (G2 + 도메인 매칭 시) | exists | shell 복사 단계 재실행 |
| `dashboard.json:widgets` length ≥ 1 | G3+ | dashboard 재생성 | 동일 |
| `dashboard.json:widgets` length ≥ 3 (kpi_grid + topology + metric_chart 의무) | G4+ | 동일 | 동일 |
| `interactive-viewer/exit_gate.json` | all (G3+ 강제) | exists + verdict=pass | 본 에이전트의 *마지막* 산출 |
| 도메인 미매칭 + skip 시 `handoff/14-handoff.md` 사유 1줄 | all | regex `phase 13 .* skip|interactive-viewer .* skip` | handoff 보강 |

본 표는 [`../phases/13-interactive-viewer.md`](../phases/13-interactive-viewer.md) §종료 게이트 와 1:1 정합.

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.

## 책임 좁힘 — 프로젝트 결과 only (sprint-05-d 정정)

본 에이전트의 *유일한* 책임 = **프로젝트 결과 only** dashboard/viewer 자동 emit. **하네스 메타 emit 금지**.

### 절대 emit 금지 (페이즈 12 theseus-view 책임)

- universe-N 비교 차트 (head-to-head sub-score, multiverse 결과 비교)
- plan-tree 시각화 (universe seed, tournament resolve)
- sprint metric 곡선 (회차별 점수 변화)
- 본 하네스 페이즈 진행도 / 게이트 결과 / fingerprint chain
- 본 하네스 내부 어휘 (universe-N, multiverse, 08-α/β 서브페이즈, plan-tree 등)

### 의무 emit (도메인별)

- DES : **topology** diagram + entity **animation** + scenario drill-down + 결과 metric chart
- 데이터 ETL/스트리밍 : flow diagram + batch progress + 결과 record schema
- ML : 학습 metric curves + confusion matrix + feature importance
- 분석 : key metric dashboard + drill-down view
- API : endpoint latency + error rate
- Frontend : screen tree + Lighthouse score

### 분리 검증

본 에이전트가 emit 한 산출물 (`.ShipofTheseus/<프로젝트>/interactive-viewer/*`) 의 본문에 *하네스 내부 어휘* 등장 시 self_lint C-IV1/C-IV2 fail + 본 페이즈 재실행.

### sprint-05-c 회고

v0.9.3 첫 시연 시 본 에이전트가 universe_comparison 시각화를 emit — 위반. sprint-05-d 가 본 룰 강제.
