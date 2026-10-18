# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""graph_demo.py writes the demo page from a share-safe export and nothing else.

The export here is a small one in the shape `passmcp-graph dashboard
--share-safe --format json` prints, with only the fields the page reads.
Run: python3 -m unittest discover -s scripts
"""

import contextlib
import copy
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import graph_demo

ROOT = Path(__file__).parent.parent
LAYOUTS = ROOT / "graph-demo" / "_layouts"
# What SSG itself supplies to a template, and the partial it includes.
SSG_FIELDS = {
    "content",
    "primary",
    "opengraph",
    "twitter",
    "apple",
    "microsoft",
    "site_url",
    "site_path",
    "permalink",
    "csp",
    "header",
    "footer",
}


def server(i, status, name="", score="", attestation="d" * 64, age="3"):
    return {
        "anchor": f"srv-{i}",
        "endpoint": f"http-server-{i + 1}",
        "name": name,
        "transport": "http",
        "score": score,
        "ageDays": age,
        "attestation": attestation,
        "tools": 2,
        "status": status,
        "statusLabel": status.capitalize(),
        "clients": [{"name": "cli_a", "anchor": "cli-0"}],
    }


EXPORT = {
    "generated": "2026-10-18T06:55:18Z",
    "shareSafe": True,
    "staleDays": 30,
    "agents": [
        {
            "name": "claude-desktop",
            "servers": 2,
            "paths": [{"server": {"anchor": "srv-0"}}, {"server": {"anchor": "srv-1"}}],
        },
        {"name": "cursor", "servers": 1, "paths": [{"server": {"anchor": "srv-1"}}]},
    ],
    "servers": [
        server(1, "ok", name="files", score="95"),
        server(0, "critical", name="crm*", score="41.5"),
        server(2, "unattested", attestation="", age=""),
    ],
    "findings": [
        {
            "severity": "critical",
            "title": "A <critical> check | failed",
            "path": "a -> b",
            "next": 'passmcp-graph query "agents -> servers where critical"',
            "server": {"anchor": "srv-0"},
        }
    ],
    "evidenceGaps": [
        {
            "title": "No attestation loaded",
            "clients": [{"name": "claude-desktop"}],
            "server": {"name": "http-server-3", "anchor": "srv-2"},
            "next": "q_gap",
        }
    ],
    "metrics": [
        {
            "id": "paths",
            "label": "Configured tool paths",
            "value": 3,
            "display": "3",
            "counts": "paths",
        },
        {
            "id": "paths.destructive",
            "label": "Destructive",
            "value": 1,
            "of": 3,
            "display": "33.3%",
            "counts": "d",
        },
        {
            "id": "servers.evidence",
            "label": "Evidence",
            "value": 2,
            "of": 3,
            "display": "66.7%",
            "counts": "e",
        },
        {
            "id": "score.mean",
            "label": "Mean score",
            "value": 2,
            "of": 3,
            "display": "68.3",
            "counts": "c",
        },
    ],
    "topIssue": {
        "severity": "critical",
        "title": "crm failed",
        "context": "Seen.",
        "rule": "auth.x",
    },
}


def fields(page):
    """The front matter, parsed back: every value is a JSON string."""
    head = page.split("---\n")[1]
    return {k: json.loads(v) for k, v in (line.split(": ", 1) for line in head.splitlines())}


def render(export=None):
    return graph_demo.render(graph_demo.load(json.dumps(export or EXPORT)), "0.0.7")


class Load(unittest.TestCase):
    def test_an_export_that_is_not_share_safe_is_refused(self):
        for value in (False, None, "true"):
            with (
                self.subTest(shareSafe=value),
                self.assertRaises(graph_demo.ExportError),
            ):
                graph_demo.load(json.dumps({**EXPORT, "shareSafe": value}))

    def test_more_clients_or_servers_than_the_layout_holds_is_refused(self):
        many = copy.deepcopy(EXPORT)
        many["servers"] = [server(i, "ok") for i in range(5)]
        with self.assertRaisesRegex(graph_demo.ExportError, "places for 3 and 4"):
            graph_demo.load(json.dumps(many))

    def test_malformed_input_is_refused(self):
        for text in ("not json", "[]", json.dumps({"shareSafe": True})):
            with self.subTest(text=text), self.assertRaises(graph_demo.ExportError):
                graph_demo.load(text)


class Render(unittest.TestCase):
    def test_every_field_the_layout_reads_is_written(self):
        text = "".join(f.read_text() for f in LAYOUTS.glob("*.html"))
        names = set(re.findall(r"\{\{[!>]? ?(?:#if )?([a-z0-9_-]+)\}\}", text))
        # A list or ring place the export does not fill is left out on purpose.
        names = {n for n in names if not re.match(r"(client|server|ring)_\d_", n)}
        missing = names - set(fields(render())) - SSG_FIELDS - {"current_about", "current_contact"}
        self.assertEqual(missing, set())

    def test_servers_are_listed_worst_first_with_their_names(self):
        f = fields(render())
        self.assertEqual(
            [f[f"server_{i}_name"] for i in (1, 2, 3)],
            ["crm*", "http-server-3", "files"],
        )
        self.assertEqual([f[f"server_{i}_sev"] for i in (1, 2, 3)], ["critical", "high", "ok"])
        self.assertEqual(f["server_2_score"], "No score")
        self.assertNotIn("server_4_name", f)

    def test_a_client_takes_the_colour_of_the_worst_server_it_reaches(self):
        f = fields(render())
        self.assertEqual((f["client_1_sev"], f["client_2_sev"]), ("critical", "ok"))
        self.assertEqual(f["client_1_meta"], "2 tool paths, 2 servers")
        self.assertEqual(f["client_2_meta"], "1 tool path, 1 server")

    def test_the_ring_has_one_arc_per_status_present_sharing_the_circle(self):
        f = fields(render())
        self.assertEqual([f[f"ring_{i}_sev"] for i in (1, 2, 3)], ["critical", "high", "ok"])
        self.assertNotIn("ring_4_sev", f)
        self.assertEqual([f[f"ring_{i}_offset"] for i in (1, 2, 3)], ["2", "35.3333", "68.6667"])
        self.assertEqual(f["ring_1_dash"], "29.3333")

    def test_key_figures_come_from_the_metrics(self):
        f = fields(render())
        self.assertEqual([f[f"kpi_{i}_value"] for i in (1, 2, 3, 4)], ["3", "33.3%", "66.7%", "68.3"])
        self.assertEqual([f[f"kpi_{i}_sev"] for i in (1, 2, 3, 4)], ["low", "high", "medium", "low"])
        self.assertIn("2 of 3 servers", f["kpi_4_note"])

    def test_figures_with_nothing_to_act_on_are_ok(self):
        calm = copy.deepcopy(EXPORT)
        calm["metrics"][1]["value"] = 0
        calm["metrics"][2]["value"] = 3
        f = fields(render(calm))
        self.assertEqual((f["kpi_2_sev"], f["kpi_3_sev"]), ("ok", "ok"))

    def test_a_missing_metric_is_refused(self):
        short = copy.deepcopy(EXPORT)
        short["metrics"] = short["metrics"][:3]
        with self.assertRaisesRegex(graph_demo.ExportError, "score.mean"):
            render(short)

    def test_the_alert_is_the_top_issue_and_absent_without_one(self):
        self.assertEqual(fields(render())["alert_title"], "crm failed")
        quiet = {k: v for k, v in EXPORT.items() if k != "topIssue"}
        self.assertNotIn("alert_title", fields(render(quiet)))

    def test_export_text_cannot_add_markup_or_markdown(self):
        body = render().split("---\n", 2)[2]
        self.assertIn("A &lt;critical&gt; check &#124; failed", body)
        self.assertNotIn("<critical>", body)
        self.assertIn("crm&#42;", body)

    def test_findings_then_gaps_with_their_queries(self):
        body = render().split("---\n", 2)[2]
        self.assertLess(body.index("A &lt;critical"), body.index("No attestation loaded"))
        self.assertIn('<span class="pill sev-low">Low</span>', body)
        self.assertIn("<code>q&#95;gap</code>", body)
        self.assertIn("| Not supplied |", body)

    def test_a_non_critical_finding_is_medium(self):
        mild = copy.deepcopy(EXPORT)
        mild["findings"][0]["severity"] = "warning"
        mild["topIssue"]["severity"] = "warning"
        page = render(mild)
        self.assertIn('<span class="pill sev-medium">Medium</span>', page)
        self.assertEqual(fields(page)["alert_sev"], "medium")

    def test_evidence_ages_read_as_the_dashboard_words_them(self):
        self.assertEqual(graph_demo.age({"attestation": "x", "ageDays": "1"}), "1 day")
        self.assertEqual(graph_demo.age({"attestation": "x", "ageDays": ""}), "Unknown")

    def test_marks_are_two_letters(self):
        self.assertEqual(graph_demo.mark("claude-desktop"), "CD")
        self.assertEqual(graph_demo.mark("cursor"), "CU")


# SHA-256 of the files copied unchanged from the Control Centre theme
# (REUSE.toml records where from); the others are adapted.
VENDORED_UNCHANGED = {
    "styles.css": "aa1c55c9073f543913ea635fce49dbcf9533898a4879dfd5022a514607defa55",
    "theme-init.js": "f483ddd61e9b9db7954b248b8d782c72803476e5dc0251289b67e03c15040805",
    "skeletonic.min.css": "116dcdcf51009485eb2dbb6f5c773856f437d972ef277b31e2ee4ef587e1fb09",
    "main.js": "116f7d1adcd3b1b72b0bfc13a46a192fc313b270d643904de77ebd3d818b9369",
}


class Vendored(unittest.TestCase):
    def test_unchanged_files_are_the_themes_byte_for_byte(self):
        for name, digest in VENDORED_UNCHANGED.items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((LAYOUTS / name).read_bytes()).hexdigest(), digest)


class Main(unittest.TestCase):
    def test_writes_the_page(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "export.json", Path(d) / "content" / "index.md"
            src.write_text(json.dumps(EXPORT))
            with contextlib.redirect_stdout(io.StringIO()):
                graph_demo.main(["graph_demo.py", str(src), str(out), "v0.0.7"])
            self.assertIn("passmcp-graph 0.0.7", fields(out.read_text())["lead"])

    def test_refuses_a_bad_export_with_its_name(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "export.json"
            src.write_text(json.dumps({**EXPORT, "shareSafe": False}))
            with self.assertRaises(SystemExit) as e:
                graph_demo.main(["graph_demo.py", str(src), str(Path(d) / "out.md"), "0.0.7"])
            self.assertIn("share-safe", str(e.exception.code))

    def test_usage(self):
        with self.assertRaises(SystemExit) as e:
            graph_demo.main(["graph_demo.py"])
        self.assertIn("usage", str(e.exception.code))


if __name__ == "__main__":
    unittest.main()
