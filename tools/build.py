"""Builds index.html, guides/*.html and sitemap.xml from src/, lib/core.js and tools/content.py.
Run: python3 tools/build.py
Optional photo: put img/hero.jpg and img/hero.txt (one line describing the photo) in the project."""
import re
import html
import json
import sys as _s; _s.path.insert(0, __import__("os").path.dirname(__file__))
from press import press_html, PRESS_CSS
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from costs import COSTS, LABOR_NOTE
from metros import METROS, NATIONAL, BLS_DATE  # noqa: E402
from content import AAA_URL, FAQ, GUIDES, PROOF, PROOF_SOURCE, RECEIPTS, REVIEWS  # noqa: E402

SITE = "https://quotegauge.pro"
TODAY = "2026-11-15"
PRODUCT_NAME = {"check": "Repair Quote Checker", "compare": "Repair Quote Comparator", "need": "Repair Necessity Checker", "any": "Any Quote Checker"}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Caveat:wght@700&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">')
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "QuoteGauge", "url": SITE + "/",
       "description": "QuoteGauge checks car repair, home repair and contractor quotes against typical local prices so people know what is fair before approving work.",
       "email": "hello@quotegauge.pro",
       "founder": {"@type": "Person", "name": "Akshay Krishnan"},
       "address": {"@type": "PostalAddress", "addressLocality": "Bengaluru", "addressCountry": "IN"},
       "areaServed": "US"}

e = lambda s: html.escape(s, quote=False)
read = lambda p: (ROOT / p).read_text()
css = read("src/style.css")
import hashlib as _h
ASSET_V = _h.sha1((css + read("lib/core.js") + read("src/app.js")).encode()).hexdigest()[:8]
(ROOT / "assets").mkdir(exist_ok=True)
(ROOT / "assets" / "site.css").write_text(css)
(ROOT / "assets" / "core.js").write_text(read("lib/core.js"))
(ROOT / "assets" / "app.js").write_text(read("src/app.js"))


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
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#0f3b2e">
{FONTS}
<script type="application/ld+json">
{ld}
</script>
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">
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
               + '\n        <a href="/repair-costs"><span>Repair and home job costs: 20 fair-price guides</span><span aria-hidden="true">→</span></a>'
               + "\n      </div>")

# Optional photos: img/hero.jpg, check.jpg, compare.jpg, need.jpg, founder.jpg, described in img/photos.json:
# {"hero": "what the photo shows", "check": "...", "founder": {"alt": "...", "name": "...", "quote": "..."}}
meta = json.loads(read("img/photos.json")) if (ROOT / "img/photos.json").exists() else {}
has = lambda k: (ROOT / "img" / (k + ".jpg")).exists() and k in meta
hero_vis = (
    '<figure class="demo" aria-label="Example: a repair estimate checked by QuoteGauge">'
    '<div class="est-paper">'
    '<div class="est-head"><b>Riverside Auto Service</b><span>Estimate 20418</span></div>'
    '<p class="est-car">2017 Honda Accord, 84,210 mi</p>'
    '<ol class="est-lines">'
    '<li class="ok" style="--d:0"><span class="it">Front brake pads and rotors</span><span class="pr">689.00</span><em>fair for this car</em></li>'
    '<li class="hi" style="--d:1"><span class="it">Brake fluid flush</span><span class="pr">179.00</span><em>usually $100&ndash;150</em></li>'
    '<li class="hi" style="--d:2"><span class="it">Cabin air filter</span><span class="pr">119.00</span><em>usually $55&ndash;90</em></li>'
    '<li class="ask" style="--d:3"><span class="it">Fuel system cleaning</span><span class="pr">229.00</span><em>ask why your car needs this</em></li>'
    '<li class="ok" style="--d:4"><span class="it">Shop supplies</span><span class="pr">45.00</span><em>fair</em></li>'
    '</ol>'
    '<div class="est-total"><span>Total</span><span>$1,261.00</span></div>'
    '</div>'
    '<div class="rep">'
    '<p class="rep-k">Your QuoteGauge result</p>'
    '<p class="rep-amt"><b>$287</b> worth asking about before you sign</p>'
    '<ul class="rep-list">'
    '<li class="ok"><span>2 lines fair</span><span>$734</span></li>'
    '<li class="hi"><span>2 lines above market</span><span>$298</span></li>'
    '<li class="ask"><span>1 line to question</span><span>$229</span></li>'
    '</ul>'
    '<div class="rep-say"><p>What to say</p><q>Before I approve this, can you walk me through the brake fluid flush, the cabin filter and the fuel cleaning? I&rsquo;m seeing lower prices for this car.</q></div>'
    '</div>'
    '<figcaption>Example estimate with illustrative figures.</figcaption>'
    '</figure>')
card_img = {k: ('<img src="img/%s.jpg" alt="%s" width="900" height="600" loading="lazy" decoding="async">' % (k, html.escape(meta[k])) if has(k) else "") for k in ("check", "compare", "need", "any")}
receipts = ('<section class="receipts" id="real-quotes" aria-labelledby="receipts-title"><div class="wrap">'
            '<div class="sec-head"><h2 id="receipts-title">Real quotes, reported in the press.</h2>'
            '<p>Two in three US drivers say they don&rsquo;t trust repair shops, according to <a href="%s" rel="noopener" target="_blank">AAA</a>. These are the quotes behind that number. None of these people had QuoteGauge.</p></div>'
            '<ol class="ledger">' % AAA_URL
            + "".join('<li><b>%s</b><p>%s</p><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (e(n), e(t), u, e(src)) for n, t, src, u in RECEIPTS)
            + '</ol><p class="ledger-note">Most shops and contractors are honest. The quote still deserves a second look.</p></div></section>')
face = ""
if has("face"):
    face = ('<section class="face-sec" aria-labelledby="face-title"><div class="wrap">'
            '<div class="sec-head"><h2 id="face-title">You know this face.</h2><p>It&rsquo;s the &ldquo;we also found a few things&rdquo; face.</p></div>'
            '<figure class="face"><img src="img/face.jpg" alt="%s" width="1280" height="720" loading="lazy" decoding="async">'
                        '<figcaption class="cap c-right">&ldquo;&hellip;we also found a few things.&rdquo;</figcaption></figure>'
            '<div class="face-foot"><p>QuoteGauge wipes that look off your face. Upload the list, see which &ldquo;few things&rdquo; are real and which are padded, and walk back to the counter knowing exactly what to say. <b>Before</b> you sign.</p>'
            '<a class="btn" href="#tool" data-start="check">Fix my face. It&rsquo;s free</a></div></div></section>') % html.escape(meta["face"])
founder = ""
if has("founder"):
    f = meta["founder"]
    founder = ('<section class="founder" aria-label="Who built this"><div class="wrap"><img src="img/founder.jpg" alt="%s" loading="lazy">'
               '<blockquote>%s<cite>%s</cite></blockquote></div></section>' % (html.escape(f["alt"]), e(f["quote"]), e(f["name"])))

home_graph = [
    ORG,
    {"@type": "WebApplication", "@id": SITE + "/#app", "name": "QuoteGauge", "url": SITE + "/",
     "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any (web browser)",
     "description": "Four web tools for consumers in the United States: a repair quote checker, a repair quote comparator, a repair necessity checker and a checker for home repair and contractor quotes.",
     "publisher": {"@id": SITE + "/#org"},
     "offers": [
         {"@type": "Offer", "name": "Free first answer", "price": "0", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Repair Quote Checker full report", "price": "4.99", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Repair Necessity Checker full report", "price": "9.99", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Any Quote Checker full report", "price": "9.99", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Repair Quote Comparator full report", "price": "14.99", "priceCurrency": "USD"},
         {"@type": "Offer", "name": "Check Any Quote Unlimited", "price": "26.00", "priceCurrency": "USD",
          "priceSpecification": {"@type": "UnitPriceSpecification", "price": "26.00", "priceCurrency": "USD", "billingDuration": "P1M", "unitCode": "MON"}},
     ]},
    faq_ld(FAQ, SITE + "/#faq"),
]
home_desc = ("Check a car repair, home repair or contractor quote before you approve it. QuoteGauge prices every line for your area, "
             "compares estimates, and tells you which repairs are urgent. Free first answer, or Pro for every quote.")
press = ('<section class="press" aria-labelledby="press-title"><div class="wrap">'
         '<p id="press-title" class="press-t">Overcharging on repair quotes is well documented. These outlets reported on it, not on us.</p>'
         '<ul class="press-list">'
         '<li><a href="%s" rel="noopener" target="_blank">AAA</a></li>'
         '<li><a href="https://www.motor1.com/news/813963/shop-overcharges-muffler/" rel="noopener" target="_blank">Motor1</a></li>'
         '<li><a href="https://www.torquenews.com/1084/i-took-my-2020-highlander-its-free-5k-oil-change-and-toyota-came-back-2584-recommended" rel="noopener" target="_blank">Torque News</a></li>'
         '<li><a href="https://www.thecooldown.com/?p=768121" rel="noopener" target="_blank">The Cool Down</a></li>'
         '</ul></div></section>') % AAA_URL
def reviews_html(items):
    if not items:
        return ""
    cards = "".join(
        '<article class="rv"><div class="rv-top"><span class="rv-what">%s</span>%s</div><blockquote>%s</blockquote>'
        '<p class="rv-who"><i aria-hidden="true">%s</i><span><b>%s</b>%s</span></p></article>'
        % (e(what), ('<span class="rv-saved">Saved $%s</span>' % e(str(saved))) if saved else "", e(words), e(name[:1]), e(name), e(state))
        for name, state, what, saved, words in items)
    return ('<section class="reviews" id="reviews" aria-labelledby="reviews-title"><div class="wrap">'
            '<div class="sec-head"><h2 id="reviews-title">What people found.</h2><p>From people who checked a quote with QuoteGauge, shared with their permission.</p></div>'
            '<div class="rv-grid">' + cards + '</div></div></section>')
reviews = reviews_html(REVIEWS)
_REP = {"brake-pad-replacement-cost":0,"brake-pads-and-rotors-cost":0,"alternator-replacement-cost":1,"starter-replacement-cost":1,"water-pump-replacement-cost":1,"timing-belt-replacement-cost":1,"car-battery-replacement-cost":0,"car-ac-recharge-cost":1,"catalytic-converter-replacement-cost":1,"wheel-alignment-cost":1,"spark-plug-replacement-cost":0,"serpentine-belt-replacement-cost":0,"oxygen-sensor-replacement-cost":1,"radiator-replacement-cost":0,"transmission-fluid-change-cost":0,"ac-replacement-cost":1,"furnace-replacement-cost":0,"water-heater-replacement-cost":0,"roof-replacement-cost":2,"ac-capacitor-replacement-cost":0}
def _nums(t): return [int(x.replace(",","")) for x in re.findall(r"\$([\d,]+)", t)][:2]
QG_DATA = json.dumps({"jobs": [[c["job"], c["kind"], *_nums(c["table"][_REP[c["slug"]]][1]), c["slug"]] for c in COSTS],
  "cities": [["United States (typical)", 1, 1]] + [["%s, %s" % (m["city"], m["st"]), round(m["auto"]/NATIONAL["auto"],3), round(m["hvac"]/NATIONAL["hvac"],3)] for m in METROS]}, separators=(",",":"))
body = (read("src/body.html").replace('  <section class="qgf"', PRESS_CSS + press_html() + '\n  <section class="qgf"', 1).replace("%%QGDATA%%", QG_DATA).replace("%%REVIEWS%%", reviews).replace("%%FAQ%%", faq_html(FAQ)).replace("%%PROOF%%", proof)
        .replace("%%GUIDES%%", guides_list).replace("%%HEROVIS%%", hero_vis).replace("%%FOUNDER%%", founder).replace("%%FACE%%", face).replace("%%RECEIPTS%%", receipts))
for k, v in card_img.items():
    body = body.replace("%%IMG_" + k + "%%", v)
home = (head("Is My Car Repair Quote Fair? Check, Compare, Verify | QuoteGauge", home_desc, SITE + "/", home_graph,
             "Don't sign that repair estimate yet")
        + "\n" + body + ('\n<script src="/assets/core.js?v=%s"></script>\n<script src="/assets/app.js?v=%s"></script>\n</body>\n</html>\n' % (ASSET_V, ASSET_V)))
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
      <div class="foot-links"><a href="/about">About</a><a href="../how-we-price.html">How we price</a><a href="../privacy.html">Privacy</a><a href="../terms.html">Terms</a><a href="../refunds.html">Refunds</a></div>
    </div>
    <p class="small">© 2026 QuoteGauge. Not affiliated with any repair shop, dealership, contractor or manufacturer.</p>
  </div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""
    (ROOT / "guides" / (g["slug"] + ".html")).write_text(page)

# ---------- How we price ----------
hwp_url = SITE + "/how-we-price"
hwp_desc = "How QuoteGauge builds each fair price range, what it can and cannot know, and how to use it with a shop or contractor."
hwp = head("How QuoteGauge Prices a Quote | QuoteGauge", hwp_desc, hwp_url,
           [ORG, {"@type": "WebPage", "@id": hwp_url, "name": "How QuoteGauge prices a quote", "description": hwp_desc, "publisher": {"@id": SITE + "/#org"}}],
           "How QuoteGauge prices a quote") + """
<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<nav class="nav" aria-label="Main"><a class="btn keep" style="font-size:19px;padding:9px 16px" href="/#tool">Start a check</a></nav></div></header>
<main>
  <article class="article">
    <p class="crumbs"><a href="/">QuoteGauge</a> / How we price</p>
    <h1>How QuoteGauge prices a quote</h1>
    <p class="answer">Every fair range is an estimate built from the standard labor time for the job, typical labor rates for your area and type of provider, and typical parts or materials cost from economy to premium. It is a starting point for a better conversation, not an inspection or a guarantee.</p>
    <h2>What goes into a range</h2>
    <ul>
      <li><b>Labor time.</b> Car repairs are priced from the standard time for that job on that vehicle. Home and contractor work uses typical hours for the trade and the size of the job.</li>
      <li><b>Labor rate.</b> Typical hourly rates for your ZIP code and the kind of provider. Dealerships and licensed specialists usually charge more, and the range allows for that.</li>
      <li><b>Parts and materials.</b> From economy to original-equipment or premium quality, so a fair price for the parts you're getting stays inside the range.</li>
      <li><b>Room for honest variation.</b> On bigger jobs the top of each range is set at a price a reputable provider might honestly charge with quality parts.</li>
    </ul>
    <h2>How lines are marked</h2>
    <ul>
      <li><b>Fair:</b> at or within 10% of the top of its range.</li>
      <li><b>Above market:</b> more than 10% over the top of its range.</li>
      <li><b>Needs verification:</b> it can't be judged without seeing the car or the job, the price is unreadable, or the description is too vague.</li>
      <li><b>Questionable charge:</b> a line that is often padded or sold as an upsell. It may still be right for you; it's worth a question.</li>
    </ul>
    <h2>What it can't know</h2>
    <ul>
      <li>The condition of your car or home, or what the technician found</li>
      <li>The exact brand and grade of parts the provider plans to use</li>
      <li>Rust, hidden damage, access problems and other things that add real labor</li>
    </ul>
    <p>That is why some lines come back as needs verification, and why the report never claims a provider acted dishonestly. Use it to ask better questions: most honest shops and contractors welcome them.</p>
    <h2>What happens to your quote</h2>
    <p>Your quote is sent to our processing provider to be analysed and is not stored by QuoteGauge after the report is produced. No shop, dealership or contractor pays us, and we don't sell personal data.</p>
    <h2>When we get it wrong</h2>
    <p>Every report has a \"Was this right?\" button, and every flagged mistake is reviewed to improve future checks. If a single report wasn't useful, email <a href="mailto:hello@quotegauge.pro">hello@quotegauge.pro</a> within 7 days for a full refund.</p>
    <div class="cta-box"><h3>Check your quote</h3><p>The first answer is free.</p><a class="btn" href="/#tool">Start a check</a></div>
  </article>
</main>
<footer class="foot"><div class="wrap"><div class="foot-row"><a class="logo" href="/" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<div class="foot-links"><a href="/about">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="refunds.html">Refunds</a></div></div>
<p class="small">© 2026 QuoteGauge. Not affiliated with any repair shop, dealership, contractor or manufacturer.</p></div></footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""
(ROOT / "how-we-price.html").write_text(hwp)


# ---------- QuoteGauge for Teams ----------
teams_url = SITE + "/teams"
teams_desc = ("QuoteGauge for Teams checks every vendor quote your property or fleet team approves: HVAC, plumbing, roofing, "
              "appliance and vehicle repairs. Fair range per line, padded charges flagged, the words to push back. From $199 a month.")
teams_faq = [
    ("Who is QuoteGauge for Teams for?", "Property managers, landlords with 10 or more units, facilities teams and small fleets that approve vendor quotes every week for HVAC, plumbing, roofing, appliances, turnovers or vehicle repairs."),
    ("How much does QuoteGauge for Teams cost?", "The Team plan is $199 a month for up to 5 people and 150 quote checks a month. The Portfolio plan is $499 a month for unlimited people and 600 checks a month. The first 10 teams get 50% off for their first 6 months."),
    ("Does QuoteGauge replace our vendors?", "No. It checks the quotes they send, so you approve fair ones faster and push back on padded lines with specific figures. Most vendors are honest; the check is about consistency, not accusation."),
    ("How do we start?", "Book a 15-minute call. Send two or three recent quotes beforehand and we will show you what the report finds on your own numbers."),
]
teams_graph = [ORG, {"@type": "WebPage", "@id": teams_url, "name": "QuoteGauge for Teams", "description": teams_desc, "publisher": {"@id": SITE + "/#org"}},
               {"@type": "Product", "name": "QuoteGauge for Teams", "description": teams_desc, "brand": {"@id": SITE + "/#org"},
                "offers": [{"@type": "Offer", "name": "Team", "price": "199.00", "priceCurrency": "USD",
                            "priceSpecification": {"@type": "UnitPriceSpecification", "price": "199.00", "priceCurrency": "USD", "billingDuration": "P1M", "unitCode": "MON"}},
                           {"@type": "Offer", "name": "Portfolio", "price": "499.00", "priceCurrency": "USD",
                            "priceSpecification": {"@type": "UnitPriceSpecification", "price": "499.00", "priceCurrency": "USD", "billingDuration": "P1M", "unitCode": "MON"}}]},
               faq_ld(teams_faq, teams_url + "#faq")]
demo = "mailto:hello@quotegauge.pro?subject=QuoteGauge%20for%20Teams%20demo&body=Company%3A%0AHow%20many%20units%20or%20vehicles%3A%0AQuotes%20approved%20per%20month%20(roughly)%3A%0ABest%20time%20for%20a%2015-minute%20call%20(with%20time%20zone)%3A%0A"
teams_page = head("QuoteGauge for Teams: Check Every Vendor Quote | QuoteGauge", teams_desc, teams_url, teams_graph, "Stop approving padded vendor quotes") + f"""
<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<nav class="nav" aria-label="Main"><a href="#how">How it works</a><a href="#plans">Plans</a><a class="btn keep" style="font-size:19px;padding:9px 16px" href="#plans">See plans</a></nav></div></header>
<main>
  <div class="hero">
    <div class="wrap">
      <p class="kicker">QuoteGauge for property managers and fleets</p>
      <h1>You approve 40 vendor quotes a month. How many were padded?</h1>
      <p class="lede" style="max-width:780px;font-size:21px;margin-top:18px">Your team signs off on HVAC calls, plumbing, roofs, appliance swaps, turnovers and van repairs every week, mostly on trust. QuoteGauge checks every quote line by line against local prices, flags the padded and vague lines, and gives your team the exact words to push back. In about a minute, from a phone.</p>
      <div class="cta-row"><a class="btn" href="{demo}">Book a 15-minute demo</a><span>Send us 3 real quotes. See what we find.</span></div>
    </div>
  </div>

  <section aria-labelledby="math-title">
    <div class="wrap">
      <div class="sec-head"><h2 id="math-title">The math your owners will like.</h2><p>An illustrative portfolio. Plug in your own numbers on the call.</p></div>
      <div class="math">
        <div><span class="k">Quotes approved a month</span><b>40</b></div>
        <div><span class="k">Average quote</span><b>$1,200</b></div>
        <div><span class="k">If 8% is avoidable</span><b>$3,840</b><small>a month in your pocket, or your owners'</small></div>
        <div class="hot"><span class="k">QuoteGauge Team</span><b>$199</b><small>a month</small></div>
      </div>
      <p class="fine">Illustration, not a promise: what is avoidable depends on your vendors and your markets. The demo uses your real quotes so you can judge for yourself.</p>
    </div>
  </section>

  <section id="how" class="dark on-dark" aria-labelledby="how-title">
    <div class="wrap">
      <div class="sec-head"><h2 id="how-title">How your team uses it.</h2><p>No software rollout. No vendor portal. A phone and a quote.</p></div>
      <div class="cols three">
        <div class="col"><h3>1. Snap the quote</h3><p>Photo, PDF or the lines typed in. HVAC, plumbing, electrical, roofing, appliances, pest, landscaping, turnovers, and vehicle repairs for fleets.</p></div>
        <div class="col"><h3>2. See what's off</h3><p>A fair range for every line for that ZIP code, with each line marked fair, above market or needs verification, and vague or padded charges called out.</p></div>
        <div class="col"><h3>3. Push back, politely</h3><p>A short script your coordinator can send the vendor, naming the lines and the fair figures. Compare up to five bids for the same job side by side.</p></div>
      </div>
    </div>
  </section>

  <section id="plans" aria-labelledby="plans-title">
    <div class="wrap">
      <div class="sec-head"><h2 id="plans-title">Plans.</h2><p>Monthly, cancel anytime. The first 10 teams get 50% off for 6 months.</p></div>
      <div class="plans">
        <article class="plan"><h3>Team</h3><p class="plan-price"><b>$199</b><span>per month · $99.50 for founding teams</span></p>
          <ul class="ticks"><li>Up to 5 people</li><li>150 quote checks a month</li><li>All four checks, every trade</li><li>Email support, same business day</li></ul>
          <button class="btn block" data-plan="team">Subscribe</button></article>
        <article class="plan best"><span class="badge">For portfolios</span><h3>Portfolio</h3><p class="plan-price"><b>$499</b><span>per month · $249.50 for founding teams</span></p>
          <ul class="ticks"><li>Unlimited people</li><li>600 quote checks a month</li><li>Bid comparisons for every job</li><li>Onboarding call and a monthly review with us</li></ul>
          <button class="btn block" data-plan="portfolio">Subscribe</button></article>
        <article class="plan"><h3>Just you?</h3><p class="plan-price"><b>$26</b><span>per month · Check Any Quote Unlimited</span></p>
          <ul class="ticks"><li>One person</li><li>Every full report unlocked</li><li>Car, home and contractor quotes</li><li>Cancel anytime</li></ul>
          <a class="btn-quiet block" href="/#pricing">See Pro</a></article>
      </div>
    </div>
  </section>

  <section style="padding-top:0" aria-labelledby="tfaq-title">
    <div class="wrap"><div class="sec-head"><h2 id="tfaq-title">Questions owners and managers ask.</h2></div>
    {faq_html(teams_faq)}
    </div>
  </section>

  <div class="promise"><div class="wrap"><p>Three of your quotes. Fifteen minutes. See what we find.</p><a class="btn" href="#plans">See plans</a></div></div>
</main>
<footer class="foot"><div class="wrap"><div class="foot-row"><a class="logo" href="/" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<div class="foot-links"><a href="/about">About</a><a href="how-we-price.html">How we price</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="mailto:hello@quotegauge.pro">hello@quotegauge.pro</a></div></div>
<p class="small">US mailing address: 123 Main St, STE 200 #456, San Francisco, CA 94105</p>
<p class="small">© 2026 QuoteGauge. Automated estimates for information only; not an inspection. Not affiliated with any vendor, contractor or manufacturer.</p></div></footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""
PAYJS = """<script>document.querySelectorAll('[data-plan]').forEach(function(b){b.onclick=function(){var t=b.textContent;b.textContent='Opening checkout…';b.disabled=true;fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan:b.dataset.plan})}).then(function(r){return r.json()}).then(function(d){if(d.url)location.href=d.url;else{b.textContent='Try again';b.disabled=false}}).catch(function(){b.textContent='Try again';b.disabled=false})}})</script>"""
from pm_page import pm_body as _pb, PM_CSS as _pc
(ROOT / "teams.html").write_text(head("QuoteGauge for Teams: Check Every Vendor Quote | QuoteGauge", teams_desc, teams_url, teams_graph, "Approve vendor quotes with proof, not trust").replace("</head>", _pc + PRESS_CSS + "</head>", 1) + _pb("hello@quotegauge.pro").replace('<section class="x-sec" id="roi">', press_html() + '<section class="x-sec" id="roi">', 1))

# ---------- Property managers page ----------
pm_url = SITE + "/property-managers"
pilot = "mailto:hello@quotegauge.pro?subject=Free%203-quote%20check&body=Company%3A%0ACity%3A%0AAttach%203%20recent%20vendor%20quotes%20(photos%20or%20PDFs)%20and%20we%27ll%20send%20results%20within%20one%20business%20day.%0A"
pm_desc = "A second opinion on every vendor quote your property team approves. Send 3 recent HVAC, plumbing, roofing or appliance quotes and get a free line-by-line fairness check within a day."
pm_graph = [ORG, {"@type": "WebPage", "@id": pm_url, "name": "QuoteGauge for Property Managers", "description": pm_desc, "publisher": {"@id": SITE + "/#org"}}, faq_ld(teams_faq, pm_url + "#faq")]
pm_page = teams_page.replace(teams_url, pm_url).replace("QuoteGauge for Teams: Check Every Vendor Quote | QuoteGauge", "QuoteGauge for Property Managers: Free 3-Quote Check | QuoteGauge")
pm_page = pm_page.replace(teams_desc, pm_desc).replace(demo, pilot)
pm_page = pm_page.replace("QuoteGauge for property managers and fleets", "For property managers and maintenance directors")
pm_page = pm_page.replace("You approve 40 vendor quotes a month. How many were padded?", "The AC is down, the resident is calling, and there's no time for three bids.")
pm_page = pm_page.replace("Your team signs off on HVAC calls, plumbing, roofs, appliance swaps, turnovers and van repairs every week, mostly on trust.", "So you approve the vendor's number and hope it was fair, then explain the invoice to the owner later.")
pm_page = pm_page.replace("Book a 15-minute demo", "Send us 3 quotes, free").replace("Send us 3 real quotes. See what we find.", "Results within one business day. No sign-up, no sales call.")
pm_page = pm_page.replace(">Book a demo<", ">Start the free check<")
pm_page = pm_page.replace('<section aria-labelledby="math-title">', """<section aria-labelledby="pilot-title">
    <div class="wrap">
      <div class="sec-head"><h2 id="pilot-title">The free 3-quote check.</h2><p>Try it on your real quotes before you decide anything.</p></div>
      <div class="cols three">
        <div class="col"><h3>1. Email 3 recent quotes</h3><p>Photos or PDFs of any HVAC, plumbing, roofing, appliance or turnover quotes you approved or are about to approve.</p></div>
        <div class="col"><h3>2. Get them back marked up</h3><p>Within one business day: each line marked fair, high or unclear for your city, with the fair range and what to ask the vendor.</p></div>
        <div class="col"><h3>3. Show your owners</h3><p>All fair? You have it in writing. Something padded? You have the numbers to push back. Either way, you keep the report.</p></div>
      </div>
    </div>
  </section>

  <section aria-labelledby="math-title">""",1)
PM_EXTRA = """.pm main>section{padding:96px 0!important}
.pm main>section+section{border-top:1px solid rgba(15,59,46,.08)}
.pm .sec-head{max-width:720px;margin-bottom:40px}
.pm .sec-head h2{font-size:clamp(30px,3.2vw,42px);text-transform:none;letter-spacing:-.01em;line-height:1.1;margin-bottom:12px}
.pm .sec-head p{font-size:18px;opacity:.8}
.pm .cols.three{gap:24px}
.pm .cols .col{background:#fff;border:1px solid rgba(15,59,46,.12);border-radius:14px;padding:26px}
.pm .dark .cols .col{background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.14)}
.pm .col h3{font-size:20px;margin-bottom:8px}
.pm .math{gap:16px}
.pm .promise{padding:64px 0!important;text-align:center}
.pm .promise .wrap{display:flex;flex-direction:column;align-items:center;gap:18px}
.pm .promise p{font-size:26px;font-weight:700}
.pm .faq{max-width:820px}
"""
PM_CSS = """<style>
.pm-hero .wrap{display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center}
.pm-hero h1{font-size:clamp(36px,4.4vw,58px);line-height:1.05;text-transform:none;letter-spacing:-.01em}
.pm-hero .lede{font-size:19px!important;max-width:560px!important}
.pm-hero .cta-row{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:26px}
.pm-hero .cta-row .btn{background:var(--brass);border-color:var(--brass);color:var(--green-2);font-weight:700;padding:14px 22px}
.pm-hero .cta-row span{opacity:.85;font-size:15px}
.pm-photo{margin:0;border-radius:18px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.35);aspect-ratio:4/5;background:#163f33}
.pm-photo img{width:100%;height:100%;object-fit:cover;display:block}
"""+PM_EXTRA+"""@media(max-width:860px){.pm-hero .wrap{grid-template-columns:1fr}.pm-photo{aspect-ratio:16/10}}
</style>
</head>"""
pm_page = pm_page.replace("</head>", PM_CSS, 1).replace("<body>", '<body class="pm">', 1).replace('<div class="hero">', '<div class="hero pm-hero">', 1)
_h = pm_page.index('pm-hero">'); _c = pm_page.index('</span></div>', _h) + len('</span></div>')
_e = pm_page.index('</div>', _c) + len('</div>')
pm_page = pm_page[:_h] + pm_page[_h:].replace('<div class="wrap">\n      <p class="kicker">', '<div class="wrap"><div>\n      <p class="kicker">', 1)
_c = pm_page.index('</span></div>', _h) + len('</span></div>')
pm_page = pm_page[:_c] + '</div>\n      <figure class="pm-photo"><img src="/img/pm-hero.jpg" alt="HVAC technician servicing an apartment air conditioner" width="800" height="1000" onerror="this.parentNode.remove()"></figure>' + pm_page[_c:]
pm_page = pm_page.replace("Three of your quotes. Fifteen minutes. See what we find.", "Three of your quotes. One business day. See what we find.").replace("QuoteGauge for Teams for?", "QuoteGauge for?").replace("Book a 15-minute call. Send two or three recent quotes beforehand and we will show you what the report finds on your own numbers.", "Email us three recent quotes. We send each one back checked within one business day, free. If it helps, we set your team up on a plan.")
_hs = pm_page.index('<div class="hero pm-hero">'); _he = pm_page.index('<section aria-labelledby="pilot-title">')
pm_page = pm_page[:_hs] + """<div class="hero pm-hero">
    <div class="wrap"><div>
      <p class="kicker">For property managers and maintenance teams</p>
      <h1>Know every vendor quote is fair before you sign.</h1>
      <p class="lede">HVAC, plumbing, roofing, appliances, turnovers. Forward any quote and get each line checked against fair local prices, with padded charges flagged and the exact words to push back.</p>
      <div class="cta-row"><a class="btn" href=\"""" + pilot + """\">Check 3 quotes free</a><span>Results in one business day. No sign-up.</span></div>
      <ul class="pm-trust"><li>Local labor data for 10+ US metros</li><li>Line-by-line, not a ballpark</li><li>Independent of every vendor</li></ul>
    </div>
      <div class="pm-visual"><figure class="pm-photo"><img src="/img/pm-hero.jpg" alt="HVAC technician servicing an apartment air conditioner" width="800" height="1000"></figure>
      <div class="pm-card" aria-label="Example result"><p class="pm-card-k">Example check · HVAC repair · Dallas</p>
        <div class="pm-row"><span>Quoted</span><b>$1,850</b></div><div class="pm-row"><span>Fair range</span><b class="ok">$1,100–1,400</b></div>
        <div class="pm-row"><span>Lines flagged</span><b class="bad">2 of 6</b></div><p class="pm-card-n">Illustrative example</p></div></div>
    </div>
  </div>

  """ + pm_page[_he:]
pm_page = pm_page.replace("</style>", """.pm-hero h1{max-width:620px}
.pm-hero .lede{margin-top:18px;opacity:.9}
.pm-trust{list-style:none;padding:0;margin:28px 0 0;display:flex;gap:10px 22px;flex-wrap:wrap;font-size:14px;opacity:.85}
.pm-trust li::before{content:"✓";color:var(--brass);margin-right:8px;font-weight:700}
.pm-visual{position:relative}
.pm-card{position:absolute;left:-36px;bottom:28px;background:#fff;color:#14231d;border-radius:14px;padding:16px 18px;width:270px;box-shadow:0 18px 40px rgba(0,0,0,.28)}
.pm-card-k{font-size:12px;font-weight:600;opacity:.65;margin:0 0 10px}
.pm-row{display:flex;justify-content:space-between;align-items:baseline;padding:6px 0;border-top:1px solid #eee;font-size:14px}
.pm-row b{font-size:16px}.pm-row .ok{color:#1f7a4d}.pm-row .bad{color:#c0392b}
.pm-card-n{font-size:11px;opacity:.5;margin:8px 0 0}
@media(max-width:860px){.pm-card{position:static;width:auto;margin-top:-40px;margin-inline:16px}}
</style>""",1)
pm_page = pm_page.replace(pilot, "#start")
pm_page = pm_page.replace('<a class="btn block" href="#start">Start the free check</a></article>\n        <article class="plan best">', '<button class="btn block" type="button" data-plan="team">Start Team</button></article>\n        <article class="plan best">',1)
pm_page = pm_page.replace('<a class="btn block" href="#start">Start the free check</a></article>\n        <article class="plan">', '<button class="btn block" type="button" data-plan="portfolio">Start Portfolio</button></article>\n        <article class="plan">',1)
pm_page = pm_page.replace('<div class="promise">', """<section id="start" class="pm-start" aria-labelledby="start-title"><div class="wrap">
    <div class="sec-head"><h2 id="start-title">Start your free 3-quote check.</h2><p>Email us three recent vendor quotes (photos or PDFs). We send each one back checked within one business day.</p></div>
    <div class="pm-mail"><span id="pm-addr">hello@quotegauge.pro</span><button type="button" class="btn" id="pm-copy">Copy email</button><a class="btn-quiet" href="mailto:hello@quotegauge.pro?subject=Free%203-quote%20check">Open my email app</a></div>
    <p class="fine">Just one quote right now? <a href="/#tool">Check it on the spot</a>.</p>
  </div></section>
  <div class="promise">""",1)
pm_page = pm_page.replace("</body>", """<script>(function(){var c=document.getElementById('pm-copy');if(c)c.onclick=function(){navigator.clipboard.writeText('hello@quotegauge.pro').then(function(){c.textContent='Copied'})};
document.querySelectorAll('[data-plan]').forEach(function(b){b.onclick=function(){var t=b.textContent;b.textContent='Opening checkout…';b.disabled=true;fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({plan:b.dataset.plan})}).then(function(r){return r.json()}).then(function(d){if(d.url)location.href=d.url;else{b.textContent=t;b.disabled=false;location.hash='start'}}).catch(function(){b.textContent=t;b.disabled=false;location.hash='start'})}})})();</script>
</body>""",1)
pm_page = pm_page.replace("</style>", ".pm-start{background:#dff3e4}.pm-mail{display:flex;gap:12px;flex-wrap:wrap;align-items:center;background:#fff;border-radius:16px;padding:16px 18px;max-width:640px}.pm-mail span{font-weight:700;font-size:20px;flex:1;min-width:220px}\n</style>",1)
from pm_page import pm_body, PM_CSS
_h = head("QuoteGauge for Property Managers: Check Every Vendor Quote | QuoteGauge", pm_desc, pm_url, pm_graph, "Approve vendor quotes with proof, not trust")
(ROOT / "property-managers.html").write_text(_h.replace("</head>", PM_CSS + PRESS_CSS + "</head>", 1) + pm_body("hello@quotegauge.pro").replace('<section class="x-sec" id="roi">', press_html() + '<section class="x-sec" id="roi">', 1))


# ---------- Cost pages ----------
COST_DATE = "2026-11-19"
COST_FOOT = """<footer class="foot">
  <div class="wrap">
    <div class="foot-row">
      <a class="logo" href="/" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
      <div class="foot-links"><a href="/about">About</a><a href="/repair-costs">Repair costs</a><a href="/how-we-price">How we price</a><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/refunds">Refunds</a></div>
    </div>
    <p class="small">© 2026 QuoteGauge. Price ranges are typical US figures from the sources listed; your local price can differ. Not affiliated with any repair shop, contractor or manufacturer.</p>
  </div>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""
COST_TOP = """<header class="top">
  <div class="wrap">
    <a class="logo" href="/" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
    <nav class="nav" aria-label="Main"><a class="btn keep top-cta" href="/#%s">%s</a></nav>
  </div>
</header>"""
ul = lambda items: "<ul>" + "".join("<li>%s</li>" % e(x) for x in items) + "</ul>"
CITY_LINKS = "".join('<a href="/cost/city/%s"><span>%s, %s</span><span aria-hidden="true">→</span></a>' % (m["slug"], e(m["city"]), m["st"]) for m in METROS)
cost_urls = []
for c in COSTS:
    url = "%s/cost/%s" % (SITE, c["slug"])
    cost_urls.append(url)
    cta = "Check my estimate" if c["kind"] == "car" else "Check my quote"
    graph = [
        ORG,
        {"@type": "Article", "@id": url + "#article", "headline": c["title"], "description": c["desc"],
         "datePublished": COST_DATE, "dateModified": COST_DATE, "mainEntityOfPage": url,
         "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"},
         "citation": [u for _, u in c["sources"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "QuoteGauge", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Repair costs", "item": SITE + "/repair-costs"},
            {"@type": "ListItem", "position": 3, "name": c["job"] + " cost", "item": url}]},
        faq_ld(c["faq"], url + "#faq"),
    ]
    rows = "".join("<tr><th scope=\"row\">%s</th><td>%s</td></tr>" % (e(a), e(b)) for a, b in c["table"])
    same = [o for o in COSTS if o["kind"] == c["kind"] and o is not c][:6]
    related = "".join('<a href="/cost/%s"><span>%s cost</span><span aria-hidden="true">→</span></a>' % (o["slug"], e(o["job"])) for o in same)
    srcs = "".join('<li><a href="%s" rel="noopener nofollow">%s</a></li>' % (u, e(n)) for n, u in c["sources"])
    labor = ("<p>%s</p>" % e(LABOR_NOTE)) if c["kind"] == "car" else ""
    page = head(c["title"] + " | QuoteGauge", c["desc"], url, graph, c["title"]) + COST_TOP % (c["product"], cta) + f"""
<main>
  <article class="article cost">
    <p class="crumbs"><a href="/">QuoteGauge</a> / <a href="/repair-costs">Repair costs</a></p>
    <h1>{e(c["title"])}</h1>
    <p class="answer">{e(c["answer"])}</p>
    <h2>Typical prices in 2026</h2>
    <div class="table-wrap"><table class="price-table"><thead><tr><th scope="col">Job</th><th scope="col">Typical US price</th></tr></thead><tbody>{rows}</tbody></table></div>
    <p class="fine">Typical ranges from the published sources below, checked {COST_DATE}. Taxes, shop fees and your local labor rate can move the total.</p>
    <h2>What a fair quote includes</h2>
    {ul(c["includes"])}
    <h2>What pushes the price up</h2>
    {ul(c["drivers"])}
    {labor}
    <h2>Red flags on a quote</h2>
    {ul(c["flags"])}
    <h2>Questions to ask before you approve</h2>
    {ul(c["ask"])}
    <div class="cta-box">
      <h3>Have a quote in hand?</h3>
      <p>Upload a photo or type the lines in. QuoteGauge prices each line for your {"car" if c["kind"] == "car" else "home"} and area, and flags what to question. The first answer is free.</p>
      <a class="btn" href="/#{c["product"]}">{cta}</a>
    </div>
    <h2>Common questions</h2>
    {faq_html(c["faq"], "    ")}
    <h2>Prices in your city</h2>
    <p>Labor rates differ by metro. See local ranges for this and other jobs, adjusted with government wage data:</p>
    <div class="guide-list one">{CITY_LINKS}</div>
    <h2>Sources</h2>
    <ul class="sources">{srcs}</ul>
    <h2>More cost guides</h2>
    <div class="guide-list one">{related}<a href="/repair-costs"><span>All cost guides</span><span aria-hidden="true">→</span></a></div>
    <p class="fine" style="margin-top:28px">General price information, not a quote or professional advice. Updated {COST_DATE}.</p>
  </article>
</main>
""" + COST_FOOT
    (ROOT / "cost").mkdir(exist_ok=True)
    (ROOT / "cost" / (c["slug"] + ".html")).write_text(page)


# ---------- Metro (city) pages ----------
REP = {"brake-pad-replacement-cost":0,"brake-pads-and-rotors-cost":0,"alternator-replacement-cost":1,"starter-replacement-cost":1,
       "water-pump-replacement-cost":1,"timing-belt-replacement-cost":1,"car-battery-replacement-cost":0,"car-ac-recharge-cost":1,
       "catalytic-converter-replacement-cost":1,"wheel-alignment-cost":1,"spark-plug-replacement-cost":0,"serpentine-belt-replacement-cost":0,
       "oxygen-sensor-replacement-cost":1,"radiator-replacement-cost":0,"transmission-fluid-change-cost":0,"ac-replacement-cost":1,
       "furnace-replacement-cost":0,"water-heater-replacement-cost":0,"roof-replacement-cost":2,"ac-capacitor-replacement-cost":0}
SHARE = {"car": 0.5, "home": 0.4}
def rnd(x):
    step = 5 if x < 200 else (10 if x < 1000 else (50 if x < 10000 else 100))
    return int(round(x / step) * step)
def money(x): return "${:,}".format(x)
def adj_range(txt, f):
    import re as _re
    nums = [float(n.replace(",", "")) for n in _re.findall(r"\$([\d,]+)", txt)]
    plus = "+" if txt.strip().endswith("+") else ""
    return "%s – %s%s" % (money(rnd(nums[0] * f)), money(rnd(nums[1] * f)), plus)
def pct(i):
    d = round((i - 1) * 100)
    return "about the same as" if abs(d) < 2 else ("%d%% above" % d if d > 0 else "%d%% below" % -d)
city_urls = []
for m in METROS:
    url = "%s/cost/city/%s" % (SITE, m["slug"])
    city_urls.append(url)
    ia, ih = m["auto"] / NATIONAL["auto"], m["hvac"] / NATIONAL["hvac"]
    fa = SHARE["car"] * ia + (1 - SHARE["car"])
    fh = SHARE["home"] * ih + (1 - SHARE["home"])
    def rows(kind, f):
        out = ""
        for c in COSTS:
            if c["kind"] != kind: continue
            lab, rng = c["table"][REP[c["slug"]]]
            out += '<tr><th scope="row"><a href="/cost/%s">%s</a><br><span class="fine">%s</span></th><td>%s</td><td>%s</td></tr>' % (
                c["slug"], e(c["job"]), e(lab), e(rng), e(adj_range(rng, f)))
        return out
    place = "%s, %s" % (m["city"], m["st"])
    title = "Car Repair and HVAC Costs in %s (2026)" % place
    desc = "Fair 2026 prices for 20 car repairs and home jobs in %s, adjusted for local mechanic and HVAC wages from BLS data, with local tips." % place
    bp = next(c for c in COSTS if c["slug"] == "brake-pad-replacement-cost")
    acr = next(c for c in COSTS if c["slug"] == "ac-replacement-cost")
    answer = ("In %s, auto technicians earn a mean $%.2f an hour, %s the US mean of $%.2f, and HVAC technicians earn $%.2f, %s the US mean of $%.2f (BLS, %s). "
              "So a front brake pad job that runs %s nationally is about %s here, and a mid-efficiency central AC that runs %s nationally is about %s.") % (
        place, m["auto"], pct(ia), NATIONAL["auto"], m["hvac"], pct(ih), NATIONAL["hvac"], BLS_DATE,
        bp["table"][0][1], adj_range(bp["table"][0][1], fa), acr["table"][1][1], adj_range(acr["table"][1][1], fh))
    faq = [("How much is a mechanic's labor in %s?" % m["city"],
            "Auto technicians in the %s metro earn a mean $%.2f an hour (BLS, %s). Shops bill well above the wage to cover overhead, so the shop's hourly rate on your quote will be higher, but it should track local wages. Compare quotes from two or three shops." % (m["msa"], m["auto"], BLS_DATE)),
           ("Are HVAC prices higher in %s than the national average?" % m["city"],
            "HVAC technician wages here are %s the national mean ($%.2f vs $%.2f an hour), which shifts the labor part of an HVAC quote by a similar amount. Equipment prices vary much less by city." % (pct(ih), m["hvac"], NATIONAL["hvac"])),
           ("How were these local prices worked out?",
            "We start from the national ranges in each cost guide and scale only the labor share (about half of a car repair, about 40%% of a home HVAC or contractor job) by the local-to-national wage ratio from BLS. Parts and equipment are kept at national prices. Treat the result as a guide, not a quote.")]
    others = "".join('<a href="/cost/city/%s"><span>%s, %s</span><span aria-hidden="true">→</span></a>' % (o["slug"], e(o["city"]), o["st"]) for o in METROS if o is not m)
    bls = "https://data.bls.gov/oes/#/area/%s/2025" % m["code"]
    graph = [ORG,
        {"@type": "Article", "@id": url + "#article", "headline": title, "description": desc, "datePublished": "2026-11-20", "dateModified": "2026-11-20",
         "mainEntityOfPage": url, "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"},
         "about": {"@type": "City", "name": place}, "citation": [bls, "https://www.bls.gov/oes/"]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "QuoteGauge", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Repair costs", "item": SITE + "/repair-costs"},
            {"@type": "ListItem", "position": 3, "name": place, "item": url}]},
        faq_ld(faq, url + "#faq")]
    th = '<thead><tr><th scope="col">Job</th><th scope="col">US typical</th><th scope="col">%s estimate</th></tr></thead>' % e(m["city"])
    page = head(title + " | QuoteGauge", desc, url, graph, title) + COST_TOP % ("check", "Check my estimate") + f"""
<main>
  <article class="article cost">
    <p class="crumbs"><a href="/">QuoteGauge</a> / <a href="/repair-costs">Repair costs</a> / {e(m["city"])}</p>
    <h1>{e(title)}</h1>
    <p class="answer">{e(answer)}</p>
    <h2>Local wages</h2>
    <div class="table-wrap"><table class="price-table"><thead><tr><th scope="col">Trade</th><th scope="col">{e(m["city"])} mean hourly wage</th><th scope="col">US mean</th></tr></thead><tbody>
      <tr><th scope="row">Auto service technicians</th><td>${m["auto"]:.2f}</td><td>${NATIONAL["auto"]:.2f}</td></tr>
      <tr><th scope="row">HVAC technicians and installers</th><td>${m["hvac"]:.2f}</td><td>${NATIONAL["hvac"]:.2f}</td></tr>
    </tbody></table></div>
    <h2>Car repair prices in {e(m["city"])}</h2>
    <div class="table-wrap"><table class="price-table">{th}<tbody>{rows("car", fa)}</tbody></table></div>
    <h2>Home and HVAC job prices in {e(m["city"])}</h2>
    <div class="table-wrap"><table class="price-table">{th}<tbody>{rows("home", fh)}</tbody></table></div>
    <p class="fine">Estimates scale the labor share of each national range by local wages. Parts, equipment, permits and taxes vary by job and are not adjusted.</p>
    <h2>What's different about {e(m["city"])}</h2>
    {ul(m["notes"])}
    <div class="cta-box">
      <h3>Got a quote from a {e(m["city"])} shop or contractor?</h3>
      <p>Upload a photo or type the lines in. QuoteGauge prices each line for your car or home and your ZIP code, and flags what to question. The first answer is free.</p>
      <a class="btn" href="/#check">Check my estimate</a>
    </div>
    <h2>Common questions</h2>
    {faq_html(faq, "    ")}
    <h2>Sources</h2>
    <ul class="sources"><li><a href="{bls}" rel="noopener nofollow">BLS Occupational Employment and Wage Statistics, {e(m["msa"])}, {BLS_DATE}</a></li><li><a href="https://www.bls.gov/oes/" rel="noopener nofollow">BLS OEWS national estimates, {BLS_DATE}</a></li><li>National price ranges: see the sources on each <a href="/repair-costs">cost guide</a></li></ul>
    <h2>Other cities</h2>
    <div class="guide-list one">{others}<a href="/repair-costs"><span>All cost guides</span><span aria-hidden="true">→</span></a></div>
    <p class="fine" style="margin-top:28px">General price information, not a quote or professional advice. Updated 2026-11-20.</p>
  </article>
</main>
""" + COST_FOOT
    (ROOT / "cost" / "city").mkdir(parents=True, exist_ok=True)
    (ROOT / "cost" / "city" / (m["slug"] + ".html")).write_text(page)

# ---------- "Is $X too much" pages ----------
TOO = [("brake-pad-replacement-cost", 800, "brake pads"), ("brake-pads-and-rotors-cost", 1200, "brakes and rotors"),
       ("alternator-replacement-cost", 1000, "an alternator"), ("timing-belt-replacement-cost", 1500, "a timing belt"),
       ("catalytic-converter-replacement-cost", 3000, "a catalytic converter"), ("car-ac-recharge-cost", 500, "a car AC recharge"),
       ("ac-replacement-cost", 12000, "a new AC unit"), ("water-heater-replacement-cost", 3000, "a water heater"),
       ("ac-capacitor-replacement-cost", 500, "an AC capacitor"), ("roof-replacement-cost", 20000, "a new roof")]
def verdict(price, txt):
    import re as _re
    n = [float(x.replace(",", "")) for x in _re.findall(r"\$([\d,]+)", txt)]
    lo, hi = n[0], n[1]
    if txt.strip().endswith("+") and price > hi: return "Possible for this job, but ask why"
    if price < lo: return "Below typical"
    if price <= hi: return "Within typical range"
    if price <= hi * 1.25: return "Slightly above typical"
    return "Well above typical"
too_urls = []
for slug, price, what in TOO:
    c = next(x for x in COSTS if x["slug"] == slug)
    pslug = "is-%d-too-much-for-%s" % (price, re.sub(r"[^a-z0-9]+", "-", what.lower().replace("a new ", "new ").replace("an ", "").replace("a ", "")).strip("-"))
    url = "%s/cost/%s" % (SITE, pslug)
    too_urls.append(url)
    pm = money(price)
    title = "Is %s Too Much for %s%s? (2026)" % (pm, what[0].upper(), what[1:])
    rows_v = [(a, b, verdict(price, b)) for a, b in c["table"] if "DIY" not in a and "per square foot" not in a and "alone" not in a]
    within = [a for a, b, v in rows_v if v == "Within typical range"]
    above = [a for a, b, v in rows_v if v.startswith("Well above") or v.startswith("Slightly")]
    if within and not above: short = "Usually no."
    elif within: short = "It depends on the job."
    else: short = "Usually yes."
    ans = "%s %s for %s is %s. %s" % (short, pm, what, ("within the typical 2026 US range for " + within[0].lower()) if within else "above the typical 2026 US range for most versions of this job",
          ("It is high for " + above[0].lower() + ", where the usual price is " + dict((a, b) for a, b, _ in rows_v)[above[0]] + ".") if above else "")
    desc = "%s for %s: how it compares with typical 2026 US prices, when it can be fair, and what to ask the shop or contractor." % (pm, what)
    faq = [("Is %s too much for %s?" % (pm, what), ans),
           ("What is a normal price?", c["answer"]),
           ("How can I check my own quote?", "Upload a photo of the quote or type in the lines on QuoteGauge. It prices each line for your car or home and ZIP code and flags what to question. The first answer is free.")]
    graph = [ORG,
        {"@type": "Article", "@id": url + "#article", "headline": title, "description": desc, "datePublished": "2026-11-20", "dateModified": "2026-11-20",
         "mainEntityOfPage": url, "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"}, "citation": [u for _, u in c["sources"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "QuoteGauge", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Repair costs", "item": SITE + "/repair-costs"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]},
        faq_ld(faq, url + "#faq")]
    vrows = "".join('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (e(a), e(b), e(v)) for a, b, v in rows_v)
    srcs = "".join('<li><a href="%s" rel="noopener nofollow">%s</a></li>' % (u, e(n)) for n, u in c["sources"])
    page = head(title + " | QuoteGauge", desc, url, graph, title) + COST_TOP % (c["product"], "Check my quote") + f"""
<main>
  <article class="article cost">
    <p class="crumbs"><a href="/">QuoteGauge</a> / <a href="/repair-costs">Repair costs</a> / <a href="/cost/{slug}">{e(c["job"])}</a></p>
    <h1>{e(title)}</h1>
    <p class="answer">{e(ans)}</p>
    <h2>{pm} compared with typical prices</h2>
    <div class="table-wrap"><table class="price-table"><thead><tr><th scope="col">Version of the job</th><th scope="col">Typical US price</th><th scope="col">{pm} is</th></tr></thead><tbody>{vrows}</tbody></table></div>
    <h2>When {pm} can be fair</h2>
    {ul(c["drivers"])}
    <h2>Signs {pm} is padded</h2>
    {ul(c["flags"])}
    <h2>What to ask before you pay</h2>
    {ul(c["ask"])}
    <div class="cta-box">
      <h3>Is your quote {pm} or close to it?</h3>
      <p>Upload it and QuoteGauge checks every line against fair prices for your {"car" if c["kind"] == "car" else "home"} and ZIP code. The first answer is free.</p>
      <a class="btn" href="/#{c["product"]}">Check my quote</a>
    </div>
    <h2>Common questions</h2>
    {faq_html(faq, "    ")}
    <h2>Prices in your city</h2>
    <div class="guide-list one">{CITY_LINKS}</div>
    <h2>Sources</h2>
    <ul class="sources">{srcs}</ul>
    <p class="fine" style="margin-top:28px">Full price guide: <a href="/cost/{slug}">{e(c["title"])}</a>. General price information, not a quote or professional advice. Updated 2026-11-20.</p>
  </article>
</main>
""" + COST_FOOT
    (ROOT / "cost" / (pslug + ".html")).write_text(page)

# ---------- Data page (original dataset) ----------
data_url = SITE + "/data/repair-labor-by-city"
csv = "metro,state,bls_area_code,auto_tech_mean_hourly,auto_index,hvac_tech_mean_hourly,hvac_index\n" + "US national,,0000000,%.2f,1.000,%.2f,1.000\n" % (NATIONAL["auto"], NATIONAL["hvac"]) + "".join(
    "%s,%s,%s,%.2f,%.3f,%.2f,%.3f\n" % (m["city"], m["st"], m["code"], m["auto"], m["auto"] / NATIONAL["auto"], m["hvac"], m["hvac"] / NATIONAL["hvac"]) for m in METROS)
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "repair-labor-by-city.csv").write_text(csv)
srt = sorted(METROS, key=lambda m: -m["hvac"])
drows = "".join('<tr><th scope="row"><a href="/cost/city/%s">%s, %s</a></th><td>$%.2f</td><td>%+d%%</td><td>$%.2f</td><td>%+d%%</td></tr>' % (
    m["slug"], e(m["city"]), m["st"], m["auto"], round((m["auto"] / NATIONAL["auto"] - 1) * 100), m["hvac"], round((m["hvac"] / NATIONAL["hvac"] - 1) * 100)) for m in srt)
dtitle = "Repair Labor Cost Index by City, 2026: Mechanic and HVAC Wages in 10 US Metros"
ddesc = "How mechanic and HVAC technician wages in 10 large US metros compare with the national average, from BLS May 2025 data. Free CSV download."
top_h, low_h = srt[0], srt[-1]
dans = ("HVAC technicians earn the most in %s ($%.2f an hour, %+d%% vs the US mean of $%.2f) and the least in %s ($%.2f). Auto technicians earn the most in %s ($%.2f) and the least in %s ($%.2f), against a US mean of $%.2f (BLS OEWS, %s).") % (
    top_h["city"], top_h["hvac"], round((top_h["hvac"] / NATIONAL["hvac"] - 1) * 100), NATIONAL["hvac"], low_h["city"], low_h["hvac"],
    max(METROS, key=lambda m: m["auto"])["city"], max(m["auto"] for m in METROS), min(METROS, key=lambda m: m["auto"])["city"], min(m["auto"] for m in METROS), NATIONAL["auto"], BLS_DATE)
dgraph = [ORG,
    {"@type": "Dataset", "@id": data_url + "#dataset", "name": dtitle, "description": ddesc, "url": data_url, "license": "https://creativecommons.org/licenses/by/4.0/",
     "creator": {"@id": SITE + "/#org"}, "dateModified": "2026-11-20", "temporalCoverage": "2025-05", "spatialCoverage": "United States",
     "isBasedOn": "https://www.bls.gov/oes/", "variableMeasured": ["Mean hourly wage, automotive service technicians (49-3023)", "Mean hourly wage, HVAC mechanics and installers (49-9021)"],
     "distribution": {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE + "/data/repair-labor-by-city.csv"}},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "QuoteGauge", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Repair labor by city", "item": data_url}]}]
dpage = head(dtitle + " | QuoteGauge", ddesc, data_url, dgraph, dtitle) + COST_TOP % ("check", "Check my estimate") + f"""
<main>
  <article class="article cost">
    <p class="crumbs"><a href="/">QuoteGauge</a> / Data</p>
    <h1>{e(dtitle)}</h1>
    <p class="answer">{e(dans)}</p>
    <h2>The index</h2>
    <div class="table-wrap"><table class="price-table"><thead><tr><th scope="col">Metro</th><th scope="col">Auto tech wage</th><th scope="col">vs US</th><th scope="col">HVAC tech wage</th><th scope="col">vs US</th></tr></thead><tbody>{drows}
      <tr><th scope="row">US national</th><td>${NATIONAL["auto"]:.2f}</td><td>0%</td><td>${NATIONAL["hvac"]:.2f}</td><td>0%</td></tr></tbody></table></div>
    <p class="fine">Mean hourly wages, BLS Occupational Employment and Wage Statistics, {BLS_DATE}. Sorted by HVAC wage.</p>
    <h2>What it means for your quote</h2>
    <ul><li>Labor is roughly half of a typical car repair bill and 30 to 50 percent of an HVAC or contractor job, so a metro with wages 15 percent above average should run about 6 to 8 percent above national prices overall.</li>
    <li>Parts and equipment prices vary much less by city than labor does.</li>
    <li>Shop and contractor hourly rates are well above technician wages because they cover overhead, but they move with local wages.</li></ul>
    <h2>Method</h2>
    <p>We took the mean hourly wage for automotive service technicians and mechanics (SOC 49-3023) and for heating, air conditioning and refrigeration mechanics and installers (SOC 49-9021) in each metro area, and divided by the national mean. The city pages apply that ratio to the labor share of each national price range.</p>
    <h2>Download and reuse</h2>
    <p><a href="/data/repair-labor-by-city.csv">Download the CSV</a>. Free to reuse under CC BY 4.0. Please credit "QuoteGauge, from BLS OEWS data" with a link to this page.</p>
    <h2>Sources</h2>
    <ul class="sources"><li><a href="https://www.bls.gov/oes/" rel="noopener nofollow">U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, {BLS_DATE}</a></li></ul>
    <p class="fine" style="margin-top:28px">Updated 2026-11-20. Contact hello@quotegauge.pro with questions about the data.</p>
  </article>
</main>
""" + COST_FOOT
(ROOT / "data" / "repair-labor-by-city.html").write_text(dpage)

# Hub
hub_url = SITE + "/repair-costs"
hub_desc = "Fair 2026 US price ranges for 20 common car repairs and home jobs, from brake pads to a new AC, with sources and what to question on a quote."
def hub_list(kind):
    return "".join('<a href="/cost/%s"><span>%s</span><span aria-hidden="true">→</span></a>' % (c["slug"], e(c["job"] + " cost")) for c in COSTS if c["kind"] == kind)
hub_graph = [ORG,
             {"@type": "CollectionPage", "@id": hub_url, "name": "Repair and home job costs", "description": hub_desc, "url": hub_url,
              "hasPart": [{"@type": "Article", "url": u} for u in cost_urls + city_urls + too_urls]},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "QuoteGauge", "item": SITE + "/"},
                 {"@type": "ListItem", "position": 2, "name": "Repair costs", "item": hub_url}]}]
TOO_LINKS = "".join('<a href="%s"><span>Is %s too much for %s?</span><span aria-hidden="true">→</span></a>' % (u.replace(SITE, ''), money(pr), e(w)) for u, (_, pr, w) in zip(too_urls, TOO))
hub = head("Repair and Home Job Costs in 2026: Fair Price Guides | QuoteGauge", hub_desc, hub_url, hub_graph, "Repair and home job costs in 2026") + COST_TOP % ("check", "Check my estimate") + f"""
<main>
  <article class="article">
    <p class="crumbs"><a href="/">QuoteGauge</a> / Repair costs</p>
    <h1>What should this cost?</h1>
    <p class="answer">Fair 2026 US price ranges for common car repairs and home jobs. Each guide shows the typical price, what a fair quote includes, the red flags, and the sources behind the numbers.</p>
    <h2>Car repairs</h2>
    <div class="guide-list one">{hub_list("car")}</div>
    <h2>Home and contractor jobs</h2>
    <div class="guide-list one">{hub_list("home")}</div>
    <h2>Prices by city</h2>
    <div class="guide-list one">{CITY_LINKS}</div>
    <h2>Is my quote too high?</h2>
    <div class="guide-list one">{TOO_LINKS}</div>
    <h2>Data</h2>
    <div class="guide-list one"><a href="/data/repair-labor-by-city"><span>Repair labor cost index by city (free CSV)</span><span aria-hidden="true">→</span></a></div>
    <div class="cta-box">
      <h3>Got a quote that looks high?</h3>
      <p>Upload a photo or type it in. QuoteGauge prices every line for your area. The first answer is free.</p>
      <a class="btn" href="/#check">Check my estimate</a>
    </div>
  </article>
</main>
""" + COST_FOOT
(ROOT / "repair-costs.html").write_text(hub)



# ---------- About ----------
about_url = SITE + "/about"
about_desc = "Who runs QuoteGauge, how it prices repair and contractor quotes, what it costs, where its numbers come from, and the refund policy."
about_graph = [ORG, {"@type": "AboutPage", "@id": about_url, "url": about_url, "name": "About QuoteGauge", "description": about_desc, "about": {"@id": SITE + "/#org"}}]
about = head("About QuoteGauge: Who We Are, How We Price, Plans and Refunds", about_desc, about_url, about_graph, "About QuoteGauge") + COST_TOP % ("check", "Check my estimate") + """
<main>
  <article class="article">
    <p class="crumbs"><a href="/">QuoteGauge</a> / About</p>
    <h1>About QuoteGauge</h1>
    <p class="answer">QuoteGauge is an online tool that checks car repair, home repair and contractor quotes against typical US prices, line by line, and tells you what to question before you approve the work. It is operated by Akshay Krishnan in Bengaluru, India, and serves customers in the United States.</p>
    <h2>Who runs it</h2>
    <p>QuoteGauge is run by Akshay Krishnan, Bengaluru, India. It is independent: it is not owned by, paid by or affiliated with any repair shop, dealership, contractor, parts seller or manufacturer, and no shop pays to be recommended. Contact: <a href="mailto:hello@quotegauge.pro">hello@quotegauge.pro</a>. We usually reply within one business day. US mailing address: 123 Main St, STE 200 #456, San Francisco, CA 94105.</p>
    <h2>What it does</h2>
    <ul><li>Reads a photo, PDF or typed copy of your estimate.</li><li>Prices each line against the typical range for that job on your vehicle or home, in your area.</li><li>Flags lines that look high, unclear or possibly unnecessary, and gives you questions and a short script to use with the shop.</li><li>Compares up to five quotes side by side.</li></ul>
    <h2>How it prices a quote</h2>
    <p>Each check uses an language model (Anthropic's Claude) guided by standard repair labor times, typical US hourly labor rates by area and shop type, and typical parts prices. Results are estimates, not an inspection or a binding price. The full method, including what QuoteGauge cannot know, is on <a href="/how-we-price">How we price</a>. Our published <a href="/repair-costs">cost guides</a> list the outside sources behind each price range.</p>
    <h2>Plans and prices</h2>
    <ul><li>Every check starts with a free first answer: the overall verdict.</li><li>A single full report costs $4.99 to $14.99 depending on the type of check.</li><li>Check Any Quote Unlimited costs $26 a month for every report on every quote. Cancel anytime.</li></ul>
    <p>Payments are processed by Dodo Payments, which acts as our merchant of record and handles billing, receipts and sales tax.</p>
    <h2>Refunds</h2>
    <p>If a single full report was not useful, email us within 7 days and we refund it. Unlimited can be cancelled at any time. Full details: <a href="/refunds">Refund policy</a>.</p>
    <h2>Privacy</h2>
    <p>Quotes you upload are sent to our processing provider (Anthropic) only to produce your report, are not kept afterwards, and are never sold or shared with shops. Details: <a href="/privacy">Privacy policy</a> and <a href="/terms">Terms of use</a>.</p>
    <h2>What QuoteGauge is not</h2>
    <p>It is not a mechanic, contractor, inspector, insurer or lender, and it cannot see your vehicle or property. For large or safety-critical repairs, get at least two itemized quotes and ask the shop to show you the worn or failed part.</p>
  </article>
</main>
""" + COST_FOOT
(ROOT / "about.html").write_text(about)

# ---------- 404 ----------
nf = head("Page not found | QuoteGauge", "This page does not exist. Check a repair or contractor quote, or browse fair-price guides.", SITE + "/404", [ORG], "Page not found").replace('<link rel="canonical" href="https://quotegauge.pro/404">', '<meta name="robots" content="noindex">') + COST_TOP % ("check", "Check my estimate") + """
<main>
  <article class="article">
    <h1>That page doesn't exist.</h1>
    <p class="answer">The link may be old or mistyped. Here is where you probably wanted to go.</p>
    <div class="guide-list one"><a href="/"><span>Check a repair or contractor quote</span><span aria-hidden="true">→</span></a><a href="/repair-costs"><span>Repair and home job cost guides</span><span aria-hidden="true">→</span></a><a href="/#faq"><span>Common questions</span><span aria-hidden="true">→</span></a></div>
  </article>
</main>
""" + COST_FOOT
(ROOT / "404.html").write_text(nf)

# ---------- Sitemap ----------
urls = [(SITE + "/", "1.0")] + [("%s/guides/%s" % (SITE, g["slug"]), "0.8") for g in GUIDES] + [(teams_url, "0.8"), (pm_url, "0.9"), (hwp_url, "0.6")] + [(hub_url, "0.9"), (about_url, "0.7")] + [(u, "0.8") for u in cost_urls + city_urls + too_urls] + [(data_url, "0.8")] + [(SITE + "/" + p, "0.2") for p in ("privacy", "terms", "refunds")]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (u, TODAY, p) for u, p in urls)
                                  + "</urlset>\n")
print("built index.html (%d bytes), %d guides, sitemap with %d urls, photos: %s" % (len(home), len(GUIDES), len(urls), ", ".join(k for k in ("hero", "check", "compare", "need", "founder") if has(k)) or "none"))

# ---------- Clean internal links (Vercel cleanUrls would otherwise 308-redirect every .html link) ----------
import re as _re
def _clean(m):
    q, href = m.group(1), m.group(2)
    if href.startswith(("http", "mailto:", "#", "/_vercel", "data:")):
        return m.group(0)
    h = _re.sub(r'(^|/)index\.html', r'\1', href)
    h = _re.sub(r'\.html(?=($|[#?]))', '', h)
    if h in ("", "../"): h = "/"
    if h.startswith("#"): pass
    return 'href=%s%s%s' % (q, h if h else "/", q)
for f in list(ROOT.glob("*.html")) + list(ROOT.glob("guides/*.html")) + list(ROOT.glob("cost/*.html")) + list(ROOT.glob("cost/city/*.html")) + list(ROOT.glob("data/*.html")):
    t = f.read_text()
    t2 = _re.sub(r'href=(["\'])([^"\']+)\1', _clean, t)
    if t2 != t:
        f.write_text(t2)
print("cost pages: %d, hub: /repair-costs" % len(COSTS))
