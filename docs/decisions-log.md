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
