# 명명 — 후보 표 / 확정본

> **프로젝트:** `<프로젝트명 — 확정 후 갱신>` · **페이즈:** `00-naming`
> **시작:** `<ISO>` · **종료:** `<ISO>` · **소요:** `<n분 n초>`
> **누적 경과:** `<n분 n초>` · **현재 시각:** `<ISO>`

## 한 줄 요약
<무엇을 명명했는가 — 프로젝트명, 1차 모듈명. 사용자가 객관식으로 선택한 결과.>

## 후보 표 (00-candidates.md 의 형식)

| 번호 | 후보 | 사전 의미 | 도메인 함의 | 충돌 검사 | 식별자 형식 |
| ---: | ---- | -------- | ----------- | -------- | ---------- |
| 1 | atlas-ledger | "지도 + 원장" | 결제 도메인 매핑 잘 됨 | npm/pypi/go 동명 없음, GitHub 없음 | `atlas-ledger` |
| 2 | orpheus-flow | "전달의 신 + 흐름" | 메시지 파이프라인 함의 | 동명 OSS 없음 | `orpheus-flow` |
| 3 | lattice-store | "격자 저장" | 분산 캐시 함의 | GitHub 동명 OSS 존재 — 검색 혼동 가능 | `lattice-store` |

## 사용자에게 묻는 질의 형식 (예시)

질의: 프로젝트명을 골라주세요.

세 후보 모두 의미상 충돌이 없습니다. 단, 3 번은 GitHub 동명 저장소가 있어 검색 시 혼동 가능성이 약간 있습니다.

선택지:
1. atlas-ledger
2. orpheus-flow
3. lattice-store
4. 모두 마음에 들지 않음 (다시 후보 생성)

## 확정본 (00-naming.md 의 형식)

```markdown
# 확정 명명

## 프로젝트명
`atlas-ledger`

**선택 사유:** 결제 도메인의 "원장" 의미가 명확하고, 외부 충돌 없음.

## 모듈명
| 모듈 | 의미 | 식별자 |
| ---- | ---- | ----- |
| be4fe | 백엔드-포-프론트엔드 (BFF), 결제 API + 도메인 로직 | `be4fe` |
| fe | 프론트엔드 + 관리자 웹뷰 | `fe` |
| ledger-core | 원장 도메인 코어 (Go) | `ledger-core` |
| ledger-adapter-pg | PostgreSQL 어댑터 | `ledger-adapter-pg` |

## 폴더 매핑
- `be4fe/` ← 백엔드 코드
- `fe/` ← 프론트엔드 코드
- `internal/ledger-core/` ← Go 도메인
- `internal/ledger-adapter-pg/` ← Go 어댑터
```

## 명명 원칙 체크

ⓐ **의도 명확** — 단어가 무엇을 의미하는지 사전적으로도 도메인적으로도 분명.
ⓑ **충돌 없음** — npm/pypi/go module/GitHub 검색에서 동명 패키지 부재 (또는 명시적 수용).
ⓒ **메타 명사 회피** — "core", "common", "utils" 같은 빈 단어 미사용.
ⓓ **저장소명 차용 금지** — `shipoftheseus` 같이 메타-저장소명을 그대로 쓰지 않음.
