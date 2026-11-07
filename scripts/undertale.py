"""assets/undertale.svg: an animated Undertale-style battle (pure SVG + SMIL, loops every DUR seconds).

Timeline: Chara's line types out; bones sweep the bullet box along the floor, then the ceiling, while the red SOUL
slips through the gap; friendliness pellets rain down and the SOUL zig-zags between them; a knife slash crosses the
box and the damage number pops. The SOUL never gets hit.

  python scripts/undertale.py
"""
from pathlib import Path

W, H, DUR = 900, 400, 7.0
FONT = "'Determination Mono','Courier New',Consolas,monospace"
AX, AY, AW, AH = 300, 112, 300, 156          # bullet box (outer)
IX0, IY0, IX1, IY1 = AX + 4, AY + 4, AX + AW - 4, AY + AH - 4
HEART = "M0,-6 C-3,-12 -14,-10 -14,-1 C-14,6 -5,11 0,16 C5,11 14,6 14,-1 C14,-10 3,-12 0,-6 Z"


def kt(*secs):
    return ";".join(f"{s / DUR:.4f}" for s in secs)


def moving(pairs, inner):
    """Group translated along pairs, with its first keyframe as the static transform."""
    _, x0, y0 = pairs[0]
    return f'<g transform="translate({x0},{y0})">{anim_translate(pairs)}{inner}</g>'


def anim_translate(pairs):
    """pairs: [(second, x, y), ...] covering 0..DUR -> SMIL translate animation."""
    return (f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" repeatCount="indefinite" '
            f'values="{";".join(f"{x},{y}" for _, x, y in pairs)}" keyTimes="{kt(*[s for s, _, _ in pairs])}" calcMode="linear"/>')


def bone(x, y0, y1):
    """Vertical bone from y0 to y1 at x (local coordinates)."""
    return (f'<rect x="{x - 4}" y="{y0}" width="8" height="{y1 - y0}" fill="#fff"/>'
            f'<circle cx="{x - 4}" cy="{y0}" r="5" fill="#fff"/><circle cx="{x + 4}" cy="{y0}" r="5" fill="#fff"/>'
            f'<circle cx="{x - 4}" cy="{y1}" r="5" fill="#fff"/><circle cx="{x + 4}" cy="{y1}" r="5" fill="#fff"/>')


def typewriter(line, x, y, start, per=0.055, cw=15.6):
    n = len(line); full = n * cw
    ts, vs = [0.0], ["0"]
    for k in range(1, n + 1):
        ts.append(start + k * per); vs.append(f"{k * cw:.1f}")
    ts.append(DUR); vs.append(f"{full:.1f}")
    return (f'<clipPath id="tw"><rect x="{x}" y="{y - 30}" width="{full:.1f}" height="40">'
            f'<animate attributeName="width" values="{";".join(vs)}" keyTimes="{kt(*ts)}" dur="{DUR}s" calcMode="discrete" repeatCount="indefinite"/>'
            f'</rect></clipPath><text x="{x}" y="{y}" clip-path="url(#tw)" class="d">{line}</text>')


# ── attacks (groups are translated in x / y and clipped to the box) ──
bones_floor = "".join(bone(x, IY1 - 70, IY1 + 6) for x in (0, 70, 140))                 # three floor bones
bones_ceil = "".join(bone(x, IY0 - 6, IY0 + 66) for x in (0, 70, 140))                   # three ceiling bones
floor_group = moving([(0, IX0 - 200, 0), (0.6, IX0 - 200, 0), (2.4, IX1 + 30, 0), (DUR, IX1 + 30, 0)], bones_floor)
ceil_group = moving([(0, IX1 + 30, 0), (2.6, IX1 + 30, 0), (4.3, IX0 - 200, 0), (DUR, IX0 - 200, 0)], bones_ceil)
pellets = ""
for px, t0 in ((450, 4.35), (380, 4.75), (525, 5.1), (415, 5.35)):
    pellets += moving([(0, px, IY0 - 20), (t0, px, IY0 - 20), (t0 + 0.75, px, IY1 + 20), (DUR, px, IY1 + 20)],
                      '<circle r="6" fill="#fff"/><circle r="2.2" fill="#000"/>')

# ── the SOUL's dodge path: above the floor bones, below the ceiling bones, then between the pellets ──
soul_path = [(0, 450, 190), (0.5, 450, 190), (0.75, 450, 150), (2.45, 450, 150), (2.7, 450, 232), (4.3, 450, 232),
             (4.45, 385, 205), (4.9, 385, 205), (5.02, 520, 205), (5.3, 520, 205), (5.42, 455, 205), (5.9, 455, 205),
             (6.05, 450, 190), (DUR, 450, 190)]
soul = moving(soul_path, f'<g class="soul"><path d="{HEART}" fill="#ff0000"/></g>')

# ── knife slash + damage ──
slash = (f'<path d="M{AX + 40},{AY + AH - 20} Q{AX + AW / 2},{AY - 30} {AX + AW - 30},{AY + 30}" fill="none" stroke="#ff0000" '
         f'stroke-width="9" stroke-linecap="round" stroke-dasharray="420" stroke-dashoffset="420" opacity="0">'
         f'<animate attributeName="stroke-dashoffset" values="420;420;0;0" keyTimes="{kt(0, 6.0, 6.25, DUR)}" dur="{DUR}s" repeatCount="indefinite"/>'
         f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, 6.0, 6.02, 6.45, 6.7, DUR)}" dur="{DUR}s" repeatCount="indefinite"/></path>')
damage = (f'<text x="{AX + AW / 2}" y="{AY - 8}" text-anchor="middle" class="dmg" opacity="0">9999'
          f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt(0, 6.2, 6.25, 6.85, DUR)}" dur="{DUR}s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0,0;0,0;0,-14;0,-10;0,-10" '
          f'keyTimes="{kt(0, 6.2, 6.4, 6.55, DUR)}" dur="{DUR}s" repeatCount="indefinite"/></text>')

btn = []
for j, (label, x) in enumerate([("FIGHT", 40), ("ACT", 255), ("ITEM", 470), ("MERCY", 685)]):
    col = "#ffff00" if j == 0 else "#ff9900"
    icon = (f'<g transform="translate({x + 32} 366) scale(.85)"><path d="{HEART}" fill="#ff0000"/></g>' if j == 0
            else f'<rect x="{x + 22}" y="354" width="22" height="22" fill="none" stroke="{col}" stroke-width="3"/>')
    btn.append(f'<rect x="{x}" y="342" width="175" height="48" fill="#000" stroke="{col}" stroke-width="4"/>{icon}'
               f'<text x="{x + 60}" y="376" class="b" style="fill:{col}">{label}</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Undertale battle: Chara's SOUL dodges bones and pellets">
<style>
  text {{ font-family: {FONT}; font-weight: 700; }}
  .d {{ fill: #fff; font-size: 26px; }}
  .b {{ font-size: 26px; letter-spacing: 1px; }}
  .s {{ fill: #fff; font-size: 18px; }}
  .dmg {{ fill: #ff0000; font-size: 34px; }}
  .soul {{ animation: beat 1.1s ease-in-out infinite; }}
  @keyframes beat {{ 0%,100% {{ transform: scale(.9); }} 15% {{ transform: scale(1.12); }} 30% {{ transform: scale(.95); }} }}
</style>
<rect width="{W}" height="{H}" fill="#000"/>
<rect x="40" y="16" width="{W - 80}" height="72" fill="#000" stroke="#fff" stroke-width="5"/>
{typewriter("* Greetings. I am Chara.", 64, 62, 0.2)}
<clipPath id="arena"><rect x="{IX0}" y="{IY0}" width="{IX1 - IX0}" height="{IY1 - IY0}"/></clipPath>
<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" fill="#000" stroke="#fff" stroke-width="5"/>
<g clip-path="url(#arena)">{floor_group}{ceil_group}{pellets}</g>
{soul}
{slash}
{damage}
<text x="40" y="320" class="s">CHARA</text><text x="150" y="320" class="s">LV 20</text>
<text x="270" y="320" class="s" style="font-size:14px">HP</text>
<rect x="302" y="304" width="110" height="20" fill="#c00"/><rect x="302" y="304" width="110" height="20" fill="#ffff00"/>
<text x="430" y="320" class="s">99 / 99</text>
{''.join(btn)}
</svg>"""
Path("assets").mkdir(exist_ok=True)
Path("assets/undertale.svg").write_text(svg, encoding="utf-8")
print("wrote assets/undertale.svg", len(svg), "bytes")
