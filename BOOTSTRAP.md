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

[`skills/theseus-harness/scoring/self_lint.py`](skills/theseus-harness/scoring/self_lint.py) 는 11 개 체크로 본 저장소를 검사:

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

ⓐ `lint_score` — 18 self_lint 체크 통과율 (현재 18/18 = 1.0)
ⓑ `pytest_score` — score.py + self_lint 의 pytest 통과율 (현재 16/16 = 1.0)
ⓒ `sample_score` — `templates/sample-inputs.json` 채점 (현재 1.0)

1차 회차 결과: **self_score = 1.000000, 임계 0.99999 통과**. 자세한 회차 보고는 [`.ShipofTheseus/theseus-self/quality/09-quality-gate.md`](.ShipofTheseus/theseus-self/quality/09-quality-gate.md).

## 회귀 개선 사이클 (본 하네스로 본 하네스 회귀)

매 PR 또는 매 릴리스마다:

① `python skills/theseus-harness/scoring/self_lint.py` 실행 → fail 검출
② fail 항목을 페이즈 06 (보완 계획) 의 TODO 로 변환
③ 페이즈 08 (보완 구현) — 실제 phase/agent/convention 본문 갱신
④ self_lint 재실행 → 0 fail 확인
⑤ `--score` 모드로 임계 0.99999 통과 확인
⑥ 실패 영역 발견 시 새 체크를 self_lint 에 추가 (C19+) → ② 로 회귀
⑦ 회차 산출물을 `.ShipofTheseus/theseus-self/sprints/NN/` 로 누적 (다음 회차의 reference)

회차 간 비교는 `quality-gate.md` 의 `self_score` 시계열로 — 본 하네스가 매 릴리스 *더 단단해지는지* 객관 측정.

## 회차 시계열 보존

ⓐ `.ShipofTheseus/theseus-self/` 는 `.gitignore` 의 예외로 커밋 — 회차마다 새 sprint 디렉터리 추가.
ⓑ 디렉터리 명명: `sprints/NN/` (NN = 회차 번호, zero-padded).
ⓒ 각 sprint 에 최소 `quality-gate.md` 와 `inputs.json` (점수 산출 입력) 보존.
ⓓ 점수 시계열 시각화는 향후 `webview/tabs/SelfEval.tsx` 후보 — sprint 점수 라인 차트.

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
ⓑ [`skills/theseus-harness/SKILL.md`](skills/theseus-harness/SKILL.md) — 본 하네스의 14 페이즈.
ⓒ [`skills/theseus-harness/conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md) — frontmatter, 단계 재진입.
