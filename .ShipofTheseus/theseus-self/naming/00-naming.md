---
skill_name: theseus-harness
skill_version: 0.2.0
phase: 00-naming
project_id: theseus-self
project_run: 20260501-184946
fingerprint: sha256:b161cf4966a37f64d4934f9de599471abb623b8401637f6102f72ac5537db565
prev_fingerprint: null
produced_at: 2026-05-01T18:49:46Z
producer_agent: human-bootstrap
---
> **시작:** 2026-05-01T18:49:46Z · **종료:** 2026-05-01T18:49:46Z · **소요:** 0초
> **누적 경과:** 0초 · **현재 시각:** 2026-05-01T18:49:46Z

# 확정 명명 — 부트스트래핑 자체 평가

## 한 줄 요약
**프로젝트명 `theseus-self`** — 본 하네스의 자기 자신에 대한 평가 회차. 모듈명은 본 저장소의 기존 디렉터리 구조를 그대로 사용 (`skills/theseus-harness/{conventions,phases,agents,scoring,templates}`), 새 모듈은 만들지 않음.

## 프로젝트명
`theseus-self`

**선택 사유:** "테세우스의 배가 자신을 본다" 의미. 외부 충돌 없음 — npm/pypi/go module 검색 없음.

## 모듈 맵 (기존)
| 모듈 | 위치 | 책임 |
| ---- | ---- | ---- |
| conventions | `skills/theseus-harness/conventions/` | 8 컨벤션 모듈 (인터뷰/시간/다이어그램/스택/빌드/계약/모델/경쟁) |
| phases | `skills/theseus-harness/phases/` | 14 페이즈 문서 |
| agents | `skills/theseus-harness/agents/` | 13 서브에이전트 프롬프트 |
| scoring | `skills/theseus-harness/scoring/` | rubric, score.py, fingerprint.py, self_lint.py, test_score.py |
| templates | `skills/theseus-harness/templates/` | 4 템플릿 + bun 웹뷰 스캐폴드 |

## 명명 원칙 체크

ⓐ 의도 명확 — `theseus-self` 가 의미하는 바가 분명.
ⓑ 충돌 없음 — 외부 검색 결과 없음.
ⓒ 메타 명사 회피 — 추상 단어 미사용.
ⓓ 저장소명 차용 금지 — `shipoftheseus` 메타-저장소명 그대로 안 쓰고 `theseus-self` 라는 새 단어.
