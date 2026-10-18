# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Render the social cards (og:image) from cards/*.html with headless Chrome.

usage: cards.py [path to Chrome]

The passmcp card's check count comes from the product page's front matter,
which make data keeps in step with the release, so the card cannot keep a
figure the product has outgrown. The PNGs are committed; run this after the
count or the wording changes.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def count():
    m = re.search(r'^metric_one_value: "(\d+)"$', (ROOT / "content/passmcp/index.md").read_text(), re.MULTILINE)
    if not m:
        sys.exit("cards: content/passmcp/index.md has no metric_one_value")
    return m.group(1)


def render(chrome, name, values):
    html = (ROOT / "cards" / f"{name}.html").read_text()
    for k, v in values.items():
        html = html.replace("{{" + k + "}}", v)
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=ROOT / "cards", delete=False) as f:
        f.write(html)
        page = Path(f.name)
    out = ROOT / "images" / f"{name}-card.png"
    try:
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--window-size=1200,630",
                f"--screenshot={out}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    finally:
        page.unlink()
    print(f"cards: wrote {out.relative_to(ROOT)}")


def main(argv):
    chrome = argv[1] if len(argv) > 1 else CHROME
    render(chrome, "passmcp", {"checks": count()})
    render(chrome, "satellion", {})


if __name__ == "__main__":
    main(sys.argv)
