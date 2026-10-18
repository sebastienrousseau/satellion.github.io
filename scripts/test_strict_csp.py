# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Every page carries the site's one policy and needs nothing it blocks.

strict_csp.py runs over the built site in `make core` and over the
passmcp-graph demo in `make graph-site`. These tests hold its rules, and
hold the layouts to the single policy in _layouts/csp.html: the site's own
origin only. The site runs no analytics, so the policy names no other
origin and blocks a beacon an edge proxy injects.
Run: python3 -m unittest discover -s scripts
"""

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import strict_csp

ROOT = Path(__file__).parent.parent
PARTIAL = ROOT / "_layouts" / "csp.html"
SHELLS = (
    ROOT / "_layouts" / "base.html",
    ROOT / "_layouts" / "base-company.html",
    ROOT / "graph-demo" / "_layouts" / "base.html",
)
META = re.compile(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)"')
# The policy, written out here rather than read from strict_csp.POLICY, so
# a change to both the partial and the checker still fails a test.
EXPECTED = {
    "default-src": ["'self'"],
    "base-uri": ["'none'"],
    "object-src": ["'none'"],
    "script-src": ["'self'"],
    "style-src": ["'self'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'"],
    "manifest-src": ["'self'"],
    "form-action": ["'self'"],
}
# The only sources a directive may name: keywords and the data: scheme.
NO_ORIGIN = re.compile(r"^('self'|'none'|data:)$")


def page(head="", body=""):
    policy = META.search(PARTIAL.read_text()).group(0) + " />"
    return f"<!DOCTYPE html><html><head>{policy}{head}</head><body>{body}</body></html>"


class Policy(unittest.TestCase):
    def test_the_partial_is_the_policy(self):
        self.assertEqual(strict_csp.policy_problems(META.search(PARTIAL.read_text()).group(1)), [])

    def test_the_partial_and_the_checker_are_the_expected_policy(self):
        partial = strict_csp.parse_policy(META.search(PARTIAL.read_text()).group(1))
        self.assertEqual(partial, EXPECTED)
        self.assertEqual(strict_csp.POLICY, EXPECTED)

    def test_the_policy_names_no_other_origin(self):
        # The site runs no analytics: re-adding Cloudflare's beacon, or any
        # host, to script-src or connect-src fails here.
        partial = strict_csp.parse_policy(META.search(PARTIAL.read_text()).group(1))
        for policy in (partial, strict_csp.POLICY):
            for directive, sources in policy.items():
                with self.subTest(directive=directive):
                    self.assertEqual([s for s in sources if not NO_ORIGIN.match(s)], [])

    def test_the_beacon_is_refused_by_the_checker(self):
        beacon = (
            META.search(PARTIAL.read_text())
            .group(1)
            .replace("script-src 'self'", "script-src 'self' https://static.cloudflareinsights.com")
        )
        self.assertTrue(strict_csp.policy_problems(beacon))

    def test_nothing_inline_is_allowed(self):
        sources = " ".join(s for v in strict_csp.POLICY.values() for s in v)
        for word in ("unsafe-inline", "unsafe-eval", "nonce-", "sha256-"):
            self.assertNotIn(word, sources)

    def test_every_shell_includes_the_partial_and_no_policy_of_its_own(self):
        for shell in SHELLS:
            with self.subTest(shell=shell.name):
                text = shell.read_text()
                self.assertEqual(text.count("{{> csp}}"), 1)
                self.assertNotIn('Content-Security-Policy" content', text)
                self.assertNotIn("form_origin", text)

    def test_a_source_named_twice_is_found(self):
        found = strict_csp.policy_problems(META.search(PARTIAL.read_text()).group(1) + " 'self'")
        self.assertIn("form-action names a source twice: 'self' 'self'", found)

    def test_the_old_same_origin_only_policy_is_found(self):
        old = "default-src 'self'; script-src 'self'; connect-src 'self'"
        self.assertTrue(strict_csp.policy_problems(old))


class Pages(unittest.TestCase):
    def test_a_page_with_the_policy_and_same_origin_assets_passes(self):
        head = '<link rel="stylesheet" href="/s.css"><script src="/m.js"></script>'
        head += '<script type="application/ld+json">{"a": 1}</script><link rel="canonical" href="https://x/">'
        self.assertEqual(
            strict_csp.page_problems(page(head, '<a href="https://example.com/">x</a>')),
            [],
        )

    def test_inline_script_style_and_handlers_are_found(self):
        body = '<script>alert(1)</script><style>p{}</style><p style="x" onclick="y">t</p>'
        found = strict_csp.page_problems(page(body=body))
        self.assertEqual(
            found,
            [
                "<script>: inline script",
                "<style>: inline stylesheet",
                "<p style=...>: inline attribute",
                "<p onclick=...>: inline attribute",
            ],
        )

    def test_assets_from_another_origin_are_found(self):
        head = (
            '<script src="https://static.cloudflareinsights.com/beacon.min.js"></script>'
            '<link rel="stylesheet" href="//cdn.example/s.css"><img src="javascript:x">'
        )
        self.assertEqual(len(strict_csp.page_problems(page(body=head))), 3)

    def test_a_page_without_one_policy_is_found(self):
        self.assertEqual(
            strict_csp.page_problems("<html><head></head></html>"),
            ["0 meta policies, want 1"],
        )


class Main(unittest.TestCase):
    def run_main(self, site):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            strict_csp.main(["strict_csp.py", str(site)])
        return out.getvalue()

    def test_passes_a_clean_site_and_fails_a_broken_one(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a").mkdir()
            (Path(d) / "a" / "index.html").write_text(page())
            self.assertIn("every page", self.run_main(d))
            (Path(d) / "b.html").write_text(page(body="<style></style>"))
            with self.assertRaises(SystemExit) as e:
                self.run_main(d)
            self.assertIn("b.html: <style>: inline stylesheet", str(e.exception.code))

    def test_header_only_skips_the_meta_policy_but_not_what_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "report.html").write_text("<html><head></head><body><p>ok</p></body></html>")
            self.assertIn("every page", self.run_main_args(["--header-only", d]))
            (Path(d) / "report.html").write_text("<html><head><style>p{}</style></head></html>")
            with self.assertRaises(SystemExit) as e:
                self.run_main_args(["--header-only", d])
            self.assertIn("report.html: <style>: inline stylesheet", str(e.exception.code))
            self.assertNotIn("meta policies", str(e.exception.code))

    def run_main_args(self, args):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            strict_csp.main(["strict_csp.py", *args])
        return out.getvalue()

    def test_an_edge_header_file_is_found(self):
        for name in strict_csp.EDGE_HEADER_FILES:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                (Path(d) / name).parent.mkdir(parents=True, exist_ok=True)
                (Path(d) / name).write_text("/*\n  Content-Security-Policy: default-src 'self'\n")
                self.assertEqual(len(strict_csp.problems(d)), 1)

    def test_usage_and_a_missing_directory(self):
        for argv in (["strict_csp.py"], ["strict_csp.py", "/nonexistent/site"]):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                strict_csp.main(argv)


if __name__ == "__main__":
    unittest.main()
