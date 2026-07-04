"""Artifact 파서 — 실행 산물(junit/coverage XML)에서 원시 수치만 뽑는다 (설계 §5).

책임 하나: *디스크의 artifact 를 파싱해 원시 count/rate 를 반환*. 이 모듈은 verdict·
score·evidence 를 만들지 않는다 — 그건 measure_submission(assembler)의 몫이다.
표준 라이브러리만 쓴다(xml.etree). LLM 이 상상한 숫자는 여기 들어올 수 없다 —
입력이 파일 경로뿐이고 반환은 그 파일에서 실제로 읽은 값이기 때문.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


class ArtifactParseError(ValueError):
    """artifact 부재·형식오류 — measure_submission 이 이를 잡아 해당 값을 결손 처리."""


@dataclass(frozen=True)
class JUnitCounts:
    """junit 한 파일에서 관측한 원시 카운트. passed 는 파생이 아니라 정의된 잔차:
    total - failed - skipped (failed = failures + errors)."""

    total: int
    passed: int
    failed: int
    skipped: int


def _suite_counts(suite: ET.Element) -> tuple[int, int, int, int]:
    """단일 <testsuite>(또는 aggregate <testsuites>)에서 (total, failures, errors, skipped).

    집계 속성(tests/failures/errors/skipped)이 있으면 그것을 신뢰하고, 없으면
    <testcase> 를 직접 세어 <failure>/<error>/<skipped> 자식으로 분류한다(속성 없는
    러너 호환).
    """
    if suite.get("tests") is not None:
        total = int(suite.get("tests", 0))
        failures = int(suite.get("failures", 0))
        errors = int(suite.get("errors", 0))
        # 러너에 따라 skipped/skip 표기가 갈린다.
        skipped = int(suite.get("skipped", suite.get("skip", 0)) or 0)
        return total, failures, errors, skipped

    total = failures = errors = skipped = 0
    for tc in suite.findall("testcase"):
        total += 1
        if tc.find("failure") is not None:
            failures += 1
        elif tc.find("error") is not None:
            errors += 1
        elif tc.find("skipped") is not None:
            skipped += 1
    return total, failures, errors, skipped


def parse_junit(path: str | Path) -> JUnitCounts:
    """junit XML → JUnitCounts. 부재/파싱불가/구조 미인식 시 ArtifactParseError.

    root 가 <testsuites> aggregate 면 그 하나만, 아니면 자식 <testsuite> 들을 합산한다
    — aggregate 와 개별 suite 를 이중 계산하지 않도록.
    """
    p = Path(path)
    if not p.exists():
        raise ArtifactParseError(f"junit artifact not found: {p}")
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError as exc:
        raise ArtifactParseError(f"junit not parseable XML: {p}: {exc}") from exc

    if root.tag == "testsuite":
        suites = [root]
    elif root.tag == "testsuites":
        # aggregate 속성이 있으면 root 하나만, 없으면 자식 suite 합산.
        suites = [root] if root.get("tests") is not None else root.findall("testsuite")
    else:
        found = root.findall(".//testsuite")
        suites = found if found else [root]

    total = failures = errors = skipped = 0
    for s in suites:
        t, f, e, sk = _suite_counts(s)
        total += t
        failures += f
        errors += e
        skipped += sk

    failed = failures + errors
    passed = total - failed - skipped
    return JUnitCounts(total=total, passed=passed, failed=failed, skipped=skipped)


def parse_coverage(path: str | Path) -> float:
    """Cobertura coverage XML → 분기 커버리지 rate([0,1]). branch-rate 우선, 없으면
    line-rate. 부재/파싱불가/rate 부재 시 ArtifactParseError.

    rubric.md 는 '분기 커버리지'를 본다 — Cobertura root 의 branch-rate 가 그것.
    """
    p = Path(path)
    if not p.exists():
        raise ArtifactParseError(f"coverage artifact not found: {p}")
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError as exc:
        raise ArtifactParseError(f"coverage not parseable XML: {p}: {exc}") from exc

    for attr in ("branch-rate", "line-rate"):
        raw = root.get(attr)
        if raw is not None:
            try:
                rate = float(raw)
            except ValueError as exc:
                raise ArtifactParseError(
                    f"coverage {attr} not a number: {raw!r} in {p}"
                ) from exc
            return rate
    raise ArtifactParseError(f"coverage has neither branch-rate nor line-rate: {p}")
