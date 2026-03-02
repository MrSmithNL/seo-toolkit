# SEO Toolkit — Architecture

Last updated: 2026-03-02

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SEO TOOLKIT                                  │
│                                                                     │
│                    ┌─────────────────────┐                          │
│                    │   RUBE RECIPE LAYER  │                          │
│                    │  (reusable services) │                          │
│                    └─────────┬───────────┘                          │
│                              │                                      │
│  ┌──────────┐ ┌──────────┐ ┌┴──────────┐ ┌──────────┐             │
│  │Technical │ │ Content  │ │ Keyword   │ │  SERP    │             │
│  │  Audit   │ │Optimizer │ │ Research  │ │ Analyzer │             │
│  │  ✅ Live │ │  ✅ Live │ │  ✅ Live  │ │  ✅ Live │             │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘             │
│       │             │             │             │                    │
│  ┌────┴─────┐ ┌────┴─────┐ ┌─────┴─────┐ ┌────┴─────┐             │
│  │   AI     │ │  Rank    │ │ Content   │ │  Link    │             │
│  │Discovery │ │ Tracker  │ │  Writer   │ │ Builder  │             │
│  │  ✅ Live │ │ 🔲 Later │ │ 🔲 Later  │ │ 🔲 Later │             │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘             │
│       │             │             │             │                    │
│  ─────┴─────────────┴─────────────┴─────────────┴──────             │
│                    SHARED DATA LAYER                                │
│            (configs, caches, keyword databases)                     │
└──────────┬──────────────────────────────────────┬───────────────────┘
           │                                      │
    ┌──────┴──────┐                        ┌──────┴──────┐
    │  DATA APIs  │                        │  CLIENT     │
    │             │                        │  WEBSITES   │
    │ Google SC ✅│                        │             │
    │ SerpAPI  ✅ │                        │ Love Over   │
    │ Composio ✅ │                        │ Exile ✅    │
    │ SEMrush  ⏳ │                        │             │
    │ DataForSEO 🔲│                       │ (future     │
    │ SE Ranking 🔲│                       │  clients)   │
    └─────────────┘                        └─────────────┘
```

---

## Components

### Rube Recipe Services (Live)

These are reusable SEO services built as Rube recipes. Each can be run on any domain, scheduled, or triggered on demand.

| Service | Recipe ID | Status | Tools Used |
|---------|-----------|--------|------------|
| SEO Technical Audit | `rcp_fUfiRNt8Bh8b` | ✅ Live | GSC, WebFetch |
| Content Optimizer | `rcp_-msCRAZI2mln` | ✅ Live | WebFetch, invoke_llm |
| Keyword Research | `rcp_083WOBwKYeNo` | ✅ Live | GSC, SerpAPI, Composio Search, invoke_llm |
| SERP Analyzer | `rcp_tebS66AkhuYq` | ✅ Live | SerpAPI, invoke_llm |
| AI Discovery Audit | `rcp_3LBwPfkiTtRT` | ✅ Live | WebFetch, invoke_llm |

### Agents (Planned — Phase 3+)

| Agent | Status | Depends On |
|-------|--------|------------|
| Rank Tracker | 🔲 Not built | SE Ranking ($52/month) |
| Content Writer | 🔲 Not built | Keyword Research data |
| Link Builder | 🔲 Not built | DataForSEO backlink data |
| Reporter | 🔲 Not built | Data from all other services |

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

| Website | Config File | Domain | Status | Last Audited |
|---------|-------------|--------|--------|--------------|
| Love Over Exile | `configs/loveoverexile.config.json` | loveoverexile.com | ✅ Audited | 2026-03-02 |

---

## Test Results (2026-03-02)

First run on loveoverexile.com:

| Recipe | Result |
|--------|--------|
| Technical Audit | 90/100 — 18 pages, 0 critical issues, 36 warnings (images, titles) |
| Content Optimizer | 74/100 avg — 15 of 17 pages need work (thin content, missing alt text) |
| Keyword Research | 7 clusters, 3 high-priority opportunities, all trending up |
| SERP Analyzer | Not ranking for any seed keywords yet (expected — site just launched) |
| AI Discovery | 100/100 — llms.txt, schema, robots.txt all perfect |

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
| 2026-02-28 | Project created | Initial structure — 8 agents defined, first client config (Love Over Exile), Rube MCP connected |
