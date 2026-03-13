# Research: E-001 Configuration & Setup — Competitor Patterns

> **Epic:** E-001 (Configuration & Setup)
> **Theme:** Autonomous Content Engine (Spec 001)
> **Date:** 2026-03-13
> **Purpose:** Inform requirements for 6 PDM features (1.1–1.6)

---

## 1. Onboarding UX Patterns

### Findings

| Tool | Onboarding Model | Steps | Data Collected Upfront |
|------|-----------------|-------|----------------------|
| **Koala.sh** | Guided wizard with tooltips | ~3 steps (account → site URL → first article) | Site URL, niche/topic keywords |
| **Byword.ai** | Domain-first auto-detect | 2 steps (enter domain → auto-detect CMS → connect) | Domain URL, CMS auto-detected |
| **SEObot** | URL-and-go | 1 step (enter URL, press go) | Website URL only — AI infers niche, audience, keywords automatically |
| **Jasper** | Multi-step workspace setup | 4–5 steps (account → workspace → brand voice → templates → first content) | Company info, brand voice samples, team roles |
| **Frase** | Quick-start for individuals, guided for enterprise | 2–3 steps (account → first document → optional governance setup) | Target keyword, URL for content briefs |
| **SEO.ai** | URL-and-go with full crawl | 2 steps (enter URL → AI crawls site → generates strategy) | Website URL, publishing pace preference |

### Key Patterns

- **Minimal-input onboarding wins:** SEObot and Byword both use a "give us your URL, we figure out the rest" approach. This is the dominant trend — reduce friction to one input field.
- **Progressive disclosure:** Koala and Jasper collect more data, but spread it across the workflow rather than demanding everything upfront. Configuration happens as you use the product.
- **Auto-detection over manual config:** Byword auto-detects CMS from the domain. SEObot infers niche and keywords from site content. SEO.ai crawls the entire site to understand existing topic coverage.
- **Enterprise = more setup:** Jasper and Frase have heavier onboarding for enterprise tiers (governance, team training, role-based access), but keep individual onboarding lean.

### Implication for E-001

Design a 2-step minimal onboarding (URL + connect CMS), with progressive configuration for brand voice, quality thresholds, and AISO preferences. Auto-infer as much as possible from the URL crawl.

---

## 2. CMS Connection Patterns

### WordPress

| Tool | Method | Auth | Permissions | Notes |
|------|--------|------|-------------|-------|
| **Koala.sh** | WordPress plugin (preferred) OR REST API | Plugin: auto-auth on install. REST API: Application Password | Create/edit posts, upload media | Plugin recommended for enhanced features. REST API as fallback. WordPress.com not supported (no Application Passwords). |
| **Byword.ai** | Direct integration (API) | WordPress Application Password | Create posts/pages, set status (draft/publish), assign author, tags, categories, upload images | Can toggle draft vs. auto-publish. Beta: page creation. |
| **SEObot** | Direct integration via REST API | WordPress credentials (Application Password expected) | Read/write content | Supports WordPress, Webflow, Ghost, Wix, Framer, Notion, HubSpot + REST API + Webhooks + Zapier + Make |

### Shopify

| Tool | Method | Auth | Permissions | Notes |
|------|--------|------|-------------|-------|
| **Koala.sh** | Not documented (WordPress focus) | — | — | — |
| **Byword.ai** | Shopify app integration | Shopify OAuth (pending app review) | Create blog posts, assign author, upload images, set tags | Integration fully built but pending Shopify app store approval as of research date |
| **SEObot** | Custom app via Admin API | Access Token (shpat_*) | `read_content` + `write_content` scopes | User creates custom Shopify app → generates API token → pastes into SEObot. Manual but straightforward. |

### Key Patterns

- **WordPress:** Application Passwords (WordPress 5.6+) is the standard auth method. No OAuth needed. Plugin install is the premium path for enhanced UX.
- **Shopify:** Two approaches — (a) Shopify App Store listing with OAuth flow (Byword's approach, but requires Shopify approval), or (b) Custom App with Admin API token (SEObot's approach, faster to ship, no approval needed).
- **Multi-CMS support is table stakes:** SEObot supports 9+ CMS platforms. Byword supports WordPress + Shopify + Webflow + Zapier.
- **Zapier/Make as escape hatch:** Multiple tools offer Zapier/Make integration for unsupported CMSs.

### Implication for E-001

Start with WordPress (Application Password auth) and Shopify (Custom App / Admin API token). Use the SEObot pattern for Shopify (no app store approval needed). Add Zapier webhook as a third option for other CMSs.

---

## 3. Brand Voice Training

### Jasper (industry leader for brand voice)

- **Input methods:** Upload up to 8 examples — text paste, file upload (.txt, .pdf, .docx), or URL scan
- **Analysis output:** Auto-generates voice description covering tone, style, language, and target audience
- **Refinement:** Preview mode shows side-by-side comparison (with voice vs. without voice) for Blog Post, LinkedIn Post, or Product Description
- **Advanced features:** Multiple voice profiles per workspace (e.g., "Executive Voice" vs. "Support Voice"), toggle between voices, public or private visibility
- **Structure:** Two components — (1) Memory (products, services, audiences, unique company info) and (2) Tone & Style (rules, formatting, writing style)

### Copy.ai

- **Input methods:** Paste content samples (minimum 300 words recommended, 3000+ for accuracy)
- **Analysis output:** Auto-generates tone, style, language, and audience description
- **Refinement:** Manual edits to generated voice profile, add more samples, replace samples
- **Multiple voices:** Separate brand voices per ICP (ideal customer profile) — e.g., enterprise voice vs. SMB voice
- **Usage:** Dropdown selector in chat interface

### Frase

- **Style Guides:** Custom rules enforced on both human writers and AI writer
- **Brand Voice:** Tone settings auto-applied to AI-generated content
- **Term Management:** Approved word list + flagged terms (real-time enforcement)

### Key Patterns

- **URL scan is the easiest input:** Jasper's URL-to-voice-profile is the smoothest UX. Paste your website, get a voice profile.
- **Sample text is the most accurate:** Both Jasper and Copy.ai recommend substantial text samples (3000+ words for best results).
- **Two-component model:** Jasper separates brand knowledge (Memory) from writing style (Tone & Style). This is a clean architecture.
- **Multiple voices per brand:** Both Jasper and Copy.ai support multiple voice profiles for different audiences or content types.
- **Real-time enforcement:** Frase flags off-brand terms as you write, not just at generation time.

### Implication for E-001

Feature 1.2 (Brand Voice Training) should support: (a) URL scan for auto-inference, (b) sample text upload/paste, (c) manual style parameter editing, (d) preview/comparison mode. Store as two components: brand knowledge + writing style. Support multiple voice profiles.

---

## 4. Quality Configuration

### Surfer SEO (Content Score)

- **Score range:** 0–100 numeric score
- **Thresholds:** <33 = not optimised, 33–66 = adequate, >66 = ready to publish
- **Recommended target:** 60+ as minimum benchmark, or 10–20 points above top competitors
- **User configuration:** Users can adjust competitors used for scoring, exclude keywords, change content structure — all affect the achievable maximum score
- **Where it appears:** Content Editor, Audit, and SERP Analyzer (slightly different calculations per context)

### Clearscope (Content Grade)

- **Score range:** Letter grades F through A++
- **Threshold:** System suggests a minimum grade based on competitor analysis (not user-configurable)
- **How it works:** Grade increases as you add more suggested terms. Measures relevance and comprehensiveness against top-ranking content.
- **No custom thresholds exposed** — the system determines what's "good enough" based on SERP analysis

### Frase (Content Governance)

- **Approach:** Style Guides with custom rules, approval workflows, template standardisation
- **Quality enforcement:** Real-time term flagging, governance dashboards for enterprise
- **No numeric score threshold** — quality is enforced through rules and workflows rather than scores

### SEO.ai

- **Approach:** Three publish modes — auto-publish, save as draft, or manual review
- **Quality gate:** Optional human review before publishing, with email notifications
- **No user-configurable score thresholds** — relies on AI + optional human review

### Key Patterns

- **Numeric scores are rare as user-configurable thresholds.** Surfer exposes a score but the "threshold" is a recommendation, not a hard gate. Clearscope doesn't expose configurable thresholds at all.
- **Publish mode as quality gate:** SEO.ai's 3-mode pattern (auto/draft/review) is the most common quality control pattern. The threshold is binary: "publish directly" vs. "human reviews first."
- **Rule-based quality > score-based quality:** Frase uses style guides and term management rather than numeric scores. This is more actionable.
- **Quality = content score + readability + brand compliance.** No single tool combines all three into one configurable threshold panel.

### Implication for E-001

Feature 1.5 (Quality Thresholds) should offer: (a) minimum SEO/content score (numeric, default 65), (b) minimum word count, (c) readability level target (e.g., Flesch-Kincaid grade), (d) publish mode (auto/draft/review), (e) brand compliance rules. This would be differentiated — no competitor offers all five as configurable user settings.

---

## 5. Topic/Niche Setup

### Approaches by Competitor

| Tool | Primary Method | Secondary Methods |
|------|---------------|-------------------|
| **SEObot** | URL scan — AI infers niche, audience, and keywords from site content | Manual keyword input |
| **SEO.ai** | Full site crawl — identifies existing topics and coverage gaps | AI keyword research from crawl results |
| **Byword.ai** | Keyword input (single keyword per article or bulk CSV upload) | Campaign builder for topic clusters, Programmatic mode for glossaries |
| **Koala.sh** | Seed keyword per article | Topic clusters via article series |
| **Frase** | Target keyword per document → SERP analysis → content brief | No bulk topic/niche setup |
| **Keyword Insights** | Seed keyword → keyword discovery (Google Autocomplete, Reddit, Quora, PAA) → auto-clustering | Import from Ahrefs, SEMrush, GSC |
| **Search Atlas** | GSC + GA4 direct connection → topic authority assessment | Semantic depth analysis, keyword clustering |

### Key Patterns

- **URL crawl is the modern standard:** SEObot and SEO.ai both derive niche understanding from crawling the user's site. No manual niche selection needed.
- **GSC import is the power-user path:** Search Atlas and other tools connect directly to GSC for real performance data. Keyword Insights supports import from GSC, Ahrefs, SEMrush.
- **Seed keywords remain the simplest input:** Byword and Koala still use per-article keyword input as the primary flow.
- **Auto-clustering:** Keyword Insights and Search Atlas automatically group keywords into topic clusters. This is more sophisticated than flat keyword lists.
- **No tool does true "niche configuration" as a standalone setup step.** The niche is either inferred from URL or implied by keyword selection. There's no "select your industry" dropdown.

### Implication for E-001

Feature 1.4 (Topic/Niche Configuration) should support three input modes: (a) URL scan for auto-inference (primary), (b) seed keyword list (manual), (c) GSC import for data-driven topic discovery. Auto-cluster keywords into topic groups. Avoid dropdown/category niche selection — infer from content.

---

## Summary: Patterns to Adopt

| Feature | Recommended Pattern | Rationale |
|---------|-------------------|-----------|
| **1.1 Site URL** | URL-and-go with auto-crawl (SEObot/SEO.ai model) | Lowest friction, highest auto-inference |
| **1.2 Brand Voice** | URL scan + text samples + manual editing (Jasper model) | Industry-proven, highest quality voice matching |
| **1.3 CMS Connection** | WordPress: Application Password. Shopify: Custom App + Admin API token | No app store approval needed, proven patterns |
| **1.4 Topic/Niche** | URL crawl + seed keywords + GSC import | Three tiers of sophistication, auto-cluster |
| **1.5 Quality Thresholds** | 5-setting panel (SEO score, word count, readability, publish mode, brand compliance) | Differentiated — no competitor offers all five |
| **1.6 AISO Preferences** | No competitor reference — novel feature | Unique differentiator for our engine |

---

## Sources

- [Koala AI In-Depth Review 2025](https://skywork.ai/skypage/en/Koala-AI-In-Depth-Review-(2025)-The-Ultimate-Guide-to-KoalaWriter-and-Beyond/1976135370246123520)
- [Koala.sh Review 2026](https://www.saasultra.com/koala-sh-review/)
- [Koala WordPress REST API Integration](https://support.koala.sh/en/article/wordpress-rest-api-integration-instructions-1m91pkv/)
- [Koala WordPress Plugin Announcement](https://blog.koala.sh/introducing-the-koala-ai-wordpress-plugin-an-enhanced-publishing-experience/)
- [Byword — Creating Content](https://learn.byword.ai/basics/creating-content)
- [Byword — WordPress Integration](https://learn.byword.ai/publishing/integrations/wordpress)
- [Byword — Shopify Integration](https://learn.byword.ai/publishing/integrations/shopify)
- [SEObot — Shopify Integration](https://seobotai.com/integrations/shopify/)
- [SEObot — CMS Integrations](https://docs.seobotai.com/en/articles/10644432-what-cms-integrations-does-seobot-support)
- [Jasper Brand Voice](https://www.jasper.ai/brand-voice)
- [Jasper Brand Voice Help](https://help.jasper.ai/hc/en-us/articles/18618693085339-Brand-Voice)
- [Jasper Brand IQ](https://www.jasper.ai/brand-iq)
- [Copy.ai Brand Voice](https://www.copy.ai/features/brand-voice)
- [Copy.ai Getting Started with Brand Voice](https://support.copy.ai/en/articles/10059100-getting-started-with-brand-voice)
- [Frase Content Governance](https://help.frase.io/intro-to-content-governance)
- [Surfer Content Score](https://docs.surferseo.com/en/articles/5700317-what-is-content-score)
- [Surfer Content Score Explained](https://docs.surferseo.com/en/articles/6109757-content-score-explained)
- [Clearscope Grading](https://www.clearscope.io/support/how-does-clearscope-grade-your-content)
- [SEO.ai Platform](https://seo.ai/)
- [Keyword Insights](https://www.keywordinsights.ai/)
