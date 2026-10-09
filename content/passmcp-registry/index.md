---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "Satellion"
title: "satellion.com/passmcp-registry"
description: "A signed public scorecard of the remote servers in the MCP Registry, each checked read-only and without credentials by a pinned passmcp release."
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
# Go resolves the module path satellion.com/passmcp-registry from these two tags.
go_import: "satellion.com/passmcp-registry git https://github.com/sebastienrousseau/passmcp-registry"
go_source: "satellion.com/passmcp-registry https://github.com/sebastienrousseau/passmcp-registry https://github.com/sebastienrousseau/passmcp-registry/tree/main{/dir} https://github.com/sebastienrousseau/passmcp-registry/blob/main{/dir}/{file}#L{line}"
eyebrow: "Go module"
headline: "satellion.com/passmcp-registry"
lead: "A signed public scorecard of the remote servers in the MCP Registry, each checked read-only and without credentials by a pinned passmcp release."
---

```sh
go install satellion.com/passmcp-registry/cmd/passmcp-registry@v0.0.5
```

- Source: [github.com/sebastienrousseau/passmcp-registry](https://github.com/sebastienrousseau/passmcp-registry)
- API documentation: [pkg.go.dev/satellion.com/passmcp-registry](https://pkg.go.dev/satellion.com/passmcp-registry)

