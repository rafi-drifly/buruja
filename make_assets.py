#!/usr/bin/env python3
"""Generate Buruja raster brand assets (favicons, apple-touch, og share card)
into the SOURCE site/ tree so build.py picks them up. Palette: Ink & Parchment."""
from PIL import Image, ImageDraw, ImageFont
import os, math

SRC   = os.path.dirname(os.path.abspath(__file__))
SITE  = os.path.join(SRC, "site")
IMG   = os.path.join(SITE, "images")
os.makedirs(IMG, exist_ok=True)

INK   = (15, 26, 24)      # #0F1A18
INK2  = (22, 32, 30)      # #16201E
CREAM = (236, 230, 217)   # #ECE6D9
WARM  = (201, 183, 154)   # #C9B79A
TEAL  = (127, 204, 196)   # #7FCCC4
TEAL2 = (91, 181, 173)    # #5BB5AD
MUTED = (154, 148, 134)   # #9A9486
LINE  = (38, 70, 64)

def font(size, paths, index=0):
    for p in paths:
        try:
            return ImageFont.truetype(p, size, index=index)
        except Exception:
            continue
    return ImageFont.load_default()

SERIF = ["/System/Library/Fonts/Palatino.ttc", "/System/Library/Fonts/Times.ttc",
         "/Library/Fonts/Georgia.ttf"]
SANS  = ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/HelveticaNeue.ttc",
         "/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]

# ---------------- 4-point star helper ----------------
def star4(d, cx, cy, r, color, sharp=0.34):
    d.polygon([(cx, cy - r), (cx + r*sharp, cy - r*sharp), (cx + r, cy),
               (cx + r*sharp, cy + r*sharp), (cx, cy + r), (cx - r*sharp, cy + r*sharp),
               (cx - r, cy), (cx - r*sharp, cy - r*sharp)], fill=color)

# ---------------- favicon / app mark ----------------
def mark(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s-1, s-1], radius=int(s*0.22), fill=INK)
    cx = cy = s/2
    # faint constellation line + companion stars
    d.line([(s*0.30, s*0.34), (cx, cy), (s*0.72, s*0.70)], fill=LINE, width=max(1, int(s*0.012)))
    star4(d, cx, cy, s*0.30, WARM)                 # main star
    d.ellipse([cx-s*0.05, cy-s*0.05, cx+s*0.05, cy+s*0.05], fill=CREAM)  # core glow
    star4(d, s*0.30, s*0.34, s*0.085, TEAL)        # small companion
    star4(d, s*0.72, s*0.70, s*0.07, TEAL2)
    return im.resize((size, size), Image.LANCZOS)

for sz in (16, 32, 48, 128, 192, 512):
    mark(sz).save(os.path.join(SITE, "favicon-%dx%d.png" % (sz, sz)))
mark(180).save(os.path.join(IMG, "apple-touch-icon.png"))
mark(64).save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
# small decorative star icon used on the homepage
ic = mark(64).convert("RGBA")
ic.save(os.path.join(IMG, "hadith_icon2.png"))

# ---------------- OG share card 1200x630 ----------------
W, H = 1200, 630
og = Image.new("RGB", (W, H), INK)
d = ImageDraw.Draw(og)
for y in range(H):                                  # vertical ink gradient
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(INK[0]*(1-t)+INK2[0]*t),
                                   int(INK[1]*(1-t)+INK2[1]*t),
                                   int(INK[2]*(1-t)+INK2[2]*t)))
# constellation (deterministic)
stars = [(150,110),(265,75),(400,140),(515,95),(70,300),
         (980,120),(1060,80),(900,190),(1120,330),(150,545),(1080,545),(620,70)]
for a, b in [(0,1),(1,2),(2,3),(5,6),(5,7),(0,4)]:
    d.line([stars[a], stars[b]], fill=LINE, width=2)
for i, (x, y) in enumerate(stars):
    star4(d, x, y, 6 + (i % 3)*3, WARM if i % 2 else CREAM)
# wordmark
wf = font(150, SERIF)
tw = d.textlength("Buruja", font=wf)
d.text(((W-tw)/2, 200), "Buruja", font=wf, fill=CREAM)
d.line([(W/2-95, 392), (W/2+95, 392)], fill=TEAL, width=3)
# tagline + url
tf = font(33, SANS)
tag = "A verse a day, for the sake of Allah"
d.text(((W-d.textlength(tag, font=tf))/2, 425), tag, font=tf, fill=MUTED)
uf = font(24, SANS)
d.text(((W-d.textlength("buruja.com", font=uf))/2, 498), "buruja.com", font=uf, fill=TEAL2)
og.save(os.path.join(SITE, "og-default.png"), "PNG")

print("Raster assets written to site/ and site/images/:")
print("  favicon-{16,32,48,128,192,512}.png, favicon.ico, images/apple-touch-icon.png,")
print("  images/hadith_icon2.png, og-default.png")
