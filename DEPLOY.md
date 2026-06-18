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

## 2. R2 — Qur'an recitation audio (needed for the player) + oversized files

The Qur'an reading pages (`/quran/<n>/`) play `/audio/<surah>_<ayah>.mp3` — 6,236 files, ~2.4 GB (Mishary Alafasy). That's too large for Pages, so it's served from R2 at the `/audio/` path. (A few short surahs are bundled locally for preview; the full set goes to R2.)

**Stage the audio with flattened names:**
```bash
mkdir -p audio_r2
for d in quran-daily/social/*_*/ ; do
  k=$(basename "$d"); f="${d}audio/audio.mp3"
  [ -f "$f" ] && cp "$f" "audio_r2/$k.mp3"
done            # -> audio_r2/1_1.mp3, audio_r2/1_2.mp3, ...
```

**Upload and serve at `/audio/`:**
1. **R2 → Create bucket** → e.g. `buruja-audio`.
2. Upload `audio_r2/*` (dashboard, or `rclone`/`wrangler r2 object put`).
3. Route `/audio/*` to the bucket — either bind it to the Pages project with a tiny Pages Function, or give the bucket a public custom domain (e.g. `audio.buruja.com`) and point the audio base there.

**Also (optional):** the two full-tafsir calendars the build removed (`quran-daily.ics` ~46 MB, `quran-page-daily.ics` ~44 MB) and the book PDFs can live on the same bucket.

---

## 3. thedailywird.com (the second site, no redirect)

Per the decision to keep **both** sites live with **no redirect**, `thedailywird.com` is its own separate Pages project served from the original `/Downloads/TheDailyWird` folder (kept on the old "The Daily Wird" branding). Set it up the same way as steps 1–6 above, from that folder's own repo. It shares no deployment with buruja.com.

---

## Notes
- SEO is built in: `public/sitemap.xml` (689 pages), `public/robots.txt`, canonical tags, Open Graph + Twitter cards, JSON-LD.
- Caching + security headers: `public/_headers`. Custom 404: `public/404.html`.
- To rebuild locally: `python3 build.py` (runs assembly → slim → drop-oversized → `content.py` → `seo.py` → `theme.py`).
