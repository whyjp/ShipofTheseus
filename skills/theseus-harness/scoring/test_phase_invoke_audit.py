"""Smoke test for phase_invoke_audit.py — sprint-43 PR-C."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase_invoke_audit import extract_declared_clis, check_invocation_trace, evaluate, main


ORCH_SAMPLE_FULL_DECLARED = """# theseus-orchestrator

## HARD-RULE 9.qq

\\`\\`\\`bash
python skills/theseus-harness/scoring/dacapo_threshold.py --tournament-md ...
\\`\\`\\`

## HARD-RULE 9.tt

\\`\\`\\`bash
python skills/theseus-harness/scoring/runtime_guard_chain.py ...
\\`\\`\\`
"""


class TestExtractDeclared(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_extracts_clis_from_orchestrator(self):
        p = self.root / 'orch.md'
        p.write_text(ORCH_SAMPLE_FULL_DECLARED, encoding='utf-8')
        info = extract_declared_clis(p)
        self.assertTrue(info['present'])
        self.assertEqual(
            sorted(info['declared_clis']),
            sorted(['dacapo_threshold', 'runtime_guard_chain']),
        )

    def test_orchestrator_missing(self):
        info = extract_declared_clis(self.root / 'nonexistent.md')
        self.assertFalse(info['present'])


class TestCheckInvocationTrace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_runtime_guard_chain_invoked(self):
        p = self.root / 'quality' / 'gate_runtime_guard_chain.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({'verdict': 'pass', 'evaluated_at': '2026-05-10T10:00:00Z'}), encoding='utf-8')
        result = check_invocation_trace(self.root, 'runtime_guard_chain')
        self.assertTrue(result['invoked'])

    def test_not_invoked(self):
        result = check_invocation_trace(self.root, 'runtime_guard_chain')
        self.assertFalse(result['invoked'])

    def test_stagnation_breakthrough_glob(self):
        # glob 브랜치 (sprints/*/...) 커버리지 — CLI_TRACE_PATHS 의 glob-매핑 CLI 로 검증.
        p = self.root / 'sprints' / '03' / 'gate_stagnation_breakthrough.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({'verdict': 'pass', 'evaluated_at': '2026-05-10T10:00:00Z'}), encoding='utf-8')
        result = check_invocation_trace(self.root, 'stagnation_breakthrough')
        self.assertTrue(result['invoked'])


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.orch = self.root / 'orch.md'
        self.proj = self.root / 'proj'
        self.proj.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_g4v2_pattern_declared_none_invoked(self):
        """g4-v2 회피 패턴 — declared CLI 전부 0 trace."""
        self.orch.write_text(ORCH_SAMPLE_FULL_DECLARED, encoding='utf-8')
        verdict = evaluate(self.orch, self.proj)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(len(verdict['not_invoked']), 2)

    def test_all_invoked_passes(self):
        self.orch.write_text(ORCH_SAMPLE_FULL_DECLARED, encoding='utf-8')
        # 2 CLI 의 trace 모두 박음
        traces = [
            ('plan/dacapo_threshold.json', {'verdict': 'pass'}),
            ('quality/gate_runtime_guard_chain.json', {'verdict': 'pass'}),
        ]
        for rel, content in traces:
            p = self.proj / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(content), encoding='utf-8')

        verdict = evaluate(self.orch, self.proj)
        self.assertEqual(verdict['verdict'], 'pass', msg=json.dumps(verdict, indent=2))


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_not_invoked(self):
        orch = self.root / 'orch.md'
        orch.write_text(ORCH_SAMPLE_FULL_DECLARED, encoding='utf-8')
        proj = self.root / 'proj'
        proj.mkdir()
        rc = main([
            '--orchestrator-skill', str(orch),
            '--project-root', str(proj),
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
