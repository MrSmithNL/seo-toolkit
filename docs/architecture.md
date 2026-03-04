# SEO Toolkit — Architecture

Last updated: 2026-03-04

---

## System Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                            SEO TOOLKIT (10 Agents)                        │
│                                                                           │
│  TIER 1 — LIVE (Rube Recipes)                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Technical │ │ Content  │ │ Keyword  │ │  SERP    │ │   AI     │       │
│  │  Audit   │ │Optimizer │ │ Research │ │ Analyzer │ │Discovery │       │
│  │  ✅ Live │ │  ✅ Live │ │  ✅ Live │ │  ✅ Live │ │  ✅ Live │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                                           │
│  TIER 2 — BUILD NEXT                                                     │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────────────────────────┐     │
│  │  Rank    │ │ Content  │ │ LINK BUILDER (Main Agent)             │     │
│  │ Tracker  │ │  Writer  │ │                                       │     │
│  │ 🔲 Next  │ │ 🔲 Next  │ │ ┌─────────────┐ ┌─────────────┐     │     │
│  └──────────┘ └──────────┘ │ │ Backlink    │ │ Prospect    │     │     │
│                             │ │ Profiler    │ │ Discovery   │     │     │
│  TIER 3 — STRATEGIC         │ └─────────────┘ └─────────────┘     │     │
│  ┌──────────┐ ┌──────────┐ │ ┌─────────────┐ ┌─────────────┐     │     │
│  │Competitor│ │ Reporter │ │ │ Linkable    │ │ Outreach    │     │     │
│  │ Monitor  │ │          │ │ │ Asset Maker │ │ Manager     │     │     │
│  │ 🔲 Later │ │ 🔲 Later │ │ └─────────────┘ └─────────────┘     │     │
│  └──────────┘ └──────────┘ │ ┌─────────────┐ ┌─────────────┐     │     │
│                             │ │ Competitor  │ │ Link Health │     │     │
│                             │ │ Link Spy    │ │ Monitor     │     │     │
│                             │ └─────────────┘ └─────────────┘     │     │
│                             │                          🔲 Next    │     │
│                             └───────────────────────────────────────┘     │
│                                                                           │
│  ─────────────────────────────────────────────────────────────────        │
│                         SHARED DATA LAYER                                 │
│          (configs, caches, keyword databases, backlinks, reports)         │
└──────────┬──────────────────────────────────────────────┬────────────────┘
           │                                              │
    ┌──────┴──────┐                                ┌──────┴──────┐
    │  DATA APIs  │                                │  CLIENT     │
    │             │                                │  WEBSITES   │
    │ Google SC ✅│                                │             │
    │ SerpAPI  ✅ │                                │ Love Over   │
    │ Composio ✅ │                                │ Exile ✅    │
    │ SEMrush  ⏳ │                                │             │
    │ DataForSEO 🔲│                               │ Hairgenetix │
    │ SE Ranking 🔲│                               │  ✅ New     │
    │ Ahrefs   🔲 │                                │             │
    └─────────────┘                                └─────────────┘
```

---

## Agent Registry (10 Agents)

### Tier 1 — Live (5 Rube Recipe Services)

| # | Agent | Recipe ID | Status | Tools Used |
|---|-------|-----------|--------|------------|
| 1 | Technical Audit | `rcp_fUfiRNt8Bh8b` | ✅ Live | GSC, WebFetch |
| 2 | Content Optimizer | `rcp_-msCRAZI2mln` | ✅ Live | WebFetch, invoke_llm |
| 3 | Keyword Research | `rcp_083WOBwKYeNo` | ✅ Live | GSC, SerpAPI, Composio Search, invoke_llm |
| 4 | SERP Analyzer | `rcp_tebS66AkhuYq` | ✅ Live | SerpAPI, invoke_llm |
| 5 | AI Discovery Audit **v2.0** | `rcp_3LBwPfkiTtRT` | ✅ Live (spec upgraded, recipe rebuild pending) | WebFetch, invoke_llm, Composio Search |

### Tier 2 — Build Next (3 Agents)

| # | Agent | Sub-Agents | Status | Depends On |
|---|-------|-----------|--------|------------|
| 6 | Rank Tracker | - | 🔲 Not built | SE Ranking ($52/month) |
| 7 | Content Writer | - | 🔲 Not built | Keyword Research data |
| 8 | **Link Builder** | **6 sub-agents** | 🔲 Not built | DataForSEO + Ahrefs |

**Link Builder Sub-Agents:**

| Sub-Agent | Purpose | Data Source |
|-----------|---------|------------|
| 8a. Backlink Profiler | Crawl full backlink profile, anchor text, toxic links | DataForSEO / Ahrefs |
| 8b. Prospect Discovery | Find + AI-score link opportunities | Web research, Ahrefs Content Explorer |
| 8c. Linkable Asset Creator | Generate statistics pages, tools, data assets | SERP analysis + invoke_llm |
| 8d. Outreach Manager | Draft pitches, manage follow-ups, CRM | invoke_llm + custom |
| 8e. Competitor Link Spy | Monitor competitor backlinks, link intersect | DataForSEO / Ahrefs |
| 8f. Link Health Monitor | Track new/lost/toxic links, anchor text ratios | DataForSEO / Ahrefs |

### Tier 3 — Strategic (2 Agents)

| # | Agent | Status | Depends On |
|---|-------|--------|------------|
| 9 | Competitor Monitor | 🔲 Not built | Keyword + SERP data |
| 10 | Reporter | 🔲 Not built | All other agents |

### Data Sources & APIs

| Service | Purpose | Auth Method | Status | Cost |
|---------|---------|-------------|--------|------|
| Google Search Console | Search performance — clicks, impressions, positions, queries | OAuth via Rube MCP | ✅ Connected (sc-domain:loveoverexile.com + sc-domain:hairgenetix.com) | Free |
| SerpAPI | SERP analysis, related searches, People Also Ask | OAuth via Rube MCP | ✅ Connected | Free (100 searches/month) |
| Composio Search | Web search, trends, news | Via Rube MCP | ✅ Connected | Free |
| SEMrush | Keyword difficulty scoring | Via Rube MCP | ⏳ Auth link sent — awaiting Malcolm | Free via Rube |
| DataForSEO | Keyword volumes, SERP data, backlinks, competitor analysis, technical audit | API login + password | 🔲 Account needed | Pay-as-you-go (~$50 deposit) |
| SE Ranking | Rank tracking, site audit, competitor research | API key or MCP | 🔲 Trial needed | $52/month (14-day free trial) |
| Ahrefs | Backlink analysis, content explorer, keyword difficulty | Via Rube MCP | 🔲 Not connected | Via Rube |
| Rube MCP | Universal connector for 500+ apps | Bearer token | ✅ Connected | Free tier |

### Client Websites

| Website | Config File | Domain | Type | Status | Last Audited |
|---------|-------------|--------|------|--------|--------------|
| Love Over Exile | `configs/loveoverexile.config.json` | loveoverexile.com | Content / Book | ✅ Audited | 2026-03-02 |
| Hairgenetix | `configs/hairgenetix.config.json` | hairgenetix.com | E-commerce / Shopify | 🆕 Testing | 2026-03-03 |

---

## Test Results (2026-03-02)

First run on loveoverexile.com:

| Recipe | Result |
|--------|--------|
| Technical Audit | 90/100 — 18 pages, 0 critical issues, 36 warnings (images, titles) |
| Content Optimizer | 74/100 avg — 15 of 17 pages need work (thin content, missing alt text) |
| Keyword Research | 7 clusters, 3 high-priority opportunities, all trending up |
| SERP Analyzer | Not ranking for any seed keywords yet (expected — site just launched) |
| AI Discovery (v1.0) | 100/100 — llms.txt, schema, robots.txt all perfect (v2.0 re-audit pending) |

---

## Accounts & Access

| Platform | Account | Owner | Credentials |
|----------|---------|-------|-------------|
| Rube MCP | msmithnl@gmail.com | Malcolm | Bitwarden: "Rube MCP — API Key" |
| Google Search Console | msmithnl@gmail.com | Malcolm | OAuth via Rube |
| SerpAPI | via Composio | Malcolm | OAuth via Rube |
| SEMrush | — | — | Auth link sent 2026-03-02 |
| DataForSEO | — | — | Not yet created |
| SE Ranking | — | — | Not yet created |

---

## Change Log

| Date | Change | Details |
|------|--------|---------|
| 2026-03-02 | 5 Rube recipe services built | Technical Audit, Content Optimizer, Keyword Research, SERP Analyzer, AI Discovery Audit — all tested on LOE |
| 2026-03-02 | GSC + SerpAPI connected | OAuth via Rube MCP. GSC has both hairgenetix.com and loveoverexile.com properties |
| 2026-03-02 | SEMrush auth initiated | Auth link sent, awaiting Malcolm to complete |
| 2026-03-03 | Architecture expanded to 10 agents | Link Builder promoted to main agent with 6 sub-agents. Added Competitor Monitor (#9) and Reporter (#10). Tiered build order defined. |
| 2026-03-03 | Hairgenetix added as second client | Config created, first e-commerce test case for all agents |
| 2026-03-04 | AI Discovery Agent v2.0 | Major upgrade: 34-factor Vida AEO framework, 6 weighted categories, external presence assessment, Share of Model measurement, platform-specific recommendations. Spec updated, recipe rebuild pending. |
| 2026-02-28 | Project created | Initial structure — 8 agents defined, first client config (Love Over Exile), Rube MCP connected |
