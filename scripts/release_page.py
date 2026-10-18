# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Compose a release page in the passmcp family's layout, and publish it.

usage: release_page.py [--publish] [--target SHA] [--note TEXT] vX.Y.Z [asset ...]

The layout is the portfolio's release page format: the title
"satellion.github.io X.Y.Z"; the hand-written "## Highlights ⭐️" from
docs/releases/vX.Y.Z.md; GitHub's generated "## What's Changed" (and
"## New Contributors" when there are any); a "## Checksums" section with
the SHA-256 of every asset on the release or, as for every release of the
site, the sentence that there are none and --note saying what is published
instead; and GitHub's "**Full Changelog**" line last. Only the highlights
are written by hand. This is the Python twin of the Go repositories'
scripts/releasepage.

Without --publish nothing is written: the title goes to stderr and the page
to stdout. --target places a tag that does not exist yet, for a dry run. A
published page is read back, and the script fails unless GitHub shows what
it composed. GitHub's generated notes need a gh token with contents access
even for a dry run.
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

NAME = "satellion.github.io"
HEADING = "## Highlights ⭐️"
FULL = "**Full Changelog**"
NO_ASSETS = "This release attaches no downloadable assets."
RELEASES = Path(__file__).resolve().parent.parent / "docs" / "releases"


class Failure(Exception):
    """A step that cannot go on, with what to tell the operator."""


def gh(*args):
    """Run gh and return its stdout; gh's stderr is passed through."""
    done = subprocess.run(["gh", *args], stdout=subprocess.PIPE, text=True, check=False)
    if done.returncode != 0:
        raise subprocess.CalledProcessError(done.returncode, "gh")
    return done.stdout


def highlights(text):
    """The highlights file from its heading on, without trailing blanks."""
    m = re.search(r"^" + re.escape(HEADING) + r"$", text, re.MULTILINE)
    if not m:
        raise Failure(f"the highlights file has no '{HEADING}' heading")
    return text[m.start() :].strip()


def split_generated(text):
    """GitHub's notes without their Full Changelog line, blank runs folded,
    and that line."""
    kept, full = [], ""
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.rstrip()
        if line.startswith(FULL):
            full = line
        elif line or (kept and kept[-1]):
            kept.append(line)
    return "\n".join(kept).strip(), full


def checksum_body(sums, note):
    """The fenced SHA-256 list, or the no-assets sentence and the note."""
    if not sums:
        return NO_ASSETS + ("\n\n" + note.strip() if note.strip() else "")
    lines = ["SHA-256 of every asset attached to this release:", "", "```text"]
    lines += [f"{digest}  {name}" for name, digest in sums]
    return "\n".join(lines + ["```"])


def compose(highlights_text, generated, sums, note):
    """The page body."""
    changes, full = split_generated(generated)
    if not full:
        raise Failure(f"GitHub's generated notes have no {FULL} line")
    parts = [highlights(highlights_text), changes, "## Checksums", checksum_body(sums, note), full]
    return "\n\n".join(p for p in parts if p) + "\n"


def checksums(files):
    """(name, sha256) of each file, sorted by name as bytes."""
    sums = [(Path(f).name, hashlib.sha256(Path(f).read_bytes()).hexdigest()) for f in files]
    return sorted(sums, key=lambda s: s[0].encode())


def with_repo(*args):
    """The gh arguments, with -R when the repository is known."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    return [*args, "-R", repo] if repo else list(args)


def generated_notes(run, tag, target):
    repo = os.environ.get("GITHUB_REPOSITORY") or "{owner}/{repo}"
    args = ["api", f"repos/{repo}/releases/generate-notes", "-f", f"tag_name={tag}"]
    if target:
        args += ["-f", f"target_commitish={target}"]
    try:
        return run(*args, "--jq", ".body")
    except subprocess.CalledProcessError as e:
        raise Failure(f"generate-notes for {tag} failed") from e


def release_assets(run, tag, given, work):
    """Whether the release exists, and the files to hash: those given, else
    the release's own, downloaded."""
    try:
        names = run(*with_repo("release", "view", tag, "--json", "assets", "--jq", ".assets[].name")).split()
    except subprocess.CalledProcessError:
        return False, given
    if given or not names:
        return True, given
    try:
        run(*with_repo("release", "download", tag, "-D", str(work)))
    except subprocess.CalledProcessError as e:
        raise Failure(f"download the assets of {tag} failed") from e
    return True, [str(Path(work) / n) for n in names]


def publish(run, tag, title, body, exists, work):
    """Create the release or edit it, then read the page back."""
    notes = Path(work) / "notes.md"
    notes.write_text(body)
    verb = ["edit", tag] if exists else ["create", tag, "--verify-tag"]
    try:
        run(*with_repo("release", *verb, "--title", title, "--notes-file", str(notes)))
        got = run(*with_repo("release", "view", tag, "--json", "name,body", "--jq", '.name + "\\n" + .body'))
    except subprocess.CalledProcessError as e:
        raise Failure(f"publish {tag} failed") from e
    if got.replace("\r\n", "\n").strip() != f"{title}\n{body}".strip():
        raise Failure(f"the published page of {tag} is not the composed one")


def parse(argv):
    p = argparse.ArgumentParser(prog="release_page.py", description=__doc__.splitlines()[0])
    p.add_argument("--publish", action="store_true", help="create or edit the release")
    p.add_argument("--target", default="", help="the commit a tag that does not exist yet would point at")
    p.add_argument("--note", default="", help="what is published instead of files")
    p.add_argument("tag", help="the release tag, vX.Y.Z")
    p.add_argument("assets", nargs="*", help="files to hash instead of the release's own")
    args = p.parse_args(argv)
    if not re.fullmatch(r"v\d+\.\d+\.\d+", args.tag):
        p.error(f"{args.tag!r} is not vX.Y.Z")
    return args


def release(args, run, out, err):
    title = f"{NAME} {args.tag[1:]}"
    text = (RELEASES / f"{args.tag}.md").read_text()
    generated = generated_notes(run, args.tag, args.target)
    with tempfile.TemporaryDirectory() as work:
        exists, files = release_assets(run, args.tag, args.assets, work)
        body = compose(text, generated, checksums(files), args.note)
        if args.publish:
            publish(run, args.tag, title, body, exists, work)
            return
    print(f"title: {title}", file=err)
    out.write(body)


def main(argv, run=gh, out=sys.stdout, err=sys.stderr):
    args = parse(argv)
    try:
        release(args, run, out, err)
    except (Failure, OSError) as e:
        print(f"release_page: {e}", file=err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
