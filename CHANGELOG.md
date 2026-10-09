<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com> -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

# Changelog

All notable changes to satellion.com are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions move by
0.0.1 a release, as across the passmcp family.

## [0.0.5] — 2026-10-09

### Changed

- **Built against passmcp 0.0.5.** The numbers, sample report and family
  table come from the 0.0.5 release.
- **Upgraded static engine to SSG 0.0.66.** Quality gate supports
  root-relative SRI verification.

## [0.0.4] — 2026-09-30

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

## [0.0.3] — 2026-09-30

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

## [0.0.1] — 2026-09-29

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
