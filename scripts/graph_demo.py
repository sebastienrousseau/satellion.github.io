# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only
"""Write the passmcp-graph demo page from passmcp-graph's share-safe export.

usage: graph_demo.py <export.json> <index.md> <passmcp-graph version>

<export.json> is what `passmcp-graph dashboard --share-safe --format json`
prints: the dashboard's summary after the share-safe profile has replaced
endpoints, identities and configuration paths with placeholders. This
writes it as the front matter and Markdown body of the Control Centre
theme's overview page (graph-demo/_layouts/index.html), which SSG builds
into /passmcp-graph/demo/. Every name, count and finding on the page comes
from the export; the words around them are fixed here.

An export without "shareSafe": true is refused, so a private estate is
never published by accident. So is one with more clients or servers than
the layout has places for, rather than a map that silently drops some.
"""

import html
import json
import sys
from pathlib import Path

# The layout's places: three clients, four servers, four ring arcs.
CLIENT_SLOTS = 3
SERVER_SLOTS = 4
# passmcp-graph's server statuses, worst first (its servers.go statusRank),
# with the theme's severity colour for each. The colour is presentation:
# the status's own words are always shown beside it.
STATUSES = ("critical", "unattested", "stale", "ok")
STATUS_SEV = {
    "critical": "critical",
    "unattested": "high",
    "stale": "medium",
    "ok": "ok",
}
# The ring legend's words for each status, after passmcp-graph's hero.go.
STATUS_LEGEND = {
    "critical": "with critical findings",
    "unattested": "with no evidence",
    "stale": "with stale evidence",
    "ok": "with no failing server checks",
}
# The four key figures, by passmcp-graph metric id.
KPI_METRICS = ("paths", "paths.destructive", "servers.evidence", "score.mean")
# Characters Markdown would read as syntax inside a table cell.
MARKDOWN = str.maketrans({c: f"&#{ord(c)};" for c in "\\`*_[]|"})

# The page's fixed copy: labels, navigation and what the demo is.
PAGE = {
    "name": "passmcp-graph demo",
    "short_name": "Graph demo",
    "author": "Sebastien Rousseau",
    "language": "en-GB",
    "schema": "page",
    "changefreq": "weekly",
    "theme_style": "style-control-centre",
    "theme-color": "#3b2fb8",
    "brand_mark": "PG",
    "brand_tagline": "Fixture graph",
    "label_skip": "Skip to main content",
    "label_home": "passmcp-graph demo home",
    "label_menu": "Menu",
    "label_nav": "Dashboard",
    "label_theme": "Change colour theme",
    "label_theme_light": "Light",
    "label_theme_dark": "Dark",
    "label_theme_system": "System",
    "label_search": "Search this page",
    "search_placeholder": "Search servers, findings…",
    "label_explore": "Explore",
    "label_start": "Report an issue",
    "report_label": "passmcp-graph issues on GitHub",
    "report_href": "https://github.com/sebastienrousseau/passmcp-graph/issues",
    "locale_path": "/passmcp-graph/demo/",
    "nav_group_estate": "Graph",
    "nav_group_site": "Satellion",
    "nav_overview": "Overview",
    "nav_findings": "Findings",
    "nav_servers": "MCP servers",
    "nav_mitigation": "Next queries",
    "nav_about": "passmcp-graph",
    "about_href": "/passmcp-graph/",
    "nav_contact": "passmcp",
    "contact_href": "/passmcp/",
    "snapshot_title": "Share-safe snapshot",
    "og_image": "https://satellion.com/images/graph-dashboard.webp",
    "og_image_width": "1200",
    "og_image_height": "750",
    "og_image_alt": "passmcp-graph's dashboard of its published fixture graph",
    "title": "passmcp-graph demo: the fixture graph as a control centre",
    "keywords": "passmcp-graph, MCP, demo, dashboard",
    "layout": "index",
    "current_home": "true",
    "eyebrow": "passmcp-graph demo",
    "headline": "Which agents reach which servers",
    "note_label": "Share-safe",
    "map_title": "Clients, servers and their status",
    "clients_title": "Configured clients",
    "servers_title": "MCP servers",
    "ring_caption": "MCP servers",
    "ring_legend": "Servers by status:",
    "kpi_title": "Key figures",
    "alert_cta_primary": "See the next queries",
    "alert_cta_secondary": "See all findings",
}


class ExportError(ValueError):
    """The export cannot be published as the demo."""


def load(text):
    """The export, refused unless it is share-safe and fits the layout."""
    try:
        export = json.loads(text)
    except (json.JSONDecodeError, RecursionError) as e:
        raise ExportError(f"not JSON: {e}") from e
    if not isinstance(export, dict) or export.get("shareSafe") is not True:
        raise ExportError("not a share-safe export; run passmcp-graph dashboard --share-safe --format json")
    for key in (
        "agents",
        "servers",
        "findings",
        "evidenceGaps",
        "metrics",
        "generated",
    ):
        if key not in export:
            raise ExportError(f"no {key!r} field")
    if len(export["agents"]) > CLIENT_SLOTS or len(export["servers"]) > SERVER_SLOTS:
        raise ExportError(
            f"{len(export['agents'])} clients and {len(export['servers'])} servers;"
            f" the layout has places for {CLIENT_SLOTS} and {SERVER_SLOTS}"
        )
    return export


def cell(value):
    """Export text as Markdown table-cell text: no markup, no syntax."""
    return html.escape(str(value), quote=False).translate(MARKDOWN)


def mark(name):
    """Two letters for a node's icon: the initials of its first two words."""
    words = [w for w in name.replace(".", "-").replace("_", "-").split("-") if w]
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return name[:2].upper()


def server_name(server):
    """The server as passmcp-graph's dashboard names it."""
    return server["name"] or server["endpoint"]


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def client_fields(export):
    """Each configured client, coloured by the worst server it reaches."""
    status = {s["anchor"]: s["status"] for s in export["servers"]}
    out = {}
    for i, agent in enumerate(export["agents"], 1):
        reached = {status[p["server"]["anchor"]] for p in agent["paths"]}
        worst = next((s for s in STATUSES if s in reached), "ok")
        out[f"client_{i}_name"] = agent["name"]
        out[f"client_{i}_mark"] = mark(agent["name"])
        out[f"client_{i}_sev"] = STATUS_SEV[worst]
        out[f"client_{i}_meta"] = f"{plural(len(agent['paths']), 'tool path')}, {plural(agent['servers'], 'server')}"
    return out


def server_fields(export):
    """Each server, worst status first, with its score when it has one."""
    out = {}
    servers = sorted(export["servers"], key=lambda s: STATUSES.index(s["status"]))
    for i, server in enumerate(servers, 1):
        out[f"server_{i}_name"] = server_name(server)
        out[f"server_{i}_mark"] = mark(server_name(server))
        out[f"server_{i}_sev"] = STATUS_SEV[server["status"]]
        out[f"server_{i}_meta"] = f"{server['endpoint']}, {server['statusLabel']}"
        out[f"server_{i}_score"] = server["score"] or "No score"
    return out


def ring_fields(export):
    """One arc per status present, its length the status's share of servers."""
    total = len(export["servers"])
    out = {"ring_value": str(total)}
    start = 0
    groups = [(s, sum(1 for v in export["servers"] if v["status"] == s)) for s in STATUSES]
    for i, (status, count) in enumerate([g for g in groups if g[1]], 1):
        share = 100 * count / total
        out[f"ring_{i}_sev"] = STATUS_SEV[status]
        out[f"ring_{i}_count"] = str(count)
        out[f"ring_{i}_label"] = STATUS_LEGEND[status]
        # A 2-unit gap either side of each arc, as the theme's own demo draws.
        out[f"ring_{i}_dash"] = f"{max(share - 4, 1):g}"
        out[f"ring_{i}_offset"] = f"{start + 2:g}"
        start += share
    return out


def kpi_sev(metric):
    """ok when a figure has nothing left to act on; otherwise its weight."""
    if metric["id"] == "paths.destructive":
        return "high" if metric["value"] else "ok"
    if metric["id"] == "servers.evidence":
        return "ok" if metric["value"] == metric.get("of") else "medium"
    return "low"


def kpi_note(metric):
    """What the figure counts, in passmcp-graph's words.

    The mean score's own note describes its value field (how many servers
    were scored), so that count is said in words instead.
    """
    if metric["id"] == "score.mean":
        return f"Out of 100, over the {metric['value']} of {metric['of']} servers with a score"
    return metric["counts"]


def kpi_fields(export):
    """The four key figures, each with passmcp-graph's note of what it counts."""
    metrics = {m["id"]: m for m in export["metrics"]}
    out = {}
    for i, key in enumerate(KPI_METRICS, 1):
        if key not in metrics:
            raise ExportError(f"no {key!r} metric")
        m = metrics[key]
        out[f"kpi_{i}_label"] = m["label"]
        out[f"kpi_{i}_value"] = m["display"]
        out[f"kpi_{i}_note"] = kpi_note(m)
        out[f"kpi_{i}_sev"] = kpi_sev(m)
    return out


def alert_fields(export):
    """The item passmcp-graph puts first, when it names one."""
    top = export.get("topIssue")
    if not top:
        return {}
    return {
        "alert_sev": "critical" if top["severity"] == "critical" else "medium",
        "alert_kicker": "Look at first:",
        "alert_title": top["title"],
        "alert_text": f"{top['context']} Rule: {top['rule']}.",
    }


def page_fields(export, version):
    """The fields that say what the page is and when it was exported."""
    gaps = len(export["evidenceGaps"])
    return {
        "copyright_year": export["generated"][:4],
        "date": export["generated"][:10],
        "description": (
            f"passmcp-graph {version}'s published fixture graph, exported share-safe and shown as a"
            " control centre: which clients reach which MCP servers, what failed and what to query next."
        ),
        "lead": (
            f"passmcp-graph {version}'s published fixture graph, exported with"
            " passmcp-graph dashboard --share-safe --format json and built into this page by SSG."
        ),
        "note_text": "Endpoints, identities and configuration paths are placeholders written by passmcp-graph's share-safe profile.",
        "crumb_root": f"passmcp-graph {version} · fixture graph",
        "footer_note": f"A demonstration of passmcp-graph {version} on its own fixture graph. Nothing here is a real estate.",
        "label_demo_content": "Demonstration data from passmcp-graph's fixture.",
        "snapshot_time": export["generated"].replace("T", " ").replace("Z", " UTC"),
        "snapshot_note": f"Ages and staleness are as of the export, with a {export['staleDays']}-day threshold.",
        "nav_findings_count": str(len(export["findings"]) + gaps),
        "nav_servers_count": str(len(export["servers"])),
    }


def front_matter(export, version):
    """Every field the layout reads, in a stable order."""
    fields = dict(PAGE)
    for part in (
        page_fields(export, version),
        alert_fields(export),
        client_fields(export),
        server_fields(export),
        ring_fields(export),
        kpi_fields(export),
    ):
        fields.update(part)
    # JSON strings are YAML double-quoted scalars.
    lines = [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fields.items()]
    return "---\n" + "\n".join(lines) + "\n---\n"


def age(server):
    """The evidence age as passmcp-graph's dashboard words it."""
    if not server.get("attestation"):
        return "Not supplied"
    if not server["ageDays"]:
        return "Unknown"
    return "1 day" if server["ageDays"] == "1" else f"{server['ageDays']} days"


def pill(sev, words):
    return f'<span class="pill sev-{sev}">{cell(words)}</span>'


def code(text):
    return f"<code>{cell(text)}</code>"


def attention(export):
    """Findings then evidence gaps, each as (title, path, severity, age, next).

    Severity follows passmcp-graph's command centre: a critical finding is
    critical, any other finding medium, and an evidence gap low.
    """
    servers = {s["anchor"]: s for s in export["servers"]}
    rows = []
    for f in export["findings"]:
        sev = "critical" if f["severity"] == "critical" else "medium"
        rows.append((f["title"], f["path"], sev, age(servers[f["server"]["anchor"]]), f["next"]))
    for g in export["evidenceGaps"]:
        path = ", ".join(c["name"] for c in g["clients"]) + " -> " + g["server"]["name"]
        rows.append((g["title"], path, "low", age(servers[g["server"]["anchor"]]), g["next"]))
    return rows


def panel(anchor, span, title, note, inner):
    return (
        f'<section class="cc-panel cc-span-{span}" id="{anchor}" aria-labelledby="{anchor}-heading">\n'
        f'<div class="cc-panel-head"><h2 id="{anchor}-heading">{title}</h2><p>{cell(note)}</p></div>\n'
        f"{inner}\n</section>\n"
    )


def table(anchor, head, rows):
    lines = ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return (
        f'<div class="cc-table" role="region" aria-labelledby="{anchor}-heading" tabindex="0">\n\n'
        + "\n".join(lines)
        + "\n\n</div>"
    )


def findings_panel(rows):
    body = [(cell(t), cell(p), pill(s, s.capitalize()), cell(a)) for t, p, s, a, _ in rows]
    inner = table("findings", ("Finding", "Path", "Severity", "Evidence age"), body)
    return panel(
        "findings",
        7,
        "Findings",
        f"{len(rows)} open: findings, then evidence gaps",
        inner,
    )


def queries_panel(rows):
    steps = "\n".join(f"<li><strong>{cell(t)}</strong> {code(n)}</li>" for t, _, _, _, n in rows)
    note = "The passmcp-graph query that shows each item's evidence"
    return panel("mitigation", 5, "Next queries", note, f'<ol class="cc-steps">\n{steps}\n</ol>')


def servers_panel(export):
    servers = sorted(export["servers"], key=lambda s: STATUSES.index(s["status"]))
    body = [
        (
            cell(server_name(s)),
            code(s["endpoint"]),
            cell(s["transport"]),
            cell(", ".join(c["name"] for c in s["clients"])),
            str(s["tools"]),
            cell(age(s)),
            pill(STATUS_SEV[s["status"]], s["statusLabel"]),
            cell(s["score"] or "No score"),
        )
        for s in servers
    ]
    head = (
        "Server",
        "Endpoint",
        "Transport",
        "Reached by",
        "Tools",
        "Evidence age",
        "Status",
        "Score",
    )
    inner = table("servers", head, body)
    return panel(
        "servers",
        12,
        "MCP servers",
        f"{len(servers)} configured, scored from their attestations",
        inner,
    )


def render(export, version):
    """The page: front matter, then the dashboard panels as its body."""
    rows = attention(export)
    body = findings_panel(rows) + "\n" + queries_panel(rows) + "\n" + servers_panel(export)
    return front_matter(export, version) + body


def main(argv):
    if len(argv) != 4:
        sys.exit(__doc__)
    source, out, version = Path(argv[1]), Path(argv[2]), argv[3].removeprefix("v")
    try:
        page = render(load(source.read_text()), version)
    except (OSError, ExportError, KeyError, TypeError, AttributeError, ValueError) as e:
        sys.exit(f"graph_demo: {source}: {e}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"graph_demo: wrote {out} from {source}")


if __name__ == "__main__":
    main(sys.argv)
