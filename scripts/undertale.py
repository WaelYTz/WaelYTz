"""assets/undertale.svg: an animated Undertale-style battle box (typewriter dialog, pulsing SOUL, HP bar, menu)."""
from pathlib import Path

W, H = 900, 300
FONT = "'Determination Mono','Courier New',Consolas,monospace"
LINES = ["* Greetings. I am Chara.", "* You're filled with DETERMINATION."]
CW = 15.6                                   # px per character at 26px monospace
T0, CHAR, GAP, DUR = 0.4, 0.06, 0.7, 10.0   # start, seconds per char, pause between lines, loop length


def typewriter(i: int, line: str, start: float) -> str:
    n = len(line); full = n * CW
    ts, vs = [0.0], ["0"]
    for k in range(1, n + 1):
        ts.append((start + k * CHAR) / DUR); vs.append(f"{k * CW:.1f}")
    ts.append(1.0); vs.append(f"{full:.1f}")
    kt = ";".join(f"{t:.4f}" for t in ts)
    return (f'<clipPath id="c{i}"><rect x="60" y="{58 + 46 * i}" width="{full:.1f}" height="40">'
            f'<animate attributeName="width" values="{";".join(vs)}" keyTimes="{kt}" dur="{DUR}s" calcMode="discrete" repeatCount="indefinite"/>'
            f'</rect></clipPath><text x="60" y="{88 + 46 * i}" clip-path="url(#c{i})" class="d">{line.replace("&", "&amp;").replace("<", "&lt;")}</text>')


heart = "M0,-6 C-3,-12 -14,-10 -14,-1 C-14,6 -5,11 0,16 C5,11 14,6 14,-1 C14,-10 3,-12 0,-6 Z"
start2 = T0 + len(LINES[0]) * CHAR + GAP
btn = []
for j, (label, x) in enumerate([("FIGHT", 40), ("ACT", 255), ("ITEM", 470), ("MERCY", 685)]):
    col = "#ffff00" if j == 0 else "#ff9900"
    icon = (f'<path d="{heart}" transform="translate({x + 32} 262) scale(.9)" fill="#ff0000" class="soul"/>' if j == 0
            else f'<rect x="{x + 22}" y="250" width="22" height="22" fill="none" stroke="{col}" stroke-width="3"/>')
    btn.append(f'<rect x="{x}" y="238" width="175" height="48" fill="#000" stroke="{col}" stroke-width="4"/>{icon}'
               f'<text x="{x + 60}" y="272" class="b" style="fill:{col}">{label}</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Undertale battle box: Greetings. I am Chara.">
<style>
  text {{ font-family: {FONT}; font-weight: 700; }}
  .d {{ fill: #fff; font-size: 26px; }}
  .b {{ font-size: 26px; letter-spacing: 1px; }}
  .s {{ fill: #fff; font-size: 18px; }}
  .soul {{ transform-box: fill-box; transform-origin: center; animation: beat 1.1s ease-in-out infinite; }}
  @keyframes beat {{ 0%,100% {{ transform: scale(.9); }} 15% {{ transform: scale(1.12); }} 30% {{ transform: scale(.95); }} }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<rect width="{W}" height="{H}" fill="#000"/>
<rect x="40" y="30" width="{W - 80}" height="150" fill="#000" stroke="#fff" stroke-width="5"/>
{typewriter(0, LINES[0], T0)}
{typewriter(1, LINES[1], start2)}
<text x="{W - 64}" y="166" class="s cursor">&#9660;</text>
<text x="40" y="218" class="s">WAEL</text><text x="140" y="218" class="s">LV 20</text>
<text x="260" y="218" class="s" style="font-size:14px">HP</text>
<rect x="292" y="202" width="110" height="20" fill="#c00"/><rect x="292" y="202" width="110" height="20" fill="#ffff00"/>
<text x="420" y="218" class="s">99 / 99</text>
{''.join(btn)}
</svg>"""
Path("assets").mkdir(exist_ok=True)
Path("assets/undertale.svg").write_text(svg, encoding="utf-8")
print("wrote assets/undertale.svg", len(svg), "bytes")
