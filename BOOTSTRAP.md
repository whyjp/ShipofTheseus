# 부트스트래핑 — 본 하네스로 본 하네스 평가하기

## 한 줄 요약
**우로보로스의 진짜 발현** — 본 하네스의 평가 절차를 본 저장소 자체에 적용해, 자기 약점을 표면화하고 다음 보완을 부트스트래핑한다. 1차는 사람 손으로, 2차부터는 본 하네스의 슬래시 명령으로.

## 왜 자기 평가가 필요한가

ⓐ 본 하네스는 사용자 프로젝트에 SoC·DIP·게이트·점수를 강제한다. 그렇다면 본 저장소도 같은 게이트를 통과해야 일관성 있다 — *내가 너에게 강제하는 것은 나에게도 강제되어야 한다.*
ⓑ 매 릴리스마다 컨벤션이 늘어난다. 컨벤션끼리 모순되거나 SKILL.md 가 일부 컨벤션을 인덱싱하지 못하는 사고가 누적된다 — 자체 lint 가 그것을 잡는다.
ⓒ 약점은 *밖에서* 보인다. 콜드 리딩한 에이전트가 본 하네스의 의도를 잘못 이해하면, 그건 본 SKILL.md 가 잘못 쓰여 있다는 신호다.

## 자기 평가 산출물 위치

```
.ShipofTheseus/theseus-self/                     # 자기 평가는 여기 (.gitignore 예외)
├── timing/start.json                            # 1차 평가 시작 시각
├── naming/00-naming.md                          # project_id=theseus-self
├── intent/01-intent.md                          # 본 하네스의 약속
├── intent/05-critique.md                        # 1차 자체 비평 — 갭/미스초이스
├── plan/06-plan.md                              # 다음 보완 TODO (다음 PR 후보)
└── quality/09-quality-gate.md                   # 자체 게이트 통과 여부 + 점수
```

## 자체 평가 절차

### 1차 — 사람 손 (이번 PR 의 산출물)

ⓐ 위 트리의 4개 핵심 산출물을 본 저장소를 입력으로 *직접 채운다*. frontmatter 는 [`scoring/fingerprint.py`](skills/theseus-harness/scoring/fingerprint.py) 로 박는다.
ⓑ 1차 산출물의 의의: **부트스트래핑의 초기 데이터** — 다음 회차의 입력이자 reference.

### 2차 이후 — 슬래시 명령

ⓐ Claude Code 세션에서:
```
/theseus-harness 본 저장소(/home/user/ShipofTheseus) 자체를 평가하고 다음 보완 계획을 세운다. 산출물 위치는 .ShipofTheseus/theseus-self/.
```
ⓑ 페이즈 06 (계획) 부터 시작 — 1차 산출물이 입력으로 들어가므로 [`conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md) 의 frontmatter 검증 → 다음 페이즈 진입.
ⓒ 결과: 갱신된 `plan/06-plan.md` + `impl/08-impl-log.md` + 본 저장소에 실제 코드/문서 변경.

### 매 릴리스마다

ⓐ MAJOR/MINOR 릴리스 직전에 자체 평가 회차 실행.
ⓑ 발견된 갭은 다음 릴리스의 PR 백로그.
ⓒ 회차 간 비교는 `.ShipofTheseus/theseus-self/sprints/NN/report.md` 의 점수 시계열로 — 본 하네스가 매 릴리스 *더 단단해지는지* 객관 측정.

## 자체 lint — 객관 측정 도구

[`skills/theseus-harness/scoring/self_lint.py`](skills/theseus-harness/scoring/self_lint.py) 는 **68 룰** 로 본 저장소를 검사 (v0.9.16 시점, 회차마다 새 룰 추가, 부트스트래핑 회귀 누적). v0.9.5 까지 62 룰 + v0.9.6~v0.9.16 sprint 회차마다 신규 컨벤션별 룰 추가 (C-NFR / C-PMF / C-SRL / C-PCR / C-MMC / C-AT-SEQ / C-AT-MP / C-TBR / C-IFP / C-ABV / C-MIF / C-BAF / C-DSI / C-DRS / C-MQG / C-ESD / C-DHS / C-BSL / C-SRO / C-CT / C-SDT / C-EDP / C-CULD / C-RDLR / C-PCQ):

| # | 체크 |
| - | --- |
| C1 | 모든 conventions/*.md 가 첫 두 줄에 # 제목 + "한 줄 요약" |
| C2 | SKILL.md 가 모든 conventions 를 링크 |
| C3 | SKILL.md 가 모든 phases 를 링크 |
| C4 | SKILL.md 가 모든 agents 를 링크 |
| C5 | 모든 agents/*.md 에 "권장 모델:" 줄 |
| C6 | PHILOSOPHY ↔ SKILL 상호 링크 |
| C7 | plugin.json version == SKILL.md frontmatter version |
| C8 | scoring/*.py 컴파일 가능 |
| C9 | INSTALL.md 가 플러그인 매니페스트 언급 |
| C10 | phases 가 자기 짝 agent 를 링크 |
| C11 | skill README 가 모든 conventions 를 노출 |
| C12 | phase 06 시퀀스 다이어그램 동봉 의무 |
| C13 | phase 08 sh + bat 빌드 스크립트 강제 |
| C14 | quality-gate frontmatter 누락 자동 fail 룰 |
| C15 | regression-analyst 가 competition 컨벤션 활용 명시 |
| C16 | competition.md 의 트리거 주체 (critic/plan-reviewer) |
| C17 | 산출물 작성 에이전트 모두 fingerprint.py 호출 |
| C18 | webview-builder Mermaid 자동 렌더 |
| C19 | autonomy convention + cross-references |
| C20 | lessons + stagnation 가 phase10/implementer/planner 박힘 |
| C21 | spec-catalog 가 intent-extractor/clarifier/phase09/template 박힘 |
| C22 | resources + ceiling 가 phase04/phase10/spec-catalog 박힘 |
| C23 | phases 05~13 본문에 사용자 인터럽트 호출 부재 (autonomy 인터뷰-only 룰) |
| C24 | checkpoints + dacapo + Q-D7 박힘 |
| C25 | test-invariants + dacapo (AIDE/Phase V) — dacapo 얇은 인덱스화 |
| C26 | fragmentation policy (SKILL.md 인덱스 형태) |
| C27 | grades 박힘 (grades.md + grade_assess.py + Q-G1) |
| C28 | 8 분해 stub + 단일 source of truth + orchestrator 체이닝 |
| C29 | sub-agents 재귀 분해 (sub-agents.md + dispatch + AIDE 매핑) |
| C30 | indexing (indexing.md + index_builder + 비직렬성 메타) |
| C31 | resume (resume.md + resume.py + state.json + Progress 탭) |
| C32 | 룰 본문 중복 부재 (fragmentation DRY) |
| C33 | PRD 처리 허들 (충실한 PRD 도 인터뷰 스킵 금지) |
| C34 | 깨고 다시 빚기 트리거 다차원 일반화 (DIP 단일이 아닌 6 차원) |
| C35 | scoring/ 의 모든 `subprocess.run(text=True)` + `tempfile.NamedTemporaryFile(mode="w")` 가 `encoding=` 명시 + `conftest.py` 의 `PYTHONIOENCODING=utf-8` 박힘 (Windows cp949 잠재 버그 가드 — 회귀가 아닌 *원래 잠재* 버그) |
| C36 | Q-D8 Verification Commands wired (oh-my-ralph 차용, v0.3.0) |
| C37 | 분해 SKILL.md 의 단독 호출 주장이 본문 점프 의존과 정합 (동반 필요 명시, v0.4.0) |
| C38 | INSTALL.md fresh-user 환경 점검 절 + self-check.{sh,bat} --check-stack-only 모드 (PR-2, v0.4.0) |
| C39 | resources.md opt-in 보조 천정 절 + Q-D3 sub-option (PR-3, v0.4.0) |
| C40 | 안티 패턴 통합 카탈로그 (PR-11, v0.4.0) |
| C41 | description 200자 이하 압축 + anti-pattern 마커 보존 (PR-12, v0.4.0) |
| C42 | interview ← prd-handling 흡수 + dead link 부재 (PR-13, 28→27 컨벤션, v0.4.0) |
| C43 | SKILL.md hard-rule markup (PR-10, v0.4.0) |
| C-PT | plan-tree wiring (5 시드 + G3+ default, v0.6.0) |
| C-RP | runtime-prereq + Q-D9 + 게이트 7 (v0.7.0) |
| C-OD | orchestrator driver HARD-RULE (livetest #1 fail 정정, v0.8.0) |
| C-LINT1 / C-WV1~3 / C-AGENT-IVB / C-TDD-08 | sprint-05-a (v0.9.1) — ruff + viewer 분리 + TDD 5 sub |
| C-MV1~5 | sprint-05-b (v0.9.2) — multiverse 폭 확장 + universe head-to-head + 분기 축 + 자동 머지 + budget profile |
| C-IV1~2 | sprint-05-d (v0.9.4) — interactive-viewer 결과 only + 책임 좁힘 |
| C-RB1 / C-IG1 | sprint-05-e (v0.9.5) — 회귀 4 분류 + plan implementation guidance |
| C-NFR | sprint-05-f (v0.9.6) — NFR derivation 자동 도출 |
| C-PMF | sprint-05-g (v0.9.7) — premortem friction |
| C-SRL / C-PCR | sprint-05-h (v0.9.8) — sprint regression loop + parallel cold review |
| C-MMC | sprint-05-i (v0.9.9) — mindmap centrality |
| C-AT-SEQ / C-AT-MP / C-TBR | sprint-06-a (v0.9.10) — AIDE multiverse 풀 발현 (symmetry + multi-phase + blind rerun) |
| C-IFP | sprint-06-b (v0.9.11) — interface-first parallel impl |
| C-ABV / C-MIF / C-BAF | sprint-06-c (v0.9.12) — analytical bound + multiverse impl fan-out + budget-aware fallback |
| C-DSI / C-DRS / C-MQG / C-ESD | sprint-07 (v0.9.13) — content depth layer (deep semantic + domain stacking + mindmap gardening + ensemble synthesis) |
| C-DHS | sprint-08 (v0.9.14) — Layer 3 결과물 허들 supremacy |
| C-BSL / C-SRO | sprint-09 (v0.9.15) — budget saturation loop + score rubric objectivity |
| C-CT / C-SDT / C-EDP / C-CULD / C-RDLR / C-PCQ | sprint-10 (v0.9.16) — 발현 검증 6 메타 (convention-traceability / sprint-score-delta / evidence-driven-sprint / cross-universe-lesson / regression-derived-lint / polyglot-code-quality) |

실행:
```bash
python skills/theseus-harness/scoring/self_lint.py
# stdout JSON, exit 0 = 모두 통과, 1 = 실패
```

또는 일괄:
```bash
./scripts/self-check.sh        # linux/mac
scripts\self-check.bat         # windows
```

## 자체 게이트 점수 — 임계 0.99999

본 하네스의 자기 평가는 사용자 프로젝트 임계 0.999 보다 한 단계 빡빡한 **0.99999** 를 자기 표준으로 강제한다 — *내가 강제하는 모든 것을 내가 100% 통과한다.*

```bash
python skills/theseus-harness/scoring/self_lint.py --score
```

가중 평균:

```
self_score = 0.40 × lint_score + 0.40 × pytest_score + 0.20 × sample_score
```

ⓐ `lint_score` — self_lint 체크 통과율 (현재 모든 룰 PASS = 1.0)
ⓑ `pytest_score` — test_score.py 의 pytest 통과율 (모두 PASS = 1.0). `compute_self_score` 가 test_self_lint 를 제외해 self-recursion 차단.
ⓒ `sample_score` — `templates/sample-inputs.json` 채점 (현재 1.0)

회차 결과 (v0.9.16): **self_score = 1.000000, 임계 0.99999 통과, 68 룰 모두 PASS, all_ok = True** — 본 저장소 최초 완전 통과. 자세한 회차 보고는 [`.ShipofTheseus/theseus-self/quality/09-quality-gate.md`](.ShipofTheseus/theseus-self/quality/09-quality-gate.md).

## 회귀 개선 사이클 (본 하네스로 본 하네스 회귀)

매 PR 또는 매 릴리스마다:

① `python skills/theseus-harness/scoring/self_lint.py` 실행 → fail 검출
② fail 항목을 페이즈 06 (보완 계획) 의 TODO 로 변환
③ 페이즈 08 (보완 구현) — 실제 phase/agent/convention 본문 갱신
④ self_lint 재실행 → 0 fail 확인
⑤ `--score` 모드로 임계 0.99999 통과 확인
⑥ 실패 영역 발견 시 새 체크를 self_lint 에 추가 (v0.9.16 시점 68 룰 누적, 신규 컨벤션마다 C-XYZ 추가) → ② 로 회귀
⑦ 회차 산출물을 `.ShipofTheseus/theseus-self/sprints/NN/` 로 누적 (다음 회차의 reference)

회차 간 비교는 `quality-gate.md` 의 `self_score` 시계열로 — 본 하네스가 매 릴리스 *더 단단해지는지* 객관 측정.

## 회차 시계열 보존

ⓐ `.ShipofTheseus/theseus-self/` 는 `.gitignore` 의 예외로 커밋 — 회차마다 새 sprint 디렉터리 추가.
ⓑ 디렉터리 명명: `sprints/NN/` (NN = 회차 번호, zero-padded).
ⓒ 각 sprint 에 최소 `quality-gate.md` 와 `inputs.json` (점수 산출 입력) 보존.
ⓓ 점수 시계열 시각화는 향후 `webview/tabs/SelfEval.tsx` 후보 — sprint 점수 라인 차트.

### v0.4.0 자동 시계열 (PR-9 신규)

`scripts/self-check.{sh,bat}` 가 실행 후 자동으로 *최신 sprint 디렉터리* 의 `report.md` 끝에 sprint run 한 줄 (self_score + 임계 + 회귀 여부) 추가. 회차 간 self_score 비교가 *수동 기록 없이* 누적.

```bash
# 한 줄 자동 추가:
## Sprint Run — 2026-05-03T...
- self_score: `1.000000`
- 임계 (theseus-self): `0.99999`
- 회귀: 0 (통과)
```

## 부트스트래핑의 5 단계

① **점화** — 1차 자체 평가 산출물을 사람 손으로 박는다 (이번 PR).
② **lint 자동화** — `self_lint.py` 가 매 PR 의 CI 역할.
③ **첫 회차 갱신** — 슬래시 명령으로 페이즈 06 부터 진입, 다음 PR 후보 도출.
④ **회차 누적** — 매 릴리스마다 점수 시계열 누적, 회귀 발견 시 페이즈 11 적용.
⑤ **메타 안정** — 본 하네스가 자기 게이트를 임계 0.999 로 통과. 그 후에는 외부 사용자 프로젝트에 적용해도 같은 신뢰 수준.

## 한계

ⓐ 본 하네스에는 "실 코드" 가 거의 없으므로 (score.py / fingerprint.py / self_lint.py / webview 스캐폴드) 정통 단위/통합/E2E 테스트 매트릭스를 그대로 적용 불가. self_lint 가 그 빈 자리를 채운다.
ⓑ 사용자 질의 페이즈는 메인테이너에게 향한다 — 본 저장소에서는 PR 리뷰어가 그 역할.
ⓒ 회귀 바이섹트는 git history 와 자체 lint 점수 시계열로 — 일반 프로젝트의 sprint 체크포인트 대신.

## 참고

ⓐ [`PHILOSOPHY.md`](PHILOSOPHY.md) — 신뢰 담보의 의미.
ⓑ [`skills/theseus-harness/SKILL.md`](skills/theseus-harness/SKILL.md) — 본 하네스의 15 페이즈 + 41 컨벤션.
ⓒ [`skills/theseus-harness/conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md) — frontmatter, 단계 재진입.
