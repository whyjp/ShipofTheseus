"""스킬 간 핸드오프 검증 — 분해된 8 스킬의 인터페이스 일관성 테스트.

theseus-orchestrator 가 8 분해 스킬을 체이닝할 때 산출물 frontmatter
체인이 끊기지 않는지, 각 stub 의 cross-link 가 살아 있는지 검증.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS = REPO_ROOT / "skills"
HARNESS = SKILLS / "theseus-harness"
FINGERPRINT = HARNESS / "scoring" / "fingerprint.py"

EXPECTED_STUBS = [
    "theseus-orchestrator",
    "theseus-intent",
    "theseus-plan",
    "theseus-implement",
    "theseus-quality",
    "theseus-sprint",
    "theseus-webview",
    "theseus-handoff",
]


def test_all_8_stub_skills_exist():
    """8 분해 스킬 디렉터리 + SKILL.md 모두 존재."""
    for stub in EXPECTED_STUBS:
        skill_md = SKILLS / stub / "SKILL.md"
        assert skill_md.exists(), f"{stub}/SKILL.md 누락"


def test_stubs_link_to_harness_source():
    """각 stub 이 ../theseus-harness/ 의 콘텐츠를 가리킴 (단일 source of truth)."""
    for stub in EXPECTED_STUBS:
        if stub == "theseus-orchestrator":
            continue   # orchestrator 는 stub 들을 가리킴 (다음 테스트)
        text = (SKILLS / stub / "SKILL.md").read_text(encoding="utf-8")
        assert "../theseus-harness/" in text, f"{stub} 가 ../theseus-harness/ 참조 누락"


def test_orchestrator_links_all_7_stubs():
    """orchestrator 가 7 분해 스킬을 모두 링크."""
    text = (SKILLS / "theseus-orchestrator" / "SKILL.md").read_text(encoding="utf-8")
    for stub in EXPECTED_STUBS:
        if stub == "theseus-orchestrator":
            continue
        assert stub in text, f"orchestrator 가 {stub} 링크 누락"


def test_no_content_duplication_in_stubs():
    """stub 들이 컨벤션/페이즈 룰 본문을 복제하지 않았는지 (fragmentation.md §1)."""
    # 본문 룰의 서명 문구 — 컨벤션에만 있어야 함
    rule_signatures = [
        "두괄식 + 한 번에 하나",                  # interview.md
        "Q-D1: 회귀(페이즈 11)",                  # autonomy.md
        "닥터 스트레인지",                         # checkpoints.md
        "Two Outputs Rule",                        # dacapo.md
    ]
    for stub in EXPECTED_STUBS:
        text = (SKILLS / stub / "SKILL.md").read_text(encoding="utf-8")
        for sig in rule_signatures:
            assert sig not in text, (
                f"{stub} 가 룰 본문 '{sig}' 복제 — fragmentation.md §1 위반"
            )


def test_stubs_have_skill_version_metadata():
    """모든 stub 이 frontmatter 에 skill_version 명시."""
    for stub in EXPECTED_STUBS:
        text = (SKILLS / stub / "SKILL.md").read_text(encoding="utf-8")
        assert re.search(r"^version:\s*\d+\.\d+\.\d+\s*$", text, re.MULTILINE), (
            f"{stub}/SKILL.md frontmatter 의 version 누락 또는 잘못된 형식"
        )


def test_stubs_describe_handoff_inputs_outputs():
    """각 분해 stub 이 *입력* + *출력* 산출물 명시."""
    for stub in EXPECTED_STUBS:
        if stub == "theseus-orchestrator":
            continue   # orchestrator 는 단일 진입점이라 입출력 표 다름
        text = (SKILLS / stub / "SKILL.md").read_text(encoding="utf-8")
        assert "## 입력" in text or "## 입력 산출물" in text, f"{stub} 가 입력 산출물 명시 누락"
        assert "## 출력" in text or "## 출력 산출물" in text, f"{stub} 가 출력 산출물 명시 누락"


def test_fingerprint_chain_for_synthetic_handoff():
    """
    합성 산출물 체인 — 한 stub 의 출력이 다음 stub 의 입력으로 valid 한지.
    실제 .ShipofTheseus/theseus-self/ 의 5 산출물 체인을 사용 (이미 박혀 있음).
    """
    self_eval_root = REPO_ROOT / ".ShipofTheseus" / "theseus-self"
    chain = [
        self_eval_root / "naming" / "00-naming.md",
        self_eval_root / "intent" / "01-intent.md",
        self_eval_root / "intent" / "05-critique.md",
        self_eval_root / "plan" / "06-plan.md",
        self_eval_root / "quality" / "09-quality-gate.md",
    ]
    for art in chain:
        assert art.exists(), f"{art} 누락 (자기 평가 산출물)"
        proc = subprocess.run(
            [sys.executable, str(FINGERPRINT), "verify", "--file", str(art)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"{art} fingerprint verify 실패: {proc.stdout}"


def test_handoff_breaks_when_fingerprint_tampered():
    """tamper 시 다음 스킬 진입 거부 시뮬레이션 — fingerprint verify exit 1."""
    # 임시로 자기 평가 산출물 복사 + tamper
    src = REPO_ROOT / ".ShipofTheseus" / "theseus-self" / "naming" / "00-naming.md"
    text = src.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        # tamper — 본문 한 줄 추가
        tampered = text + "\n\n# TAMPERED BY TEST\n"
        f.write(tampered)
        tampered_path = Path(f.name)
    try:
        proc = subprocess.run(
            [sys.executable, str(FINGERPRINT), "verify", "--file", str(tampered_path)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0, "tamper 된 산출물의 verify 가 통과 — 핸드오프 안전 장치 깨짐"
        out = json.loads(proc.stdout)
        assert out["ok"] is False
    finally:
        tampered_path.unlink(missing_ok=True)


def test_orchestrator_describes_chaining_pseudocode():
    """orchestrator 가 메인 체이닝 의사코드 + 핸드오프 검증 흐름 명시."""
    text = (SKILLS / "theseus-orchestrator" / "SKILL.md").read_text(encoding="utf-8")
    assert "verify_handoff" in text, "orchestrator 의 의사코드에 verify_handoff 누락"
    assert "invoke_skill" in text, "orchestrator 의 의사코드에 invoke_skill 누락"
    assert "체이닝" in text or "chain" in text.lower(), "orchestrator 가 '체이닝' 언급 누락"


def test_two_entrypoints_documented_with_relation():
    """orchestrator 와 harness 두 진입점의 관계 명시."""
    orch = (SKILLS / "theseus-orchestrator" / "SKILL.md").read_text(encoding="utf-8")
    assert "theseus-harness" in orch, "orchestrator 가 theseus-harness 와의 관계 미언급"
    assert "두 진입점" in orch or "공식 메인" in orch, "두 진입점 관계 명시 누락"
