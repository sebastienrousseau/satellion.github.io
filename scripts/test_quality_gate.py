# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Tests for quality_gate.py. Run: python3 -m unittest discover -s scripts"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import quality_gate

CLEAN_QUALITY = {
    "passed_pillars": 2,
    "total_pillars": 2,
    "pass_rate": 100.0,
    "total_issues": 0,
    "pillars": {"1. Output": {"pass": True, "issues": []}, "6. Navbar": {"pass": True, "issues": []}},
}
CLEAN_A11Y = {"pages_scanned": 3, "total_issues": 0, "wcag_version": "2.2", "pages": []}
CLEAN_MANIFEST = {"name": "Satellion", "short_name": "Satellion", "theme_color": "#214186"}


def site(quality=CLEAN_QUALITY, a11y=CLEAN_A11Y, manifest=CLEAN_MANIFEST):
    d = tempfile.mkdtemp()
    if manifest is not None:
        (Path(d) / quality_gate.MANIFEST).write_text(json.dumps(manifest))
    if quality is not None:
        (Path(d) / quality_gate.QUALITY).write_text(json.dumps(quality))
    if a11y is not None:
        (Path(d) / quality_gate.ACCESSIBILITY).write_text(json.dumps(a11y))
    return d


class QualityGate(unittest.TestCase):
    def test_clean_reports_pass(self):
        self.assertEqual(quality_gate.problems(site()), [])

    def test_a_failing_pillar_is_named_with_its_issues(self):
        quality = json.loads(json.dumps(CLEAN_QUALITY))
        quality["passed_pillars"] = 1
        quality["pillars"]["6. Navbar"] = {"pass": False, "issues": ["index.html: Missing responsive navbar"]}
        self.assertEqual(
            quality_gate.problems(site(quality=quality)),
            [
                "quality gate: 1/2 pillars pass",
                "quality gate: 6. Navbar: index.html: Missing responsive navbar",
            ],
        )

    def test_an_accessibility_issue_fails(self):
        a11y = {
            "pages": [
                {
                    "path": "index.html",
                    "issues": [
                        {"criterion": "1.1.1", "severity": "error", "message": "<img> missing alt text: /a.svg"}
                    ],
                }
            ]
        }
        self.assertEqual(
            quality_gate.problems(site(a11y=a11y)),
            ["accessibility: index.html: [1.1.1] <img> missing alt text: /a.svg"],
        )

    def test_a_null_manifest_field_fails(self):
        manifest = {**CLEAN_MANIFEST, "short_name": None, "theme_color": None}
        self.assertEqual(
            quality_gate.problems(site(manifest=manifest)),
            [
                "manifest.json: short_name is null; set it in front matter",
                "manifest.json: theme_color is null; set it in front matter",
            ],
        )

    def test_a_missing_report_fails(self):
        found = quality_gate.problems(site(quality=None, a11y=None, manifest=None))
        self.assertEqual(len(found), 3)
        self.assertTrue(all("missing" in f for f in found))

    def test_main_passes_clean_and_exits_with_the_findings(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            quality_gate.main(["quality_gate.py", site()])
        self.assertIn("every pillar passes", out.getvalue())
        with self.assertRaises(SystemExit) as e:
            quality_gate.main(["quality_gate.py", site(quality=None)])
        self.assertIn("missing", str(e.exception.code))

    def test_main_without_its_argument_prints_the_usage(self):
        with self.assertRaises(SystemExit) as e:
            quality_gate.main(["quality_gate.py"])
        self.assertIn("usage", str(e.exception.code))


if __name__ == "__main__":
    unittest.main()
