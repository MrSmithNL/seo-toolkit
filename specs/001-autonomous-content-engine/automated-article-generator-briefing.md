# Briefing: Automated Article Generator

> **Spec ID:** PROD-001-SPEC-001
> **Feature:** Automated Article Generator — Autonomous SEO/GEO/AISO Article Researcher, Writer, Publisher & Auditor
> **Product:** SEO Toolkit (PROD-001) — standalone service, also deployable as AISOGEN vertical
> **Author:** Malcolm Smith / Claude
> **Date:** 2026-03-12
> **Status:** BRIEFING — ready for RE gates

---

## 1. What We're Building

A fully autonomous content engine that takes a website's keyword strategy, content gaps, and SEO/GEO/AISO audit scores as inputs — and produces researched, written, optimised, published, and validated articles as output. With a dashboard for human oversight and editorial control.

### The Closed Loop (No Competitor Does This)

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS CONTENT ENGINE                  │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ RESEARCH  │──▶│  WRITE   │──▶│ OPTIMISE │──▶│ PUBLISH  │ │
│  │           │   │          │   │          │   │          │ │
│  │ • Keywords│   │ • Draft  │   │ • SEO    │   │ • CMS    │ │
│  │ • SERP    │   │ • Sources│   │ • GEO    │   │ • Schema │ │
│  │ • Gaps    │   │ • E-E-A-T│   │ • AISO   │   │ • Meta   │ │
│  │ • Topics  │   │ • Format │   │ • Score  │   │ • i18n   │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│        ▲                                            │        │
│        │           ┌──────────┐                     │        │
│        │           │  AUDIT   │◀────────────────────┘        │
│        │           │          │                              │
│        │           │ • ChatGPT│                              │
│        │           │ • Gemini │                              │
│        │           │ • Score  │                              │
│        └───────────│ • Triage │                              │
│         re-optimise│ • Fix    │                              │
│                    └──────────┘                              │
└─────────────────────────────────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │ DASHBOARD │
                    │           │
                    │ • Calendar│
                    │ • Scores  │
                    │ • Status  │
                    │ • Strategy│
                    │ • Before/ │
                    │   After   │
                    └───────────┘
```

### What Makes This Different From Every Competitor

| Capability | Best Competitor | Their Limit | Our Approach |
|-----------|----------------|-------------|--------------|
| Full autonomous loop | SEO.ai | 4 of 5 steps; no post-publish audit | All 5 steps + re-optimise loop |
| GEO/AISO in writing workflow | Writesonic | Bolt-on dashboard, not integrated | Baked into every step |
| Per-language AISO scoring | Nobody | Generate in 80 langs, score in 0 | Score each language independently |
| Shopify-native publishing | SEObot (shallow) | Basic publish only | Full template, schema, translation |
| Autonomous re-optimisation | Nobody | All require human intervention | Detect drop → diagnose → fix → verify |
| Dual-model validation | Nobody | Self-scored or single model | ChatGPT + Gemini cross-validation |

---

## 2. Competitive Landscape

### Direct Competitors (Content + SEO)

| Tool | Price | Strengths | Gaps |
|------|-------|-----------|------|
| **SurferSEO** | $99–219/mo | Content scoring (0.28 correlation to rankings) | No GEO/AISO, no autonomous publishing |
| **Jasper AI** | $39–59/mo | 30+ languages, brand voice | No SEO scoring, no publishing |
| **Frase.io** | $45–230/mo | 5-platform AI citation tracking (add-on) | No publish, no multilingual AISO |
| **MarketMuse** | $99–499/mo | Topical authority mapping | No content generation, no publishing |
| **SEO.ai** | Custom | Closest to full pipeline; Shopify support | No GEO/AISO scoring |
| **Byword** | $99–1999/mo | Programmatic SEO at scale; 80+ languages | No AISO, no Shopify, no strategy |
| **Writesonic** | $20–1499/mo | SEO + GEO combined (best current combo) | GEO is add-on; not multilingual AISO |
| **ContentShake AI** | ~$60–100/mo | Backed by Semrush's 26B keyword DB | Semrush ecosystem lock-in |
| **Koala AI** | $9–179/mo | Lowest cost/word; Deep Research Mode | No AISO, no strategy layer |
| **SEObot** | Subscription | Most autonomous found; Shopify; 50 langs | No AISO, no per-language scoring |

### GEO/AISO Monitoring Tools (Not Competitors — Potential Partners)

| Tool | What It Does | Gap |
|------|-------------|-----|
| **Otterly.ai** | AI citation tracking (ChatGPT, AIO, Perplexity) | No content action layer |
| **Profound** | 9-platform citation monitoring | Enterprise only, no content creation |
| **Scrunch AI** | Replacement analysis (who replaced you) | No action pathway from data |

### The Market Gap

**No single platform closes the full loop:** research → write → optimise → publish → audit → re-optimise — across multiple languages — with per-language AISO scoring — with Shopify-native integration.

Every GEO/AISO tool is monitoring-only. Every content tool stops at publishing. The bridge between "your citation dropped" and "content updated" does not exist.

---

## 3. What We Already Have (Foundation)

### Live Services (Production-Ready)

| Service | Recipe ID | Status |
|---------|-----------|--------|
| Technical Audit | `rcp_fUfiRNt8Bh8b` | Live |
| Keyword Research | `rcp_083WOBwKYeNo` | Live |
| Content Optimizer | `rcp_-msCRAZI2mln` | Live |
| SERP Analyzer | `rcp_tebS66AkhuYq` | Live |
| AI Discovery Audit v2.1 | `rcp_3LBwPfkiTtRT` | Live |
| Dual-Model AISO Audit | `rcp_W-q_oTUO94iI` | Live |

### Proven Frameworks

| Framework | What It Does | Where |
|-----------|-------------|-------|
| AISO 36-Factor Model | Score any page across 6 categories for AI visibility | `~/.claude/skills/aiso/` |
| 20-Criterion Page Audit | Dual-model ChatGPT + Gemini validation | `~/.claude/skills/seo-aiso-validator/` |
| Topical Cluster Architecture | Pillar + cluster content planning | `~/.claude/skills/seo-content-strategy/` |
| Content Writer Agent Spec | Article generation pipeline design | `seo-toolkit/docs/agents/content-writer-agent.md` |
| Content Pipeline Objective | 8-task pipeline with acceptance criteria | `objectives/PROD-001-seo-content-pipeline.md` |

### Battle-Tested on Real Sites

| Client | Pages Audited | Score Journey | Languages |
|--------|--------------|---------------|-----------|
| Hairgenetix | 12+ pages | 5.5 → 8.95/10 on hair-loss page | 9 languages |
| Love Over Exile | 6+ pages | Tech 90, Content 74 | 1 language |

### Key Lessons From Production Use

1. **External validators are essential.** Self-scored pages overestimate by 25-40%. ChatGPT + Gemini cross-validation catches blind spots.
2. **Schema-only changes produce zero AI score gains.** Must pair with visible content.
3. **Layout impact assessment is mandatory.** Visible SEO content has broken page designs.
4. **Shopify CDN cache is 10-30 min.** Verification must account for propagation delay.
5. **The "article blueprint" works.** Pages with answer-first + question H2s + comparison table + citations + internal links consistently score 8.5+/10.
6. **Multilingual translations must be pushed per-locale.** Shopify doesn't auto-translate template section content.

---

## 4. Feature Requirements (High-Level)

### 4.1 Autonomous Pipeline

The engine operates as a 5-stage pipeline that can run end-to-end without human intervention, but allows human override at every stage.

#### Stage 1: Research & Planning
- Input: website URL, keyword strategy, content gaps, competitor analysis
- Output: content calendar with topics, target keywords, search intent, cluster mapping
- Sources: keyword database, SERP analysis, competitor content, GSC data
- Human touchpoint: approve/edit calendar before production starts

#### Stage 2: Content Creation
- Input: approved topic + brief from Stage 1
- Output: draft article (1,500-4,000 words depending on type)
- Process: SERP analysis → outline → source research → draft → E-E-A-T signals → internal links
- Quality: citation of primary sources (PubMed, DOI for YMYL), answer-first format, question H2s, comparison tables, FAQ section
- Human touchpoint: review draft before optimisation (configurable: auto-approve or require approval)

#### Stage 3: Optimisation
- Input: draft article from Stage 2
- Output: SEO/GEO/AISO-optimised article with scores
- Process: NLP keyword density check → readability → schema generation (Article, FAQPage, BreadcrumbList) → meta tags → internal link injection → image alt text
- Scoring: run AISO 36-factor audit + 20-criterion page audit on draft
- Target: all criteria ≥ 9.0/10 before proceeding
- Loop: if score < 9.0, auto-revise and re-score (max 3 iterations)

#### Stage 4: Publishing
- Input: optimised article from Stage 3
- Output: live article on target CMS
- CMS targets (Release 1): Shopify blog posts via GraphQL Admin API
- CMS targets (Release 2): WordPress via REST API, headless CMS via webhooks
- Process: create blog article → set meta tags → deploy schema → push translations (all configured languages) → verify live page
- Human touchpoint: final publish approval (configurable: auto-publish or require approval)

#### Stage 5: Post-Publication Audit & Re-Optimisation
- Input: published article URL
- Output: live audit score + re-optimisation if needed
- Process: wait for CDN propagation → fetch live page → run dual-model audit (ChatGPT + Gemini) → compare to pre-publish score → if delta > threshold, investigate and auto-fix
- Schedule: audit at publish + 24h, then weekly for first month, then monthly
- Trigger re-optimisation: if score drops below 8.5 or AI citation lost

### 4.2 Dashboard (User Interface)

The dashboard is the human control plane. It provides visibility and editorial control over the autonomous pipeline.

#### View 1: Content Calendar & Planning
- Visual calendar (month/week view) showing planned, in-progress, and published articles
- Each article card shows: title, target keyword, cluster, status, assigned language(s)
- Drag-and-drop to reschedule
- Click to edit topic, keywords, brief
- Colour-coded by status: planned (grey), researching (blue), drafting (yellow), optimising (orange), ready for review (purple), published (green), needs attention (red)

#### View 2: Content Strategy
- Guiding content strategy document (editable by client/user)
- Topic clusters visualised as hub-and-spoke diagram
- Proposed topics per cluster with keyword data (volume, difficulty, intent)
- Coverage heatmap: which clusters are well-covered vs gaps
- Pillar pages identified and linked

#### View 3: Article Detail
- Full article preview with SEO/GEO/AISO scores
- Score breakdown: 20 criteria with individual scores
- Model comparison: ChatGPT score vs Gemini score vs average
- Edit capability: client can modify content directly
- Publishing controls: approve, schedule, reject with feedback
- Translation status per language
- Revision history

#### View 4: Site Scorecard (Before/After)
- Overall site SEO/GEO/AISO scores
- Score trend over time (line chart)
- Before vs after comparison for each page
- Per-language scoring breakdown
- AI citation tracking: is the site being cited by ChatGPT, Gemini, Perplexity?
- Share of Model (SoM) for target keywords

#### View 5: Publication Status
- Pipeline status for all articles (Kanban board or table view)
- Per-article: research status, draft status, optimisation score, publish status, audit status
- Alerts: articles needing attention (score dropped, audit failed, translation missing)
- Bulk actions: approve multiple, schedule batch, pause pipeline

### 4.3 Multi-Language Support

- All content produced in primary language first
- Auto-translation to all configured languages
- Per-language AISO scoring (run audit per locale independently)
- Per-language keyword targeting (different keywords per market)
- Translation quality check before publishing

### 4.4 Multi-Client / Multi-Site

- Each client/site has its own configuration: domain, CMS type, languages, keyword strategy, content calendar, approval workflow
- Agency view: see all clients' pipelines in one dashboard
- White-label: agency branding on reports and dashboard

---

## 5. Architecture (Standalone + Vertical)

### Standalone Service

```
┌─────────────────────────────────────┐
│        Content Engine Service        │
│                                      │
│  ┌──────────┐  ┌──────────────────┐ │
│  │ Pipeline  │  │    Dashboard     │ │
│  │ Orchestr. │  │   (React/Next)   │ │
│  │           │  │                  │ │
│  │ Stage 1-5 │  │ Calendar, Scores │ │
│  │ Scheduler │  │ Strategy, Status │ │
│  └─────┬────┘  └────────┬─────────┘ │
│        │                │            │
│  ┌─────▼────────────────▼──────────┐ │
│  │          API Layer              │ │
│  │  (REST + WebSocket for live)    │ │
│  └─────────────┬───────────────────┘ │
│                │                     │
│  ┌─────────────▼───────────────────┐ │
│  │      Agent Orchestrator         │ │
│  │                                 │ │
│  │ ┌────────┐ ┌────────┐ ┌──────┐ │ │
│  │ │Keyword │ │Content │ │AISO  │ │ │
│  │ │Research│ │Writer  │ │Audit │ │ │
│  │ └────────┘ └────────┘ └──────┘ │ │
│  │ ┌────────┐ ┌────────┐ ┌──────┐ │ │
│  │ │SERP    │ │CMS     │ │Trans-│ │ │
│  │ │Analyze │ │Publish │ │lation│ │ │
│  │ └────────┘ └────────┘ └──────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### As Part of AISOGEN Vertical (PROD-004)

```
PROD-004 SaaS Platform (Turborepo)
├── packages/
│   ├── core/           ← Auth, DB, tenant management
│   ├── seo-engine/     ← SEO Toolkit agents (already exists)
│   └── content-engine/ ← THIS FEATURE (new package)
│
├── apps/
│   └── aisogen/        ← AISOGEN vertical
│       ├── uses packages/content-engine
│       ├── uses packages/seo-engine
│       └── adds: billing, onboarding, marketplace
```

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Next.js + React | Agency standard (ADR-013) |
| API | tRPC or REST | Type-safe, fits Turborepo |
| Database | PostgreSQL + Prisma | Multi-tenant RLS (agency standard) |
| Queue/Scheduler | BullMQ + Redis | Pipeline orchestration, retry, scheduling |
| AI Models | Claude (writing), GPT-4o (validation), Gemini 2.5 (validation) | Multi-model for quality + cross-validation |
| CMS Connectors | Shopify GraphQL, WordPress REST | Pluggable adapter pattern |
| Translation | DeepL API or Claude | Per-language with quality check |
| Hosting | Vercel (frontend) + Railway/Fly (backend) | Agency standard |

---

## 6. Product Roadmap

### Release 1: Foundation (MVP)
**Goal:** Autonomous pipeline working end-to-end for one client (Hairgenetix) on Shopify.

| Feature | Priority | Effort |
|---------|----------|--------|
| Pipeline orchestrator (5-stage scheduler) | Must | Large |
| Research agent (keyword gaps → topic briefs) | Must | Medium |
| Content writer agent (brief → draft article) | Must | Large |
| SEO/AISO optimiser (score + auto-revise) | Must | Medium |
| Shopify publisher (blog article + schema + meta + translations) | Must | Medium |
| Post-publish auditor (dual-model re-audit) | Must | Medium |
| Dashboard: content calendar (read-only) | Must | Medium |
| Dashboard: article detail + scores | Must | Medium |
| Dashboard: site scorecard (before/after) | Should | Small |
| Single-client config | Must | Small |

**Validation:** Run full pipeline on Hairgenetix. Produce 5 articles autonomously. Score ≥ 8.5/10 on all. Publish to all 9 languages.

### Release 2: Dashboard & Control
**Goal:** Full editorial dashboard with human controls. Multi-client support.

| Feature | Priority | Effort |
|---------|----------|--------|
| Dashboard: content calendar (editable, drag-drop) | Must | Large |
| Dashboard: content strategy editor | Must | Medium |
| Dashboard: publication status (Kanban) | Must | Medium |
| Dashboard: per-language score breakdown | Should | Medium |
| Approval workflows (auto-approve vs human review) | Must | Medium |
| Multi-client configuration | Must | Medium |
| WordPress publisher adapter | Should | Medium |
| Notification system (article ready for review, score dropped) | Should | Small |

### Release 3: Intelligence & Automation
**Goal:** AI citation tracking and autonomous re-optimisation.

| Feature | Priority | Effort |
|---------|----------|--------|
| AI citation monitoring (ChatGPT, Gemini, Perplexity) | Must | Large |
| Share of Model tracking per keyword | Must | Large |
| Autonomous re-optimisation on score/citation drop | Must | Large |
| Competitor content monitoring | Should | Medium |
| Content freshness automation (update dates, stats, links) | Should | Medium |
| Per-language AISO scoring pipeline | Must | Medium |
| White-label agency view | Should | Medium |

### Release 4: Scale & Marketplace
**Goal:** Productise for external users via AISOGEN.

| Feature | Priority | Effort |
|---------|----------|--------|
| Self-service onboarding (connect CMS, import keywords) | Must | Large |
| Billing integration (Stripe / Lemon Squeezy) | Must | Medium |
| Content marketplace (pre-built strategies per niche) | Should | Large |
| API for third-party integrations | Should | Medium |
| Mobile dashboard | Could | Medium |
| Headless CMS adapters (Contentful, Sanity, Strapi) | Could | Medium |

---

## 7. Pricing Strategy (Informed by Market)

| Tier | Price | Includes | Target |
|------|-------|----------|--------|
| **Starter** | $79/mo | 1 site, 1 language, 10 articles/mo, SEO scoring | Small brands (Hairgenetix-size) |
| **Growth** | $199/mo | 3 sites, 3 languages, 30 articles/mo, SEO + AISO scoring | Growing e-commerce |
| **Agency** | $499/mo | 10 sites, 9 languages, unlimited articles, white-label, full closed loop | SEO agencies |
| **Enterprise** | Custom | Custom integrations, SLA, dedicated support | Large brands |

**Rationale:** $79 entry avoids the $49 quality-signal trap. $199 sweet spot aligns with Surfer/Frase agency tiers. $499 undercuts MarketMuse Enterprise ($12k/yr) while offering more automation.

---

## 8. Success Metrics

### Release 1 Validation Criteria

| Metric | Target | How We Measure |
|--------|--------|----------------|
| Articles produced autonomously | 5 articles for Hairgenetix | Count |
| Average AISO score | ≥ 8.5/10 | Dual-model audit |
| Languages per article | 9 (all Hairgenetix locales) | Translation verification |
| Human intervention per article | < 15 min review time | Time tracking |
| Pipeline duration | < 2 hours from brief to published | Pipeline logs |
| Zero layout breakage | 0 incidents | Visual verification |

### Long-Term KPIs

| Metric | Target (6 months) |
|--------|-------------------|
| Organic traffic increase | +30% on content-hub pages |
| AI citation rate | Brand mentioned in ≥ 3 AI platforms |
| Content freshness | All articles updated within 90 days |
| Customer article approval rate | > 80% first-pass approval |
| Per-article cost | < $5 (AI + compute costs) |

---

## 9. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| AI-generated content penalised by Google | High | Low | E-E-A-T signals, human review, primary source citations, author attribution |
| Content quality insufficient for YMYL (health) | High | Medium | Mandatory medical reviewer signal, PubMed citations, fact-checking agent |
| Keyword cannibalization (blog vs product pages) | Medium | Medium | Intent separation enforced: blog = informational only, products = transactional |
| Shopify API rate limits | Medium | Low | Queue-based publishing with backoff |
| Multi-language quality drift | Medium | Medium | Per-language AISO audit; native speaker review for top markets |
| Scope creep (too many features in R1) | High | High | MVP is pipeline + basic dashboard only. No calendar editing, no multi-client in R1 |
| Competitor catches up (Frase, SEO.ai) | Medium | Medium | Speed to market; build on existing battle-tested infrastructure |

---

## 10. Dependencies

| Dependency | Status | Blocker? |
|-----------|--------|----------|
| SEO Toolkit agents (5 live recipes) | Ready | No |
| AISO 36-factor scoring framework | Ready | No |
| Dual-model audit (ChatGPT + Gemini) | Ready | No |
| Shopify GraphQL API access | Ready (Hairgenetix connected) | No |
| Content Writer Agent spec | Written, not implemented | Yes — R1 |
| SaaS Platform monorepo (PROD-004) | Phase 0 complete | No — R1 standalone first |
| DeepL or translation API | Not connected | Yes — R1 multilingual |
| BullMQ / queue infrastructure | Not set up | Yes — R1 pipeline |
| Dashboard frontend | Not started | Yes — R1 |

---

## 11. Development Approach

### Phase 1: Internal Proof (Hairgenetix)
Build the pipeline as a Claude Code skill/agent first. Run it manually on Hairgenetix to validate the full loop before building the SaaS UI. This follows our "prove on ourselves first" principle.

### Phase 2: Standalone Service
Extract the pipeline into a standalone service with API and basic dashboard. Deploy for 2-3 internal clients (Hairgenetix, Love Over Exile, + 1 new).

### Phase 3: AISOGEN Integration
Package as `packages/content-engine` in the PROD-004 Turborepo. Wire into the AISOGEN vertical with multi-tenant support, billing, and onboarding.

### Spec-Driven Development (Rule 14)
This briefing feeds into the RE gate process:
- **Gate 1 (Scope):** This document → Malcolm approval
- **Gate 2 (Completeness):** Detailed requirements + design doc
- **Gate 3 (Build):** Task breakdown → sprint plan → implementation

---

## 12. Open Questions for Malcolm

1. **Approval workflow preference:** Should articles auto-publish after scoring ≥ 9.0, or always require human review before publishing?
2. **Author identity:** Articles published as "Malcolm Smith, Founder" or should we create an editorial brand voice?
3. **Priority CMS:** Shopify first (Hairgenetix), then WordPress (Love Over Exile) — correct?
4. **Translation approach:** DeepL API ($25/mo) for machine translation + human spot-check, or Claude for translation?
5. **Dashboard hosting:** Part of the agency dashboard (GitHub Pages) or standalone app (Vercel)?
6. **Budget for R1:** AI API costs (Claude + GPT-4o + Gemini) estimated at $50-100/mo for 30 articles. Acceptable?

---

## Appendix A: Competitor Feature Matrix

| Feature | Surfer | Frase | SEO.ai | Byword | Writesonic | SEObot | **Ours (R1)** | **Ours (R3)** |
|---------|--------|-------|--------|--------|------------|--------|---------------|---------------|
| AI content writing | Yes | Yes | Yes | Yes | Yes | Yes | **Yes** | **Yes** |
| SEO scoring | Yes | Yes | Yes | No | Yes | Basic | **Yes** | **Yes** |
| GEO/AISO scoring | No | Add-on | No | No | Add-on | No | **Yes** | **Yes** |
| Per-language scoring | No | No | No | No | No | No | **No** | **Yes** |
| Content calendar | No | No | Yes | No | No | No | **Yes** | **Yes** |
| Auto-publish to CMS | No | No | Yes | WP only | WP only | Shopify | **Shopify** | **Multi** |
| Post-publish audit | No | No | No | No | No | No | **Yes** | **Yes** |
| Auto re-optimise | No | No | No | No | No | No | **No** | **Yes** |
| AI citation tracking | No | Yes | No | No | No | No | **No** | **Yes** |
| Multilingual | No | No | Unk | 80+ gen | 25+ gen | 50 gen | **9 langs** | **Unlimited** |
| Shopify-native | No | No | Yes | No | No | Yes | **Yes** | **Yes** |
| Dual-model validation | No | No | No | No | No | No | **Yes** | **Yes** |
| Topical cluster planning | No | No | No | No | No | No | **Yes** | **Yes** |
| White-label | No | No | No | No | No | No | **No** | **Yes** |

## Appendix B: Technology Trends (2025-2026)

| Trend | Implication for Us |
|-------|-------------------|
| Multi-model architectures | Already doing this (Claude + GPT-4o + Gemini). Competitive advantage. |
| Agentic pipelines replacing single-shot generation | Our 5-stage pipeline is agent-native from day one. |
| GEO/AISO terminology fragmentation | Opportunity to define and own the terminology. First mover wins mindshare. |
| E-E-A-T automation gap | No tool automates compliance. Our author attribution + medical reviewer + citation pipeline is ahead. |
| Content freshness as ranking factor (#6) | Our re-audit + re-optimise loop directly addresses this. |
| Shopify ecosystem underserved | WordPress saturated. Shopify-first is a strategic differentiator. |

## Appendix C: Sources

- SurferSEO pricing and features — surferseo.com/pricing
- Frase.io GEO features — frase.io
- MarketMuse pricing — marketmuse.com/pricing
- Otterly.ai AI citation tracking — otterly.ai/pricing
- Profound citation monitoring — tryprofound.com
- Writesonic GEO review — tryanalyze.ai
- SEObot Shopify integration — coldiq.com/tools/seobot
- Byword programmatic SEO — byword.ai
- HubSpot AEO Grader — hubspot.com/aeo-grader
- AI platform citation patterns — tryprofound.com/blog
- Content freshness ranking factor — firstpagesage.com
- Topic cluster SEO impact — seo.ai/blog/topic-clusters
- Agentic AI in SEO — searchengineland.com
- AISO vs SEO vs GEO terminology — therankmasters.com
