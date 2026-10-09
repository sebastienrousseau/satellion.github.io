---
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
name: "passmcp"
short_name: "passmcp"
title: "passmcp — prove an MCP server is safe for your agents"
description: "passmcp tests a live MCP server the way an agent would: 138 checks in nine phases, every finding tied to the request that showed it, and a signed attestation you can verify offline. Open source, runs where your credentials already are."
keywords: "MCP server testing, MCP security, Model Context Protocol conformance, MCP attestation, MCP scanner, agent security, MCP Inspector alternative, MCP CI gate"
author: "Sebastien Rousseau"
date: "2026-09-26"
layout: "index"
# Go resolves the module path satellion.com/passmcp from these two tags.
go_import: "satellion.com/passmcp git https://github.com/sebastienrousseau/passmcp"
go_source: "satellion.com/passmcp https://github.com/sebastienrousseau/passmcp https://github.com/sebastienrousseau/passmcp/tree/main{/dir} https://github.com/sebastienrousseau/passmcp/blob/main{/dir}/{file}#L{line}"
language: "en-GB"
schema: "page"
changefreq: "weekly"
copyright_year: "2026"
form_origin: "'self'"
theme_style: "style-passmcp"
theme_colour: "#F9A12C"
brand_mark: "P"
footer_note: "A verdict is worth what its evidence is worth."

eyebrow: "Open source · runs on your machine or in CI · no telemetry"
headline: "Prove an MCP server is safe for your agents, with evidence anyone can check."
lead: "passmcp connects to a live MCP server the way an agent would, runs 138 checks in nine phases, and ties every finding to the request that showed it. It writes a signed attestation that a gateway, a registry or an auditor can verify offline. Nothing is uploaded and nothing is guessed."
cta_primary: "Install"
cta_secondary: "See a real report"
cta_tertiary: "Verify an attestation"

readout_kicker: "passmcp's sample report"
metric_one_label: "Checks in passmcp"
metric_one_value: "138"
metric_two_label: "Protocol generations"
metric_two_value: "Both"
metric_three_label: "Bytes sent to us"
metric_three_value: "None"
proof_note: "This is passmcp's real output, not a mock-up: the sample report is passmcp run against a fixture server with deliberate flaws, and the score, ledger, phases and evidence on this page are read from it."

only_eyebrow: "What only passmcp does"
only_title: "Validation you can prove, not a posture you have to trust."
only_lead: "Discovery and dashboards tell you what exists. passmcp tells you what a server actually does when an agent talks to it, and gives you a signed record of it."
only_one_title: "Live protocol validation"
only_one_text: "Handshake, conformance, catalogue, safe execution, latency and recovery, run against the real server over the real transport, on both the handshake revisions and the stateless 2026-07-28 revision."
only_two_title: "Evidence tied to requests"
only_two_text: "Every finding cites the numbered request that produced it, and the report directory keeps the NDJSON event stream and a HAR file. A verdict you dispute is a verdict you can replay."
only_three_title: "Signed, offline-verifiable attestations"
only_three_text: "passmcp writes an in-toto statement about the server. The verifier is Apache-2.0 and has no dependencies, so a gateway, registry or auditor can check it without trusting anyone's server."
only_four_title: "A gate, not a report"
only_four_text: "Exit status 2 on a failed check, a policy file for what counts, SARIF for code scanning and JUnit for test reports. The check that gates a release is the one an engineer already ran."

why_eyebrow: "Why it runs here"
why_title: "A tester you upload to is a tester you trust twice."
why_lead: "Handing an endpoint to a hosted tester means handing over whatever reaches it. For a server behind OAuth, that is a working credential. passmcp is the same test, run from inside your own trust boundary."
why_one_title: "Your credentials stay put"
why_one_text: "passmcp authenticates from your machine with the token you already hold. Secrets are registered with the recorder before the first request and masked everywhere they appear, including tokens the server issues mid-run."
why_two_title: "Your network is the network"
why_two_text: "A server on a private address, behind a VPN, inside a CI runner, or run as a local program over stdio, is reached exactly as your agents reach it."
why_three_title: "Read-only by default"
why_three_text: "Only tools that declare readOnlyHint are called. A tool with no annotation is destructive by the specification's default, so it is skipped and the report says so. Mutations are an explicit opt-in."

compare_eyebrow: "How it compares"
compare_title: "Use the right tool for the question."
compare_lead: "The Inspector is for exploring by hand; static scanners read metadata and code; hosted agent-security platforms inventory what exists across your SaaS. passmcp answers a different question: does this server behave safely, and can you prove it?"
compare_note: "Sources, as each project describes itself on 26 Sep 2026: Cisco mcp-scanner (github.com/cisco-ai-defense/mcp-scanner), Snyk agent-scan (github.com/snyk/agent-scan), MCP Inspector (github.com/modelcontextprotocol/inspector), and the public product pages of hosted agent-security platforms such as reco.ai. 'Not documented' means we found no public description of the capability, not proof that it is absent. Corrections are welcome as issues."

ledger_eyebrow: "Scoring"
ledger_title: "Every deduction named."
ledger_lead: "A grade with no arithmetic behind it is a brand, not a measurement. These are the six categories passmcp scores, their weights, and what the sample server lost in each."

evidence_eyebrow: "Evidence"
evidence_title: "Nothing passes without a request that showed it."
evidence_lead: "Two findings from the sample report, each with the request that produced it. In the report, every finding links to its request in the HAR file and to its guidance in the manual."

phases_eyebrow: "Method"
phases_title: "Nine phases, in the order an agent meets them."
phases_lead: "The order matters: a catalogue check means nothing if the handshake never completed, and a latency figure means nothing if half the calls failed. When a phase blocks, every later one is recorded as skipped, with the reason."

integrations_eyebrow: "Where it plugs in"
integrations_title: "One verdict, used everywhere a decision is made."
integrations_lead: "passmcp never sits in your agents' traffic. It produces evidence, and the tools that do sit there can act on it."
int_one_title: "GitHub Actions and GitLab CI"
int_one_text: "passmcp-action runs passmcp from its release image, pinned by digest, and writes the report, SARIF and an attestation. A GitLab template does the same."
int_two_title: "Your agents, through MCP"
int_two_text: "passmcp-server exposes passmcp as three read-only tools, so an agent can evaluate a server or verify an attestation. It is listed in the MCP Registry."
int_three_title: "agentgateway"
int_three_text: "An ExtMcp processor in passmcp-reporting lets agentgateway refuse MCP backends whose attestation is missing, stale or failing, verified offline, with no call to passmcp."
int_four_title: "Code scanning and test reports"
int_four_text: "SARIF for GitHub code scanning, JUnit XML for any CI, JSON and NDJSON for pipelines, HAR for devtools, OTLP traces for your collector."
int_five_title: "Your package manager"
int_five_text: "Homebrew, the Arch User Repository (yay -S passmcp), Nix, .deb and .rpm, a signed container image, or go install."
int_six_title: "Your own code"
int_six_text: "The Go packages the CLI is built on are public. The attestation verifier is Apache-2.0 with no dependencies, so any consumer can embed it."

trust_eyebrow: "Trust"
trust_title: "Auditable the way it asks servers to be."
trust_lead: "passmcp is software you run, not a service you send data to, so the questions that matter are about the software itself. Here is how to check each answer yourself."
trust_one_title: "Signed and attested releases"
trust_one_text: "Signed tags; checksums signed with keyless cosign; SLSA build provenance; a CycloneDX SBOM per archive; the container base pinned by digest."
trust_two_title: "No telemetry, ever"
trust_two_text: "No account, no analytics, no phone-home. passmcp contacts the server you named and the authorization endpoints it advertises, and nothing else unless you opt in by flag, as with --osv for advisories or --model for explain. That is a recorded decision, ADR 0006."
trust_three_title: "Never in the data path"
trust_three_text: "passmcp does not proxy, terminate or forward an agent's request, and no agent request waits on anything passmcp operates. ADR 0007 draws that line, and the gateway integrations respect it."
trust_four_title: "Compliance, stated honestly"
trust_four_text: "passmcp holds no SOC 2 or ISO 27001 certificate; those apply to service providers, and passmcp runs on yours. Every check is mapped to the SOC 2 Trust Services Criteria, ISO/IEC 27001:2022 Annex A and GDPR articles it evidences, released in 0.0.1, so its evidence drops into your audit. Mappings, not certifications: an auditor certifies."

context_eyebrow: "Why now"
context_title: "The dates your agent programme is working to."
context_lead: "Agents are moving into production while the guidance and the obligations around them arrive. Each date below links to its source."


faq_eyebrow: "Questions"
faq_title: "The things people ask before installing."
faq_lead: "Short answers. Longer ones are in the manual."
faq_one_q: "How is this different from the official MCP Inspector?"
faq_one_a: "The Inspector is an excellent place to explore a server by hand: click a tool, read a response, debug an OAuth flow. passmcp is the non-interactive counterpart. It runs 138 checks, scores the result, cites its evidence, signs an attestation and returns an exit code. Most teams use both."
faq_two_q: "How is it different from static MCP scanners?"
faq_two_a: "Scanners such as Cisco's mcp-scanner read tool metadata and source code. passmcp talks to the running server over its real transport, so it sees what the server does: whether it rejects a bad token, validates arguments, honours Origin, recovers a session. passmcp also reads the catalogue for hidden instructions and poisoning, so the two overlap on text but not on behaviour."
faq_three_q: "Does it support the stateless 2026-07-28 revision?"
faq_three_a: "Yes. All nine phases run on either generation. passmcp settles which revision a server speaks before first contact, because the shape of the first request depends on the answer."
faq_four_q: "Is it safe to run against production?"
faq_four_a: "It is designed for it. Only tools that declare readOnlyHint are called, and requests are throttled. Conformance probes are sent (an invalid token, an unknown method, malformed JSON, a session id the server never issued) to see how the server handles them, and nothing else adversarial. It is a diagnostic, not a penetration test."
faq_five_q: "Does it test stdio servers?"
faq_five_a: "Yes. passmcp --stdio -- <command> starts the server as a child process and runs every phase over its pipes. On Linux it also watches where the server connects, what it writes and what it spawns, and can seed decoy credentials to see whether it reads or sends them."
faq_six_q: "What does it cost, and what does it send back to you?"
faq_six_a: "It is free and open source: the engine is GPL-3.0 and the attestation format and verifier are Apache-2.0. It sends nothing back, and there is no telemetry, account or analytics."
faq_seven_q: "Can I verify an attestation without trusting you?"
faq_seven_a: "Yes. passmcp verify checks a statement offline, and the verifier is a dependency-free Apache-2.0 Go package you can read, vendor or reimplement. Sign statements with the tooling you already trust, such as cosign, and verify the signature before you act on the verdict."

install_eyebrow: "Get started"
install_title: "One command, and no account to make."
install_lead: "Install it, point it at a server, read the verdict. Everything below runs on your machine; the only requests passmcp makes are to the server you name."
readout_target: "acme-crm 2.4.0, passmcp's deliberately flawed fixture server"
readout_verdict: "5 failing checks to fix before agents rely on it"
readout_score: "69.25"
readout_grade: "C"
readout_note: "71 checks · 38 pass · 6 warn · 5 fail · 10 skipped · 12 info"
ledger_1_area: "Connectivity"
ledger_1_weight: "10"
ledger_1_score: "100"
ledger_1_status: "pass"
ledger_1_deduction: "0"
ledger_2_area: "Authorization"
ledger_2_weight: "20"
ledger_2_score: "95"
ledger_2_status: "pass"
ledger_2_deduction: "−1"
ledger_3_area: "Protocol"
ledger_3_weight: "20"
ledger_3_score: "0"
ledger_3_status: "fail"
ledger_3_deduction: "−20"
ledger_4_area: "Catalogue"
ledger_4_weight: "15"
ledger_4_score: "55"
ledger_4_status: "warn"
ledger_4_deduction: "−6.75"
ledger_5_area: "Execution"
ledger_5_weight: "20"
ledger_5_score: "85"
ledger_5_status: "warn"
ledger_5_deduction: "−3"
ledger_6_area: "Performance"
ledger_6_weight: "15"
ledger_6_score: "100"
ledger_6_status: "pass"
ledger_6_deduction: "0"
phase_1: "Connectivity"
phase_2: "Authorization"
phase_3: "Credentials"
phase_4: "Handshake"
phase_5: "Protocol"
phase_6: "Catalog"
phase_7: "Execution"
phase_8: "Performance"
phase_9: "Resilience"
evidence_1_req: "req#11"
evidence_1_id: "protocol.invalid_params"
evidence_1_title: "tools/call without a name is rejected"
evidence_1_detail: "a tools/call with no name succeeded"
evidence_2_req: "req#12"
evidence_2_id: "protocol.unknown_tool"
evidence_2_title: "Unknown tool is reported"
evidence_2_detail: "calling a non-existent tool returned success"
readout_version: "0.0.5"
---

## Install

```sh
brew install sebastienrousseau/tap/passmcp     # macOS and Linux
yay -S passmcp                                 # Arch Linux, or: paru -S passmcp
mise use -g github:sebastienrousseau/passmcp   # with mise
nix run github:sebastienrousseau/passmcp -- --help
go install satellion.com/passmcp/cmd/passmcp@v0.0.5
```

Then point it at a server:

```sh
passmcp check https://mcp.example.com/mcp
```

That is the whole first run. No account, no config file, no signup. Add a
credential when the server needs one:

```sh
passmcp check https://mcp.example.com/mcp --token-env MCP_TOKEN
```

Or open the same diagnostic in a browser, still running locally:

```sh
passmcp serve
```

<h2 id="verify">Verify</h2>

Every run can write an attestation. Check the one behind the sample report
yourself; `passmcp verify` works offline and trusts nothing but the bytes:

```sh
curl -fsSLO https://satellion.com/passmcp/sample/attestation.json
passmcp verify attestation.json
```

A gateway or registry does the same with the Apache-2.0 verifier in
[passmcp-reporting](https://github.com/sebastienrousseau/passmcp-reporting),
without running passmcp at all.

## In a pipeline

passmcp exits non-zero when a server fails, so it gates a merge without any
extra plumbing:

```sh
passmcp check "$MCP_ENDPOINT" --token-env MCP_TOKEN \
  --output json --report-dir ./passmcp-report
```

The report directory holds the JSON verdict, the NDJSON event stream and a
HAR archive of every exchange. Attach it to the build and the question
"how do you know?" has an answer that outlives the person who ran it.

## What it checks

Connectivity and TLS. How the server asks to be authorized, and whether it
refuses a bad token. The MCP handshake, and which generation of the protocol
it speaks — passmcp supports both the handshake revisions and the stateless
`2026-07-28` one. Protocol behaviour on the edge cases an agent will hit.
The tool catalogue, as a model reads it: descriptions, schemas, annotations,
and whether `$ref` and `$defs` resolve. Safe calls, with results checked
against the contracts the tools declare. Latency under repeat and parallel
calls. Recovery from a lost session, or from a server that turns out not to
be as stateless as it claims.

## What it will not do

It calls only tools that declare `readOnlyHint` unless you say otherwise.
It throttles itself. It sends one deliberately invalid token to check the
server rejects it, and nothing else adversarial. It is a diagnostic, not a
penetration test, and the difference is deliberate.

It also will not phone home. There is no telemetry, no account and no
analytics — the only requests passmcp makes are to the server you named.
