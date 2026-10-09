# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
#
# Build satellion.com from this repository and a release of passmcp.
#
# The site shows passmcp's real output, so it is built against a passmcp
# release: the sample report is passmcp run against its fixture server, the
# manual is passmcp's docs/, and the page's numbers come from that report.

.PHONY: all core site passmcp sample data check-data family check-family manual test coverage coverage-publish verify-versions readme-check lint complexity check serve clean help name-guard demo build

build: core

PASSMCP_REPO ?= https://github.com/sebastienrousseau/passmcp
# The latest release tag unless one is named: make site PASSMCP_REF=v0.0.4
PASSMCP_REF  ?= $(shell git ls-remote --tags --refs --sort=-v:refname $(PASSMCP_REPO) 'v*' | head -n1 | sed 's|.*refs/tags/||')
SSG_VERSION ?= 0.0.66
WORK := .build
DIST := dist
# The tests' own virtual environment: coverage.py, hash-locked.
TESTENV := $(WORK)/venv-test
# The family's coverage gate. coverage.py measures branches too, so the gate
# holds statements and branches together to this floor.
COVERAGE_MIN := 85

all: site

# passmcp at the release, checked out once per ref.
passmcp:
	@test -n "$(PASSMCP_REF)" || { echo "no passmcp release found" >&2; exit 1; }
	@if [ "$$(git -C $(WORK)/passmcp describe --tags --exact-match 2>/dev/null)" != "$(PASSMCP_REF)" ]; then \
	  rm -rf $(WORK)/passmcp; \
	  git clone --quiet --depth 1 --branch $(PASSMCP_REF) $(PASSMCP_REPO) $(WORK)/passmcp; \
	fi
	cd $(WORK)/passmcp && go build -o ../passmcp-bin ./cmd/passmcp

# passmcp's own sample report: passmcp run against its deliberately flawed fixture.
sample: passmcp
	rm -rf $(WORK)/sample
	cd $(WORK)/passmcp && go run ./scripts/samplereport/main.go ../passmcp-bin ../sample

# The page's score, grade, counts and ledger, from that report.
data: sample
	python3 scripts/site_data.py $(WORK)/sample/report.json content/passmcp/index.md $(WORK)/passmcp/docs/checks.md

check-data: sample
	python3 scripts/site_data.py $(WORK)/sample/report.json content/passmcp/index.md $(WORK)/passmcp/docs/checks.md --check

# The family table on the company page and passmcp's page, from the
# ecosystem.json of the passmcp release being built. site renders it from
# that release, as it does the numbers, and pull requests run check-family
# beside check-data. passmcp 0.0.2 publishes schema 2; family.py still reads
# schema 1, which passmcp 0.0.1 published.
FAMILY_MANIFEST ?= $(WORK)/passmcp/ecosystem.json

family: passmcp
	python3 scripts/family.py $(FAMILY_MANIFEST) _layouts/family.html $(PASSMCP_REF)

check-family: passmcp
	python3 scripts/family.py $(FAMILY_MANIFEST) _layouts/family.html $(PASSMCP_REF) --check

# The site's own scripts' tests (python3's unittest; no dependencies).
test:
	python3 -m unittest discover -s scripts -p 'test_*.py'

$(TESTENV)/.installed: scripts/requirements.txt
	python3 -m venv $(TESTENV)
	$(TESTENV)/bin/pip install --quiet --disable-pip-version-check --require-hashes -r scripts/requirements.txt
	touch $@

# The same tests under coverage.py, gated at COVERAGE_MIN, and the
# shields.io endpoint document behind the README's coverage badge.
coverage: $(TESTENV)/.installed
	$(TESTENV)/bin/python -m coverage erase
	$(TESTENV)/bin/python -m coverage run -m unittest discover -s scripts -p 'test_*.py'
	$(TESTENV)/bin/python -m coverage report -m --fail-under=$(COVERAGE_MIN)
	$(TESTENV)/bin/python -m coverage json -q -o $(WORK)/coverage-report.json
	python3 scripts/coverage_badge.py $(WORK)/coverage-report.json $(WORK)/coverage.json

# Into the built site, where the badge reads it: https://satellion.com/coverage.json.
# After core or site, because SSG wipes $(DIST) on every build.
coverage-publish: coverage
	@test -d $(DIST) || { echo "coverage-publish: build the site first (make core or make site)" >&2; exit 1; }
	cp $(WORK)/coverage.json $(DIST)/coverage.json

# The portfolio's complexity ceilings on the build's scripts: cyclomatic
# 10 per function (xenon's rank B) and cognitive 15 (complexipy).
complexity: $(TESTENV)/.installed
	$(TESTENV)/bin/xenon --max-absolute B --max-modules B --max-average A scripts
	$(TESTENV)/bin/complexipy scripts --max-complexity-allowed 15 --quiet

# Every version reference names the newest CHANGELOG release.
verify-versions:
	scripts/verify-release-versions.sh

readme-check:
	scripts/readme-check.sh

# The prose gates docs-lint.yml runs, for the tools installed locally.
lint: readme-check name-guard
	codespell
	npx --yes markdownlint-cli2@0.18.1

# Everything CI checks that needs no passmcp release.
check: lint complexity verify-versions coverage core

manual: passmcp
	python3 -m venv $(WORK)/venv
	$(WORK)/venv/bin/pip install --quiet --disable-pip-version-check --require-hashes -r $(WORK)/passmcp/docs/requirements.txt
	cd $(WORK)/passmcp && ../venv/bin/mkdocs build --strict --site-dir $(CURDIR)/$(WORK)/manual

# Always from the release being built, so a deployed page cannot show another
# release's numbers. Pull requests also run check-data, so the committed page
# is kept equal to what gets deployed.
# core is everything that needs no passmcp release: the company page, the
# product page with its committed numbers, the Go module and format pages,
# both icon sets and security.txt. It is what deploys before the first
# release exists, because Go needs the module pages to fetch that release.
core:
	@v=$$(ssg --version 2>/dev/null | awk '{print $$2}'); [ "$$v" = "$(SSG_VERSION)" ] || { echo "ssg $(SSG_VERSION) required, found '$$v'" >&2; exit 1; }
	ssg build -f ssg.toml
	# SSG renders pages and templates; static files are copied after it,
	# because it wipes its output directory on every build.
	mkdir -p $(DIST)/images && cp -R images/. $(DIST)/images/
	# Satellion's icons at the root, passmcp's beside its pages.
	mkdir -p $(DIST)/brand && cp -R brand/satellion $(DIST)/brand/
	cp brand/satellion/favicon.ico brand/satellion/favicon.svg brand/satellion/apple-touch-icon.png $(DIST)/
	mkdir -p $(DIST)/passmcp && cp brand/passmcp/* $(DIST)/passmcp/
	# SSG 0.0.63 links /highlight.css but writes it fingerprinted; publish
	# it under the linked name too until SSG rewrites that link itself.
	for f in $(DIST)/highlight.*.css; do [ -e "$$f" ] && cp "$$f" $(DIST)/highlight.css; done
	# security.txt (RFC 9116), from content/index.md's security_* keys. SSG
	# writes it at the root; the RFC's location is /.well-known/. The check
	# fails the build when Expires is under 30 days away (EU CRA).
	python3 scripts/security_txt.py $(DIST)/security.txt
	mkdir -p $(DIST)/.well-known && cp $(DIST)/security.txt $(DIST)/.well-known/security.txt
	python3 scripts/modules.py $(DIST)
	# SSG audits every build (ten quality pillars, WCAG 2.2 per page) but
	# only logs what it finds; the build fails on any finding instead.
	python3 scripts/quality_gate.py $(DIST)
	echo satellion.com > $(DIST)/CNAME
	@echo "core: built $(DIST)"

# site is core plus what comes from the passmcp release: the numbers on the
# product page, the family table, the manual and the sample report.
site: data family manual core
	cp -R $(WORK)/manual $(DIST)/passmcp/docs
	cp -R $(WORK)/sample $(DIST)/passmcp/sample
	# Last, because it indexes the finished tree.
	cd $(WORK)/passmcp && go run ./scripts/sitemap/main.go $(CURDIR)/$(DIST)
	@echo "site: built $(DIST) against passmcp $(PASSMCP_REF)"

# The README demo (.github/demo.gif): the company page and passmcp's page
# of the core build, served on loopback and captured by headless Chrome at
# 1440x900, four seconds each. A web page has no terminal session to
# record, so this recipe stands in for a VHS tape (AGENTS.md section 7.1.1).
# Needs Chrome, ffmpeg and timeout (coreutils): a headless Chrome that does
# not exit after writing its screenshot is stopped after 60 seconds, and the
# screenshot is what is checked.
CHROME ?= /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
DEMO_PORT ?= 17840
DEMO_PAGES := / /passmcp/
demo: core
	rm -rf $(WORK)/demo && mkdir -p $(WORK)/demo/profile
	python3 -m http.server $(DEMO_PORT) --bind 127.0.0.1 --directory $(DIST) >/dev/null 2>&1 & srv=$$!; \
	  trap 'kill $$srv' EXIT; sleep 1; n=0; \
	  for page in $(DEMO_PAGES); do n=$$((n + 1)); \
	    timeout 60 "$(CHROME)" --headless=new --user-data-dir="$(CURDIR)/$(WORK)/demo/profile" --no-first-run \
	      --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1440,900 \
	      --screenshot="$(CURDIR)/$(WORK)/demo/$$n.png" "http://127.0.0.1:$(DEMO_PORT)$$page" >/dev/null 2>&1 || true; \
	    test -s "$(WORK)/demo/$$n.png" || { echo "demo: no screenshot of $$page" >&2; exit 1; }; \
	  done
	ffmpeg -loglevel error -y -framerate 1/4 -i "$(WORK)/demo/%d.png" \
	  -vf "scale=1200:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a" \
	  -loop 0 .github/demo.gif
	@echo "demo: wrote .github/demo.gif"

serve: site
	cd $(DIST) && python3 -m http.server 8000

clean:
	rm -rf $(WORK) $(DIST)

help:
	@grep -E '^[a-z-]+:' $(MAKEFILE_LIST) | cut -d: -f1 | sort -u

# The project's retired names may not appear anywhere in this repository.
name-guard:
	./scripts/name-guard.sh
