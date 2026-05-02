# Ship of Theseus — 재귀 멀티 에이전트 코딩 하네스

> **English readers**: see [`README.en.md`](README.en.md) — single-page summary in English.

## 한 줄 요약

**조립을 다시 하든, 부수고 다시 만들든, 결국 처음 의도한 이름으로 불릴 수 있는 결과물을 보장**하는 Claude Code 스킬 묶음. 14 페이즈를 8 분해 스킬 + 1 인덱스 스킬 + 1 플래그십(단일 source of truth)으로 파편화해 운영한다. 진입점은 [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) (전체 자동 진행) 또는 [`theseus-harness`](skills/theseus-harness/SKILL.md) (단일 호출).

## 현재 성숙도 — 정직 박스 (v0.2.2)

> **v0.2.x 는 자기 평가만 통과한 스캐폴드입니다. 외부 실 프로젝트 적용 0 건.**
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

| 단계 | 페이즈 | 담당 스킬 | 산출물 |
| ---: | ----- | -------- | ------ |
| 00 | 명명 | `theseus-intent` | `naming/00-naming.md` |
| 01–05 | 의도·마인드맵·교차 이해·인터뷰·비평 | `theseus-intent` | `intent/01..05*.md` |
| 06–07 | TODO DAG 계획·재이해 | `theseus-plan` | `plan/06..07*.md` |
| 08 | 모듈 구현 (코드+테스트+빌드) | `theseus-implement` | `impl/08-impl-log.md` + 코드 |
| 09 | 5 종 게이트 + Phase V 측정 유효성 | `theseus-quality` | `quality/09-quality-gate.md` |
| 10–11 | 무한 스프린트 루프 + 회귀 바이섹트 + 멀티버스 | `theseus-sprint` | `sprints/NN/{report,inputs,bisect}.*` |
| 12 | bun 기반 인터랙티브 웹뷰 자동 생성 | `theseus-webview` | `webview/` (hono + react, 6 탭) |
| 13 | 한 줄 요약 + 점수 시계열 + (자율 시) PR 생성 | `theseus-handoff` | `handoff/13-handoff.md` |

플래그십 [`theseus-harness`](skills/theseus-harness/SKILL.md) 가 위 모든 페이즈의 *콘텐츠 단일 source of truth* — 21 컨벤션 + 14 페이즈 + 13 에이전트 + 채점기. 분해 스킬은 *형태와 인터페이스만* 정의하고 본문을 위임한다.

## 수록 스킬 (9 개)

| 스킬 | 역할 | 가이드 |
| ---- | ---- | ----- |
| [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) | 14 페이즈를 8 분해 스킬로 순차 위임하는 인덱스. 단순 호출은 grade-assess 로 거부 또는 미니 모드로 자동 다운시프트. 사용자 인터뷰는 페이즈 04 한 번. | [docs/skills/theseus-orchestrator.md](docs/skills/theseus-orchestrator.md) |
| [`theseus-intent`](skills/theseus-intent/SKILL.md) | 페이즈 00–05. 명명 + 의도 추출 + 마인드맵 + 콜드 재이해 + 사용자 질의(Q-G1+Q-D1~D7+NFR) + 비평·대안. | [docs/skills/theseus-intent.md](docs/skills/theseus-intent.md) |
| [`theseus-plan`](skills/theseus-plan/SKILL.md) | 페이즈 06–07. TODO DAG 계획 + 시퀀스 다이어그램 + 콜드 재이해. 경쟁 트리거 가능. | [docs/skills/theseus-plan.md](docs/skills/theseus-plan.md) |
| [`theseus-implement`](skills/theseus-implement/SKILL.md) | 페이즈 08. TODO 별 모듈 단위 구현 (코드 + 테스트 + 목 표면 한 호출에). | [docs/skills/theseus-implement.md](docs/skills/theseus-implement.md) |
| [`theseus-quality`](skills/theseus-quality/SKILL.md) | 페이즈 09. 5 게이트 + Phase V 측정 유효성 + frontmatter 검증. | [docs/skills/theseus-quality.md](docs/skills/theseus-quality.md) |
| [`theseus-sprint`](skills/theseus-sprint/SKILL.md) | 페이즈 10–11. 무한 스프린트 루프 (그레이드별 임계 0.95~0.99999) + 회귀 바이섹트 + 정체 감지 + 천정 자동 조정 + 멀티버스. | [docs/skills/theseus-sprint.md](docs/skills/theseus-sprint.md) |
| [`theseus-webview`](skills/theseus-webview/SKILL.md) | 페이즈 12. bun + hono + react 인터랙티브 웹뷰 자동 생성 (6 탭 + Mermaid 자동 렌더 + TimingHeader 라이브). | [docs/skills/theseus-webview.md](docs/skills/theseus-webview.md) |
| [`theseus-handoff`](skills/theseus-handoff/SKILL.md) | 페이즈 13. 한 줄 요약 + 점수 시계열 + 자율 결정 이력 + 웹뷰 실행 명령 + (자율 권한 시) PR 생성. | [docs/skills/theseus-handoff.md](docs/skills/theseus-handoff.md) |
| [`theseus-harness`](skills/theseus-harness/SKILL.md) | **플래그십.** 21 컨벤션 + 14 페이즈 + 13 에이전트 + 채점기를 모두 담은 단일 source of truth. **분해 스킬 없이 단독 호출 가능 — 분해 stub 은 본문이 본 플래그십 점프이므로 fresh user 가 분해 stub 만 설치하면 dead link.** | [docs/skills/theseus-harness.md](docs/skills/theseus-harness.md) |

스킬 간 인터페이스는 산출물 frontmatter ([`conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md)) 가 계약. 검증 실패 시 다음 스킬이 진입을 거부 — 분해의 안전 장치.

새 스킬은 `skills/<이름>/SKILL.md` 로 추가하고 [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) `skills` 배열에 등록한다.

## 빠른 사용

ⓐ **전체 자동 진행 (권장)** — `theseus-orchestrator` 가 14 페이즈를 자동 위임:

```
/theseus-orchestrator <요구사항>
```

ⓑ **단일 호출** — 단일 source of truth 인 `theseus-harness` 직접:

```
/theseus-harness <요구사항>
```

ⓒ **부분 호출 (재진입)** — 외부에서 받은 산출물로 *다음 단계부터*:

```
/theseus-plan       # plan/06 부터, intent 산출물이 입력
/theseus-implement  # impl/08 부터, plan 산출물이 입력
```

frontmatter 핑거프린트가 입력 무결성을 검증해야 진입한다.

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
