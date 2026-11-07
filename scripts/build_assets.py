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
            "ut-h-projects.svg": "* PROJECTS", "ut-h-stack.svg": "* STACK", "ut-h-stat.svg": "* STAT", "ut-h-activity.svg": "* LAST 31 DAYS"}


def heading(label: str) -> str:
    W, H = 900, 52
    body = ut.soul(6, 18, 3, 'class="beat"') + ut.text(label, 42, 14, 3.4) + '<rect x="0" y="48" width="900" height="3" fill="#ffffff" opacity=".18"/>'
    return ut.svg(W, H, body, label.replace("* ", ""), ut.BEAT)


if __name__ == "__main__":
    for name, label in HEADINGS.items():
        (OUT / name).parent.mkdir(exist_ok=True)
        (OUT / name).write_text(heading(label), encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    for name, fn in (("ut-save.svg", header), ("ut-technoblade.svg", technoblade), ("ut-footer.svg", footer)):
        (OUT / name).write_text(fn(), encoding="utf-8")
        print("wrote", OUT / name)
