ITEMS = [
 ("AAA","Two out of three U.S. drivers do not trust auto repair shops.","AAA driver survey","https://newsroom.aaa.com/2016/12/u-s-drivers-leery-auto-repair-shops/"),
 ("AAA","73% of drivers who distrust shops cite overcharging for services.","AAA driver survey","https://newsroom.aaa.com/wp-content/uploads/2016/12/Auto-Repair-Survey-FINAL.pdf"),
 ("FTC","For expensive repairs, consider getting a second opinion.","Auto Repair Basics","https://consumer.ftc.gov/articles/0211-auto-repair-basics"),
 ("ConsumerAffairs","Only 17% of drivers feel they're always charged fairly for repairs.","Driver survey","https://www.consumeraffairs.com/automotive/auto-mechanics-trust-issues.html"),
 ("Jerry","Nearly 9 in 10 Americans say they've been, or may have been, overcharged for car repairs.","Car repair cost study","https://getjerry.com/studies/americans-united-in-confusion-distrust-over-car-repair-costs"),
 ("Housecall Pro","97% of homeowners expect transparent pricing before hiring a contractor.","Homeowner survey, 2025","https://www.contractormag.com/around-the-web/news/55340108/homeowners-prioritize-experience-over-price-alone-new-housecall-pro-study-finds"),
 ("Scripps News","Knowing whether a contractor's quote is fair is a lot harder than getting one.","Don't Waste Your Money","https://www.scrippsnews.com/dont-waste-your-money/fair-quote-or-ripoff-how-to-get-the-best-price-on-a-big-job"),
 ("Washington AG","If an estimate seems too high, ask why and get a second opinion.","Auto repair guide","https://www.atg.wa.gov/auto-repair"),
]
def press_html():
    cards = "".join(f'<a class="pr-c" href="{u}" target="_blank" rel="noopener"><span class="pr-src">{s}</span><q>{q}</q><small>{n}</small></a>' for s,q,n,u in ITEMS)
    dup = cards.replace("<a ", '<a aria-hidden="true" tabindex="-1" ')
    return '<section class="pr" aria-label="What consumer research says about repair quotes"><p class="pr-h">What the research says about repair quotes</p><div class="pr-v"><div class="pr-t">' + cards + dup + '</div></div></section>'
PRESS_CSS = """<style>
.pr{background:#fff;padding:40px 0 44px;border-bottom:1px solid #e6ece8;overflow:hidden}
.pr-h{text-align:center;font-weight:700;font-size:14px;color:#5b6b63;margin:0 0 22px}
.pr-v{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
.pr-t{display:flex;gap:20px;width:max-content;animation:prs 70s linear infinite}.pr:hover .pr-t{animation-play-state:paused}
@keyframes prs{from{transform:translateX(-50%)}to{transform:translateX(0)}}
.pr-c{flex:0 0 320px;display:flex;flex-direction:column;gap:10px;background:#f6f8f7;border:1px solid #e3e9e5;border-radius:18px;padding:22px 24px;text-decoration:none;color:#1a2520;filter:grayscale(1)}
.pr-src{font-weight:800;font-size:18px;letter-spacing:-.01em;color:#111}
.pr-c q{font-size:16px;line-height:1.45;quotes:"\\201C" "\\201D"}.pr-c small{color:#6b7a73;font-size:13px;margin-top:auto}
@media(prefers-reduced-motion:reduce){.pr-t{animation:none}.pr-v{overflow-x:auto}}
</style>"""
