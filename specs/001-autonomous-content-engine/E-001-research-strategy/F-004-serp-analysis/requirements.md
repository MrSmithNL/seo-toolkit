---
id: "FTR-SEO-004"
type: feature
title: "SERP Analysis"
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

# F-004: SERP Analysis — Requirements

## Problem Statement

Knowing a keyword has 8,000 monthly searches tells you the opportunity. Knowing what currently ranks for that keyword tells you whether you can compete and what the content must contain. Without SERP analysis, content briefs are built from keyword data alone — no baseline for word count, no knowledge of SERP features that steal clicks, no understanding of whether the top results are blogs, product pages, or YouTube videos.

**Who has this problem:** The pipeline itself — F-005 (Competitor Content Analysis), F-006 (Content Gap), and F-007 (Content Calendar) all require SERP data as input. Without F-004, downstream features either can't run or produce lower-quality output. The store owner doesn't directly request SERP analysis; the pipeline needs it to produce accurate content strategy.

**Cost of inaction:** Content briefs target incorrect formats. Keyword difficulty estimates stay at heuristic quality. AI Overview detection is impossible — the fastest-growing SERP feature that directly reduces organic clicks. Gap analysis (F-006) can't compare content coverage without knowing what ranks.

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors) and epic-status.md § Competitive Deep-Dive.

### Competitor Analysis (for this feature)

| Feature/Capability | Frase | SEO.ai | SurferSEO | Semrush ContentShake | Prevalence | Our Approach | Rationale |
|-------------------|-------|--------|-----------|----------------------|:----------:|-------------|-----------|
| SERP result count analysed | Top 20 | Top 10 (estimated) | Top 20+ (documented) | Top 10 via SERP data | 4/4 | Top 10 for R1 (DataForSEO API); configurable to 20 for R2 | DataForSEO top-10 is sufficient for content brief and gap analysis; top-20 upgrade path defined |
| Featured snippet detection | Yes | Yes | Yes | Yes | 4/4 | Yes — via SERP feature flags from DataForSEO | Table stakes; DataForSEO returns SERP features with every query |
| People Also Ask (PAA) extraction | Yes — used in brief | Yes | Yes | Yes | 4/4 | Yes — extract PAA questions for FAQ section generation | Table stakes; PAA questions are direct FAQ content inputs |
| AI Overview detection | Not documented | Not documented | Not documented | Not documented | 0/4 | Yes — detect AI Overview presence for target keyword | **Differentiator** — AI Overviews reduce organic CTR by 30-60%; critical for prioritisation |
| Knowledge panel detection | Not documented | Not documented | Not documented | Yes (partial) | 1/4 | Yes — flag knowledge panels (reduces organic click share) | Important for intent/click share analysis |
| Content type detection (blog/product/video) | Yes — Frase categorises results | Yes | Yes — content type shown | Yes | 4/4 | Yes — classify each result as: blog / product page / category / video / tool / news | Determines what content format to compete with |
| SERP snapshot persistence | Not documented | Not documented | "14-day refresh lag" (documented anti-pattern) | Not documented | 0/4 | Yes — store full SERP snapshot with timestamp | **Differentiator** — enables trend comparison over time; SurferSEO's 14-day lag is a known complaint |
| Rate limiting / cost controls | Not applicable (all SaaS) | — | — | — | — | Max 50 SERP requests/day for R1; configurable | DataForSEO charges per request; budget control required |

### Key Findings

- SurferSEO analysing 20+ results is the most thorough. But their 14-day data refresh lag is a documented user complaint. We match depth with R1 top-10 (expandable to 20) and snapshot on demand — no stale data.
- AI Overview detection is absent from all 4 competitors in their documented features. Given that AI Overviews now appear on 15-30% of Google searches in major markets (and growing), this is the most significant gap in the competitive landscape. A keyword where Google shows an AI Overview may have 30-60% fewer organic clicks — it should be deprioritised or targeted for AISO instead of traditional SEO.
- SERP snapshot persistence enables trend analysis (did featured snippet move? did AI Overview appear?). No competitor documents this capability. It feeds directly into E-005 Measurement.
- DataForSEO SERP API: confirmed at ~$0.0006 per request. At 50 SERP requests/day: ~$0.03/day, $1/month — well within budget. Planned for R1 month 3+. For R1 launch (month 1-2), use DataForSEO when available or fall back to free Google scraping at rate-limited volume.

### Sources

- Parent epic deep-dive: `specs/E-001/epic-status.md` § Competitive Deep-Dive
- Epic anti-pattern #7: "14-day data refresh lag (SurferSEO)"
- Epic table stakes #1: "SERP analysis (top 20+ results with entities, structure, word count)"
- Epic RAID A4: "SERP scraping at < 50 queries/day is within API ToS — DataForSEO confirmed"

---

## User Stories

### US-001: Top-10 SERP Result Scraping

**As a** pipeline, **I want** to fetch the top 10 organic search results for a target keyword, **so that** downstream features can analyse what already ranks and generate competitive content briefs.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

```
WHEN a keyword is submitted for SERP analysis
THE SYSTEM SHALL retrieve the top 10 organic results for that keyword
AND for each result SHALL capture:
  - position (1-10)
  - URL
  - page title
  - meta description (if available)
  - estimated word count (from page content if accessible, or from SERP snippet)
  - content type (blog | product_page | category_page | video | tool | news | other)
  - domain name
AND store the results as a SerpSnapshot record with a fetched_at timestamp
```

```
WHEN submitting SERP requests
THE SYSTEM SHALL rate-limit to a maximum of 50 requests per day (configurable via `SERP_DAILY_LIMIT` env var)
AND log each request to enforce the daily budget
AND halt with a clear error message if the daily limit is reached: "SERP daily limit reached (50/50). Next requests available after midnight UTC."
```

```
WHEN the SERP API returns no organic results (e.g., query triggers only SERP features)
THE SYSTEM SHALL store an empty results array with a flag: "no_organic_results"
AND continue pipeline execution with the flagged keyword
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | "FUE hair transplant", country=DE | 10 organic results with URL, title, content type, word count estimate; fetched_at timestamp |
| Video-heavy SERP | "hair transplant before after results" | Mix of blog (positions 1-4) and video (positions 5-8) content types detected |
| Mostly navigational SERP | "hairgenetix" (brand search) | Positions 1-3: brand website pages (navigational); positions 4-10: review/directory sites |
| Daily limit hit | 51st request in the same day | Error: "SERP daily limit reached (50/50). Next requests available after midnight UTC." |
| API unavailable | DataForSEO returns 503 | Retry 3x with exponential backoff; if all fail: mark keyword as "serp_unavailable", continue pipeline |
| Zero organic results | Query triggers only AI Overview | Empty organic results array, flagged "no_organic_results"; SERP features still captured |

---

### US-002: SERP Feature Detection

**As a** content strategist, **I want** to know which SERP features appear for a target keyword, **so that** I can prioritise keywords where organic results get the most click share and adjust strategy for keywords dominated by AI Overviews or featured snippets.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN SERP results are retrieved for a keyword (US-001)
THE SYSTEM SHALL detect and record the presence of the following SERP features:
  - ai_overview: boolean (AI Overview / SGE box present)
  - featured_snippet: boolean
  - people_also_ask: boolean + array of up to 5 PAA questions (string[])
  - knowledge_panel: boolean
  - image_pack: boolean
  - video_carousel: boolean
  - local_pack: boolean
  - shopping_results: boolean
AND store all feature flags in the SerpSnapshot record
```

```
WHEN an AI Overview is detected for a keyword
THE SYSTEM SHALL flag the keyword with an "ai_overview_detected" warning
AND include this flag in the keyword's priority score inputs for F-007 (Content Calendar)
```

```
WHEN People Also Ask questions are detected
THE SYSTEM SHALL extract the question text for each PAA result (up to 5)
AND store questions in the SerpSnapshot for use in content brief FAQ generation (E-002)
```

**Examples:**

| Keyword | Expected SERP Features Detected |
|---------|--------------------------------|
| "what is FUE hair transplant" | ai_overview: true (informational query, common AI Overview trigger), featured_snippet: true, people_also_ask: true (["How long does FUE take?", "Is FUE permanent?", ...]) |
| "hair transplant clinic Berlin" | local_pack: true, shopping_results: false, ai_overview: false |
| "hair transplant before after photos" | image_pack: true, video_carousel: true, featured_snippet: false |
| "hairgenetix reviews" | knowledge_panel: false (not a large brand), featured_snippet: false, people_also_ask: true |
| Purely organic SERP | "FUE vs DHI recovery comparison" | All feature flags: false; 10 organic results only |

---

### US-003: SERP Snapshot Persistence

**As a** pipeline operator, **I want** SERP snapshots stored with timestamps, **so that** I can compare SERP state over time and detect when AI Overviews appear or featured snippets change.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN a SERP analysis completes for a keyword
THE SYSTEM SHALL persist a SerpSnapshot record containing:
  - keyword text
  - language / country
  - fetched_at timestamp
  - organic_results: array of result objects (from US-001)
  - serp_features: feature flag object (from US-002)
  - result_count: integer
  - api_source: "dataforseo" | "google_scrape"
  - tenant_id
```

```
WHEN a SERP analysis is run again for the same keyword (on a subsequent pipeline run)
THE SYSTEM SHALL create a new SerpSnapshot record (not overwrite)
AND preserve all previous snapshots for trend comparison
AND expose a query: getLatestSerpSnapshot(keyword, language) that returns the most recent snapshot
```

```
WHEN downstream features (F-005, F-006) request SERP data
THE SYSTEM SHALL serve from the stored snapshot if it is less than 7 days old
AND trigger a fresh SERP fetch if the snapshot is older than 7 days (configurable via `SERP_CACHE_DAYS` env var)
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| First snapshot | "FUE hair transplant", DE | SerpSnapshot created with 10 results, feature flags, fetched_at = now |
| Second run (3 days later) | Same keyword | Snapshot is 3 days old (< 7 days); served from cache; no new API request |
| Second run (10 days later) | Same keyword | Snapshot is 10 days old (> 7 days); fresh fetch triggered; new snapshot created; both records retained |
| Trend comparison | "FUE hair transplant", 3 snapshots over 3 months | All 3 snapshots returned; caller can detect that ai_overview changed from false → true between snapshot 1 and 2 |
| Standalone mode | No database configured | Snapshots saved to `data/serp/{domain}/{language}/{keyword_slug}.json`; filename includes ISO timestamp |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN fetching SERP data for a single keyword THE SYSTEM SHALL complete within 10 seconds | p95 < 10s per keyword | Integration test with timer | No |
| 2 | **Scalability** | N/A — R1 targets max 50 SERP requests/day; not a high-throughput system | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN the SERP API returns an error THE SYSTEM SHALL retry with exponential backoff (max 3 retries, delays: 2s, 4s, 8s) AND mark keyword as "serp_unavailable" on persistent failure without halting the pipeline | 0 pipeline halts from single SERP API failure | Integration test with mocked API failure | Yes |
| 5 | **Security** | WHEN storing DataForSEO API credentials THE SYSTEM SHALL read from environment variables (`DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`), never hardcoded | No credentials in source code | grep scan in pre-commit hook | Yes |
| 6 | **Privacy** | N/A — SERP data is public; no PII processed | — | — | No |
| 7 | **Compliance / Regulatory** | WHEN using the Google free scraping fallback THE SYSTEM SHALL rate-limit to max 30 requests/day with 5-second delays between requests | Request counter in logs; delay enforced in code | Log audit + unit test for delay | No |
| 8 | **Interoperability** | WHEN outputting SERP data THE SYSTEM SHALL use the SerpSnapshot schema (defined in contracts/) AND the schema SHALL be consumed by F-005 and F-006 without transformation | Schema validation on every output | Unit test with Zod validation | Yes |
| 9 | **Portability** | WHEN running in standalone mode THE SYSTEM SHALL save snapshots to `data/serp/{domain}/{language}/{keyword_slug}-{timestamp}.json`; WHEN in platform mode THE SYSTEM SHALL use DatabasePort adapter | Both modes produce identical query results | Integration test both adapters | Yes |
| 10 | **Maintainability** | THE SYSTEM SHALL abstract the SERP data source behind a SerpDataSource interface so DataForSEO can be swapped for a different provider without changing pipeline logic | New provider addable in ≤ 1 day | Architecture review | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support a mock SerpDataSource returning fixture snapshot data | Tests run without API keys | CI run without DATAFORSEO credentials set | Yes |
| 12 | **Usability** | N/A — CLI only for R1; no interactive UI | — | — | No |
| 13 | **Localisation** | WHEN fetching SERP data THE SYSTEM SHALL pass the correct country/language parameters to the SERP API for each of the 9 Hairgenetix languages | Language-correct SERP results returned | Integration test with DE + NL keyword queries | No |
| 14 | **Monitoring** | WHEN SERP analysis completes for a batch THE SYSTEM SHALL log: keywords fetched, SERP features detected (counts per type), API calls made, daily request counter, cost estimate, duration | Structured JSON log entry | Log schema validation | No |
| 15 | **Auditability** | WHEN SERP requests are made THE SYSTEM SHALL log each request with: keyword, language, timestamp, api_source, cost (if known) to enable daily budget review | All requests logged before firing | Unit test verifies log before API call | No |
| 16 | **Disaster Recovery** | N/A — SERP snapshots are re-fetchable on demand; no DR required for R1 | — | — | No |
| 17 | **Capacity** | WHEN the daily SERP request limit (50) is reached THE SYSTEM SHALL queue remaining keywords for the next day AND notify the operator via CLI output: "[N] keywords queued — SERP limit reached for today" | No silent data loss | Unit test for queue behaviour at limit | No |
| 18 | **Cost** | WHEN using DataForSEO THE SYSTEM SHALL log estimated cost per request ($0.0006) AND alert if projected monthly cost exceeds $5 based on current daily run rate | Cost tracked and visible | Log audit | No |
| 19-35 | Remaining categories | N/A — R1 CLI tool | — | — | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | N/A — F-004 does not use LLM for data collection; LLM used only for content type classification of result pages (optional in R1) | — | — |
| Token economics | WHEN using LLM for content type classification of SERP results THE SYSTEM SHALL consume fewer than 5,000 tokens per SERP request (10 results × ~400 tokens each) | < $0.02 per keyword at Claude Haiku pricing | Token counter in logs |
| Hallucination rate | N/A — SERP data is deterministic from API; content type classification uses structured LLM output (enum) not free text | — | — |
| Model degradation detection | N/A — R1; content type detection accuracy reviewed during R1 validation | — | — |
| Prompt versioning | WHEN using LLM prompts for content type classification THE SYSTEM SHALL version prompts in `prompts/serp-content-type-v{N}.txt` | Prompt version in every LLM log entry | File structure check |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (inherited from epic Gate 1 decision); F-004 is a pipeline-internal feature with no direct human interaction |
| User personas and goals | [x] | F-004 serves the pipeline, not the store owner directly; downstream JTBD 1 + 2 (epic-status.md) depend on SERP data |
| N/A justification | [x] | No UI for R1 and no direct user interaction — F-004 is a data-collection feature consumed by F-005, F-006, F-007. |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. Auth deferred to platform integration (R2+). |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-004 behind `FEATURE_SERP_ANALYSIS` flag (env var); `SERP_DAILY_LIMIT` and `SERP_CACHE_DAYS` configurable |
| Config management | [x] | DataForSEO credentials via environment variables. Daily limit and cache TTL via env vars or config file. |
| N/A justification | [x] | No admin UI or billing for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | DataForSEO SERP API (login + password auth, ~$0.0006/request); Google scraping fallback (rate-limited, no auth) |
| API protocol | [x] | Internal: TypeScript module exports (commands/queries pattern). DataForSEO: REST + Basic Auth. |
| Resilience per dependency | [x] | DataForSEO: retry 3x with exponential backoff; graceful degradation to "serp_unavailable" flag. Google fallback: same retry, same degradation. |
| Rate limiting | [x] | Max 50 SERP requests/day (DataForSEO); max 30/day with 5s delays (Google fallback). Enforced by request counter. |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature. No migration. SerpSnapshot schema designed for forward-compatibility with platform DB. Note interim solution: Google scraping fallback for R1 months 1-2 before DataForSEO is configured — expiry: when DataForSEO is live; owner: Malcolm; sunset criteria: DataForSEO API key configured and validated. |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs: keywords fetched, SERP features detected, API requests made, daily counter, cost estimate, duration |
| Cost budget | [x] | DataForSEO: max $1.50/month at 50 requests/day. Google fallback: $0. Total F-004 cost: < $2/month for R1. |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 (top-10 SERP) | `[table-stakes]` | All 4 competitors analyse top 10-20 SERP results | 1-Features |
| US-001 (content type detection) | `[table-stakes]` | Frase, SEO.ai, SurferSEO all classify content type | 1-Features |
| US-002 (featured snippet) | `[table-stakes]` | All 4 competitors detect featured snippet | 1-Features |
| US-002 (PAA extraction) | `[table-stakes]` | All 4 competitors use PAA for brief generation | 2-Workflows |
| US-002 (AI Overview detection) | `[differentiator]` | 0/4 competitors document AI Overview detection; AI Overviews directly reduce organic CTR | 1-Features |
| US-002 (knowledge panel) | `[competitor-parity]` | Semrush ContentShake detects knowledge panels (partial) | 1-Features |
| US-003 (snapshot persistence) | `[differentiator]` | No competitor documents SERP snapshot storage with historical comparison; SurferSEO's 14-day refresh lag is an explicit anti-pattern (anti-pattern #7) | 5-Data |

## Out of Scope

- Full page content extraction and word count (belongs in F-005 Competitor Content Analysis — F-004 captures URL and snippet only)
- SERP position tracking over time for our own domain (belongs in E-005 Measurement)
- Mobile SERP analysis (desktop SERP is sufficient for R1 content strategy; mobile parity deferred to R2+)
- Video SERP analysis (YouTube-specific SERP features — deferred to R2+)
- News carousel analysis (not relevant for evergreen content strategy)

## Open Questions

- [ ] Should SERP snapshots older than 90 days be archived or deleted? (Proposed: retain indefinitely for R1 — data volume is small at < 50 snapshots/day; add retention policy in R2+ with configurable TTL)
- [ ] When the daily SERP limit is reached mid-pipeline-run, should the pipeline halt or continue with the remaining features that don't require fresh SERP data? (Proposed: continue — mark affected keywords as "serp_pending", use cached snapshots for others, queue remainder for next day)
- [ ] DataForSEO requires a $50 deposit for the first month (R1 month 3). For R1 months 1-2, is free Google scraping acceptable as the sole SERP source? (Proposed: yes — Malcolm to confirm; rate limits are conservative enough to avoid IP blocks per epic RAID A4)

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 Keyword Research | Internal | Not started | US-001 — SERP analysis runs on keywords from F-001 |
| DataForSEO API credentials | External | Deferred to R1 month 3 ($50 deposit) | US-001 primary data source; Google fallback used until configured |
| SerpSnapshot schema (contracts/) | Internal | To be defined | US-001, US-002, US-003 output; F-005 + F-006 input |
| F-005 Competitor Content Analysis | Internal | Not started | Consumes SerpSnapshot records — dependency direction: F-004 → F-005 |
| F-006 Content Gap Identification | Internal | Not started | Consumes SerpSnapshot records — dependency direction: F-004 → F-006 |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | DataForSEO SERP API returns AI Overview detection flag in standard response | Medium | Verify during DataForSEO integration (R1 month 3); if not available natively, use HTML response parsing as fallback |
| A2 | 50 SERP requests/day is sufficient for R1 pipeline runs (covering target keyword set for Hairgenetix) | High | Hairgenetix target keyword set estimated at 20-50 priority keywords for initial calendar; rate matches |
| A3 | Google free scraping at < 30 requests/day with 5-second delays will not trigger IP blocks | High | Validated in epic RAID A4; conservative limit confirmed |
| A4 | SerpSnapshot schema with top-10 results per keyword is sufficient for F-005 competitor content analysis | Medium | Validate during F-005 build; if top-20 needed, DataForSEO supports it — configurable upgrade |
| A5 | 7-day snapshot cache TTL balances freshness vs API cost | Medium | Validate during R1 pilot; SERP results for evergreen content keywords change slowly; adjust if keyword rankings are more volatile |
