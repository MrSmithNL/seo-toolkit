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

The agent scores websites on a **0-100 scale** across **6 weighted categories** containing **34 auditable factors** plus **7 diagnostic factors** (advisory, no score impact). Based on the Vida AEO framework, adapted with findings from the Princeton GEO study, Qwairy citation analysis (118,101 AI answers), Previsible session study (1.96M sessions), and Omniscient Digital citation research (23,000+ citations).

### Category Weights

| # | Category | Weight | # Factors | What It Measures |
|---|----------|--------|-----------|-----------------|
| A | Content Structure & Extractability | **30%** | 10 | Can AI systems easily extract, quote, and cite your content? |
| B | Schema & Structured Data | **20%** | 8 | Does your site speak the machine-readable language AI relies on? |
| C | Authority & Trustworthiness | **20%** | 8 | Does AI have enough evidence to trust your brand? |
| D | Technical Accessibility | **15%** | 8 | Can AI crawlers access, read, and understand your site? |
| E | Freshness & Recency | **10%** | 4 | Is your content current enough for AI to confidently cite? |
| F | Conversational Readiness | **5%** | 3 | Does your content match how AI formulates answers? |

**Total: 100% across 6 categories, 34 scored factors + 7 diagnostic factors.**

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
| B3 | Article Schema | 0.15 | Do blog posts and articles have Article/NewsArticle schema with author, datePublished, dateModified? | 10 = all articles marked up correctly; 0 = missing |
| B4 | Product Schema | 0.10 | Do product pages have Product schema with offers, pricing, availability, reviews? (E-commerce sites only — scored as N/A for non-commerce) | 10 = complete product schema; 0 = missing |
| B5 | Author / Person Schema | 0.10 | Is there Person schema for authors/experts with credentials, sameAs links, and affiliation? Feeds E-E-A-T signals. | 10 = complete author schema linked from articles; 0 = missing |
| B6 | HowTo Schema | 0.10 | Do step-by-step guides have HowTo schema? This content type is easily extractable by AI. | 10 = all how-to content marked up; 0 = missing |
| B7 | Review / AggregateRating Schema | 0.10 | Do pages with reviews/testimonials have proper Review or AggregateRating schema? Social proof signals for AI. | 10 = all review content marked up; 0 = missing |
| B8 | Schema-Content Alignment | 0.15 | Does the schema data actually match the visible page content? Misaligned schema is worse than no schema — it signals untrustworthiness. | 10 = perfect alignment; 0 = mismatches found |

**How to audit:** Fetch HTML of key pages. Parse JSON-LD blocks. Validate against Schema.org specs. Cross-check schema values against visible content. Use Google Rich Results Test for validation.

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

**Additional technical checks (no score impact — diagnostic only):**
- llms.txt file presence, format compliance, and content quality
- llms-full.txt presence (extended version)
- Open Graph tags on all pages
- Canonical URLs
- Title tags and meta descriptions
- H1 validation
- Image alt text
- Heading structure compliance (H1 > H2 > H3)

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
### Immediate (this week)
### Short-term (this month)
### Medium-term (next quarter)
### Long-term (ongoing)

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

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-28 | Initial agent — basic llms.txt, schema, robots.txt checks. 10-item checklist. |
| 2.0 | 2026-03-04 | **Major upgrade.** 34-factor audit based on Vida AEO framework + research. 6 weighted categories. External presence assessment. Share of Model measurement. Platform-specific recommendations. Prioritised action plans. Comprehensive report structure. |
