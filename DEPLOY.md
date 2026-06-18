# Deploying Buruja to Cloudflare

The site is a static build in **`public/`** (689 indexable pages, ~190 MB, every file under Cloudflare Pages' 25 MB limit — the build drops the two oversized calendars; see R2 below). You run these steps with your own Cloudflare account.

---

## 1. buruja.com → Cloudflare Pages (recommended: Git-connected)

1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git**.
2. Pick the repo **`rafi-drifly/buruja`**, branch `main`.
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*  — the repo already contains the built `public/`
   - **Build output directory:** `public`
4. **Save and Deploy.** First build takes a minute; you'll get a `buruja.pages.dev` URL.

### Custom domain
5. In the Pages project → **Custom domains → Set up a custom domain** → `buruja.com` (repeat for `www.buruja.com`).
6. If the domain's DNS is on Cloudflare, the records are added automatically. Otherwise add the CNAME they show you at your registrar.

> Updates: every `git push` to `main` redeploys automatically. (If you change content locally, run `python3 build.py` first, then commit `public/`.)

### CLI alternative
```bash
npm i -g wrangler          # or use npx
wrangler login
wrangler pages deploy public --project-name=buruja
```

---

## 2. R2 for the oversized files (optional, only if you want them live)

The build removes two full-tafsir calendars that exceed Pages' 25 MB/file cap:
- `quran-daily/quran-daily.ics` (~46 MB)
- `quran-daily/quran-page-daily.ics` (~44 MB)

(The lite `.ics` versions stay on Pages.) Nothing on the site links these yet, so this is optional until you add calendar-subscribe buttons. To host them — and later the audio recitations + book PDFs:

1. **R2 → Create bucket** → e.g. `buruja-assets`.
2. Upload the files (dashboard or `wrangler r2 object put buruja-assets/quran-daily.ics --file=...`).
3. **Bucket → Settings → Public access → connect a domain**, e.g. `assets.buruja.com`.
4. Link to them as `https://assets.buruja.com/quran-daily.ics`.

---

## 3. thedailywird.com (the second site, no redirect)

Per the decision to keep **both** sites live with **no redirect**, `thedailywird.com` is its own separate Pages project served from the original `/Downloads/TheDailyWird` folder (kept on the old "The Daily Wird" branding). Set it up the same way as steps 1–6 above, from that folder's own repo. It shares no deployment with buruja.com.

---

## Notes
- SEO is built in: `public/sitemap.xml` (689 pages), `public/robots.txt`, canonical tags, Open Graph + Twitter cards, JSON-LD.
- Caching + security headers: `public/_headers`. Custom 404: `public/404.html`.
- To rebuild locally: `python3 build.py` (runs assembly → slim → drop-oversized → `content.py` → `seo.py` → `theme.py`).
