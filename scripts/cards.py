"""Self-hosted Undertale-style profile cards (pixel font, no third-party image services).

Recreates the game's overworld menu: a small status box (name / LV / HP / G), the ITEM-STAT-CELL menu with the SOUL
cursor, and the big page on the right. Data is the owner's public GitHub activity (GraphQL API).
  stat.svg      STAT page   (AT = commits (+PRs), DF = public repos (+followers), EXP = contributions, GOLD = stars)
  items.svg     ITEM page   (languages by share, USE / INFO / DROP row)
  activity.svg  last 31 days of contributions as pixel bars
  repo-<name>.svg  project dialog boxes

  GITHUB_TOKEN=... python scripts/cards.py WaelYTz            # in GitHub Actions
  python scripts/cards.py WaelYTz --data data.json            # local preview from a saved API response
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

import ut

FEATURED = ["trafficflowbench-2026", "Refactoring-Swarm-El-equipe", "resist-one-road-out", "vec-leaderboard-insights",
            "ML_AlgorithmsFromScratch"]
OUT = Path("dist")
NAME = "Wael"

QUERY = """
query($login: String!) {
  user(login: $login) {
    login name
    followers { totalCount }
    pullRequests { totalCount }
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


def numbers(u: dict) -> dict:
    cc = u["contributionsCollection"]
    exp = cc["contributionCalendar"]["totalContributions"]
    return dict(exp=exp, nxt=100 - exp % 100,
                at=cc["totalCommitContributions"] + cc["restrictedContributionsCount"], at_b=u["pullRequests"]["totalCount"],
                df=u["repositories"]["totalCount"], df_b=u["followers"]["totalCount"],
                gold=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]))


def side_panel(n: dict, cursor: str) -> str:
    """Left column of the overworld menu: status box + ITEM / STAT / CELL with the SOUL on `cursor`."""
    s = 2.6
    status = (ut.box(20, 20, 220, 150) + ut.text(NAME, 44, 44, 3.2)
              + ut.text("LV  20", 44, 88, 2.2) + ut.text("HP  99/99", 44, 112, 2.2) + ut.text(f"G   {n['gold']}", 44, 136, 2.2))
    menu = ut.box(20, 186, 220, 150)
    for i, label in enumerate(("ITEM", "STAT", "CELL")):
        y = 214 + 38 * i
        menu += ut.text(label, 84, y, s)
        if label == cursor:
            menu += ut.soul(48, y + 1, 2.6, 'class="beat"')
    return status + menu


def stat_card(u: dict) -> str:
    W, H = 940, 356
    n = numbers(u)
    x, x2, s = 300, 600, 2.6
    page = (ut.box(256, 20, 664, 316) + ut.text(f'"{NAME}"', x, 48, 3.2)
            + ut.text("LV  20", x, 96, s) + ut.text("HP  99 / 99", x, 126, s)
            + ut.text(f"AT  {n['at']}({n['at_b']})", x, 172, s) + ut.text(f"EXP: {n['exp']}", x2, 172, s)
            + ut.text(f"DF  {n['df']}({n['df_b']})", x, 202, s) + ut.text(f"NEXT: {n['nxt']}", x2, 202, s)
            + ut.text("WEAPON: Python", x, 240, s) + ut.text("ARMOR: PyTorch", x, 268, s)
            + ut.text(f"GOLD: {n['gold']}", x, 308, s) + ut.text("KILLS: 0", x2, 308, s))
    return ut.svg(W, H, side_panel(n, "STAT") + page, "Undertale STAT menu with GitHub stats", ut.BEAT)


def items_card(u: dict) -> str:
    W, H = 940, 356
    n = numbers(u)
    agg: dict[str, int] = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            agg[e["node"]["name"]] = agg.get(e["node"]["name"], 0) + e["size"]
    top = sorted(agg.items(), key=lambda kv: -kv[1])[:6]
    tot = sum(v for _, v in top) or 1
    page = ut.box(256, 20, 664, 316)
    for i, (name, size) in enumerate(top):
        y = 46 + 38 * i
        page += ut.text(name, 330, y, 2.6) + ut.text(f"{100 * size / tot:.1f}%", 880, y, 2.6, anchor="end")
    page += ut.text("USE", 330, 290, 2.6) + ut.text("INFO", 520, 290, 2.6) + ut.text("DROP", 720, 290, 2.6)
    page += ut.soul(296, 47, 2.6, 'class="beat"')
    return ut.svg(W, H, side_panel(n, "ITEM") + page, "Undertale ITEM menu with languages", ut.BEAT)


def calendar(u: dict) -> list[tuple[str, int]]:
    days = [(d["date"], d["contributionCount"]) for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    today = dt.date.today().isoformat()
    return [d for d in days if d[0] <= today]


def activity_card(u: dict) -> str:
    W, H = 940, 236
    days = calendar(u)[-31:]
    mx = max(1, max(c for _, c in days))
    x0, base, ch, bw, gap = 44, 196, 120, 22, 5.6
    body = [ut.box(0, 0, W, H), ut.text("* Last 31 days", 30, 24, 2.6),
            ut.text(f"PEAK {mx} - TOTAL {sum(c for _, c in days)}", W - 30, 26, 2.2, ut.GREY, "end")]
    for i, (_, c) in enumerate(days):
        x = x0 + i * (bw + gap)
        if c == 0:
            body.append(f'<rect x="{x:.1f}" y="{base - 4}" width="{bw}" height="4" fill="#444"/>')
            continue
        h = max(8.0, round(ch * c / mx / 4) * 4)
        col = ut.YELLOW if i == len(days) - 1 else ut.WHITE
        body.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" fill="{col}" class="up" '
                    f'style="animation-delay:{.03 * i:.2f}s"/>')
    body.append(ut.text(days[0][0], 44, 208, 1.8, ut.GREY) + ut.text(days[-1][0], W - 44, 208, 1.8, ut.GREY, "end"))
    style = (".up { transform-box: fill-box; transform-origin: bottom; animation: up .8s steps(8) backwards; }"
             "@keyframes up { from { transform: scaleY(0); } }")
    return ut.svg(W, H, "".join(body), "Contributions in the last 31 days", style)


def journey_card(u: dict) -> str:
    """The year's contribution grid as pixel cells; the SOUL slithers through it like the contribution snake, eating
    every lit day (flash, then dark), then the grid refills and the hunt loops."""
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    W, H, cell, gap = 940, 236, 12, 3
    step = cell + gap
    n = len(weeks)
    x0 = (W - n * step + gap) / 2
    y0 = 92
    EMPTY = "#1c1c1c"
    shade = lambda c: EMPTY if c == 0 else "#5a5a5a" if c <= 2 else "#b4b4b4" if c <= 5 else "#ffffff" if c <= 9 else ut.YELLOW
    grid = {}
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            grid[(wi, dt.date.fromisoformat(d["date"]).isoweekday() % 7)] = d["contributionCount"]   # Sunday = 0

    # greedy hunt: always head for the nearest lit cell, one grid step at a time (horizontal, then vertical)
    targets = {k for k, c in grid.items() if c > 0}
    pos, path, eaten_at = (-1, 0), [(-1, 0)], {}
    while targets:
        tgt = min(targets, key=lambda k: (abs(k[0] - pos[0]) + abs(k[1] - pos[1]), k[0], k[1]))
        while pos != tgt:
            if pos[0] != tgt[0]:
                pos = (pos[0] + (1 if tgt[0] > pos[0] else -1), pos[1])
            else:
                pos = (pos[0], pos[1] + (1 if tgt[1] > pos[1] else -1))
            path.append(pos)
            if pos in targets:
                eaten_at[pos] = len(path) - 1
                targets.discard(pos)
    while pos[0] < n:                                                     # leave the board to the right
        pos = (pos[0] + 1, pos[1]); path.append(pos)
    per = 0.075
    hold = 1.6
    dur = (len(path) - 1) * per + hold
    t_of = lambda i: i * per / dur

    xy = [(x0 + c * step, y0 + r * step) for c, r in path]
    vals = ";".join(f"{x:.1f},{y:.1f}" for x, y in xy) + f";{xy[-1][0]:.1f},{xy[-1][1]:.1f}"
    kts = ";".join(f"{t_of(i):.5f}" for i in range(len(path))) + ";1"

    def mover(begin: float, inner: str) -> str:
        return (f'<g transform="translate({xy[0][0]:.1f},{xy[0][1]:.1f})"><animateTransform attributeName="transform" type="translate" '
                f'calcMode="linear" dur="{dur:.2f}s" begin="{begin:.3f}s" repeatCount="indefinite" values="{vals}" keyTimes="{kts}"/>{inner}</g>')

    cells = []
    for (wi, wd), c in grid.items():
        x, y = x0 + wi * step, y0 + wd * step
        anim = ""
        if (wi, wd) in eaten_at:
            te = t_of(eaten_at[(wi, wd)])
            anim = (f'<animate attributeName="fill" calcMode="discrete" dur="{dur:.2f}s" repeatCount="indefinite" '
                    f'values="{shade(c)};#ffffff;{EMPTY}" keyTimes="0;{te:.5f};{min(0.9999, te + 0.06 / dur):.5f}"/>')
        cells.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" fill="{shade(c)}">{anim}</rect>')

    tail = ""                                                             # just the SOUL, no tail
    head = mover(0, ut.soul(-1, 0, 2))
    body = (ut.box(0, 0, W, H) + ut.text(f"* {total} contributions this year.", 30, 26, 2.6)
            + ut.text("less", W - 250, 56, 1.6, ut.GREY)
            + "".join(f'<rect x="{W - 206 + i * 16}" y="54" width="12" height="12" fill="{c}"/>'
                      for i, c in enumerate([EMPTY, "#5a5a5a", "#b4b4b4", "#ffffff", ut.YELLOW]))
            + ut.text("more", W - 120, 56, 1.6, ut.GREY) + "".join(cells) + tail + head)
    return ut.svg(W, H, body, f"{total} contributions this year; the SOUL hunts them like the contribution snake")

def wrap(s: str, n: int, lines: int) -> list[str]:
    out, cur = [], ""
    for word in ut.clean(s).split():
        if len(cur) + len(word) + (1 if cur else 0) > n:
            out.append(cur); cur = word
        else:
            cur = f"{cur} {word}".strip()
    out.append(cur)
    if len(out) > lines:
        out = out[:lines]; out[-1] = out[-1][: n - 3].rstrip() + "..."
    return out


def repo_card(r: dict) -> str:
    W, H = 470, 186
    body = [ut.box(0, 0, W, H), ut.text(f"* {r['name']}", 26, 24, 2.3)]
    for i, line in enumerate(wrap(r["description"] or "", 38, 4)):
        body.append(ut.text(line, 26, 62 + 22 * i, 1.8))
    lang = (r["primaryLanguage"] or {}).get("name", "")
    body.append(ut.text(f"{lang}   STARS {r['stargazerCount']}   FORKS {r['forkCount']}", 26, 158, 1.8, ut.GREY))
    return ut.svg(W, H, "".join(body), r["name"])


def main():
    login = sys.argv[1]
    u = (json.load(open(sys.argv[sys.argv.index("--data") + 1], encoding="utf-8"))["data"]["user"]
         if "--data" in sys.argv else fetch(login))
    OUT.mkdir(exist_ok=True)
    cards = {"stat.svg": stat_card(u), "items.svg": items_card(u), "activity.svg": activity_card(u), "soul-hunt.svg": journey_card(u)}
    byname = {r["name"]: r for r in u["repositories"]["nodes"]}
    for name in FEATURED:
        if name in byname:
            cards[f"repo-{name}.svg"] = repo_card(byname[name])
    for f, s in cards.items():
        (OUT / f).write_text(s, encoding="utf-8")
    print("wrote", ", ".join(cards))


if __name__ == "__main__":
    main()
