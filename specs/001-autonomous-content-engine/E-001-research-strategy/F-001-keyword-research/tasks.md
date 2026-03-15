# F-001: Keyword Research / Gap Analysis — Tasks

## Task T-001: Keyword Schema & Migration [Foundation]
**Story:** US-005 (Keyword Output & Persistence)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Create the Drizzle schema for `keyword`, `keyword_metric`, and `keyword_gap` tables as defined in design.md. Generate Zod validation schemas via `drizzle-zod`. Write the migration file with RLS policies for all three tables. Define shared enums (`keywordSourceEnum`, `gapStatusEnum`, `difficultySourceEnum`) and the `KeywordRecord` contract type used by downstream features.

### Files
- Create: `modules/content-engine/research/schema/keyword.ts`
- Create: `modules/content-engine/research/contracts/keyword-record.ts`
- Create: `modules/content-engine/research/migrations/0001_keyword_tables.sql`
- Create (tests): `modules/content-engine/research/schema/__tests__/keyword.schema.test.ts`
- Read (context): `epic-design.md` (ADR-E001-004 RLS pattern)

### Test Scenarios (from tests.md)
- PI-001: Non-empty keyword text
- PI-002: Valid language tag
- PI-008: Tenant isolation (tenant_id non-null)
- PI-009: No duplicate keywords (unique constraint on normalized_key + campaign)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] All three tables defined with correct column types and constraints
- [ ] RLS policies applied in the same migration
- [ ] Zod schemas auto-generated from Drizzle schema
- [ ] `KeywordRecord` contract type exported for F-002, F-003, F-007 consumption
- [ ] Dedup unique index on `(campaignId, normalizedKey)` works
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write schema code, run tests, validate RLS
- Ask: change column types that affect F-002/F-003 contracts
- Never: skip RLS on tenant_id tables, store secrets in code

---

## Task T-002: Storage Port & Adapters [Foundation]
**Story:** US-005 (Keyword Output & Persistence)
**Size:** M
**Depends on:** T-001
**Parallel:** No

### What
Implement the `KeywordStoragePort` interface with two adapters: `DatabaseKeywordAdapter` (Drizzle + PostgreSQL) and `JsonFileKeywordAdapter` (standalone JSON mode). Both must support `save`, `update`, `getByDomain`, `getGapKeywords`, and `getTrends` queries. The JSON adapter writes to `data/keywords/{domain}/{language}.json`.

### Files
- Create: `modules/content-engine/research/ports/keyword-storage.port.ts`
- Create: `modules/content-engine/research/adapters/database-keyword.adapter.ts`
- Create: `modules/content-engine/research/adapters/json-file-keyword.adapter.ts`
- Create (tests): `modules/content-engine/research/ports/__tests__/keyword-storage.port.test.ts`
- Create (tests): `modules/content-engine/research/adapters/__tests__/database-keyword.adapter.test.ts`
- Create (tests): `modules/content-engine/research/adapters/__tests__/json-file-keyword.adapter.test.ts`
- Read (context): `contracts/keyword-record.ts`

### Test Scenarios (from tests.md)
- ATS-018: First run persistence (150 records saved)
- ATS-019: Second run deduplication (update, not duplicate)
- ATS-020: Downstream query interface (`getKeywordsByDomain` with filters)
- ATS-021: Standalone JSON mode
- INT-006: Database vs JSON storage parity

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Both adapters produce identical query results for same input data
- [ ] Upsert logic: second run updates existing records, flags >30% volume delta
- [ ] JSON adapter writes valid, parseable files
- [ ] Database adapter uses Drizzle ORM (no raw SQL)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change storage port interface
- Never: skip tests, bypass RLS, use raw SQL

---

## Task T-003: Keyword Normalisation & Deduplication [Domain Logic]
**Story:** US-001 (Seed Keyword Discovery)
**Size:** S
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Implement keyword normalisation (lowercase, trim, collapse whitespace) and two-phase deduplication: exact hash-based dedup, then sorted-token fuzzy match per ADR-F001-002. The fuzzy match merges variants, keeping the highest-volume term as canonical.

### Files
- Create: `modules/content-engine/research/domain/keyword-normaliser.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/keyword-normaliser.test.ts`

### Test Scenarios (from tests.md)
- PI-009: No duplicate keywords after dedup
- Design P1: `normalise(normalise(keyword)) === normalise(keyword)` (idempotent)
- Design P2: `dedup(keywords).length <= keywords.length` (never grows)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Exact dedup removes identical normalised strings
- [ ] Fuzzy dedup merges word-order variants ("hair transplant cost" ↔ "cost of hair transplant")
- [ ] Canonical keyword selected by highest volume
- [ ] Property-based tests verify idempotency and non-growth
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change dedup strategy (affects downstream data quality)
- Never: use LLM for dedup (too expensive for pre-processing)

---

## Task T-004: URL Crawler & Seed Extractor [Domain Logic]
**Story:** US-001 (Seed Keyword Discovery)
**Size:** L
**Depends on:** T-003
**Parallel:** Yes [P]

### What
Build the URL crawler that extracts seed keywords from a target website. Fetch `sitemap.xml` first; if absent, BFS crawl homepage + internal links (max depth 2, max 50 pages). Extract keywords from `<title>`, `<meta description>`, `<h1>`-`<h3>`, and product category breadcrumbs using cheerio. Validate URLs (block private IPs, limit redirects to 3) per STRIDE-Lite.

### Files
- Create: `modules/content-engine/research/domain/url-crawler.ts`
- Create: `modules/content-engine/research/domain/seed-extractor.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/url-crawler.test.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/seed-extractor.test.ts`
- Create: `modules/content-engine/research/__fixtures__/sitemap.xml`
- Create: `modules/content-engine/research/__fixtures__/sample-page.html`
- Read (context): `design.md` (ADR-F001-001 crawl strategy)

### Test Scenarios (from tests.md)
- ATS-001: Happy path — URL with sitemap returns 20+ seeds
- ATS-003: Small site (3 pages) returns 10+ seeds
- ATS-004: No sitemap falls back to BFS crawl
- ATS-005: Invalid URL returns clear error message

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Sitemap-first strategy with BFS fallback implemented
- [ ] SSRF mitigations: private IP block, redirect limit, scheme allowlist
- [ ] Extracts keywords from title, meta, headings, breadcrumbs
- [ ] Max 50 pages crawled
- [ ] MSW mocks used for HTTP calls in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, validate URL safety
- Ask: add npm dependency (cheerio expected)
- Never: make real HTTP calls in unit tests, skip SSRF validation

---

## Task T-005: Google Autocomplete Adapter [Data Source]
**Story:** US-001 (Seed Keyword Discovery)
**Size:** S
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the `GoogleAutocompleteAdapter` conforming to the `KeywordDataSource` interface. Queries `suggestqueries.google.com` with locale parameter. Enforces rate limiting (100 req/day, 2-second delays). Parses XML response into keyword suggestions.

### Files
- Create: `modules/content-engine/research/adapters/google-autocomplete.adapter.ts`
- Create (tests): `modules/content-engine/research/adapters/__tests__/google-autocomplete.adapter.test.ts`
- Create: `modules/content-engine/research/__fixtures__/autocomplete-response.xml`
- Read (context): `epic-design.md` (KeywordDataSource interface)

### Test Scenarios (from tests.md)
- INT-002: Rate limiting (2s spacing, max 100/day)
- ATS-001: Expansion to 50+ suggestions per language

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Implements `KeywordDataSource` interface (capabilities: `suggestions`)
- [ ] Rate limiter enforces 2-second delay and 100 req/day cap
- [ ] XML response parsed correctly
- [ ] MSW mock used for HTTP calls in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change KeywordDataSource interface (epic-level contract)
- Never: make real HTTP calls in tests, exceed rate limits

---

## Task T-006: Keywords Everywhere Adapter [Data Source]
**Story:** US-002 (Volume & Metrics Enrichment)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the `KeywordsEverywhereAdapter` conforming to `KeywordDataSource`. Batch POST endpoint accepting up to 100 keywords per call. Supports multi-locale enrichment via `country` parameter. Parses volume, CPC, and 12-month trend array. Implements retry with exponential backoff (max 3 retries). API key read from environment variable.

### Files
- Create: `modules/content-engine/research/adapters/keywords-everywhere.adapter.ts`
- Create (tests): `modules/content-engine/research/adapters/__tests__/keywords-everywhere.adapter.test.ts`
- Create: `modules/content-engine/research/__fixtures__/keywords-everywhere-response.json`
- Read (context): `epic-design.md` (KeywordDataSource interface)

### Test Scenarios (from tests.md)
- ATS-006: Happy path — volume, CPC, trend returned
- ATS-007: Multi-language enrichment (3 separate records)
- ATS-008: Zero volume keyword retained
- ATS-009: Batch efficiency (150 keywords = 2 calls)
- ATS-010: API error with retry and graceful degradation
- INT-001: API round-trip
- INT-007: API key from environment
- Design P5: `enrichBatch.apiCalls <= ceil(keywords.length / 100)`

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Implements `KeywordDataSource` interface (capabilities: `volume`, `suggestions`, `trends`)
- [ ] Batch size capped at 100 keywords per API call
- [ ] Retry with exponential backoff on 429/5xx errors
- [ ] API key read from `KEYWORDS_EVERYWHERE_API_KEY` env var
- [ ] Key never appears in logs (redaction middleware)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change batch size, add new API endpoint
- Never: hardcode API keys, make real API calls in tests

---

## Task T-007: Keyword Difficulty Estimator [Domain Logic]
**Story:** US-003 (Keyword Difficulty Estimation)
**Size:** M
**Depends on:** T-005, T-006
**Parallel:** No

### What
Implement the heuristic difficulty estimator (0-100 scale) using three signals: Google Autocomplete depth, volume bracket, and LLM assessment of top-ranking domain authority. Flag all heuristic scores as `source: "heuristic"` with rationale text. Abstract behind the `KeywordDataSource` interface so DataForSEO can replace it later.

### Files
- Create: `modules/content-engine/research/domain/difficulty-estimator.ts`
- Create: `modules/content-engine/research/prompts/difficulty-heuristic-v1.txt`
- Create (tests): `modules/content-engine/research/domain/__tests__/difficulty-estimator.test.ts`
- Create: `modules/content-engine/research/__fixtures__/difficulty-heuristic-response.json`

### Test Scenarios (from tests.md)
- ATS-011: Low difficulty keyword (~15)
- ATS-012: High difficulty keyword (~85)
- ATS-013: DataForSEO source swap (adapter pattern)
- PI-004: Difficulty range 0-100
- PI-006: Difficulty source tagged

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Heuristic uses autocomplete depth + volume + LLM assessment
- [ ] All scores flagged `source: "heuristic"` with rationale
- [ ] DataForSEO adapter slot exists (not implemented, just interface)
- [ ] LLM prompt versioned in `prompts/` directory
- [ ] Mock AI gateway used in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, version prompts
- Ask: change scoring formula (affects downstream prioritisation)
- Never: use inline prompt strings, skip source tagging

---

## Task T-008: Keyword Gap Analyser [Domain Logic]
**Story:** US-004 (Gap Analysis vs Competitors)
**Size:** L
**Depends on:** T-002, T-006
**Parallel:** No

### What
Implement the keyword gap analysis comparing user domain vs competitor domains. When GSC data is available, use it as authoritative source of "keywords we rank for". When GSC is absent, fall back to SERP-based discovery (check if user domain appears in top 50 for each keyword). Produce deduplicated gap list across multiple competitors with position data.

### Files
- Create: `modules/content-engine/research/domain/gap-analyser.ts`
- Create: `modules/content-engine/research/adapters/google-search-console.adapter.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/gap-analyser.test.ts`
- Create (tests): `modules/content-engine/research/adapters/__tests__/google-search-console.adapter.test.ts`
- Read (context): `design.md` (gap analysis flow)

### Test Scenarios (from tests.md)
- ATS-014: Happy path with GSC data
- ATS-015: No GSC fallback to SERP-based discovery
- ATS-016: No gaps found — returns message
- ATS-017: Multiple competitors — unified deduplicated list
- INT-003: GSC OAuth integration

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] GSC-first strategy with SERP fallback implemented
- [ ] Gap keywords include competitor URL, position, and volume
- [ ] Multiple competitors produce deduplicated unified list
- [ ] GSC adapter implements `KeywordDataSource` interface
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change gap analysis algorithm, add competitor data source
- Never: make real GSC API calls in tests, bypass tenant isolation

---

## Task T-009: Research Pipeline Orchestrator [Integration]
**Story:** All user stories
**Size:** L
**Depends on:** T-003, T-004, T-005, T-006, T-007, T-008
**Parallel:** No

### What
Implement the `RunKeywordResearch` command handler that orchestrates the full F-001 pipeline: URL crawl → seed extraction → autocomplete expansion → dedup → volume enrichment → difficulty estimation → gap analysis → persistence. Emits `KeywordResearchCompletedEvent` on success. Handles partial failures gracefully (continue with remaining keywords if one step fails for some).

### Files
- Create: `modules/content-engine/research/commands/run-keyword-research.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/run-keyword-research.test.ts`
- Modify: `modules/content-engine/research/index.ts` (export command)
- Read (context): `design.md` (API contracts, event schema)

### Test Scenarios (from tests.md)
- ATS-001: Full happy path — URL to keyword output
- INT-004: F-001 output compatible with F-002 input
- INT-005: F-001 output compatible with F-003 input
- NFR 1: 50 seeds processed within 5 minutes
- NFR 4: API failure retry with no data loss

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Full pipeline executes: crawl → expand → dedup → enrich → difficulty → gap → persist
- [ ] `RunKeywordResearchResult` returned with counts and duration
- [ ] `KeywordResearchCompletedEvent` emitted on success
- [ ] Structured JSON logging: keywords found, API calls, credits, duration
- [ ] Partial failure does not halt the full pipeline
- [ ] Feature flag `FEATURE_KEYWORD_RESEARCH` checked at entry
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change event schema
- Never: skip tests, bypass feature flag

---

## Task T-010: Config Validation & Module Bootstrap [Foundation]
**Story:** US-005, NFR 5, NFR 11
**Size:** S
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Create the module configuration schema (Zod) that validates API keys, feature flags, and adapter selection at startup. Expose a `createResearchModule()` factory that wires adapters based on config (database vs JSON, Keywords Everywhere key present or mock mode). Ensure tests run without API keys by supporting mock adapter injection.

### Files
- Create: `modules/content-engine/research/config.ts`
- Create: `modules/content-engine/research/module.ts`
- Create (tests): `modules/content-engine/research/__tests__/config.test.ts`
- Read (context): `epic-design.md` (module pattern)

### Test Scenarios (from tests.md)
- NFR 5: API keys from environment, never hardcoded
- NFR 11: Tests run without API keys (mock mode)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Zod config schema validates all required env vars
- [ ] Missing required keys fail fast with clear error message
- [ ] Mock adapter mode enabled when `NODE_ENV=test`
- [ ] Feature flag `FEATURE_KEYWORD_RESEARCH` defaults to false
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new config parameters
- Never: store secrets in code, skip config validation
