"""Smoke test for sprint_loop_cap.py — sprint-41 PR-D."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sprint_loop_cap import evaluate, main


def _write(path: Path, content: str | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, dict):
        path.write_text(json.dumps(content), encoding='utf-8')
    else:
        path.write_text(content, encoding='utf-8')


class TestSprintLoopCap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bench_root = Path(self.tmp.name)
        # `<project_root>` = `bench_root/.ShipofTheseus/<proj>`
        # `evaluation_report.json` = `bench_root/results/...` 또는 `<project_root>/results/...`
        # 실제 구조 모방
        self.project_root = self.bench_root / '.ShipofTheseus' / 'proj'
        self.project_root.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_eval_report(self, pass_rate: float) -> None:
        # bench_root/.ShipofTheseus/proj 의 *parent* = bench_root/.ShipofTheseus
        # 본 파일의 candidate 1 = project_root.parent / 'results' = bench_root/.ShipofTheseus/results
        # 단순화 — candidate 3 = project_root/evaluation_report.json
        _write(
            self.project_root / 'evaluation_report.json',
            {'automated_checks': {'pass_rate': pass_rate}},
        )

    def _write_quality_gate(self, verdict: str, fail_count: int = 0) -> None:
        body = f"""# Phase 09 — Quality gate

| Gate | Result |
| --- | --- |
| G1 | **PASS** |
| G2 | **PASS** |
""" + ("| G3 | **FAIL** |\n" * fail_count) + f"""

## Verdict

{verdict}
"""
        _write(self.project_root / 'quality' / '09-quality-gate.md', body)

    def _write_dacapo(self, ratio: float, where: str) -> None:
        verdict = 'pass' if ratio >= 0.999 else 'fail'
        _write(
            self.project_root / where / 'dacapo_threshold.json',
            {
                'schema_version': '0.9.46',
                'verdict': verdict,
                'ratio': ratio,
                'threshold': 0.999,
            },
        )

    def test_0510_regression_pattern(self):
        """0510 회차 회피 패턴 — Auto 100% / Tournament 0.95 / Internal proceed but missing files / External 90.

        sprint cap = 1 자율 stop 했던 상황. 본 CLI 가 *continue* 강제 하는지 검증.
        """
        self._write_eval_report(1.0)
        self._write_quality_gate('proceed', fail_count=0)
        self._write_dacapo(0.95, 'plan')
        self._write_dacapo(0.95, 'impl')
        # external 미존재 — 3 layer 만 검사

        verdict = evaluate(self.project_root, current_iteration=1, max_iterations=10)
        self.assertEqual(verdict['verdict'], 'continue')
        self.assertIn('tournament', verdict['fail_layers'])

    def test_all_pass_3layer_no_external(self):
        self._write_eval_report(1.0)
        self._write_quality_gate('proceed', fail_count=0)
        self._write_dacapo(1.0, 'plan')
        self._write_dacapo(1.0, 'impl')

        verdict = evaluate(self.project_root, current_iteration=1, max_iterations=10)
        self.assertEqual(verdict['verdict'], 'stop')
        self.assertEqual(verdict['fail_layers'], [])

    def test_max_iterations_force_stop(self):
        self._write_eval_report(0.5)
        self._write_quality_gate('halt', fail_count=3)
        self._write_dacapo(0.7, 'plan')
        self._write_dacapo(0.7, 'impl')

        verdict = evaluate(self.project_root, current_iteration=10, max_iterations=10)
        self.assertEqual(verdict['verdict'], 'stop')
        self.assertTrue(verdict['sprint_loop_terminated_by_max_iter'])

    def test_external_layer_when_present(self):
        self._write_eval_report(1.0)
        self._write_quality_gate('proceed', fail_count=0)
        self._write_dacapo(1.0, 'plan')
        self._write_dacapo(1.0, 'impl')
        # external 80/100 → < 0.95 = fail
        ext = self.bench_root / 'results' / 'zero_context_review.md'
        ext.parent.mkdir(parents=True, exist_ok=True)
        ext.write_text("Score 80/100\n", encoding='utf-8')
        # candidate path = project_root.parent / 'results' = bench_root/.ShipofTheseus/results
        # 단순 — project_root/results 에 박음
        _write(self.project_root / 'results' / 'zero_context_review.md', "Score 80/100\n")

        verdict = evaluate(self.project_root, current_iteration=1, max_iterations=10)
        self.assertIn('external', verdict['fail_layers'])
        self.assertEqual(verdict['verdict'], 'continue')

    def test_cli_reporting_mode_exit_0_by_default(self):
        """설계 B2 §2.3 — default 는 보고 모드(비게이팅). continue 라도 exit 0."""
        self._write_eval_report(1.0)
        self._write_quality_gate('proceed')
        self._write_dacapo(0.95, 'plan')
        self._write_dacapo(0.95, 'impl')

        rc = main([
            '--project-root', str(self.project_root),
            '--current-iteration', '1',
            '--max-iterations', '10',
            '--quiet',
        ])
        self.assertEqual(rc, 0)

    def test_cli_gate_opt_in_exit_1_on_continue(self):
        """--gate opt-in 시 예전 4-layer 차단 동작 복원 — continue → exit 1."""
        self._write_eval_report(1.0)
        self._write_quality_gate('proceed')
        self._write_dacapo(0.95, 'plan')
        self._write_dacapo(0.95, 'impl')

        rc = main([
            '--project-root', str(self.project_root),
            '--current-iteration', '1',
            '--max-iterations', '10',
            '--gate',
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
