#!/usr/bin/env python3
"""Builds the static Khokhar TV site.

Each page body lives in src/pages/<name>.html. This wraps it in the shared
layout (head/meta/header/footer), writes <name>.html at the repo root (where
GitHub Pages serves from), and regenerates sitemap.xml.

    python3 scripts/build.py

No dependencies beyond the standard library. Edit SITE_URL once the custom
domain is live; everything canonical/OG/sitemap derives from it.
"""
import datetime
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"

# Public URL of the site, without a trailing slash. On a GitHub project page
# that includes the repo path; with a custom domain it's just the origin.
SITE_URL = "https://iamjunaidkhokhar.github.io/khokhar-tv-website"
# Path prefix that root-relative links ("/download") need, derived from SITE_URL.
BASE_PATH = "/" + SITE_URL.split("://", 1)[1].partition("/")[2].strip("/")
BASE_PATH = "" if BASE_PATH == "/" else BASE_PATH
SITE_NAME = "Khokhar TV"
WHATSAPP = "447882746104"
WHATSAPP_URL = (
    f"https://wa.me/{WHATSAPP}?text=Hi!%20I%27d%20like%20to%20subscribe%20to%20Khokhar%20TV."
)
# Prices shown on /pricing. None shows "Ask us" with a WhatsApp link instead.
PRICES = {"monthly": None, "yearly": None, "currency": "USD"}

ICONS = {
    "check": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "download": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12m0 0 5-5m-5 5-5-5M4 21h16"/></svg>',
    "whatsapp": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3a.5.5 0 0 0 0-.5l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.5-.3Z"/></svg>',
    "tv": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="6.5" width="19" height="13" rx="2.5"/><path d="m8 2.5 4 4 4-4"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M11 18.5h2"/></svg>',
    "windows": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 5.3 10.4 4v7.3H3V5.3Zm8.4-1.4L21 2.5v8.8h-9.6V3.9ZM3 12.6h7.4V20L3 18.7v-6.1Zm8.4 0H21v8.9l-9.6-1.4v-7.5Z"/></svg>',
    "linux": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="3.5" width="19" height="14" rx="2"/><path d="m6.5 8 3 2.5-3 2.5M11.5 13h4M8 21h8"/></svg>',
    "apple": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.5 2-3.6a4.3 4.3 0 0 0-3.4-1.8c-1.4-.2-2.8.8-3.5.8s-1.8-.8-3-.8a4.5 4.5 0 0 0-3.8 2.3c-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3s1.6-.7 3-.7 1.8.7 3 .7 2-1.1 2.8-2.3a10 10 0 0 0 1.3-2.6 3.9 3.9 0 0 1-2.5-3.6ZM14.1 5.5A4 4 0 0 0 15 2.5a4.1 4.1 0 0 0-2.7 1.4 3.8 3.8 0 0 0-1 2.8 3.4 3.4 0 0 0 2.8-1.2Z"/></svg>',
    "firetv": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3c1 3 4 4.5 4 8.5a4 4 0 0 1-8 0c0-1.8.8-3 1.8-4 .2 1.5 1 2.3 1.7 2.5C11 8 11 5.5 12 3Z"/><path d="M5 21h14"/></svg>',
    "remote": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="7" y="2.5" width="10" height="19" rx="5"/><circle cx="12" cy="8.5" r="2"/><path d="M12 14v.01M12 17.5v.01"/></svg>',
    "grid": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="8" height="7" rx="1.5"/><rect x="13" y="4" width="8" height="7" rx="1.5"/><rect x="3" y="13" width="8" height="7" rx="1.5"/><rect x="13" y="13" width="8" height="7" rx="1.5"/></svg>',
    "guide": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 4v16M14 13h4M14 16.5h2"/></svg>',
    "resume": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/></svg>',
    "mic": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="2.5" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3.5"/></svg>',
    "subs": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M7 13h3M13 13h4M7 16h6M15 16h2"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="10.5" width="16" height="10.5" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/></svg>',
    "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/></svg>',
    "sync": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11a8 8 0 0 0-14.3-4.9L4 8M4 4v4h4M4 13a8 8 0 0 0 14.3 4.9L20 16M20 20v-4h-4"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20s-7.5-4.6-9.3-9.3A5 5 0 0 1 12 6a5 5 0 0 1 9.3 4.7C19.5 15.4 12 20 12 20Z"/></svg>',
    "menu": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

NAV = [
    ("index", "/", "Home"),
    ("features", "/features", "Features"),
    ("download", "/download", "Download"),
    ("pricing", "/pricing", "Pricing"),
    ("support", "/support", "Help"),
]


def head(meta, name):
    path = meta.get("path", "/" if name == "index" else f"/{name}")
    url = SITE_URL + path
    title = meta["title"]
    full_title = title if name == "index" else f"{title} | {SITE_NAME}"
    desc = meta["description"]
    robots = meta.get("robots", "index,follow")
    ld = meta.get("jsonld", "").replace("{{site}}", SITE_URL).replace("{{host}}", SITE_URL.split("://", 1)[1])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#07090d">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{full_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE_URL}/assets/img/og.png">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/img/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/inter-extrabold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://mchwhfdfpovaxbyeijjr.supabase.co" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(name):
    items = "\n".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if key == name else ""}>{label}</a></li>'
        for key, href, label in NAV
    )
    return f"""<header class="site-header">
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="/" aria-label="Khokhar TV home"><img src="/assets/img/logo.svg" alt="" width="34" height="34">KHOKHAR TV</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false" aria-controls="nav-links">{ICONS["menu"]}</button>
    <ul class="nav-links" id="nav-links">
{items}
    </ul>
    <a class="btn btn-accent btn-sm" href="/download">{ICONS["download"]}Get the app</a>
  </nav>
</header>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="/"><img src="/assets/img/logo.svg" alt="" width="30" height="30" loading="lazy">KHOKHAR TV</a>
        <p style="margin-top:14px;max-width:30em">A fast, remote-friendly player for live TV, movies and series on Android TV, Google TV, Fire TV, Android, Windows and Linux.</p>
      </div>
      <div>
        <h4>Product</h4>
        <ul><li><a href="/features">Features</a></li><li><a href="/download">Download</a></li><li><a href="/pricing">Pricing</a></li></ul>
      </div>
      <div>
        <h4>Help</h4>
        <ul><li><a href="/support">FAQ &amp; setup</a></li><li><a href="/support#fire-tv">Install on Fire TV</a></li><li><a href="{WHATSAPP_URL}" rel="noopener">WhatsApp us</a></li></ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul><li><a href="/privacy">Privacy policy</a></li><li><a href="/terms">Terms of service</a></li></ul>
      </div>
    </div>
    <p class="legal">&copy; <span id="year">{datetime.date.today().year}</span> Khokhar TV. Khokhar TV is a media player. It does not provide, host or sell TV channels, movies or series; it plays the service assigned to your account. Android, Google TV and Android TV are trademarks of Google LLC. Fire TV is a trademark of Amazon.com, Inc. Windows is a trademark of Microsoft Corporation.</p>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def parse(text):
    """Pages start with an HTML comment holding a JSON object of metadata."""
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    if not m:
        raise SystemExit("page is missing its metadata comment")
    return json.loads(m.group(1)), text[m.end():]


def price_html(key):
    p = PRICES[key]
    if p is None:
        return '<div class="price">Ask us</div><div class="per">Message us for today\'s price</div>'
    per = "per month" if key == "monthly" else "per year"
    return f'<div class="price">{PRICES["currency"]} {p}</div><div class="per">{per}</div>'


def render(body):
    body = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: ICONS[m.group(1)], body)
    body = body.replace("{{whatsapp}}", WHATSAPP_URL)
    body = body.replace("{{site}}", SITE_URL)
    body = body.replace("{{host}}", SITE_URL.split("://", 1)[1])
    body = body.replace("{{price:monthly}}", price_html("monthly"))
    body = body.replace("{{price:yearly}}", price_html("yearly"))
    return body


def rebase(html):
    """Prefixes root-relative URLs with BASE_PATH (project pages live under /<repo>/)."""
    if not BASE_PATH:
        return html
    html = re.sub(r'((?:href|src)=")/(?!/)', r"\g<1>" + BASE_PATH + "/", html)
    return re.sub(r"(srcset=\"[^\"]*)", lambda m: re.sub(r"(^srcset=\"|, )/(?!/)", r"\g<1>" + BASE_PATH + "/", m.group(1)), html)


def main():
    pages = []
    for f in sorted(SRC.glob("*.html")):
        name = f.stem
        meta, body = parse(f.read_text())
        out = rebase(head(meta, name) + header(name) + render(body) + footer())
        target = ROOT / meta.get("out", f"{name}.html")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out)
        if meta.get("robots", "index,follow").startswith("index"):
            pages.append((meta.get("path", "/" if name == "index" else f"/{name}"), meta.get("priority", "0.6")))
        print("built", target.relative_to(ROOT))

    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>"
        for p, pr in pages
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    )
    icons = [{"src": f"{BASE_PATH}/assets/img/icon-{s}.png", "sizes": f"{s}x{s}", "type": "image/png"} for s in (192, 512)]
    (ROOT / "site.webmanifest").write_text(json.dumps({
        "name": SITE_NAME, "short_name": SITE_NAME, "start_url": f"{BASE_PATH}/",
        "display": "standalone", "background_color": "#07090d", "theme_color": "#07090d", "icons": icons}) + "\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("built sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
