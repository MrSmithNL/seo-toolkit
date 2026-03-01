# SEO Toolkit — Accounts & Access

Last updated: 2026-03-01

All credentials are stored in Bitwarden (`msmithnl@gmail.com`). Nothing is stored in git or plain text files.

---

## Active Accounts

| Service | Account | Purpose | Auth Method | Status | Bitwarden Entry |
|---------|---------|---------|-------------|--------|-----------------|
| GitHub | MrSmithNL/seo-toolkit | Source code repository | SSH key | Active | "GitHub — MrSmithNL" |
| Rube MCP | msmithnl@gmail.com | Universal API connector (500+ apps) — used for SEMrush, Ahrefs, Google tools | Bearer token | Active | "Rube MCP — API Key" |

---

## Pending Accounts (Not Yet Created)

| Service | Purpose | Auth Method | Action Needed | Estimated Cost |
|---------|---------|-------------|---------------|----------------|
| DataForSEO | Primary keyword/SERP data, backlink analysis, technical audit data | API login + password | Malcolm: create account at dataforseo.com, deposit $50 | $50 initial deposit, then pay-as-you-go |
| SE Ranking | Rank tracking, site audit, competitor research | API key | Malcolm: start 14-day free trial at seranking.com | Free trial, then $52/month |
| Google Search Console | Real search performance data — clicks, impressions, positions, queries for loveoverexile.com | OAuth (via Rube MCP or service account) | Malcolm: verify loveoverexile.com property in GSC | Free |

---

## How Credentials Are Managed

1. **API keys and passwords** go in `.env` in the project root (gitignored — never committed)
2. **Master copies** of all credentials are stored in Bitwarden
3. **OAuth tokens** (Google Search Console) are managed through Rube MCP — no raw tokens stored locally
4. **Naming convention in Bitwarden:** `[Service Name] — [Purpose/Label]` (e.g., "DataForSEO — API Credentials")

---

## Environment Variables Needed

These go in `.env` (see `.env.example` for template):

```bash
# DataForSEO
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password

# SE Ranking
SE_RANKING_API_KEY=your_api_key

# Google (if using service account instead of Rube MCP)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

---

## Service Details

### DataForSEO
- **Website:** https://dataforseo.com
- **What we use it for:** Keyword volumes, SERP data, backlink analysis, on-page audit data, competitor analysis
- **Pricing:** Pay-as-you-go. $50 minimum deposit. Typical cost per client: ~$30-50/month depending on keyword count
- **API docs:** https://docs.dataforseo.com
- **Auth:** HTTP Basic Auth (login + password in every request)
- **Status:** Account not yet created (SEO-001 in todo)

### SE Ranking
- **Website:** https://seranking.com
- **What we use it for:** Daily rank tracking, automated site audits, competitor position tracking
- **Pricing:** Essential plan $52/month (100 keywords). 14-day free trial available.
- **API docs:** https://seranking.com/api.html
- **Auth:** API key in request header
- **Status:** Account not yet created (SEO-003 in todo)

### Google Search Console
- **Website:** https://search.google.com/search-console
- **What we use it for:** Real Google search data — what queries people use, click-through rates, indexing status, Core Web Vitals
- **Pricing:** Free
- **Auth:** OAuth 2.0 — either through Rube MCP or a Google service account
- **Status:** Property needs to be verified for loveoverexile.com (SEO-002 in todo)

### Rube MCP
- **Website:** Connected via Composio/Rube
- **What we use it for:** Universal connector for 500+ apps. Provides access to SEMrush, Ahrefs, Google Sheets, and other tools without separate API accounts
- **Pricing:** Free tier (sufficient for current usage)
- **Auth:** Bearer token (stored in Bitwarden as "Rube MCP — API Key")
- **Status:** Active and connected

---

## Access Matrix

Who can access what:

| Person | GitHub | DataForSEO | SE Ranking | GSC | Rube MCP | Bitwarden |
|--------|--------|-----------|-----------|-----|----------|-----------|
| Malcolm | Owner | Owner (pending) | Owner (pending) | Owner (pending) | Owner | Owner |
| Claude Code | Read/Write via SSH | Read via .env | Read via .env | Read via Rube MCP | Read via bearer token | Read via `bw` CLI (when unlocked) |

---

## Change Log

| Date | Change |
|------|--------|
| 2026-02-28 | GitHub repo created. Rube MCP connected with bearer token. |
| 2026-03-01 | Accounts document created. DataForSEO, SE Ranking, GSC documented as pending. |
