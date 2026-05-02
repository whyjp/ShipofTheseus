# theseus-plan 가이드

## 한 줄 요약

**페이즈 06–07 — TODO DAG 계획 + 콜드 재이해.** intent 산출물을 입력으로 받아 모듈 단위 작업 그래프를 만들고, 시퀀스 다이어그램을 동봉한다.

## 언제 호출하는가

ⓐ orchestrator 가 자동 위임 (intent 직후).
ⓑ 외부에서 받은 의도 산출물로 *계획부터 다시 시작* 하고 싶을 때 — 단독 호출.
ⓒ 기존 계획이 부족해 재작성이 필요할 때 (산출물 frontmatter 의 `phase: 06` 으로 재진입).

## 호출 형식

```
/theseus-plan <요구사항>
```

단, *intent 산출물* (`naming/00`, `intent/01..05*`) 이 `.ShipofTheseus/<프로젝트>/` 에 존재해야 한다. 본 스킬이 frontmatter 검증을 수행하고, 실패 시 진입을 거부한다.

## 페이즈별 산출물

| 페이즈 | 파일 | 내용 |
| ----- | ---- | --- |
| 06 | `plan/06-plan.md` | TODO DAG (모듈 → TODO → 의존 엣지) + 시퀀스 다이어그램 + 페이즈 V 측정 계획 |
| 07 | `plan/07-plan-review.md` | 콜드 재이해 (다른 에이전트가 06 을 처음 본 것처럼 검토) + 미스초이스 감지 |

## TODO DAG 형식

```
TODO-001  module=auth          deps=[]
TODO-002  module=auth          deps=[TODO-001]
TODO-003  module=order         deps=[TODO-002]
TODO-004  module=order-fe      deps=[TODO-003]
```

각 TODO 는 페이즈 08 (구현) 의 *모듈 단위 호출* 기준이 된다. DAG 깊이가 깊어지면 [`../../skills/theseus-harness/conventions/sub-agents.md`](../../skills/theseus-harness/conventions/sub-agents.md) 의 재귀 분해 규칙에 따라 서브 에이전트로 위임.

## 시퀀스 다이어그램 (의무)

페이즈 06 산출물은 *반드시* Mermaid 시퀀스 다이어그램을 동봉한다 (self_lint C12 강제). 마인드맵 → 유즈케이스 → 시퀀스의 진화는 [`../../skills/theseus-harness/conventions/diagrams.md`](../../skills/theseus-harness/conventions/diagrams.md).

## 경쟁 트리거

플래너가 단일 후보로 결정하기 어려운 경우 (예: 여러 아키텍처 옵션이 동등하게 합리), `competition.md` 의 격리 병렬 경쟁을 트리거한다 — N 후보를 격리 병렬로 만든 뒤 자동 resolve. 자세한 절차는 [`../../skills/theseus-harness/conventions/competition.md`](../../skills/theseus-harness/conventions/competition.md).

## 입출력 (단독 호출)

- **입력**: `naming/00-naming.md` + `intent/01..05*.md` (frontmatter 검증 통과 필수).
- **출력**: `plan/06-plan.md` + `plan/07-plan-review.md`. 다음 스킬 (`theseus-implement`) 이 입력으로 받음.

```bash
# 외부에서 받은 intent 산출물 검증
python skills/theseus-harness/scoring/fingerprint.py verify --file .ShipofTheseus/<프로젝트>/intent/01-intent.md
python skills/theseus-harness/scoring/fingerprint.py chain --dir .ShipofTheseus/<프로젝트>/
```

## 자주 묻는 질문

**Q. 페이즈 06 만 하고 07 은 스킵해도 되는가?**
A. 안 된다. 07 의 콜드 재이해가 06 의 미스초이스를 잡는 *방어 테스트* — orchestrator 가 강제. 단독 호출 시에도 본 스킬은 06 + 07 을 묶어 진행한다.

**Q. TODO DAG 가 너무 커지면?**
A. `sub-agents.md` 의 깊이 2 한도 적용 — 한 모듈이 LOC>200 / 복합 책임 / 다중 스택 / 회귀 누적 중 하나 이상이면 서브 에이전트로 자동 분해.

**Q. 의도가 도중에 바뀌면?**
A. 페이즈 06 까지 도달 후 의도 변경이 들어오면 페이즈 11 (sprint) 의 `re-architect` 트리거 — 기존 모듈을 깨고 페이즈 06 부터 다시 빚는다 ([`../../skills/theseus-harness/conventions/lessons.md`](../../skills/theseus-harness/conventions/lessons.md)).

## 더 읽을거리

- [`../../skills/theseus-plan/SKILL.md`](../../skills/theseus-plan/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/conventions/diagrams.md`](../../skills/theseus-harness/conventions/diagrams.md) — 다이어그램 진화.
- [`../../skills/theseus-harness/conventions/competition.md`](../../skills/theseus-harness/conventions/competition.md) — 경쟁 트리거.
- [`../../skills/theseus-harness/conventions/sub-agents.md`](../../skills/theseus-harness/conventions/sub-agents.md) — 재귀 분해.
