<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com> -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

<p align="center">
  <img src="https://raw.githubusercontent.com/sebastienrousseau/satellion.github.io/main/brand/satellion/logo.svg" alt="Satellion logo" width="180" />
</p>

<h1 align="center">satellion.com</h1>

<p align="center">
  The source of <a href="https://satellion.com/">satellion.com</a>: Satellion's home, passmcp's pages, and the pages Go and attestation readers resolve, built with SSG.
</p>

<p align="center">
  <a href="https://github.com/sebastienrousseau/satellion.github.io/actions/workflows/pages.yml"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/satellion.github.io/pages.yml?branch=main&style=for-the-badge&logo=github&label=Build" alt="Build" /></a>
  <a href="https://github.com/sebastienrousseau/satellion.github.io/blob/main/DEVELOPMENT.md#coverage"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fsatellion.com%2Fcoverage.json&style=for-the-badge&logo=codecov&logoColor=white" alt="Coverage" /></a>
  <a href="https://github.com/sebastienrousseau/satellion.github.io/releases"><img src="https://img.shields.io/github/v/release/sebastienrousseau/satellion.github.io?style=for-the-badge&color=fc8d62&logo=github&label=Release" alt="Release" /></a>
  <a href="https://satellion.com/"><img src="https://img.shields.io/badge/docs-manual-007d9c?style=for-the-badge&labelColor=555555&logo=readthedocs&logoColor=white" alt="Docs" /></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/sebastienrousseau/satellion.github.io"><img src="https://img.shields.io/ossf-scorecard/github.com/sebastienrousseau/satellion.github.io?style=for-the-badge&label=OpenSSF%20Scorecard&logo=openssf" alt="OpenSSF Scorecard" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0--only-blue.svg?style=for-the-badge" alt="License: GPL-3.0-only" /></a>
  <a href="https://github.com/sebastienrousseau/satellion.github.io/blob/main/DEVELOPMENT.md#requirements"><img src="https://img.shields.io/badge/ssg-0.0.63-93450a.svg?style=for-the-badge&logo=rust" alt="SSG 0.0.63" /></a>
</p>

<p align="center">
  <img src=".github/demo.gif" alt="The core build of satellion.com served locally and captured by headless Chrome: the Satellion company page, then the passmcp product page" width="100%" />
</p>

---

## Contents

**Getting started**

- [Install](#install) — SSG and the repository
- [Requirements](#requirements) — Python 3.12+, SSG 0.0.63, and Go for the full site
- [Quick Start](#quick-start) — build and serve the site locally, with or without a passmcp release

**The satellion.com ecosystem**

- [The satellion.com ecosystem](#the-satellioncom-ecosystem) — `passmcp`, `passmcp-reporting`, `passmcp-server`, `passmcp-action`, `passmcp-graph`, `passmcp-registry`, `passmcp-lsp`, `passmcp-census`, `satellion.com`

**Library reference**

- [Capabilities at a glance](#capabilities-at-a-glance) — what the build produces
- [Ecosystem comparison](#ecosystem-comparison) — not applicable
- [Benchmarks](#benchmarks) — not applicable
- [Features](#features) — what keeps the pages accurate
- [Configuration](#configuration) — `ssg.toml` and the Makefile variables
- [Examples](#examples) — building against a given release

**Operational**

- [When not to use satellion.com](#when-not-to-use-satellioncom) — limits
- [Development](#development) — make targets, CI
- [Security](#security) — reporting
- [Documentation](#documentation) — where the docs live
- [Stability guarantees](#stability-guarantees) — the URLs other systems rely on
- [License](#license)

---

## Install

```sh
cargo install ssg --locked --version 0.0.63
git clone https://github.com/sebastienrousseau/satellion.github.io
cd satellion.github.io
```

---

## Requirements

`make core` needs Python 3.12 or later and exactly SSG 0.0.63; the Makefile
refuses any other SSG version. `make site` also needs Go (stable), git and
network access to GitHub: it clones passmcp at its latest release tag,
builds it, and installs the manual's hash-locked requirements into a local
virtual environment under `.build/`. `make coverage` installs coverage.py,
hash-locked, into `.build/venv-test`. CI runs Python 3.12 and SSG 0.0.63;
[DEVELOPMENT.md](DEVELOPMENT.md#requirements) has the full table.

---

## Quick Start

```sh
make core     # the pages that need no passmcp release
make site     # core, plus the manual and sample report from the latest release
make serve    # then open http://localhost:8000
```

---

## The satellion.com ecosystem

Every component is released at **0.0.5** and moves in lockstep: one version across the family, released together ([docs/ecosystem.md](https://github.com/sebastienrousseau/passmcp/blob/main/docs/ecosystem.md)).

| Component | Purpose | Use case |
| :--- | :--- | :--- |
| [passmcp](https://github.com/sebastienrousseau/passmcp) | The MCP server diagnostic: checks in nine phases, every finding tied to the request that showed it, signed attestations | Test a server before your agents trust it, and gate it in CI |
| [passmcp-reporting](https://github.com/sebastienrousseau/passmcp-reporting) | The attestation format, its JSON Schemas and offline verifier, the graph model, and the agentgateway processor | Verify an attestation in a gateway, registry or pipeline |
| [passmcp-server](https://github.com/sebastienrousseau/passmcp-server) | passmcp's diagnostics as read-only MCP tools | Evaluate a server, or check an attestation, from inside the agent |
| [passmcp-action](https://github.com/sebastienrousseau/passmcp-action) | passmcp in GitHub Actions and GitLab CI, the image pinned by digest | Fail a build on the findings you choose |
| [passmcp-graph](https://github.com/sebastienrousseau/passmcp-graph) | A local graph of agents, servers, tools and identities built from attestations | Find inherited risk and over-privilege, and gate on policy |
| [passmcp-registry](https://github.com/sebastienrousseau/passmcp-registry) | A signed public scorecard of the MCP Registry's remote servers | Check a public server's standing before connecting to it |
| [passmcp-lsp](https://github.com/sebastienrousseau/passmcp-lsp) | A language server for MCP artefacts, with check-id hover from the guidance catalogue | Catch mistakes in server.json, tool schemas and client configuration while editing |
| [passmcp-census](https://github.com/sebastienrousseau/passmcp-census) | The published reliability census: dataset, methodology, disclosure log and reproduction command | Cite ecosystem-wide reliability figures, and reproduce them |
| [satellion.com](https://github.com/sebastienrousseau/satellion.github.io) | The website, the Go module paths and the format URIs | Read the manual, and resolve `satellion.com/...` imports |

---

## Capabilities at a glance

| Area | Capability | Status |
| :--- | :--- | :--- |
| Company page | Satellion's home, from `content/index.md` and the `company` layout | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Product page | passmcp's page at `/passmcp/`, from `content/passmcp/index.md` | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Go module pages | `satellion.com/passmcp`, `/passmcp-reporting` (and its nested agentgateway module), `/passmcp-server`, `/passmcp-graph` and `/passmcp-registry` resolve to their repositories | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Go module pages | `satellion.com/passmcp-lsp` and `satellion.com/passmcp-census` resolve to their repositories | [Released in 0.0.3](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.3) |
| Format pages | The attestation and graph format URIs resolve to their specifications | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Numbers | Score, grade, counts, ledger, phases and evidence from passmcp's sample report | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Manual | passmcp's `docs/`, built with MkDocs `--strict`, at `/passmcp/docs/` | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Sample | passmcp's real report against its fixture server, at `/passmcp/sample/` | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| security.txt | RFC 9116 at `/.well-known/security.txt`, failing the build 30 days before it expires | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Social cards | Rendered from `cards/` by `scripts/cards.py` | [Released in 0.0.1](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.1) |
| Family listing | All nine components with their release status, on the company and product pages, rendered from passmcp's `ecosystem.json` | [Released in 0.0.3](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.3) |
| Coverage badge | `/coverage.json`, the scripts' coverage measured on every deploy | [Released in 0.0.3](https://github.com/sebastienrousseau/satellion.github.io/releases/tag/v0.0.3) |

---

## Ecosystem comparison

Not applicable: this repository is a website, not a library. How passmcp
compares with other tools is on the site itself, with sources.

---

## Benchmarks

Not applicable: the site is static. passmcp's benchmarks are in its
[manual](https://satellion.com/passmcp/docs/BENCHMARKS/).

---

## Features

- **Numbers that cannot drift.** `scripts/site_data.py` writes every check
  count and the sample's numbers from passmcp's release on every build, and
  pull requests fail if the committed pages differ.
- **Module paths that cannot break quietly.** `scripts/modules.py` fails the
  build if any Go module page lacks its `go-import` tag or names the wrong
  repository.
- **A security.txt that cannot lapse.** The build fails when its Expires date
  is under 30 days away.
- **Versions that agree.** `scripts/verify-release-versions.sh` fails when a
  module page's install line, the README or the product page names a version
  other than the newest CHANGELOG release.
- **Built against a release, not a branch.** The Makefile resolves passmcp's
  newest tag; a daily build keeps the site on it.

---

## Configuration

`ssg.toml` sets the site name, base URL and directories. The Makefile takes
`PASSMCP_REF` (a passmcp tag, default the latest), `PASSMCP_REPO` and
`SSG_VERSION`.

---

## Examples

```sh
make site PASSMCP_REF=v0.0.5   # build against a specific release
make data                      # rewrite the page's numbers from the sample report
make check-data                # fail if they differ, as CI does on pull requests
```

---

## When not to use satellion.com

To learn or run passmcp itself, go to
[passmcp's repository](https://github.com/sebastienrousseau/passmcp) or the
[manual](https://satellion.com/passmcp/docs/). This repository only builds the
site; it is not a template for other sites, and it hosts no application
([ADR 0003](docs/adr/0003-static-site-not-the-application.md)).

---

## Development

```bash
make check          # lint, complexity, versions, tests under the coverage gate, core build
make test           # the scripts' tests alone
make coverage       # the same, gated at 85%, writing .build/coverage.json
make verify-versions
make name-guard
```

[DEVELOPMENT.md](DEVELOPMENT.md) maps every CI gate to its local command.
Pull requests run `ci.yml` (tests, coverage, complexity, versions, core build),
`docs-lint.yml` (REUSE, markdownlint, codespell, links, README template,
retired name), `pages.yml` (the full site and the page's numbers), DCO,
PR-base, CodeQL and OpenSSF Scorecard. Pushes to `main` and a daily schedule
build and deploy the site to GitHub Pages. Commits follow Conventional
Commits, are signed, and carry a DCO sign-off.

---

## Security

The site at <https://satellion.com/> serves static files only, sets no cookies
and runs no analytics. The build's GitHub Actions are pinned by commit SHA,
its Python tooling is hash-locked, and OpenSSF Scorecard and CodeQL run on
every push to `main`.

Report vulnerabilities according to [`SECURITY.md`](SECURITY.md).

---

## Documentation

- **User manual:** [satellion.com/passmcp/docs](https://satellion.com/passmcp/docs/), passmcp's manual as this site serves it.
- **API reference:** not applicable to this repository; the family's Go APIs are on [pkg.go.dev/satellion.com/passmcp](https://pkg.go.dev/satellion.com/passmcp) and its siblings.
- **Developer docs:** [DEVELOPMENT.md](DEVELOPMENT.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/adr/](docs/adr/README.md) and [AGENTS.md](AGENTS.md).
- **Ecosystem map:** [passmcp's docs/ecosystem.md](https://github.com/sebastienrousseau/passmcp/blob/main/docs/ecosystem.md) and the [table above](#the-satellioncom-ecosystem).
- [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md), [SUPPORT.md](SUPPORT.md) and [GOVERNANCE.md](GOVERNANCE.md).

---

## Stability guarantees

These URLs are stable, because other systems resolve them: `/`,
`/passmcp/`, `/passmcp/docs/`, `/passmcp/sample/`, the Go module paths
(`/passmcp`, `/passmcp-reporting`,
`/passmcp-reporting/integrations/agentgateway-extmcp`, `/passmcp-server`,
`/passmcp-graph`, `/passmcp-registry`, `/passmcp-lsp`, `/passmcp-census`),
and the format URIs (`/attestation/mcp-evaluation/v1`,
`/attestation/a2a-evaluation/v1`, `/graph/v1`). Removing or moving one needs
an ADR. Layout and copy change freely; numbers always come from a passmcp
release. The version follows the family's lockstep, moving by 0.0.1 a
release; SSG's version is pinned exactly and raised only in a change of its
own.

---

## License

Licensed under the **[GNU General Public License v3.0 only](LICENSE)**, as
passmcp is. The layouts in `_layouts/` are MIT, vendored from the SSG theme
suite ([REUSE.toml](REUSE.toml)). The Satellion name and marks are not
licensed.

<p align="right"><a href="#contents">Back to Top</a></p>
