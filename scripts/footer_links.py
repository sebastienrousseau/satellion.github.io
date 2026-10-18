# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Fail when a page's footer links another project's source or policy.

usage: footer_links.py <built site directory>

Every page's footer links the source, the issues and the security policy
of the repository the page is about, from the page's footer_repo front
matter. A copied page or a missing key would send a reader who wants to
report a vulnerability in passmcp-lsp to passmcp's policy instead. This
derives the repository from the page's path, independently of the front
matter, and fails when the footer's "Source on GitHub" or "Security
policy" link names another. Pages other projects build and the site
copies in (passmcp's manual and sample report, the passmcp-graph demo)
carry their own footers and are skipped.
"""

import re
import sys
from pathlib import Path

import modules

# The format pages document specifications published in passmcp-reporting.
FORMATS = {"graph": "passmcp-reporting", "attestation": "passmcp-reporting"}
COPIED = ("passmcp/docs/", "passmcp/sample/", "passmcp-graph/demo/")
LINK = re.compile(r'<a href="https://github\.com/sebastienrousseau/([^"/]+)([^"]*)"[^>]*>([^<]+)</a>')
CHECKED = {"Source on GitHub": "", "Security policy": "/blob/main/SECURITY.md"}


def repo_for(path):
    """The repository a page at path (relative, ending index.html) is about."""
    first = path.split("/", 1)[0] if "/" in path else ""
    if first in modules.ROOTS:
        return first
    if first in FORMATS:
        return FORMATS[first]
    return "satellion.github.io" if first == "" else None


def footer_problems(html, repo):
    """What is wrong with one page's footer links, one message each."""
    footer = html[html.rfind("<footer") :]
    links = {text: (r, rest) for r, rest, text in LINK.findall(footer) if text in CHECKED}
    out = []
    for text, rest in CHECKED.items():
        if text not in links:
            out.append(f"no {text!r} link in the footer")
        elif links[text] != (repo, rest):
            out.append(f"{text!r} links {links[text][0]}{links[text][1]}, want {repo}{rest}")
    return out


def problems(site):
    out = []
    for page in sorted(Path(site).rglob("index.html")):
        rel = page.relative_to(site).as_posix()
        if rel.startswith(COPIED):
            continue
        repo = repo_for(rel)
        if repo is None:
            out.append(f"{rel}: no repository is known for this page; add it to footer_links.py")
            continue
        out += [f"{rel}: {p}" for p in footer_problems(page.read_text(encoding="utf-8"), repo)]
    return out


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    found = problems(argv[1])
    if found:
        sys.exit("footer_links: \n" + "\n".join(found))
    print(f"footer_links: every page in {argv[1]} links the source and security policy it is about")


if __name__ == "__main__":
    main(sys.argv)
