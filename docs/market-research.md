# SEO Toolkit — Market Research

Last updated: 2026-03-01

---

## Market Overview

The global SEO software market is valued at approximately $5.2 billion (2025) and projected to grow to $10-12 billion by 2030, driven by increasing digital adoption and the complexity of modern search.

### Why the Market Is Growing

1. **Every website needs SEO** — There are 200M+ active websites. Most are invisible to search engines because they do not invest in SEO.
2. **Search is fragmenting** — Google is no longer the only search engine that matters. AI-powered search (ChatGPT, Perplexity, Gemini, Claude) is changing how people find information. Businesses now need to optimise for both traditional and AI search.
3. **SEO is getting more complex** — Core Web Vitals, E-E-A-T, AI overviews, zero-click searches, featured snippets — the rulebook keeps expanding. Small businesses cannot keep up manually.
4. **Content marketing depends on SEO** — Companies investing in content marketing (blogs, articles, guides) need SEO to make that content discoverable. Without it, content sits unseen.

### Market Segments

| Segment | Description | Typical Spend | Key Players |
|---------|------------|---------------|-------------|
| Enterprise SEO platforms | Full-suite tools for large companies | $500-10,000+/month | Ahrefs, SEMrush, BrightEdge, Conductor |
| SMB SEO tools | Simplified tools for small businesses | $50-250/month | SE Ranking, Moz, Ubersuggest, Mangools |
| Technical SEO / Crawlers | Site audit and technical analysis | $100-500/year | Screaming Frog, Sitebulb, Lumar |
| Content SEO tools | Content optimisation and writing assistance | $50-400/month | Surfer SEO, Clearscope, Frase, MarketMuse |
| Rank tracking specialists | Position monitoring only | $20-100/month | AccuRanker, SERPWatcher, Wincher |
| AI SEO tools (emerging) | AI-powered analysis and automation | $50-500/month | Few exist yet — this is the gap |

---

## Key Market Trends (2025-2027)

### 1. AI Search Engines Are Changing Discovery

ChatGPT, Perplexity, Gemini, and Claude are now answering questions that used to require Google searches. This creates a new optimisation challenge: how do you ensure AI engines cite your content?

**Implications for us:** The AI Discovery Agent addresses this directly. No major competitor has a dedicated AI search optimisation feature.

### 2. AI-Generated Content Saturation

The volume of AI-generated content has exploded since 2023. Google's response has been to emphasise E-E-A-T (Experience, Expertise, Authority, Trust) and reward genuinely useful content over keyword-stuffed filler.

**Implications for us:** Our Content Writer Agent must focus on quality over quantity. Integration with real expertise (Malcolm's book content, original research) is the differentiator.

### 3. Zero-Click Searches

Over 60% of Google searches now end without a click — the answer appears directly in search results (featured snippets, knowledge panels, AI overviews). Websites need to optimise for visibility in these features, not just traditional blue links.

**Implications for us:** Agents need to track SERP features, not just position rankings. Schema markup and structured data (AI Discovery Agent) become critical.

### 4. Programmatic SEO

Companies are using data + templates to generate thousands of targeted pages (e.g., "best [X] in [city]"). This scales SEO but requires good tooling to manage.

**Implications for us:** Our multi-agent architecture is well-suited for programmatic SEO — Keywords Agent identifies opportunities, Content Writer generates pages at scale.

### 5. Link Building Is Getting Harder

Google continues to devalue manipulative link building. The emphasis is shifting to earned links through genuine PR, unique data, and linkable assets.

**Implications for us:** Our Link Builder Agent follows DEC-006 — earned links only. This is the right strategic direction as the market moves away from volume-based link building.

---

## Competitive Landscape Summary

| Competitor | Price Range | Strengths | Key Weakness |
|-----------|-----------|-----------|-------------|
| Ahrefs | $99-999/mo | Best backlink database, excellent content explorer | Expensive, no automation, steep learning curve |
| SEMrush | $119-449/mo | Most comprehensive feature set, good advertising tools | Bloated UI, expensive, analysis paralysis |
| Moz | $49-599/mo | Domain authority metric is industry standard, good community | Smaller database than Ahrefs/SEMrush, slow crawler |
| SE Ranking | $31-119/mo | Affordable, good rank tracking, all-in-one | Smaller backlink database, less brand recognition |
| Screaming Frog | $259/year | Best technical crawler, fast, thorough | Desktop app only, technical SEO only, no keywords/content |
| Surfer SEO | $59-239/mo | Best content optimisation, NLP-driven | Content only — no technical SEO, no link building |
| Ubersuggest | $12-40/mo | Cheapest, Neil Patel brand recognition | Limited data, often inaccurate, basic features |

**Full competitor analysis:** See `docs/competitor-analysis.md`

---

## The Gap: AI-Agent-Driven SEO

Every tool in the current market is a **dashboard** — it shows you data and expects you to take action. Some have AI features (content suggestions, keyword recommendations), but these are AI-assisted, not AI-driven.

**What does not exist yet:**
- 8 specialised AI agents that work together autonomously
- Agents that find problems, create solutions, and suggest next steps — not just report data
- AI Discovery optimisation as a first-class concern
- A system that gets smarter over time as it learns what works for each client
- True multi-client architecture where agencies manage many sites from one platform

This is the gap we are filling.

---

## Target Customer Profiles

### Profile 1: The Solo Content Creator
- Runs a blog or niche website
- Knows SEO matters but does not have time to learn the tools
- Currently does SEO manually or not at all
- Budget: $50-100/month
- **Our value:** Automated SEO that works without expertise

### Profile 2: The Small Business Owner
- Has a business website with 10-100 pages
- Hires freelancers for occasional SEO work
- Frustrated by inconsistent results and high agency fees
- Budget: $100-300/month
- **Our value:** Consistent, automated SEO at a fraction of agency cost

### Profile 3: The Digital Marketing Agency
- Manages SEO for 5-50 client websites
- Uses Ahrefs/SEMrush but needs custom reporting and automation
- Time is the bottleneck — too many clients, too many tasks
- Budget: $300-1,000/month
- **Our value:** AI agents handle the repetitive work, freeing analysts for strategy

---

## Data Sources Available

The SEO data market has several providers we can use:

| Provider | Best For | Access Method | Cost Model |
|----------|---------|---------------|-----------|
| DataForSEO | Keywords, SERPs, backlinks, on-page data | REST API | Pay-per-call (~$0.001-0.01 per request) |
| Google Search Console | Real search performance data | OAuth API | Free |
| SE Ranking | Rank tracking, site audit | REST API | Monthly subscription |
| SEMrush / Ahrefs | Competitor research, backlink audit | Via Rube MCP | Included in Rube subscription |
| Google PageSpeed Insights | Core Web Vitals, performance | REST API | Free |
| Schema.org validators | Structured data validation | REST API | Free |

---

## Change Log

| Date | Change |
|------|--------|
| 2026-03-01 | Market research document created. Market overview, trends, competitive landscape, target profiles, data sources documented. |
