# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Every page's footer links the repository the page is about.

footer_links.py runs over the built site in `make core`. These tests hold
its rules, and hold every content page to a footer_repo and footer_license
of its own, with the repository its path names.
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
import footer_links

ROOT = Path(__file__).parent.parent
GH = "https://github.com/sebastienrousseau"


def footer(repo, policy_repo=None):
    policy_repo = policy_repo or repo
    return (
        f'<main><a href="{GH}/passmcp">passmcp</a></main><footer>'
        f'<a href="{GH}/{repo}" rel="noopener">Source on GitHub</a>'
        f'<a href="{GH}/{policy_repo}/blob/main/SECURITY.md" rel="noopener">Security policy</a></footer>'
    )


def front_matter(page):
    head = page.read_text().split("---\n")[1]
    return dict(re.findall(r'^([a-z_-]+): "(.*)"$', head, re.MULTILINE))


class RepoFor(unittest.TestCase):
    def test_paths_name_their_repositories(self):
        cases = {
            "index.html": "satellion.github.io",
            "passmcp/index.html": "passmcp",
            "passmcp-lsp/index.html": "passmcp-lsp",
            "passmcp-reporting/integrations/agentgateway-extmcp/index.html": "passmcp-reporting",
            "graph/v1/index.html": "passmcp-reporting",
            "attestation/mcp-evaluation/v1/index.html": "passmcp-reporting",
            "elsewhere/index.html": None,
        }
        for path, repo in cases.items():
            with self.subTest(path=path):
                self.assertEqual(footer_links.repo_for(path), repo)


class FooterProblems(unittest.TestCase):
    def test_the_pages_own_repository_passes(self):
        self.assertEqual(footer_links.footer_problems(footer("passmcp-lsp"), "passmcp-lsp"), [])

    def test_another_projects_policy_is_found(self):
        found = footer_links.footer_problems(footer("passmcp-lsp", policy_repo="passmcp"), "passmcp-lsp")
        self.assertEqual(
            found, ["'Security policy' links passmcp/blob/main/SECURITY.md, want passmcp-lsp/blob/main/SECURITY.md"]
        )

    def test_links_outside_the_footer_are_not_read(self):
        found = footer_links.footer_problems(footer("passmcp"), "passmcp-lsp")
        self.assertEqual(len(found), 2)

    def test_a_missing_link_is_found(self):
        self.assertEqual(
            footer_links.footer_problems("<footer></footer>", "passmcp"),
            ["no 'Source on GitHub' link in the footer", "no 'Security policy' link in the footer"],
        )


class Site(unittest.TestCase):
    def build(self, d, pages):
        for path, html in pages.items():
            (Path(d) / path).parent.mkdir(parents=True, exist_ok=True)
            (Path(d) / path).write_text(html)

    def test_copied_pages_are_skipped_and_unknown_ones_found(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(
                d,
                {
                    "index.html": footer("satellion.github.io"),
                    "passmcp/docs/index.html": "<footer>MkDocs</footer>",
                    "passmcp-graph/demo/index.html": "<footer>demo</footer>",
                    "elsewhere/index.html": footer("passmcp"),
                },
            )
            found = footer_links.problems(d)
            self.assertEqual(
                found, ["elsewhere/index.html: no repository is known for this page; add it to footer_links.py"]
            )

    def test_main_passes_and_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d, {"index.html": footer("satellion.github.io")})
            with contextlib.redirect_stdout(io.StringIO()) as out:
                footer_links.main(["footer_links.py", d])
            self.assertIn("every page", out.getvalue())
            self.build(d, {"passmcp-lsp/index.html": footer("passmcp")})
            with self.assertRaises(SystemExit) as e:
                footer_links.main(["footer_links.py", d])
            self.assertIn("passmcp-lsp/index.html", str(e.exception.code))
        with self.assertRaises(SystemExit):
            footer_links.main(["footer_links.py"])


class ContentPages(unittest.TestCase):
    def test_every_page_names_its_repository_and_licence(self):
        for page in sorted((ROOT / "content").rglob("index.md")):
            rel = page.relative_to(ROOT / "content").with_suffix(".html").as_posix()
            with self.subTest(page=rel):
                fields = front_matter(page)
                self.assertEqual(fields.get("footer_repo"), footer_links.repo_for(rel))
                self.assertRegex(fields.get("footer_license", ""), r"(GPL|AGPL|Apache|MIT|CC-BY)")

    def test_no_footer_names_a_repository_of_its_own(self):
        for name in ("footer.html", "footer-company.html"):
            with self.subTest(footer=name):
                text = (ROOT / "_layouts" / name).read_text()
                self.assertNotRegex(text, r"sebastienrousseau/passmcp[a-z-]*/(issues|blob|security)")
                self.assertIn("{{footer_repo}}", text)


if __name__ == "__main__":
    unittest.main()
