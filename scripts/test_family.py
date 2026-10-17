# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""The site's family table agrees with the README's ecosystem table.

_layouts/family.html is shown on the company page and on passmcp's page.
These tests hold it to the README: the same components, each linking its
repository, each with a concrete status that links its release or the
changelog tracking it, and a Go module page for every Go component.
It is rendered by family.py from passmcp's ecosystem.json, which is read
in both of its schemas.
Run: python3 -m unittest discover -s scripts
"""
import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import family
import modules

ROOT = Path(__file__).parent.parent
REPO = modules.REPO
ROW = re.compile(r'<tr><th scope="row"><a href="([^"]+)" rel="noopener">([^<]+)</a></th><td>[^<]+</td><td>(.*?)</td></tr>')


def readme_components():
    text = (ROOT / "README.md").read_text()
    section = text.split("## The satellion.com ecosystem", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^\| \[([^\]]+)\]\((https://github\.com/[^)]+)\) \|", section, re.M)


def site_rows():
    return ROW.findall((ROOT / "_layouts" / "family.html").read_text())


class Family(unittest.TestCase):
    def test_the_readme_lists_nine_components(self):
        self.assertEqual(len(readme_components()), 9)

    def test_the_site_lists_the_readmes_components_in_order_with_their_repositories(self):
        site = [(name, url) for url, name, _ in site_rows()]
        self.assertEqual(site, readme_components())

    def test_every_status_is_concrete_and_links_its_evidence(self):
        versions = set(re.findall(r"Released in (\d+\.\d+\.\d+)", (ROOT / "_layouts" / "family.html").read_text()))
        self.assertEqual(len(versions), 1, "the family is in lockstep: one version")
        v = versions.pop()
        for url, name, status in site_rows():
            with self.subTest(component=name):
                released = f'<a href="{url}/releases/tag/v{v}" rel="noopener">Released in {v}</a>'
                unreleased = f'<a href="{url}/blob/main/CHANGELOG.md" rel="noopener">Not yet released</a>'
                self.assertIn(status, (released, unreleased))

    def test_no_vague_status_appears_on_either_page(self):
        vague = re.compile(r"\b(Shipping|Shipped|Available|Planned|Coming soon)\b")
        for path in ("_layouts/family.html", "_layouts/index.html", "_layouts/company.html"):
            with self.subTest(path=path):
                self.assertIsNone(vague.search((ROOT / path).read_text()))

    def test_every_go_component_has_a_module_page(self):
        names = {name for name, _ in readme_components()}
        for m in modules.ROOTS:
            with self.subTest(module=m):
                self.assertIn(m, names)
                self.assertIn((m, f"{REPO}/{m}"), readme_components())

    def test_both_pages_include_the_family_table(self):
        for layout in ("company.html", "index.html"):
            with self.subTest(layout=layout):
                self.assertIn("{{> family}}", (ROOT / "_layouts" / layout).read_text())


def manifest(schema, rows):
    return json.dumps({"schema_version": schema, "family": "passmcp", "repositories": rows})


SCHEMA_1 = manifest(1, [
    {"name": "passmcp", "status": "shipping", "role": "The engine."},
    {"name": "satellion.com", "status": "shipping", "role": "The site."},
    {"name": "passmcp-lsp", "status": "planned", "role": "A language server."},
    {"name": "passmcp-wasm", "status": "rejected", "role": "A browser build.", "rejected_because": "CORS."},
])
SCHEMA_2 = manifest(2, [
    {"name": "passmcp", "repository": "passmcp", "status": "released", "role": "The engine."},
    {"name": "satellion.com", "repository": "satellion.github.io", "status": "released", "role": "The site."},
    {"name": "passmcp-lsp", "repository": "passmcp-lsp", "status": "unreleased", "role": "A language server."},
    {"name": "passmcp-wasm", "repository": "passmcp-wasm", "status": "rejected", "role": "A browser build.",
     "rejected_because": "CORS."},
])


class Render(unittest.TestCase):
    def test_both_schemas_read_as_the_same_rows(self):
        s1, rows1 = family.load(SCHEMA_1)
        s2, rows2 = family.load(SCHEMA_2)
        self.assertEqual((s1, s2), (1, 2))
        self.assertEqual(rows1, rows2)
        self.assertEqual([r["status"] for r in rows2], ["released", "released", "unreleased", "rejected"])
        self.assertEqual(rows1[1]["url"], f"{REPO}/satellion.github.io")

    def test_both_schemas_render_the_same_table_but_for_the_schema_note(self):
        one = family.render(*family.load(SCHEMA_1), "v0.0.2").replace("(schema 1)", "")
        two = family.render(*family.load(SCHEMA_2), "0.0.2").replace("(schema 2)", "")
        self.assertEqual(one, two)

    def test_rows_link_their_release_or_changelog(self):
        out = family.render(*family.load(SCHEMA_2), "v0.0.2")
        self.assertIn(f'<a href="{REPO}/passmcp/releases/tag/v0.0.2" rel="noopener">Released in 0.0.2</a>', out)
        self.assertIn(f'<a href="{REPO}/passmcp-lsp/blob/main/CHANGELOG.md" rel="noopener">Not yet released</a>', out)
        self.assertIn("Three components, one version.", out)
        self.assertNotIn(f"{REPO}/passmcp-wasm", out)

    def test_rejected_components_are_not_on_the_page(self):
        # The site lists what the family is; what it decided against is
        # recorded in passmcp's docs/ecosystem.md, not published here.
        out = family.render(*family.load(SCHEMA_2), "0.0.2")
        self.assertNotIn("Considered and rejected", out)
        self.assertNotIn("passmcp-wasm", out)

    def test_the_table_is_its_own_single_scroll_region(self):
        # The region carries SSG's wrapper class, so SSG does not nest a
        # second, identically labelled region inside it: one tab stop, one
        # announced landmark.
        out = family.render(*family.load(SCHEMA_2), "0.0.2")
        self.assertIn('<div class="table-scroll ssg-table-scroll" role="region" '
                      'aria-label="The passmcp family, scrollable horizontally" tabindex="0">', out)
        self.assertEqual(out.count('role="region"'), 1)

    def test_a_large_family_is_counted_in_digits(self):
        rows = [{"name": f"c{i}", "status": "released"} for i in range(13)]
        self.assertIn("13 components", family.render(*family.load(manifest(2, rows)), "0.0.2"))

    def test_server_text_is_escaped(self):
        rows = [{"name": "x", "status": "released", "role": "<script>&"}]
        out = family.render(*family.load(manifest(2, rows)), "0.0.2")
        self.assertIn("&lt;script&gt;&amp;", out)
        self.assertNotIn("<script>", out)

    def test_an_unknown_status_or_schema_is_refused(self):
        with self.assertRaisesRegex(ValueError, "x: unknown status 'someday'"):
            family.load(manifest(2, [{"name": "x", "status": "someday"}]))
        with self.assertRaisesRegex(ValueError, "unsupported ecosystem.json schema_version 3"):
            family.load(manifest(3, []))

    def test_a_malformed_manifest_is_refused_not_crashed(self):
        # Each of these crashed with AttributeError, KeyError or TypeError
        # instead of the "family: <file>: <reason>" exit main promises.
        for text in ["[]", '"x"', json.dumps({"schema_version": 2}),
                     json.dumps({"schema_version": 2, "repositories": 5}),
                     manifest(2, ["passmcp"]),
                     manifest(2, [{"status": "released"}]),
                     manifest(2, [{"name": 7, "status": "released"}]),
                     manifest(2, [{"name": "x", "status": "released", "role": 3}]),
                     manifest(2, [{"name": "x", "status": ["released"]}])]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                family.load(text)

    def test_deeply_nested_json_is_refused_not_crashed(self):
        # json.loads raises RecursionError, not ValueError, past Python's
        # recursion limit.
        with self.assertRaisesRegex(ValueError, "nested too deeply"):
            family.load("[" * 100_000)

    def test_a_repository_name_cannot_leave_its_link(self):
        # The repository goes into an href; a quote in it would add
        # attributes to the site's markup.
        for repository in ['x" onmouseover="alert(1)', "../x", "x/y", "..", "a b"]:
            rows = [{"name": "x", "repository": repository, "status": "released"}]
            with self.subTest(repository=repository), \
                    self.assertRaisesRegex(ValueError, "x: repository"):
                family.load(manifest(2, rows))

    def test_main_writes_then_checks_and_fails_on_drift(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d, "ecosystem.json"), Path(d, "family.html")
            src.write_text(SCHEMA_2)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                family.main(["family.py", str(src), str(out), "v0.0.2"])
                family.main(["family.py", str(src), str(out), "v0.0.2", "--check"])
            self.assertIn("matches", stdout.getvalue())
            with self.assertRaisesRegex(SystemExit, "disagrees with"):
                family.main(["family.py", str(src), str(out), "v0.0.3", "--check"])
            src.write_text(manifest(9, []))
            with self.assertRaisesRegex(SystemExit, "unsupported"):
                family.main(["family.py", str(src), str(out), "v0.0.2"])

    def test_main_without_its_arguments_prints_the_usage(self):
        with self.assertRaisesRegex(SystemExit, "usage"):
            family.main(["family.py"])


if __name__ == "__main__":
    unittest.main()
