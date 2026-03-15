# F-005: Competitor Content Analysis — Tasks

## Task T-001: CompetitorSnapshot Schema & Migration [Foundation]
**Story:** US-003 (Snapshot Persistence)
**Size:** M
**Depends on:** F-004 T-001 (serp schema for FK)
**Parallel:** Yes [P]

### What
Create the Drizzle schema for `competitor_snapshot` table with all columns from design.md (structural extraction, quality assessment, change detection, metadata). Generate Zod validation schemas. Write the migration with RLS policy and all indexes.

### Files
- Create: `modules/content-engine/research/schema/competitor.ts`
- Create: `modules/content-engine/research/contracts/competitor-snapshot.ts`
- Create: `modules/content-engine/research/migrations/0004_competitor_snapshot.sql`
- Create (tests): `modules/content-engine/research/schema/__tests__/competitor.schema.test.ts`
- Read (context): `design.md` (Data Model section)

### Test Scenarios (from tests.md)
- PI-001: Word count non-negative
- PI-002: Heading counts non-negative
- PI-003: Depth score range 1-5
- PI-005: crawled_at present
- PI-006: Tenant isolation (tenant_id non-null)
- PI-009: Snapshots append-only

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] All columns per design.md defined
- [ ] RLS policy in migration
- [ ] 4 indexes created (tenant, keyword, url+date, domain)
- [ ] Zod schema auto-generated
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write schema, migration, tests
- Ask: add columns beyond design
- Never: skip RLS, store raw HTML

---

## Task T-002: RobotsTxtChecker [Domain Logic]
**Story:** US-001 (robots.txt compliance)
**Size:** S
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the `RobotsTxtChecker` that fetches and parses robots.txt, checks if a URL path is crawlable, and extracts crawl-delay if specified. Cache robots.txt per domain for 24h (in-memory Map, cleared on restart). Use `robots-parser` npm package.

### Files
- Create: `modules/content-engine/research/services/robots-txt-checker.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/robots-txt-checker.test.ts`
- Create: `modules/content-engine/research/__fixtures__/robots-txt/`

### Test Scenarios (from tests.md)
- ATS-002: robots.txt blocks crawling — URL skipped, no request made
- INT-004: Disallow /private/ path correctly blocked
- PI-010: Crawl rate respected (crawl-delay compliance)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Fetches and parses robots.txt per domain
- [ ] Returns `{ allowed: boolean; crawl_delay?: number }`
- [ ] Caches per domain for 24h (in-memory Map)
- [ ] MSW mock for robots.txt fetch in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change cache duration
- Never: skip robots.txt check before crawling

---

## Task T-003: Domain-Aware Rate Limiter [Domain Logic]
**Story:** US-001 (Rate limiting), NFR
**Size:** M
**Depends on:** T-002 (for crawl-delay)
**Parallel:** Yes [P]

### What
Implement the per-domain token bucket rate limiter per ADR-F005-003. Each domain gets its own bucket (rate from robots.txt crawl-delay or default 500ms). Global concurrency limited to 2 in-flight requests. Implemented as an async semaphore with per-domain delay tracking.

### Files
- Create: `modules/content-engine/research/services/crawl-rate-limiter.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/crawl-rate-limiter.test.ts`

### Test Scenarios (from tests.md)
- ATS-007: Requests spaced ≥500ms, max 2/sec per domain
- PI-010: Crawl rate respected for any request sequence

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Per-domain token bucket with configurable delay (default 500ms)
- [ ] Global concurrency limit: 2 in-flight requests
- [ ] `acquire(domain)` waits for rate compliance, returns release function
- [ ] Respects robots.txt crawl-delay when available
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change default rate limits
- Never: bypass rate limiter, remove concurrency limit

---

## Task T-004: ContentExtractor (cheerio) [Domain Logic]
**Story:** US-001 (Page Download and Extraction)
**Size:** L
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the `ContentExtractor` that parses HTML with cheerio and extracts structural fields: word count (stripping nav/footer/header/aside/script/style), h1, h2/h3 headings and texts, JSON-LD schema types, FAQ section detection, internal/external link counts, image count, JS-rendered page detection, thin content flag (<300 words).

### Files
- Create: `modules/content-engine/research/services/content-extractor.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/content-extractor.test.ts`
- Create: `modules/content-engine/research/__fixtures__/competitor-pages/` (4+ fixture HTML files)
- Read (context): `design.md` (ContentExtractor component design)

### Test Scenarios (from tests.md)
- ATS-001: Full extraction — word count, headings, schema, links, images
- ATS-004: JS-rendered page detection (body text < 100 chars)
- ATS-005: Thin page detection (<300 words)
- PI-001: word_count >= 0
- PI-002: h2_count/h3_count >= 0
- PI-012: Link counts >= 0
- PI-013: Image count >= 0

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Strips nav/footer/header/aside/script/style before word count
- [ ] Extracts JSON-LD from `<script type="application/ld+json">`
- [ ] FAQ detection: FAQPage itemtype, H2 "FAQ", or `<details>` groups
- [ ] JS-rendered flag when body text < 100 chars after stripping
- [ ] Thin content flag when word count < 300
- [ ] 4+ fixture HTML files covering: normal page, thin page, SPA, FAQ page
- [ ] Property tests: word_count >= 0, h2_texts.length === h2_count
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, create fixture HTML
- Ask: add npm dependency (cheerio expected)
- Never: execute JavaScript in extracted content

---

## Task T-005: PageDownloader with SSRF Protection [Domain Logic]
**Story:** US-001
**Size:** M
**Depends on:** T-002, T-003 (robots check + rate limiter)
**Parallel:** No

### What
Implement the `PageDownloader` that fetches competitor pages with SSRF protection. Validates URLs (allowlist http/https schemes, block private IPs, limit redirects to 3). Integrates with RobotsTxtChecker (skip if disallowed) and CrawlRateLimiter (wait for rate compliance). Computes MD5 hash of raw HTML for change detection. DOMPurify on extracted text before storage.

### Files
- Create: `modules/content-engine/research/services/page-downloader.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/page-downloader.test.ts`

### Test Scenarios (from tests.md)
- ATS-003: HTTP 404 → crawl_failed, pipeline continues
- ATS-006: 429 → exponential backoff (3 retries), then crawl_failed
- PI-007: raw_html_hash always non-empty MD5 string

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] SSRF: private IP block, scheme allowlist, redirect limit 3
- [ ] robots.txt check before fetch (skip if disallowed)
- [ ] Rate limiter integration (wait for domain slot)
- [ ] Retry with exponential backoff (30s, 60s, 120s, max 3)
- [ ] MD5 hash computed from raw HTML
- [ ] DOMPurify sanitisation on extracted text
- [ ] Descriptive User-Agent string
- [ ] MSW mocks for all HTTP calls in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, validate URL safety
- Ask: add headless browser (Playwright) for JS-rendered pages
- Never: skip SSRF validation, bypass rate limiter, store raw HTML

---

## Task T-006: QualityAssessor (LLM) [Domain Logic]
**Story:** US-002 (Content Quality Benchmarking)
**Size:** M
**Depends on:** T-004 (extractor provides compressed content)
**Parallel:** No

### What
Implement the `QualityAssessor` that sends compressed page content (first 2000 chars + headings + author section + references section) to Claude Haiku with structured JSON output. Produces depth_score (1-5), topics_covered, has_original_data, has_author_credentials, eeat_signals, quality_rationale. Batches 5 pages per LLM call. Falls back gracefully on LLM failure (status = "failed", pipeline continues).

### Files
- Create: `modules/content-engine/research/services/quality-assessor.ts`
- Create: `modules/content-engine/research/prompts/competitor-quality-assessment/v1.txt`
- Create (tests): `modules/content-engine/research/services/__tests__/quality-assessor.test.ts`
- Create: `modules/content-engine/research/__fixtures__/quality-assessment-response.json`

### Test Scenarios (from tests.md)
- ATS-008: Authoritative page → depth_score=5, E-E-AT signals
- ATS-009: Thin page → depth_score=2, no E-E-AT
- ATS-010: Medium quality → depth_score=3
- ATS-011: German page → valid quality profile
- ATS-012: Crawl-failed → quality skipped
- ATS-013: 12 pages → 3 LLM batch calls (5+5+2)
- ATS-014: Depth score rubric adherence
- PI-003: Depth score always 1-5
- PI-008: LLM fields flagged
- PI-011: Rationale present when scored

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Compressed input: first 2000 chars + headings + author + references
- [ ] Capped at 2000 tokens per page input
- [ ] Batch 5 pages per LLM call
- [ ] Prompt versioned in `prompts/` directory
- [ ] LLM failure → 2 retries → status="failed", pipeline continues
- [ ] All LLM-assessed fields tagged in `llm_assessed_fields` array
- [ ] Mock AI gateway in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, version prompts
- Ask: switch from Haiku to Sonnet, change batch size
- Never: use inline prompts, skip LLM field labelling, exceed 2K tokens/page

---

## Task T-007: CompetitorSnapshotRepo (DB + File) [Integration]
**Story:** US-003 (Snapshot Persistence)
**Size:** M
**Depends on:** T-001 (schema)
**Parallel:** Yes [P]

### What
Implement the `CompetitorSnapshotPort` interface with `DatabaseCompetitorSnapshotRepo` and `FileCompetitorSnapshotRepo`. Both support create (append-only), getLatest, getByKeyword (for F-006 benchmarks), and getHistory. Change detection: compare raw_html_hash with previous snapshot.

### Files
- Create: `modules/content-engine/research/ports/competitor-snapshot-port.ts`
- Create: `modules/content-engine/research/repos/db-competitor-snapshot-repo.ts`
- Create: `modules/content-engine/research/repos/file-competitor-snapshot-repo.ts`
- Create (tests): `modules/content-engine/research/repos/__tests__/competitor-snapshot-repo.test.ts`

### Test Scenarios (from tests.md)
- ATS-015: First crawl → content_changed=false
- ATS-016: Second crawl, content changed → content_changed=true, new snapshot
- ATS-017: Second crawl, unchanged → content_changed=false, skip quality re-assessment
- ATS-018: getLatest returns most recent snapshot
- INT-005: Standalone file output validates
- PI-009: Append-only (never overwrite)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Append-only create (never overwrite existing snapshots)
- [ ] Change detection via raw_html_hash comparison
- [ ] getLatest, getByKeyword, getHistory queries
- [ ] File adapter writes to `data/competitor-snapshots/{domain}/{path-slug}.json`
- [ ] Both adapters produce identical query results (parity test)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change storage structure
- Never: overwrite existing snapshots, skip tenant_id

---

## Task T-008: AnalyseCompetitorPage + BatchAnalyse Commands [Integration]
**Story:** All user stories
**Size:** L
**Depends on:** T-002, T-003, T-004, T-005, T-006, T-007
**Parallel:** No

### What
Implement the `AnalyseCompetitorPageCommand` and `BatchAnalyseCompetitorsCommand` handlers that orchestrate the full F-005 pipeline: robots check → rate limit → download → extract → quality assess → hash → persist → emit event. Batch command processes all URLs from a SERP snapshot, tracking succeeded/failed/robots_blocked counts.

### Files
- Create: `modules/content-engine/research/commands/analyse-competitor.ts`
- Create: `modules/content-engine/research/commands/batch-analyse-competitors.ts`
- Create: `modules/content-engine/research/events/competitor-events.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/analyse-competitor.test.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/batch-analyse-competitors.test.ts`
- Modify: `modules/content-engine/research/index.ts` (export commands)

### Test Scenarios (from tests.md)
- ATS-001: Happy path — full extraction + quality assessment
- ATS-002: robots.txt blocked → skipped, logged
- ATS-003: 404 → crawl_failed, pipeline continues
- ATS-006: 429 → retry → crawl_failed, pipeline continues
- INT-001: F-004 output as input (SERP URLs)
- INT-002: F-005 output consumable by F-006
- INT-006: Token budget compliance (< 2K per page, < $0.20 for 10 pages)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Full pipeline: robots → rate limit → download → extract → assess → hash → persist → event
- [ ] `AnalyseCompetitorPageResult` with crawl_status, word_count, depth_score, content_changed
- [ ] `BatchAnalyseCompetitorsOutput` with succeeded/failed/robots_blocked counts
- [ ] `CompetitorAnalysisCompleted` event emitted per snapshot
- [ ] `CompetitorBatchCompleted` event emitted for batch
- [ ] Partial failures don't halt the batch
- [ ] Feature flag `FEATURE_COMPETITOR_ANALYSIS` checked at entry
- [ ] Structured JSON logging: URLs crawled, status, tokens, cost, duration
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change event schema
- Never: skip robots.txt, bypass rate limiter, skip tests
