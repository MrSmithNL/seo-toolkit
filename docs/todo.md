# SEO Toolkit — Todo

Last updated: 2026-03-02

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

## Phase 3 — Tracking & Growth

Ongoing monitoring and content generation. These need paid services or more data.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| SEO-020 | Build Rank Tracker Agent | 🔲 Todo | Needs SE Ranking ($52/month) for daily tracking |
| SEO-021 | Build Content Writer Agent | 🔲 Todo | Automated article pipeline using keyword research data |
| SEO-022 | Build Link Builder Agent | 🔲 Todo | Needs DataForSEO for backlink data |
| SEO-023 | Build Reporter Agent | 🔲 Todo | Weekly/monthly dashboards combining all service data |
| SEO-024 | Schedule recurring audits | 🔲 Todo | Set up weekly/monthly Rube recipe schedules |
| SEO-025 | Apply audit recommendations to LOE | 🔲 Todo | Fix titles, meta descriptions, alt text, thin content |

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

---

## Session Log

| Date | What happened |
|------|--------------|
| 2026-02-28 | Project created. 8 agents defined. Love Over Exile as first client. Rube MCP connected with bearer token. |
| 2026-03-02 | 5 Rube recipe services built and tested on LOE. GSC + SerpAPI connected. SEMrush auth link sent. Architecture and todo updated. |
