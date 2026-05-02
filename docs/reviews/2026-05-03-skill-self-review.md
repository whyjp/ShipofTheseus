# Sprint-01 자기 리뷰 — 본 하네스 강점 부각 + 거울 매트릭스 + 감산 변경표

> **컨텍스트:** v0.3.0 → v0.4.0 의 부트스트래핑 회차 sprint-01. 본 하네스가 자기 자신에게 *거울 원칙* 을 적용한 첫 회차. 디자인 스펙: [`.ShipofTheseus/theseus-self/sprints/01/00-review-design.md`](../../.ShipofTheseus/theseus-self/sprints/01/00-review-design.md) v4.

## 1. 거울 원칙

상세는 [`PHILOSOPHY.md`](../../PHILOSOPHY.md) "외부 패턴 차용 메서돌로지 — *거울 원칙*" 절. 6 항 ⓐ~ⓕ:

ⓐ **본래 스킬이 1순위** — 기존 14 페이즈 / 28 컨벤션 / 13 에이전트의 컨셉을 *최대한 보존*.
ⓑ **외부 = 참조용 거울** — "본 하네스가 *어디를 놓쳤는지* 외부의 시선으로 발견".
ⓒ **차용 오더 = 자동 합성 면허 아님**.
ⓓ **중복 기능은 중첩 금지**.
ⓔ **상호보완 축 (직교 차원) 만 차용 정당**.
ⓕ **동결 예외** — *직교 차원 + 기존 증강만* 이 동결 예외, *새 파일 추가* 는 동결 그대로.

## 2. Claude Skills Guide 정합 매트릭스 (10 조항)

| 조항 | 본 하네스 대응 | 정합 |
|--|--|--|
| name (lowercase + hyphens) | 9 스킬 모두 | ✓ |
| description (1~2 줄) | v0.4.0 PR-12 로 *압축 완료* — 600자 → 100~150자 | △ → ✓ (PR-12 후) |
| examples | examples/ 3 시나리오 (v0.3.0) | ✓ |
| anti-patterns (when NOT to use) | description + grades.md G1 자동 거부 | ✓ |
| discoverability | description 키워드 + 슬래시 명령 | ✓ |
| tool permissions | 미선언 — *본 하네스 컨셉 정합* | △ (보존, PR-14 선택 적용 시 ✓) |
| HARD-GATE 마크업 | 텍스트 명시 ("하드 룰" 절) — 마크업은 PR-10 선택 | △ (보존) |
| process flow diagram | Mermaid 마인드맵 + 시퀀스 + 자동 웹뷰 | ✓ (오히려 더 풍부) |
| skill priority | theseus-orchestrator 단일 진입점 | ✓ |
| single SKILL.md | *명시 분해* (fragmentation 컨셉) | △ (의도된 trade-off) |

→ 7 직접 정합 + 3 컨셉 trade-off (description 길이는 PR-12 로 부분 해소 / 단일 파일 미준수는 컨셉 보존 / tool permissions 는 PR-14 선택).

## 3. 멀티 스킬 거울 매트릭스

### 3-1. oh-my-ralph (9 원자)

| 원자 | 결정 | 본 하네스 답안 |
|--|--|--|
| RALPH.md 6 섹션 | 드롭 (부록만) | 14 페이즈 + Q-D 8 사전 위임 + frontmatter 봉인 (더 풍부) |
| Verification Commands | 차용 완료 (Q-D8, v0.3.0) | n/a |
| Visual Spec (RALPH.png + clarify-image) | 드롭 | 마인드맵 + Mermaid + 자동 웹뷰 (시각 축 답) |
| .ralph/bootstrap.sh | 기존 증강 (PR-2) | INSTALL.md 한 절 (직교 차원) |
| .ralph/check.sh | 드롭 | scripts/self-check.{sh,bat} 가 답 |
| .ralph/run.sh (wall-clock) | 기존 증강 (PR-3) | resources.md opt-in 한 절 (직교, 컨셉 충돌 명시) |
| .ralph/config | (PR-3 통합) | 위와 통합 |
| Success Criteria 1:1 | 차용 완료 (Q-D8) | n/a |
| Risks 누적 ("Do not remove") | 드롭 | frontmatter 봉인 + 회차 디렉터리 (자동화) |
| 메타 CLI 부재 | 드롭 | orchestrator 가 *의도된* 메타 레이어 |

### 3-2. superpowers (9 원자)

| 원자 | 결정 | 본 하네스 답안 |
|--|--|--|
| HARD-GATE 마크업 | 선택 증강 (PR-10) | "하드 룰" 절 텍스트 (의미는 동일) |
| Skill 자기 호출 계층 | 드롭 | orchestrator → 8 분해 (frontmatter 봉인 자동) |
| Red Flags 안티 패턴 표 | 머스트 증강 (PR-11) | 페이즈별 분산 → 통합 카탈로그로 |
| brainstorming HARD-GATE | 드롭 | grades.md G1 자동 거부 + Phase 04 인터뷰 의무 |
| TDD red-green-refactor | 드롭 | sprint 루프 + PHILOSOPHY ⓐ 매핑 |
| systematic-debugging | 드롭 | Phase 11 회귀 바이섹트 + 멀티버스 (더 풍부) |
| finishing-a-development-branch | 드롭 | Phase 13 핸드오프 |
| verification-before-completion | 차용 완료 (Q-D8) | n/a |
| writing-skills | 무관 | n/a |

### 3-3. OMC (5 원자)

| 원자 | 결정 | 본 하네스 답안 |
|--|--|--|
| agent 카탈로그 | 드롭 | agents/ 13 에이전트 (페이즈 매핑 더 명시) |
| 모델 라우팅 (Opus/Sonnet/Haiku) | 드롭 | conventions/models.md (페이즈별 모델 명시) |
| tier-0 워크플로 (autopilot/ralph/...) | 드롭 | orchestrator 자동 진행 (그레이드별 활성 더 명확) |
| Hooks/system reminder | 무관 | (Claude Code 레이어) |
| Worktree 격리 | 드롭 (부록만) | 산출물 디렉터리 + 멀티버스 분기 (다른 추상) |

### 3-4. autoresearch (4 원자)

| 원자 | 결정 | 본 하네스 답안 |
|--|--|--|
| `Iterations: N` bounded iter | 기존 증강 (PR-3 통합) | grades.md sprint cap + resources opt-in |
| strict evaluator contract | 드롭 | rubric 6 차원 + DIP hard cap + self_lint (더 풍부) |
| markdown decision logs | 드롭 | intent/05-decisions + sprint 디렉터리 + frontmatter 봉인 |
| max-runtime stop behavior | 기존 증강 (PR-3 통합) | resources opt-in 의 on_breach 정책 |

## 4. 본 하네스만의 10 차원 강점 (부각 메인)

| # | 차원 | 본 하네스 답 | 외부 답 |
|--|--|--|--|
| 1 | 부트스트래핑 (자기 적용 + 회차 시계열) | BOOTSTRAP.md + .ShipofTheseus/theseus-self/ + self_lint + 임계 0.99999 | (없음) |
| 2 | 그레이드 시스템 + G1 자동 거부 | grades.md + grade_assess.py + Q-G1 | superpowers HARD-GATE 부분 매핑 |
| 3 | frontmatter 핑거프린트 체인 (페이즈 재진입) | contracts.md + fingerprint.py | (없음) |
| 4 | 35 self_lint 자기 검증 | self_lint.py + scripts/self-check.* | (없음) |
| 5 | 14 페이즈 분해 깊이 | 명명→의도→마인드맵→재이해→인터뷰→비평→계획→재이해→구현→게이트→스프린트→바이섹트→웹뷰→핸드오프 | RALPH.md 6 / autoresearch 단일 보다 풍부 |
| 6 | **합성 패턴의 단단한 흡수** | Ralph + OhMy + 우로보로스 + AIDE + Wiki + Da Capo 6 패턴 명시 차용 + 자기 점수 검증 + 멀티버스 (닥터 스트레인지) | (다른 스킬은 *자신의 패턴* 만, 합성 메서돌로지 부재) |
| 7 | 도자기 장인 — 깨고 다시 빚기 6 차원 트리거 | PHILOSOPHY (DIP / 코드 오류 / 기획-구현 갭 / NFR / 의도 표류 / 정체) | (없음) |
| 8 | DIP 단독 hard cap | quality-gate 5 게이트 + DIP cap 0.6 | (없음 — 다른 스킬은 SOLID 동등) |
| 9 | Phase 04 *유일* 인터럽트 + Q-D 사전 위임 | autonomy.md + Q-D1~D8 | (없음 — autonomy 강한 약속 부재) |
| 10 | bun + hono + react 자동 웹뷰 | webview-builder + Phase 12 + 6 탭 + Mermaid 자동 + TimingHeader | (없음) |

## 5. 본 하네스의 의도된 한계 (컨셉 정당화)

ⓐ description 길이 — PR-12 로 부분 해소 (600 → ~150자), 그러나 *anti-pattern + when-to-use* 절은 보존
ⓑ 단일 SKILL.md 미준수 — fragmentation 컨셉, 보존
ⓒ tool permissions 비선언 — 페이즈별 광범위, PR-14 선택
ⓓ 이미지 입력 미커버 — 텍스트 기반 컨셉
ⓔ Phase 04 외 verification 실행 미요구 — LLM/사용자 책임 분리
ⓕ 메타 CLI 레이어 (orchestrator) — *의도된* 메타

## 6. 감산 변경표 (v4 신규)

> **TBD — Task 10 (PR-8 final) 에서 PR-12, PR-13, PR-11 머지 후 실제 값 채움.**

### 6-1. SKILL.md description 압축 (PR-12)

| 스킬 | 변경 전 (자) | 변경 후 (자) | 압축률 |
|--|--|--|--|
| theseus-harness | TBD | TBD | TBD |
| theseus-orchestrator | TBD | TBD | TBD |
| theseus-intent | TBD | TBD | TBD |
| theseus-plan | TBD | TBD | TBD |
| theseus-implement | TBD | TBD | TBD |
| theseus-quality | TBD | TBD | TBD |
| theseus-sprint | TBD | TBD | TBD |
| theseus-webview | TBD | TBD | TBD |
| theseus-handoff | TBD | TBD | TBD |

### 6-2. 컨벤션 통합 (PR-13)

| 통합 후 | 흡수된 원본 | 영향 라인 | self_lint 갱신 |
|--|--|--|--|
| TBD | TBD | TBD | TBD |

### 6-3. anti-pattern 통합 카탈로그 (PR-11)

| 통합 위치 | 흡수된 페이즈 본문 | 페이즈별 *고유* 실패만 남김 |
|--|--|--|
| TBD | TBD | TBD |

## 7. 다음 회차 후보 (sprint-02 candidates)

ⓐ 첫 외부 실 프로젝트 적용 1 건 + 4 메트릭 post-mortem (정직 박스 ⓓ)
ⓑ 선택 PR-10 (HARD-RULE 마크업) / PR-14 (allowed-tools) 머지
ⓒ 추가 거울 비교 (frontend-design / claude-hud / ...)

## 8. PR 머지 SHA + 영향 표

> **TBD — Task 10 에서 모든 PR 머지 후 실제 SHA + 라인 수 + 영향 파일 채움.**

| PR | SHA | 영향 파일 | +/- 라인 | self_lint 신규 |
|--|--|--|--|--|
| PR-7 메서돌로지 | fe6428d | 2 (PHILOSOPHY, README) | TBD | (없음) |
| PR-8 draft | (this PR) | 1 (docs/reviews/) | (initial) | (없음) |
| PR-1 분해 stub 단독성 | TBD | TBD | TBD | C36 |
| PR-2 INSTALL prep | TBD | TBD | TBD | C37 |
| PR-3 resources opt-in | TBD | TBD | TBD | C38 |
| PR-9 sprint 시계열 | TBD | TBD | TBD | (없음) |
| PR-11 anti-patterns 통합 | TBD | TBD | TBD | C40 |
| PR-12 description 압축 | TBD | TBD | TBD | C41 |
| PR-13 컨벤션 통합 | TBD | TBD | TBD | C42 |
| PR-8 final | TBD | 1 (amend) | TBD | (없음) |

총합 (TBD — Task 10 에서 채움).
