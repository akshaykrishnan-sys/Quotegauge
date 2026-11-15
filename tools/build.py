"""Builds index.html, guides/*.html and sitemap.xml from src/, lib/core.js and tools/content.py.
Run: python3 tools/build.py
Optional photo: put img/hero.jpg and img/hero.txt (one line describing the photo) in the project."""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from content import AAA_URL, FAQ, GUIDES, PROOF, PROOF_SOURCE  # noqa: E402

SITE = "https://quotegauge.example"
TODAY = "2026-11-15"
PRODUCT_NAME = {"check": "Repair Quote Checker", "compare": "Repair Quote Comparator", "need": "Repair Necessity Checker"}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@400;500;600&family=Caveat:wght@700&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">')
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "QuoteGauge", "url": SITE + "/",
       "description": "QuoteGauge checks car repair estimates against typical local prices so drivers know what is fair before approving work."}

e = lambda s: html.escape(s, quote=False)
read = lambda p: (ROOT / p).read_text()
css = read("src/style.css")


def faq_ld(pairs, ident):
    return {"@type": "FAQPage", "@id": ident,
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}


def faq_html(pairs, indent="      "):
    rows = "\n".join("%s  <details%s><summary>%s</summary><p>%s</p></details>" % (indent, " open" if i == 0 else "", e(q), e(a))
                     for i, (q, a) in enumerate(pairs))
    return '<div class="faq">\n' + rows + "\n" + indent + "</div>"


def head(title, desc, url, graph, og_title):
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="QuoteGauge">
<meta property="og:title" content="{html.escape(og_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%23ffd60a'/%3E%3Ccircle cx='32' cy='32' r='20' fill='%23111'/%3E%3Cpath d='M32 32 L43 17' stroke='%23ffd60a' stroke-width='6' stroke-linecap='round'/%3E%3C/svg%3E">
<meta name="theme-color" content="#ffd60a">
{FONTS}
<script type="application/ld+json">
{ld}
</script>
<style>
{css}</style>
</head>
<body>
"""


# ---------- Home page ----------
proof = ('<section id="proof" class="proof-sec" aria-labelledby="proof-title">\n    <div class="wrap">\n'
         '      <div class="sec-head"><h2 id="proof-title">You\'re not being paranoid.</h2><p>Most drivers feel the same way at the service counter.</p></div>\n'
         '      <div class="stats">\n'
         + "\n".join('        <div class="stat-card"><b>%s</b><p>%s</p></div>' % (e(n), e(t)) for n, t in PROOF)
         + '\n      </div>\n      <p class="cite">Source: <a href="%s" rel="noopener">%s</a>.</p>\n    </div>\n  </section>' % (AAA_URL, e(PROOF_SOURCE)))

guides_list = ('<div class="guide-list">\n'
               + "\n".join('        <a href="guides/%s.html"><span>%s</span><span aria-hidden="true">→</span></a>' % (g["slug"], e(g["title"])) for g in GUIDES)
               + "\n      </div>")

# Optional photos: img/hero.jpg, check.jpg, compare.jpg, need.jpg, founder.jpg, described in img/photos.json:
# {"hero": "what the photo shows", "check": "...", "founder": {"alt": "...", "name": "...", "quote": "..."}}
meta = json.loads(read("img/photos.json")) if (ROOT / "img/photos.json").exists() else {}
has = lambda k: (ROOT / "img" / (k + ".jpg")).exists() and k in meta
hero_vis = ""
if has("hero"):
    hero_vis = ('<div class="shot"><img src="img/hero.jpg" alt="%s" width="1280" height="1024">'
                '<div class="chip c1" aria-hidden="true"><i class="fair"></i>Brake pads + rotors · $689 · fair</div>'
                '<div class="chip c2" aria-hidden="true"><i class="above"></i>Brake fluid flush · $179 · above market</div>'
                '<div class="chip c3" aria-hidden="true"><i class="verify"></i>Fuel system cleaning · ask why</div>'
                '<p class="paper-note">Example labels with illustrative figures.</p></div>') % html.escape(meta["hero"])
card_img = {k: ('<img src="img/%s.jpg" alt="%s" width="900" height="600">' % (k, html.escape(meta[k])) if has(k) else "") for k in ("check", "compare", "need")}
founder = ""
if has("founder"):
    f = meta["founder"]
    founder = ('<section class="founder" aria-label="Who built this"><div class="wrap"><img src="img/founder.jpg" alt="%s" loading="lazy">'
               '<blockquote>%s<cite>%s</cite></blockquote></div></section>' % (html.escape(f["alt"]), e(f["quote"]), e(f["name"])))

home_graph = [
    ORG,
    {"@type": "WebApplication", "@id": SITE + "/#app", "name": "QuoteGauge", "url": SITE + "/",
     "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any (web browser)",
     "description": "Three web tools for car owners in the United States: a repair quote checker, a repair quote comparator and a repair necessity checker.",
     "publisher": {"@id": SITE + "/#org"},
     "offers": [
         {"@type": "Offer", "name": "Free first answer", "price": "0", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Repair Quote Checker full report", "price": "4.99", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Repair Necessity Checker full report", "price": "9.99", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Repair Quote Comparator full report", "price": "14.99", "priceCurrency": "USD"},
     ]},
    faq_ld(FAQ, SITE + "/#faq"),
]
home_desc = ("Check a car repair estimate before you approve it. QuoteGauge prices every line for your car and area, "
             "compares estimates from different shops, and tells you which recommended repairs are urgent. Free first answer.")
body = (read("src/body.html").replace("%%FAQ%%", faq_html(FAQ)).replace("%%PROOF%%", proof)
        .replace("%%GUIDES%%", guides_list).replace("%%HEROVIS%%", hero_vis).replace("%%FOUNDER%%", founder))
for k, v in card_img.items():
    body = body.replace("%%IMG_" + k + "%%", v)
home = (head("Is My Car Repair Quote Fair? Check, Compare, Verify | QuoteGauge", home_desc, SITE + "/", home_graph,
             "Don't sign that repair estimate yet")
        + "\n" + body + "\n<script>\n" + read("lib/core.js") + "</script>\n<script>\n" + read("src/app.js") + "</script>\n</body>\n</html>\n")
(ROOT / "index.html").write_text(home)

# ---------- Guides ----------
(ROOT / "guides").mkdir(exist_ok=True)


def blocks(items):
    out = []
    for it in items:
        if isinstance(it, list):
            out.append("<ul>" + "".join("<li>%s</li>" % e(x) for x in it) + "</ul>")
        else:
            out.append("<p>%s</p>" % e(it).replace("(AAA, 2016)", '(<a href="%s" rel="noopener">AAA, 2016</a>)' % AAA_URL))
    return "\n      ".join(out)


for g in GUIDES:
    url = "%s/guides/%s" % (SITE, g["slug"])
    graph = [
        ORG,
        {"@type": "Article", "@id": url + "#article", "headline": g["title"], "description": g["desc"],
         "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": url,
         "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "QuoteGauge", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": g["title"], "item": url}]},
        faq_ld(g["faq"], url + "#faq"),
    ]
    others = "".join('<a href="%s.html"><span>%s</span><span aria-hidden="true">→</span></a>' % (o["slug"], e(o["title"])) for o in GUIDES if o is not g)
    sections = "\n".join('    <h2>%s</h2>\n      %s' % (e(h), blocks(items)) for h, items in g["sections"])
    page = head(g["title"] + " | QuoteGauge", g["desc"], url, graph, g["title"]) + f"""
<header class="top">
  <div class="wrap">
    <a class="logo" href="../index.html" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
    <nav class="nav" aria-label="Main"><a class="btn keep" style="font-size:19px;padding:9px 16px" href="../index.html#{g["product"]}">{e(g["cta"])}</a></nav>
  </div>
</header>
<main>
  <article class="article">
    <p class="crumbs"><a href="../index.html">QuoteGauge</a> / Guides</p>
    <h1>{e(g["title"])}</h1>
    <p class="answer">{e(g["answer"])}</p>
{sections}
    <div class="cta-box">
      <h3>Want this done for you?</h3>
      <p>The {PRODUCT_NAME[g["product"]]} does this in about a minute. The first answer is free.</p>
      <a class="btn" href="../index.html#{g["product"]}">{e(g["cta"])}</a>
    </div>
    <h2>Common questions</h2>
    {faq_html(g["faq"], "    ")}
    <h2>More guides</h2>
    <div class="guide-list one">{others}</div>
    <p class="fine" style="margin-top:28px">General information, not professional mechanical advice. Updated {TODAY}.</p>
  </article>
</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot-row">
      <a class="logo" href="../index.html" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
      <div class="foot-links"><a href="../privacy.html">Privacy</a><a href="../terms.html">Terms</a><a href="../refunds.html">Refunds</a></div>
    </div>
    <p class="small">© 2026 QuoteGauge. Not affiliated with any repair shop, dealership or vehicle manufacturer.</p>
  </div>
</footer>
</body>
</html>
"""
    (ROOT / "guides" / (g["slug"] + ".html")).write_text(page)

# ---------- Sitemap ----------
urls = [(SITE + "/", "1.0")] + [("%s/guides/%s" % (SITE, g["slug"]), "0.8") for g in GUIDES] + [(SITE + "/" + p, "0.2") for p in ("privacy", "terms", "refunds")]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (u, TODAY, p) for u, p in urls)
                                  + "</urlset>\n")
print("built index.html (%d bytes), %d guides, sitemap with %d urls, photos: %s" % (len(home), len(GUIDES), len(urls), ", ".join(k for k in ("hero", "check", "compare", "need", "founder") if has(k)) or "none"))
