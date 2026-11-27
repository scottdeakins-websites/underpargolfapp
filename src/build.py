#!/usr/bin/env python3
"""Builds the Under Par Performance Golf static site into ../public.

Run:  python3 src/build.py
Content lives in src/content (Markdown with YAML front matter).
To change where every "Start" button goes, edit SIGNUP_URL below.
"""
import datetime, html, json, pathlib, re, shutil
import markdown, yaml

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "public"
SITE = "https://underpargolfapp.com"

# ---- Sign-up link (placeholder until the Mighty Forms sign-up page URL is ready) ----
SIGNUP_URL = "/pages/join-the-under-par-team-standard-monthly"
MONTHLY_URL = "/pages/join-the-under-par-team-standard-monthly"
ANNUAL_URL = "/pages/join-the-under-par-team-standard-annually"
PRICE = 39
ANNUAL_PRICE = 374
FULL_PRICE = 199
WAITLIST = "/pages/wait-list"
JOIN = "/pages/join-today"

CATEGORIES = {
    "the-blog": ("Practice", "Practice sessions and plans you can take straight to the range."),
    "full-swing-guide-from-scratch-golf": ("Full Swing", "Setup, ball flight and swing changes, explained plainly."),
    "short-game-improvement-guide": ("Short Game", "Chipping, pitching and bunker work that saves par."),
    "scratch-golfs-guide-to-putting": ("Putting", "Speed control, start line and putting games."),
    "playing-strategies-for-golfers": ("Strategy", "Course management: smarter targets, fewer big numbers."),
    "mindset": ("Mental Game", "Routines and habits that hold up under pressure."),
    "fitness-for-golfers": ("Fitness", "Strength and mobility for a faster, healthier swing."),
    "daily-mindset-2": ("Daily Mindset", "Short daily thoughts to keep your head in the game."),
    "golf-content": ("Features", "Podcasts, books and features from the Under Par team."),
}

NAV = [("Training", "/pages/resources"), ("Practice Plans", "/pages/sample-practice-plan"),
       ("Players", "/pages/player-testimonials"), ("Coaches", "/pages/coaches"), ("Blog", "/pages/blog")]

# Media still hosted on the Shopify store's CDN (move into the repo before closing Shopify)
SHOP = "https://cdn.shopify.com/s/files/1/0611/8208/3286/files/"
ART = "https://cdn.shopify.com/s/files/1/0611/8208/3286/articles/"
LOGO_IMG = (f'<img class="logo" src="{SHOP}Under_Par_Golf_-_Full_Logo.png?width=200" '
            f'srcset="{SHOP}Under_Par_Golf_-_Full_Logo.png?width=200 1x, {SHOP}Under_Par_Golf_-_Full_Logo.png?width=400 2x" '
            'alt="Under Par Performance Golf" width="180" height="46">')

# Every old Shopify blog URL (68). Ones not migrated yet redirect to their category hub.
OLD_POSTS = """the-blog/top-5-indoor-training-tools-for-your-christmas-list
mindset/setting-your-annual-golf-goals-the-do-s-and-don-ts
the-blog/how-to-introduce-a-kid-to-golf
the-blog/what-you-can-learn-from-a-pros-practice-routine
the-blog/learning-from-ben-hogans-practice-approach
mindset/work-ethic-a-common-character-trait-of-the-goats
mindset/jack-nicklaus-on-hard-work
mindset/bob-rotellas-guide-to-a-golfing-mindset
scratch-golfs-guide-to-putting/using-a-line-on-the-golf-ball-to-line-up-putts
playing-strategies-for-golfers/effectively-using-a-golf-range-finder
full-swing-guide-from-scratch-golf/practice-session-to-help-improve-your-club-head-control
full-swing-guide-from-scratch-golf/practice-session-to-dial-in-your-accuracy
playing-strategies-for-golfers/hit-more-drivers-off-the-tee-to-go-low
full-swing-guide-from-scratch-golf/improving-your-wedge-play-to-lower-your-golf-scores
mindset/3-things-to-focus-on-to-build-a-positive-mindset-for-your-next-round
mindset/bobby-jones-work-and-suffer-and-wait-for-fate
scratch-golfs-guide-to-putting/putting-practice-session-for-you-to-try-out
short-game-improvement-guide/short-game-practice-session-to-help-you-save-par
short-game-improvement-guide/getting-it-up-and-down-to-lower-your-scores
short-game-improvement-guide/pressure-cooker-short-game-practice
scratch-golfs-guide-to-putting/holing-putts-a-practice-session-to-help-you-roll-em-in
playing-strategies-for-golfers/a-65-sand-save-rate-would-put-you-at-1-on-the-pga-tour
the-blog/3-ways-to-improve-your-focus-when-practicing
mindset/5-things-i-learned-working-with-a-sports-psychologist
the-blog/watch-out-for-these-signs-that-you-need-a-golf-practice-plan
the-blog/best-1-hour-golf-practice-session
playing-strategies-for-golfers/tracking-golf-stats-a-great-way-to-improve-your-game
playing-strategies-for-golfers/5-ways-to-optimize-your-practice-rounds
golf-content/wicked-smart-golf-play-better-without-swing-changes-5-strategies
mindset/understanding-tigers-pre-shot-routine-how-to-get-in-the-zone
playing-strategies-for-golfers/how-to-manage-your-game-like-a-pga-player
playing-strategies-for-golfers/warmup-session-strategy
mindset/the-post-shot-routine-learning-from-happy-gilmore-and-shooter-mcgavin
scratch-golfs-guide-to-putting/will-zalatoris-good-or-bad-putter
playing-strategies-for-golfers/3-quick-tips-to-optimizing-angles-off-the-tee
mindset/7-ways-to-break-out-of-a-golf-slump
playing-strategies-for-golfers/10-tournament-golf-tips-to-play-your-best-golf-under-pressure
full-swing-guide-from-scratch-golf/master-the-art-of-hitting-absolute-bombs
full-swing-guide-from-scratch-golf/building-a-yardage-guide
full-swing-guide-from-scratch-golf/how-to-manage-wedge-distances-like-a-pro
full-swing-guide-from-scratch-golf/the-art-of-making-swing-changes
the-blog/you-are-wasting-your-time-practicing
playing-strategies-for-golfers/5-keys-to-scoring
playing-strategies-for-golfers/intermediate-target-alignment-get-aligned-correctly-for-every-shot
mindset/why-you-need-to-speed-up-your-pre-shot-routine
mindset/how-to-manage-a-bad-ball-striking-day-on-the-golf-course
short-game-improvement-guide/building-a-pre-shot-routine-for-your-short-game
playing-strategies-for-golfers/how-to-choose-the-right-golf-tournaments-for-your-next-golf-season
the-blog/3-strategies-to-maximize-your-golf-simulator-practice
playing-strategies-for-golfers/why-pga-tour-golfers-turn-to-statisticians-for-a-lower-score
full-swing-guide-from-scratch-golf/the-great-waggle-debate-does-wiggling-your-club-improve-your-golf-game
mindset/4-keys-to-achieving-your-golf-goals
full-swing-guide-from-scratch-golf/3-steps-to-building-a-fairway-finder-off-the-tee
full-swing-guide-from-scratch-golf/the-art-of-hitting-flighted-wedges
the-blog/practice-tip-practice-from-bad-lies
mindset/a-simple-blueprint-for-your-pre-shot-routine
the-blog/sample-practice-session-target-challenge
the-blog/sample-practice-session-landing-zone
the-blog/sample-practice-session-saucy-wedges
the-blog/sample-practice-session-putting-speed-control
fitness-for-golfers/5-muscle-groups-to-focus-on-to-maximize-your-golf-fitness
full-swing-guide-from-scratch-golf/how-to-read-the-data-from-your-golf-launch-monitor
daily-mindset-2/rory-mcilroy-on-the-journey
daily-mindset-2/aristotle-on-excellence
fitness-for-golfers/distance-builder
daily-mindset-2/koepka-on-high-highs-and-low-lows
full-swing-guide-from-scratch-golf/the-fundamentals-of-ball-position
playing-strategies-for-golfers/mastering-the-fade-and-draw-the-basics-for-hitting-different-shot-shapes-in-golf""".split()

LOGO = ('<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="12.5" '
        'fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M10.5 20V7.5l8.5 3.8-8.5 3.8" fill="none" '
        'stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/></svg>')


def esc(s):
    return html.escape(str(s), quote=True)


def load(folder):
    items = []
    for f in sorted((ROOT / "content" / folder).glob("*.md")):
        raw = f.read_text()
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm)
        meta["html"] = body if meta.get("raw") else markdown.markdown(body, extensions=["tables", "attr_list", "md_in_html"])
        meta["words"] = len(re.sub(r"<[^>]+>", " ", meta["html"]).split())
        items.append(meta)
    return items


def head(title, desc, path, schema, og_type="website", image=None):
    url = SITE + (path if path == "/" else path)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Under Par Performance Golf">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{esc(image or SHOP + 'Under_Par_Screen_Shot.webp?width=1200')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@UnderParCoach">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(path):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if path.startswith(h) else ""}>{t}</a>' for t, h in NAV)
    return f"""<header class="site-head">
<div class="wrap head-row">
<a class="brand" href="/">{LOGO_IMG}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open Menu"><span></span><span></span><span></span></button>
<nav class="nav" id="site-nav" aria-label="Main">{links}<a class="btn nav-cta" href="{JOIN}">Get Started</a></nav>
</div>
<script>
(function(){{var b=document.querySelector('.menu-btn'),n=document.getElementById('site-nav');
b.addEventListener('click',function(){{var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!o));b.setAttribute('aria-label',o?'Open Menu':'Close Menu');n.classList.toggle('open',!o);document.body.classList.toggle('menu-open',!o);}});}})();
</script>
</header>
<main id="main">
"""


def cta_band(heading="Ready to <em>Go Low?</em>", text=None):
    text = text or (f"Structured practice and golf fitness plans in the Under Par app, from ${PRICE} a month. "
                    f"Want a personal coach? Full Access coaching (${FULL_PRICE}/month) is currently full, so join the waitlist.")
    return f"""<section class="cta-band">
<div class="wrap">
<h2>{heading}</h2>
<p>{text}</p>
<div class="hero-actions" style="justify-content:center"><a class="btn" href="{JOIN}">Get Started</a><a class="btn btn-ghost" href="{WAITLIST}">Join the Coaching Waitlist</a></div>
</div>
</section>
"""


SOCIAL = [("Facebook", "https://www.facebook.com/Under-Par-Performance-Golf-102095152341941",
           '<path d="M14 8h3V4h-3c-2.8 0-5 2.2-5 5v2H7v4h2v9h4v-9h3l1-4h-4V9c0-.6.4-1 1-1z"/>'),
          ("X (Twitter)", "https://twitter.com/UnderParCoach",
           '<path d="M17.8 3h3.3l-7.2 8.2L22.4 21h-6.6l-5.2-6.8L4.6 21H1.3l7.7-8.8L1 3h6.8l4.7 6.2L17.8 3zm-1.2 16h1.8L7.3 4.9H5.4L16.6 19z"/>'),
          ("LinkedIn", "https://www.linkedin.com/company/78333110/",
           '<path d="M4.98 3.5a2.5 2.5 0 11-.01 5 2.5 2.5 0 01.01-5zM3 9h4v12H3zM9 9h3.8v1.7h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.6c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9V21H9z"/>')]


def footer():
    cats = "".join(f'<a href="/blogs/{k}">{v[0]}</a>' for k, v in CATEGORIES.items())
    return f"""</main>
<footer class="site-foot">
<div class="wrap foot-grid">
<div class="foot-brand"><a class="brand" href="/">{LOGO_IMG}</a>
<p>Golf practice and fitness plans in the Under Par app, plus Full Access coaching for players who want a coach in their corner.</p>
<p>121 N. Wayne Avenue, Suite 201<br>Wayne, PA 19087<br><a href="mailto:team@underpargolfapp.com">team@underpargolfapp.com</a></p>
<div class="social">{"".join(f'<a href="{u}" aria-label="{n}" rel="noopener"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">{p}</svg></a>' for n, u, p in SOCIAL)}</div></div>
<div><h3>Coaching</h3><a href="/pages/practice-plan">Practice Plan</a><a href="/pages/workout">Golf Workouts</a><a href="/pages/swing-coaching">Swing Coaching</a><a href="/pages/playing-strategies">Playing Strategy</a><a href="/pages/mindset-coaching">Mindset Coaching</a><a href="/pages/app-guide">The App</a></div>
<div><h3>Learn</h3>{cats}<a href="/pages/download">Free Practice Sessions</a></div>
<div><h3>Company</h3><a href="/pages/our-mission">Our Mission</a><a href="/pages/coaches">Coaches</a><a href="/pages/player-testimonials">Players</a><a href="/pages/contact-us">Contact</a></div>
</div>
<div class="wrap foot-legal"><span>© {datetime.date.today().year} Scratch Golf, Inc. d/b/a Under Par</span><a href="/policies/privacy-policy">Privacy Policy</a><a href="/policies/terms-of-service">Terms of Service</a></div>
</footer>
</body>
</html>
"""


ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "Under Par Performance Golf", "url": SITE + "/",
       "email": "team@underpargolfapp.com",
       "address": {"@type": "PostalAddress", "streetAddress": "121 N. Wayne Avenue, Suite 201",
                   "addressLocality": "Wayne", "addressRegion": "PA", "postalCode": "19087",
                   "addressCountry": "US"},
       "sameAs": ["https://twitter.com/UnderParCoach",
                  "https://www.facebook.com/Under-Par-Performance-Golf-102095152341941"]}
SERVICE = {"@type": "Service", "name": "Under Par golf practice and fitness plans", "serviceType": "Online golf practice and fitness plans",
           "provider": {"@id": SITE + "/#org"}, "areaServed": "Worldwide",
           "offers": [
               {"@type": "Offer", "name": "App plan, monthly", "price": str(PRICE), "priceCurrency": "USD",
                "description": "Online practice and fitness plans in the Under Par app, billed monthly"},
               {"@type": "Offer", "name": "App plan, annual", "price": str(ANNUAL_PRICE), "priceCurrency": "USD",
                "description": "Online practice and fitness plans in the Under Par app, billed yearly"},
               {"@type": "Offer", "name": "Full Access coaching", "price": str(FULL_PRICE), "priceCurrency": "USD",
                "availability": "https://schema.org/OutOfStock",
                "description": "Personal coaching plus practice and fitness plans. Currently full; waitlist open."}]}


def crumbs(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(trail)]}


def write(path, doc):
    target = OUT / ("index.html" if path == "/" else path.strip("/") + "/index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc)


FULL_NOTE = (f'<div class="callout full-note"><p><strong>Personal coaching is part of Full Access, our full monthly coaching plan (${FULL_PRICE}/month) with unlimited reviews from your coach. It is currently full.</strong> The ${PRICE}/month app plan includes the online practice and fitness plans, '
             f'not access to a coach. <a href="{WAITLIST}">Join the Full Access waitlist</a>.</p></div>')


def render(text):
    return (text.replace("{{JOIN}}", JOIN).replace("{{PRICE}}", str(PRICE))
            .replace("{{SIGNUP_URL}}", SIGNUP_URL).replace("{{MONTHLY_URL}}", MONTHLY_URL)
            .replace("{{ANNUAL_URL}}", ANNUAL_URL).replace("{{ANNUAL_PRICE}}", str(ANNUAL_PRICE))
            .replace("{{FULL_PRICE}}", str(FULL_PRICE)).replace("{{WAITLIST}}", WAITLIST)
            .replace("{{FULL_ACCESS}}", FULL_NOTE).replace("{{CDN}}", SHOP).replace("{{ART}}", ART))


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    pages, posts = load("pages"), load("posts")
    posts.sort(key=lambda p: str(p["date"]), reverse=True)
    for key in [k for k in CATEGORIES if not any(x["category"] == k for x in posts)]:
        del CATEGORIES[key]
    sitemap = []

    def card(p):
        cat = CATEGORIES[p["category"]][0]
        thumb = f'<img class="thumb" src="{esc(p["image"])}" alt="" loading="lazy">' if p.get("image") else ""
        return (f'<a class="post-card" href="{p["path"]}">{thumb}<span class="kicker">{cat}</span>'
                f'<h3>{esc(p["title"])}</h3><p>{esc(p["description"])}</p>'
                f'<span class="meta">{max(2, round(p["words"] / 230))} min read</span></a>')

    # Pages
    for p in pages:
        trail = [("Home", "/")] + ([(p["crumb"], p["path"])] if p["path"] != "/" else [])
        schema = {"@context": "https://schema.org", "@graph": [ORG, SERVICE, crumbs(trail)] + p.get("schema", [])}
        body = render(p["html"])
        if p.get("featured"):
            picks = [x for f in p["featured"] for x in posts if x["path"] == f]
            body = body.replace("<!--LATEST-->", '<div class="post-grid">' + "".join(card(x) for x in picks) + "</div>")
        if p["path"] == "/pages/blog":
            groups = []
            for key, (name, blurb) in CATEGORIES.items():
                items = [x for x in posts if x["category"] == key]
                if items:
                    groups.append(f'<section class="cat-block"><div class="cat-head"><h2><a href="/blogs/{key}">{name}</a></h2>'
                                  f'<p>{blurb}</p></div><div class="post-grid">{"".join(card(x) for x in items)}</div></section>')
            body = body.replace("<!--BLOG-->", "".join(groups))
        doc = head(p["title"], p["description"], p["path"], schema) + header(p["path"])
        doc += body if p.get("raw") else f'<article class="wrap page prose">{body}</article>'
        if not p.get("no_cta"):
            doc += cta_band()
        write(p["path"], doc + footer())
        sitemap.append(p["path"])

    # Category hubs
    for key, (name, blurb) in CATEGORIES.items():
        items = [x for x in posts if x["category"] == key]
        path = f"/blogs/{key}"
        schema = {"@context": "https://schema.org", "@graph": [ORG, crumbs([("Home", "/"), ("Blog", "/pages/blog"), (name, path)])]}
        doc = head(f"{name} tips and drills | Under Par Performance Golf", blurb, path, schema) + header("/pages/blog")
        doc += (f'<section class="wrap page"><p class="crumbs"><a href="/pages/blog">Blog</a> / {name}</p>'
                f'<h1>{name}</h1><p class="lede">{blurb}</p><div class="post-grid">{"".join(card(x) for x in items)}</div></section>')
        write(path, doc + cta_band() + footer())
        sitemap.append(path)

    # Posts
    for p in posts:
        name = CATEGORIES[p["category"]][0]
        trail = [("Home", "/"), ("Blog", "/pages/blog"), (name, f"/blogs/{p['category']}"), (p["title"], p["path"])]
        art = {"@type": "BlogPosting", "headline": p["title"], **({"image": p["image"]} if p.get("image") else {}), "description": p["description"],
               "datePublished": str(p["date"]), "dateModified": str(p["updated"]),
               "author": {"@type": "Organization", "name": "Under Par Coaching Team", "url": SITE + "/pages/coaches"},
               "publisher": {"@id": SITE + "/#org"}, "mainEntityOfPage": SITE + p["path"]}
        graph = [ORG, art, crumbs(trail)]
        if p.get("faq"):
            graph.append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"].items()]})
        related = [x for x in posts if x is not p and x["category"] == p["category"]][:2]
        related += [x for x in posts if x is not p and x not in related and x["category"] in p.get("related", [])][: 3 - len(related)]
        faq_html = ""
        if p.get("faq"):
            faq_html = '<h2>Common questions</h2>' + "".join(
                f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in p["faq"].items())
        updated = datetime.date.fromisoformat(str(p["updated"])).strftime("%B %-d, %Y")
        doc = head(p.get("seo_title", p["title"] + " | Under Par Golf"), p["description"], p["path"],
                   {"@context": "https://schema.org", "@graph": graph}, "article", p.get("image")) + header("/pages/blog")
        doc += f"""<article class="wrap post">
<p class="crumbs"><a href="/pages/blog">Blog</a> / <a href="/blogs/{p['category']}">{name}</a></p>
<h1>{esc(p['title'])}</h1>
{f'<img class="post-hero" src="{esc(p["image"])}" alt="{esc(p.get("image_alt", p["title"]))}">' if p.get("image") else ""}
<p class="post-meta">Under Par Coaching Team · Updated <time datetime="{p['updated']}">{updated}</time> · {max(2, round(p['words'] / 230))} min read</p>
<div class="prose">{render(p['html'])}{faq_html}</div>
<aside class="coach-note"><h2>Want sessions like this every week?</h2>
<p>The Under Par app gives you structured practice and golf fitness plans with video drills and results tracking, from ${PRICE} a month. Personal coaching is our Full Access plan (${FULL_PRICE}/month), currently full with a waitlist.</p>
<a class="btn" href="{JOIN}">See Plans</a></aside>
</article>
<section class="wrap related"><h2>Keep reading</h2><div class="post-grid">{"".join(card(x) for x in related)}</div></section>
"""
        write(p["path"], doc + footer())
        sitemap.append(p["path"])

    # 404
    (OUT / "404.html").write_text(head("Page not found | Under Par Performance Golf", "Page not found.", "/404", {"@context": "https://schema.org", "@graph": [ORG]})
                                  + header("") + '<section class="wrap page"><h1>That page went out of bounds.</h1>'
                                  '<p class="lede">Try the <a href="/pages/blog">blog</a>, the <a href="/pages/sample-practice-plan">free practice plan</a>, or head <a href="/">home</a>.</p></section>' + footer())

    # Redirects
    migrated = {p["path"] for p in posts}
    lines = ["# Old Shopify URLs", "/pages/reviews  /pages/player-testimonials  301",
             "/pages/training  /pages/resources  301", "/blogs  /pages/blog  301", "/blog  /pages/blog  301",
             f"/account  {JOIN}  302", f"/cart  {JOIN}  302", f"/collections/*  {JOIN}  302", f"/products/*  {JOIN}  302",
             "", "# Posts not migrated yet: send to their topic page (302 until migrated)"]
    for old in OLD_POSTS:
        path = "/blogs/" + old
        cat = old.split("/")[0]
        if path not in migrated:
            lines.append(f"{path}  {'/blogs/' + cat if cat in CATEGORIES else '/pages/blog'}  302")
    for cat in ["daily-mindset-2", "golf-content", "scratch-golfs-guide-to-putting", "short-game-improvement-guide", "mindset", "the-blog", "full-swing-guide-from-scratch-golf", "playing-strategies-for-golfers"]:
        if cat in CATEGORIES:
            continue
        lines.append(f"/blogs/{cat}  /pages/blog  302")
    (OUT / "_redirects").write_text("\n".join(lines) + "\n")

    today = datetime.date.today().isoformat()
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{SITE}{'' if u == '/' else u}</loc><lastmod>{today}</lastmod></url>\n" for u in sitemap) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /404\n\nSitemap: {SITE}/sitemap.xml\n")
    print(f"Built {len(pages)} pages, {len(CATEGORIES)} topic hubs, {len(posts)} posts -> {OUT}")


if __name__ == "__main__":
    build()
