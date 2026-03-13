# Phase 2 Analysis — E-001 Configuration & Setup

> **Epic:** E-001 | **Date:** 2026-03-13
> **Builds on:** `../research/e001-configuration-setup-patterns.md` (Phase 1 domain research)

---

## Value Proposition Canvas — Top 3 Competitors for Configuration

### Competitor 1: SEObot (closest to our autonomous model)

**Customer Profile:**
- **Jobs:** Set up autonomous content generation for my site. Connect CMS. Start getting articles published.
- **Pains:** Too many manual steps to configure. API tokens are confusing. Don't know which keywords to target. Setup takes hours.
- **Gains:** One-click setup. Articles start appearing within hours. No technical knowledge needed.

**Value Map:**
- **Products/Services:** URL-and-go setup, auto-detected niche, 9+ CMS integrations, Shopify Custom App pattern.
- **Pain Relievers:** Single URL input, auto-inference of niche/keywords, guided Shopify token setup.
- **Gain Creators:** Immediate content generation after setup, 50+ language support.

**Weakness vs us:** No brand voice. No quality thresholds. No AISO configuration. Setup is fire-and-forget with no customisation.

### Competitor 2: Jasper (best brand voice setup)

**Customer Profile:**
- **Jobs:** Create brand-consistent content at scale. Train AI on our voice. Manage multiple brand voices.
- **Pains:** AI content sounds generic. Inconsistent tone across team members. Hard to maintain brand identity at scale.
- **Gains:** Every piece of content sounds like us. Easy voice switching. Team-wide consistency.

**Value Map:**
- **Products/Services:** Brand IQ (URL scan + sample upload), Memory (brand knowledge), Tone & Style (writing rules), multi-voice profiles.
- **Pain Relievers:** Auto-generated voice profiles from existing content. Preview mode for comparison.
- **Gain Creators:** Brand consistency score. Multiple voices per workspace. Public/private voice sharing.

**Weakness vs us:** No CMS publishing. No autonomous pipeline. No SEO/AISO configuration. Jasper is a writing assistant, not a pipeline.

### Competitor 3: Koala.sh (best WordPress integration)

**Customer Profile:**
- **Jobs:** Publish SEO-optimised articles to my WordPress site. Minimise manual steps. Get articles live fast.
- **Pains:** Copy-pasting articles is tedious. WordPress REST API setup is confusing. Want to auto-publish with proper formatting.
- **Gains:** Click a button, article is live on WordPress. Proper headings, images, categories.

**Value Map:**
- **Products/Services:** WordPress plugin (one-click install) + REST API fallback. Deep Research Mode. KoalaLinks (internal linking). Model choice (GPT-5.2/Claude 4.5).
- **Pain Relievers:** Plugin auto-handles auth. Draft/publish toggle. Category/tag auto-assignment.
- **Gain Creators:** Fastest path from keyword to published article. Auto internal linking.

**Weakness vs us:** No Shopify. No brand voice. No quality thresholds. No AISO. No multi-language configuration.

---

## Blue Ocean ERRC Grid — E-001 Configuration

| Action | Factors | Rationale |
|--------|---------|-----------|
| **Eliminate** | Multi-step onboarding wizard. Manual niche/category selection dropdown. Plugin installation requirement (for V1). | Competitors waste setup time on unnecessary steps. URL crawl replaces manual selection. REST API works without plugins. |
| **Reduce** | Manual data entry during setup. Number of required fields before first article can be generated. CMS connection complexity (especially Shopify). | The fewer fields, the faster to value. SEObot proves 1-field setup works. |
| **Raise** | Quality configuration granularity (5 settings vs competitors' 0-1). CMS connection verification (test publish, not just "connected"). Multi-language awareness at config time. | No competitor lets users set quality gates. Our test-publish verification catches auth issues early. Multi-language is critical for Hairgenetix (9 locales). |
| **Create** | AISO scoring preferences (entirely novel). Brand voice as a configurable pipeline parameter (not just a writing feature). Per-site configuration persistence (run pipeline repeatedly from saved config). | No competitor has AISO config. Jasper has voice but not as pipeline input. No autonomous tool persists full pipeline config. |

---

## Specification-as-Context — What the Building Agent Needs to Know

> Frame each finding as future build context.

### For F-001 (Site Registration):
- **Pattern:** Auto-crawl the URL to detect: CMS type (check for wp-json endpoint, Shopify CDN patterns), available languages (hreflang tags, Shopify locale URLs), existing content inventory (sitemap.xml), site metadata.
- **Tech:** Use `fetch` to check for `/wp-json/wp/v2/` (WordPress detection) and `cdn.shopify.com` in source (Shopify detection). Parse sitemap.xml for content count.
- **Constraint:** Must work for both www and non-www. Handle redirects. Timeout at 10s per check.

### For F-002 (CMS Connection):
- **WordPress:** Application Password auth. Endpoint: `{site}/wp-json/wp/v2/posts`. Test by creating a draft post, verifying success, then deleting it. Store: site URL + username + application password (encrypted).
- **Shopify:** Custom App + Admin API access token (`shpat_*`). Endpoint: `{store}.myshopify.com/admin/api/2024-10/graphql.json`. Required scopes: `read_content`, `write_content`. Test by querying blog list. Store: store domain + access token (encrypted).
- **Security:** All credentials must be AES-256 encrypted at rest. Never logged. Never included in error messages.

### For F-003 (Brand Voice):
- **Input:** Accept 1-5 URLs to crawl for voice analysis. Extract text content (strip HTML, nav, footer). Feed to Claude with prompt: "Analyse the writing style of this content. Output a structured voice profile covering: tone (formal/casual/technical), sentence structure (short/long/mixed), vocabulary level (simple/intermediate/advanced), person (first/second/third), and distinctive patterns."
- **Output:** JSON voice profile stored per site configuration. Used as system prompt modifier in E-003 (Generation).

### For F-004 (Topic Config):
- **Three input modes:** (1) Auto from URL crawl — extract topics from existing content headings and meta keywords. (2) Seed keywords — user pastes a list, system clusters with KeyBERT or similar. (3) GSC import — connect via Google Search Console API, pull top queries, auto-cluster.
- **Clustering:** Group keywords by semantic similarity. Each cluster becomes a topic. Use for content calendar in E-002.

### For F-005 (Quality Thresholds):
- **5 settings with sensible defaults:** SEO score min (default: 65/100), AISO score min (default: 7/10), readability target (default: Grade 8 Flesch-Kincaid), word count range (default: 1500-3000), publish mode (default: draft for review).
- **Stored per site.** Read by E-003 scoring loop and E-004 publish decision.

### For F-006 (AISO Preferences):
- **Defaults-first approach.** Toggle: "Use recommended AISO settings" (default: on). When off, expose: priority factors from 36-factor model (checkboxes), schema types to generate (Article, FAQPage, HowTo, Product, BreadcrumbList, Organization), AI platform targets (ChatGPT, Perplexity, Gemini — all on by default).
- **Stored per site.** Read by E-003 AISO scoring and E-004 schema injection.

---

## Assumption Validation (from Phase 1)

| # | Assumption | Phase 1 Risk | Phase 2 Evidence | Updated Status |
|---|-----------|:----:|---------|--------|
| A1 | Shopify GraphQL Admin API supports blog article creation | M | **Confirmed** — SEObot uses this exact pattern. `read_content` + `write_content` scopes. Custom App route needs no app store approval. | ✅ Validated |
| A2 | WordPress REST API is sufficient (no plugin needed) | M | **Confirmed** — Koala, Byword, SEObot all use REST API with Application Passwords. Plugin is optional enhancement. | ✅ Validated |
| A3 | Brand voice can be trained from 3-5 sample URLs | H | **Partially validated** — Jasper does URL scan successfully with up to 8 samples. Quality depends on content volume at those URLs. 3000+ words recommended. | ⚠️ Partially validated — need minimum content threshold |
| A4 | Users will configure quality thresholds | L | **Confirmed low risk** — no competitor offers this, so no user expectation to compare against. Default-heavy design with advanced override is correct. | ✅ Validated (low priority) |
| A5 | Multi-language config can be set at site level | M | **Confirmed** — Shopify locales are per-store (admin API exposes locale list). WordPress has WPML/Polylang pattern. | ✅ Validated |
| A6 | AISO scoring preferences are meaningful at config time | H | **Still weak** — no competitor reference. But our 36-factor model has been tested on real sites (Hairgenetix 5.5→8.95). The preferences are meaningful because different sites prioritise different factors. | ⚠️ Accepted risk — validate with real usage in E-003 |
| A7 | One-time setup is sufficient | M | **Partially validated** — SEObot and Koala both use one-time setup. But Shopify tokens don't expire (Custom Apps), WordPress Application Passwords don't expire unless revoked. Main risk: site content changes over time → topic config may drift. | ⚠️ Partially validated — add "refresh config" capability for V2 |

---

## Feature Matrix — E-001 Capabilities vs Competitors

| Capability | SEObot | Jasper | Koala | Byword | SEO.ai | **Ours (E-001)** |
|-----------|:------:|:------:|:-----:|:------:|:------:|:----------------:|
| URL-and-go setup | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Auto-detect CMS | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| WordPress connection | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Shopify connection | ✅ | ❌ | ❌ | ⚠️ (pending) | ✅ | ✅ |
| Brand voice training | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| Multiple voice profiles | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ (V2) |
| Topic auto-inference | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| GSC import | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Quality thresholds | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| AISO preferences | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Multi-language config | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Config persistence | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Differentiation:** Quality thresholds, AISO preferences, GSC import, and brand voice + autonomous pipeline are unique to our solution. No competitor combines all of these.
