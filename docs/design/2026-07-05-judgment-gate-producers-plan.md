# 구현 계획 — 판단-게이트 Producer (JW1~JW5)

> **작성**: Claude Fable 5 (설계·계획 산출물 소유자)
> **일자**: 2026-07-05
> **확정 스펙(계약)**: `docs/design/2026-07-05-judgment-gate-producers-design.md` — 어긋나면 **스펙이 우선**
> **실행자**: JW1/JW4 = opus, JW2/JW3/JW5 = sonnet (§9 WP 표)
> **통합 검증**: 오케스트레이터 직접 수행 (본 문서 말미 디스패치 노트)

---

## 스펙과의 차이

**없음.** 스펙과 모순되는 결정은 없다. 다만 스펙이 열어둔 지점을 아래와 같이 구체화했다
(실행자는 이 구체화를 계약처럼 따른다):

1. **per-test junit 파서 신설(JW2).** `parsers.parse_junit` 은 집계 카운트만 반환하고
   test-id→상태 맵을 주지 않는다. 스펙 §3.1 `test` kind 는 "ctx.junit 에 존재 AND
   상태=passed" 를 요구하므로 `parsers.py` 에 **추가 전용** 함수 `parse_junit_cases` 를
   신설한다(기존 `parse_junit`/`parse_coverage` 는 한 글자도 수정 금지). parsers.py 는
   스펙 §0 무수정 목록(커널·measure_submission·CheckSpec·manifest)에 없다.
2. **glob 의미론 단일화.** `diff` kind 와 scope_map 의 path glob 은 모두
   `claims.match_glob`(= `fnmatch.fnmatchcase`, posix 문자열) 하나를 쓴다. fnmatch 의
   `*` 는 `/` 를 가로지르므로 `**` 와 `*` 는 동치다 — 스펙 예시(`src/auth/**`,
   `src/auth/reset*.py`)를 모두 만족하며, 두 소비자의 의미론이 갈라지지 않는다.
3. **git diff 헬퍼는 claims.py 에 둔다.** measure_submission(무수정)과
   `_evidence_common.py`(수정 금지, §9 병렬성 주의)를 건드릴 수 없으므로, JW2/JW3 이
   공유할 `git_diff_files` 를 JW1 의 claims.py(공유 코어)에 둔다. 시그니처·의미는
   `measure_submission._git_diff_files` 와 동일하게 재구현한다.
4. **test-id 중복 시 worst-status-wins.** 같은 이름의 testcase 가 여러 개면(클래스가
   다른 동명 테스트) 가장 나쁜 상태(failed > error > skipped > passed)를 기록한다 —
   ref 가 verified 이려면 그 이름의 **모든** 케이스가 passed 여야 한다(보수적·결정적).
5. **선언 아티팩트의 판정 필드 = 즉시 거부(exit 2).** 스펙 §2 불변식1 "판정 필드를
   담으면 계약 위반"을 관측 가능한 동작으로 강제한다: criteria/todos/contract 엔트리에
   `verified`/`score`/`pass`/`passed`/`result`/`verdict` 키가 있으면 producer 는 emit
   없이 exit 2 로 종료한다(무시하고 재검사하는 것보다 위반을 조기에 드러낸다).
6. **exit code 정책(3 producer 공통).** `0` = 정상 실행(emit 됐거나, 정직한 결손으로
   의도적 미emit) / `2` = 선언 아티팩트 저작 오류(JSON 파싱 불가·스키마 위반·화이트리스트
   밖 backing kind·판정 필드 포함). "선언 자체가 없어서 못 잰다"(결손)와 "선언이
   틀렸다"(저작 오류)를 exit code 로 구분한다.
7. **enumeration 밖 모듈의 claim 도 검사는 한다(JW4).** 스펙 §3.4 는 그 모듈을 "통과
   불가로 계수"만 규정한다. dip_violation 규칙(§3.4 "DIP claim 중 하나라도 미검증이면
   1")은 enumeration 여부를 가르지 않으므로, claim 검증 자체는 수행하고 결과를 리포트에
   남기되 모듈 통과 계수에서만 제외한다.

---

## 공통 규약 (모든 WP 에 적용)

### 파일 경계 — 절대 수정 금지 목록

어떤 WP 도 다음을 수정하지 않는다(읽기·import 는 허용):

- `skills/theseus-harness/scoring/kernel/` 전부 (evidence.py, checkspec.py, kernel.py, meta_audit.py, manifest.py)
- `skills/theseus-harness/scoring/producers/measure_submission.py`
- `skills/theseus-harness/scoring/producers/_evidence_common.py`
- `skills/theseus-harness/scoring/producers/measure_deep_module.py`
- `skills/theseus-harness/checks/*.json` (CheckSpec 레지스트리)
- `skills/theseus-harness/pipeline.manifest.json`

WP 별 소유 파일(이 밖은 손대지 않는다 — 병렬 충돌 방지):

| WP | 생성 | 수정 |
|---|---|---|
| JW1 | `producers/claims.py`, `producers/tests/test_claims.py` | — |
| JW2 | `producers/measure_intent_fidelity.py`, `producers/tests/test_measure_intent_fidelity.py` | `producers/parsers.py` (**추가 전용**: `parse_junit_cases`) |
| JW3 | `producers/measure_scope_map.py`, `producers/tests/test_measure_scope_map.py` | — |
| JW4 | `producers/measure_solid_static.py`, `producers/tests/test_measure_solid_static.py` | `scoring/deep_module_metric.py` (**추출 전용**: `enumerate_modules`) |
| JW5 | `scoring/dogfood_inputs/{intent-criteria,plan-todos,solid-contract}.json` | `scoring/dogfood.py`, `scoring/test_dogfood.py`(기대값 갱신), `docs/design/2026-07-04-kernel-dogfood-report.md` |

(경로 접두 `producers/` = `skills/theseus-harness/scoring/producers/`, `scoring/` =
`skills/theseus-harness/scoring/`.)

### 불변식 가드 (스펙 §2 — 위반 시 리뷰 반려)

1. **producer 는 verdict/score 를 emit 하지 않는다.** measured 에 들어가는 것은 원시
   측정값(이산화·집계 = "기계 검증 결과의 결정 함수")뿐. evidence JSON 직렬화 문자열에
   `"verdict"`/`"pass"` 키가 없음을 테스트로 단언한다(기존
   `test_measure_deep_module.test_producer_emits_raw_values_no_verdict_mixed_in` 패턴).
2. **선언 아티팩트의 판정을 신뢰하지 않는다.** 모든 backing 은 claims.py 가 디스크에서
   재검사한다. 판정 필드가 들어오면 exit 2(구체화 결정 5).
3. **claim 0개(또는 intent 의 required 0개) → emit 안 함.** 커널 법칙1
   (evidence_missing)이 FAIL 하도록 결손을 유지한다 — 무노동 만점 봉쇄.
4. **결정성.** 판정 경로에서 시간/난수/네트워크 금지. `measured_at` 은
   `--measured-at` 주입 가능(기본 `ec.now_iso()`), 컬렉션 순회는 정렬 고정, 리포트
   artifact 에는 **절대경로를 넣지 않는다**(code_root/submission 기준 posix 상대경로만)
   — 같은 fixture 2회 실행 시 리포트·evidence 바이트 동일이 성립해야 한다.
5. **`encoding="utf-8"`.** 모든 open/read_text/write_text/subprocess 에 명시
   (self_lint C35). 파일 쓰기는 `ec.write_json_artifact`/`ec.write_evidence` 경유.

### Evidence 조립 공통 패턴

세 producer 모두 `_evidence_common`(`import _evidence_common as ec`) 를 재사용한다 —
`ec.write_json_artifact`(리포트), `ec.relpath`/`ec.sha256_of_file`(provenance),
`ec.build_measured`/`ec.assemble_record`/`ec.write_evidence`(레코드). Evidence 조립
로직을 자체 구현하면 반려. `run_root = out_dir.parent`, `project_run` 기본
`run_root.name`, `produced_by="run"`/`self_reported=False` 는 `assemble_record` 고정.

emit 파일명/리포트명(스펙 §3.2~3.4 확정):

| producer | check_id | evidence 파일 | 리포트 artifact | measured 키 |
|---|---|---|---|---|
| intent | `gate.intent_fidelity` | `gate.intent_fidelity.json` | `gate.intent_fidelity.report.json` | `intent_fidelity` |
| scope | `gate.scope_map` | `gate.scope_map.json` | `gate.scope_map.report.json` | `files_mapped_to_todos` |
| solid | `gate.solid_static` | `gate.solid_static.json` | `gate.solid_static.report.json` | `modules_passing_solid`, `modules_total`, `dip_violation` |

`gate.*` 는 사전순으로 `quality.*`/`scoring.*` 앞이라 `_index_from_evidence`(사전순
첫 파일 승리)에서 항상 신규 producer 값이 승계된다(스펙 §4.1). 리포트 `*.report.json`
은 최상위 `measured` dict 가 없으므로 `_index_from_evidence` 가 무시한다 — 리포트에
`measured` 라는 최상위 키를 만들지 말 것.

CLI 공통 인자: `--phase <str>`(정보용 기본값은 WP 별), `--project-run`,
`--measured-at`(결정성 주입), `--out-dir`(required, `<run>/evidence`). producer_cmd 는
measure_deep_module 의 `_reconstruct_cmd` 패턴("python <script 절대경로> <핵심 인자>")
을 따른다 — gate.* 에는 CheckSpec 이 없으므로 cmd_pattern 제약은 없지만 스타일을
통일한다. stdout 으로 요약 JSON 한 덩어리를 낸다(기존 producer 와 동일).

### 테스트 공통 패턴

- 위치: `producers/tests/` — conftest.py 가 producers/kernel/scoring 세 디렉터리를
  sys.path 에 넣어주므로 평면 import(`import claims`, `import measure_scope_map`,
  `import kernel`, `import evidence as evidence_mod`, `import checkspec`,
  `import measure_submission`) 사용.
- 고정 타임스탬프 `FIXED_TS = "2026-07-05T00:00:00+00:00"`.
- 실 CheckSpec 로드: `REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"`
  → `checkspec.load_checkspec(REAL_CHECKS_DIR / "scoring.correctness.json")` 등.
- 커널 왕복: producer 실행 → `measure_submission.run(build_parser().parse_args([...]))`
  (`--from-evidence` = producer out_dir) → emit 된 `scoring.*.json` 을
  `evidence_mod.load_evidence` 로 로드 → `kernel.verify(spec, ev,
  artifact_root=run_root, verified_at=FIXED_TS)` 로 PASS/FAIL 재판정.
- **git fixture 헬퍼**(JW2/JW3 커널 왕복에 필수 — 그대로 구현):

  ```python
  def _make_repo(root: Path, base: dict[str, str], changed: dict[str, str]) -> None:
      """base 파일들을 커밋한 뒤 changed 파일들을 워킹트리에만 반영 —
      `git diff --name-only HEAD` 가 changed 키 목록을 내도록 만든다."""
      root.mkdir(parents=True, exist_ok=True)
      run = lambda *a: subprocess.run(
          ["git", "-C", str(root), *a], check=True, capture_output=True,
          text=True, encoding="utf-8")
      run("init", "-q")
      run("config", "user.email", "t@t")
      run("config", "user.name", "t")
      for rel, text in base.items():
          p = root / rel; p.parent.mkdir(parents=True, exist_ok=True)
          p.write_text(text, encoding="utf-8")
      run("add", "-A"); run("commit", "-q", "-m", "base")
      for rel, text in changed.items():
          p = root / rel; p.parent.mkdir(parents=True, exist_ok=True)
          p.write_text(text, encoding="utf-8")
  ```

- **결정성 테스트 2종**: (a) 같은 fixture·같은 `--measured-at` 로 producer 를 2회
  실행(2회차가 덮어씀) → evidence·리포트 파일의 **바이트**가 1회차 캡처와 동일.
  (b) 서로 다른 tmp 루트 2곳에 동일 fixture → 두 evidence 의 `measured` dict 동일
  (deep_module 테스트 패턴 — producer_cmd 는 절대경로라 비교에서 제외).

---

## JW1 — `claims.py` 공유 backing 검증 코어 (opus, 임계 경로)

### 파일

- 생성: `skills/theseus-harness/scoring/producers/claims.py`
- 생성: `skills/theseus-harness/scoring/producers/tests/test_claims.py`
- 그 외 일절 수정 금지(다른 producer 파일이 아직 없어도 만들지 않는다 — JW2~4 소유).

### 공개 인터페이스 (이 시그니처가 JW2/JW3/JW4 의 계약)

```python
"""claims.py — backing-kind 검증 코어 (판단-게이트 스펙 §3.1). verdict 아님."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

BACKING_KINDS: frozenset[str]  # {"test","symbol","diff","file","absent_import","import_of","symbol_count_max"}

class UnknownBackingKind(ValueError):
    """화이트리스트 밖 kind — 임의 검사 표면 차단 (스펙 §3.1)."""

@dataclass
class Context:
    """검증기가 읽는 디스크 핸들 — 필요한 필드만 채워서 쓴다. 결손(None)은
    '검증 불가 → False' 로 관측된다(스펙 §3.1 ctx 결손 규칙)."""
    submission: Path | None = None      # 제출물 루트 (file/symbol)
    git_files: list[str] | None = None  # git diff --name-only 결과, posix 상대경로 (symbol/diff)
    junit: dict[str, str] | None = None # test id -> "passed"|"failed"|"error"|"skipped" (test)
    code_root: Path | None = None       # AST 스캔 루트 (absent_import/import_of/symbol_count_max)
    module: str | None = None           # code_root 기준 posix 상대경로 (모듈 스코프 3종)

def verify(claim: dict, ctx: Context) -> tuple[bool, dict]:
    """claim = {"kind": str, "ref": str|dict}. kind 화이트리스트 밖 → UnknownBackingKind.
    그 외 어떤 실패(파일 부재·파싱 실패·ctx 결손·ref 형오류)도 예외가 아니라
    (False, detail) — 측정 실패는 '미검증'으로 관측된다."""

def match_glob(path: str, pattern: str) -> bool:
    """posix 경로 glob 매칭 단일 소스 — fnmatch.fnmatchcase. `*` 는 `/` 를 가로지른다
    (`**` ≡ `*`). diff kind 와 measure_scope_map(JW3)이 공유한다."""

def git_diff_files(repo: Path, base: str) -> tuple[list[str] | None, str | None]:
    """`git -C repo diff --name-only base`. 성공 → (files, None), 실패 → (None, error).
    measure_submission._git_diff_files 와 동일 의미(그 파일은 무수정이라 재구현)."""
```

내부 레지스트리: `_VERIFIERS: dict[str, Callable[[Any, Context], tuple[bool, dict]]]`
— `verify` 는 kind 조회 → 없으면 `raise UnknownBackingKind(kind)` → 있으면 위임.
detail dict 는 **항상 JSON 직렬화 가능**하고 최소 `{"kind": ..., "ref": ..., "reason": <str>}`
를 담는다(True 인 경우 reason 은 `"verified"` + 근거 필드, False 는 실패 사유).

### 검증기 알고리즘 (kind 별 — 스펙 §3.1 표의 코드 절차)

모든 검증기 공통: 필요한 ctx 필드가 None 이면 즉시
`(False, {..., "reason": "<field> not provided"})` (ctx 결손 규칙).

1. **`test`** — ref 가 str 아니면 False("ref must be a string"). `status =
   ctx.junit.get(ref)`; 없으면 False("test id not found in junit");
   `status != "passed"` 면 False(detail 에 status); 아니면 True.
2. **`symbol`** — ctx.git_files·ctx.submission 필요. 패턴
   `re.compile(r"(?<![A-Za-z0-9_])" + re.escape(ref) + r"(?![A-Za-z0-9_])")`
   (단어 경계 — `AuthService` 가 `AuthServiceX` 에 매칭되지 않게). `sorted(ctx.git_files)`
   순회, `ctx.submission / f` 가 `is_file()` 인 것만
   `read_text(encoding="utf-8", errors="replace")` 로 읽어 search. 첫 매칭에서
   True(detail `matched_file`). 끝까지 없으면 False("symbol not found in any diff file").
   (디스크에서 지워진 diff 파일은 건너뜀 — 읽을 수 없는 것은 근거가 아니다.)
3. **`diff`** — ctx.git_files 필요. `sorted(ctx.git_files)` 중
   `match_glob(f, ref)` 첫 매칭 → True(detail `matched_file`); 없으면 False.
4. **`file`** — ctx.submission 필요. ref 가 절대경로이거나
   `(submission / ref).resolve()` 가 `submission.resolve()` 밖이면
   False("ref escapes submission root"). 아니면 존재 여부가 곧 결과.
5. **`absent_import`** — `imports = _module_imports(ctx.code_root, ctx.module)`;
   None(파일 부재·SyntaxError)이면 False(사유 명시 — *absence 를 검증하려면 파싱이
   성공해야 한다*). `ref in imports` → False("concrete import present"),
   아니면 True(detail 에 `imports_scanned` 개수).
6. **`import_of`** — 같은 `_module_imports`; None → False. `ref in imports` → True,
   아니면 False("abstract import absent").
7. **`symbol_count_max`** — ref 는 `{"symbol": "public_class"|"public_function",
   "max": int(>=0)}`; 형오류 → False("invalid ref shape"). 모듈 AST 파싱 실패 → False.
   **모듈 최상위(body 직속)** 의 public(이름이 `_` 로 시작하지 않는) `ClassDef`
   (public_class) / `FunctionDef`+`AsyncFunctionDef`(public_function) 개수 `n`;
   `n <= max` 가 결과(detail 에 `count`/`max`).

`_module_imports(code_root: Path, module: str) -> set[str] | None`(내부):
`path = code_root / module`; `is_file()` 아니면 None; `ast.parse(read_text(utf-8,
errors="replace"))`, `SyntaxError`/`ValueError` → None. 집합 구성 —
`ast.Import`: `alias.name`(dotted 전체) + 최상위 세그먼트(`name.split(".")[0]`);
`ast.ImportFrom`: `node.module`(있으면 dotted 전체 + 최상위 세그먼트) + 각
`alias.name`. (예: `from sqlite3 import connect` 는 {"sqlite3","connect"} 기여 —
`absent_import ref="sqlite3"` 가 from-import 도 잡는다.)

`git_diff_files`: `subprocess.run(["git","-C",str(repo),"diff","--name-only",base],
capture_output=True, text=True, encoding="utf-8")`; `OSError/ValueError` →
`(None, f"git invocation failed: {exc}")`; returncode != 0 → `(None, f"git diff exit
{rc}: {stderr.strip()}")`; 성공 → 비어있지 않은 줄 리스트.

### 테스트 매트릭스 (`test_claims.py`)

fixture: `tmp_path` 에 소형 파일 트리 직접 작성(임시 git repo 불필요 — git_files 는
리스트로 직접 주입). 각 kind True/False + ctx 결손:

| # | 케이스 | 기대 |
|---|---|---|
| 1 | test: junit 맵에 passed → | True |
| 2 | test: failed 상태 | False, detail.status=="failed" |
| 3 | test: id 부재 | False |
| 4 | test: ctx.junit None | False, reason 에 "not provided" |
| 5 | symbol: touched 파일 텍스트에 존재 | True, matched_file |
| 6 | symbol: 어디에도 없음 | False |
| 7 | symbol: `AuthService` vs 파일엔 `AuthServiceX` 만 | False (경계 매칭) |
| 8 | symbol: git_files None | False |
| 9 | symbol: diff 목록의 파일이 디스크에 없음(삭제) | False (건너뜀) |
| 10 | diff: `src/auth/reset*.py` 가 `src/auth/reset_pw.py` 에 매칭 | True |
| 11 | diff: `src/auth/**` 가 `src/auth/x/y.py` 에 매칭 (중첩) | True |
| 12 | diff: 무매칭 / git_files None | False / False |
| 13 | file: 존재 / 부재 | True / False |
| 14 | file: `../escape.txt` | False (root 이탈) |
| 15 | absent_import: 모듈이 `import sqlite3` | False |
| 16 | absent_import: `from sqlite3 import connect` | False (from-import 도 잡힘) |
| 17 | absent_import: import 없음 | True |
| 18 | absent_import: 모듈 파일 부재 / SyntaxError 파일 | False / False (예외 아님) |
| 19 | absent_import: ctx.module None | False |
| 20 | import_of: `from x import Repository`, ref="Repository" | True |
| 21 | import_of: 부재 | False |
| 22 | symbol_count_max: public class 1개, max 1 | True, count==1 |
| 23 | symbol_count_max: public def 3개, max 2 | False |
| 24 | symbol_count_max: `_private` def/중첩 def 는 미계수 | True (계수 제외 확인) |
| 25 | symbol_count_max: ref 형오류(`max` 없음 / symbol 오타) | False, "invalid ref shape" |
| 26 | kind="grep" (화이트리스트 밖) | `pytest.raises(UnknownBackingKind)` |
| 27 | 대표 케이스들의 detail 이 `json.dumps` 가능 | 예외 없음 |
| 28 | 같은 입력 2회 → 동일 (bool, detail) | 결정성 |
| 29 | match_glob 직접: posix 경로/패턴 표본 | 문서화된 의미론 고정 |
| 30 | git_diff_files: 비-git 디렉터리 | (None, error 문자열) |

### 수용 명령

```
python -m pytest skills/theseus-harness/scoring/producers/tests/test_claims.py -q
```
전건 통과. 추가로 기존 회귀 없음:
```
python -m pytest skills/theseus-harness/scoring/producers -q
```

### 불변식 가드 (JW1 특칙)

- claims.py 는 Evidence 를 만들지 않는다 — `(bool, detail)` 반환뿐. `_evidence_common`
  import 금지(층 분리).
- 검증기 내부에서 `datetime`/`random`/네트워크 접근 금지.
- 화이트리스트는 모듈 상수로 닫는다 — 런타임 등록 API(`register_kind` 류)를 만들지
  않는다(임의 검사 표면 차단).

---

## JW2 — `measure_intent_fidelity.py` (sonnet)

### 파일

- 생성: `producers/measure_intent_fidelity.py`, `producers/tests/test_measure_intent_fidelity.py`
- 수정(추가 전용): `producers/parsers.py` — 아래 `parse_junit_cases` 함수 하나만 append.
  기존 함수·클래스·모듈 docstring 은 무수정.

### parsers.py 추가 함수

```python
def parse_junit_cases(path: str | Path) -> dict[str, str]:
    """junit XML → test id 별 상태 맵. 부재/파싱불가 시 ArtifactParseError(기존 규약).

    키: 각 <testcase> 의 name, 그리고 classname 이 있으면 "classname::name" 도 병기.
    값: failure 자식 → "failed", error → "error", skipped → "skipped", 없으면 "passed".
    같은 키가 여러 케이스에서 나오면 나쁜 상태 우선(failed > error > skipped > passed)
    — ref 하나가 여러 케이스를 가리키면 전부 passed 여야 검증된다(보수적).
    """
```

구현: `ET.parse` → `root.iter("testcase")` 순회(집계 형태와 무관하게 케이스 단위 수집).
상태 심각도 맵 `{"failed":3,"error":2,"skipped":1,"passed":0}` 으로 병합.

### CLI (스펙 §3.2)

```
python measure_intent_fidelity.py --criteria <intent-criteria.json> \
    --submission <dir> [--test-junit <path>] [--git-base HEAD] [--phase 09] \
    [--project-run <name>] [--measured-at <ISO8601>] --out-dir <run>/evidence
```

상수: `CHECK_ID = "gate.intent_fidelity"`, `DEFAULT_PHASE = "09"`,
measured source 문자열 = `"claims_backing"` (스펙 §3.2 확정).

### 알고리즘 (`run(args) -> dict`)

1. `out_dir`/`run_root`/`project_run`/`measured_at`/`producer_cmd` 준비(공통 규약).
2. **criteria 파일 부재** → `{"emitted": False, "reason": "criteria file absent"}`
   stdout, **exit 0** (정직한 결손 — phase 가 아직 저작하지 않은 경우).
3. criteria 로드·스키마 검증. 위반 시 stderr 메시지 + **exit 2**, emit 없음:
   JSON 파싱 불가 / 최상위가 `{"criteria": [...]}` 아님 / 엔트리에 `id`(str)·
   `required`(bool)·`backing`(dict, `kind` str + `ref` 존재) 결손 / 엔트리 또는
   backing 에 판정 필드(`verified`/`score`/`pass`/`passed`/`result`/`verdict`) 존재
   (구체화 결정 5) / `id` 중복.
4. **criteria 0개 또는 `required:true` 가 0개** → emit 안 함, exit 0, summary reason
   `"no required criteria - refusing vacuous measurement"` (스펙 §3.2 — optional 만으로
   0.7 바닥 확보 경로 봉쇄).
5. `git_files, git_error = claims.git_diff_files(submission, args.git_base)`.
   `--test-junit` 이 주어지면 `parsers.parse_junit_cases`; `ArtifactParseError` 는
   junit=None + 사유 기록(producer 는 죽지 않는다 — 해당 test claim 들이 ctx 결손으로
   False). 미제공이면 None. **git 실패도 no-emit 사유가 아니다** — symbol/diff claim
   이 ctx 결손 False 로 관측될 뿐(§3.1 일반 규칙; no-emit 결손 조건은 4번뿐).
6. `ctx = claims.Context(submission=submission, git_files=git_files, junit=junit_map)`.
   criteria 파일 순서대로 `claims.verify(c["backing"], ctx)`.
   `UnknownBackingKind` 는 잡아서 stderr + **exit 2** (저작 오류).
7. **이산화**(커널 assertion `intent_fidelity ∈ {1.0,0.7,0.0}`):
   - required 중 하나라도 미검증 → `0.0`
   - required 전부 검증 ∧ optional 중 하나 이상 미검증 → `0.7`
   - 전 criterion 검증 → `1.0`
8. 리포트 `gate.intent_fidelity.report.json` (`ec.write_json_artifact`):
   ```jsonc
   {"criteria": [{"id","required","kind","ref","verified","detail"} ...],  // 파일 순서
    "counts": {"required_total","required_verified","optional_total","optional_verified"},
    "git_base": "...", "git_files_count": <int|null>, "git_error": <str|null>,
    "junit_provided": <bool>, "junit_error": <str|null>,
    "value": <이산화 결과>}
   ```
   절대경로 금지(결정성 — submission 경로 자체는 리포트에 넣지 않는다).
9. `measured = {"intent_fidelity": ec.build_measured(value, "claims_backing", rel)}`,
   `artifact_digests = {rel: ec.sha256_of_file(report_path)}` →
   `ec.assemble_record(check_id=CHECK_ID, phase=args.phase, ...)` →
   `ec.write_evidence`. stdout 요약: `{"emitted": true, "value": ...,
   "evidence_path": ..., "report_path": ..., "counts": {...}}`. exit 0.

### 테스트 매트릭스 (`test_measure_intent_fidelity.py`)

| # | 케이스 | 기대 |
|---|---|---|
| 1 | parse_junit_cases: passed/failure/error/skipped 케이스 각 1 | 상태 맵 정확 + `classname::name` 병기 키 |
| 2 | parse_junit_cases: 동명 케이스 passed+failed | worst-wins → "failed" |
| 3 | parse_junit_cases: 파일 부재 | `ArtifactParseError` |
| 4 | 이산화 A: required 2 전부 검증 + optional 1 검증 | value == 1.0 |
| 5 | 이산화 B: required 전부 검증 + optional 1 미검증 | value == 0.7 |
| 6 | 이산화 C: required 1 미검증(optional 은 전부 검증) | value == 0.0 |
| 7 | criteria 0개 | emit 안 함(evidence 파일 부재), exit 0 |
| 8 | required 0개(optional 만) | emit 안 함, exit 0 |
| 9 | criteria 파일 부재 | emit 안 함, exit 0 |
| 10 | criteria JSON 깨짐 / backing.kind 화이트리스트 밖 / 엔트리에 `verified:true` | 각각 exit 2, emit 없음 |
| 11 | --test-junit 미제공 + required test claim | 그 claim False → value 0.0 (ctx 결손 규칙) |
| 12 | evidence 무판정: 직렬화에 `"verdict"`/`"pass"` 키 없음, produced_by=="run", self_reported False, measured 키 == {"intent_fidelity"} | 가드 1 |
| 13 | **커널 왕복 PASS**: `_make_repo` fixture(변경 파일 + 심볼) + junit(전부 passed) + criteria(test/symbol/diff 3종, 전부 충족) → producer → measure_submission `--from-evidence` → scoring.correctness 로드 → `kernel.verify` | result=="PASS", value == (passed/total)×1.0 |
| 14 | **커널 왕복 value 반영**: required 미검증 criteria 로 0.0 emit → 왕복 | scoring.correctness PASS(assertion 은 충족), value == 0.0 |
| 15 | **결손 유지 왕복**: producer 미실행(또는 required 0 으로 미emit) 상태에서 measure_submission | summary.skipped["scoring.correctness"] 에 "intent_fidelity" 포함, scoring.correctness 미emit |
| 16 | 결정성 (a) 같은 경로 2회 바이트 동일 (b) 두 루트 measured 동일 | 공통 규약 |
| 17 | CLI subprocess 실행(`sys.executable`) exit 0 + evidence 스키마 로드 가능 | 기존 패턴 |

### 수용 명령

```
python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_intent_fidelity.py -q
python -m pytest skills/theseus-harness/scoring/producers -q
```
전건 통과(기존 parsers/measure_submission 테스트 포함 무회귀).

---

## JW3 — `measure_scope_map.py` (sonnet)

### 파일

- 생성: `producers/measure_scope_map.py`, `producers/tests/test_measure_scope_map.py`
- 다른 파일 수정 금지 (parsers.py 도 금지 — JW2 소유).

### CLI (스펙 §3.3)

```
python measure_scope_map.py --plan-todos <plan-todos.json> --submission <dir> \
    [--git-base HEAD] [--phase 09] [--project-run <name>] \
    [--measured-at <ISO8601>] --out-dir <run>/evidence
```

상수: `CHECK_ID = "gate.scope_map"`, `DEFAULT_PHASE = "09"`,
source 문자열 = `"todo_glob_git_diff"`.

### 알고리즘

1. 공통 준비. plan-todos **파일 부재** → emit 안 함, exit 0 (결손).
2. 스키마 검증(위반 → exit 2): 최상위 `{"todos":[...]}`; 엔트리 `id`(str, 중복 금지) +
   `paths`(비어있지 않은 str 리스트); 판정 필드 존재 시 거부(구체화 결정 5).
   (`text` 는 선택 — 검사에 안 쓰고 리포트에 그대로 통과.)
3. **todos 0개** → emit 안 함, exit 0 (스펙 §3.3 결손 조건).
4. `git_files, git_error = claims.git_diff_files(submission, args.git_base)`.
   **None(diff 실패) → emit 안 함, exit 0**, summary 에 git_error (스펙 §3.3 —
   touched 집합을 관측 못 하면 측정이 아니다). **빈 리스트는 실패가 아니다** —
   `files_mapped_to_todos = 0` 을 emit 한다(측정은 성립; 커널의 scope_fit 는
   measure_submission 쪽 `files_touched > 0` assertion 으로 정직하게 FAIL).
5. 매칭: touched 파일 f 마다
   `matched = [t["id"] for t in todos if any(claims.match_glob(f, p) for p in t["paths"])]`.
   `files_mapped_to_todos = len([f for f in git_files if f 의 matched 비어있지 않음])`
   — **파일 단위 계수**(여러 todo 에 걸려도 1). matched ⊆ touched 이므로 같은
   `--git-base` 에서 `files_mapped_to_todos <= files_touched` 구조적 충족(스펙 §4.2).
6. 리포트 `gate.scope_map.report.json`:
   ```jsonc
   {"git_base": "...", "files_touched_observed": <len(git_files)>,
    "files": [{"path","matched_todos":[ids]} ... path 정렬],
    "todos": [{"id","paths"} ...], "value": <files_mapped_to_todos>}
   ```
   `files_touched_observed` 는 **리포트 전용 관측값**이다 — measured 로 emit 하지
   않는다(`files_touched` 는 measure_submission 이 자기 git diff 로 직접 측정, 스펙 §3.3).
7. measured `files_mapped_to_todos` 하나로 evidence 조립·emit. stdout 요약. exit 0.

### 테스트 매트릭스 (`test_measure_scope_map.py`)

| # | 케이스 | 기대 |
|---|---|---|
| 1 | `_make_repo`: changed 4파일 중 2개가 todo glob 에 매칭 | value == 2, 리포트 per-file matched_todos 정확 |
| 2 | 한 파일이 두 todo 에 매칭 | 1로 계수(파일 단위) |
| 3 | `src/auth/**` 가 중첩 경로 매칭 / `db/schema/**` 무매칭 파일 제외 | match_glob 의미론 |
| 4 | 전 파일 무매칭 | value == 0, emit 됨 |
| 5 | 빈 diff(변경 없음) | value == 0 emit (실패 아님) |
| 6 | todos 0개 / 파일 부재 | emit 안 함, exit 0 |
| 7 | JSON 깨짐 / paths 빈 리스트 / 판정 필드 | exit 2 |
| 8 | 비-git 디렉터리(diff 실패) | emit 안 함, exit 0, summary 에 git_error |
| 9 | evidence 무판정 + measured 키 == {"files_mapped_to_todos"} | 가드 1 |
| 10 | **커널 왕복 PASS**: 같은 `--git-base` 로 producer+measure_submission → scoring.scope_fit | PASS, value == mapped/touched, 그리고 승계값 ≤ files_touched 단언 |
| 11 | **커널 왕복 FAIL**: 빈 diff → mapped 0 emit + measure_submission files_touched 0 | scoring.scope_fit FAIL, reasons 에 "no files touched" |
| 12 | **결손 유지**: producer 미실행 → measure_submission skipped["scoring.scope_fit"] 에 "files_mapped_to_todos" | 스펙 §5 |
| 13 | 결정성 (a)(b) + CLI subprocess exit 0 | 공통 규약 |

### 수용 명령

```
python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_scope_map.py -q
python -m pytest skills/theseus-harness/scoring/producers -q
```

---

## JW4 — `measure_solid_static.py` + enumeration 추출 (opus)

### 파일

- 생성: `producers/measure_solid_static.py`, `producers/tests/test_measure_solid_static.py`
- 수정(추출 전용): `scoring/deep_module_metric.py` — `build_report` 안의 모듈 열거
  3단계(rglob·테스트 제외·`__init__` 크기 필터, 현재 137~146행)를 순수 함수로 추출:

  ```python
  def enumerate_modules(code_root: Path, ignore_tests: bool = True) -> list[Path]:
      """code_root 아래 '모듈'로 계수되는 .py 파일의 정렬된 목록 — module_count 정의의
      단일 소스. build_report(deep_module)와 measure_solid_static(JW4)가 공유해
      modules_total 브릿지 정합(설계 §4.1)을 보장한다."""
  ```

  `build_report` 는 이 함수를 호출하도록 바꾸되 **동작 불변**(반환 리스트가 기존 코드와
  파일 단위로 동일해야 한다 — 기존 `test_measure_deep_module.py`·`build_report` 경유
  테스트가 무수정 통과하는 것이 그 증명). 그 외(정규식·analyze_module·main·CLI)는 무수정.

### CLI (스펙 §3.4)

```
python measure_solid_static.py --code-root <dir> [--solid-contract <json>] \
    [--phase 08] [--project-run <name>] [--measured-at <ISO8601>] \
    --out-dir <run>/evidence
```

상수: `CHECK_ID = "gate.solid_static"`, `DEFAULT_PHASE = "08"`,
source 문자열 = `"solid_static_report"`.

### 알고리즘

1. 공통 준비. `modules = deep_module_metric.enumerate_modules(code_root)`;
   `enum_rel = [posix relpath(m, code_root) for m in modules]` (이미 정렬);
   `modules_total = len(modules)` — **0 이어도 emit 한다**(측정은 성립; 커널
   `modules_total > 0` assertion 이 정직하게 FAIL).
2. contract 처리:
   - `--solid-contract` 미제공 **또는 파일 부재** → contract 없음 경로:
     measured 는 `modules_total` **하나만**(스펙 §3.4 — `modules_passing_solid`/
     `dip_violation` 은 결손 유지, zero-config 휴리스틱 금지). summary 에
     `"solid_claims": "deficit (no contract)"` 명시. exit 0.
   - 제공+존재 → 스키마 검증(위반 exit 2): 최상위 `{"modules":[...]}`; 엔트리
     `module`(str) + `claims`(리스트; 각 `principle` str + `backing` dict); 판정 필드
     거부; 같은 `module` 경로 중복 엔트리는 claim 을 **병합**(한 모듈의 전체 claim 집합).
3. contract 각 모듈 `m`(claims 병합 후):
   - `mrel = PurePosixPath(m["module"]).as_posix()` 정규화.
   - `ctx = claims.Context(code_root=code_root, module=mrel)` 로 각 claim
     `claims.verify` (`UnknownBackingKind` → exit 2). 이 producer 의 ctx 에는
     submission/git_files/junit 이 없으므로 contract 가 test/symbol/diff/file kind 를
     선언하면 ctx 결손 False 로 관측된다(정직 — 리포트에 사유가 남는다).
   - `in_enumeration = mrel in set(enum_rel)`. **모듈 통과** = `in_enumeration` ∧
     전 claim 검증. enumeration 밖이면 통과 불가 + 리포트 사유
     `"module not in enumeration"` (claim 검증 결과 자체는 기록 — 구체화 결정 7).
4. `modules_passing_solid = |통과 모듈 집합|` — 통과 ⊆ enumeration 이므로
   `modules_passing_solid <= modules_total` 구조적 충족(스펙 §3.4).
5. `dip_violation` = contract 전체에서 `principle == "DIP"` 인 claim 중 하나라도
   미검증이면 1, 아니면 0. (DIP claim 0개면 0 — 공진리. 스펙 §7 정직 고지가 이를
   충분성 한계로 이미 문서화했으므로 producer 는 막지 않되, 리포트에
   `dip_claims_total` 을 남겨 감사 가능하게 한다.)
6. 리포트 `gate.solid_static.report.json`:
   ```jsonc
   {"modules_total": <int>, "enumeration": [rel ...],
    "contract_provided": <bool>,
    "modules": [{"module","in_enumeration","passed",
                 "claims":[{"principle","kind","ref","verified","detail"} ...]} ...],
    "dip_claims_total": <int>, "dip_claims_unverified": <int>}
   ```
   (enumeration·modules 는 code_root 상대 posix — 절대경로 금지.)
7. measured 조립: contract 있으면
   `{modules_passing_solid, modules_total, dip_violation}` 3키, 없으면
   `{modules_total}` 1키 — 모두 source `"solid_static_report"`, artifact_path=리포트.
   emit + stdout 요약(`emitted_keys` 포함). exit 0.

### 테스트 매트릭스 (`test_measure_solid_static.py`)

fixture: tmp code_root 에 소형 .py 모듈 3~4개(`import sqlite3` 하는 모듈, 추상
import 모듈, public class 2개 모듈 등) + contract JSON 조립.

| # | 케이스 | 기대 |
|---|---|---|
| 1 | enumerate_modules: tests/·test_*.py·conftest·100바이트 이하 `__init__.py` 제외, 정렬 | 필터 정확 (기존 build_report 경유 동작 불변 확인 포함) |
| 2 | 통과 계수: 모듈 A(전 claim 충족)+모듈 B(SRP 위반: public_class 2 > max 1) | passing==1, total==enumeration 수, dip_violation==0 (SRP 실패는 DIP 아님) |
| 3 | dip 케이스: DIP absent_import ref="sqlite3" 인데 모듈이 import sqlite3 | dip_violation==1 |
| 4 | dip 케이스: DIP import_of ref="Repository" 충족 + absent_import 충족 | dip_violation==0, 그 모듈 passed |
| 5 | enumeration 밖 모듈(비존재 경로) contract 에 포함 | 그 모듈 passed==False + 사유, passing 에 미계수, `passing <= total` 유지 |
| 6 | contract 미제공 | measured 키 == {"modules_total"} 만, exit 0 |
| 7 | contract 판정 필드 / 깨진 JSON / 화이트리스트 밖 kind | exit 2 |
| 8 | **modules_total 브릿지 정합**: 같은 code_root 에 measure_deep_module 과 본 producer 둘 다 실행 | 두 evidence 의 modules_total value 동일; measure_submission `--from-evidence` 승계 source 가 `from_evidence:gate.solid_static.json` (사전순 승자 = 신규 producer, 스펙 §4.1) |
| 9 | **결손 유지 왕복**: contract 없이 emit → measure_submission | skipped["scoring.solid"] 에 modules_passing_solid·dip_violation, scoring.solid 미emit (기존 deep_module 브릿지 테스트와 동형) |
| 10 | **커널 왕복 PASS**: 전 모듈 contract 충족 + dip 0 → measure_submission → scoring.solid | PASS, value == passing/total |
| 11 | **커널 왕복 FAIL**: dip_violation=1 emit → 왕복 | scoring.solid FAIL, reasons 에 "DIP violation present" |
| 12 | evidence 무판정(직렬화에 "verdict"/"pass" 없음 — 리포트의 `passed` 필드는 리포트 전용, evidence 레코드엔 없음) | 가드 1 |
| 13 | 결정성 (a)(b) + CLI subprocess exit 0 | 공통 규약 |
| 14 | modules_total==0 (빈 code_root) | emit 됨(3키 또는 1키), 커널 왕복 시 scoring.solid FAIL("no modules measured") |

### 수용 명령

```
python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_solid_static.py -q
python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_deep_module.py -q   # 추출 무회귀
python -m pytest skills/theseus-harness/scoring -q                                               # build_report 소비자 전건
```

---

## JW5 — self-repo 데모 + dogfood 갱신 (sonnet)

**선행**: JW1~JW4 머지 완료 후 시작. 이 WP 는 "3 deficit → backed 전환"을 **실측
값으로** 실증한다(스펙 §6.5) — 과장 금지: 전환되지 않는 deficit(coverage/e2e/dacapo/
tournament/regression 5종)은 그대로 deficit 로 보고한다.

### 파일

1. **선언 아티팩트 3종 생성** — `scoring/dogfood_inputs/` (신설 디렉터리):
   - `intent-criteria.json` — scoring 자기 코드에 대한 반증가능 claim. **주의**:
     dogfood 는 clean tree 에서 `--git-base HEAD` 로 돌므로 diff 가 비어 있어
     `symbol`/`diff` kind 는 False 가 된다. 워킹트리 상태와 무관하게 결정적인
     `file`/`test` kind 만 쓴다. 예:
     ```jsonc
     {"criteria": [
       {"id": "c1", "text": "커널 판정자가 존재한다", "required": true,
        "backing": {"kind": "file", "ref": "skills/theseus-harness/scoring/kernel/kernel.py"}},
       {"id": "c2", "text": "얕은 모듈 게이트가 커널 왕복으로 검증된다", "required": true,
        "backing": {"kind": "test", "ref": "test_kernel_passes_all_deep_modules"}},
       {"id": "c3", "text": "evidence 스키마 계약 파일(부가)", "required": false,
        "backing": {"kind": "file", "ref": "skills/theseus-harness/scoring/kernel/evidence.py"}}
     ]}
     ```
     (test ref 는 실제 junit 의 testcase name 과 일치해야 한다 — 저작 후 junit 을 열어
     확인하고 조정할 것. 판정 필드 금지.)
   - `plan-todos.json` — scoring 코드 영역을 덮는 todo/glob. clean tree 에선 diff 가
     비어 value 0 이 관측된다 — 그것이 정직한 값이다:
     ```jsonc
     {"todos": [
       {"id": "t1", "text": "scoring 커널/producer", "paths": ["skills/theseus-harness/scoring/**"]},
       {"id": "t2", "text": "설계 문서", "paths": ["docs/design/**"]}
     ]}
     ```
   - `solid-contract.json` — 실재 scoring 모듈 몇 개에 대한 **참인** claim 만 저작
     (저작 후 producer 를 돌려 리포트로 자기 확인 — 미검증 claim 을 그대로 두면
     dip_violation/미통과가 그대로 보고된다. 사실이 그렇다면 그대로 둔다 — 값을
     맞추려고 claim 을 지우는 것은 허용되나 거짓 claim 추가는 금지). 모듈 경로는
     `--code-root`(= `scoring/`) 기준 상대 posix. 예: `producers/_evidence_common.py`
     에 DIP `absent_import ref="requests"` + SRP `symbol_count_max public_class max 0` 등.
2. **`scoring/dogfood.py` 수정** — gate producer 단계 추가:
   - CLI 인자 추가: `--intent-criteria` / `--plan-todos` / `--solid-contract`
     (기본값 = `scoring/dogfood_inputs/` 의 세 파일 경로).
   - `_gate_producers(...)` 단계 신설: `_quality_producers` 뒤·`_submission_producer`
     앞에서 세 producer 를 `_run` 으로 호출(각각 `--out-dir <evidence_dir>`,
     `--measured-at` 주입; intent 는 `--submission <repo>` `--test-junit <junit_path>`
     `--git-base`, scope 는 `--plan-todos` `--submission` `--git-base`, solid 는
     `--code-root <code_root>` `--solid-contract`). 각 결과를
     `steps["gates"]` 에 {returncode, summary} 로 기록. 입력 파일이 없으면 그 producer
     는 건너뛰고 사유를 기록(기존 `_cold_producer` 의 부재 처리와 동형 — 정직한 결손
     경로 보존).
   - 그 외 로직(classify/meta_audit/summary 스키마) 무수정.
3. **`scoring/test_dogfood.py` 갱신** — deficit 카운트·분류를 단언하는 기존 테스트가
   있으면 새 관측값으로 갱신 + gate 단계 존재를 단언하는 케이스 추가(파일을 먼저 읽고
   실제 단언을 확인해서 고칠 것 — 추측 금지).
4. **`docs/design/2026-07-04-kernel-dogfood-report.md` 갱신** — §1 카운트 표·§1.1
   행 1~3·§1.2 evidence 목록·§2 before/after 에 재실행 실측값 반영. 문서 상단에
   갱신 이력 한 줄(일자 + "판단-게이트 producer 적용 재실행") 추가. **verdict 는
   여전히 FAIL 일 것**(coverage/e2e 등 잔여 deficit) — 그대로 정직하게 기록하고,
   "8 deficit → 5 deficit + 3 measured(각 PASS/실FAIL 값)" 전환을 값으로 보인다.

### 수용 명령 (값 기반)

```
python skills/theseus-harness/scoring/dogfood.py \
    --measured-at 2026-07-05T00:00:00+00:00 --verified-at 2026-07-05T00:00:00+00:00
```
기대(값으로 확인):
- stdout 분류에서 `scoring.correctness`/`scoring.scope_fit`/`scoring.solid` 가
  **deficit 이 아니라** PASS 또는 FAIL(실 assertion)로 나오고 value 가 붙는다.
- `counts.deficit` 이 기존 8 에서 5 로 감소, `counts.measured_backed` 가 5 에서 8 로 증가
  (실행 환경에 따라 실측값이 다르면 **관측값을 그대로** 보고서에 기록 — 숫자를 맞추기
  위한 조작 금지).
- `evidence/` 에 `gate.intent_fidelity.json`·`gate.scope_map.json`·
  `gate.solid_static.json` + 각 `.report.json` 존재.
- 같은 인자 2회 실행 → `quality/gate_meta_audit.json` 의 verdict/value/reasons 동일.

```
python -m pytest skills/theseus-harness/scoring -q      # 전건 무회귀
```

---

## 오케스트레이터용 디스패치 노트

```
JW1 (opus)  claims.py + test_claims.py          ← 임계 경로, 단독 선행
   │  머지 후
   ├── JW2 (sonnet)  measure_intent_fidelity + parsers.parse_junit_cases   ┐
   ├── JW3 (sonnet)  measure_scope_map                                     ├ 병렬
   └── JW4 (opus)    measure_solid_static + deep_module enumeration 추출   ┘
          │  3건 모두 머지 후
          └── JW5 (sonnet)  dogfood_inputs + dogfood.py/test_dogfood.py/보고 갱신
```

- **병렬 안전 근거**: JW2/JW3/JW4 는 서로 다른 신규 파일만 소유. 공유 파일 접점은
  JW2 의 `parsers.py`(추가 전용)와 JW4 의 `deep_module_metric.py`(추출 전용)뿐이고
  서로 겹치지 않는다. 셋 다 `claims.py`(JW1 산출)·`_evidence_common.py`(기존)를
  **읽기 전용**으로 쓴다.
- 각 실행자에게는 본 문서의 해당 WP 절 + "공통 규약" 절 + 스펙 문서를 함께 전달한다.
  실행자는 자기 WP 의 수용 명령까지 자기 검증하고 종료한다.
- **통합 검증은 오케스트레이터가 직접 수행한다** (JW5 완료 후, 어떤 실행자에게도
  위임하지 않는다):
  ```
  python -m pytest skills/theseus-harness/scoring -q                        # 전건 통과
  python skills/theseus-harness/scoring/self_lint.py                        # exit 0 (all_ok)
  python skills/theseus-harness/scoring/kernel/manifest.py drift-check \
      --manifest skills/theseus-harness/pipeline.manifest.json \
      --checks-dir skills/theseus-harness/checks                            # ok:true, problems []
  ```
  (신규 producer 는 CheckSpec/manifest 를 추가하지 않으므로 drift-check 는 기존 상태
  그대로 [] 여야 한다 — 달라졌다면 어떤 WP 가 금지 파일을 건드린 것이다.)
