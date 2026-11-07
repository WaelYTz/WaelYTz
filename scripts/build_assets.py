"""Static Undertale-style graphics for the profile README (pixel font, no external assets).

  python scripts/build_assets.py   -> assets/ut-header.svg, assets/ut-technoblade.svg, assets/ut-footer.svg
"""
from pathlib import Path

import ut

OUT = Path("assets")

STAR = [".....#.....", ".....#.....", "....###....", "....###....", "###########", ".#########.",
        "..#######..", "...#####...", "..###.###..", ".##.....##.", "##.......##"]
CROWN = ["#.....#.....#", "##...###...##", "###.#####.###", "#############", "##p##p#p##p##", "#############",
         "hhhhhhhhhhhhh"]


def header() -> str:
    W, H, D = 900, 360, 6.0
    title = ut.text("WAEL", 450, 26, 15, ut.WHITE, "middle")
    tag = ut.text("ML engineer - AI agent builder - competition data scientist", 450, 156, 2.2, ut.GREY, "middle")
    # save menu (white rows, then the yellow "file saved" state, like the game)
    bx, by, bw, bh = 140, 196, 620, 148
    rows_white = (ut.text("WAEL", bx + 34, by + 26, 3.2) + ut.text("LV 20", bx + bw / 2, by + 26, 3.2, anchor="middle")
                  + ut.text("20:26", bx + bw - 34, by + 26, 3.2, anchor="end")
                  + ut.text("Kaggle - Zindi - GitHub", bx + 34, by + 66, 3.2)
                  + ut.soul(bx + 40, by + 108, 3.2, 'class="beat"')
                  + ut.text("Save", bx + 80, by + 106, 3.2) + ut.text("Return", bx + 330, by + 106, 3.2))
    rows_yellow = (ut.text("WAEL", bx + 34, by + 26, 3.2, ut.YELLOW) + ut.text("LV 20", bx + bw / 2, by + 26, 3.2, ut.YELLOW, "middle")
                   + ut.text("20:26", bx + bw - 34, by + 26, 3.2, ut.YELLOW, "end")
                   + ut.text("Kaggle - Zindi - GitHub", bx + 34, by + 66, 3.2, ut.YELLOW)
                   + ut.text("File saved.", bx + 80, by + 106, 3.2, ut.YELLOW))
    vis_w = f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.62;.63;.99;1" dur="{D}s" repeatCount="indefinite"/>'
    vis_y = f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.62;.63;.99;1" dur="{D}s" repeatCount="indefinite"/>'
    star = f'<g class="tw">{ut.sprite(STAR, 62, 234, 4.4, {"#": ut.YELLOW})}</g>'
    body = (title + ut.soul(439, 135, 2.6, 'class="beat"')
            + tag + ut.box(bx, by, bw, bh) + f'<g>{vis_w}{rows_white}</g><g opacity="0">{vis_y}{rows_yellow}</g>' + star)
    style = ut.BEAT + (".tw { transform-box: fill-box; transform-origin: center; animation: tw 2.2s ease-in-out infinite; }"
                       "@keyframes tw { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: .55; transform: scale(.86); } }")
    return ut.svg(W, H, body, "WAEL - LV 20 - save file", style)


def technoblade() -> str:
    W, H, D = 900, 222, 9.0
    portrait = ut.sprite(CROWN, 58, 74, 8, {"#": "#ffd700", "p": "#ff4fa3", "h": "#b8860b"})
    lines = [("* If you wish to defeat me,", 0.3), ("  train for another 100 years.", 1.9), ("* Technoblade never dies.", 3.8)]
    x0, y0, sc = 210, 52, 3.2
    typed = "".join(ut.typewriter(s, x0, y0 + 40 * i, sc, t, D, 0.05, cid=f"tb{i}") for i, (s, t) in enumerate(lines))
    body = (ut.box(30, 22, 840, 166) + portrait + typed
            + ut.text("In memory of Technoblade  1999 - 2022", W - 34, 200, 1.8, ut.GREY, "end"))
    return ut.svg(W, H, body, "Technoblade: If you wish to defeat me, train for another 100 years. Technoblade never dies.")


def footer() -> str:
    W, H = 900, 110
    body = (ut.soul(300, 44, 3.4, 'class="beat"') + ut.text("* Stay determined.", 345, 42, 3.4)
            + ut.text("Thanks for visiting", 450, 86, 1.8, ut.GREY, "middle"))
    return ut.svg(W, H, body, "Stay determined.", ut.BEAT)


HEADINGS = {"ut-h-whoami.svg": "* WHO AM I", "ut-h-leaderboard.svg": "* LEADERBOARD LOG", "ut-h-artofwar.svg": "* THE ART OF WAR",
            "ut-h-technoblade.svg": "* TECHNOBLADE NEVER DIES", "ut-h-determination.svg": "* DETERMINATION",
            "ut-h-projects.svg": "* PROJECTS", "ut-h-stack.svg": "* STACK", "ut-h-stat.svg": "* STAT", "ut-h-encounter.svg": "* ENCOUNTER", "ut-h-recent.svg": "* RECENT ACTIVITY", "ut-h-activity.svg": "* LAST 31 DAYS"}


def heading(label: str) -> str:
    W, H = 900, 52
    body = ut.soul(6, 18, 3, 'class="beat"') + ut.text(label, 42, 14, 3.4) + '<rect x="0" y="48" width="900" height="3" fill="#ffffff" opacity=".18"/>'
    return ut.svg(W, H, body, label.replace("* ", ""), ut.BEAT)


# ───────────────────────── encounter buttons (each is a link in the README) ─────────────────────────
ICONS = {
    "FIGHT": ["......##", ".....###", "....###.", "#..###..", ".####...", "..##....", ".####...", "##..#..."],
    "ACT": [".#######.", "#.......#", "#.#.#.#.#", "#.......#", ".###.###.", "...##....", "..##.....", ".##......"],
    "ITEM": ["...###...", "..#...#..", "...###...", ".#######.", "#.......#", "#.#####.#", "#.......#", ".#######."],
    "MERCY": ["##.....##", ".##...##.", "..##.##..", "...###...", "..##.##..", ".##...##.", "##.....##", "........."],
}


def button(label: str) -> str:
    W, H = 220, 70
    body = (f'<rect x="3" y="3" width="{W - 6}" height="{H - 6}" fill="#000" stroke="{ut.ORANGE}" stroke-width="5"/>'
            + ut.sprite(ICONS[label], 22, 23, 3, {"#": ut.ORANGE})
            + ut.text(label, 132, 25, 3.2, ut.ORANGE, "middle"))
    return ut.svg(W, H, body, label)


# ───────────────────────── leaderboard log and the Art of War as pixel dialog boxes ─────────────────────────
LOG = [
    ("* 2026 - Kaggle - IEEE Big Data Cup", "TrafficFlowBench: reconstruct, forecast & explain", "10 freeway corridors. Strictly causal, post-T verified."),
    ("* 2026 - Zindi - Bias Bounty", "Mapping Equity: found 2.88M residents behind a", "single road link. Best Bias Discovery & Documentation entry."),
    ("* 2026 - NeurIPS - Virtual Embryo Challenge", "Leaderboard insights: which metric to improve next,", "and what it is worth in rank."),
]
WAR = [
    ("If you know the enemy and know yourself, you need not fear the result of a hundred battles.",
     "Know the metric, know your validation set."),
    ("All warfare is based on deception.", "A leaderboard can lie. Trust the validation you built honestly."),
    ("Let your plans be dark and impenetrable as night, and when you move, fall like a thunderbolt.",
     "Ship quietly, strike once."),
    ("The victorious strategist only seeks battle after the victory has been won.", "Win on validation first. Submit second."),
    ("He will win who knows when to fight and when not to fight.", "Some metrics are identities. Know which levers not to pull."),
]


def wrap(s: str, n: int) -> list[str]:
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + (1 if cur else 0) > n:
            out.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    return out + [cur]


def leaderboard() -> str:
    W, lines, y = 940, [], 30
    for head, a, b in LOG:
        lines.append(ut.text(head, 34, y, 2.6, ut.YELLOW)); y += 30
        lines.append(ut.text("  " + a, 34, y, 2.2, raw=False)); y += 24
        lines.append(ut.text("  " + b, 34, y, 2.2)); y += 40
    H = y - 6
    return ut.svg(W, H, ut.box(0, 0, W, H) + "".join(lines), "Leaderboard log")


def artofwar() -> str:
    W, lines, y = 940, [], 30
    lines.append(ut.text("Sun Tzu - The Art of War (tr. Lionel Giles, 1910)", 34, y, 2.0, ut.GREY)); y += 40
    for quote, note in WAR:
        for i, part in enumerate(wrap(quote, 58)):
            lines.append(ut.text(("* " if i == 0 else "  ") + part, 34, y, 2.3)); y += 26
        lines.append(ut.text("  > " + note, 34, y, 2.0, ut.YELLOW)); y += 40
    H = y - 6
    return ut.svg(W, H, ut.box(0, 0, W, H) + "".join(lines), "The Art of War, leaderboard edition")


if __name__ == "__main__":
    for name, label in HEADINGS.items():
        (OUT / name).parent.mkdir(exist_ok=True)
        (OUT / name).write_text(heading(label), encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    for lab in ICONS:
        (OUT / f"btn-{lab.lower()}.svg").write_text(button(lab), encoding="utf-8")
    for name, fn in (("ut-save.svg", header), ("ut-technoblade.svg", technoblade), ("ut-footer.svg", footer),
                     ("ut-leaderboard.svg", leaderboard), ("ut-artofwar.svg", artofwar)):
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", OUT / name)
