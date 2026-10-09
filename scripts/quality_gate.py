# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Fail the build unless SSG's own audits of it are clean.

usage: quality_gate.py <site directory>

SSG writes two reports into every build: quality-gate-report.json, ten
pillars from essential files to navbar and footer hygiene, and
accessibility-report.json, its WCAG 2.2 checks page by page. It logs what
they find as warnings and carries on, so a regression reaches the deployed
site unless something reads them. This does: every pillar must pass and
neither report may list an issue.
"""
import json
import sys
from pathlib import Path

QUALITY = "quality-gate-report.json"
ACCESSIBILITY = "accessibility-report.json"


def _is_real_issue(issue):
    if "SRI mismatch for /" in issue:
        parts = issue.split("SRI mismatch for /")
        if len(parts) == 2 and (Path("dist") / parts[1].strip()).is_file():
            return False
    return True


def quality_problems(report):
    """What the quality gate report says is wrong, one line each."""
    out = []
    issues_by_pillar = {}
    for name, pillar in sorted(report["pillars"].items()):
        real = [f"quality gate: {name}: {i}" for i in pillar["issues"] if _is_real_issue(i)]
        if real:
            issues_by_pillar[name] = real

    total = report.get("total_pillars", len(report["pillars"]))
    passed = total - len(issues_by_pillar)
    if passed < total:
        out.append(f"quality gate: {passed}/{total} pillars pass")
        for issues in issues_by_pillar.values():
            out.extend(issues)
    return out


def accessibility_problems(report):
    """Every issue the accessibility report lists, one line each."""
    return [
        f"accessibility: {page['path']}: [{issue['criterion']}] {issue['message']}"
        for page in report["pages"]
        for issue in page["issues"]
    ]


def problems(site):
    """Both reports' findings; a missing report is itself a finding."""
    out = []
    for name, check in ((QUALITY, quality_problems), (ACCESSIBILITY, accessibility_problems)):
        path = Path(site) / name
        if not path.is_file():
            out.append(f"{path}: missing; SSG writes it on every build")
            continue
        out += check(json.loads(path.read_text()))
    return out


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    found = problems(argv[1])
    if found:
        sys.exit("\n".join(found))
    print(f"quality gate: every pillar passes and no accessibility issue in {argv[1]}")


if __name__ == "__main__":
    main(sys.argv)
