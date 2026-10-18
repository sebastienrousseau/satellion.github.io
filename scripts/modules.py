# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Check that every Go module path on satellion.com resolves.

usage: modules.py <built site directory>

Go fetches https://satellion.com/<module>?go-get=1 and reads one meta tag,
go-import, to learn where the source lives. A page missing it, or naming
the wrong repository, breaks `go install` for everyone, and nothing else
would notice until a user did. The build fails instead.
"""

import sys
from pathlib import Path

REPO = "https://github.com/sebastienrousseau"
# One page per Go module in the family. passmcp-action is not a Go module
# (it is a GitHub Action and a GitLab CI template), so it has no page here.
ROOTS = [
    "passmcp",
    "passmcp-reporting",
    "passmcp-server",
    "passmcp-graph",
    "passmcp-registry",
    "passmcp-lsp",
    "passmcp-census",
]
# A nested module (its own go.mod in a subdirectory) is fetched at its own
# path, so it needs its own page. The tag on it names the repository root:
# Go accepts a go-import prefix of the path it asked for, then finds the
# module in the subdirectory.
NESTED = {"passmcp-reporting/integrations/agentgateway-extmcp": "passmcp-reporting"}
MODULES = ROOTS + list(NESTED)


def root_of(module):
    return NESTED.get(module, module)


def expected(module):
    r = root_of(module)
    return f'<meta name="go-import" content="satellion.com/{r} git {REPO}/{r}" />'


def problems(site):
    out = []
    for m in MODULES:
        page = Path(site) / m / "index.html"
        if not page.is_file():
            out.append(f"{m}: no page at /{m}/")
            continue
        html = page.read_text()
        if expected(m) not in html:
            out.append(f"{m}: /{m}/ has no go-import tag for satellion.com/{root_of(m)}")
        if html.count('name="go-import"') != 1:
            out.append(f"{m}: /{m}/ must carry exactly one go-import tag")
    return out


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    found = problems(argv[1])
    for p in found:
        print(f"modules: {p}", file=sys.stderr)
    if found:
        sys.exit(1)
    print(f"modules: {len(MODULES)} Go module paths resolve to their repositories")


if __name__ == "__main__":
    main(sys.argv)
