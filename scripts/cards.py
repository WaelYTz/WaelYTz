"""Self-hosted profile cards (no third-party image services).

Fetches public data for the profile owner from the GitHub GraphQL API and writes animated SVG cards to dist/:
  stats.svg, langs.svg, streak.svg, activity.svg, repo-<name>.svg

  GITHUB_TOKEN=... python scripts/cards.py WaelYTz            # in GitHub Actions
  python scripts/cards.py WaelYTz --data data.json            # local preview from a saved API response
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape
from pathlib import Path

FEATURED = ["trafficflowbench-2026", "Refactoring-Swarm-El-equipe", "resist-one-road-out", "vec-leaderboard-insights"]
OUT = Path("dist")
BG, PANEL, TEXT, MUTED = "#0d1117", "#161b22", "#e6edf3", "#8b949e"
A1, A2, A3 = "#7c3aed", "#c026d3", "#c4b5fd"
FONT = "'JetBrains Mono','Fira Code',Consolas,'Segoe UI',monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    login name
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        name description stargazerCount forkCount
        primaryLanguage { name color }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch(login: str) -> dict:
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
                                          "Content-Type": "application/json", "User-Agent": "profile-cards"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if "errors" in d:
        raise SystemExit(d["errors"])
    return d["data"]["user"]


def frame(w: int, h: int, title: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{A1}"/><stop offset="1" stop-color="{A2}"/></linearGradient>
  <linearGradient id="gv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{A2}" stop-opacity=".55"/><stop offset="1" stop-color="{A1}" stop-opacity="0"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  text {{ font-family: {FONT}; fill: {TEXT}; }}
  .t {{ font-size: 15px; font-weight: 700; fill: {A3}; }}
  .m {{ fill: {MUTED}; font-size: 12px; }}
  .v {{ font-size: 13px; font-weight: 700; }}
  .f {{ animation: fade .6s ease-out backwards; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  @keyframes dash {{ from {{ stroke-dashoffset: var(--len); }} to {{ stroke-dashoffset: var(--off); }} }}
</style>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="{BG}" stroke="url(#g)" stroke-opacity=".7"/>
<rect x="1" y="1" width="{w - 2}" height="3" rx="1.5" fill="url(#g)"/>
<text x="22" y="34" class="t">{escape(title)}</text>
{body}
</svg>"""


def stats_card(u: dict) -> str:
    repos = u["repositories"]["nodes"]
    cc = u["contributionsCollection"]
    rows = [("contributions (12 mo)", cc["contributionCalendar"]["totalContributions"]),
            ("commits (12 mo)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
            ("pull requests", u["pullRequests"]["totalCount"]),
            ("public repos", u["repositories"]["totalCount"]),
            ("stars earned", sum(r["stargazerCount"] for r in repos)),
            ("followers", u["followers"]["totalCount"])]
    body = []
    for i, (k, v) in enumerate(rows):
        y = 64 + i * 24
        body.append(f'<g class="f" style="animation-delay:{.12 * i:.2f}s"><circle cx="28" cy="{y - 4}" r="3.5" fill="url(#g)" filter="url(#glow)"/>'
                    f'<text x="40" y="{y}" class="m">{k}</text><text x="250" y="{y}" class="v" text-anchor="end">{v:,}</text></g>')
    total = rows[0][1]
    r, c = 52, 2 * 3.14159 * 52
    frac = min(1.0, total / max(total, 500))
    body.append(f'<g transform="translate(360 112)"><circle r="{r}" fill="none" stroke="{PANEL}" stroke-width="10"/>'
                f'<circle r="{r}" fill="none" stroke="url(#g)" stroke-width="10" stroke-linecap="round" transform="rotate(-90)" filter="url(#glow)" '
                f'stroke-dasharray="{c:.1f}" style="--len:{c:.1f};--off:{c * (1 - frac):.1f};stroke-dashoffset:{c * (1 - frac):.1f};animation:dash 1.4s ease-out"/>'
                f'<text y="2" text-anchor="middle" style="font-size:22px;font-weight:800">{total:,}</text>'
                f'<text y="22" text-anchor="middle" class="m" style="font-size:10px">contributions</text></g>')
    return frame(470, 215, "⚡ telemetry", "\n".join(body))


def langs_card(u: dict) -> str:
    agg: dict[str, list] = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            a = agg.setdefault(e["node"]["name"], [0, e["node"]["color"] or A3])
            a[0] += e["size"]
    top = sorted(agg.items(), key=lambda kv: -kv[1][0])[:6]
    tot = sum(v[0] for _, v in top) or 1
    x, bars = 22.0, []
    for name, (size, col) in top:
        w = 426 * size / tot
        bars.append(f'<rect x="{x:.1f}" y="52" width="{max(w, 2):.1f}" height="12" fill="{col}" style="transform-origin:22px 58px;animation:grow 1s ease-out backwards"/>')
        x += w
    legend = []
    for i, (name, (size, col)) in enumerate(top):
        cx, cy = 22 + (i % 2) * 220, 92 + (i // 2) * 26
        legend.append(f'<g class="f" style="animation-delay:{.1 * i:.2f}s"><circle cx="{cx + 6}" cy="{cy - 4}" r="5.5" fill="{col}"/>'
                      f'<text x="{cx + 18}" y="{cy}" class="v" style="font-weight:600">{escape(name)}</text>'
                      f'<text x="{cx + 200}" y="{cy}" class="m" text-anchor="end">{100 * size / tot:.1f}%</text></g>')
    body = f'<clipPath id="bar"><rect x="22" y="52" width="426" height="12" rx="6"/></clipPath><g clip-path="url(#bar)">{"".join(bars)}</g>' + "".join(legend)
    return frame(470, 175, "🧬 languages", body)


def calendar(u: dict) -> list[tuple[str, int]]:
    days = [(d["date"], d["contributionCount"]) for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    today = dt.date.today().isoformat()
    return [d for d in days if d[0] <= today]


def streak_card(u: dict) -> str:
    days = calendar(u)
    cur = 0
    for i, (_, n) in enumerate(reversed(days)):
        if n > 0:
            cur += 1
        elif i > 0:            # today may still be empty
            break
    best = run = 0
    for _, n in days:
        run = run + 1 if n > 0 else 0
        best = max(best, run)
    active = sum(1 for _, n in days if n > 0)
    cols = [("current streak", f"{cur} d"), ("longest streak", f"{best} d"), ("active days (12 mo)", f"{active}")]
    body = []
    for i, (k, v) in enumerate(cols):
        cx = 85 + i * 150
        body.append(f'<g class="f" style="animation-delay:{.15 * i:.2f}s"><text x="{cx}" y="92" text-anchor="middle" '
                    f'style="font-size:30px;font-weight:800;fill:url(#g)" filter="url(#glow)">{v}</text>'
                    f'<text x="{cx}" y="118" text-anchor="middle" class="m">{k}</text></g>')
    body.append(f'<text x="235" y="150" text-anchor="middle" class="m" style="font-size:10px">{days[0][0]} → {days[-1][0]}</text>')
    return frame(470, 165, "🔥 streak", "\n".join(body))


def activity_card(u: dict) -> str:
    days = calendar(u)[-31:]
    w, h, x0, y0, ch = 940, 200, 30, 50, 120
    mx = max(1, max(n for _, n in days))
    step = (w - 2 * x0) / (len(days) - 1)
    pts = [(x0 + i * step, y0 + ch - ch * n / mx) for i, (_, n) in enumerate(days)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{x0},{y0 + ch} " + line + f" {pts[-1][0]:.1f},{y0 + ch}"
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#fff" class="f" style="animation-delay:{.02 * i:.2f}s"/>' for i, (x, y) in enumerate(pts))
    grid = "".join(f'<line x1="{x0}" x2="{w - x0}" y1="{y0 + ch * k / 4:.1f}" y2="{y0 + ch * k / 4:.1f}" stroke="{PANEL}"/>' for k in range(5))
    labels = (f'<text x="{x0}" y="{h - 12}" class="m">{days[0][0]}</text>'
              f'<text x="{w - x0}" y="{h - 12}" class="m" text-anchor="end">{days[-1][0]}</text>'
              f'<text x="{w - x0}" y="34" class="m" text-anchor="end">peak {mx}/day · {sum(n for _, n in days)} in 31 days</text>')
    body = (grid + f'<polygon points="{area}" fill="url(#gv)" class="f"/>'
            f'<polyline points="{line}" fill="none" stroke="url(#g)" stroke-width="3" stroke-linejoin="round" filter="url(#glow)" '
            f'stroke-dasharray="3000" style="--len:3000;--off:0;animation:dash 2s ease-out"/>' + dots + labels)
    return frame(w, h, "📈 last 31 days", body)


def wrap(s: str, n: int) -> list[str]:
    out, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + 1 > n:
            out.append(cur); cur = word
        else:
            cur = f"{cur} {word}".strip()
    out.append(cur)
    return out[:2] if len(out) <= 2 else [out[0], out[1][: n - 1] + "…"]


def repo_card(r: dict) -> str:
    desc = wrap(r["description"] or "", 54)
    lang = r["primaryLanguage"] or {"name": "", "color": MUTED}
    body = "".join(f'<text x="22" y="{62 + 18 * i}" class="m f" style="animation-delay:{.1 * i:.1f}s">{escape(t)}</text>' for i, t in enumerate(desc))
    body += (f'<circle cx="28" cy="{110}" r="5.5" fill="{lang["color"] or MUTED}"/><text x="40" y="114" class="m">{escape(lang["name"])}</text>'
             f'<text x="200" y="114" class="m">★ {r["stargazerCount"]}</text><text x="250" y="114" class="m">⑂ {r["forkCount"]}</text>')
    return frame(470, 132, r["name"], body)


def main():
    login = sys.argv[1]
    u = json.load(open(sys.argv[sys.argv.index("--data") + 1], encoding="utf-8"))["data"]["user"] if "--data" in sys.argv else fetch(login)
    OUT.mkdir(exist_ok=True)
    cards = {"stats.svg": stats_card(u), "langs.svg": langs_card(u), "streak.svg": streak_card(u), "activity.svg": activity_card(u)}
    byname = {r["name"]: r for r in u["repositories"]["nodes"]}
    for n in FEATURED:
        if n in byname:
            cards[f"repo-{n}.svg"] = repo_card(byname[n])
    for f, s in cards.items():
        (OUT / f).write_text(s, encoding="utf-8")
    print("wrote", ", ".join(cards))


if __name__ == "__main__":
    main()
