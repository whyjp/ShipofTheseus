# Ship of Theseus — 재귀 멀티 에이전트 코딩 하네스

> **English readers**: see [`README.en.md`](README.en.md) — single-page summary in English.

## 한 줄 요약

**조립을 다시 하든, 부수고 다시 만들든, 결국 처음 의도한 이름으로 불릴 수 있는 결과물을 보장**하는 Claude Code 스킬 묶음. 14 페이즈를 1 entry 스킬 (orchestrator) + 1 source 스킬 (harness) 의 2 SKILL.md 로 운영한다. 진입점은 [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md).

## 현재 성숙도 — 정직 박스 (v0.8.x, *체감 성숙도 0.4~0.5*)

> **v0.8.x 의 라벨은 SemVer 누적이지만 *체감 성숙도는 0.4~0.5 수준*** — 외부 실 프로젝트 적용 1 건도 아직 없음. 라벨 = 마이그레이션 추적, *실 maturity ≠ 라벨*.
>
> **진척 지표 (2026-05-03)**:
> - ✅ 자기 평가 (self_lint 47/47, pytest 106/106, 자기 임계 0.99999 통과)
> - ✅ livetest scenario #1 (G2 url-shortener) v0.8.0 PASS — sub-claude 가 14 페이즈 산출물 11개 정확 생성 (HARD-RULE 정정 후)
> - ✅ livetest scenario #2 (G3 notification backend) v0.8.0 PASS — plan-tree 폭 2 + 토너먼트 + impl + sprint cap 3 + webview 8 탭
> - ⏸ livetest scenario #3 (G4 task management, FE+BE) — 미실행
> - ⏸ livetest scenario #4 (G5 payment webhook) — 미실행
> - ⏸ **외부 실 프로젝트 적용 1건** (정직박스 ⓓ) — 미실행. 본 적용 후 maturity 0.6~0.7 도달 가능.
>
> v1.0 = 외부 적용 ≥ 5 건 + 사각지대 0 + maintainer 외 사용자가 prod 채택. 현재는 그 길의 절반 이전.

> **이전 v0.2.x 정직 박스 본문**: 자기 평가만 통과한 스캐폴드. 외부 실 프로젝트 적용 0 건.
>
> ⓐ `self_lint 35/35 pass`, `sample_score 1.0`, `임계 0.99999 통과` 같은 수치는 **본 저장소의 마크다운·코드 인덱스 정합성·예시 입력 채점 통과** 를 의미합니다 — *LLM 에이전트가 프롬프트를 행동으로 따르는지* 의 외부 실증과 다릅니다.
> ⓑ self_lint 는 *마크다운 텍스트 패턴* 만 검사합니다. "phase 10 본문에 lessons + stagnation 단어가 박혀 있는가" 는 검증되지만, "implementer 에이전트가 *실제로* lesson_pack 을 받아 forbidden 전략을 회피하는가" 는 검증 불가.
> ⓒ **임계 0.999 / 자기 임계 0.99999 는 SLO 가용성이 아닙니다** — 6 차원 rubric 가중평균 + DIP 단독 hard cap 0.6 + 5 hard cap 의 *명명 규칙* 입니다. 외부 사용자에게 "99.999% 신뢰 가능" 으로 오해되지 않도록 본 README 에서 명시.
> ⓓ **v0.3.0 의 유일 시급 목표**: 첫 외부 실 프로젝트 적용 1 건 + 4 메트릭(인터럽트 0 / 14 페이즈 시간 / 의도 일치 / 채택 가능) post-mortem. 그때까지 새 컨벤션·새 도구 추가 동결.
> ⓔ **자기 평가 통과 수치는 OS 무관** — Linux / Mac / Windows 모두에서 `bash scripts/self-check.sh` 또는 `scripts\self-check.bat` 으로 같은 결과 재현. v0.2.1 까지는 한국어 로케일 Windows 에서 cp949 디코딩 비호환으로 재현이 깨져 있었으며 v0.2.2 의 `scoring/conftest.py` + 명시 `encoding="utf-8"` + self_lint C35 가드로 해소.
> ⓕ **외부 차용 메서돌로지 — 거울 원칙** (v0.4.0 신규): oh-my-ralph 등 외부 스킬은 *사각지대 탐지용 거울* 로만 사용. *합성 source 가 아님*. 차용은 본 하네스의 *컨셉 보존* 우선, *직교 차원 입증 시* 만 *기존 한 단락 증강*. 자세한 메서돌로지는 [`PHILOSOPHY.md`](PHILOSOPHY.md) "외부 패턴 차용 메서돌로지" 절. 본 메서돌로지가 v0.3.0 정직 박스 ⓓ 의 *동결 룰* 을 자연스럽게 흡수 — 동결 예외는 *직교 차원 + 기존 증강만* 으로 좁아짐.

## 왜 "테세우스의 배" 인가

배의 모든 판자를 하나씩 갈아 끼워도 같은 배라고 부를 수 있는가 — 이 사고 실험이 본 저장소의 핵심 은유다. 코드는 페이즈마다, 스프린트마다 분해·재조립·재구현되지만, **최초 의도한 타이틀의 결과물이라고 부를 수 있는 신뢰**가 끝까지 유지되어야 한다. 하네스의 모든 게이트와 점수, 회귀 바이섹트는 그 신뢰를 담보하기 위해 존재한다.

깊은 설계 동기, 도자기 장인 비유, Ralph 루프·OhMy 시리즈·우로보로스 합성 근거는 [`PHILOSOPHY.md`](PHILOSOPHY.md) 참조.

## 어떤 작업에 쓰는가

ⓐ **추천 (G3 이상)** — 다중 모듈 / FE+BE 동시 / 도메인이 미정착인 신규 기능 / 회귀 바이섹트가 필요한 장기 리팩터.
ⓑ **거부 (G1)** — 한 줄 수정, 오타 정정, 단일 함수 추가. 본 하네스가 자기 거부 — `intent` 페이즈에서 grade-assess 가 G1 으로 판정되면 호출이 종료된다 ([`conventions/grades.md`](skills/theseus-harness/conventions/grades.md)).
ⓒ **미니 모드 (G2)** — 단일 모듈·단일 스택의 작은 기능. 페이즈 일부 스킵.

## 14 페이즈 파이프라인

| 단계 | 페이즈 | 산출물 |
| ---: | ----- | ------ |
| 00 | 명명 (G3+) | `naming/00-naming.md` |
| 01–05 | 의도·마인드맵·교차 이해·인터뷰·비평 | `intent/01..05*.md` (+ `04-{verification,runtime-prereq}.md`) |
| 06 | TODO DAG 계획 (G3+ AIDE 트리) | `plan/{tournament,06-plan}.md` + `plan/candidates/universe-N/` |
| 07 | 계획 재이해 (G4+) | `plan/07-plan-review.md` |
| 08 | 모듈 구현 (코드+테스트+빌드) | `impl/08-impl-log.md` + 코드 |
| 09 | 7 종 게이트 (의도·범위·SOLID·테스트·FE-BE 패리티·NFR·실 부팅) | `quality/09-quality-gate.md` |
| 10 | 무한 스프린트 루프 (G3+) | `sprints/NN/{report,inputs}.*` |
| 11 | 회귀 바이섹트 (G4+) | `sprints/NN/bisect.md` |
| 12 | bun 인터랙티브 웹뷰 자동 생성 (G3+) | `webview/` (8 탭) |
| 13 | 한 줄 요약 + 점수 시계열 + (자율 시) PR 생성 | `handoff/13-handoff.md` |

페이즈별 활성 그레이드 + 컨벤션은 [`conventions/grades.md`](skills/theseus-harness/conventions/grades.md) 의 매트릭스. 22 컨벤션 + 14 에이전트 + 채점기는 모두 `theseus-harness/` 단일 source.

## 수록 스킬 (2 개, v0.9.0)

| 스킬 | 역할 | 가이드 |
| ---- | ---- | ----- |
| [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) | **사용자 entry point.** HARD-RULE (호출 직후 첫 동작 강제) + 그레이드 처리 인덱스 + harness 동반 의존 명시. | [docs/skills/theseus-orchestrator.md](docs/skills/theseus-orchestrator.md) |
| [`theseus-harness`](skills/theseus-harness/SKILL.md) | **콘텐츠 source of truth.** 22 컨벤션 + 14 페이즈 + 14 에이전트 + 채점기 (`scoring/`) + 템플릿 (`templates/`). | [docs/skills/theseus-harness.md](docs/skills/theseus-harness.md) |

> **v0.9.0 sprint-03-b 단순화** — 이전 9 SKILL.md (orchestrator + harness + 7 phase 분해 stub) 에서 7 phase stub 제거. pure delegation 이라 cost > benefit 으로 판정 (livetest #1 fail 분석). 사용자 entry namespace (`/shipoftheseus:theseus-orchestrator`) 동일.

스킬 간 인터페이스는 산출물 frontmatter ([`conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md)) 가 계약. 페이즈 산출물 fingerprint chain 으로 무결성 검증.

새 스킬은 `skills/<이름>/SKILL.md` 로 추가하고 [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) 에 등록한다.

## 빠른 사용

**기본** — `theseus-orchestrator` 가 14 페이즈를 자동 driver 로:

```
/shipoftheseus:theseus-orchestrator <요구사항>
```

페이즈 04 인터뷰 1회 후 인터럽트 0. 그레이드 매트릭스 + Q-D1~Q-D9 사전 위임 답에 따라 자율 진행.

frontmatter 핑거프린트가 입력 무결성을 검증해야 다음 페이즈 진입한다.

## 설치

상세 안내는 [`INSTALL.md`](INSTALL.md). 가장 단순한 형태:

```bash
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus

# 본인 프로젝트 루트에서 — 9 스킬 일괄 링크
cd /path/to/your/project
mkdir -p .claude/skills
for s in ~/src/shipoftheseus/skills/*/; do
  ln -s "$s" ".claude/skills/$(basename "$s")"
done
```

또는 Claude Code 마켓플레이스 패턴 (본 저장소가 마켓플레이스 + 단일 플러그인 동시 역할 — [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) 등록):

```
/plugin marketplace add https://github.com/whyjp/shipoftheseus
/plugin install shipoftheseus@shipoftheseus
```

## 산출물 위치

모든 산출물은 프로젝트 루트의 `.ShipofTheseus/<프로젝트명>/` 아래에 카테고리·단계·스프린트별로 배치된다. 자세한 트리는 [`skills/theseus-harness/SKILL.md`](skills/theseus-harness/SKILL.md) 의 "산출물 트리" 섹션 참조.

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/00-naming.md
├── intent/01..05*.md
├── plan/06..07*.md
├── impl/08-impl-log.md
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                           # bun + hono + react
└── handoff/13-handoff.md
```

## 자기 평가 (부트스트래핑)

본 하네스는 *자기 자신* 을 같은 게이트로 평가한다 — *내가 너에게 강제하는 것은 나에게도 강제되어야 한다.* 자세한 절차는 [`BOOTSTRAP.md`](BOOTSTRAP.md).

```bash
./scripts/self-check.sh        # linux/mac
scripts\self-check.bat         # windows
```

수행 단계: 35 self_lint 체크 → pytest (score + self_lint) → sample 채점 → 자기 점수 (임계 0.99999) → frontmatter 체인 무결성. 결과는 `.ShipofTheseus/theseus-self/` 에 누적되어 회차 간 점수 시계열로 회귀를 잡는다.

## 더 읽을거리

- [`examples/`](examples/) — 3 시나리오 (evolving-spec / frozen-spec / fix-bug) — 페이즈 04 의 사전 위임 8 답 + Q-D8 verification commands 답 실제 입력 예시.
- [`PHILOSOPHY.md`](PHILOSOPHY.md) — 신뢰 담보의 의미, Ralph 루프·OhMy 시리즈·우로보로스 합성 근거, SOLID/TDD/BDD/DDD/Hexagonal 매핑.
- [`BOOTSTRAP.md`](BOOTSTRAP.md) — 본 하네스로 본 저장소를 평가하는 부트스트래핑 절차, 35 self_lint 체크 목록.
- [`INSTALL.md`](INSTALL.md) — 설치·갱신·트러블슈팅.
- [`docs/skills/`](docs/skills/) — 스킬별 가이드 (역할, 입출력, 단독 호출 시점, 자주 묻는 질문).
- [`skills/theseus-harness/conventions/`](skills/theseus-harness/conventions/) — 21 컨벤션 모듈 (의도·다이어그램·계약·모델·경쟁·자율성·정체 극복·NFR·리소스·체크포인트·테스트·Da Capo·파편화·그레이드·재귀 분해·인덱싱·리줌·PRD).

## 라이선스

MIT. [`LICENSE`](LICENSE) 참조.
