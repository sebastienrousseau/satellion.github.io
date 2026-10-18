# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Write the numbers the home page shows from passmcp's own sample report.

The page's score, grade, check counts and scoring ledger are front-matter
fields. Typing them by hand is how the old page came to show a score out of
120 and a ledger with categories passmcp never had. This script sets them from
the report.json that `scripts/samplereport` in passmcp writes, so the page shows
what passmcp produced, and `--check` fails CI when the committed page and the
report disagree.

    python3 scripts/site_data.py <report.json> content/passmcp/index.md <docs/checks.md> [--check]
"""

import json
import re
import sys
from pathlib import Path

LABELS = {
    "connectivity": "Connectivity",
    "authorization": "Authorization",
    "protocol": "Protocol",
    "catalog": "Catalogue",
    "execution": "Execution",
    "performance": "Performance",
}


def readout(report):
    """The headline figures: score, grade, target, verdict and counts."""
    score = report["score"]
    counts = report["counts"]
    total = sum(counts.values())
    return {
        "readout_score": f"{score['total']:g}",
        "readout_grade": score["grade"],
        "readout_target": f"{report['server']['name']} {report['server']['version']}, passmcp's deliberately flawed fixture server",
        "readout_verdict": f"{counts['fail']} failing checks to fix before agents rely on it",
        "readout_version": report["passmcp"]["version"],
        "readout_note": (
            f"{total} checks · {counts['pass']} pass · {counts['warn']} warn · "
            f"{counts['fail']} fail · {counts['skip']} skipped · {counts['info']} info"
        ),
    }


def status(score):
    return "pass" if score >= 90 else ("warn" if score >= 50 else "fail")


def ledger(categories):
    """One ledger row per scoring category, in the report's order."""
    out = {}
    for i, cat in enumerate(categories, start=1):
        lost = cat["weight"] * (100 - cat["score"]) / 100
        out[f"ledger_{i}_area"] = LABELS.get(cat["name"], cat["name"].title())
        out[f"ledger_{i}_weight"] = str(cat["weight"])
        out[f"ledger_{i}_score"] = f"{cat['score']:g}"
        out[f"ledger_{i}_status"] = status(cat["score"])
        out[f"ledger_{i}_deduction"] = "0" if lost == 0 else f"−{lost:g}"
    return out


def evidence(phases):
    """Two findings as the evidence cards: failures that cite the request
    that showed them, first in report order."""
    cited = [
        f for phase in phases for f in phase.get("findings") or [] if f.get("status") == "fail" and f.get("evidence")
    ]
    if len(cited) < 2:
        sys.exit("site_data: the sample report has fewer than two cited failures to show")
    out = {}
    for i, f in enumerate(cited[:2], start=1):
        out[f"evidence_{i}_req"] = ", ".join(f["evidence"])
        out[f"evidence_{i}_id"] = f["id"]
        out[f"evidence_{i}_title"] = f["title"]
        out[f"evidence_{i}_detail"] = f["detail"].replace('"', "'")
    return out


def fields(report):
    out = readout(report)
    out.update(ledger(report["score"]["categories"]))
    # The nine phases, in the order the report ran them.
    for i, phase in enumerate(report["phases"], start=1):
        out[f"phase_{i}"] = phase.get("title") or phase["name"]
    out.update(evidence(report["phases"]))
    return out


# Every place the page states passmcp's check count. The count is read from
# the release's docs/checks.md, which passmcp regenerates from its source; a
# typed figure is how the old page kept "76" long after passmcp had 92.
COUNT_FILES = ["content/passmcp/index.md", "content/index.md", "_layouts/index.html", "_layouts/base.html", "ssg.toml"]
COUNT_PATTERN = re.compile(r"\b\d{2,4}(?=( checks\b|&nbsp;checks\b| checks, \d+ phases))")


def check_count(checks_md):
    m = re.search(r"\*\*(\d+) checks\*\*", Path(checks_md).read_text())
    if not m:
        sys.exit(f"site_data: {checks_md} does not state its check count")
    return m.group(1)


def pin_install(text, version):
    """The go install line names the release the page was built against."""
    return re.sub(r"passmcp/cmd/passmcp@v[0-9]+\.[0-9]+\.[0-9]+", f"passmcp/cmd/passmcp@v{version}", text)


def apply(text, values):
    for key, value in values.items():
        line = f'{key}: "{value}"'
        pattern = re.compile(rf'(?m)^{re.escape(key)}: ".*"$')
        if pattern.search(text):
            text = pattern.sub(lambda _m, line=line: line, text, count=1)
        else:
            text = text.replace("\n---\n", f"\n{line}\n---\n", 1)
    return text


def stale_files(report, page_path, count):
    """Each count file whose text differs from what the release says, with
    the text it should have."""
    out = {}
    for path in COUNT_FILES:
        text = Path(path).read_text()
        new = COUNT_PATTERN.sub(count, text)
        if path == page_path:
            new = pin_install(apply(new, fields(report)), report["passmcp"]["version"])
            new = apply(new, {"metric_one_value": count})
        if new != text:
            out[path] = new
    return out


def main(argv):
    args = [a for a in argv[1:] if a != "--check"]
    check = "--check" in argv[1:]
    if len(args) != 3:
        sys.exit(__doc__)
    report_path, page_path, checks_md = args
    report = json.loads(Path(report_path).read_text())
    count = check_count(checks_md)
    stale = stale_files(report, page_path, count)
    version = report["passmcp"]["version"]
    if check and stale:
        sys.exit(f"site_data: {', '.join(stale)} disagree with passmcp {version}; run make data")
    if check:
        print(f"site_data: the page matches passmcp {version}: {count} checks, score {report['score']['total']:g}")
        return
    for path, new in stale.items():
        Path(path).write_text(new)
    print(
        f"site_data: {count} checks and the sample report written into "
        + (", ".join(stale) if stale else "nothing (already current)")
    )


if __name__ == "__main__":
    main(sys.argv)
