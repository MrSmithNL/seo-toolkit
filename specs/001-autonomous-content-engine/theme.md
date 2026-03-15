# Theme — Autonomous Content Engine

> **What this is:** A theme tracks a strategic objective that spans multiple epics (12+ weeks).
> It defines the end-to-end business process, the functional breakdown, and the epic sequence.

---

## Theme Identity

| Field | Value |
|-------|-------|
| **Theme name** | Autonomous Content Engine |
| **Strategic objective** | Fully autonomous SEO/GEO/AISO content lifecycle — research through publication, scoring, and re-optimisation |
| **Product** | PROD-001 (SEO Toolkit), consumed by PROD-004 SaaS Platform via AISOGEN vertical |
| **Total appetite** | 16 weeks (4 sprints × 4 phases) |
| **Owner** | Claude (autonomous), Malcolm (gate approvals) |
| **Created** | 2026-03-15 |
| **Baseline version** | null |

---

## Architecture Classification (Gate 0)

> **COMPLETED.** See [status.md](status.md) for full Gate 0 details (RE v4.23).

| Field | Value |
|-------|-------|
| **SaaS ecosystem?** | Yes |
| **Hierarchy level** | L3-module |
| **Primary hierarchy location** | `modules/content-engine/` |
| **Capability group** | seo |
| **Tenant aware** | Yes |
| **Dual mode** | Yes — standalone CLI now, platform web later |
| **Five-Port** | Yes — Database, Auth, AIGateway, FeatureFlags, Notifications |

---

## Traceability

| Level | Reference |
|-------|-----------|
| **Product goal** | Autonomous SEO/GEO/AISO content pipeline — from keyword gap to published, scored, re-optimised article |
| **Product OKR** | KR2.1: Publish 5 autonomous articles on Hairgenetix with avg AISO score ≥ 8.5/10 (Q2 2026) |
| **BA briefing** | [automated-article-generator-briefing.md](automated-article-generator-briefing.md) |

---

## Definition of Ready (DOR) — Verified Before Epic Decomposition

> From `docs/capabilities/requirements-engineering.md` § Theme Level DOR

- [x] Parent product-level DOD is met (BA briefing complete)
- [x] Theme connected to measurable OKR (KR2.1: 5 articles, ≥8.5 AISO)
- [x] Business process this theme supports is fully mapped (5-stage pipeline — see below)
- [x] Process Decomposition Map (PDM) complete — 33 L3 sub-processes + 9 cross-cutting capabilities identified with automation level, feature class, and evidence
- [x] Capability framework D2 diagram rendered (SVG + PNG) — `diagrams/capability-framework.d2`
- [x] Competitive context for this theme's capability area documented — 10 competitors × 33 features (`research/aisogen-pdm-competitive-feature-matrix-2026.md`)
- [x] Investment appetite defined (16 weeks, $50-100/mo AI API costs)
- [x] Dependencies on other themes surfaced (PROD-004 SaaS Platform for L3→L5 integration)
- [x] Decomposition strategy chosen — Business Process (pipeline stages = epic boundaries)

## Definition of Done (DOD) — Verified Before Marking Complete

- [ ] All DOR criteria met and documented
- [ ] `specs/theme.md` fully populated: process map, PDM, FBS, capability map, epic breakdown, sequence, D2 diagram
- [ ] All epics identified with clear boundaries, scope envelopes, and dependencies
- [ ] Epic sequence diagram showing parallel/serial relationships
- [ ] Theme-level success criteria defined and measurable
- [ ] Boundary objects created: domain model, glossary, architecture guardrails, frozen decisions
- [ ] Shared contracts folder (`specs/contracts/`) populated
- [ ] Malcolm has reviewed and approved the theme-level design
- [ ] Theme spec baselined (frozen — changes require change request)

---

## Scope Flags

> Items discovered during work that fall outside this theme's scope. Escalated, not implemented.

None currently.

---

## Business Process Map

> Map the end-to-end user journey this theme supports. From BA briefing §4.1.

### End-to-End Content Lifecycle (Closed Loop)

```
[1. Research & Plan] → [2. Create Content] → [3. Optimise] → [4. Publish] → [5. Audit & Re-optimise]
        ▲                                                                              │
        └──────────────── re-optimise trigger (score drop < 8.5) ──────────────────────┘
```

### Process Steps → Candidate Epics

| Process Step | Description | Candidate Epic | Priority |
|-------------|-------------|---------------|----------|
| 1. Research & Plan | Keyword gap analysis, SERP analysis, competitor research, content calendar generation | E-001 | Must |
| 2. Create Content | AI article generation: outline → research → draft → E-E-A-T signals → internal links | E-002 | Must |
| 3. Optimise | NLP keyword density, readability, schema generation, meta tags, AISO scoring | E-003 | Must |
| 4. Publish | CMS integration (Shopify GraphQL), multi-language translation, scheduling | E-004 | Must |
| 5. Audit & Re-optimise | Post-publish dual-model scoring, automated re-revision, score tracking | E-005 | Must |
| 6. Dashboard | Content calendar, strategy editor, article detail, site scorecard, publication status | E-006 | Must |

### Exception Flows

| Exception | Trigger | Handling | Maps to |
|-----------|---------|----------|---------|
| Score below threshold | Optimisation score < 9.0 after max 3 iterations | Alert user, log failure, flag for manual review | Story in E-003 |
| CMS publish failure | Shopify API error, rate limit, network timeout | Retry with backoff (3 attempts), then queue for retry, notify user | Story in E-004 |
| Translation quality issue | Translation score below threshold | Re-translate with alternative model, flag for human review | Story in E-004 |
| Score drop post-publish | Audit score drops below 8.5 or AI citation lost | Trigger re-optimisation pipeline (max 2 auto-attempts), then escalate | Story in E-005 |
| CDN propagation delay | Live page not matching published content after 30 min | Extend wait, retry audit, notify if persistent | Story in E-005 |
| YMYL compliance flag | Medical/health content without citations | Block publication, require human review with PubMed citations | Story in E-003 |

---

## Process Decomposition Map (PDM)

> **Mandatory.** Decomposes the entire value chain into 4 levels. Every L3 sub-process becomes a candidate feature.
> Evidence column records competitor coverage (N/M competitors). Source: `research/aisogen-pdm-competitive-feature-matrix-2026.md` (10 competitors analysed).

### Full Process Decomposition

| Process ID | L1 Domain | L2 Process Area | L3 Sub-Process | Automation | Class | Evidence | Coverage | Target Epic |
|:----------:|-----------|-----------------|----------------|:----------:|:-----:|:--------:|:--------:|:-----------:|
| 1.0 | **Research & Strategy** | | — | — | — | — | — | — |
| 1.1 | | Keyword Intelligence | Keyword research / gap analysis | AUTO | TS | 10/10 | GAP | E-001 |
| 1.2 | | Keyword Intelligence | Topic clustering | AUTO | DF | 7/10 | GAP | E-001 |
| 1.3 | | Keyword Intelligence | Search intent classification | AUTO | TS | 10/10 | GAP | E-001 |
| 1.4 | | Competitive Intelligence | SERP analysis | AUTO | TS | 10/10 | GAP | E-001 |
| 1.5 | | Competitive Intelligence | Competitor content analysis | AUTO | TS | 10/10 | GAP | E-001 |
| 1.6 | | Competitive Intelligence | Content gap identification | AUTO | TS | 10/10 | GAP | E-001 |
| 1.7 | | Content Planning | Content calendar / planning | ASSISTED | TS | 8/10 | GAP | E-001 |
| 2.0 | **Content Creation** | | — | — | — | — | — | — |
| 2.1 | | Article Generation | AI article generation (long-form) | AUTO | TS | 9/10 | GAP | E-002 |
| 2.2 | | Article Generation | Outline generation | AUTO | TS | 9/10 | GAP | E-002 |
| 2.3 | | Article Generation | Research / source citation | AUTO | DF | 9/10 (3 YES) | GAP | E-002 |
| 2.4 | | Content Enhancement | E-E-A-T signal injection | AUTO | DF | 9/10 (0 YES) | GAP | E-002 |
| 2.5 | | Content Enhancement | Internal linking | AUTO | DF | 7/10 | GAP | E-002 |
| 2.6 | | Content Enhancement | Image generation / selection | ASSISTED | DF | 7/10 | GAP | E-002 |
| 2.7 | | Content Enhancement | Brand voice / tone matching | AUTO | TS | 9/10 | GAP | E-002 |
| 3.0 | **Optimisation** | | — | — | — | — | — | — |
| 3.1 | | SEO Scoring | On-page SEO scoring | AUTO | TS | 10/10 | GAP | E-003 |
| 3.2 | | SEO Scoring | NLP keyword optimisation | AUTO | TS | 9/10 | GAP | E-003 |
| 3.3 | | SEO Scoring | Readability analysis | AUTO | TS | 9/10 | GAP | E-003 |
| 3.4 | | SEO Scoring | Content structure analysis | AUTO | TS | 10/10 | GAP | E-003 |
| 3.5 | | Technical SEO | Schema markup generation | AUTO | IN | 4/10 (all partial) | GAP | E-003 |
| 3.6 | | Technical SEO | Meta tag optimisation | AUTO | TS | 10/10 | GAP | E-003 |
| 3.7 | | AI Visibility | AISO / AI visibility scoring | AUTO | TS | 9/10 | GAP | E-003 |
| 4.0 | **Publishing** | | — | — | — | — | — | — |
| 4.1 | | CMS Integration | CMS integration (WordPress) | AUTO | TS | 10/10 | GAP | E-004 |
| 4.2 | | CMS Integration | CMS integration (Shopify) | AUTO | IN | 2/10 | GAP | E-004 |
| 4.3 | | Content Delivery | Multi-language translation | AUTO | DF | 9/10 (4 YES) | GAP | E-004 |
| 4.4 | | Content Delivery | Scheduling / content calendar | AUTO | TS | 8/10 | GAP | E-004 |
| 4.5 | | Content Governance | Version control / history | AUTO | DF | 9/10 (2 YES) | GAP | E-004 |
| 4.6 | | Content Governance | Approval workflows | ASSISTED | DF | 7/10 | GAP | E-004 |
| 5.0 | **Measurement & Re-optimisation** | | — | — | — | — | — | — |
| 5.1 | | Performance Monitoring | Post-publish content audit | AUTO | DF | 7/10 (2 YES) | GAP | E-005 |
| 5.2 | | Performance Monitoring | Score tracking over time | AUTO | TS | 8/10 | GAP | E-005 |
| 5.3 | | Performance Monitoring | AI citation monitoring | AUTO | TS | 8/10 | GAP | E-005 |
| 5.4 | | Performance Monitoring | Performance dashboards | ASSISTED | TS | 10/10 | GAP | E-006 |
| 5.5 | | Performance Monitoring | Competitor rank tracking | AUTO | TS | 8/10 | GAP | E-005 |
| 5.6 | | Autonomous Remediation | Automated re-optimisation | AUTO | IN | 3/10 (all partial) | GAP | E-005 |

### Cross-Cutting Capabilities

> Capabilities that span multiple L1 domains. Use `X.N` IDs.

| ID | Capability | Automation | Class | Evidence | Coverage |
|:--:|-----------|:----------:|:-----:|:--------:|:--------:|
| X.1 | Pipeline orchestration (BullMQ job queue) | AUTO | EN | 2/10 (SEObot, AirOps) | GAP |
| X.2 | Multi-model AI gateway (Claude + GPT-4o + Gemini) | AUTO | EN | 3/10 (partial) | GAP |
| X.3 | Five-Port adapter interfaces | AUTO | EN | 0/10 | GAP |
| X.4 | Audit trail / execution logging | AUTO | EN | 4/10 (partial) | GAP |
| X.5 | Feature flags (per-tenant) | AUTO | EN | 1/10 | GAP |
| X.6 | Per-language AISO scoring | AUTO | IN | 0/10 | GAP |
| X.7 | Product-aware content briefs (e-commerce) | AUTO | IN | 0/10 | GAP |
| X.8 | Multi-CMS orchestration | AUTO | IN | 1/10 (SEO.ai partial) | GAP |
| X.9 | YMYL compliance gate | ASSISTED | DF | 0/10 | GAP |

### Coverage Statistics

| Metric | Value |
|--------|-------|
| Total L3 sub-processes | 33 |
| AUTO | 30 (91%) |
| ASSISTED | 3 (9%) |
| HUMAN-LED | 0 (0%) |
| HUMAN-ONLY | 0 (0%) |
| Table-stakes (TS) | 21 |
| Differentiators (DF) | 9 |
| Innovations (IN) | 3 |
| Enablers (EN — cross-cutting) | 5 |
| Innovation opportunities (cross-cutting) | 4 |
| Coverage gaps | 33/33 (all GAP — greenfield) |
| Competitors analysed | 10 |
| Cross-cutting capabilities | 9 |

### Capability Framework Diagram

> Render as D2 diagram: `specs/001-autonomous-content-engine/diagrams/capability-framework.d2` → `.svg` + `.png`

![Capability Framework](diagrams/capability-framework.svg)

Source: [`diagrams/capability-framework.d2`](diagrams/capability-framework.d2) — rendered to SVG + PNG.

---

## Functional Breakdown Structure

> Derived from the PDM above. Same hierarchy as a tree, with automation level and feature class tags inline.

```
Theme: Autonomous Content Engine
├── E-001: Research & Strategy
│   ├── Feature 1.1: Keyword research / gap analysis [AUTO] [TS]
│   │   ├── Story: Seed keyword expansion via AI + SERP API
│   │   ├── Story: Keyword difficulty scoring
│   │   └── Story: Gap-vs-competitor report generation
│   ├── Feature 1.2: Topic clustering [AUTO] [DF]
│   │   ├── Story: Semantic clustering algorithm
│   │   └── Story: Cluster-to-pillar mapping
│   ├── Feature 1.3: Search intent classification [AUTO] [TS]
│   │   └── Story: Intent classifier (informational / transactional / navigational)
│   ├── Feature 1.4: SERP analysis [AUTO] [TS]
│   │   ├── Story: Top-10 SERP scraping and parsing
│   │   └── Story: SERP feature detection (PAA, featured snippet, AI overview)
│   ├── Feature 1.5: Competitor content analysis [AUTO] [TS]
│   │   ├── Story: Competitor page download and extraction
│   │   └── Story: Content quality benchmarking (word count, structure, E-E-A-T signals)
│   ├── Feature 1.6: Content gap identification [AUTO] [TS]
│   │   └── Story: Gap matrix (our topics vs competitor topics)
│   └── Feature 1.7: Content calendar / planning [ASSISTED] [TS]
│       ├── Story: AI-generated content calendar from gap analysis
│       └── Story: Priority scoring (opportunity × difficulty)
├── E-002: Content Creation
│   ├── Feature 2.1: AI article generation (long-form) [AUTO] [TS]
│   │   ├── Story: Multi-section article generation (2000-4000 words)
│   │   ├── Story: Iterative section-by-section writing with context window
│   │   └── Story: Multi-model generation (Claude primary, GPT-4o fallback)
│   ├── Feature 2.2: Outline generation [AUTO] [TS]
│   │   ├── Story: SERP-informed outline from top-10 analysis
│   │   └── Story: Outline approval checkpoint (ASSISTED gate)
│   ├── Feature 2.3: Research / source citation [AUTO] [DF]
│   │   ├── Story: PubMed / academic source retrieval for YMYL topics
│   │   ├── Story: Citation formatting and verification
│   │   └── Story: Source credibility scoring
│   ├── Feature 2.4: E-E-A-T signal injection [AUTO] [DF]
│   │   ├── Story: Author bio and credentials insertion
│   │   ├── Story: Expert quote / study reference integration
│   │   └── Story: First-person experience signals for health content
│   ├── Feature 2.5: Internal linking [AUTO] [DF]
│   │   ├── Story: Site crawl / sitemap parsing for link inventory
│   │   └── Story: Contextual anchor text insertion
│   ├── Feature 2.6: Image generation / selection [ASSISTED] [DF]
│   │   ├── Story: Stock image search and selection
│   │   └── Story: Alt text generation
│   └── Feature 2.7: Brand voice / tone matching [AUTO] [TS]
│       ├── Story: Brand voice profile creation from existing content
│       └── Story: Tone consistency scoring
├── E-003: Optimisation
│   ├── Feature 3.1: On-page SEO scoring [AUTO] [TS]
│   │   ├── Story: 36-factor AISO scoring engine (existing framework)
│   │   └── Story: Score breakdown with actionable recommendations
│   ├── Feature 3.2: NLP keyword optimisation [AUTO] [TS]
│   │   ├── Story: TF-IDF keyword density analysis
│   │   └── Story: Semantic keyword variant insertion
│   ├── Feature 3.3: Readability analysis [AUTO] [TS]
│   │   └── Story: Flesch-Kincaid + custom health content readability
│   ├── Feature 3.4: Content structure analysis [AUTO] [TS]
│   │   ├── Story: Heading hierarchy validation (H1→H6)
│   │   └── Story: Paragraph length and scannability scoring
│   ├── Feature 3.5: Schema markup generation [AUTO] [IN]
│   │   ├── Story: Article schema (NewsArticle, HowTo, FAQ)
│   │   ├── Story: Product schema for e-commerce content
│   │   └── Story: Medical/health schema (MedicalWebPage) for YMYL
│   ├── Feature 3.6: Meta tag optimisation [AUTO] [TS]
│   │   ├── Story: Title tag generation (keyword + brand)
│   │   └── Story: Meta description with CTA
│   └── Feature 3.7: AISO / AI visibility scoring [AUTO] [TS]
│       ├── Story: Dual-model validation (ChatGPT + Gemini)
│       ├── Story: Citation likelihood prediction
│       └── Story: AI-specific content signals (definitional, comparative, listicle)
├── E-004: Publishing
│   ├── Feature 4.1: CMS integration (WordPress) [AUTO] [TS]
│   │   └── Story: WordPress REST API publish adapter
│   ├── Feature 4.2: CMS integration (Shopify) [AUTO] [IN]
│   │   ├── Story: Shopify GraphQL blog article creation
│   │   ├── Story: Shopify metafield population (SEO, schema)
│   │   └── Story: Layout-safe content injection (no breakage — BA §3.4 lesson)
│   ├── Feature 4.3: Multi-language translation [AUTO] [DF]
│   │   ├── Story: AI translation (9 Hairgenetix languages)
│   │   ├── Story: Translation quality scoring
│   │   └── Story: Per-language SEO metadata translation
│   ├── Feature 4.4: Scheduling / content calendar [AUTO] [TS]
│   │   └── Story: Scheduled publish with timezone support
│   ├── Feature 4.5: Version control / history [AUTO] [DF]
│   │   └── Story: Content revision tracking (diff + rollback)
│   └── Feature 4.6: Approval workflows [ASSISTED] [DF]
│       ├── Story: Human review gate (< 15 min target)
│       └── Story: Auto-approve for score ≥ 9.0 (configurable)
├── E-005: Measurement & Re-optimisation
│   ├── Feature 5.1: Post-publish content audit [AUTO] [DF]
│   │   ├── Story: Live page fetch and re-score
│   │   └── Story: CDN propagation detection and wait
│   ├── Feature 5.2: Score tracking over time [AUTO] [TS]
│   │   └── Story: Score history database with trend analysis
│   ├── Feature 5.3: AI citation monitoring [AUTO] [TS]
│   │   ├── Story: ChatGPT citation check (via API)
│   │   ├── Story: Gemini citation check (via API)
│   │   └── Story: Citation drop alert trigger
│   ├── Feature 5.5: Competitor rank tracking [AUTO] [TS]
│   │   └── Story: SERP position monitoring per keyword
│   └── Feature 5.6: Automated re-optimisation [AUTO] [IN]
│       ├── Story: Score drop detection (threshold < 8.5)
│       ├── Story: Automated diagnosis (what changed)
│       ├── Story: Content revision generation
│       └── Story: Re-publish + re-score loop (max 2 auto-attempts)
└── E-006: Dashboard & Reporting
    └── Feature 5.4: Performance dashboards [ASSISTED] [TS]
        ├── Story: Content calendar view
        ├── Story: Article detail with score history
        ├── Story: Site scorecard (aggregate AISO scores)
        └── Story: Publication status tracker
```

---

## Capability Map

> Business capabilities this theme delivers. Maturity: 0 = none, 1 = basic, 2 = functional, 3 = optimised, 4 = leading.

| ID | Capability | Tier | Current | Target | Gap | Epic |
|----|-----------|------|:-------:|:------:|:---:|------|
| CAP-SEO-001 | Keyword & Content Research | Core | 2 | 4 | Major | E-001 |
| CAP-SEO-002 | AI Content Generation | Core | 2 | 4 | Major | E-002 |
| CAP-SEO-003 | Content Optimisation & Scoring | Core | 3 | 4 | Moderate | E-003 |
| CAP-SEO-004 | CMS Publishing Pipeline | Core | 1 | 4 | Major | E-004 |
| CAP-SEO-005 | Post-Publish Audit & Re-optimisation | Core | 1 | 4 | Major | E-005 |
| CAP-SEO-006 | Content Performance Dashboards | Supporting | 0 | 3 | Major | E-006 |
| CAP-SEO-007 | Multi-Language Content Delivery | Supporting | 1 | 3 | Moderate | E-004 |
| CAP-SEO-008 | Schema & Structured Data Generation | Supporting | 0 | 3 | Major | E-003 |
| CAP-SEO-009 | AISO / AI Visibility Scoring | Core | 3 | 4 | Moderate | E-003/E-005 |
| CAP-SEO-010 | Pipeline Orchestration (BullMQ) | Enabling | 0 | 3 | Major | E-001 (infra) |

> **Current maturity notes:** CAP-SEO-001 and CAP-SEO-002 at level 2 because 6 production recipes exist (BA §3). CAP-SEO-003 and CAP-SEO-009 at level 3 because the 36-factor AISO framework is proven (Hairgenetix 5.5→8.95). CAP-SEO-004 at level 1 because Shopify publishing is manual today. CAP-SEO-005 at level 1 because scoring exists but re-optimisation is manual.

---

## Epic Breakdown

| ID | Epic | Capability Area | Appetite | Priority | Depends On | Status |
|----|------|----------------|----------|----------|------------|--------|
| E-001 | Research & Strategy Engine | Keyword Intelligence, Competitive Intel, Content Planning | 3 weeks | Must | — | Not started |
| E-002 | Content Creation Pipeline | Article Generation, Content Enhancement | 4 weeks | Must | E-001 | Not started |
| E-003 | Optimisation & Scoring Engine | SEO Scoring, Technical SEO, AI Visibility | 3 weeks | Must | E-002 | Not started |
| E-004 | Publishing Pipeline | CMS Integration, Translation, Scheduling, Governance | 3 weeks | Must | E-003 | Not started |
| E-005 | Audit & Re-optimisation Loop | Performance Monitoring, Autonomous Remediation | 2 weeks | Must | E-004 | Not started |
| E-006 | Dashboard & Reporting | Performance Dashboards, Content Calendar UI | 1 week | Must | E-005 | Not started |

> **Total: 16 weeks** — matches theme appetite. E-001 through E-005 are serial (pipeline stages). E-006 can begin partial work alongside E-004/E-005 (dashboard scaffolding).

### Epic Sequence

```
E-001 (Research) ──→ E-002 (Create) ──→ E-003 (Optimise) ──→ E-004 (Publish) ──→ E-005 (Audit)
                                                                    │                    │
                                                                    └──→ E-006 (Dashboard) ←─┘
```

> **Serial pipeline:** Each epic produces outputs consumed by the next. E-006 is partially parallel — dashboard scaffolding can start during E-004, but data views require E-005 outputs.

### Epic Scope Envelopes

| Epic | In Scope | Out of Scope |
|------|----------|-------------|
| E-001 | Keyword research, SERP analysis, competitor analysis, gap identification, topic clustering, intent classification, content calendar generation | Paid keyword data (use free APIs + AI), Google Ads integration |
| E-002 | Long-form article generation, outline generation, research/citation, E-E-A-T signals, internal linking, image selection, brand voice | Video content, social media content, ad copy |
| E-003 | On-page SEO scoring, NLP keyword optimisation, readability, structure analysis, schema markup, meta tags, AISO scoring, YMYL compliance | Backlink analysis, domain authority scoring |
| E-004 | Shopify GraphQL publishing, WordPress REST API, 9-language translation, scheduling, version control, approval workflows | Custom CMS adapters beyond Shopify/WordPress |
| E-005 | Live page audit, score tracking, AI citation monitoring, competitor rank tracking, automated re-optimisation (max 2 auto-attempts) | Google Analytics integration, paid rank tracking APIs |
| E-006 | Content calendar, article detail, site scorecard, publication status | Custom report builder, data export, white-labelling |

### Decomposition Strategy Used

> **Business Process** decomposition — each epic covers a stage of the content lifecycle pipeline (Research → Create → Optimise → Publish → Audit). This aligns naturally with the BA briefing's 5-stage architecture and the module's pipeline-based design.

Reasoning: The content engine is fundamentally a pipeline — each stage transforms inputs from the previous stage. The stages have clear boundaries (different data shapes, different external dependencies, different failure modes). This makes Business Process the natural decomposition strategy over Value Stream (which would mix stages) or Capability Area (which would fragment the pipeline).

---

## Research Summary

> BA-provided research (refine-only, per BA→RE integration rule):

| Research | Status | Key Finding |
|----------|--------|-------------|
| Market sizing (BA §7) | Complete (BA) | 4 tiers: Starter $79, Growth $199, Agency $499, Enterprise custom |
| Existing capabilities (BA §3) | Complete (BA) | 6 production recipes, 36-factor AISO framework, proven on Hairgenetix (5.5→8.95/10) |
| Technology landscape (BA §5) | Complete (BA) | Next.js + BullMQ + Drizzle + multi-model (Claude/GPT-4o/Gemini) |
| Competitive feature matrix | **Complete** | 10 competitors × 33 features. 21 TS, 9 DF, 3 IN. Market leader SEO.ai at 76%. AISOGEN targets 100%. See `research/aisogen-pdm-competitive-feature-matrix-2026.md` |
| Lessons from production (BA §3.4) | Complete (BA) | 6 key lessons: self-scoring overestimates 25-40%, schema-only = 0 gain, layout breakage risk |

---

## Success Criteria (Theme-Level)

> From BA briefing §8:

- [ ] 5 articles produced autonomously on Hairgenetix with avg AISO score ≥ 8.5/10
- [ ] Pipeline duration < 2 hours (brief to published)
- [ ] Human intervention < 15 min review time per article
- [ ] All 9 Hairgenetix languages translated and scored
- [ ] Zero layout breakage incidents
- [ ] Per-article cost < $5 (AI + compute)

---

## Frozen Decisions (Boundary Objects)

| # | Decision | Rationale | Date | Reversible? |
|---|----------|-----------|------|-------------|
| 1 | L3 Business Module in PROD-004 | Pluggable business feature, not foundation | 2026-03-15 | No |
| 2 | Dual-mode: standalone CLI + platform web | Prove value standalone, integrate later | 2026-03-15 | No |
| 3 | Five-Port adapter pattern | Same interfaces, swap adapters for platform | 2026-03-15 | No |
| 4 | TypeScript for engine | Five-Port chain is TS-native, PROD-004 is TS | 2026-03-15 | No |
| 5 | Business Process decomposition | Pipeline stages = natural epic boundaries | 2026-03-15 | Yes |
| 6 | Shopify-first CMS adapter | Hairgenetix is the R1 validation target | 2026-03-15 | Yes |
| 7 | Dual-model validation (ChatGPT + Gemini) | Self-scoring overestimates by 25-40% (BA §3.4) | 2026-03-15 | No |

---

## Glossary

| Term | Definition |
|------|-----------|
| **AISO** | AI Search Optimisation — optimising content for AI platforms (ChatGPT, Gemini, Perplexity) to cite |
| **GEO** | Generative Engine Optimisation — broader term for AISO + AI-native search |
| **E-E-A-T** | Experience, Expertise, Authoritativeness, Trustworthiness — Google's quality signals |
| **YMYL** | Your Money or Your Life — content that could impact health/safety/finances (requires higher quality bar) |
| **Five-Port** | Adapter pattern with 5 standard interfaces (Database, Auth, AIGateway, FeatureFlags, Notifications) |
| **Dual-mode** | Module works standalone (CLI) now and as platform package later |
| **PDM** | Process Decomposition Map — 4-level process-to-feature hierarchy |
| **FBS** | Functional Breakdown Structure — tree view of Theme → Epic → Feature → Story |

---

## Session Log

| Date | What Happened | Next Step |
|------|--------------|-----------|
| 2026-03-15 | Gate 0 architecture classification completed (RE v4.23). All 29 dependency items assessed. | Phase 0: Theme Identification |
| 2026-03-15 | Theme.md created with identity, traceability, process map, success criteria, frozen decisions, glossary. Competitive research launched for PDM evidence. | Populate PDM with competitive research results |
| 2026-03-15 | PDM populated: 33 L3 sub-processes + 9 cross-cutting capabilities. FBS tree with ~55 stories. Capability map (10 capabilities, maturity scored). Epic breakdown (6 epics, 16 weeks, serial pipeline). Competitive feature matrix: 10 competitors, 21 TS / 9 DF / 3 IN. | Render D2 capability diagram, Malcolm review |
