# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""The site's main stylesheet is Skeletonic Stylus 3.0.0's core.

_layouts/skeletonic.min.css is the core build of Skeletonic Stylus 3.0.0
(css/core/skeletonic.min.css in @sebastienrousseau/skeletonic-stylus),
the same file the SSG theme suite pins for every gallery theme, and every
page shell loads it before the site's own styles.css, which only builds on
its tokens. A copy edited by hand, or a shell that drops or reorders it,
fails here.
Run: python3 -m unittest discover -s scripts
"""

import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
LAYOUTS = ROOT / "_layouts"
# sha256 of css/core/skeletonic.min.css in skeletonic-stylus 3.0.0's
# package, as ssg-themes' scripts/validate.py pins it.
SKELETONIC_3_0_0 = "116dcdcf51009485eb2dbb6f5c773856f437d972ef277b31e2ee4ef587e1fb09"
SHELLS = ("base.html", "base-company.html")
STYLESHEET = re.compile(r'<link rel="stylesheet" href="\{\{site_path\}\}([^"]+)" />')


class Skeletonic(unittest.TestCase):
    def test_the_core_is_skeletonic_3_0_0_byte_for_byte(self):
        digest = hashlib.sha256((LAYOUTS / "skeletonic.min.css").read_bytes()).hexdigest()
        self.assertEqual(digest, SKELETONIC_3_0_0)

    def test_every_shell_loads_skeletonic_then_the_sites_styles(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                sheets = STYLESHEET.findall((LAYOUTS / shell).read_text())
                self.assertEqual(sheets[:2], ["skeletonic.min.css", "styles.css"])

    def test_the_sites_styles_import_nothing_else(self):
        # styles.css builds on Skeletonic's tokens; another framework
        # pulled in underneath would no longer be "Skeletonic for main CSS".
        self.assertNotIn("@import", (LAYOUTS / "styles.css").read_text())


if __name__ == "__main__":
    unittest.main()
