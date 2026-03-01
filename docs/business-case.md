# SEO Toolkit — Business Case

Last updated: 2026-03-01

---

## Summary

The SEO Toolkit is an 8-agent AI platform that automates search engine optimisation for websites. It starts as an internal tool for Smith AI Agency projects (first client: Love Over Exile), then gets productised as a SaaS service for external clients.

**The core value proposition:** Most businesses know SEO matters but cannot afford the time, expertise, or tools to do it properly. The SEO Toolkit automates 80% of SEO work through specialised AI agents, at a fraction of the cost of hiring an SEO agency or buying multiple premium tools.

---

## Phase 1: Internal Tool (Now — Q2 2026)

### What It Does
Provides automated SEO for all Smith AI Agency websites — starting with Love Over Exile, later applied to SellFunnel, Book Rocket, and Marketing Engine.

### Cost Per Client

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| DataForSEO API calls | ~$30-50 | Pay-as-you-go. Keywords + SERPs + backlinks |
| SE Ranking | ~$52 | Essential plan (100 keywords tracked) |
| Google Search Console | Free | Google's own data |
| Rube MCP | Free | Free tier covers current usage |
| Claude Code (execution) | Included | Already running for other projects |
| **Total per client** | **~$50-100/month** | |

### Value Created
- Replaces manual SEO work that would take 10-20 hours/month per website
- Finds keyword opportunities that a human would miss
- Catches technical issues before they hurt rankings
- Generates content briefs and draft articles automatically
- Tracks competitor movements daily

---

## Phase 2: Productised SaaS (Q3 2026 — onwards)

### Revenue Model

| Tier | Monthly Price | What's Included | Target Customer |
|------|-------------|----------------|-----------------|
| Starter | $99/month | 3 agents (Audit, Keywords, Rank Tracker), 1 website, 50 tracked keywords | Freelancers, bloggers |
| Professional | $249/month | All 8 agents, 3 websites, 200 tracked keywords, weekly reports | Small businesses, consultants |
| Agency | $499/month | All 8 agents, 10 websites, 500 tracked keywords, daily reports, white-label | SEO agencies, marketing firms |

### Revenue Projections (Conservative)

| Milestone | Timeline | Customers | MRR | ARR |
|-----------|----------|-----------|-----|-----|
| First paying customer | Q3 2026 | 1 | $249 | $2,988 |
| 10 customers | Q4 2026 | 10 | $2,490 | $29,880 |
| 25 customers | Q1 2027 | 25 | $6,225 | $74,700 |
| 50 customers | Q2 2027 | 50 | $12,450 | $149,400 |

These projections assume an average revenue per customer of $249/month (Professional tier).

### Cost Structure at Scale

| Item | Cost at 50 customers | Notes |
|------|---------------------|-------|
| DataForSEO | ~$1,500/month | Usage scales with customer count |
| SE Ranking | ~$200/month | Higher-tier plan for more keywords |
| Cloud hosting | ~$50/month | Lightweight — agents run tasks, not serving traffic |
| Support/maintenance | ~$500/month | Malcolm's time |
| **Total** | **~$2,250/month** | |
| **Gross margin** | **~82%** | $12,450 revenue - $2,250 cost |

---

## Market Opportunity

The SEO tools market is valued at over $5 billion globally and growing at 15%+ annually. This is driven by:

- Every business with a website needs SEO
- SEO is complex and time-consuming — most businesses do it badly or not at all
- AI is transforming how SEO is done, but most tools still require manual work
- The rise of AI search engines (ChatGPT, Perplexity, Gemini) adds a new dimension that existing tools barely address

### The Gap We Fill

| What exists today | What we offer |
|-------------------|--------------|
| Dashboards that show data | Agents that take action |
| Manual keyword research | Automated keyword discovery + strategy |
| One-off site audits | Continuous monitoring + auto-fix suggestions |
| Content recommendations | AI-generated content briefs and drafts |
| Backlink reports | AI-researched link prospects + outreach pitches |
| Traditional SEO only | Traditional SEO + AI Discovery optimisation |

### Addressable Market

| Segment | Size | Our fit |
|---------|------|---------|
| Solo entrepreneurs / bloggers | Millions worldwide | Starter tier — affordable, automated |
| Small businesses (1-50 employees) | ~30M globally | Professional tier — replaces manual SEO |
| Digital marketing agencies | ~60,000 in US/EU | Agency tier — white-label for their clients |
| SaaS companies | Hundreds of thousands | Professional tier — content + technical SEO |

We do not need to capture a large share. 50 customers at an average of $249/month is $150K ARR — a meaningful business for a one-person agency.

---

## Competitive Advantages

1. **AI-native architecture** — Not AI bolted onto a dashboard. 8 specialised agents that work together autonomously.
2. **Low operational cost** — No team of developers to maintain. Claude Code builds and maintains the agents.
3. **Multi-client from day one** — Architecture supports any number of websites via config files.
4. **AI Discovery included** — No competitor has a dedicated agent for AI search engine optimisation (ChatGPT, Perplexity, Gemini discoverability).
5. **Battle-tested internally** — Every feature is proven on our own websites before being sold to customers.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| DataForSEO raises prices significantly | Low | Medium | Multiple data sources available (SEMrush via Rube, free tools as fallback) |
| Google changes SEO fundamentals drastically | Low | High | Agent architecture is adaptable — update individual agents without rewriting everything |
| Competitors add AI agents | Medium | Medium | First-mover advantage + vertical focus + lower price point |
| Agents produce poor quality outputs | Medium | High | Enterprise code quality standards, testing, human review gates |
| AI search engines reduce traditional SEO value | Medium | Medium | AI Discovery Agent specifically addresses this — we cover both worlds |

---

## Success Criteria

### Phase 1 (Internal Tool) — by Q2 2026
- [ ] All 8 agents operational
- [ ] Love Over Exile organic traffic growing month-over-month
- [ ] At least 10 keywords in top 20 positions
- [ ] Weekly automated reports running

### Phase 2 (Productised SaaS) — by Q4 2026
- [ ] First paying external customer
- [ ] 10 customers
- [ ] $2,000+ MRR
- [ ] Customer churn below 10%/month

---

## Decision

**Build it.** The toolkit pays for itself immediately as an internal tool (~$50/month in data costs replaces 10-20 hours/month of manual SEO work). The SaaS potential is a bonus — even modest adoption (50 customers) creates a $150K/year revenue stream with 80%+ margins.

---

## Change Log

| Date | Change |
|------|--------|
| 2026-03-01 | Business case created. Internal tool economics, SaaS pricing model, market analysis, risk assessment documented. |
