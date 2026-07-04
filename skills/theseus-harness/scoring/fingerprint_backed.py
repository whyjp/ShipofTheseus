#!/usr/bin/env python3
"""backing-evidence 기반 fingerprint 검증 (설계 §10, WP7).

fingerprint 단독(자기 sha256)은 아무것도 보증하지 않는다 — 비밀 없는 자기 해시라
에이전트가 `fingerprint.py compute` 로 언제든 재서명할 수 있기 때문(감사 P4). 위조
차단을 hash 가 아니라 '이 페이즈 산출물 뒤에 통과한 Evidence Record가 있는가'로 옮긴다.

backed 판정의 핵심 조건:
  - frontmatter 의 fingerprint 가 self-hash 로 valid 하다는 것만으로는 backed=False.
    (self-hash 유효성은 진단으로만 기록하고 판정에 넣지 않는다 — §10.)
  - 산출물 frontmatter 의 phase(+있으면 project_run) 에 해당하는 Evidence Record 가
    evidence-dir 에 존재하고, 다음 중 하나로 뒷받침되어야 backed=True:
      * checks-dir 가 주어지고 매칭 CheckSpec 이 있으면 → 커널이 그 spec 으로 PASS.
      * (spec 부재) 최소 backing → produced_by=='run' & exit 0 & self_reported 아님 &
        evidence 의 artifact_digests 가 디스크 실파일 sha256 과 일치.
  - 뒷받침하는 evidence 가 하나도 없으면 backed=False (위조/미실행으로 간주).

커널(kernel.py / evidence.py / checkspec.py)은 import 만 하고 수정하지 않는다 —
판정 로직·파일 해시·정규화를 재사용한다(§11 순감: 새 검증기를 만들지 않는다).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# 이 모듈은 fingerprint.py 와 같은 scoring/ 에 있고, 커널 모듈은 scoring/kernel/ 하위다.
# 스크립트 실행(`python fingerprint_backed.py ...`)과 pytest(상위 conftest 가 kernel/
# 을 삽입) 양쪽에서 같은 최상위 모듈로 import 되도록 kernel 디렉터리를 sys.path 에
# 확실히 넣는다. fingerprint(base) 도 같은 scoring/ 에서 재사용한다.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_KERNEL_DIR = os.path.join(_THIS_DIR, "kernel")
for _d in (_KERNEL_DIR, _THIS_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import checkspec  # noqa: E402  (kernel/ 경로 확정 후 평면 import)
import evidence  # noqa: E402
import fingerprint  # noqa: E402  (frontmatter 파서 재사용)
import kernel  # noqa: E402


def _load_specs(checks_dir: str | None) -> dict:
    """checks-dir 의 CheckSpec 을 check_id 로 색인. CheckSpec 이 아닌 JSON 은 건너뛴다.

    레지스트리에 다른 JSON 이 섞여 있어도 우리는 CheckSpec 만 취한다 — 로드 실패는
    조용히 무시(그 evidence 는 최소 backing 경로로 떨어진다)."""
    specs: dict = {}
    if not checks_dir:
        return specs
    root = Path(checks_dir)
    if not root.exists():
        return specs
    for p in sorted(root.rglob("*.json")):
        try:
            spec = checkspec.load_checkspec(p)
        except checkspec.CheckSpecError:
            continue
        specs[spec.check_id] = spec
    return specs


def _candidate_evidence(evidence_dir: str, phase, project_run) -> list:
    """evidence-dir 에서 이 페이즈(+project_run 일치 시) 에 해당하는 Evidence Record 수집.

    파싱 불가/구조 결손 파일은 제외한다 — 부재·파싱불가는 '미실행'과 동급(§2 원칙2).
    반환: [(path, EvidenceRecord)] (경로 정렬로 결정성 확보)."""
    out: list = []
    root = Path(evidence_dir)
    if not root.exists():
        return out
    want_phase = str(phase).strip()
    want_run = str(project_run).strip() if project_run else ""
    for p in sorted(root.rglob("*.json")):
        ev = evidence.try_load_evidence(p)
        if ev is None:
            continue
        if str(ev.phase).strip() != want_phase:
            continue
        # project_run 은 양쪽 다 있을 때만 일치 강제 — 한쪽이 비면 phase 로만 매칭.
        if want_run and str(ev.project_run).strip() and str(ev.project_run).strip() != want_run:
            continue
        out.append((p, ev))
    return out


def _artifact_digests_match_disk(ev, artifact_root: str) -> list:
    """evidence 의 artifact_digests 가 디스크 실파일 sha256 과 일치하는가.

    커널 법칙3 의 artifact 대조와 같은 검사를 spec 없이 수행(최소 backing 바닥).
    반환: 불일치/부재 사유 목록(빈 목록 = 일치). artifact_digests 가 비면 '실행에
    묶일 artifact 자체가 없음' → backing 아님."""
    reasons: list = []
    if not ev.artifact_digests:
        reasons.append("evidence has no artifact_digests (no execution artifact to bind to)")
        return reasons
    root = Path(artifact_root)
    for rel_path, declared in ev.artifact_digests.items():
        disk = root / rel_path
        if not disk.exists():
            reasons.append(f"artifact missing on disk: {rel_path}")
            continue
        actual = evidence.sha256_of_file(disk)
        if actual != evidence.normalize_digest(declared):
            reasons.append(f"artifact digest mismatch: {rel_path}")
    return reasons


def _minimal_backing_gaps(ev, artifact_root: str) -> list:
    """CheckSpec 없이 최소 backing 성립 여부 — 커널 법칙2~3의 spec-무관 부분 재현.

    반환: 결손 사유 목록(빈 목록 = backing 성립)."""
    reasons: list = []
    if ev.produced_by != "run":
        reasons.append(f"produced_by must be 'run', got {ev.produced_by!r}")
    if ev.self_reported:
        reasons.append("self_reported=true (no whitelist without CheckSpec)")
    if ev.producer_exit_code != 0:
        reasons.append(f"producer_exit_code != 0 (got {ev.producer_exit_code})")
    reasons.extend(_artifact_digests_match_disk(ev, artifact_root))
    return reasons


def verify_backed(
    artifact_path: str,
    evidence_dir: str,
    checks_dir: str | None = None,
    artifact_root: str | None = None,
) -> dict:
    """페이즈 산출물이 통과한 Evidence Record 로 뒷받침되는지 판정.

    반환: {"file": str, "backed": bool, "reasons": [str, ...]}."""
    path = Path(artifact_path)
    reasons: list = []
    if not path.exists():
        return {"file": str(path), "backed": False, "reasons": [f"artifact not found: {path}"]}

    fm, _body = fingerprint.parse_frontmatter(path.read_text(encoding="utf-8"))
    phase = fm.get("phase")
    project_run = fm.get("project_run")
    fp = fm.get("fingerprint")

    # 진단: self-hash 유효성은 backed 판정에 넣지 않는다(§10 핵심). 정보로만 남긴다.
    if not fp:
        reasons.append("diagnostic: frontmatter fingerprint 없음")
    elif not str(fp).startswith("sha256:"):
        reasons.append(
            f"diagnostic: fingerprint 가 sha256 규격 아님 (사람이 쓴 슬러그 = 미실행 물증?): {fp!r}"
        )

    if not phase:
        reasons.append("frontmatter phase 없음 — backing evidence 를 특정할 수 없음")
        return {"file": str(path), "backed": False, "reasons": reasons}

    art_root = artifact_root if artifact_root is not None else evidence_dir
    specs = _load_specs(checks_dir)
    candidates = _candidate_evidence(evidence_dir, phase, project_run)

    if not candidates:
        reasons.append(
            f"phase {phase} 에 해당하는 Evidence Record 없음 (backing 부재 → 위조/미실행)"
        )
        return {"file": str(path), "backed": False, "reasons": reasons}

    backed = False
    for ev_path, ev in candidates:
        spec = specs.get(ev.check_id)
        if spec is not None:
            verdict = kernel.verify(spec, ev, artifact_root=art_root)
            if verdict.result == kernel.PASS:
                backed = True
                reasons.append(f"backed by {ev.check_id} (kernel PASS, {ev_path.name})")
                break
            reasons.append(f"{ev.check_id}: kernel FAIL — {'; '.join(verdict.reasons)}")
        else:
            gaps = _minimal_backing_gaps(ev, art_root)
            if not gaps:
                backed = True
                note = "no CheckSpec; artifact digests match disk" if checks_dir else "artifact digests match disk"
                reasons.append(f"backed by {ev.check_id} ({note}, {ev_path.name})")
                break
            reasons.append(f"{ev.check_id}: {'; '.join(gaps)}")

    return {"file": str(path), "backed": backed, "reasons": reasons}


def run_verify_backed(args) -> int:
    """CLI 핸들러 — fingerprint.py 의 verify-backed 서브커맨드도 이 함수를 호출한다."""
    result = verify_backed(
        args.file,
        args.evidence_dir,
        checks_dir=getattr(args, "checks_dir", None),
        artifact_root=getattr(args, "artifact_root", None),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["backed"] else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="backing-evidence 기반 fingerprint 검증 (§10)")
    sub = p.add_subparsers(dest="cmd", required=True)
    vb = sub.add_parser("verify-backed")
    vb.add_argument("--file", required=True, help="페이즈 산출물 마크다운")
    vb.add_argument("--evidence-dir", required=True, help="run/evidence 디렉터리")
    vb.add_argument("--checks-dir", default=None, help="CheckSpec 레지스트리 (있으면 커널 판정)")
    vb.add_argument(
        "--artifact-root", default=None, help="artifact 상대경로 해석 기준 (기본: evidence-dir)"
    )
    vb.set_defaults(func=run_verify_backed)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
