# QuoteGauge

Three checks for car owners: Repair Quote Checker ($4.99), Repair Quote Comparator ($14.99) and Repair Necessity Checker ($9.99). Static site plus two
serverless functions, built to deploy on Vercel.

## What's here

| Path | Purpose |
|---|---|
| `index.html` | Built page: landing page, the three checks and their reports (do not edit; run `python3 tools/build.py`) |
| `src/` | Page source: `body.html`, `style.css`, `app.js` |
| `tools/build.py` | Builds `index.html`, `guides/*.html` and `sitemap.xml` |
| `tools/content.py` | Questions and answers, sourced statistics and the guide articles |
| `guides/` | Built guide pages for search and AI answers |
| `img/` | Photos. Add any of `hero.jpg`, `check.jpg`, `compare.jpg`, `need.jpg`, `founder.jpg`, describe them in `img/photos.json`, and rebuild |
| `og.png` | Share image used when the site is linked on social media |
| `api/check.js` | Reads the quote with the Claude API, returns the free verdict and a sealed full report |
| `api/pay.js` | Starts a Dodo Payments checkout for a sealed report |
| `api/unlock.js` | Confirms the payment with Dodo, then opens the sealed report (free in test mode) |
| `lib/dodo.js` | Dodo Payments calls and the payment check |
| `lib/core.js` | Prompts, validation and scoring for the three products, shared by the server and the page |
| `lib/seal.js` | Encrypts the full report until it is unlocked |
| `test/report.test.js` | Tests for the scoring and sealing logic (`npm test`) |
| `privacy.html`, `terms.html`, `refunds.html` | Policy pages (drafts, see below) |
| `robots.txt`, `sitemap.xml`, `llms.txt` | Search and AI-assistant discovery files |

## Before going live

1. **Domain.** Replace every `quotegauge.example` with the real domain. It appears
   in `index.html` (canonical, Open Graph, structured data, footer email),
   `robots.txt`, `sitemap.xml`, `llms.txt` and the three policy pages.
2. **Name.** "QuoteGauge" is a working name. Check the domain and trademark before
   committing to it.
3. **Policy pages.** Fill in every `[bracketed]` placeholder and have the pages
   reviewed. They are drafts, not legal advice.
4. **Environment variables** (Vercel project settings):
   - `ANTHROPIC_API_KEY`: key from the Claude Console
   - `REPORT_SECRET`: a long random string, used to seal reports
   - `ANTHROPIC_MODEL` (optional): defaults to `claude-sonnet-5-5`
   - `PAYMENTS_LIVE`: leave unset for test mode (reports open free)
   - `SITE_URL` (optional): e.g. `https://quotegauge.pro`; buyers return here after paying
5. **Payments (Dodo Payments).** In the Dodo dashboard create three one-time
   products (Repair Quote Checker $4.99, Repair Quote Comparator $14.99, Repair
   Necessity Checker $9.99) and an API key, then set:
   - `DODO_API_KEY`
   - `DODO_MODE`: `test` or `live` (a test key only works in test mode)
   - `DODO_PRODUCT_CHECK`, `DODO_PRODUCT_COMPARE`, `DODO_PRODUCT_NEED`: the product IDs (`pdt_...`)
   - `PAYMENTS_LIVE=true`
   Flow: the unlock button calls `/api/pay`, which creates a checkout tied to that
   report and redirects the buyer. Dodo sends them back to `/?payment_id=...`; the
   page calls `/api/unlock`, which fetches the payment from Dodo and opens the
   report only if it succeeded, isn't refunded, and was made for that report and
   product. No database or webhook is needed. Try a test-mode purchase with a
   test card before switching `DODO_MODE` to `live`.
6. **Abuse limits.** Every check costs an API call. Add a rate limit (for example
   Vercel Firewall rules on `/api/check`) before sending traffic to the site.
7. **Analytics.** Turn on Web Analytics in the Vercel project; the page already sends `check_started`, `check_done` and `unlock_clicked` events.
8. **Photos.** See `img/` above. `photos.json` looks like `{"hero": "what the photo shows", "founder": {"alt": "...", "name": "...", "quote": "..."}}`.

## How the paywall works

`/api/check` computes the whole report on the server, returns only the verdict
fields to the browser, and returns the full report encrypted (AES-256-GCM) with
`REPORT_SECRET`. The browser cannot read it. `/api/unlock` decrypts it once the
purchase is confirmed. Nothing is stored in a database.

## Local check

```
npm test
```

The API functions have not been run against the live Claude API in this
repository's history; test them with a real key before launch.
