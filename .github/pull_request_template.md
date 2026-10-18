<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com> -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->
<!--
Thanks for contributing to satellion.com.

Branch from `main` and target `main`. Every claim on the site must be backed
by passmcp's source, its output, or a cited public source.
-->

## What this changes

<!-- One or two sentences. What is different on the site after this merges? -->

## Why

<!-- The problem, not the patch. If it fixes an issue, link it: Fixes #123 -->

## How it was verified

- [ ] `make check` passes
- [ ] New or changed behaviour has a test in `scripts/test_<name>.py` that fails without it, and `make coverage` stays at 85% or more
- [ ] A new or changed claim links its evidence
- [ ] A new Go module page is listed in `scripts/modules.py`
- [ ] `CHANGELOG.md` has an entry under the version being prepared

---

- [ ] Commits are signed and carry a DCO `Signed-off-by` trailer (`git commit -s -S`)
