# SEO Toolkit — Architecture

Last updated: 2026-02-28

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SEO TOOLKIT                                  │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐             │
│  │  Audit   │ │ Keywords │ │ Content   │ │  Rank    │             │
│  │  Agent   │ │  Agent   │ │ Optimizer │ │ Tracker  │             │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘             │
│       │             │             │             │                    │
│  ┌────┴─────┐ ┌────┴─────┐ ┌─────┴─────┐ ┌────┴─────┐             │
│  │ Content  │ │  Link    │ │    AI     │ │ Reporter │             │
│  │  Writer  │ │ Builder  │ │ Discovery │ │          │             │
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
    │ DataForSEO  │                        │             │
    │ Google SC   │                        │ Love Over   │
    │ SE Ranking  │                        │ Exile       │
    │ Rube MCP    │                        │             │
    │ (SEMrush,   │                        │ (future     │
    │  Ahrefs)    │                        │  clients)   │
    └─────────────┘                        └─────────────┘
```

---

## Components

### Agents

| Agent | Status | Scripts Dir | Skill Installed |
|-------|--------|-------------|-----------------|
| Audit | 🔲 Not built | `scripts/audit/` | No |
| Keywords | 🔲 Not built | `scripts/keywords/` | No |
| Content Optimizer | 🔲 Not built | `scripts/content/` | No |
| Rank Tracker | 🔲 Not built | `scripts/keywords/` | No |
| Content Writer | 🔲 Not built | `scripts/content/` | No |
| Link Builder | 🔲 Not built | `scripts/links/` | No |
| AI Discovery | 🔲 Not built | `scripts/ai-discovery/` | No |
| Reporter | 🔲 Not built | `scripts/reporting/` | No |

### Data Sources & APIs

| Service | Purpose | Auth Method | Status | Cost |
|---------|---------|-------------|--------|------|
| DataForSEO | Keyword volumes, SERP data, backlinks, competitor analysis, technical audit | API login + password | 🔲 Account needed | Pay-as-you-go (~$50 deposit) |
| Google Search Console | Real search performance — clicks, impressions, positions, queries | OAuth via Rube MCP | 🔲 Property needed | Free |
| SE Ranking | Rank tracking, site audit, competitor research | API key or MCP | 🔲 Trial needed | $52/month (14-day free trial) |
| SEMrush | Keyword research, competitor analysis, backlink audit | Via Rube MCP | 🔲 Not connected | Via Rube |
| Ahrefs | Backlink analysis, content explorer, keyword difficulty | Via Rube MCP | 🔲 Not connected | Via Rube |
| Rube MCP | Universal connector for 500+ apps | Bearer token | ✅ Connected | Free tier |
| claude-seo | Technical site audits, E-E-A-T analysis, schema validation | GitHub install (local) | 🔲 Not installed | Free |

### Client Websites

| Website | Config File | Domain | Status |
|---------|-------------|--------|--------|
| Love Over Exile | `configs/loveoverexile.config.json` | loveoverexile.com | 🔲 Config created, not audited |

---

## Accounts & Access

| Platform | Account | Owner | Credentials |
|----------|---------|-------|-------------|
| Rube MCP | msmithnl@gmail.com | Malcolm | Bitwarden: "Rube MCP — API Key" |
| DataForSEO | — | — | Not yet created |
| SE Ranking | — | — | Not yet created |
| Google Search Console | — | — | Not yet connected |

---

## Change Log

| Date | Change | Details |
|------|--------|---------|
| 2026-02-28 | Project created | Initial structure — 8 agents defined, first client config (Love Over Exile), Rube MCP connected |
