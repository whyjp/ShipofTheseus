"""Smoke test for surrender_phrase_grep.py — sprint-42 PR-E."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from surrender_phrase_grep import evaluate, main, SURRENDER_PATTERNS


# 0510-2 회피 패턴 — sprints/03/report.json 의 lessons_outbound[1] 직접 인용
REPORT_0510_2 = {
    "sprint": 3,
    "score": 0.97,
    "stagnation_detected": True,
    "decision": "exit_sprint_loop_per_DEC-autonomy",
    "lessons_outbound": [
        "trinity score plateaued at 0.97; further sprints would only fine-tune narrative",
        "0.97 < 0.999 G4 asymptote; defer to opus-reviewer scoring as final ground truth",
    ],
}


class TestPatterns(unittest.TestCase):
    def test_8_patterns_loaded(self):
        self.assertEqual(len(SURRENDER_PATTERNS), 8)


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _w(self, rel: str, content) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, dict):
            p.write_text(json.dumps(content), encoding='utf-8')
        else:
            p.write_text(content, encoding='utf-8')

    def test_0510_2_pattern_blocks(self):
        """0510-2 회피 패턴 — 4 surrender 어휘 (plateaued, would only fine-tune narrative, asymptote, defer to opus-reviewer, final ground truth) 매치 → fail."""
        self._w('sprints/03/report.json', REPORT_0510_2)
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'fail')
        # plateaued / would_only / asymptote / defer_to_external / final_ground_truth_external 매치 의무
        kinds = {m['kind'] for f in verdict['per_file'] for m in f['matches']}
        self.assertIn('plateaued', kinds)
        self.assertIn('asymptote', kinds)
        self.assertIn('defer_to_external', kinds)
        self.assertIn('would_only', kinds)
        self.assertIn('final_ground_truth_external', kinds)

    def test_clean_text_passes(self):
        self._w('intent/01-intent.md', '# intent\nClean modeling and simulation.\n')
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'pass')

    def test_override_allows_match(self):
        self._w(
            'sprints/03/report.md',
            '''---
surrender_override: true
surrender_override_reason: "사용자 직접 ack — 외부 reviewer 통합 단계"
---

# Sprint 03 — defer to opus-reviewer for final ground truth.
''',
        )
        verdict = evaluate(self.root)
        # match 는 있지만 override = pass
        self.assertEqual(verdict['verdict'], 'pass')
        self.assertGreater(verdict['overridden_count'], 0)

    def test_partial_override_does_not_apply_globally(self):
        """Override 는 *해당 파일* 안에서만 — 다른 파일 매치 차단."""
        self._w(
            'sprints/02/report.md',
            '---\nsurrender_override: true\nsurrender_override_reason: ack\n---\nplateaued.\n',
        )
        self._w(
            'sprints/03/report.md',
            '# defer to opus-reviewer\n',  # override 없음
        )
        verdict = evaluate(self.root)
        self.assertEqual(verdict['verdict'], 'fail')

    def test_safe_phrases_not_matched(self):
        """legitimate 어휘 false positive 회피."""
        self._w('intent/05-critique.md', 'plateau at score 0.95 was observed in baseline.\n')
        # `plateaued` 패턴이 'plateau at \d' 는 negative lookahead 로 회피
        verdict = evaluate(self.root)
        # 이 어휘는 negative lookahead 의해 통과
        # 실제 매치되면 안 됨
        kinds = {m['kind'] for f in verdict['per_file'] for m in f['matches']}
        self.assertNotIn('plateaued', kinds)


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_exit_1_on_match(self):
        p = self.root / 'sprints' / '03' / 'report.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(REPORT_0510_2), encoding='utf-8')
        rc = main([
            '--project-root', str(self.root),
            '--quiet',
        ])
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
