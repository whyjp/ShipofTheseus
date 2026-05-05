# Idiomatic Code Quality — Code quality 만점 push (sprint-16 / v0.9.22)

## 한 줄 요약

**Code quality 9→10 (-1pt) 정정.** [`polyglot-code-quality.md`](polyglot-code-quality.md) (au, v0.9.16) 의 6 메트릭 (cyclomatic / function_length / nesting / duplicate / lint / format) 위에 *언어 idiomatic-ness* 4 차원 추가 — naming convention / preferred construct / standard library / readability heuristic. 단순 lint pass 가 아니라 *언어 native 사용자가 자연스럽다고 느끼는 코드*.

## 1. 4 idiomatic 차원

### D1 Naming convention (언어별 표준)

| 언어 | 함수 | 클래스 | 상수 | 변수 | 모듈 |
|---|---|---|---|---|---|
| Python | `snake_case` | `PascalCase` | `UPPER_SNAKE` | `snake_case` | `snake_case.py` |
| Go | `camelCase` (priv) / `CamelCase` (pub) | `CamelCase` | `CamelCase` | `camelCase` | `lowercase.go` |
| TypeScript | `camelCase` | `PascalCase` | `UPPER_SNAKE` | `camelCase` | `kebab-case.ts` |
| Rust | `snake_case` | `PascalCase` | `UPPER_SNAKE` | `snake_case` | `snake_case.rs` |

위반 ratio 0.05 이하 의무 (95%+ 정합).

### D2 Preferred construct (언어 native pattern)

| 언어 | 권장 | 회피 |
|---|---|---|
| Python | comprehension / dataclass / Path / contextmanager / type hints | 명령형 loop append / dict by hand / os.path / try-finally manual |
| Go | error 반환 / interface 기반 / channel for sync / table-driven test | panic / interface{} 남발 / mutex 직접 |
| TypeScript | discriminated union / strict null check / readonly | any / Object 타입 / let 남발 |
| Rust | Result + ? / Option + map / iterator chain | unwrap() 남발 / mut 남발 |

### D3 Standard library 우선

언어 stdlib 가 제공하는 기능 직접 구현 금지 :
- Python: `pathlib` / `dataclasses` / `enum` / `functools` / `itertools` 우선
- Go: `net/http` / `encoding/json` / `context` 우선
- TypeScript: `Map` / `Set` / `Date` / `URL` 우선
- Rust: `std::collections` / `std::iter` 우선

### D4 Readability heuristic

| heuristic | 임계 |
|---|---|
| 함수명이 *동사* 시작 (action) | 95%+ |
| 클래스명이 *명사* (entity) | 100% |
| boolean 변수가 `is_*` / `has_*` / `can_*` 시작 | 90%+ |
| 약어 (abbreviation) 사용 ratio | ≤ 5% (id, url, http 같은 표준 외) |
| magic number 직접 박힘 | 0 (모두 named constant) |
| line length ≤ 100 자 | 99%+ |

## 2. frontmatter sync (페이즈 08 impl-log)

```yaml
---
idiomatic_code_quality:
  language: Python
  naming_violation_ratio: 0.02            # ≤ 0.05 의무
  preferred_construct_ratio: 0.94         # ≥ 0.90 의무
  stdlib_first_ratio: 0.97                # ≥ 0.95 의무
  readability_heuristic_passes: 6/6       # 6 heuristic 모두 PASS
  magic_number_count: 0                    # = 0 의무
idiomatic_grade: A                        # A (모두 PASS) / B (1 fail) / C (≥2)
---
```

## 3. self_lint C-ICQ 룰

```python
def check_idiomatic_code_quality(artifact_dir: Path) -> list[str]:
    impl_log = artifact_dir / 'impl' / '08-impl-log.md'
    if not impl_log.exists():
        return []
    fm = parse_frontmatter(impl_log)
    errors = []

    icq = fm.get('idiomatic_code_quality', {})
    if icq.get('naming_violation_ratio', 1.0) > 0.05:
        errors.append(f'naming_violation_ratio {icq.get("naming_violation_ratio")} > 0.05')
    if icq.get('preferred_construct_ratio', 0) < 0.90:
        errors.append('preferred_construct_ratio < 0.90')
    if icq.get('stdlib_first_ratio', 0) < 0.95:
        errors.append('stdlib_first_ratio < 0.95')
    if icq.get('magic_number_count', -1) != 0:
        errors.append(f'magic_number_count != 0')
    if icq.get('readability_heuristic_passes', '').count('/') == 1:
        passes, total = icq['readability_heuristic_passes'].split('/')
        if int(passes) < int(total):
            errors.append(f'readability_heuristic {passes}/{total} (모두 PASS 의무)')

    if fm.get('idiomatic_grade') not in ['A', 'B']:
        errors.append('idiomatic_grade ∉ {A, B}')

    return errors
```

## 4. cold session 적용 — Code quality 9→10 push

au (6 메트릭) + 본 컨벤션 (4 idiomatic 차원) :
- au = lint pass 측정 (객관 도구)
- 본 = 언어 native idiomatic-ness 측정 (heuristic)

bench rubric 의 *Code quality* 차원 +1pt 회수 가능 :
- naming convention 위반 ≤ 5% → +0.5pt
- magic number 0 + readability 6/6 → +0.5pt

## 5. 안티 패턴

a- **lint pass = idiomatic** — pylint 0 위반 ≠ Pythonic. comprehension 대신 loop, pathlib 대신 os.path → 비-idiomatic 이지만 lint pass.
b- **언어 mismatch 모방** — Python 에 Go 스타일 (interface{}-like duck typing) → Pythonic 아님.
c- **abbreviation 남발** — `tx_pos`, `cfg_mgr` 같은 약어 → readability heuristic fail.
d- **magic number 직접** — `if x > 100` → `MAX_TRUCKS = 100; if x > MAX_TRUCKS`.
e- **stdlib 우회 자체 구현** — `from datetime import` 대신 직접 timestamp parse.

## 6. 호환성

- [`polyglot-code-quality.md`](polyglot-code-quality.md) (au) — 6 객관 메트릭 + 본 컨벤션 4 idiomatic 차원 = 두 layer.
- [`build-and-config.md`](build-and-config.md) — ruff / golangci-lint / eslint 설정에 idiomatic check rule 활성 입력.
- [`commentary-policy.md`](commentary-policy.md) (bh) — audience=external-reviewer 시 readability 더 엄격.
