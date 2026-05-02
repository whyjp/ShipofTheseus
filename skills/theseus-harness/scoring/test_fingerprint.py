"""fingerprint.py 테스트.

v0.2.1 회귀 수정 검증 — `TIMING_HEADER_RE` 의 `\\A` 앵커 버그 (Cursor Bugbot
PR#1 지적) 가 *timing-invariant fingerprint* 라는 contracts.md 의 핵심
설계 약속을 깨뜨리고 있었음을 회귀 테스트로 박는다.

같은 본문 + 다른 시각 → 같은 fingerprint 가 되어야 한다.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

# 본 모듈을 직접 import 가능하게 (pytest 없이도 단독 실행).
SCORING_DIR = Path(__file__).parent
sys.path.insert(0, str(SCORING_DIR))

import fingerprint as fp  # noqa: E402

FP = SCORING_DIR / "fingerprint.py"


# ─── canonical_body 단위 테스트 ─────────────────────────────────────────────

def test_canonical_body_strips_timing_block_after_title():
    """템플릿 패턴: '# 제목' + 빈 줄 + '> **프로젝트:** ...' + '> **시작:** ...'
    이 경우 v0.2.0 의 `\\A>` 앵커는 매치 실패 → 본 테스트가 회귀 가드."""
    body_a = (
        "# 의도 — 결제 API\n"
        "\n"
        "> **프로젝트:** `atlas-ledger` · **페이즈:** `01-intent`\n"
        "> **시작:** `2026-05-01T17:44:12+09:00` · **종료:** `2026-05-01T17:46:30+09:00`\n"
        "> **누적 경과:** `2분 18초` · **현재 시각:** `2026-05-01T17:46:30+09:00`\n"
        "\n"
        "## 무엇을\n"
        "결제 API.\n"
    )
    body_b = (
        "# 의도 — 결제 API\n"
        "\n"
        "> **프로젝트:** `atlas-ledger` · **페이즈:** `01-intent`\n"
        "> **시작:** `2026-05-02T09:11:08+09:00` · **종료:** `2026-05-02T09:13:42+09:00`\n"
        "> **누적 경과:** `2분 34초` · **현재 시각:** `2026-05-02T09:13:42+09:00`\n"
        "\n"
        "## 무엇을\n"
        "결제 API.\n"
    )
    assert fp.canonical_body(body_a) == fp.canonical_body(body_b)
    # 그리고 strip 후 본문은 timing 마커를 포함하지 않아야 한다.
    canon = fp.canonical_body(body_a)
    for marker in fp.TIMING_MARKERS:
        assert marker not in canon, f"timing 마커 '{marker}' 가 canonical_body 에 잔존"


def test_canonical_body_preserves_non_timing_blockquote():
    """timing 마커가 없는 일반 인용 블록은 보존되어야 한다."""
    body = (
        "# 인용 예시\n"
        "\n"
        "> 이것은 평범한 인용문입니다.\n"
        "> 두 번째 줄도 있습니다.\n"
        "\n"
        "본문.\n"
    )
    canon = fp.canonical_body(body)
    assert "이것은 평범한 인용문입니다." in canon
    assert "두 번째 줄도 있습니다." in canon


def test_canonical_body_strips_timing_block_at_body_start():
    """contracts.md 가 명세하는 *frontmatter 직후 timing 헤더* 형태 (제목 없음) 도 처리."""
    body_a = (
        "> **시작:** `T1` · **종료:** `T2`\n"
        "> **누적 경과:** `1분` · **현재 시각:** `T2`\n"
        "\n"
        "본문 동일.\n"
    )
    body_b = (
        "> **시작:** `U1` · **종료:** `U2`\n"
        "> **누적 경과:** `9분` · **현재 시각:** `U2`\n"
        "\n"
        "본문 동일.\n"
    )
    assert fp.canonical_body(body_a) == fp.canonical_body(body_b)


def test_canonical_body_strips_sprint_timing_variant():
    """스프린트 보고서 헤더는 '이 스프린트 소요:' 마커를 사용 (timing.md §스프린트)."""
    body_a = (
        "# 스프린트 03 보고서\n"
        "\n"
        "> **프로젝트:** `x` · **스프린트:** `03`\n"
        "> **체크포인트 커밋:** `abc123`\n"
        "> **시작:** `T1` · **종료:** `T2`\n"
        "> **이 스프린트 소요:** `7분 04초` · **누적 경과:** `54분` · **현재 시각:** `T2`\n"
        "\n"
        "## 스위트\n"
    )
    body_b = body_a.replace("T1", "U1").replace("T2", "U2").replace("abc123", "def456").replace("7분 04초", "11분 22초").replace("54분", "1시간 5분")
    # 체크포인트 커밋·시각·소요 모두 다름. canonical_body 는 같아야 함.
    assert fp.canonical_body(body_a) == fp.canonical_body(body_b)


# ─── compute_fingerprint timing-invariance ─────────────────────────────────

def test_fingerprint_is_timing_invariant():
    """같은 본문 + 다른 시각 → 같은 fingerprint. v0.2.0 에서 깨져 있던 약속."""
    fm = {
        "skill_name": "theseus-harness",
        "skill_version": "0.2.1",
        "phase": "01-intent",
        "project_id": "test-proj",
        "project_run": "20260501-174412",
        "prev_fingerprint": None,
    }
    body_t1 = (
        "# 의도 — X\n"
        "\n"
        "> **프로젝트:** `test-proj` · **페이즈:** `01-intent`\n"
        "> **시작:** `2026-05-01T17:44:12+09:00`\n"
        "> **현재 시각:** `2026-05-01T17:46:30+09:00`\n"
        "\n"
        "## 무엇을\nX 만든다.\n"
    )
    body_t2 = body_t1.replace("2026-05-01T17:44:12", "2026-05-02T09:11:08").replace(
        "2026-05-01T17:46:30", "2026-05-02T09:13:42"
    )
    assert fp.compute_fingerprint(fm, body_t1) == fp.compute_fingerprint(fm, body_t2)


def test_fingerprint_changes_when_body_changes():
    """반례 — 본문이 바뀌면 fingerprint 가 바뀌어야 한다 (timing-invariance 가
    *모든* 변경을 무효화하지 않는다는 가드)."""
    fm = {
        "skill_name": "theseus-harness",
        "skill_version": "0.2.1",
        "phase": "01-intent",
        "project_id": "p",
        "project_run": "r",
        "prev_fingerprint": None,
    }
    body_a = "# X\n\n> **시작:** `T`\n\n본문 A.\n"
    body_b = "# X\n\n> **시작:** `T`\n\n본문 B.\n"
    assert fp.compute_fingerprint(fm, body_a) != fp.compute_fingerprint(fm, body_b)


def test_fingerprint_changes_when_prev_changes():
    """체인 무결성 — prev_fingerprint 가 바뀌면 현재도 바뀌어야 한다."""
    fm_base = {
        "skill_name": "theseus-harness",
        "skill_version": "0.2.1",
        "phase": "06-plan",
        "project_id": "p",
        "project_run": "r",
    }
    body = "# 계획\n\n> **시작:** `T`\n\n본문.\n"
    fm_a = {**fm_base, "prev_fingerprint": "sha256:aaa"}
    fm_b = {**fm_base, "prev_fingerprint": "sha256:bbb"}
    assert fp.compute_fingerprint(fm_a, body) != fp.compute_fingerprint(fm_b, body)


# ─── compute / verify CLI 통합 ─────────────────────────────────────────────

def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


def test_cli_compute_then_verify_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        md = _write(
            tmp,
            "01-intent.md",
            "---\n"
            "skill_name: theseus-harness\n"
            "skill_version: 0.2.1\n"
            "phase: 01-intent\n"
            "project_id: test\n"
            "project_run: 20260501\n"
            "fingerprint: \n"
            "prev_fingerprint: null\n"
            "produced_at: 2026-05-01T17:46:30+09:00\n"
            "producer_agent: intent-extractor\n"
            "---\n"
            "# 의도 — X\n"
            "\n"
            "> **시작:** `T1` · **종료:** `T2`\n"
            "\n"
            "## 무엇을\n본문.\n",
        )
        rc = subprocess.run(
            [sys.executable, str(FP), "compute", "--file", str(md), "--prev", "none"],
            capture_output=True,
            text=True,
        )
        assert rc.returncode == 0, rc.stderr
        out = json.loads(rc.stdout)
        assert out["fingerprint"].startswith("sha256:")

        rc_v = subprocess.run(
            [sys.executable, str(FP), "verify", "--file", str(md)],
            capture_output=True,
            text=True,
        )
        assert rc_v.returncode == 0, rc_v.stdout
        assert json.loads(rc_v.stdout)["ok"] is True


def test_cli_compute_is_timing_invariant_end_to_end():
    """v0.2.1 핵심 회귀 테스트 — 같은 본문 + 다른 timing 으로 compute 두 번,
    같은 fingerprint 가 나와야 한다. v0.2.0 에서는 이 테스트가 fail."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        head = (
            "---\n"
            "skill_name: theseus-harness\n"
            "skill_version: 0.2.1\n"
            "phase: 01-intent\n"
            "project_id: test\n"
            "project_run: 20260501\n"
            "fingerprint: \n"
            "prev_fingerprint: null\n"
            "produced_at: PRODUCED_AT_PLACEHOLDER\n"
            "---\n"
        )
        # produced_at 은 frontmatter 키이지만 fingerprint payload 에 포함되지 않음
        # (compute_fingerprint 가 명시 nominate 한 키만 사용). 본문 timing 만 strip 하면
        # 충분.
        body_t1 = (
            "# 의도 — Y\n"
            "\n"
            "> **프로젝트:** `t` · **페이즈:** `01-intent`\n"
            "> **시작:** `2026-05-01T17:44:12+09:00`\n"
            "> **현재 시각:** `2026-05-01T17:46:30+09:00`\n"
            "\n"
            "## 무엇을\n동일 본문.\n"
        )
        body_t2 = body_t1.replace("2026-05-01T17:44:12", "2026-09-09T09:09:09").replace(
            "2026-05-01T17:46:30", "2026-09-09T09:11:11"
        )
        md1 = _write(tmp, "a.md", head.replace("PRODUCED_AT_PLACEHOLDER", "2026-05-01T17:46:30+09:00") + body_t1)
        md2 = _write(tmp, "b.md", head.replace("PRODUCED_AT_PLACEHOLDER", "2026-09-09T09:11:11+09:00") + body_t2)

        for md in (md1, md2):
            rc = subprocess.run(
                [sys.executable, str(FP), "compute", "--file", str(md), "--prev", "none"],
                capture_output=True,
                text=True,
            )
            assert rc.returncode == 0, rc.stderr

        fm1, _ = fp.parse_frontmatter(md1.read_text(encoding="utf-8"))
        fm2, _ = fp.parse_frontmatter(md2.read_text(encoding="utf-8"))
        assert fm1["fingerprint"] == fm2["fingerprint"], (
            f"timing-invariance 위반: {fm1['fingerprint']} vs {fm2['fingerprint']}"
        )


# ─── pytest 없이 단독 실행 ─────────────────────────────────────────────────

def _run_all() -> int:
    """pytest 미설치 환경에서 단독 실행. 실패 시 첫 fail 에서 정지."""
    failed = 0
    fns = [
        test_canonical_body_strips_timing_block_after_title,
        test_canonical_body_preserves_non_timing_blockquote,
        test_canonical_body_strips_timing_block_at_body_start,
        test_canonical_body_strips_sprint_timing_variant,
        test_fingerprint_is_timing_invariant,
        test_fingerprint_changes_when_body_changes,
        test_fingerprint_changes_when_prev_changes,
        test_cli_compute_then_verify_roundtrip,
        test_cli_compute_is_timing_invariant_end_to_end,
    ]
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all())
