# Capability Map — Autonomous Content Engine

> **Standalone capability map** extracted from `theme.md` per RE v4.15 requirement.
> This is the single source of truth for capability mapping. Updates here MUST be reflected back into `theme.md`.

---

## Business Capabilities

| ID | Capability | Tier | Current Maturity | Target Maturity | Gap | Epic | Key L3 Sub-Processes |
|----|-----------|------|:----------------:|:--------------:|:---:|------|---------------------|
| CAP-CE-001 | Site & Pipeline Configuration | Supporting | 0 | 3 | Major | E-001 | 1.1-1.6 (site setup, brand voice, CMS connect, topic config, quality thresholds, AISO prefs) |
| CAP-CE-002 | Keyword Intelligence | Core | 0 | 4 | Major | E-002 | 2.1-2.4 (keyword research, clustering, intent classification, cannibalisation) |
| CAP-CE-003 | Content Gap Analysis | Core | 0 | 3 | Major | E-002 | 2.5.1-2.5.3 (competitor audit, gap ID, SERP analysis) |
| CAP-CE-004 | AISO Intelligence | Strategic | 0 | 4 | Major | E-002 | 2.6.1-2.6.3 (AI citation analysis, entity coverage, schema opportunities) |
| CAP-CE-005 | AI Content Generation | Core | 0 | 4 | Major | E-003 | 3.1-3.6 (brief, outline, article, AISO-native, NLP, images) |
| CAP-CE-006 | Content Optimisation (SEO+AISO) | Strategic | 0 | 5 | Major | E-003 | 3.7.1-3.7.6 (SEO score, AISO score, dual score, iteration, readability, fact-check) |
| CAP-CE-007 | CMS Publishing | Core | 0 | 3 | Major | E-004 | 4.1-4.6 (WordPress, Shopify, schema, internal links, images, scheduling) |
| CAP-CE-008 | Schema Markup Automation | Strategic | 0 | 4 | Major | E-004 | 4.3 (6+ schema types injected at publish time) |
| CAP-CE-009 | Performance Monitoring | Core | 0 | 3 | Major | E-005 | 5.1-5.4 (rank tracking, AI visibility, decay detection, citation probability) |
| CAP-CE-010 | Content Lifecycle Management | Strategic | 0 | 3 | Major | E-005 | 5.5.1-5.5.2 (auto-refresh trigger, update generation) |

## Maturity Scale

| Level | Description |
|:-----:|-------------|
| 0 | Not started — no implementation |
| 1 | Initial — manual/ad-hoc process exists |
| 2 | Managed — basic automation with human oversight |
| 3 | Defined — fully automated with monitoring |
| 4 | Quantitatively managed — metrics-driven with continuous optimisation |
| 5 | Optimising — self-improving with feedback loops |

## Capability Tier Definitions

| Tier | Description | Capabilities |
|------|-------------|-------------|
| **Strategic** | Competitive advantage — unique to us, hard to replicate | CAP-CE-004, CAP-CE-006, CAP-CE-008, CAP-CE-010 |
| **Core** | Essential for the product — must be excellent | CAP-CE-002, CAP-CE-003, CAP-CE-005, CAP-CE-007, CAP-CE-009 |
| **Supporting** | Necessary but not differentiating | CAP-CE-001 |

## Capability-to-Epic Mapping

```
E-001 (Configuration)
  └─ CAP-CE-001: Site & Pipeline Configuration [Supporting]

E-002 (Research & Intelligence)
  ├─ CAP-CE-002: Keyword Intelligence [Core]
  ├─ CAP-CE-003: Content Gap Analysis [Core]
  └─ CAP-CE-004: AISO Intelligence [Strategic] ★

E-003 (Content Generation & Optimisation)
  ├─ CAP-CE-005: AI Content Generation [Core]
  └─ CAP-CE-006: Content Optimisation (SEO+AISO) [Strategic] ★

E-004 (Content Publishing)
  ├─ CAP-CE-007: CMS Publishing [Core]
  └─ CAP-CE-008: Schema Markup Automation [Strategic] ★

E-005 (Monitoring & Refresh)
  ├─ CAP-CE-009: Performance Monitoring [Core]
  └─ CAP-CE-010: Content Lifecycle Management [Strategic] ★
```

★ = Strategic differentiator capabilities — these are the competitive moat.

## Capability Framework Diagram

See [diagrams/capability-framework.svg](diagrams/capability-framework.svg) for the rendered D2 diagram.
