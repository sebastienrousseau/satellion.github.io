# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Fuzz family.py, the one script that writes another repository's text
into the site's markup, with Atheris.

usage: fuzz_family.py CORPUS_DIR [libFuzzer flags, e.g. -max_total_time=120]

Whatever bytes arrive as passmcp's ecosystem.json, family.load either
refuses them with ValueError, the error main reports, or returns rows that
render to the family table's own markup and nothing else: only the tags and
attributes the table uses, and every link inside the account on GitHub.
Anything else, a crash or markup the manifest put there, is a finding.

Atheris ships wheels for Linux on x86-64 only, so CI runs the fuzzer;
test_fuzz_family.py runs the same check over the seeds anywhere.
"""

import html.parser
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import family

# The markup render writes, and the attributes each element carries.
ALLOWED = {
    "section": {"class", "id", "aria-labelledby"},
    "div": {"class", "role", "aria-label", "tabindex"},
    "p": {"class"},
    "h2": {"id"},
    "table": set(),
    "caption": {"class"},
    "thead": set(),
    "tbody": set(),
    "tr": set(),
    "th": {"scope"},
    "td": set(),
    "a": {"href", "rel"},
}

SEEDS = [
    (
        b'{"schema_version": 2, "repositories": [{"name": "passmcp", "repository": "passmcp",'
        b' "status": "released", "role": "The engine."}, {"name": "passmcp-lsp", "status":'
        b' "unreleased", "role": "A <b>language</b> server & more."}, {"name": "w",'
        b' "status": "rejected"}]}'
    ),
    (
        b'{"schema_version": 1, "repositories": [{"name": "satellion.com", "status": "shipping",'
        b' "role": "The site."}, {"name": "x", "status": "planned"}]}'
    ),
]


class Markup(html.parser.HTMLParser):
    """Every start tag in a document, with its attributes."""

    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def problems(out):
    """What in rendered markup the table itself would never write."""
    parser = Markup()
    parser.feed(out)
    found = []
    for tag, attrs in parser.tags:
        if tag not in ALLOWED or not set(attrs) <= ALLOWED[tag]:
            found.append(f"<{tag} {sorted(attrs)}>")
        href = attrs.get("href")
        if href is not None and not href.startswith(family.REPO + "/"):
            found.append(f"href {href!r}")
    return found


def check(data):
    """One fuzz input: refused with ValueError, or rendered as the table."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return
    try:
        schema, rows = family.load(text)
    except ValueError:
        return
    found = problems(family.render(schema, rows, "0.0.8"))
    if found:
        raise AssertionError(f"rendered markup the table never writes: {found}")


def seed(corpus):
    """Write the seeds into an empty corpus directory."""
    corpus.mkdir(parents=True, exist_ok=True)
    if not any(corpus.iterdir()):
        for i, s in enumerate(SEEDS):
            (corpus / f"seed-{i}.json").write_bytes(s)


def main(argv):
    import atheris

    if len(argv) < 2 or argv[1].startswith("-"):
        sys.exit(__doc__)
    seed(Path(argv[1]))
    atheris.instrument_all()
    atheris.Setup(argv, check)
    atheris.Fuzz()


if __name__ == "__main__":
    main(sys.argv)
