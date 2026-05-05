---
id: anti-patterns
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# 안티 패턴 통합 카탈로그

## 한 줄 요약

페이즈별 *공통* 안티 패턴을 본 파일로 통합. 페이즈 본문에는 *해당 페이즈 고유* 의 실패만 잔존. (superpowers Red Flags 차용 — 합성 아닌 *내부 중복 제거*. 거울 원칙 정합.)

## A. 설계 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A1 | 조기 추상화 — 단일 사용처에서 *재사용 가능성* 가정 | 06 (계획), 08 (구현) | 사용처 ≥ 2 까지 인라인 유지 |
| A2 | 분산 모놀리스 — 모듈 간 강한 결합 (DIP 위반) | 08 (구현) | 어댑터 분리, 포트 인터페이스 |
| A3 | Sync-where-async — 비동기 도메인에 동기 인터페이스 강제 | 08 (구현) | 큐 / 이벤트 / async 채택 |
| A4 | 자체 인증 / 자체 직렬화 — 표준 라이브러리 회피 | 08 (구현) | oauth2, json, 검증된 SDK |

## B. 인터뷰 / 산출물 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A5 | 두괄식 누락 — 첫 줄 한 줄 요약 없음 | 04 (인터뷰), 모든 산출물 | [`interview.md`](interview.md) 의 두괄식 룰 |
| A6 | 객관식 알파벳 라벨 (a/b/c) | 04 (인터뷰) | 숫자 1~5 만 |
| A7 | frontmatter 누락 | 모든 산출물 | quality-gate 자동 fail (C14) |
| A8 | 페이즈 생략 | 모든 페이즈 | "발견 없음" 으로 기록 의무 |

## C. 자율성 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A9 | 페이즈 04 외 사용자 ack 호출 | 05~13 | [`autonomy.md`](autonomy.md) C23 |
| A10 | 자율 결정의 침묵 (라이브 보고 누락) | 05~13 | [`timing.md`](timing.md) 라이브 보고 |

## 적용

페이즈별 *고유* 안티 패턴은 [`../phases/`](../phases/) 본문에 잔존 — 본 카탈로그는 *공통* 만. self_lint C40 가 통합 정합 검증.
