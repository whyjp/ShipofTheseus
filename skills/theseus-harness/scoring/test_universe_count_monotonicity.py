"""Smoke test for universe_count_monotonicity.py — sprint-42 PR-C."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from universe_count_monotonicity import evaluate, main


T1_BODY = """---
phase: 06-plan-tournament-01
---

# Plan Tournament 01

| Universe | Score |
|---|---|
| universe-1 | 0.96 |
| universe-2 | 0.82 |
| universe-3 | 0.74 |

Winner: universe-1.
"""

T2_RERATE_SAME = """---
phase: 06-plan-tournament-02
---

# Plan Tournament 02 — blind re-rerun

| universe-1 | 0.95 |
| universe-2 | 0.81 |
| universe-3 | 0.73 |

Winner identical: universe-1.
"""

T2_NEW_UNIVERSE = """---
phase: 06-plan-tournament-02
---

# Plan Tournament 02 — new universe

| universe-1 | 0.95 |
| universe-2 | 0.81 |
| universe-3 | 0.73 |
| universe-4 | 0.97 |

Winner shifts to universe-4.
"""

IMPL_T1_SINGLE_NO_SEVEN = """---
phase: 08-impl-tournament-01
---

# Implementation Tournament 01 — verdict

| universe-1 | implemented |

Single-universe implementation since plan tournament locked.
Verdict: ship universe-1.
"""

IMPL_T1_SINGLE_WITH_SEVEN = """---
phase: 08-impl-tournament-01
---

# Implementation Tournament 01

| universe-1 | implemented |

Per HARD-RULE 9.jj impl-multiverse-strict, the 7-condition gate was assessed:
| 1. >= 2 plan universes scored | yes |
| 2. Tournament re-rerun blind | yes |
| 3. Da Capo step F-G applied | yes |
| 4. Reproducibility verified | yes |
| 5. All capacity-1 edges modelled | yes |
| 6. Wall-clock < 5 min | yes |
| 7. Tests green | yes |

Verdict: ship universe-1.
"""


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _w(self, rel: str, content: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

    def test_0510_2_pattern_round2_zero_new_universe(self):
        """0510-2 회피 패턴 — round 2 가 same 3 re-rate (NEW=0) → fail."""
        self._w('plan/tournament-01.md', T1_BODY)
        self._w('plan/tournament-02.md', T2_RERATE_SAME)
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertTrue(any(v['kind'] == 'plan_round_zero_new_universe' for v in verdict['violations']))

    def test_round2_with_new_universe_passes(self):
        self._w('plan/tournament-01.md', T1_BODY)
        self._w('plan/tournament-02.md', T2_NEW_UNIVERSE)
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'pass', msg=json.dumps(verdict, indent=2))

    def test_impl_single_no_seven_condition_fails(self):
        self._w('plan/tournament-01.md', T1_BODY)
        self._w('plan/tournament-02.md', T2_NEW_UNIVERSE)
        self._w('impl/tournament-impl-01.md', IMPL_T1_SINGLE_NO_SEVEN)
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertTrue(
            any(v['kind'] == 'impl_single_universe_without_seven_condition' for v in verdict['violations']),
        )

    def test_impl_single_with_seven_condition_passes(self):
        self._w('plan/tournament-01.md', T1_BODY)
        self._w('plan/tournament-02.md', T2_NEW_UNIVERSE)
        self._w('impl/tournament-impl-01.md', IMPL_T1_SINGLE_WITH_SEVEN)
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'pass')

    def test_no_tournaments_no_violations(self):
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertEqual(len(verdict['violations']), 0)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_zero_new_universe(self):
        p = self.root / 'plan' / 'tournament-01.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(T1_BODY, encoding='utf-8')
        (self.root / 'plan' / 'tournament-02.md').write_text(T2_RERATE_SAME, encoding='utf-8')
        rc = main([
            '--project-root', str(self.root),
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
