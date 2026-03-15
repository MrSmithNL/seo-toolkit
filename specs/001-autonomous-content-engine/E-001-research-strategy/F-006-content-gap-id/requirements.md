---
id: "FTR-SEO-006"
type: feature
title: "Content Gap Identification"
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

# F-006: Content Gap Identification — Requirements

## Problem Statement

Knowing which keywords exist (F-001) and which competitor pages rank for them (F-004, F-005) means nothing without the pivotal question: which of these topics does our site NOT cover? Without a gap analysis, the content calendar (F-007) has no way to prioritise content opportunities over content we've already published.

The problem has two dimensions. The first is topic gaps — subjects competitors cover that our site does not address at all. The second is quality gaps — topics our site technically covers but where our content is significantly weaker than ranking competitors (thin content). Both require different remediation strategies.

**Who has this problem:** The pipeline itself (F-007 needs ranked opportunities, not just a keyword list) and ultimately the store owner who reviews the calendar.

**Cost of inaction:** F-007 cannot prioritise meaningfully without gap data. Calendar recommendations default to arbitrary keyword selection rather than opportunity-based selection. Malcolm's 15-minute review becomes difficult: "why this topic?" has no answer.

---

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors). Focus: gap analysis methodology.

### Competitor Analysis (for this feature)

| Feature/Capability | Semrush | Frase | SurferSEO | SEO.ai | Prevalence | Our Approach | Rationale |
|-------------------|---------|-------|-----------|--------|:----------:|-------------|-----------|
| Keyword gap tool | Full Content Gap — compares your domain vs competitors keyword-by-keyword using their 9B keyword DB | Partial — brief-level gap only (what topics to add to a single article) | Topical Map — shows which keyword groups the site covers vs misses | Not documented | 3/4 | SERP-based gap matrix: compare our pages against competitor SERP positions | No access to Semrush 9B keyword DB; SERP comparison achieves same result at zero cost |
| Topic coverage mapping | Domain-level coverage across all keyword clusters | Article-level topic coverage | Site-level topical authority map | Unknown | 3/4 | Topic-level coverage matrix from competitor content analysis (F-005 output) | Combines SERP position data + content analysis for richer signal than keyword-only |
| Thin content identification | Not a focus — keyword gap only | Yes — identifies topics an article undercoverers vs competitors | Not a focus | Not documented | 1/4 | Flag pages with word_count < 50% of competitor average AND ranking in positions 11-30 | Frase's approach extended: we use objective word count + rank position as thin content signals |
| Opportunity scoring | Volume × difficulty shown; no composite score | Not scored — manual prioritisation | Cluster importance score (opaque) | Not documented | 1/4 | volume × (1 / difficulty) × gap_score composite (transparent algorithm, shown in calendar) | Differentiator: transparent scoring vs opaque. Anti-pattern: SEO.ai black-box selection |
| Multilingual gap analysis | Not documented (Semrush has per-language DBs but no cross-language gap) | Not documented | Not documented | Not documented | 0/4 | Language-aware gap analysis: gaps identified per language, not just in EN | Differentiator — Hairgenetix operates in 9 languages; EN gaps != DE gaps |
| GSC integration for "what we rank for" | Yes — imports GSC data as baseline | No | Yes | Not documented | 2/4 | GSC query data as primary source of "keywords we rank for"; SERP-based fallback | Best accuracy source. GSC connected for Hairgenetix (confirmed). |

### Key Findings

- **Semrush's gap tool is the gold standard** — domain-level comparison with volume data per gap. The limitation is it requires Semrush's keyword DB ($139+/mo). Our SERP-based approach replicates the output without the DB dependency.
- **Frase's gap detection is article-level only** — useful for optimising existing articles but cannot identify which new articles to write. We need domain-level gap detection.
- **SurferSEO's Topical Map** is the closest to our approach — shows keyword cluster coverage gaps. But it's GSC-dependent (excludes new sites) and doesn't show competitor quality benchmarks.
- **No competitor offers multilingual gap analysis** — Semrush can do gaps per country/language DB, but no tool compares gaps across 9 languages simultaneously. This is our clearest differentiator for AISOGEN.
- **Gap recall >= 80%** is the measurable quality target from the Hallucination Risk Assessment (epic-status.md § Hallucination Risk Assessment). This must be validated against manual audit.

### Sources

- Parent epic deep-dive: `specs/001-autonomous-content-engine/E-001-research-strategy/epic-status.md` § Competitive Deep-Dive
- Hallucination risk: `epic-status.md` § Hallucination Risk Assessment — "correctly identifies gaps: ≥80% recall against manual audit"
- RAID log: epic-status.md D2 (GSC access confirmed for Hairgenetix)

---

## User Stories

### US-001: Gap Matrix Generation

**As a** pipeline operator, **I want** a gap matrix showing which topics competitors rank for that our site does not cover, **so that** the content calendar (F-007) can target genuine content opportunities.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

```
WHEN F-004 (SERP data) and F-005 (competitor content data) are available for a domain
THE SYSTEM SHALL produce a gap matrix where each row is a topic/keyword group
AND each column represents a domain (user's site + each competitor)
AND each cell contains:
  - ranking_position (integer 1-50, or null if not ranking)
  - page_url (string or null)
  - word_count (integer or null — from F-005 extraction)
  - depth_score (1-5 or null — from F-005 quality assessment)
```

```
WHEN Google Search Console data is available for the user's site
THE SYSTEM SHALL use GSC query data as the authoritative source of "keywords we rank for"
AND cross-reference GSC queries against the keyword list from F-001
AND classify each keyword as:
  - own_coverage: GSC shows impressions for this keyword (we rank, even if poorly)
  - own_gap: no GSC impressions, but competitor(s) rank in top 10
  - new_opportunity: no GSC impressions, no competitor in top 10 (low competition)
```

```
WHEN GSC data is NOT available
THE SYSTEM SHALL fall back to SERP-based coverage:
  - Check top 50 SERP results per keyword for the user's domain
  - Absence of user domain in top 50 = own_gap
AND flag the analysis as "GSC unavailable — SERP-based coverage (lower accuracy)"
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path (GSC available) | hairgenetix.com vs hairtransplantclinic.de, keyword: "FUE vs DHI" | Row: {keyword: "FUE vs DHI", hairgenetix: {position: null, GSC_impressions: 0}, competitor: {position: 3, url: "/.../fue-vs-dhi", word_count: 3200, depth_score: 4}, classification: "own_gap"} |
| Thin content identified | "hair transplant recovery week 3" — we rank #22, competitor ranks #4 with 2800 words; our page has 450 words | classification: "own_coverage", thin_content: true, our_word_count: 450, competitor_avg: 2800, position: 22 |
| Low-competition opportunity | "post-FUE scalp massage timing" — no competitor in top 10, no GSC impressions | classification: "new_opportunity", competitor_presence: false |
| No GSC available | hairgenetix.com, GSC not connected | Matrix produced with SERP-based coverage, warning: "GSC unavailable — accuracy lower" |
| All topics covered | User site covers every keyword in the research set | Gap matrix shows 0 own_gap rows; new_opportunity rows shown if any |

---

### US-002: Thin Content Identification

**As a** store owner, **I want** to know which of our existing pages rank poorly compared to much-stronger competitor pages, **so that** I can prioritise updating weak existing content alongside creating new content.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN generating the gap matrix
THE SYSTEM SHALL identify thin content entries where:
  - user_site ranks in positions 11-50 for a keyword (ranking but underperforming)
  - AND user_site word_count < 50% of competitor average word count for that keyword
AND flag these entries as thin_content: true
AND include:
  - our_word_count (integer)
  - competitor_avg_word_count (integer — average across top-3 ranking competitor pages)
  - estimated_word_count_gap (integer — words needed to reach competitor average)
  - thin_content_rationale (string — "Ranks #18. Competitor average: 2800 words. Our page: 420 words. 85% below competitor average.")
```

```
WHEN a page is flagged as thin content
THE SYSTEM SHALL recommend "Update existing" rather than "Create new" in the calendar output
AND pass the existing page URL to F-007 so the calendar item links to the page to update
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Classic thin content | We rank #18 for "FUE aftercare", our page is 400 words, top 3 competitors average 2,900 words | thin_content=true, our_word_count=400, competitor_avg=2900, gap=2500, recommendation="Update existing: /aftercare" |
| Ranking well despite fewer words | We rank #4 for "hair transplant Turkey cost", our page is 800 words, competitor avg is 1200 words | thin_content=false (ranking well — don't flag as thin despite word count gap) |
| Not ranking at all | We don't appear in top 50 | Not a thin content case — classified as own_gap |
| Word count unavailable | Competitor page was crawl_failed | thin_content assessment skipped for that comparison, marked "insufficient data" |

---

### US-003: Opportunity Scoring

**As a** pipeline operator, **I want** each gap/opportunity scored by potential value, **so that** F-007 can rank content opportunities from highest to lowest priority.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN the gap matrix is complete
THE SYSTEM SHALL calculate an opportunity_score for each own_gap and new_opportunity row
USING the formula:
  opportunity_score = (volume_normalised × 0.4) + (difficulty_inverse_normalised × 0.3) + (gap_score × 0.3)
WHERE:
  volume_normalised = keyword monthly volume / max volume in this keyword set (0-1 scale)
  difficulty_inverse_normalised = (100 - keyword_difficulty) / 100 (0-1 scale; easier = higher score)
  gap_score = 1.0 if no competitor in top 5 | 0.7 if competitor in positions 6-10 | 0.4 if competitor in positions 1-5
AND store the score and formula inputs alongside each gap row for transparency
```

```
WHEN thin_content rows are scored
THE SYSTEM SHALL use a separate thin_content_priority_score:
  thin_content_priority_score = (position_bucket × 0.5) + (word_count_gap_normalised × 0.5)
WHERE position_bucket = (50 - current_position) / 50 (higher position = more urgent)
AND word_count_gap_normalised = word_count_gap / max_word_count_gap_in_set (larger gap = higher priority)
```

```
WHEN outputting opportunity scores
THE SYSTEM SHALL include a human-readable score_rationale for each entry
USING the format: "Score: 0.74 — High volume (8,100/mo), low difficulty (32/100), no competitor in top 5."
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| High-value gap | "FUE vs DHI comparison" — volume 8100, difficulty 32, no competitor in top 5 | opportunity_score=0.74, score_rationale="High volume (8,100/mo), low difficulty (32/100), no competitor in top 5." |
| Low-value gap | "hair transplant Nairobi" — volume 40, difficulty 15, competitor at #3 | opportunity_score=0.18, score_rationale="Low volume (40/mo), low difficulty (15/100), competitor at position 3." |
| Thin content priority | We rank #22, 380-word page, 2,900-word competitor average | thin_content_priority_score=0.82, rationale="Ranking at #22 (improvable). Content gap: 2,520 words below competitor average." |
| Zero volume keyword | volume=0 (zero/low flagged by F-001) | opportunity_score adjusted: volume_normalised=0, score may still be non-zero due to low difficulty + gap. Included in output but flagged "zero volume — AISO value only". |

---

### US-004: Multilingual Gap Analysis

**As a** store owner with a 9-language store, **I want** gap analysis run per language so I know which topics are missing in each market, **so that** I can prioritise content creation per locale rather than assuming EN gaps apply everywhere.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN the pipeline is configured for multiple languages
THE SYSTEM SHALL run gap analysis separately for each configured language
AND produce a gap matrix per language (not a merged EN-only matrix)
AND a gap present in EN is NOT assumed to exist in DE — each language has independent SERP data
```

```
WHEN comparing gap matrices across languages
THE SYSTEM SHALL produce a cross-language summary showing:
  - gaps present in ALL configured languages (universal gaps)
  - gaps present in only some languages (language-specific gaps)
  - languages where a topic already has coverage (no gap)
```

```
WHEN a topic is a universal gap (missing in all languages)
THE SYSTEM SHALL flag it as universal_gap: true
AND weight this positively in the opportunity score (+0.1 bonus to opportunity_score)
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Universal gap | "FUE vs DHI comparison" missing in DE, FR, NL, EN | universal_gap=true, opportunity_score boosted +0.1, note: "Missing in 4/4 analysed languages" |
| Language-specific gap | "Haartransplantation Kosten" — gap in DE only, equivalent term covered in EN | language_specific: ["DE"], EN coverage: "/hair-transplant-cost-uk" |
| Already covered in all languages | "hair transplant surgery" — we rank top 5 in all configured languages | No gap row. Appears in own_coverage section only. |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN generating the gap matrix for 100 keywords and 3 competitors THE SYSTEM SHALL complete within 3 minutes | p95 < 3 min | Integration test with fixture dataset | No |
| 2 | **Scalability** | N/A — R1 targets 1-5 domains, max 100 keywords, max 5 competitors. Not an at-scale requirement. | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN a competitor data record is missing (crawl_failed in F-005) THE SYSTEM SHALL exclude that competitor from that keyword's gap calculation AND mark the gap row as "partial — [n] competitor(s) excluded" | No pipeline halts from missing competitor data | Integration test with partial competitor fixture | Yes |
| 5 | **Security** | N/A — gap analysis uses internal data only (F-004 + F-005 outputs); no new external systems accessed | — | — | No |
| 6 | **Privacy** | N/A — all input data is public SERP and competitor content data | — | — | No |
| 7 | **Compliance / Regulatory** | N/A — gap analysis is computational; no crawling in this feature | — | — | No |
| 8 | **Interoperability** | WHEN outputting gap analysis data THE SYSTEM SHALL use the ContentGap schema (defined in contracts/) | Schema validation on every output | Unit test with Zod validation | Yes |
| 9 | **Portability** | WHEN running in standalone mode THE SYSTEM SHALL save the gap matrix to `data/gap-analysis/{domain}/{language}.json` | Both storage modes produce identical queryable output | Integration test both adapters | Yes |
| 10 | **Maintainability** | THE SYSTEM SHALL keep opportunity scoring formula in a named, documented constant (not inline) so the formula can be updated without touching pipeline logic | Formula change = 1-line config update | Architecture review | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support fixture-based input (mock SERP records + mock competitor snapshots) so tests run without live data dependencies | Unit + integration tests run fully offline | Test suite passes without network or DB | Yes |
| 12 | **Usability** | N/A — CLI only for R1. Gap matrix surfaces to human via F-007 Content Calendar output. | — | — | No |
| 13 | **Localisation** | WHEN running gap analysis for multiple languages THE SYSTEM SHALL produce independent gap matrices per language AND a cross-language summary | All 9 Hairgenetix languages produce independent matrices | Integration test with 2-language fixture dataset | No |
| 14 | **Monitoring** | WHEN gap analysis completes THE SYSTEM SHALL log: keywords analysed, gap count by classification (own_gap / thin_content / new_opportunity), languages processed, duration | Structured JSON log entry | Log schema validation | No |
| 15 | **Auditability** | WHEN producing opportunity scores THE SYSTEM SHALL persist formula inputs alongside each score (volume, difficulty, gap_score components) so the score is reproducible | Each gap row includes score_inputs object | Unit test checks score_inputs presence | No |
| 16-35 | Remaining categories | N/A — R1 CLI tool; enterprise NFRs apply from R2 (platform integration) | — | — | No |

### AI-Specific NFRs

> Gap analysis is primarily algorithmic (no LLM calls in this feature). AI inputs come from F-005 (quality scores already computed). No new LLM calls in F-006.

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Hallucination rate | WHEN consuming F-005 LLM quality scores THE SYSTEM SHALL treat depth_score fields tagged "llm_assessed" as estimated inputs AND not present them as objective measurements | All gap matrix outputs label LLM-derived fields as "llm_assessed" | Unit test checks field labelling |
| Prompt versioning | N/A — F-006 makes no direct LLM calls | — | — |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (approved at Gate 1) |
| User personas and goals | [x] | JTBD 1-4 in epic-status.md — gap matrix surfaces in F-007 calendar for Malcolm's 15-min review |
| N/A justification | [x] | No UI for R1. F-006 is a pipeline stage. Output surfaces via F-007 Content Calendar in human-readable format. |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. Auth deferred to platform integration (R2+). Config-file tenant context for standalone mode. |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-006 behind `FEATURE_CONTENT_GAP_ANALYSIS` flag (env var in standalone, platform flags in R2+) |
| Config management | [x] | Opportunity scoring weights configurable via `.env` (default weights defined in requirements US-003). Thin content threshold (50% of competitor average) configurable. |
| N/A justification | [x] | No admin UI, billing, or reporting for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | Google Search Console API (for GSC coverage data — OAuth, confirmed connected). No other external APIs. All other inputs are F-004 and F-005 internal outputs. |
| API protocol | [x] | Internal: TypeScript module exports. GSC: Google APIs Node.js client. |
| Resilience per dependency | [x] | GSC API: retry 3x, graceful degradation to SERP-based fallback if GSC unavailable. F-004/F-005 data: pipeline validates input completeness before running; warns if data is partial. |
| Rate limiting | [x] | GSC API: 1200 req/min quota is generous for our scale (max 100 keywords per run). |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature — no migration. Gap matrix schema designed for forward-compatibility with platform DB. |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs: gap counts by classification, languages processed, GSC availability, duration |
| Cost budget | [x] | No LLM calls in F-006. GSC API is free. Total cost: £0. |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. Added at platform integration (R2+). |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 (gap matrix) | `[table-stakes]` | Semrush Content Gap tool, SurferSEO Topical Map, Frase brief-level gaps | 1-Features |
| US-001 (GSC as coverage source) | `[table-stakes]` | Semrush + SurferSEO use GSC data as baseline | 4-Integration |
| US-002 (thin content) | `[table-stakes]` | Frase identifies undercovered topics vs competitors | 1-Features |
| US-003 (transparent opportunity score) | `[differentiator]` | SEO.ai uses opaque scoring (top complaint: 3.4/5 G2) — we show formula inputs | 2-Workflows |
| US-003 (opportunity score formula) | `[anti-pattern]` | SurferSEO cluster importance score is opaque; Semrush shows volume + difficulty separately but no composite | 1-Features |
| US-004 (multilingual gap analysis) | `[differentiator]` | 0/4 competitors offer cross-language gap analysis simultaneously | 1-Features |

---

## Out of Scope

- Competitor domain authority or backlink gap analysis (separate capability)
- Real-time gap monitoring (notify when a competitor publishes a new article on a gap topic) — R2+
- Auto-generating content to fill gaps (that is F-007 → E-002)
- Keyword gap analysis based on paid search (Google Ads) — organic only
- Gap analysis for non-website content (social media, video, podcast) — future capability

---

## Open Questions

- [ ] What is the minimum gap recall threshold to consider F-006 "production-ready"? Proposed: 80% recall vs manual audit (from Hallucination Risk Assessment). Validation plan: run gap analysis on Hairgenetix, compare vs 2-hour manual competitor review by Malcolm.
- [ ] Should thin content rows appear in the same calendar as gap rows, or in a separate "content to update" section? Proposed: separate section in F-007 calendar — "New content" (own_gap + new_opportunity) and "Update existing" (thin_content). Confirm with Malcolm.
- [x] Is GSC connected for Hairgenetix? Yes — confirmed by Malcolm (RAID log D2 closed).
- [ ] What is the default keyword volume minimum for a gap to appear in the calendar? Proposed: 50 monthly searches (captures long-tail with AISO value without flooding the calendar with zero-volume terms). Confirm before build.

---

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-004 SERP Analysis | Internal | Not started | US-001 — competitor ranking positions come from SERP data |
| F-005 Competitor Content Analysis | Internal | Not started | US-001, US-002 — competitor word counts and depth scores come from F-005 |
| Google Search Console API (OAuth) | External | Connected (confirmed) | US-001 accuracy — GSC provides authoritative "what we rank for" data |
| F-001 Keyword Research | Internal | Not started | US-003, US-004 — keyword volume + difficulty used in opportunity scoring |
| F-007 Content Calendar | Internal | Not started | Downstream consumer of gap matrix output |

---

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | GSC impressions data is a reliable proxy for "keywords we rank for" | High | GSC is the authoritative source; confirmed connected for Hairgenetix |
| A2 | The opportunity scoring formula (volume × difficulty inverse × gap) produces sensible rankings for Hairgenetix keyword set | Medium | Compare formula output vs Malcolm's manual prioritisation of 20 keywords; calibrate weights if needed |
| A3 | 80% gap recall vs manual audit is achievable with SERP-based + GSC methodology | Medium | Validate during R1 pilot. Mitigation: if <80%, add LLM-assisted coverage detection as fallback |
| A4 | The 50% of competitor average word count threshold correctly identifies thin content | Medium | Test with Hairgenetix existing pages ranked 11-50; validate with Malcolm whether flagged pages are genuinely thin |
| A5 | EN and DE keyword sets have sufficiently different SERP landscapes to justify separate per-language gap analysis | High | Standard SEO knowledge: SERP results differ significantly by language/country |
