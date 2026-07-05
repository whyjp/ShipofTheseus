"""Smoke test for dacapo_threshold.py — sprint-41 PR-B.

stdlib unittest 만 사용. 0510 회차의 실 tournament-impl-01.md 본문 패턴으로 테스트.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dacapo_threshold import evaluate, extract_winner_score, main


SAMPLE_TOURNAMENT_IMPL = """---
skill_name: theseus-orchestrator
skill_version: 0.9.45
phase: "08-impl-tournament-01"
fingerprint: "impl-08-tournament-01-smt-g4-2026-05-10"
prev_fingerprint: "impl-08-u3-meta-smt-g4-2026-05-10"
created_at: "2026-05-09T17:01:15Z"
grade: G4
round: 1
---

# Implementation tournament — round 1

## 6-dim sub-scores (all on actual evaluator outcome)

| Dim | U1 (engine + minimal report) | U2 (round-robin) | U3 (engine + extended report) | Combined U1+U3 (canonical) |
| --- | --- | --- | --- | --- |
| Evaluator pass-rate | 53/53 (predicted) | likely 52/53 | 53/53 (predicted) | **53/53 (measured)** |
| Behavioural saturation | yes | uncertain | yes | yes |
| Code quality | clean | clean | clean | clean |
| Auditability | OK | OK | high (12 event cols, topology.png) | high |
| Reviewer ergonomics | OK | OK | high | high |
| Runtime | ~4 s | ~4 s | ~4 s + 2 s plot | 7.97 s end-to-end |
| **Total** | 50/60 | 41/60 | 56/60 | **57/60** |

## Winner

- Combined U1 engine + U3 reporting wins.
- Predicted in plan tournament; confirmed by measured evaluator outcome.
"""

SAMPLE_PLAN_TOURNAMENT = """---
skill_name: theseus-orchestrator
skill_version: 0.9.45
phase: "06-plan-tournament-01"
---

# Plan tournament — round 1

| Dim | U1 | U2 | U3 | Note |
| --- | --- | --- | --- | --- |
| Spec adherence | 10/10 | 4/10 | 10/10 | YAML says nearest |
| Predicted throughput | 9/10 | 6/10 | 9/10 | U2 wastes |
| **Total** | **50/60** | **41/60** | **56/60** | — |

## Winner

- U3 wins.
"""

SAMPLE_PERFECT = """---
skill_name: theseus-orchestrator
phase: "06-plan-tournament-02"
winner_score: 60
winner_max: 60
---

# Plan tournament — round 2

Perfect score reached.
"""


class TestExtractWinnerScore(unittest.TestCase):
    def test_impl_tournament_extracts_57_60(self):
        result = extract_winner_score(SAMPLE_TOURNAMENT_IMPL)
        self.assertIsNotNone(result)
        score, max_, source = result
        self.assertEqual(score, 57)
        self.assertEqual(max_, 60)
        self.assertEqual(source, 'total_row_max_ratio')

    def test_plan_tournament_extracts_56_60(self):
        result = extract_winner_score(SAMPLE_PLAN_TOURNAMENT)
        self.assertIsNotNone(result)
        score, max_, source = result
        self.assertEqual(score, 56)
        self.assertEqual(max_, 60)

    def test_frontmatter_priority(self):
        result = extract_winner_score(SAMPLE_PERFECT)
        self.assertIsNotNone(result)
        score, max_, source = result
        self.assertEqual(score, 60)
        self.assertEqual(max_, 60)
        self.assertEqual(source, 'frontmatter')


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_57_60_fails_threshold_0999(self):
        path = self.tmpdir / 'tournament-impl-01.md'
        path.write_text(SAMPLE_TOURNAMENT_IMPL, encoding='utf-8')
        verdict = evaluate(path, 0.999)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(verdict['ratio'], 0.95)
        self.assertTrue(verdict['next_round_required'])

    def test_60_60_passes(self):
        path = self.tmpdir / 'tournament-02.md'
        path.write_text(SAMPLE_PERFECT, encoding='utf-8')
        verdict = evaluate(path, 0.999)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertEqual(verdict['ratio'], 1.0)
        self.assertFalse(verdict['next_round_required'])

    def test_score_text_override(self):
        verdict = evaluate(self.tmpdir / 'unused.md', 0.999, score_text_override='60/60')
        self.assertEqual(verdict['verdict'], 'pass')

    def test_reporting_mode_no_threshold_is_non_gating(self):
        """설계 B2 §2.3 — threshold 미지정(default) = 보고 모드. 57/60 라도 verdict='report'
        (비게이팅) + ratio 계속 보고. 점수 절대값은 종료 게이트가 아니다."""
        path = self.tmpdir / 'tournament-impl-01.md'
        path.write_text(SAMPLE_TOURNAMENT_IMPL, encoding='utf-8')
        verdict = evaluate(path)  # threshold None (default)
        self.assertEqual(verdict['verdict'], 'report')
        self.assertEqual(verdict['ratio'], 0.95)
        self.assertFalse(verdict['next_round_required'])


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_fail(self):
        path = self.tmpdir / 't.md'
        path.write_text(SAMPLE_TOURNAMENT_IMPL, encoding='utf-8')
        out = self.tmpdir / 'out.json'
        rc = main([
            '--tournament-md', str(path),
            '--threshold', '0.999',
            '--output', str(out),
            '--quiet',
        ])
        self.assertEqual(rc, 1)
        self.assertTrue(out.exists())
        data = json.loads(out.read_text(encoding='utf-8'))
        self.assertEqual(data['verdict'], 'fail')

    def test_cli_exit_0_on_pass(self):
        rc = main(['--score-text', '60/60', '--threshold', '0.999', '--quiet'])
        self.assertEqual(rc, 0)

    def test_cli_reporting_mode_exit_0_without_threshold(self):
        """--threshold 미지정 = 보고 모드 → 57/60(0.95) 라도 exit 0(비게이팅, §2.3)."""
        path = self.tmpdir / 't.md'
        path.write_text(SAMPLE_TOURNAMENT_IMPL, encoding='utf-8')
        rc = main(['--tournament-md', str(path), '--quiet'])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
