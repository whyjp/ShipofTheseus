# Ship of Theseus — 스킬 저장소

## 한 줄 요약
**조립을 다시 하든, 부수고 다시 만들든, 결국 처음 의도한 이름으로 불릴 수 있는 결과물을 보장**하는 재귀 멀티 에이전트 코딩 하네스 모음. 플래그십 스킬은 [`theseus-harness`](skills/theseus-harness/SKILL.md).

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
