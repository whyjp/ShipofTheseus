"""Smoke test for dashboard_submission_parity.py — sprint-43 PR-D."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dashboard_submission_parity import evaluate, parse_dashboard_files, main


# g4-v2 회차 dashboard md 패턴
G4V2_DASHBOARD_MD = """---
id: "test"
totalScore: 91
files:
  - path: "requirements.txt"
    bytes: 89
  - path: "results/evaluation_report.json"
    bytes: 14550
  - path: "run_experiment.py"
    bytes: 6057
  - path: "src/mine_sim/__init__.py"
    bytes: 146
  - path: "src/mine_sim/config.py"
    bytes: 8696
---
"""


class TestParseDashboard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse_files_block(self):
        p = self.root / 'd.md'
        p.write_text(G4V2_DASHBOARD_MD, encoding='utf-8')
        info = parse_dashboard_files(p)
        self.assertTrue(info['present'])
        self.assertEqual(len(info['declared_paths']), 5)
        self.assertIn('requirements.txt', info['declared_paths'])
        self.assertIn('src/mine_sim/config.py', info['declared_paths'])

    def test_no_dashboard(self):
        info = parse_dashboard_files(self.root / 'absent.md')
        self.assertFalse(info['present'])


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sub = self.root / 'sub'
        self.sub.mkdir()
        self.dash_md = self.root / 'dashboard.md'
        self.dash_md.write_text(G4V2_DASHBOARD_MD, encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def _touch(self, rel: str) -> None:
        p = self.sub / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('content', encoding='utf-8')

    def test_g4v2_pattern_5_declared_0_disk(self):
        """g4-v2 패턴 — dashboard 5 declared, disk 빈 (또는 .pyc 만)."""
        # disk 에 .pyc 만 박음 (legitimate cleanup 제외)
        self._touch('src/mine_sim/__pycache__/config.cpython-312.pyc')
        verdict = evaluate(self.sub, self.dash_md)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(verdict['missing_on_disk_count'], 5)

    def test_full_match_passes(self):
        for rel in ['requirements.txt', 'results/evaluation_report.json', 'run_experiment.py',
                    'src/mine_sim/__init__.py', 'src/mine_sim/config.py']:
            self._touch(rel)
        verdict = evaluate(self.sub, self.dash_md)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertEqual(verdict['missing_on_disk_count'], 0)

    def test_partial_match_fails(self):
        self._touch('requirements.txt')
        self._touch('results/evaluation_report.json')
        verdict = evaluate(self.sub, self.dash_md)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(verdict['missing_on_disk_count'], 3)

    def test_untracked_on_dashboard_warning_only(self):
        """disk 에 dashboard 미tracked 파일이 있어도 missing 0 면 pass."""
        for rel in ['requirements.txt', 'results/evaluation_report.json', 'run_experiment.py',
                    'src/mine_sim/__init__.py', 'src/mine_sim/config.py',
                    'extra.txt']:  # 추가 untracked 파일
            self._touch(rel)
        verdict = evaluate(self.sub, self.dash_md)
        self.assertEqual(verdict['verdict'], 'pass')  # missing 0 → pass
        self.assertEqual(verdict['untracked_on_dashboard_count'], 1)

    def test_pycache_legitimate_cleanup(self):
        """__pycache__ 안 파일은 untracked 로 잡지 않음."""
        for rel in ['requirements.txt', 'results/evaluation_report.json', 'run_experiment.py',
                    'src/mine_sim/__init__.py', 'src/mine_sim/config.py']:
            self._touch(rel)
        self._touch('src/mine_sim/__pycache__/config.cpython-312.pyc')
        verdict = evaluate(self.sub, self.dash_md)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertEqual(verdict['untracked_on_dashboard_count'], 0)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sub = self.root / 'sub'
        self.sub.mkdir()
        self.dash_md = self.root / 'dashboard.md'
        self.dash_md.write_text(G4V2_DASHBOARD_MD, encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_missing(self):
        rc = main([
            '--submission-dir', str(self.sub),
            '--dashboard-md', str(self.dash_md),
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
