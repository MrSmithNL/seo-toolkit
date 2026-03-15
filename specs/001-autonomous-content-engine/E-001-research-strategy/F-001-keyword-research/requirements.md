---
id: "FTR-SEO-001"
type: feature
title: "Keyword Research / Gap Analysis"
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

# F-001: Keyword Research / Gap Analysis — Requirements

## Problem Statement

Store owners need to know which keywords to target for their content. Without systematic keyword research, content is created blind — targeting terms with no search volume, ignoring competitor gaps, or duplicating existing coverage. Manual keyword research via Claude + skills takes 30-60 minutes per topic and produces no persistent data.

**Who has this problem:** E-commerce store owners (Hairgenetix first) who need SEO/AISO content but lack time or expertise to do keyword research.

**Cost of inaction:** Content targets wrong keywords. Articles get no traffic. Pipeline is keyword-blind from step one.

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors) and Keyword Data Sources Analysis (441 lines).

### Competitor Analysis (for this feature)

| Feature/Capability | Frase | SEO.ai | SurferSEO | Semrush | Prevalence | Our Approach | Rationale |
|-------------------|-------|--------|-----------|---------|:----------:|-------------|-----------|
| Seed keyword expansion | Auto-expand from URL or keyword | Auto from URL (black box) | Manual keyword entry | Massive keyword DB + auto-suggest | 4/4 | Auto-expand from URL + optional seeds | Match Frase/Semrush UX; URL-first for store owners |
| Keyword volume data | Via Semrush/Ahrefs integration ($35 add-on) | Built-in (undisclosed source) | Built-in | Built-in (9B keyword DB) | 4/4 | Keywords Everywhere API ($10) | Approved by Malcolm; best ROI for R1 |
| Keyword difficulty | Via integration | Built-in | SurferSEO custom score | KD% + Personal KD% | 4/4 | Heuristic from autocomplete depth + volume (R1), DataForSEO difficulty (R1 month 3+) | Free heuristic for MVP; paid upgrade path defined |
| Multi-language keywords | Not documented | Not documented | Limited | Full (140+ DBs) | 1/4 | 9-language simultaneous via Keywords Everywhere `country` param | **Differentiator** — no competitor handles 9-language research |
| Keyword gap vs competitors | Not in research feature | Not available | Not in research | Full gap analysis | 1/4 | URL-based gap analysis via GSC + SERP comparison | Simpler approach for R1; no need for competitor keyword DB |
| Related keywords / long-tail | Auto-suggest from SERP | Auto-generated | Manual exploration | Keyword Magic Tool | 4/4 | Google Autocomplete API + LLM semantic expansion | Free, multilingual, unlimited |
| Search volume trends | Not in research | Not available | Historical chart | 12-month trend | 2/4 | Keywords Everywhere 12-month trend data | Included in $10 credit purchase |

### Key Findings

- **Best-of-breed for keyword research UX:** Semrush (deepest data) and Frase (cleanest workflow). Semrush's "Personal KD%" is unique — adjusts difficulty based on your site's authority. Worth adding in R2+.
- **User complaints:** Frase's keyword data is a $35/mo add-on (top complaint on G2). SurferSEO requires manual keyword entry (no URL-based discovery). SEO.ai gives no transparency on keyword selection.
- **Our platform advantage:** 9-language simultaneous research (no competitor does this), transparent scoring (show the "why"), persistent keyword database that grows over time.

### Sources

- Parent epic deep-dive: `specs/E-001/epic-status.md` § Competitive Deep-Dive
- Keyword data analysis: `specs/E-001/research/keyword-data-sources-analysis.md`

---

## User Stories

### US-001: Seed Keyword Discovery from URL

**As a** store owner, **I want** to provide my website URL and get a list of relevant keyword suggestions, **so that** I can discover what topics I should write about without SEO expertise.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

```
WHEN a user provides a website URL
THE SYSTEM SHALL crawl the site's sitemap or top-level pages (max 50 pages)
AND extract existing content topics, product categories, and meta keywords
AND generate a seed keyword list of at least 20 keywords
AND each keyword SHALL include the source page URL it was derived from
```

```
WHEN a user provides a website URL AND optional seed keywords
THE SYSTEM SHALL use the seed keywords as additional input alongside URL-derived topics
AND expand the combined seed list via Google Autocomplete API
AND return at least 50 keyword suggestions per language requested
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | `https://hairgenetix.com` + no seeds | 20+ seeds from sitemap (e.g., "hair transplant", "FUE", "hair loss treatment"), expanded to 50+ via Autocomplete |
| With seeds | `https://hairgenetix.com` + seeds: ["hair growth serum", "post-transplant care"] | Seeds merged with URL-derived topics, expanded to 100+ keywords |
| Small site (few pages) | `https://example.com` (3 pages) | At least 10 seeds from available content, expanded via Autocomplete to 30+ |
| Site with no sitemap | URL with no `sitemap.xml` | Falls back to crawling homepage + linked pages (max 50), still produces seeds |
| Invalid URL | `https://doesnotexist.invalid` | Error: "Could not reach website. Check the URL and try again." |

---

### US-002: Keyword Volume & Metrics Enrichment

**As a** store owner, **I want** each keyword to include search volume, CPC, and trend data, **so that** I can prioritise keywords by real demand rather than guessing.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN keywords have been discovered (from US-001)
THE SYSTEM SHALL enrich each keyword with monthly search volume via Keywords Everywhere API
AND include CPC (cost per click) data
AND include 12-month trend data (array of 12 monthly values)
AND tag the country/language for each data point
```

```
WHEN enriching keywords for multiple languages
THE SYSTEM SHALL query Keywords Everywhere separately for each language/country combination
AND store per-language volume data (the same keyword may have different volume in DE vs FR)
AND batch requests (up to 100 keywords per API call) to minimise API usage
```

```
WHEN the Keywords Everywhere API returns zero volume for a keyword
THE SYSTEM SHALL retain the keyword but flag it as "low/zero volume"
AND NOT automatically discard it (it may still be valuable for AISO/long-tail)
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | "hair transplant", country=DE | volume: 18100, cpc: 2.45, trend: [14800, 15200, ..., 18100] |
| Multi-language | "hair transplant", countries=[DE, FR, NL] | 3 records: DE=18100, FR=12500, NL=3200 |
| Zero volume keyword | "hair transplant week 47 recovery photos" | volume: 0, flagged: "low/zero volume", retained |
| API error | Keywords Everywhere returns 429 | Retry with exponential backoff (max 3 retries), then mark as "volume unavailable" |
| Batch efficiency | 150 keywords, 1 language | 2 API calls (100 + 50), not 150 individual calls |

---

### US-003: Keyword Difficulty Estimation

**As a** store owner, **I want** a difficulty score for each keyword, **so that** I don't waste time writing articles for keywords I can't realistically rank for.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN keywords have been enriched with volume data (from US-002)
THE SYSTEM SHALL estimate keyword difficulty on a 0-100 scale
AND use the following heuristic for R1:
  - Google Autocomplete depth (more autocomplete variants = more established topic = higher difficulty)
  - Volume bracket (higher volume generally = higher difficulty)
  - LLM assessment of top-ranking domain authority (Claude evaluates "are the top results from major sites or niche blogs?")
AND flag the difficulty as "estimated (heuristic)" to distinguish from API-sourced scores
```

```
WHEN DataForSEO is available (R1 month 3+)
THE SYSTEM SHALL use DataForSEO keyword difficulty scores instead of heuristic
AND flag as "API-sourced (DataForSEO)"
AND the data source interface SHALL be abstracted so the source can be swapped without changing pipeline logic
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Low difficulty | "hair transplant recovery week 3 photos" (niche, low volume) | difficulty: 15, source: "heuristic", rationale: "low autocomplete depth, niche topic" |
| High difficulty | "hair transplant" (head term, massive volume) | difficulty: 85, source: "heuristic", rationale: "high volume, dominated by medical sites" |
| Medium difficulty | "FUE hair transplant cost Germany" (specific, moderate volume) | difficulty: 45, source: "heuristic" |
| DataForSEO available | Same keyword, DataForSEO configured | difficulty: 42, source: "DataForSEO", rationale: null (API score is authoritative) |

---

### US-004: Keyword Gap Analysis vs Competitors

**As a** store owner, **I want** to see which keywords my competitors rank for that I don't, **so that** I can identify content opportunities I'm missing.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

```
WHEN a user provides their website URL AND at least one competitor URL
THE SYSTEM SHALL compare the user's keyword coverage against competitors
AND identify "gap keywords" — terms competitors rank for (top 50) that the user does not
AND for each gap keyword, include: the competitor URL that ranks, estimated position, and volume
```

```
WHEN Google Search Console data is available for the user's site
THE SYSTEM SHALL use GSC query data as the authoritative source of "keywords we rank for"
AND compare against competitor coverage derived from SERP analysis (F-004)
```

```
WHEN GSC data is NOT available
THE SYSTEM SHALL fall back to SERP-based discovery:
  - For each expanded keyword (US-001), check if the user's domain appears in top 50 results
  - Keywords where user's domain is absent but competitor domains appear = gap keywords
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path (GSC available) | hairgenetix.com vs hairtransplantclinic.de | Gap: "FUE vs DHI comparison" (competitor ranks #7, we don't rank), volume: 2400 |
| No GSC | hairgenetix.com vs competitor.com, no GSC connected | SERP-based gap: keyword checked against top 50, user domain not found, competitor at #12 |
| No gaps found | hairgenetix.com vs tiny-competitor.com | "No significant gaps found. Your site covers more keywords than this competitor." |
| Multiple competitors | hairgenetix.com vs [comp1.com, comp2.com, comp3.com] | Unified gap list, deduplicated, showing which competitor(s) rank for each gap keyword |

---

### US-005: Keyword Output & Persistence

**As a** pipeline operator, **I want** keyword research results saved in a structured format, **so that** downstream pipeline stages (clustering, calendar, content creation) can consume them.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN keyword research completes for a domain
THE SYSTEM SHALL persist all keyword data to the database (or JSON file in standalone mode)
AND each keyword record SHALL include:
  - keyword text
  - language/country
  - monthly volume
  - CPC
  - 12-month trend
  - difficulty score + source
  - intent classification (from F-003)
  - gap status (own_keyword | competitor_gap | new_opportunity)
  - source URLs (where discovered)
  - discovered_at timestamp
  - tenant_id
```

```
WHEN keyword research is run again for the same domain
THE SYSTEM SHALL update existing records (not create duplicates)
AND preserve historical data (previous volume, previous difficulty)
AND flag keywords that have changed significantly (volume delta > 30%)
```

```
WHEN keyword data is requested by downstream features (F-002, F-003, F-006, F-007)
THE SYSTEM SHALL expose a query interface:
  - getKeywordsByDomain(domain, language?, minVolume?, maxDifficulty?)
  - getGapKeywords(domain, competitors[])
  - getKeywordTrends(keyword, language, months)
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| First run | hairgenetix.com, DE | 150 keyword records saved with all fields populated |
| Second run (1 month later) | hairgenetix.com, DE | 150 records updated; 12 flagged as "volume changed >30%"; 8 new keywords added |
| Query by downstream | getKeywordsByDomain("hairgenetix.com", "DE", minVolume=100) | Filtered list of keywords with volume >= 100 in German market |
| Standalone mode | No database configured | Keywords saved to `data/keywords/{domain}/{language}.json` |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN processing a domain with 50 seed keywords THE SYSTEM SHALL complete keyword research WITHIN 5 minutes for a single language | p95 < 5 min | Integration test with timer | No |
| 2 | **Scalability** | N/A — R1 targets 1-5 domains, not thousands | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN an external API call fails THE SYSTEM SHALL retry with exponential backoff (max 3 retries) AND continue with remaining keywords | 0 data loss from transient API errors | Integration test with mock API failures | Yes |
| 5 | **Security** | WHEN storing API keys (Keywords Everywhere, DataForSEO) THE SYSTEM SHALL read from environment variables or config file, never hardcoded | No API keys in source code | grep scan in pre-commit hook | Yes |
| 6 | **Privacy** | N/A — keyword data is public; no PII processed | — | — | No |
| 7 | **Compliance** | WHEN scraping Google Autocomplete THE SYSTEM SHALL rate-limit to max 100 requests/day with 2-second delays | Request counter in logs | Log audit | No |
| 8 | **Interoperability** | WHEN outputting keyword data THE SYSTEM SHALL use the KeywordRecord schema (defined in contracts/) | Schema validation on every output | Unit test with Zod validation | Yes |
| 9 | **Portability** | WHEN running in standalone mode THE SYSTEM SHALL use JSON file storage; WHEN running in platform mode THE SYSTEM SHALL use DatabasePort adapter | Both modes produce identical query results | Integration test both adapters | Yes |
| 10 | **Maintainability** | THE SYSTEM SHALL abstract keyword data sources behind a KeywordDataSource interface | New sources addable without pipeline changes | Architecture review | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support a mock KeywordDataSource that returns fixture data | Tests run without API keys | Unit test suite runs offline | Yes |
| 12 | **Usability** | N/A for R1 — CLI only, no interactive UI | — | — | No |
| 13 | **Localisation** | WHEN processing multiple languages THE SYSTEM SHALL support all 9 Hairgenetix languages (DE, FR, NL, ES, IT, PT, PL, TR, EN) | All 9 languages return results | Integration test per language | No |
| 14 | **Monitoring** | WHEN keyword research completes THE SYSTEM SHALL log: keywords found, API calls made, credits consumed, duration | Structured JSON log entry | Log schema validation | No |
| 15-35 | Remaining categories | N/A — R1 CLI tool; enterprise NFRs apply from R2 (platform integration) | — | — | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN using LLM for difficulty estimation THE SYSTEM SHALL complete within 30 seconds per batch of 50 keywords | p95 < 30s | Integration test with timer |
| Token economics | WHEN using LLM for keyword expansion/difficulty THE SYSTEM SHALL consume < 10K tokens per domain research run | < $0.10 per domain at Claude pricing | Token counter in logs |
| Hallucination rate | WHEN LLM estimates keyword difficulty THE SYSTEM SHALL flag all estimates as "heuristic" and include rationale text | 100% of heuristic scores flagged | Unit test checks flag |
| Prompt versioning | WHEN using LLM prompts for keyword tasks THE SYSTEM SHALL version prompts in source code (not inline strings) | All prompts in `prompts/` directory | File structure check |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (approved at Gate 1) |
| User personas and goals | [x] | JTBD 1-4 in epic-status.md |
| N/A justification | [x] | No UI for R1. CLI outputs structured JSON/Markdown. Dashboard in E-006 (R2+). All competitors have web UI; CLI justified for internal tool validation (Gate 1 approved). |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. Auth deferred to platform integration (R2+). Config-file tenant context for standalone mode. |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-001 behind `FEATURE_KEYWORD_RESEARCH` flag (env var in standalone, platform flags in R2+) |
| Config management | [x] | API keys via environment variables or `.env` file. Config schema validated at startup. |
| N/A justification | [x] | No admin UI, billing, or reporting for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | Google Autocomplete (free, no auth), Keywords Everywhere API (API key), Google Search Console API (OAuth), DataForSEO (API key, R1 month 3+) |
| API protocol | [x] | Internal: TypeScript module exports (commands/queries pattern). External consumers: JSON file output (R1), REST API (R2+). |
| Resilience per dependency | [x] | All external APIs: retry 3x with exponential backoff, circuit breaker after 5 consecutive failures, graceful degradation (continue with partial data) |
| Rate limiting | [x] | Google Autocomplete: 100 req/day, 2s delay. Keywords Everywhere: 1 req/s, 100 keywords/batch. GSC: 1200 req/min (generous). |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature — no migration. Data format designed for forward-compatibility with platform DB. |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs: keywords found, API calls, credits consumed, errors, duration |
| Cost budget | [x] | Keywords Everywhere: $10 deposit covers 100K lookups (~2.5 years at R1 scale). LLM: < $0.10 per domain run. |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. Added at platform integration (R2+). |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 | `[table-stakes]` | All 4 competitors auto-expand from URL or keyword | 1-Features |
| US-002 | `[table-stakes]` | 4/4 competitors provide volume data | 1-Features |
| US-002 (multi-lang) | `[differentiator]` | 0/4 competitors handle 9-language simultaneous | 1-Features |
| US-003 | `[table-stakes]` | 4/4 provide difficulty scores | 1-Features |
| US-003 (heuristic) | `[anti-pattern]` | Frase paywalls keyword data at $35/mo | 2-Workflows |
| US-004 | `[table-stakes]` | Semrush full gap analysis; others partial or absent | 1-Features |
| US-005 | `[differentiator]` | No competitor exposes persistent keyword DB with query interface | 5-Data |

## Out of Scope

- Backlink analysis (belongs in E-003 or separate epic)
- Keyword rank tracking over time (belongs in E-005 Measurement)
- Paid keyword / Google Ads analysis (not needed for organic content pipeline)
- Real-time SERP monitoring (belongs in E-005)
- Competitor backlink profiles (belongs in separate capability)

## Open Questions

- [x] Which keyword data source? → Keywords Everywhere ($10), approved by Malcolm
- [x] Is GSC connected for Hairgenetix? → Yes, confirmed by Malcolm
- [ ] What is the minimum keyword count to consider research "complete" for a domain? (Proposed: 50 keywords per language)
- [ ] Should zero-volume keywords be included in the content calendar or filtered out? (Proposed: include but deprioritise — AISO value may exist even without search volume)

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| Keywords Everywhere API key | External | Needs setup ($10 purchase) | US-002 volume data |
| Google Search Console OAuth | External | Connected (confirmed) | US-004 gap analysis accuracy |
| DataForSEO API key | External | Deferred to R1 month 3 | US-003 difficulty upgrade |
| F-003 Intent Classification | Internal | Not started | US-005 intent field |
| F-004 SERP Analysis | Internal | Not started | US-004 competitor coverage data |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | Keywords Everywhere API supports all 9 Hairgenetix languages including Turkish | High | Test API with TR country code before pipeline build |
| A2 | Google Autocomplete at <100 req/day with 2s delays will not trigger IP blocks | High | Validated by keyword data analysis research |
| A3 | LLM difficulty heuristic is accurate enough for R1 content targeting | Medium | Compare heuristic vs DataForSEO scores for 50 keywords when DataForSEO is added |
| A4 | 50 seed pages from sitemap is sufficient for keyword discovery | Medium | Test with Hairgenetix sitemap (actual page count) |
