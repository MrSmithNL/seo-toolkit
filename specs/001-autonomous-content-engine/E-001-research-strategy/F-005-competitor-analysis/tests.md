---
id: "FTR-SEO-005"
title: "Test Plan: Competitor Content Analysis"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 37
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-005: Competitor Content Analysis — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: Competitor Page Download and Extraction

**ATS-001: Happy path — full extraction**

```
GIVEN a competitor URL "https://hairtransplantclinic.de/fue-vs-dhi" ranking #3 for "FUE vs DHI"
WHEN competitor page download and extraction runs
THEN the extracted record includes: word_count (e.g. 3200), h1_text, h2_count (e.g. 8), h3_count, h2_texts array, schema_types (e.g. ["Article"]), has_faq_section (e.g. true), internal_link_count, external_link_count, image_count, page_url, crawled_at timestamp
```

**ATS-002: robots.txt blocks crawling**

```
GIVEN a competitor site with robots.txt that disallows /blog/
AND the target URL is under /blog/
WHEN extraction is attempted
THEN the URL is skipped
AND logged as "blocked by robots.txt"
AND no HTTP request is made to the page
```

**ATS-003: Page returns 404**

```
GIVEN a competitor URL that returns HTTP 404
WHEN download is attempted
THEN the record is marked crawl_failed=true with status_code=404
AND pipeline continues with remaining URLs
AND downstream gap analysis excludes this URL
```

**ATS-004: JS-rendered page fallback**

```
GIVEN a competitor page that uses React SPA with content not in initial HTML
WHEN download runs
THEN static HTML extraction continues with available content
AND the record is flagged "may be incomplete — JS-rendered page detected"
AND a best-effort word_count is returned
```

**ATS-005: Very short (thin) page detected**

```
GIVEN a competitor page with only 180 words of body text
WHEN extraction runs
THEN word_count=180
AND the record is flagged "thin content" (below 300-word threshold)
```

**ATS-006: Rate limit exceeded — 429 response**

```
GIVEN a competitor domain responds with HTTP 429
WHEN the system retries with exponential backoff (30s, 60s, 120s, max 3)
AND all retries fail
THEN the URL is marked crawl_failed=true
AND pipeline continues
```

**ATS-007: Crawl rate compliance**

```
GIVEN 10 competitor URLs from the same domain
WHEN download runs
THEN requests are spaced at least 500ms apart
AND no more than 2 requests per second are made to that domain
AND User-Agent string is descriptive
```

### US-002: Content Quality Benchmarking

**ATS-008: Authoritative competitor page**

```
GIVEN a 4,200-word article on "FUE recovery" by a surgeon, citing 3 studies
WHEN LLM quality assessment runs
THEN depth_score=5
AND eeat_signals includes "author_bio", "medical_review", "citations"
AND has_original_data=true
AND quality_rationale explains the authoritative assessment
```

**ATS-009: Thin competitor page**

```
GIVEN a 350-word blog post on "hair transplant aftercare" with no author
WHEN LLM quality assessment runs
THEN depth_score=2
AND eeat_signals is empty
AND has_original_data=false
AND rationale mentions "brief overview" and "no credentials"
```

**ATS-010: Medium quality page**

```
GIVEN an 1,800-word guide covering main topics but no citations
WHEN LLM quality assessment runs
THEN depth_score=3
AND topics_covered includes main subtopics (e.g. "recovery timeline", "washing instructions")
AND has_original_data=false
```

**ATS-011: Non-English (German) competitor page**

```
GIVEN a competitor page entirely in German
WHEN LLM quality assessment runs
THEN a valid quality profile is produced
AND topics are identified (translated to EN for pipeline use)
AND depth_score is on the 1-5 scale
```

**ATS-012: Crawl-failed page — quality assessment skipped**

```
GIVEN a URL with crawl_failed=true
WHEN quality assessment stage is reached
THEN quality profile is skipped
AND quality_assessment_status="skipped — crawl failed"
```

**ATS-013: Batch processing — 5 pages per LLM batch**

```
GIVEN 12 competitor pages to assess
WHEN quality assessment runs
THEN pages are processed in batches of 5 (3 LLM calls: 5+5+2)
AND all profiles are stored alongside extraction records
```

**ATS-014: Depth score rubric adherence**

```
GIVEN any competitor page with extracted text
WHEN quality assessment runs
THEN depth_score follows the documented rubric:
  1=surface, 2=introductory, 3=solid, 4=in-depth, 5=authoritative
AND the rationale string is consistent with the assigned score
```

### US-003: Competitor Snapshot Storage

**ATS-015: First crawl snapshot**

```
GIVEN a competitor URL crawled for the first time
WHEN extraction and quality assessment complete
THEN a CompetitorSnapshot is stored with all fields + raw_html_hash + crawled_at
AND content_changed=false (no prior snapshot)
```

**ATS-016: Second crawl — content changed**

```
GIVEN a competitor URL crawled previously, and the competitor has added 800 words
WHEN the same URL is crawled again
THEN raw_html_hash differs from stored hash
AND new snapshot is stored with content_changed=true
AND the previous snapshot is preserved (not overwritten)
```

**ATS-017: Second crawl — content unchanged**

```
GIVEN a competitor URL crawled previously with identical content
WHEN the same URL is crawled again
THEN raw_html_hash matches
AND content_changed=false
AND pipeline skips re-analysis of quality profile
```

**ATS-018: Query most recent snapshot**

```
GIVEN 3 snapshots for "hairtransplantclinic.de/fue-vs-dhi" at different timestamps
WHEN getCompetitorSnapshot("hairtransplantclinic.de/fue-vs-dhi") is called
THEN the most recent snapshot is returned
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: F-004 output → F-005 input pipeline**

```
GIVEN F-004 has produced SerpSnapshot records with competitor URLs
WHEN F-005 receives the URLs
THEN all competitor URLs from organic_results are available for download
AND extraction runs for each URL
```

**INT-002: F-005 output → F-006 input pipeline**

```
GIVEN F-005 has produced CompetitorSnapshot records
WHEN F-006 (Content Gap Identification) consumes them
THEN word_count, depth_score, and h2_texts are available for gap analysis
AND CompetitorSnapshot schema validates
```

**INT-003: Claude API quality assessment round-trip**

```
GIVEN valid Claude API credentials and an 8K-character page extract
WHEN quality assessment LLM call runs
THEN the response includes depth_score, topics_covered, eeat_signals, quality_rationale
AND tokens consumed < 2K for the single page
```

**INT-004: robots.txt parser integration**

```
GIVEN a competitor site with robots.txt containing "Disallow: /private/"
WHEN extraction attempts /private/article.html
THEN the URL is skipped
AND robots.txt compliance is logged
```

**INT-005: Standalone file output**

```
GIVEN standalone mode (no database)
WHEN competitor analysis completes
THEN snapshots are saved to data/competitor-snapshots/{domain}/{path-slug}.json
AND files validate against CompetitorSnapshot schema
```

**INT-006: LLM token budget compliance**

```
GIVEN 10 competitor pages for quality assessment
WHEN assessment runs
THEN total tokens consumed < 20K (< 2K per page)
AND cost estimate is < $0.20 at Claude pricing
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | Word count non-negative | word_count is always >= 0 |
| PI-002 | Heading counts non-negative | h2_count and h3_count are always >= 0 |
| PI-003 | Depth score range | depth_score is always 1-5 inclusive (integer) |
| PI-004 | Schema types valid | schema_types is an array of strings (may be empty) |
| PI-005 | Crawled_at present | Every CompetitorSnapshot has a non-null crawled_at ISO 8601 timestamp |
| PI-006 | Tenant isolation | Every CompetitorSnapshot has a non-null tenant_id |
| PI-007 | Hash non-empty | raw_html_hash is always a non-empty string (MD5) |
| PI-008 | LLM fields flagged | All AI-assessed fields (depth_score, topics_covered, quality_rationale) are tagged "llm_assessed" |
| PI-009 | Snapshots append-only | Subsequent crawls for the same URL create new records, never overwrite |
| PI-010 | Crawl rate respected | Requests to any single domain never exceed 2/second with >= 500ms spacing |
| PI-011 | Rationale present when scored | Every non-null depth_score has a non-empty quality_rationale |
| PI-012 | Link counts non-negative | internal_link_count and external_link_count are always >= 0 |
| PI-013 | Image count non-negative | image_count is always >= 0 |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 | Integration | Requires HTTP download of competitor page |
| ATS-002 to ATS-003 | Unit | robots.txt parsing and HTTP status handling are unit-testable |
| ATS-004 to ATS-007 | Integration | Requires HTTP client with rate limiting and retry logic |
| ATS-008 to ATS-014 | Integration | Requires LLM call for quality assessment |
| ATS-015 to ATS-018 | Integration | Requires storage layer for snapshot persistence |
| INT-001 to INT-006 | Integration | Cross-feature data flow and API boundaries |
| PI-001 to PI-013 | Property | Fast-check on CompetitorSnapshot schema constraints |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
