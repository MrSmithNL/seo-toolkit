# Keyword Data Sources — Cost-Benefit Analysis for Autonomous Content Engine

**Prepared for:** Smith AI Agency — SEO Toolkit (PROD-001)
**Date:** 2026-03-15
**Context:** R1 MVP autonomous content pipeline for Hairgenetix (9 languages, 5–10 articles/month)
**Decision:** Free-only vs paid keyword data sources

---

## Executive Summary

For R1 at Hairgenetix scale (50–100 keyword lookups/day, 9 languages), the free sources give you roughly 60% of what you need. The critical gap is **search volume** — free sources cannot reliably tell you how many people search a term per month. Everything else (keyword ideas, intent signals, SERP structure) can be approximated for free.

**Recommendation: Start with the $10/mo Keywords Everywhere option.** It fills the single most important gap (volume data) at negligible cost, supports all 9 languages, and gives 100,000 lookups — far more than needed for R1.

---

## Part 1 — Free Sources

### 1. Google Autocomplete (no key needed)

**What it provides:**
- Keyword suggestions as users type (long-tail phrase discovery)
- Related search suggestions
- No volume, difficulty, CPC, or intent data

**How it works technically:**
Hit `https://suggestqueries.google.com/complete/search?client=firefox&q=KEYWORD&hl=LANG` — no API key, no auth. Returns JSON. Works per-language via `hl=` parameter.

**Accuracy:** High for topical relevance (these are real user queries). Zero for any quantitative metric.

**Rate limits:** Unofficial. Google does not publish limits. At low volume (under ~500 requests/day with polite delays of 1–2 seconds), it is reliable. At scale, IP blocks occur. No official SLA.

**Scale for 50–100 lookups/day:** Yes, achievable with rate-limiting.

**Language support:** All 9 languages (DE, FR, NL, ES, IT, PT, PL, TR, EN) via `hl=` parameter.

**Build-vs-buy:** Already replicable for free. Pure scrape.

**Verdict:** Excellent for keyword idea generation. Useless for prioritisation.

---

### 2. Google Trends API (pytrends)

**What it provides:**
- Relative interest over time (0–100 index, not absolute volume)
- Geographic breakdown of interest
- Related queries and rising topics
- Does NOT provide search volume numbers

**Accuracy:** Relative trends only. A score of 80 means higher interest than a score of 40 for the same term — it tells you nothing about whether that term gets 100 searches/month or 100,000.

**Key limitation:** pytrends is not an official API. It is a Python wrapper that scrapes the Google Trends web interface. Google changed its backend in 2024–2025, causing pytrends to break 2–3 times per year. Google launched an official Trends API in 2025, but it is in alpha with limited endpoints and limited access.

**Rate limits:** Aggressive. Google blocks requests with CAPTCHAs at low thresholds. Production use is unreliable without proxy rotation.

**Scale for 50–100 lookups/day:** Marginal. Risky without proxies.

**Language support:** Yes, via `geo=` parameter (country-level).

**Build-vs-buy:** Not worth building around — too fragile. Good for supplementary trend signals only.

**Verdict:** Useful as a soft signal for content calendar timing (is this topic rising or falling?). Not suitable as a primary data source in an automated pipeline due to fragility.

---

### 3. People Also Ask (PAA) Scraping

**What it provides:**
- Question-format keyword variants (great for FAQ content, featured snippets)
- Strong intent signal (informational queries)
- No volume, difficulty, or CPC data

**How it works technically:** Requires scraping a Google SERP. There is no official PAA API. The HTML element is `div[data-initq]` inside the PAA accordion. Google's anti-scraping measures (CAPTCHAs, IP throttling) make this fragile in production.

**Accuracy:** High for intent and question discovery. Zero for quantitative data.

**Rate limits:** Effectively zero limit from Google's perspective — they do not allow it. In practice, without a proxy pool, a pipeline making 50+ SERP requests/day will be blocked within hours.

**Scale for 50–100 lookups/day:** No — not safely without paid proxy infrastructure.

**Language support:** Yes, via `hl=` + `gl=` parameters.

**Build-vs-buy:** Can be built, but requires ongoing maintenance as Google changes its HTML structure, plus proxy rotation costs (~$20–50/mo for reliable proxies at this scale — which means it is no longer free).

**Verdict:** High-quality intent data, but not production-safe as a free source. DataForSEO's SERP API (paid) includes PAA extraction cleanly.

---

### 4. Google Search Console API

**What it provides:**
- Actual click data for pages that already rank (impressions, clicks, CTR, average position)
- Real queries that brought traffic to your site
- Country and device breakdowns
- Works per language/locale if hreflang is implemented correctly

**Accuracy:** This is real Google data — the most accurate source you have for keywords you ALREADY rank for. It is not a keyword research tool; it is a performance measurement tool.

**Rate limits:** 1,200 queries per minute via API. 50,000 rows per day per property. Very generous.

**Scale for 50–100 lookups/day:** Not applicable — GSC doesn't work as a lookup tool. You pull existing performance data.

**Language support:** Full. Filter by `dimensionFilter: {dimension: "COUNTRY"}` + hreflang URL paths.

**Critical limitation:** GSC only shows keywords you rank for. For a new content pipeline generating articles on keywords you do NOT yet rank for, GSC provides zero prospecting value. It is invaluable for the FEEDBACK LOOP (measuring how articles perform after publication) but cannot power the discovery or prioritisation phase.

**Build-vs-buy:** Already connected to Hairgenetix. No additional cost. Use for post-publication measurement.

**Verdict:** Essential for pipeline feedback, irrelevant for keyword discovery. Already free and connected.

---

### 5. Free Tiers of Keyword Tools

**Ubersuggest (free):**
- 3 searches per 24 hours
- Shows volume, CPC, competition, keyword ideas
- Unusable for an automated pipeline

**Wordtracker (free):**
- Volume, competition score (0–100), historical trends
- Approximately 10–12 free searches/day before prompt to upgrade
- Cannot be accessed via API on free tier
- Blocks automated scraping

**Google Keyword Planner (free, requires Google Ads account):**
- Official Google volume data — same source as most paid tools
- Free to use BUT provides bucketed ranges (1K–10K, 10K–100K) not exact numbers
- No official API for programmatic access — only accessible via Google Ads API, which requires an active ad spend or approved developer token
- Getting a Google Ads API developer token for a non-advertising account is a lengthy approval process

**Verdict:** None of the free tiers are suitable for automated pipeline use at any volume. Rate limits are too low, no programmatic API, or approval barriers are high.

---

### 6. LLM-Based Keyword Estimation (Claude/GPT)

**What it provides:**
- Keyword idea generation: Excellent. LLMs can generate topically comprehensive keyword lists, cluster by intent, identify semantic variants, and propose content angles.
- Difficulty estimation: Plausible-sounding but unreliable. LLMs have no live SERP data. They estimate based on training data which may be 6–18 months old.
- Search volume estimation: Unreliable. LLMs cannot produce accurate volume numbers — they will generate plausible figures but these are pattern-matched guesses, not data. A 2025 study by PageOptimizer Pro found LLM SEO metrics diverged significantly from tool-measured data.
- Intent classification: Excellent. LLMs reliably classify informational / commercial / transactional / navigational intent from keyword text alone.

**Accuracy for volume/difficulty:** Low. Cannot be trusted for business decisions.

**Rate limits:** None beyond API costs (already paying for Claude/GPT).

**Scale:** Unlimited.

**Language support:** All 9 languages.

**Best use in pipeline:** Topic ideation, intent classification, content angle generation, semantic clustering. NOT for volume or difficulty data.

**Verdict:** LLMs are a force multiplier for the creative and strategic layer but cannot replace quantitative keyword data. Use for ideas; pay for numbers.

---

## Part 2 — Paid Sources

### 1. DataForSEO API (~$50/mo at our scale)

**What it provides:**
- Google Ads search volume (exact monthly figures, 24 months historical)
- Keyword difficulty (DataForSEO Labs)
- Full SERP data (organic positions, featured snippets, PAA, Knowledge Graph)
- CPC and competition data
- Bulk keyword data (up to 1,000 keywords per API task)

**Pricing model:** Pay-as-you-go. No monthly subscription. $50 minimum deposit, credits roll over.
- Google Ads search volume: $0.05 per task (1 task = up to 1,000 keywords). At full capacity: $50 covers 1 million keyword lookups.
- SERP API: $0.0006 per SERP request (standard queue). $50 buys ~83,000 SERP requests.
- At R1 scale (100 keywords/day, 30 days): ~$0.15/month for volume data. The $50 deposit would last 12–18 months.

**Accuracy:** DataForSEO pulls from Google Ads API directly for volume, then refines with Bing and clickstream data. The closest available approximation to Google's own data outside Keyword Planner.

**Rate limits:** 12 requests/minute for live Google Ads endpoints. Effectively unlimited for the standard queue.

**Scale for 50–100 lookups/day:** Yes, trivially.

**Language support:** All Google-supported locations and languages, including all 9 Hairgenetix languages.

**Build-vs-buy:** DataForSEO IS the "build our own" option — it exposes the raw data infrastructure. Their Google Ads integration is already the underlying data layer that most other tools resell.

**Verdict:** Best value in the paid category. At R1 scale, $50 deposit lasts months. The "~$50/mo" cost estimate in the brief is worst-case for high-volume users; actual R1 spend would be under $5/month.

---

### 2. SerpAPI (~$50/mo)

**What it provides:**
- Real-time SERP scraping (organic results, ads, PAA, featured snippets, shopping)
- Supports 80+ search engines
- Clean JSON output, very reliable uptime
- Does NOT provide search volume or keyword difficulty

**Pricing:** $50/mo plan gives 5,000 searches/month. At 100 SERP checks/day that is 3,000/month — fits the $50 plan. Overages cost extra.

**Accuracy:** Excellent for SERP structure. Zero for volume/difficulty.

**Rate limits:** Plan-based. 5,000 searches/month on $50 plan.

**Scale for 50–100 lookups/day:** Yes, but at the limit of the cheapest plan.

**Language support:** Full. Google supports all languages via `hl` and `gl` parameters.

**Build-vs-buy:** SerpAPI's value is legal protection (they handle Google's TOS issues) and reliability. You could scrape yourself for free but face blocking, maintenance, and legal grey area.

**Verdict:** SerpAPI solves a real problem (reliable SERP scraping), but it ONLY provides SERP data — no volume or difficulty. You would still need a volume data source on top. Not the right first purchase.

---

### 3. Keywords Everywhere API (~$10/mo at R1 scale)

**What it provides:**
- Search volume (Google-sourced, monthly)
- CPC and competition data
- 12-month trend data
- Related keywords and long-tail variants
- Works via browser extension AND via API

**Pricing:** Credit-based. $10 buys 100,000 credits (1 credit = 1 keyword lookup). Credits valid 1 year. At R1 scale (100 keywords/day, 30 days = 3,000 keywords/month), $10 covers 33 months of data.

**Accuracy:** Volume data sourced from Google Keyword Planner — same baseline as most tools. Reliable for trend direction; bucketing applies at very low volumes (under ~10 searches/month shown as 0 or 10).

**Rate limits:** API: 1 request per second, up to 100 keywords per request. Generous for automation.

**Scale for 50–100 lookups/day:** Yes, easily.

**Language support:** Multiple countries supported. The API accepts a `country` and `currency` parameter. Covers all major Hairgenetix markets (DE, FR, NL, ES, IT, PT, PL, TR). Note: verify Turkish (TR) support before committing, as smaller-market languages occasionally have gaps.

**Build-vs-buy:** Cannot replicate this for free. Google Keyword Planner requires a developer token and active Ads account — a 2–4 week approval process minimum.

**Verdict:** The highest ROI option for R1. At $10 for 100,000 lookups, this is effectively free at our scale. The primary limitation is that it does not provide keyword difficulty scores or SERP position data.

---

### 4. ValueSERP (~$25–40/mo)

**What it provides:**
- SERP scraping (organic results, PAA, featured snippets, local pack, shopping)
- Batch processing (schedule up to 15,000 requests)
- JSON/HTML/CSV output
- Does NOT provide search volume or keyword difficulty

**Pricing:** Starts at $40/mo for 25,000 monthly searches. Rate: $0.50–$1.60 per 1,000 searches depending on plan.

**Accuracy:** Reliable SERP data. No volume data.

**Scale for 50–100 lookups/day:** Yes. 25,000/month is far more than needed.

**Language support:** Full via `hl` and `gl` parameters.

**Verdict:** A cheaper alternative to SerpAPI for SERP data only. Same limitation: no volume data. DataForSEO's SERP API is cheaper still at $0.60 per 1,000 requests vs ValueSERP's $1.60. Redundant if DataForSEO is already in use.

---

### 5. SEMrush API ($140/mo minimum)

**What it provides:**
- The most comprehensive dataset: volume, difficulty, intent, SERP positions, backlinks, competitor keywords, content gap analysis, and more
- 9 billion keywords in database
- Domain-level organic position tracking
- Full API access on Business plan ($449/mo) — basic API on lower plans

**Pricing:** $140/mo (Pro) for limited API access; $449/mo (Business) for meaningful programmatic use. Substantially above the stated budget.

**Accuracy:** Industry standard. Most agencies use SEMrush as the benchmark. Volume correlation with Google Keyword Planner is ~85–90% for mid-volume terms.

**Language support:** All 9 languages fully supported with separate country databases.

**Verdict:** Best-in-class but 3–9x over budget. Not appropriate for R1. Relevant for the long-term roadmap when building agency-level tooling that serves multiple clients.

---

## Part 3 — Capability Comparison Table

| Capability | Best Free Option | Best Paid Option | Gap Without Paid | Impact on Article Quality |
|---|---|---|---|---|
| **Search volume (monthly)** | None — LLM estimates only (unreliable) | Keywords Everywhere API ($10 deposit) | Cannot prioritise keywords by demand. Risk writing 10 articles on zero-traffic terms. | High — determines whether the article can ever drive traffic |
| **Keyword difficulty score** | None — qualitative assessment only | DataForSEO Labs (included in DataForSEO) | Cannot assess whether a target keyword is winnable for a new/small site. | High — avoid wasting effort on impossible keywords |
| **Search intent classification** | LLM classification (Claude/GPT) — excellent | Any paid tool reinforces this | Negligible — LLMs classify intent well from keyword text alone | Low — free option is sufficient |
| **Keyword idea generation** | Google Autocomplete + LLM — good | DataForSEO Keyword Ideas endpoint | Small gap — free options cover most use cases | Low to medium |
| **SERP structure (what ranks)** | Not available without scraping (fragile) | DataForSEO SERP API or SerpAPI | Cannot see what content type wins for a query (blog post, product page, video) | Medium — affects content format decisions |
| **People Also Ask questions** | Not available without scraping (fragile) | DataForSEO SERP API (included) | Miss FAQ content angles that drive featured snippets | Medium |
| **CPC / commercial value** | None | Keywords Everywhere API ($10 deposit) | Cannot identify high-commercial-value keywords to prioritise | Medium for Hairgenetix (products to sell) |
| **Multilingual volume (9 languages)** | None | DataForSEO or Keywords Everywhere | Cannot validate non-English demand — may target keywords with no local search volume | High for 9-language Hairgenetix strategy |
| **Competitor keyword gaps** | Manual inspection only | SEMrush ($140/mo) or DataForSEO Labs | Cannot systematically find what competitors rank for that Hairgenetix does not | Low for R1 (manual research acceptable at 5–10 articles/month) |
| **Post-publication performance** | Google Search Console API (free, already connected) | Not needed — GSC is the source of truth | None | Essential — already free |
| **Trend direction (rising/falling)** | pytrends or Google Trends (fragile) | DataForSEO Keyword Trends endpoint | Marginal — can avoid obviously declining topics manually | Low |

---

## Part 4 — Recommendations

### Option A — Free-Only R1

**What you CAN do:**
- Generate keyword ideas from Google Autocomplete (all 9 languages)
- Classify intent using Claude (informational / commercial / transactional)
- Use GSC to measure performance of published articles
- Use LLMs to estimate topical relevance and content angles
- Use Google Trends (manually, not automated) for rough trend signals

**What you LOSE:**
- Search volume data — you are flying blind on demand. You may write 10 articles and discover all 10 targets get fewer than 50 searches/month combined.
- Keyword difficulty — no signal on whether a given keyword is winnable. A new Shopify store competing for "hair transplant" (extremely high difficulty) vs "hair transplant recovery week 3 photos" (low difficulty) makes an enormous difference in results.
- Multilingual validation — you cannot confirm that German or Turkish variants have any actual search demand before investing in translation and content.
- SERP intelligence — no automated signal on what content format wins for a query.

**R1 article quality with free-only:** Moderate. Content will be topically relevant but may be mis-targeted in terms of volume and difficulty. Approximately 30–40% of articles may target keywords with negligible real-world traffic.

**Verdict:** Viable only if the goal is to test the pipeline infrastructure itself, not to drive meaningful traffic. Acceptable as a 4-week proof-of-concept before spending any money.

---

### Option B — Minimal Paid R1 (Recommended)

**Keywords Everywhere API — $10 one-time deposit**

This fills the single most critical gap at minimal cost. At R1 scale, $10 buys 100,000 keyword lookups — approximately 2.5 years of R1 pipeline operation.

What this adds over free-only:
- Monthly search volume for any keyword in any of the 9 languages
- CPC data (identifies commercially valuable keywords to prioritise for a store)
- 12-month trend data (is interest growing or declining?)
- Related keyword suggestions with volume attached

**Remaining gap with this option:** No keyword difficulty score, no SERP structure data. These gaps can be partially mitigated by:
1. Using the Google Autocomplete depth heuristic (many autocomplete variants = lower difficulty, established format = lower difficulty)
2. Using LLM assessment of competitor domain strength as a rough difficulty proxy
3. Manual spot-checks on 2–3 keywords per article to verify SERP structure

**Expected R1 article quality with $10 Keywords Everywhere:** High for traffic targeting. Articles will be aimed at real demand. Difficulty assessment remains approximate but is manageable at 5–10 articles/month via manual checks.

**Total R1 cost: $10 (one-time credit purchase)**

---

### Option C — Full Paid R1

**DataForSEO ($50 initial deposit)**

Adds what Keywords Everywhere lacks: keyword difficulty, full SERP data including PAA, automated multilingual SERP checks, and competitor position data.

At R1 scale (100 keyword lookups/day, SERP checks for each article target), actual monthly spend on DataForSEO is approximately $3–8/month. The $50 deposit is not a monthly cost — it is a credit balance that lasts 6–12 months.

What DataForSEO adds over Keywords Everywhere:
- Keyword difficulty scores (DataForSEO Labs)
- SERP structure per query (organic results, PAA, featured snippets)
- Direct competitor analysis for any keyword
- All data via a single API — simpler pipeline architecture

**Total R1 cost: $50 initial deposit (covers 6–12 months of actual usage)**

This is the recommended option if building toward the long-term autonomous pipeline described in the brief, because DataForSEO's architecture is designed for programmatic use — it is the data infrastructure layer that the SEO Toolkit (PROD-001) can be built on top of.

---

## Part 5 — Build Your Own Roadmap

The long-term goal (own this capability rather than depend on paid APIs) is achievable but requires 6–18 months of investment. Here is the realistic path:

### Phase 1 — Months 1–3: Foundation (do this now)
- Use Keywords Everywhere API for volume data ($10 deposit)
- Use Google Search Console API for performance feedback (free, already connected)
- Use Claude for intent classification and keyword ideation (already paid for)
- Use Google Autocomplete for keyword discovery (free)
- Build the pipeline around clean data contracts so the source is swappable

**What this achieves:** A working pipeline that produces well-targeted articles. Dependency: Keywords Everywhere (external).

### Phase 2 — Months 3–6: SERP Intelligence
- Integrate DataForSEO SERP API for PAA and SERP structure data (~$5–15/month actual spend)
- Build a caching layer — store every SERP response so you never pay twice for the same query
- Build a keyword database (PostgreSQL) that accumulates volume, difficulty, and intent data over time

**What this achieves:** Full SERP intelligence without recurring high costs. Dependency: DataForSEO (external for fresh data).

### Phase 3 — Months 6–12: Reduce Dependency
- Implement a Google Keyword Planner integration via Google Ads API (requires developer token approval — 3–4 weeks, free once approved)
- This replicates the Keywords Everywhere volume data for free but only for the Hairgenetix Google Ads account
- Build a difficulty estimation model trained on your accumulated keyword-performance data from GSC — as articles rank, you get real difficulty signal
- Implement a PAA scraper with rotating residential proxies (cost: ~$15–20/month for a proxy pool, but you own the infrastructure)

**What this achieves:** Replaces Keywords Everywhere volume data with free Google source. Difficulty estimation becomes proprietary.

### Phase 4 — Months 12–18: Full Ownership
- Accumulated GSC data across 100+ published articles gives you a proprietary keyword-to-performance dataset
- LLM difficulty estimation improves as it is trained on your actual ranking results
- Volume data from Google Ads API covers all Hairgenetix keywords for free
- The only remaining dependency is SERP structure data (DataForSEO or equivalent) — difficult to replicate for free without scraping infrastructure

**Honest assessment of full ownership:** You can reach 80–90% of paid tool capability for near-zero marginal cost within 12–18 months, but SERP data will always have either an infrastructure cost (proxies + maintenance) or a small API cost. The economics of building and maintaining a scraping infrastructure vs paying DataForSEO's ~$5/month at R1 scale rarely favour building.

---

## Final Decision: YES/NO

**YES — spend $10 on Keywords Everywhere credits before building the pipeline.**

**Reasoning:**

The free sources solve everything except the one thing that determines whether the pipeline produces traffic: search volume data. Without volume data, you will build technically functional articles that target low or zero-traffic keywords. You only discover this after publishing. At 5–10 articles/month, that is 2–3 months of wasted content production before the GSC feedback loop tells you something is wrong.

$10 fixes this. The credit balance lasts 2+ years at R1 scale. The API is programmer-friendly, multilingual, and well-documented.

**Do NOT buy SerpAPI or ValueSERP for R1.** These provide SERP data only — no volume. They are the wrong first purchase.

**Do NOT buy SEMrush at $140/mo for R1.** Overkill by 10–20x for 5–10 articles/month.

**DataForSEO is the right long-term choice** (and is effectively pay-per-use, not a subscription), but the $50 initial deposit is not necessary for the first 4–6 weeks. Start with Keywords Everywhere, validate the pipeline produces traffic, then add DataForSEO for difficulty scores and SERP structure.

| Phase | Spend | What You Get | What You're Missing |
|---|---|---|---|
| R1 Week 1–4 (free test) | $0 | Pipeline infrastructure, intent classification, keyword ideas | Volume data, difficulty — articles may miss targets |
| R1 Month 1–3 (Keywords Everywhere) | $10 one-time | Volume + CPC data for all 9 languages | Keyword difficulty, SERP structure |
| R1 Month 3+ (add DataForSEO) | ~$50 initial deposit, ~$5–10/mo actual | Full data stack: volume, difficulty, SERP, PAA | Nothing critical — full production pipeline |
| Long-term | ~$5–15/mo | All of the above with partial in-house replacement | SERP scraping always needs infrastructure or API |

---

## Sources

- [DataForSEO Google Ads API Pricing](https://dataforseo.com/pricing/keywords-data/google-ads)
- [DataForSEO SERP API](https://dataforseo.com/apis/serp-api)
- [DataForSEO Language and Location Support](https://dataforseo.com/help-center/countries-and-locations-serp-api)
- [Keywords Everywhere Pricing](https://keywordseverywhere.com/credits.html)
- [DataForSEO Review 2026 — NextGrowth.ai](https://nextgrowth.ai/dataforseo-review/)
- [SerpAPI vs ValueSERP comparison](https://serpapi.com/blog/compare-serpapi-with-the-alternatives-serper-and-searchapi/)
- [ValueSERP Pricing](https://trajectdata.com/serp/value-serp-api/pricing/)
- [Google Search Console Data Limitations — SEOtesting.com](https://seotesting.com/google-search-console/data-limitations/)
- [pytrends GitHub (unofficial Google Trends API)](https://github.com/GeneralMills/pytrends)
- [pytrends limitations and alternatives — Glimpse](https://meetglimpse.com/google-trends-api/)
- [Google Autocomplete scraping overview — DataForSEO Blog](https://dataforseo.com/blog/google-autocomplete-api-for-keyword-research-tool)
- [LLM SEO comparison — PageOptimizer Pro](https://www.pageoptimizer.pro/blog/we-analyzed-9-major-llms-heres-which-llm-is-best-for-seo)
- [Google Search Console multilingual setup — Linguise](https://www.linguise.com/blog/guide/how-to-setup-the-google-search-console-for-multilingual-websites/)
- [Best SERP APIs 2026 — Scrapfly](https://scrapfly.io/blog/posts/google-serp-api-and-alternatives)
- [Keyword research APIs comparison — Coefficient.io](https://coefficient.io/keyword-research-apis)
