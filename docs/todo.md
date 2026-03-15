# SEO Toolkit — Todo

Last updated: 2026-03-15

---

## Phase 1 — Foundation (complete)

Get the data pipes connected so agents have real numbers to work with.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| SEO-001 | Create DataForSEO account + deposit $50 | 🔲 Todo | Malcolm action — dataforseo.com |
| SEO-002 | Connect Google Search Console via Rube | ✅ Done | Both sc-domain:loveoverexile.com and sc-domain:hairgenetix.com available |
| SEO-003 | Start SE Ranking 14-day free trial | 🔲 Todo | Malcolm action — seranking.com |
| SEO-004 | Install claude-seo from GitHub | 🔲 Todo | Free technical audit tool (lower priority now that Rube recipes exist) |
| SEO-005 | Run first full audit on loveoverexile.com | ✅ Done | Score: 90/100 — 18 pages, 0 critical, 36 warnings |
| SEO-006 | Run first keyword research with real data | ✅ Done | 7 clusters, 3 high-priority opportunities, SerpAPI + GSC |
| SEO-007 | Connect SEMrush via Rube | ⏳ Pending | Auth link sent to Malcolm 2026-03-02 |
| SEO-008 | Connect SerpAPI via Rube | ✅ Done | 100 free searches/month |

## Phase 2 — Core Services (complete)

Built as reusable Rube recipes that work on any domain.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| SEO-010 | Build Technical Audit service | ✅ Done | Recipe `rcp_fUfiRNt8Bh8b` — sitemap discovery, page crawl, GSC, scoring |
| SEO-011 | Build Keyword Research service | ✅ Done | Recipe `rcp_083WOBwKYeNo` — GSC + SerpAPI + trends + AI clustering |
| SEO-012 | Build Content Optimizer service | ✅ Done | Recipe `rcp_-msCRAZI2mln` — 6-dimension scoring + AI suggestions |
| SEO-013 | Build AI Discovery Audit service | ✅ Done | Recipe `rcp_3LBwPfkiTtRT` — llms.txt, schema, robots.txt, AI readiness |
| SEO-014 | Build SERP Analyzer service | ✅ Done | Recipe `rcp_tebS66AkhuYq` — top 10 analysis, PAA, related searches, AI strategy |

## Phase 2b — Multi-Client Validation (complete)

All 5 agents tested on a second client (Hairgenetix) to confirm they work on any domain.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| SEO-015 | Test all 5 agents on hairgenetix.com | ✅ Done | Tech 83/100, Keywords 104, SERP #2 mesotherapy, AI 74/100, Content 64/100 |

## Spec-Driven Development — Autonomous Content Engine (Theme 001)

Active RE process for the Autonomous Content Engine. Syncs with product roadmap (Now/Next/Later).

| ID | Task | Status | Notes |
|----|------|--------|-------|
| RE-001 | Theme 001 — Process map, FBS, epic breakdown | ✅ Done | Gate 0 approved (architecture classification) |
| RE-002 | E-001 — Research & Strategy: Phase 1 (Understand) | ✅ Done | Problem framing, JTBD, assumption mapping |
| RE-003 | E-001 — Phase 2 (Research): Competitive deep-dive | ✅ Done | 5-dimension analysis, 4 competitors, keyword data sources |
| RE-004 | E-001 — Gate 1 (Scope Validation) | ✅ Done | Malcolm approved 2026-03-15 |
| RE-005 | E-001 — Phase 3 (Requirements): All 7 features | ✅ Done | 2,659 lines across F-001 to F-007. EARS acceptance criteria. |
| RE-006 | E-001 — Gate 2 (Completeness Review) | 🔲 Todo | Next step — present to Malcolm |
| RE-007 | E-001 — Phase 4 (Design) | 🔲 Todo | Architecture, data model, API contracts |
| RE-008 | E-001 — Gate 3 (Build Approval) | 🔲 Todo | After Phase 5 (Tasks) |
| RE-009 | Purchase Keywords Everywhere API key ($10) | 🔲 Todo | Malcolm approved spend 2026-03-15 |
| RE-010 | E-002 to E-005 — spec remaining epics | 🔲 Todo | After E-001 reaches Gate 3 |

## Phase 3 — Tracking & Growth

Ongoing monitoring and content generation. These need paid services or more data.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| SEO-020 | Build Rank Tracker Agent | 🔲 Todo | Needs SE Ranking ($52/month) for daily tracking |
| SEO-021 | Build Content Writer Agent | ⏳ In Progress | Content pipeline objective active. LOE gaps complete (2026-03-14), HG gaps complete (2026-03-15): 10 gaps total. Next: content brief template (T-003), LOE briefs (T-004), HG briefs (T-005). |
| SEO-022 | Build Link Builder Agent | 🔲 Todo | Needs DataForSEO for backlink data |
| SEO-023 | Build Reporter Agent | 🔲 Todo | Weekly/monthly dashboards combining all service data |
| SEO-024 | Schedule recurring audits | 🔲 Todo | Set up weekly/monthly Rube recipe schedules |
| SEO-025 | Apply audit recommendations to LOE | ⏳ In Progress | Re-audited 2026-03-09: 90/100 tech, 63/100 content (40 pages). T-001 + T-002 + T-004 done. Fix list compiled (53 issues, 5 phases). Next: T-006/T-007/T-008 (meta, alt, heading fixes — human_level 2) |
| SEO-026 | Apply audit recommendations to Hairgenetix | ⏳ In Progress | Re-audited 2026-03-11: 72/100 tech (down from 83). Fix list compiled (280 issues, 5 phases). Root cause: Cloudflare bot protection blocks 32 pages. T-003 + T-005 done. Next: T-009 (llms.txt draft), T-010 (meta fixes) — both human_level 2 |
| SEO-027 | Rebuild AI Discovery Rube recipe for v2.0 | 🔲 Todo | Implement 34-factor audit in recipe `rcp_3LBwPfkiTtRT` — content scoring, external presence, SoM |
| SEO-028 | Re-audit Love Over Exile with AI Discovery v2.0 | 🔲 Todo | Re-score with new 34-factor model (was 100/100 on v1.0 — expect lower on v2.0) |
| SEO-029 | Re-audit Hairgenetix with AI Discovery v2.0 | 🔲 Todo | Re-score with new 34-factor model (was 74/100 on v1.0) |

## Phase 4 — Productise

Make it publishable and usable by others.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| SEO-030 | Package as installable skill set | 🔲 Todo | Global Claude Code skills |
| SEO-031 | Write user documentation | 🔲 Todo | Setup guide for new websites |
| SEO-032 | Create onboarding script | 🔲 Todo | Auto-generates config for new client site |

---

## Completed

| ID | Task | Date | Notes |
|----|------|------|-------|
| — | Project created | 2026-02-28 | Structure, CLAUDE.md, configs, agent specs |
| SEO-002 | GSC connected via Rube | 2026-03-02 | OAuth — both LOE and hairgenetix properties |
| SEO-008 | SerpAPI connected via Rube | 2026-03-02 | 100 free searches/month |
| SEO-010 | Technical Audit recipe | 2026-03-02 | `rcp_fUfiRNt8Bh8b` — tested on LOE: 90/100 |
| SEO-011 | Keyword Research recipe | 2026-03-02 | `rcp_083WOBwKYeNo` — tested on LOE: 7 clusters |
| SEO-012 | Content Optimizer recipe | 2026-03-02 | `rcp_-msCRAZI2mln` — tested on LOE: 74/100 avg |
| SEO-013 | AI Discovery Audit recipe | 2026-03-02 | `rcp_3LBwPfkiTtRT` — tested on LOE: 100/100 |
| SEO-014 | SERP Analyzer recipe | 2026-03-02 | `rcp_tebS66AkhuYq` — tested on LOE: 3 keywords |
| SEO-005 | First full audit on LOE | 2026-03-02 | 90/100 — 0 critical, 36 warnings |
| SEO-006 | First keyword research | 2026-03-02 | 7 clusters, 3 high-priority, all trending up |
| SEO-015 | All 5 agents tested on hairgenetix.com | 2026-03-03 | Tech 83/100, 104 keywords, SERP #2 mesotherapy, AI 74/100, Content 64/100 avg |
| — | AI Discovery Agent upgraded to v2.0 | 2026-03-04 | 34-factor audit based on Vida AEO framework. 6 weighted categories. External presence + SoM measurement. |

---

## Session Log

| Date | What happened |
|------|--------------|
| 2026-02-28 | Project created. 8 agents defined. Love Over Exile as first client. Rube MCP connected with bearer token. |
| 2026-03-02 | 5 Rube recipe services built and tested on LOE. GSC + SerpAPI connected. SEMrush auth link sent. Architecture and todo updated. |
| 2026-03-03 | All 5 agents tested on hairgenetix.com — multi-client validation complete. All services confirmed working on any domain. |
| 2026-03-04 | AI Discovery Agent upgraded to v2.0 — 34-factor audit framework based on Vida AEO, Princeton GEO, and 40+ industry sources. New capabilities: content extractability scoring, external presence assessment, Share of Model measurement, platform-specific recommendations. |
