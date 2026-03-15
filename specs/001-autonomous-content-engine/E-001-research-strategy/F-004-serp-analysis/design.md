---
id: "FTR-SEO-004"
type: feature
title: "SERP Analysis"
project: PROD-001
domain: seo.content-pipeline
parent: "PROD-001-SPEC-E-001"
status: draft
phase: 4-design
created: 2026-03-15
last_updated: 2026-03-15
refs:
  requirements: "./requirements.md"

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

# F-004: SERP Analysis — Design

## Architecture Overview

F-004 sits between keyword research (F-001) and downstream consumers (F-005, F-006). It fetches SERP data for each keyword, detects SERP features, and persists timestamped snapshots.

```
F-001 Keywords ──→ [SerpAnalysisCommand]
                        │
                        ▼
                   [RateLimiter]
                        │
                        ▼
                   [SerpDataSource] ◄── interface
                    ╱          ╲
          DataForSEO        GoogleScraper
          Adapter            Adapter
                        │
                        ▼
                   [SerpFeatureDetector]
                        │
                        ▼
                   [SerpSnapshotRepo] ──→ PostgreSQL / JSON file
                        │
                        ▼
              F-005 + F-006 (consumers)
```

## Architecture Decision Records

### ADR-F004-001: SERP Data Source Abstraction

**Status:** Proposed
**Context:** We need DataForSEO for R1 month 3+ but Google scraping as a fallback for months 1-2. Future providers (SerpAPI, Brightdata) are possible.
**Decision:** Implement the `SerpDataSource` interface from epic ADR-E001-002. Each provider gets its own adapter. A `SerpSourceSelector` picks the active adapter from config.
**Alternatives considered:**
1. Single DataForSEO adapter with inline fallback — tightly coupled, hard to test, violates open-closed principle.
2. Strategy pattern with runtime switching — functionally identical to adapter but less explicit about the data transformation role.
**Consequences:** Two adapters to maintain. Mock adapter makes testing trivial. New providers are one class each.

### ADR-F004-002: Rate Limiting Strategy

**Status:** Proposed
**Context:** DataForSEO charges per request (~$0.0006). Google scraping risks IP blocks. Both need rate limiting but with different limits (50/day vs 30/day + 5s delay).
**Decision:** Token bucket rate limiter with per-source configuration. Daily counter stored in Redis (key: `serp:daily:{source}:{date}`) with midnight UTC reset. The limiter is injected into each adapter, not embedded.
**Alternatives considered:**
1. In-adapter rate limiting — duplicates logic across adapters. Harder to monitor globally.
2. BullMQ rate limiter — BullMQ has built-in rate limiting, but it operates at the queue level, not per-provider. We need per-source limits.
**Consequences:** Requires Redis (already available for BullMQ). Daily counter survives process restarts. Rate limit config lives in env vars (`SERP_DAILY_LIMIT_DATAFORSEO=50`, `SERP_DAILY_LIMIT_GOOGLE=30`).

### ADR-F004-003: SERP Feature Detection as Post-Processing

**Status:** Proposed
**Context:** SERP features can be detected from the API response (DataForSEO returns feature flags) or parsed from raw HTML (Google scraper). Different sources provide features differently.
**Decision:** SERP feature detection is a separate `SerpFeatureDetector` class that normalises feature flags from any source into a canonical `SerpFeatures` object. DataForSEO adapter maps API response fields; Google scraper adapter parses HTML indicators.
**Alternatives considered:**
1. Feature detection inside each adapter — duplicates the normalisation logic.
2. Single unified parser — doesn't work because DataForSEO returns structured JSON, not HTML.
**Consequences:** Each adapter must implement a `mapFeatures()` method. The detector validates completeness (warns if AI Overview detection is unsupported by the source).

## Data Model

### Drizzle Schema

```typescript
import { pgTable, uuid, text, integer, timestamp, boolean, jsonb, index } from 'drizzle-orm/pg-core';

// --- serp_snapshot ---
export const serpSnapshot = pgTable('serp_snapshot', {
  id: text('id').primaryKey(),                              // ss_xxx (prefixed UUID)
  tenant_id: uuid('tenant_id').notNull(),
  keyword_id: text('keyword_id').notNull()
    .references(() => keyword.id),
  keyword_text: text('keyword_text').notNull(),             // denormalised for query convenience
  language: text('language').notNull(),                     // BCP 47: "de", "en", "fr"
  country: text('country').notNull(),                      // ISO 3166-1: "DE", "GB"
  fetched_at: timestamp('fetched_at', { withTimezone: true }).notNull(),
  api_source: text('api_source').notNull(),                // "dataforseo" | "google_scrape" | "mock"
  result_count: integer('result_count').notNull().default(0),
  no_organic_results: boolean('no_organic_results').notNull().default(false),

  // SERP features (flat booleans for queryability)
  has_ai_overview: boolean('has_ai_overview').notNull().default(false),
  has_featured_snippet: boolean('has_featured_snippet').notNull().default(false),
  has_people_also_ask: boolean('has_people_also_ask').notNull().default(false),
  has_knowledge_panel: boolean('has_knowledge_panel').notNull().default(false),
  has_image_pack: boolean('has_image_pack').notNull().default(false),
  has_video_carousel: boolean('has_video_carousel').notNull().default(false),
  has_local_pack: boolean('has_local_pack').notNull().default(false),
  has_shopping_results: boolean('has_shopping_results').notNull().default(false),
  paa_questions: jsonb('paa_questions').$type<string[]>().default([]),

  // Pipeline tracking
  pipeline_run_id: text('pipeline_run_id'),
  cost_estimate_usd: text('cost_estimate_usd'),            // text to avoid float issues

  created_at: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('serp_snapshot_tenant_idx').on(table.tenant_id),
  keywordIdx: index('serp_snapshot_keyword_idx').on(table.tenant_id, table.keyword_id),
  latestIdx: index('serp_snapshot_latest_idx').on(table.tenant_id, table.keyword_text, table.language, table.fetched_at),
}));

// --- serp_result (child of serp_snapshot) ---
export const serpResult = pgTable('serp_result', {
  id: text('id').primaryKey(),                              // sr_xxx
  tenant_id: uuid('tenant_id').notNull(),
  snapshot_id: text('snapshot_id').notNull()
    .references(() => serpSnapshot.id, { onDelete: 'cascade' }),
  position: integer('position').notNull(),                  // 1-10
  url: text('url').notNull(),
  domain: text('domain').notNull(),
  title: text('title'),
  meta_description: text('meta_description'),
  estimated_word_count: integer('estimated_word_count'),
  content_type: text('content_type'),                       // "blog" | "product_page" | "category_page" | "video" | "tool" | "news" | "other"

  created_at: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  snapshotIdx: index('serp_result_snapshot_idx').on(table.snapshot_id),
  tenantIdx: index('serp_result_tenant_idx').on(table.tenant_id),
}));
```

### RLS Policies

```sql
ALTER TABLE serp_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE serp_result ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON serp_snapshot
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
CREATE POLICY tenant_isolation ON serp_result
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

## API Contracts

### Commands

```typescript
// --- AnalyseSerpCommand ---
interface AnalyseSerpInput {
  tenant_id: string;
  keyword_id: string;
  keyword_text: string;
  language: string;         // BCP 47
  country: string;          // ISO 3166-1
  pipeline_run_id?: string;
  force_refresh?: boolean;  // bypass cache TTL
}

interface AnalyseSerpOutput {
  snapshot_id: string;
  result_count: number;
  serp_features: SerpFeatures;
  from_cache: boolean;
  cost_estimate_usd: string;
}

type AnalyseSerpResult = Result<AnalyseSerpOutput, SerpError>;

// --- BatchAnalyseSerpCommand ---
interface BatchAnalyseSerpInput {
  tenant_id: string;
  keywords: Array<{ keyword_id: string; keyword_text: string; language: string; country: string }>;
  pipeline_run_id: string;
}

interface BatchAnalyseSerpOutput {
  completed: number;
  cached: number;
  failed: number;
  queued_for_tomorrow: number;     // hit daily limit
  snapshots: AnalyseSerpOutput[];
  errors: Array<{ keyword_id: string; error: string }>;
}
```

### Queries

```typescript
// --- GetLatestSerpSnapshot ---
interface GetLatestSnapshotInput {
  tenant_id: string;
  keyword_text: string;
  language: string;
  max_age_days?: number;          // default: 7 (SERP_CACHE_DAYS)
}

type GetLatestSnapshotResult = Result<SerpSnapshotRecord | null, QueryError>;

// --- GetSerpHistory ---
interface GetSerpHistoryInput {
  tenant_id: string;
  keyword_text: string;
  language: string;
  limit?: number;                 // default: 10
}

type GetSerpHistoryResult = Result<SerpSnapshotRecord[], QueryError>;
```

### Shared Types

```typescript
interface SerpFeatures {
  ai_overview: boolean;
  featured_snippet: boolean;
  people_also_ask: boolean;
  paa_questions: string[];
  knowledge_panel: boolean;
  image_pack: boolean;
  video_carousel: boolean;
  local_pack: boolean;
  shopping_results: boolean;
}

type SerpError =
  | { code: 'RATE_LIMIT_EXCEEDED'; daily_count: number; limit: number; next_reset: string }
  | { code: 'API_UNAVAILABLE'; source: string; retries_attempted: number }
  | { code: 'INVALID_INPUT'; field: string; message: string };
```

### Events

```typescript
// Emitted after each SERP snapshot is created
interface SerpAnalysisCompleted {
  type: 'research.serp.analysed';
  tenant_id: string;
  keyword_id: string;
  snapshot_id: string;
  has_ai_overview: boolean;
  result_count: number;
}

// Emitted when daily limit hit
interface SerpDailyLimitReached {
  type: 'research.serp.daily_limit_reached';
  tenant_id: string;
  source: string;
  daily_count: number;
  queued_keywords: number;
}
```

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **Info Disclosure** — Cross-tenant SERP data leakage | H | RLS on both tables. `tenant_id` in every query. CI gate validates RLS policy exists. |
| **DoS** — Exhausting DataForSEO credits via runaway pipeline | M | Token bucket rate limiter with daily cap. Redis-persisted counter. Alert at 80% of daily limit. Circuit breaker: 3 consecutive API failures halts requests for 10 minutes. |

## ATAM-Lite

| Decision | Quality Attribute | Sensitivity | Trade-off |
|----------|------------------|:-----------:|-----------|
| Snapshot per fetch (never overwrite) | **Auditability** vs Storage | High | More disk/rows, but enables trend detection. At 50 snapshots/day, growth is ~1.5K rows/month — negligible. |
| Feature detection as post-processing | **Modifiability** vs Simplicity | Medium | Extra class, but isolates the normalisation logic. Adding a new SERP feature is one field + one mapping line. |
| Per-source rate limits in Redis | **Reliability** vs Complexity | High | Survives restarts. Redis dependency already exists for BullMQ. Alternative (in-memory counter) resets on crash, risking overuse. |

## Build Boundaries

### Always (no approval needed)
- Write adapters, commands, queries within this design
- Run tests, fix failures, refactor within F-004 scope
- Create mock adapter and fixture data
- Update specs and docs

### Ask First
- Add a new SERP data source adapter beyond DataForSEO and Google
- Change the SerpSnapshot schema after Gate 3
- Modify rate limit defaults beyond what's in requirements

### Never
- Store DataForSEO credentials in code
- Bypass rate limiter
- Delete SERP snapshots (append-only design)
- Skip RLS on any table

## Test Architecture

### Test Pyramid

| Level | Count | What | Tools |
|-------|:-----:|------|-------|
| Unit | ~20 | Rate limiter logic, feature detection normalisation, cache TTL checks, content type mapping | Vitest |
| Integration | ~8 | DataForSEO adapter with recorded responses, Google scraper adapter with fixture HTML, snapshot persistence round-trip, batch command with daily limit | Vitest + testcontainers (PostgreSQL) |
| Property | ~3 | Rate limiter never exceeds configured limit (fast-check), snapshot ordering is always newest-first, all SerpFeatures booleans are set | Vitest + fast-check |

### Mocking Strategy

- **SerpDataSource**: `MockSerpDataSource` returns fixture snapshots. Configured via dependency injection.
- **Redis (rate limiter)**: In-memory Map for unit tests. Real Redis via testcontainers for integration.
- **Database**: testcontainers PostgreSQL for integration tests. Pure function tests need no DB.
- **HTTP (Google scraper)**: `msw` (Mock Service Worker) to intercept HTTP requests with fixture HTML responses.

### Property Invariants

1. `daily_request_count <= SERP_DAILY_LIMIT` — for any sequence of calls within a UTC day, the counter never exceeds the configured limit.
2. `getLatestSerpSnapshot` returns the snapshot with the most recent `fetched_at` — for any set of snapshots for the same keyword, ordering is deterministic.
3. All `SerpFeatures` fields are booleans — no null, no undefined. `paa_questions` is always an array (possibly empty).

## NFR Implementation

| NFR | Requirement | Implementation | CI Gate |
|-----|-------------|----------------|---------|
| #4 Reliability (retry) | 3x exponential backoff on API failure | `withRetry(fn, { maxAttempts: 3, delays: [2000, 4000, 8000] })` utility wrapping adapter calls | Yes — integration test with mock 503 responses |
| #5 Security (no credentials in code) | Env vars only | `SerpConfig` reads from `process.env`. eslint rule `no-hardcoded-credentials`. | Yes — pre-commit grep scan |
| #8 Interoperability (SerpSnapshot schema) | Zod validation on output | `serpSnapshotSchema` generated via `drizzle-zod`. All outputs validated before return. | Yes — unit test round-trip |
| #9 Portability (standalone mode) | JSON file storage fallback | `SerpSnapshotPort` interface with `DatabaseSerpSnapshotRepo` and `FileSerpSnapshotRepo` implementations | Yes — integration test both adapters |
| #11 Testability (mock data source) | No API keys in tests | `MockSerpDataSource` in test fixtures. CI env has no `DATAFORSEO_*` vars. | Yes — CI runs without credentials |
