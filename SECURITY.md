<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com> -->
<!-- SPDX-License-Identifier: GPL-3.0-only -->

# Security Policy

This repository builds the static site at <https://satellion.com/>. It serves
no application and holds no credentials: every page is a static file, and
the site sets no cookies and runs no analytics. Every page's
Content-Security-Policy (`_layouts/csp.html`) allows scripts and
connections to the site's own origin only, so it also blocks an
analytics beacon an edge proxy injects.

## Reporting a vulnerability

- **In passmcp itself**, the tool, its reports or its attestations: follow
  [passmcp's security policy](https://github.com/sebastienrousseau/passmcp/blob/main/SECURITY.md).
- **In this site**, for example injected content, a misconfigured header or
  a compromised build: report it privately through
  [GitHub security advisories](https://github.com/sebastienrousseau/satellion.github.io/security/advisories/new).
  Please do not open a public issue.

Reports are acknowledged within 72 hours, as for passmcp.
