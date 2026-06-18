#!/usr/bin/env python3
"""Generate Buruja raster brand assets into the SOURCE site/ tree so build.py
picks them up. Emblem: Rub el Hizb (۞) 8-point star, gold on ink. Ink & Parchment."""
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC  = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(SRC, "site")
IMG  = os.path.join(SITE, "images")
os.makedirs(IMG, exist_ok=True)

INK    = (15, 26, 24)      # #0F1A18
INK2   = (22, 32, 30)      # #16201E
CREAM  = (236, 230, 217)   # #ECE6D9
GOLD   = (166, 128, 59)    # #A6803B
GOLDLT = (228, 199, 120)   # #E4C778
WARM   = (201, 183, 154)   # #C9B79A
TEAL   = (127, 204, 196)   # #7FCCC4
TEAL2  = (91, 181, 173)    # #5BB5AD
MUTED  = (154, 148, 134)   # #9A9486
LINE   = (43, 70, 63)

def font(size, paths, index=0):
    for p in paths:
        try:
            return ImageFont.truetype(p, size, index=index)
        except Exception:
            continue
    return ImageFont.load_default()

SERIF = ["/System/Library/Fonts/Palatino.ttc", "/System/Library/Fonts/Times.ttc"]
SANS  = ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/HelveticaNeue.ttc",
         "/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Palatino.ttc"]

def star4(d, cx, cy, r, color, sharp=0.34):
    d.polygon([(cx, cy-r), (cx+r*sharp, cy-r*sharp), (cx+r, cy), (cx+r*sharp, cy+r*sharp),
               (cx, cy+r), (cx-r*sharp, cy+r*sharp), (cx-r, cy), (cx-r*sharp, cy-r*sharp)], fill=color)

def rubhizb(d, cx, cy, h, w, color):
    """Rub el Hizb: an axis-aligned square + a 45-degree square, outlined."""
    d.rectangle([cx-h, cy-h, cx+h, cy+h], outline=color, width=w)
    dg = h * 1.41421
    d.polygon([(cx, cy-dg), (cx+dg, cy), (cx, cy+dg), (cx-dg, cy)], outline=color, width=w)

# ---------------- favicon / app mark ----------------
def mark(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s-1, s-1], radius=int(s*0.22), fill=INK)
    cx = cy = s/2
    rubhizb(d, cx, cy, s*0.20, max(2, int(s*0.05)), GOLD)
    d.ellipse([cx-s*0.052, cy-s*0.052, cx+s*0.052, cy+s*0.052], fill=GOLDLT)
    return im.resize((size, size), Image.LANCZOS)

for sz in (16, 32, 48, 128, 192, 512):
    mark(sz).save(os.path.join(SITE, "favicon-%dx%d.png" % (sz, sz)))
mark(180).save(os.path.join(IMG, "apple-touch-icon.png"))
mark(64).save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
mark(64).save(os.path.join(IMG, "hadith_icon2.png"))

# ---------------- OG share card 1200x630 ----------------
W, H = 1200, 630
og = Image.new("RGB", (W, H), INK)
d = ImageDraw.Draw(og)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(INK[0]*(1-t)+INK2[0]*t), int(INK[1]*(1-t)+INK2[1]*t),
                                   int(INK[2]*(1-t)+INK2[2]*t)))
stars = [(150,110),(265,75),(400,140),(515,95),(70,300),(980,120),(1060,80),(900,190),
         (1120,330),(150,545),(1080,545),(620,70)]
for a, b in [(0,1),(1,2),(2,3),(5,6),(5,7),(0,4)]:
    d.line([stars[a], stars[b]], fill=LINE, width=2)
for i, (x, y) in enumerate(stars):
    star4(d, x, y, 6 + (i % 3)*3, WARM if i % 2 else CREAM)
# emblem
rubhizb(d, W/2, 150, 34, 4, GOLD)
d.ellipse([W/2-6, 144, W/2+6, 156], fill=GOLDLT)
# wordmark + tagline
wf = font(132, SERIF)
d.text(((W-d.textlength("Buruja", font=wf))/2, 225), "Buruja", font=wf, fill=CREAM)
d.line([(W/2-95, 405), (W/2+95, 405)], fill=TEAL, width=3)
tf = font(32, SANS)
tag = "A verse a day, for the sake of Allah"
d.text(((W-d.textlength(tag, font=tf))/2, 432), tag, font=tf, fill=MUTED)
uf = font(23, SANS)
d.text(((W-d.textlength("buruja.com", font=uf))/2, 500), "buruja.com", font=uf, fill=TEAL2)
og.save(os.path.join(SITE, "og-default.png"), "PNG")

print("Brand assets written (Rub el Hizb emblem): favicons, apple-touch, og-default.png")
