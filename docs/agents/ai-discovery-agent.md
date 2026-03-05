# AI Discovery Agent

## Purpose

Audit, score, and optimise websites for discovery, citation, and recommendation by AI systems — ChatGPT, Perplexity, Google AI Overviews, Copilot, Claude, and Gemini. This agent performs the most comprehensive AI visibility audit available, based on the Vida AEO 34-factor framework, Princeton GEO research, and industry best practices from 40+ sources.

In plain English: when someone asks an AI "what's the best product for X?" or "how do I solve Y?", this agent makes sure your website is one of the sources the AI cites in its answer.

## Why This Matters

- AI traffic surged **527% year-on-year** between 2024-2025
- AI-referred traffic surged **1,200%** between mid-2025 and early 2026
- **86% of high-commercial-intent queries** now trigger AI-generated responses
- LLM traffic converts at **6x the rate** of traditional Google search traffic
- AI answers cite only **2-7 sources** per response — being cited is a massive competitive advantage
- **Brand search volume — not backlinks — is the strongest predictor** of AI citations

---

## Scoring Model

### Overview

The agent scores websites on a **0-100 scale** across **6 weighted categories** containing **36 auditable factors** plus **10 diagnostic factors** (advisory, no score impact). Based on the Vida AEO framework, adapted with findings from the Princeton GEO study, Qwairy citation analysis (118,101 AI answers), Previsible session study (1.96M sessions), and Omniscient Digital citation research (23,000+ citations).

### Category Weights

| # | Category | Weight | # Factors | What It Measures |
|---|----------|--------|-----------|-----------------|
| A | Content Structure & Extractability | **30%** | 10 | Can AI systems easily extract, quote, and cite your content? |
| B | Schema & Structured Data | **20%** | 9 | Does your site speak the machine-readable language AI relies on? |
| C | Authority & Trustworthiness | **20%** | 8 | Does AI have enough evidence to trust your brand? |
| D | Technical Accessibility | **15%** | 9 | Can AI crawlers access, read, and understand your site? |
| E | Freshness & Recency | **10%** | 4 | Is your content current enough for AI to confidently cite? |
| F | Conversational Readiness | **5%** | 3 | Does your content match how AI formulates answers? |

**Total: 100% across 6 categories, 36 scored factors + 10 diagnostic factors.**

### Score Interpretation

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | AI-ready — actively being cited by major AI platforms |
| 75-89 | Good | Strong foundation — minor gaps limiting AI visibility |
| 60-74 | Fair | Missing significant signals — AI may know you exist but rarely cites you |
| 40-59 | Poor | Major gaps — AI systems have little reason to cite your content |
| 0-39 | Critical | Invisible to AI — fundamental work needed across most categories |

---

## Category A: Content Structure & Extractability (30%)

The highest-weighted category. AI systems extract passages, not pages — each piece of content must be self-sufficient, fact-dense, and structured for easy citation. Research shows 44.2% of all LLM citations come from the first 30% of text.

| ID | Factor | Weight | What It Checks | Scoring Criteria |
|----|--------|--------|---------------|-----------------|
| A1 | Answer-First Format | 0.15 | Do pages lead with the direct answer before expanding with context? | 10 = every key page leads with answer; 0 = buried answers |
| A2 | Atomic Paragraphs | 0.10 | Does each paragraph convey one complete, standalone idea extractable by AI? | 10 = self-sufficient paragraphs; 0 = run-on blocks |
| A3 | Question-Based Headings | 0.08 | Do H2/H3 headings match how people ask questions to AI? | 10 = question headings on majority of content pages; 0 = generic headings |
| A4 | Fact Density | 0.10 | Is content packed with verifiable facts, statistics, and data points? Content with verifiable facts shows 89% higher citation probability. | 10 = rich data throughout; 0 = opinion-only content |
| A5 | List & Step Formatting | 0.08 | Does content use numbered lists, bullet points, and step-by-step formats that AI can extract? | 10 = structured lists on all guide/how-to content; 0 = wall-of-text |
| A6 | Summary / TL;DR Blocks | 0.10 | Do key pages include a summary block at the top that AI can quote directly? | 10 = TL;DR on all long-form content; 0 = no summaries |
| A7 | Concise Definitions | 0.08 | Does content include clear, quotable definitions of key terms? AI systems extract these heavily. | 10 = definitions for all key concepts; 0 = no explicit definitions |
| A8 | Comparison Content | 0.06 | Are there comparison tables, product comparisons, and structured side-by-side evaluations? Listicles and comparisons are the most-cited format. | 10 = comparison content present; 0 = none |
| A9 | Natural Language Tone | 0.08 | Does content match how AI formulates responses? Conversational, clear, no jargon or hedging. | 10 = natural, direct tone; 0 = overly formal/promotional |
| A10 | Content Depth | **0.17** | How comprehensive and semantically complete is the content? This is the **highest-weighted individual factor**. Content scoring 8.5/10+ on semantic completeness is 4.2x more likely to be cited. | 10 = comprehensive topic coverage from multiple angles; 0 = surface-level |

**How to audit:** Crawl 10-20 representative pages. Score each factor per page. Average across pages for the category score. Use `invoke_llm` for content quality analysis (A1, A2, A4, A7, A9, A10).

---

## Category B: Schema & Structured Data (20%)

Pages with comprehensive schema markup get a **36% advantage** in AI-generated summaries and citations. Schema feeds the knowledge graph and context layers that AI relies on.

| ID | Factor | Weight | What It Checks | Scoring Criteria |
|----|--------|--------|---------------|-----------------|
| B1 | Organization Schema | 0.15 | Is there a complete Organization schema with name, URL, logo, social profiles, contact info? Establishes brand entity in knowledge graphs. | 10 = complete with all properties; 0 = missing |
| B2 | FAQ Schema | 0.15 | Do FAQ/Q&A pages have FAQPage schema markup? FAQ content is the format most naturally cited by AI. | 10 = all FAQ content marked up; 0 = no FAQ schema |
| B3 | Article / MedicalScholarlyArticle Schema | 0.15 | Do blog posts have Article schema? Do health/science pages use MedicalScholarlyArticle with citation arrays linking to PubMed or scholarly sources? Health/medical sites must use medical schema types. | 10 = all articles marked up with correct type; 0 = missing |
| B4 | Product Schema | 0.10 | Do product pages have Product schema with offers.price (decimal format), priceCurrency, availability, gtin/sku, AggregateRating, shippingDetails, returnPolicy? (E-commerce only — N/A for non-commerce) | 10 = complete product schema; 0 = missing |
| B5 | Author / Person Schema | 0.10 | Is there Person schema for authors/experts with credentials, sameAs links, and affiliation? Feeds E-E-A-T signals. | 10 = complete author schema linked from articles; 0 = missing |
| B6 | HowTo Schema | 0.10 | Do step-by-step guides have HowTo schema with supply[], tool[], and step[] arrays? This content type is easily extractable by AI. | 10 = all how-to content marked up; 0 = missing |
| B7 | Review / AggregateRating Schema | 0.10 | Do pages with reviews/testimonials have proper Review or AggregateRating schema? Product pages should always have AggregateRating if reviews exist. | 10 = all review content marked up; 0 = missing |
| B8 | Schema-Content Alignment | 0.10 | Does the schema data actually match the visible page content? Misaligned schema (wrong price, stale dates, empty values) is worse than no schema. | 10 = perfect alignment; 0 = mismatches found |
| B9 | Schema Deduplication | 0.05 | Are there duplicate @types from different sources (CMS auto-generated + custom + theme + apps)? Duplicate schemas confuse AI and search engines. | 10 = one canonical schema per type per page; 0 = duplicates found |

**How to audit:** Fetch HTML of key pages. Parse all JSON-LD blocks. Validate against Schema.org specs. Cross-check schema values against visible content. Check for duplicates from multiple sources (CMS built-in vs custom). Use the dedicated Schema Audit Agent for deep-dive analysis. See `docs/agents/schema-audit-agent.md` for full methodology.

---

## Category C: Authority & Trustworthiness (20%)

AI systems evaluate brands across five trust dimensions: expert authority, factual accuracy, entity consistency, content freshness, and corroboration. 96% of AI Overview citations come from sources with strong E-E-A-T signals.

| ID | Factor | Weight | What It Checks | Scoring Criteria |
|----|--------|--------|---------------|-----------------|
| C1 | Author Credentials | 0.15 | Are there named authors with verifiable credentials? Author bio pages with links to publications, certifications, profiles? | 10 = detailed author pages with credentials; 0 = no author info |
| C2 | About / Contact Pages | 0.10 | Does the site have complete About and Contact pages with real business information? | 10 = detailed about + contact with address/phone; 0 = missing |
| C3 | Outbound Citations | 0.10 | Does content cite authoritative external sources? AI trusts content that references reputable data. Most effective GEO strategy per Princeton research. | 10 = regular citations to authoritative sources; 0 = no outbound links |
| C4 | Content Originality | 0.15 | Does the site have original research, proprietary data, or unique insights not found elsewhere? Original research attracts citations disproportionately. | 10 = significant original content/research; 0 = purely derivative |
| C5 | Social Proof | 0.10 | Review platform profiles (Trustpilot, G2, Capterra). Sites with review profiles have 3x higher chance of AI citation. Minimum 3.5/5 rating target. | 10 = active profiles with good ratings; 0 = no review presence |
| C6 | Entity Consistency | 0.10 | Is the brand name, description, and information consistent across the site and external mentions? | 10 = perfect consistency; 0 = conflicting information |
| C7 | Legal Pages | 0.10 | Privacy policy, terms of service, editorial standards. Transparency signals. | 10 = complete legal pages; 0 = missing |
| C8 | Brand Recognition | **0.30** | The **highest-weighted factor in this category**. Brand search volume, Wikipedia/Wikidata presence, Knowledge Panel, third-party mentions. Brand search volume — not backlinks — is the strongest predictor of AI citations. | 10 = strong brand recognition signals; 0 = unknown brand |

**How to audit:** Crawl about/contact/legal pages for completeness. Check review platforms via web search. Verify entity consistency across site pages. For C8, search "[brand name]" across platforms and check for Knowledge Panel, Wikipedia, Wikidata entries.

---

## Category D: Technical Accessibility (15%)

The foundation layer. If AI crawlers can't access your content, nothing else matters.

| ID | Factor | Weight | What It Checks | Scoring Criteria |
|----|--------|--------|---------------|-----------------|
| D1 | AI Crawler Access | **0.25** | Does robots.txt allow GPTBot, ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot, ChatGPT-User? Are search/retrieval crawlers allowed even if training crawlers are blocked? | 10 = all search crawlers allowed; 0 = AI crawlers blocked |
| D2 | HTTPS | 0.10 | Is the site served over HTTPS? Security baseline for trust. | 10 = HTTPS everywhere; 0 = HTTP or mixed content |
| D3 | Page Speed | 0.20 | Fast sites get crawled more thoroughly. Check Core Web Vitals (LCP, CLS, INP). | 10 = all CWV passing; 0 = poor across all metrics |
| D4 | Mobile Responsive | 0.10 | AI systems check rendering quality. Is the site fully responsive? | 10 = fully responsive; 0 = desktop-only |
| D5 | XML Sitemap | 0.10 | Is there a valid XML sitemap with accurate lastmod dates? Auto-updating when content changes? | 10 = valid sitemap with correct lastmod; 0 = missing or stale |
| D6 | Clean URLs | 0.05 | Are URLs human-readable and descriptive? Help AI understand page hierarchy. | 10 = clean, descriptive URLs; 0 = parameter-heavy/cryptic |
| D7 | Internal Linking | 0.10 | Strong internal link structure reinforces topical relationships for AI. Topic cluster linking. | 10 = clear hub-and-spoke linking; 0 = orphan pages |
| D8 | Server-Side Rendering | 0.10 | Is content available in the initial HTML response? JavaScript-heavy sites may not be crawled properly by AI. | 10 = full SSR/SSG; 0 = client-side only rendering |

| D9 | hreflang / Multilingual | 0.05 | For multi-language sites: are hreflang tags correctly implemented? Do canonical URLs point correctly? AI systems use these to serve the right language version. | 10 = correct hreflang + canonicals; 0 = missing or conflicting; N/A for single-language |

**Additional technical checks (no score impact — diagnostic only):**
- llms.txt file presence, format compliance, and content quality
- llms-full.txt presence (extended version)
- ai.txt file presence (emerging standard for AI-specific crawling permissions and preferences)
- Open Graph tags on all pages
- Canonical URLs — cross-check against hreflang for consistency
- Title tags and meta descriptions
- H1 validation
- Image alt text
- Heading structure compliance (H1 > H2 > H3)
- **GA4 AI traffic channel** — check if GA4 is configured to track "AI Referral" as a channel (traffic from chat.openai.com, perplexity.ai, claude.ai, copilot.microsoft.com)
- **Conversion event audit** — verify that conversion events (add to cart, purchase, signup) are firing and attributed correctly for AI-referred sessions

**How to audit:** Fetch robots.txt and parse AI crawler rules. Fetch llms.txt and validate format. Check HTTPS, sitemap, speed via web tools. Crawl sample pages for SSR/URL structure/internal links.

---

## Category E: Freshness & Recency (10%)

AI engines weigh recency when selecting sources. Content recency carries the highest individual weight of any single factor across all categories (0.40 within this category).

| ID | Factor | Weight | What It Checks | Scoring Criteria |
|----|--------|--------|---------------|-----------------|
| E1 | Content Recency | **0.40** | When was the content last updated? AI prefers recent sources. Recommended: 2x per week publication for blogs. | 10 = regular recent updates; 0 = all content over 12 months old |
| E2 | Visible Dates | 0.20 | Do pages show published/updated dates visibly? "Last updated" timestamps signal freshness to AI. | 10 = visible dates on all content; 0 = no dates anywhere |
| E3 | Freshness Signals | 0.20 | Does content reference current events, recent data, or 2025-2026 information? | 10 = current references throughout; 0 = dated references only |
| E4 | Copyright Footer Date | 0.20 | Does the footer show the current year? A basic but noticeable staleness signal. | 10 = current year; 0 = old year or no date |

**How to audit:** Check publication dates on articles/blog posts. Look for "Last updated" timestamps. Scan content for date references. Check footer copyright year.

---

## Category F: Conversational Readiness (5%)

The smallest category by weight, but it directly affects whether AI systems quote your content verbatim.

| ID | Factor | Weight | What It Checks | Scoring Criteria |
|----|--------|--------|---------------|-----------------|
| F1 | Q&A Format | 0.40 | Does the site include FAQ pages or question-answer formatted content? FAQPage is the schema type most naturally cited by AI. | 10 = dedicated FAQ + Q&A throughout content; 0 = none |
| F2 | Snippet Formatting | 0.30 | Are there "snippet-ready" blocks — concise 2-3 sentence answers that AI can quote directly? | 10 = quotable snippets throughout; 0 = no snippet-ready content |
| F3 | Long-Tail Query Targeting | 0.30 | Does content target specific, conversational queries (the way people ask AI questions) rather than just short keywords? | 10 = content matches conversational queries; 0 = keyword-stuffed |

**How to audit:** Check for FAQ pages and FAQ schema. Analyze content for snippet-ready blocks. Review keyword targeting strategy.

---

## llms.txt Audit (Diagnostic — Detailed Assessment)

The llms.txt file is checked as part of Category D (Technical Accessibility) but gets its own detailed diagnostic section because it's the single most AI-specific technical requirement.

### What to check:

| Check | Pass Criteria |
|-------|-------------|
| **File exists** | `yoursite.com/llms.txt` returns HTTP 200 |
| **MIME type** | Served as `text/plain` or `text/markdown` |
| **Encoding** | UTF-8 |
| **No auth required** | Accessible without login |
| **Pure text** | No HTML boilerplate, no JavaScript — raw markdown only |
| **Format compliance** | Follows llmstxt.org spec: `# Title`, `> Description`, `## Sections`, `- [Page](url): Description` |
| **Content completeness** | All major site sections represented |
| **URLs valid** | All linked URLs return HTTP 200 |
| **RSS/Atom feed** | Links to content feeds for automated discovery |
| **Recently updated** | Content matches current site structure |
| **llms-full.txt** | Extended version with full content summaries (bonus, not required) |

---

## External Presence Assessment

This is a strategic advisory section that goes beyond on-site auditing. The agent checks for off-site signals that heavily influence AI citation decisions.

### Third-Party Presence Check

| Platform | What to Check | Why It Matters |
|----------|-------------|---------------|
| **Reddit** | Brand mentions, subreddit presence, sentiment | #1 most-cited source at 40.1% citation frequency. 39,551 AI citations in 30 days for top brands |
| **YouTube** | Branded channel, video content, descriptions | Most frequently cited source for Google AI Overviews |
| **Trustpilot** | Profile exists, rating, review volume | Sites with review profiles have 3x higher AI citation chance |
| **G2 / Capterra** | Profile exists, rating (SaaS/B2B only) | Direct influence on ChatGPT product recommendations |
| **Wikipedia** | Article exists, accuracy, completeness | Wikipedia is ChatGPT's #1 cited source (7.8%) |
| **Wikidata** | Entity entry, completeness | Feeds knowledge graphs used by all AI platforms |
| **Google Business Profile** | Complete listing, reviews, photos | Knowledge Panel presence signals entity recognition |
| **Industry Directories** | Relevant listings, consistent NAP | Directory inclusion carries 65% weight on Claude |

### How the agent checks this:

1. Search `"[brand name]" site:reddit.com` — count mentions, assess sentiment
2. Search `"[brand name]" site:youtube.com` — check for branded channel
3. Search `"[brand name]" site:trustpilot.com` — check for profile
4. Search `"[brand name]" site:en.wikipedia.org` — check for article
5. Search `"[brand name]"` on Google — check for Knowledge Panel
6. Report findings with specific recommendations

---

## Share of Model (SoM) Measurement

The primary KPI for AI visibility. Replaces Share of Voice for the AI era.

### What it measures

How often your brand is mentioned, cited, or recommended in AI-generated answers to non-branded queries in your category.

### Methodology

1. **Define 25-50 high-intent queries** that mirror the buyer's journey in the client's category
2. **Submit each query** to ChatGPT, Perplexity, and Google (AI Mode / AI Overviews)
3. **For each response, track:**
   - Was the brand mentioned? (yes/no)
   - Was a URL cited? (yes/no)
   - What was the sentiment? (positive/neutral/negative)
   - What competitors were mentioned?
   - What position was the brand in the response? (first mentioned, middle, last)
4. **Calculate:**
   - **SoM %** = brand mentions / total brand mentions across all responses
   - **Citation rate** = responses with URL / total responses
   - **Sentiment score** = weighted average (positive=1, neutral=0, negative=-1)
   - **Competitive gap** = your SoM vs top competitor

### Benchmarks

| Metric | Poor | Fair | Good | Excellent |
|--------|------|------|------|-----------|
| SoM % | <5% | 5-10% | 10-15% | 15%+ |
| Citation Rate | <10% | 10-25% | 25-50% | 50%+ |
| Sentiment | <0 | 0-0.3 | 0.3-0.7 | 0.7+ |

### SoM Query Design

Queries should cover the full buyer journey:

| Stage | Example Queries | Purpose |
|-------|---------------|---------|
| Awareness | "what is [problem]?", "how does [topic] work?" | Does AI mention your brand when educating? |
| Consideration | "best [product category]", "[product A] vs [product B]" | Are you in the consideration set? |
| Decision | "is [brand] worth it?", "[brand] reviews" | What does AI say about you specifically? |
| Support | "how to use [product]", "[product] troubleshooting" | Does AI reference your content for support? |

---

## Platform-Specific Recommendations

Different AI engines weight different signals. The agent provides platform-specific recommendations.

### Platform Optimization Matrix

| Signal | ChatGPT | Perplexity | Google AI Overviews | Claude | Copilot |
|--------|---------|------------|---------------------|--------|---------|
| **Search index** | Bing | Proprietary (200B+ URLs) | Google | Brave Search | Bing |
| **Avg citations/response** | 7.92 | 21.87 | 3-7 | Variable | 2.47 |
| **Top cited source** | Wikipedia (7.8%) | Reddit (6.6%) | YouTube | Institutional/research | Varies |
| **Schema importance** | High | Medium | Critical | Medium | Medium |
| **Review platforms** | Medium | High (biggest lever) | Medium | Low | Medium |
| **Awards/accreditations** | 18% influence | 5% influence | Medium | 19% influence | Medium |
| **Brand authority** | Highest factor | Important | Important | Highest factor | Important |
| **Content freshness** | Important | Critical | Important | Medium | Important |
| **Directory listings** | 25% influence | 35% influence | Medium | 65% influence | Medium |

### Platform-Specific Recommendations Template

For each platform, the agent generates targeted recommendations:

1. **Quick wins** — things that can be done today with immediate impact
2. **Medium-term** — improvements that take 2-4 weeks to implement
3. **Long-term** — strategic initiatives that build over months (brand building, earned media, Reddit presence)

---

## Invisible GEO — Machine-Only Optimizations

A key strategic category: optimizations that improve AI/LLM visibility without changing what visitors see on the page. These are zero-risk, high-impact changes that should be recommended first.

### What Counts as Invisible GEO

| Optimization | What It Does | Visible to Readers? |
|-------------|-------------|-------------------|
| **JSON-LD schema markup** | Tells AI systems exactly what the content is, who wrote it, and why to trust it | No — hidden in page source |
| **Meta descriptions** | AI systems often use these as summaries when deciding whether to cite | No — only in source code |
| **Open Graph tags** | Help AI understand content when shared or crawled | No — only in page head |
| **hreflang tags** | Tell AI which language version to serve | No — only in page head |
| **Canonical URLs** | Prevent AI from splitting signals across duplicate pages | No — only in page head |
| **llms.txt / llms-full.txt** | Machine-readable site map specifically for AI systems | No — separate files |
| **ai.txt** | AI-specific crawling permissions and preferences | No — separate file |
| **robots.txt AI directives** | Control which AI crawlers can access content | No — separate file |
| **Internal linking structure** | Reinforces topical relationships for AI understanding | Subtle — improves UX too |
| **Image alt text** | Helps AI understand visual content | Only for screen readers |
| **Semantic HTML** | Proper heading hierarchy (H1>H2>H3) helps AI parse content structure | Subtle — improves UX too |
| **FAQ schema on product pages** | Adds Q&A to product pages that AI can cite, without visible FAQ section | No — only in schema |

### Why This Matters

Many website owners resist SEO changes because they fear affecting the customer experience. Invisible GEO eliminates this concern — it's pure upside with zero customer-facing risk. The audit should always categorize recommendations as "invisible" (schema, meta, technical) vs "visible" (content rewrites, new pages) so clients can prioritize accordingly.

---

## Audit Report Structure

The agent generates a comprehensive report saved to `reports/{domain}/ai-discovery-{date}.md`:

```
# AI Discovery Audit — {domain}
## Date: {date}

## Executive Summary
- Overall score: XX/100 ({rating})
- Top 3 strengths
- Top 3 critical gaps
- Estimated improvement potential

## Scores by Category
| Category | Score | Weight | Weighted Score |
|----------|-------|--------|----------------|
| A. Content Structure & Extractability | /100 | 30% | /30 |
| B. Schema & Structured Data | /100 | 20% | /20 |
| C. Authority & Trustworthiness | /100 | 20% | /20 |
| D. Technical Accessibility | /100 | 15% | /15 |
| E. Freshness & Recency | /100 | 10% | /10 |
| F. Conversational Readiness | /100 | 5% | /5 |
| **TOTAL** | | | **/100** |

## Detailed Factor Scores
[All 34 factors with individual scores and specific findings]

## Diagnostic Factors
[7 diagnostic items — pass/fail with details]

## llms.txt Assessment
[Detailed llms.txt audit results]

## External Presence Assessment
[Third-party platform presence check results]

## Share of Model Results
[SoM measurement across AI platforms — if queries provided]

## Platform-Specific Recommendations
### ChatGPT Optimization
### Perplexity Optimization
### Google AI Overviews Optimization
### Claude Optimization

## Prioritised Action Plan

### Invisible GEO (no visible changes — implement first)
[Schema fixes, meta tags, technical changes — zero customer-facing risk]

### Visible Changes (requires content review)
[Content rewrites, new pages, structural changes — discuss with stakeholder first]

### Immediate (this week)
### Short-term (this month)
### Medium-term (next quarter)
### Long-term (ongoing)

## Analytics & Measurement Setup
### AI Traffic Channel (GA4)
[Is AI referral tracking configured? If not, provide setup instructions]
### Conversion Attribution
[Are conversions being attributed to AI-referred sessions?]

## Comparison with Previous Audit
[Score changes, improvements, new issues — if previous audit exists]
```

---

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| Site crawl (WebFetch) | HTML content, schema, meta tags, headers, llms.txt | Primary |
| Google Search Console | Search performance data, indexed pages | Primary |
| Web search (Composio) | Brand mentions, review profiles, external presence | Primary |
| invoke_llm | Content quality scoring (A1-A10), semantic analysis | Primary |
| robots.txt | AI crawler access rules | Primary |
| Schema.org validator | Schema validation reference | Reference |
| llmstxt.org spec | llms.txt format specification | Reference |
| AI engine testing | Manual SoM measurement | Supplementary |

---

## Rube Recipe Implementation

**Current recipe:** `rcp_3LBwPfkiTtRT`

The recipe implements the full audit workflow:

1. **Input:** domain URL, optional list of SoM queries
2. **Technical crawl:** Fetch robots.txt, llms.txt, sitemap, sample pages
3. **Schema analysis:** Parse and validate JSON-LD on all fetched pages
4. **Content analysis:** Score content factors (A1-A10) using invoke_llm
5. **Authority check:** Search for brand mentions, review profiles, Wikipedia
6. **Freshness check:** Analyze publication dates, update signals
7. **Score calculation:** Apply weights, calculate category and overall scores
8. **Report generation:** Produce full audit report with recommendations
9. **SoM measurement:** If queries provided, test across AI platforms

---

## Schedule

- **After any content change** — update llms.txt and schema checks
- **Monthly** — full 34-factor AI discovery audit
- **Quarterly** — Share of Model measurement across all AI platforms
- **Quarterly** — external presence deep dive (Reddit, reviews, Wikipedia)

---

## Research Foundation

This agent's methodology is based on:

- **Vida AEO 34-Factor Framework** — the most detailed published audit methodology for AI visibility
- **Princeton GEO Study (KDD 2024)** — academic foundation proving GEO can boost AI visibility by 40%
- **Previsible Study** — 1.96M LLM-driven sessions analysed across 12 months
- **Qwairy Study** — 118,101 AI-generated answers analysed for citation patterns
- **Omniscient Digital Study** — 23,000+ AI citations analysed for content patterns
- **Search Engine Land Four-Phase GEO Framework** — Assess, Optimize, Measure, Iterate
- **First Page Sage Platform-Specific Research** — effectiveness data per AI platform
- **40+ industry publications** — full research document at `smith-ai-agency/research/ai-visibility-optimization-research.md`

---

## Shopify Implementation Recipes

Repeatable fix procedures for common GEO gaps found during audits on Shopify stores. Each recipe is a standalone function that can be run via the Shopify GraphQL Admin API.

### Recipe 1: Create ai.txt

**Fixes:** ai.txt diagnostic check (Category D)
**What it does:** Creates a page with AI content policy and sets up a URL redirect from `/ai.txt` to `/pages/ai-txt`.

**Steps:**
1. Create a Shopify page via `pageCreate` mutation with handle `ai-txt`
2. Content should include: brand identity, AI content usage policy, preferred citation format, content categories with URLs, structured data summary, available languages
3. Create URL redirect via `urlRedirectCreate`: path `/ai.txt` → target `/pages/ai-txt`
4. Verify by fetching `{domain}/ai.txt` — should resolve to the page

**Template content structure:**
```
[Brand name] — [tagline]
Website: [url]

## AI Content Usage Policy
[Terms for AI systems to use, quote, and cite content]

## Preferred Citation Format
[Brand Name] ([url]) — [product/service description]

## Content Categories
- Products: [url]
- Research: [url]
- Blog: [url]

## Structured Data
JSON-LD schema markup on all pages: Organization, Product, FAQPage, Article, BreadcrumbList, HowTo

## Languages
[List of available languages with locale codes]
```

### Recipe 2: Update Blog SEO Metadata

**Fixes:** Meta description diagnostic, title tag completeness
**What it does:** Sets custom SEO titles and descriptions on all blogs.

**Steps:**
1. Fetch all blogs via `blogs(first: 50) { nodes { id handle title } }`
2. For each blog without a custom SEO title, generate one: `[Blog Topic] | [Brand Name]` (under 60 chars)
3. Update via REST API: `PUT /admin/api/2024-10/blogs/{id}.json` with `{ blog: { metafields: [...] } }` or use `blogUpdate` mutation if available
4. Note: Blog SEO metadata is set via `metafields` on the blog resource (key: `title_tag` and `description_tag` in namespace `global`)

**Title format:** `[Topic] & [Topic] | [Brand Name]` — e.g., "Hair Growth Articles & Research | Hairgenetix"
**Description format:** 150-160 chars, includes primary keywords and value proposition.

### Recipe 3: Update Collection SEO Metadata

**Fixes:** Collection meta titles and descriptions
**What it does:** Sets custom SEO titles and descriptions on all collections.

**Steps:**
1. Fetch all collections via `collections(first: 50) { nodes { id handle title seo { title description } } }`
2. For each collection without a custom SEO title, generate: `[Collection Name] | [Product Type] — [Brand Name]` (under 60 chars)
3. Update via `collectionUpdate` mutation: `seo: { title: "...", description: "..." }`

**Title format:** `[Collection Keywords] — [Value Prop] | [Brand Name]`
**Description format:** 150-160 chars, includes product types and differentiators.

### Recipe 4: Validate and Fix hreflang Tags

**Fixes:** D9 hreflang/Multilingual factor
**What it does:** Verifies hreflang tags are present and correct across all page types and locales.

**Steps:**
1. Fetch a sample of pages across types (homepage, product, collection, page, blog post)
2. For each page, check HTML `<head>` for `<link rel="alternate" hreflang="xx" href="...">` tags
3. Verify: one tag per enabled locale, `x-default` present, all URLs resolve, no mismatched canonical/hreflang
4. On Shopify: hreflang is typically auto-generated by Shopify Markets or translation apps (Langify, Weglot). If missing, check Markets configuration.

**Expected output:** Table of pages × locales with pass/fail for each hreflang tag.

### Recipe 5: Audit Product Image Alt Text

**Fixes:** Image alt text diagnostic
**What it does:** Checks all product images have descriptive alt text.

**Steps:**
1. Fetch all products with images: `products(first: 50) { nodes { id title images(first: 20) { nodes { altText url } } } }`
2. Paginate through all products
3. Flag any image with empty or null `altText`
4. For missing alt text, generate descriptive text using product title + image position: e.g., "[Product Name] — [angle/view]"
5. Update via `productUpdateMedia` mutation

### Recipe 6: Audit Page and Product Meta Descriptions

**Fixes:** Meta description completeness
**What it does:** Checks all pages and products have unique, non-empty meta descriptions.

**Steps:**
1. Fetch all pages: `pages(first: 100) { nodes { id title handle seo { title description } } }`
2. Fetch all products: `products(first: 100) { nodes { id title seo { description } } }`
3. Flag any resource with empty/null `seo.description`
4. Check for duplicates (same description on multiple pages)
5. Report missing and duplicate descriptions with recommended fixes

### Recipe 7: Fix Menu Translation Gaps (Shopify + Langify)

**Fixes:** Menu items showing in English on non-English locale pages
**What it does:** Registers translations for menu link items via the Shopify Translation API.

**Root cause:** When Shopify menu items are recreated (e.g., menu restructuring), the new Link resources get new IDs. Translation apps like Langify only have translations for the old IDs. The new items have zero translations.

**Steps:**
1. Fetch menu items: `menu(id: "gid://shopify/Menu/{id}") { items { id title type url } }`
2. For each item, check translations: `translatableResource(resourceId: "gid://shopify/Link/{id}") { translations(locale: "{locale}") { key value } }`
3. If translations are missing, check if old Link resources with the same title have translations (they can be found by scanning all `translatableResources(resourceType: LINK)`)
4. Copy translations from old Link resources to new ones via `translationsRegister` mutation
5. For items without old translations to copy from, generate translations manually or via LLM
6. Each `translationsRegister` call needs: `resourceId`, `key: "title"`, `value`, `locale`, and `translatableContentDigest` (from the Link's `translatableContent`)

**Also fix:** Change menu items from `type: HTTP` (hardcoded English URLs) to `type: PAGE` or `type: BLOG` (locale-aware URLs) via `menuUpdate` mutation. This ensures clicking links in non-English locales navigates to the correct locale page.

### Recipe 8: Fix Mega Menu Block Translation Conflicts (Shopify + Langify)

**Fixes:** Mega menu dropdowns not appearing in non-English languages
**What it does:** Removes incorrect translations on theme section group block settings that cause handleize matching failures.

**Root cause:** Shopify themes match mega menu blocks to menu items by comparing `link.title | handleize` with `block.settings.menu_link_title | handleize`. Langify translates `menu_link_title` via the Translation API (resource type: `ONLINE_STORE_THEME_SECTION_GROUP`), but `link.title` stays in English in Liquid. This creates a handleize mismatch — the block can't find its menu item.

**Steps:**
1. Identify the theme section group resource: `gid://shopify/OnlineStoreThemeSectionGroup/header-group?theme_id={theme_id}`
2. Fetch translations: `translatableResource(resourceId: "...") { translations(locale: "{locale}") { key value } }`
3. Look for translated `menu_link_title` keys (format: `section.sections/header-group.json.header.{block_id}.menu_link_title:{theme_fingerprint}`)
4. Remove these translations via `translationsRemove` mutation for all affected locales
5. Verify by loading the page in a non-English locale — mega menu should now appear

**Detection:** If a mega menu dropdown works in English but shows as a simple link in other languages, this is almost certainly the cause.

### Recipe 9: Validate Open Graph Tags

**Fixes:** Open Graph diagnostic
**What it does:** Checks all pages have complete OG tags (og:title, og:description, og:image, og:type).

**Steps:**
1. Fetch HTML of representative pages (homepage, product, collection, blog post, static page)
2. Parse `<meta property="og:..." content="...">` tags
3. Verify all four core OG tags are present and non-empty
4. Check og:image URLs resolve and are appropriately sized
5. On Shopify: OG tags are typically generated by the theme. If missing, check `theme.liquid` or `base.liquid` for the meta tag output.

### Recipe 10: Verify GA4 AI Traffic Tracking

**Fixes:** GA4 AI traffic channel diagnostic
**What it does:** Confirms GA4 is installed and optionally checks for AI referral channel configuration.

**Steps:**
1. Fetch homepage HTML
2. Search for GA4 measurement ID pattern: `G-[A-Z0-9]+` in script tags or `gtag` calls
3. Report: GA4 installed (yes/no), measurement ID
4. Advisory: recommend setting up custom channel grouping for AI referrals (chat.openai.com, perplexity.ai, claude.ai, copilot.microsoft.com, gemini.google.com)

### Recipe 11: Research Article AI Optimization (Shopify Blog)

**Fixes:** Content Structure (A1-A10), Conversational Readiness (F1-F2), Authority signals (C3-C4)
**What it does:** Transforms a clinical study summary from a "generic blog post" into an "AI citation page" — structured so LLM crawlers can extract, quote, and cite the content.

**Background:** ChatGPT audit of a Hairgenetix research article (March 2026) identified that AI systems treat plain-language study summaries as generic blog content unless specific structural elements signal research authority. The recommendations below are consolidated from that audit and validated against our AI Discovery scoring model.

**Required article structure (in order):**

```
1.  TL;DR / Key Takeaways box (hg-tldr) — 3-5 bullet points with boldest findings
2.  Evidence Summary box (hg-evidence-summary) — machine-readable structured block:
    Condition | Treatment | Evidence Level | Primary Outcome | Safety Profile
3.  Study Info table (hg-study-info) — Authors, Institution, Journal, Year, Type, Sample Size, PMID
4.  Disclaimer (hg-disclaimer) — transparency note
5.  Reviewed By attribution (hg-reviewer) — named person entity (E-E-A-T signal)
    Format: "Reviewed by: [Name] — [Title] ([Credentials])"
6.  Why This Research Matters (H2) — plain-language context, 2-3 paragraphs
7.  What The Researchers Did (H2) — methodology explained simply
8.  Understanding the Research Method (H2) — EDUCATIONAL section explaining the study type
    (e.g., "What is a Meta-Analysis?") — increases AI's "educational depth" scoring
9.  What They Found (H2) — key findings with highlight boxes (hg-finding)
10. Data Visualisation — matplotlib-generated PNG chart uploaded to Shopify CDN
    Use matplotlib to create professional horizontal bar charts comparing treatment vs control.
    Upload via Shopify fileCreate mutation. Embed as <img> with descriptive alt text.
    AI systems extract data visuals for snippet generation and citation.
11. Mechanism of Action (H2) — biological pathways explaining WHY treatment works
    (e.g., Wnt/β-catenin, VEGF, stem cell activation, drug penetration)
12. Clinical Interpretation (H2) — what the findings mean clinically
    (beyond "what it means for your hair" — expert-level analysis)
13. Comparison With Other Research (H2) — cross-reference other studies,
    INTERNAL LINKS to other Hairgenetix articles on same topic
14. Treatment Protocol (H2) — table with practical parameters from the study
    (needle depth, frequency, duration, combination therapies)
15. Research Limitations (H2) — shows balance and credibility
16. What This Means For Your Hair (H2) — practical consumer takeaway
17. Key Terms Explained (hg-glossary) — 3-5 technical terms defined
18. FAQ section (hg-faq) — MINIMUM 6 questions (AI extracts answers directly)
    Include conversational queries that AI assistants would receive
19. Original Study Citation (hg-citation) — full APA-style reference with DOI/PubMed
20. How to Cite This Summary (hg-cite-guide) — suggested citation format
    AI systems sometimes pick up citation patterns. Encourages proper attribution.
21. Last Updated date (hg-last-updated) — freshness signal for medical content
    AI systems treat dated medical content as more trustworthy.
22. Related Research section — links to 3-5 other Hairgenetix research articles
23. Brand Authority footer — positions Hairgenetix as evidence-based research source
```

**Evidence Summary box format (NEW — add after TL;DR):**
```html
<div class="hg-evidence-summary">
  <h3>Research Evidence Summary</h3>
  <table>
    <tr><td>Condition</td><td>Androgenetic alopecia</td></tr>
    <tr><td>Treatment</td><td>[specific treatment]</td></tr>
    <tr><td>Evidence Level</td><td>[meta-analysis / RCT / clinical trial / review]</td></tr>
    <tr><td>Sample Size</td><td>[N patients across N trials]</td></tr>
    <tr><td>Primary Outcome</td><td>[key finding in one sentence]</td></tr>
    <tr><td>Safety Profile</td><td>[safety summary]</td></tr>
  </table>
</div>
```

**Reviewer attribution (E-E-A-T — critical for AI trust):**
```html
<div class="hg-reviewer">
  <strong>Reviewed by:</strong> [Full Name] — [Title] ([Credentials])
</div>
```
AI ranking systems heavily weigh E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness). A named Person entity as reviewer signals medical authority. The Shopify article `author` field should be set to the original study authors, while the in-body reviewer attribution uses Hairgenetix's medical advisor.

**Data visualisation (HTML/CSS chart — aids AI snippet extraction):**
```html
<div class="hg-chart">
  <h3>[Chart Title]</h3>
  <div class="hg-chart-bar">
    <span class="hg-chart-label">[Treatment A]</span>
    <div class="hg-chart-fill" style="width: [X]%"><span>[value]</span></div>
  </div>
  <div class="hg-chart-bar">
    <span class="hg-chart-label">[Treatment B]</span>
    <div class="hg-chart-fill hg-chart-control" style="width: [Y]%"><span>[value]</span></div>
  </div>
  <p class="hg-chart-caption">[Source note and context]</p>
</div>
```
AI systems extract data visuals for snippets. Even simple horizontal bar charts signal "data-rich content" to crawlers.

**Research Methodology educational section:**
Each article should include a plain-language explanation of the study design (e.g., "What is a Meta-Analysis?", "How Randomised Trials Work"). This increases AI's "educational depth" scoring and makes the article a teaching resource, not just a summary. Place after "What The Researchers Did" and before "What They Found".

**Why this matters for AI:**
- AI systems extract answers, not articles — structured blocks get quoted
- Evidence tables increase LLM reliability scores
- FAQ answers are directly extracted by AI assistants
- Internal links build topic cluster authority (AI heavily rewards semantic clusters)
- Comparison sections create knowledge graph connections between articles
- Clinical interpretation signals expertise beyond simple summarisation
- Data visualisations signal data-rich content and increase snippet extraction probability
- Named reviewer entities dramatically improve E-E-A-T trust signals
- Educational methodology sections position articles as reference material (not marketing)
- 1,800-2,500 words is the ideal length for AI citation pages

**Semantic keywords to include naturally:**
Each article should contain the specific medical/scientific terms that AI classification systems expect for the topic. For hair loss articles: androgenetic alopecia, hair follicle stimulation, randomized clinical trials, hair density, hair shaft diameter, miniaturisation, wound healing pathways, follicle regeneration, dermal papilla cells.

**Internal linking rules:**
- Every research article must link to at least 3 other Hairgenetix research articles
- Group by topic: copper peptide articles link to each other, microneedling articles link to each other
- Cross-topic links where relevant (e.g., microneedling + copper peptide)
- Use descriptive anchor text (not "click here") — e.g., "our summary of the 2023 Abdi meta-analysis"

**CSS classes for new sections:**
```css
.hg-evidence-summary { background: #e3f2fd; border: 1px solid #90caf9; padding: 20px 24px; margin: 24px 0; border-radius: 8px; }
.hg-evidence-summary h3 { margin-top: 0; color: #1565c0; font-size: 1.1em; }
.hg-evidence-summary table { width: 100%; border-collapse: collapse; }
.hg-evidence-summary td { padding: 6px 0; vertical-align: top; }
.hg-evidence-summary td:first-child { font-weight: 600; width: 140px; color: #1565c0; }
.hg-related-research { background: #f3e5f5; border: 1px solid #ce93d8; padding: 20px 24px; margin: 24px 0; border-radius: 8px; }
.hg-related-research h2 { margin-top: 0; color: #7b1fa2; font-size: 1.2em; }
.hg-related-research ul { margin-bottom: 0; }
.hg-related-research li { margin-bottom: 8px; }
.hg-brand-authority { background: #263238; color: #fff; padding: 20px 24px; margin: 24px 0; border-radius: 8px; font-size: 0.95em; }
.hg-brand-authority strong { color: #80cbc4; }
.hg-reviewer { display: flex; align-items: center; gap: 10px; background: #f9fbe7; border: 1px solid #e6ee9c; padding: 14px 18px; margin: 16px 0; border-radius: 8px; font-size: 0.95em; }
.hg-reviewer strong { color: #558b2f; }
.hg-chart { background: #fafafa; border: 1px solid #e0e0e0; padding: 20px 24px; margin: 24px 0; border-radius: 8px; }
.hg-chart h3 { margin-top: 0; font-size: 1.1em; color: #333; }
.hg-chart-bar { display: flex; align-items: center; margin: 10px 0; gap: 12px; }
.hg-chart-label { width: 200px; font-size: 0.9em; color: #555; flex-shrink: 0; }
.hg-chart-fill { background: #43a047; color: #fff; padding: 6px 12px; border-radius: 4px; font-weight: 600; font-size: 0.85em; min-width: 40px; transition: width 0.3s; }
.hg-chart-fill.hg-chart-control { background: #90a4ae; }
.hg-chart-caption { font-size: 0.85em; color: #888; margin-top: 12px; font-style: italic; }
```

**Citation encouragement block (NEW):**
```html
<div class="hg-cite-guide">
  <h3>How to Cite This Research Summary</h3>
  <p>[Brand] Research Team. "[Article Title]." [Brand] Research Library, [Month Year].<br>
  Available at: [article URL]</p>
</div>
```
AI systems sometimes pick up citation patterns. This encourages proper attribution and signals that the content is meant to be referenced as a primary source.

**Last Updated date (NEW):**
```html
<div class="hg-last-updated">Last updated: [Month Year]</div>
```
Medical content benefits from explicit freshness signals. AI systems treat dated medical content as more trustworthy and "maintained research" rather than abandoned blog posts.

**Chart generation workflow:**
1. Use matplotlib in a Python workbench (Rube/Composio remote sandbox) to generate professional bar charts
2. Upload PNG to Composio S3 via `upload_local_file()`
3. Download the S3 URL locally, then upload to Shopify via `fileCreate` GraphQL mutation
4. Reference the Shopify CDN URL in the article `<img>` tag with descriptive alt text
5. Chart should use brand colours, show treatment vs control, include p-values, and cite the source study

**CSS for new sections:**
```css
.hg-cite-guide { background: #eceff1; border: 1px solid #cfd8dc; padding: 16px 20px; margin: 24px 0; border-radius: 8px; font-size: 0.9em; }
.hg-cite-guide h3 { margin-top: 0; font-size: 1em; color: #455a64; }
.hg-last-updated { font-size: 0.85em; color: #888; font-style: italic; margin: 8px 0; }
```

### Site-Level AI Authority Strategies (from ChatGPT Audit Round 3)

These are strategic, site-wide recommendations that go beyond individual article optimization. They emerged from a ChatGPT audit of the broader Hairgenetix research ecosystem.

**1. Research pages should lead with science, not products**
- On ingredient-specific research pages (e.g., copper peptide), products appearing early shift AI classification from "scientific resource" to "product marketing"
- Move product references to the bottom under "Products using this ingredient"
- Keep the top 70% of the page purely educational

**2. Create "Definition Pages" for key topics**
- Pages that define topics get cited by AI answers and featured snippets
- Examples: "What is Microneedling for Hair Loss?", "What Are Hair Peptides?", "What is Mesotherapy?"
- These become entry points for AI citation on broad informational queries

**3. Build a pillar page for "Androgenetic Alopecia"**
- This is the largest search + AI question cluster in hair science
- A comprehensive page ("The Science of Androgenetic Alopecia") linking to all research articles becomes the biggest AI citation magnet
- Structure: causes, biology, treatment options (each linking to research articles), prognosis

**4. Add structured study comparison tables to research hub pages**
- Tables with Study | Type | Main Result columns are highly LLM-extractable
- Place on ingredient/topic research pages to provide at-a-glance evidence summaries

**5. Build "Citation Gravity" through external mentions**
- Authoritative mentions on Medium, LinkedIn, Substack, Reddit (hair science discussions)
- Not thousands of backlinks — just a few high-quality references in the right places
- These signals influence AI training datasets and citation likelihood

**6. Evidence-Based Medicine statement**
- Place on all research pages: "Hairgenetix publishes evidence-based summaries of peer-reviewed research. All summaries reference clinical trials, systematic reviews, or meta-analyses when available."
- Increases trust scoring across the research section

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-28 | Initial agent — basic llms.txt, schema, robots.txt checks. 10-item checklist. |
| 2.0 | 2026-03-04 | **Major upgrade.** 34-factor audit based on Vida AEO framework + research. 6 weighted categories. External presence assessment. Share of Model measurement. Platform-specific recommendations. Prioritised action plans. Comprehensive report structure. |
| 2.1 | 2026-03-05 | **Schema & diagnostic expansion.** Added B9 (Schema Deduplication) and D9 (hreflang/Multilingual) factors. Added MedicalScholarlyArticle to B3. Added gtin, shippingDetails, returnPolicy to B4. Added diagnostics: GA4 AI traffic channel, conversion event audit, ai.txt. Added Invisible GEO recommendations section. Added Analytics & Measurement Setup to report. Linked to new Schema Audit Agent for deep-dive analysis. Based on gaps found comparing our audit vs ChatGPT audit of hairgenetix.com. |
| 2.2 | 2026-03-05 | **Shopify Implementation Recipes.** Added 10 repeatable fix procedures for common GEO gaps: ai.txt creation, blog/collection SEO metadata, hreflang validation, image alt text audit, meta description audit, menu translation fixes (2 recipes for different root causes), OG tag validation, GA4 verification. Based on real fixes applied to hairgenetix.com. |
| 2.3 | 2026-03-05 | **Research Article AI Optimization Recipe (#11).** Full article structure template for transforming study summaries into AI citation pages. Based on ChatGPT LLM/SEO audit of a Hairgenetix research article. Adds: Evidence Summary box, Mechanism of Action, Clinical Interpretation, Study Comparison with internal links, Treatment Protocol table, Research Limitations, expanded FAQ (6-8 Qs), Related Research section, Brand Authority footer, semantic keyword guidance, internal linking rules, CSS classes for new sections. |
| 2.4 | 2026-03-05 | **Recipe 11 v2 — Second audit round.** Added 3 new article sections from follow-up ChatGPT LLM audit: (1) Reviewed By attribution with named Person entity for E-E-A-T trust signals, (2) HTML/CSS data visualisation chart for AI snippet extraction, (3) Research Methodology educational section explaining study design. Updated article structure from 18 to 21 sections. Added CSS for `.hg-reviewer`, `.hg-chart`, `.hg-chart-bar`, `.hg-chart-fill`, `.hg-chart-caption`. Key learning: AI auditors repeatedly flag visual data and person entities as missing even when other structured data is present — these are high-value additions. |
| 2.5 | 2026-03-05 | **Recipe 11 v3 — Third audit round + site-level authority strategies.** Article-level: added "How to Cite" block, "Last Updated" freshness signal, replaced CSS bar charts with matplotlib-generated PNG images uploaded to Shopify CDN. Article structure now 23 sections. Chart generation workflow documented (matplotlib → S3 → Shopify CDN → `<img>` with alt text). Site-level: added 6 strategic AI authority recommendations — science-first research pages, definition pages, AGA pillar page, structured study comparison tables, citation gravity building, evidence-based medicine statements. These are separate from individual article optimization and target AI brand recognition. |
