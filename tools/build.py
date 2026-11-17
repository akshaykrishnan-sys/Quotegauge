"""Builds index.html, guides/*.html and sitemap.xml from src/, lib/core.js and tools/content.py.
Run: python3 tools/build.py
Optional photo: put img/hero.jpg and img/hero.txt (one line describing the photo) in the project."""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from content import AAA_URL, FAQ, GUIDES, PROOF, PROOF_SOURCE, RECEIPTS  # noqa: E402

SITE = "https://quotegauge.pro"
TODAY = "2026-11-15"
PRODUCT_NAME = {"check": "Repair Quote Checker", "compare": "Repair Quote Comparator", "need": "Repair Necessity Checker", "any": "Any Quote Checker"}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Barlow:wght@400;500;600&family=Caveat:wght@700&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">')
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "QuoteGauge", "url": SITE + "/",
       "description": "QuoteGauge checks car repair, home repair and contractor quotes against typical local prices so people know what is fair before approving work.",
       "email": "hello@quotegauge.pro"}

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
    hero_vis = ('<div class="shot"><img src="img/hero.jpg" alt="%s" width="1280" height="853">'
                '<div class="chip c1" aria-hidden="true"><i class="fair"></i>Brake pads + rotors · $689 · fair</div>'
                '<div class="chip c2" aria-hidden="true"><i class="above"></i>Brake fluid flush · $179 · above market</div>'
                '<div class="chip c3" aria-hidden="true"><i class="verify"></i>Fuel system cleaning · ask why</div>'
                '<p class="paper-note">Example labels with illustrative figures.</p></div>') % html.escape(meta["hero"])
card_img = {k: ('<img src="img/%s.jpg" alt="%s" width="900" height="600" loading="lazy" decoding="async">' % (k, html.escape(meta[k])) if has(k) else "") for k in ("check", "compare", "need", "any")}
receipts = ('<section class="receipts" aria-labelledby="receipts-title"><div class="wrap">'
            '<div class="sec-head"><h2 id="receipts-title">These are real quotes.</h2>'
            '<p>All reported in the press. None of these people had QuoteGauge. You will.</p></div><div class="rc-grid">'
            + "".join('<article class="rc"><b>%s</b><p>%s</p><a href="%s" rel="noopener" target="_blank">Source: %s</a></article>' % (e(n), e(t), u, e(src)) for n, t, src, u in RECEIPTS)
            + '</div><p class="rc-foot">Most shops and contractors are honest. The quote still deserves a sanity check. <a class="btn" href="#tool" data-start="check">Check mine, free</a></p></div></section>')
face = ""
if has("face"):
    face = ('<section class="face-sec" aria-labelledby="face-title"><div class="wrap">'
            '<div class="sec-head"><h2 id="face-title">You know this face.</h2><p>It&rsquo;s the &ldquo;we also found a few things&rdquo; face.</p></div>'
            '<figure class="face"><img src="img/face.jpg" alt="%s" width="1280" height="720" loading="lazy" decoding="async">'
            '<figcaption class="cap c-left">The shop texts: &ldquo;Your car is ready!&rdquo;</figcaption>'
            '<figcaption class="cap c-right">&ldquo;&hellip;we also found a few things.&rdquo;</figcaption></figure>'
            '<div class="face-foot"><p>QuoteGauge gets you back to the first face. Upload the list, see which &ldquo;few things&rdquo; are real and which are padded, and walk back to the counter knowing exactly what to say. <b>Before</b> you sign.</p>'
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
body = (read("src/body.html").replace("%%FAQ%%", faq_html(FAQ)).replace("%%PROOF%%", proof)
        .replace("%%GUIDES%%", guides_list).replace("%%HEROVIS%%", hero_vis).replace("%%FOUNDER%%", founder).replace("%%FACE%%", face).replace("%%RECEIPTS%%", receipts))
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
      <div class="foot-links"><a href="../how-we-price.html">How we price</a><a href="../privacy.html">Privacy</a><a href="../terms.html">Terms</a><a href="../refunds.html">Refunds</a></div>
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
<header class="top"><div class="wrap"><a class="logo" href="index.html" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<nav class="nav" aria-label="Main"><a class="btn keep" style="font-size:19px;padding:9px 16px" href="index.html#tool">Start a check</a></nav></div></header>
<main>
  <article class="article">
    <p class="crumbs"><a href="index.html">QuoteGauge</a> / How we price</p>
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
    <p>Your quote is sent to our AI provider to be analysed and is not stored by QuoteGauge after the report is produced. No shop, dealership or contractor pays us, and we don't sell personal data.</p>
    <h2>When we get it wrong</h2>
    <p>Every report has a \"Was this right?\" button, and every flagged mistake is reviewed to improve future checks. If a single report wasn't useful, email <a href="mailto:hello@quotegauge.pro">hello@quotegauge.pro</a> within 7 days for a full refund.</p>
    <div class="cta-box"><h3>Check your quote</h3><p>The first answer is free.</p><a class="btn" href="index.html#tool">Start a check</a></div>
  </article>
</main>
<footer class="foot"><div class="wrap"><div class="foot-row"><a class="logo" href="index.html" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<div class="foot-links"><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="refunds.html">Refunds</a></div></div>
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
<header class="top"><div class="wrap"><a class="logo" href="index.html" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<nav class="nav" aria-label="Main"><a href="#how">How it works</a><a href="#plans">Plans</a><a class="btn keep" style="font-size:19px;padding:9px 16px" href="{demo}">Book a demo</a></nav></div></header>
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
          <a class="btn block" href="{demo}">Book a demo</a></article>
        <article class="plan best"><span class="badge">For portfolios</span><h3>Portfolio</h3><p class="plan-price"><b>$499</b><span>per month · $249.50 for founding teams</span></p>
          <ul class="ticks"><li>Unlimited people</li><li>600 quote checks a month</li><li>Bid comparisons for every job</li><li>Onboarding call and a monthly review with us</li></ul>
          <a class="btn block" href="{demo}">Book a demo</a></article>
        <article class="plan"><h3>Just you?</h3><p class="plan-price"><b>$26</b><span>per month · Check Any Quote Unlimited</span></p>
          <ul class="ticks"><li>One person</li><li>Every full report unlocked</li><li>Car, home and contractor quotes</li><li>Cancel anytime</li></ul>
          <a class="btn-quiet block" href="index.html#pricing">See Pro</a></article>
      </div>
    </div>
  </section>

  <section style="padding-top:0" aria-labelledby="tfaq-title">
    <div class="wrap"><div class="sec-head"><h2 id="tfaq-title">Questions owners and managers ask.</h2></div>
    {faq_html(teams_faq)}
    </div>
  </section>

  <div class="promise"><div class="wrap"><p>Three of your quotes. Fifteen minutes. See what we find.</p><a class="btn" href="{demo}">Book a demo</a></div></div>
</main>
<footer class="foot"><div class="wrap"><div class="foot-row"><a class="logo" href="index.html" aria-label="QuoteGauge home"><i></i>QuoteGauge</a>
<div class="foot-links"><a href="how-we-price.html">How we price</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="mailto:hello@quotegauge.pro">hello@quotegauge.pro</a></div></div>
<p class="small">© 2026 QuoteGauge. AI estimates for information only; not an inspection. Not affiliated with any vendor, contractor or manufacturer.</p></div></footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""
(ROOT / "teams.html").write_text(teams_page)

# ---------- Sitemap ----------
urls = [(SITE + "/", "1.0")] + [("%s/guides/%s" % (SITE, g["slug"]), "0.8") for g in GUIDES] + [(teams_url, "0.8"), (hwp_url, "0.6")] + [(SITE + "/" + p, "0.2") for p in ("privacy", "terms", "refunds")]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + "".join("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (u, TODAY, p) for u, p in urls)
                                  + "</urlset>\n")
print("built index.html (%d bytes), %d guides, sitemap with %d urls, photos: %s" % (len(home), len(GUIDES), len(urls), ", ".join(k for k in ("hero", "check", "compare", "need", "founder") if has(k)) or "none"))
