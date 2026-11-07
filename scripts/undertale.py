"""assets/undertale-fight.svg: an animated Undertale-style bullet-box fight (pure SVG + SMIL, loops every DUR s).

Three attack patterns, each dodged by the red SOUL (with an afterimage trail):
  1. bone corridor  - floor/ceiling bone pairs march through with a moving gap; the SOUL weaves through every gap
  2. pellet ring    - friendliness pellets close in from all sides; the SOUL escapes through the single opening
  3. blaster beams  - a warning line flashes, then a beam fires on the SOUL's row or column; the SOUL slides out
The SOUL path is an eased (smootherstep) curve sampled at 30 fps. A collision check runs on every build and refuses
to write the file if anything would touch the SOUL. Button icons are drawn as pixel art.

  python scripts/undertale.py
"""
import math
from pathlib import Path

W, H, FPS = 900, 350, 30
T0, Y0 = 1.8, 0                                   # attacks start after the dialog; box moved down
DUR = 8.0 + T0 + 0.8
FONT = "'Courier New',Courier,monospace"
AX, AY, AW, AH = 270, 30 + Y0, 360, 200                    # bullet box (outer)
IX0, IY0, IX1, IY1 = AX + 5, AY + 5, AX + AW - 5, AY + AH - 5
HEART = "M0,-6 C-3,-12 -14,-10 -14,-1 C-14,6 -5,11 0,16 C5,11 14,6 14,-1 C14,-10 3,-12 0,-6 Z"
SOUL_BOX = (-13, -11, 13, 15)                          # hitbox around the SOUL's origin (l, t, r, b)
OUT = Path("assets/undertale-fight.svg")
ORANGE, YELLOW = "#ff8c1a", "#ffff00"


def smoother(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)


def path_at(way, t):
    """Eased interpolation through waypoints [(t, x, y), ...]."""
    for (t0, x0, y0), (t1, x1, y1) in zip(way, way[1:]):
        if t0 <= t <= t1:
            e = smoother((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    return way[-1][1], way[-1][2]


def lin_at(keys, t):
    for (t0, a0), (t1, a1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return a0 + (a1 - a0) * ((t - t0) / (t1 - t0) if t1 > t0 else 1.0)
    return keys[-1][1]


def smil_translate(samples, begin=0.0):
    vals = ";".join(f"{x:.1f},{y:.1f}" for x, y in samples)
    return (f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" begin="{begin}s" '
            f'repeatCount="indefinite" calcMode="linear" values="{vals}"/>')


def smil_keys(attr, keys):
    vals = ";".join(f"{v:g}" for _, v in keys)
    kt = ";".join(f"{t / DUR:.4f}" for t, _ in keys)
    return f'<animate attributeName="{attr}" dur="{DUR}s" repeatCount="indefinite" values="{vals}" keyTimes="{kt}"/>'


def smil_move(keys):
    vals = ";".join(f"{x:.1f},{y:.1f}" for _, x, y in keys)
    kt = ";".join(f"{t / DUR:.4f}" for t, _, _ in keys)
    return (f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" repeatCount="indefinite" '
            f'calcMode="linear" values="{vals}" keyTimes="{kt}"/>')


def pixels(rows, x, y, px, color):
    """Pixel-art icon from a list of strings ('#' = on), merged into horizontal runs."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == "#":
                s = c
                while c < len(row) and row[c] == "#":
                    c += 1
                out.append(f'<rect x="{x + s * px:.1f}" y="{y + r * px:.1f}" width="{(c - s) * px:.1f}" height="{px:.1f}" fill="{color}"/>')
            else:
                c += 1
    return "".join(out)


ICONS = {
    "ACT": [".#######.", "#.......#", "#.#.#.#.#", "#.......#", ".###.###.", "...##....", "..##.....", ".##......"],
    "ITEM": ["...###...", "..#...#..", "...###...", ".#######.", "#.......#", "#.#####.#", "#.......#", ".#######."],
    "MERCY": ["##.....##", ".##...##.", "..##.##..", "...###...", "..##.##..", ".##...##.", "##.....##", "........."],
}

# ───────────────────────── phase 1: bone corridor ─────────────────────────
GAPS = [136, 100, 150, 192, 165, 118]
GAPS = [g - 6 + Y0 for g in GAPS]                          # box sits 6 px higher than the original layout
GAP_HALF, PAIR_DX, SPEED, P1_T, P1_X = 36, 85, 260.0, 0.35 + T0, IX0 - 30
pass_t = [P1_T + (450 - P1_X + PAIR_DX * k) / SPEED for k in range(len(GAPS))]
p1_end_x = IX1 + 20 + PAIR_DX * (len(GAPS) - 1)
p1_end_t = P1_T + (p1_end_x - P1_X) / SPEED
bones_keys = [(0, P1_X, 0), (P1_T, P1_X, 0), (p1_end_t, p1_end_x, 0), (DUR, p1_end_x, 0)]


def bone_v(x, y0, y1):
    return (f'<rect x="{x - 4}" y="{y0}" width="8" height="{y1 - y0}" fill="#fff"/>'
            f'<circle cx="{x - 4}" cy="{y0}" r="4.5" fill="#fff"/><circle cx="{x + 4}" cy="{y0}" r="4.5" fill="#fff"/>'
            f'<circle cx="{x - 4}" cy="{y1}" r="4.5" fill="#fff"/><circle cx="{x + 4}" cy="{y1}" r="4.5" fill="#fff"/>')


bone_shapes = []                                      # (offset_x, y0, y1) for collision
for k, g in enumerate(GAPS):
    ox = -PAIR_DX * k
    bone_shapes += [(ox, IY0 - 8, g - GAP_HALF), (ox, g + GAP_HALF, IY1 + 8)]
bones_svg = (f'<g transform="translate({P1_X},0)">{smil_move(bones_keys)}'
             + "".join(bone_v(ox, y0, y1) for ox, y0, y1 in bone_shapes) + "</g>")

# ───────────────────────── phase 2: pellet ring ─────────────────────────
RC = (450, 130 + Y0); R0, R1 = 165, 0
RING_IN, RING_T0, RING_T1 = 3.75 + T0, 3.95 + T0, 5.05 + T0          # fade-in start, collapse start, collapse end
ANGLES = [k * 30 for k in range(1, 12)]               # 11 pellets, opening at angle 0 (to the right)


def ring_r(t):
    if t < RING_T0:
        return R0
    u = min(1.0, (t - RING_T0) / (RING_T1 - RING_T0))
    return R0 + (R1 - R0) * (u * u)                   # accelerating collapse


ring_samples = [i / FPS for i in range(int(DUR * FPS) + 1)]
pellets_svg = ""
for a in ANGLES:
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    pts = [(RC[0] + c * ring_r(t), RC[1] + s * ring_r(t)) for t in ring_samples]
    op = [(0, 0), (RING_IN, 0), (RING_T0, 1), (RING_T1 - 0.05, 1), (RING_T1 + 0.05, 0), (DUR, 0)]
    pellets_svg += (f'<g transform="translate({pts[0][0]:.1f},{pts[0][1]:.1f})" opacity="0">{smil_translate(pts)}'
                    f'{smil_keys("opacity", op)}<g class="spin"><rect x="-6" y="-2" width="12" height="4" fill="#fff"/>'
                    f'<rect x="-2" y="-6" width="4" height="12" fill="#fff"/><rect x="-4" y="-4" width="8" height="8" fill="#fff"/></g></g>')

# ───────────────────────── phase 3: blaster beams ─────────────────────────
BEAMS = [  # (kind, centre, warn_start, fire_start, fire_end)
    ("h", 130 + Y0, 5.30 + T0, 5.62 + T0, 5.95 + T0),
    ("v", 560, 5.95 + T0, 6.27 + T0, 6.60 + T0),
    ("h", 194 + Y0, 6.55 + T0, 6.87 + T0, 7.20 + T0),
]
BEAM_HALF = 22
beams_svg = ""
for kind, c, tw, tf, te in BEAMS:
    if kind == "h":
        warn = f'<rect x="{IX0}" y="{c - 1.5}" width="{IX1 - IX0}" height="3" fill="#fff"/>'
        beam = f'<rect x="{IX0}" y="{c - BEAM_HALF}" width="{IX1 - IX0}" height="{2 * BEAM_HALF}" fill="#fff" filter="url(#beam)"/>'
    else:
        warn = f'<rect x="{c - 1.5}" y="{IY0}" width="3" height="{IY1 - IY0}" fill="#fff"/>'
        beam = f'<rect x="{c - BEAM_HALF}" y="{IY0}" width="{2 * BEAM_HALF}" height="{IY1 - IY0}" fill="#fff" filter="url(#beam)"/>'
    blink = [(0, 0), (tw, 0), (tw + .08, .9), (tw + .16, .2), (tw + .24, .9), (tf, .5), (tf + .01, 0), (DUR, 0)]
    fire = [(0, 0), (tf, 0), (tf + .04, 1), (te - .08, 1), (te, 0), (DUR, 0)]
    beams_svg += f'<g opacity="0">{smil_keys("opacity", blink)}{warn}</g><g opacity="0">{smil_keys("opacity", fire)}{beam}</g>'

# ───────────────────────── the SOUL's path ─────────────────────────
HOLD = 0.09
way = [(0.0, 450, 130 + Y0), (pass_t[0] - HOLD - 0.2, 450, 130 + Y0)]
for t, g in zip(pass_t, GAPS):
    way += [(t - HOLD, 450, g), (t + HOLD, 450, g)]
way += [(pass_t[-1] + 0.45, 450, 130 + Y0),          # back to the ring centre
        (4.20 + T0, 450, 130 + Y0), (4.55 + T0, 590, 130 + Y0),     # escape through the ring's opening
        (5.32 + T0, 590, 130 + Y0), (5.55 + T0, 570, 194 + Y0),     # beam on the SOUL's row -> drop
        (5.97 + T0, 570, 194 + Y0), (6.22 + T0, 420, 194 + Y0),     # beam on the SOUL's column -> slide left
        (6.57 + T0, 420, 194 + Y0), (6.82 + T0, 450, 106 + Y0),     # beam on the new row -> rise
        (7.25 + T0, 450, 106 + Y0), (7.65 + T0, 450, 130 + Y0), (DUR, 450, 130 + Y0)]
samples = [path_at(way, i / FPS) for i in range(int(DUR * FPS) + 1)]


# ───────────────────────── collision check ─────────────────────────
def soul_rect(t):
    x, y = path_at(way, t)
    return x + SOUL_BOX[0], y + SOUL_BOX[1], x + SOUL_BOX[2], y + SOUL_BOX[3]


def overlap(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


hits = []
for i in range(int(DUR * 400)):
    t = i / 400
    sr = soul_rect(t)
    gx = lin_at([(k[0], k[1]) for k in bones_keys], t)
    for ox, y0, y1 in bone_shapes:
        bx = gx + ox
        if IX0 - 9 < bx < IX1 + 9 and overlap(sr, (bx - 9, y0 - 5, bx + 9, y1 + 5)):
            hits.append(("bone", round(t, 3)))
    if RING_IN <= t <= RING_T1:
        for a in ANGLES:
            px = RC[0] + math.cos(math.radians(a)) * ring_r(t); py = RC[1] + math.sin(math.radians(a)) * ring_r(t)
            if overlap(sr, (px - 7, py - 7, px + 7, py + 7)):
                hits.append(("pellet", round(t, 3)))
    for kind, c, tw, tf, te in BEAMS:
        if tf <= t <= te:
            box = (IX0, c - BEAM_HALF, IX1, c + BEAM_HALF) if kind == "h" else (c - BEAM_HALF, IY0, c + BEAM_HALF, IY1)
            if overlap(sr, box):
                hits.append(("beam", round(t, 3)))
    if T0 <= t <= DUR - 0.8 and not (IX0 <= sr[0] and sr[2] <= IX1 and IY0 <= sr[1] and sr[3] <= IY1):
        hits.append(("wall", round(t, 3)))
if hits:
    raise SystemExit(f"collision: {hits[:8]}")


# ───────────────────────── assemble ─────────────────────────
SOUL_ON = smil_keys("opacity", [(0, 0), (T0 - 0.12, 0), (T0, 1), (DUR - 0.85, 1), (DUR - 0.75, 0), (DUR, 0)])


def soul_copy(begin, opacity, cls):
    return (f'<g opacity="0">{SOUL_ON}<g transform="translate({samples[0][0]},{samples[0][1]})" opacity="{opacity}">'
            f'{smil_translate(samples, begin)}<g class="{cls}"><path d="{HEART}" fill="#ff0000"/></g></g></g>')


import ut
BUG = ["....#.....#....", ".....#...#.....", "....#######....", "...#########...", "#.##..###..##.#", ".#############.",
       "..###########..", "#.#####.#####.#", ".#############.", "..###########..", ".#..#######..#.", "#....#...#....#"]
K = 900 / 640
btn = []
for j, (label, x640) in enumerate([("FIGHT", 32), ("ACT", 185), ("ITEM", 345), ("MERCY", 500)]):
    x, bw, by, bh = x640 * K, 110 * K, 284, 42 * K
    col = YELLOW if j == 0 else ORANGE
    icon = (f'<g transform="translate({x + 24:.1f} {by + bh / 2:.1f}) scale(.8)"><path d="{HEART}" fill="#ff0000"/></g>' if j == 0
            else pixels(ICONS[label], x + 11, by + bh / 2 - 12, 2.7, col))
    btn.append(f'<rect x="{x + 2:.1f}" y="{by + 2}" width="{bw - 4:.1f}" height="{bh - 4:.1f}" fill="#000" stroke="{col}" stroke-width="4"/>'
               + icon + ut.text(label, x + bw / 2 + 14, by + bh / 2 - 10, 3.0, col, "middle"))


GRID = ""                                          # most fights are on plain black
BUG_SVG = ""                                       # no enemy sprite
WIDE, TALL = (40 + 2.5, AY + 2.5 + 25, 820 - 5, 150 - 5), (AX + 2.5, AY + 2.5, AW - 5, AH - 5)
_kt = f"0;{(T0 - 0.45) / DUR:.4f};{(T0 - 0.05) / DUR:.4f};{(DUR - 0.75) / DUR:.4f};{(DUR - 0.35) / DUR:.4f};1"
BOX_ANIM = "".join(f'<animate attributeName="{a}" values="{w};{w};{t};{t};{w};{w}" keyTimes="{_kt}" dur="{DUR}s" repeatCount="indefinite" calcMode="spline" '
                   f'keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/>'
                   for a, w, t in zip(("x", "y", "width", "height"), WIDE, TALL))
DIALOG = (f'<g>{smil_keys("opacity", [(0, 1), (T0 - 0.5, 1), (T0 - 0.45, 0), (DUR - 0.3, 0), (DUR - 0.25, 1), (DUR, 1)])}'
          + ut.typewriter("* You're filled with DETERMINATION.", 80, AY + 59, 3.2, 0.15, DUR, 0.04, cid="dlg") + "</g>")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Undertale-style battle: the SOUL dodges bones, a pellet ring and blaster beams" shape-rendering="crispEdges">
<defs>
  <clipPath id="arena"><rect x="{IX0}" y="{IY0}" width="{IX1 - IX0}" height="{IY1 - IY0}"/></clipPath>
  <filter id="beam" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  text {{ font-family: {FONT}; font-weight: 700; }}
  .b {{ font-size: 30px; letter-spacing: 2px; }}
  .s {{ fill: #fff; font-size: 20px; letter-spacing: 1px; }}
  .soul, .ghost {{ animation: beat 1.1s ease-in-out infinite; }}
  .soul path, .ghost path {{ shape-rendering: geometricPrecision; }}
  @keyframes beat {{ 0%,100% {{ transform: scale(.94); }} 15% {{ transform: scale(1.08); }} 30% {{ transform: scale(.97); }} }}
  .spin {{ animation: spin .6s linear infinite; }}
  .bob {{ animation: bob 1.6s ease-in-out infinite; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(5px); }} }}
  @keyframes spin {{ to {{ transform: rotate(90deg); }} }}
</style>
<rect width="{W}" height="{H}" fill="#000"/>
{GRID}{BUG_SVG}<rect x="{AX + 2.5}" y="{AY + 2.5}" width="{AW - 5}" height="{AH - 5}" fill="#000" stroke="#fff" stroke-width="5">{BOX_ANIM}</rect>{DIALOG}
<g clip-path="url(#arena)">{bones_svg}{pellets_svg}{beams_svg}</g>
{soul_copy(0.10, 0.18, "ghost")}
{soul_copy(0.05, 0.38, "ghost")}
{soul_copy(0.0, 1, "soul")}
{ut.text("WAEL", 44, 248, 2.6)}{ut.text("LV 20", 190, 248, 2.6)}{ut.text("HP", 330, 251, 1.6)}<rect x="356" y="246" width="119" height="22" fill="#ff0000"/><rect x="356" y="246" width="119" height="22" fill="{YELLOW}"/>{ut.text("99 / 99", 490, 248, 2.6)}
{''.join(btn)}
</svg>"""
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"wrote {OUT} ({len(svg):,} bytes); collision check passed; bone passes at {[round(t, 2) for t in pass_t]}")
