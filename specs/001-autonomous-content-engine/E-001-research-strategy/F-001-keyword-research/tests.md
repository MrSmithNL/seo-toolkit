---
id: "FTR-SEO-001"
title: "Test Plan: Keyword Research / Gap Analysis"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 42
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-001: Keyword Research / Gap Analysis — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: Seed Keyword Discovery from URL

**ATS-001: Happy path — URL-only discovery**

```
GIVEN a valid website URL "https://hairgenetix.com" with a sitemap containing 30 pages
WHEN the user submits the URL with no seed keywords
THEN the system returns at least 20 seed keywords derived from the sitemap
AND each keyword includes the source page URL it was derived from
AND seeds are expanded to at least 50 keyword suggestions via Google Autocomplete
```

**ATS-002: URL with optional seed keywords**

```
GIVEN a valid website URL "https://hairgenetix.com"
AND seed keywords ["hair growth serum", "post-transplant care"]
WHEN the user submits both
THEN the seed keywords are merged with URL-derived topics
AND the combined list is expanded to at least 100 keyword suggestions
AND original seeds appear in the output tagged as "user-provided"
```

**ATS-003: Small site with few pages**

```
GIVEN a website URL with only 3 crawlable pages
WHEN the user submits the URL
THEN at least 10 seeds are extracted from available content
AND Autocomplete expansion produces at least 30 keyword suggestions
```

**ATS-004: Site with no sitemap**

```
GIVEN a website URL that returns 404 for /sitemap.xml
WHEN the user submits the URL
THEN the system falls back to crawling homepage + linked pages (max 50)
AND still produces a seed keyword list
```

**ATS-005: Invalid URL**

```
GIVEN an unreachable URL "https://doesnotexist.invalid"
WHEN the user submits the URL
THEN the system returns an error: "Could not reach website. Check the URL and try again."
AND no keywords are generated
```

### US-002: Keyword Volume & Metrics Enrichment

**ATS-006: Happy path — single language enrichment**

```
GIVEN a keyword "hair transplant" and country=DE
WHEN enrichment runs via Keywords Everywhere API
THEN the keyword record includes volume (e.g. 18100), CPC (e.g. 2.45), and a 12-element trend array
AND the country/language tag is set to DE
```

**ATS-007: Multi-language enrichment**

```
GIVEN a keyword "hair transplant" and countries=[DE, FR, NL]
WHEN enrichment runs
THEN 3 separate volume records are created (DE=18100, FR=12500, NL=3200)
AND each record has the correct country tag
```

**ATS-008: Zero volume keyword retained**

```
GIVEN a keyword "hair transplant week 47 recovery photos"
WHEN Keywords Everywhere returns volume=0
THEN the keyword is retained with volume=0
AND flagged as "low/zero volume"
AND is NOT automatically discarded
```

**ATS-009: API rate limiting — batch efficiency**

```
GIVEN 150 keywords for 1 language
WHEN enrichment runs
THEN exactly 2 API calls are made (batch of 100 + batch of 50)
AND NOT 150 individual calls
```

**ATS-010: API error with retry**

```
GIVEN Keywords Everywhere returns HTTP 429
WHEN the system retries with exponential backoff (max 3 retries)
AND all retries fail
THEN the keyword is marked "volume unavailable"
AND the pipeline continues with remaining keywords
```

### US-003: Keyword Difficulty Estimation

**ATS-011: Low difficulty heuristic**

```
GIVEN a niche keyword "hair transplant recovery week 3 photos" with low volume
WHEN difficulty estimation runs using the R1 heuristic
THEN difficulty score is approximately 15 (0-100 scale)
AND source is "heuristic"
AND rationale mentions "low autocomplete depth" and "niche topic"
```

**ATS-012: High difficulty heuristic**

```
GIVEN a head term "hair transplant" with massive volume
WHEN difficulty estimation runs
THEN difficulty score is approximately 85
AND source is "heuristic"
AND rationale mentions "high volume" and "dominated by medical sites"
```

**ATS-013: DataForSEO source swap**

```
GIVEN DataForSEO is configured
WHEN difficulty estimation runs for "FUE hair transplant cost Germany"
THEN the score is sourced from DataForSEO (e.g. difficulty=42)
AND source is "DataForSEO"
AND rationale is null (API score is authoritative)
```

### US-004: Keyword Gap Analysis vs Competitors

**ATS-014: Happy path with GSC**

```
GIVEN hairgenetix.com vs hairtransplantclinic.de
AND GSC data is available for hairgenetix.com
WHEN gap analysis runs
THEN gap keywords are identified where competitors rank in top 50 but user domain does not
AND each gap keyword includes: competitor URL, estimated position, and volume
```

**ATS-015: No GSC fallback**

```
GIVEN hairgenetix.com vs competitor.com with no GSC connected
WHEN gap analysis runs
THEN SERP-based discovery checks top 50 results for user domain presence
AND keywords where user domain is absent but competitor appears are classified as gaps
```

**ATS-016: No gaps found**

```
GIVEN hairgenetix.com vs a tiny competitor with limited rankings
WHEN gap analysis runs and no significant gaps exist
THEN the system returns "No significant gaps found."
```

**ATS-017: Multiple competitors**

```
GIVEN hairgenetix.com vs [comp1.com, comp2.com, comp3.com]
WHEN gap analysis runs
THEN a unified gap list is produced, deduplicated
AND each gap keyword shows which competitor(s) rank for it
```

### US-005: Keyword Output & Persistence

**ATS-018: First run persistence**

```
GIVEN a first-time keyword research run for hairgenetix.com in DE
WHEN research completes with 150 keywords
THEN all 150 records are saved with all required fields (keyword text, language, volume, CPC, trend, difficulty, intent, gap status, source URLs, discovered_at, tenant_id)
```

**ATS-019: Second run deduplication**

```
GIVEN keyword research was previously run for hairgenetix.com in DE
WHEN research runs again 1 month later
THEN existing records are updated (not duplicated)
AND historical data is preserved
AND keywords with volume delta > 30% are flagged
```

**ATS-020: Downstream query interface**

```
GIVEN 150 keyword records for hairgenetix.com
WHEN getKeywordsByDomain("hairgenetix.com", "DE", minVolume=100) is called
THEN only keywords with volume >= 100 in the German market are returned
```

**ATS-021: Standalone JSON mode**

```
GIVEN no database is configured
WHEN keyword research completes
THEN keywords are saved to data/keywords/{domain}/{language}.json
AND the JSON file is valid and parseable
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: Keywords Everywhere API round-trip**

```
GIVEN valid Keywords Everywhere API credentials
WHEN a batch of 10 test keywords is submitted for country=DE
THEN each keyword returns a valid response with volume, CPC, and trend fields
AND the response matches the KeywordRecord schema
```

**INT-002: Google Autocomplete rate limiting**

```
GIVEN the autocomplete module is running
WHEN 100 requests are made in a session
THEN requests are spaced at least 2 seconds apart
AND no more than 100 requests are made per day
```

**INT-003: GSC OAuth integration**

```
GIVEN valid GSC OAuth credentials for hairgenetix.com
WHEN query data is requested
THEN the system returns keyword impression data
AND the response is used to populate gap_status fields
```

**INT-004: F-001 output → F-002 input compatibility**

```
GIVEN F-001 has completed and produced keyword records
WHEN F-002 (Topic Clustering) consumes the output
THEN all required fields for clustering are present (keyword text, volume, language)
AND the schema validates without errors
```

**INT-005: F-001 output → F-003 input compatibility**

```
GIVEN F-001 has completed keyword records
WHEN F-003 (Intent Classification) consumes the output
THEN keyword text and metadata are available for classification
```

**INT-006: Database vs JSON storage parity**

```
GIVEN the same keyword research run
WHEN executed in standalone mode (JSON) and platform mode (DB)
THEN both produce identical query results via getKeywordsByDomain()
```

**INT-007: API key from environment**

```
GIVEN KEYWORDS_EVERYWHERE_API_KEY is set as an environment variable
WHEN the module initialises
THEN the key is read from the environment
AND no API key appears in source code or logs
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | Non-empty keyword text | Every KeywordRecord has a non-empty `keyword` string |
| PI-002 | Valid language tag | Every KeywordRecord `language` is one of the 9 supported codes (de, fr, nl, es, it, pt, pl, tr, en) |
| PI-003 | Volume non-negative | `volume` is always >= 0 (never negative) |
| PI-004 | Difficulty range | `difficulty` is always 0-100 inclusive |
| PI-005 | Trend array length | `trend` array always has exactly 12 elements |
| PI-006 | Difficulty source tagged | Every difficulty score has a `source` field set to "heuristic" or "DataForSEO" |
| PI-007 | Timestamp present | Every record has a non-null `discovered_at` ISO 8601 timestamp |
| PI-008 | Tenant isolation | Every record has a non-null `tenant_id` |
| PI-009 | No duplicate keywords | No two records share the same (keyword, language, tenant_id) tuple |
| PI-010 | Gap status valid | `gap_status` is always one of: "own_keyword", "competitor_gap", "new_opportunity" |
| PI-011 | Batch size constraint | Keywords Everywhere API calls never exceed 100 keywords per batch |
| PI-012 | CPC non-negative | `cpc` is always >= 0 |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 to ATS-005 | Integration | Requires URL crawling and Autocomplete API |
| ATS-006 to ATS-010 | Integration | Requires Keywords Everywhere API (or mock) |
| ATS-011 to ATS-013 | Unit | Difficulty heuristic is pure computation; DataForSEO swap is unit-testable with mock |
| ATS-014 to ATS-017 | Integration | Requires GSC API or SERP data |
| ATS-018 to ATS-021 | Integration | Requires storage layer (DB or file system) |
| INT-001 to INT-007 | Integration | External API and storage boundaries |
| PI-001 to PI-012 | Property | Fast-check / property-based tests on KeywordRecord schema |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
