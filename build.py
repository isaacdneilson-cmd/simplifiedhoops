#!/usr/bin/env python3
"""Builds the Simplified Hoops static site into ./dist.

To add a weekly article: add a file to posts/ (see existing ones for the header format),
then run:  python3 build.py
"""
import html, json, os, re, shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
SITE = "https://simplifiedhoops.com"

# ---- Business settings -------------------------------------------------------
BIZ = {
    "name": "Simplified Hoops",
    "coach": "Coach Isaac Neilson",
    "phone": "385-505-8374",
    "phone_href": "+13855058374",
    "email": "",  # add once the domain email exists, e.g. coach@simplifiedhoops.com
    "city": "Dallas, Texas",
    "instagram": "", "tiktok": "", "facebook": "", "youtube": "",
}
# Paste your Breely booking page link here once the account is set up.
# The Book page embeds it automatically and adds an "open in a new tab" link as a backup.
BOOKING_URL = "https://simplified-hoops.breely.com/form/25485"

# ---- Shared pieces -----------------------------------------------------------
LOGO = """<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="9" fill="#1D4ED8"/>
<circle cx="20" cy="20" r="11" fill="#F06A1F"/><path d="M9 20h22M20 9v22M12.5 12.5c4 4 4 11 0 15M27.5 12.5c-4 4-4 11 0 15" stroke="#0E1A2B" stroke-width="1.6" fill="none"/></svg>"""

NAV = [("index.html", "Home"), ("training.html", "Training & prices"),
       ("about.html", "About Coach Isaac"), ("blog/index.html", "Blog")]


def head(title, desc, depth, path, extra=""):
    pre = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{path}">
<link rel="icon" href="{pre}img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}css/site.css">
<!-- Google Ads / Analytics tag goes here -->
{extra}
</head>
<body>
"""


def header(depth, current):
    pre = "../" * depth
    links = "".join(
        f'<a href="{pre}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<header class="site-header"><div class="wrap">
<a class="brand" href="{pre}index.html">{LOGO}<span>Simplified Hoops</span></a>
<button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
<nav class="nav" id="nav" aria-label="Main">{links}<a class="btn btn-primary" href="{pre}book.html">Book training</a></nav>
</div></header>
<main>
"""


def footer(depth):
    pre = "../" * depth
    socials = [(k.title() if k != "tiktok" else "TikTok", v) for k, v in
               (("instagram", BIZ["instagram"]), ("tiktok", BIZ["tiktok"]),
                ("facebook", BIZ["facebook"]), ("youtube", BIZ["youtube"])) if v]
    social_html = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in socials) or \
        "<li>Follow along on social — links coming soon</li>"
    email = f'<li><a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></li>' if BIZ["email"] else ""
    return f"""</main>
<footer class="site-footer"><div class="wrap">
<div>
<a class="brand" href="{pre}index.html" style="color:#fff">{LOGO}<span>Simplified Hoops</span></a>
<p style="margin-top:16px;max-width:36ch">Private and small-group basketball training for youth and high school players in Dallas, with Coach Isaac Neilson.</p>
</div>
<div><h4>Contact</h4><ul>
<li><a href="tel:{BIZ['phone_href']}">{BIZ['phone']}</a></li>{email}
<li>Serving Dallas and nearby suburbs</li></ul></div>
<div><h4>Explore</h4><ul>
<li><a href="{pre}training.html">Training &amp; prices</a></li>
<li><a href="{pre}book.html">Book a session</a></li>
<li><a href="{pre}about.html">About Coach Isaac</a></li>
<li><a href="{pre}blog/index.html">Blog</a></li>
{social_html}</ul></div>
<p class="legal">© {date.today().year} Simplified Hoops. Training sessions in Dallas, Texas at YMCAs, recreation centers, parks and client homes.</p>
</div></footer>
<script>
(function(){{var b=document.querySelector('.nav-toggle'),n=document.getElementById('nav');
if(!b||!n)return;b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)}});}})();
</script>
</body></html>
"""


def page(path, title, desc, body, current=None, extra=""):
    depth = path.count("/")
    out = head(title, desc, depth, path if path != "index.html" else "", extra) + \
        header(depth, current or path) + body.replace("{pre}", "../" * depth) + footer(depth)
    dest = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f:
        f.write(out)


# ---- Blog posts --------------------------------------------------------------
def thumb(kind):
    """Small court diagrams used as article art (no photos needed)."""
    lane = '<rect x="110" y="0" width="100" height="120" fill="#16379C"/><path d="M0 0h320M110 0v120h100V0M160 120m-38 0a38 38 0 1 0 76 0a38 38 0 1 0-76 0" stroke="#fff" stroke-width="2.5" fill="none" opacity=".9"/><circle cx="160" cy="28" r="7" stroke="#F06A1F" stroke-width="3" fill="none"/>'
    marks = {
        "dropstep": '<circle cx="232" cy="62" r="11" fill="#F06A1F"/><path d="M226 74c-14 24-44 18-56-20" stroke="#fff" stroke-width="3.5" fill="none" stroke-dasharray="6 6"/><path d="M164 58l6-10 6 10" stroke="#fff" stroke-width="3.5" fill="none"/>',
        "defense": '<circle cx="236" cy="70" r="11" fill="#F06A1F"/><path d="M212 52l16 16M228 52l-16 16" stroke="#fff" stroke-width="4"/><path d="M290 150l-48-70" stroke="#fff" stroke-width="3" stroke-dasharray="5 6"/>',
        "iq": '<circle cx="60" cy="150" r="10" fill="#F06A1F"/><circle cx="260" cy="150" r="10" fill="#fff"/><circle cx="232" cy="64" r="10" fill="#fff"/><circle cx="88" cy="64" r="10" fill="#fff"/><path d="M72 146c60-30 120-30 176 0" stroke="#fff" stroke-width="3" fill="none" stroke-dasharray="5 6"/>',
    }
    return f'<svg viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="320" height="200" fill="#1D4ED8"/>{lane}{marks.get(kind, "")}</svg>'


def load_posts():
    posts = []
    pdir = os.path.join(ROOT, "posts")
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".html"):
            continue
        raw = open(os.path.join(pdir, fn)).read()
        meta_block, body = raw.split("\n---\n", 1)
        meta = dict(line.split(":", 1) for line in meta_block.strip().splitlines())
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        meta["body"] = body
        meta["slug"] = fn[:-5]
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def fmt_date(d):
    y, m, dd = map(int, d.split("-"))
    return date(y, m, dd).strftime("%B %-d, %Y")


def post_card(p, pre):
    return f"""<a class="post-card" href="{pre}blog/{p['slug']}.html">
<div class="thumb">{thumb(p.get('art', ''))}</div>
<p class="meta">{fmt_date(p['date'])} · {p.get('minutes', '5')} min read</p>
<h3>{p['title']}</h3><p>{p['summary']}</p></a>"""


# ---- Build -------------------------------------------------------------------
def build():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, "css"), os.path.join(DIST, "css"))
    shutil.copytree(os.path.join(ROOT, "img"), os.path.join(DIST, "img"))

    posts = load_posts()
    parts = {n: open(os.path.join(ROOT, "pages", n)).read() for n in os.listdir(os.path.join(ROOT, "pages"))}

    latest = "".join(post_card(p, "{pre}") for p in posts[:3])

    schema = {
        "@context": "https://schema.org", "@type": "SportsActivityLocation",
        "name": BIZ["name"], "url": SITE, "telephone": BIZ["phone"],
        "areaServed": "Dallas, TX", "priceRange": "$$",
        "description": "Private and small-group basketball training for youth and high school players: fundamentals, footwork, shooting, ball handling, post play, post defense and basketball IQ.",
        "founder": {"@type": "Person", "name": "Isaac Neilson"},
        "address": {"@type": "PostalAddress", "addressLocality": "Dallas", "addressRegion": "TX", "addressCountry": "US"},
    }
    ld = f'<script type="application/ld+json">{json.dumps(schema)}</script>'

    page("index.html", "Basketball Training in Dallas for Youth & High School | Simplified Hoops",
         "Private basketball training in Dallas with former D1 post player Coach Isaac Neilson. Fundamentals, footwork, shooting, post play and basketball IQ for youth and high school players.",
         parts["home.html"].replace("{latest}", latest), extra=ld)
    page("training.html", "Basketball Training Programs & Prices in Dallas | Simplified Hoops",
         "Private sessions $100/hour, 5- and 10-session packages, small-group training and a free player strategy call. Youth and high school basketball training in Dallas.",
         parts["training.html"])
    page("about.html", "About Coach Isaac Neilson | Simplified Hoops Dallas",
         "Coach Isaac Neilson played Division I basketball at BYU and Utah Valley, earned All-WAC Defensive Team honors, and has trained youth and high school players for over seven years.",
         parts["about.html"])

    if BOOKING_URL:
        booking = f'<div class="booking-frame"><iframe src="{BOOKING_URL}" title="Book with Simplified Hoops" loading="lazy"></iframe></div><p class="small" style="margin-top:12px">Calendar not loading? <a href="{BOOKING_URL}" target="_blank" rel="noopener">Open the booking page in a new tab</a>.</p>'
    else:
        booking = f'<div class="booking-frame"><div class="booking-placeholder"><h3>Online booking is coming soon</h3><p>The calendar will appear right here. Until then, call or text Coach Isaac at <a href="tel:{BIZ["phone_href"]}">{BIZ["phone"]}</a> to book a strategy call or session.</p></div></div>'
    page("book.html", "Book Basketball Training | Simplified Hoops Dallas",
         "Book a free player strategy call or a private basketball training session with Coach Isaac Neilson in Dallas.",
         parts["book.html"].replace("{booking}", booking))

    cards = "".join(post_card(p, "{pre}") for p in posts)
    page("blog/index.html", "Basketball Training Tips & Drills Blog | Simplified Hoops",
         "Weekly basketball tips for players and parents from Coach Isaac Neilson: post moves, defense, footwork, shooting and basketball IQ.",
         f"""<section class="page-head"><div class="wrap"><h1 class="display">The film room</h1>
<p class="lede">A new breakdown every week: one skill, explained simply, with what to practice at home.</p></div></section>
<section><div class="wrap"><div class="posts">{cards}</div></div></section>""",
         current="blog/index.html")

    for p in posts:
        art_ld = json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
                             "datePublished": p["date"], "author": {"@type": "Person", "name": "Isaac Neilson"},
                             "publisher": {"@type": "Organization", "name": BIZ["name"]}})
        body = f"""<header class="article-head"><div class="wrap">
<p class="meta"><a href="{{pre}}blog/index.html">Blog</a> · {fmt_date(p['date'])} · {p.get('minutes','5')} min read</p>
<h1>{p['title']}</h1><p class="lede">{p['summary']}</p></div></header>
<article class="article">{p['body']}</article>
<aside class="article-cta"><h3>Want Coach Isaac to break this down with your player?</h3>
<p>Start with a free 15-minute strategy call. We'll talk about your player's position, goals and what to work on first.</p>
<a class="btn btn-light" href="{{pre}}book.html">Book a free strategy call</a></aside>"""
        page(f"blog/{p['slug']}.html", f"{p['title']} | Simplified Hoops", p["summary"], body,
             current="blog/index.html", extra=f'<script type="application/ld+json">{art_ld}</script>')

    urls = ["", "training.html", "about.html", "book.html", "blog/index.html"] + [f"blog/{p['slug']}.html" for p in posts]
    with open(os.path.join(DIST, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                "".join(f"<url><loc>{SITE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(DIST, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"Built {len(urls)} pages into dist/")


if __name__ == "__main__":
    build()
