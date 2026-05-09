"""Smoke test for cold_session_artefacts.py — sprint-41 PR-C."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cold_session_artefacts import evaluate, ARTEFACTS, main


def _write_pass_artefact(root: Path, rel: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == '.json':
        p.write_text(json.dumps({'schema_version': '0.9.46', 'verdict': 'pass'}), encoding='utf-8')
    else:
        p.write_text('# test\n', encoding='utf-8')


def _write_methodology_skip(root: Path) -> None:
    p = root / 'quality/gate_methodology_completeness.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps({
            'schema_version': '0.9.46',
            'domain_matched': False,
            'verdict': 'skip',
        }),
        encoding='utf-8',
    )


class TestColdSessionArtefacts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_project_fails(self):
        """0510 회차 회피 패턴 — 모든 산출물 부재."""
        verdict = evaluate(self.root, 'G4', 'DES', True)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(len(verdict['missing']), 13)  # G4 + domain matched = 13 모두 의무

    def test_all_pass(self):
        for spec in ARTEFACTS:
            _write_pass_artefact(self.root, spec['path'])
        verdict = evaluate(self.root, 'G4', 'DES', True)
        self.assertEqual(verdict['verdict'], 'pass', msg=json.dumps(verdict, indent=2))

    def test_methodology_skip_when_domain_unmatched(self):
        """gate_methodology_completeness.json 의 domain_matched=false 시 skip 허용."""
        for spec in ARTEFACTS:
            if spec['id'] == 'gate_methodology_completeness':
                _write_methodology_skip(self.root)
            else:
                _write_pass_artefact(self.root, spec['path'])
        verdict = evaluate(self.root, 'G4', None, False)
        self.assertEqual(verdict['verdict'], 'pass')

    def test_g2_domain_unmatched_skips_viewer(self):
        """G2 + domain unmatched → interactive-viewer 산출물 skip 허용."""
        # G2 의무만 작성 (gate_methodology_completeness, modeling_shortcuts, cascaded_subq, interactive_viewer_* 제외)
        g2_required_specs = [s for s in ARTEFACTS if 'G2' in s.get('require_grades', [])]
        for spec in g2_required_specs:
            if spec['id'] in ('interactive_viewer_exit_gate', 'interactive_viewer_dashboard'):
                continue  # G2 + 미매칭 시 skip 허용
            _write_pass_artefact(self.root, spec['path'])
        verdict = evaluate(self.root, 'G2', None, False)
        self.assertEqual(verdict['verdict'], 'pass', msg=json.dumps(verdict, indent=2))

    def test_invalid_json_detected(self):
        for spec in ARTEFACTS:
            _write_pass_artefact(self.root, spec['path'])
        # gate_v6 invalid JSON 박음
        (self.root / 'quality/gate_v6_reproducibility.json').write_text(
            '{ broken json',
            encoding='utf-8',
        )
        verdict = evaluate(self.root, 'G4', 'DES', True)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertEqual(len(verdict['invalid']), 1)

    def test_verdict_fail_detected(self):
        for spec in ARTEFACTS:
            if spec['id'] == 'gate_pnc':
                p = self.root / spec['path']
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({'verdict': 'fail'}), encoding='utf-8')
            else:
                _write_pass_artefact(self.root, spec['path'])
        verdict = evaluate(self.root, 'G4', 'DES', True)
        self.assertEqual(verdict['verdict'], 'fail')
        self.assertIn('quality/gate_pnc.json', verdict['verdict_fail'])

    def test_cli_exit_1_on_empty(self):
        rc = main([
            '--project-root', str(self.root),
            '--grade', 'G4',
            '--domain', 'DES',
            '--domain-matched',
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
