#!/usr/bin/env python3
"""
theseus-harness 저장소 자체 lint.

본 하네스가 사용자 프로젝트에 적용하는 게이트(SoC, DIP, 컨벤션 정합)를
*본 저장소* 에 거꾸로 적용해 컨벤션 누락, 교차 링크 깨짐, 버전 불일치,
frontmatter 누락을 잡아낸다 — 부트스트래핑 자체 평가의 객관 측정 도구.

체크 항목 (요약 → 상세는 BOOTSTRAP.md 참조):

  C1  모든 conventions/*.md 가 첫 두 줄에 # 제목 + "한 줄 요약" 섹션을 가진다
  C2  SKILL.md 가 모든 conventions/*.md 를 링크
  C3  SKILL.md 가 모든 phases/*.md 를 링크 (인덱스 표)
  C4  SKILL.md 가 모든 agents/*.md 를 링크
  C5  모든 agents/*.md 가 "권장 모델:" 줄을 가진다
  C6  PHILOSOPHY.md 와 SKILL.md 가 서로 링크
  C7  .claude-plugin/plugin.json 의 version 이 SKILL.md frontmatter 의
      skill_version 과 일치
  C8  scoring/score.py 와 scoring/fingerprint.py 가 import 가능
  C9  INSTALL.md 가 .claude-plugin/plugin.json 또는 .claude/skills 를 언급
  C10 모든 phases/NN-*.md 의 짝 agents/*.md (있으면) 가 페이즈에서 링크
  C11 README (skills/theseus-harness/README.md) 가 모든 conventions 를
      d-1 … 형식으로 노출

사용법:
    self_lint.py [--repo-root <path>]

stdout 으로 JSON, exit 0 = 모든 체크 통과, 1 = 실패가 하나라도.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _files(root: Path, pattern: str) -> list[Path]:
    return sorted(root.glob(pattern))


def check_convention_one_line_summary(skill_root: Path) -> list[str]:
    """C1 — 모든 conventions/*.md 의 첫 두 줄 검사 (INDEX.md 제외 — router 메타). sprint-27 v0.9.32 — frontmatter skip."""
    issues: list[str] = []
    for p in _files(skill_root / "conventions", "*.md"):
        if p.name == "INDEX.md":
            continue   # router 메타 파일, 컨벤션 아님
        text = _read(p)
        lines = text.splitlines()
        # sprint-27: skip leading YAML frontmatter (--- ... ---)
        i = 0
        if lines and lines[0].strip() == "---":
            i = 1
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            i += 1   # past closing ---
            # skip blank lines after frontmatter
            while i < len(lines) and not lines[i].strip():
                i += 1
        head = lines[i:i+8]
        if not head or not head[0].startswith("# "):
            issues.append(f"{p.name}: 첫 줄이 # 제목 아님 (frontmatter skip 후)")
            continue
        if not any("## 한 줄 요약" in line for line in head):
            issues.append(f"{p.name}: '## 한 줄 요약' 섹션 누락")
    return issues


def check_conventions_frontmatter_drift(skill_root: Path) -> list[str]:
    """C-IDX-2 (sprint-27 v0.9.32) — conventions/*.md frontmatter ↔ conventions/INDEX.md drift detection.

    각 conventions/<id>.md 의 YAML frontmatter (id / category / applies-to-phases / applies-to-grades / trigger-when) 가
    conventions/INDEX.md router 표 row 와 일치하는지 검증.
    """
    import re
    issues: list[str] = []
    idx_path = skill_root / "conventions" / "INDEX.md"
    if not idx_path.exists():
        return ["conventions/INDEX.md 누락"]
    idx_body = _read(idx_path)
    router = {}
    for m in re.finditer(
        r'^\|\s*([a-z][a-z0-9-]+)\s*\|\s*([^|]+?)\s*\|\s*(\[[^\]]+\])\s*\|\s*(\[[^\]]+\])\s*\|\s*([^|]+?)\s*\|',
        idx_body, re.M,
    ):
        rid = m.group(1)
        if rid == "id":
            continue
        router[rid] = {
            "category": m.group(2).strip(),
            "applies-to-phases": m.group(3).strip(),
            "applies-to-grades": m.group(4).strip(),
            "trigger-when": m.group(5).strip(),
        }
    for p in _files(skill_root / "conventions", "*.md"):
        if p.name == "INDEX.md":
            continue
        rid = p.stem
        if rid not in router:
            issues.append(f"{p.name}: INDEX.md 에 router row 부재")
            continue
        text = _read(p)
        if not text.startswith("---\n"):
            issues.append(f"{p.name}: frontmatter (router metadata) 부재 — sprint-27 backfill 의무")
            continue
        # extract frontmatter block
        end = text.find("\n---\n", 4)
        if end < 0:
            issues.append(f"{p.name}: frontmatter 종료 마커 부재")
            continue
        fm_block = text[4:end]
        for key in ["id", "category", "applies-to-phases", "applies-to-grades", "trigger-when", "indexed-in"]:
            if f"\n{key}:" not in "\n" + fm_block and not fm_block.startswith(f"{key}:"):
                issues.append(f"{p.name}: frontmatter '{key}' 필드 부재")
        # drift check (id-only — full value drift는 over-strict 가능)
        m_id = re.search(r'^id:\s*(.+?)\s*$', fm_block, re.M)
        if m_id and m_id.group(1) != rid:
            issues.append(f"{p.name}: frontmatter id={m_id.group(1)} ≠ filename {rid}")
    return issues


def check_skill_links_all_conventions(skill_root: Path) -> list[str]:
    """C2 — SKILL.md ∪ conventions/INDEX.md (sprint-20 v0.9.25 lazy-load 분리)."""
    skill = _read(skill_root / "SKILL.md")
    idx_path = skill_root / "conventions" / "INDEX.md"
    idx = _read(idx_path) if idx_path.exists() else ""
    combined = skill + "\n" + idx
    issues: list[str] = []
    for p in _files(skill_root / "conventions", "*.md"):
        if p.name == "INDEX.md":
            continue
        # INDEX 의 router 표는 stem 만 포함 (`| <id> |`), SKILL 은 markdown link `conventions/<file>.md`
        if f"conventions/{p.name}" in combined or f"| {p.stem} |" in idx:
            continue
        issues.append(f"SKILL.md ∪ INDEX 가 conventions/{p.name} 를 링크/등록하지 않음")
    return issues


def check_skill_links_all_phases(skill_root: Path) -> list[str]:
    """C3."""
    skill = _read(skill_root / "SKILL.md")
    issues: list[str] = []
    for p in _files(skill_root / "phases", "*.md"):
        rel = f"phases/{p.name}"
        if rel not in skill:
            issues.append(f"SKILL.md 가 {rel} 를 링크하지 않음")
    return issues


def check_skill_links_all_agents(skill_root: Path) -> list[str]:
    """C4."""
    skill = _read(skill_root / "SKILL.md")
    issues: list[str] = []
    for p in _files(skill_root / "agents", "*.md"):
        rel = f"agents/{p.name}"
        if rel not in skill:
            issues.append(f"SKILL.md 가 {rel} 를 링크하지 않음")
    return issues


def check_agents_recommended_model(skill_root: Path) -> list[str]:
    """C5."""
    issues: list[str] = []
    for p in _files(skill_root / "agents", "*.md"):
        if "권장 모델:" not in _read(p):
            issues.append(f"{p.name}: '권장 모델:' 줄 누락")
    return issues


def check_philosophy_skill_cross_link(repo_root: Path, skill_root: Path) -> list[str]:
    """C6."""
    issues: list[str] = []
    philo = _read(repo_root / "PHILOSOPHY.md")
    skill = _read(skill_root / "SKILL.md")
    if "PHILOSOPHY.md" not in skill:
        issues.append("SKILL.md 가 PHILOSOPHY.md 를 링크하지 않음")
    if "skills/theseus-harness" not in philo and "SKILL.md" not in philo:
        # PHILOSOPHY 는 SKILL 직접 링크 의무가 약하므로 노트 수준만
        pass
    return issues


def check_plugin_version_consistency(repo_root: Path, skill_root: Path) -> list[str]:
    """C7."""
    issues: list[str] = []
    plugin = json.loads(_read(repo_root / ".claude-plugin" / "plugin.json"))
    skill_text = _read(skill_root / "SKILL.md")
    m = re.search(r"^version:\s*(\S+)\s*$", skill_text, re.MULTILINE)
    if not m:
        issues.append("SKILL.md frontmatter 의 version 누락")
        return issues
    skill_version = m.group(1)
    plugin_version = plugin.get("version")
    if skill_version != plugin_version:
        issues.append(
            f"버전 불일치: SKILL.md={skill_version} vs plugin.json={plugin_version}"
        )
    return issues


def check_imports(skill_root: Path) -> list[str]:
    """C8 — score.py / fingerprint.py 가 컴파일 가능한지 빠르게 확인."""
    import py_compile

    issues: list[str] = []
    for name in ("score.py", "fingerprint.py", "self_lint.py"):
        p = skill_root / "scoring" / name
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            issues.append(f"{name}: 컴파일 실패 — {e}")
    return issues


def check_install_doc(repo_root: Path, skill_root: Path) -> list[str]:
    """C9."""
    issues: list[str] = []
    install = _read(repo_root / "INSTALL.md")
    if ".claude-plugin" not in install and ".claude/skills" not in install:
        issues.append("INSTALL.md 가 플러그인 매니페스트 또는 .claude/skills 미언급")
    return issues


def check_phase_agent_links(skill_root: Path) -> list[str]:
    """C10 — 모든 phases/NN-*.md 가 자기 짝 agent (있으면) 를 링크."""
    issues: list[str] = []
    agent_names = {p.stem for p in _files(skill_root / "agents", "*.md")}
    for phase in _files(skill_root / "phases", "*.md"):
        text = _read(phase)
        # 페이즈가 어떤 에이전트라도 언급하면 통과 (메타 페이즈 핸드오프 제외)
        if "agents/" not in text:
            # 일부 메타 페이즈 (handoff 등) 는 에이전트 없을 수 있음
            if "handoff" in phase.name or "naming" in phase.name:
                continue
            if not any(name in text for name in agent_names):
                issues.append(f"{phase.name}: agents/* 링크 또는 에이전트 이름 언급 누락")
    return issues


def check_skill_readme_lists_all_conventions(skill_root: Path) -> list[str]:
    """C11 — skills/theseus-harness/README.md 가 conventions 를 d-N 형식으로 노출."""
    issues: list[str] = []
    readme = _read(skill_root / "README.md")
    for p in _files(skill_root / "conventions", "*.md"):
        rel = f"conventions/{p.name}"
        if rel not in readme:
            issues.append(f"skill README 가 {rel} 를 노출하지 않음")
    return issues


def check_phase06_sequence_diagram(skill_root: Path) -> list[str]:
    """C12 — phases/06-plan.md 가 시퀀스 다이어그램 동봉 의무를 본문에 명시."""
    text = _read(skill_root / "phases" / "06-plan.md")
    if "시퀀스" not in text and "sequence" not in text.lower():
        return ["phases/06-plan.md: '시퀀스 다이어그램' 동봉 의무 본문 누락"]
    return []


def check_phase08_script_clause(skill_root: Path) -> list[str]:
    """C13 — sprint-21 v0.9.26: 08-implement.md router + 08-B-impl-code.md + agents/implementer.md 결합 본문에 sh+bat."""
    parts = [_read(skill_root / "phases" / "08-implement.md")]
    p2 = skill_root / "phases" / "08-B-impl-code.md"
    if p2.exists():
        parts.append(_read(p2))
    impl = skill_root / "agents" / "implementer.md"
    if impl.exists():
        parts.append(_read(impl))
    text = "\n".join(parts)
    issues: list[str] = []
    if ".sh" not in text or ".bat" not in text:
        issues.append("phases/{08-implement.md, 08-B-impl-code.md} ∪ agents/implementer.md: sh + bat 빌드 스크립트 본문 누락")
    return issues


def check_quality_gate_frontmatter(skill_root: Path) -> list[str]:
    """C14 — agents/quality-gate.md 가 frontmatter 누락 자동 fail 룰을 본문에 명시."""
    text = _read(skill_root / "agents" / "quality-gate.md")
    if "frontmatter" not in text or "fail" not in text.lower():
        return ["agents/quality-gate.md: frontmatter 누락 자동 fail 룰 본문 누락"]
    return []


def check_regression_competition(skill_root: Path) -> list[str]:
    """C15 — agents/regression-analyst.md 가 경쟁 컨벤션 사용 가능성 언급."""
    text = _read(skill_root / "agents" / "regression-analyst.md")
    if "competition" not in text and "경쟁" not in text:
        return ["agents/regression-analyst.md: competition.md 또는 '경쟁' 언급 누락"]
    return []


def check_competition_triggers(skill_root: Path) -> list[str]:
    """C16 — conventions/competition.md 가 critic 또는 plan-reviewer 트리거 책임을 명시."""
    text = _read(skill_root / "conventions" / "competition.md")
    if "critic" not in text.lower() and "plan-reviewer" not in text.lower() and "비평가" not in text and "설계자" not in text:
        return ["conventions/competition.md: 트리거 주체 (critic/plan-reviewer) 명시 누락"]
    return []


def check_writer_agents_fingerprint(skill_root: Path) -> list[str]:
    """C17 — 산출물 작성 에이전트가 fingerprint.py 호출 명시."""
    writer_agents = [
        "intent-extractor.md",
        "planner.md",
        "implementer.md",
        "clarifier.md",
        "critic.md",
        "doc-reviewer.md",
        "independent-comprehender.md",
        "plan-reviewer.md",
        "quality-gate.md",
        "tester.md",
        "regression-analyst.md",
        "project-namer.md",
    ]
    issues: list[str] = []
    for name in writer_agents:
        text = _read(skill_root / "agents" / name)
        if "fingerprint" not in text.lower():
            issues.append(f"agents/{name}: fingerprint.py 호출 명시 누락")
    return issues


def check_webview_mermaid(skill_root: Path) -> list[str]:
    """C18 — webview-builder.md 가 Mermaid 자동 렌더를 명시."""
    text = _read(skill_root / "agents" / "webview-builder.md")
    if "mermaid" not in text.lower():
        return ["agents/webview-builder.md: Mermaid 자동 렌더 명시 누락"]
    return []


def check_autonomy_convention_present(skill_root: Path) -> list[str]:
    """C19 — autonomy.md 가 존재하고 SKILL.md / competition.md 에서 참조됨."""
    issues: list[str] = []
    autonomy = skill_root / "conventions" / "autonomy.md"
    if not autonomy.exists():
        return ["conventions/autonomy.md 누락"]
    skill = _read(skill_root / "SKILL.md")
    if "autonomy.md" not in skill:
        issues.append("SKILL.md 가 autonomy.md 를 참조 안 함")
    competition = _read(skill_root / "conventions" / "competition.md")
    if "autonomy" not in competition.lower():
        issues.append("competition.md 가 autonomy 를 언급 안 함 (자율 resolve 룰 연결)")
    return issues


def check_spec_catalog_wired(skill_root: Path) -> list[str]:
    """C21 — spec-catalog.md 가 존재 + intent-extractor / clarifier / phase 09 / template 에 박힘."""
    issues: list[str] = []
    cat = skill_root / "conventions" / "spec-catalog.md"
    if not cat.exists():
        return ["conventions/spec-catalog.md 누락 — NFR 자동 제안 카탈로그 필요"]
    ie = _read(skill_root / "agents" / "intent-extractor.md")
    if "spec-catalog" not in ie and "NFR" not in ie:
        issues.append("agents/intent-extractor.md 가 spec-catalog 또는 NFR 자동 제안 명시 누락")
    cl = _read(skill_root / "agents" / "clarifier.md")
    if "spec-catalog" not in cl and "NFR" not in cl:
        issues.append("agents/clarifier.md 가 NFR 확정 질의 명시 누락")
    p9 = _read(skill_root / "phases" / "09-quality-gates.md")
    if "NFR" not in p9 and "spec-catalog" not in p9:
        issues.append("phases/09-quality-gates.md 가 NFR 게이트(6) 누락")
    tmpl = _read(skill_root / "templates" / "intent.template.md")
    if "성능" not in tmpl and "NFR" not in tmpl:
        issues.append("templates/intent.template.md 가 성능/NFR 섹션 누락")
    return issues


def check_checkpoints_wired(skill_root: Path) -> list[str]:
    """C24 — checkpoints.md + checkpoint.py + autonomy.md Q-D7 + dacapo.md cross-link."""
    issues: list[str] = []
    if not (skill_root / "conventions" / "checkpoints.md").exists():
        return ["conventions/checkpoints.md 누락"]
    if not (skill_root / "scoring" / "checkpoint.py").exists():
        issues.append("scoring/checkpoint.py 누락")
    autonomy = _read(skill_root / "conventions" / "autonomy.md")
    if "Q-D7" not in autonomy:
        issues.append("autonomy.md 가 Q-D7 (체크포인트 회귀 정책) 누락")
    dacapo_path = skill_root / "conventions" / "dacapo.md"
    if dacapo_path.exists() and "checkpoints" not in _read(dacapo_path).lower() and "백트랙" not in _read(dacapo_path):
        issues.append("dacapo.md 가 checkpoints.md 와 cross-link 누락")
    return issues


def check_test_invariants_present(skill_root: Path) -> list[str]:
    """
    C25 — test-invariants.md (Phase V + 불변 조건) + dacapo.md (얇은 인덱스).

    dacapo.md 는 fragmentation.md DRY 룰 따라 *얇은 인덱스* 만 — 본문 의사코드
    재진술 금지 (lessons/checkpoints/test-invariants/phase 10 가 source).
    """
    issues: list[str] = []
    inv = skill_root / "conventions" / "test-invariants.md"
    if not inv.exists():
        return ["conventions/test-invariants.md 누락 — 테스트 목적 보호 룰 정의 필요"]
    text = _read(inv)
    if "Phase V" not in text:
        issues.append("test-invariants.md 가 'Phase V' 측정 유효성 점검 명시 누락")
    if "불변 조건" not in text and "invariants" not in text.lower():
        issues.append("test-invariants.md 가 '불변 조건' 명시 누락")

    dacapo = skill_root / "conventions" / "dacapo.md"
    if not dacapo.exists():
        issues.append("conventions/dacapo.md 누락")
        return issues
    dacapo_text = _read(dacapo)

    # 얇은 인덱스 — 핵심 매핑 표 + 신규 2 개념 (방어 테스트 / 모순 감지) 만
    for must_have in ["AIDE 4 오퍼레이터", "Two Outputs", "방어 테스트", "모순 감지", "고유 신규"]:
        if must_have not in dacapo_text:
            issues.append(f"dacapo.md 의 얇은 인덱스 핵심 항목 누락: '{must_have}'")
    # 본문 의사코드 재진술 금지 — phase 10 의 의사코드 시그니처가 dacapo 본문에 통째로 있으면 fail
    duplicated_pseudocode = (
        "run_test_matrix()" in dacapo_text
        and "find_regression_target" in dacapo_text
        and "regress_to" in dacapo_text
    )
    if duplicated_pseudocode:
        issues.append(
            "dacapo.md 가 본문 의사코드를 재진술 — fragmentation.md DRY 위반. "
            "본문 룰은 lessons/checkpoints/phase 10 이 source, dacapo 는 매핑만"
        )
    return issues


def check_prd_handling_wired(skill_root: Path) -> list[str]:
    """
    C33 — PRD 처리 룰 박힘 + 인터뷰 스킵 금지 허들.

    검증 항목 (PR-13 이후 — prd-handling.md 가 interview.md 로 흡수됨):
      a- interview.md 에 PRD/스펙 입력 처리 절 존재
      b- phase 04 가 PRD 처리 절차 + user_explicit_confirmation 명시
      c- agents/clarifier.md 가 PRD 입력 시 명시 확정 룰 명시
    """
    issues: list[str] = []

    # PR-13: prd-handling.md → interview.md 흡수. interview.md 의 흡수 절 검증.
    interview = skill_root / "conventions" / "interview.md"
    if not interview.exists():
        return ["conventions/interview.md 누락 — 인터뷰 룰 정의 필요"]

    text = _read(interview)
    # 핵심 키워드 — passive default 채택 차단을 위한 명시 검증
    for must_have in [
        "user_explicit_confirmation",
        "prd_evidence_cited",
        "PRD/스펙 입력 처리",
        "인터뷰 스킵",
        "confirmed_at",
    ]:
        if must_have not in text:
            issues.append(f"interview.md 가 '{must_have}' 명시 누락 (C33 PRD 처리 허들)")

    p4 = _read(skill_root / "phases" / "04-clarify.md")
    if "user_explicit_confirmation" not in p4:
        issues.append(
            "phases/04-clarify.md 가 PRD 처리 절차 또는 user_explicit_confirmation 의무 누락"
        )

    cl = _read(skill_root / "agents" / "clarifier.md")
    if "user_explicit_confirmation" not in cl:
        issues.append("agents/clarifier.md 가 PRD 입력 시 명시 확정 룰 누락")

    return issues


def check_convention_consolidation_prd(repo_root: Path, skill_root: Path) -> list[str]:
    """C42 — interview.md 가 PRD/스펙 입력 처리 절 흡수 + prd-handling.md 제거 + dead link 부재."""
    issues: list[str] = []

    # 1. interview.md has the absorbed section
    interview_path = skill_root / "conventions" / "interview.md"
    interview = interview_path.read_text(encoding="utf-8")
    if "PRD/스펙 입력 처리" not in interview:
        issues.append("interview.md: PRD/스펙 입력 처리 흡수 절 누락 (PR-13)")
    if "prd-handling.md 흡수" not in interview:
        issues.append("interview.md: prd-handling 흡수 명시 누락 (PR-13)")

    # 2. prd-handling.md is gone
    if (skill_root / "conventions" / "prd-handling.md").exists():
        issues.append("prd-handling.md 가 여전히 존재 — interview.md 로 흡수되어야 (PR-13)")

    # 3. No dead links to prd-handling.md
    import re
    targets = (
        list((skill_root / "phases").glob("*.md"))
        + list((skill_root / "agents").glob("*.md"))
        + [skill_root / "SKILL.md", skill_root / "README.md"]
    )
    for t in targets:
        if not t.exists():
            continue
        text = t.read_text(encoding="utf-8")
        if "prd-handling.md" in text:
            issues.append(f"{t.name}: dead link 'prd-handling.md' 잔존 (PR-13)")

    return issues


def check_rewrite_trigger_multidimensional(repo_root: Path, skill_root: Path) -> list[str]:
    """
    C34 — *깨고 다시 빚기* 트리거가 SOLID/DIP 단일 차원에 묶여 있지 않고
    모든 깊은 품질 위반 차원으로 일반화되어 있는지 검증.

    배경: 사용자 지시 — "깨고 다시 진행하는 건 깊은 SOLID/DIP 위반 뿐 아니라
    코드 오류·기획-구현 갭·성능 이슈 모든 면에서 요구된다." 본 룰을 *문서* 와
    *실제 스킬 흐름* 양쪽에서 검증해, SKILL.md / PHILOSOPHY.md / lessons.md /
    checkpoints.md / regression-analyst.md / phase 11 모두 다차원 트리거 표현
    누락 없이 일관 체이닝되었는지 자동 점검.

    검증 항목:
      a- 각 문서에 6 차원 (DIP·코드 오류·스펙 누락·NFR·의도 표류·정체) 이 모두 등장.
      b- checkpoints.md `find_regression_target` 가 11 분류 (intent_mismatch /
         plan_misfit / module_impl_violation / test_regression / resource_ceiling /
         stagnation / dip_violation / scope_creep / code_error_cascade /
         spec_omission / nfr_violation) 를 포함.
      c- regression-analyst.md 가 "깊은 품질 위반 점검 (6 차원)" 또는 동등 섹션 보유.
      d- phase 11 권고 2-(`re-architect`) 가 SOLID 단일 한정이 아닌 *깊은 품질 위반*
         으로 표현됨.
    """
    issues: list[str] = []

    # 6 차원 키워드 — 의미가 같은 동의어를 OR 묶음으로
    dim_keywords = [
        ("DIP/SOLID",       ["DIP", "SOLID"]),
        ("코드 오류 누적",   ["코드 오류", "code_error", "버그 누적"]),
        ("기획-구현 갭",     ["기획-구현 갭", "스펙 누락", "spec_omission"]),
        ("성능/NFR 미달",    ["NFR 미달", "성능", "nfr_violation", "천정"]),
        ("의도 표류",        ["의도 표류", "scope_creep"]),
        ("정체/회귀 누적",   ["정체", "stagnation", "회귀 누적"]),
    ]

    targets = [
        ("PHILOSOPHY.md",                      repo_root / "PHILOSOPHY.md"),
        ("SKILL.md",                           skill_root / "SKILL.md"),
        ("conventions/lessons.md",             skill_root / "conventions" / "lessons.md"),
        ("conventions/checkpoints.md",         skill_root / "conventions" / "checkpoints.md"),
        ("agents/regression-analyst.md",       skill_root / "agents" / "regression-analyst.md"),
        ("phases/11-regression-bisect.md",     skill_root / "phases" / "11-regression-bisect.md"),
    ]

    for label, path in targets:
        if not path.exists():
            issues.append(f"{label} 누락 — 깨고 다시 빚기 트리거 다차원 검증 불가")
            continue
        text = _read(path)
        for dim_label, syns in dim_keywords:
            if not any(syn in text for syn in syns):
                issues.append(
                    f"{label} 가 깨고 다시 빚기 트리거 차원 '{dim_label}' 표현 누락 — "
                    f"동의어 후보: {syns}"
                )

    # checkpoints.md 의 11 분류 검증
    cp_text = _read(skill_root / "conventions" / "checkpoints.md")
    expected_kinds = [
        "intent_mismatch",
        "plan_misfit",
        "module_impl_violation",
        "test_regression",
        "resource_ceiling",
        "stagnation",
        "dip_violation",
        "scope_creep",
        "code_error_cascade",
        "spec_omission",
        "nfr_violation",
    ]
    for kind in expected_kinds:
        if kind not in cp_text:
            issues.append(
                f"conventions/checkpoints.md 의 find_regression_target 에 failure.kind '{kind}' 분류 누락"
            )

    # regression-analyst.md 의 "깊은 품질 위반" 6 차원 점검 섹션
    ra_text = _read(skill_root / "agents" / "regression-analyst.md")
    if "깊은 품질 위반 점검" not in ra_text:
        issues.append(
            "agents/regression-analyst.md 가 '깊은 품질 위반 점검' 6 차원 섹션 누락 — "
            "DIP 단일 점검만 있으면 다른 깊은 위반이 부분 수정으로 흘려보내짐"
        )

    # phase 11 권고 2- 가 "SOLID 위반" 단일 한정이 아닌 "깊은 품질 위반" 으로 일반화
    p11_text = _read(skill_root / "phases" / "11-regression-bisect.md")
    if "깊은 품질 위반" not in p11_text and "다차원" not in p11_text:
        issues.append(
            "phases/11-regression-bisect.md 의 re-architect 권고가 SOLID 단일 한정 — "
            "깊은 품질 위반 (DIP·코드 오류·스펙 누락·NFR·의도 표류·정체) 다차원으로 일반화되어야 함"
        )

    return issues


def check_qd8_verification_commands_wired(skill_root: Path) -> list[str]:
    """
    C36 — Q-D8 (Verification Commands, oh-my-ralph 차용, v0.3.0) wiring 일관성.

    배경: 본 하네스의 6 차원 rubric 가중평균 ≥ 0.999 는 *내부 정합* 측정 —
    *외부에서 보아 완료* 인지는 사용자 정의 검증 명령으로만 판정. oh-my-ralph
    의 *Verification Commands* 룰 차용. 페이즈 04 끝의 Q-D8 답이 누락되거나
    intent/04-verification.md 의 Verification Commands 블록이 비면 페이즈 05
    진입 거부 — 검증 없는 자율 진행은 본 하네스가 거부.

    검증 항목:
      a- conventions/autonomy.md 에 ### Q-D8 섹션 + entry_blocked + manual_only
         + oh-my-ralph 키워드.
      b- phases/04-clarify.md 의 산출물 목록에 intent/04-verification.md +
         Q-D8 본문 명시.
      c- agents/clarifier.md 의 동작 단계에 Q-D8 처리 룰 (entry_blocked 박음
         로직).
      d- phases/05-critique.md 의 입력에 04-verification.md + 진입 가드 의사
         코드 (entry_blocked 검사).
      e- templates/verification.template.md 존재 + frontmatter 의 commands_count
         + manual_only + entry_blocked 키 포함.
    """
    issues: list[str] = []

    autonomy = _read(skill_root / "conventions" / "autonomy.md")
    for must_have in ["### Q-D8", "entry_blocked", "manual_only", "oh-my-ralph"]:
        if must_have not in autonomy:
            issues.append(f"conventions/autonomy.md 가 Q-D8 wiring 키워드 '{must_have}' 누락")

    phase04 = _read(skill_root / "phases" / "04-clarify.md")
    if "04-verification.md" not in phase04:
        issues.append("phases/04-clarify.md 산출물 목록에 04-verification.md 누락")
    if "Q-D8" not in phase04:
        issues.append("phases/04-clarify.md 본문에 Q-D8 명시 누락")
    if "8 답" not in phase04 and "Q-D1 ~ Q-D8" not in phase04:
        issues.append("phases/04-clarify.md 가 사전 위임 8 답 (Q-D1~Q-D8) 명시 누락")

    clarifier = _read(skill_root / "agents" / "clarifier.md")
    if "Q-D8" not in clarifier:
        issues.append("agents/clarifier.md 동작에 Q-D8 처리 룰 누락")
    if "entry_blocked" not in clarifier:
        issues.append("agents/clarifier.md 가 entry_blocked frontmatter 박음 룰 누락")

    phase05 = _read(skill_root / "phases" / "05-critique.md")
    if "04-verification.md" not in phase05:
        issues.append("phases/05-critique.md 입력 목록에 04-verification.md 누락")
    if "entry_blocked" not in phase05:
        issues.append(
            "phases/05-critique.md 진입 가드에 entry_blocked 검사 누락 — "
            "Q-D8 검증 부재 시 페이즈 05 진입을 막는 의사코드 필요"
        )
    if "SkillEntryError" not in phase05 and "진입 거부" not in phase05:
        issues.append("phases/05-critique.md 가 진입 거부 메커니즘 명시 누락")

    template = skill_root / "templates" / "verification.template.md"
    if not template.exists():
        issues.append("templates/verification.template.md 누락 — 사용자/하네스가 채울 reference 부재")
    else:
        tmpl_text = _read(template)
        for key in ["commands_count", "manual_only", "entry_blocked"]:
            if f"{key}:" not in tmpl_text:
                issues.append(f"templates/verification.template.md frontmatter 에 '{key}' 키 누락")
        if "Verification Commands" not in tmpl_text:
            issues.append("templates/verification.template.md 본문에 'Verification Commands' 섹션 누락")

    return issues


def check_subprocess_encoding_explicit(skill_root: Path) -> list[str]:
    """
    C35 — Windows 인코딩 비호환 가드 (회귀 아닌 *원래 잠재* 버그 재유입 방지).

    배경 (v0.2.2 외부 리뷰): `subprocess.run(text=True)` 와
    `tempfile.NamedTemporaryFile(mode="w")` 의 *기본* 인코딩이 OS 로케일
    의존 (Windows 한국어 = cp949) 이라, 자식 Python 이 한국어 JSON 을
    출력하면 부모가 디코딩 못 한 바이트에서 잘려 JSON 파싱 실패. 결과적으로
    `test_self_score_meets_99999` 가 0.8 까지 떨어져 정직 박스의 가장 큰
    약속(`self_score=1.0`) 이 *OS 의존* 이었음 — *작동하다 깨진 회귀가 아니라
    v0.2.0 부터 Windows 에서 한 번도 작동한 적 없는 잠재 버그*.

    본 체크는 *모든 새 테스트/도구* 에 같은 비호환이 재유입되는 것을 패턴
    매칭으로 막는다 — `scoring/` 의 `.py` 파일에서:
      a- `tempfile.NamedTemporaryFile(... mode="w" ...)` 호출에 `encoding=`
         미명시 → fail.
      b- `subprocess.run(... text=True ...)` 호출에 `encoding=` 미명시 → fail.
         단, 부모가 `PYTHONIOENCODING` 을 자식에 전달하는 경우는 conftest.py 가
         처리 — 본 체크는 *방어 심층화* 로 명시도 강제.
      c- `scoring/conftest.py` 존재 (pytest 세션 부트 자체).

    검출 휴리스틱: 호출 멀티라인 가능성 때문에 함수 호출 단위로 묶어 검사.
    `encoding=` 키워드가 같은 호출의 닫는 괄호 *전* 에 있는지 본다.
    """
    issues: list[str] = []

    conftest = skill_root / "scoring" / "conftest.py"
    if not conftest.exists():
        issues.append("scoring/conftest.py 누락 — Windows 자식 Python stdout 인코딩 가드 부재")
    else:
        text = conftest.read_text(encoding="utf-8")
        if "PYTHONIOENCODING" not in text:
            issues.append("scoring/conftest.py 가 PYTHONIOENCODING 박지 않음")

    # 호출 단위 패턴 — re.DOTALL 로 멀티라인 호출 감쌈.
    tempfile_pat = re.compile(
        r"tempfile\.NamedTemporaryFile\s*\((?P<args>[^()]*?)\)",
        re.DOTALL,
    )
    subprocess_pat = re.compile(
        r"subprocess\.run\s*\((?P<args>[^()]*(?:\([^()]*\)[^()]*)*?)\)",
        re.DOTALL,
    )

    for py in sorted((skill_root / "scoring").glob("*.py")):
        # 본 체크 자체는 자기 자신 정규식을 검사 대상에 포함시키면 안 됨 — 메타 회피.
        if py.name == "self_lint.py":
            continue
        body = py.read_text(encoding="utf-8")
        for m in tempfile_pat.finditer(body):
            call = m.group(0)
            if 'mode="w"' not in call and "mode='w'" not in call:
                continue   # 읽기 또는 바이너리 — 인코딩 무관
            if "encoding=" not in call:
                line_no = body.count("\n", 0, m.start()) + 1
                issues.append(
                    f"scoring/{py.name}:{line_no} tempfile.NamedTemporaryFile(mode='w') 에 encoding= 누락 — "
                    f"Windows cp949 비호환 위험"
                )
        for m in subprocess_pat.finditer(body):
            call = m.group(0)
            if "text=True" not in call:
                continue   # bytes 모드 — 명시 디코딩 안 함, OK
            if "encoding=" not in call:
                line_no = body.count("\n", 0, m.start()) + 1
                issues.append(
                    f"scoring/{py.name}:{line_no} subprocess.run(text=True) 에 encoding= 누락 — "
                    f"부모 디코딩이 OS 로케일에 떨어짐"
                )

    return issues


def check_no_rule_duplication(skill_root: Path) -> list[str]:
    """
    C32 — 룰 본문 중복 검출 휴리스틱.

    fragmentation.md 안티 패턴 c- "한 룰을 두 파일에서 다르게 정의" 방지.
    *룰 본문* 의 시그니처 문구가 *2 컨벤션 이상* 에 동시 등장하면 의심.
    예외: 매핑/cross-link 컨벤션 (fragmentation/dacapo/indexing) 은
    *위치 가리킴* 이 본업이라 시그니처 등장이 정상 — allow_referrers 로 제외.
    """
    # (signature, primary_owner) — primary_owner 외 다른 컨벤션에 등장하면 fail
    signatures = [
        ("두괄식 + 한 번에 하나",                                   "interview.md"),
        ("Q-D1: 회귀(페이즈 11)",                                   "autonomy.md"),
        ("닥터 스트레인지의 14,000,605",                              "checkpoints.md"),
        ("종합 정체 (window=3, eps=0.005)",                          "lessons.md"),
        ("천정 도달 (avg ≥ 추정 천정의 90%)",                        "resources.md"),
        ("phase 05~13 본문에 사용자 인터럽트 호출 *없음*",             "autonomy.md"),
        # fragmentation.md / dacapo.md / indexing.md / SKILL.md / README 는 매핑이 본업 — 제외
    ]
    allow_referrers = {
        "fragmentation.md", "dacapo.md", "indexing.md",
        "SKILL.md", "README.md", "BOOTSTRAP.md",
    }
    issues: list[str] = []
    convention_files = list((skill_root / "conventions").glob("*.md"))
    for sig, owner in signatures:
        for cf in convention_files:
            if cf.name == owner or cf.name in allow_referrers:
                continue
            text = _read(cf)
            if sig in text:
                issues.append(
                    f"중복 룰 본문 의심: '{sig}' 가 {owner} 의 source 인데 "
                    f"{cf.name} 에도 등장 — fragmentation.md DRY 위반"
                )
    return issues


def check_resume_wired(skill_root: Path) -> list[str]:
    """C31 — resume.md + resume.py + state.json 표준 + Progress 탭 + SKILL/README 노출."""
    issues: list[str] = []
    rm = skill_root / "conventions" / "resume.md"
    if not rm.exists():
        return ["conventions/resume.md 누락 — 리줌 룰 정의 필요"]
    text = _read(rm)
    # 핵심 키워드 검증
    for k in ["state.json", "interrupt_reason", "resume_hint", "fingerprint", "Progress"]:
        if k not in text:
            issues.append(f"resume.md 가 '{k}' 명시 누락")
    # 도구
    if not (skill_root / "scoring" / "resume.py").exists():
        issues.append("scoring/resume.py 누락")
    # webview Progress 탭
    progress_tab = skill_root / "templates" / "webview" / "src" / "tabs" / "Progress.tsx"
    if not progress_tab.exists():
        issues.append("templates/webview/src/tabs/Progress.tsx 누락 — FE 라이브 진행 추적 부재")
    # server.ts /api/state
    server = _read(skill_root / "templates" / "webview" / "server.ts")
    if "/api/state" not in server or "/api/resume" not in server:
        issues.append("server.ts 가 /api/state 또는 /api/resume 엔드포인트 누락")
    # SKILL/README 노출
    skill = _read(skill_root / "SKILL.md")
    if "resume.md" not in skill:
        issues.append("SKILL.md 가 resume.md 노출 누락")
    readme = _read(skill_root / "README.md")
    if "resume.md" not in readme:
        issues.append("skill README 가 resume.md 노출 누락")
    return issues


def check_indexing_wired(skill_root: Path) -> list[str]:
    """C30 — indexing.md + index_builder.py + frontmatter 비직렬성 메타 + INDEX.md 자동 갱신 룰."""
    issues: list[str] = []
    idx = skill_root / "conventions" / "indexing.md"
    if not idx.exists():
        return ["conventions/indexing.md 누락 — 산출물 인덱싱 룰 정의 필요"]
    text = _read(idx)
    # 비직렬성 메타 5종 명시
    for field in ["universe", "parent_branch", "parent_module", "depth", "branch_kind"]:
        if field not in text:
            issues.append(f"indexing.md 가 비직렬성 메타 '{field}' 명시 누락")
    # 도구 존재
    if not (skill_root / "scoring" / "index_builder.py").exists():
        issues.append("scoring/index_builder.py 누락")
    # contracts.md 도 비직렬성 메타 인지
    contracts = _read(skill_root / "conventions" / "contracts.md")
    if "indexing.md" not in contracts and "INDEX.md" not in contracts and "비직렬성" not in contracts:
        issues.append("contracts.md 가 indexing.md (비직렬성 메타 확장) 참조 누락")
    # SKILL/README 노출
    skill = _read(skill_root / "SKILL.md")
    if "indexing.md" not in skill:
        issues.append("SKILL.md 가 indexing.md 노출 누락")
    readme = _read(skill_root / "README.md")
    if "indexing.md" not in readme:
        issues.append("skill README 가 indexing.md 노출 누락")
    return issues


def check_sub_agents_wired(skill_root: Path) -> list[str]:
    """C29 — sub-agents.md + sub_agent_dispatch.py + 단독 호출 input 매트릭스 + SKILL/README 노출."""
    issues: list[str] = []
    sa = skill_root / "conventions" / "sub-agents.md"
    if not sa.exists():
        return ["conventions/sub-agents.md 누락 — 서브에이전트 재귀 분해 정의 필요"]
    text = _read(sa)
    # v0.8.1 sprint-03-b: 7 phase 분해 stub 제거됨. orchestrator + harness 만.
    # 본 매트릭스의 검증 대상은 conventions/sub-agents.md 안의 *서브에이전트 분해*
    # (planner/implementer/etc.) 이지 외부 분해 스킬이 아님.
    # AIDE 4 오퍼레이터 매핑 검증
    for op in ["Draft", "Improve", "Debug", "Memory"]:
        if op not in text:
            issues.append(f"sub-agents.md 가 AIDE 오퍼레이터 {op} 매핑 누락")
    # 깊이 한도
    if "깊이 2" not in text and "DEPTH_LIMIT" not in text:
        issues.append("sub-agents.md 가 재귀 깊이 한도 명시 누락")
    # 도구 존재
    if not (skill_root / "scoring" / "sub_agent_dispatch.py").exists():
        issues.append("scoring/sub_agent_dispatch.py 누락")
    # SKILL/README 노출
    skill = _read(skill_root / "SKILL.md")
    if "sub-agents.md" not in skill:
        issues.append("SKILL.md 가 sub-agents.md 노출 누락")
    readme = _read(skill_root / "README.md")
    if "sub-agents.md" not in readme:
        issues.append("skill README 가 sub-agents.md 노출 누락")
    return issues


def check_decomposition_stubs(repo_root: Path, skill_root: Path) -> list[str]:
    """C28 — orchestrator + harness 두 스킬 존재 + harness 가 source of truth (v0.8.1 sprint-03-b).

    이전 v0.8.x 까지: 8 분해 stub (orchestrator + 7 phase stub) 검증.
    sprint-03-b 에서 7 phase stub 제거 — pure delegation 만 했으므로 cost > benefit.
    이제는 단순히 두 스킬 존재 + cross-link 만 검증.
    """
    skills_root = repo_root / "skills"
    issues: list[str] = []
    expected = ["theseus-orchestrator", "theseus-harness"]
    for s in expected:
        if not (skills_root / s / "SKILL.md").exists():
            issues.append(f"{s}/SKILL.md 누락")
    orch = skills_root / "theseus-orchestrator" / "SKILL.md"
    if orch.exists():
        orch_text = orch.read_text(encoding="utf-8")
        if "theseus-harness" not in orch_text:
            issues.append("theseus-orchestrator 가 theseus-harness 참조 누락 (single source of truth)")
    return issues


def check_grades_wired(skill_root: Path) -> list[str]:
    """C27 — grades.md + grade_assess.py + SKILL.md 호출 표 + phase 04 Q-G1."""
    issues: list[str] = []
    if not (skill_root / "conventions" / "grades.md").exists():
        return ["conventions/grades.md 누락 — 그레이드 시스템 정의 필요"]
    if not (skill_root / "scoring" / "grade_assess.py").exists():
        issues.append("scoring/grade_assess.py 누락 — 자동 그레이드 추정 도구 필요")
    skill = _read(skill_root / "SKILL.md")
    if "Grade 1" not in skill or "Grade 5" not in skill or "grades.md" not in skill:
        issues.append("SKILL.md 가 호출 그레이드 표 (G1~G5) 또는 grades.md 링크 누락")
    p4 = _read(skill_root / "phases" / "04-clarify.md")
    if "Q-G1" not in p4 or "grade" not in p4.lower():
        issues.append("phases/04-clarify.md 가 Q-G1 그레이드 확정 첫 질의 누락")
    return issues


def check_grade_scope_no_gate(skill_root: Path) -> list[str]:
    """C-GS — grade 가 entry/blocked/reject/거부/종료/진입 거부 와 결합되면 fail.
    그레이드는 내부 모듈레이션만, 진행/거부 게이트로 쓰면 안 됨 (v0.5.0 sprint-02-a)."""
    import re
    issues: list[str] = []
    bad_combos = [
        (r"호출\s*거부", "호출 거부"),
        (r"reject_harness_call", "reject_harness_call 잔존"),
        (r"G1\s*[^\n]{0,20}자동\s*거부", "G1 자동 거부"),
        (r"Grade\s*1[^\n]{0,40}(거부|종료|차단)", "Grade 1 + 거부/종료/차단"),
        (r"grade[^\n]{0,40}(진입\s*거부|진입\s*차단)", "grade + 진입 거부/차단"),
    ]
    targets = [
        skill_root / "conventions" / "grades.md",
        skill_root / "phases" / "04-clarify.md",
        skill_root / "scoring" / "grade_assess.py",
        skill_root / "SKILL.md",
        skill_root / "README.md",
        skill_root / "conventions" / "sub-agents.md",
    ]
    # v0.6.x sprint-02-c — 분해 스킬 stub 도 검사 (sprint-02-a 의 sweep 미완 보강).
    # theseus-harness/ 의 부모 = skills/, 형제 분해 스킬 8 개의 SKILL.md 도 동일 룰 적용.
    sibling_root = skill_root.parent
    if sibling_root.name == "skills":
        for sibling in sorted(sibling_root.iterdir()):
            if sibling.is_dir() and sibling.name.startswith("theseus-") and sibling.name != skill_root.name:
                stub = sibling / "SKILL.md"
                if stub.exists():
                    targets.append(stub)
    for tgt in targets:
        if not tgt.exists():
            continue
        # self_lint.py 자체는 패턴 정의가 들어있으므로 false-positive 회피 — 본 함수 호출 대상에 없음
        text = _read(tgt)
        for pattern, label in bad_combos:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                # sibling skill (theseus-orchestrator/...) 도 검사 대상이라 skill_root
                # 의 부모 (skills/) 기준으로 relative path 계산 — relative_to 크래시 회피.
                try:
                    rel = tgt.relative_to(skill_root)
                except ValueError:
                    rel = tgt.relative_to(skill_root.parent)
                issues.append(f"{rel}: {label} 잔존 (\"{m.group(0)[:50]}\")")
    return issues


def check_fragmentation_policy(skill_root: Path) -> list[str]:
    """C26 — fragmentation.md 가 존재 + SKILL.md 가 인덱스 형태 (룰 본문 비대화 방지)."""
    issues: list[str] = []
    frag = skill_root / "conventions" / "fragmentation.md"
    if not frag.exists():
        return ["conventions/fragmentation.md 누락 — 파편화 우선 룰 정의 필요"]
    skill = _read(skill_root / "SKILL.md")
    # SKILL.md 가 일정 길이 초과면 룰 본문 누적 의심.
    # 임계: 26500 자 (v0.9.24 sprint-19 — 70 컨벤션 + ce~cj 6 신규 sprint-19 절 추가. 표 인덱스 행은 룰 본문 X 라 fragmentation 위반 아님 — 다음 sprint 에 별도 CHANGELOG.md 분리 검토.
    # 이전 임계 12000 은 21 컨벤션 시점, plan-tree + runtime-prereq + HARD-RULE 추가 후 13000~ 정상.
    if len(skill) > 26500:
        issues.append(
            f"SKILL.md 길이 {len(skill)} 자 — 임계 26500 초과. 룰 본문이 컨벤션으로 분해되지 않은 의심 (fragmentation.md §1 위반)"
        )
    if "fragmentation.md" not in skill:
        issues.append("SKILL.md 가 fragmentation.md 를 노출하지 않음")
    return issues


def check_no_user_interrupt_post_phase04(skill_root: Path) -> list[str]:
    """
    C23 — 페이즈 05~13 본문에 사용자 인터럽트 호출 패턴이 *있으면* fail.

    autonomy.md 의 핵심 룰: 페이즈 04 가 유일한 인터럽트 지점. 페이즈 05~13 은
    모든 ack 가 사전 위임 답 자동 매핑이어야 함.

    예외: "인터럽트 없음", "사전 위임", "Q-D[0-9]" 같은 *부재 명시* 단어가
    같은 줄에 있으면 통과 (룰 명시지 호출 아님).
    """
    issues: list[str] = []
    forbidden_patterns = ["AskUserQuestion", "사용자 ack", "ask_user", "ack_per_autonomy"]
    allow_markers = ["인터럽트 없음", "사전 위임", "Q-D", "ack 호출 절대 없음", "자동 매핑", "자동 적용"]

    for phase_file in _files(skill_root / "phases", "*.md"):
        # 04 는 인터럽트 정상
        if phase_file.name.startswith("04-"):
            continue
        # 00–03 은 명령형 인터럽트 가능 (의도 추출/리뷰 단계)
        if phase_file.name[:2] in {"00", "01", "02", "03"}:
            continue
        text = _read(phase_file)
        for line in text.splitlines():
            for pat in forbidden_patterns:
                if pat in line:
                    if any(m in line for m in allow_markers):
                        continue   # 룰 명시 (사전 위임/없음 등) — 통과
                    issues.append(
                        f"{phase_file.name}: 인터럽트 패턴 '{pat}' 발견 — "
                        f"페이즈 05~13 은 사전 위임 자동 매핑이어야 함 (라인: {line.strip()[:80]})"
                    )
    return issues


def check_resources_ceiling_wired(skill_root: Path) -> list[str]:
    """C22 — resources.md + resource_ceiling.py 가 phase 04, phase 10, spec-catalog 에 박힘."""
    issues: list[str] = []
    res = skill_root / "conventions" / "resources.md"
    if not res.exists():
        return ["conventions/resources.md 누락 — 리소스 기반 NFR 추정치 필요"]
    ceiling = skill_root / "scoring" / "resource_ceiling.py"
    if not ceiling.exists():
        issues.append("scoring/resource_ceiling.py 누락 — 천정 감지 도구 필요")
    p4 = _read(skill_root / "phases" / "04-clarify.md")
    if "resource-profile" not in p4 and "resources.md" not in p4:
        issues.append("phases/04-clarify.md 가 resource-profile 산출물 또는 resources.md 참조 누락")
    p10 = _read(skill_root / "phases" / "10-test-loop.md")
    if "resource_ceiling" not in p10 and "천정" not in p10:
        issues.append("phases/10-test-loop.md 가 resource_ceiling 또는 천정 자동 조정 누락")
    sc = _read(skill_root / "conventions" / "spec-catalog.md")
    if "resources.md" not in sc and "리소스" not in sc:
        issues.append("conventions/spec-catalog.md 가 resources.md 또는 리소스 기반 임계 언급 누락")
    return issues


def check_lessons_stagnation_wired(skill_root: Path) -> list[str]:
    """C20 — lessons.md 와 stagnation.py 가 phase 10, implementer, planner 에 박힘."""
    issues: list[str] = []
    lessons = skill_root / "conventions" / "lessons.md"
    if not lessons.exists():
        return ["conventions/lessons.md 누락 — 정체 극복 룰 정의 필요"]
    stag = skill_root / "scoring" / "stagnation.py"
    if not stag.exists():
        issues.append("scoring/stagnation.py 누락 — 정체 감지 도구 필요")
    phase10 = _read(skill_root / "phases" / "10-test-loop.md")
    if "lesson_pack" not in phase10 or "stagnation" not in phase10.lower():
        issues.append("phases/10-test-loop.md 가 lesson_pack 또는 stagnation 을 본문에 박지 않음")
    impl = _read(skill_root / "agents" / "implementer.md")
    if "lesson_pack" not in impl or "preserve" not in impl.lower():
        issues.append("agents/implementer.md 가 lesson_pack 입력 + preserve 룰 누락")
    plan = _read(skill_root / "agents" / "planner.md")
    if "lesson_pack" not in plan:
        issues.append("agents/planner.md 가 lesson_pack 입력 가능성 누락")
    return issues


def check_install_fresh_user_section(repo_root: Path, skill_root: Path) -> list[str]:
    """C38 — INSTALL.md 가 fresh-user 환경 prep 절 + self-check.{sh,bat} 가 --check-stack-only 모드 보유."""
    issues: list[str] = []
    install = (repo_root / "INSTALL.md").read_text(encoding="utf-8")
    if "Fresh User 환경 점검" not in install:
        issues.append("INSTALL.md: Fresh User 환경 점검 절 누락 (PR-2)")
    for script in ("scripts/self-check.sh", "scripts/self-check.bat"):
        text = (repo_root / script).read_text(encoding="utf-8")
        if "--check-stack-only" not in text:
            issues.append(f"{script}: --check-stack-only 모드 누락 (PR-2)")
    return issues


def check_resources_supplementary_ceiling(repo_root: Path, skill_root: Path) -> list[str]:
    """C39 — resources.md 의 opt-in 보조 천정 절 + 컨셉 충돌 + 기본 비활성 + Q-D3 sub-option 흡수 일관."""
    issues: list[str] = []
    resources = (skill_root / "conventions" / "resources.md").read_text(encoding="utf-8")
    autonomy = (skill_root / "conventions" / "autonomy.md").read_text(encoding="utf-8")

    if "Opt-In 보조 천정" not in resources:
        issues.append("resources.md: Opt-In 보조 천정 절 누락 (PR-3)")
    if "컨셉 충돌" not in resources:
        issues.append("resources.md: 컨셉 충돌 명시 누락 (PR-3)")
    if "기본 비활성" not in resources:
        issues.append("resources.md: 기본 비활성 명시 누락 (PR-3)")
    if "[supplementary_ceiling]" not in resources:
        issues.append("resources.md: config.toml schema 누락 (PR-3)")

    if "1-aux" not in autonomy or "2-aux" not in autonomy:
        issues.append("autonomy.md: Q-D3 sub-option (1-aux/2-aux) 흡수 누락 (PR-3)")

    return issues


def check_anti_patterns_consolidation(repo_root: Path, skill_root: Path) -> list[str]:
    """C40 — SKILL.md 의 안티 패턴 통합 카탈로그 + 페이즈별 본문이 통합 카탈로그 링크."""
    issues: list[str] = []
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "안티 패턴 통합 카탈로그" not in skill:
        issues.append("SKILL.md: 안티 패턴 통합 카탈로그 절 누락 (PR-11)")
    for p in sorted((skill_root / "phases").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if "흔한 실패" in text and "안티 패턴 통합 카탈로그" not in text:
            issues.append(f"{p.name}: 흔한 실패 절은 있으나 통합 카탈로그 링크 누락 (PR-11)")
    return issues


def check_description_length_and_anti_pattern(repo_root: Path, skill_root: Path) -> list[str]:
    """C41 — 2 SKILL.md description 이 200자 이하 + 두 스킬 모두 anti-pattern 마커 보유 (v0.8.1)."""
    issues: list[str] = []
    skill_dirs = ["theseus-harness", "theseus-orchestrator"]
    for name in skill_dirs:
        path = repo_root / "skills" / name / "SKILL.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^description:\s*(.+?)$", text, re.MULTILINE)
        if not m:
            issues.append(f"{name}: frontmatter description 누락")
            continue
        desc = m.group(1).strip()
        if len(desc) > 200:
            issues.append(f"{name}: description {len(desc)}자 — 200자 초과 (PR-12 압축 후)")
        # grade-scope 위반 어구 검증 (v0.8.3) — 호출 거부 의미의 표현 부재.
        for forbidden in ["사용 금지", "호출 거부", "진입 거부", "사소한 작업"]:
            if forbidden in desc:
                issues.append(
                    f"{name}: description 에 grade-as-gate 위반 어구 '{forbidden}' 잔존 "
                    f"(그레이드는 내부 모듈레이션만, 외부 거부 의미 표현 금지)"
                )
    return issues


def check_hard_rule_markup(repo_root: Path, skill_root: Path) -> list[str]:
    """C43 — theseus-harness SKILL.md 의 하드 룰 절이 HARD-RULE 마크업 보유."""
    issues: list[str] = []
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "## 하드 룰" in skill and "<!-- HARD-RULE:" not in skill:
        issues.append("SKILL.md: 하드 룰 절은 있으나 HARD-RULE 마크업 누락 (PR-10)")
    return issues


def check_decomposed_standalone_honesty(repo_root: Path, skill_root: Path) -> list[str]:
    """C37 — orchestrator 가 harness 동반 의존 명시 (v0.8.1 sprint-03-b 단순화).

    이전: 7 phase stub 의 단독 호출 가능성 + 본문 점프 정직성.
    sprint-03-b 에서 7 stub 제거. orchestrator 가 harness 의 콘텐츠를
    참조하므로 'theseus-harness 동반 필수' 명시만 검증.
    """
    issues: list[str] = []
    orch_path = repo_root / "skills" / "theseus-orchestrator" / "SKILL.md"
    if not orch_path.exists():
        return ["theseus-orchestrator/SKILL.md 누락"]
    text = orch_path.read_text(encoding="utf-8")
    if "theseus-harness" not in text:
        issues.append("theseus-orchestrator 가 theseus-harness 의존 명시 누락")
    return issues


def check_plan_tree_wired(skill_root: Path) -> list[str]:
    """C-PT — plan-tree.md (AIDE 플랜 트리, v0.6.0) wiring 일관성.

    검증 항목:
      a- conventions/plan-tree.md 존재 + 5 시드 카탈로그 (domain-first /
         adapter-first / minimal-subtraction / tdd-topology / strict-layering).
      b- phases/06-plan.md 가 plan-tree.md 링크 + G3+ 디폴트 명시.
      c- conventions/grades.md 매트릭스 row 에 plan-tree.md.
      d- SKILL.md 산출물 트리에 plan/candidates/ + tournament.md 명시.
    """
    issues: list[str] = []
    pt = skill_root / "conventions" / "plan-tree.md"
    if not pt.exists():
        return ["conventions/plan-tree.md 누락 — AIDE 플랜 트리 컨벤션 정의 필요"]
    pt_text = _read(pt)
    seeds = ["domain-first", "adapter-first", "minimal-subtraction", "tdd-topology", "strict-layering"]
    for seed in seeds:
        if seed not in pt_text:
            issues.append(f"conventions/plan-tree.md 가 5 시드 카탈로그 '{seed}' 누락")

    phase06 = _read(skill_root / "phases" / "06-plan.md")
    if "plan-tree.md" not in phase06:
        issues.append("phases/06-plan.md 가 plan-tree.md 링크 누락")
    if "G3" not in phase06 or "디폴트" not in phase06:
        issues.append("phases/06-plan.md 가 G3+ 디폴트 트리 명시 누락")

    grades = _read(skill_root / "conventions" / "grades.md")
    if "plan-tree.md" not in grades:
        issues.append("conventions/grades.md 매트릭스에 plan-tree.md row 누락")

    skill = _read(skill_root / "SKILL.md")
    if "plan/candidates" not in skill and "candidates/universe" not in skill:
        issues.append("SKILL.md 산출물 트리에 plan/candidates/ 명시 누락")
    if "tournament.md" not in skill:
        issues.append("SKILL.md 산출물 트리에 plan/tournament.md 명시 누락")

    # planner 에이전트가 5 시드 prompt prefix 를 *문자 그대로* 명시하는지 (sprint-02-e #1)
    planner = _read(skill_root / "agents" / "planner.md")
    for seed in seeds:
        if f"UNIVERSE SEED: {seed}" not in planner:
            issues.append(f"agents/planner.md 가 시드 prefix '[UNIVERSE SEED: {seed}]' 누락")

    # universe-meta 템플릿 존재 + 핵심 키 (sprint-02-e #5)
    universe_template = skill_root / "templates" / "universe-meta.template.md"
    if not universe_template.exists():
        issues.append("templates/universe-meta.template.md 누락 — meta.md reference 부재")
    else:
        ut = _read(universe_template)
        for key in ["universe_id", "seed", "depth", "score:", "status", "hypothesis"]:
            if key not in ut:
                issues.append(f"templates/universe-meta.template.md 가 frontmatter 키 '{key}' 누락")
    return issues


def check_runtime_prereq_wired(skill_root: Path) -> list[str]:
    """C-RP — runtime-prereq.md + Q-D9 + 게이트 7 (v0.7.0) wiring 일관성.

    검증 항목 (RP1~RP4):
      RP1- conventions/runtime-prereq.md 가 .env / .gitignore 자동 추가 룰 명시.
      RP2- Q-D9 wiring — autonomy.md ### Q-D9 + env_satisfied + entry_blocked,
           phases/04-clarify.md 산출물 04-runtime-prereq.md + Q-D9 + 9 답,
           phases/09-quality-gates.md 게이트 7 + env-satisfied 키워드.
      RP3- runtime-prereq.md 가 .env.template 보안 가드 (sk_live_ / prod-) 명시.
      RP4- G5 mock 금지 명시 (runtime-prereq.md + grades.md 매트릭스).
    """
    issues: list[str] = []
    rp = skill_root / "conventions" / "runtime-prereq.md"
    if not rp.exists():
        return ["conventions/runtime-prereq.md 누락 — Q-D9 / 게이트 7 컨벤션 정의 필요"]
    rp_text = _read(rp)

    # RP1 — .env / .gitignore 자동 추가 룰
    if ".gitignore" not in rp_text or ".env" not in rp_text:
        issues.append("[RP1] runtime-prereq.md 가 .env / .gitignore 자동 추가 룰 누락")

    # RP2 — Q-D9 wiring
    autonomy = _read(skill_root / "conventions" / "autonomy.md")
    for must in ["### Q-D9", "env_satisfied", "entry_blocked"]:
        if must not in autonomy:
            issues.append(f"[RP2] autonomy.md 가 Q-D9 wiring '{must}' 누락")

    phase04 = _read(skill_root / "phases" / "04-clarify.md")
    if "04-runtime-prereq.md" not in phase04:
        issues.append("[RP2] phases/04-clarify.md 산출물에 04-runtime-prereq.md 누락")
    if "Q-D9" not in phase04:
        issues.append("[RP2] phases/04-clarify.md 본문에 Q-D9 명시 누락")
    if "Q-D1 ~ Q-D9" not in phase04 and "9 답" not in phase04:
        issues.append("[RP2] phases/04-clarify.md 가 사전 위임 9 답 (Q-D1~Q-D9) 명시 누락")

    phase09 = _read(skill_root / "phases" / "09-quality-gates.md")
    if "게이트 7" not in phase09 and "Gate 7" not in phase09:
        issues.append("[RP2] phases/09-quality-gates.md 가 게이트 7 (env-satisfied) 명시 누락")
    if "env-satisfied" not in phase09 and "env_satisfied" not in phase09:
        issues.append("[RP2] phases/09-quality-gates.md 게이트 7 에 env-satisfied 키워드 누락")

    # RP3 — .env.template 보안 가드
    if "sk_live_" not in rp_text or "prod" not in rp_text:
        issues.append("[RP3] runtime-prereq.md 가 .env.template 보안 가드 (sk_live_ / prod-) 명시 누락")

    # RP4 — G5 mock 금지
    if "mock 금지" not in rp_text and "mock 금지" not in _read(skill_root / "conventions" / "grades.md"):
        issues.append("[RP4] runtime-prereq.md 또는 grades.md 가 G5 mock 금지 룰 명시 누락")

    # RP5 — runtime-detector 에이전트 존재 + clarifier 가 부속 호출 (sprint-02-e #3)
    detector = skill_root / "agents" / "runtime-detector.md"
    if detector.exists():
        det_text = _read(detector)
        for must in ["Q-D9", "env_satisfied", ".env.template"]:
            if must not in det_text:
                issues.append(f"[RP5] agents/runtime-detector.md 가 wiring 키워드 '{must}' 누락")

    # RP6 — runtime-prereq.template + env.template 존재 (sprint-02-e #5)
    rp_template = skill_root / "templates" / "runtime-prereq.template.md"
    if not rp_template.exists():
        issues.append("[RP6] templates/runtime-prereq.template.md 누락 — Q-D9 산출물 reference 부재")
    else:
        rt = _read(rp_template)
        for key in ["env_satisfied", "secrets_count", "mode", "boot_command", "entry_blocked"]:
            if f"{key}:" not in rt:
                issues.append(f"[RP6] templates/runtime-prereq.template.md frontmatter '{key}' 키 누락")

    env_template = skill_root / "templates" / "env.template.md"
    if not env_template.exists():
        issues.append("[RP6] templates/env.template.md 누락 — 도메인별 .env 키 카탈로그 부재")

    # RP7 — webview Runtime 탭 (sprint-02-e #6)
    runtime_tab = skill_root / "templates" / "webview" / "src" / "tabs" / "Runtime.tsx"
    if not runtime_tab.exists():
        issues.append("[RP7] templates/webview/src/tabs/Runtime.tsx 누락 — Q-D9 / 게이트 7 사용자 대면 표면 부재")
    app_tsx = skill_root / "templates" / "webview" / "src" / "App.tsx"
    if app_tsx.exists():
        app_text = _read(app_tsx)
        if "Runtime" not in app_text or "runtime" not in app_text:
            issues.append("[RP7] templates/webview/src/App.tsx 가 Runtime 탭 등록 누락")
    phase12 = _read(skill_root / "phases" / "12-webview-assembly.md")
    if "Runtime" not in phase12:
        issues.append("[RP7] phases/12-webview-assembly.md 가 Runtime 탭 명시 누락")

    return issues


def check_orchestrator_driver_hardrule(skill_root: Path) -> list[str]:
    """C-OD — orchestrator 강제 driver HARD-RULE 명시 검증 (sprint-03-a, v0.8.0).

    livetest 시나리오 #1 fail (sub-claude 가 직접 코드 작성 + retroactive
    metadata generator 작성으로 우회) 정정. 본 룰은 다음을 검증:
      a- harness/SKILL.md + orchestrator/SKILL.md 모두 'HARD-RULE' 헤더 + 첫 동작
         (timing/start.json + intent/01-intent.md or naming/00-naming.md) 명시.
      b- 위반 안티패턴 (retroactive metadata generator / build_artifacts.py /
         out-of-sandbox / 페이즈 04 생략) 모두 명시.
    """
    issues: list[str] = []
    # sprint-20 v0.9.25 — HARD-RULE 본문은 HARD-CORE.md 로 분리 (SKILL.md 는 인덱스만)
    hard_core = skill_root / "HARD-CORE.md"
    if hard_core.exists():
        targets = [hard_core, skill_root.parent / "theseus-orchestrator" / "SKILL.md"]
    else:
        targets = [skill_root / "SKILL.md", skill_root.parent / "theseus-orchestrator" / "SKILL.md"]
    must_haves = [
        "HARD-RULE",
        "timing/start.json",
        "intent/01-intent.md",
        "build_artifacts.py",     # retroactive 안티패턴 명시
        "out-of-sandbox",         # 우회 사유 안티패턴 명시
        "00-violation.md",        # 위반 시 처리 산출물
        "의무 산출물",             # HARD-RULE 8 — 그레이드별 산출물 체크리스트 (sprint-03-c)
        "조기 종료",               # 자발적 조기 종료 금지 명시
    ]
    for tgt in targets:
        if not tgt.exists():
            issues.append(f"{tgt.name} 누락 — orchestrator driver HARD-RULE 적용 대상")
            continue
        text = _read(tgt)
        for must in must_haves:
            if must not in text:
                rel = tgt.relative_to(skill_root.parent)
                issues.append(f"{rel}: HARD-RULE 키워드 '{must}' 누락")
    return issues


# === sprint-05-a 신규 룰 (TDD test-first — RED 확인 단계) ===

def check_build_config_ruff_integration(skill_root: Path) -> list[str]:
    """C-LINT1 — conventions/build-and-config.md 가 ruff 통합을 명시 (sprint-05-a A)."""
    text = _read(skill_root / "conventions" / "build-and-config.md")
    issues: list[str] = []
    if "ruff" not in text.lower():
        issues.append("conventions/build-and-config.md: ruff 통합 본문 누락")
    if "ruff check" not in text and "ruff format" not in text:
        issues.append(
            "conventions/build-and-config.md: ruff 호출 명령 (ruff check / ruff format) 누락"
        )
    return issues


def check_phase12_theseus_view_naming(skill_root: Path) -> list[str]:
    """C-WV1 — phases/12-webview-assembly.md 본문에 theseus-view 명시 (sprint-05-a C)."""
    text = _read(skill_root / "phases" / "12-webview-assembly.md")
    if "theseus-view" not in text:
        return [
            "phases/12-webview-assembly.md: 'theseus-view' (스킬 진행 추적 viewer) 명시 누락"
        ]
    return []


def check_phase13_interactive_viewer_present(skill_root: Path) -> list[str]:
    """C-WV2 — phases/13-interactive-viewer.md 신규 + 본문 키워드 (sprint-05-a C)."""
    p = skill_root / "phases" / "13-interactive-viewer.md"
    if not p.exists():
        return [
            "phases/13-interactive-viewer.md: 신규 페이즈 파일 누락 "
            "(interactive-viewer = 프로젝트 output observability 관측용 뷰어)"
        ]
    text = _read(p)
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["interactive-viewer", "observability", "도메인", "dashboard"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"phases/13-interactive-viewer.md: '{kw}' 키워드 본문 누락")
    return issues


def check_phase14_handoff_renamed(skill_root: Path) -> list[str]:
    """C-WV3 — phases/14-handoff.md 신규 (현 13-handoff → 14-handoff 이동, sprint-05-a C)."""
    p = skill_root / "phases" / "14-handoff.md"
    if not p.exists():
        return [
            "phases/14-handoff.md: 페이즈 14 신규 누락 "
            "(현 phases/13-handoff.md → phases/14-handoff.md 이동 의무)"
        ]
    text = _read(p)
    if "페이즈 14" not in text and "phase 14" not in text.lower():
        return ["phases/14-handoff.md: 페이즈 14 번호 본문 명시 누락"]
    return []


def check_interactive_viewer_builder_agent(skill_root: Path) -> list[str]:
    """C-AGENT-IVB — agents/interactive-viewer-builder.md 신규 (페이즈 13 책임, sprint-05-a C)."""
    p = skill_root / "agents" / "interactive-viewer-builder.md"
    if not p.exists():
        return [
            "agents/interactive-viewer-builder.md: 신규 에이전트 파일 누락 (페이즈 13 책임)"
        ]
    text = _read(p)
    issues: list[str] = []
    if "권장 모델:" not in text:
        issues.append("agents/interactive-viewer-builder.md: '권장 모델:' 줄 누락")
    if "fingerprint" not in text.lower():
        issues.append("agents/interactive-viewer-builder.md: fingerprint.py 호출 명시 누락")
    return issues


def check_phase08_tdd_subphases(skill_root: Path) -> list[str]:
    """C-TDD-08 — phases/08-implement.md 본문에 5 서브페이즈 + RED-GREEN-REFACTOR (sprint-05-a TDD)."""
    text = _read(skill_root / "phases" / "08-implement.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["08-α", "08-β", "08-γ", "RED", "GREEN", "REFACTOR", "test-first", "universe 변경"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(
                f"phases/08-implement.md: '{kw}' 5 서브페이즈/TDD 키워드 본문 누락"
            )
    return issues


# === sprint-05-b 신규 룰 (TDD test-first — multi-universe 폭 확장 + impl head-to-head) ===

def check_grades_multiverse_width_expanded(skill_root: Path) -> list[str]:
    """C-MV1 — conventions/grades.md 의 G3/G4/G5 멀티버스 폭 확장 (sprint-05-b)."""
    text = _read(skill_root / "conventions" / "grades.md")
    issues: list[str] = []
    needed = ["폭 3", "폭 4", "폭 6", "sprint-05-b"]
    for kw in needed:
        if kw not in text:
            issues.append(f"conventions/grades.md: '{kw}' 멀티버스 폭 확장 키워드 누락")
    return issues


def check_phase08_universe_head_to_head(skill_root: Path) -> list[str]:
    """C-MV2 — phases/08-implement.md 본문에 universe 별 5 서브페이즈 사이클 + head-to-head (sprint-05-b)."""
    text = _read(skill_root / "phases" / "08-implement.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["universe 별 implementer", "head-to-head", "universe 별 5 서브페이즈"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"phases/08-implement.md: '{kw}' multi-universe head-to-head 키워드 누락")
    return issues


def check_plan_tree_axis_catalog(skill_root: Path) -> list[str]:
    """C-MV3 — conventions/plan-tree.md 분기 축 카탈로그 ≥6 axis (sprint-05-b)."""
    text = _read(skill_root / "conventions" / "plan-tree.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed_axes = [
        "process-vs-data",
        "sync-vs-async",
        "centralized-vs-distributed",
        "dynamic-vs-static",
        "push-vs-pull",
        "mutable-vs-immutable",
    ]
    found = sum(1 for ax in needed_axes if ax in text_lower)
    if found < 6:
        issues.append(
            f"conventions/plan-tree.md: 분기 축 카탈로그 ≥6 axis 누락 (현재 {found}/6: "
            f"{', '.join(ax for ax in needed_axes if ax not in text_lower)} 누락)"
        )
    return issues


def check_competition_auto_merge_algorithm(skill_root: Path) -> list[str]:
    """C-MV4 — conventions/competition.md 자동 머지 알고리즘 강화 (sprint-05-b)."""
    text = _read(skill_root / "conventions" / "competition.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["자동 머지 알고리즘", "차원별 sub-score", "head-to-head"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"conventions/competition.md: '{kw}' 자동 머지 강화 키워드 누락")
    return issues


def check_resources_multiverse_budget(skill_root: Path) -> list[str]:
    """C-MV5 — conventions/resources.md 의 universe N 병렬 budget profile (sprint-05-b)."""
    text = _read(skill_root / "conventions" / "resources.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["universe N 병렬 budget", "병렬 universe 메모리 가드"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"conventions/resources.md: '{kw}' multi-universe 자원 가드 키워드 누락")
    return issues


# === sprint-05-d 신규 룰 (페이즈 13 interactive-viewer 의 결과 프로덕트 only 강제) ===

def check_phase13_product_only(skill_root: Path) -> list[str]:
    """C-IV1 — phases/13-interactive-viewer.md 본문에 결과 프로덕트 only 명시 + 하네스 메타 emit 금지 (sprint-05-d)."""
    text = _read(skill_root / "phases" / "13-interactive-viewer.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["결과 프로덕트", "topology", "animation", "drill-down", "하네스 메타 emit 금지"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"phases/13-interactive-viewer.md: '{kw}' 결과 프로덕트 only 키워드 누락 (sprint-05-d)")
    return issues


def check_interactive_viewer_agent_product_only(skill_root: Path) -> list[str]:
    """C-IV2 — agents/interactive-viewer-builder.md 의 책임 좁힘 (결과 프로덕트 only, 하네스 메타 금지) (sprint-05-d)."""
    text = _read(skill_root / "agents" / "interactive-viewer-builder.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["프로젝트 결과 only", "하네스 메타 emit 금지", "topology", "animation"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"agents/interactive-viewer-builder.md: '{kw}' 결과 프로덕트 only 책임 명시 누락 (sprint-05-d)")
    return issues


# === sprint-05-e 신규 룰 (Q1 회귀 원인 분류 + Q3 plan 본문 implementation guidance) ===

def check_phase11_regression_classification(skill_root: Path) -> list[str]:
    """C-RB1 — phases/11-regression-bisect.md 본문에 회귀 원인 4 분류 (sprint-05-e Q1)."""
    text = _read(skill_root / "phases" / "11-regression-bisect.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["plan defect", "impl defect", "data defect", "external defect", "회귀 원인 분류"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"phases/11-regression-bisect.md: '{kw}' 회귀 분류 키워드 누락 (sprint-05-e)")
    return issues


def check_phase06_implementation_guidance(skill_root: Path) -> list[str]:
    """C-IG1 — phases/06-plan.md 본문에 implementation guidance 절 (sprint-05-e Q3)."""
    text = _read(skill_root / "phases" / "06-plan.md")
    text_lower = text.lower()
    issues: list[str] = []
    needed = ["implementation guidance", "데이터 구조", "의사코드", "클래스 시그니처"]
    for kw in needed:
        if kw not in text and kw.lower() not in text_lower:
            issues.append(f"phases/06-plan.md: '{kw}' implementation guidance 키워드 누락 (sprint-05-e)")
    return issues


def check_convention_traceability(skill_root: Path) -> list[str]:
    """C-CT — convention-traceability.md 본문 + contracts.md 의 expected catalog spec (v0.9.16 sprint-10 #1)."""
    issues: list[str] = []
    ct_path = skill_root / "conventions" / "convention-traceability.md"
    if not ct_path.exists():
        issues.append("conventions/convention-traceability.md 누락")
        return issues
    ct = _read(ct_path)
    required = ["applied_conventions", "expected", "convention_usage", "zero-applied"]
    for kw in required:
        if kw not in ct:
            issues.append(f"convention-traceability.md: '{kw}' 키워드 누락")
    return issues


def check_sprint_score_delta_tracking(skill_root: Path) -> list[str]:
    """C-SDT — sprint-score-delta-tracking.md + budget-saturation-loop cross-ref (v0.9.16 sprint-10 #2)."""
    issues: list[str] = []
    sdt_path = skill_root / "conventions" / "sprint-score-delta-tracking.md"
    bsl_path = skill_root / "conventions" / "budget-saturation-loop.md"
    if not sdt_path.exists():
        issues.append("conventions/sprint-score-delta-tracking.md 누락")
        return issues
    sdt = _read(sdt_path)
    bsl = _read(bsl_path)
    required = ["delta", "lesson_applied", "EXPECTED_DELTA", "label honesty"]
    for kw in required:
        if kw not in sdt:
            issues.append(f"sprint-score-delta-tracking.md: '{kw}' 키워드 누락")
    if "sprint-score-delta-tracking" not in bsl:
        issues.append("budget-saturation-loop.md: sprint-score-delta-tracking cross-ref 누락")
    return issues


def check_evidence_driven_sprint_planning(skill_root: Path) -> list[str]:
    """C-EDP — evidence-driven-sprint-planning.md + score-rubric / budget-sat cross-ref (v0.9.16 sprint-10 #3)."""
    issues: list[str] = []
    edp_path = skill_root / "conventions" / "evidence-driven-sprint-planning.md"
    sro_path = skill_root / "conventions" / "score-rubric-objectivity.md"
    bsl_path = skill_root / "conventions" / "budget-saturation-loop.md"
    if not edp_path.exists():
        issues.append("conventions/evidence-driven-sprint-planning.md 누락")
        return issues
    edp = _read(edp_path)
    sro = _read(sro_path)
    bsl = _read(bsl_path)
    required = ["next_sprint_candidates", "lesson_source", "free_lesson_allowed", "candidate_match"]
    for kw in required:
        if kw not in edp:
            issues.append(f"evidence-driven-sprint-planning.md: '{kw}' 키워드 누락")
    if "evidence-driven-sprint-planning" not in sro:
        issues.append("score-rubric-objectivity.md: evidence-driven-sprint-planning cross-ref 누락")
    if "evidence-driven-sprint-planning" not in bsl:
        issues.append("budget-saturation-loop.md: evidence-driven-sprint-planning cross-ref 누락")
    return issues


def check_cross_universe_lesson_distillation(skill_root: Path) -> list[str]:
    """C-CULD — cross-universe-lesson-distillation.md + plan-tree / ensemble cross-ref (v0.9.16 sprint-10 #4)."""
    issues: list[str] = []
    culd_path = skill_root / "conventions" / "cross-universe-lesson-distillation.md"
    pt_path = skill_root / "conventions" / "plan-tree.md"
    ens_path = skill_root / "conventions" / "ensemble-synthesis-default.md"
    if not culd_path.exists():
        issues.append("conventions/cross-universe-lesson-distillation.md 누락")
        return issues
    culd = _read(culd_path)
    pt = _read(pt_path)
    ens = _read(ens_path)
    required = ["Patterns to Avoid", "avoid_patterns", "extract_loser_weakness", "weakest_dim"]
    for kw in required:
        if kw not in culd:
            issues.append(f"cross-universe-lesson-distillation.md: '{kw}' 키워드 누락")
    if "cross-universe-lesson-distillation" not in pt:
        issues.append("plan-tree.md: cross-universe-lesson-distillation cross-ref 누락")
    if "cross-universe-lesson-distillation" not in ens:
        issues.append("ensemble-synthesis-default.md: cross-universe-lesson-distillation cross-ref 누락")
    return issues


def check_regression_derived_lint_rule_autogen(skill_root: Path) -> list[str]:
    """C-RDLR — regression-derived-lint-rule-autogen.md + phase 11 cross-ref (v0.9.16 sprint-10 #5)."""
    issues: list[str] = []
    rdlr_path = skill_root / "conventions" / "regression-derived-lint-rule-autogen.md"
    p11_path = skill_root / "phases" / "11-regression-bisect.md"
    if not rdlr_path.exists():
        issues.append("conventions/regression-derived-lint-rule-autogen.md 누락")
        return issues
    rdlr = _read(rdlr_path)
    p11 = _read(p11_path)
    required = ["lint_rule_proposal", "rule_id", "regression_lint_registry", "C-RDR"]
    for kw in required:
        if kw not in rdlr:
            issues.append(f"regression-derived-lint-rule-autogen.md: '{kw}' 키워드 누락")
    if "regression-derived-lint-rule-autogen" not in p11:
        issues.append("phases/11-regression-bisect.md: regression-derived-lint-rule-autogen cross-ref 누락")
    return issues


def check_grade_assess_v2(skill_root: Path) -> list[str]:
    """C-GAv2 — grade_assess.py 의 키워드 매칭 폐기 + default G4 + 다중 신호 (v0.9.17 sprint-11)."""
    issues: list[str] = []
    ga = (skill_root / "scoring" / "grade_assess.py").read_text(encoding="utf-8")
    grades_md = (skill_root / "conventions" / "grades.md").read_text(encoding="utf-8")
    p1 = (skill_root / "phases" / "01-intent.md").read_text(encoding="utf-8")
    p4 = (skill_root / "phases" / "04-clarify.md").read_text(encoding="utf-8")

    # 1. grade_assess.py 에서 키워드 매칭 폐기 확인
    deprecated_kw = ["TRIGGERS_G5", "TRIGGERS_G4", "TRIGGERS_G2", "TRIGGERS_G1"]
    for kw in deprecated_kw:
        if kw in ga:
            issues.append(f"grade_assess.py: 폐기 키워드 set '{kw}' 잔존 (v0.9.17 키워드 매칭 폐기)")

    # 2. grade_assess.py 가 다중 신호 dataclass + default G4 보유
    required_ga = ["GradeSignals", "ESCALATION_TRIGGERS", "_is_proven_simple", "primary_grade", "default_was"]
    for kw in required_ga:
        if kw not in ga:
            issues.append(f"grade_assess.py: '{kw}' 누락 (v0.9.17 다중 신호 알고리즘)")

    # 3. grades.md 가 default G4 + 18+ 신호 카탈로그 + 키워드 매칭 폐기 명시
    required_grades = ["default = G4", "키워드 매칭 폐기", "GradeSignals", "escalation triggers", "단순함 증명"]
    for kw in required_grades:
        if kw not in grades_md:
            issues.append(f"grades.md: '{kw}' 키워드 누락 (v0.9.17)")

    # 4. phase 01 §j grade signals 산출 단계
    if "grade-signals.json" not in p1 or "mindmap-signals.json" not in p1:
        issues.append("phases/01-intent.md: §j grade signals 산출물 (intent/01-grade-signals.json / intent/01-mindmap-signals.json) 누락")

    # 5. phase 04 Q-G1 의 default G4 명시
    if "default = G4" not in p4 and "default G4" not in p4:
        issues.append("phases/04-clarify.md: Q-G1 본문에 'default = G4' 명시 누락")

    return issues


def check_polyglot_code_quality(skill_root: Path) -> list[str]:
    """C-PCQ — polyglot-code-quality.md + 9 언어 카탈로그 + 6 메트릭 (v0.9.16 sprint-10 #6)."""
    issues: list[str] = []
    pcq_path = skill_root / "conventions" / "polyglot-code-quality.md"
    bnc_path = skill_root / "conventions" / "build-and-config.md"
    if not pcq_path.exists():
        issues.append("conventions/polyglot-code-quality.md 누락")
        return issues
    pcq = _read(pcq_path)
    bnc = _read(bnc_path)
    required_languages = ["Python", "Go", "TypeScript", "Rust", "Java", "Ruby"]
    for lang in required_languages:
        if lang not in pcq:
            issues.append(f"polyglot-code-quality.md: '{lang}' 언어 카탈로그 누락")
    required_metrics = [
        "cyclomatic_complexity", "function_length", "nesting_depth",
        "duplicate_blocks", "lint_errors", "format_diff",
    ]
    for m in required_metrics:
        if m not in pcq:
            issues.append(f"polyglot-code-quality.md: '{m}' 메트릭 누락")
    if "polyglot-code-quality" not in bnc:
        issues.append("build-and-config.md: polyglot-code-quality cross-ref 누락")
    return issues


def check_dacapo_enforcement(skill_root: Path) -> list[str]:
    """C-DCL-GATE — dacapo-enforcement.md (bm, sprint-16 v0.9.22) — 의사코드 → runtime guard."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-enforcement.md"
    if not p.exists():
        issues.append("conventions/dacapo-enforcement.md 누락 (bm, v0.9.22)")
        return issues
    body = _read(p)
    for kw in [
        "HARD-RULE 9.o", "gate_phase06_to_07", "dacapo_loop_executed",
        "step_d_tournament_pass", "step_d_shadow_pass", "fallback_reason",
        "intent/00-violation.md", "force_re_enter_phase",
    ]:
        if kw not in body:
            issues.append(f"dacapo-enforcement.md: '{kw}' 키워드 누락")
    orch = skill_root.parent / "theseus-orchestrator" / "SKILL.md"
    if orch.exists() and "HARD-RULE 9.p" not in _read(orch):
        issues.append("orchestrator/SKILL.md: HARD-RULE 9.p (dacapo-enforcement) 누락")
    return issues


def check_dacapo_frontmatter_schema(skill_root: Path) -> list[str]:
    """C-DCL-FRONTMATTER — dacapo-frontmatter-schema.md (bn, sprint-16 v0.9.22)."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-frontmatter-schema.md"
    if not p.exists():
        issues.append("conventions/dacapo-frontmatter-schema.md 누락 (bn, v0.9.22)")
        return issues
    body = _read(p)
    for field in [
        "dacapo_loop_executed", "rerun_count", "step_d_converged",
        "winner_score", "winner_sub_scores", "weakest_dim",
        "step_e_cap_reached", "budget_used_total", "next_action",
        "anonymized_prev_winner_id", "fresh_seeds_picked",
        "prior_context_token_count", "loaded_artifacts", "agent_call_id",
    ]:
        if field not in body:
            issues.append(f"dacapo-frontmatter-schema.md: '{field}' 필드 누락")
    return issues


def check_shadow_grader_zero_context(skill_root: Path) -> list[str]:
    """C-DCL-SHADOW-CONTEXT — shadow-grader-zero-context.md (bo, sprint-16 v0.9.22)."""
    issues: list[str] = []
    p = skill_root / "conventions" / "shadow-grader-zero-context.md"
    if not p.exists():
        issues.append("conventions/shadow-grader-zero-context.md 누락 (bo, v0.9.22)")
        return issues
    body = _read(p)
    for kw in [
        "prior_context_token_count", "agent_call_id", "loaded_artifacts",
        "subagent_type", "rubric_path", "check_shadow_independence",
        "check_unique_agent_call", "3pt", "복사 의심",
    ]:
        if kw not in body:
            issues.append(f"shadow-grader-zero-context.md: '{kw}' 키워드 누락")
    return issues


def check_dacapo_skip_sentinel(skill_root: Path) -> list[str]:
    """C-DCL-SENTINEL — dacapo-skip-sentinel.md (bp, sprint-16 v0.9.22)."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-skip-sentinel.md"
    if not p.exists():
        issues.append("conventions/dacapo-skip-sentinel.md 누락 (bp, v0.9.22)")
        return issues
    body = _read(p)
    for kw in [
        "Sentinel A", "Sentinel B", "Sentinel C",
        "SENTINEL_A_PATTERNS", "SENTINEL_B_PATTERNS", "SENTINEL_C_LOG_PATTERNS",
        "force_re_enter_phase", "intent/00-violation.md",
        "Winner clear", "skip dacapo", "0회 충분", "단일 탑",
        "universe_skip", "sprint_trinity_skip",
    ]:
        if kw not in body:
            issues.append(f"dacapo-skip-sentinel.md: '{kw}' 키워드 누락")
    return issues


def check_domain_model_completeness(skill_root: Path) -> list[str]:
    """C-DMC — domain-model-completeness.md (bs, sprint-16 v0.9.22) — Conceptual modelling 만점 push."""
    issues: list[str] = []
    p = skill_root / "conventions" / "domain-model-completeness.md"
    if not p.exists():
        issues.append("conventions/domain-model-completeness.md 누락 (bs, v0.9.22)")
        return issues
    body = _read(p)
    for kw in ["D1 entity catalog", "D2 state space", "D3 transition diagram",
               "D4 invariants", "D5 boundaries", "stateDiagram-v2",
               "conceptual_completeness_grade", "§m Domain Model"]:
        if kw not in body:
            issues.append(f"domain-model-completeness.md: '{kw}' 키워드 누락")
    return issues


def check_data_structure_invariants_conv(skill_root: Path) -> list[str]:
    """C-DSI — data-structure-invariants.md (bt, sprint-16 v0.9.22) — Data & topology 만점 push."""
    issues: list[str] = []
    p = skill_root / "conventions" / "data-structure-invariants.md"
    if not p.exists():
        issues.append("conventions/data-structure-invariants.md 누락 (bt, v0.9.22)")
        return issues
    body = _read(p)
    for kw in ["Invariants:", "Topology:", "Access patterns:", "Bounds:",
               "data_topology_grade", "with_invariants_ratio"]:
        if kw not in body:
            issues.append(f"data-structure-invariants.md: '{kw}' 키워드 누락")
    return issues


def check_simulation_physical_invariants(skill_root: Path) -> list[str]:
    """C-SPI — simulation-physical-invariants.md (bu, sprint-16 v0.9.22) — Sim correctness 만점 push."""
    issues: list[str] = []
    p = skill_root / "conventions" / "simulation-physical-invariants.md"
    if not p.exists():
        issues.append("conventions/simulation-physical-invariants.md 누락 (bu, v0.9.22)")
        return issues
    body = _read(p)
    for kw in ["mass conservation", "resource exclusivity", "monotonic time",
               "bounded queue", "no-deadlock", "SimulationInvariantChecker",
               "sim_correctness_grade", "I1", "I2", "I3", "I4", "I5"]:
        if kw not in body:
            issues.append(f"simulation-physical-invariants.md: '{kw}' 키워드 누락")
    return issues


def check_experimental_control_protocol(skill_root: Path) -> list[str]:
    """C-ECP — experimental-control-protocol.md (bv, sprint-16 v0.9.22) — Experimental design 만점 push."""
    issues: list[str] = []
    p = skill_root / "conventions" / "experimental-control-protocol.md"
    if not p.exists():
        issues.append("conventions/experimental-control-protocol.md 누락 (bv, v0.9.22)")
        return issues
    body = _read(p)
    for kw in ["**IV**", "**DV**", "**CV**", "**N**", "**seed**",
               "experimental_design_grade", "reproducibility_seed_explicit",
               "Experimental Control Protocol"]:
        if kw not in body:
            issues.append(f"experimental-control-protocol.md: '{kw}' 키워드 누락")
    return issues


def check_results_decision_mapping(skill_root: Path) -> list[str]:
    """C-RDM — results-decision-mapping.md (bw, sprint-16 v0.9.22) — Results & interpretation 만점 push."""
    issues: list[str] = []
    p = skill_root / "conventions" / "results-decision-mapping.md"
    if not p.exists():
        issues.append("conventions/results-decision-mapping.md 누락 (bw, v0.9.22)")
        return issues
    body = _read(p)
    for kw in ["Results → Decisions Mapping", "Owner", "Deadline",
               "negative_findings_count", "results_interpretation_grade",
               "with_decision_ratio"]:
        if kw not in body:
            issues.append(f"results-decision-mapping.md: '{kw}' 키워드 누락")
    return issues


def check_idiomatic_code_quality(skill_root: Path) -> list[str]:
    """C-ICQ — idiomatic-code-quality.md (bx, sprint-16 v0.9.22) — Code quality 만점 push."""
    issues: list[str] = []
    p = skill_root / "conventions" / "idiomatic-code-quality.md"
    if not p.exists():
        issues.append("conventions/idiomatic-code-quality.md 누락 (bx, v0.9.22)")
        return issues
    body = _read(p)
    for kw in ["Naming convention", "Preferred construct", "Standard library",
               "Readability heuristic", "idiomatic_grade", "magic_number_count",
               "naming_violation_ratio"]:
        if kw not in body:
            issues.append(f"idiomatic-code-quality.md: '{kw}' 키워드 누락")
    return issues


def check_phase_lineage_viewer(skill_root: Path) -> list[str]:
    """C-PLV — phase-lineage-viewer.md (br, sprint-16 v0.9.22) — 프로젝트 전체 lineage 가시화."""
    issues: list[str] = []
    p = skill_root / "conventions" / "phase-lineage-viewer.md"
    if not p.exists():
        issues.append("conventions/phase-lineage-viewer.md 누락 (br, v0.9.22)")
        return issues
    body = _read(p)
    for kw in [
        "lineage.md", "phase 00", "phase 14", "fingerprint chain",
        "Da Capo loop 요약", "Sentinel 위반 이벤트",
        "update_phase_lineage", "final_outcome", "HANDOFF",
        "bypass", "drill-down", "페이즈 04 답안 매핑",
    ]:
        if kw not in body:
            issues.append(f"phase-lineage-viewer.md: '{kw}' 키워드 누락")
    skill = _read(skill_root / "SKILL.md")
    if "phase-lineage-viewer" not in skill:
        issues.append("SKILL.md: phase-lineage-viewer.md 인덱스 누락")
    return issues


def check_dacapo_flow_trace(skill_root: Path) -> list[str]:
    """C-DCL-FLOW-LOG — dacapo-flow-trace.md (bq, sprint-16 v0.9.22)."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-flow-trace.md"
    if not p.exists():
        issues.append("conventions/dacapo-flow-trace.md 누락 (bq, v0.9.22)")
        return issues
    body = _read(p)
    for kw in [
        "dacapo-flow.md", "Mermaid", "flowchart", "subgraph R",
        "timeline", "update_dacapo_flow_diagram", "final_outcome",
        "CONVERGED", "BUDGET_BOUND", "RE_ENTERED", "SENTINEL_REGRESSION",
    ]:
        if kw not in body:
            issues.append(f"dacapo-flow-trace.md: '{kw}' 키워드 누락")
    phase06 = skill_root / "phases" / "06-plan.md"
    if phase06.exists() and "v0.9.22" not in _read(phase06):
        issues.append("phases/06-plan.md: v0.9.22 sprint-16 절 누락")
    phase08 = skill_root / "phases" / "08-implement.md"
    if phase08.exists():
        body = _read(phase08)
        # sprint-22+ history narration cleanup — version label 의존 제거. Da Capo enforcement gate keyword 만 검사.
        if "Da Capo enforcement gate" not in body and "다카포" not in body:
            issues.append("phases/08-implement.md: Da Capo enforcement gate 본문 누락")
    return issues


def check_dacapo_no_forward_projection(skill_root: Path) -> list[str]:
    """C-DCL-NO-FORWARD-PROJECT (sprint-17) — fallback_reason 본문에 forward time projection 라벨 차단.

    LLM 의 시간 추정은 인간 작업시간 기준 → 항상 "시간내 처리 불가능" 으로 편향.
    측정값 (clock_now - start) 외에 사용 금지. cold session 002 winner-by-projection 회귀 정정.
    """
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-enforcement.md"
    if not p.exists():
        return issues
    body = _read(p)
    for kw in [
        "C-DCL-NO-FORWARD-PROJECT",
        "forward projection",
        "측정 only",
        "anticipated",
    ]:
        if kw not in body:
            issues.append(f"dacapo-enforcement.md: sprint-17 '{kw}' 키워드 누락")
    return issues


def check_dacapo_min_loop_attempt(skill_root: Path) -> list[str]:
    """C-DCL-MIN-LOOP-ATTEMPT (sprint-17) — rerun_count >= 1 의무 (cap 발동 전 최소 1 회 실 rerun)."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-enforcement.md"
    if not p.exists():
        return issues
    body = _read(p)
    for kw in [
        "C-DCL-MIN-LOOP-ATTEMPT",
        "최소 1 회 실 rerun",
        "min loop attempt",
    ]:
        if kw not in body:
            issues.append(f"dacapo-enforcement.md: sprint-17 '{kw}' 키워드 누락")
    return issues


def check_diagrams_and_coverage(skill_root: Path) -> list[str]:
    """C-DIAG-AND-COVERAGE (sprint-17) — HARD-RULE 9.a OR → AND.

    sequence + usecase + interface 셋 다 의무. cold session 002 의 sequence 0 / usecase 0 / interface 7
    로 OR 우측 만으로 9.a 통과 회귀 정정.
    """
    issues: list[str] = []
    p = skill_root / "conventions" / "diagrams.md"
    if not p.exists():
        issues.append("conventions/diagrams.md 누락")
        return issues
    body = _read(p)
    for kw in [
        "C-DIAG-AND-COVERAGE",
        "sequenceDiagram ≥ 1 AND",
        "셋 다 의무",
    ]:
        if kw not in body:
            issues.append(f"diagrams.md: sprint-17 '{kw}' 키워드 누락")
    orch = skill_root.parent / "theseus-orchestrator" / "SKILL.md"
    if orch.exists():
        orch_body = _read(orch)
        if "AND Mermaid usecase" not in orch_body:
            issues.append("orchestrator/SKILL.md: HARD-RULE 9.a 가 sequenceDiagram + usecase AND 셋 다 의무 갱신 누락")
    return issues


def check_intent_refresh_post_interview(skill_root: Path) -> list[str]:
    """C-IRPI (sprint-17) — phase 04 → 05 사이 의도 refresh 4 framing universe + 01-additional 의무."""
    issues: list[str] = []
    p = skill_root / "conventions" / "intent-refresh-post-interview.md"
    if not p.exists():
        issues.append("conventions/intent-refresh-post-interview.md 누락 (by, sprint-17)")
        return issues
    body = _read(p)
    for kw in [
        "domain-paradigm", "constraint-paradigm", "risk-paradigm", "outcome-paradigm",
        "01-1-intent.md", "01-2-intent.md", "01-3-intent.md", "01-4-intent.md",
        "01-additional.md",
        "C-IRPI-COUNT", "C-IRPI-FRAMING", "C-IRPI-CHAIN",
        "C-IRPI-CONSUMED", "C-IRPI-CONTRADICTION",
        "interview_answers_consumed",
    ]:
        if kw not in body:
            issues.append(f"intent-refresh-post-interview.md: '{kw}' 키워드 누락")
    phase05 = skill_root / "phases" / "05-critique.md"
    if phase05.exists():
        p5 = _read(phase05)
        if ("01-{1,2,3,4}-intent.md" not in p5) and ("01-1-intent.md" not in p5):
            issues.append("phases/05-critique.md: refresh 4 universes 입력 갱신 누락")
        if "01-additional.md" not in p5:
            issues.append("phases/05-critique.md: 01-additional.md 입력 누락")
    # sprint-20 v0.9.25 — SKILL.md slim 후 INDEX.md 가 단일 router. 둘 중 하나에 있으면 OK.
    harness_skill = skill_root / "SKILL.md"
    harness_idx = skill_root / "conventions" / "INDEX.md"
    found = False
    for p in [harness_skill, harness_idx]:
        if p.exists() and "intent-refresh-post-interview" in _read(p):
            found = True
            break
    if not found:
        issues.append("theseus-harness/{SKILL.md, conventions/INDEX.md}: intent-refresh-post-interview 등록 누락")
    orch = skill_root.parent / "theseus-orchestrator" / "SKILL.md"
    if orch.exists():
        if "intent-refresh-post-interview" not in _read(orch):
            issues.append("orchestrator/SKILL.md: 페이즈별 lookup 표에 intent-refresh-post-interview 누락")
    return issues


def check_readme_numbers_from_summary(skill_root: Path) -> list[str]:
    """C-RNFS (sprint-18, bz) — doc 숫자 vs measurement artifact ±0.01% 일치."""
    issues: list[str] = []
    p = skill_root / "conventions" / "readme-numbers-from-summary.md"
    if not p.exists():
        issues.append("conventions/readme-numbers-from-summary.md 누락 (bz, sprint-18)")
        return issues
    body = _read(p)
    for kw in ["readme-numbers-from-summary", "±0.01%", "summary.json", "drift", "grep", "C-RNFS"]:
        if kw not in body:
            issues.append(f"readme-numbers-from-summary.md: '{kw}' 키워드 누락")
    phase09 = skill_root / "phases" / "09-quality-gates.md"
    if phase09.exists() and "G-RNFS" not in _read(phase09):
        issues.append("phases/09-quality-gates.md: G-RNFS 게이트 등록 누락")
    return issues


def check_reproducibility_doublecheck(skill_root: Path) -> list[str]:
    """C-RDC (sprint-18, ca) — entry script 2회 실행 후 출력 sha256 byte-equal."""
    issues: list[str] = []
    p = skill_root / "conventions" / "reproducibility-doublecheck.md"
    if not p.exists():
        issues.append("conventions/reproducibility-doublecheck.md 누락 (ca, sprint-18)")
        return issues
    body = _read(p)
    for kw in ["reproducibility-doublecheck", "byte-equal", "2회", "sha256", "C-RDC", "hash() 솔트", "PYTHONHASHSEED"]:
        if kw not in body:
            issues.append(f"reproducibility-doublecheck.md: '{kw}' 키워드 누락")
    phase09 = skill_root / "phases" / "09-quality-gates.md"
    if phase09.exists() and "G-RDC" not in _read(phase09):
        issues.append("phases/09-quality-gates.md: G-RDC 게이트 등록 누락")
    return issues


def check_magic_number_traceability(skill_root: Path) -> list[str]:
    """C-MNT (sprint-18, cb) — 코드 매직넘버 → A_i 가정 또는 데이터 파일 출처 1:1 매핑."""
    issues: list[str] = []
    p = skill_root / "conventions" / "magic-number-traceability.md"
    if not p.exists():
        issues.append("conventions/magic-number-traceability.md 누락 (cb, sprint-18)")
        return issues
    body = _read(p)
    for kw in ["magic-number-traceability", "literal", "A_i 가정", "CSV/YAML", "C-MNT", "programming constants"]:
        if kw not in body:
            issues.append(f"magic-number-traceability.md: '{kw}' 키워드 누락")
    phase09 = skill_root / "phases" / "09-quality-gates.md"
    if phase09.exists() and "G-MNT" not in _read(phase09):
        issues.append("phases/09-quality-gates.md: G-MNT 게이트 등록 누락")
    return issues


def check_dead_code_zero(skill_root: Path) -> list[str]:
    """C-DCZ (sprint-18, cc) — 언어별 dead-code analyzer 위반 0 강제."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dead-code-zero.md"
    if not p.exists():
        issues.append("conventions/dead-code-zero.md 누락 (cc, sprint-18)")
        return issues
    body = _read(p)
    for kw in ["dead-code-zero", "ruff", "F,ARG,SIM", "vulture", "C-DCZ", "위반 0"]:
        if kw not in body:
            issues.append(f"dead-code-zero.md: '{kw}' 키워드 누락")
    phase09 = skill_root / "phases" / "09-quality-gates.md"
    if phase09.exists() and "G-DCZ" not in _read(phase09):
        issues.append("phases/09-quality-gates.md: G-DCZ 게이트 등록 누락")
    return issues


def check_submission_portability(skill_root: Path) -> list[str]:
    """C-SPB (sprint-18, cd) — entry script --data-dir CLI flag + DATA_DIR env var fallback."""
    issues: list[str] = []
    p = skill_root / "conventions" / "submission-portability.md"
    if not p.exists():
        issues.append("conventions/submission-portability.md 누락 (cd, sprint-18)")
        return issues
    body = _read(p)
    for kw in ["submission-portability", "--data-dir", "CLI flag", "env var", "C-SPB", "REPO_ROOT.parent.parent", "argparse"]:
        if kw not in body:
            issues.append(f"submission-portability.md: '{kw}' 키워드 누락")
    phase09 = skill_root / "phases" / "09-quality-gates.md"
    if phase09.exists() and "G-SPB" not in _read(phase09):
        issues.append("phases/09-quality-gates.md: G-SPB 게이트 등록 누락")
    return issues


def check_dacapo_mandatory_rerun(skill_root: Path) -> list[str]:
    """C-DCMR (sprint-19, ce) — winner score 임계 도달해도 무조건 ≥ 1 rerun (high-score promote 우회 차단)."""
    issues: list[str] = []
    p = skill_root / "conventions" / "dacapo-mandatory-rerun.md"
    if not p.exists():
        issues.append("conventions/dacapo-mandatory-rerun.md 누락 (ce, sprint-19)")
        return issues
    body = _read(p)
    for kw in ["dacapo-mandatory-rerun", "mandatory_first_rerun_satisfied", "rerun_count >= 1", "예외 0", "C-DCMR", "Step F", "Step G"]:
        if kw not in body:
            issues.append(f"dacapo-mandatory-rerun.md: '{kw}' 키워드 누락")
    return issues


def check_plan_tournament_scoring_strict(skill_root: Path) -> list[str]:
    """C-PTSS (sprint-19, cf) — tournament 6-dim weighted 의무 + 1-5 cold-read coarse reject."""
    issues: list[str] = []
    p = skill_root / "conventions" / "plan-tournament-scoring-strict.md"
    if not p.exists():
        issues.append("conventions/plan-tournament-scoring-strict.md 누락 (cf, sprint-19)")
        return issues
    body = _read(p)
    for kw in ["plan-tournament-scoring-strict", "6-dim weighted", "decision_coverage", "feasibility", "modular_clarity", "1-5 cold-read", "C-PTSS"]:
        if kw not in body:
            issues.append(f"plan-tournament-scoring-strict.md: '{kw}' 키워드 누락")
    return issues


def check_canonical_not_stub(skill_root: Path) -> list[str]:
    """C-CNS (sprint-19, cg) — canonical 산출물 ≥ winner 80% inline 또는 shared schema mode."""
    issues: list[str] = []
    p = skill_root / "conventions" / "canonical-not-stub.md"
    if not p.exists():
        issues.append("conventions/canonical-not-stub.md 누락 (cg, sprint-19)")
        return issues
    body = _read(p)
    for kw in ["canonical-not-stub", "80%", "shared schema", "inline mode", "C-CNS", "asof_fingerprint"]:
        if kw not in body:
            issues.append(f"canonical-not-stub.md: '{kw}' 키워드 누락")
    return issues


def check_impl_multiverse_strict(skill_root: Path) -> list[str]:
    """C-IMS (sprint-19, ch) — phase 08 G4+ multiverse + tournament + dacapo-flow + 5 sub-phase TDD 7 조건 게이트."""
    issues: list[str] = []
    p = skill_root / "conventions" / "impl-multiverse-strict.md"
    if not p.exists():
        issues.append("conventions/impl-multiverse-strict.md 누락 (ch, sprint-19)")
        return issues
    body = _read(p)
    for kw in ["impl-multiverse-strict", "7 조건", "impl/candidates/universe-N", "impl/tournament-impl-NN.md", "5 sub-phase TDD", "C-IMS"]:
        if kw not in body:
            issues.append(f"impl-multiverse-strict.md: '{kw}' 키워드 누락")
    return issues


def check_intent_refresh_post_critique(skill_root: Path) -> list[str]:
    """C-IRPC (sprint-19, ci) — phase 05 후 2nd intent refresh + 04/05 cascade re-write."""
    issues: list[str] = []
    p = skill_root / "conventions" / "intent-refresh-post-critique.md"
    if not p.exists():
        issues.append("conventions/intent-refresh-post-critique.md 누락 (ci, sprint-19)")
        return issues
    body = _read(p)
    for kw in [
        "intent-refresh-post-critique",
        "01-1-intent.v2.md", "01-2-intent.v2.md", "01-3-intent.v2.md", "01-4-intent.v2.md",
        "04-refreshed.md", "05-refreshed.md",
        "critique_findings_consumed", "intent_v1_supersedes",
        "C-IRPC", "사용자 ack 없음",
    ]:
        if kw not in body:
            issues.append(f"intent-refresh-post-critique.md: '{kw}' 키워드 누락")
    phase05 = skill_root / "phases" / "05-critique.md"
    if phase05.exists():
        p5 = _read(phase05)
        if "intent-refresh-post-critique" not in p5:
            issues.append("phases/05-critique.md: sprint-19 mandatory 2nd refresh 절 누락")
        if "01-1-intent.v2.md" not in p5:
            issues.append("phases/05-critique.md: 01-N-intent.v2.md 산출물 명시 누락")
    return issues


def check_cross_phase_shared_context(skill_root: Path) -> list[str]:
    """C-CPSC (sprint-19, cj) — shared 정보 단일 위치 + asof_fingerprint 의무."""
    issues: list[str] = []
    p = skill_root / "conventions" / "cross-phase-shared-context.md"
    if not p.exists():
        issues.append("conventions/cross-phase-shared-context.md 누락 (cj, sprint-19)")
        return issues
    body = _read(p)
    for kw in [
        "cross-phase-shared-context",
        "asof_fingerprint", "shared_context_refs",
        "Domain entity catalog", "Module interface", "TODO DAG",
        "drift", "DRY", "C-CPSC",
    ]:
        if kw not in body:
            issues.append(f"cross-phase-shared-context.md: '{kw}' 키워드 누락")
    return issues


def check_hard_core_size(skill_root: Path) -> list[str]:
    """C-HC1 (sprint-20, v0.9.25) — HARD-CORE.md 본문 ≤ 4000 chars (always-load 부풀음 영구 차단)."""
    issues: list[str] = []
    p = skill_root / "HARD-CORE.md"
    if not p.exists():
        issues.append("HARD-CORE.md 누락 (sprint-20 v0.9.25)")
        return issues
    body = _read(p)
    n = len(body)
    if n > 4000:
        issues.append(f"HARD-CORE.md 길이 {n} chars — 임계 4000 초과 (always-load 부풀음 — lazy 분리 의미 소실)")
    for kw in ["HR1", "HR8", "HR9", "Layer 3", "H1", "H5", "fingerprint", "페이즈 04 외 인터럽트 0"]:
        if kw not in body:
            issues.append(f"HARD-CORE.md: '{kw}' 키워드 누락 (always-load 의무 항목)")
    return issues


def check_conventions_index_completeness(skill_root: Path) -> list[str]:
    """C-IDX-1 (sprint-20, v0.9.25) — conventions/*.md ↔ conventions/INDEX.md row 1:1 매칭."""
    issues: list[str] = []
    idx = skill_root / "conventions" / "INDEX.md"
    if not idx.exists():
        issues.append("conventions/INDEX.md 누락 (sprint-20 v0.9.25)")
        return issues
    body = _read(idx)
    files = {p.stem for p in (skill_root / "conventions").glob("*.md") if p.name != "INDEX.md"}
    import re
    table_ids = set()
    # markdown 표 header row 만 제외 — 첫 컬럼 "id" 가 header 지표 (다른 column 명 'grades' 등은 실 convention 명과 충돌)
    for m in re.finditer(r'^\|\s*([a-z][a-z0-9-]+)\s*\|', body, re.M):
        token = m.group(1)
        if token == "id":
            continue
        table_ids.add(token)
    missing_in_index = files - table_ids
    extra_in_index = table_ids - files
    for x in sorted(missing_in_index):
        issues.append(f"conventions/{x}.md 가 INDEX 에 누락")
    for x in sorted(extra_in_index):
        issues.append(f"INDEX 에 '{x}' row 있으나 conventions/{x}.md 부재")
    return issues


def check_conservative_margin_judging(skill_root: Path) -> list[str]:
    """C-CMJ (sprint-30 v0.9.35) — conservative-margin-judging.md 본문 의무 keyword.

    모든 internal judge (tournament/shadow/sprint stop) 보수적 prior + 0.999 마진 보존 + Da Capo 무한 회귀.
    """
    issues: list[str] = []
    p = skill_root / "conventions" / "conservative-margin-judging.md"
    if not p.exists():
        return ["conventions/conservative-margin-judging.md 누락 (sprint-30)"]
    body = _read(p)
    for kw in [
        "C-CMJ",
        "보수적 prior",
        "0.999 마진",
        "improvement_axes_remaining",
        "judge 자신감 sentinel",
        "rerun-별 score cap",
        "no further sprints required",
    ]:
        if kw not in body:
            issues.append(f"conservative-margin-judging.md: '{kw}' 키워드 누락 (sprint-30)")
    return issues


def check_impl_multiverse_semantics(skill_root: Path) -> list[str]:
    """C-IMS-SEMANTICS (sprint-29 v0.9.34) — impl multiverse 가 plan multiverse 의 손자가 아님 + 입력 격리.

    cold session attempt-2 회귀 정정 — 'Universes 2/3/4 lost the plan tournament before code was written'
    / 'walkover' 패턴 차단. impl universes = plan winner 의 *코드 구현 변형* (입력 격리).
    """
    issues: list[str] = []
    p = skill_root / "conventions" / "impl-multiverse-strict.md"
    if not p.exists():
        return ["conventions/impl-multiverse-strict.md 누락"]
    body = _read(p)
    for kw in [
        "impl multiverse 의미",
        "plan multiverse 의 손자",
        "입력 격리",
        "출력 격리",
        "lost the plan tournament before code was written",
        "walkover",
        "impl universe ID 가 plan universe ID 상속",
        "무한 회귀",
    ]:
        if kw not in body:
            issues.append(f"impl-multiverse-strict.md: '{kw}' 키워드 누락 (sprint-29 정정)")
    return issues


def check_dacapo_fresh_universe(skill_root: Path) -> list[str]:
    """C-DCL-FRESH-UNIVERSE (sprint-28 v0.9.33) — Da Capo Round N+1 = NEW universes 의무.

    cold session 003 attempt-2 회귀 정정 — agent 가 'Round 2 = top-K 생존자 head-to-head' 로
    Da Capo 를 오해. 본 lint 는 컨벤션 본문에 anti-pattern + fresh universe 정의 명시 검증.
    """
    issues: list[str] = []
    p = skill_root / "conventions" / "intra-phase-dacapo-loop.md"
    if not p.exists():
        return ["conventions/intra-phase-dacapo-loop.md 누락"]
    body = _read(p)
    for kw in [
        "C-DCL-FRESH-UNIVERSE",
        "survivors rerun",
        "fresh universe 가 재라벨링",
        "역순 작성",
        "무한 회귀",
        "scoring granularity coarse",
    ]:
        if kw not in body:
            issues.append(f"intra-phase-dacapo-loop.md: '{kw}' 키워드 누락 (sprint-28 anti-pattern g/h/i/j/k)")
    return issues


CHECKS: list[tuple[str, str, callable]] = [
    ("C1", "convention one-line summary", check_convention_one_line_summary),
    ("C2", "SKILL links all conventions", check_skill_links_all_conventions),
    ("C3", "SKILL links all phases", check_skill_links_all_phases),
    ("C4", "SKILL links all agents", check_skill_links_all_agents),
    ("C5", "agents have recommended model", check_agents_recommended_model),
    ("C6", "philosophy/SKILL cross-link", check_philosophy_skill_cross_link),
    ("C7", "plugin/SKILL version match", check_plugin_version_consistency),
    ("C8", "scoring imports compile", check_imports),
    ("C9", "INSTALL doc mentions plugin", check_install_doc),
    ("C10", "phase/agent links", check_phase_agent_links),
    ("C11", "skill README lists conventions", check_skill_readme_lists_all_conventions),
    ("C12", "phase06 sequence diagram clause", check_phase06_sequence_diagram),
    ("C13", "phase08 sh+bat script clause", check_phase08_script_clause),
    ("C14", "quality-gate frontmatter fail rule", check_quality_gate_frontmatter),
    ("C15", "regression-analyst competition mention", check_regression_competition),
    ("C16", "competition trigger subjects", check_competition_triggers),
    ("C17", "writer agents call fingerprint", check_writer_agents_fingerprint),
    ("C18", "webview-builder mermaid render", check_webview_mermaid),
    ("C19", "autonomy convention present + cross-referenced", check_autonomy_convention_present),
    ("C20", "lessons + stagnation wired into phase10/implementer/planner", check_lessons_stagnation_wired),
    ("C21", "spec-catalog wired into intent-extractor/clarifier/phase09/template", check_spec_catalog_wired),
    ("C22", "resources + ceiling wired into phase04/phase10/spec-catalog", check_resources_ceiling_wired),
    ("C23", "no user interrupt in phases 05-13 (autonomy.md interview-only rule)", check_no_user_interrupt_post_phase04),
    ("C24", "checkpoints + dacapo + Q-D7 wired", check_checkpoints_wired),
    ("C25", "test-invariants + dacapo present (AIDE/Phase V)", check_test_invariants_present),
    ("C26", "fragmentation policy enforced (SKILL.md is index, not heavy)", check_fragmentation_policy),
    ("C27", "grades wired (grades.md + grade_assess.py + SKILL call table + phase04 Q-G1)", check_grades_wired),
    ("C-GS", "grade scope (no entry/reject gate, internal modulation only) — v0.5.0", check_grade_scope_no_gate),
    ("C28", "8 decomposition stubs + single source of truth + orchestrator chains all", check_decomposition_stubs),
    ("C29", "sub-agents recursion (sub-agents.md + dispatch + input contract matrix + AIDE ops)", check_sub_agents_wired),
    ("C30", "indexing wired (indexing.md + index_builder + non-serial frontmatter meta)", check_indexing_wired),
    ("C31", "resume wired (resume.md + resume.py + state.json + Progress tab + /api/state)", check_resume_wired),
    ("C32", "no rule duplication across conventions (fragmentation DRY)", check_no_rule_duplication),
    ("C33", "PRD handling hurdle (no interview skip even with full PRD)", check_prd_handling_wired),
    ("C34", "rewrite trigger generalized to all deep quality violations (multi-dimensional, not DIP-only)", check_rewrite_trigger_multidimensional),
    ("C35", "subprocess/tempfile encoding explicit (Windows cp949 latent-bug guard, v0.2.2)", check_subprocess_encoding_explicit),
    ("C36", "Q-D8 Verification Commands wired (oh-my-ralph latch, v0.3.0)", check_qd8_verification_commands_wired),
    ("C37", "decomposed stub standalone honesty (동반 필요 명시, v0.4.0)", check_decomposed_standalone_honesty),
    ("C38", "INSTALL.md fresh-user prep + self-check stack-only mode (PR-2, v0.4.0)", check_install_fresh_user_section),
    ("C39", "resources opt-in supplementary ceiling + Q-D3 sub-option (PR-3, v0.4.0)", check_resources_supplementary_ceiling),
    ("C40", "anti-patterns consolidation catalog (PR-11, v0.4.0)", check_anti_patterns_consolidation),
    ("C41", "description compressed (≤200) + anti-pattern preserved (PR-12, v0.4.0)", check_description_length_and_anti_pattern),
    ("C42", "interview ← prd-handling consolidation + no dead links (PR-13, v0.4.0)", check_convention_consolidation_prd),
    ("C43", "SKILL.md hard-rule markup (PR-10, v0.4.0)", check_hard_rule_markup),
    ("C-PT", "plan-tree wiring (5 seeds + G3+ default + grades matrix + outputs, v0.6.0)", check_plan_tree_wired),
    ("C-RP", "runtime-prereq + Q-D9 + 게이트 7 wiring (RP1~RP4, v0.7.0)", check_runtime_prereq_wired),
    ("C-OD", "orchestrator driver HARD-RULE (livetest #1 fail 정정, v0.8.0)", check_orchestrator_driver_hardrule),
    ("C-LINT1", "build-and-config ruff integration (sprint-05-a A)", check_build_config_ruff_integration),
    ("C-WV1", "phase12 theseus-view naming (sprint-05-a C)", check_phase12_theseus_view_naming),
    ("C-WV2", "phase13 interactive-viewer present + body keywords (sprint-05-a C)", check_phase13_interactive_viewer_present),
    ("C-WV3", "phase14 handoff renamed from 13 (sprint-05-a C)", check_phase14_handoff_renamed),
    ("C-AGENT-IVB", "interactive-viewer-builder agent present (sprint-05-a C)", check_interactive_viewer_builder_agent),
    ("C-TDD-08", "phase08 5 sub-phases + RED-GREEN-REFACTOR + universe trigger (sprint-05-a TDD)", check_phase08_tdd_subphases),
    ("C-MV1", "grades multiverse 폭 확장 G3 폭3 / G4 폭4 / G5 폭6 (sprint-05-b)", check_grades_multiverse_width_expanded),
    ("C-MV2", "phase08 universe 별 5 서브페이즈 head-to-head (sprint-05-b)", check_phase08_universe_head_to_head),
    ("C-MV3", "plan-tree 분기 축 카탈로그 ≥6 axis (sprint-05-b)", check_plan_tree_axis_catalog),
    ("C-MV4", "competition 자동 머지 알고리즘 + 차원별 sub-score (sprint-05-b)", check_competition_auto_merge_algorithm),
    ("C-MV5", "resources universe N 병렬 budget profile (sprint-05-b)", check_resources_multiverse_budget),
    ("C-IV1", "phase13 interactive-viewer 결과 프로덕트 only + 하네스 메타 emit 금지 (sprint-05-d)", check_phase13_product_only),
    ("C-IV2", "interactive-viewer-builder agent 책임 좁힘 결과 only (sprint-05-d)", check_interactive_viewer_agent_product_only),
    ("C-RB1", "phase11 회귀 원인 4 분류 plan/impl/data/external defect (sprint-05-e Q1)", check_phase11_regression_classification),
    ("C-IG1", "phase06 implementation guidance 본문 의무 (sprint-05-e Q3)", check_phase06_implementation_guidance),
    ("C-CT", "convention-traceability.md (v0.9.16 sprint-10 #1 발현 검증)", check_convention_traceability),
    ("C-SDT", "sprint-score-delta-tracking.md + budget-saturation cross-ref (v0.9.16 sprint-10 #2)", check_sprint_score_delta_tracking),
    ("C-EDP", "evidence-driven-sprint-planning.md + SRO/BSL cross-ref (v0.9.16 sprint-10 #3)", check_evidence_driven_sprint_planning),
    ("C-CULD", "cross-universe-lesson-distillation.md + plan-tree/ensemble cross-ref (v0.9.16 sprint-10 #4)", check_cross_universe_lesson_distillation),
    ("C-RDLR", "regression-derived-lint-rule-autogen.md + phase 11 cross-ref (v0.9.16 sprint-10 #5)", check_regression_derived_lint_rule_autogen),
    ("C-PCQ", "polyglot-code-quality.md + 9 언어 카탈로그 + 6 메트릭 (v0.9.16 sprint-10 #6)", check_polyglot_code_quality),
    ("C-GAv2", "grade_assess v2 — 키워드 매칭 폐기 + default G4 + 다중 신호 (v0.9.17 sprint-11)", check_grade_assess_v2),
    ("C-DCL-GATE", "dacapo-enforcement.md — phase 06/08 핸드오프 6 조건 의무 게이트 (bm, v0.9.22 sprint-16)", check_dacapo_enforcement),
    ("C-DCL-FRONTMATTER", "dacapo-frontmatter-schema.md — tournament/shadow-grade/dacapo-rerun 의무 필드 (bn, v0.9.22)", check_dacapo_frontmatter_schema),
    ("C-DCL-SHADOW-CONTEXT", "shadow-grader-zero-context.md — Step C 무결성 5 룰 (bo, v0.9.22)", check_shadow_grader_zero_context),
    ("C-DCL-SENTINEL", "dacapo-skip-sentinel.md — 3 sentinel 자동 회귀 + 로그 패턴 (bp, v0.9.22)", check_dacapo_skip_sentinel),
    ("C-DCL-FLOW-LOG", "dacapo-flow-trace.md — 단일 마크다운 가시화 누적 갱신 (bq, v0.9.22)", check_dacapo_flow_trace),
    ("C-PLV", "phase-lineage-viewer.md — 프로젝트 전체 phase 00~14 lineage 단일 마크다운 가시화 (br, v0.9.22)", check_phase_lineage_viewer),
    ("C-DMC", "domain-model-completeness.md — Conceptual modelling 5 차원 (entity/state/transition/invariant/boundary) (bs, v0.9.22)", check_domain_model_completeness),
    ("C-DSI", "data-structure-invariants.md — Invariants/Topology/Access/Bounds 4 항목 (bt, v0.9.22)", check_data_structure_invariants_conv),
    ("C-SPI", "simulation-physical-invariants.md — 5 invariant 런타임 assert (bu, v0.9.22)", check_simulation_physical_invariants),
    ("C-ECP", "experimental-control-protocol.md — IV/DV/CV/N/seed 5 항목 + N≥30 (bv, v0.9.22)", check_experimental_control_protocol),
    ("C-RDM", "results-decision-mapping.md — 결과 → 결정 1:1 매핑 (bw, v0.9.22)", check_results_decision_mapping),
    ("C-ICQ", "idiomatic-code-quality.md — naming/preferred/stdlib/readability 4 차원 (bx, v0.9.22)", check_idiomatic_code_quality),
    ("C-DCL-NO-FORWARD-PROJECT", "dacapo-enforcement.md sprint-17 — forward time projection 차단", check_dacapo_no_forward_projection),
    ("C-DCL-MIN-LOOP-ATTEMPT", "dacapo-enforcement.md sprint-17 — rerun ≥ 1 최소 loop attempt", check_dacapo_min_loop_attempt),
    ("C-DIAG-AND-COVERAGE", "diagrams.md sprint-17 — HARD-RULE 9.a OR → AND (sequence + usecase + interface 셋 다)", check_diagrams_and_coverage),
    ("C-IRPI", "intent-refresh-post-interview.md (by, sprint-17) — phase 04 → 05 refresh 4 framing universe + 01-additional", check_intent_refresh_post_interview),
    ("C-RNFS", "readme-numbers-from-summary.md (bz, sprint-18) — doc 숫자 vs measurement artifact ±0.01% 일치", check_readme_numbers_from_summary),
    ("C-RDC", "reproducibility-doublecheck.md (ca, sprint-18) — entry script 2회 실행 sha256 byte-equal", check_reproducibility_doublecheck),
    ("C-MNT", "magic-number-traceability.md (cb, sprint-18) — code literal → A_i 또는 데이터 출처 1:1 매핑", check_magic_number_traceability),
    ("C-DCZ", "dead-code-zero.md (cc, sprint-18) — 언어별 dead-code analyzer 위반 0", check_dead_code_zero),
    ("C-SPB", "submission-portability.md (cd, sprint-18) — entry script --data-dir CLI + DATA_DIR env var fallback", check_submission_portability),
    ("C-DCMR", "dacapo-mandatory-rerun.md (ce, sprint-19) — winner ≥ 임계 도달해도 무조건 ≥ 1 rerun (polishing pass 강제)", check_dacapo_mandatory_rerun),
    ("C-PTSS", "plan-tournament-scoring-strict.md (cf, sprint-19) — tournament 6-dim weighted 의무, 1-5 coarse reject", check_plan_tournament_scoring_strict),
    ("C-CNS", "canonical-not-stub.md (cg, sprint-19) — canonical ≥ winner 80% inline 또는 shared schema mode", check_canonical_not_stub),
    ("C-IMS", "impl-multiverse-strict.md (ch, sprint-19) — phase 08 G4+ multiverse + tournament + 5 sub-phase TDD 7 조건 게이트", check_impl_multiverse_strict),
    ("C-IRPC", "intent-refresh-post-critique.md (ci, sprint-19) — phase 05 후 2nd intent refresh + 04/05 cascade", check_intent_refresh_post_critique),
    ("C-CPSC", "cross-phase-shared-context.md (cj, sprint-19) — shared 정보 단일 위치 + asof_fingerprint 인용 의무", check_cross_phase_shared_context),
    ("C-HC1", "HARD-CORE.md (sprint-20 v0.9.25) — always-load 본문 ≤ 4000 chars + 의무 키워드 (HR1/HR8/HR9/Layer 3/fingerprint)", check_hard_core_size),
    ("C-IDX-1", "conventions/INDEX.md (sprint-20 v0.9.25) — 88 컨벤션 router 단일 진실 원천 + 1:1 매칭", check_conventions_index_completeness),
    ("C-IDX-2", "conventions/*.md frontmatter (sprint-27 v0.9.32) — router metadata backfill + INDEX drift detection", check_conventions_frontmatter_drift),
    ("C-DCL-FRESH-UNIVERSE", "intra-phase-dacapo-loop.md (sprint-28) — Round N+1 = NEW fresh universes (NOT survivors rerun, NOT 재라벨링)", check_dacapo_fresh_universe),
    ("C-IMS-SEMANTICS", "impl-multiverse-strict.md (sprint-29) — impl multiverse = plan winner 코드 구현 변형 (NOT plan multiverse 손자)", check_impl_multiverse_semantics),
    ("C-CMJ", "conservative-margin-judging.md (sprint-30) — 모든 internal judge 보수적 prior + 0.999 마진 보존 + 무한 회귀 동력", check_conservative_margin_judging),
]


def run(repo_root: Path) -> dict:
    skill_root = repo_root / "skills" / "theseus-harness"
    results: list[dict] = []
    for code, name, fn in CHECKS:
        sig = fn.__code__.co_argcount
        if sig == 2:
            issues = fn(repo_root, skill_root)
        else:
            issues = fn(skill_root)
        results.append(
            {"code": code, "name": name, "ok": not issues, "issues": issues}
        )
    return {
        "all_ok": all(r["ok"] for r in results),
        "checks": results,
    }


def compute_self_score(repo_root: Path) -> dict:
    """
    자기 평가 점수 계산 — 본 하네스가 자기 자신에게 강제하는 점수.

    임계 0.99999 (사용자 프로젝트 임계 0.999 보다 한 단계 빡빡 — "내가 강제하는 모든
    것을 내가 100% 통과한다" 는 자기 표준).

    계산:
      lint_score   = lint_pass_count / lint_total_count
      pytest_score = pytest_pass_count / pytest_total_count
      sample_score = score.py 의 sample-inputs 채점 결과 (0..1)

      self_score = w_lint × lint_score + w_pytest × pytest_score + w_sample × sample_score
                   (w_lint=0.40, w_pytest=0.40, w_sample=0.20)

    pytest 와 sample 채점은 subprocess 로 실행 — score.py / test_score.py 가 단순한
    경로에 있다는 가정.
    """
    import subprocess

    skill_root = repo_root / "skills" / "theseus-harness"

    lint = run(repo_root)
    lint_total = len(lint["checks"])
    lint_pass = sum(1 for c in lint["checks"] if c["ok"])
    lint_score = lint_pass / lint_total if lint_total else 1.0

    pytest_proc = subprocess.run(
        # test_self_lint.py 를 포함하면 자기 안에서 self_lint --score 를 다시 호출
        # → 무한 재귀. 점수 계산용 pytest 는 test_score.py 만.
        [sys.executable, "-m", "pytest", str(skill_root / "scoring" / "test_score.py"), "-q", "--tb=no"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(skill_root),
    )
    pytest_pass_count = pytest_total_count = 0
    for line in pytest_proc.stdout.splitlines():
        m = re.search(r"(\d+) passed", line)
        if m:
            pytest_pass_count = int(m.group(1))
        m2 = re.search(r"(\d+) failed", line)
        if m2:
            pytest_total_count += int(m2.group(1))
    pytest_total_count += pytest_pass_count
    pytest_score = (
        pytest_pass_count / pytest_total_count if pytest_total_count else 1.0
    )

    sample_path = skill_root / "templates" / "sample-inputs.json"
    score_py = skill_root / "scoring" / "score.py"
    sample_proc = subprocess.run(
        [
            sys.executable,
            str(score_py),
            "--inputs",
            str(sample_path),
            "--threshold",
            "0.0",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    try:
        sample_score = json.loads(sample_proc.stdout)["score"]
    except Exception:
        sample_score = 0.0

    w_lint, w_pytest, w_sample = 0.40, 0.40, 0.20
    self_score = w_lint * lint_score + w_pytest * pytest_score + w_sample * sample_score
    return {
        "self_score": round(self_score, 6),
        "lint_score": round(lint_score, 6),
        "lint_pass": lint_pass,
        "lint_total": lint_total,
        "pytest_score": round(pytest_score, 6),
        "pytest_pass": pytest_pass_count,
        "pytest_total": pytest_total_count,
        "sample_score": round(sample_score, 6),
        "passes_threshold_99999": self_score >= 0.99999,
        "lint_failures": [c for c in lint["checks"] if not c["ok"]],
    }


def main(argv: Iterable[str] | None = None) -> int:
    # 본 스크립트가 직접 실행될 때 stdout 이 OS 로케일(cp949) 로 떨어지면 한국어
    # issue 메시지의 em-dash 같은 문자에서 UnicodeEncodeError 가 발생한다 — C35
    # 가 잡으려는 회귀와 같은 부류. 자기 출력도 같은 가드로.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[3]),
        help="저장소 루트 (기본: 본 스크립트 위치 기준)",
    )
    p.add_argument(
        "--score",
        action="store_true",
        help="lint + pytest + sample 가중 평균으로 자기 평가 점수 산출 (임계 0.99999)",
    )
    args = p.parse_args(list(argv) if argv is not None else None)
    if args.score:
        out = compute_self_score(Path(args.repo_root))
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0 if out["passes_threshold_99999"] else 1
    out = run(Path(args.repo_root))
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
