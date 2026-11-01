---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "Satellion"
title: "satellion.com/passmcp-census"
description: "The passmcp reliability census: aggregate figures about the MCP Registry's remote servers, each checked read-only and without credentials by a released passmcp, with the methodology, the disclosure log and the command that reproduces them. No edition has been published yet."
author: "Sebastien Rousseau"
date: "2026-09-29"
layout: "doc"
language: "en-GB"
schema: "page"
changefreq: "monthly"
copyright_year: "2026"
theme_style: "style-satellion"
theme-color: "#214186"
footer_note: "Evidence you can check, not claims you have to trust."
footer_repo: "passmcp-census"
footer_license: "passmcp-census's code is released under Apache-2.0, and its census data under CC-BY-4.0."
# Go resolves the module path satellion.com/passmcp-census from these two tags.
go_import: "satellion.com/passmcp-census git https://github.com/sebastienrousseau/passmcp-census"
go_source: "satellion.com/passmcp-census https://github.com/sebastienrousseau/passmcp-census https://github.com/sebastienrousseau/passmcp-census/tree/main{/dir} https://github.com/sebastienrousseau/passmcp-census/blob/main{/dir}/{file}#L{line}"
eyebrow: "Go module"
headline: "satellion.com/passmcp-census"
lead: "The passmcp reliability census: aggregate figures about the MCP Registry's remote servers, each checked read-only and without credentials by a released passmcp, with the methodology, the disclosure log and the command that reproduces them. No edition has been published yet."
---

```sh
go install satellion.com/passmcp-census/cmd/passmcp-census@v0.0.8
```

- Source: [github.com/sebastienrousseau/passmcp-census](https://github.com/sebastienrousseau/passmcp-census)
- API documentation: [pkg.go.dev/satellion.com/passmcp-census](https://pkg.go.dev/satellion.com/passmcp-census)
