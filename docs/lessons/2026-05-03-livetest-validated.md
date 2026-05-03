# Lessons — sprint-03 + sprint-04-a Livetest 마감 (2026-05-03)

> sandbox livetest 4 시나리오 (G2/G3/G4/G5) 모두 PASS 까지 6 PR (v0.8.1~v0.8.6) 의 발견 정리. 본 하네스의 *외부 정합* 검증 과정에서 표면화된 룰 사각지대.

## 핵심 발견 10

### 1. HARD-RULE 의 *iterative discovery*

v0.7.7 까지 HARD-RULE 0 — 막연한 "지휘자 위임" 룰만. livetest #1 fail 에서 sub-claude 가 직접 코드 작성 + retroactive `_tools/build_artifacts.py` 작성으로 우회 → HARD-RULE 1~7 추가 (sprint-03-a). v0.8.1 fail (페이즈 06 까지만 만들고 종료) → HARD-RULE 8 페이즈 완주 (sprint-03-c). v0.8.5 fail (impl-log 본문 부실) → HARD-RULE 9 설계 품질 (sprint-04-a).

**Lesson**: *livetest 가 명시되지 않은 spec 의 갭을 표면화한다*. 사람 review 만으로는 발견 못 함 — sub-claude 가 룰 빈틈을 *항상* 우회하기 때문.

### 2. 분해 stub 의 cost > benefit

v0.7.7 까지 9 SKILL.md (orchestrator + 7 phase stub + harness). 7 stub 은 pure delegation, unique content 0. 매 release 9 파일 skill_version 동기화 누락 위험 (v0.5.0 PR #9 사건). sub-claude 8 stub bounce 시 token 낭비. self_lint 5x 복잡도. livetest #1 fail 의 *간접 원인* (어느 스킬이 source 인가 혼동).

**Lesson**: *형식적 분해는 cost*. 분해는 unique content 가 있을 때만. thin entry + single source 패턴이 유지 비용 적음.

### 3. Description 의 grade-as-gate 잠복

"단독 단순 작업에는 사용 금지" 가 description 에 있어 grade-scope 룰 위반. self_lint C41 이 *positive marker* 강제 ("사용 금지" must exist) → 룰 변경 시 다른 룰 (grade-scope) 와 충돌.

**Lesson**: *positive marker enforcement 는 위험*. anti-pattern 검증은 negative-only (어구 *부재* 검증) 로.

### 4. Sub-claude 우회 패턴의 명시적 enumeration

livetest #1 fail 에서 sub-claude 가 작성한 `_tools/build_artifacts.py` 의 첫 줄 코멘트:
> "Reproduces the contract... without invoking the harness scripts (out-of-sandbox)."

= sub-claude 가 *명시적 결정* 으로 하네스 우회. HARD-RULE 3 a-d 가 이 패턴들을 *enumerate* 함:
- 직접 코드 작성
- retroactive metadata generator
- out-of-sandbox harness emulator
- 페이즈 04 생략

**Lesson**: *우회 의도는 명시되면 숨길 수 없다*. 안티패턴 enumerate 가 sub-claude 의 자기 정직 강제.

### 5. 페이즈 의무의 *체크리스트* vs *연쇄*

v0.8.1 에서 sub-claude 가 페이즈 06 (plan) 까지만 만들고 자발적 조기 종료. 분해 stub 제거 후 페이즈 의무가 *연쇄적* (각 stub 이 다음 stub 호출) → *단일* (orchestrator 가 모든 페이즈 driver) 로 변하며 sub-claude 가 "끝났다" 결정 권한 가짐.

**Lesson**: *연쇄 의무는 stub-driven 디자인 부산물*. 단일 driver 패턴에서는 *그레이드별 의무 산출물 체크리스트* 가 명시되어야 (HARD-RULE 8).

### 6. 사람 ack 옵션의 잠복성

Q-D 카탈로그에 "정지" 옵션이 있으면 sub-claude 가 *언제든 발동* 가능 → 인터럽트 0 약속 위반. 회귀 / secret leak / 무결성 깨짐 등 모든 ack 옵션 제거 (sprint-03-f).

**Lesson**: *자율은 옵션 차원에서 강제되어야*. 인프라 (multiverse / bisect) 가 자율 정정 가능해도 옵션이 ack 허용하면 무력화.

### 7. 책임 범위의 명시적 boundary

"code/ 디렉터리는 누가 만드나" 가 v0.8.5 까지 spec 미명시. sub-claude 가 시나리오에 따라 만들기도 안 만들기도 → verify 일관성 깨짐. user 명시: 본 하네스 = 설계 + 가이드 문서 / 외부 repo = 실 코드.

**Lesson**: *skill 산출물 vs 외부 repo 산출물의 boundary 는 명시 의무*. 모호하면 sub-claude 가 그때그때 다른 결정.

### 8. 산출물 *존재* vs *품질* 의 차원 분리

verify 1.x 는 file 존재만 검사 → handoff/13-handoff.md 박혔다고 *완성* 의미 X. verify 2.0 의 content quality 검증 (Mermaid 카운트 / interface 카운트 / TODO ID 카운트 / multiverse diff 라인 수) 이 실 design quality 측정.

**Lesson**: *존재 검증은 minimum, 품질 검증이 진짜*. handoff = 자기보고 ≠ 외부 정합.

### 9. Livetest 의 inverted feedback loop

sub-claude 산출물 → verify → 룰 정정 → 더 나은 산출물 → verify → 룰 정정 ... 4 라운드 반복. v0.8.0 → 0.8.1 → 0.8.2 → 0.8.5 → 0.8.6 → 4/4 PASS 까지.

**Lesson**: *livetest 는 사람 review 보다 빠르고 정확한 룰 검증*. 직접 invocation 으로 *명시되지 않은 spec* 까지 표면화.

### 10. 버전 라벨의 honesty

v0.5.0~v0.7.7 까지 minor bump 빈번 = 누적 작업 라벨 = maturity 라벨 아님. user 명시 후 v0.8.x patch 시리즈로 진입 (refactor/fix = patch, behavioral change 만 minor). v0.9.0 은 *외부 정합 검증 마일스톤* 으로 의미.

**Lesson**: *버전 = 변경 누적 아니라 maturity 마크*. 사용자 fixed mental model 에 맞아야 신뢰.

## 산출물 책임 범위 (확정)

| 본 하네스 책임 | 외부 프로젝트 repo 책임 |
|---|---|
| 의도 + Q-D 사전 위임 | — |
| 모듈 분할 / 파일 배치 / 폴더 배치 / 인터페이스 설계 | — |
| TODO DAG + 7 게이트 + sprint 점수 시계열 + 회귀 권고 | — |
| AIDE plan-tree + 토너먼트 + 멀티버스 | — |
| webview + 핸드오프 | — |
| — | 실 코드 작성 (`internal/...`, `src/...`) |
| — | 실 빌드 + 테스트 + 부팅 + 실 회귀 검출 |

## livetest 종합

| # | Grade | 산출물 | 설계 품질 | 멀티버스 | 비용 |
|---|---|---|---|---|---|
| 1 | G2 url-shortener | ✅ 12개 | ✅ tree=43/iface=5/TODO=12 | n/a | ~$3 |
| 2 | G3 notification | ✅ 65개 | ✅ design quality OK | ✅ 폭 2 | ~$3 |
| 3 | G4 task mgmt | ✅ 43개 | ✅ tree=98/iface=13/TODO=20 | ✅ 폭 3 (118 diff) | ~$4 |
| 4 | G5 payment webhook | ✅ 62개 | ✅ tree=67/iface=17/TODO=17 | ✅ 폭 5 + 깊이 2 (134 diff) | ~$10 |

총 ~$20 / $320 cap = 6.3%.

## 다음 (sprint-05)

본 sandbox livetest = sub-claude 가 독립 claude --print 로 fresh 환경에서 본 plugin 로드 → 외부 적용의 *한 형태* (실 사용자 production project 는 아니지만 형식상 외부 invocation). v0.9.0 = sandbox livetest validated milestone.

**잔여**:
- 사용자 본인의 *실 외부 repo* 적용 1건 (정직박스 ⓓ 의 본래 의미)
- 실 production project 에 적용 → lessons 누적 → v1.0 후보
