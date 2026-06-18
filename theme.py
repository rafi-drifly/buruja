#!/usr/bin/env python3
"""Site-wide skin pass over public/: replace the legacy mosque logo with the
gold Rub el Hizb emblem and inject the shared buruja.css on pillar pages.
Idempotent; runs after seo.py in the build."""
import os, re, sys

PUB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
CSS_LINK = '<link rel="stylesheet" href="/buruja.css">'

# legacy mark: any <svg ... viewBox="0 0 80 74" ...> ... </svg> (the mosque artboard)
MOSQUE = re.compile(r'<svg\b[^>]*viewBox="0 0 80 74"[^>]*>.*?</svg>', re.S)
def _swap(m):
    tag = m.group(0)
    wm = re.search(r'width="(\d+)"', tag); hm = re.search(r'height="(\d+)"', tag)
    return emblem(wm.group(1) if wm else "40", hm.group(1) if hm else "37")

_counter = [0]
def emblem(w, h):
    _counter[0] += 1
    gid = "rh%d" % _counter[0]
    return ('<svg width="%s" height="%s" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-label="Buruja">'
            '<defs><linearGradient id="%s" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#E4C778"/><stop offset="1" stop-color="#A6803B"/></linearGradient></defs>'
            '<g fill="none" stroke="url(#%s)" stroke-width="2.4" stroke-linejoin="round">'
            '<rect x="13" y="13" width="22" height="22"/>'
            '<rect x="13" y="13" width="22" height="22" transform="rotate(45 24 24)"/></g>'
            '<circle cx="24" cy="24" r="2.6" fill="#E4C778"/></svg>') % (w, h, gid, gid)

n_pages = n_marks = n_css = 0
for dp, _d, files in os.walk(PUB):
    for fn in files:
        if not fn.lower().endswith((".html", ".htm")):
            continue
        fp = os.path.join(dp, fn)
        try:
            doc = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        orig = doc
        doc, k = MOSQUE.subn(_swap, doc)
        # inject the shared stylesheet on pillar pages only (they carry .topbar)
        if 'class="topbar"' in doc and CSS_LINK not in doc and "</head>" in doc:
            doc = doc.replace("</head>", "  " + CSS_LINK + "\n</head>", 1)
            n_css += 1
        if doc != orig:
            open(fp, "w", encoding="utf-8").write(doc)
            n_pages += 1; n_marks += k

print("theme pass: %d pages updated, %d mosque marks -> Rub el Hizb, %d buruja.css links" % (n_pages, n_marks, n_css))
