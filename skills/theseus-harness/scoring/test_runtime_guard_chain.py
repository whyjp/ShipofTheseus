"""Smoke test for runtime_guard_chain.py — sprint-41 PR-E."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from runtime_guard_chain import (
    parse_version,
    check_skill_version,
    check_phase_monotonicity,
    evaluate,
    main,
)


class TestParseVersion(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(parse_version('0.9.46'), (0, 9, 46))
        self.assertEqual(parse_version('1.0.0'), (1, 0, 0))
        self.assertEqual(parse_version('garbage'), (0, 0, 0))


class TestCheckSkillVersion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_md(self, rel: str, version: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f'---\nskill_name: theseus-harness\nskill_version: {version}\nphase: 09\n---\n\n# test\n',
            encoding='utf-8',
        )

    def test_minor_silent_skip_blocked(self):
        """0510 회차 패턴 — frontmatter 0.9.40 vs orchestrator 0.9.46 → fail."""
        self._write_md('intent/01.md', '0.9.40')
        self._write_md('plan/06.md', '0.9.40')
        result = check_skill_version(self.root, '0.9.46')
        self.assertFalse(result['passed'])

    def test_minor_match_passes(self):
        self._write_md('intent/01.md', '0.9.46')
        self._write_md('plan/06.md', '0.9.46')
        result = check_skill_version(self.root, '0.9.46')
        self.assertTrue(result['passed'])

    def test_minor_higher_passes(self):
        self._write_md('intent/01.md', '0.9.50')
        result = check_skill_version(self.root, '0.9.46')
        self.assertTrue(result['passed'])

    def test_no_frontmatter_fails(self):
        result = check_skill_version(self.root, '0.9.46')
        self.assertFalse(result['passed'])


class TestCheckPhaseMonotonicity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_phase(self, rel: str, phase: str, created_at: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f'---\nskill_version: 0.9.46\nphase: {phase}\ncreated_at: {created_at}\n---\n\n',
            encoding='utf-8',
        )

    def test_monotonic(self):
        self._write_phase('intent/01.md', '01', '2026-05-10T10:00:00Z')
        self._write_phase('plan/06.md', '06', '2026-05-10T11:00:00Z')
        self._write_phase('impl/08.md', '08', '2026-05-10T12:00:00Z')
        result = check_phase_monotonicity(self.root, '09')
        self.assertTrue(result['passed'])

    def test_violation(self):
        self._write_phase('intent/01.md', '01', '2026-05-10T10:00:00Z')
        self._write_phase('plan/06.md', '06', '2026-05-10T11:00:00Z')
        self._write_phase('impl/08.md', '08', '2026-05-10T09:00:00Z')  # backfill 위반
        result = check_phase_monotonicity(self.root, '09')
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['violations']), 1)


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_phase(self, rel: str, phase: str, version: str = '0.9.46') -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f'---\nskill_version: {version}\nphase: {phase}\ncreated_at: 2026-05-10T10:00:00Z\n---\n\n',
            encoding='utf-8',
        )

    def test_skill_version_violation_blocks(self):
        self._write_phase('intent/01.md', '01', version='0.9.40')
        verdict = evaluate(
            self.root, '09', 'entry', 'G4', 'DES', True, '0.9.46',
        )
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertIn('skill_version', verdict['fail_checks'])
        self.assertTrue(verdict['advance_blocked'])

    def test_basic_pass_no_hook(self):
        """phase 01 entry — hook 없음, skill_version + monotonicity 만 검사."""
        self._write_phase('intent/01.md', '01')
        verdict = evaluate(
            self.root, '01', 'entry', 'G4', 'DES', True, '0.9.46',
        )
        # hook 없으므로 2 check (skill_version + monotonicity) 만
        self.assertEqual(len([c for c in verdict['checks'] if 'check' in c]), 2)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_skill_version_fail(self):
        p = self.root / 'intent' / '01.md'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            '---\nskill_version: 0.9.40\nphase: 01\ncreated_at: 2026-05-10T10:00:00Z\n---\n',
            encoding='utf-8',
        )
        rc = main([
            '--project-root', str(self.root),
            '--phase', '01',
            '--transition', 'entry',
            '--grade', 'G4',
            '--orchestrator-version', '0.9.46',
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
