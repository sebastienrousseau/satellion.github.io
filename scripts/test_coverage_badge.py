# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Tests for coverage_badge.py. Run: python3 -m unittest discover -s scripts"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import coverage_badge


class Badge(unittest.TestCase):
    def test_the_colour_bands_are_the_familys(self):
        cases = {
            100.0: "brightgreen",
            90.0: "brightgreen",
            89.99: "green",
            85.0: "green",
            84.99: "yellow",
            70.0: "yellow",
            69.9: "red",
            0.0: "red",
        }
        for pct, colour in cases.items():
            with self.subTest(pct=pct):
                self.assertEqual(coverage_badge.badge(pct)["color"], colour)

    def test_the_figure_is_truncated_so_the_gate_is_never_shown_met_early(self):
        self.assertEqual(
            coverage_badge.badge(84.96),
            {"schemaVersion": 1, "label": "coverage", "message": "84.9%", "color": "yellow"},
        )
        self.assertEqual(coverage_badge.badge(100.0)["message"], "100.0%")

    def test_main_writes_the_endpoint_document_from_statement_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            report, out = Path(d, "report.json"), Path(d, "coverage.json")
            report.write_text(json.dumps({"totals": {"percent_covered": 50.0, "percent_statements_covered": 91.25}}))
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                coverage_badge.main(["coverage_badge.py", str(report), str(out)])
            self.assertEqual(
                out.read_text(), '{"schemaVersion":1,"label":"coverage","message":"91.2%","color":"brightgreen"}\n'
            )
            self.assertIn("91.2% written to", stdout.getvalue())

    def test_main_without_both_paths_prints_the_usage(self):
        with self.assertRaises(SystemExit) as e:
            coverage_badge.main(["coverage_badge.py"])
        self.assertIn("coverage_badge.py <coverage.py JSON report>", str(e.exception))


if __name__ == "__main__":
    unittest.main()
