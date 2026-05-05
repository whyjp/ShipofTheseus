---
id: polyglot-code-quality
category: quality
applies-to-phases: '[09]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Polyglot Code Quality — 언어 무관 코드 품질 게이트

## 한 줄 요약

**v0.9.1 [`build-and-config.md`](build-and-config.md) 의 ruff 통합은 *Python 전용*. Go / TS / Rust / Java / Ruby 프로젝트에 적용 시 코드 품질 게이트 0 발현.** 본 컨벤션이 *언어 무관 메트릭* + *언어별 표준 도구 카탈로그* 로 일반화 — 외부 사용자가 어떤 언어를 쓰든 페이즈 09 게이트 3 (코드 품질) 발현.

## 1. 결손 진단

[`build-and-config.md`](build-and-config.md) §8 :

```
페이즈 09 게이트 3 (SOLID DIP) 부속:
  - ruff check (errors 0)
  - ruff format --check (diff 0)
```

→ ruff = Python 전용. 본 하네스가 *백엔드 기본 Go* (HARD-RULE f) 라고 하면서 *코드 품질 게이트는 Python 전용*. 외부 사용자가 Go / TS 프로젝트에 본 하네스 적용 시 페이즈 09 게이트 3 *비활성*. simulation-bench 가 Python 이라 *우연히* 발현됐을 뿐.

v0915-cold01 코드 품질 점수 9/10 (-1pt) 도 ruff 만으로는 부족 시그널 (cyclomatic complexity / type hints coverage 누락).

## 2. 운영 룰

### Step 1 — 언어 무관 메트릭 카탈로그

| 메트릭 | 의미 | 임계 (default) | 측정 도구 |
|---|---|---|---|
| `cyclomatic_complexity` | 함수당 분기 복잡도 | ≤ 10 | radon (Py) / gocyclo (Go) / complexity-report (TS) |
| `function_length` | 함수당 LOC | ≤ 50 | 위 도구들 |
| `nesting_depth` | 함수당 최대 nest | ≤ 4 | 위 도구들 |
| `duplicate_blocks` | DRY 위반 (≥6 LOC 중복) | 0 | jscpd / pmd-cpd |
| `lint_errors` | 언어 표준 lint | 0 | 아래 §2-2 카탈로그 |
| `format_diff` | 언어 표준 format | 0 | 아래 §2-2 카탈로그 |

위 6 메트릭 = 모든 언어 동일.

### Step 2 — 언어별 표준 도구 카탈로그

페이즈 04 stack 답안에 따라 자동 매핑 (Q-D5 stack 답):

| 언어 | lint | format | cyclomatic | duplicate |
|---|---|---|---|---|
| **Python** | `ruff check` | `ruff format --check` | `radon cc -s` | `jscpd` |
| **Go** | `golangci-lint run` | `gofmt -d` | `gocyclo -over 10` | `dupl -threshold 50` |
| **TypeScript** | `biome check` | `biome format --check` | `complexity-report` | `jscpd` |
| **JavaScript** | `eslint .` (또는 biome) | `prettier --check` | 위 동일 | `jscpd` |
| **Rust** | `cargo clippy -- -D warnings` | `cargo fmt --check` | `cargo-geiger` | `pmd-cpd` |
| **Java** | `checkstyle` | `google-java-format -n` | `pmd` | `pmd-cpd` |
| **Ruby** | `rubocop` | `rubocop -a --check` | `flog` | `flay` |
| **C/C++** | `clang-tidy` | `clang-format -n` | `cppcheck` | `pmd-cpd` |
| **Kotlin** | `detekt` | `ktlint -F` | `detekt` | `pmd-cpd` |

`stack.md` 의 사전 점검 단계가 본 카탈로그의 *해당 도구 설치 여부* 체크 추가.

### Step 3 — 페이즈 09 게이트 3 일반화

```yaml
gate_3_code_quality:
  language: <Q-D5 stack 답안>
  metrics:
    cyclomatic_complexity:
      tool: <카탈로그[language].cyclomatic>
      threshold: 10
      result: PASS|FAIL
    function_length:
      threshold: 50
      result: PASS|FAIL
    # ... 6 메트릭 모두 ...
  pass_criteria: 모든 메트릭 PASS
```

`build-and-config.md` §8 의 ruff 절은 *카탈로그 1번* 으로 격하 — 본 컨벤션 §2 의 카탈로그가 master.

### Step 4 — 다중 언어 프로젝트 (FE+BE)

페이즈 04 답안에 *language_primary* + *language_secondary* 가 있으면 둘 다 게이트 3 발현. 임계는 *각 언어별로 독립* (예: Go BE + TS FE = 두 게이트).

## 3. self_lint 룰

`scoring/self_lint.py` C-PCQ (신규):

```python
def lint_polyglot_code_quality(skill_root: Path) -> list[str]:
    errors = []
    pcq = (skill_root / "conventions" / "polyglot-code-quality.md").read_text(encoding="utf-8")
    bnc = (skill_root / "conventions" / "build-and-config.md").read_text(encoding="utf-8")
    # 1. build-and-config 가 본 컨벤션 cross-reference + ruff 절 격하 명시
    if "polyglot-code-quality" not in bnc:
        errors.append("build-and-config missing polyglot-code-quality cross-ref")
    # 2. 본 컨벤션 카탈로그에 핵심 언어 ≥6 (Python / Go / TypeScript / Rust / Java / Ruby)
    required_languages = ["Python", "Go", "TypeScript", "Rust", "Java", "Ruby"]
    for lang in required_languages:
        if lang not in pcq:
            errors.append(f"polyglot-code-quality missing language: {lang}")
    # 3. 언어 무관 메트릭 6 종 명시
    required_metrics = ["cyclomatic_complexity", "function_length", "nesting_depth",
                         "duplicate_blocks", "lint_errors", "format_diff"]
    for m in required_metrics:
        if m not in pcq:
            errors.append(f"polyglot-code-quality missing metric: {m}")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 6 메트릭 = 모든 언어 동일, 도메인 X.
b- 9 언어 카탈로그 = 표준 도구 매핑, 도메인 X.
c- 임계 (cyclomatic ≤10 / function ≤50 LOC / nesting ≤4) = 산업 표준.
d- 다중 언어 프로젝트 처리 = 일반 룰.

## 5. 안티 패턴

a- **ruff 만 적용 (build-and-config 의 잔존)** — 본 컨벤션 핵심 위반. C-PCQ fail.
b- **Q-D5 stack 답 무관하게 ruff 호출** — 언어 매칭 누락. 페이즈 09 산출물 frontmatter 의 `language` 필드 의무.
c- **카탈로그에 없는 언어 (Elixir / Crystal / Zig 등)** — 사용자 명시 도구 답안 입력 (Q-D5 sub-option) 또는 *언어 무관 메트릭 4 종* (cyclomatic / function / nesting / duplicate) 만 적용.
d- **임계 무시 (예: function 200 LOC)** — 단순 lint PASS 만 보고 깊은 메트릭 무시 = v0915-cold01 의 -1pt 패턴.

## 6. 외부 사용자 접근성 (v1.0 prerequisite)

본 하네스의 v1.0 = *사용자 외 maintainer prod 채택*. Python 외 언어 사용자가 본 하네스 채택 시:

- ruff 만 = "이 하네스는 Python 전용?" 의문
- 본 컨벤션 후 = 9 언어 표준 도구 자동 매핑, 언어 중립

→ v1.0 외부 채택의 prerequisite 인프라.

## 7. 자기 검증

본 하네스 자체 = Python (scoring/) + Markdown — 본 컨벤션 자기 적용 시 Python 메트릭 검증 (radon cyclomatic / 함수 길이 / nesting). 본 컨벤션 도입 sprint 의 lesson = *본 하네스 자기 적용으로 발견한 score 메트릭 결손* (예: self_lint.py 의 함수 ≥50 LOC 인 함수 N 개).
