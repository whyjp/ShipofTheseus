"""Smoke test for generate_sprint40_artefacts.py — sprint-41 PR-F."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_sprint40_artefacts import emit_all, SKELETONS, main


class TestGenerateArtefacts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_emit_all_in_empty_dir(self):
        verdict = emit_all(self.root)
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertEqual(verdict['total'], 13)
        self.assertEqual(verdict['emitted'], 13)
        self.assertEqual(verdict['skipped'], 0)

    def test_skip_existing_files(self):
        # 첫 emit
        emit_all(self.root)
        # 둘째 emit — 모두 skip
        verdict = emit_all(self.root, overwrite=False)
        self.assertEqual(verdict['emitted'], 0)
        self.assertEqual(verdict['skipped'], 13)

    def test_overwrite_replaces(self):
        emit_all(self.root)
        # 사용자가 한 산출물 수정
        target = self.root / 'quality' / 'gate_pnc.json'
        target.write_text(json.dumps({'verdict': 'pass'}), encoding='utf-8')
        # overwrite=True 로 덮어쓰기
        verdict = emit_all(self.root, overwrite=True)
        self.assertEqual(verdict['emitted'], 13)
        # 다시 pending 상태
        data = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(data['verdict'], 'pending')

    def test_emitted_files_are_valid_json(self):
        emit_all(self.root)
        for rel in SKELETONS.keys():
            path = self.root / rel
            self.assertTrue(path.exists(), f'{rel} 미생성')
            data = json.loads(path.read_text(encoding='utf-8'))
            # verdict 필드 존재 (skip dashboard.json)
            if rel != 'interactive-viewer/dashboard.json':
                self.assertEqual(data.get('verdict'), 'pending', f'{rel} verdict 미pending')

    def test_cascaded_subq_md_emitted(self):
        emit_all(self.root)
        path = self.root / 'intent' / '04-cascaded-subq.md'
        self.assertTrue(path.exists())
        text = path.read_text(encoding='utf-8')
        self.assertIn('cascaded sub-Q', text)
        self.assertIn('keyword_matched', text)

    def test_cli_exit_0(self):
        rc = main([
            '--project-root', str(self.root),
            '--quiet',
        ])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
