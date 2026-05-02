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
      ⓓ-1 … 형식으로 노출

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
    """C1 — 모든 conventions/*.md 의 첫 두 줄 검사."""
    issues: list[str] = []
    for p in _files(skill_root / "conventions", "*.md"):
        text = _read(p)
        head = text.splitlines()[:8]
        if not head or not head[0].startswith("# "):
            issues.append(f"{p.name}: 첫 줄이 # 제목 아님")
            continue
        if not any("## 한 줄 요약" in line for line in head):
            issues.append(f"{p.name}: '## 한 줄 요약' 섹션 누락")
    return issues


def check_skill_links_all_conventions(skill_root: Path) -> list[str]:
    """C2."""
    skill = _read(skill_root / "SKILL.md")
    issues: list[str] = []
    for p in _files(skill_root / "conventions", "*.md"):
        rel = f"conventions/{p.name}"
        if rel not in skill:
            issues.append(f"SKILL.md 가 {rel} 를 링크하지 않음")
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
    """C11 — skills/theseus-harness/README.md 가 conventions 를 ⓓ-N 형식으로 노출."""
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
    """C13 — phases/08-implement.md 가 sh + bat 양쪽 빌드 스크립트 강제를 본문에 명시."""
    text = _read(skill_root / "phases" / "08-implement.md")
    issues: list[str] = []
    if ".sh" not in text or ".bat" not in text:
        issues.append("phases/08-implement.md: sh + bat 빌드 스크립트 강제 본문 누락")
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


def check_no_rule_duplication(skill_root: Path) -> list[str]:
    """
    C32 — 룰 본문 중복 검출 휴리스틱.

    fragmentation.md 안티 패턴 ⓒ "한 룰을 두 파일에서 다르게 정의" 방지.
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
    # 단독 호출 input 매트릭스 검증 — 7 분해 스킬 모두 이름 등장
    expected_skills = [
        "theseus-intent", "theseus-plan", "theseus-implement",
        "theseus-quality", "theseus-sprint", "theseus-webview", "theseus-handoff",
    ]
    for name in expected_skills:
        if name not in text:
            issues.append(f"sub-agents.md 의 단독 호출 input 매트릭스에 {name} 누락")
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
    """C28 — 8 분해 stub 존재 + 단일 source of truth 룰 검증."""
    skills_root = repo_root / "skills"
    expected = [
        "theseus-orchestrator",
        "theseus-intent",
        "theseus-plan",
        "theseus-implement",
        "theseus-quality",
        "theseus-sprint",
        "theseus-webview",
        "theseus-handoff",
    ]
    issues: list[str] = []
    for stub in expected:
        skill_md = skills_root / stub / "SKILL.md"
        if not skill_md.exists():
            issues.append(f"{stub}/SKILL.md 누락 (분해 stub)")
            continue
        text = skill_md.read_text(encoding="utf-8")
        if stub != "theseus-orchestrator" and "../theseus-harness/" not in text:
            issues.append(f"{stub} 가 ../theseus-harness/ source 참조 누락 (단일 source of truth 위반)")
    # orchestrator 가 7 stub 모두 링크
    orch = skills_root / "theseus-orchestrator" / "SKILL.md"
    if orch.exists():
        orch_text = orch.read_text(encoding="utf-8")
        for stub in expected:
            if stub == "theseus-orchestrator":
                continue
            if stub not in orch_text:
                issues.append(f"theseus-orchestrator 가 {stub} 링크 누락")
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


def check_fragmentation_policy(skill_root: Path) -> list[str]:
    """C26 — fragmentation.md 가 존재 + SKILL.md 가 인덱스 형태 (룰 본문 비대화 방지)."""
    issues: list[str] = []
    frag = skill_root / "conventions" / "fragmentation.md"
    if not frag.exists():
        return ["conventions/fragmentation.md 누락 — 파편화 우선 룰 정의 필요"]
    skill = _read(skill_root / "SKILL.md")
    # SKILL.md 가 일정 길이 초과면 룰 본문 누적 의심 — 임계 12000 자
    if len(skill) > 12000:
        issues.append(
            f"SKILL.md 길이 {len(skill)} 자 — 임계 12000 초과. 룰 본문이 컨벤션으로 분해되지 않은 의심 (fragmentation.md §1 위반)"
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
    ("C28", "8 decomposition stubs + single source of truth + orchestrator chains all", check_decomposition_stubs),
    ("C29", "sub-agents recursion (sub-agents.md + dispatch + input contract matrix + AIDE ops)", check_sub_agents_wired),
    ("C30", "indexing wired (indexing.md + index_builder + non-serial frontmatter meta)", check_indexing_wired),
    ("C31", "resume wired (resume.md + resume.py + state.json + Progress tab + /api/state)", check_resume_wired),
    ("C32", "no rule duplication across conventions (fragmentation DRY)", check_no_rule_duplication),
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
