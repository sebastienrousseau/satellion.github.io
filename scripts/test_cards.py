# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Tests for cards.py. Run: python3 -m unittest discover -s scripts

Chrome is replaced by a stub that records its arguments and writes the
screenshot, so the tests cover what cards.py hands the browser without
needing one.
"""

import contextlib
import io
import os
import stat
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cards

STUB = """#!/bin/sh
# Record the arguments, copy the page Chrome was given, write the screenshot.
printf '%s\\n' "$@" > "$(dirname "$0")/args"
for a in "$@"; do
  case "$a" in
    --screenshot=*) : > "${a#--screenshot=}" ;;
    file://*) cp "${a#file://}" "$(dirname "$0")/page.html" ;;
  esac
done
"""


@contextlib.contextmanager
def tree(front='metric_one_value: "131"\n'):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for sub in ("cards", "images", "content/passmcp", "bin"):
            (root / sub).mkdir(parents=True)
        (root / "content/passmcp/index.md").write_text(f"---\n{front}---\n")
        (root / "cards/passmcp.html").write_text("<p>{{checks}} checks</p>")
        (root / "cards/satellion.html").write_text("<p>Satellion</p>")
        chrome = root / "bin/chrome"
        chrome.write_text(STUB)
        chrome.chmod(chrome.stat().st_mode | stat.S_IXUSR)
        with unittest.mock.patch.object(cards, "ROOT", root):
            yield root, str(chrome)


class Cards(unittest.TestCase):
    def test_the_check_count_comes_from_the_product_page(self):
        with tree():
            self.assertEqual(cards.count(), "131")

    def test_a_product_page_without_a_count_is_refused(self):
        with tree(front='title: "passmcp"\n'):
            with self.assertRaises(SystemExit) as e:
                cards.count()
            self.assertIn("no metric_one_value", str(e.exception))

    def test_main_renders_both_cards_and_removes_the_temporary_page(self):
        with tree() as (root, chrome):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                cards.main(["cards.py", chrome])
            self.assertTrue((root / "images/passmcp-card.png").is_file())
            self.assertTrue((root / "images/satellion-card.png").is_file())
            self.assertEqual(sorted(os.listdir(root / "cards")), ["passmcp.html", "satellion.html"])
            self.assertIn("cards: wrote images/satellion-card.png", out.getvalue())
            self.assertIn("--window-size=1200,630", (root / "bin/args").read_text())

    def test_the_count_is_substituted_into_the_card(self):
        with tree() as (root, chrome), contextlib.redirect_stdout(io.StringIO()):
            cards.render(chrome, "passmcp", {"checks": "131"})
            self.assertEqual((root / "bin/page.html").read_text(), "<p>131 checks</p>")

    def test_a_failed_render_still_removes_the_temporary_page(self):
        with tree() as (root, _):
            with self.assertRaises(FileNotFoundError):
                cards.render(str(root / "bin/missing"), "satellion", {})
            self.assertEqual(sorted(os.listdir(root / "cards")), ["passmcp.html", "satellion.html"])


if __name__ == "__main__":
    unittest.main()
