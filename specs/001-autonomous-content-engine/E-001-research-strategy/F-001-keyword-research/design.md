# F-001: Keyword Research / Gap Analysis — Design

> Feature-level architecture decisions, data model, API contracts, and test strategy.
> Cross-cutting decisions (pipeline orchestration, tenant isolation, caching) are in `epic-design.md`.

---

## Architecture ADRs

### ADR-F001-001: URL Crawling Strategy for Seed Extraction

**Status:** Proposed
**Context:** US-001 requires extracting seed keywords from a user's website. Need to decide how deeply to crawl and what to extract.
**Decision:** Fetch `sitemap.xml` first. If present, extract up to 50 page URLs. If absent, crawl homepage + internal links (BFS, max depth 2, max 50 pages). From each page, extract: `<title>`, `<meta name="description">`, `<h1>`-`<h3>`, product category breadcrumbs. Use cheerio for HTML parsing.
**Alternatives considered:**
1. Full recursive crawl — Too slow, unbounded. Risk of crawling thousands of pages.
2. Homepage only — Too few seeds for keyword discovery.
3. Third-party crawl API (ScreamingFrog API, Sitebulb) — Unnecessary dependency for seed extraction.
**Consequences:** Simple, bounded crawl. May miss deep pages on large sites, but 50 pages is sufficient for seed generation. Cheerio keeps dependency footprint small.

### ADR-F001-002: Keyword Deduplication and Normalisation

**Status:** Proposed
**Context:** Keywords from multiple sources (URL extraction, autocomplete, manual seeds) will contain duplicates and near-duplicates ("hair transplant cost" vs "cost of hair transplant").
**Decision:** Two-phase deduplication:
1. **Exact match** — normalise to lowercase, trim whitespace, collapse multiple spaces. Hash-based dedup.
2. **Fuzzy match** — sort tokens alphabetically, compare. "cost of hair transplant" and "hair transplant cost" produce the same sorted-token key. Merge fuzzy matches, keeping the variant with higher volume as canonical.
**Alternatives considered:**
1. LLM-based dedup — Expensive and slow for a pre-processing step. Reserve LLM budget for clustering (F-002).
2. Levenshtein distance — Catches typos but misses word-order variants. Sorted-token approach is simpler and sufficient.
**Consequences:** Some semantic near-duplicates may survive (e.g., "hair transplant" vs "hair transplantation"). Acceptable for R1 — F-002 clustering will group these.

### ADR-F001-003: Multi-Locale Architecture

**Status:** Proposed
**Context:** US-002 requires keyword enrichment across 9 languages. Each keyword can have different volume/CPC per locale.
**Decision:** Store keyword-locale pairs as separate rows in `keyword_metric` (one keyword text can have 9 metric rows). The `keyword` table stores the canonical term; `keyword_metric` stores per-locale volume/CPC/trend data. Keywords Everywhere API accepts a `country` parameter — one batch call per locale.
**Alternatives considered:**
1. Single row with JSON locale map — Makes querying by locale difficult. Violates 1NF.
2. Separate tables per locale — Fragmented, hard to manage.
**Consequences:** More rows (keywords x locales), but clean relational model. Indexes on `(keyword_id, locale)` keep queries fast.

---

## Data Model

### Drizzle Schema

```typescript
// modules/content-engine/research/schema/keyword.ts

import { pgTable, uuid, text, integer, real, timestamp, jsonb, pgEnum, index, uniqueIndex } from 'drizzle-orm/pg-core';

export const keywordSourceEnum = pgEnum('keyword_source', [
  'url_extraction', 'autocomplete', 'manual_seed', 'gap_analysis'
]);

export const gapStatusEnum = pgEnum('gap_status', [
  'own_keyword', 'competitor_gap', 'new_opportunity'
]);

export const difficultySourceEnum = pgEnum('difficulty_source', [
  'heuristic', 'datafor_seo'
]);

// Canonical keyword record (one per term per campaign)
export const keyword = pgTable('keyword', {
  id: text('id').primaryKey(),                    // kw_<uuid>
  tenantId: uuid('tenant_id').notNull(),
  campaignId: text('campaign_id').notNull().references(() => campaign.id),
  term: text('term').notNull(),                   // normalised lowercase
  normalizedKey: text('normalized_key').notNull(), // sorted-token key for dedup
  source: keywordSourceEnum('source').notNull(),
  sourceUrl: text('source_url'),                  // page URL it was discovered from
  gapStatus: gapStatusEnum('gap_status').default('new_opportunity'),
  difficulty: integer('difficulty'),               // 0-100
  difficultySource: difficultySourceEnum('difficulty_source'),
  difficultyRationale: text('difficulty_rationale'),
  // Intent fields populated by F-003
  intent: text('intent'),
  intentConfidence: text('intent_confidence'),
  intentRationale: text('intent_rationale'),
  recommendedFormat: text('recommended_format'),
  formatSignal: text('format_signal'),
  classifiedAt: timestamp('classified_at'),
  // Cluster FK populated by F-002
  clusterId: text('cluster_id'),
  discoveredAt: timestamp('discovered_at').defaultNow(),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  tenantIdx: index('keyword_tenant_idx').on(table.tenantId),
  campaignIdx: index('keyword_campaign_idx').on(table.campaignId),
  dedupIdx: uniqueIndex('keyword_dedup_idx').on(table.campaignId, table.normalizedKey),
  clusterIdx: index('keyword_cluster_idx').on(table.clusterId),
}));

// Per-locale volume/CPC/trend data
export const keywordMetric = pgTable('keyword_metric', {
  id: text('id').primaryKey(),                     // km_<uuid>
  tenantId: uuid('tenant_id').notNull(),
  keywordId: text('keyword_id').notNull().references(() => keyword.id),
  locale: text('locale').notNull(),                // "de", "fr", "nl", etc.
  country: text('country').notNull(),              // "DE", "FR", "NL", etc.
  volume: integer('volume'),                       // monthly search volume
  cpc: real('cpc'),                                // cost per click (USD)
  trend: jsonb('trend').$type<number[]>(),         // 12-month array
  dataSource: text('data_source').default('keywords_everywhere'),
  fetchedAt: timestamp('fetched_at').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  keywordLocaleIdx: uniqueIndex('km_keyword_locale_idx').on(table.keywordId, table.locale),
  tenantIdx: index('km_tenant_idx').on(table.tenantId),
  volumeIdx: index('km_volume_idx').on(table.volume),
}));

// Competitor gap records
export const keywordGap = pgTable('keyword_gap', {
  id: text('id').primaryKey(),                     // kg_<uuid>
  tenantId: uuid('tenant_id').notNull(),
  campaignId: text('campaign_id').notNull(),
  keywordId: text('keyword_id').notNull().references(() => keyword.id),
  competitorDomain: text('competitor_domain').notNull(),
  competitorUrl: text('competitor_url'),
  competitorPosition: integer('competitor_position'),
  ourPosition: integer('our_position'),            // null = not ranking
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  tenantIdx: index('kg_tenant_idx').on(table.tenantId),
  campaignKeywordIdx: index('kg_campaign_keyword_idx').on(table.campaignId, table.keywordId),
}));
```

### RLS Policies

All three tables get tenant RLS per ADR-E001-004. Applied in the same migration that creates the tables.

---

## API Contracts

### Commands (Writes)

```typescript
// RunKeywordResearch — orchestrates the full F-001 pipeline
interface RunKeywordResearchCommand {
  tenantId: string;
  campaignId: string;
  targetUrl: string;
  seedKeywords?: string[];              // optional manual seeds
  locales: string[];                    // ["de", "fr", "nl", ...]
  competitors?: string[];              // competitor domains for gap analysis
  options?: {
    maxPages?: number;                  // default 50
    skipEnrichment?: boolean;           // skip volume lookup (testing)
    skipDifficulty?: boolean;           // skip difficulty estimation
  };
}

interface RunKeywordResearchResult {
  runId: string;
  keywordsDiscovered: number;
  keywordsEnriched: number;
  gapKeywordsFound: number;
  localesProcessed: string[];
  duration: number;                     // milliseconds
  apiCreditsUsed: { source: string; credits: number }[];
}

// EnrichKeywordVolume — batch volume lookup (can be called independently)
interface EnrichKeywordVolumeCommand {
  tenantId: string;
  keywordIds: string[];
  locale: string;
  country: string;
}

// EstimateKeywordDifficulty — heuristic or API-based
interface EstimateKeywordDifficultyCommand {
  tenantId: string;
  keywordIds: string[];
  locale: string;
}
```

### Queries (Reads)

```typescript
interface GetKeywordsByDomainQuery {
  tenantId: string;
  campaignId: string;
  filters?: {
    locale?: string;
    minVolume?: number;
    maxDifficulty?: number;
    intent?: 'informational' | 'commercial' | 'transactional' | 'navigational';
    gapStatus?: 'own_keyword' | 'competitor_gap' | 'new_opportunity';
    minConfidence?: 'high' | 'medium';
  };
  pagination?: { limit: number; offset: number };
}

interface GetGapKeywordsQuery {
  tenantId: string;
  campaignId: string;
  competitorDomains: string[];
  minVolume?: number;
}

interface GetKeywordTrendsQuery {
  tenantId: string;
  keywordId: string;
  locale: string;
}
```

### Events (Async Out)

```typescript
// Emitted when F-001 completes — consumed by F-002 and F-003
interface KeywordResearchCompletedEvent {
  type: 'research.keywords.completed';
  tenantId: string;
  campaignId: string;
  runId: string;
  keywordCount: number;
  locales: string[];
}
```

---

## Data Source Adapters

```typescript
// Implements KeywordDataSource from epic-design.md ADR-E001-002

class KeywordsEverywhereAdapter implements KeywordDataSource {
  readonly capabilities = new Set(['volume', 'suggestions', 'trends'] as const);
  // Batch endpoint: POST /keywords/data — accepts up to 100 keywords
  // Rate limit: 1 req/s
  // Auth: X-Api-Key header
}

class GoogleAutocompleteAdapter implements KeywordDataSource {
  readonly capabilities = new Set(['suggestions'] as const);
  // GET http://suggestqueries.google.com/complete/search?output=toolbar&q={seed}&hl={locale}
  // Rate limit: 100 req/day, 2s delay between requests
  // No auth required
}

class DataForSEOAdapter implements KeywordDataSource {
  readonly capabilities = new Set(['volume', 'difficulty', 'serp'] as const);
  // Fallback / R1 month 3+ upgrade
  // Auth: Basic auth (login:password)
}

class GoogleSearchConsoleAdapter implements KeywordDataSource {
  readonly capabilities = new Set(['volume'] as const);
  // For gap analysis: provides "keywords we rank for"
  // Auth: OAuth2 (already connected for Hairgenetix)
}
```

---

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **SSRF via target URL** | H | Validate URL: allowlist `http://` and `https://` schemes only. Block private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, ::1). DNS resolution check before fetch. Max redirect depth = 3. |
| **API key exposure in logs** | M | Never log API keys. Structured logger with key-redaction middleware. API keys from env vars only, validated at startup with Zod config schema. |

---

## ATAM-Lite

| Decision | Quality Attribute | Trade-off |
|----------|------------------|-----------|
| Sorted-token dedup (ADR-F001-002) | Performance vs Accuracy | Fast O(n) dedup. Misses semantic near-dupes ("hair transplant" vs "hair transplantation"). Acceptable — F-002 clustering catches these. |
| Separate `keyword_metric` table (ADR-F001-003) | Normalisation vs Query simplicity | Requires JOIN for volume-filtered queries. Worth it — clean 1NF, easy per-locale queries, avoids JSON column anti-pattern. |
| Heuristic difficulty for R1 | Cost vs Accuracy | Free but estimated. Flagged as "heuristic" in output. Clean upgrade path to DataForSEO via adapter pattern. |

---

## Build Boundaries

| Tier | Actions |
|------|---------|
| **Always** | Write module code, run tests, implement adapters, update prompts, refactor within feature scope |
| **Ask** | Add npm dependency, change KeywordDataSource interface (epic-level), modify shared keyword schema fields consumed by F-002/F-003/F-007 |
| **Never** | Store API keys in code, skip RLS on new tables, bypass dedup (creates dirty data for downstream features), make real API calls in unit tests |

---

## Test Architecture

### Test Pyramid

| Level | Count | What | Framework |
|-------|:-----:|------|-----------|
| Unit | ~25 | Dedup logic, normalisation, URL validation, adapter response parsing, config validation | Vitest |
| Integration | ~10 | Full pipeline with mock adapters, database round-trip (keyword + metric persistence), query filters, gap analysis flow | Vitest + testcontainers (PostgreSQL) |
| Property | ~5 | Dedup idempotency, normalisation stability, batch size invariants | fast-check |
| E2E | 1-2 | Full pipeline with fixture adapters, verify end-to-end keyword output matches expected schema | Vitest |

### Mocking Strategy

- **KeywordDataSource adapters**: Mock at the interface boundary. Fixture files in `__fixtures__/keywords-everywhere-response.json`, `__fixtures__/autocomplete-response.xml`.
- **LLM (difficulty heuristic)**: Mock AI gateway. Fixture in `__fixtures__/difficulty-heuristic-response.json`.
- **Database**: Testcontainers for integration tests. In-memory Map for unit tests of query logic.
- **HTTP (URL crawling)**: MSW (Mock Service Worker) for sitemap and page fetch responses.

### Property Invariants

```
P1: normalise(normalise(keyword)) === normalise(keyword)  // idempotent
P2: dedup(keywords).length <= keywords.length              // never grows
P3: for all kw in dedup(keywords): kw.volume >= 0          // no negative volumes
P4: for all km in keywordMetrics: km.trend.length === 12   // always 12-month array
P5: enrichBatch(keywords, 100).apiCalls <= ceil(keywords.length / 100)  // batch efficiency
```

### Fixture Data

Hairgenetix DE keyword set (50 keywords) as golden fixture for integration tests. Covers: head terms, long-tail, zero-volume, multi-locale, gap keywords.
