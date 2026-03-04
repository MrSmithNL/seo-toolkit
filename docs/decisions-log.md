# SEO Toolkit — Decisions Log

---

## DEC-001 — Separate project, not embedded in website repos

**Date:** 2026-02-28
**Decision:** Build SEO toolkit as a standalone project, not inside the Love Over Exile website repo.
**Why:** Malcolm plans to build more websites. A standalone toolkit can be pointed at any domain via config files. Upgrades apply to all clients. Could eventually be published as a product/service.
**Trade-off:** Slightly more complex initial setup vs. long-term reusability.

## DEC-002 — 8-agent architecture

**Date:** 2026-02-28
**Decision:** Split SEO functionality into 8 specialised agents rather than one monolithic tool.
**Why:** Each agent has a clear purpose, its own data sources, and its own schedule. Easier to build incrementally, test independently, and maintain over time. Agents can share data via the shared data layer.
**Agents:** Audit, Keywords, Content Optimizer, Rank Tracker, Content Writer, Link Builder, AI Discovery, Reporter.

## DEC-003 — DataForSEO as primary data source

**Date:** 2026-02-28
**Decision:** Use DataForSEO API as the primary keyword and SERP data provider.
**Why:** Pay-as-you-go pricing (no subscription lock-in), comprehensive API coverage (keywords, SERPs, backlinks, on-page), good for programmatic access. SEMrush/Ahrefs available via Rube MCP as supplements.
**Cost:** ~$50 initial deposit, then usage-based.

## DEC-004 — Client config model

**Date:** 2026-02-28
**Decision:** Each website gets a JSON config file in `configs/` rather than hardcoding domains.
**Why:** Makes the toolkit multi-tenant from day one. Adding a new website = adding a new config file. No code changes needed.

## DEC-005 — AI Discovery as a dedicated agent

**Date:** 2026-02-28
**Decision:** Give AI engine optimisation its own agent rather than bundling it into the Audit agent.
**Why:** AI discoverability (llms.txt, AI-friendly content structure, citation tracking) is a distinct and fast-evolving discipline. It deserves focused attention and will grow in importance over 2026–2027.

## DEC-006 — Link Builder = "Earned Link Engine", not a posting bot

**Date:** 2026-03-01
**Decision:** The Link Builder Agent must be designed as an "earned link engine" — helping users earn editorial links through PR, pitching, and linkable assets. It must NOT automate publishing to external sites or run mass outreach campaigns.
**Why:** Google explicitly penalises large-scale guest-posting campaigns done primarily to build links. Automated placement at scale creates detectable footprints. The commercially viable and safe approach is: discover high-quality prospects, generate genuinely valuable linkable assets (data, tools, stats pages), draft personalised pitches with human approval, and monitor for risk/compliance.
**Key principles:**
- Never auto-publish to external sites
- Never buy links or use PBNs
- AI assists with prospect scoring, asset creation, pitch drafting, and risk detection
- Human approves all outreach
- Proper rel attributes (sponsored, ugc, nofollow) always used
- Build in 3 MVPs: (1) Prospecting + Fit Scoring → (2) Asset-First Pitching → (3) Risk & Compliance
**Trade-off:** Slower link acquisition vs. sustainable, penalty-proof growth that can be sold as a legitimate service.

## DEC-007 — AI Discovery Agent v2.0: Vida AEO 34-Factor Framework

**Date:** 2026-03-04
**Decision:** Upgrade the AI Discovery Agent from a basic 10-item checklist to a comprehensive 34-factor audit based on the Vida AEO framework, Princeton GEO research, and 40+ industry sources.
**Why:** The original agent checked surface-level items (llms.txt exists, schema present, robots.txt allows crawlers) and scored 100/100 for Love Over Exile — but a detailed external audit by ChatGPT revealed significant gaps in content structure, external presence, and conversational readiness. The 10-item checklist was too shallow to catch real AI visibility problems. The new 34-factor model covers the full spectrum: content extractability (30%), schema (20%), authority (20%), technical (15%), freshness (10%), and conversational readiness (5%).
**Key additions in v2.0:**
- Content Structure & Extractability analysis (answer-first format, fact density, atomic paragraphs, semantic completeness)
- External Presence Assessment (Reddit, YouTube, Trustpilot, Wikipedia, Knowledge Graph)
- Share of Model (SoM) measurement across multiple AI platforms
- Platform-specific recommendations (ChatGPT, Perplexity, Google AI Overviews, Claude, Copilot)
- Prioritised action plans (immediate → short-term → medium-term → long-term)
- Competitor comparison and trend tracking
**Research basis:** Full research document at `smith-ai-agency/research/ai-visibility-optimization-research.md`
**Trade-off:** More complex audit that takes longer to run vs. genuinely actionable insights that move the needle on AI visibility.
