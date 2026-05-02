# Ship of Theseus — 스킬 저장소

## 한 줄 요약
**조립을 다시 하든, 부수고 다시 만들든, 결국 처음 의도한 이름으로 불릴 수 있는 결과물을 보장**하는 재귀 멀티 에이전트 코딩 하네스 모음. 플래그십 스킬은 [`theseus-harness`](skills/theseus-harness/SKILL.md).

## 현재 성숙도 — 정직 박스 (v0.2.1)

> **v0.2.x 는 자기 평가만 통과한 스캐폴드입니다. 외부 실 프로젝트 적용 0 건.**
>
> ⓐ `self_lint 34/34 pass`, `sample_score 1.0`, `임계 0.99999 통과` 같은 수치는 **본 저장소의 마크다운·코드 인덱스 정합성·예시 입력 채점 통과** 를 의미합니다 — *LLM 에이전트가 프롬프트를 행동으로 따르는지* 의 외부 실증과 다릅니다.
> ⓑ self_lint 는 *마크다운 텍스트 패턴* 만 검사합니다. "phase 10 본문에 lessons + stagnation 단어가 박혀 있는가" 는 검증되지만, "implementer 에이전트가 *실제로* lesson_pack 을 받아 forbidden 전략을 회피하는가" 는 검증 불가.
> ⓒ **임계 0.999 / 자기 임계 0.99999 는 SLO 가용성이 아닙니다** — 6 차원 rubric 가중평균 + DIP 단독 hard cap 0.6 + 5 hard cap 의 *명명 규칙* 입니다. 외부 사용자에게 "99.999% 신뢰 가능" 으로 오해되지 않도록 본 README 에서 명시.
> ⓓ **v0.3.0 의 유일 시급 목표**: 첫 외부 실 프로젝트 적용 1 건 + 4 메트릭(인터럽트 0 / 14 페이즈 시간 / 의도 일치 / 채택 가능) post-mortem. 그때까지 새 컨벤션·새 도구 추가 동결.

## v0.2.1 핫픽스 (Cursor Bugbot PR#1 후속)

ⓐ **`fingerprint.py` timing-invariance 회귀 수정** — `TIMING_HEADER_RE` 의 `\A>` 앵커는 템플릿이 `# 제목\n\n> **프로젝트:**` 로 시작하는 패턴에 절대 매치되지 않아, *timing-invariant fingerprint* 라는 [`contracts.md`](skills/theseus-harness/conventions/contracts.md) 의 핵심 약속이 깨져 있었음. → 본문 어디에 위치하든 timing 마커(`**시작:** / **종료:** / **누적 경과:** / **현재 시각:** / **이 스프린트 소요:** / **소요:**`) 를 포함한 blockquote 블록을 식별·strip 하도록 수정. [`scoring/test_fingerprint.py`](skills/theseus-harness/scoring/test_fingerprint.py) 9 회귀 케이스로 박음 — 같은 본문 + 다른 시각 → 같은 fingerprint 보장.
ⓑ **`Sprints.tsx` 차트 데이터 소스 회귀 수정** — `s.inputs?.score` 는 `inputs.json`(score.py 의 *입력*) 에 score 필드가 없어 항상 빈 차트였음. `score.py --out` 플래그 신규로 `sprints/NN/score.json` 산출 의무화 + `server.ts` `/api/sprints` 가 score.json 도 로드 + Sprints.tsx 가 `s.score?.score` 사용. [`phases/10-test-loop.md`](skills/theseus-harness/phases/10-test-loop.md) 의 score.py 호출 형식도 갱신.
ⓒ **0.999 / 0.99999 SLO 의미론 오용 가드** — README 정직 박스 + [`scoring/rubric.md`](skills/theseus-harness/scoring/rubric.md) §"0.999 / 0.99999 의 의미" 섹션 신규. 외부 사용자가 "99.999% 가용성" 으로 오해하지 않도록 *6 차원 가중평균 임계 + self_lint 정합성 측정* 임을 명시.

## 왜 테세우스의 배인가
배의 모든 판자를 하나씩 갈아 끼워도 같은 배라고 부를 수 있는가 — 이 사고 실험이 이 저장소의 핵심 은유다. 코드는 페이즈마다, 스프린트마다 분해·재조립·재구현되지만, **최초 의도한 타이틀의 결과물이라고 부를 수 있는 신뢰**가 끝까지 유지되어야 한다. 하네스의 모든 게이트와 점수, 회귀 바이섹트는 그 신뢰를 담보하기 위해 존재한다.

## 수록 스킬

| 스킬 | 목적 |
| ---- | ---- |
| [`theseus-harness`](skills/theseus-harness/SKILL.md) | 의도 추출 → 명명 → 문서화 → 교차 이해 → 사용자 질의 → 비평 → 계획 → 재계획 → 구현 → 품질 게이트 → 점수 0.9 도달까지 무한 스프린트 루프 → 회귀 바이섹트 → be4fe + bun 기반 fe 웹뷰 자동 생성 → 핸드오프 |

새 스킬은 `skills/<이름>/SKILL.md` 로 추가한다.

## 설치

상세 안내는 [`INSTALL.md`](INSTALL.md). 한 줄 요약:

```bash
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus
ln -s ~/src/shipoftheseus/skills/theseus-harness .claude/skills/theseus-harness
# 세션에서: /theseus-harness <요구사항>
```

저장소 루트에 [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) 매니페스트가 포함되어, Claude Code 플러그인 매니저가 지원되는 버전에서는 `claude plugin install <repo-url>` 형태로도 설치 가능.

## 산출물 위치

모든 산출물은 프로젝트 루트의 `.ShipofTheseus/<프로젝트명>/` 아래에 카테고리·단계·스프린트별로 배치된다. 자세한 구조는 [`skills/theseus-harness/SKILL.md`](skills/theseus-harness/SKILL.md) 의 "산출물 트리" 섹션 참조.

## 더 읽을거리

- [`PHILOSOPHY.md`](PHILOSOPHY.md) — 신뢰 담보의 의미, Ralph 루프·OhMy 시리즈·우로보로스 합성 근거, SOLID/TDD/BDD/DDD/Hexagonal 매핑.
- [`skills/theseus-harness/conventions/interview.md`](skills/theseus-harness/conventions/interview.md) — 사용자 질의 컨벤션(두괄식, 1회 1질의, 숫자 객관식 5개 이하 등).

## 라이선스

MIT. [`LICENSE`](LICENSE) 참조.
