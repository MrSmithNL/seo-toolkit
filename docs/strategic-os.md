# SEO Toolkit — Strategic Operating System

> Cascaded from the company-level Strategic OS (smith-ai-agency/docs/strategic-frameworks.md).
> Contains 4 frameworks adapted for this product. Updated quarterly.
> Last updated: 2026-03-05

---

## 1. Product Business Model Canvas

| Block | SEO Toolkit (PROD-001) |
|-------|----------------------|
| **Customer Segments** | Solo entrepreneurs and freelancers ($99 tier). Small businesses and consultants ($249 tier). SEO agencies and marketing firms ($499 tier). See [market-research.md](market-research.md) for segment profiles. |
| **Value Propositions** | 8 AI agents that act, not dashboards that report. Automates 80% of SEO work at 1/10th the cost of hiring an agency. AI-native from day one — not AI bolted onto legacy tools. |
| **Channels** | Agency website (planned), content marketing, case studies (LOE + Hairgenetix), direct outreach, word of mouth. |
| **Customer Relationships** | Self-serve SaaS (Starter/Professional). Managed onboarding + support (Agency tier). Weekly automated reports for all tiers. |
| **Revenue Streams** | 3-tier SaaS subscription: $99/$249/$499 per month. See [business-case.md](business-case.md) § Phase 2 for full model. |
| **Key Resources** | Claude Code (execution engine), DataForSEO (search data), SE Ranking (rank tracking), Google Search Console/GA4, modular agent library. |
| **Key Activities** | Agent development and maintenance, client SEO audits (automated weekly), content generation, rank monitoring, competitor tracking, report generation. |
| **Key Partnerships** | Anthropic (Claude API), DataForSEO (search intelligence), SE Ranking (rank tracking), Google (GSC/GA4 APIs). |
| **Cost Structure** | ~$50-100/month per client (Phase 1). ~$45/client at scale (Phase 2, 82% gross margin). See [business-case.md](business-case.md) for full breakdown. |

**Company BMC connection:** This product IS the SaaS subscription revenue stream in the company BMC. It embodies the "AI Operations" primary activity from the company Value Chain. Customer segments here are the company's primary market.

---

## 2. Product OKRs — Q2 2026 (April–June)

> Feeds into Company O1 (revenue) and O2 (credibility).
> See smith-ai-agency/docs/okrs/q2-2026.md for company-level OKRs.

**Objective: Make the SEO Toolkit ready for first paying customers**

| # | Key Result | Target | Current | Score |
|---|-----------|--------|---------|-------|
| KR1 | Core agents live (of 8 total) | 7 live | 5 live | — |
| KR2 | Love Over Exile showing measurable SEO improvement | +10 pts audit score | Baseline TBD | — |
| KR3 | Pricing page and onboarding flow defined | Complete | Not started | — |
| KR4 | Cost per client below target | <$75/month | ~$50-100 | — |

**Alignment:**
- KR1 → Company O1 KR1 (Launch SEO Toolkit as paid SaaS)
- KR1 → Production BU KR1 (7 of 8 core agents live)
- KR2 → Company O2 KR2 (All client SEO scores at 80+)
- KR3 → Revenue Ops BU KR4 (Define SaaS pricing model)
- KR4 → Company O1 KR4 (Complete cost inventory)

---

## 3. Product Balanced Scorecard

| Perspective | KPI | Current | Target | Source |
|------------|-----|---------|--------|--------|
| **Financial** | Monthly Recurring Revenue | €0 | €249 (1 customer by Q3) | — |
| **Financial** | Gross margin | ~82% (projected) | 80%+ | [business-case.md](business-case.md) |
| **Financial** | API cost per client | ~$50-100 | <$75 | DataForSEO + SE Ranking invoices |
| **Customer** | Client SEO audit score improvement | HG: +4 pts (83→87) | +10 pts per client | Audit Agent |
| **Customer** | Client AI Discovery improvement | HG: +5 pts (74→79) | 80+ all clients | AI Discovery Agent |
| **Customer** | External paying customers | 0 | 1 by Q3 2026 | — |
| **Internal Process** | Agents live / total | 5/8 | 7/8 by end Q2 | Agent registry |
| **Internal Process** | Time from audit to implementation | Not tracked | <4 hours | — |
| **Internal Process** | Automated report delivery | Not operational | Weekly for all clients | Reporter Agent |
| **Learning & Growth** | New agent capabilities shipped | 0 this quarter | 2 (Content Writer + Rank Tracker) | [roadmap.md](roadmap.md) |
| **Learning & Growth** | Research cycles applied to product | 0 | 2 | INFRA-005 |

**Company BSC connection:** Product MRR feeds the Financial perspective. Client SEO scores feed the Customer perspective. Agent reliability feeds Internal Process. New capabilities feed Learning & Growth. See smith-ai-agency/docs/strategic-frameworks.md § Balanced Scorecard.

---

## 4. Product SWOT

> Last reviewed: 2026-03-05 (baseline). Next review: June 2026 (Q2 scoring).

### Strengths (Internal)

- **AI-native architecture** — AI IS the product, not a bolt-on. Every agent built from scratch for AI execution.
- **AI Discovery agent** — unique capability. No competitor offers automated AI visibility auditing.
- **Multi-client architecture** — same agents serve multiple clients. Cost per client decreases with scale.
- **Battle-tested internally** — Hairgenetix Tech SEO 83→87, AI Discovery 74→79, schema 4/10→10/10 in one session.
- **82% gross margin model** — cost structure allows aggressive pricing while maintaining healthy margins.
- **Modular agent library** — each agent is standalone and reusable. Compounding advantage.

### Weaknesses (Internal)

- **Pre-revenue** — zero paying customers. All projections are untested.
- **CLI only** — no web UI, no onboarding flow. Requires Claude Code to operate.
- **3 agents not built** — Content Writer, Rank Tracker, and Reporter are still planned.
- **Single-person development** — all agent development depends on Malcolm + Claude Code sessions.
- **Dependency on DataForSEO + SE Ranking** — if either raises prices or degrades, we're exposed.
- **No automated testing** — agent quality relies on manual review.

### Opportunities (External)

- **$5.2B SEO tools market** growing at 15%+ annually. Massive addressable market.
- **AI search creating new optimisation need** — AI Overviews, ChatGPT search, Perplexity are new channels that require new approaches. We're ahead.
- **Agencies drowning in manual work** — even large agencies still do SEO manually. Automation demand is real.
- **Outcome-based pricing shift** — 40% of enterprise SaaS spend moving to usage/outcome pricing. We can price on results.
- **Solo founder explosion** — 36.3% of startups now solo-founded (vs 23.7% in 2019). They need exactly what we build.

### Threats (External)

- **Ahrefs and SEMrush adding AI features** — if they get it right, they have existing distribution and trust.
- **Race to bottom on pricing** — AI lowers barriers, more tools compete on price.
- **Google algorithm changes** — any major update can invalidate current optimisation strategies.
- **DataForSEO pricing risk** — costs could increase as they scale.
- **LLM model risk** — Anthropic pricing changes, quality degradation, or competitors overtaking Claude.

**Company SWOT connection:** The product's AI-native strength is the company's core strength applied to a specific market. Pre-revenue weakness mirrors the company-level weakness. AI Discovery opportunity is unique to this product and feeds the company's "AI visibility gap" opportunity. See smith-ai-agency/docs/swot-analysis.md.
