---
id: cross-process-anti-patterns
category: quality
applies-to-phases: '[09]'
applies-to-grades: '[all]'
trigger-when: 'V6 evidence-bound gate'
indexed-in: conventions/INDEX.md
---

# Cross-process anti-patterns 카탈로그 (sprint-40 PR-B 신규)

## 한 줄 요약

**별 process 호출 시 비결정성을 야기하는 함수/패턴 카탈로그. phase 09 §V6-Evidence-Bound (G-RDC 강화) 가 본 카탈로그의 모든 regex 를 src/ grep 자동 검사.** simulation-bench 001 v0.9.44 g4-v2 회차의 D-6/V6 회귀 (`SeedSequence([base, hash(scenario_id), rep])`) 의 1:1 대응 catalogue.

## 결손 진단

| 결손 | 증거 |
|---|---|
| Python `hash()` salt 비결정성 모름 | scenario_id 같은 string 의 `hash()` 가 process invocation 마다 다른 값 — `SeedSequence` 안에 들어가면 출력 비결정 |
| intra-process 통과 = cross-process 통과 가정 | `test_replication_rng_deterministic` (한 process 내 두 호출) 통과 → V6 PASS 마크. 실 cross-process 깨짐 |
| anti-pattern catalogue 없음 | 알려진 비결정 함수 (`hash`, `os.urandom`, `id`, `random` global) 가 phase 09 grep guard 에 박혀 있지 않아 *재발 차단 0* |

## 카탈로그 — Python

| 패턴 | regex | 비결정 발현 | 정정 |
|---|---|---|---|
| `hash()` salt | `SeedSequence\([^)]*hash\(` | process invocation 마다 hash 값 다름 (PYTHONHASHSEED 미설정 시) | `hashlib.md5(s.encode()).digest()` 또는 `int.from_bytes(... [:4], "big")` |
| numpy seed hash | `np\.random\.seed\(.*hash\(` | 동일 | 동일 |
| random global hash | `random\.seed\(.*hash\(` | 동일 | 동일 |
| `os.urandom` mix | `os\.urandom\(\d+\)\s*[+\|^]` | OS 엔트로피 = 매 호출마다 다른 결과 | seed 외부 입력 → SeedSequence 단일 경로 |
| `id()` 사용 | `\bid\([a-zA-Z_]` | object id = process 마다 메모리 다름 | object 의 stable identity 사용 (e.g., name 또는 hashlib) |
| `time.time()` seed | `\.seed\([^)]*time\.time\(\)` | 매 호출 다름 | 명시 base_seed |
| `datetime.now()` seed | `\.seed\([^)]*datetime\.(now|utcnow)\(\)` | 동일 | 동일 |
| `uuid.uuid4()` seed | `\.seed\([^)]*uuid\.uuid4\(\)` | 매 호출 random | `uuid.uuid5(NAMESPACE, name)` deterministic |

## 카탈로그 — 일반 환경

| 패턴 | 발현 | 정정 |
|---|---|---|
| `os.listdir()` / `glob.glob()` 정렬 안 함 | OS 별 / 파일시스템 별 순서 다름 | `sorted(...)` 명시 |
| dict iteration 의존 (PYTHONHASHSEED 미설정 + Python 3.6 미만) | dict 순서 비결정 | Python 3.7+ insertion-order 보장 + PYTHONHASHSEED=0 |
| multiprocessing 결과 합산 | worker 완료 순서 비결정 | `pool.map` (순서 보장) 또는 명시 sort |
| threading race | 메모리 visibility | `threading.Lock` + ordered queue |
| timestamp / wall-clock 출력 leak | summary.json 안에 박힘 | metadata 분리 또는 frozen_clock |

## 검사 알고리즘 (phase 09 §V6-Evidence-Bound 호출)

```python
import re, subprocess, pathlib

PATTERNS = [
    (r'SeedSequence\([^)]*hash\(', 'cap_correctness', 'hash() salt in SeedSequence'),
    (r'np\.random\.seed\(.*hash\(', 'cap_correctness', 'hash() salt in numpy seed'),
    (r'random\.seed\(.*hash\(', 'cap_correctness', 'hash() salt in random.seed'),
    (r'os\.urandom\(\d+\)\s*[+\|^]', 'cap_correctness', 'os.urandom mixed into seed'),
    (r'\bid\([a-zA-Z_]', 'warning', 'id() used (memory-dependent)'),
    (r'\.seed\([^)]*time\.time\(\)', 'cap_correctness', 'time.time() as seed'),
    (r'\.seed\([^)]*uuid\.uuid4\(\)', 'cap_correctness', 'uuid.uuid4() as seed'),
]

def scan_violations(src_root: pathlib.Path) -> list[dict]:
    violations = []
    for py in src_root.rglob('*.py'):
        text = py.read_text(encoding='utf-8', errors='ignore')
        for pattern, severity, why in PATTERNS:
            for m in re.finditer(pattern, text):
                violations.append({
                    'file': str(py),
                    'pattern': pattern,
                    'match': m.group(0),
                    'severity': severity,
                    'why': why,
                })
    return violations
```

## frontmatter (gate_v6_reproducibility.json 의 `anti_pattern_grep` 절)

```json
{
  "anti_pattern_grep": {
    "scanned_globs": ["src/**/*.py"],
    "patterns_checked": 7,
    "violations": []
  }
}
```

`violations` 비어 있어야 phase 09 진입 허용.

## 다른 언어로 확장

[`polyglot-code-quality.md`](polyglot-code-quality.md) 의 언어별 표 정합 — Go / Rust / TypeScript 의 cross-process 비결정 함수 카탈로그는 본 컨벤션에서 분기.

| 언어 | 핵심 anti-pattern |
|---|---|
| Go | `time.Now().UnixNano()` seed, map iteration 순서 (1.0+ randomized) |
| Rust | `rand::thread_rng()` (process-local), `HashMap` (DoS resistance random hasher) |
| TypeScript / Node | `Date.now()` seed, `Math.random()` (no seed control), object key order |

## self_lint C-CXP (cross-process anti-pattern catalogue)

본 컨벤션 파일 존재 + phase 09-quality-gates.md 본문에 `cross-process-anti-patterns.md` 참조 + §V6-Evidence-Bound 키워드 박힘 검증.

## 안티 패턴 (본 컨벤션 *적용* 안티)

a- **카탈로그 외부 비결정 함수 만남 시 무시** — 새 패턴 발견 시 본 카탈로그 *추가* 의무. silent skip 금지.
b- **regex false positive 회피로 검사 무력화** — false positive 발생 시 더 좁은 regex 로 좁히되 검사 자체 skip 금지. allow_list 본문에 명시.
c- **PYTHONHASHSEED 만 강제하고 실 anti-pattern grep skip** — PYTHONHASHSEED=0 도 일부 패턴 (e.g., `os.urandom`, `time.time`) 못 막음.

## 메모리 정합

- [`project_bench_001_v0944.md`](../../../memory/project_bench_001_v0944.md) — D-6/V6 회귀 root cause 사례.
- [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md) — 컨벤션 런타임 집행 결손의 직접 보강.
