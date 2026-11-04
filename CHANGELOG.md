<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com> -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

# Changelog

All notable changes to satellion.com are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions move by
0.0.1 a release, as across the passmcp family.

## [Unreleased]

Work towards the family's 0.0.9. Version places stay at 0.0.8 until the
family's release step.

### Security

- **certifi is held at 2026.10.18 or later.** `scripts/requirements.in`
  sets a floor on certifi, which requests pulls in, so no release that
  GHSA-6q48-6c7w-9gw2 (PYSEC-2026-4320) affects can resolve. The
  hash-locked `scripts/requirements.txt` moves from 2026.7.22 to
  2026.10.23, and `pip-audit` finds nothing in either lock. Supersedes
  Dependabot's #13.

### Fixed

- **`scripts/test_release_page.py` imports `unittest` one way.** It took
  both `import unittest` and `from unittest import mock`, which CodeQL
  flags; it now uses `unittest.mock` throughout.

## [0.0.8] - 2026-10-31

### Added

- **`family.py` is fuzzed.** `scripts/fuzz_family.py` feeds Atheris's
  inputs to it as passmcp's `ecosystem.json` and fails on a crash or on
  any markup the family table never writes: an element or attribute
  outside the table's own, or a link outside the account on GitHub.
  `make fuzz` runs it, and CI's new fuzz job runs it for two minutes on
  every change, with Atheris installed hash-locked from
  `scripts/fuzz-requirements.txt`. `scripts/test_fuzz_family.py` runs the
  same check over its seeds on any machine.

- **The site's main stylesheet is held to Skeletonic Stylus 3.0.0.**
  `scripts/test_skeletonic.py` fails unless `_layouts/skeletonic.min.css`
  is byte for byte the 3.0.0 core the SSG theme suite pins, and both page
  shells load it before `styles.css`.

- **The live passmcp-graph demo is back, built by SSG.**
  `/passmcp-graph/demo/` is passmcp-graph's published fixture graph,
  exported with `passmcp-graph dashboard --share-safe --format json` and
  written by the new `scripts/graph_demo.py` into the Control Centre
  theme's overview page: clients, servers and their status around a ring,
  four key figures, the findings and evidence gaps, and the query that
  shows each one's evidence. `make graph-site` builds it with SSG into a
  directory of its own and `make site` publishes it; the generator refuses
  an export that is not share-safe. The theme's layouts are vendored, MIT,
  in `graph-demo/_layouts/`, with their source recorded in `REUSE.toml`.
  passmcp's page and passmcp-graph's page link the demo again.
- **Every built page is held to the site's policy.**
  `scripts/strict_csp.py` runs in `make core` and `make graph-site` and
  fails on a page without the site's one Content-Security-Policy, or with
  an inline script, style element, style or event-handler attribute, or
  an asset from another origin.

- **ruff lints and formats the build's scripts.** `make ruff` runs
  `ruff check` and `ruff format --check` over `scripts/` with `ruff.toml`,
  at the version `scripts/requirements.txt` locks, and CI runs it. The
  existing findings are fixed at their causes: `family.py` raises its own
  `ManifestError` (still a `ValueError`) for a malformed manifest, and
  `security_txt.py` leaves RFC 3339's Z suffix to Python's own parser.
- **The SSG pin is checked.** `make verify-versions` fails when the
  README, the contributor docs, `AGENTS.md`, the architecture document or
  a workflow names an SSG version other than the Makefile's
  `SSG_VERSION`.
- **passmcp's sample report is held to the policy once passmcp can meet
  it.** `make check-sample-csp`, part of `make site`, fails a sample
  report that needs an inline style or script, from passmcp
  `SAMPLE_CSP_FROM` (0.0.8) on. passmcp 0.0.7's report inlines its
  styles, so it renders unstyled under the site's header; the fix belongs
  in passmcp's generator, not in a rewrite here.

### Changed

- **SSG 0.0.68.** The Makefile, both workflows and the docs move from
  0.0.66 to 0.0.68. Its minifier keeps the spaces inside string literals that 0.0.66 dropped,
  so `graph-demo/_layouts/main.js` is now the Control Centre theme's file
  byte for byte, pinned by SHA-256 like the other unchanged files. 0.0.68
  still links `/highlight.css` by its plain name, so the copy of the
  fingerprinted file stays.

### Fixed

- **A manifest's repository can no longer add markup to the site.** The
  repository went into the family table's links unescaped, so a value
  with a quote in it added attributes; it must now be a repository name.
  The site's Content-Security-Policy already blocked inline handlers, and
  the manifest is passmcp's own, so nothing reached a visitor.
- **One page policy, own origin only.** Every page's
  Content-Security-Policy is written once, in `_layouts/csp.html`, which
  both page shells and the passmcp-graph demo include, instead of in each
  shell; `form-action` no longer names `'self'` twice. It allows scripts,
  styles and connections from the site's own origin only, so it blocks
  third-party scripts, analytics an edge proxy injects (Cloudflare's Web
  Analytics beacon) included: the site runs no analytics.
- **The docs name the SSG the build uses.** `DEVELOPMENT.md`, the
  README, `CONTRIBUTING.md`, `AGENTS.md` and the architecture document
  said SSG 0.0.63; the Makefile and CI pin 0.0.68.
- **The web app manifest has no null field.** SSG fills `theme_color`
  from a `theme-color` front matter key, so the pages' `theme_colour` key
  is now `theme-color` and feeds both the manifest and the
  `<meta name="theme-color">` tag; the demo sets `short_name` too.
  `scripts/quality_gate.py` fails a build whose `manifest.json` has a
  null field.
- **No stale header file ships.** SSG's `[edge_headers]` wrote a Netlify
  `_headers` and Cloudflare Workers headers with SSG's default policy,
  not the site's. The site is served from GitHub Pages behind Cloudflare,
  which applies neither, so they are no longer written, and
  `scripts/strict_csp.py` fails a build that ships one.
- **Each page's footer names its own project.** The footers linked
  passmcp's source, issues and security policy, and said "passmcp is
  released under GPL-3.0-only", on every page, including passmcp-lsp's
  (Apache-2.0) and passmcp-registry's (AGPL-3.0-only). Each page now sets
  `footer_repo` and `footer_license` in its front matter, from that
  repository's licence; the format pages name passmcp-reporting, where the
  formats are published, and the company page names this repository.
  `scripts/footer_links.py`, run in `make core`, fails a page whose
  footer links another repository's source or security policy.
- **Contributors are asked for a failing test.** `CONTRIBUTING.md` and
  the pull request template say new or changed behaviour comes with a
  test in `scripts/test_<name>.py` that fails without it, held by the 85%
  coverage gate.
- **A malformed manifest is refused, not crashed on.** A manifest that
  was not an object, had no `repositories` list, had a row without a
  string name, role or status, or was nested past Python's recursion
  limit stopped `family.py` with a traceback instead of the
  `family: <file>: <reason>` exit it promises.

## [0.0.7] - 2026-10-17

0.0.5 was never tagged; its changes ship in this release, at the family's
version.

### Added

- **A live passmcp-graph demo.** passmcp's page has a section on
  passmcp-graph with a still of its dashboard, and `make site` serves the
  page itself at `/passmcp-graph/demo/`: passmcp-graph's published fixture
  graph, rendered share-safe by `passmcp-graph dashboard` from its latest
  release (`PASSMCP_GRAPH_REF`). `make graph-shot` re-renders the still,
  and `make verify-versions` fails when the version it shows is not the
  family's.

### Changed

- **Built against passmcp 0.0.7.** The numbers, sample report and family
  table come from the 0.0.7 release, and every `go install` and `go get`
  line pins 0.0.7.
- **Every package described as it ships at 0.0.7.** passmcp-graph's page
  names its reports, client configurations, policy gate and dashboard;
  passmcp-lsp's names policies and attestations; passmcp-census's says no
  edition has been published yet; passmcp-registry's and
  passmcp-reporting's follow their READMEs; the agentgateway processor's
  says it re-verifies on reload, and its comment names the prefixed tags
  Go reads.
- **passmcp's page corrected against passmcp 0.0.7.**
  - passmcp writes an in-toto attestation and leaves signing to cosign
    (ADR 0010); the page no longer says it signs one.
  - `--stdio` is a flag of `passmcp check`; the egress watch and decoy
    credentials are opt-in flags on every platform, and only the
    post-handshake witness is Linux-only.
  - passmcp sends protocol conformance probes, not only an invalid
    token, and contacts the authorization servers a target advertises as
    well as the target.
  - The agentgateway processor refuses an attestation that is missing,
    invalid, about another endpoint, below a score floor or failing in a
    named category; it has no staleness check.
  - The Nix and AUR install lines are removed: passmcp's flake has no
    vendor hash at 0.0.7, and the AUR package is at 0.0.4.
  - SBOMs cover packages as well as archives, the container image is
    cosign-signed, unmapped checks are marked with a reason, the report
    directory's files are listed in full, and the licence reads
    GPL-3.0-only.
  - The comparison table's cells for MCP Inspector, Cisco mcp-scanner and
    Snyk agent-scan follow each project's README as of 17 Oct 2026.
- **The company page's OpenVEX claim made exact.** A release carries an
  OpenVEX statement only when a dependency advisory does not affect it.
- **Upgraded the GitHub Actions** CodeQL and Scorecard use (Dependabot
  #7).
- **Upgraded static engine to SSG 0.0.66.** Quality gate supports
  root-relative SRI verification.

## [0.0.4] - 2026-09-30

### Added

- **The build fails on SSG's own audit findings.** `make core` runs
  `scripts/quality_gate.py`, which fails unless SSG's quality gate passes
  all ten pillars and its accessibility report lists no issue.

### Changed

- **Built against passmcp 0.0.4.** The numbers, the sample report and
  the family table come from the 0.0.4 release: 138 checks in nine
  phases, and every member of the family at 0.0.4.
- **The author's name links to sebastienrousseau.com.** Both footers
  read "© 2026 Sebastien Rousseau", with the name linking to the
  author's site; the company footer no longer carries the licence note.
- **The pages are laid out as a bento grid.** The home page, passmcp's
  page and the module pages set their content in opaque cells on CSS
  Grid: the sample report's verdict, score and figures as one mosaic, the
  capabilities, trust notes and phases as cells, and each table inside its
  own card. The layout goes from a mosaic at desktop widths to two tracks
  and then one column on phones. The words, numbers and links are
  unchanged.
- **The header is frosted glass, and opaque when asked.** The sticky
  header is the only blurred layer, over a static colour mesh behind the
  page. With `prefers-reduced-transparency: reduce`,
  `prefers-contrast: more`, forced colours, or no `backdrop-filter`
  support, both become solid. Buttons are an opaque gradient whose label
  holds 4.5:1 or more on every stop, in both themes.
- **The family table lists only the family.** The "Considered and
  rejected" section is gone from the company and product pages; what was
  decided against stays recorded in passmcp's `docs/ecosystem.md`.

### Fixed

- **passmcp's navigation no longer breaks inside a word.** From 1024 to
  1280px its labels wrapped mid-word ("passm / cp"); the product header
  now collapses to the menu below 1280px, checked at every width from 320
  to 1600px.
- **The trust headings on the home page are readable in the light
  theme.** They were dark ink on the dark band, 1.15:1.
- **Every page passes SSG's quality gate and accessibility report.** The
  company header's brand link says it is the home link (`rel="home"`),
  and Satellion's decorative mark is drawn by CSS rather than as an image
  with empty alt text, which also stops both theme variants downloading.
- **Each table is one scroll region.** SSG nested a second region labelled
  "Table, scrollable horizontally" inside each table's own; the corner
  cell of the comparison table is no longer an empty header; the sample
  score is exposed as one labelled image; and commands in prose wrap
  instead of scrolling where a keyboard cannot reach them.

## [0.0.3] - 2026-09-30

### Added

- **Go module pages for `satellion.com/passmcp-lsp` and
  `satellion.com/passmcp-census`**, checked by `scripts/modules.py` like the
  others.
- **The whole family on the site.** The company page and passmcp's page list
  all nine components with their release status, and the components the
  family considered and rejected with the reason, rendered by
  `scripts/family.py` (`make family`) from passmcp's `ecosystem.json`. It
  reads both manifest schemas: schema 2's `repository` field and
  `released`/`unreleased`/`rejected` statuses, and schema 1's
  `shipping`/`planned`. passmcp's page shows that discovery, the graph and
  the compliance mappings were released in passmcp 0.0.1 rather than as
  planned work.
- **A coverage badge.** `make coverage` runs the scripts' tests under
  coverage.py, gated at 85%, and the deploy publishes
  `https://satellion.com/coverage.json`.
- **The family's standard files and gates:** `ci.yml`, `docs-lint.yml`
  (REUSE, markdownlint, codespell, links), OpenSSF Scorecard, DCO and PR-base
  workflows; `scripts/verify-release-versions.sh`; AGENTS.md, DEVELOPMENT.md,
  GOVERNANCE.md, SUPPORT.md, docs/ARCHITECTURE.md and ADRs; issue and pull
  request templates, CODEOWNERS, `.editorconfig`, `.gitattributes`,
  `.codespellrc` and a pre-commit configuration.
- Tests for `scripts/site_data.py` and `scripts/cards.py`, and a complexity
  gate (`make complexity`) at cyclomatic 10 and cognitive 15 per function.

### Changed

- `scripts/site_data.py` and `scripts/security_txt.py` are split into
  smaller functions to meet those ceilings; their output is unchanged.
- The README's badges, ecosystem table and statuses follow the family
  standard.
- Built against passmcp 0.0.3: the product page, the Go module pages and the
  README name 0.0.3, and the deploy renders the family table from that
  release's manifest, which lists passmcp-lsp and passmcp-census as
  released. Their module pages now carry an install line, so
  `go install satellion.com/passmcp-lsp/...` and
  `satellion.com/passmcp-census/...` resolve once this deploys.
- The "Planned" roadmap section of passmcp's page: all three items it
  listed were released in passmcp 0.0.1.

## [0.0.1] - 2026-09-29

The first release.

### Added

- **Satellion's home** at `/`, in the logo's own palette, with light and
  dark themes.
- **passmcp's page** at `/passmcp/`, its manual at `/passmcp/docs/` and a real
  sample report at `/passmcp/sample/`, all built from passmcp's release.
- **Go module pages** for `satellion.com/passmcp` and its four sibling
  modules, checked on every build by `scripts/modules.py`.
- **Format pages** for the attestation and graph format URIs.
- **A security.txt** at `/.well-known/security.txt` (RFC 9116) that fails the
  build before it can expire.
- **Social cards** rendered from `cards/` by `scripts/cards.py`.
- **Two builds:** `make core` needs no passmcp release, and `make site` adds
  what comes from one.
