"""Build light/dark SVG profile banners with text outlined to paths (OFL fonts)."""
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = sys.argv[1]
SANS = "C:/Windows/Fonts/NotoSansSC-VF.ttf"
MONO = os.environ["LOCALAPPDATA"] + "/Microsoft/Windows/Fonts/JetBrainsMonoNLNerdFont-Medium.ttf"

sans = TTFont(SANS)
mono = TTFont(MONO)


def make_writer(font, location=None):
    gs = font.getGlyphSet(location=location) if location else font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm

    def write(text, x, y, size, tracking=0.0, anchor="start"):
        s = size / upm
        names = [cmap.get(ord(c), ".notdef") for c in text]
        width = sum(gs[n].width * s + tracking for n in names) - tracking
        if anchor == "end":
            x -= width
        elif anchor == "middle":
            x -= width / 2
        pen = SVGPathPen(gs)
        cx = x
        for n in names:
            gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += gs[n].width * s + tracking
        return pen.getCommands(), width

    return write


bold = make_writer(sans, {"wght": 700})
regular = make_writer(sans, {"wght": 400})
mono_w = make_writer(mono)

W, H = 1200, 320
THEMES = {
    "light": dict(bg="#fbfaf6", ink="#24527a", text="#1b1f24", muted="#5c6670", accent="#d9480f"),
    "dark": dict(bg="#0f141a", ink="#8fb4d9", text="#e6edf3", muted="#8b949e", accent="#ff8a4c"),
}


def build(t):
    texts = []

    def txt(d, fill, cls=""):
        texts.append(f'<path class="{cls}" fill="{fill}" d="{d}"/>')

    # left: identity
    d, _ = mono_w("SHEET 00 — PROFILE", 72, 92, 13, tracking=1.2)
    txt(d, t["muted"])
    d, w1 = bold("阿哲", 70, 178, 80)
    txt(d, t["text"])
    d, _ = bold("Phil", 70 + w1 + 22, 178, 80)
    txt(d, t["text"])
    d, w2 = regular("不想画图的建筑师", 72, 228, 26)
    txt(d, t["text"])
    d, w3 = regular("→", 72 + w2 + 10, 228, 26)
    txt(d, t["accent"])
    d, _ = regular("AIGC 设计师 & 架构师", 72 + w2 + w3 + 20, 228, 26)
    txt(d, t["text"])
    d, _ = mono_w("AI CONTENT · AGENT SKILLS · BRAND GROWTH", 72, 266, 13, tracking=1.2)
    txt(d, t["muted"])

    # right: title block cells (x from 700 to 1168, y 252..288)
    cells = [("DRAWN BY", "AGENT"), ("CHECKED BY", "PHIL"), ("SCALE", "1:1"), ("DATE", "2026")]
    cw = (1168 - 700) / len(cells)
    for i, (k, v) in enumerate(cells):
        x = 700 + i * cw + 12
        d, _ = mono_w(k, x, 266, 9, tracking=1)
        txt(d, t["muted"])
        d, _ = mono_w(v, x, 283, 13, tracking=0.8)
        txt(d, t["accent"] if v == "AGENT" else t["text"])

    # dimension labels
    d, _ = mono_w("27 000", 955, 46, 11, anchor="middle")
    txt(d, t["ink"], "lbl")
    d, _ = mono_w("±0.000", 704, 214, 10)
    txt(d, t["ink"], "lbl")

    ink = t["ink"]
    # elevation drawing, each stroke draws itself in order
    strokes = [
        # (path, stroke width, delay seconds)
        ("M700 222 H1168", 2.2, 0.0),                       # ground line
        ("M770 222 V132 H960 V222", 1.6, 0.3),              # lower volume
        ("M820 132 V72 H1092 V132 H820", 1.6, 0.7),         # cantilevered upper volume
        ("M1062 132 V222", 1.2, 1.1),                       # column
        ("M850 72 V132 M880 72 V132 M910 72 V132 M940 72 V132 M970 72 V132 "
         "M1000 72 V132 M1030 72 V132 M1060 72 V132", 0.8, 1.3),  # mullions
        ("M800 160 H900 V222 M800 160 V222 M920 182 H945 V222 M920 182 V222", 0.9, 1.6),  # glazing + door
        ("M820 56 H1092 M820 51 V61 M1092 51 V61 M816 60 L824 52 M1088 60 L1096 52", 0.7, 1.9),  # top dim
        ("M1124 72 V222 M1119 72 H1129 M1119 222 H1129 M1120 76 L1128 68 M1120 226 L1128 218", 0.7, 2.1),  # side dim
    ]
    guides = "M700 72 H1150 M700 132 H1150 M820 30 V240 M1092 30 V240"
    paths = []
    for i, (p, sw, delay) in enumerate(strokes):
        paths.append(
            f'<path class="draw" style="animation-delay:{delay}s" pathLength="1" d="{p}" '
            f'stroke="{ink}" stroke-width="{sw}" fill="none" stroke-linecap="butt"/>'
        )

    # vertical dim label rotated: draw upright text then rotate group
    d, _ = mono_w("15 000", 0, 0, 11, anchor="middle")
    vlabel = f'<g class="lbl" transform="translate(1142 147) rotate(-90)"><path fill="{ink}" d="{d}"/></g>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="阿哲 Phil — 不想画图的建筑师 → AIGC 设计师 &amp; 架构师">
<title>阿哲 Phil — 不想画图的建筑师 → AIGC 设计师 &amp; 架构师</title>
<defs>
<pattern id="minor" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="{ink}" stroke-width="0.5" opacity="0.10"/></pattern>
<pattern id="major" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="{ink}" stroke-width="0.8" opacity="0.16"/></pattern>
<clipPath id="sheet"><rect x="16" y="16" width="{W-32}" height="{H-32}"/></clipPath>
</defs>
<style>
.draw{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.1s cubic-bezier(.6,0,.2,1) forwards}}
.lbl{{opacity:0;animation:fade .6s ease 2.6s forwards}}
.cursor{{opacity:0;animation:fade .3s ease 2.4s forwards,blink 1.2s steps(1) 3s infinite}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.draw{{animation:none;stroke-dashoffset:0}}.lbl,.cursor{{animation:none;opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>
<g clip-path="url(#sheet)"><rect width="{W}" height="{H}" fill="url(#minor)"/><rect width="{W}" height="{H}" fill="url(#major)"/></g>
<rect x="16" y="16" width="{W-32}" height="{H-32}" fill="none" stroke="{ink}" stroke-width="1" opacity="0.55"/>
<rect x="24" y="24" width="{W-48}" height="{H-48}" fill="none" stroke="{ink}" stroke-width="0.6" opacity="0.35"/>
<g stroke="{ink}" stroke-width="0.6" fill="none" opacity="0.5">
<path d="M700 244 H1168 V288 H700 Z"/>
<path d="M{700+cw:.1f} 244 V288 M{700+2*cw:.1f} 244 V288 M{700+3*cw:.1f} 244 V288"/>
</g>
<path d="{guides}" stroke="{ink}" stroke-width="0.5" stroke-dasharray="3 5" opacity="0.28" fill="none"/>
{chr(10).join(paths)}
<g class="cursor" stroke="{t["accent"]}" stroke-width="1.2" fill="none"><path d="M1092 60 V84 M1080 72 H1104"/><circle cx="1092" cy="72" r="5"/></g>
{vlabel}
{chr(10).join(texts)}
</svg>
'''


os.makedirs(OUT, exist_ok=True)
for name, theme in THEMES.items():
    svg = build(theme)
    with open(os.path.join(OUT, f"banner-{name}.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print(name, len(svg.encode()) // 1024, "KB")
