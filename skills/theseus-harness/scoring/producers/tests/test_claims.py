"""claims.py(backing 검증 코어) 단위 테스트 — 판단-게이트 스펙 §3.1 / 계획 JW1.

테스트 매트릭스 30케이스(계획 JW1 표)를 그대로 구현한다. fixture 는 tmp_path 에 소형
파일 트리를 직접 작성하고 git_files 는 리스트로 직접 주입한다(임시 git repo 불필요 —
단, git_diff_files 자체 테스트만 비-git 디렉터리를 쓴다).

실행: python -m pytest skills/theseus-harness/scoring/producers/tests/test_claims.py -q
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import claims


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- test kind (1~4) -----------------------------------------------------------


def test_01_test_passed_true():
    ctx = claims.Context(junit={"test_login_ok": "passed"})
    ok, detail = claims.verify({"kind": "test", "ref": "test_login_ok"}, ctx)
    assert ok is True
    assert detail["kind"] == "test"
    assert detail["reason"] == "verified"


def test_02_test_failed_false_with_status():
    ctx = claims.Context(junit={"test_x": "failed"})
    ok, detail = claims.verify({"kind": "test", "ref": "test_x"}, ctx)
    assert ok is False
    assert detail["status"] == "failed"


def test_03_test_id_absent_false():
    ctx = claims.Context(junit={"other": "passed"})
    ok, detail = claims.verify({"kind": "test", "ref": "test_missing"}, ctx)
    assert ok is False


def test_04_test_junit_none_false_not_provided():
    ctx = claims.Context(junit=None)
    ok, detail = claims.verify({"kind": "test", "ref": "test_x"}, ctx)
    assert ok is False
    assert "not provided" in detail["reason"]


# --- symbol kind (5~9) ---------------------------------------------------------


def test_05_symbol_present_true_matched_file(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "src" / "auth" / "service.py", "class AuthService:\n    pass\n")
    ctx = claims.Context(submission=sub, git_files=["src/auth/service.py"])
    ok, detail = claims.verify({"kind": "symbol", "ref": "AuthService"}, ctx)
    assert ok is True
    assert detail["matched_file"] == "src/auth/service.py"


def test_06_symbol_absent_false(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "src" / "auth" / "service.py", "class Other:\n    pass\n")
    ctx = claims.Context(submission=sub, git_files=["src/auth/service.py"])
    ok, detail = claims.verify({"kind": "symbol", "ref": "AuthService"}, ctx)
    assert ok is False


def test_07_symbol_word_boundary_false(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "s.py", "class AuthServiceX:\n    pass\n")
    ctx = claims.Context(submission=sub, git_files=["s.py"])
    ok, detail = claims.verify({"kind": "symbol", "ref": "AuthService"}, ctx)
    assert ok is False  # AuthService 는 AuthServiceX 에 경계 매칭되지 않는다


def test_08_symbol_git_files_none_false(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "s.py", "class AuthService:\n    pass\n")
    ctx = claims.Context(submission=sub, git_files=None)
    ok, detail = claims.verify({"kind": "symbol", "ref": "AuthService"}, ctx)
    assert ok is False


def test_09_symbol_diff_file_missing_on_disk_skipped(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir(parents=True, exist_ok=True)  # 파일은 만들지 않음(삭제된 diff 파일)
    ctx = claims.Context(submission=sub, git_files=["src/auth/deleted.py"])
    ok, detail = claims.verify({"kind": "symbol", "ref": "AuthService"}, ctx)
    assert ok is False


# --- diff kind (10~12) ---------------------------------------------------------


def test_10_diff_star_glob_match_true():
    ctx = claims.Context(git_files=["src/auth/reset_pw.py", "README.md"])
    ok, detail = claims.verify({"kind": "diff", "ref": "src/auth/reset*.py"}, ctx)
    assert ok is True
    assert detail["matched_file"] == "src/auth/reset_pw.py"


def test_11_diff_doublestar_nested_match_true():
    ctx = claims.Context(git_files=["src/auth/x/y.py"])
    ok, detail = claims.verify({"kind": "diff", "ref": "src/auth/**"}, ctx)
    assert ok is True


def test_12_diff_no_match_and_git_files_none_false():
    ctx = claims.Context(git_files=["db/schema/a.py"])
    ok1, _ = claims.verify({"kind": "diff", "ref": "src/auth/**"}, ctx)
    assert ok1 is False
    ctx_none = claims.Context(git_files=None)
    ok2, _ = claims.verify({"kind": "diff", "ref": "src/auth/**"}, ctx_none)
    assert ok2 is False


# --- file kind (13~14) ---------------------------------------------------------


def test_13_file_exists_and_absent(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "present.py", "x = 1\n")
    ctx = claims.Context(submission=sub)
    ok_present, _ = claims.verify({"kind": "file", "ref": "present.py"}, ctx)
    ok_absent, _ = claims.verify({"kind": "file", "ref": "missing.py"}, ctx)
    assert ok_present is True
    assert ok_absent is False


def test_14_file_escape_root_false(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir(parents=True, exist_ok=True)
    _write(tmp_path / "escape.txt", "secret\n")  # 루트 밖에 실재하더라도 거부되어야
    ctx = claims.Context(submission=sub)
    ok, detail = claims.verify({"kind": "file", "ref": "../escape.txt"}, ctx)
    assert ok is False
    assert "escape" in detail["reason"]


def test_14b_file_absolute_ref_false(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "present.py", "x = 1\n")
    ctx = claims.Context(submission=sub)
    abs_ref = str((sub / "present.py").resolve())
    ok, detail = claims.verify({"kind": "file", "ref": abs_ref}, ctx)
    assert ok is False  # 절대경로 ref 는 거부


# --- absent_import kind (15~19) ------------------------------------------------


def test_15_absent_import_concrete_present_false(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "import sqlite3\n\nx = 1\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, detail = claims.verify({"kind": "absent_import", "ref": "sqlite3"}, ctx)
    assert ok is False
    assert detail["reason"] == "concrete import present"


def test_16_absent_import_from_import_caught_false(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "from sqlite3 import connect\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, _ = claims.verify({"kind": "absent_import", "ref": "sqlite3"}, ctx)
    assert ok is False  # from-import 도 잡힌다


def test_17_absent_import_not_imported_true(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "x = 1\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, detail = claims.verify({"kind": "absent_import", "ref": "sqlite3"}, ctx)
    assert ok is True
    assert detail["imports_scanned"] == 0


def test_18_absent_import_missing_file_and_syntax_error_false(tmp_path):
    root = tmp_path / "code"
    ctx_missing = claims.Context(code_root=root, module="nope.py")
    ok_missing, _ = claims.verify({"kind": "absent_import", "ref": "sqlite3"}, ctx_missing)
    assert ok_missing is False  # 예외 아님

    _write(root / "bad.py", "def (:\n    pass\n")
    ctx_bad = claims.Context(code_root=root, module="bad.py")
    ok_bad, _ = claims.verify({"kind": "absent_import", "ref": "sqlite3"}, ctx_bad)
    assert ok_bad is False  # SyntaxError → False, 예외 아님


def test_19_absent_import_module_none_false(tmp_path):
    root = tmp_path / "code"
    ctx = claims.Context(code_root=root, module=None)
    ok, detail = claims.verify({"kind": "absent_import", "ref": "sqlite3"}, ctx)
    assert ok is False
    assert "not provided" in detail["reason"]


# --- import_of kind (20~21) ----------------------------------------------------


def test_20_import_of_present_true(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "from x import Repository\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, _ = claims.verify({"kind": "import_of", "ref": "Repository"}, ctx)
    assert ok is True


def test_21_import_of_absent_false(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "from x import Other\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, detail = claims.verify({"kind": "import_of", "ref": "Repository"}, ctx)
    assert ok is False
    assert detail["reason"] == "abstract import absent"


# --- symbol_count_max kind (22~25) ---------------------------------------------


def test_22_symbol_count_max_class_within_max_true(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "class One:\n    pass\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, detail = claims.verify(
        {"kind": "symbol_count_max", "ref": {"symbol": "public_class", "max": 1}}, ctx
    )
    assert ok is True
    assert detail["count"] == 1


def test_23_symbol_count_max_def_exceeds_false(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "def a():\n    pass\n\ndef b():\n    pass\n\ndef c():\n    pass\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, detail = claims.verify(
        {"kind": "symbol_count_max", "ref": {"symbol": "public_function", "max": 2}}, ctx
    )
    assert ok is False
    assert detail["count"] == 3


def test_24_symbol_count_max_excludes_private_and_nested_true(tmp_path):
    root = tmp_path / "code"
    _write(
        root / "mod.py",
        "def public_one():\n"
        "    def nested():\n"
        "        pass\n"
        "    return 1\n"
        "\n"
        "def _private():\n"
        "    pass\n",
    )
    ctx = claims.Context(code_root=root, module="mod.py")
    ok, detail = claims.verify(
        {"kind": "symbol_count_max", "ref": {"symbol": "public_function", "max": 1}}, ctx
    )
    assert ok is True
    assert detail["count"] == 1  # _private/중첩 def 미계수


def test_25_symbol_count_max_invalid_ref_shape_false(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "class One:\n    pass\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    # max 없음
    ok1, d1 = claims.verify(
        {"kind": "symbol_count_max", "ref": {"symbol": "public_class"}}, ctx
    )
    assert ok1 is False
    assert d1["reason"] == "invalid ref shape"
    # symbol 오타
    ok2, d2 = claims.verify(
        {"kind": "symbol_count_max", "ref": {"symbol": "public_klass", "max": 1}}, ctx
    )
    assert ok2 is False
    assert d2["reason"] == "invalid ref shape"


# --- 화이트리스트 밖 kind (26) --------------------------------------------------


def test_26_unknown_kind_raises():
    ctx = claims.Context()
    with pytest.raises(claims.UnknownBackingKind):
        claims.verify({"kind": "grep", "ref": "x"}, ctx)


# --- 직렬화·결정성·match_glob·git_diff_files (27~30) ----------------------------


def test_27_details_json_serializable(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "class One:\n    pass\n")
    sub = tmp_path / "sub"
    _write(sub / "s.py", "class AuthService:\n    pass\n")
    samples = [
        claims.verify({"kind": "test", "ref": "t"}, claims.Context(junit={"t": "passed"})),
        claims.verify(
            {"kind": "symbol", "ref": "AuthService"},
            claims.Context(submission=sub, git_files=["s.py"]),
        ),
        claims.verify(
            {"kind": "symbol_count_max", "ref": {"symbol": "public_class", "max": 1}},
            claims.Context(code_root=root, module="mod.py"),
        ),
        claims.verify({"kind": "diff", "ref": "s.py"}, claims.Context(git_files=["s.py"])),
    ]
    for _ok, detail in samples:
        json.dumps(detail)  # 예외 없어야 한다


def test_28_deterministic_same_input(tmp_path):
    root = tmp_path / "code"
    _write(root / "mod.py", "import sqlite3\n")
    ctx = claims.Context(code_root=root, module="mod.py")
    claim = {"kind": "absent_import", "ref": "sqlite3"}
    r1 = claims.verify(claim, ctx)
    r2 = claims.verify(claim, ctx)
    assert r1 == r2


def test_29_match_glob_semantics():
    assert claims.match_glob("src/auth/reset_pw.py", "src/auth/reset*.py") is True
    assert claims.match_glob("src/auth/x/y.py", "src/auth/**") is True  # ** ≡ *
    assert claims.match_glob("src/auth/x/y.py", "src/auth/*") is True   # * 는 / 를 가로지름
    assert claims.match_glob("db/schema/a.py", "src/auth/**") is False
    assert claims.match_glob("api/login.py", "api/login.py") is True


def test_30_git_diff_files_non_git_dir(tmp_path):
    files, error = claims.git_diff_files(tmp_path, "HEAD")
    assert files is None
    assert isinstance(error, str) and error
