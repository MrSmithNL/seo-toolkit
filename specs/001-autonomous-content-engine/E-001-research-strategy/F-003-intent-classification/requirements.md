---
id: "FTR-SEO-003"
type: feature
title: "Search Intent Classification"
project: PROD-001
domain: seo.content-pipeline
parent: "PROD-001-SPEC-E-001"
status: draft
phase: 3-requirements
priority: must
created: 2026-03-15
last_updated: 2026-03-15

parent_baseline:
  id: "PROD-001-SPEC-E-001"
  version: null
  hash: null
  status: aligned

saas_ecosystem: true
hierarchy_level: L3-module
hierarchy_location: "modules/content-engine/"
capability_group: seo
module_manifest: required
tenant_aware: true

traces_to:
  product_goal: "Autonomous SEO/GEO/AISO content pipeline"
  theme: "001-autonomous-content-engine"
  epic: "E-001"
  capability: "CAP-SEO-001"
---

# F-003: Search Intent Classification — Requirements

## Problem Statement

A keyword with 8,000 monthly searches is not automatically valuable. "Hair transplant" typed by someone researching the procedure requires an informational article. The same phrase typed by someone ready to book a consultation requires a landing page. Writing the wrong content format for a keyword's intent results in poor rankings, zero conversions, and wasted content budget.

**Who has this problem:** Store owners who receive a keyword list (F-001) and don't know what type of content to create for each keyword. Without intent classification, the content calendar (F-007) cannot recommend the right article format.

**Cost of inaction:** Content calendar produces keyword targets with no format guidance. Writers produce informational articles for transactional keywords (no conversion) or product pages for informational queries (no ranking). Pipeline is blind to the single most important content strategy decision.

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors) and epic-status.md § Competitive Deep-Dive.

### Competitor Analysis (for this feature)

| Feature/Capability | Frase | SEO.ai | SurferSEO | Semrush ContentShake | Prevalence | Our Approach | Rationale |
|-------------------|-------|--------|-----------|----------------------|:----------:|-------------|-----------|
| 4-type intent classification (info/comm/trans/nav) | Yes — shown in research workflow | Yes — auto-classified | Yes — shown in SERP analyzer | Yes — in Keyword Magic Tool | 4/4 | LLM classifies from keyword text alone | Match table stakes; LLM approach validated (research confirms 90%+ accuracy on keyword text alone) |
| Intent-to-format mapping | None — shows label only | None visible | None | None | 0/4 | LLM recommends content format (article type, structure) based on intent | **Differentiator** — epic differentiator #5 |
| Intent confidence score | None | None | None | None | 0/4 | Confidence score per classification (high/medium/low) | Transparency — avoids silent misclassifications |
| Batch processing | Not documented | Yes (auto-pipeline) | Not documented | Yes — Keyword Magic processes thousands | 2/4 | Batch all keywords from F-001 in one LLM call per 50-keyword chunk | Efficient; avoids per-keyword LLM calls |
| SERP-validated intent | Uses SERP data for brief generation | Uses SERP | SERP is primary input | Uses SERP | 4/4 | Text-only for R1; SERP-validated intent in R2+ (after F-004 is live) | R1 pragmatism; text-only LLM accuracy is sufficient for content planning |

### Key Findings

- All 4 competitors classify intent but none map intent to a recommended content format. A store owner who knows a keyword is "informational" still has to decide whether to write a how-to guide, a definition article, a comparison post, or a FAQ page. This mapping is our differentiator.
- LLM-based intent classification from keyword text alone achieves 90%+ agreement with human manual review (validated by multiple SEO studies cited in competitive deep-dive research). No SERP scraping required for R1.
- The 4-type taxonomy (informational, commercial, transactional, navigational) is the industry standard. Using a different taxonomy would break interoperability with competitor mental models and user expectations.
- SEO.ai classifies intent automatically but users cannot see why — this is part of the same black-box complaint pattern that applies to their clustering. Our confidence score and reasoning text addresses this.

### Sources

- Parent epic deep-dive: `specs/E-001/epic-status.md` § Competitive Deep-Dive
- Epic differentiator #5: "Intent-to-format mapping — recommending article format, not just intent classification"
- Table stakes #5: "Search intent classification (4-type)"

---

## User Stories

### US-001: Four-Type Intent Classification

**As a** pipeline operator, **I want** every keyword classified by search intent (informational, commercial, transactional, navigational), **so that** I know what user need each keyword represents before creating content.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN keyword research (F-001) has completed for a domain
THE SYSTEM SHALL classify each keyword into one of four intent types:
  - informational: user wants to learn or understand something
  - commercial: user is researching options before a purchase decision
  - transactional: user intends to take an action (buy, book, sign up)
  - navigational: user is looking for a specific website or brand
AND each classification SHALL include a confidence level: high | medium | low
AND each classification SHALL include a one-sentence rationale
```

```
WHEN classifying keywords in batch
THE SYSTEM SHALL process keywords in chunks of up to 50 per LLM call
AND return classifications for all keywords in a single pipeline pass
AND preserve the original keyword order in the response
```

```
WHEN a keyword has ambiguous intent (could be classified as informational OR commercial)
THE SYSTEM SHALL classify it as the higher-intent type (commercial > informational)
AND set confidence to "medium"
AND include both candidate intents in the rationale
```

**Examples:**

| Keyword | Expected Intent | Confidence | Rationale |
|---------|:--------------:|:----------:|-----------|
| "hair transplant recovery timeline" | informational | high | User wants to understand the recovery process — no purchase signal |
| "best hair transplant clinic Germany" | commercial | high | User is comparing providers before booking — classic commercial investigation |
| "book hair transplant consultation" | transactional | high | Explicit action intent — "book" is a strong transactional signal |
| "hairgenetix" (brand name) | navigational | high | User is looking for a specific brand |
| "hair transplant" (head term) | commercial | medium | Ambiguous — could be informational research OR commercial investigation; commercial assigned as higher-intent |
| "FUE procedure" | informational | medium | Could be pre-purchase research; assigned informational, rationale notes commercial possibility |

---

### US-002: Content Format Recommendation

**As a** content planner, **I want** a recommended article format for each keyword based on its intent, **so that** I know what type of content to commission without needing SEO expertise.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

```
WHEN a keyword has been classified with an intent type (US-001)
THE SYSTEM SHALL recommend one content format from the following list:
  - how-to guide
  - definition / explainer
  - comparison article
  - listicle (top N list)
  - FAQ page
  - product landing page
  - category page
  - location page
  - brand / navigational page
AND the recommendation SHALL be based on both the intent type AND the keyword phrasing signals
```

```
WHEN the keyword contains format signals (e.g., "how to", "best", "vs", "what is", "near me")
THE SYSTEM SHALL weight the format recommendation towards the signal-indicated format
AND include the signal detected in the rationale field
```

```
WHEN the content format recommendation is consumed by F-007 (Content Calendar)
THE SYSTEM SHALL expose format as a structured field (not free text) so the calendar can group articles by format type
```

**Examples:**

| Keyword | Intent | Recommended Format | Signal Detected |
|---------|:------:|-------------------|----------------|
| "how to care for hair after transplant" | informational | how-to guide | "how to" prefix |
| "FUE vs DHI hair transplant" | commercial | comparison article | "vs" signal |
| "best hair transplant clinics" | commercial | listicle (top N list) | "best" signal |
| "what is alopecia areata" | informational | definition / explainer | "what is" signal |
| "hair transplant consultation Berlin" | transactional | location page | location + transactional intent |
| "hair growth serum" (generic) | commercial | category page | No specific signal; commercial + short-tail = category |
| "hairgenetix reviews" | commercial | brand / navigational page | Brand name + "reviews" |

---

### US-003: Batch Classification Output and Persistence

**As a** pipeline operator, **I want** intent classifications saved alongside keyword data, **so that** downstream features (content calendar, brief generation) can filter and sort by intent without re-running classification.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

```
WHEN intent classification completes for a domain's keyword set
THE SYSTEM SHALL persist intent and format fields to the KeywordRecord schema (F-001 US-005)
AND the fields SHALL be:
  - intent: "informational" | "commercial" | "transactional" | "navigational"
  - intent_confidence: "high" | "medium" | "low"
  - intent_rationale: string (1 sentence)
  - recommended_format: enum from approved format list
  - format_signal: string | null (detected keyword signal, if any)
  - classified_at: timestamp
```

```
WHEN a keyword's volume data changes significantly (>30% delta) on a subsequent F-001 run
THE SYSTEM SHALL NOT automatically re-classify intent (intent is stable; volume changes do not change intent)
AND SHALL expose a `--reclassify` flag for manual re-run
```

```
WHEN downstream features query keyword data
THE SYSTEM SHALL support filtering by intent type:
  getKeywordsByDomain(domain, filters: { intent?: IntentType, minConfidence?: "high" | "medium" })
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| First classification run | 150 keywords for hairgenetix.com | All 150 records updated with intent + format fields |
| Second run (volume refresh) | Same 150 keywords, 1 month later | Intent fields unchanged; only volume/trend fields updated |
| Manual reclassify | `--reclassify` flag passed | All intent fields recalculated from current keyword text |
| Downstream filter | `getKeywordsByDomain("hairgenetix.com", { intent: "transactional" })` | Returns only keywords classified as transactional (e.g., 12 of 150) |
| High-confidence only | `getKeywordsByDomain("hairgenetix.com", { minConfidence: "high" })` | Returns only keywords where confidence = "high" |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN classifying up to 150 keywords THE SYSTEM SHALL complete within 90 seconds | p95 < 90s | Integration test with timer | No |
| 2 | **Scalability** | N/A — R1 targets 50-200 keywords per domain | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN an LLM call for classification fails THE SYSTEM SHALL retry once AND mark affected keywords as "intent_unclassified" rather than failing the entire batch | No total failure on single LLM error | Integration test with mocked LLM failure | Yes |
| 5 | **Security** | N/A — no new API keys; uses existing Claude API configuration | — | — | No |
| 6 | **Privacy** | N/A — keyword data is public; no PII processed | — | — | No |
| 7 | **Compliance / Regulatory** | N/A — no regulatory requirements for intent classification | — | — | No |
| 8 | **Interoperability** | WHEN outputting intent data THE SYSTEM SHALL extend the KeywordRecord schema (F-001 contracts/) with intent fields; no separate schema object | Schema validation on every output | Unit test with Zod validation | Yes |
| 9 | **Portability** | N/A — uses same storage adapter as F-001; no additional portability requirements | — | — | No |
| 10 | **Maintainability** | THE SYSTEM SHALL use a versioned classification prompt stored in `prompts/intent-classification-v{N}.txt` AND the approved format list SHALL be defined as a TypeScript enum in `contracts/` | Prompt version in every LLM log; no hardcoded format strings | File structure check | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support a mock LLM response returning fixture intent data | Unit tests run without API keys | CI run without CLAUDE_API_KEY | Yes |
| 12 | **Usability** | N/A — CLI only for R1 | — | — | No |
| 13 | **Localisation** | WHEN classifying keywords in non-English languages THE SYSTEM SHALL produce intent classifications in the same English taxonomy (informational / commercial / transactional / navigational) regardless of keyword language | All 9 languages classified correctly | Integration test with DE keyword set |  No |
| 14 | **Monitoring** | WHEN classification completes THE SYSTEM SHALL log: keywords classified, intent distribution (count per type), confidence distribution, tokens consumed, duration | Structured JSON log entry | Log schema validation | No |
| 15-35 | Remaining categories | N/A — R1 CLI tool; enterprise NFRs apply from R2 | — | — | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN classifying 150 keywords in batches of 50 THE SYSTEM SHALL complete within 90 seconds total | p95 < 90s | Integration test with timer |
| Token economics | WHEN classifying 150 keywords THE SYSTEM SHALL consume fewer than 30,000 LLM input+output tokens | < $0.12 at Claude Sonnet pricing | Token counter in logs |
| Hallucination rate | WHEN classifying keywords THE SYSTEM SHALL achieve >= 90% agreement with manual human review on a sample of 50 Hairgenetix keywords | >= 90% match rate | Manual audit during R1 validation |
| Model degradation detection | N/A — R1; accuracy validated once during R1 pilot | — | — |
| Prompt versioning | WHEN using LLM prompts for classification THE SYSTEM SHALL version prompts in `prompts/` directory | All prompts in `prompts/` with version suffix | File structure check |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (inherited from epic Gate 1 decision) |
| User personas and goals | [x] | JTBD 2 + 4 in epic-status.md — prioritised list + transparent reasoning |
| N/A justification | [x] | No UI for R1. CLI outputs intent-enriched keyword data as JSON. All competitors show intent in web UI; CLI is justified for internal validation (Gate 1 approved). |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. Auth deferred to platform integration (R2+). |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-003 behind `FEATURE_INTENT_CLASSIFICATION` flag (env var) |
| Config management | [x] | No new secrets. Prompt version controlled via file naming convention. |
| N/A justification | [x] | No admin UI or billing for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | Claude API (LLM classification) — already configured from F-001. No new external dependencies for R1. |
| API protocol | [x] | Internal module only. Intent fields extend KeywordRecord schema (F-001 contracts/). |
| Resilience per dependency | [x] | Claude API: retry once on failure; unclassified flag on persistent failure. No silent data loss. |
| Rate limiting | [x] | Batches 50 keywords per LLM call — 3 calls for 150 keywords; no additional rate limits. |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature. Extends F-001 KeywordRecord schema with additive fields only (no breaking change). |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs: intent distribution, confidence distribution, tokens consumed, duration, prompt version |
| Cost budget | [x] | < $0.12 per classification run at 150 keywords (30K tokens at Claude Sonnet pricing) |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 (4-type intent) | `[table-stakes]` | All 4 competitors classify intent using informational/commercial/transactional/navigational | 1-Features |
| US-002 (format recommendation) | `[differentiator]` | 0/4 competitors map intent to content format; listed as epic differentiator #5 | 2-Workflows |
| US-001 (confidence + rationale) | `[differentiator]` | Transparent reasoning — counters SEO.ai black-box complaint (epic anti-pattern #2) | 2-Workflows |
| US-003 (batch persistence) | `[differentiator]` | No competitor exposes persistent keyword DB with queryable intent field (epic differentiator, persistent DB) | 5-Data |

## Out of Scope

- SERP-validated intent classification (using live SERP results to confirm intent — deferred to R2+ when F-004 is live and SERP data is available)
- Sub-intent classification (e.g., "informational > how-to vs informational > definition" — the 4-type taxonomy is sufficient for R1 content planning)
- Intent change detection over time (belongs in E-005 Measurement)
- User-facing intent override UI (belongs in E-006 dashboard)

## Open Questions

- [ ] Should the format recommendation list be extensible by the user (e.g., add "podcast episode" or "video script" as formats)? (Proposed: fixed enum for R1 to ensure F-007 can group by format; extensible in R2+ via config)
- [ ] How should we handle navigational keywords (brand searches) in the content calendar — include, exclude, or flag separately? (Proposed: include but flag — they may indicate landing page optimisation opportunities)

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 Keyword Research | Internal | Not started | US-001 — classification requires keyword list |
| KeywordRecord schema (contracts/) | Internal | To be defined in F-001 | US-003 — intent fields extend this schema |
| Claude API (existing config) | External | Ready | All stories — LLM classification |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | LLM classification from keyword text alone achieves >= 90% agreement with manual review | High | Validate with 50-keyword Hairgenetix sample during R1 build; compare LLM output vs Malcolm's manual classification |
| A2 | The 4-type intent taxonomy is sufficient for R1 content planning decisions | High | Matches all 4 competitors; no evidence of user need for finer taxonomy at planning stage |
| A3 | Intent is stable across keyword refreshes (volume changes don't change intent) | High | Linguistically true for stable keywords; edge case: new SERP trends can shift intent over months — address in R2 with SERP-validated intent |
| A4 | Non-English keywords can be accurately classified into English intent categories by the LLM | High | LLM multilingual classification is well-established; validate with DE keyword set during pilot |
