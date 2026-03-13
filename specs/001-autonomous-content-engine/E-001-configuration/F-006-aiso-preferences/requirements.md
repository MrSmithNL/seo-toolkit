---
id: "FTR-CONFIG-006"
type: feature
title: "AISO Scoring Preferences"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 3-requirements
priority: could
created: 2026-03-13
last_updated: 2026-03-13

# === PARENT ALIGNMENT ===
parent_baseline:
  id: "EPC-CONFIG-001"
  version: null
  hash: null
  status: aligned

# === ARCHITECTURE CLASSIFICATION (Gate 0) ===
saas_ecosystem: true
hierarchy_level: L3-module
hierarchy_location: "modules/content-engine/"
capability_group: "seo"
module_manifest: required
tenant_aware: true

# === TRACEABILITY ===
traces_to:
  product_goal: "PROD-001: SEO Toolkit capability engine"
  theme: "specs/001-autonomous-content-engine/theme.md"
  epic: "E-001 Configuration & Setup"
  capability: "CAP-CE-001 — Site & Pipeline Configuration"
---

# AISO Scoring Preferences — Requirements

## Problem Statement

Different sites have different AISO priorities — a product-focused site needs Product schema and citation-friendly definitions, while a blog-focused site needs FAQ schema and topical authority. Without configurable AISO preferences, the pipeline applies a one-size-fits-all approach to AI search optimisation. This is an entirely novel feature — no competitor offers AISO configuration.

## Research Summary

### Competitor Analysis

No competitor offers AISO configuration. This feature is based entirely on our own 36-factor AISO model tested on Hairgenetix (5.5 -> 8.95 score improvement) and Skingenetix.

### Key Findings

- Our 36-factor AISO model covers: content structure, schema markup, citation patterns, entity salience, source attribution, and AI platform targeting
- Different sites benefit from different AISO factor prioritisation
- Default "recommended settings" should work for 80%+ of cases
- Power users (like Malcolm) may want to fine-tune factor weights

### Sources

- `~/.claude/skills/aiso/SKILL.md` (36-factor model)
- Hairgenetix AISO audit results (5.5 -> 8.95)

## Impact Map

```
Goal: Optimise content for AI search citations per site's specific needs
  +-- Actor: Agency operator (Malcolm) / Future SaaS user
       +-- Impact: Content ranks better in AI search results for the site's niche
            +-- Deliverable: Default AISO settings (recommended)
            +-- Deliverable: Priority factor selection
            +-- Deliverable: Schema type configuration
            +-- Deliverable: AI platform targeting
```

## Domain Model

```
AISOPreferences {
  id: UUID
  site_id: UUID (FK -> SiteConfig.id)

  use_recommended: boolean [default: true]

  # When use_recommended is false:
  priority_factors: string[] (from 36-factor model, e.g., ["structured_data", "entity_salience", "citation_hooks"])
  schema_types: enum[] (Article, FAQPage, HowTo, Product, BreadcrumbList, Organization) [default: [Article, FAQPage, BreadcrumbList]]
  ai_platform_targets: enum[] (chatgpt, perplexity, gemini) [default: [chatgpt, perplexity, gemini]]

  created_at: timestamp
  updated_at: timestamp
}
```

## User Stories

### US-001: Use recommended AISO settings

**As a** content pipeline operator, **I want** to use the recommended AISO settings without configuration, **so that** I get good AI search optimisation by default.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN a site is first configured
THE SYSTEM SHALL create AISOPreferences with use_recommended=true
AND apply the standard 36-factor model with equal weighting
AND generate Article, FAQPage, and BreadcrumbList schema by default
AND target all 3 AI platforms (ChatGPT, Perplexity, Gemini)

**Examples:**

| Scenario | Action | Expected State |
|----------|--------|---------------|
| New site, no customisation | Site configured | use_recommended=true, all defaults |

### US-002: Customise AISO priority factors

**As a** content pipeline operator, **I want** to select which AISO factors to prioritise, **so that** content optimisation focuses on what matters most for my site's niche.

**Priority:** Could
**Size:** M

**Acceptance Criteria:**

WHEN the user disables "recommended settings"
THE SYSTEM SHALL display the available AISO factors grouped by category
AND allow the user to select priority factors (subset of the 36-factor model)
AND set use_recommended to false

WHEN priority factors are set
THE SYSTEM SHALL weight those factors higher during E-003 AISO scoring

**Examples:**

| Scenario | Selected Factors | Expected Effect |
|----------|-----------------|-----------------|
| E-commerce site | structured_data, product_schema, entity_salience | Content optimised for product-related AI citations |
| Blog site | faq_schema, topical_authority, citation_hooks | Content optimised for informational AI queries |
| Default (recommended) | All 36 factors equally weighted | Balanced optimisation |

### US-003: Configure schema types per site

**As a** content pipeline operator, **I want** to choose which schema types to generate per article, **so that** schema markup matches my site's content type.

**Priority:** Could
**Size:** S

**Acceptance Criteria:**

WHEN the user customises schema types
THE SYSTEM SHALL accept a selection from: Article, FAQPage, HowTo, Product, BreadcrumbList, Organization
AND store the selection in AISOPreferences
AND E-004 (Publish) uses this selection when injecting schema

**Examples:**

| Scenario | Site Type | Selected Schema | Expected in Articles |
|----------|----------|----------------|---------------------|
| E-commerce | Hairgenetix | Article, Product, FAQPage, BreadcrumbList | All 4 schema types in generated articles |
| Blog | Digital Builders | Article, HowTo, FAQPage, BreadcrumbList | All 4 schema types |
| Minimal | Simple site | Article, BreadcrumbList | Only 2 schema types |

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN reading AISO preferences THE SYSTEM SHALL return the config WITHIN 100ms | p95 < 100ms | Unit test | Yes |
| 2 | **Security** | N/A — no sensitive data in AISO preferences | — | — | No |
| 3 | **Reliability** | WHEN AISO preferences are corrupted or missing THE SYSTEM SHALL fall back to recommended defaults | Fail-safe to defaults | Integration test | Yes |
| 4-8 | **Scalability/Availability/Maintainability/Portability/Accessibility** | N/A | — | — | No |
| 9 | **Usability** | WHEN configuring AISO THE SYSTEM SHALL default to "Use recommended settings" toggle ON | Defaults-first UX | Manual verification | No |
| 10-18 | **Remaining categories** | N/A — AISO preferences are simple config data | — | — | No |
| 19 | **Operation Pattern** | WHEN any command or query is executed THE SYSTEM SHALL follow the 5-step Operation pattern (P-008): Zod input → OperationContext → business logic → persist → emit event + return Result<T, OperationError> | All operations return Result type | Architecture fitness test FF-030 | Yes |
| 20 | **Error Handling** | WHEN an AISO preferences operation fails THE SYSTEM SHALL return an OperationError (not throw) with RFC 7807-compatible error codes and `suggested_action` field | Zero naked `throw` in commands/queries | FF-032 + code review | Yes |
| 21 | **Structured Logging** | WHEN any AISO preferences operation executes THE SYSTEM SHALL emit `operation.started`, `operation.completed`, and `operation.failed` structured JSON events via pino with correlationId + tenantId | 3 log events per operation | Log assertion in integration test | Yes |
| 22 | **Tenant Isolation** | WHEN querying AISO preferences data THE SYSTEM SHALL enforce RLS so Tenant A cannot read/update/delete Tenant B's AISO preferences. Cross-tenant access returns 404 (not 403). | `tenant-isolation.test.ts` passes | Integration test (FF-034) | Yes |
| 23 | **Idempotency** | WHEN creating AISO preferences THE SYSTEM SHALL accept an optional idempotencyKey. Duplicate requests with the same key return the original result without creating duplicates. | Duplicate request = same response | Integration test | Yes |
| 24 | **Serialisable I/O** | WHEN returning AISO preferences data from any operation THE SYSTEM SHALL use ISO 8601 strings for dates (never Date objects), plain objects only (no class instances) | JSON.parse(JSON.stringify(output)) === output | Unit test | Yes |
| 25 | **Contract Completeness** | WHEN exposing AISO preferences commands or queries THE SYSTEM SHALL have a Zod input schema AND explicit TypeScript return type for each | Every public function has Zod + return type | FF-029 | Yes |
| 26 | **No Module State** | THE SYSTEM SHALL NOT use `let` or `var` at module scope in AISO preferences `src/` files (except type exports and `const`) | Zero mutable module-level state | FF-033 | Yes |
| 27 | **PII Redaction** | WHEN logging AISO preferences data THE SYSTEM SHALL redact any email, phone, IP address, or personal data fields using pino's redaction config | PII fields show `[REDACTED]` in logs | Log inspection test | Yes |
| 28 | **Prefixed IDs** | WHEN creating an AISOPreferences record THE SYSTEM SHALL generate IDs with `asp_` prefix using NanoID or UUID v7 | All IDs match `asp_*` pattern | Unit test | Yes |

## Out of Scope

- AISO scoring logic (evaluating content against factors) — that's E-003
- Schema generation/injection — that's E-004
- AI platform monitoring (checking actual citations) — that's E-005
- Custom AISO factor creation — V2 (36 factors are hardcoded for V1)

## Open Questions

- [x] Should we expose all 36 factors or group them? **Answer:** Group by category (content structure, schema, citations, entities, sources, platforms). Show groups, expand on demand.
- [x] Is this feature necessary for V1? **Answer:** The defaults work without user input (US-001). Customisation (US-002, US-003) is Could-have. If time is tight, ship defaults-only.

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-005 (Quality Thresholds) | Internal | In progress | AISO score minimum defined in F-005 feeds into this feature |
| AISO 36-factor model | Internal (skill) | Ready | Factor list from `aiso` skill |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | Recommended defaults work for 80%+ of sites without customisation | Medium | Test with 3 test sites — do defaults produce good AISO scores? |
| A2 | Users can meaningfully select priority factors from the 36-factor model | Low | UX research needed — are 36 factors too many? Group into 6 categories. |
| A3 | Different schema type selections produce meaningfully different AISO scores | Medium | Test with Hairgenetix — compare Article-only vs Article+FAQ+Product |
