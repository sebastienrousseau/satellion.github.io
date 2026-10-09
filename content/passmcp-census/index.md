---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "Satellion"
title: "satellion.com/passmcp-census"
description: "The published MCP reliability census: the dataset, the methodology, the disclosure log and the command that reproduces the figures."
author: "Sebastien Rousseau"
date: "2026-09-29"
layout: "doc"
language: "en-GB"
schema: "page"
changefreq: "monthly"
copyright_year: "2026"
form_origin: "'self'"
theme_style: "style-satellion"
theme_colour: "#214186"
footer_note: "Evidence you can check, not claims you have to trust."
# Go resolves the module path satellion.com/passmcp-census from these two tags.
go_import: "satellion.com/passmcp-census git https://github.com/sebastienrousseau/passmcp-census"
go_source: "satellion.com/passmcp-census https://github.com/sebastienrousseau/passmcp-census https://github.com/sebastienrousseau/passmcp-census/tree/main{/dir} https://github.com/sebastienrousseau/passmcp-census/blob/main{/dir}/{file}#L{line}"
eyebrow: "Go module"
headline: "satellion.com/passmcp-census"
lead: "The published MCP reliability census: the dataset, the methodology, the disclosure log and the command that reproduces the figures."
---

```sh
go install satellion.com/passmcp-census/cmd/passmcp-census@v0.0.5
```

- Source: [github.com/sebastienrousseau/passmcp-census](https://github.com/sebastienrousseau/passmcp-census)
- API documentation: [pkg.go.dev/satellion.com/passmcp-census](https://pkg.go.dev/satellion.com/passmcp-census)
