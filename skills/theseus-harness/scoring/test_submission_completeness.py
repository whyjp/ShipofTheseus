"""Smoke test for submission_completeness.py — sprint-43 PR-B."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from submission_completeness import evaluate, main


# g4-v2 회피 패턴 — eval 시 모든 output_exists_* pass, 그러나 disk 에 .pyc 만
EVAL_REPORT_FULL_PASS = {
    "automated_checks": {
        "passed": 57,
        "total": 57,
        "checks": [
            {"name": "output_exists_conceptual_model.md", "passed": True},
            {"name": "output_exists_README.md", "passed": True},
            {"name": "output_exists_results.csv", "passed": True},
            {"name": "output_exists_summary.json", "passed": True},
            {"name": "output_exists_event_log.csv", "passed": True},
        ],
    },
}


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_eval(self) -> Path:
        p = self.root / 'results' / 'evaluation_report.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(EVAL_REPORT_FULL_PASS), encoding='utf-8')
        return p

    def _touch(self, rel: str, content: str = '# test\n') -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

    def test_g4v2_pyc_only_pattern_fails(self):
        """g4-v2 회피 패턴 — eval pass + disk .pyc 만 → fail."""
        eval_path = self._write_eval()
        # .pyc 만 박음
        self._touch('src/mine_sim/__pycache__/config.cpython-312.pyc', 'binary')
        self._touch('src/mine_sim/__pycache__/model.cpython-312.pyc', 'binary')
        self._touch('tests/__pycache__/test_invariants.cpython-312.pyc', 'binary')

        verdict = evaluate(self.root, eval_path, grade='G4')
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertTrue(verdict['pyc_only_pattern'])
        kinds = {v['kind'] for v in verdict['violations']}
        self.assertIn('pyc_only', kinds)
        self.assertIn('low_survival_ratio', kinds)
        self.assertIn('governance_trail_missing', kinds)

    def test_full_artefacts_passes(self):
        eval_path = self._write_eval()
        self._touch('conceptual_model.md', '# concept')
        self._touch('README.md', '# readme')
        self._touch('outputs/results.csv', 'a,b\n1,2')
        self._touch('outputs/summary.json', '{}')
        self._touch('outputs/event_log.csv', 'a\n')
        self._touch('.ShipofTheseus/proj/intent/01-intent.md', '# intent')

        verdict = evaluate(self.root, eval_path, grade='G4')
        self.assertEqual(verdict['verdict'], 'pass', msg=json.dumps(verdict, indent=2))

    def test_partial_loss_below_threshold_fails(self):
        eval_path = self._write_eval()
        # 5 중 1 만 잔존 = 20% < 50%
        self._touch('conceptual_model.md', '# concept')
        verdict = evaluate(self.root, eval_path, grade='G2', survival_threshold=0.5)
        self.assertEqual(verdict['verdict'], 'fail')
        kinds = {v['kind'] for v in verdict['violations']}
        self.assertIn('low_survival_ratio', kinds)

    def test_g2_no_governance_required(self):
        eval_path = self._write_eval()
        # G2 = governance trail 의무 없음
        self._touch('conceptual_model.md', '# c')
        self._touch('README.md', '# r')
        self._touch('outputs/results.csv', 'a')
        self._touch('outputs/summary.json', '{}')
        self._touch('outputs/event_log.csv', 'a')
        verdict = evaluate(self.root, eval_path, grade='G2')
        # governance 부재여도 G2 면 violation X
        kinds = {v['kind'] for v in verdict['violations']}
        self.assertNotIn('governance_trail_missing', kinds)

    def test_eval_report_missing_handled(self):
        verdict = evaluate(self.root, self.root / 'nonexistent.json', grade='G4')
        # eval report 없으면 survival check skip, 하지만 governance + pyc-only 는 검사
        # 빈 디렉터리는 pyc 0 + 다른 0 → pyc_only False
        self.assertFalse(verdict['eval_info']['eval_report_present'])


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_pyc_only(self):
        eval_p = self.root / 'results' / 'evaluation_report.json'
        eval_p.parent.mkdir(parents=True, exist_ok=True)
        eval_p.write_text(json.dumps(EVAL_REPORT_FULL_PASS), encoding='utf-8')
        cache = self.root / 'src' / '__pycache__' / 'a.cpython-312.pyc'
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text('binary', encoding='utf-8')

        rc = main([
            '--submission-dir', str(self.root),
            '--eval-report', str(eval_p),
            '--grade', 'G4',
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
