# E-001 Research & Strategy — Competitive Deep-Dive
## Autonomous Content Engine | PROD-001 / AISOGEN

**Research date:** 2026-03-15
**Scope:** E-001 capability area — Keyword Research, Topic Clustering, Search Intent Classification, SERP Analysis, Competitor Content Analysis, Content Gap Identification, Content Calendar / Planning
**Focus competitors:** Frase.io, SEO.ai, SurferSEO, Semrush ContentShake/Content Toolkit
**Methodology:** Official docs, help centres, API docs, third-party reviews (G2, Capterra), comparative review articles
**Status:** Complete — ready for Gate 1 review

---

## Table Stakes Summary (before the deep-dive)

| Feature | Frase.io | SEO.ai | SurferSEO | Semrush ContentShake |
|---------|----------|--------|-----------|----------------------|
| Keyword research | Yes (add-on $35/mo for volume data) | Yes (autonomous) | Yes (native) | Yes (26B+ DB via Keyword Magic) |
| Topic clustering | Yes (NLP-based from SERP) | Yes (site-crawl based) | Yes (Topical Map w/ GSC) | Yes (Keyword Strategy Builder) |
| Search intent classification | Yes (SERP-inferred) | Yes | Yes (per-cluster) | Yes (explicit filter: info/nav/comm/trans) |
| SERP analysis | Yes (top 20, 500+ signals) | Partial (benchmarking only) | Yes (top 50, 500+ signals) | Yes (top 10 via SEO Content Template) |
| Competitor content analysis | Yes (content gaps, topic coverage) | No (not documented) | Yes (Topical Map competitor view) | Yes (Keyword Gap tool) |
| Content gap identification | Yes (topic score vs competitors) | Yes (site-crawl gaps) | Yes (covered/uncovered in Topical Map) | Yes (Keyword Gap + Topic Research) |
| Content calendar / planning | Partial (article queue, no calendar UI) | Yes (full calendar with email preview) | Partial (article list from Topical Map) | Partial (content dashboard, no calendar per se) |

---

## Dimension 1: Features & Functions

### Frase.io

**Positioning:** "Agentic SEO & GEO Platform" — strongest autonomous research in the set. Positioned as a research-first, then optimise tool.

| Feature | What it does | Free vs Paid | User praise | User complaints |
|---------|-------------|-------------|-------------|----------------|
| SERP Research | Fetches top 20 organic results for any keyword. Extracts word count, domain authority, H1/H2 structure, backlinks, images per page | All paid plans | "Saves 4 hours of manual SERP work per brief" | "Only shows top 20, not 50 like Surfer" |
| Topic Score | Real-time 0-100 score comparing your draft's topic coverage vs top-ranking pages using NLP | All paid plans | "Green bar makes it obvious what to add" | "Score can be gamed by keyword stuffing" |
| Content Brief Builder | Auto-generates outlines from SERP: headings, PAA questions, related searches, recommended word count | All paid plans | "Point-and-click to add headings from SERP — fastest brief tool in market" | "Briefs need heavy human editing to make engaging" |
| People Also Ask integration | Surfaces PAA questions from Google, Quora, Reddit for topic depth | All paid plans | "Multi-source questions better than competitors" | None major |
| Keyword Research (add-on) | Search volume, keyword difficulty, keyword suggestions with intent tags | $35/month add-on (separate from base plan) | "Useful when bundled" | "Hidden cost — should be included. Makes base plan feel incomplete for keyword research" |
| Competitor Gap Analysis | Compares topic coverage across top-ranking competitor pages | All paid plans | "Shows exactly which topics competitors cover that you don't" | "No backlink gap analysis" |
| AI Visibility Tracking | Tracks brand/content mentions across ChatGPT, Perplexity, Claude, Gemini, Grok, Copilot, DeepSeek, Google AI | Starter: 2 platforms; Scale: 5; Enterprise: 8 | "Unique GEO feature — ahead of competition" | "Only 2 platforms on entry plan is limiting" |
| GEO Scoring | Scores content for AI search citation readiness | All paid plans | "Forward-looking" | "Still early — criteria unclear" |
| Site Audit | Crawls site, flags technical and content issues programmatically | All paid plans | "50 audit pages/month on starter is enough for SMBs" | "Enterprise audit coverage still limited" |
| AI Agent (80+ skills) | Handles research, writing, optimisation, publishing autonomously | All paid plans | "Single agent replaces 4 tools" | "Output still needs human review" |

**Pricing:** $39/mo (Starter, 1 user) → $129/mo (Professional, 3 users) → $299/mo (Scale, 5 users) → Enterprise (custom). 7-day free trial, no credit card. Keyword research add-on: $35/mo extra. API access add-on: $40/mo.

**Sources:**
- https://www.frase.io/features/seo-research
- https://www.frase.io/integrations
- https://www.frase.io/pricing
- https://www.frase.io/features/api-integrations
- https://searchatlas.com/blog/frase-review/
- https://aiflowreview.com/frase-review-2025/

---

### SEO.ai

**Positioning:** "AI SEO — done for you by AI." Most autonomous tool in the set. Built AI-first from 2022 (Danish startup). Emphasis on hands-off operation.

| Feature | What it does | Free vs Paid | User praise | User complaints |
|---------|-------------|-------------|-------------|----------------|
| Autonomous keyword research | AI finds keywords using search data + topic relevance. Long-tail opportunity finder | Paid ($169/mo+) | "Reduces time to keyword list significantly" | "Too generic — not relevant to specific business niche. Keyword suggestions not usable" |
| Site-crawl content gap finder | Crawls your entire website to identify missing content topics | Paid | "Good for identifying obvious gaps" | "Can't customise the crawl depth or gap criteria" |
| Content calendar | Full scheduling interface. User sets frequency (weekly to daily). Email preview before publish | Paid | "Set-and-forget publishing pipeline" | "Limited manual override options" |
| SEO benchmarking | Compares each content piece against ranking pages for the target keyword | Paid | "Useful for post-publish tracking" | "Not detailed enough for competitive analysis" |
| Autonomous content pipeline | Full pipeline: keyword analysis → publication planning → research → writing → internal linking → image generation → publishing | Paid | "Most autonomous tool tested — genuinely hands-off" | "Quality inconsistent — robotic phrasing, keyword stuffing" |
| CMS auto-publish | Direct publishing to WordPress, Webflow, Wix, Squarespace, Shopify, Magento | Paid | "Works with any CMS — broadest integration list" | "Shopify integration not as polished as WordPress" |
| Missing Keywords metric | Shows which keywords top-ranking pages use that your content lacks | Paid | "Helpful for gap-filling during optimisation" | "Limited contextual explanation of why to add them" |
| Competitor content analysis | Not explicitly documented as a standalone feature | N/A | N/A | "No dedicated competitor research dashboard" |

**Pricing:** Starts at $169/month. 10-day free trial. G2 rating: 3.4/5 (8 reviews) — low confidence signal, low review volume.

**Sources:**
- https://seo.ai/
- https://www.g2.com/products/seo-ai/reviews (summarised via search)
- https://medium.com/@timsoulo/best-ai-seo-tools-for-2026 (via search)

---

### SurferSEO

**Positioning:** "Content Score leader." Strongest SERP signal analysis in the set. 500+ on-page signals. Known for quantitative rigour. Recently expanded into AI visibility tracking.

| Feature | What it does | Free vs Paid | User praise | User complaints |
|---------|-------------|-------------|-------------|----------------|
| Keyword Research | Find and evaluate keywords: volume, difficulty, intent, content score benchmark. Location-specific. Relative difficulty adjusted for domain strength | Standard ($99/mo+) | "Domain-adjusted difficulty is more realistic than generic KD" | "Database smaller than Semrush/Ahrefs. No CPC data, no SERP feature data" |
| SERP Analyzer | Breaks down top 50 SERP results across 500+ on-page signals: word count, keyword density, NLP entities, H1/H2 structure, page speed, image count. Correlation analysis | Standard ($99/mo+) | "Most comprehensive SERP analysis in market. 500 signals vs Frase's essentials" | "Correlation ≠ causation. Encourages formulaic, checklist-driven content that harms UX" |
| Topical Map | Visualises site's topical coverage. Shows covered/uncovered clusters. Semantic similarity-based. Requires GSC connection for full accuracy. Refreshes every 14 days. Competitor coverage comparison | Pro ($182/mo+) | "Best visual topical planning tool. GSC integration makes it personalised to my site" | "Requires existing site traffic — useless for new sites. 14-day refresh is slow" |
| Topic Cluster Builder | Groups related keywords by intent into pillar + support article structure | Standard ($99/mo+) | "Fast cluster generation" | "No way to customise cluster definitions" |
| Content Editor | Real-time Content Score (0-100) during writing. Keyword target list. Heading recommendations. Word count guidance | Standard ($99/mo+) | "Industry standard content scoring tool" | "Score optimisation encourages stuffing. Suggestions too prescriptive" |
| Cannibalization Report | Detects keyword cannibalization across existing pages | Pro ($182/mo+) | "Saves manual audit time" | "Only available on Pro tier" |
| AI Visibility Monitoring | Tracks brand/content visibility on ChatGPT, Perplexity, Google AI Overview, Gemini | Standard: ChatGPT only; Pro: ChatGPT + Perplexity + Google + Gemini + AI Overview | "Integrates AISO tracking into the SEO workflow" | "AI prompt tracking limited on standard plan" |
| Topical Authority Score | Measures how well your site covers a topic vs competitors | Pro ($182/mo+) | "Useful for strategy prioritisation" | "Scoring methodology opaque" |

**Pricing:** Standard $99/mo (yearly) → Pro $182/mo → Peace of Mind $299/mo → Enterprise (custom). No free trial (confirmed). 200 tracked pages, 30 article optimisations, 5 AI articles on Standard.

**Sources:**
- https://docs.surferseo.com/en/articles/11891594-keyword-research
- https://docs.surferseo.com/en/articles/9383782-topical-map
- https://docs.surferseo.com/en/articles/7831346-reading-your-results-in-serp-analyzer
- https://surferseo.com/pricing/
- https://searchatlas.com/blog/surfer-seo-review/
- https://thedoublethink.com/frase-vs-surfer/

---

### Semrush ContentShake / Content Toolkit

**Positioning:** "Backed by 26B keyword database." Most data-dense research capability in the set. ContentShake is the AI content layer on top of Semrush's research infrastructure. Recently rebranded to "Content Toolkit."

| Feature | What it does | Free vs Paid | User praise | User complaints |
|---------|-------------|-------------|-------------|----------------|
| Keyword Magic Tool | 26B+ keyword database. Seed → thousands of related keywords. Match modifiers (broad, phrase, exact, related). Left-sidebar group clustering by shared theme | Semrush plan required | "Largest keyword database. Grouped sidebar makes cluster identification fast" | "Overwhelming for non-experts. Requires understanding of match types" |
| Keyword Overview | Detailed per-keyword analysis: volume, trend, KD%, Personal KD% (site-adjusted), CPC, competitive density, SERP features, intent classification | Semrush plan | "Personal KD% adjusted for your domain is more actionable than generic KD" | "Requires knowing which keyword to look up first" |
| Keyword Gap Tool | Compares your keyword profile against up to 5 competitors. Shows: shared, competitor-only, and your-only keywords | Semrush plan | "Best competitive keyword analysis in market — shows exactly where you're losing to competitors" | "Max 5 competitors at once is limiting for broad research" |
| Topic Research Tool | Enter a broad topic → trending subtopics, popular questions, top headlines. Mind-map view | Semrush plan | "Good for content ideation from thin air" | "Ideas sometimes too generic, not always search-relevant" |
| Keyword Strategy Builder | Auto-clusters keyword list into pillar/subtopic hierarchy. One-click clustering | Semrush plan | "Fastest cluster generation" | "Doesn't always cluster semantically correctly" |
| SEO Content Template | Enters top 10 SERP results for target keyword. Generates brief: recommended word count, semantically related keywords, competitor backlink count, SERP feature opportunities | ContentShake ($60/mo or included in Semrush plans) | "Brief quality backed by full Semrush data infrastructure. Saves 6-8 hours of manual research per brief" | "Focused on top 10 only — misses long-tail SERP patterns" |
| SEO Writing Assistant | Real-time Content Score (0-100). Color-coded keyword coverage highlighting. Readability score (Flesch). Tone of voice slider. Passive voice detection. Live updates | ContentShake | "Most detailed real-time feedback during writing" | "Google Docs plugin glitchy on documents >3,000 words" |
| ContentShake AI | Auto-generates full draft with H2/H3 structure in 20-30 seconds. Embeds AI images. One-click WordPress publish | ContentShake $60/mo | "Fastest full draft generation in the set" | "Draft quality requires significant editing. AI images hit-or-miss" |
| Content Calendar / Dashboard | Three workflows: Create from topic/keyword, Optimise existing article, Repurpose article. Topic Finder for trending ideas | ContentShake | "Clean three-option dashboard — easy entry point" | "Not a real calendar — no date scheduling, no editorial workflow" |
| AI Visibility Toolkit | Tracks brand mentions across ChatGPT + Google AI Overviews | Semrush Pro+ | "Integrated with keyword data — shows AI visibility alongside organic" | "Separate product from ContentShake — no unified workflow" |

**Pricing:** ContentShake AI standalone: $60/month (unlimited articles). Full Semrush plans start from $139.95/month (Pro) with ContentShake integrated. ContentShake also available as Semrush app.

**Sources:**
- https://www.semrush.com/blog/how-to-use-semrush-keyword-research/
- https://butterblogs.com/blog/semrush-content-tools-review-2026-a-full-breakdown/
- https://mattrics.com/blog/contentshake-ai/
- https://www.ainvest.com/news/ai-content-revolution-semrush-contentshake-rewriting-seo-future-2025-2506/
- https://selfmademillennials.com/contentshake-ai-review/

---

## Dimension 2: Processes & Workflows

### Frase.io — Workflow

**Start state:** "I have a website and a topic area"
**End state:** "I have a prioritised content brief ready for writing"

| Step | Action | Automated or Manual | Time |
|------|--------|--------------------|----|
| 1 | Enter target keyword | Manual | 30 sec |
| 2 | Frase fetches top 20 SERP results | Automated | ~10 sec |
| 3 | System extracts: word count, H1/H2 structure, backlinks, images, PAA questions, related searches from each result | Automated | ~30 sec |
| 4 | Topic Score calculated: compares your coverage vs competitor average | Automated | Instant |
| 5 | User reviews research sidebar: questions, headings, stats, sources, subtopics | Manual (review) | 5-10 min |
| 6 | Click-to-add headings/questions to build outline in Brief Builder | Manual (click) | 5-15 min |
| 7 | AI drafts content from brief or user begins writing with live Topic Score guidance | Semi-automated | Varies |
| 8 | Optimise: Topic Score drives iteration until green | Semi-automated | 15-30 min |
| 9 | Export to WordPress, Webflow, Sanity, Google Docs, or via API | Automated (click) | 1 min |
| 10 | Google Search Console data tracks performance post-publish | Automated | Ongoing |

**Total steps to prioritised content plan:** 6 manual + 4 automated. Estimated time from keyword to publishable brief: 20-40 minutes per article.

**Key workflow differentiator:** The research sidebar stays visible during writing. Research and writing happen in one window. No context-switching.

**What is NOT automated:** Keyword prioritisation (you decide which keywords to research), editorial strategy (no tool tells you which brief to write first), content calendar (no scheduling layer).

---

### SEO.ai — Workflow

**Start state:** "I have a website URL"
**End state:** "Content is published on my site automatically"

| Step | Action | Automated or Manual | Time |
|------|--------|--------------------|----|
| 1 | Connect website (URL input) | Manual | 5 min |
| 2 | AI crawls site to identify content gaps | Automated | 10-30 min |
| 3 | AI selects target keywords using search data + topic relevance | Automated | Automated |
| 4 | AI performs deep research on each keyword | Automated | Automated |
| 5 | AI writes content: headings, body, internal links, meta, featured image | Automated | Automated |
| 6 | User sets publishing frequency (weekly/daily) and reviews email preview | Manual (settings) | 5 min setup |
| 7 | Auto-publish to CMS (WordPress, Webflow, Shopify, etc.) | Automated | Automated |
| 8 | Performance tracking: clicks, impressions, rankings via GSC integration | Automated | Ongoing |

**Total manual steps:** 2 (initial setup + frequency configuration). Most autonomous pipeline in the set.

**Critical caveat:** Low G2 rating (3.4/5) suggests the automation produces inconsistent quality. "Keywords not relevant to business" is the top complaint — the autonomous keyword selection is the key weakness.

**What is NOT in control:** User has minimal control over which keywords are targeted. The "autonomous" selection is a black box. No transparent keyword research dashboard.

---

### SurferSEO — Workflow

**Start state:** "I have a domain with existing content and GSC connected"
**End state:** "I have a topical map with prioritised article opportunities"

| Step | Action | Automated or Manual | Time |
|------|--------|--------------------|----|
| 1 | Connect Google Search Console | Manual (one-time) | 5 min |
| 2 | Topical Map fetches your GSC keyword data and builds topic cluster map | Automated | 5-15 min |
| 3 | Review hexagon-based visual map: covered vs uncovered topics | Manual (review) | 10-20 min |
| 4 | Select uncovered cluster(s) to target | Manual | 5 min |
| 5 | Enter keyword into SERP Analyzer: analyze top 50 results across 500+ signals | Manual (per keyword) | Automated in ~30 sec |
| 6 | Review correlation chart: identify high-signal factors (word count, entities, etc.) | Manual (review) | 5-10 min |
| 7 | Send cluster to Content Editor → generates Content Score benchmark | Automated | ~1 min |
| 8 | Write/edit with live Content Score guidance | Manual | Writing time |
| 9 | Export to Google Docs or WordPress | Manual (click) | 1 min |

**Total steps to prioritised content plan (Topical Map → brief ready):** Steps 1-7. ~4-6 steps manual, 3 automated. Topical Map is the strongest planning tool but requires existing traffic (Step 1 dependency).

**Limitation:** No automatic brief generation. User must manually construct outline after reviewing SERP data. Frase's outline builder is faster for brief creation.

---

### Semrush ContentShake / Content Toolkit — Workflow

**Start state:** "I have a topic or seed keyword"
**End state:** "I have a clustered content strategy with AI-generated drafts"

| Step | Action | Automated or Manual | Time |
|------|--------|--------------------|----|
| 1 | Enter seed keyword in Keyword Magic Tool | Manual | 30 sec |
| 2 | Filter keyword list by match type, intent, KD%, volume | Manual | 5-15 min |
| 3 | Run Keyword Gap vs up to 5 competitors | Manual | 5 min |
| 4 | Import keyword list into Keyword Strategy Builder | Manual | 1 min |
| 5 | Auto-cluster into pillar/subtopic hierarchy | Automated | ~30 sec |
| 6 | Select target keyword/cluster → SEO Content Template generates brief | Manual (per keyword) | Automated in ~1 min |
| 7 | ContentShake AI generates full draft from brief | Manual (click) | 20-30 sec |
| 8 | SEO Writing Assistant scores draft in real-time; user edits | Semi-automated | 30-60 min |
| 9 | One-click publish to WordPress | Manual (click) | 1 min |

**Total steps to prioritised content plan (keyword → brief):** Steps 1-6. Heavy on manual filtering/decision-making. Richest data at each step but most cognitive load.

**Key workflow differentiator:** Keyword Gap Tool directly identifies competitor rankings gaps before any content brief is created. Most data-rich research entry point.

---

## Dimension 3: User Interfaces & Experience

### Frase.io

**Primary UI pattern:** Split-panel editor. Left: AI research sidebar (competitor SERP data, questions, sources). Right: writing editor. Both panels always visible.

| UI Element | What it shows | Notable detail |
|-----------|--------------|----------------|
| Research Sidebar | Top 20 SERP results with word count, links, domain authority, H1/H2 structure | Stays visible while writing — no context switch |
| Topic Score Bar | Green/yellow/red progress bar (0-100) | Updates in real-time as you type |
| Brief Builder | Drag-and-drop outline construction from SERP headings | Click any competitor heading to add to your outline |
| Questions Panel | PAA + Reddit + Quora questions grouped by theme | Multi-source (stronger than Surfer) |
| AI Visibility Dashboard | Share-of-voice charts across 8 AI platforms | Hexagonal visualization |
| Onboarding | Document creation wizard: enter keyword → immediate SERP analysis | No setup required — functional in 60 seconds |

**Onboarding:** 7-day free trial, no credit card. Immediate SERP analysis from first keyword — low barrier to first value.

**Reported UX issues:** "Overwhelming dashboard for beginners." Export formatting requires manual cleanup when pasting into Google Docs. Editor feels cluttered when all panels open.

---

### SEO.ai

**Primary UI pattern:** Dashboard-forward. Setup wizard + monitoring view. Not a writing editor — this is an operations console.

| UI Element | What it shows | Notable detail |
|-----------|--------------|----------------|
| Website Setup | URL input + CMS connection | 5-minute onboarding |
| Content Calendar | Scheduled publication list with frequency controls | Email preview before publish — user reviews content before it goes live |
| Performance Dashboard | GSC-connected clicks, impressions, rankings | Passive monitoring — no active editing interface |
| Content Queue | List of AI-planned articles with status (planned/written/published) | No keyword research UI — fully automated |
| Benchmarking View | Content piece vs ranking competitors comparison | Post-publish only |

**Onboarding:** 10-day free trial. Designed for "set and forget" users — not content strategists who want control. Minimal keyword research UI by design.

**Reported UX issues:** Keyword selection is a black box. Users cannot see why a keyword was chosen. No way to override the AI's keyword strategy without breaking the automation.

---

### SurferSEO

**Primary UI pattern:** Tool-by-tool navigation. Four distinct tools with separate entry points (Content Editor, SERP Analyzer, Topical Map, Keyword Research). No unified research-to-brief pipeline view.

| UI Element | What it shows | Notable detail |
|-----------|--------------|----------------|
| Topical Map | Hexagon-based cluster visualisation. Green = covered, grey = uncovered | Requires GSC. Refreshes every 14 days |
| SERP Analyzer | Bar chart of 500+ signals across top 50 results. Correlation strength per factor | Most granular SERP UI in the set |
| Content Editor | Real-time Content Score (0-100) + keyword suggestion list in sidebar | Industry-standard scoring UI |
| Keyword Research | Table view: keyword + volume + difficulty + intent + content score benchmark | Location-specific (23 countries) |
| AI Visibility Panel | Prompt tracking for ChatGPT, Perplexity, Google AI, Gemini | Separate tracking per AI platform |
| Sites Hub | All-in-one GSC management view. Site-level metrics + ranking changes | New in 2025 updates |

**Onboarding:** No free trial. Starts at $99/month. Learning curve higher due to tool fragmentation. Requires GSC for best features.

**Reported UX issues:** Tool fragmentation means no single research-to-brief workflow. Users must jump between Keyword Research → SERP Analyzer → Content Editor manually. No outline builder — gap vs Frase.

---

### Semrush ContentShake / Content Toolkit

**Primary UI pattern:** Three-option content dashboard as entry point. Research tools (Keyword Magic, Keyword Gap) are in the main Semrush platform — ContentShake is a layer on top.

| UI Element | What it shows | Notable detail |
|-----------|--------------|----------------|
| Content Dashboard | Three workflow tiles: Create / Optimise / Repurpose | Clear entry point — low cognitive load |
| Topic Finder | Trending topics by industry and location | Weekly refresh |
| Keyword Magic Tool | Table with left-sidebar topic groups. Volume, KD%, CPC, intent, trend | 26B row database — most powerful keyword UI |
| Keyword Gap View | Venn diagram of shared/unique keywords vs competitors | Most intuitive competitive gap visual |
| Keyword Strategy Builder | Pillar + subtopic cluster tree | Auto-generated in ~30 seconds |
| SEO Content Template | Recommendations card: word count, semantic keywords, competitor backlinks, SERP features | Generated per keyword in ~1 min |
| SEO Writing Assistant | Color-coded content: green (good), yellow (improve), red (fix). Live Content Score | Most detailed real-time writing guidance |

**Onboarding:** ContentShake has a guided project setup (topic, audience, brand voice, tone, content length). Integrates with existing Semrush account. Google Docs plugin and WordPress plugin available.

**Reported UX issues:** Google Docs plugin glitchy on docs >3,000 words. Workflow split between Semrush (research) and ContentShake (writing) causes context switching. Full keyword research power requires being on a Semrush plan, not just ContentShake.

---

## Dimension 4: Integrations & Ecosystem

| Integration Category | Frase.io | SEO.ai | SurferSEO | Semrush ContentShake |
|---------------------|----------|--------|-----------|----------------------|
| **Keyword data source** | Proprietary SERP-derived NLP + keyword add-on (source not disclosed) | Google Search data + topic relevance engine (proprietary) | "Trusted data partners" (source not disclosed). Proprietary SERP analysis | Semrush 26B keyword database (own infrastructure, Google-derived) |
| **SERP data source** | Live Google SERP scraping (top 20) | Not detailed | Live Google SERP scraping (top 50) | Live Google SERP top 10 for brief generation |
| **Search Console** | Yes — clicks, impressions, CTR, avg position | Yes — performance tracking | Yes — required for Topical Map. Central to content strategy | Yes — within Semrush Position Tracking |
| **Google Analytics** | Not listed | Not listed | Not listed | Yes (within Semrush) |
| **CMS — WordPress** | Yes (Yoast + Rank Math meta auto-populate) | Yes | Yes (plugin, real-time collaboration) | Yes (one-click publish) |
| **CMS — Webflow** | Yes (smart field mapping) | Yes | Not listed | Not listed |
| **CMS — Shopify** | Not listed | Yes | Not listed | Not listed |
| **CMS — Wix** | Not listed | Yes | Not listed | Not listed |
| **CMS — Sanity** | Yes (Portable Text conversion) | Not listed | Not listed | Not listed |
| **CMS — Contentful** | Not listed | Not listed | Yes (Peace of Mind plan) | Not listed |
| **Google Docs** | Yes (import/export with formatting) | Not listed | Yes (integration) | Yes (plugin — glitchy >3k words) |
| **Notion** | Yes (import/export as native blocks) | Not listed | Not listed | Not listed |
| **Zapier / Make / n8n** | Yes (via REST API) | Not listed | Yes (Peace of Mind plan) | Not listed |
| **Slack** | Yes (review/audit notifications) | Not listed | Not listed | Not listed |
| **API** | Yes — 50+ REST endpoints, webhooks (9 event types), MCP-compatible, Claude/ChatGPT compatible | Not documented publicly | Yes (Peace of Mind plan) | Yes (within Semrush API) |
| **AI platform tracking** | 8 platforms (ChatGPT, Perplexity, Claude, Gemini, Grok, Copilot, DeepSeek, Google AI) | Not listed | ChatGPT, Perplexity, Google, Gemini, AI Overview (Pro+) | ChatGPT + Google AI Overviews (Pro+) |
| **Link building** | Not listed | Yes (automatic from real topic-relevant websites — unverified claim) | Not listed | Not listed |

**Key finding — keyword data source opacity:** None of the four competitors publicly disclose their exact keyword data source. Industry context: DataForSEO is the dominant B2B keyword data supplier for tools in this tier (Frase, SurferSEO likely customers). Semrush uses its own 26B-row database. Google Search Console is the one universally supported authoritative integration.

**Sources:**
- https://www.frase.io/integrations
- https://seo.ai/ (CMS integrations section)
- https://surferseo.com/pricing/ (integration tiers)
- https://docs.surferseo.com/en/articles/8985467-why-you-should-connect-your-gsc-to-surfer
- https://dataforseo.com/apis (for context on B2B keyword data supply chain)

---

## Dimension 5: Data Models & Structure

### Frase.io — Inferred Data Model

Based on API documentation (50+ endpoints), feature set, and webhook event types:

| Entity | Key Attributes | Relationships |
|--------|--------------|--------------|
| **Document** | id, title, keyword (target), domain, created_at, status (draft/published/audited) | Has many SERPResults, one Brief, one ContentScore |
| **SERPResult** | position, url, domain, word_count, domain_authority, heading_count, link_count, image_count, snippet | Belongs to Document |
| **TopicScore** | score (0-100), topics_covered, topics_missing, topic_coverage_pct | Belongs to Document (updates on edit) |
| **Brief** | outline (ordered list of headings), questions (PAA + multi-source), word_count_target, keywords (cluster), sources | Belongs to Document |
| **Keyword** | term, volume (add-on), difficulty (add-on), intent, related_terms | Referenced in Brief |
| **Competitor** | url, domain, share_of_voice | Referenced in gap analysis |
| **AIVisibilityPrompt** | platform (ChatGPT/Perplexity/etc.), prompt_text, brand_position, competitor_positions, tracked_at | Belongs to Domain |
| **SiteAudit** | pages_crawled, issues (array), severity (critical/warning/info), audit_type | Belongs to Domain |
| **Webhook** | event_type (9 types: content.ready, brief.ready, research.completed, audit.completed, etc.), payload | Emitted by Document/Audit events |

**Research depth:** API exposes `/serp/analyze` returning AI Overview presence, organic positions, PAA, related searches per keyword. Deep research endpoint supports general/competitor/gap analysis at three depth levels (quick/standard/deep).

---

### SEO.ai — Inferred Data Model

Limited public documentation. Inferred from feature descriptions:

| Entity | Key Attributes | Relationships |
|--------|--------------|--------------|
| **Website** | url, cms_type, crawl_date, content_gap_count | Has many Pages, one ContentCalendar |
| **Page** | url, title, keywords_ranking, impressions, clicks, status (ranking/not-ranking) | Belongs to Website |
| **ContentGap** | topic, suggested_keyword, search_volume, priority_score | Belongs to Website |
| **ContentCalendarEntry** | keyword, planned_date, status (planned/written/published), email_preview_sent | Belongs to Website |
| **GeneratedArticle** | title, keyword, content (body), meta_title, meta_description, internal_links, featured_image_url, published_url | Belongs to ContentCalendarEntry |
| **BenchmarkResult** | keyword, competitor_urls, competitor_avg_word_count, missing_keywords | Belongs to GeneratedArticle |

**Key gap:** No public API documentation. No transparent keyword research data model. Autonomous keyword selection is a black box — no data model entities visible to the user.

---

### SurferSEO — Inferred Data Model

Based on official knowledge base docs and feature descriptions:

| Entity | Key Attributes | Relationships |
|--------|--------------|--------------|
| **Domain** | url, gsc_connected, topical_authority_score | Has many TopicClusters, Pages |
| **TopicCluster** | main_keyword, search_volume, keyword_difficulty, intent, status (covered/uncovered), aggregate_impressions | Belongs to Domain; has many Keywords, Articles |
| **Keyword** | term, volume, difficulty, intent, content_score_benchmark, position (if ranking), impression_count | Belongs to TopicCluster |
| **Article** | title, target_keyword, url (if published), content_score, status (covered/uncovered/new) | Belongs to TopicCluster |
| **SERPResult** | position, url, word_count, keyword_density, entity_list, h1/h2_count, image_count, page_speed, structured_data | Belongs to Article (SERP Analyzer context) |
| **ContentScore** | score (0-100), keyword_targets (list), suggested_word_count, heading_suggestions, entity_targets | Belongs to Article (Content Editor context) |
| **NLPEntity** | entity_text, entity_type, frequency, correlation_strength | Belongs to SERPResult |
| **TopicalMap** | domain_id, last_refreshed (14-day cycle), covered_count, uncovered_count, competitor_coverage (array) | Belongs to Domain |

**Data density:** 500+ on-page signals per SERP result is the richest per-result data model in the set. NLP entity tracking at field level is unique.

---

### Semrush ContentShake / Content Toolkit — Inferred Data Model

Based on official Semrush keyword research workflow docs and ContentShake feature descriptions:

| Entity | Key Attributes | Relationships |
|--------|--------------|--------------|
| **Keyword** | term, volume, kd_pct, personal_kd_pct (domain-adjusted), cpc, competitive_density, intent (info/nav/comm/trans), trend (12-month), serp_features | Standalone research entity |
| **KeywordCluster** | pillar_keyword, subtopic_keywords (array), aggregate_volume, cluster_intent | Has many Keywords; generated by Keyword Strategy Builder |
| **CompetitorKeywordProfile** | domain, organic_keywords (array), keyword_gap (vs your domain) | Referenced in Keyword Gap analysis |
| **ContentBrief** | target_keyword, recommended_word_count, semantic_keywords (array), competitor_backlink_benchmarks, serp_feature_opportunities, intent_type | Generated by SEO Content Template; belongs to Keyword |
| **ContentDraft** | title, keyword, h2_structure, body_content, content_score (0-100), readability_score (Flesch), tone_score, keyword_density, ai_image_url | Generated by ContentShake AI; linked to ContentBrief |
| **TopicHierarchy** | pillar_topic, subtopics (array), internal_link_structure | Generated by Topic Cluster Builder |
| **AIVisibilityAlert** | brand_mention, platform (ChatGPT/Google AI Overview), context, date | Belongs to Domain |

**Key advantage:** Personal KD% field is unique in the set — adjusts keyword difficulty to your specific domain's authority using your backlink profile. Provides more actionable prioritisation signal than raw KD%.

**Sources:**
- https://www.semrush.com/blog/how-to-use-semrush-keyword-research/
- https://butterblogs.com/blog/semrush-content-tools-review-2026-a-full-breakdown/

---

## Synthesis

### Table Stakes (Must Match)

These features exist in 3 or 4 competitors. Not having them is a disqualifying gap:

| Feature | Minimum viable implementation |
|---------|------------------------------|
| SERP analysis (top 10-20 results) | Fetch live SERP, extract: word count, H structure, entities, meta. Per keyword on demand |
| Topic Score / Content Score | 0-100 numeric score comparing draft coverage vs SERP competitors. Must update in real-time during editing |
| Content Brief generation | Auto-generate outline + keyword list + word count target from SERP data. One-click |
| PAA / question research | Surface People Also Ask + related searches for every keyword |
| Topic clustering | Group keywords by semantic similarity into pillar + support structure |
| Search intent classification | Classify each keyword as informational / navigational / commercial / transactional |
| Google Search Console integration | Connect GSC for performance data (clicks, impressions, avg position) |
| Keyword gap analysis | Compare your coverage vs competitors by keyword |
| WordPress direct publish | One-click publish from tool to WordPress |
| AI visibility tracking | Monitor brand/content mentions on at least ChatGPT + Perplexity |

---

### Differentiators (Opportunity)

Areas where no competitor has a strong solution, or where the market leader's solution has documented weaknesses:

| Opportunity | Gap in market | AISOGEN angle |
|------------|--------------|--------------|
| **Transparent keyword selection with reasoning** | SEO.ai's autonomous selection is a black box. Users don't know why keywords were chosen. SurferSEO requires manual selection. | Expose the reasoning: "This keyword selected because: search volume 2,400/mo, difficulty 32, your site has 0 content on this cluster, competitors average 1,200 words." Make the AI's strategy legible |
| **Multi-language keyword research natively** | None of the four competitors offer multilingual keyword research as a first-class feature. Semrush supports localisation but not simultaneous multi-language planning | Hairgenetix use case: 9-language simultaneous keyword research + content planning is a genuine gap |
| **Intent-to-format mapping** | Competitors classify intent but don't map it to content format recommendations. Knowing a keyword is "informational" doesn't tell you whether to write a how-to, a definition article, a comparison, or a list | Add: "For this keyword, the SERP shows 7/10 results are comparison articles. We recommend comparison format." |
| **Durable pipeline with stage-level resumability** | SEO.ai's autonomous pipeline can fail silently. Frase has no pipeline state. SurferSEO has no pipeline at all | Built-in pipeline: research → brief → draft → optimise → publish. Each stage independently resumable. BullMQ-backed |
| **YMYL-aware content validation** | No competitor has domain-specific guardrails for health/legal/financial content | Health domain check: flag medical claims without citations, detect regulatory language, require source attribution |
| **Competitor content freshness tracking** | All competitors show competitor content at analysis time but none track when competitor content was published or updated | "Competitor X published a new article on this keyword 3 days ago — re-analyse before writing" |
| **Content calendar with strategic prioritisation scoring** | SEO.ai has a calendar but no prioritisation. SurferSEO has a list but no calendar. Semrush has a dashboard but no scheduling | True editorial calendar: keyword prioritised by (volume × difficulty × business value × content gap score). Scheduled with commit |
| **Autonomous topic discovery without GSC dependency** | SurferSEO's Topical Map requires GSC + existing traffic. New sites cannot use it | Use site-crawl + keyword seed + competitor domain analysis to bootstrap topic map for sites with zero traffic |

---

### Anti-Patterns (Avoid)

Documented failure modes across the four competitors — do not replicate:

| Anti-pattern | Competitor | Why to avoid |
|-------------|-----------|-------------|
| Keyword research behind an upsell paywall | Frase.io ($35/mo add-on on top of $39/mo base) | Users feel deceived. Core research capability should not be a hidden cost |
| Black-box autonomous keyword selection | SEO.ai | 3.4/5 G2 rating. Top complaint: "keywords not relevant to business." Autonomy without transparency destroys trust |
| No outline builder — user must build manually after SERP analysis | SurferSEO | Frase's point-and-click outline builder is cited as a key advantage in every comparison. Not having it is a workflow gap |
| Tool fragmentation (keyword tool + SERP tool + editor = 3 separate tools) | SurferSEO | Users must jump between tools, losing context. Unified research-to-brief pipeline reduces friction |
| Content Score gaming via keyword stuffing | SurferSEO, Frase.io | Score optimisation encourages formulaic content that harms readability and user experience |
| Google Docs plugin instability | Semrush ContentShake | Breaks on docs >3,000 words. CMS integrations must be tested at real-world content lengths |
| Topical Map unusable for new/low-traffic sites | SurferSEO | GSC dependency means the best planning feature is unavailable to users who need it most |
| 14-day data refresh on topical planning | SurferSEO | Fast-moving niches require more frequent updates. 14-day lag is a product limitation |
| AI write-and-publish with no human review gate | SEO.ai | Content quality issues published automatically damage SEO and brand. Human-in-the-loop gates required |
| Content score that encourages ignoring user experience | SurferSEO | "500 signals" sounds impressive but correlation-based scoring can optimise for ranking factors at the cost of content quality |

---

### Key Competitive Insight

The market has split into two camps — **research-first tools** (Frase, Semrush) that give humans rich data and expect human decisions, and **autonomy-first tools** (SEO.ai) that make all decisions but with opaque, low-trust output — and the white space is a **transparent agentic pipeline** that automates the execution while keeping the reasoning legible and the human in control of strategy.

---

### Where We Follow the Market

- SERP analysis (top 20+ results, word count, entities, heading structure)
- Topic Score / Content Score (0-100, real-time in editor)
- Content brief auto-generation from SERP
- Topic clustering (pillar + support structure)
- Search intent classification (4-type)
- Google Search Console integration
- Keyword gap analysis vs competitors
- Content calendar / article queue
- WordPress + Shopify publish integration
- AI visibility tracking (minimum: ChatGPT + Perplexity)

---

### Where We Diverge (and Why)

| Divergence | Rationale |
|-----------|-----------|
| **Multi-language keyword research as a first-class feature** | Hairgenetix requires 9-language coverage. No competitor handles this natively. Unlocks a market segment none target |
| **Transparent autonomous reasoning** | SEO.ai's black-box automation is the top user complaint in the autonomous tier. AISOGEN will show the "why" for every keyword, cluster, and content decision — building trust through legibility |
| **Autonomous pipeline with stage-level resumability** | No competitor has a durable pipeline. All require manual re-entry if a step fails. BullMQ-backed stage resumption is a reliability differentiator for high-volume content operations |
| **YMYL domain guardrails** | Health, legal, and financial domains require content safety checks that no competitor provides. This is a compliance gap that becomes a feature for regulated-domain customers |
| **Content calendar with algorithmic prioritisation** | Market offers either full automation (SEO.ai, low trust) or manual ordering. AISOGEN will score each potential article by (search volume × difficulty inverse × business value weight × content gap score) and surface a ranked backlog — human approves the plan, AI executes it |
| **New-site topical mapping without GSC dependency** | SurferSEO's best planning feature is unusable for new sites. AISOGEN will bootstrap a topical map from competitor domain analysis + keyword seed, no traffic required |

---

## Source Index

| Source | Competitor | Type | URL |
|--------|-----------|------|-----|
| Frase SERP Research feature page | Frase.io | Official | https://www.frase.io/features/seo-research |
| Frase Integrations page | Frase.io | Official | https://www.frase.io/integrations |
| Frase Pricing page | Frase.io | Official | https://www.frase.io/pricing |
| Frase API documentation | Frase.io | Official | https://www.frase.io/features/api-integrations |
| Frase Review — SearchAtlas | Frase.io | Third-party review | https://searchatlas.com/blog/frase-review/ |
| Frase Review 2025 — AI Flow Review | Frase.io | Third-party review | https://aiflowreview.com/frase-review-2025/ |
| Frase vs SurferSEO comparison | Both | Third-party | https://thedoublethink.com/frase-vs-surfer/ |
| SEO.ai homepage | SEO.ai | Official | https://seo.ai/ |
| SEO.ai G2 reviews (via search) | SEO.ai | User reviews | https://www.g2.com/products/seo-ai/reviews |
| SurferSEO Keyword Research KB | SurferSEO | Official | https://docs.surferseo.com/en/articles/11891594-keyword-research |
| SurferSEO Topical Map KB | SurferSEO | Official | https://docs.surferseo.com/en/articles/9383782-topical-map |
| SurferSEO SERP Analyzer KB | SurferSEO | Official | https://docs.surferseo.com/en/articles/7831346-reading-your-results-in-serp-analyzer |
| SurferSEO Pricing page | SurferSEO | Official | https://surferseo.com/pricing/ |
| SurferSEO Review — SearchAtlas | SurferSEO | Third-party review | https://searchatlas.com/blog/surfer-seo-review/ |
| Semrush Keyword Research guide | Semrush | Official | https://www.semrush.com/blog/how-to-use-semrush-keyword-research/ |
| Semrush Content Tools Review 2026 | Semrush | Third-party review | https://butterblogs.com/blog/semrush-content-tools-review-2026-a-full-breakdown/ |
| ContentShake AI Guide 2025 | Semrush | Third-party guide | https://mattrics.com/blog/contentshake-ai/ |
| Semrush ContentShake AI statistics | Semrush | Third-party | https://originality.ai/blog/content-shake-ai-semrush-statistics |
| DataForSEO APIs overview | Data supply chain | Reference | https://dataforseo.com/apis |
| SurferSEO GSC integration KB | SurferSEO | Official | https://docs.surferseo.com/en/articles/8985467-why-you-should-connect-your-gsc-to-surfer |
