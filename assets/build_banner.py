"""Artistic profile banners: flow / ink / aurora, light + dark. Text outlined from OFL fonts."""
import math
import os
import random
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = sys.argv[1]
LF = os.environ["LOCALAPPDATA"] + "/Microsoft/Windows/Fonts/"
SERIF = TTFont("C:/Windows/Fonts/NotoSerifSC-VF.ttf")
SANS = TTFont("C:/Windows/Fonts/NotoSansSC-VF.ttf")
W, H = 1200, 320


def writer(font, location=None):
    gs = font.getGlyphSet(location=location) if location else font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm

    def write(text, x, y, size, tracking=0.0):
        s = size / upm
        pen = SVGPathPen(gs)
        cx = x
        for c in text:
            n = cmap.get(ord(c), ".notdef")
            gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += gs[n].width * s + tracking
        return pen.getCommands(), cx - tracking - x

    return write


serif_black = writer(SERIF, {"wght": 900})
serif_light = writer(SERIF, {"wght": 300})
sans_light = writer(SANS, {"wght": 300})
sans_reg = writer(SANS, {"wght": 400})


# ---------- Perlin noise ----------
def make_noise(seed):
    rnd = random.Random(seed)
    p = list(range(256))
    rnd.shuffle(p)
    p += p

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def grad(h, x, y):
        h &= 7
        u, v = (x, y) if h < 4 else (y, x)
        return (-u if h & 1 else u) + (-2 * v if h & 2 else 2 * v)

    def noise(x, y):
        xi, yi = int(math.floor(x)) & 255, int(math.floor(y)) & 255
        xf, yf = x - math.floor(x), y - math.floor(y)
        u, v = fade(xf), fade(yf)
        aa, ab = p[p[xi] + yi], p[p[xi] + yi + 1]
        ba, bb = p[p[xi + 1] + yi], p[p[xi + 1] + yi + 1]
        x1 = grad(aa, xf, yf) + u * (grad(ba, xf - 1, yf) - grad(aa, xf, yf))
        x2 = grad(ab, xf, yf - 1) + u * (grad(bb, xf - 1, yf - 1) - grad(ab, xf, yf - 1))
        return (x1 + v * (x2 - x1)) / 2.2

    def fbm(x, y, octaves=4):
        a, f, s = 1.0, 1.0, 0.0
        for _ in range(octaves):
            s += a * noise(x * f, y * f)
            a *= 0.5
            f *= 2.0
        return s

    return noise, fbm


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def text_block(t, title_fill, sub_fill, accent, y0=150):
    out = []
    d, w = serif_black("阿哲", 72, y0, 92)
    out.append(f'<path fill="{title_fill}" d="{d}"/>')
    d, _ = serif_light("Phil", 72 + w + 20, y0, 92)
    out.append(f'<path fill="{title_fill}" d="{d}"/>')
    d, w2 = sans_light("不想画图的建筑师", 75, y0 + 52, 24, tracking=1.5)
    out.append(f'<path fill="{sub_fill}" d="{d}"/>')
    d, w3 = sans_light("→", 75 + w2 + 12, y0 + 52, 24)
    out.append(f'<path fill="{accent}" d="{d}"/>')
    d, _ = sans_light("AIGC 设计师 & 架构师", 75 + w2 + w3 + 24, y0 + 52, 24, tracking=1.5)
    out.append(f'<path fill="{sub_fill}" d="{d}"/>')
    d, _ = sans_reg("AI CONTENT  ·  AGENT SKILLS  ·  BRAND GROWTH", 76, y0 + 96, 12, tracking=2.4)
    out.append(f'<path fill="{sub_fill}" opacity="0.7" d="{d}"/>')
    return "\n".join(out)


def svg_wrap(body, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="阿哲 Phil — 不想画图的建筑师 → AIGC 设计师 &amp; 架构师">\n'
        f"<title>阿哲 Phil — 不想画图的建筑师 → AIGC 设计师 &amp; 架构师</title>\n"
        f"<style>{style}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>\n"
        f"{body}\n</svg>\n"
    )


GRAIN = (
    '<filter id="grain" x="0" y="0" width="100%" height="100%">'
    '<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7" stitchTiles="stitch"/>'
    '<feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.9 0"/></filter>'
)


# ---------- A. flow field ----------
def flow(theme):
    noise, fbm = make_noise(11)
    rnd = random.Random(3)
    if theme == "light":
        bg, title, sub, accent = "#faf7f2", "#16131f", "#3b3646", "#e4572e"
        stops = [("#2b2d7c", 0), ("#7b3fa0", 0.45), ("#e4572e", 0.8), ("#f3a712", 1)]
        op = 0.55
    else:
        bg, title, sub, accent = "#0b0d12", "#f4f1fa", "#c9c4d6", "#ff8a65"
        stops = [("#3ad1c7", 0), ("#6c8cff", 0.4), ("#c77dff", 0.75), ("#ff8fab", 1)]
        op = 0.6
    lines = []
    for _ in range(260):
        x, y = rnd.uniform(300, 1240), rnd.uniform(-20, 340)
        pts = [(x, y)]
        for _ in range(90):
            a = fbm(x * 0.0035, y * 0.006, 3) * math.pi * 2.4 + 0.15
            x += math.cos(a) * 4
            y += math.sin(a) * 4
            if not (-40 < x < 1240 and -40 < y < 360):
                break
            pts.append((x, y))
        if len(pts) > 12:
            d = "M" + " ".join(f"{px:.0f} {py:.0f}" for px, py in pts)
            lines.append(f'<path d="{d}" stroke-width="{rnd.choice([0.5, 0.7, 0.9, 1.2])}"/>')
    grad = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for c, o in stops)
    body = f"""<defs>
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="300" y1="0" x2="1200" y2="320">{grad}</linearGradient>
<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0.28" stop-color="#fff" stop-opacity="0"/><stop offset="0.62" stop-color="#fff"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#fadeL)"/></mask>
<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>
{GRAIN}
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{bg}"/>
<g clip-path="url(#r)"><g mask="url(#m)" fill="none" stroke="url(#ink)" stroke-linecap="round" opacity="{op}" class="drift">
{chr(10).join(lines)}
</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{0.06 if theme == 'light' else 0.08}"/></g>
{text_block(theme, title, sub, accent)}"""
    style = ".drift{animation:drift 14s ease-in-out infinite alternate}@keyframes drift{to{transform:translateX(-18px)}}"
    return svg_wrap(body, style)


# ---------- B. ink wash ----------
def ink(theme):
    noise, fbm = make_noise(5)
    if theme == "light":
        bg, inkc, title, sub, accent, orb, orb_op = "#f3eee4", "#1c1c1a", "#1c1c1a", "#4a4640", "#b3362c", "#c8473b", 0.85
        alphas = [0.16, 0.28, 0.48, 0.82]
    else:
        bg, inkc, title, sub, accent, orb, orb_op = "#101113", "#d9dde3", "#eef0f3", "#a9adb4", "#d9574a", "#e9e4d6", 0.9
        alphas = [0.10, 0.18, 0.30, 0.55]
    layers = []
    defs = []
    for i, a in enumerate(alphas):
        base = 150 + i * 32
        amp = 70 - i * 8
        pts = []
        for x in range(-10, W + 11, 6):
            r = smooth(420, 880, x)
            h = (fbm(x * (0.004 + i * 0.0015), i * 3.7, 5) + 0.35) * amp * (0.2 + 0.8 * r) * 1.6
            pts.append((x, base - h + (1 - r) * max(0, 300 - base)))
        d = "M-10 330 L" + " L".join(f"{x} {y:.1f}" for x, y in pts) + f" L{W + 10} 330 Z"
        top = min(y for _, y in pts)
        defs.append(
            f'<linearGradient id="g{i}" gradientUnits="userSpaceOnUse" x1="0" y1="{top:.0f}" x2="0" y2="{base + 70}">'
            f'<stop offset="0" stop-color="{inkc}" stop-opacity="{a}"/><stop offset="1" stop-color="{inkc}" stop-opacity="0"/></linearGradient>'
        )
        layers.append(f'<path d="{d}" fill="url(#g{i})" filter="url(#brush)"/>')
    seal_d, _ = serif_black("哲", 0, 0, 26)
    _, tw1 = serif_black("阿哲", 0, 0, 92)
    _, tw2 = serif_light("Phil", 0, 0, 92)
    seal_x = 72 + tw1 + 20 + tw2 + 20
    body = f"""<defs>
{''.join(defs)}
<filter id="brush" x="-5%" y="-20%" width="110%" height="140%">
<feTurbulence type="fractalNoise" baseFrequency="0.012 0.035" numOctaves="3" seed="3" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="9" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feGaussianBlur in="d" stdDeviation="1.1"/>
</filter>
<filter id="soft"><feGaussianBlur stdDeviation="1.2"/></filter>
<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>
{GRAIN}
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{bg}"/>
<g clip-path="url(#r)">
<circle cx="905" cy="92" r="34" fill="{orb}" opacity="{orb_op}" filter="url(#soft)"/>
{chr(10).join(layers)}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{0.10 if theme == 'light' else 0.07}"/>
</g>
<g transform="translate({seal_x:.0f} 112)"><rect width="38" height="38" rx="4" fill="{accent}"/>
<g transform="translate(6 30)"><path fill="{bg}" d="{seal_d}"/></g></g>
{text_block(theme, title, sub, accent)}"""
    return svg_wrap(body)


# ---------- C. aurora ----------
def aurora(theme):
    if theme == "light":
        bg, title, sub, accent = "#fbf8f4", "#1a1424", "#3d3548", "#d6336c"
        blobs = [(820, 60, 230, "#ffb4a2"), (1030, 230, 220, "#b8c0ff"), (640, 300, 200, "#ffd6a5"),
                 (1150, 40, 170, "#cdb4db"), (470, -40, 160, "#bde0fe")]
        bop = 0.95
    else:
        bg, title, sub, accent = "#0c0a14", "#f6f2ff", "#cfc7e0", "#ff7eb6"
        blobs = [(820, 60, 230, "#5b2a86"), (1030, 230, 220, "#1f6f8b"), (640, 300, 200, "#9d2b6b"),
                 (1150, 40, 170, "#3a49c8"), (470, -40, 160, "#24345e")]
        bop = 0.9
    circles = "\n".join(
        f'<circle class="b{i % 3}" cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for i, (x, y, r, c) in enumerate(blobs)
    )
    body = f"""<defs>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath>
{GRAIN}
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{bg}"/>
<g clip-path="url(#r)">
<g filter="url(#blur)" opacity="{bop}">{circles}</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{0.09 if theme == 'light' else 0.10}"/>
</g>
{text_block(theme, title, sub, accent)}"""
    style = (
        ".b0{animation:m0 18s ease-in-out infinite alternate}.b1{animation:m1 22s ease-in-out infinite alternate}"
        ".b2{animation:m2 26s ease-in-out infinite alternate}"
        "@keyframes m0{to{transform:translate(-60px,30px)}}@keyframes m1{to{transform:translate(50px,-25px)}}"
        "@keyframes m2{to{transform:translate(-30px,-35px)}}"
    )
    return svg_wrap(body, style)


os.makedirs(OUT, exist_ok=True)
for name, fn in [("flow", flow), ("ink", ink), ("aurora", aurora)]:
    for theme in ("light", "dark"):
        svg = fn(theme)
        p = os.path.join(OUT, f"{name}-{theme}.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg)
        print(name, theme, len(svg.encode()) // 1024, "KB")
