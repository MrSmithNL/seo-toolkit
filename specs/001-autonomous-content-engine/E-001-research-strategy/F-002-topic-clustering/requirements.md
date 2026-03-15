---
id: "FTR-SEO-002"
type: feature
title: "Topic Clustering"
project: PROD-001
domain: seo.content-pipeline
parent: "PROD-001-SPEC-E-001"
status: draft
phase: 3-requirements
priority: should
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

# F-002: Topic Clustering — Requirements

## Problem Statement

A raw keyword list of 100-200 keywords is not actionable for content planning. Without grouping keywords into semantic topics, a content calendar becomes a flat list with no coherent structure — articles compete with each other, internal linking is arbitrary, and topical authority is never built.

**Who has this problem:** Store owners using the pipeline who need a hub-and-spoke content strategy, not just a keyword dump.

**Cost of inaction:** Content calendar (F-007) produces a flat, unstructured article list. No pillar pages are identified. No internal linking strategy is possible. AISO topical authority signal is weak. The pipeline delivers data but not strategy.

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors) and epic-status.md § Competitive Deep-Dive.

### Competitor Analysis (for this feature)

| Feature/Capability | Frase | SEO.ai | SurferSEO | Semrush ContentShake | Prevalence | Our Approach | Rationale |
|-------------------|-------|--------|-----------|----------------------|:----------:|-------------|-----------|
| Topic clustering / grouping | Manual grouping via topic score UI | Auto-clusters (fully black-box) | "Topical Map" — visual pillar + support structure | Topic Research tool (separate product) | 4/4 | LLM semantic clustering with transparent grouping rationale | Avoid SEO.ai's black-box problem; show why keywords are grouped |
| Pillar page identification | User decides | Auto-selects (no explanation) | Identifies pillar automatically | Manual selection from map | 3/4 | LLM selects pillar candidate per cluster with reasoning | Transparent selection + human override |
| Cluster quality scoring | None | None visible | Not documented | None | 0/4 | Coherence score per cluster (tight semantic focus = high score) | **Differentiator** — no competitor scores cluster quality |
| Cluster-to-content mapping | Brief template per cluster | Article generated per cluster | Visual map only | Topic cards only | 2/4 | Each cluster maps to: 1 pillar brief + N supporting article briefs | Direct pipeline output to E-002 |
| New-site topical mapping | Not documented | Not documented | GSC-dependent | Not documented | 0/4 | LLM-only clustering works without GSC data | **Differentiator** — see epic RAID A2 + epic anti-pattern #6 |

### Key Findings

- SurferSEO's Topical Map is the most complete visual implementation but requires domain history (GSC). New sites are excluded — this is a top complaint.
- SEO.ai auto-clusters but gives no insight into grouping decisions. Users can't challenge or adjust clusters. This is the single largest trust problem in the category (G2 reviews confirm).
- No competitor scores cluster quality. A tight cluster (all keywords map cleanly to one topic) is far more valuable than a loose one — but users currently have no signal for this.
- Our advantage: LLM semantic grouping works without domain history, is transparent by design, and produces structured output compatible with E-002 content brief generation.

### Sources

- Parent epic deep-dive: `specs/E-001/epic-status.md` § Competitive Deep-Dive
- Key anti-pattern #6: "GSC-only topical mapping (SurferSEO — excludes new sites)"
- Key differentiator #2: "Transparent autonomous reasoning — show the 'why' for every keyword decision"

---

## User Stories

### US-001: Semantic Keyword Clustering

**As a** pipeline operator, **I want** keywords grouped into semantic topic clusters automatically, **so that** I can see which keywords belong together and build a hub-and-spoke content structure without manual sorting.

**Priority:** Should
**Size:** M

**Acceptance Criteria:**

```
WHEN keyword research (F-001) has completed for a domain
THE SYSTEM SHALL group the keyword set into semantic clusters using LLM analysis
AND each cluster SHALL contain between 3 and 20 keywords
AND keywords with no clear semantic grouping SHALL be placed in an "unclustered" set
AND the grouping rationale for each cluster SHALL be returned as a short text summary (1-2 sentences)
```

```
WHEN clustering 150 or fewer keywords
THE SYSTEM SHALL complete clustering WITHIN 60 seconds
AND consume fewer than 50,000 LLM tokens for the full clustering operation
```

```
WHEN two or more keywords are semantically equivalent (same intent, minor phrasing variation)
THE SYSTEM SHALL group them in the same cluster
AND flag one as the "primary keyword" (highest volume) and the others as "variants"
```

**Examples:**

| Scenario | Input Keywords | Expected Output |
|----------|---------------|----------------|
| Happy path | "FUE hair transplant", "FUE procedure", "FUE vs FUT", "FUE recovery time", "FUE cost Germany" | Cluster: "FUE Hair Transplant" (5 keywords), rationale: "All keywords relate to the FUE surgical technique — procedure, comparison, recovery, and cost queries" |
| Loose keyword | "celebrity hair transplant" | Placed in "unclustered" — insufficient volume of related keywords to form a cluster |
| Variant detection | "hair transplant cost", "cost of hair transplant", "hair transplant price" | Same cluster; "hair transplant cost" flagged as primary (highest volume) |
| Large set | 150 keywords from hairgenetix.com | 8-15 clusters produced, each with 3-20 keywords; unclustered set ≤ 15 keywords |
| Very small set | 10 keywords | 2-4 clusters produced; all keywords placed |

---

### US-002: Pillar Page Identification

**As a** pipeline operator, **I want** one pillar topic identified per cluster, **so that** I know which article should be the cornerstone piece that other articles link back to.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

```
WHEN a cluster has been formed (US-001)
THE SYSTEM SHALL identify one keyword as the pillar candidate
AND the pillar candidate SHALL be the keyword with: highest search volume AND broadest intent scope (covers the cluster topic at a general level)
AND the selection rationale SHALL be returned (1 sentence)
```

```
WHEN a cluster contains only transactional or navigational keywords
THE SYSTEM SHALL flag the cluster as "no suitable pillar — consider informational expansion"
AND still return the highest-volume keyword as the provisional pillar
```

**Examples:**

| Scenario | Cluster Keywords | Expected Pillar | Rationale |
|----------|-----------------|----------------|-----------|
| Clear pillar | "hair transplant" (vol: 8100), "hair transplant Germany" (vol: 2400), "hair transplant before after" (vol: 1300) | "hair transplant" | Highest volume, broadest scope — covers the topic at the category level |
| All transactional | "buy hair growth serum", "hair growth serum price", "order hair growth serum online" | "buy hair growth serum" (provisional) | Flagged: "no suitable pillar — consider informational expansion (e.g., 'hair growth serum guide')" |
| Tie on volume | Two keywords at 2400 | Broader-intent keyword selected | Intent scope breaks tie; rationale explains choice |

---

### US-003: Cluster Quality Scoring

**As a** pipeline operator, **I want** a quality score for each cluster, **so that** I can prioritise tight, high-value clusters over loose, unfocused ones when planning the content calendar.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

```
WHEN a cluster has been formed (US-001) and pillar identified (US-002)
THE SYSTEM SHALL assign a coherence score from 1-10 to the cluster
WHERE:
  - 8-10 = tight cluster (all keywords clearly support one topic, strong internal linking opportunity)
  - 5-7 = moderate cluster (mostly related but some peripheral keywords included)
  - 1-4 = loose cluster (keywords share a theme but diverge on intent or topic)
AND the score SHALL be derived from LLM evaluation of keyword semantic relatedness within the cluster
AND the score SHALL include a one-sentence explanation
```

```
WHEN cluster output is requested by the content calendar (F-007)
THE SYSTEM SHALL include the coherence score as a sort/filter field
AND clusters with coherence score < 4 SHALL be flagged with a warning: "Low coherence — review before planning content"
```

**Examples:**

| Cluster Name | Keywords | Expected Score | Rationale |
|-------------|----------|:--------------:|-----------|
| FUE Hair Transplant | "FUE procedure", "FUE vs FUT", "FUE recovery", "FUE cost", "FUE surgeon Germany" | 9 | All keywords map to the same surgical technique with complementary intent (procedure, comparison, recovery, cost, provider) |
| Hair Loss General | "hair loss", "hair transplant", "hair growth serum", "bald spot treatment", "alopecia" | 4 | Keywords span multiple sub-topics; low cohesion — better split into 3 clusters |
| Post-Transplant Care | "post-transplant care", "after hair transplant", "hair transplant recovery week 1", "recovery week 3" | 8 | Tight focus on recovery phase; all keywords support one pillar article |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN clustering up to 150 keywords THE SYSTEM SHALL complete within 60 seconds | p95 < 60s | Integration test with timer | No |
| 2 | **Scalability** | N/A — R1 targets 50-200 keywords per domain, not thousands | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN the LLM call for clustering fails THE SYSTEM SHALL retry once with exponential backoff AND return a partial result (keywords in unclustered set) rather than failing entirely | No total failure on single LLM error | Integration test with mocked LLM failure | Yes |
| 5 | **Security** | N/A — no new API keys; uses existing Claude API key from F-001 config | — | — | No |
| 6 | **Privacy** | N/A — keyword data is public; no PII processed | — | — | No |
| 7 | **Compliance / Regulatory** | N/A — no regulatory requirements for keyword clustering | — | — | No |
| 8 | **Interoperability** | WHEN outputting cluster data THE SYSTEM SHALL use the TopicCluster schema (defined in contracts/) AND the schema SHALL be consumed by F-007 (Content Calendar) without transformation | Schema validation on every output | Unit test with Zod validation | Yes |
| 9 | **Portability** | WHEN running in standalone mode THE SYSTEM SHALL save cluster output to `data/clusters/{domain}.json`; WHEN in platform mode THE SYSTEM SHALL use DatabasePort adapter | Both modes produce identical query results | Integration test both adapters | Yes |
| 10 | **Maintainability** | THE SYSTEM SHALL use a versioned clustering prompt stored in `prompts/clustering-v{N}.txt` | Prompt version in every LLM log entry | File structure check + log audit | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support a mock LLM response that returns fixture cluster data so tests run without API keys | Unit test suite passes offline | CI run without CLAUDE_API_KEY set | Yes |
| 12 | **Usability** | N/A — CLI only for R1; no interactive UI | — | — | No |
| 13 | **Localisation** | WHEN clustering keywords from multiple languages THE SYSTEM SHALL cluster each language's keyword set independently (not cross-language) | Per-language clusters returned | Integration test with DE + EN keyword sets | No |
| 14 | **Monitoring** | WHEN clustering completes THE SYSTEM SHALL log: cluster count, avg cluster size, coherence scores, LLM tokens consumed, duration | Structured JSON log entry | Log schema validation | No |
| 15-26 | Remaining categories | N/A — R1 CLI tool; applies from R2 (platform integration) | — | — | No |
| 27 | **Configuration / Customisation** | WHEN running the pipeline THE SYSTEM SHALL accept a `--max-cluster-size` parameter (default 20) AND a `--min-cluster-size` parameter (default 3) | Custom sizes applied in clustering output | Unit test with custom params | No |
| 28-35 | Remaining categories | N/A — R1 CLI tool | — | — | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN clustering 150 keywords THE SYSTEM SHALL complete all LLM calls within 60 seconds | p95 < 60s | Integration test with timer |
| Token economics | WHEN clustering a keyword set of 150 keywords THE SYSTEM SHALL consume fewer than 50,000 LLM input+output tokens | < $0.20 at Claude Sonnet pricing | Token counter in logs |
| Hallucination rate | WHEN assigning keywords to clusters THE SYSTEM SHALL include each keyword in exactly one cluster or the unclustered set; no keyword SHALL be omitted or duplicated | 100% keyword coverage, 0% duplication | Unit test validates input vs output keyword sets match exactly |
| Model degradation detection | N/A — R1; cluster quality reviewed by human at content calendar stage | — | — |
| Prompt versioning | WHEN using LLM prompts for clustering THE SYSTEM SHALL version prompts in `prompts/` directory (not inline strings) | All prompts in `prompts/` with version suffix | File structure check |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (inherited from epic Gate 1 decision) |
| User personas and goals | [x] | JTBD 1 + 2 in epic-status.md |
| N/A justification | [x] | No UI for R1. CLI outputs cluster data as JSON/Markdown. All competitors have web UI for topic maps; CLI is justified as internal validation tool (Gate 1 approved). |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. Auth deferred to platform integration (R2+). |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-002 behind `FEATURE_TOPIC_CLUSTERING` flag (env var) |
| Config management | [x] | Cluster size parameters via CLI args or config file. No new secrets required. |
| N/A justification | [x] | No admin UI or billing for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | Claude API (LLM clustering) — already configured from F-001. No new external dependencies. |
| API protocol | [x] | Internal: TypeScript module exports. Output: JSON (standalone) or DatabasePort adapter (platform). |
| Resilience per dependency | [x] | Claude API: retry once on failure; graceful degradation to unclustered set on persistent failure. |
| Rate limiting | [x] | No additional rate limits — batches keywords into a single LLM call per language set. |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature. No migration. TopicCluster schema designed for forward-compatibility with platform DB. |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs: cluster count, coherence scores, tokens consumed, duration, prompt version |
| Cost budget | [x] | < $0.20 per clustering run at 150 keywords (50K tokens at Claude Sonnet pricing) |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 (clustering) | `[table-stakes]` | All 4 competitors provide topic grouping | 1-Features |
| US-001 (rationale text) | `[differentiator]` | SEO.ai black-box clustering is top trust complaint; transparent reasoning is white space | 2-Workflows |
| US-002 (pillar ID) | `[table-stakes]` | SurferSEO Topical Map, SEO.ai auto-select | 1-Features |
| US-002 (new-site support) | `[differentiator]` | SurferSEO requires GSC; excludes new sites (anti-pattern #6 in epic) | 1-Features |
| US-003 (coherence score) | `[differentiator]` | 0/4 competitors score cluster quality; provides actionable signal for calendar prioritisation | 5-Data |

## Out of Scope

- Visual topic map UI (planned for E-006 dashboard, R2+)
- Cross-language cluster merging (e.g., grouping the DE and EN versions of the same topic — deferred to R2+)
- Cluster performance tracking over time (belongs in E-005 Measurement)
- Backlink-based cluster authority scoring (requires domain data not available in R1)

## Open Questions

- [ ] Should clusters be re-run automatically when F-001 keyword data refreshes, or only on explicit user request? (Proposed: explicit request for R1; auto-refresh on keyword delta > 20% for R2+)
- [ ] What is the maximum acceptable cluster count for a 150-keyword set before the content calendar becomes unmanageable? (Proposed: cap at 15 clusters; merge smallest clusters if exceeded)

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 Keyword Research | Internal | Not started | US-001 — clustering requires keyword list |
| Claude API (existing config) | External | Ready | All stories — LLM clustering |
| TopicCluster schema (contracts/) | Internal | To be defined | US-001 output, F-007 input |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | LLM semantic clustering produces coherent groups without a vector database (epic RAID A2) | Medium | Validate with Hairgenetix keyword set during R1 build; compare LLM clusters vs manual human grouping |
| A2 | 150 keywords can be clustered in a single LLM context window without chunking | High | Claude Sonnet context window is sufficient for 150 keyword strings + prompt |
| A3 | 50,000 tokens is sufficient for clustering 150 keywords (prompt + full keyword list + output) | Medium | Measure during prototype; adjust budget threshold if needed |
| A4 | Per-language independent clustering (A1) is acceptable for R1 — cross-language deduplication deferred | High | Confirmed in epic scope (single-language pilot for Hairgenetix DE first) |
