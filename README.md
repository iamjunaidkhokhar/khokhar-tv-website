# Khokhar TV website

Official marketing and download site for Khokhar TV. Plain static HTML/CSS
with a few lines of JS, served by GitHub Pages from the repo root.

## Editing

Page bodies live in `src/pages/*.html` (each starts with a JSON metadata
comment: title, description, optional JSON-LD). The shared head, header and
footer are in `scripts/build.py`. After editing:

```bash
python3 scripts/build.py   # regenerates *.html, apk/index.html, sitemap.xml, robots.txt
```

Commit both the source and the generated files.

- **Address:** the site lives at
  https://iamjunaidkhokhar.github.io/khokhar-tv-website. To move to a custom
  domain, set `SITE_URL` in `scripts/build.py` to it (links re-base
  automatically), rebuild, and add a `CNAME` file containing the bare domain.
- **Prices:** set `PRICES` in `scripts/build.py` (None shows "Ask us").
- **WhatsApp number:** `WHATSAPP` in `scripts/build.py`.

## Downloads

Download buttons read
`https://mchwhfdfpovaxbyeijjr.supabase.co/storage/v1/object/public/releases/manifest.json`,
which the app repo's CI (`scripts/publish-build.mjs`) updates after every
Android, Windows and Linux build. Large files (over Supabase's 50 MB free-plan
cap) are attached to this repo's GitHub Releases. Buttons stay disabled
("Publishing soon") until a platform has an entry.

`/apk` is a short link for the Fire TV Downloader app: it redirects to the
newest Android TV APK.
