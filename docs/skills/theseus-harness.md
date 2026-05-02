# theseus-harness 가이드 (플래그십)

## 한 줄 요약

**14 페이즈 + 21 컨벤션 + 13 에이전트 + 채점기를 한 곳에 담은 단일 source of truth.** 8 분해 스킬은 *형태와 인터페이스만* 정의하고 본문을 본 스킬에 위임한다.

## 언제 호출하는가

ⓐ **단일 호출로 14 페이즈 전체** 를 진행하고 싶을 때 — orchestrator 위임 없이 직접.
ⓑ 분해 스킬을 통한 위임 흐름이 부담스러운 작은 G2~G3 작업.
ⓒ 본 저장소 자체를 평가할 때 (BOOTSTRAP 자기 평가 — 본 하네스로 본 하네스 회귀).

orchestrator 와의 차이는 [`theseus-orchestrator.md`](theseus-orchestrator.md) 의 FAQ 참조.

## 호출 형식

```
/theseus-harness <요구사항>
```

## 본 스킬이 담는 것

| 카테고리 | 개수 | 위치 |
| ------- | --- | ---- |
| 페이즈 본문 | 14 | [`../../skills/theseus-harness/phases/`](../../skills/theseus-harness/phases/) |
| 컨벤션 | 21 | [`../../skills/theseus-harness/conventions/`](../../skills/theseus-harness/conventions/) |
| 서브 에이전트 프롬프트 | 13 | [`../../skills/theseus-harness/agents/`](../../skills/theseus-harness/agents/) |
| 채점기 | 4 모듈 | [`../../skills/theseus-harness/scoring/`](../../skills/theseus-harness/scoring/) |
| 템플릿 | 6+ | [`../../skills/theseus-harness/templates/`](../../skills/theseus-harness/templates/) |

## 21 컨벤션 (한 줄 요약)

| # | 컨벤션 | 핵심 |
| - | ------ | --- |
| 1 | [`interview.md`](../../skills/theseus-harness/conventions/interview.md) | 두괄식·1 회 1 질의·숫자 5 개·확증 회귀 |
| 2 | [`timing.md`](../../skills/theseus-harness/conventions/timing.md) | 산출물 헤더 시간 메타·라이브 보고 |
| 3 | [`diagrams.md`](../../skills/theseus-harness/conventions/diagrams.md) | 마인드맵→유즈케이스→시퀀스 진화 |
| 4 | [`stack.md`](../../skills/theseus-harness/conventions/stack.md) | 언어/컴파일러/패키지 매니저 사전 점검 |
| 5 | [`build-and-config.md`](../../skills/theseus-harness/conventions/build-and-config.md) | sh+bat·TOML·docs/·폐기·병렬·메모리 |
| 6 | [`contracts.md`](../../skills/theseus-harness/conventions/contracts.md) | 산출물 frontmatter — 단계 재진입 |
| 7 | [`models.md`](../../skills/theseus-harness/conventions/models.md) | 에이전트 역할별 Opus/Sonnet/Haiku 매핑 |
| 8 | [`competition.md`](../../skills/theseus-harness/conventions/competition.md) | 2~3 후보 격리 병렬 경쟁 + 자동 resolve |
| 9 | [`autonomy.md`](../../skills/theseus-harness/conventions/autonomy.md) | 자율성 우선·페이즈 04 외 자율 결정 |
| 10 | [`lessons.md`](../../skills/theseus-harness/conventions/lessons.md) | 정체 감지·레슨팩·통째 재작성 강제 |
| 11 | [`spec-catalog.md`](../../skills/theseus-harness/conventions/spec-catalog.md) | 도메인별 NFR 자동 카탈로그 |
| 12 | [`resources.md`](../../skills/theseus-harness/conventions/resources.md) | 리소스 기반 임계 + 천정 자동 조정 |
| 13 | [`checkpoints.md`](../../skills/theseus-harness/conventions/checkpoints.md) | 체크포인트·멀티버스 (닥터 스트레인지) |
| 14 | [`test-invariants.md`](../../skills/theseus-harness/conventions/test-invariants.md) | 테스트 목적 보호·Phase V 측정 유효성 |
| 15 | [`dacapo.md`](../../skills/theseus-harness/conventions/dacapo.md) | Da Capo 루프·AIDE × LLM Wiki 결합 |
| 16 | [`fragmentation.md`](../../skills/theseus-harness/conventions/fragmentation.md) | 파편화 우선·단일 헤비 스킬 금지 |
| 17 | [`grades.md`](../../skills/theseus-harness/conventions/grades.md) | 그레이드 시스템 (G1 거부 ~ G5 빡빡) |
| 18 | [`sub-agents.md`](../../skills/theseus-harness/conventions/sub-agents.md) | 서브 에이전트 재귀 분해 |
| 19 | [`indexing.md`](../../skills/theseus-harness/conventions/indexing.md) | 산출물 = DB·비직렬성 트리 인덱싱 |
| 20 | [`resume.md`](../../skills/theseus-harness/conventions/resume.md) | 리줌 (중단/재개)·state.json |
| 21 | [`prd-handling.md`](../../skills/theseus-harness/conventions/prd-handling.md) | PRD 처리 허들·인터뷰 스킵 금지 |

## 채점기

| 모듈 | 역할 |
| ---- | --- |
| [`score.py`](../../skills/theseus-harness/scoring/score.py) | 6 차원 가중평균 채점, 임계 0.999, DIP hard cap 0.6, 5 hard cap |
| [`fingerprint.py`](../../skills/theseus-harness/scoring/fingerprint.py) | frontmatter 핑거프린트 계산·검증·체인 무결성 |
| [`self_lint.py`](../../skills/theseus-harness/scoring/self_lint.py) | 본 저장소 35 체크 + `--score` 모드 (임계 0.99999) |
| [`rubric.md`](../../skills/theseus-harness/scoring/rubric.md) | 6 차원 채점 룰 + 0.999 / 0.99999 의미론 |

## 입출력

- **입력**: 사용자 자연어 요청 + 레포 컨텍스트 (orchestrator 와 동일).
- **출력**: 14 페이즈 산출물 모두 + 웹뷰 + 핸드오프 메시지.

산출물 위치: `.ShipofTheseus/<project_id>/`.

## 자주 묻는 질문

**Q. orchestrator 와 둘 중 무엇을 고르는가?**
A.
- 일반 사용 → orchestrator (분해의 이점 누림: 단독 호출, 자기 거부 grade-assess).
- 본 저장소 자체 평가 (BOOTSTRAP) → harness (단일 호출이 의도).
- 작은 G2 → harness (위임 오버헤드 최소화).

**Q. 단독 호출과 orchestrator 호출의 산출물이 다른가?**
A. 같다. 둘 다 같은 페이즈 본문·같은 채점기·같은 frontmatter 계약을 따른다 — 분해는 콘텐츠를 *나누지 않는다*, *호출 인터페이스만 나눈다*.

**Q. 21 컨벤션을 다 읽어야 호출 가능한가?**
A. 사용자는 안 읽어도 된다. LLM 이 [`SKILL.md`](../../skills/theseus-harness/SKILL.md) 인덱스를 통해 필요한 컨벤션을 페이즈마다 가져간다. 사용자는 [`README.md`](../../README.md) + 본 가이드 정도만 읽으면 충분.

## 더 읽을거리

- [`../../skills/theseus-harness/SKILL.md`](../../skills/theseus-harness/SKILL.md) — 기계 진입점 (LLM 이 읽음).
- [`../../skills/theseus-harness/README.md`](../../skills/theseus-harness/README.md) — 빠른 참조 (사람이 읽음, 본 가이드와 일부 중복).
- [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — 신뢰 담보, 도자기 장인, Ralph/우로보로스.
- [`../../BOOTSTRAP.md`](../../BOOTSTRAP.md) — 본 하네스로 본 저장소를 평가하는 절차.
