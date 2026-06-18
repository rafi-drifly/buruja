#!/usr/bin/env python3
"""Reader-experience pass over public/ (runs in build before seo.py):
 1. Companion entry pages open directly on the deep read (index = chapter), and
    the internal-format picker pills (Deep chapter/Blog/Email/Social) are removed.
 2. Each companion gets its Omar Suleiman 'The Firsts' video embedded.
 3. Every verse block gets the canonical Uthmani Arabic added above the translation,
    taken from quran-daily/verses.json (already grounded via quran.ai). Idempotent."""
import os, re, sys, json

SRC = os.path.dirname(os.path.abspath(__file__))
PUB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, "public")

# canonical Uthmani verses: (surah, ayah) -> arabic
VERSES = {}
for v in json.load(open(os.path.join(SRC, "quran-daily", "verses.json"), encoding="utf-8")):
    VERSES[(v["s"], v["a"])] = v["ar"]

def arabic_for(ref):
    m = re.match(r'(\d+):(\d+)(?:-(\d+))?$', ref)
    if not m:
        return None
    s, a1 = int(m.group(1)), int(m.group(2))
    a2 = int(m.group(3)) if m.group(3) else a1
    parts = [VERSES.get((s, a)) for a in range(a1, a2 + 1)]
    parts = [p for p in parts if p]
    return "  ".join(parts) if parts else None

# companion videos: slug -> (youtube id, title)
VID = {}
for line in open(os.path.join(SRC, "companions", "manifest.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 3 or p[0] == "index":
        continue
    VID[p[2]] = (p[1], (p[5] if len(p) > 5 else "").replace('"', ""))

PILL = re.compile(r'<a [^>]*href="(?:chapter|blog|email|social)\.html"[^>]*>.*?</a>', re.S)
CREF = re.compile(r'class="c">[^<]*?(\d+:\d+(?:-\d+)?)')
AYAH = re.compile(r'<div class="ayah"[^>]*>.*?</div>', re.S)

def strip_pills(html):
    return PILL.sub("", html)

def add_arabic(html):
    def rep(m):
        block = m.group(0)
        if 'class="ar"' in block:
            return block
        cm = CREF.search(block)
        if not cm:
            return block
        ar = arabic_for(cm.group(1))
        if not ar:
            return block
        gt = block.index(">") + 1          # end of opening <div class="ayah" ...>
        return block[:gt] + '<span class="ar">' + ar + "</span>" + block[gt:]
    return AYAH.sub(rep, html)

def video_html(yid, title):
    return ('<div class="video"><div class="vlabel">Watch &middot; The Firsts, Dr. Omar Suleiman</div>'
            '<div class="vwrap"><iframe src="https://www.youtube.com/embed/' + yid + '" title="' + title +
            '" loading="lazy" allow="accelerometer; encrypted-media; picture-in-picture" allowfullscreen></iframe>'
            '</div></div>')

ANCHOR = '<hr class="goldrule">'
n_read = n_vid = n_arabic = 0

# Pass 1: companion entry = the deep read (+ video)
for slug, (yid, title) in VID.items():
    cdir = os.path.join(PUB, "companions", slug)
    ch = os.path.join(cdir, "chapter.html")
    if not os.path.isfile(ch):
        continue
    html = strip_pills(open(ch, encoding="utf-8").read())
    if yid and "/embed/" not in html and ANCHOR in html:
        i = html.index(ANCHOR) + len(ANCHOR)
        html = html[:i] + video_html(yid, title) + html[i:]
        n_vid += 1
    open(os.path.join(cdir, "index.html"), "w", encoding="utf-8").write(html)
    open(ch, "w", encoding="utf-8").write(html)   # keep chapter.html in sync (seo will noindex it)
    n_read += 1

# Pass 2: every page -> strip pills + add Arabic to verse blocks
for dp, _d, files in os.walk(PUB):
    for fn in files:
        if not fn.endswith(".html"):
            continue
        fp = os.path.join(dp, fn)
        doc = open(fp, encoding="utf-8").read()
        new = add_arabic(strip_pills(doc))
        if new != doc:
            if 'class="ar"' in new and 'class="ar"' not in doc:
                n_arabic += 1
            open(fp, "w", encoding="utf-8").write(new)

print("content pass: %d companion reads, %d videos, %d pages gained Arabic" % (n_read, n_vid, n_arabic))
