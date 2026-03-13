# Theme — Autonomous Content Engine

> **What this is:** A theme tracks a strategic objective that spans multiple epics (12+ weeks).
> It defines the end-to-end business process, the functional breakdown, and the epic sequence.

---

## Theme Identity

| Field | Value |
|-------|-------|
| **Theme name** | Autonomous Content Engine |
| **Strategic objective** | Build a fully autonomous content generation pipeline that creates SEO+AISO-optimised articles from keyword input to published page, with no human intervention required |
| **Product** | PROD-001 (SEO Toolkit) |
| **Total appetite** | 16 weeks |
| **Owner** | Malcolm |
| **Created** | 2026-03-13 |
| **Baseline version** | null |

---

## Traceability

| Level | Reference |
|-------|-----------|
| **Product goal** | PROD-001: SEO Toolkit — the capability engine that powers AISOGEN and agency client work |
| **Product OKR** | Company O1 KR1.1 — Revenue from AISOGEN/SellFunnel products; Company O1 KR1.2 — Content pipeline operational for client SEO services |

---

## Definition of Ready (DOR) — Verified Before Epic Decomposition

> From `docs/capabilities/requirements-engineering.md` § Theme Level DOR

- [x] Parent product-level DOD is met (product is fully understood)
- [x] Theme connected to measurable OKR (Objective + Key Results)
- [x] Business process this theme supports is fully mapped (end-to-end user journey)
- [x] Process Decomposition Map (PDM) complete — all L1→L3 sub-processes identified with automation level and feature class
- [x] Capability framework D2 diagram rendered (SVG + PNG)
- [x] Competitive context for this theme's capability area documented
- [x] Investment appetite defined (time, budget, capacity)
- [x] Dependencies on other themes surfaced
- [x] Decomposition strategy chosen (Value Stream / User Journey / Capability / Process)

## Definition of Done (DOD) — Verified Before Marking Complete

> From `docs/capabilities/requirements-engineering.md` § Theme Level DOD

- [x] All DOR criteria met and documented
- [x] `specs/theme.md` fully populated: process map, PDM, FBS, capability map, epic breakdown, sequence, D2 diagram
- [x] All epics identified with clear boundaries, scope envelopes, and dependencies
- [x] Epic sequence diagram showing parallel/serial relationships
- [x] Theme-level success criteria defined and measurable
- [ ] Boundary objects created: domain model, glossary, architecture guardrails, frozen decisions
- [ ] Shared contracts folder (`specs/contracts/`) populated
- [ ] Malcolm has reviewed and approved the theme-level design
- [ ] Theme spec **baselined** (frozen — changes require change request)

---

## Scope Flags

> Items discovered during work that fall outside this theme's scope. Escalated, not implemented.

None currently.

---

## Business Process Map

> Map the end-to-end user journey this theme supports. Each major step becomes a candidate epic.

### End-to-End Content Pipeline Journey

```
[Step 1: Configure] → [Step 2: Research] → [Step 3: Generate] → [Step 4: Optimise] → [Step 5: Publish] → [Step 6: Monitor & Refresh]
```

### Process Steps → Epics

| Process Step | Description | Candidate Epic | Priority |
|-------------|-------------|---------------|----------|
| Configure | User sets up target site, brand voice, topics, publishing credentials, quality thresholds | E-001 | Must |
| Research | System performs keyword research, SERP analysis, competitor content analysis, identifies content gaps | E-002 | Must |
| Generate | AI generates full-length articles with SEO+AISO optimisation baked in from first draft | E-003 | Must |
| Optimise | System scores article against 36-factor AISO model + NLP coverage, iterates to meet thresholds | E-003 | Must |
| Publish | System publishes to CMS (WordPress, Shopify) with schema markup, images, internal links | E-004 | Should |
| Monitor & Refresh | System tracks rankings + AI visibility, auto-detects content decay, triggers refresh | E-005 | Could |

### Exception Flows

| Exception | Trigger | Handling | Maps to |
|-----------|---------|----------|---------|
| Quality below threshold | Article scores < 6/10 on AISO model | Regenerate with adjusted parameters (max 3 attempts), then flag for human review | Story in E-003 |
| CMS publish failure | API error, auth expired, rate limit | Retry with backoff, queue for manual publish, notify user | Story in E-004 |
| Keyword cannibalisation detected | New article targets keyword already ranking | Skip keyword, suggest alternative, log for user review | Story in E-002 |
| AI model unavailable | Primary model API down | Failover to secondary model (GPT-4o fallback) | Story in E-003 |

---

## Process Decomposition Map (PDM)

> **Mandatory.** Decomposes the entire value chain into 4 levels. Every L3 sub-process becomes a candidate feature. Based on competitive research of 13 competitors (see `research/competitive-landscape.md`).

### Full Process Decomposition

| Process ID | L1 Domain | L2 Process Area | L3 Sub-Process | Automation | Class | Evidence | Coverage | Target Epic |
|:----------:|-----------|-----------------|----------------|:----------:|:-----:|:--------:|:--------:|:-----------:|
| 1.0 | configure | Site & Brand Setup | — | — | — | — | — | E-001 |
| 1.1 | configure | Site & Brand Setup | Site URL registration & crawl config | AUTO | TS | 10/13 competitors | GAP | E-001 |
| 1.2 | configure | Site & Brand Setup | Brand voice training | ASSISTED | DF | 3/13 (Jasper, Frase, Copy.ai) | GAP | E-001 |
| 1.3 | configure | Site & Brand Setup | CMS connection setup (WordPress, Shopify) | ASSISTED | TS | 10/13 competitors | GAP | E-001 |
| 1.4 | configure | Site & Brand Setup | Topic/niche configuration | ASSISTED | TS | 8/13 competitors | GAP | E-001 |
| 1.5 | configure | Site & Brand Setup | Quality threshold settings | ASSISTED | DF | 2/13 (Surfer, Clearscope) | GAP | E-001 |
| 1.6 | configure | Site & Brand Setup | AISO scoring preferences | ASSISTED | IN | 0/13 competitors | GAP | E-001 |
| 2.0 | research | Keyword Intelligence | — | — | — | — | — | E-002 |
| 2.1 | research | Keyword Intelligence | Keyword research & discovery | AUTO | TS | 9/13 competitors | GAP | E-002 |
| 2.2 | research | Keyword Intelligence | Keyword clustering & topic mapping | AUTO | DF | 3/13 (Scalenut, MarketMuse, Frase) | GAP | E-002 |
| 2.3 | research | Keyword Intelligence | Search intent classification | AUTO | DF | 4/13 (Surfer, Frase, Scalenut, Clearscope) | GAP | E-002 |
| 2.4 | research | Keyword Intelligence | Keyword cannibalisation detection | AUTO | DF | 2/13 (Clearscope, MarketMuse) | GAP | E-002 |
| 2.5 | research | Content Gap Analysis | — | — | — | — | — | E-002 |
| 2.5.1 | research | Content Gap Analysis | Competitor content audit | AUTO | TS | 8/13 competitors | GAP | E-002 |
| 2.5.2 | research | Content Gap Analysis | Content gap identification | AUTO | TS | 7/13 competitors | GAP | E-002 |
| 2.5.3 | research | Content Gap Analysis | SERP analysis & feature detection | AUTO | TS | 8/13 competitors | GAP | E-002 |
| 2.6 | research | AISO Intelligence | — | — | — | — | — | E-002 |
| 2.6.1 | research | AISO Intelligence | AI engine citation analysis | AUTO | IN | 0/13 (Frase/Scalenut monitor but don't analyse for generation) | GAP | E-002 |
| 2.6.2 | research | AISO Intelligence | Entity coverage gap analysis | AUTO | IN | 0/13 competitors | GAP | E-002 |
| 2.6.3 | research | AISO Intelligence | Schema opportunity detection | AUTO | IN | 0/13 competitors | GAP | E-002 |
| 3.0 | generate | Content Generation | — | — | — | — | — | E-003 |
| 3.1 | generate | Content Generation | Content brief generation | AUTO | TS | 7/13 (Frase, Surfer, Scalenut, ContentShake, Writesonic, Koala, MarketMuse) | GAP | E-003 |
| 3.2 | generate | Content Generation | Article outline generation | AUTO | TS | 10/13 competitors | GAP | E-003 |
| 3.3 | generate | Content Generation | Full article generation (1,500-5,000 words) | AUTO | TS | 11/13 competitors | GAP | E-003 |
| 3.4 | generate | Content Generation | AISO-native content structuring | AUTO | IN | 0/13 (our 36-factor model is unique) | GAP | E-003 |
| 3.5 | generate | Content Generation | NLP term integration | AUTO | DF | 6/13 (Surfer, Frase, Scalenut, NeuronWriter, Clearscope, MarketMuse) | GAP | E-003 |
| 3.6 | generate | Content Generation | Image generation/sourcing | ASSISTED | DF | 4/13 (ArticleForge, Koala, Writesonic, ContentShake) | GAP | E-003 |
| 3.7 | generate | Content Optimisation | — | — | — | — | — | E-003 |
| 3.7.1 | generate | Content Optimisation | SEO content scoring (0-100) | AUTO | TS | 7/13 competitors | GAP | E-003 |
| 3.7.2 | generate | Content Optimisation | AISO content scoring (36-factor) | AUTO | IN | 0/13 competitors | GAP | E-003 |
| 3.7.3 | generate | Content Optimisation | Dual SEO+AISO scoring | AUTO | IN | 0/13 (Frase has dual but not 36-factor depth) | GAP | E-003 |
| 3.7.4 | generate | Content Optimisation | Iterative improvement loop | AUTO | DF | 2/13 (Surfer content editor, Frase AI agent) | GAP | E-003 |
| 3.7.5 | generate | Content Optimisation | Readability scoring | AUTO | TS | 5/13 competitors | GAP | E-003 |
| 3.7.6 | generate | Content Optimisation | Fact-checking & citation validation | ASSISTED | DF | 1/13 (Writesonic) | GAP | E-003 |
| 4.0 | publish | Content Publishing | — | — | — | — | — | E-004 |
| 4.1 | publish | Content Publishing | WordPress publishing (API) | AUTO | TS | 10/13 competitors | GAP | E-004 |
| 4.2 | publish | Content Publishing | Shopify blog publishing | AUTO | DF | 2/13 (Koala, Writesonic) | GAP | E-004 |
| 4.3 | publish | Content Publishing | Schema markup injection (6+ types) | AUTO | IN | 0/13 (Koala does entity-only) | GAP | E-004 |
| 4.4 | publish | Content Publishing | Internal link insertion | AUTO | DF | 2/13 (Koala, NeuronWriter) | GAP | E-004 |
| 4.5 | publish | Content Publishing | Image upload & alt text | AUTO | TS | 6/13 competitors | GAP | E-004 |
| 4.6 | publish | Content Publishing | Scheduled publishing | AUTO | DF | 2/13 (ArticleForge, Koala) | GAP | E-004 |
| 5.0 | monitor | Performance Monitoring | — | — | — | — | — | E-005 |
| 5.1 | monitor | Performance Monitoring | Traditional rank tracking | AUTO | TS | 5/13 (Surfer, Scalenut, Semrush ecosystem) | GAP | E-005 |
| 5.2 | monitor | Performance Monitoring | AI visibility tracking | AUTO | DF | 3/13 (Frase, Scalenut, Writesonic) | GAP | E-005 |
| 5.3 | monitor | Performance Monitoring | Content decay detection | AUTO | IN | 0/13 competitors | GAP | E-005 |
| 5.4 | monitor | Performance Monitoring | AI citation probability scoring | AUTO | IN | 0/13 competitors | GAP | E-005 |
| 5.5 | monitor | Content Refresh | — | — | — | — | — | E-005 |
| 5.5.1 | monitor | Content Refresh | Auto-refresh trigger (decay detected) | AUTO | IN | 0/13 competitors | GAP | E-005 |
| 5.5.2 | monitor | Content Refresh | Content update generation | AUTO | IN | 0/13 competitors | GAP | E-005 |

> **Note:** "Target Epic" column back-filled after epic breakdown below.

> **Evidence column:** Competitor count based on analysis of 13 competitors in `research/competitive-landscape.md`.

**Automation levels:** `AUTO` (no human input) · `ASSISTED` (AI does most, human reviews) · `HUMAN-LED` (human does primary, AI assists) · `HUMAN-ONLY` (no automation)

**Feature classes:** `TS` (table-stakes — most competitors have it) · `DF` (differentiator — 2-3 competitors have it) · `IN` (innovation — no competitor has it) · `EN` (enabler — never customer-facing)

**Coverage:** `BUILT` · `PLANNED` · `GAP`

### Cross-Cutting Capabilities

> Capabilities that span multiple L1 domains.

| ID | Capability | Automation | Class | Evidence | Coverage |
|:--:|-----------|:----------:|:-----:|:--------:|:--------:|
| X.1 | Multi-model AI routing (choose best LLM per task) | AUTO | DF | 1/13 (Jasper) | GAP |
| X.2 | API access for programmatic use | AUTO | TS | 7/13 competitors | GAP |
| X.3 | Multi-language support | AUTO | TS | 8/13 competitors | GAP |
| X.4 | Bulk generation (batch mode) | AUTO | DF | 5/13 (Koala, Byword, Writesonic, ArticleForge, Scalenut) | GAP |
| X.5 | Brand voice profiles (per-client) | ASSISTED | DF | 3/13 (Jasper, Frase, Copy.ai) | GAP |
| X.6 | White-label/agency mode | HUMAN-LED | DF | 2/13 (SEO.AI, agency tiers) | GAP |

### Coverage Statistics

| Metric | Value |
|--------|-------|
| Total L3 sub-processes | 38 |
| AUTO | 34 (89%) |
| ASSISTED | 4 (11%) |
| HUMAN-LED | 0 (0%) |
| HUMAN-ONLY | 0 (0%) |
| Table-stakes | 14 |
| Differentiators | 13 |
| Innovations | 11 |
| Coverage gaps | 38 (100% — greenfield) |
| Competitors analysed | 13 |
| Cross-cutting capabilities | 6 |

### Capability Framework Diagram

> Render as D2 diagram: `specs/diagrams/capability-framework.d2` → `.svg` + `.png`

![Capability Framework](diagrams/capability-framework.svg)

---

## Functional Breakdown Structure

> Derived from the PDM above. Same hierarchy as a tree.

```
Theme: Autonomous Content Engine
├── Epic E-001: Configuration & Setup
│   ├── Feature 1.1: Site URL registration & crawl config [AUTO] [TS]
│   ├── Feature 1.2: Brand voice training [ASSISTED] [DF]
│   ├── Feature 1.3: CMS connection setup [ASSISTED] [TS]
│   ├── Feature 1.4: Topic/niche configuration [ASSISTED] [TS]
│   ├── Feature 1.5: Quality threshold settings [ASSISTED] [DF]
│   └── Feature 1.6: AISO scoring preferences [ASSISTED] [IN]
├── Epic E-002: Research & Intelligence
│   ├── Feature 2.1: Keyword research & discovery [AUTO] [TS]
│   ├── Feature 2.2: Keyword clustering & topic mapping [AUTO] [DF]
│   ├── Feature 2.3: Search intent classification [AUTO] [DF]
│   ├── Feature 2.4: Keyword cannibalisation detection [AUTO] [DF]
│   ├── Feature 2.5.1: Competitor content audit [AUTO] [TS]
│   ├── Feature 2.5.2: Content gap identification [AUTO] [TS]
│   ├── Feature 2.5.3: SERP analysis & feature detection [AUTO] [TS]
│   ├── Feature 2.6.1: AI engine citation analysis [AUTO] [IN]
│   ├── Feature 2.6.2: Entity coverage gap analysis [AUTO] [IN]
│   └── Feature 2.6.3: Schema opportunity detection [AUTO] [IN]
├── Epic E-003: Content Generation & Optimisation
│   ├── Feature 3.1: Content brief generation [AUTO] [TS]
│   ├── Feature 3.2: Article outline generation [AUTO] [TS]
│   ├── Feature 3.3: Full article generation (1,500-5,000 words) [AUTO] [TS]
│   ├── Feature 3.4: AISO-native content structuring [AUTO] [IN]
│   ├── Feature 3.5: NLP term integration [AUTO] [DF]
│   ├── Feature 3.6: Image generation/sourcing [ASSISTED] [DF]
│   ├── Feature 3.7.1: SEO content scoring [AUTO] [TS]
│   ├── Feature 3.7.2: AISO content scoring (36-factor) [AUTO] [IN]
│   ├── Feature 3.7.3: Dual SEO+AISO scoring [AUTO] [IN]
│   ├── Feature 3.7.4: Iterative improvement loop [AUTO] [DF]
│   ├── Feature 3.7.5: Readability scoring [AUTO] [TS]
│   └── Feature 3.7.6: Fact-checking & citation validation [ASSISTED] [DF]
├── Epic E-004: Content Publishing
│   ├── Feature 4.1: WordPress publishing (API) [AUTO] [TS]
│   ├── Feature 4.2: Shopify blog publishing [AUTO] [DF]
│   ├── Feature 4.3: Schema markup injection (6+ types) [AUTO] [IN]
│   ├── Feature 4.4: Internal link insertion [AUTO] [DF]
│   ├── Feature 4.5: Image upload & alt text [AUTO] [TS]
│   └── Feature 4.6: Scheduled publishing [AUTO] [DF]
└── Epic E-005: Monitoring & Refresh
    ├── Feature 5.1: Traditional rank tracking [AUTO] [TS]
    ├── Feature 5.2: AI visibility tracking [AUTO] [DF]
    ├── Feature 5.3: Content decay detection [AUTO] [IN]
    ├── Feature 5.4: AI citation probability scoring [AUTO] [IN]
    ├── Feature 5.5.1: Auto-refresh trigger [AUTO] [IN]
    └── Feature 5.5.2: Content update generation [AUTO] [IN]
```

---

## Capability Map

> Business capabilities this theme delivers.

| ID | Capability | Tier | Current Maturity | Target Maturity | Gap | Epic |
|----|-----------|------|:----------------:|:--------------:|:---:|------|
| CAP-CE-001 | Site & Pipeline Configuration | Supporting | 0 | 3 | Major | E-001 |
| CAP-CE-002 | Keyword Intelligence | Core | 0 | 4 | Major | E-002 |
| CAP-CE-003 | Content Gap Analysis | Core | 0 | 3 | Major | E-002 |
| CAP-CE-004 | AISO Intelligence | Strategic | 0 | 4 | Major | E-002 |
| CAP-CE-005 | AI Content Generation | Core | 0 | 4 | Major | E-003 |
| CAP-CE-006 | Content Optimisation (SEO+AISO) | Strategic | 0 | 5 | Major | E-003 |
| CAP-CE-007 | CMS Publishing | Core | 0 | 3 | Major | E-004 |
| CAP-CE-008 | Schema Markup Automation | Strategic | 0 | 4 | Major | E-004 |
| CAP-CE-009 | Performance Monitoring | Core | 0 | 3 | Major | E-005 |
| CAP-CE-010 | Content Lifecycle Management | Strategic | 0 | 3 | Major | E-005 |

---

## Epic Breakdown

| ID | Epic | Capability Area | Appetite | Priority | Depends On | Status |
|----|------|----------------|----------|----------|------------|--------|
| E-001 | Configuration & Setup | Pipeline configuration, CMS integration, brand voice | 2 weeks | Must | — | Not started |
| E-002 | Research & Intelligence | Keyword research, content gaps, AISO intelligence | 4 weeks | Must | E-001 | Not started |
| E-003 | Content Generation & Optimisation | Article generation, SEO+AISO scoring, iterative improvement | 5 weeks | Must | E-002 | Not started |
| E-004 | Content Publishing | CMS publishing, schema injection, internal linking | 3 weeks | Should | E-003 | Not started |
| E-005 | Monitoring & Refresh | Rank tracking, AI visibility, content refresh | 3 weeks | Could | E-004 | Not started |

**Total: ~17 weeks** (with 1 week buffer = 16 week appetite above accounts for overlap)

### Epic Sequence

```
E-001 (Config) ─→ E-002 (Research) ─→ E-003 (Generate) ─→ E-004 (Publish)
                                                              └──→ E-005 (Monitor)
```

All epics are serial — each builds on the output of the previous. E-004 and E-005 have slight overlap potential (monitoring can start while publishing is being refined).

### Decomposition Strategy Used

> **Business Process** strategy chosen.

The autonomous content engine follows a clear pipeline process: configure → research → generate → optimise → publish → monitor. Each step in the pipeline maps naturally to an epic. This is a workflow-heavy product (not a platform with independent features), so process-based decomposition produces the cleanest boundaries.

Alternative considered: **Capability Area** decomposition (SEO capability, AISO capability, Publishing capability). Rejected because capabilities cut across the pipeline — AISO applies at research, generation, scoring, and monitoring stages. Process-based decomposition keeps each pipeline stage self-contained.

---

## Research Summary

> Product-level research lives in `specs/research/`.

| Research | Status | Key Finding |
|----------|--------|-------------|
| [Market sizing & business models](research/market-sizing-and-business-models.md) | Complete | TAM $1.2-2.65B (2025), SAM $400-700M, SOM $40-350K Y1. Hybrid pricing (subscription + credits) recommended. Target freelance SEO consultants first. |
| [Competitive landscape](research/competitive-landscape.md) | Complete | 13 competitors analysed. No competitor has AISO-native content generation. Frase + Scalenut closest (GEO scoring) but lack 36-factor depth. Blue ocean: autonomous pipeline + comprehensive schema + AI citation prediction. |
| [Technology landscape](research/technology-landscape.md) | Complete | Claude Sonnet 4.6 as primary model ($0.12-0.18/article). DataForSEO for keyword/SERP data ($0.0006/request). Hybrid NLP stack (open-source + optional Surfer API). Queue-based pipeline architecture recommended. |

---

## Success Criteria (Theme-Level)

- [ ] A user can input a keyword/topic and receive a fully generated, SEO+AISO-optimised article with schema markup — with no human editing required
- [ ] Generated articles score ≥7/10 on the 36-factor AISO scoring model
- [ ] Generated articles score ≥80/100 on SEO content scoring (comparable to Surfer/Frase)
- [ ] Pipeline cost per article ≤ $2.00 (at Claude Sonnet 4.6 pricing)
- [ ] Publishing to WordPress works autonomously via API
- [ ] At least one client site has 10+ articles generated and published by the engine within 30 days of launch

---

## Session Log

| Date | What Happened | Next Step |
|------|--------------|-----------|
| 2026-03-13 | Phase 0 started. All 3 strategic research streams completed (market sizing, competitive landscape, technology). Theme.md created with PDM (38 L3 sub-processes, 13 competitors), FBS, capability map, 5 epics identified. Two hook conflicts found and fixed (PIF-001, PIF-002). | Create D2 capability diagram, populate contracts/, proceed to Phase 1 (E-001 epic). |
