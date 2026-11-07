"""assets/technoblade-crown.svg: animated tribute banner with a vector crown (no emoji).

  python scripts/technoblade.py
"""
from pathlib import Path

W, H = 900, 300
OUT = Path("assets/technoblade-crown.svg")

# crown geometry (centred on x = 450)
PEAKS = [(362, 100), (406, 80), (450, 56), (494, 80), (538, 100)]
VALLEYS = [(384, 128), (428, 114), (472, 114), (516, 128)]
outline = [(374, 154)]
for i, p in enumerate(PEAKS):
    outline.append(p)
    if i < len(VALLEYS):
        outline.append(VALLEYS[i])
outline.append((526, 154))
crown_d = "M" + " L".join(f"{x},{y}" for x, y in outline) + " Z"


def star(cx, cy, r, delay, dur=2.4):
    d = f"M{cx},{cy - r} Q{cx},{cy} {cx + r},{cy} Q{cx},{cy} {cx},{cy + r} Q{cx},{cy} {cx - r},{cy} Q{cx},{cy} {cx},{cy - r} Z"
    return f'<path d="{d}" fill="#fff6d5" class="tw" style="animation-delay:{delay}s;animation-duration:{dur}s"/>'


sparkles = "".join(star(*s) for s in [(318, 86, 9, 0.0), (586, 70, 11, 0.7), (346, 160, 6, 1.3), (566, 150, 7, 0.4),
                                      (300, 126, 5, 1.8), (612, 118, 6, 1.1), (450, 30, 7, 0.9)])
orbs = "".join(f'<circle cx="{x}" cy="{y - 7}" r="7.5" fill="url(#gold)" stroke="#7a4a00" stroke-width="2"/>'
               f'<circle cx="{x - 2.5}" cy="{y - 9.5}" r="2.4" fill="#fffbe6" opacity=".9"/>' for x, y in PEAKS)
gems = (f'<ellipse cx="450" cy="166" rx="13" ry="9" fill="url(#gem)" stroke="#7a1043" stroke-width="2"/>'
        f'<ellipse cx="446" cy="163" rx="4" ry="2.5" fill="#ffd6ea" opacity=".9"/>'
        + "".join(f'<rect x="{x - 6}" y="160" width="12" height="12" rx="2" transform="rotate(45 {x} 166)" fill="url(#gem)" stroke="#7a1043" stroke-width="1.6"/>'
                  for x in (398, 502))
        + "".join(f'<circle cx="{x}" cy="166" r="3.2" fill="#fff3b0" stroke="#7a4a00" stroke-width="1"/>' for x in (378, 422, 478, 522)))

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Technoblade never dies">
<defs>
  <radialGradient id="bg" cx="50%" cy="38%" r="70%"><stop offset="0" stop-color="#2a0f22"/><stop offset=".55" stop-color="#140912"/><stop offset="1" stop-color="#0d1117"/></radialGradient>
  <radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff4fa3" stop-opacity=".45"/><stop offset="1" stop-color="#ff4fa3" stop-opacity="0"/></radialGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0"/><stop offset=".35" stop-color="#ffd166"/><stop offset=".75" stop-color="#e09f00"/><stop offset="1" stop-color="#a86b00"/></linearGradient>
  <linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe08a"/><stop offset=".5" stop-color="#d99400"/><stop offset="1" stop-color="#8f5800"/></linearGradient>
  <radialGradient id="gem" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#ffd6ea"/><stop offset=".4" stop-color="#ff4fa3"/><stop offset="1" stop-color="#b0145e"/></radialGradient>
  <linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff4fa3"/><stop offset=".5" stop-color="#ff9ecf"/><stop offset="1" stop-color="#ffd166"/></linearGradient>
  <linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="300" y1="0" x2="420" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-160 0;360 0;360 0" keyTimes="0;.45;1" dur="3.6s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="crownclip"><path d="{crown_d}"/><rect x="368" y="150" width="164" height="32" rx="5"/></clipPath>
  <filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000" flood-opacity=".6"/></filter>
</defs>
<style>
  .float {{ animation: float 3.2s ease-in-out infinite; }}
  @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
  .tw {{ transform-box: fill-box; transform-origin: center; animation: tw 2.4s ease-in-out infinite; }}
  @keyframes tw {{ 0%,100% {{ opacity: .15; transform: scale(.4) rotate(0deg); }} 50% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}
  .pulse {{ animation: pulse 3.2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .7; }} 50% {{ opacity: 1; }} }}
  text {{ font-family: 'Segoe UI Black','Arial Black','Segoe UI',Impact,sans-serif; font-weight: 900; }}
</style>
<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="15" fill="none" stroke="url(#title)" stroke-opacity=".55" stroke-width="2"/>
<ellipse cx="450" cy="118" rx="210" ry="96" fill="url(#halo)" class="pulse"/>
{sparkles}
<g class="float" filter="url(#soft)">
  <path d="{crown_d}" fill="url(#gold)" stroke="#7a4a00" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M392,146 L406,96 L420,142 Z M436,142 L450,80 L464,142 Z M480,142 L494,96 L508,146 Z" fill="#fff8d6" opacity=".22"/>
  <rect x="368" y="150" width="164" height="32" rx="5" fill="url(#band)" stroke="#7a4a00" stroke-width="2.5"/>
  <rect x="372" y="153" width="156" height="5" rx="2" fill="#fff3b0" opacity=".55"/>
  {orbs}
  {gems}
  <rect x="300" y="40" width="300" height="150" fill="url(#sheen)" clip-path="url(#crownclip)" style="mix-blend-mode:screen"/>
</g>
<text x="450" y="242" text-anchor="middle" font-size="46" letter-spacing="3" fill="url(#title)" filter="url(#glow)">TECHNOBLADE NEVER DIES</text>
<text x="450" y="276" text-anchor="middle" font-size="13" letter-spacing="7" fill="#ffd166" opacity=".75" style="font-family:'Segoe UI',Arial,sans-serif;font-weight:700">BLOOD FOR THE BLOOD GOD</text>
</svg>"""
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print("wrote", OUT, len(svg), "bytes")
