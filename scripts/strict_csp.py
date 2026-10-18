# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Fail when a built page needs more than the site's policy allows.

usage: strict_csp.py [--header-only] <site directory>

satellion.com allows scripts, styles and connections from its own origin
only, and runs no analytics. Every page carries that policy as a meta tag
(_layouts/csp.html); a browser applies it as well as whatever header the
edge sends, so a beacon an edge proxy injects is blocked.

This reads every HTML file under the directory and fails on:

- a page whose meta policy is missing, differs from POLICY, or names a
  source twice in one directive;
- anything either policy blocks: an inline <script>, a <style> element, a
  style or event-handler attribute, a javascript: URL, or a script,
  stylesheet, image or frame loaded from another origin.

A page that breaks a rule renders broken in production, as the first
passmcp-graph demo did, while looking fine from a file or a server without
the header. JSON-LD (<script type="application/ld+json">) is data, not
script, and is allowed. Links (<a href>) may go anywhere: following one
loads nothing.

--header-only checks pages another project generates and the site copies
in (passmcp's sample report): they need nothing the header blocks, but
carry no meta policy of the site's, so that part is not asked of them.

It also fails when the site ships a header file from SSG's [edge_headers]
(EDGE_HEADER_FILES), whose policy would disagree with this one.
"""

import sys
from html.parser import HTMLParser
from pathlib import Path

# The policy, directive by directive: own origin only. frame-ancestors and
# upgrade-insecure-requests have no effect in a meta tag; the header carries
# them.
POLICY = {
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
DATA_SCRIPTS = {"application/ld+json"}
# Elements whose URL attribute makes the page load something.
LOADS = {
    "script": "src",
    "img": "src",
    "iframe": "src",
    "source": "src",
    "link": "href",
}
# Header files SSG's [edge_headers] writes for Netlify, Cloudflare Workers
# and Vercel. Their policy is SSG's default, not POLICY, and the site's
# host applies none of them, so none may ship.
EDGE_HEADER_FILES = ("_headers", ".ssg/edge/wrangler-headers.toml", ".ssg/edge/vercel-headers.json")
# <link> relations that only describe the page and load nothing.
INERT_LINKS = {"canonical", "alternate", "author", "license", "sbom"}


def offsite(url):
    """True when url names another origin or runs script."""
    url = url.strip().lower()
    return url.startswith(("http:", "https:", "//", "javascript:"))


def parse_policy(text):
    """The policy as {directive: [sources]}, in the order written."""
    out = {}
    for part in text.split(";"):
        words = part.split()
        if words:
            out.setdefault(words[0].lower(), []).extend(words[1:])
    return out


def policy_problems(text):
    """What is wrong with one meta policy, one message each."""
    policy = parse_policy(text)
    out = [
        f"{name} names a source twice: {' '.join(sources)}"
        for name, sources in policy.items()
        if len(set(sources)) != len(sources)
    ]
    if {k: sorted(set(v)) for k, v in policy.items()} != {k: sorted(v) for k, v in POLICY.items()}:
        out.append(f"meta policy differs from the site's: {text}")
    return out


def inline_attributes(tag, attrs):
    """A style or event-handler attribute on the element, one message each."""
    return [f"<{tag} {name}=...>: inline attribute" for name in attrs if name == "style" or name.startswith("on")]


class Page(HTMLParser):
    """Collects what the policy would block, one message each."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocked = []
        self.policies = []
        self.inline_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.blocked += inline_attributes(tag, a)
        if tag == "style":
            self.blocked.append("<style>: inline stylesheet")
        self.inline_script = tag == "script" and not a.get("src") and (a.get("type") or "") not in DATA_SCRIPTS
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "content-security-policy":
            self.policies.append(a.get("content") or "")
        self.check_url(tag, a)

    def check_url(self, tag, a):
        if tag not in LOADS:
            return
        if tag == "link" and set((a.get("rel") or "").split()) <= INERT_LINKS:
            return
        url = a.get(LOADS[tag]) or ""
        if offsite(url):
            self.blocked.append(f"<{tag} {LOADS[tag]}={url}>: not same-origin")

    def handle_data(self, data):
        if self.inline_script and data.strip():
            self.blocked.append("<script>: inline script")
        self.inline_script = False

    def handle_endtag(self, tag):
        self.inline_script = False


def page_problems(text, meta=True):
    """Everything wrong with one page; with meta False, only what is blocked."""
    parser = Page()
    parser.feed(text)
    out = list(parser.blocked)
    if not meta:
        return out
    if len(parser.policies) != 1:
        out.append(f"{len(parser.policies)} meta policies, want 1")
    for policy in parser.policies:
        out += policy_problems(policy)
    return out


def problems(site, meta=True):
    """Every problem on every page under site, prefixed by its file."""
    out = [
        f"{name}: a header file with SSG's policy, not the site's; remove [edge_headers]"
        for name in EDGE_HEADER_FILES
        if (Path(site) / name).exists()
    ]
    for page in sorted(Path(site).rglob("*.html")):
        out += [f"{page.relative_to(site)}: {p}" for p in page_problems(page.read_text(encoding="utf-8"), meta)]
    return out


def main(argv):
    args = [a for a in argv[1:] if a != "--header-only"]
    if len(args) != 1:
        sys.exit(__doc__)
    site = Path(args[0])
    if not site.is_dir():
        sys.exit(f"strict_csp: {site} is not a directory")
    found = problems(site, meta="--header-only" not in argv[1:])
    if found:
        sys.exit("strict_csp: pages the site's policy does not cover:\n" + "\n".join(found))
    print(f"strict_csp: every page in {site} carries the site's policy and needs nothing it blocks")


if __name__ == "__main__":
    main(sys.argv)
