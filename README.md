# Buruja

**Buruja** (from *al-Burūj*, البروج — "the constellations of light") is a *sadaqah jariyah* project: a verse of the Qur'an a day, with the stories of the Companions, the Seerah, the Prophets, the 99 Names of Allah, Juz 'Amma, a daily *wird* of remembrance, and a path for new Muslims. Free for the global ummah.

- **Primary:** https://buruja.com
- **Also live:** https://thedailywird.com (redirects / canonical → buruja.com)

## This repository

The deployable static site lives in [`public/`](public/), assembled by [`build.py`](build.py) from the project's source content.

Handled separately (not in this repo): social-media renders, audio recitations, video, and book PDFs — regenerable assets destined for Cloudflare R2 — and the SalatTid.se Swedish prayer-times sub-brand.

## Site map (`public/`)

| Path | Content |
|------|---------|
| `/` | Homepage |
| `/quran-daily/` | Daily Qur'an calendar subscriptions (`.ics`) |
| `/companions/` | The Companions — 183 Sahaba |
| `/seerah/` | The Seerah — 104 daily entries |
| `/prophets/` | Stories of the Prophets |
| `/asma-ul-husna/` | The 99 Names of Allah |
| `/juz-amma/` | Juz ʿAmma |
| `/adhkar/` | Dhikr & Duʿaʾ |
| `/quran-reader/` | Tajweed Qur'an reader |
| `/new-muslim/` | New Muslim path |
| `/the-365/` | The 365 tracks (calendars) |

## Deploy (Cloudflare Pages)

- Build output directory: `public/`
- No build command required (static site).
