---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "Satellion"
title: "satellion.com/passmcp-graph"
description: "A local graph of which agents use which MCP servers, which tools those servers expose and which identities reach them, built from passmcp's attestations and queried offline."
author: "Sebastien Rousseau"
date: "2026-09-28"
layout: "doc"
language: "en-GB"
schema: "page"
changefreq: "monthly"
copyright_year: "2026"
form_origin: "'self'"
theme_style: "style-satellion"
theme_colour: "#214186"
footer_note: "Evidence you can check, not claims you have to trust."
# Go resolves the module path satellion.com/passmcp-graph from these two tags.
go_import: "satellion.com/passmcp-graph git https://github.com/sebastienrousseau/passmcp-graph"
go_source: "satellion.com/passmcp-graph https://github.com/sebastienrousseau/passmcp-graph https://github.com/sebastienrousseau/passmcp-graph/tree/main{/dir} https://github.com/sebastienrousseau/passmcp-graph/blob/main{/dir}/{file}#L{line}"
eyebrow: "Go module"
headline: "satellion.com/passmcp-graph"
lead: "A local graph of which agents use which MCP servers, which tools those servers expose and which identities reach them, built from passmcp's attestations and queried offline."
---

```sh
go install satellion.com/passmcp-graph/cmd/passmcp-graph@v0.0.5
```

- Source: [github.com/sebastienrousseau/passmcp-graph](https://github.com/sebastienrousseau/passmcp-graph)
- API documentation: [pkg.go.dev/satellion.com/passmcp-graph](https://pkg.go.dev/satellion.com/passmcp-graph)

