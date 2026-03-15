# Epic Status — Research & Strategy Engine

> **What this is:** Status tracker for the Research & Strategy pipeline stage —
> the first stage of the Autonomous Content Engine.

---

## Epic Identity

| Field | Value |
|-------|-------|
| **Epic ID** | E-001 |
| **Epic name** | Research & Strategy Engine |
| **Product** | PROD-001 (SEO Toolkit) |
| **Parent theme** | [theme.md](../theme.md) — Autonomous Content Engine |
| **Phase** | Release 1 (MVP) |
| **Shape Up appetite** | 3 weeks |
| **Owner** | Claude (autonomous), Malcolm (gate approvals) |
| **Created** | 2026-03-15 |
| **Capability** | CAP-SEO-001 — Keyword & Content Research |
| **Baseline version** | null |
| **Parent baseline** | Theme v0 (not yet baselined) |

---

## Architecture Classification (Gate 0)

> Inherited from theme-level Gate 0. See [theme.md](../theme.md) § Architecture Classification.

| Field | Value |
|-------|-------|
| **SaaS ecosystem?** | Yes |
| **Hierarchy level** | L3-module |
| **Hierarchy location** | `modules/content-engine/` |
| **Capability group** | seo |
| **Module manifest** | Required |
| **Tenant aware** | Yes |

### Architecture Integration Checklist

- [ ] Tenant context — every data model includes `tenant_id`
- [ ] Module manifest — `module-manifest.json` defined
- [ ] Event contracts — `research.completed`, `calendar.generated`, `brief.created` declared
- [ ] Agent tools — Keyword Research + SERP Analyzer registered in manifest
- [ ] Dependency direction — modules depend on `packages/` only
- [ ] Feature flags — all 7 features behind flags
- [ ] Temporary tenant solution — config-file tenant context (standalone mode)

---

## Traceability

| Level | Reference |
|-------|-----------|
| **Product goal** | Autonomous SEO/GEO/AISO content pipeline |
| **Theme** | `specs/001-autonomous-content-engine/theme.md` |
| **Capability** | CAP-SEO-001 — Keyword & Content Research |
| **PDM processes** | 1.1–1.7 (7 L3 sub-processes) |
| **OKR** | KR2.1: Publish 5 autonomous articles on Hairgenetix with avg AISO score >= 8.5/10 |

---

## Definition of Ready (DOR) — Verified Before Feature Decomposition

- [x] Parent theme-level DOD is met (theme PDM, FBS, epic breakdown complete)
- [ ] Lean Business Case completed
- [x] Business process this epic supports is mapped (theme.md § Business Process Map, Stage 1)
- [ ] Competitive Deep-Dive completed (5 dimensions)
- [ ] UX pattern research for this workflow completed
- [ ] Architecture decisions for this epic documented
- [ ] Cross-cutting concerns addressed
- [ ] Interface contracts with adjacent epics defined (E-001 → E-002: content briefs)
- [x] Capability map entry updated (CAP-SEO-001: current 2, target 4)
- [ ] Scope envelope created

---

## Definition of Done (DOD) — Verified Before Marking Complete

- [ ] All DOR criteria met and documented
- [ ] `epic-status.md` and `epic-design.md` fully populated
- [ ] All features identified with priorities, dependencies, and scope boundaries
- [ ] Feature dependency graph documented
- [ ] Epic-level acceptance criteria defined and measurable
- [ ] Interface contracts updated: content brief schema, research event contracts
- [ ] Scope envelopes documented for each feature
- [ ] Malcolm has reviewed and approved the epic-level design
- [ ] Epic spec baselined

---

## Scope Flags

> Items discovered during work that fall outside this epic's scope.

None currently.

---

## Phase 1: Understand the Objective

### Problem Framing Triad

#### 1. Five Whys

1. **Why do we need a Research & Strategy Engine?** — Because articles without keyword targeting don't rank or get cited by AI platforms.
2. **Why don't they rank?** — Because content is created without systematic SERP analysis, gap identification, or intent matching.
3. **Why isn't there systematic research?** — Because current research is manual (Claude + skills), taking 30-60 min per topic with no persistence.
4. **Why is manual research insufficient?** — Because it doesn't scale to 30 articles/month across 9 languages and multiple sites.
5. **Root cause:** No automated, persistent research pipeline that produces structured content briefs from keyword gaps.

#### 2. Problem Statement Canvas

| Dimension | Answer |
|-----------|--------|
| **Who has this problem?** | E-commerce store owners (Hairgenetix first) who need SEO/AISO content but lack time/expertise to research what to write |
| **Current state** | Manual keyword research via Claude + `seo-content-strategy` skill + Rube recipes. No persistence. No content calendar. No automated gap detection. |
| **Desired future state** | Input: website URL → Output: prioritised content calendar with topics, keywords, intent, cluster mapping. < 15 min human review to approve. |
| **Constraints** | Free keyword data sources only (no SEMrush/Ahrefs API budget for R1). Shopify + WordPress target CMS. $50-100/mo total AI API budget for all 5 stages. |
| **Cost of inaction** | Content remains ad-hoc, keyword-blind, not competitive. AISO scores stagnate. Organic traffic doesn't grow. Pipeline can't start without research output. |

#### 3. Jobs-to-Be-Done (JTBD)

- **JTBD 1:** "When I want to grow organic traffic, I want to know which topics my site is missing compared to competitors, so I can fill content gaps systematically."
- **JTBD 2:** "When I have a content budget (time/money), I want a prioritised list of articles to write, so I can focus on highest-impact topics first."
- **JTBD 3:** "When planning content across multiple languages, I want language-specific keyword data, so I can target the right terms in each market."
- **JTBD 4:** "When I'm not an SEO expert, I want the system to explain why each topic was chosen, so I can make informed approval decisions in < 15 minutes."

### Interaction Modality Decision (MANDATORY)

| User Class | Interaction Modality | Justification | Interim Solution (if deferred) |
|-----------|---------------------|---------------|-------------------------------|
| Store owner (Malcolm) | **CLI** (R1), **Web dashboard** (R2+) | Dual-mode architecture — prove value via CLI first, integrate into AISOGEN dashboard later | CLI outputs structured JSON/Markdown; human reviews via generated calendar document |
| Developer | **API / SDK** | Module exposes commands/queries via Five-Port interface | Same CLI commands callable programmatically |
| AISOGEN user (R4) | **Web dashboard** | Content Strategy view from BA briefing §4.2 | Not applicable until AISOGEN vertical ships |

**Competitor modality check:** All 10 competitors provide web dashboards for keyword research. CLI-only for R1 is justified because: (1) this is an internal tool first (Hairgenetix validation), (2) dashboard is planned for E-006, (3) the BA briefing explicitly specifies CLI-first dual-mode. Flagged as RAID risk.

### Assumption Mapping

| Assumption | Risk (H/M/L) | Evidence (Strong/Weak/None) | Action |
|------------|:-----------:|:-------------------------:|--------|
| Free keyword data sources provide sufficient accuracy for content planning | H | Weak | Research in Phase 2 — compare free (Google Autocomplete, Google Trends, People Also Ask) vs paid (SEMrush, DataForSEO) |
| Topic clustering can be done effectively with LLM semantic analysis (no vector DB) | M | Weak | Validate in Phase 2 — test with Hairgenetix keyword set |
| Content calendar approval takes < 15 min for a 10-article batch | M | None | Validate during R1 pilot with Malcolm |
| SERP scraping is legally and technically feasible at our scale (1-5 queries/day) | M | Strong | Low volume, SerpAPI/DataForSEO available, within ToS at this scale |
| Existing `seo-content-strategy` skill and Rube recipes are reusable as pipeline components | M | Strong | Recipes are live and tested (BA §3) |
| Gap analysis requires Google Search Console data for accuracy | H | Strong | GSC integration needed — check if Hairgenetix GSC is connected |

---

## Business Process Supported

> Stage 1 of the content lifecycle pipeline (from theme.md).

### Process Flow

```
[1. Seed Input]       → [2. Keyword Expand]   → [3. SERP Analyse]
                                                        ↓
[6. Calendar Generate] ← [5. Priority Score]   ← [4. Gap Identify]
        ↓
[7. Human Approve] → output to E-002 (Content Creation)
```

### Process Steps → Features

| Process Step | What Happens | Feature |
|-------------|-------------|---------|
| 1. Seed Input | User provides website URL + optional seed keywords | F-001 (Keyword Research) |
| 2. Keyword Expand | AI expands seeds via autocomplete, PAA, related searches | F-001 (Keyword Research) |
| 3. SERP Analyse | Scrape top-10 results per target keyword; detect SERP features | F-004 (SERP Analysis) |
| 4. Gap Identify | Compare our content vs competitor content coverage | F-006 (Content Gap ID) |
| 5. Priority Score | Score each topic by opportunity (volume × gap × difficulty) | F-001 + F-003 (Intent) |
| 6. Calendar Generate | Produce prioritised content calendar with clusters | F-007 (Content Calendar) |
| 7. Human Approve | Malcolm reviews and approves/edits calendar (< 15 min) | F-007 (Content Calendar) |

---

## Functional Breakdown

> From theme.md FBS, E-001 section.

```
Epic: E-001 Research & Strategy Engine
├── F-001: Keyword Research / Gap Analysis [AUTO] [TS]
│   ├── Story: Seed keyword expansion via AI + SERP API
│   ├── Story: Keyword difficulty scoring
│   └── Story: Gap-vs-competitor report generation
├── F-002: Topic Clustering [AUTO] [DF]
│   ├── Story: Semantic clustering algorithm
│   └── Story: Cluster-to-pillar mapping
├── F-003: Search Intent Classification [AUTO] [TS]
│   └── Story: Intent classifier (informational / transactional / navigational)
├── F-004: SERP Analysis [AUTO] [TS]
│   ├── Story: Top-10 SERP scraping and parsing
│   └── Story: SERP feature detection (PAA, featured snippet, AI overview)
├── F-005: Competitor Content Analysis [AUTO] [TS]
│   ├── Story: Competitor page download and extraction
│   └── Story: Content quality benchmarking
├── F-006: Content Gap Identification [AUTO] [TS]
│   └── Story: Gap matrix (our topics vs competitor topics)
└── F-007: Content Calendar / Planning [ASSISTED] [TS]
    ├── Story: AI-generated content calendar from gap analysis
    └── Story: Priority scoring (opportunity × difficulty)
```

---

## Current Phase

| Phase | Status | Date |
|-------|--------|------|
| **Gate 0: Architecture** | [x] Passed (theme-level) | 2026-03-15 |
| Research (Phase 1-2) | [x] In progress | 2026-03-15 |
| Design (Phase 4) | [ ] Not started | |
| **Gate 1: Scope** | [ ] Not reached | |
| Feature specs | [ ] Not started | |
| **Gate 2: Completeness** | [ ] Not reached | |
| Task breakdown | [ ] Not started | |
| **Gate 3: Build Approval** | [ ] Not reached | |
| Build | [ ] Not started | |
| **Gate: Ship** | [ ] Not reached | |

---

## Epic Goal

**One sentence:** Deliver an automated research pipeline that takes a website URL and produces a prioritised content calendar with keyword data, cluster mapping, and search intent — ready for human approval in < 15 minutes.

**Success criteria (epic-level):**
- [ ] Content calendar generated for Hairgenetix with >= 10 topic recommendations
- [ ] Each topic includes: target keyword, search volume estimate, difficulty, intent, cluster
- [ ] Human review time < 15 min for a 10-topic calendar
- [ ] Gap analysis correctly identifies >= 5 topics competitors rank for that we don't
- [ ] Pipeline runs autonomously end-to-end (no manual steps except final approval)
- [ ] Output schema compatible with E-002 (Content Creation) input requirements

---

## Feature Breakdown

| ID | Feature | Priority | Status | Depends On | Est. |
|----|---------|----------|--------|------------|------|
| F-001 | Keyword Research / Gap Analysis | Must | Not started | — | 3 days |
| F-002 | Topic Clustering | Should | Not started | F-001 | 2 days |
| F-003 | Search Intent Classification | Must | Not started | F-001 | 1 day |
| F-004 | SERP Analysis | Must | Not started | F-001 | 2 days |
| F-005 | Competitor Content Analysis | Must | Not started | F-004 | 2 days |
| F-006 | Content Gap Identification | Must | Not started | F-004, F-005 | 2 days |
| F-007 | Content Calendar / Planning | Must | Not started | F-001, F-006 | 3 days |

**Must-have features (MVP):** F-001, F-003, F-004, F-005, F-006, F-007
**Should-have features:** F-002 (topic clustering — valuable but calendar works without it)
**Could-have features:** None — all features are needed for a functional research stage

---

## Progress Summary

| Metric | Count |
|--------|-------|
| **Total features** | 7 |
| **Features complete** | 0 |
| **Total tasks** | 0 |
| **Tasks complete** | 0 |

---

## Research Summary

> Key findings from epic-level research. Full research in `research/` subfolder.

| Research File | Key Finding |
|---------------|-------------|
| `research/competitive-deep-dive.md` | _In progress — 5-dimension analysis of Frase, SEO.ai, SurferSEO, Semrush CS_ |

---

## Competitive Deep-Dive (5-Dimension Analysis)

> _In progress — being populated by research agent. See `research/competitive-deep-dive.md` when complete._

### Competitors Analysed

| # | Competitor | Product | Pricing Tier | Source Used |
|---|-----------|---------|-------------|-------------|
| A | Frase.io | Agentic SEO + GEO Platform | Solo $15/mo, Team $115/mo | docs, help centre, API |
| B | SEO.ai | Autonomous SEO Pipeline | Starter $49/mo, Business $249/mo | docs, help centre |
| C | SurferSEO | Content Scoring + Research | Essential $89/mo, Scale $129/mo | docs, blog, updates |
| D | Semrush ContentShake | SEO Ecosystem Content Tool | Part of Semrush ($139+/mo) | docs, API docs |

_Full 5-dimension tables will be populated from research agent output._

---

## Dependencies

### External Dependencies (blockers we don't control)
| Dependency | Status | Impact if delayed |
|-----------|--------|-------------------|
| Google Search Console access (Hairgenetix) | Unknown | Gap analysis less accurate without GSC data |
| Keyword data source (free or paid API) | Researching | Core feature blocked without keyword volume data |
| SERP scraping API (SerpAPI / DataForSEO) | Available | ~$50/mo for DataForSEO at our scale |

### Cross-Feature Dependencies
```
F-001 (Keywords) ──→ F-002 (Clustering)
       │──→ F-003 (Intent)
       │──→ F-004 (SERP) ──→ F-005 (Competitors) ──→ F-006 (Gaps)
       └──→ F-007 (Calendar) ←──── F-006 (Gaps)
```

### Cross-Epic Dependencies
| This epic needs | From epic | Status |
|----------------|-----------|--------|
| Nothing — E-001 is the first pipeline stage | — | — |

| This epic provides | To epic | Interface |
|-------------------|---------|-----------|
| Content briefs + calendar | E-002 (Content Creation) | `ContentBrief` schema (to be defined in design) |
| Keyword data | E-003 (Optimisation) | `KeywordTarget` schema |
| SERP baseline | E-005 (Measurement) | `SERPBaseline` schema |

---

## Descoping Rules

**Time trigger:** If 60% of appetite (1.8 weeks) consumed with < 40% features complete → evaluate scope.

**Descope order:**
1. F-002 (Topic Clustering) — calendar works without clusters
2. F-005 (Competitor Content Analysis) — can use simpler URL-based gap detection
3. Never cut: F-001, F-004, F-006, F-007 (core pipeline)

---

## RAID Log

### Risks
| ID | Risk | Probability | Impact | Owner | Mitigation | Status |
|----|------|:-----------:|:------:|-------|------------|:------:|
| R1 | Free keyword data sources insufficient for accurate volume/difficulty | Medium | High | Claude | Research paid alternatives in Phase 2; DataForSEO as fallback ($50/mo) | Open |
| R2 | CLI-only modality for R1 limits usability | Low | Medium | Malcolm | Dashboard in E-006; CLI outputs human-readable Markdown | Accepted |
| R3 | Google Search Console not connected for Hairgenetix | Medium | Medium | Malcolm | Check GSC access; fallback to SERP-only gap analysis | Open |

### Assumptions
| ID | Assumption | Confidence | Validation |
|----|-----------|:----------:|------------|
| A1 | Free keyword data (autocomplete, PAA) is sufficient for R1 | Low | Phase 2 research |
| A2 | LLM semantic clustering is sufficient without vector DB | Medium | Phase 2 prototype |
| A3 | Existing Rube recipes are reusable as pipeline components | High | BA §3 confirms live |
| A4 | SERP scraping at < 50 queries/day is within API ToS | High | DataForSEO confirmed |

### Issues
None currently.

### Dependencies
| ID | Dependency | Type | Status | Blocks |
|----|-----------|------|:------:|--------|
| D1 | Keyword volume data source | External | Researching | F-001 accuracy |
| D2 | GSC access for Hairgenetix | External | Unknown | F-006 accuracy |
| D3 | ContentBrief schema (output contract) | Internal | Not started | E-002 input |

---

## Session Log

| Date | What Happened | Next Step |
|------|--------------|-----------|
| 2026-03-15 | E-001 epic-status.md created. Phase 1 (Understand) complete: problem framing, JTBD, assumption mapping, interaction modality decision, process flow, feature breakdown. Phase 2 competitive deep-dive launched (background). | Populate 5-dimension deep-dive from research results |
