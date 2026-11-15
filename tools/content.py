"""Site copy that feeds both the visible pages and their structured data."""

AAA_URL = "https://newsroom.aaa.com/2016/12/u-s-drivers-leery-auto-repair-shops/"

# Sourced statistics shown on the home page. Every number names where it came from.
PROOF = [
    ("2 in 3", "US drivers say they do not trust auto repair shops in general."),
    ("76%", "of those drivers point to recommendations for services they did not need."),
    ("73%", "of them point to being overcharged."),
]
PROOF_SOURCE = "AAA survey of US drivers, 2016"

FAQ = [
    ("How do I know if my car repair quote is fair?",
     "Compare each line of the quote with the typical price for your vehicle, your area and the type of shop. QuoteGauge does this in about a minute: add the estimate and it marks every line as fair, above market or needs verification, and totals the amount above market."),
    ("How much does QuoteGauge cost?",
     "The first answer on every check is free. Full reports are one-time purchases with no subscription: the Repair Quote Checker is $4.99, the Repair Necessity Checker is $9.99 and the Repair Quote Comparator is $14.99."),
    ("How do I compare repair quotes from different mechanics?",
     "Add two to five estimates for the same repair to the Repair Quote Comparator. It lines them up side by side, shows the parts and labor differences, points out what each estimate leaves out, ranks them by price and by value, and recommends the best value with its caveats."),
    ("How do I know if I really need the repairs my mechanic recommended?",
     "Add the inspection report or repair list to the Repair Necessity Checker. It explains each repair in plain language, sorts it into do now, do soon, can wait or verify first, lists the symptoms you would notice and the questions to ask, and says when an independent inspection is worth getting. It cannot inspect your car, so safety items are never marked as able to wait."),
    ("How accurate are QuoteGauge's price ranges?",
     "They are AI estimates built from standard labor times and typical regional labor rates. They are closest on routine jobs such as filters, fluid services and brake pads, and wider on large repairs, where honest shops can differ by hundreds of dollars. Use them to ask better questions, not as a guarantee."),
    ("Does QuoteGauge work for dealership quotes?",
     "Yes. You say whether the estimate is from a dealership, an independent shop or a national chain. Dealerships usually charge more, so QuoteGauge compares a dealership estimate with dealership prices."),
    ("What should I do if my repair quote is too high?",
     "Ask the shop to explain each line marked above market, ask which items are needed now and which can wait, and get a second estimate for the expensive ones. The full Repair Quote Checker report includes a short script with the specific items and fair figures to mention."),
    ("Which vehicles and repairs does QuoteGauge cover?",
     "Most cars, SUVs and light trucks sold in the United States, for common maintenance and mechanical repairs such as brakes, fluids, filters, belts, batteries and suspension. It does not cover collision or body work, or insurance estimates."),
    ("Does QuoteGauge keep my estimate?",
     "No. Your estimate is sent to our AI provider to be analysed, and QuoteGauge does not store it after the report is produced. QuoteGauge does not sell personal data."),
    ("Is QuoteGauge connected to any repair shop?",
     "No. QuoteGauge is independent. It takes no referral fees or commissions from repair shops, dealerships or parts sellers."),
]

AAA_LINE = ("In an AAA survey of US drivers, two out of three said they do not trust auto repair shops in general. "
            "Of those, 76% pointed to recommendations for unnecessary services and 73% to overcharging (AAA, 2016).")

# Guides: each opens with a direct answer, then explains. A paragraph is a string, a list is a bullet list.
GUIDES = [
    {
        "slug": "is-my-car-repair-quote-fair",
        "product": "check", "cta": "Check my estimate",
        "title": "How to Tell if a Car Repair Quote Is Fair",
        "desc": "A fair repair quote has reasonable labor hours, a normal local hourly rate and sensibly priced parts. Here is how to check each one before you approve the work.",
        "answer": "A repair quote is fair when each line falls within the typical price for that job on your vehicle, in your area, at that type of shop. Check three things on every line: the labor hours against the standard time for the job, the hourly rate against local rates, and the parts price against what the part sells for.",
        "sections": [
            ("Split the quote into parts, labor and fees", [
                "A proper estimate lists parts, labor and fees separately. Labor is hours multiplied by the shop's hourly rate. If your quote shows only one lump sum per job, ask for the breakdown before anything else; you cannot judge a price you cannot see.",
            ]),
            ("Check the labor first", [
                "Shops price labor from labor guides, which list a standard time for each job on each vehicle. This is often called book time.",
                ["Ask how many hours are billed for each job and what the hourly rate is.",
                 "Compare the hours with the standard time for that job on your vehicle.",
                 "Expect the hourly rate to depend on your region and the type of shop. Dealerships usually charge more per hour than independent shops.",
                 "Watch for overlapping labor. Two jobs in the same part of the car share disassembly, so they should not both be billed at full time."],
            ]),
            ("Then check the parts", [
                "Ask which brand and grade of part is being fitted. Original-equipment parts cost more than aftermarket ones, and a shop's markup over the retail price is normal. What matters is that the price matches the grade of part you are getting.",
            ]),
            ("Read the small lines", [
                "Shop supplies, disposal fees and diagnostic charges are common and usually legitimate. Ask what each one covers, and whether the diagnostic fee is credited if you have the repair done there.",
            ]),
            ("Why five minutes of checking is worth it", [AAA_LINE]),
        ],
        "faq": [
            ("Is it rude to question a repair quote?", "No. Reputable shops expect questions and will walk you through each line. Ask for the labor hours, the hourly rate and the part brand; a clear answer is a good sign."),
            ("Why do repair quotes for the same job differ so much?", "Shops charge different hourly rates, use different grades of parts and include different things in the job. That is why quotes should be compared line by line and not by the total."),
        ],
    },
    {
        "slug": "how-to-compare-car-repair-quotes",
        "product": "compare", "cta": "Compare my estimates",
        "title": "How to Compare Car Repair Quotes from Different Shops",
        "desc": "Compare repair quotes line by line, not by the total. Check that each shop is quoting the same work, the same grade of parts and a comparable warranty.",
        "answer": "Compare repair quotes line by line, not by the total. Make sure each shop is quoting the same work, the same grade of parts and a comparable warranty. The cheapest total often leaves something out.",
        "sections": [
            ("Make sure it is the same job", [
                "Two quotes for a brake job can describe different work: pads only, pads and rotors, or pads, rotors and a fluid service. Write down what each shop says is wrong and what it plans to replace before you look at any price.",
            ]),
            ("Line up parts, labor and fees", [
                ["Parts: brand, grade (original-equipment or aftermarket) and price.",
                 "Labor: hours billed and the hourly rate.",
                 "Fees: shop supplies, disposal and diagnostic charges.",
                 "Taxes, so you are comparing out-the-door totals."],
            ]),
            ("Look for what is missing", [
                "A lower quote is only better if it covers the same work. Check whether the cheaper shop has left out a part or service the other includes, and ask both whether it is actually needed. Sometimes the cheaper quote is right to leave it out; sometimes it will come back as an extra charge later.",
            ]),
            ("Weigh the warranty and the parts", [
                "A longer warranty on parts and labor has real value, and so does a better grade of part on components that wear, such as brakes and suspension. Ask each shop for its warranty terms in writing.",
            ]),
            ("Decide on value, not price", [
                "Rank the quotes by what you get for the money: complete work, suitable parts and a warranty you can use. Then choose the best value among shops you are comfortable with.",
            ]),
        ],
        "faq": [
            ("How many repair quotes should I get?", "For an expensive repair, two or three quotes for the same work are usually enough to see what is normal. For routine maintenance, one quote checked against typical prices is often sufficient."),
            ("Should I tell a shop about a lower quote?", "Yes. Show the other estimate and ask the shop to explain the difference. A good shop will either match like for like or tell you what the other quote leaves out."),
        ],
    },
    {
        "slug": "do-i-really-need-this-car-repair",
        "product": "need", "cta": "Check my repair list",
        "title": "Do I Really Need This Repair? How to Check a Mechanic's Recommendations",
        "desc": "A recommended repair is credible when the shop can show evidence and it matches your car's mileage, maintenance schedule or a symptom you have noticed.",
        "answer": "Ask for evidence. A recommended repair is credible when the shop can show you the worn part, a measurement or a test result, and when it fits your car's mileage, its maintenance schedule or a symptom you have noticed yourself.",
        "sections": [
            ("Sort the list by urgency", [
                ["Do now: anything affecting brakes, tires, steering, suspension, or a fuel or fluid leak.",
                 "Do soon: wear items and scheduled maintenance that is due.",
                 "Can wait: routine items that are not yet due.",
                 "Verify first: anything recommended without a clear reason."],
                "If a shop tells you the car is unsafe to drive, take that seriously and get it confirmed quickly instead of putting it off.",
            ]),
            ("Ask for evidence", [
                ["Ask to see the worn or leaking part on the car.",
                 "Ask for measurements, such as brake pad thickness, tire tread depth or a battery test result.",
                 "Ask for photos if you cannot go into the workshop."],
            ]),
            ("Check it against the maintenance schedule", [
                "Your owner's manual lists when the manufacturer wants each fluid, filter and belt replaced. A service recommended well before its scheduled interval is not necessarily wrong, but it deserves the question: why now?",
            ]),
            ("Know the services that are often sold early", [
                "Fluid flushes ahead of schedule, fuel-system or induction cleaning without symptoms, and engine flushes are commonly offered as add-ons. Each can be legitimate. Ask what symptom or test result led to the recommendation.",
                AAA_LINE,
            ]),
            ("When a second inspection is worth it", [
                "Get an independent inspection when the repair is expensive, you have noticed no symptoms, or you are being pressed to decide on the spot.",
            ]),
        ],
        "faq": [
            ("Can I ask a mechanic to show me the old part?", "Yes. You can ask to see the worn part before the work and to have replaced parts returned afterwards. Some US states require shops to return them on request."),
            ("Is a fluid flush ever necessary?", "Yes, when the maintenance schedule calls for it or a test shows the fluid has degraded. Ask which of those applies to your car."),
        ],
    },
    {
        "slug": "how-to-read-a-car-repair-estimate",
        "product": "check", "cta": "Check my estimate",
        "title": "How to Read a Car Repair Estimate",
        "desc": "A repair estimate has four parts: your vehicle and complaint, parts, labor, and fees and taxes. Here is what each line means and what to ask before you sign.",
        "answer": "A repair estimate has four parts: your vehicle and the problem reported, the parts with their prices, the labor in hours and hourly rate, and fees and taxes. Before you sign, you should be able to say what each line is, why it is needed and what it costs.",
        "sections": [
            ("The header", [
                "This identifies your vehicle, its mileage and the complaint you described. Check that the problem written down is the one you reported, because the diagnosis and the repair follow from it.",
            ]),
            ("Parts lines", [
                "Each part should have a description, a quantity and a price. Abbreviations are common: OEM means original-equipment parts, and A/M or aftermarket means parts from another manufacturer. Ask for the brand if it is not shown.",
            ]),
            ("Labor lines", [
                "Labor is billed as hours multiplied by the shop's hourly rate. The hours usually come from a labor guide's standard time for the job, not from a stopwatch, so the charge is the same whether the technician is fast or slow.",
            ]),
            ("Fees and taxes", [
                ["Shop supplies: consumables such as cleaners, rags and small hardware.",
                 "Disposal or environmental fees: handling of old fluids, tires and parts.",
                 "Diagnostic fee: the time spent finding the fault, sometimes credited toward the repair."],
            ]),
            ("Before you sign", [
                ["Get the estimate in writing.",
                 "Ask the shop to call you for approval before doing any work beyond the estimate.",
                 "Ask for the warranty on parts and labor in writing."],
            ]),
        ],
        "faq": [
            ("What is book time on a repair estimate?", "Book time is the standard number of labor hours a labor guide assigns to a job on a specific vehicle. Shops multiply it by their hourly rate to price the labor."),
            ("What are shop supplies on a repair bill?", "Shop supplies cover consumables used during the repair, such as cleaners, rags and small hardware. Shops charge them as a flat fee or a percentage of labor; ask how yours is calculated."),
        ],
    },
    {
        "slug": "what-to-say-when-a-repair-quote-is-too-high",
        "product": "check", "cta": "Get my script",
        "title": "What to Say When a Car Repair Quote Is Too High",
        "desc": "A calm, specific script for questioning a high repair quote: name the line, give the fair figure, and ask the shop to explain or adjust it.",
        "answer": "Name the specific line, give the fair figure you found, and ask the shop to explain the difference. For example: \"I'm seeing this job priced lower for my car. Can you walk me through the labor hours and the part you're using?\" Stay calm and ask about one line at a time.",
        "sections": [
            ("Before you speak, know your numbers", [
                "A general complaint that the quote feels high gives the shop nothing to respond to. Pick the two or three lines that look out of range and note the fair figure for each. Specific numbers change the conversation.",
            ]),
            ("A script you can use", [
                ["Open: \"Thanks for putting this together. Before I approve it, I have a couple of questions.\"",
                 "Labor: \"How many hours are you billing for this job, and what's your hourly rate?\"",
                 "Parts: \"Which brand of part is this? Is there a quality aftermarket option?\"",
                 "Price: \"I'm seeing this job priced lower for my car in this area. Can you match that, or explain what's different?\"",
                 "Add-ons: \"What symptom or test result led to this recommendation? Can it wait until my next visit?\""],
            ]),
            ("What a good answer sounds like", [
                "A good shop explains the hours, names the part and tells you why a service is due. It may adjust the price, offer a different part, or drop an optional item. Vague answers or pressure to decide immediately are reasons to get a second quote.",
            ]),
            ("If the shop will not move", [
                "Approve only the work you are confident about and take the rest elsewhere for a second quote. For anything that affects brakes, steering or tires, get that second opinion quickly instead of postponing the repair.",
                AAA_LINE,
            ]),
        ],
        "faq": [
            ("Can you negotiate car repair prices?", "Often, yes. Shops have room on parts choice, optional services and sometimes the labor rate. You are more likely to get an adjustment when you ask about a specific line with a specific fair figure."),
            ("Is it okay to decline part of a repair estimate?", "Yes. You can approve some lines and decline others. Ask the shop which items are safety-related so you do not postpone something urgent."),
        ],
    },
    {
        "slug": "common-car-repair-upsells",
        "product": "need", "cta": "Check my repair list",
        "title": "Common Car Repair Upsells, and When They Are Actually Needed",
        "desc": "Fluid flushes, fuel-system cleaning and early filter changes are often sold as add-ons. Here is when each one is worth doing and what to ask first.",
        "answer": "The services most often sold early are fluid flushes, fuel-system or injector cleaning, engine flushes and filter changes. Each can be legitimate. It is worth doing when your maintenance schedule calls for it, a test shows a problem, or you have a matching symptom. Otherwise, ask why it is needed now.",
        "sections": [
            ("Why these services get recommended", [
                "Add-on services are quick to perform and easy to bundle into a visit, so they are commonly offered alongside the repair you came in for. That does not make them wrong, but it does mean the reason matters.",
                AAA_LINE,
            ]),
            ("Fluid flushes", [
                "Brake fluid, coolant and transmission fluid all have replacement intervals in the owner's manual. A flush is reasonable when the interval is due or a test shows the fluid has degraded. Ask which applies, and ask to see the test result.",
            ]),
            ("Fuel-system and injector cleaning", [
                "This is usually worth considering only when there is a symptom, such as rough idle, hesitation or a related warning light. Without one, ask what led to the recommendation.",
            ]),
            ("Filters", [
                "Engine and cabin air filters do wear out, and they are easy to check. Ask to see the filter. If it is visibly dirty, replacing it is fair; the price is what to compare.",
            ]),
            ("Three questions that settle most of these", [
                ["What does my maintenance schedule say for this service at my mileage?",
                 "What symptom, measurement or test result shows it is needed now?",
                 "What happens if I wait until my next visit?"],
            ]),
        ],
        "faq": [
            ("Is fuel injector cleaning necessary?", "Usually only when there is a symptom such as rough idle or hesitation. Many cars never need it as a routine service. Ask what symptom or test led to the recommendation."),
            ("How often should brake fluid be flushed?", "Follow the interval in your owner's manual, which differs by manufacturer. A shop can also test the fluid; ask to see the result if a flush is recommended early."),
        ],
    },
]
