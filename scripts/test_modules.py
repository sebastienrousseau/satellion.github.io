# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Tests for modules.py. Run: python3 -m unittest discover -s scripts"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modules


def site(pages):
    d = tempfile.mkdtemp()
    for m, html in pages.items():
        (Path(d) / m).mkdir(parents=True)
        (Path(d) / m / "index.html").write_text(html)
    return d


class Modules(unittest.TestCase):
    def test_every_module_page_with_its_tag_passes(self):
        d = site({m: f"<head>{modules.expected(m)}</head>" for m in modules.MODULES})
        self.assertEqual(modules.problems(d), [])

    def test_a_missing_page_a_wrong_repository_and_a_duplicate_tag_fail(self):
        pages = {m: f"<head>{modules.expected(m)}</head>" for m in modules.MODULES}
        del pages["passmcp-graph"]
        pages["passmcp-server"] = (
            '<meta name="go-import" content="satellion.com/passmcp-server git https://github.com/someone/else" />'
        )
        pages["passmcp"] = pages["passmcp"] * 2
        found = "\n".join(modules.problems(site(pages)))
        self.assertIn("passmcp-graph: no page", found)
        self.assertIn("passmcp-server: /passmcp-server/ has no go-import tag", found)
        self.assertIn("passmcp: /passmcp/ must carry exactly one", found)

    def test_the_committed_pages_declare_the_right_tags(self):
        root = Path(__file__).parent.parent / "content"
        for m in modules.MODULES:
            front = (root / m / "index.md").read_text()
            r = modules.root_of(m)
            self.assertIn(f'go_import: "satellion.com/{r} git {modules.REPO}/{r}"', front)

    def test_a_nested_module_page_must_name_its_repository_root(self):
        nested = "passmcp-reporting/integrations/agentgateway-extmcp"
        pages = {m: f"<head>{modules.expected(m)}</head>" for m in modules.MODULES}
        pages[nested] = f'<meta name="go-import" content="satellion.com/{nested} git {modules.REPO}/{nested}" />'
        found = "\n".join(modules.problems(site(pages)))
        self.assertIn(f"{nested}: /{nested}/ has no go-import tag for satellion.com/passmcp-reporting", found)

    def test_the_language_server_and_the_census_have_module_pages(self):
        for m in ("passmcp-lsp", "passmcp-census"):
            self.assertIn(m, modules.ROOTS)
            front = (Path(__file__).parent.parent / "content" / m / "index.md").read_text()
            self.assertIn(f'go_source: "satellion.com/{m} {modules.REPO}/{m} ', front)

    def test_main_reports_success_on_stdout_and_problems_on_stderr(self):
        good = site({m: f"<head>{modules.expected(m)}</head>" for m in modules.MODULES})
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            modules.main(["modules.py", good])
            with self.assertRaises(SystemExit) as e:
                modules.main(["modules.py", site({})])
        self.assertEqual(e.exception.code, 1)
        self.assertIn(f"{len(modules.MODULES)} Go module paths resolve", out.getvalue())
        self.assertIn("modules: passmcp: no page at /passmcp/", err.getvalue())

    def test_main_without_a_directory_prints_the_usage(self):
        with self.assertRaises(SystemExit) as e:
            modules.main(["modules.py"])
        self.assertIn("usage", str(e.exception))


if __name__ == "__main__":
    unittest.main()
