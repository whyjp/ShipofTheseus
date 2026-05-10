"""Smoke test for stagnation_breakthrough.py — sprint-42 PR-D."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stagnation_breakthrough import evaluate, main


# 0510-2 회피 패턴 — sprint-03 report.json 직접 인용
REPORT_0510_2 = {
    "sprint": 3,
    "phase": "10-test-loop",
    "fingerprint": "ph10-sprint03-report",
    "score": 0.97,
    "delta": 0.0,
    "stagnation_threshold": 0.001,
    "stagnation_detected": True,
    "decision": "exit_sprint_loop_per_DEC-autonomy",
    "lessons_outbound": [
        "trinity score plateaued at 0.97; further sprints would only fine-tune narrative",
        "0.97 < 0.999 G4 asymptote; defer to opus-reviewer scoring as final ground truth",
    ],
}

REPORT_NO_STAGNATION = {
    "sprint": 3,
    "score": 0.95,
    "stagnation_detected": False,
    "decision": "continue",
}

REPORT_HIGH_SCORE = {
    "sprint": 3,
    "score": 0.9995,
    "stagnation_detected": True,
    "decision": "stop_threshold_reached",
}


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_report(self, iteration: int, content: dict) -> None:
        p = self.root / 'sprints' / str(iteration).zfill(2) / 'report.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(content), encoding='utf-8')

    def _write_attempt(self, content: str) -> None:
        p = self.root / 'plan' / 'tournament-03.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

    def test_0510_2_pattern_blocks(self):
        """0510-2 회피 패턴 — stagnation + 0.97 + 0 시도 → fail."""
        self._write_report(3, REPORT_0510_2)
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(verdict['breakthrough_attempts']['attempt_count'], 0)

    def test_no_stagnation_passes(self):
        self._write_report(3, REPORT_NO_STAGNATION)
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'pass')

    def test_high_score_overrides_stagnation(self):
        """score ≥ threshold 시 stagnation 무관 stop OK."""
        self._write_report(3, REPORT_HIGH_SCORE)
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'pass')

    def test_stagnation_with_new_universe_attempt(self):
        self._write_report(3, REPORT_0510_2)
        self._write_attempt(
            '# Plan tournament 03\nspawned new universe-4 to break stagnation.\n'
        )
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertIn('new_universe', verdict['breakthrough_attempts']['attempt_kinds_present'])

    def test_stagnation_with_ensemble_attempt(self):
        self._write_report(3, REPORT_0510_2)
        self._write_attempt(
            '# Plan\nApplied ensemble synthesis from universes-1 and 2.\n'
        )
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertIn('ensemble_synthesis', verdict['breakthrough_attempts']['attempt_kinds_present'])

    def test_stagnation_with_lateral_think(self):
        self._write_report(3, REPORT_0510_2)
        self._write_attempt(
            '# lateral thinking — alternative hypothesis applied to break asymptote\n'
        )
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'pass')

    def test_no_report_skips(self):
        verdict = evaluate(self.root, current_iteration=3)
        self.assertEqual(verdict['verdict'], 'pass')


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_block(self):
        p = self.root / 'sprints' / '03' / 'report.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(REPORT_0510_2), encoding='utf-8')
        rc = main([
            '--project-root', str(self.root),
            '--current-iteration', '3',
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
