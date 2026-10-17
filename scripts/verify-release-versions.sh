#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
#
# Fail unless every place that names the family's version names the same
# one: the newest CHANGELOG heading, the release notes, the version the
# README's ecosystem section states, every `go install` and `go get` line
# on the Go module pages, the passmcp release the product page was built
# against, the passmcp-graph release its dashboard still shows, and the
# PASSMCP_REF and PASSMCP_GRAPH_REF examples. The passmcp family moves in
# lockstep, so every one of them is the same version.
#
#   scripts/verify-release-versions.sh            # the newest CHANGELOG version
#   scripts/verify-release-versions.sh v0.0.1     # a named one
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

newest=$(sed -nE 's/^## \[([0-9]+\.[0-9]+\.[0-9]+)\].*/\1/p' CHANGELOG.md | head -n1)
tag="${1:-${newest}}"
ver="${tag#v}"
[ -n "${ver}" ] || { echo "verify-release-versions: CHANGELOG.md has no '## [x.y.z]' heading" >&2; exit 2; }
fail=0
bad() { echo "verify-release-versions: $*" >&2; fail=1; }

[ "${newest}" = "${ver}" ] || bad "the newest CHANGELOG.md heading is '${newest}', not ${ver}"

notes="docs/releases/v${ver}.md"
if [ ! -f "${notes}" ]; then
  bad "${notes} does not exist"
elif ! grep -q '^## Highlights ⭐️$' "${notes}"; then
  bad "${notes} has no '## Highlights ⭐️' section"
fi

grep -Fq "Every component is released at **${ver}**" README.md ||
  bad "README.md's ecosystem section does not state ${ver}"

# Every pinned module version on the site; at least one must be found, so
# a pattern that stops matching cannot pass silently.
pins=$(grep -rEoh 'satellion\.com/[a-z0-9./-]+@v[0-9]+\.[0-9]+\.[0-9]+' content README.md || true)
if [ -z "${pins}" ]; then
  bad "no go install or go get line found to check"
elif stale=$(grep -v "@v${ver}\$" <<<"${pins}"); then
  bad "a module page pins a version other than ${ver}: ${stale//$'\n'/, }"
fi

built=$(sed -nE 's/^readout_version: "([^"]*)"$/\1/p' content/passmcp/index.md)
[ "${built}" = "${ver}" ] || bad "content/passmcp/index.md was built against passmcp '${built}', not ${ver}; run make data"

graph=$(sed -nE 's/^graph_version: "([^"]*)"$/\1/p' content/passmcp/index.md)
[ "${graph}" = "${ver}" ] || bad "content/passmcp/index.md shows passmcp-graph '${graph}', not ${ver}; run make graph-shot and update graph_version"

refs=$(grep -Eoh 'PASSMCP(_GRAPH)?_REF=v[0-9]+\.[0-9]+\.[0-9]+' Makefile README.md DEVELOPMENT.md || true)
if stale=$(grep -v "=v${ver}\$" <<<"${refs}"); then
  bad "a PASSMCP_REF or PASSMCP_GRAPH_REF example names a release other than ${ver}: ${stale//$'\n'/, }"
fi

[ "${fail}" -eq 0 ] && echo "verify-release-versions: every version reference agrees on ${ver}"
exit "${fail}"
