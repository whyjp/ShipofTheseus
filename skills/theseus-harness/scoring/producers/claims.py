"""claims.py — backing-kind 검증 코어 (판단-게이트 스펙 §3.1). verdict 아님.

이 모듈은 *측정 코어*이지 판정기·증거 조립기가 아니다. 각 검증기는 순수 디스크
검사(파일 존재·텍스트 매칭·git diff 조회·AST import/심볼 조회)로 `(bool, detail)`
을 반환한다. detail 은 리포트 artifact 에 기록될 근거(무엇을 어디서 확인했는지)이며
항상 JSON 직렬화 가능하다.

층 분리 불변식(JW1 특칙):
  - Evidence 를 만들지 않는다 — `_evidence_common` 을 import 하지 않는다.
  - 시간(datetime)/난수(random)/네트워크 접근 금지 — 같은 디스크 상태 → 같은 결과
    (결정성, 스펙 §2 원칙5).
  - backing kind 화이트리스트는 모듈 상수(`BACKING_KINDS` frozenset)로 닫는다 —
    런타임 등록 API 를 두지 않는다(임의 검사 표면 차단, 스펙 §3.1).
  - 화이트리스트 밖 kind → `UnknownBackingKind` 예외. 그 외 모든 실패(파일 부재·
    파싱 실패·ctx 결손·ref 형오류)는 예외가 아니라 `(False, detail)` — 측정 실패는
    '미검증'으로 관측된다(스펙 §2 원칙2 "증거 없음 = FAIL"과 동형).
  - 모든 read_text/subprocess 는 `encoding="utf-8"` 명시(self_lint C35).

저장소 self_lint C35 — 모든 파일 접근 `encoding="utf-8"`.
"""
from __future__ import annotations

import ast
import fnmatch
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

# 닫힌 화이트리스트 — 이 밖의 kind 는 UnknownBackingKind. 런타임 등록 API 없음.
BACKING_KINDS: frozenset[str] = frozenset(
    {
        "test",
        "symbol",
        "diff",
        "file",
        "absent_import",
        "import_of",
        "symbol_count_max",
    }
)


class UnknownBackingKind(ValueError):
    """화이트리스트 밖 kind — 임의 검사 표면 차단 (스펙 §3.1)."""


@dataclass
class Context:
    """검증기가 읽는 디스크 핸들 — 필요한 필드만 채워서 쓴다. 결손(None)은
    '검증 불가 → False' 로 관측된다(스펙 §3.1 ctx 결손 규칙)."""

    submission: Path | None = None      # 제출물 루트 (file/symbol)
    git_files: list[str] | None = None  # git diff --name-only 결과, posix 상대경로 (symbol/diff)
    junit: dict[str, str] | None = None  # test id -> "passed"|"failed"|"error"|"skipped" (test)
    code_root: Path | None = None       # AST 스캔 루트 (absent_import/import_of/symbol_count_max)
    module: str | None = None           # code_root 기준 posix 상대경로 (모듈 스코프 3종)


# --- 공유 유틸 -----------------------------------------------------------------


def match_glob(path: str, pattern: str) -> bool:
    """posix 경로 glob 매칭 단일 소스 — fnmatch.fnmatchcase. `*` 는 `/` 를 가로지른다
    (`**` ≡ `*`). diff kind 와 measure_scope_map(JW3)이 공유한다."""
    return fnmatch.fnmatchcase(path, pattern)


def git_diff_files(repo: Path, base: str) -> tuple[list[str] | None, str | None]:
    """`git -C repo diff --name-only base`. 성공 → (files, None), 실패 → (None, error).
    measure_submission._git_diff_files 와 동일 의미(그 파일은 무수정이라 재구현)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "diff", "--name-only", base],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        return None, f"git invocation failed: {exc}"
    if proc.returncode != 0:
        return None, f"git diff exit {proc.returncode}: {proc.stderr.strip()}"
    files = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return files, None


def _module_tree(code_root: Path, module: str) -> ast.Module | None:
    """code_root/module 를 AST 로 파싱. 파일 부재/SyntaxError/ValueError → None
    (예외로 producer 를 죽이지 않는다 — 측정 실패는 '미검증'으로 관측)."""
    path = code_root / module
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return ast.parse(text)
    except (SyntaxError, ValueError):
        return None


def _module_imports(code_root: Path, module: str) -> set[str] | None:
    """모듈의 AST import 집합. 파일 부재·파싱 실패 → None.

    ast.Import: alias.name(dotted 전체) + 최상위 세그먼트.
    ast.ImportFrom: node.module(있으면 dotted 전체 + 최상위 세그먼트) + 각 alias.name.
    (예: `from sqlite3 import connect` → {"sqlite3", "connect"} 기여 —
    absent_import ref="sqlite3" 가 from-import 도 잡는다.)
    """
    tree = _module_tree(code_root, module)
    if tree is None:
        return None
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
                imports.add(node.module.split(".")[0])
            for alias in node.names:
                imports.add(alias.name)
    return imports


# --- 검증기 (kind 별 — 스펙 §3.1 표의 코드 절차) --------------------------------
#
# 각 검증기는 (ref, ctx) 를 받아 (bool, detail) 반환. detail 에 "kind"/"ref" 는
# verify() 가 주입하므로 여기서는 "reason" + 근거 필드만 채운다. 필요한 ctx 필드가
# None 이면 즉시 (False, {"reason": "<field> not provided"}) (ctx 결손 규칙).


def _verify_test(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.junit is None:
        return False, {"reason": "junit not provided"}
    if not isinstance(ref, str):
        return False, {"reason": "ref must be a string"}
    status = ctx.junit.get(ref)
    if status is None:
        return False, {"reason": "test id not found in junit"}
    if status != "passed":
        return False, {"reason": "test not passed", "status": status}
    return True, {"reason": "verified", "status": status}


def _verify_symbol(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.submission is None:
        return False, {"reason": "submission not provided"}
    if ctx.git_files is None:
        return False, {"reason": "git_files not provided"}
    if not isinstance(ref, str):
        return False, {"reason": "ref must be a string"}
    pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(ref) + r"(?![A-Za-z0-9_])")
    for f in sorted(ctx.git_files):
        p = ctx.submission / f
        if not p.is_file():
            # 디스크에서 지워진 diff 파일은 건너뜀 — 읽을 수 없는 것은 근거가 아니다.
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            return True, {"reason": "verified", "matched_file": f}
    return False, {"reason": "symbol not found in any diff file"}


def _verify_diff(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.git_files is None:
        return False, {"reason": "git_files not provided"}
    if not isinstance(ref, str):
        return False, {"reason": "ref must be a string"}
    for f in sorted(ctx.git_files):
        if match_glob(f, ref):
            return True, {"reason": "verified", "matched_file": f}
    return False, {"reason": "no diff file matches glob"}


def _verify_file(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.submission is None:
        return False, {"reason": "submission not provided"}
    if not isinstance(ref, str):
        return False, {"reason": "ref must be a string"}
    if Path(ref).is_absolute():
        return False, {"reason": "ref escapes submission root"}
    root = ctx.submission.resolve()
    target = (ctx.submission / ref).resolve()
    if not target.is_relative_to(root):
        return False, {"reason": "ref escapes submission root"}
    if target.exists():
        return True, {"reason": "verified"}
    return False, {"reason": "file absent"}


def _verify_absent_import(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.code_root is None:
        return False, {"reason": "code_root not provided"}
    if ctx.module is None:
        return False, {"reason": "module not provided"}
    if not isinstance(ref, str):
        return False, {"reason": "ref must be a string"}
    imports = _module_imports(ctx.code_root, ctx.module)
    if imports is None:
        # absence 를 검증하려면 파싱이 성공해야 한다 — 못 읽으면 미검증.
        return False, {"reason": "module unreadable or unparseable"}
    if ref in imports:
        return False, {"reason": "concrete import present"}
    return True, {"reason": "verified", "imports_scanned": len(imports)}


def _verify_import_of(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.code_root is None:
        return False, {"reason": "code_root not provided"}
    if ctx.module is None:
        return False, {"reason": "module not provided"}
    if not isinstance(ref, str):
        return False, {"reason": "ref must be a string"}
    imports = _module_imports(ctx.code_root, ctx.module)
    if imports is None:
        return False, {"reason": "module unreadable or unparseable"}
    if ref in imports:
        return True, {"reason": "verified", "imports_scanned": len(imports)}
    return False, {"reason": "abstract import absent"}


_SYMBOL_KINDS = frozenset({"public_class", "public_function"})


def _verify_symbol_count_max(ref: Any, ctx: Context) -> tuple[bool, dict]:
    if ctx.code_root is None:
        return False, {"reason": "code_root not provided"}
    if ctx.module is None:
        return False, {"reason": "module not provided"}
    if not isinstance(ref, dict):
        return False, {"reason": "invalid ref shape"}
    symbol = ref.get("symbol")
    v_max = ref.get("max")
    if symbol not in _SYMBOL_KINDS:
        return False, {"reason": "invalid ref shape"}
    if not isinstance(v_max, int) or isinstance(v_max, bool) or v_max < 0:
        return False, {"reason": "invalid ref shape"}
    tree = _module_tree(ctx.code_root, ctx.module)
    if tree is None:
        return False, {"reason": "module unreadable or unparseable"}
    count = 0
    for node in tree.body:  # 모듈 최상위(body 직속)만 — 중첩 def/메서드는 미계수.
        if symbol == "public_class":
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                count += 1
        else:  # public_function
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                count += 1
    ok = count <= v_max
    reason = "verified" if ok else "symbol count exceeds max"
    return ok, {"reason": reason, "count": count, "max": v_max, "symbol": symbol}


_VERIFIERS: dict[str, Callable[[Any, Context], tuple[bool, dict]]] = {
    "test": _verify_test,
    "symbol": _verify_symbol,
    "diff": _verify_diff,
    "file": _verify_file,
    "absent_import": _verify_absent_import,
    "import_of": _verify_import_of,
    "symbol_count_max": _verify_symbol_count_max,
}


def verify(claim: dict, ctx: Context) -> tuple[bool, dict]:
    """claim = {"kind": str, "ref": str|dict}. kind 화이트리스트 밖 → UnknownBackingKind.
    그 외 어떤 실패(파일 부재·파싱 실패·ctx 결손·ref 형오류)도 예외가 아니라
    (False, detail) — 측정 실패는 '미검증'으로 관측된다.

    반환 detail 은 항상 JSON 직렬화 가능하고 최소 {"kind","ref","reason"} 를 담는다.
    """
    kind = claim.get("kind")
    ref = claim.get("ref")
    if kind not in BACKING_KINDS:
        raise UnknownBackingKind(str(kind))
    ok, detail = _VERIFIERS[kind](ref, ctx)
    full: dict = {"kind": kind, "ref": ref}
    full.update(detail)
    return ok, full
