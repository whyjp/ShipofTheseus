---
id: multiverse-width-default-bump
category: planning
applies-to-phases: '[06,08]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'frozen(advisory)'
indexed-in: conventions/INDEX.md
---

# Multiverse Width Default Bump — 동결 stub (설계 §8, B2-F1)

## 한 줄 요약

**동결**: 폭 격상(G3 3→5 / G4 4→7 / G5 6→9, root 폭 9 + depth 2 head-to-head)은
편익 미실증으로 §8 동결됐다. **활성 폭의 유일 권위 = `pipeline.manifest.json`
`multiverse_widths`**(G2=1/G3=3/G4=4/G5=6). 격상 폭은 동일 파일 `frozen_widths`
(G3=5/G4=7/G5=9)에 비활성(advisory) 상태로 기록돼 있다.

폭 확대는 **가능하나 의무 아니다** — 사용자가 명시적으로 ack 하면(옵션
default G3=10/G4=12/G5=16, [`budget-aware-fallback.md`](budget-aware-fallback.md)
cap 동기 갱신 포함) 여전히 수행할 수 있다. 스크립트/템플릿/폭 매트릭스 로직은
물리 존치 — 강제 호출만 해제됐다.

**재승격 경로**: `frozen.multiverse_width_benefit` CheckSpec 의 A/B 실증(효과
확인 시 manifest `multiverse_widths` 갱신 제안).

관련: [`resources.md`](resources.md) §universe parallel cap ·
[`impl-multiverse-strict.md`](impl-multiverse-strict.md)(활성 폭 3/4/6 무수정,
동결 대상 밖).
