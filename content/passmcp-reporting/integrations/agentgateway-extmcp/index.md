---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "Satellion"
title: "satellion.com/passmcp-reporting/integrations/agentgateway-extmcp"
description: "The agentgateway processor that gates MCP backends on passmcp attestations, verified offline."
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
# A nested module of passmcp-reporting: Go fetches this path, reads the
# repository root's tag, and finds the module in integrations/agentgateway-extmcp.
go_import: "satellion.com/passmcp-reporting git https://github.com/sebastienrousseau/passmcp-reporting"
go_source: "satellion.com/passmcp-reporting https://github.com/sebastienrousseau/passmcp-reporting https://github.com/sebastienrousseau/passmcp-reporting/tree/main{/dir} https://github.com/sebastienrousseau/passmcp-reporting/blob/main{/dir}/{file}#L{line}"
eyebrow: "Go module"
headline: "satellion.com/passmcp-reporting/integrations/agentgateway-extmcp"
lead: "The agentgateway processor that gates MCP backends on passmcp attestations, verified offline at startup."
---

```sh
go install satellion.com/passmcp-reporting/integrations/agentgateway-extmcp/cmd/agentgateway-extmcp@v0.0.5
```

- Module: [satellion.com/passmcp-reporting](/passmcp-reporting/)
- Source: [integrations/agentgateway-extmcp](https://github.com/sebastienrousseau/passmcp-reporting/tree/main/integrations/agentgateway-extmcp)
