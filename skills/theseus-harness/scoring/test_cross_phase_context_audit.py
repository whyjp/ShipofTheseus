"""Smoke test for cross_phase_context_audit.py — sprint-42 PR-B."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cross_phase_context_audit import (
    count_references,
    evaluate_phase,
    evaluate,
    main,
)


class TestCountReferences(unittest.TestCase):
    def test_phase_label_match(self):
        text = "References phase 04 answers in Q-D3 ..."
        c = count_references(text, 4)
        self.assertGreaterEqual(c.get('phase_label', 0), 1)

    def test_decision_id_for_phase_4(self):
        text = "Per Q-D3.1 and Q-D5 the dispatch policy is..."
        c = count_references(text, 4)
        self.assertGreaterEqual(c.get('Q-D', 0), 2)

    def test_intent_path_match(self):
        text = "see intent/04-answers.md for context"
        c = count_references(text, 4)
        self.assertGreaterEqual(c.get('intent_path', 0), 1)

    def test_no_false_positive(self):
        text = "phase 09 only mentions phase 09 itself"
        c = count_references(text, 4)
        self.assertEqual(sum(c.values()), 0)


class TestEvaluatePhase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, rel: str, content: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

    def test_0510_2_regression_pattern_phase_8_fails(self):
        """0510-2 회피 패턴 — phase 08 본문에 phase 02/04/05 인용 0."""
        self._write('intent/01-intent.md', '# intent')
        self._write('intent/04-answers.md', 'Q-D3 = lognormal')
        self._write('intent/05-critique.md', 'C1.1 ...')
        self._write('plan/06-plan.md', 'plan body')
        self._write(
            'impl/tournament-impl-01.md',
            '''---
phase: 08-impl-tournament-01
---
# Implementation Tournament 01 — verdict
Single-universe implementation. 7-condition assessed.
| 1. >= 2 plan universes scored | yes (3 universes) |
Verdict: implement universe-1 only; ship.
''',
        )
        # phase 08 본문 — phase 02/04/05 인용 0, immediate phase 7 인용 0
        result = evaluate_phase(self.root, '08', 1, 1)
        self.assertEqual(result['verdict'], 'fail')

    def test_passes_when_cited(self):
        self._write('intent/04-answers.md', 'Q-D3 = lognormal')
        self._write('plan/07-plan-review.md', '# review')
        self._write(
            'impl/08-impl-log.md',
            '''---
phase: 08-impl-log
---
# Impl log
Per Q-D3 (intent/04-answers.md) and phase 07 plan-review (plan/07-plan-review.md), we...
''',
        )
        result = evaluate_phase(self.root, '08', 1, 1)
        self.assertEqual(result['verdict'], 'pass')

    def test_skip_when_no_artefacts(self):
        result = evaluate_phase(self.root, '08', 1, 1)
        self.assertEqual(result['verdict'], 'skip')

    def test_phase_02_no_distant(self):
        """phase 02 — distant phases = [0, 1] only. phase 1 인용만 있어도 OK."""
        self._write('intent/01-intent.md', 'intent body')
        self._write(
            'intent/02-review.md',
            '''---
phase: 02-review
---
# Review
Building on phase 01 (intent/01-intent.md), the assumption ...
''',
        )
        result = evaluate_phase(self.root, '02', 1, 0)  # distant min 0 — phase 02 의 distant 는 phase 0 뿐
        self.assertEqual(result['verdict'], 'pass')


class TestEvaluateOverall(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_artefacts_skips_all_pass(self):
        verdict = evaluate(self.root, ['08', '09'], 1, 1)
        # 산출물 없음 → 모두 skip → fail_phases = []
        self.assertEqual(verdict['verdict'], 'pass')


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_fail(self):
        # phase 08 본문 인용 0 — fail
        p = self.root / 'impl' / 'tournament-impl-01.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            '---\nphase: 08-impl-tournament-01\n---\n# verdict\nimplement universe-1; ship.\n',
            encoding='utf-8',
        )
        rc = main([
            '--project-root', str(self.root),
            '--phase', '08',
            '--min-immediate', '1',
            '--min-distant', '1',
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
