# F-004: SERP Analysis — Tasks

## Task T-001: SerpSnapshot Drizzle Schema + RLS + Zod
**Story:** US-003 (SERP Snapshot Persistence)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Define the `serp_snapshot` and `serp_result` Drizzle schema tables with all columns from the design, including indexes and tenant_id. Add RLS policies via a migration. Generate Zod schemas with `drizzle-zod` for runtime validation.

### Files
- Create: `modules/content-engine/research/schema/serp.ts`
- Create: `modules/content-engine/research/schema/serp.zod.ts`
- Create: `migrations/XXXX_serp_tables.sql`
- Create (tests): `modules/content-engine/research/schema/__tests__/serp.test.ts`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (Data Model section)

### Test Scenarios (from tests.md)
- PI-001 to PI-012: Property invariants on schema constraints
- ATS-015: First snapshot created with all required fields

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `serp_snapshot` and `serp_result` tables defined in Drizzle with all columns from design
- [ ] Indexes match design (tenant, keyword, latest)
- [ ] RLS policies in migration SQL
- [ ] Zod schemas auto-generated from Drizzle
- [ ] Property tests validate position range (1-10), content_type enum, boolean feature flags, api_source enum
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write schema, create migration, run tests
- Ask: change column types or add columns beyond design
- Never: skip RLS, store credentials in schema file

---

## Task T-002: SerpDataSource Interface + Mock Adapter
**Story:** US-001 (Top-10 SERP Result Scraping)
**Size:** S
**Depends on:** —
**Parallel:** Yes [P]

### What
Define the `SerpDataSource` interface per ADR-F004-001 and ADR-E001-002. Create a `MockSerpDataSource` that returns fixture data for testing. Define the `SerpFeatures` shared type and `SerpError` union type.

### Files
- Create: `modules/content-engine/research/ports/serp-data-source.ts`
- Create: `modules/content-engine/research/types/serp.ts`
- Create: `modules/content-engine/research/adapters/__mocks__/mock-serp-data-source.ts`
- Create: `modules/content-engine/research/adapters/__mocks__/fixtures/serp-fixtures.ts`
- Create (tests): `modules/content-engine/research/ports/__tests__/serp-data-source.test.ts`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (API Contracts section)

### Test Scenarios (from tests.md)
- ATS-013: Purely organic SERP — no features (mock returns all-false features)
- PI-004: Feature flags boolean invariant

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `SerpDataSource` interface with `fetchSerp()` method defined
- [ ] `SerpFeatures`, `SerpError`, `AnalyseSerpInput/Output` types defined
- [ ] `MockSerpDataSource` returns configurable fixture data
- [ ] Fixture data covers: happy path, video-heavy SERP, zero organic results, feature-rich SERP
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write interfaces, mock adapter, types
- Ask: add methods to interface beyond design
- Never: hardcode API credentials in types

---

## Task T-003: Rate Limiter (Token Bucket + Redis Counter)
**Story:** US-001 (rate limiting), NFR-7 (Google fallback rate)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement a token bucket rate limiter with per-source daily counters stored in Redis. The limiter enforces configurable daily maximums (default: 50 for DataForSEO, 30 for Google scraper) with midnight UTC reset. Expose `canRequest()` and `recordRequest()` methods.

### Files
- Create: `modules/content-engine/research/services/serp-rate-limiter.ts`
- Create: `modules/content-engine/research/config/serp-config.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/serp-rate-limiter.test.ts`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (ADR-F004-002)

### Test Scenarios (from tests.md)
- ATS-004: Daily rate limit enforcement (51st request blocked)
- ATS-007: Configurable daily limit via env var
- PI-009: Daily limit respected — counter never exceeds limit
- INT-006: Daily request counter persistence across restarts

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Token bucket with per-source (dataforseo/google) daily counters
- [ ] Redis key pattern: `serp:daily:{source}:{date}` with midnight UTC expiry
- [ ] `canRequest(source)` returns boolean + remaining count
- [ ] `recordRequest(source)` increments counter atomically
- [ ] Error message on limit: "SERP daily limit reached (N/N). Next requests available after midnight UTC."
- [ ] Property test: daily_request_count never exceeds configured limit for any call sequence
- [ ] In-memory Map fallback for unit tests (no Redis required)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write limiter, config, tests
- Ask: change default rate limits
- Never: bypass rate limiter, remove Redis persistence

---

## Task T-004: SerpFeatureDetector
**Story:** US-002 (SERP Feature Detection)
**Size:** M
**Depends on:** T-002 (SerpDataSource interface)
**Parallel:** No

### What
Implement the `SerpFeatureDetector` that normalises SERP feature flags from any data source into the canonical `SerpFeatures` object. Each adapter provides raw feature data; the detector produces a consistent boolean-flag object with PAA question extraction.

### Files
- Create: `modules/content-engine/research/services/serp-feature-detector.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/serp-feature-detector.test.ts`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (ADR-F004-003)

### Test Scenarios (from tests.md)
- ATS-008: AI Overview detected, keyword flagged with warning
- ATS-009: Featured snippet detected
- ATS-010: PAA extraction (up to 5 questions)
- ATS-011: Local pack detected
- ATS-012: Image pack and video carousel
- ATS-013: Purely organic SERP, all flags false
- PI-004: All feature fields are boolean
- PI-005: PAA array has 0-5 elements

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Normalises DataForSEO response fields to canonical `SerpFeatures`
- [ ] Normalises Google scraper HTML indicators to canonical `SerpFeatures`
- [ ] PAA questions extracted as string array (max 5)
- [ ] AI Overview warning flag emitted when detected
- [ ] All SerpFeatures fields are boolean (never null/undefined)
- [ ] Property tests: all booleans, PAA array length 0-5
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write detector, normalisation logic, tests
- Ask: add new SERP feature types beyond design
- Never: skip normalisation for any source

---

## Task T-005: DataForSEO Adapter
**Story:** US-001 (Top-10 SERP Result Scraping)
**Size:** M
**Depends on:** T-002 (SerpDataSource interface), T-003 (Rate Limiter), T-004 (SerpFeatureDetector)
**Parallel:** No

### What
Implement the DataForSEO adapter that fetches SERP data via the DataForSEO REST API, maps the response to the internal schema, and integrates with the rate limiter and feature detector. Includes retry with exponential backoff (3x: 2s, 4s, 8s).

### Files
- Create: `modules/content-engine/research/adapters/dataforseo-adapter.ts`
- Create: `modules/content-engine/research/adapters/__tests__/dataforseo-adapter.test.ts`
- Create: `modules/content-engine/research/adapters/__fixtures__/dataforseo-responses.json`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (ADR-F004-001)

### Test Scenarios (from tests.md)
- ATS-001: Happy path — 10 organic results returned
- ATS-005: API failure with 3x retry and graceful degradation
- ATS-006: Zero organic results (AI Overview only)
- INT-001: DataForSEO round-trip with recorded response
- INT-007: Credential security (env vars only)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Implements `SerpDataSource` interface
- [ ] Fetches top-10 organic results with position, URL, title, meta description, domain
- [ ] Content type mapped from DataForSEO response fields
- [ ] Reads credentials from `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` env vars
- [ ] Retry with exponential backoff: 2s, 4s, 8s (max 3 retries)
- [ ] Returns `serp_unavailable` error on persistent failure
- [ ] Rate limiter checked before each request
- [ ] Tests use recorded API responses (msw), no live API calls
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write adapter, retry logic, tests with fixtures
- Ask: add support for top-20 results
- Never: store credentials in code, bypass rate limiter

---

## Task T-006: SerpSnapshotRepo (Database + File Adapters)
**Story:** US-003 (SERP Snapshot Persistence)
**Size:** M
**Depends on:** T-001 (Schema)
**Parallel:** Yes [P] (parallel with T-004, T-005)

### What
Implement the `SerpSnapshotPort` interface with two implementations: `DatabaseSerpSnapshotRepo` (PostgreSQL via Drizzle) and `FileSerpSnapshotRepo` (JSON files for standalone mode). Both support create, getLatest (with cache TTL), and getHistory queries.

### Files
- Create: `modules/content-engine/research/ports/serp-snapshot-port.ts`
- Create: `modules/content-engine/research/repos/db-serp-snapshot-repo.ts`
- Create: `modules/content-engine/research/repos/file-serp-snapshot-repo.ts`
- Create (tests): `modules/content-engine/research/repos/__tests__/serp-snapshot-repo.test.ts`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (Queries section)

### Test Scenarios (from tests.md)
- ATS-015: First snapshot created with all fields
- ATS-016: Cache hit — snapshot within 7 days served from cache
- ATS-017: Cache miss — fresh fetch triggered when snapshot > 7 days
- ATS-018: Trend comparison across multiple snapshots
- ATS-019: Standalone file mode
- ATS-020: Configurable cache TTL
- INT-008: DB vs JSON storage parity
- PI-011: Snapshots append-only (never overwrite)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `SerpSnapshotPort` interface defined with create/getLatest/getHistory
- [ ] `DatabaseSerpSnapshotRepo` persists to PostgreSQL via Drizzle
- [ ] `FileSerpSnapshotRepo` persists to `data/serp/{domain}/{language}/{keyword_slug}-{timestamp}.json`
- [ ] `getLatest` respects configurable cache TTL (default 7 days, `SERP_CACHE_DAYS` env var)
- [ ] Both adapters produce identical query results (parity integration test)
- [ ] Property test: snapshot ordering always newest-first
- [ ] Tests pass (testcontainers for DB, tmp dir for files)
- [ ] No regression

### Boundaries
- Always: write repos, port interface, tests
- Ask: change cache TTL default
- Never: overwrite existing snapshots, skip tenant_id

---

## Task T-007: AnalyseSerpCommand + BatchAnalyseSerpCommand
**Story:** US-001, US-002, US-003 (all user stories)
**Size:** L
**Depends on:** T-001, T-002, T-003, T-004, T-005, T-006
**Parallel:** No

### What
Implement the command handlers that orchestrate the full SERP analysis flow: check cache, check rate limiter, fetch SERP data via adapter, detect features, persist snapshot, emit events. Includes both single-keyword and batch commands. The batch command handles daily limit queueing.

### Files
- Create: `modules/content-engine/research/commands/analyse-serp.ts`
- Create: `modules/content-engine/research/commands/batch-analyse-serp.ts`
- Create: `modules/content-engine/research/events/serp-events.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/analyse-serp.test.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/batch-analyse-serp.test.ts`
- Read (context): `specs/001-autonomous-content-engine/E-001-research-strategy/F-004-serp-analysis/design.md` (Commands section)

### Test Scenarios (from tests.md)
- ATS-001: Happy path end-to-end
- ATS-004: Daily limit reached, error returned
- ATS-005: API failure, graceful degradation
- ATS-006: Zero organic results, flagged
- ATS-014: AI Overview warning propagates to F-007
- INT-003: F-001 output as input
- INT-004, INT-005: F-004 output consumed by F-005, F-006
- NFR-4: Retry with exponential backoff, no pipeline halt on failure
- NFR-17: Remaining keywords queued when limit reached

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `AnalyseSerpCommand` orchestrates: cache check -> rate limit -> fetch -> detect features -> persist -> emit event
- [ ] `BatchAnalyseSerpCommand` processes keyword array, tracks completed/cached/failed/queued counts
- [ ] Returns `from_cache: true` when serving cached snapshot
- [ ] Emits `SerpAnalysisCompleted` event per snapshot
- [ ] Emits `SerpDailyLimitReached` event when limit hit, queues remaining keywords
- [ ] Cost estimate calculated and logged per request
- [ ] Structured JSON logging: keywords fetched, features detected, API calls, daily counter, cost, duration
- [ ] Tests pass with mock adapter and mock repo
- [ ] No regression

### Boundaries
- Always: write commands, event emitters, logging, tests
- Ask: add new command variants, change event schema
- Never: skip rate limiter check, delete snapshots
