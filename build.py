#!/usr/bin/env python3
"""Assemble the deployable Buruja static site into public/.
Mounts each pillar's web-root at its URL path; excludes the social factory,
audio/video, PDFs, build source, and archives."""
import os, shutil, sys, re, html as _html

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "public")

# (url_path, source_web_root)
MOUNTS = [
    ("",              "site"),                  # homepage + data + sitemap at /
    ("adhkar",        "adhkar"),
    ("asma-ul-husna", "asma-ul-husna"),
    ("companions",    "companions/companions"), # inner dir is the web-root
    ("juz-amma",      "juz-amma"),
    ("new-muslim",    "new-muslim"),
    ("prophets",      "prophets"),
    ("quran-reader",  "quran-reader"),
    ("seerah",        "seerah"),
    ("the-365",       "the-365"),
    ("quran-daily",   "quran-daily"),           # data/calendar only (see rule below)
]

WEB_EXT = {'.html','.htm','.css','.js','.svg','.json','.xml','.ics','.woff','.woff2',
           '.ico','.webmanifest','.txt','.map'}
IMG_EXT = {'.jpg','.jpeg','.png','.gif','.webp','.avif'}
SKIP_DIR = {'social','_social','__pycache__','_archive-pre-brand','_archive','archive',
            'brand-samples','_brand_samples','transcripts','node_modules','.git',
            '_social_packs','social-packs','_cache','_raw','_cfg','_html'}

def include(src_rel_root, rel, fn):
    ext = os.path.splitext(fn)[1].lower()
    if src_rel_root == "quran-daily":          # calendar subscriptions only
        return ext == '.ics'                    # verses.json/tafsirs.json unused by the site
    return ext in WEB_EXT or ext in IMG_EXT

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

summary, total_files, total_bytes = [], 0, 0
for url_path, src_rel in MOUNTS:
    src = os.path.join(SRC, src_rel)
    if not os.path.isdir(src):
        summary.append((url_path or "/", src_rel, 0, 0.0, "MISSING")); continue
    cnt = byts = 0
    for dp, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIR]
        rel_dir = os.path.relpath(dp, src)
        for fn in files:
            if fn == '.DS_Store':
                continue
            if not include(src_rel, os.path.join(rel_dir, fn), fn):
                continue
            srcf = os.path.join(dp, fn)
            rel  = os.path.normpath(os.path.join(url_path, rel_dir, fn))
            dstf = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dstf), exist_ok=True)
            shutil.copy2(srcf, dstf)
            cnt += 1; byts += os.path.getsize(srcf)
    summary.append((url_path or "/", src_rel, cnt, byts/1048576, ""))
    total_files += cnt; total_bytes += byts

# quran-reader entry is reader.html -> ensure /quran-reader/ has an index.html
qr = os.path.join(OUT, "quran-reader")
if os.path.isdir(qr) and not os.path.exists(os.path.join(qr, "index.html")) \
   and os.path.exists(os.path.join(qr, "reader.html")):
    shutil.copy2(os.path.join(qr, "reader.html"), os.path.join(qr, "index.html"))
    print("note: created /quran-reader/index.html from reader.html")

# --- slim: drop raster images not referenced by any html/css/js/json (social cards) ---
_IMG = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}
_KEEP = ('favicon', 'apple-touch', 'icon', 'og-default', 'logo')
_attr = re.compile(r'(?:src|href|poster|content)\s*=\s*["\']([^"\']+)["\']', re.I)
_css  = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', re.I)
_srcs = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.I)
_anyi = re.compile(r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|avif))["\']', re.I)
_ref = set()
def _add(hf, raw):
    raw = _html.unescape(raw.strip())
    if not raw or raw.startswith(('http://', 'https://', 'data:', 'mailto:', 'tel:', '#', 'javascript:')):
        return
    raw = raw.split('?')[0].split('#')[0]
    if not raw:
        return
    p = os.path.normpath(os.path.join(OUT, raw.lstrip('/'))) if raw.startswith('/') \
        else os.path.normpath(os.path.join(os.path.dirname(hf), raw))
    _ref.add(p)
for dp, _d, files in os.walk(OUT):
    for fn in files:
        if not fn.lower().endswith(('.html', '.htm', '.css', '.js', '.json')):
            continue
        fp = os.path.join(dp, fn)
        try:
            t = open(fp, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for m in _attr.finditer(t): _add(fp, m.group(1))
        for m in _css.finditer(t):  _add(fp, m.group(1))
        for m in _srcs.finditer(t):
            for part in m.group(1).split(','):
                u = part.strip().split(' ')[0]
                if u: _add(fp, u)
        for m in _anyi.finditer(t): _add(fp, m.group(1))
_slim = _slimb = 0
for dp, _d, files in os.walk(OUT):
    for fn in files:
        if os.path.splitext(fn)[1].lower() not in _IMG:
            continue
        fp = os.path.join(dp, fn)
        if fp in _ref or any(k in fp.lower() for k in _KEEP):
            continue
        _slimb += os.path.getsize(fp); os.remove(fp); _slim += 1
for dp, _d, _f in os.walk(OUT, topdown=False):
    if os.path.isdir(dp) and not os.listdir(dp):
        os.rmdir(dp)
print("slimmed %d unreferenced social images (%.1f MB)" % (_slim, _slimb/1048576))

print("\n%-16s %-26s %7s %9s" % ("URL", "SRC", "FILES", "MB"))
for u, s, c, mb, note in summary:
    print("  %-14s %-26s %7d %8.1f  %s" % (u, s, c, mb, note))
print("\nTOTAL: %d files, %.1f MB  ->  %s" % (total_files, total_bytes/1048576, OUT))

# --- SEO pass: canonical, meta, Open Graph, JSON-LD, robots.txt, sitemap.xml ---
import subprocess
print()
subprocess.run([sys.executable, os.path.join(SRC, "seo.py"), OUT], check=False)
