# Roadmap — Autonomous Content Engine

> **What this is:** Follow-up roadmap for PROD-001 SEO Toolkit after E-001 Configuration & Setup.
> Tracks epic sequence, known limitations, and tech debt across the full content pipeline.

---

## E-001: Configuration & Setup — COMPLETE

| Field | Value |
|-------|-------|
| **Status** | Complete (v0.1.0 shipped) |
| **Shipped** | 2026-03-14 |
| **Features** | 6 (site registration, brand voice, CMS connection, topic config, quality thresholds, AISO preferences) |
| **Tasks** | 33/33 completed |
| **Tests** | 255 (253 unit/integration + 2 smoke) |
| **Framework compliance** | 97% |
| **Build duration** | ~30h actual (vs 90h estimated — spec quality 4.5/5.0 made implementation mechanical) |

### Key Outcomes

- All 6 services follow consistent pattern: Repository (Drizzle) → Service (DI, OperationContext, Result<T,E>) → Tests (in-memory SQLite)
- Staging verification against real sites caught a WordPress detector false-positive on Shopify password pages
- Phase Transition Review Protocol added to RE v4.17 based on lessons learned
- Full audit report: `research/e2e-devops-framework-audit-e001.md` (smith-ai-agency)

---

## E-002: Research & Content Intelligence

| Field | Value |
|-------|-------|
| **Priority** | HIGH (core capability — everything downstream depends on research quality) |
| **Appetite** | 4 weeks |
| **Dependencies** | E-001 (site registration provides target sites, brand voice informs research scope) |
| **Estimated scope** | 10 features, ~40 tasks |
| **Capabilities** | CAP-CE-002 (Keyword Intelligence), CAP-CE-003 (Content Gap Analysis), CAP-CE-004 (AISO Intelligence) |

### Features (from PDM)

| ID | Feature | Automation | Class | Competitive Position |
|----|---------|:----------:|:-----:|---------------------|
| 2.1 | Keyword research & discovery | AUTO | TS | 9/13 competitors have this — table stakes |
| 2.2 | Keyword clustering & topic mapping | AUTO | DF | Only 3/13 (Scalenut, MarketMuse, Frase) |
| 2.3 | Search intent classification | AUTO | DF | 4/13 competitors |
| 2.4 | Keyword cannibalisation detection | AUTO | DF | Only 2/13 (Clearscope, MarketMuse) |
| 2.5.1 | Competitor content audit | AUTO | TS | 8/13 competitors |
| 2.5.2 | Content gap identification | AUTO | TS | 7/13 competitors |
| 2.5.3 | SERP analysis & feature detection | AUTO | TS | 8/13 competitors |
| 2.6.1 | AI engine citation analysis | AUTO | IN | 0/13 — unique to us |
| 2.6.2 | Entity coverage gap analysis | AUTO | IN | 0/13 — unique to us |
| 2.6.3 | Schema opportunity detection | AUTO | IN | 0/13 — unique to us |

### Strategic Notes

- Features 2.6.x (AISO Intelligence) are the primary differentiator — no competitor does AI engine citation analysis, entity coverage gaps, or schema opportunity detection at this depth
- DataForSEO confirmed as keyword/SERP data provider ($0.0006/request) from technology landscape research
- Hybrid NLP stack (open-source + optional Surfer API) for content analysis
- Must handle keyword cannibalisation against existing site content (registered in E-001)

### Lessons from E-001 to Apply

1. Set up CI in Phase 1, not Phase 7
2. Apply 0.5x estimation multiplier (spec quality > 4.0 expected)
3. Use Phase Transition Reviews at every boundary (RE v4.17)
4. Work in seo-toolkit directory for build sessions (avoid cross-project hook friction)
5. Never use sed for structured file updates — use Python scripts

---

## E-003: Content Generation & Optimisation

| Field | Value |
|-------|-------|
| **Priority** | HIGH (revenue driver — this is what users pay for) |
| **Appetite** | 5 weeks |
| **Dependencies** | E-002 (research output informs content briefs, keyword targets, entity requirements) |
| **Estimated scope** | 12 features, ~50 tasks |
| **Capabilities** | CAP-CE-005 (AI Content Generation), CAP-CE-006 (Content Optimisation) |

### Features (from PDM)

| ID | Feature | Automation | Class | Competitive Position |
|----|---------|:----------:|:-----:|---------------------|
| 3.1 | Content brief generation | AUTO | TS | 7/13 competitors |
| 3.2 | Article outline generation | AUTO | TS | 10/13 competitors |
| 3.3 | Full article generation (1,500-5,000 words) | AUTO | TS | 11/13 competitors |
| 3.4 | AISO-native content structuring | AUTO | IN | 0/13 — our 36-factor model is unique |
| 3.5 | NLP term integration | AUTO | DF | 6/13 (Surfer, Frase, Scalenut, NeuronWriter, Clearscope, MarketMuse) |
| 3.6 | Image generation/sourcing | ASSISTED | DF | 4/13 competitors |
| 3.7.1 | SEO content scoring (0-100) | AUTO | TS | 7/13 competitors |
| 3.7.2 | AISO content scoring (36-factor) | AUTO | IN | 0/13 — unique to us |
| 3.7.3 | Dual SEO+AISO scoring | AUTO | IN | 0/13 (Frase has dual but not 36-factor depth) |
| 3.7.4 | Iterative improvement loop | AUTO | DF | 2/13 (Surfer content editor, Frase AI agent) |
| 3.7.5 | Readability scoring | AUTO | TS | 5/13 competitors |
| 3.7.6 | Fact-checking & citation validation | ASSISTED | DF | 1/13 (Writesonic) |

### Strategic Notes

- Claude Sonnet 4.6 as primary model ($0.12-0.18/article target cost)
- Multi-model AI routing (cross-cutting capability X.1) may be introduced here — choose best LLM per sub-task
- Success criteria: articles score >=7/10 on 36-factor AISO model AND >=80/100 on SEO content scoring
- Quality threshold from E-001 config feeds the iterative improvement loop (3.7.4) — articles re-generate until they meet configured thresholds (max 3 attempts, then flag for human review)
- Multi-language support (cross-cutting X.3) should be considered at generation time

---

## E-004: Publishing & Distribution

| Field | Value |
|-------|-------|
| **Priority** | MEDIUM (completes the autonomous pipeline but can be partially manual initially) |
| **Appetite** | 3 weeks |
| **Dependencies** | E-003 (generated content is the input to publishing) |
| **Estimated scope** | 6 features, ~25 tasks |
| **Capabilities** | CAP-CE-007 (CMS Publishing), CAP-CE-008 (Schema Markup Automation) |

### Features (from PDM)

| ID | Feature | Automation | Class | Competitive Position |
|----|---------|:----------:|:-----:|---------------------|
| 4.1 | WordPress publishing (REST API) | AUTO | TS | 10/13 competitors |
| 4.2 | Shopify blog publishing (Admin API) | AUTO | DF | Only 2/13 (Koala, Writesonic) |
| 4.3 | Schema markup injection (6+ types) | AUTO | IN | 0/13 (Koala does entity-only) |
| 4.4 | Internal link insertion | AUTO | DF | 2/13 (Koala, NeuronWriter) |
| 4.5 | Image upload & alt text | AUTO | TS | 6/13 competitors |
| 4.6 | Scheduled publishing | AUTO | DF | 2/13 (ArticleForge, Koala) |

### Strategic Notes

- CMS connections from E-001 provide API credentials and platform detection
- Schema markup injection (4.3) is a major differentiator — automated injection of Article, FAQPage, HowTo, Product, BreadcrumbList, and Organization schema
- Content versioning needed for audit trail and rollback
- Test sites: Hairgenetix + Skingenetix (Shopify), Digital Builders.nl (WordPress)

---

## E-005: Monitoring & Refresh (Future)

| Field | Value |
|-------|-------|
| **Priority** | LOW (could-have for V1, becomes must-have for retention) |
| **Appetite** | 3 weeks |
| **Dependencies** | E-004 (published content is what gets monitored) |
| **Estimated scope** | 6 features, ~25 tasks |
| **Capabilities** | CAP-CE-009 (Performance Monitoring), CAP-CE-010 (Content Lifecycle Management) |

### Features (from PDM)

| ID | Feature | Automation | Class | Competitive Position |
|----|---------|:----------:|:-----:|---------------------|
| 5.1 | Traditional rank tracking | AUTO | TS | 5/13 competitors |
| 5.2 | AI visibility tracking | AUTO | DF | 3/13 (Frase, Scalenut, Writesonic) |
| 5.3 | Content decay detection | AUTO | IN | 0/13 — unique to us |
| 5.4 | AI citation probability scoring | AUTO | IN | 0/13 — unique to us |
| 5.5.1 | Auto-refresh trigger (decay detected) | AUTO | IN | 0/13 — unique to us |
| 5.5.2 | Content update generation | AUTO | IN | 0/13 — unique to us |

### Strategic Notes

- This epic contains the most innovations (4 out of 6 features unique to us)
- Content decay detection + auto-refresh is a closed-loop system that no competitor offers
- AI citation probability scoring ties back to the 36-factor AISO model from E-003
- E-004 and E-005 have overlap potential — monitoring development can start while publishing is being refined

---

## Epic Sequence

```
E-001 (Config)     ──→  E-002 (Research)  ──→  E-003 (Generate)  ──→  E-004 (Publish)
  COMPLETE ✓              NEXT                    Blocked by E-002       └──→ E-005 (Monitor)
  v0.1.0                  4 weeks                 5 weeks                3w      3w
```

**Total remaining: ~15 weeks** (with spec quality multiplier, likely ~10 weeks actual)

---

## Known Limitations from E-001

Issues identified during E-001 that need addressing in future epics or as standalone work.

### 1. CMS Platform Support

- **Current:** WordPress and Shopify CMS detectors only
- **Needed:** Wix, Squarespace, custom/headless CMS detection
- **When:** E-004 (Publishing) is the natural place to expand CMS support
- **Impact:** Limits addressable market — Wix alone has 6M+ sites

### 2. Database — SQLite Only

- **Current:** SQLite for local development and CLI usage
- **Needed:** PostgreSQL for production multi-tenant deployment (PROD-004 SaaS Platform)
- **When:** Before SaaS Platform integration — likely a standalone migration task
- **Impact:** No RLS enforcement possible on SQLite; multi-tenant isolation is application-level only
- **Note:** Drizzle ORM abstraction makes the migration straightforward (schema stays the same, change the driver)

### 3. No Web UI

- **Current:** CLI-only interface
- **Needed:** Web dashboard for non-technical users
- **When:** PROD-004 SaaS Platform provides the UI layer — SEO Toolkit stays as the engine
- **Impact:** Limits to technical users until SaaS Platform is ready. By design — toolkit is the capability engine, not the product surface.

### 4. ESLint TypeScript Configuration

- **Current:** ESLint not configured for TypeScript files
- **Needed:** Full TypeScript-aware linting (strict rules, import ordering, no-unused-vars)
- **When:** Should be done before E-002 build starts (tech debt task)
- **Impact:** TypeScript compiler catches type errors, but stylistic and best-practice rules are not enforced

### 5. CI Quality Gate Layers

- **Current:** Only 2 of 9 quality gate layers in CI (typecheck + test)
- **Needed:** Full 9-layer pipeline (lint, typecheck, test, coverage threshold, conformance suites, migration lint, RLS check, fitness functions, security scan)
- **When:** Incrementally — add 2-3 layers before each epic
- **Impact:** Some quality checks only run locally; CI doesn't enforce them on PR

---

## Tech Debt from E-001

Prioritised backlog of technical debt to address before or during E-002.

| # | Item | Priority | When | Effort |
|---|------|----------|------|--------|
| TD-001 | Add ESLint TypeScript configuration | HIGH | Before E-002 | 2h |
| TD-002 | Add remaining CI quality gate layers (lint, coverage threshold, conformance) | HIGH | Phase 1 of E-002 | 4h |
| TD-003 | Set up Changesets for versioning | MEDIUM | Before E-002 | 2h |
| TD-004 | Add CLI deployment variant to RE Phase 7 guidance | LOW | Agency-level doc update | 1h |
| TD-005 | Add Technology Decision Cross-Reference to Gate 0 checklist | LOW | Agency-level doc update | 30m |

### Tech Debt Principles

- TD-001 and TD-002 are blockers for E-002 — CI must be solid before the next build phase
- TD-003 enables proper semantic versioning (v0.1.0 was manually tagged)
- TD-004 and TD-005 are agency-level framework improvements identified in the E-001 retrospective — they live in smith-ai-agency docs, not here

---

## Cross-Cutting Capabilities (Future)

These span multiple epics and will be addressed as the pipeline matures.

| ID | Capability | When | Notes |
|----|-----------|------|-------|
| X.1 | Multi-model AI routing | E-003 | Choose best LLM per sub-task (research vs generation vs scoring) |
| X.2 | API access for programmatic use | Post-E-004 | REST API for external consumers (feeds into PROD-004 SaaS) |
| X.3 | Multi-language support | E-003 | Generation in multiple languages (8/13 competitors have this) |
| X.4 | Bulk generation (batch mode) | E-003/E-004 | Generate and publish multiple articles in one run |
| X.5 | Brand voice profiles (per-client) | E-001 delivered | Basic brand voice training already in v0.1.0; expand in E-003 |
| X.6 | White-label/agency mode | Post-E-005 | Agency pricing tier for client management |

---

## Session Log

| Date | What Happened |
|------|--------------|
| 2026-03-14 | Roadmap created after E-001 completion and E2E framework audit. |
