---
id: "FTR-SEO-005"
type: feature
title: "Competitor Content Analysis"
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

# F-005: Competitor Content Analysis — Requirements

## Problem Statement

To identify content gaps, we need to understand not just which keywords competitors rank for (F-004 SERP data), but what those ranking pages actually contain. Without this, gap analysis (F-006) is shallow: we know a competitor ranks for "FUE vs DHI comparison" but not whether their page is a 300-word stub or a 4,000-word authoritative guide. We can't produce a meaningful content brief if we don't know the quality bar we need to clear.

**Who has this problem:** The autonomous pipeline itself — F-006 (Content Gap Identification) and F-007 (Content Calendar) cannot produce a quality-calibrated output without competitor content benchmarks.

**Cost of inaction:** Gap analysis produces false opportunities (competitor ranks with thin content we could easily beat) and missed warnings (competitor has exceptional content that requires significant resource). Calendar recommendations lack realistic scope estimates.

---

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors). Focus: how each competitor analyses SERP-ranking pages.

### Competitor Analysis (for this feature)

| Feature/Capability | Frase | SurferSEO | Semrush | SEO.ai | Prevalence | Our Approach | Rationale |
|-------------------|-------|-----------|---------|--------|:----------:|-------------|-----------|
| SERP result page download | Yes — downloads top 20 results, extracts full text | Yes — top 10 SERP results | Yes — Content Analyzer downloads and extracts | Yes — downloads top results (opaque) | 4/4 | Download top-10 ranking competitor pages per keyword | Top 10 sufficient for R1; mirrors industry standard |
| Word count extraction | Yes | Yes — counts words, headings, paragraphs | Yes | Unknown | 3/4 | Extract word count from cleaned body text (HTML stripped) | Table stakes — direct match |
| Heading structure analysis | Yes — H2/H3 hierarchy extracted | Yes — heading count by level | Yes | Unknown | 3/4 | Extract H1-H3 hierarchy, count per level | Table stakes — used by F-006 topic mapping |
| Schema markup detection | Not documented | Not documented | Yes — schema types flagged | Unknown | 1/4 | Detect JSON-LD and microdata schema types present | Differentiator for AISO; schema presence predicts AI citation |
| Content quality signals | Frase score (proprietary — entity + NLP-based) | Content Score (correlation-based, correlation ≠ quality) | Not a quality signal — structural only | Unknown | 1/4 | LLM quality assessment: depth, accuracy signals, E-E-A-T markers | Anti-pattern: SurferSEO's correlation-based score rewards keyword stuffing (documented in deep-dive anti-patterns) |
| Topic / entity coverage | Yes — entities extracted from top results | No — keyword-count only | Not in research feature | Unknown | 2/4 | LLM-extracted topic list per page (not entity-based) | LLM approach is more robust than NLP entity extraction for R1 |
| Respectful crawling | Not documented | Not documented | Not documented | Not documented | 0/4 | robots.txt respected, 2 req/s max, User-Agent declared | Our standard — ethical crawling practice |
| Snapshot storage | Not documented | Not documented | Not documented | Not documented | 0/4 | Competitor page snapshots stored with timestamp for longitudinal comparison | Differentiator — enables "competitor updated their page" detection in R2+ |

### Key Findings

- **Table stakes:** Word count, heading structure, and content length benchmarks are provided by 3/4 competitors. This is the minimum required for F-006 to produce useful gap analysis.
- **Quality signal problem:** SurferSEO's Content Score is documented as correlation-based (high word count + keyword density = high score), which is explicitly listed as an anti-pattern in the deep-dive. Frase's entity-based approach is better but proprietary. Our LLM-based quality assessment sidesteps this entirely.
- **Schema detection gap:** No competitor documents schema markup detection in their research/analysis feature. This is a meaningful differentiator — schema presence correlates with AISO citation probability (from AISO skill research).
- **No competitor documents ethical crawling practices** — robots.txt compliance, rate limiting, and User-Agent transparency are not mentioned in any competitor docs. We implement as baseline hygiene.
- **Snapshot storage:** No competitor stores versioned competitor snapshots. In R2+ this enables change detection ("competitor updated their FUE page last month").

### Sources

- Parent epic deep-dive: `specs/001-autonomous-content-engine/E-001-research-strategy/epic-status.md` § Competitive Deep-Dive
- Anti-patterns reference: deep-dive anti-pattern #5 (Content Score gaming via keyword stuffing — SurferSEO, Frase)

---

## User Stories

### US-001: Competitor Page Download and Extraction

**As a** pipeline operator, **I want** the system to download and extract structured data from competitor pages that rank for target keywords, **so that** downstream features have concrete benchmarks for what high-ranking content looks like.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

```
WHEN F-004 (SERP Analysis) has identified competitor URLs ranking in top 10 for a target keyword
THE SYSTEM SHALL download each competitor page (max 10 per keyword)
AND extract the following fields from each page:
  - word_count (integer — body text only, no navigation/footer)
  - h1_text (string)
  - h2_count (integer)
  - h3_count (integer)
  - h2_texts (array of strings)
  - schema_types (array — JSON-LD types detected, e.g. ["Article", "FAQPage"])
  - has_faq_section (boolean — presence of FAQ-structured content)
  - internal_link_count (integer)
  - external_link_count (integer)
  - image_count (integer)
  - page_url (string)
  - crawled_at (ISO 8601 timestamp)
```

```
WHEN downloading a competitor page
THE SYSTEM SHALL respect the site's robots.txt
AND wait a minimum of 500ms between requests to the same domain
AND NOT exceed 2 requests per second to any domain
AND identify itself with a descriptive User-Agent string
```

```
WHEN a competitor page returns a non-200 HTTP status code
THE SYSTEM SHALL log the error (status code, URL, timestamp)
AND continue processing remaining competitor URLs
AND mark that URL as "crawl_failed" in the extraction record
```

```
WHEN a competitor page uses JavaScript rendering (content not in initial HTML)
THE SYSTEM SHALL fall back to static HTML extraction
AND flag the record as "may be incomplete — JS-rendered page detected"
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | `https://hairtransplantclinic.de/fue-vs-dhi` (ranks #3 for "FUE vs DHI") | Extracted record: word_count=3200, h2_count=8, schema_types=["Article"], has_faq=true, crawled_at="2026-03-15T10:23:00Z" |
| robots.txt blocks crawling | robots.txt disallows `/blog/` | URL skipped, logged as "blocked by robots.txt", no extraction attempt |
| Page returns 404 | Competitor URL no longer exists | Record: crawl_failed=true, status_code=404, downstream gap analysis excludes this URL |
| JS-rendered page | React SPA, content not in HTML source | Extraction continues with available HTML, flagged: "may be incomplete — JS-rendered page detected", best-effort word_count returned |
| Very short page | Competitor page has 180 words | word_count=180, flagged: "thin content" (< 300 words threshold) |
| Rate limit exceeded | Domain responds with 429 | Exponential backoff (30s, 60s, 120s), max 3 retries, then mark crawl_failed |

---

### US-002: Content Quality Benchmarking

**As a** pipeline operator, **I want** an LLM-assessed quality profile for each competitor page, **so that** the gap analysis knows not just that a competitor covers a topic but how well they cover it.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN competitor page extraction is complete (from US-001)
THE SYSTEM SHALL pass the extracted text to an LLM for quality assessment
AND produce a quality profile with:
  - depth_score (1-5 integer — surface/introductory/solid/in-depth/authoritative)
  - topics_covered (array of strings — main subtopics identified in the content)
  - has_original_data (boolean — contains statistics, research, case studies, or original data)
  - has_author_credentials (boolean — author byline with credentials present)
  - eeat_signals (array — detected signals: "author_bio", "medical_review", "citations", "first_person_experience")
  - quality_rationale (string — 1-2 sentences explaining the depth score)
```

```
WHEN producing a depth score
THE SYSTEM SHALL use the following rubric:
  1 = Surface: topic mentioned, no detail
  2 = Introductory: definitions and overview only
  3 = Solid: covers main subtopics, some practical content
  4 = In-depth: comprehensive treatment, addresses edge cases
  5 = Authoritative: original data, expert credentials, cited research
AND include the rationale string so the score is auditable
```

```
WHEN batch-processing competitor pages for a keyword group
THE SYSTEM SHALL process pages in batches of 5 to manage LLM token usage
AND store quality profiles alongside extraction records
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Authoritative competitor page | 4,200-word article on "FUE recovery", author is a surgeon, cites 3 studies | depth_score=5, eeat_signals=["author_bio", "medical_review", "citations"], has_original_data=true |
| Thin competitor page | 350-word blog post on "hair transplant aftercare", no author | depth_score=2, eeat_signals=[], has_original_data=false, rationale: "Brief overview with no detail. No credentials. Ranks likely due to domain authority." |
| Medium-quality page | 1,800-word guide, covers main topics, no citations | depth_score=3, topics_covered=["recovery timeline", "washing instructions", "activity restrictions"], has_original_data=false |
| Non-English page (German) | Competitor page in DE | LLM still processes and produces quality profile (topic extraction in DE, translated to EN for pipeline use) |
| Extraction failed (crawl_failed=true) | No text available | Quality profile skipped, quality_assessment_status="skipped — crawl failed" |

---

### US-003: Competitor Snapshot Storage

**As a** pipeline operator, **I want** competitor page data stored as timestamped snapshots, **so that** repeated pipeline runs can detect when competitors have updated their content.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

```
WHEN a competitor page is successfully extracted
THE SYSTEM SHALL store the CompetitorSnapshot record with:
  - all extracted structural fields (from US-001)
  - quality profile (from US-002)
  - raw_html_hash (MD5 of the page HTML — for change detection)
  - crawled_at timestamp
  - domain + path
  - tenant_id
```

```
WHEN a competitor URL has been crawled before
THE SYSTEM SHALL compare the new raw_html_hash against the stored hash
AND flag the record as "content_changed" if hashes differ
AND preserve the previous snapshot (do not overwrite — append new version)
```

```
WHEN downstream features query competitor data
THE SYSTEM SHALL return the most recent snapshot by default
AND support a query for historical snapshots by date range
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| First crawl | `hairtransplantclinic.de/fue-vs-dhi` | Snapshot stored with crawled_at=now, content_changed=false (no prior) |
| Second crawl, page updated | Same URL, competitor added 800 words | New snapshot stored, content_changed=true, previous snapshot preserved |
| Second crawl, page unchanged | Same URL, same content | New snapshot stored, content_changed=false, pipeline skips re-analysis |
| Query most recent | getCompetitorSnapshot("hairtransplantclinic.de/fue-vs-dhi") | Returns most recent snapshot |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN extracting and analysing a competitor page THE SYSTEM SHALL complete within 30 seconds per page (including LLM quality assessment) | p95 < 30s per page | Integration test with timer | No |
| 2 | **Scalability** | N/A — R1 targets 1-5 domains, top 10 competitors per keyword. Max ~100 pages per pipeline run. | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN a competitor page download fails THE SYSTEM SHALL continue with remaining pages AND mark failed URLs as "crawl_failed" so downstream features exclude them gracefully | 0 pipeline halts from individual page failures | Integration test with mock HTTP failures | Yes |
| 5 | **Security** | N/A — crawling public pages, no credentials involved in this feature | — | — | No |
| 6 | **Privacy** | N/A — all competitor data is publicly accessible content | — | — | No |
| 7 | **Compliance / Regulatory** | WHEN crawling competitor pages THE SYSTEM SHALL respect robots.txt directives AND NOT crawl pages disallowed by the site's robots.txt | 100% robots.txt compliance | Unit test: mock robots.txt with disallowed paths, confirm skipped | Yes |
| 8 | **Interoperability** | WHEN outputting competitor analysis data THE SYSTEM SHALL use the CompetitorSnapshot schema (defined in contracts/) | Schema validation on every output | Unit test with Zod validation | Yes |
| 9 | **Portability** | WHEN running in standalone mode THE SYSTEM SHALL save competitor snapshots to `data/competitor-snapshots/{domain}/{path-slug}.json` | Both modes (standalone + platform) produce queryable snapshot data | Integration test both storage adapters | Yes |
| 10 | **Maintainability** | THE SYSTEM SHALL abstract page extraction behind an ExtractorPort interface so the extraction library can be swapped | New extractors addable without pipeline changes | Architecture review | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support mock HTTP responses returning fixture HTML so tests run without live network calls | Unit + integration tests run offline | Test suite runs without network | Yes |
| 12 | **Usability** | N/A — CLI only for R1. No interactive UI. | — | — | No |
| 13 | **Localisation** | WHEN extracting competitor pages in non-English languages THE SYSTEM SHALL extract structural fields (word count, headings, schema) regardless of language AND pass text to LLM for language-aware quality assessment | Quality profiles produced for all 9 Hairgenetix languages | Integration test with DE-language fixture page | No |
| 14 | **Monitoring** | WHEN competitor analysis completes for a keyword group THE SYSTEM SHALL log: pages attempted, pages successful, pages failed, LLM calls made, tokens consumed, duration | Structured JSON log entry | Log schema validation | No |
| 15 | **Auditability** | N/A — no financial or compliance-critical actions | — | — | No |
| 16 | **Disaster Recovery** | N/A — competitor snapshots are re-crawlable; not primary data | — | — | No |
| 17 | **Capacity** | N/A — max 100 pages per pipeline run at R1 scale | — | — | No |
| 18 | **Cost** | WHEN running LLM quality assessment THE SYSTEM SHALL consume < 2K tokens per page AND < 20K tokens per full competitor analysis run (10 keywords × 10 pages) | < $0.20 per full run at Claude pricing | Token counter in logs | No |
| 19-35 | Remaining categories | N/A — R1 CLI tool; enterprise NFRs (accessibility, billing, etc.) apply from R2 (platform integration) | — | — | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN assessing a competitor page quality THE SYSTEM SHALL complete the LLM call within 20 seconds | p95 < 20s | Integration test with timer |
| Token economics | WHEN running quality assessment THE SYSTEM SHALL use a compressed page summary (not full HTML) as LLM input, capped at 2K tokens per page | < 2K tokens input per page | Token counter in logs |
| Hallucination rate | WHEN producing depth scores and topic lists THE SYSTEM SHALL include a rationale string AND flag AI-assessed fields as "llm_assessed" | 100% of AI-assessed fields flagged | Unit test checks field tags |
| Prompt versioning | WHEN using LLM prompts for quality assessment THE SYSTEM SHALL version prompts in `prompts/competitor-quality-assessment/` directory | All prompts in prompts/ directory | File structure check |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (approved at Gate 1) |
| User personas and goals | [x] | JTBD 1-4 in epic-status.md — this feature serves the pipeline, not a human directly |
| N/A justification | [x] | No UI for R1. F-005 is a pipeline stage with no human-facing output. Results surface in F-007 Content Calendar for human review. All competitors have web UI for competitor analysis; CLI justified for internal tool validation (Gate 1 approved). |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. Auth deferred to platform integration (R2+). Config-file tenant context for standalone mode. |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-005 behind `FEATURE_COMPETITOR_ANALYSIS` flag (env var in standalone, platform flags in R2+) |
| Config management | [x] | Crawl rate limits and robots.txt compliance configurable via `.env`. LLM model for quality assessment configurable. |
| N/A justification | [x] | No admin UI, billing, or reporting for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | Competitor websites (public HTTP/HTTPS), Claude API (quality assessment LLM calls). No additional external APIs. |
| API protocol | [x] | Internal: TypeScript module exports (commands/queries pattern). External: HTTP GET to competitor pages (no auth). |
| Resilience per dependency | [x] | HTTP: retry 3x with exponential backoff, robots.txt check before each crawl, graceful degradation on failure. LLM: retry 2x on 429/500 errors. |
| Rate limiting | [x] | Max 2 req/s to any domain, 500ms minimum between requests to same domain, robots.txt crawl-delay directive respected if present. |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature — no migration. Snapshot storage schema designed for forward-compatibility with platform DB. |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs per run: pages attempted, succeeded, failed (with reasons), LLM tokens used, total duration |
| Cost budget | [x] | LLM quality assessment: < $0.20 per full run (20K tokens × Claude Haiku pricing). Negligible cost at R1 scale. |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. Added at platform integration (R2+). |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 (page download + extraction) | `[table-stakes]` | All 4 competitors download SERP-ranking pages for analysis | 1-Features |
| US-001 (schema detection) | `[differentiator]` | 0/4 competitors document schema markup detection in research feature | 1-Features |
| US-001 (ethical crawling) | `[differentiator]` | 0/4 competitors document robots.txt compliance or rate limiting | 2-Workflows |
| US-002 (LLM quality vs correlation-based score) | `[anti-pattern]` | SurferSEO/Frase Content Score rewards keyword stuffing, not quality | 1-Features |
| US-002 (E-E-A-T signal detection) | `[differentiator]` | 0/4 competitors extract E-E-A-T signals (author credentials, medical review, citations) | 5-Data |
| US-003 (snapshot storage) | `[differentiator]` | 0/4 competitors store versioned competitor snapshots for longitudinal comparison | 5-Data |

---

## Out of Scope

- Full-text archival of competitor HTML (we store structural data and quality profile, not the raw HTML body)
- Backlink analysis of competitor pages (separate capability)
- Competitor page performance metrics (Core Web Vitals, load time) — not relevant to content gap analysis
- Social share counts or engagement metrics for competitor pages
- Competitor page monitoring / alerting on changes (snapshot change detection is Should for R1; alerting is R2+)
- Paid competitor content behind paywalls or login walls

---

## Open Questions

- [ ] Should the LLM quality assessment use Claude Haiku (cost-efficient) or Sonnet (higher quality)? Proposed: Haiku for R1 (sufficient for 1-5 depth score, low cost). Upgrade path to Sonnet if quality scores prove inaccurate.
- [ ] What is the maximum page size (in characters) to pass to the LLM? Proposed: 8,000 characters of body text (after HTML stripping) — captures enough for quality assessment without exceeding token limits.
- [x] Do we respect `Crawl-delay` in robots.txt? Yes — mandatory. If no crawl-delay specified, our default 500ms minimum applies.

---

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-004 SERP Analysis | Internal | Not started | US-001 — competitor URLs come from SERP data |
| Claude API (LLM quality assessment) | External | Available (API key in use) | US-002 quality profiles |
| robots.txt parser library | Internal | Needs selection | US-001 crawl compliance |
| F-006 Content Gap Identification | Internal | Not started | Downstream consumer of this feature's output |

---

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | Top 10 competitor pages per keyword provides sufficient benchmarks for gap analysis | High | Frase and SurferSEO use top 10-20; top 10 is conservative and defensible |
| A2 | Claude Haiku can produce accurate depth scores (1-5) and topic lists from 8K-character page extracts | Medium | Test with 10 Hairgenetix competitor pages before implementation |
| A3 | Static HTML extraction will cover >= 80% of competitor pages (most are server-rendered) | High | Hair/medical industry sites are predominantly WordPress/static — low JS-rendering risk |
| A4 | Storing structural data (not full HTML) is sufficient for F-006 gap analysis | High | F-006 needs word count, headings, topics, schema — not raw HTML |
