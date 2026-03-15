---
id: "FTR-SEO-004"
title: "Test Plan: SERP Analysis"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 40
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-004: SERP Analysis — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: Top-10 SERP Result Scraping

**ATS-001: Happy path — standard SERP retrieval**

```
GIVEN a keyword "FUE hair transplant" and country=DE
WHEN SERP analysis runs
THEN 10 organic results are returned
AND each result includes: position (1-10), URL, page title, meta description, estimated word count, content type, domain name
AND a SerpSnapshot record is created with fetched_at timestamp
```

**ATS-002: Video-heavy SERP detected**

```
GIVEN a keyword "hair transplant before after results"
WHEN SERP analysis runs
THEN content types include a mix of "blog" and "video" entries
AND video results are classified as content_type="video"
```

**ATS-003: Navigational SERP**

```
GIVEN a brand keyword "hairgenetix"
WHEN SERP analysis runs
THEN positions 1-3 are classified as brand website pages
AND positions 4-10 include review/directory sites
```

**ATS-004: Daily rate limit enforcement**

```
GIVEN 50 SERP requests have already been made today
WHEN a 51st request is attempted
THEN the system returns error: "SERP daily limit reached (50/50). Next requests available after midnight UTC."
AND no API call is made
```

**ATS-005: API failure with retry and graceful degradation**

```
GIVEN DataForSEO returns HTTP 503
WHEN the system retries 3x with exponential backoff (2s, 4s, 8s)
AND all retries fail
THEN the keyword is marked "serp_unavailable"
AND the pipeline continues with remaining keywords
```

**ATS-006: Zero organic results SERP**

```
GIVEN a query that triggers only AI Overview with no organic results
WHEN SERP analysis runs
THEN organic_results is an empty array
AND flagged "no_organic_results"
AND SERP features are still captured
```

**ATS-007: Configurable daily limit**

```
GIVEN SERP_DAILY_LIMIT env var set to 25
WHEN 26 requests are attempted
THEN the 26th is blocked with the daily limit message
```

### US-002: SERP Feature Detection

**ATS-008: AI Overview detected**

```
GIVEN a keyword "what is FUE hair transplant" (informational, common AI Overview trigger)
WHEN SERP feature detection runs
THEN ai_overview is true
AND the keyword is flagged with "ai_overview_detected" warning
```

**ATS-009: Featured snippet detected**

```
GIVEN a keyword where Google shows a featured snippet
WHEN SERP feature detection runs
THEN featured_snippet is true
```

**ATS-010: People Also Ask extraction**

```
GIVEN a keyword with PAA results
WHEN SERP feature detection runs
THEN people_also_ask is true
AND up to 5 PAA questions are extracted as strings
```

**ATS-011: Local pack detected**

```
GIVEN a keyword "hair transplant clinic Berlin"
WHEN SERP feature detection runs
THEN local_pack is true
```

**ATS-012: Image pack and video carousel**

```
GIVEN a keyword "hair transplant before after photos"
WHEN SERP feature detection runs
THEN image_pack is true
AND video_carousel may be true (depending on SERP state)
```

**ATS-013: Purely organic SERP — no features**

```
GIVEN a keyword "FUE vs DHI recovery comparison" with no SERP features
WHEN SERP feature detection runs
THEN all feature flags are false
AND 10 organic results are present
```

**ATS-014: AI Overview warning propagates to F-007**

```
GIVEN a keyword with ai_overview_detected=true
WHEN F-007 priority scoring uses this keyword
THEN the AI Overview flag is included as a scoring input
```

### US-003: SERP Snapshot Persistence

**ATS-015: First snapshot created**

```
GIVEN a keyword "FUE hair transplant" in DE with no prior snapshot
WHEN SERP analysis completes
THEN a SerpSnapshot is created with: keyword, language, fetched_at, organic_results, serp_features, result_count, api_source, tenant_id
```

**ATS-016: Cache hit — snapshot within 7 days**

```
GIVEN a snapshot for "FUE hair transplant" created 3 days ago
WHEN a downstream feature requests SERP data
THEN the cached snapshot is served
AND no new API request is made
```

**ATS-017: Cache miss — snapshot older than 7 days**

```
GIVEN a snapshot for "FUE hair transplant" created 10 days ago
WHEN a downstream feature requests SERP data
THEN a fresh SERP fetch is triggered
AND a new snapshot is created
AND the previous snapshot is preserved (not overwritten)
```

**ATS-018: Trend comparison across multiple snapshots**

```
GIVEN 3 snapshots for "FUE hair transplant" taken over 3 months
WHEN historical snapshots are queried
THEN all 3 are returned
AND the caller can detect that ai_overview changed from false to true between snapshots
```

**ATS-019: Standalone file mode**

```
GIVEN standalone mode with no database
WHEN SERP analysis completes
THEN snapshots are saved to data/serp/{domain}/{language}/{keyword_slug}.json
AND filename includes ISO timestamp
```

**ATS-020: Configurable cache TTL**

```
GIVEN SERP_CACHE_DAYS env var set to 14
WHEN a snapshot is 10 days old
THEN the cached snapshot is served (within 14-day TTL)
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: DataForSEO API round-trip**

```
GIVEN valid DataForSEO credentials (login + password)
WHEN a SERP request is submitted for keyword "FUE hair transplant", country=DE
THEN a valid response is returned with organic results and SERP features
AND the response matches the SerpSnapshot schema
```

**INT-002: Google scraping fallback**

```
GIVEN DataForSEO is not configured
WHEN SERP analysis runs using the Google scraping fallback
THEN rate limiting is enforced (max 30/day, 5s delays)
AND results are returned in SerpSnapshot format
```

**INT-003: F-001 output → F-004 input pipeline**

```
GIVEN F-001 has produced a keyword list
WHEN F-004 receives keywords for SERP analysis
THEN all required fields (keyword text, language, country) are present
```

**INT-004: F-004 output → F-005 input pipeline**

```
GIVEN F-004 has produced SerpSnapshot records
WHEN F-005 (Competitor Content Analysis) consumes them
THEN competitor URLs from organic_results are available for download
AND schema validation passes
```

**INT-005: F-004 output → F-006 input pipeline**

```
GIVEN F-004 has produced SerpSnapshot records
WHEN F-006 (Content Gap Identification) consumes them
THEN ranking positions and competitor domains are available for gap matrix
```

**INT-006: Daily request counter persistence**

```
GIVEN 30 requests made today
WHEN the process is restarted
THEN the daily counter reflects 30 (not reset to 0)
AND the remaining budget is correctly calculated
```

**INT-007: Credential security**

```
GIVEN DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD are set as environment variables
WHEN the module initialises
THEN credentials are read from environment
AND no credentials appear in source code, logs, or SERP output
```

**INT-008: Database vs JSON storage parity**

```
GIVEN the same SERP analysis run
WHEN executed in standalone mode (JSON) and platform mode (DB)
THEN getLatestSerpSnapshot() returns identical results from both
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | Position range | Every organic result position is 1-10 inclusive |
| PI-002 | URL non-empty | Every organic result has a non-empty URL string |
| PI-003 | Content type valid | content_type is one of: "blog", "product_page", "category_page", "video", "tool", "news", "other" |
| PI-004 | Feature flags boolean | All SERP feature fields (ai_overview, featured_snippet, etc.) are boolean |
| PI-005 | PAA array limit | people_also_ask questions array has 0-5 elements |
| PI-006 | Timestamp present | Every SerpSnapshot has a non-null fetched_at ISO 8601 timestamp |
| PI-007 | Tenant isolation | Every SerpSnapshot has a non-null tenant_id |
| PI-008 | API source valid | api_source is one of: "dataforseo", "google_scrape" |
| PI-009 | Daily limit respected | Total SERP requests per UTC day never exceed SERP_DAILY_LIMIT |
| PI-010 | Result count matches | result_count equals the length of organic_results array |
| PI-011 | Snapshots append-only | Subsequent SERP fetches for the same keyword create new records, never overwrite |
| PI-012 | Word count non-negative | estimated word_count is always >= 0 |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 to ATS-007 | Integration | Requires SERP API call (DataForSEO or mock) |
| ATS-008 to ATS-014 | Integration | Requires SERP API response with feature flags |
| ATS-015 to ATS-020 | Integration | Requires storage layer for snapshot persistence |
| INT-001 to INT-008 | Integration | External API and storage boundaries |
| PI-001 to PI-012 | Property | Fast-check on SerpSnapshot schema constraints |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
