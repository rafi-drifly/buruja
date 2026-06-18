#!/usr/bin/env python3
"""SEO pass over public/: inject canonical, meta description, Open Graph,
Twitter cards, and JSON-LD into every page; generate robots.txt + sitemap.xml.
Idempotent — safe to re-run. Intended to run after build.py."""
import os, re, html, json, sys

PUB    = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
ORIGIN = "https://buruja.com"
SITE   = "Buruja"
OG_IMG = ORIGIN + "/og-default.png"   # placeholder until brand artwork is designed

PILLAR_LABELS = {
    "adhkar": "Dhikr & Du'a", "asma-ul-husna": "The 99 Names of Allah",
    "companions": "The Companions", "juz-amma": "Juz Amma",
    "new-muslim": "New Muslim", "prophets": "Stories of the Prophets",
    "quran-reader": "Qur'an Reader", "seerah": "The Seerah",
    "the-365": "The 365", "quran-daily": "Daily Qur'an",
}

def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def canonical_for(relpath):
    # relpath is POSIX, relative to PUB
    parts = relpath.split("/")
    if parts[-1] == "index.html":
        url = "/".join(parts[:-1])
        url = "/" + (url + "/" if url else "")
    elif parts[-1] == "reader.html":            # duplicate of quran-reader/index.html
        url = "/" + "/".join(parts[:-1]) + "/"
    else:
        url = "/" + relpath
    return ORIGIN + url.replace("//", "/").replace(":/", "://")

def first_paragraph(body):
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", body, re.S | re.I):
        txt = strip_tags(m.group(1))
        if len(txt) >= 40:
            return txt
    return ""

stats = {"pages": 0, "canonical": 0, "desc": 0, "og": 0, "jsonld": 0}
sitemap_urls = []

for dp, _dirs, files in os.walk(PUB):
    for fn in files:
        if not fn.lower().endswith((".html", ".htm")):
            continue
        fp = os.path.join(dp, fn)
        rel = os.path.relpath(fp, PUB).replace(os.sep, "/")
        try:
            doc = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        stats["pages"] += 1
        fnl = fn.lower()
        is_reader_dup = fnl == "reader.html"
        segs = rel.split("/")
        is_variant = (fnl in ("blog.html", "email.html", "social.html", "sheet.html")
                      or re.match(r"slide-\d+\.html$", fnl) is not None
                      or "social-images" in segs or "social" in segs)
        noindex = is_reader_dup or is_variant
        if noindex:                       # alternate-format renderings -> canonical to the entry page
            d = os.path.dirname(rel)
            canon = canonical_for((d + "/index.html") if d else "index.html")
        else:
            canon = canonical_for(rel)
            sitemap_urls.append(canon)

        # --- title ---
        mt = re.search(r"<title[^>]*>(.*?)</title>", doc, re.S | re.I)
        title = strip_tags(mt.group(1)) if mt else ""
        if not title:
            mh = re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.S | re.I)
            title = strip_tags(mh.group(1)) if mh else SITE
        if SITE.lower() not in title.lower():
            new_title = title + " · " + SITE
            if mt:
                doc = doc[:mt.start()] + "<title>" + html.escape(new_title) + "</title>" + doc[mt.end():]
            title = new_title

        # --- description ---
        md = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', doc, re.S | re.I)
        if md and strip_tags(md.group(1)):
            desc = strip_tags(md.group(1))
        else:
            desc = first_paragraph(doc) or title
        desc = desc[:158].rstrip()

        # --- build head tags to inject (only those not already present) ---
        add = []
        if "rel=\"canonical\"" not in doc and "rel='canonical'" not in doc:
            add.append('<link rel="canonical" href="%s">' % canon); stats["canonical"] += 1
        if not md:
            add.append('<meta name="description" content="%s">' % html.escape(desc)); stats["desc"] += 1
        if noindex:
            add.append('<meta name="robots" content="noindex,follow">')
        if 'rel="icon"' not in doc and "rel='icon'" not in doc:
            add += ['<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
                    '<link rel="icon" href="/favicon-32x32.png" sizes="32x32" type="image/png">',
                    '<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">']
        if "og:title" not in doc:
            stats["og"] += 1
            ptype = "article" if rel.count("/") >= 2 else "website"
            add += [
                '<meta property="og:type" content="%s">' % ptype,
                '<meta property="og:site_name" content="%s">' % SITE,
                '<meta property="og:title" content="%s">' % html.escape(title),
                '<meta property="og:description" content="%s">' % html.escape(desc),
                '<meta property="og:url" content="%s">' % canon,
                '<meta property="og:image" content="%s">' % OG_IMG,
                '<meta name="twitter:card" content="summary_large_image">',
                '<meta name="twitter:title" content="%s">' % html.escape(title),
                '<meta name="twitter:description" content="%s">' % html.escape(desc),
                '<meta name="twitter:image" content="%s">' % OG_IMG,
            ]

        # --- JSON-LD (skip alternate-format / noindex pages) ---
        if "application/ld+json" not in doc and not noindex:
            stats["jsonld"] += 1
            seg = rel.split("/")
            if rel == "index.html":
                ld = [
                    {"@context": "https://schema.org", "@type": "Organization", "name": SITE,
                     "url": ORIGIN, "logo": OG_IMG},
                    {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": ORIGIN},
                ]
            else:
                pillar = seg[0]
                crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"}]
                if pillar in PILLAR_LABELS:
                    crumbs.append({"@type": "ListItem", "position": 2, "name": PILLAR_LABELS[pillar],
                                   "item": "%s/%s/" % (ORIGIN, pillar)})
                is_leaf = rel.count("/") >= 2
                if is_leaf:
                    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": title.split(" · ")[0], "item": canon})
                ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs}]
                if is_leaf:
                    ld.append({"@context": "https://schema.org", "@type": "Article",
                               "headline": title.split(" · ")[0], "description": desc,
                               "url": canon, "inLanguage": "en",
                               "isPartOf": {"@type": "WebSite", "name": SITE, "url": ORIGIN},
                               "publisher": {"@type": "Organization", "name": SITE, "logo": OG_IMG}})
                else:
                    ld.append({"@context": "https://schema.org", "@type": "CollectionPage",
                               "name": title.split(" · ")[0], "url": canon,
                               "isPartOf": {"@type": "WebSite", "name": SITE, "url": ORIGIN}})
            add.append('<script type="application/ld+json">%s</script>'
                       % json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False, separators=(",", ":")))

        # --- ensure <html lang> ---
        if re.search(r"<html(?![^>]*\blang=)", doc, re.I):
            doc = re.sub(r"<html\b", '<html lang="en"', doc, count=1, flags=re.I)

        # --- inject before </head> ---
        if add:
            inject = "\n  " + "\n  ".join(add) + "\n"
            if re.search(r"</head>", doc, re.I):
                doc = re.sub(r"</head>", inject + "</head>", doc, count=1, flags=re.I)
            else:  # no head: prepend after <html> or at top
                doc = inject + doc
            open(fp, "w", encoding="utf-8").write(doc)

# --- robots.txt ---
robots = "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % ORIGIN
open(os.path.join(PUB, "robots.txt"), "w").write(robots)

# --- sitemap.xml ---
sitemap_urls = sorted(set(sitemap_urls))
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in sitemap_urls:
    lines.append("  <url><loc>%s</loc></url>" % html.escape(u))
lines.append("</urlset>")
open(os.path.join(PUB, "sitemap.xml"), "w").write("\n".join(lines))

print("SEO pass complete:")
for k, v in stats.items():
    print("  %-10s %d" % (k, v))
print("  sitemap urls: %d" % len(sitemap_urls))
print("  robots.txt + sitemap.xml written")
