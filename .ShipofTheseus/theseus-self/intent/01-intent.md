---
skill_name: theseus-harness
skill_version: 0.2.0
phase: 01-intent
project_id: theseus-self
project_run: 20260501-184946
fingerprint: sha256:db8710ef8f7b07e9b8601af3c660fb53745bd3bf74b695faa1edb6d97cfa4a16
prev_fingerprint: sha256:b161cf4966a37f64d4934f9de599471abb623b8401637f6102f72ac5537db565
produced_at: 2026-05-01T18:49:46Z
producer_agent: human-bootstrap
---
> **시작:** 2026-05-01T18:49:46Z · **종료:** 2026-05-01T18:50:30Z · **소요:** 44초
> **누적 경과:** 44초 · **현재 시각:** 2026-05-01T18:50:30Z

# 의도 — `theseus-self` (본 하네스의 자기 평가)

## 한 줄 요약
**본 하네스가 자기 자신에게 자기의 평가 절차를 적용해, 약점·갭·불일치를 표면화하고 다음 보완 후보를 부트스트래핑한다.** 우로보로스의 진짜 발현 — 자기 꼬리를 무는 뱀이 자기 평가 도구로도 동작.

## 무엇을
본 저장소(`whyjp/shipoftheseus`)를 한 *프로젝트* 로 간주해 페이즈 01–09 의 산출물을 생성한다. 결과는 `.ShipofTheseus/theseus-self/` 트리. 1차는 사람 손, 2차부터는 본 하네스의 슬래시 명령으로 자동 갱신.

## 왜
ⓐ 본 하네스는 사용자 프로젝트에 SoC/DIP/게이트/점수를 강제한다 — 본 저장소도 같은 게이트를 통과해야 일관성 있다.
ⓑ 매 릴리스마다 컨벤션이 늘어 컨벤션 간 모순·인덱싱 누락이 누적된다 — 자체 lint 가 잡는다.
ⓒ 약점은 *밖에서* 보인다 — 본 하네스가 자기 자신을 외부처럼 보면 SKILL.md 의 모호함이 드러난다.

## 비목표
ⓐ 본 하네스에 새 페이즈 추가 — 자기 평가는 *기존 페이즈* 를 재사용.
ⓑ 사용자 프로젝트 자동 평가 — 자기 평가는 본 저장소만 대상.
ⓒ 100% 코드 커버리지 추구 — 본 저장소는 문서 비중이 크므로 self_lint 로 충분.

## 제약
- **성능:** self_lint 는 < 1초, score test 는 < 1초.
- **호환:** Python 3.11+ (PEP 604 union 문법, `tomllib`).
- **이식:** sh + bat 양쪽으로 self-check 동작.
- **버전:** plugin.json 과 SKILL.md frontmatter 의 skill_version 일치 강제.

## 유비쿼터스 언어
| 용어 | 정의 |
| ---- | ---- |
| **자기 평가** | 본 하네스의 페이즈 절차를 본 저장소를 입력으로 적용 |
| **부트스트래핑** | 1차는 사람 손, 2차부터 자동으로 회차 누적되는 자체 평가 |
| **self_lint** | 컨벤션·교차 링크·버전 정합성을 검사하는 11 체크 도구 |
| **메타 게이트** | 본 저장소가 통과해야 하는 자체 품질 게이트 (e2e/parity 는 n/a) |

## 스테이크홀더
- **사용자:** 본 저장소의 메인테이너 (whyjp), PR 리뷰어, 본 하네스를 사용하려는 외부 개발자.
- **운영자:** GitHub Actions 또는 `scripts/self-check.{sh,bat}` 를 수동으로 실행하는 메인테이너.
- **소유자:** whyjp.

## 성공 지표
ⓐ `self_lint.py` 의 11 체크 모두 통과.
ⓑ `pytest scoring/test_score.py` 12 케이스 통과.
ⓒ 매 PR 에서 `scripts/self-check.sh` 가 0 exit.
ⓓ 자기 평가 회차 간 점수 시계열이 단조 증가 또는 평탄.

## 스택 가정
- 검사 도구: Python 3.11+ 표준 라이브러리만 (`pathlib`, `re`, `json`, `hashlib`, `py_compile`).
- 외부 의존 없음 — 본 저장소가 Claude Code 스킬 저장소이므로 의존을 최소화.

## 열린 질문
- 자기 평가 회차의 점수가 떨어지는 PR 을 자동 차단할까? (CI 강제 vs 권고 — 메인테이너 정책 결정 필요)
- 자기 평가 산출물의 한국어 톤을 유지할까, 다국어로 확장할까?
- self_lint 의 체크 항목을 더 늘릴 가치가 있는 영역은? (예: phases 의 시간 메타 헤더 검사, agents 의 "완료 조건" 줄 검사 등)
