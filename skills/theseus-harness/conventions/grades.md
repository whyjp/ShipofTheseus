---
id: grades
category: core
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# 그레이드 시스템 — 작업 복잡도별 허들 구조

## 한 줄 요약
**15 페이즈 + 47 컨벤션 풀세트는 *복잡 작업* 의 비용을 정당화하지만, *증명된 단순 작업* 에는 over-engineering.** **default = G4** (본 하네스 호출 자체가 G4+ 의도 신호 — G3 이하 작업은 본 하네스 없이도 진행 가능). 페이즈 01 (의도 + 마인드맵) 의 *다중 신호 카탈로그* 로 그레이드 추정 후 페이즈 04 Q-G1 으로 사용자 확정. **그레이드는 내부 동작 (페이즈/컨벤션/임계/멀티버스/모델 라우팅) 만 모듈레이션 — 진행/거부에 관여하지 않음.**

## 키워드 매칭 폐기

*사용자 원문 키워드 매칭* 알고리즘은 폐기 — 키워드는 도메인 어휘를 추적 못해 잘못된 분류의 직접 원인. **현재**: *페이즈 01 의도 + 마인드맵 다중 신호* 기반 grade 추정.

## 5 그레이드

**임계 컬럼은 폐지 — 정지 권위는 manifest `stop_policy`(설계 B2 §2.2) 단일 소스다.** G5 의 엄격성은 도달 불가 숫자가 아니라 *구조*로 낸다: `plateau_window[G5]=3`(무개선 3회 연속 확인 후에만 정지 — G3/G4 의 2회보다 엄격) + G5 전용 게이팅 체크 셋(frozen.\* 포함 확장).

| Grade | 별칭 | 진입 조건 | 페이즈 | 컨벤션 | 멀티버스 | stop_policy 구조 |
| ----- | ---- | ------ | ------ | -----: | -------- | ---: |
| **1** | Trivial | TBD (v0.5.x 후속) | TBD | 0 | X | TBD |
| **2** | Simple | G3 단순 증명 + mindmap nodes ≤5 + 단일 모듈 + 단일 도메인 용어 — 사용자 ack 의무 | 01+04+06+08+09 (5) | 7 | X | — |
| **3** | Standard | 12 차원 단순 증명 (외부 evaluator X / measured metrics X / multi-scenario X / NFR X / single stakeholder / mindmap 실재 작음) — 사용자 ack 의무. *G3 작업은 본 하네스 없이도 진행 가능 — 본 하네스 가치 부분만 활용* | 00-09 + 10(3 sprint cap) + 13 (12) | 12 | X | plateau_window 2 |
| **4** | **Complex (default)** | **default — 단순함 증명 미달 시 자동.** 본 하네스 호출 자체가 G4+ 의도 신호. escalation trigger (external evaluator / measured value / multi-scenario / domain adapter / FE+BE) 1+ 매칭 시 default 강화 | 15 풀 + sprint regression loop 의무 | 47 | 옵션 (Q-D7=1 시) | plateau_window 2 |
| **5** | Mission Critical | 사용자 *명시 ack* (`safety_critical` 또는 `irreversible_change`) 만 — 자율 키워드 매칭 X | 15 풀 + 빡빡 모드 | 47 + 추가 가드 | 강제 | plateau_window 3(구조 엄격화) |

### 빡빡 모드 (Grade 5 추가 가드)

a- DIP cap 0.6 → 0.4 (위반 시 더 큰 패널티).
b- 회귀 임계 0.05 → 0.02 (작은 회귀도 즉시 페이즈 11 트리거).
c- Q-D 답 옵션 1 (모두 자동) → 옵션 2 (회귀만 자동) 강제.
d- 멀티버스 우주 수 2~3 → 3~5.
e- 페이즈 11 회귀 바이섹트도 자율 적용 — 본 하네스의 핵심 원칙 (페이즈 04 외 인터럽트 0). G5 빡빡 모드라도 ack 강제 안 함, multiverse + bisect 가 자율 정정 인프라.

## 그레이드 추정 알고리즘 — 페이즈 01 다중 신호 (`scoring/grade_assess.py`, v0.9.17)

**호출 시점**: 페이즈 01 (의도 + 마인드맵) 완료 후, 페이즈 04 Q-G1 직전. intent-extractor 가 페이즈 01 산출물 작성 시 부산물로 *grade signals JSON* 를 박는다 (`intent/01-grade-signals.json`).

**핵심 원칙**:
- **default = G4** (본 하네스 호출 자체가 G4+ 의도 신호)
- **G5 상향** = 사용자 *명시 ack* (`safety_critical` / `irreversible_change`) 만 — 자율 키워드 매칭 0
- **G3 하향** = 단순함 *positive 증명* (12 차원 모두 negative + 마인드맵 실재 단순) + 사용자 ack 의무
- **G2 하향** = G3 + 매우 단순 (mindmap nodes ≤ 5 + 단일 모듈 + 단일 도메인 용어)
- **no signals** = G4 보존 (데이터 부재 ≠ 단순함)

### 18+ 신호 카탈로그 (`GradeSignals` dataclass)

페이즈 01 의도 §a~§i 모든 섹션 + 마인드맵을 신호 source 로:

| 출처 | 신호 |
|---|---|
| 마인드맵 ([`mindmap-quality.md`](mindmap-quality.md) §3) | `mindmap_node_count` / `mindmap_axis_count` / `mindmap_max_depth` / `mindmap_external_systems` / `mindmap_domain_nouns` |
| 의도 §a 무엇을 | `observable_results_count` |
| 의도 §c 비목표 | `explicit_non_goals_count` |
| 의도 §d 제약 | `constraint_count` / `explicit_thresholds_count` |
| 의도 §e 유비쿼터스 언어 | `domain_term_count` |
| 의도 §f 스테이크홀더 | `stakeholder_count` |
| 의도 §g 성공 지표 | `success_metric_count` / `measured_metrics_count` |
| 의도 §h 열린 질문 | `open_question_count` |
| 의도 §i Derived NFRs ([`nfr-derivation.md`](nfr-derivation.md)) | `derived_nfr_count` / `qualitative_adjective_count` |
| 외부 평가 / multi-scenario | `external_evaluator` / `multi_scenario` |
| 인터페이스 / 리팩터 | `fe_be_split` / `refactor_scope_module_count` |
| 미션 크리티컬 (사용자 명시 ack 의무) | `safety_critical` / `irreversible_change` |

### G3 → G4 escalation triggers (5 차원, 1+ 매칭 시 G4 강화)

| Trigger | 의미 |
|---|---|
| `external_evaluator` | bench / leaderboard / submission / external review |
| `measured_value_obligation` | numeric metric ≥ 1 |
| `multi_scenario` | multi-scenario 또는 sensitivity matrix |
| `domain_adapter_stack` | 마인드맵 도메인 noun ≥ 1 (어댑터 stack 가능) |
| `fe_be_split` | FE + BE 동시 진행 |

### G4 → G3 하향 — 단순함 *positive 증명* (12 차원 모두 negative)

```
no_explicit_thresholds   no_measured_metrics      no_multi_scenario
no_external_evaluator    no_derived_nfr           single_stakeholder
few_open_questions       mindmap_present (≥1)     mindmap_small (≤10)
mindmap_few_axes (≤2)    no_domain_stack          no_fe_be
```

`mindmap_present` 가 핵심 — *데이터 없음 (no signals)* 은 단순함 증명 X. 마인드맵이 *실재 작은* 경우만 단순으로 인정.

### 사용

```bash
python scoring/grade_assess.py --mindmap-json intent/01-mindmap-signals.json --intent-json intent/01-grade-signals.json
```

또는 직접 신호 입력:

```bash
python scoring/grade_assess.py --signals '{"external_evaluator":true,"measured_metrics_count":5,...}'
```

## Q-G1 — 페이즈 04 의 첫 질의 (모든 그레이드 공통)

페이즈 01 마인드맵 + 의도 다중 신호로 grade_assess.py 가 추정한 결과를 두괄식으로 보여준 뒤 5 보기 객관식 (default = G4):

```
질의: 본 작업의 그레이드를 확정해주세요.

자동 추정: Grade 4 (default — 본 하네스 호출 자체가 G4+ 의도 신호).
        escalation triggers 매칭: [external evaluator, measured value, multi-scenario]
        (또는 단순함 증명 미달 차원 명시)

선택지:
1. Grade 1 (Trivial) — TBD (v0.5.x 후속)
2. Grade 2 (Simple) — 5 페이즈 / 7 컨벤션
3. Grade 3 (Standard) — 12 페이즈 / 12 컨벤션 / stop_policy plateau_window 2
4. Grade 4 (Complex, default) — 15 페이즈 풀 / 47 컨벤션 / stop_policy plateau_window 2 (자동 추정)
5. Grade 5 (Mission Critical) — 빡빡 모드 / stop_policy plateau_window 3(구조 엄격화)
```

G3·G2 하향 선택 시 grade_assess 가 단순함 증명 reasons 를 함께 보여주어 사용자가 *근거 있는* 선택. 답을 `intent/04-grade.md` 에 기록.

## 그레이드의 역할 — 내부 모듈레이션만

a- 그레이드는 *내부 동작 모듈레이션* 만 한다 — 페이즈 수, 컨벤션 적용, 임계, 멀티버스 분기 수, 모델 라우팅 (haiku/sonnet/opus).
b- **진행/거부 결정에는 관여하지 않는다.** 본 하네스는 호출되면 *항상* 진행한다. G1 (Trivial) 도 진행 (단, v0.5.x 후속 PR 에서 G1 의 모듈레이션을 가장 가볍게 정의 예정).
c- self_lint C-GS 룰: grade 단어가 entry/blocked/reject/거부/종료 와 결합된 표현 검출 시 fail.

## 그레이드별 컨벤션 적용 매트릭스

| 컨벤션 | G2 Simple | G3 Standard | G4 Complex | G5 Critical |
| ------ | :------: | :--------: | :--------: | :---------: |
| interview.md | ✅ | ✅ | ✅ | ✅ |
| timing.md | ✅ | ✅ | ✅ | ✅ |
| contracts.md (frontmatter) | ✅ | ✅ | ✅ | ✅ |
| models.md (Opus/Sonnet/Haiku) | ✅ | ✅ | ✅ | ✅ |
| build-and-config.md | ✅ | ✅ | ✅ | ✅ |
| sprint-narrative.md (§4 lessons) | ✅ | ✅ | ✅ | ✅ |
| fragmentation.md | ✅ | ✅ | ✅ | ✅ |
| diagrams.md | ⚠️ 마인드맵만 | ✅ | ✅ | ✅ |
| stack.md | — | ✅ | ✅ | ✅ |
| spec-catalog.md | — | ✅ | ✅ | ✅ |
| resources.md | — | ✅ | ✅ | ✅ |
| autonomy.md | ⚠️ Q-G1만 | ✅ Q-D1-D6 | ✅ Q-D1-D7 | ✅ |
| competition.md | — | — | 옵션 | ✅ 강제 |
| plan-tree.md | — | ✅ (폭 2 / 깊이 1) | ✅ (폭 3 / 깊이 1, 옵션 2) | ✅ 강제 (활성 폭 6 / 깊이 2 — manifest 참조, 격상 폭 9 는 frozen advisory) |
| runtime-prereq.md (Q-D9) | 옵션 | ✅ | ✅ | ✅ + 실 모드 강제 (mock 금지) |
| checkpoints.md | — | — | 옵션 | ✅ 강제 |
| test-invariants.md | — | ✅ | ✅ | ✅ |
| dacapo.md | — | — | ✅ | ✅ |
| spec-catalog (NFR 게이트 6) | — | ⚠️ 일부 | ✅ | ✅ |

## 그레이드별 페이즈 활성화

| 페이즈 | G2 | G3 | G4 | G5 |
| ----- | :-: | :-: | :-: | :-: |
| 00 명명 | — | ✅ | ✅ | ✅ |
| 01 의도 + 마인드맵 | ✅ | ✅ | ✅ | ✅ |
| 02 의도 리뷰 | — | ✅ | ✅ | ✅ |
| 03 콜드 재이해 | — | ✅ | ✅ | ✅ |
| 04 사용자 질의 + Q-G1/Q-D | ✅ | ✅ | ✅ | ✅ |
| 05 비평 | — | ✅ | ✅ | ✅ |
| 06 계획 | ✅ | ✅ | ✅ | ✅ |
| 07 계획 재이해 | — | — | ✅ | ✅ |
| 08 구현 | ✅ | ✅ | ✅ | ✅ |
| 09 게이트 | ✅ | ✅ | ✅ | ✅ |
| 10 스프린트 루프 | — | ⚠️ 3 sprint cap | ✅ 무한 | ✅ 무한 |
| 11 회귀 바이섹트 | — | — | ✅ | ✅ |
| 12 웹뷰 자동 생성 | — | ⚠️ 단순 | ✅ | ✅ |
| 13 핸드오프 | ✅ | ✅ | ✅ | ✅ |

## 그레이드 다운그레이드 권고 (자율)

자동 추정 < 사용자 답 (예: 자동 G2, 사용자 G4) → 본 하네스가 *다운그레이드 권고* :

```
[자율 결정] 자동 추정은 Grade 2 (단일 모듈) 인데 Grade 4 로 진행 선택. 비용 ~5배.
정말 진행하시겠습니까? (페이즈 05 진입 전 마지막 확인)

선택지:
1. 그대로 Grade 4 진행 (사용자 책임)
2. Grade 2 로 다운그레이드
3. Grade 3 절충
```

자동 추정 > 사용자 답 (예: 자동 G4, 사용자 G2) → 본 하네스가 *업그레이드 권고* (위험 명시):

```
[자율 결정] 자동 추정은 Grade 4 (FE+BE) 인데 Grade 2 로 진행 선택. 위험: 다중 모듈
의존이 미검증, FE/BE 패리티 게이트 비활성, 임계 0.95 로 완화.

선택지:
1. 그대로 Grade 2 진행 (위험 본인 부담)
2. Grade 4 로 업그레이드 (자동 추정 채택)
3. Grade 3 절충
```

## 안티 패턴

a- **Grade 판정 없이 풀 14 페이즈 진행** — 단순 작업에 over-engineering. 본 컨벤션 핵심 위반.
b- **Grade 를 진행/거부 게이트로 사용** — 그레이드는 내부 모듈레이션만. G1 답이어도 진행한다.
c- **자동 추정만 믿고 사용자 확정 생략** — Q-G1 은 *모든 그레이드 공통* 의무 질의. 자동 추정은 *후보* 일 뿐.
d- **그레이드 중간 변경** — 페이즈 04 답이 source of truth. 페이즈 05 이후 그레이드 변경은 페이즈 04 재진입 의미.
e- **빡빡 모드 (G5) 인데 Q-D 답이 옵션 1 (최대 자율)** — G5 는 보수적 옵션 강제. 페이즈 04 에서 자동 보정 + 사용자 알림.

## 자기 평가에서의 적용

본 저장소 (`theseus-self`) 의 자기 평가 그레이드 = **Grade 5 (Mission Critical)** — 본 하네스 자체는 *다른 모든 프로젝트의 신뢰 담보 도구* 이므로 가장 빡빡한 표준 적용.

a- stop_policy plateau_window 3 (G5 표준 — 구조 엄격화, 도달 불가 숫자 아님).
b- 모든 26 컨벤션 적용.
c- 멀티버스 강제 (회차마다 분기 가능).
d- DIP cap 0.4 (현재 0.6 보다 빡빡).
e- 회귀 임계 0.02 (현재 0.05 보다 빡빡).

위 강화는 v0.3.0 의 BOOTSTRAP.md 갱신 후보.

## 멀티버스 폭 확장 (sprint-05-b)

본 하네스의 강점 = *다차원 동시진행* (plan-tree N universe + 경쟁 + 머지). 폭이 좁으면 디자인 다양성 부족 — *동급 외부 스킬 (plan-mode 96 / ouroboros 97)* 을 능가하려면 폭 확장 필수.

| Grade | sprint-05-a 까지 (default) | sprint-05-b 후 (확장 default) | 사유 |
|----|:-:|:-:|----|
| G3 Standard | 폭 2 / 깊이 1 | **폭 3 / 깊이 1** | 단일 사이드 작업도 3 디자인 후보 비교 → process/data/sync 등 ≥3 axis |
| G4 Complex | 폭 3 / 깊이 1 | **폭 4 / 깊이 1** | FE+BE 의 본질적 다차원 (frontend stance × backend stance) 표현 |
| G5 Critical | 폭 5 / 깊이 2 | **폭 6 / 깊이 2** | 미션 크리티컬은 6 후보 head-to-head 비교 + 깊이 2 의 자식 분기 |

폭 확장 트레이드오프 :
a- **비용** : 폭 N → planner sub-agent N 회 호출. wall-clock = max(N) (병렬). 토큰 = sum(N).
b- **메모리** : N 병렬 sub-agent 의 메모리 합 → [`resources.md`](resources.md) 의 universe N 병렬 budget profile (sprint-05-b) 가 가드.
c- **머지 복잡도** : 후보 ↑ → tournament resolve 알고리즘 부담 ↑. [`competition.md`](competition.md) 의 자동 머지 알고리즘 (sprint-05-b) 강화로 흡수.

폭 축소 옵션 — 사용자 시간/비용 압박 시 Q-D3 답으로 폭 축소 가능 (G3 폭 2 / G4 폭 3 등). default 만 확장.
