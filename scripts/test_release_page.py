# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Tests for release_page.py. Run: python3 -m unittest discover -s scripts"""

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import release_page

# The shapes GitHub's notes and a highlights file take: a New Contributors
# section, the runs of blank lines GitHub leaves, an SPDX header.
HIGHLIGHTS = """<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com> -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

## Highlights ⭐️

* **One thing**: It changed for the user.
* **Another thing**: So did this.

"""
GENERATED = """## What's Changed
* feat: add a check by @alice in https://github.com/o/r/pull/7
* fix(deps): bump x by @dependabot[bot] in https://github.com/o/r/pull/8


## New Contributors
* @alice made their first contribution in https://github.com/o/r/pull/7


**Full Changelog**: https://github.com/o/r/compare/v0.0.1...v0.0.2
"""
PAGE = """## Highlights ⭐️

* **One thing**: It changed for the user.
* **Another thing**: So did this.

## What's Changed
* feat: add a check by @alice in https://github.com/o/r/pull/7
* fix(deps): bump x by @dependabot[bot] in https://github.com/o/r/pull/8

## New Contributors
* @alice made their first contribution in https://github.com/o/r/pull/7

## Checksums

{checksums}

**Full Changelog**: https://github.com/o/r/compare/v0.0.1...v0.0.2
"""
ASSETS = {"checksums.txt": b"sums\n", "app_Linux_x86_64.tar.gz": b"archive\n"}
HASHED = """SHA-256 of every asset attached to this release:

```text
371e16ce98051a3ea7af3eaef8b87d69033154fb5bb33da349d611f0fae061d6  app_Linux_x86_64.tar.gz
c001d0d1d2da2d23b87521529826ff1bb00c6afaac20b652c0871905c84d1508  checksums.txt
```"""
NOTE = "The site is deployed from this tag."


class FakeGH:
    """Answers the gh calls release_page makes, and records them."""

    def __init__(self, assets=None, exists=True, fail_on="", tamper=False, generated=GENERATED):
        self.assets, self.exists, self.fail_on, self.tamper = assets or {}, exists, fail_on, tamper
        self.generated, self.calls, self.published = generated, [], ""

    def __call__(self, *args):
        self.calls.append(args)
        joined = " ".join(args)
        if self.fail_on and self.fail_on in joined:
            raise subprocess.CalledProcessError(1, "gh")
        if args[0] == "api":
            return self.generated
        if "name,body" in joined:
            return "another page" if self.tamper else self.published
        if args[:2] == ("release", "view"):
            if not self.exists:
                raise subprocess.CalledProcessError(1, "gh")
            return "".join(n + "\n" for n in self.assets)
        if args[:2] == ("release", "download"):
            return self.download(args)
        return self.write(args)

    def download(self, args):
        d = Path(args[args.index("-D") + 1])
        for name, data in self.assets.items():
            (d / name).write_bytes(data)
        return ""

    def write(self, args):
        notes = Path(args[args.index("--notes-file") + 1]).read_text()
        self.published = args[args.index("--title") + 1] + "\n" + notes
        return ""

    def called(self, prefix):
        return [" ".join(c) for c in self.calls if " ".join(c).startswith(prefix)]


class ReleasePage(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        (self.dir / "v0.0.2.md").write_text(HIGHLIGHTS)
        patcher = unittest.mock.patch.object(release_page, "RELEASES", self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)
        env = unittest.mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "o/r"})
        env.start()
        self.addCleanup(env.stop)

    def page(self, fake, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = release_page.main(list(argv), run=fake, out=out, err=err)
        return code, out.getvalue(), err.getvalue()

    def test_prints_the_page_with_the_release_assets_hashed(self):
        fake = FakeGH(assets=ASSETS)
        code, out, err = self.page(fake, "v0.0.2")
        self.assertEqual((code, err), (0, "title: satellion.github.io 0.0.2\n"))
        self.assertEqual(out, PAGE.format(checksums=HASHED))
        self.assertEqual(fake.called("api"), ["api repos/o/r/releases/generate-notes -f tag_name=v0.0.2 --jq .body"])
        self.assertEqual(fake.called("release edit") + fake.called("release create"), [])

    def test_assets_given_are_hashed_instead_of_the_release(self):
        for name, data in ASSETS.items():
            (self.dir / name).write_bytes(data)
        fake = FakeGH(exists=False)
        files = [str(self.dir / n) for n in ASSETS]
        code, out, _ = self.page(fake, "--target", "abc123", "v0.0.2", *files)
        self.assertEqual(code, 0)
        self.assertEqual(out, PAGE.format(checksums=HASHED))
        self.assertIn("-f target_commitish=abc123", fake.called("api")[0])

    def test_no_assets_says_so_and_what_is_published_instead(self):
        fake = FakeGH()
        code, out, _ = self.page(fake, "--note", NOTE, "v0.0.2")
        self.assertEqual(code, 0)
        self.assertEqual(out, PAGE.format(checksums=release_page.NO_ASSETS + "\n\n" + NOTE))
        self.assertEqual(fake.called("release download"), [])

    def test_notes_with_only_the_changelog_line_leave_no_empty_section(self):
        fake = FakeGH(generated="**Full Changelog**: https://github.com/o/r/commits/v0.0.2\r\n")
        _, out, _ = self.page(fake, "v0.0.2")
        want = (
            "## Highlights ⭐️\n\n* **One thing**: It changed for the user.\n* **Another thing**: So did this.\n\n"
            "## Checksums\n\n"
            + release_page.NO_ASSETS
            + "\n\n**Full Changelog**: https://github.com/o/r/commits/v0.0.2\n"
        )
        self.assertEqual(out, want)

    def test_publish_edits_the_release_and_reads_it_back(self):
        fake = FakeGH(assets=ASSETS)
        code, out, err = self.page(fake, "--publish", "v0.0.2")
        self.assertEqual((code, out, err), (0, "", ""))
        edit = fake.called("release edit")[0]
        self.assertTrue(edit.startswith("release edit v0.0.2 --title satellion.github.io 0.0.2 --notes-file "), edit)
        self.assertTrue(edit.endswith(" -R o/r"), edit)
        self.assertEqual(fake.published, "satellion.github.io 0.0.2\n" + PAGE.format(checksums=HASHED))

    def test_publish_creates_a_release_that_does_not_exist(self):
        fake = FakeGH(exists=False)
        code, _, _ = self.page(fake, "--publish", "v0.0.2")
        self.assertEqual(code, 0)
        self.assertTrue(fake.called("release create v0.0.2 --verify-tag --title satellion.github.io 0.0.2"))

    def test_a_published_page_that_differs_fails(self):
        code, _, err = self.page(FakeGH(tamper=True), "--publish", "v0.0.2")
        self.assertEqual(code, 1)
        self.assertIn("is not the composed one", err)

    def test_gh_failures_name_the_step(self):
        cases = {
            "generate-notes": "generate-notes for v0.0.2 failed",
            "release download": "download the assets of v0.0.2 failed",
            "release edit": "publish v0.0.2 failed",
        }
        for fail_on, want in cases.items():
            code, _, err = self.page(FakeGH(assets=ASSETS, fail_on=fail_on), "--publish", "v0.0.2")
            self.assertEqual(code, 1, fail_on)
            self.assertIn(want, err)

    def test_bad_inputs_fail(self):
        (self.dir / "v0.0.3.md").write_text("## Changes\n* x\n")
        cases = [
            (FakeGH(), "v0.0.3", "has no '## Highlights ⭐️' heading"),
            (FakeGH(), "v0.0.4", "v0.0.4.md"),
            (FakeGH(generated="## What's Changed\n* x\n"), "v0.0.2", "no **Full Changelog** line"),
        ]
        for fake, tag, want in cases:
            code, _, err = self.page(fake, tag)
            self.assertEqual(code, 1, tag)
            self.assertIn(want, err)

    def test_a_tag_that_is_not_vxyz_is_a_usage_error(self):
        with self.assertRaises(SystemExit) as e, unittest.mock.patch("sys.stderr", io.StringIO()):
            release_page.main(["0.0.2"], run=FakeGH())
        self.assertEqual(e.exception.code, 2)

    def test_without_a_repository_gh_infers_it(self):
        with unittest.mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": ""}):
            fake = FakeGH()
            self.page(fake, "v0.0.2")
        self.assertIn("repos/{owner}/{repo}/releases/generate-notes", fake.called("api")[0])
        self.assertFalse(any("-R" in c for c in fake.calls))

    def test_gh_runs_the_real_command(self):
        with unittest.mock.patch.object(subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout="ok")
            self.assertEqual(release_page.gh("version"), "ok")
            run.return_value = subprocess.CompletedProcess([], 1, stdout="")
            with self.assertRaises(subprocess.CalledProcessError):
                release_page.gh("version")


if __name__ == "__main__":
    unittest.main()
