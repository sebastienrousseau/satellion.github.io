# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Render the passmcp family table from passmcp's ecosystem.json.

usage: family.py <ecosystem.json> <family.html> <version> [--check]

passmcp's ecosystem.json is the family's single record of its components,
what each is for and whether it is released. The table on the company page
and on passmcp's page is rendered from it, so the site never states a
status the manifest does not. <version> is the family's lockstep version,
the passmcp release the site is built against; released rows link it.

Both manifest schemas are read. Schema 2 names each row's repository and
says released, unreleased or rejected. Schema 1, which passmcp 0.0.1
published, has no repository field and said shipping and planned; its rows
are read as the same statuses and its repository taken to be its name.

With --check, nothing is written: the script fails when <family.html>
differs from what the manifest renders.
"""

import html
import json
import re
import sys
from pathlib import Path

REPO = "https://github.com/sebastienrousseau"
SCHEMAS = (1, 2)
# Schema 1's words for schema 2's statuses.
STATUSES = {
    "released": "released",
    "shipping": "released",
    "unreleased": "unreleased",
    "planned": "unreleased",
    "rejected": "rejected",
}
# Schema 1 has no repository field. Every row but this site's is named
# after its repository; the site is named after its domain.
SCHEMA_1_REPOSITORIES = {"satellion.com": "satellion.github.io"}
# What GitHub allows in a repository name.
REPOSITORY = re.compile(r"[A-Za-z0-9._-]+")
NUMBERS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]


class ManifestError(ValueError):
    """The manifest cannot be read as the family table: wrong shape or value."""


def text_field(entry, key, default=None):
    """A string field of a manifest row, or a ManifestError naming the row."""
    value = entry.get(key, default)
    if not isinstance(value, str):
        raise ManifestError(f"{entry.get('name')!r}: {key} is not a string")
    return value


def row(entry):
    """One manifest row as the table needs it, whichever schema wrote it."""
    if not isinstance(entry, dict):
        raise ManifestError(f"a repositories entry is not an object: {entry!r}")
    name = text_field(entry, "name")
    status = entry.get("status")
    status = STATUSES.get(status) if isinstance(status, str) else None
    if status is None:
        raise ManifestError(f"{name}: unknown status {entry.get('status')!r}")
    repository = text_field(entry, "repository", "") or SCHEMA_1_REPOSITORIES.get(name, name)
    # The repository becomes part of an href: a GitHub repository name, and
    # nothing that could leave the attribute or the account's path.
    if not REPOSITORY.fullmatch(repository) or repository in (".", ".."):
        raise ManifestError(f"{name}: repository {repository!r} is not a repository name")
    return {
        "name": name,
        "url": f"{REPO}/{repository}",
        "status": status,
        "role": text_field(entry, "role", ""),
    }


def load(text):
    """The manifest's schema version and its rows, normalised."""
    try:
        manifest = json.loads(text)
    except RecursionError:
        raise ManifestError("the manifest is nested too deeply to read") from None
    if not isinstance(manifest, dict):
        raise ManifestError("the manifest is not a JSON object")
    schema = manifest.get("schema_version")
    if schema not in SCHEMAS:
        raise ManifestError(f"unsupported ecosystem.json schema_version {schema!r}; this reads {SCHEMAS}")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list):
        raise ManifestError("the manifest has no repositories list")
    return schema, [row(e) for e in repositories]


def status_cell(r, version):
    if r["status"] == "released":
        return f'<a href="{r["url"]}/releases/tag/v{version}" rel="noopener">Released in {version}</a>'
    return f'<a href="{r["url"]}/blob/main/CHANGELOG.md" rel="noopener">Not yet released</a>'


def component_row(r, version):
    name, role = html.escape(r["name"]), html.escape(r["role"])
    link = f'<a href="{r["url"]}" rel="noopener">{name}</a>'
    return f'        <tr><th scope="row">{link}</th><td>{role}</td><td>{status_cell(r, version)}</td></tr>'


def table(label, caption, head, rows):
    # ssg-table-scroll is SSG's own wrapper class: a page that carries it is
    # left alone, so SSG does not nest a second region labelled "Table,
    # scrollable horizontally" inside this one.
    return "\n".join(
        [
            f'  <div class="container"><div class="table-scroll ssg-table-scroll" role="region" aria-label="{label}, scrollable horizontally" tabindex="0">',
            "    <table>",
            f'      <caption class="visually-hidden">{caption}</caption>',
            f'      <thead><tr><th scope="col">Component</th><th scope="col">Purpose</th><th scope="col">{head}</th></tr></thead>',
            "      <tbody>",
            *rows,
            "      </tbody>",
            "    </table>",
            "  </div></div>",
        ]
    )


def render(schema, rows, version):
    version = version.removeprefix("v")
    built = [r for r in rows if r["status"] != "rejected"]
    count = NUMBERS[len(built)].capitalize() if len(built) < len(NUMBERS) else str(len(built))
    parts = [
        f"<!-- Generated by scripts/family.py from passmcp's ecosystem.json (schema {schema}) at",
        f"     {version}. Do not edit: run make family. -->",
        '<section class="section section-soft" id="ecosystem" aria-labelledby="ecosystem-heading">',
        f'  <div class="container split-heading"><div><p class="eyebrow">The passmcp family</p><h2 id="ecosystem-heading">{count} components, one version.</h2></div><p class="lead">The family moves in lockstep: one version across every component, released together. Each status links to its release, or to the changelog that tracks what is not released yet.</p></div>',
        table(
            "The passmcp family",
            "The components of the passmcp family, what each is for, and its release status",
            "Status",
            [component_row(r, version) for r in built],
        ),
    ]
    # Rejected components are recorded in passmcp's docs/ecosystem.md; the
    # site lists only what the family is.
    return "\n".join(parts + ["</section>", ""])


def main(argv):
    args = [a for a in argv[1:] if a != "--check"]
    if len(args) != 3:
        sys.exit(__doc__)
    manifest, out, version = args
    try:
        schema, rows = load(Path(manifest).read_text())
    except ValueError as e:
        sys.exit(f"family: {manifest}: {e}")
    new = render(schema, rows, version)
    if "--check" not in argv[1:]:
        Path(out).write_text(new)
        print(f"family: {out} written from {manifest} (schema {schema})")
        return
    if Path(out).read_text() != new:
        sys.exit(f"family: {out} disagrees with {manifest}; run make family")
    print(f"family: {out} matches {manifest} (schema {schema})")


if __name__ == "__main__":
    main(sys.argv)
