# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Tests for site_data.py. Run: python3 -m unittest discover -s scripts"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import site_data


def finding(fid, status, evidence=None):
    return {
        "id": fid,
        "title": f"{fid} title",
        "detail": f'{fid} said "no"',
        "status": status,
        "evidence": evidence or [],
    }


def report(cited=2):
    fails = [finding(f"F-{i}", "fail", [f"req-{i}"]) for i in range(cited)]
    return {
        "score": {
            "total": 71.5,
            "grade": "C",
            "categories": [
                {"name": "connectivity", "weight": 20, "score": 100},
                {"name": "catalog", "weight": 10, "score": 60},
                {"name": "custom", "weight": 10, "score": 0},
            ],
        },
        "counts": {"pass": 5, "warn": 1, "fail": cited, "skip": 1, "info": 1},
        "server": {"name": "fixture", "version": "1.0"},
        "passmcp": {"version": "0.0.1"},
        "phases": [
            {"name": "connect", "title": "Connect", "findings": [finding("P-1", "pass"), finding("F-x", "fail")]},
            {"name": "catalog", "findings": fails},
            {"name": "empty", "findings": None},
        ],
    }


PAGE = """---
title: "passmcp"
readout_score: "0"
metric_one_value: "1"
---

Run 12 checks with go install satellion.com/passmcp/cmd/passmcp@v0.0.0 today.
"""


@contextlib.contextmanager
def site_tree(count="131"):
    """A throwaway copy of the files main() rewrites, as the working directory."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for path in site_data.COUNT_FILES:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(PAGE if path == "content/passmcp/index.md" else "It runs 12 checks.\n")
        (root / "report.json").write_text(json.dumps(report()))
        (root / "checks.md").write_text(f"passmcp runs **{count} checks** in nine phases.\n")
        cwd = os.getcwd()
        os.chdir(root)
        try:
            yield root
        finally:
            os.chdir(cwd)


def run_main(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        site_data.main(["site_data.py", *args])
    return out.getvalue()


ARGS = ("report.json", "content/passmcp/index.md", "checks.md")


class Fields(unittest.TestCase):
    def test_the_readout_ledger_phases_and_evidence_come_from_the_report(self):
        got = site_data.fields(report())
        self.assertEqual(got["readout_score"], "71.5")
        self.assertEqual(got["readout_grade"], "C")
        self.assertEqual(got["readout_note"], "10 checks · 5 pass · 1 warn · 2 fail · 1 skipped · 1 info")
        self.assertEqual(got["ledger_1_area"], "Connectivity")
        self.assertEqual(got["ledger_1_status"], "pass")
        self.assertEqual(got["ledger_1_deduction"], "0")
        self.assertEqual(got["ledger_2_area"], "Catalogue")
        self.assertEqual(got["ledger_2_status"], "warn")
        self.assertEqual(got["ledger_2_deduction"], "−4")
        self.assertEqual(got["ledger_3_area"], "Custom")
        self.assertEqual(got["ledger_3_status"], "fail")
        self.assertEqual(got["phase_1"], "Connect")
        self.assertEqual(got["phase_2"], "catalog")
        self.assertEqual(got["evidence_1_id"], "F-0")
        self.assertEqual(got["evidence_1_req"], "req-0")
        self.assertEqual(got["evidence_2_detail"], "F-1 said 'no'")

    def test_a_report_with_fewer_than_two_cited_failures_is_refused(self):
        with self.assertRaises(SystemExit) as e:
            site_data.fields(report(cited=1))
        self.assertIn("fewer than two cited failures", str(e.exception))


class Helpers(unittest.TestCase):
    def test_the_check_count_is_read_from_checks_md(self):
        with tempfile.TemporaryDirectory() as d:
            good, bad = Path(d, "good.md"), Path(d, "bad.md")
            good.write_text("There are **131 checks** here.")
            bad.write_text("No count.")
            self.assertEqual(site_data.check_count(good), "131")
            with self.assertRaises(SystemExit):
                site_data.check_count(bad)

    def test_the_install_line_is_pinned_to_the_release(self):
        text = "go install satellion.com/passmcp/cmd/passmcp@v0.0.0"
        self.assertEqual(site_data.pin_install(text, "0.0.1"), "go install satellion.com/passmcp/cmd/passmcp@v0.0.1")

    def test_apply_replaces_a_key_and_appends_a_missing_one(self):
        got = site_data.apply(PAGE, {"readout_score": "99", "new_key": "x"})
        self.assertIn('readout_score: "99"', got)
        self.assertIn('new_key: "x"\n---\n', got)


class Main(unittest.TestCase):
    def test_a_write_updates_every_count_and_the_page(self):
        with site_tree() as root:
            out = run_main(*ARGS)
            self.assertIn("131 checks and the sample report written into", out)
            page = (root / "content/passmcp/index.md").read_text()
            self.assertIn('metric_one_value: "131"', page)
            self.assertIn("Run 131 checks", page)
            self.assertIn("passmcp@v0.0.1", page)
            self.assertIn("runs 131 checks", (root / "ssg.toml").read_text())
            self.assertIn("already current", run_main(*ARGS))

    def test_check_fails_on_a_stale_page_and_passes_on_a_current_one(self):
        with site_tree():
            with self.assertRaises(SystemExit) as e:
                run_main(*ARGS, "--check")
            self.assertIn("run make data", str(e.exception))
            run_main(*ARGS)
            self.assertIn("the page matches passmcp 0.0.1: 131 checks, score 71.5", run_main(*ARGS, "--check"))

    def test_the_wrong_arguments_print_the_usage(self):
        with self.assertRaises(SystemExit) as e:
            run_main("only-one")
        self.assertIn("site_data.py <report.json>", str(e.exception))


if __name__ == "__main__":
    unittest.main()
