# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""The fuzz harness's check holds for its seeds and catches what it is for.

The fuzzer itself needs Atheris, which runs in CI on Linux; these tests run
the same check anywhere, so the harness cannot rot between fuzz runs.
Run: python3 -m unittest discover -s scripts
"""

import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import family
import fuzz_family


class Check(unittest.TestCase):
    def test_the_seeds_render_as_the_table(self):
        for s in fuzz_family.SEEDS:
            with self.subTest(seed=s[:40]):
                fuzz_family.check(s)
                self.assertEqual(fuzz_family.problems(family.render(*family.load(s.decode()), "0.0.8")), [])

    def test_refused_and_undecodable_input_is_not_a_finding(self):
        for data in [
            b"\xff\xfe",
            b"",
            b"[]",
            b"{",
            b"[" * 100_000,
            (b'{"schema_version": 2, "repositories": [{"name": "x", "repository": "a\\" b", "status": "released"}]}'),
        ]:
            with self.subTest(data=data[:40]):
                fuzz_family.check(data)

    def test_markup_the_table_never_writes_is_a_finding(self):
        self.assertEqual(fuzz_family.problems('<a href="https://example.com/">x</a>'), ["href 'https://example.com/'"])
        self.assertEqual(
            fuzz_family.problems(f'<a href="{family.REPO}/x" onmouseover="y">x</a>'), ["<a ['href', 'onmouseover']>"]
        )
        self.assertEqual(fuzz_family.problems("<script>x</script>"), ["<script []>"])

    def test_a_render_that_lets_markup_through_fails_the_check(self):
        leaky = '<a href="https://example.com/" rel="noopener">x</a>'
        with (
            unittest.mock.patch.object(family, "render", return_value=leaky),
            self.assertRaisesRegex(AssertionError, "never writes"),
        ):
            fuzz_family.check(fuzz_family.SEEDS[0])

    def test_seeds_fill_only_an_empty_corpus(self):
        with tempfile.TemporaryDirectory() as d:
            corpus = Path(d, "corpus")
            fuzz_family.seed(corpus)
            self.assertEqual(len(list(corpus.iterdir())), len(fuzz_family.SEEDS))
            (corpus / "seed-0.json").write_bytes(b"found")
            fuzz_family.seed(corpus)
            self.assertEqual((corpus / "seed-0.json").read_bytes(), b"found")

    def test_main_without_a_corpus_prints_the_usage(self):
        with (
            unittest.mock.patch.dict(sys.modules, {"atheris": unittest.mock.MagicMock()}),
            self.assertRaisesRegex(SystemExit, "usage"),
        ):
            fuzz_family.main(["fuzz_family.py"])

    def test_main_seeds_the_corpus_and_runs_atheris(self):
        atheris = unittest.mock.MagicMock()
        with tempfile.TemporaryDirectory() as d, unittest.mock.patch.dict(sys.modules, {"atheris": atheris}):
            fuzz_family.main(["fuzz_family.py", d, "-runs=1"])
            self.assertTrue(any(Path(d).iterdir()))
        atheris.instrument_all.assert_called_once()
        atheris.Setup.assert_called_once_with(["fuzz_family.py", d, "-runs=1"], fuzz_family.check)
        atheris.Fuzz.assert_called_once()


if __name__ == "__main__":
    unittest.main()
