---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "Satellion"
title: "satellion.com/passmcp-lsp"
description: "A language server for MCP artefacts: it checks server.json, MCP client configurations, MCP tool definitions, and passmcp policies and attestations as you type, and shows passmcp's guidance when you hover a check id."
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
footer_repo: "passmcp-lsp"
footer_license: "passmcp-lsp is released under Apache-2.0."
# Go resolves the module path satellion.com/passmcp-lsp from these two tags.
go_import: "satellion.com/passmcp-lsp git https://github.com/sebastienrousseau/passmcp-lsp"
go_source: "satellion.com/passmcp-lsp https://github.com/sebastienrousseau/passmcp-lsp https://github.com/sebastienrousseau/passmcp-lsp/tree/main{/dir} https://github.com/sebastienrousseau/passmcp-lsp/blob/main{/dir}/{file}#L{line}"
eyebrow: "Go module"
headline: "satellion.com/passmcp-lsp"
lead: "A language server for MCP artefacts: it checks server.json, MCP client configurations, MCP tool definitions, and passmcp policies and attestations as you type, and shows passmcp's guidance when you hover a check id."
---

```sh
go install satellion.com/passmcp-lsp/cmd/passmcp-lsp@v0.0.7
```

- Source: [github.com/sebastienrousseau/passmcp-lsp](https://github.com/sebastienrousseau/passmcp-lsp)
- API documentation: [pkg.go.dev/satellion.com/passmcp-lsp](https://pkg.go.dev/satellion.com/passmcp-lsp)
