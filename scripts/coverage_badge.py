# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Write the shields.io endpoint document behind the README's coverage badge.

usage: coverage_badge.py <coverage.py JSON report> <coverage.json to write>

The input is what `coverage json` writes; the figure is its statement
coverage, as the rest of the passmcp family reports. The output is the
endpoint schema shields.io reads, in the family's colour bands:
brightgreen from 90, green from 85 (the gate), yellow from 70, red below.
The percentage is truncated, not rounded, so 84.96% reads 84.9% and the
badge never shows the gate as met when it is not.
"""

import json
import math
import sys
from pathlib import Path

BANDS = ((90, "brightgreen"), (85, "green"), (70, "yellow"))


def badge(pct):
    shown = math.floor(pct * 10) / 10
    colour = next((c for floor, c in BANDS if shown >= floor), "red")
    return {"schemaVersion": 1, "label": "coverage", "message": f"{shown:.1f}%", "color": colour}


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    totals = json.loads(Path(argv[1]).read_text())["totals"]
    doc = badge(totals["percent_statements_covered"])
    Path(argv[2]).write_text(json.dumps(doc, separators=(",", ":")) + "\n")
    print(f"coverage_badge: {doc['message']} written to {argv[2]}")


if __name__ == "__main__":
    main(sys.argv)
