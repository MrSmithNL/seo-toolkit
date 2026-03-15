# Product Roadmap — PROD-001: SEO Toolkit

> **Format:** Now / Next / Later (Delivery Manager SOP O11)
> **Reviewed:** Every sprint planning + every RE gate approval
> **Last updated:** 2026-03-15
> **Sprint:** S001 (2026-03-10 to 2026-03-21)

---

## Feature Hierarchy

> Traces product items: OKR → Theme → Epic → Feature → Sprint Task

| OKR | Theme | Epic | Features | Sprint |
|-----|-------|------|----------|--------|
| KR1.1: Launch AISOGEN MVP | 001 — Autonomous Content Engine | E-001 Research & Strategy | F-001 Keyword Research, F-002 Topic Clustering, F-003 Intent Classification, F-004 SERP Analysis, F-005 Competitor Analysis, F-006 Content Gap ID, F-007 Content Calendar | S002+ (Gate 3 pending) |
| KR1.1: Launch AISOGEN MVP | 001 — Autonomous Content Engine | E-002 Content Creation | (not yet specced) | — |
| KR1.1: Launch AISOGEN MVP | 001 — Autonomous Content Engine | E-003 Content Optimisation | (not yet specced) | — |
| (operational) | — | — | SEO audit recommendations | S001 (active) |
| (operational) | — | — | Content pipeline analysis | S001 (active) |

---

## Now — In Sprint / Gate 3 Approved

> Only items with Gate 3 approved OR operational tasks in active sprint.

| # | Item | Category | ARID | Spec | Gate | Sprint | Status |
|---|------|----------|:----:|:----:|:----:|:------:|--------|
| 1 | Re-run Technical Audit on hairgenetix.com | operational | — | N/A | N/A | S001 | Done |
| 2 | Compile LOE audit findings into prioritised fix list | operational | — | N/A | N/A | S001 | Done |
| 3 | Compile HG audit findings into prioritised fix list | operational | — | N/A | N/A | S001 | Done |
| 4 | Analyse LOE keyword research for top 5 content gaps | operational | — | N/A | N/A | S001 | Done |
| 5 | Analyse HG keyword research for top 5 content gaps | operational | — | N/A | N/A | S001 | Done |
| 6 | Create reusable content brief template | operational | — | N/A | N/A | S001 | In progress |

---

## Next — Gates 1-2 Complete / RE In Progress

> Items with active specs, working through RE phases. Move to Now when Gate 3 passes.

| # | Item | Category | ARID | Spec | Gate Status | Target Sprint | Notes |
|---|------|----------|:----:|:----:|:-----------:|:------------:|-------|
| 7 | E-001 Research & Strategy (7 features) | product | 11.2 | Phase 5 complete | Gate 1 ✅, Gate 2 ✅, Gate 3 ✅ | S002 | Gate 3 approved 2026-03-15. **Build (Phase 6) in progress.** Python in seo-toolkit (DEC-008). |
| 8 | Purchase Keywords Everywhere API ($10) | product | 9.0 | N/A | N/A — purchase | S002 | Malcolm approved 2026-03-15. Needed before F-001 build. |
| 9 | DataForSEO API setup ($50 deposit) | product | 6.0 | N/A | N/A — purchase | S003+ | Deferred to month 3 per cost analysis. |

---

## Later — Strategic Direction / Not Yet Specced

> Backlog items. ARID scored for preliminary ranking (Spec Readiness = 1).

| # | Item | Category | ARID | Source | Priority | Depends On |
|---|------|----------|:----:|--------|:--------:|------------|
| 10 | E-002 Content Creation epic | product | 5.6 | Theme 001 | High | E-001 complete (ContentBrief schema) |
| 11 | E-003 Content Optimisation epic | product | 4.8 | Theme 001 | High | E-002 |
| 12 | E-004 Publishing & Distribution | product | 3.2 | Theme 001 | Medium | E-003 |
| 13 | E-005 Performance Tracking | product | 3.0 | Theme 001 | Medium | E-001 (baseline data) |
| 14 | Build Rank Tracker Agent | product | 4.0 | Competitor rec T-006 | High | SE Ranking ($52/mo) |
| 15 | Build Link Builder Agent (earned links) | product | 3.5 | Competitor rec T-003 | High | DataForSEO |
| 16 | Build Reporter Agent | product | 2.8 | Dashboard + metrics | Medium | Multiple agents operational |
| 17 | Multi-site dashboard | product | 2.5 | Competitor rec T-004 | Medium | Platform (PROD-004) |
| 18 | Define pricing tiers | strategy | 3.0 | Competitor rec S-002 | Medium | MVP features defined |
| 19 | "Set it and forget it" messaging | marketing | 2.0 | Competitor rec M-001 | Medium | Product launched |
| 20 | Love Over Exile case study | marketing | 2.5 | Competitor rec M-003 | Medium | Results to show |
| 21 | Free audit report lead magnet | marketing | 2.0 | Marketing strategy | Medium | Audit Agent operational |
| 22 | Comparison landing pages (vs Ahrefs, vs SEMrush) | marketing | 1.5 | Marketing strategy | Low | Product launched |
| 23 | White-label reports for agencies | product | 1.0 | Feature request | Low | Reporter Agent |
| 24 | Schema markup generator | product | 2.0 | Content Optimizer dep | Medium | Content Optimizer |
| 25 | Productise as standalone SaaS (Phase 2) | strategy | 1.0 | Long-term | Low | Proven on clients |
| 26 | **Migrate E-001 to saas-platform TypeScript module** | engineering | 8.0 | DEC-008 | **High** | SaaS Platform Phase 2+ operational. See DEC-008. |

---

## Discovered Scope

> Items surfaced during development (PRs, audits, RE phases). Triaged weekly — ARID-scored and promoted to Now/Next/Later or declined.

| # | Item | Source | Date Discovered | ARID | Disposition |
|---|------|--------|:---------------:|:----:|-------------|
| D1 | Keywords Everywhere API integration | E-001 keyword data analysis | 2026-03-15 | 9.0 | Promoted to Next (#8) |
| D2 | Multilingual gap analysis (9 languages) | F-006 requirements | 2026-03-15 | — | Included in F-006 scope |
| D3 | ContentBrief TypeScript interface contract | F-007 requirements | 2026-03-15 | — | Included in contracts/domain-model.md |

---

## Blockers

| Blocker | Impact | Owner | Status |
|---------|--------|-------|--------|
| Keywords Everywhere API key ($10) | Blocks F-001 volume enrichment | Malcolm | Approved — needs purchase |
| DataForSEO account ($50 deposit) | Blocks F-004 SERP data, F-005 competitor data | Malcolm | Deferred to month 3 |
| Google Search Console verification (hairgenetix) | Blocks HG-specific GSC data | Malcolm | Needs DNS cutover |

---

## ARID Scoring Reference

> ARID = (Business Value × Time Criticality × Spec Readiness) / (Review Effort × Blast Radius)
> Scale: each factor 1-5. Higher = do sooner. Scores are relative within this roadmap.

---

## Change Log

| Date | What Changed |
|------|-------------|
| 2026-03-15 | Gate 2 approved — E-001 completeness review passed. Roadmap synced. Phase 4 (Design) begins. |
| 2026-03-15 | Gate 2 sync — E-001 ARID updated 8.4→11.2 (Spec Readiness 3→4). S001 operational tasks updated to Done. 237 EARS criteria + 270 test scenarios documented. |
| 2026-03-01 | v1.0 — Initial roadmap from competitor recommendations. 23 items across 3 time horizons. |
| 2026-03-15 | v2.0 — Converted to Now/Next/Later format (DM SOP O11). Added Feature Hierarchy tracing, ARID scores, Discovered Scope section. Integrated E-001 RE progress (7 features at Phase 3). Added blockers from keyword data analysis. |
| 2026-03-15 | Gate 3 approved — E-001 build started (Python, DEC-008). Migration item #26 added to Later. |
