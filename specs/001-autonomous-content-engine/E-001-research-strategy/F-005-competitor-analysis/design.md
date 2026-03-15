---
id: "FTR-SEO-005"
type: feature
title: "Competitor Content Analysis"
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

# F-005: Competitor Content Analysis — Design

## Architecture Overview

F-005 takes SERP result URLs from F-004, downloads each page, extracts structural data, runs LLM quality assessment, and stores timestamped snapshots. Downstream consumers (F-006, F-007) query snapshots via the query port.

```
F-004 SerpSnapshot ──→ [CompetitorAnalysisCommand]
                              │
                              ▼
                        [RobotsTxtChecker]
                              │ (skip if disallowed)
                              ▼
                        [PageDownloader]
                              │ (rate-limited: 2 req/s, 500ms same-domain)
                              ▼
                        [ContentExtractor] ◄── cheerio
                              │
                              ├──→ structural fields (word count, headings, schema, links)
                              │
                              ▼
                        [QualityAssessor] ◄── LLM (Claude Haiku)
                              │
                              ▼
                        [CompetitorSnapshotRepo] ──→ PostgreSQL / JSON file
                              │
                              ▼
                    F-006 + F-007 (consumers)
```

## Architecture Decision Records

### ADR-F005-001: HTML Sanitisation Strategy

**Status:** Proposed
**Context:** Competitor pages may contain malicious HTML, XSS payloads, or unexpected encoding. We parse HTML with cheerio and extract text content.
**Decision:** Two-layer sanitisation: (1) cheerio loads HTML in a non-executing context (no script execution by design); (2) extracted text is sanitised with DOMPurify before storage and before LLM input. Raw HTML is never stored — only the MD5 hash for change detection.
**Alternatives considered:**
1. Store raw HTML for re-analysis — storage overhead, security risk, not needed per requirements (structural data only).
2. jsdom instead of cheerio — heavier, slower, includes script execution by default. cheerio is parse-only.
**Consequences:** No raw HTML in the database. If we need to re-analyse, we re-crawl. Hash comparison detects changes without storing content.

### ADR-F005-002: LLM Quality Assessment — Compressed Input

**Status:** Proposed
**Context:** Competitor pages can be 10,000+ words. Sending full text to LLM exceeds token budgets (2K tokens/page cap from NFR). Need to compress without losing quality signal.
**Decision:** Extract a compressed representation: first 2,000 characters of body text + all H2/H3 headings + author bio section (if detected) + any "Sources"/"References" section. Cap total LLM input at 2,000 tokens. Pass to Claude Haiku with a structured output prompt requesting the quality profile schema.
**Alternatives considered:**
1. Full page text to Sonnet — accurate but 5-10x token cost. Budget is $0.20/run.
2. Word count + heading count only (no LLM) — misses depth, E-E-A-T, and topic coverage. Requirements mandate LLM quality assessment.
3. Summarise with LLM first, then assess — double LLM call, double cost. Unnecessary when compressed extraction captures the quality signals.
**Consequences:** Quality assessment may miss signals buried deep in long articles. Acceptable trade-off: top-of-page and structural signals capture 80%+ of quality indicators. Upgrade path to Sonnet if Haiku accuracy is insufficient (open question in requirements).

### ADR-F005-003: Crawl Rate Limiting — Domain-Aware Token Bucket

**Status:** Proposed
**Context:** Requirements mandate 2 req/s global max, 500ms minimum between same-domain requests, and robots.txt crawl-delay compliance. Multiple competitor domains may be crawled in parallel.
**Decision:** Per-domain token bucket rate limiter. Each domain gets its own bucket (rate from robots.txt crawl-delay or default 500ms). Global concurrency limited to 2 in-flight requests. Implemented as an async semaphore with per-domain delay tracking.
**Alternatives considered:**
1. Global fixed-rate limiter — doesn't respect per-domain crawl-delay.
2. Sequential crawling — correct but slow. 10 pages × 500ms minimum = 5 seconds minimum. Parallel with domain isolation is faster and still respectful.
**Consequences:** In-memory rate state (per-domain timestamps). Resets on restart — acceptable since crawl sessions are short-lived.

## Data Model

### Drizzle Schema

```typescript
import { pgTable, uuid, text, integer, timestamp, boolean, jsonb, index } from 'drizzle-orm/pg-core';

// --- competitor_snapshot ---
export const competitorSnapshot = pgTable('competitor_snapshot', {
  id: text('id').primaryKey(),                              // cs_xxx
  tenant_id: uuid('tenant_id').notNull(),
  keyword_id: text('keyword_id').notNull(),
  serp_snapshot_id: text('serp_snapshot_id').notNull()
    .references(() => serpSnapshot.id),
  url: text('url').notNull(),
  domain: text('domain').notNull(),
  serp_position: integer('serp_position').notNull(),

  // Structural extraction (US-001)
  crawl_status: text('crawl_status').notNull(),             // "success" | "crawl_failed" | "robots_blocked" | "js_rendered"
  http_status_code: integer('http_status_code'),
  word_count: integer('word_count'),
  h1_text: text('h1_text'),
  h2_count: integer('h2_count'),
  h3_count: integer('h3_count'),
  h2_texts: jsonb('h2_texts').$type<string[]>().default([]),
  schema_types: jsonb('schema_types').$type<string[]>().default([]),
  has_faq_section: boolean('has_faq_section').default(false),
  internal_link_count: integer('internal_link_count'),
  external_link_count: integer('external_link_count'),
  image_count: integer('image_count'),
  is_thin_content: boolean('is_thin_content').default(false), // < 300 words

  // Quality assessment (US-002)
  quality_assessment_status: text('quality_assessment_status'), // "completed" | "skipped" | "failed"
  depth_score: integer('depth_score'),                       // 1-5
  topics_covered: jsonb('topics_covered').$type<string[]>().default([]),
  has_original_data: boolean('has_original_data'),
  has_author_credentials: boolean('has_author_credentials'),
  eeat_signals: jsonb('eeat_signals').$type<string[]>().default([]),
  quality_rationale: text('quality_rationale'),

  // Change detection (US-003)
  raw_html_hash: text('raw_html_hash'),                     // MD5
  content_changed: boolean('content_changed').default(false),

  // Metadata
  crawled_at: timestamp('crawled_at', { withTimezone: true }).notNull(),
  llm_tokens_used: integer('llm_tokens_used'),
  pipeline_run_id: text('pipeline_run_id'),

  created_at: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('comp_snapshot_tenant_idx').on(table.tenant_id),
  keywordIdx: index('comp_snapshot_keyword_idx').on(table.tenant_id, table.keyword_id),
  urlIdx: index('comp_snapshot_url_idx').on(table.tenant_id, table.url, table.crawled_at),
  domainIdx: index('comp_snapshot_domain_idx').on(table.tenant_id, table.domain),
}));
```

### RLS Policies

```sql
ALTER TABLE competitor_snapshot ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON competitor_snapshot
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

## API Contracts

### Commands

```typescript
// --- AnalyseCompetitorPageCommand ---
interface AnalyseCompetitorPageInput {
  tenant_id: string;
  keyword_id: string;
  serp_snapshot_id: string;
  url: string;
  domain: string;
  serp_position: number;
  pipeline_run_id?: string;
}

interface AnalyseCompetitorPageOutput {
  snapshot_id: string;
  crawl_status: 'success' | 'crawl_failed' | 'robots_blocked' | 'js_rendered';
  word_count: number | null;
  depth_score: number | null;
  content_changed: boolean;
}

type AnalyseCompetitorPageResult = Result<AnalyseCompetitorPageOutput, CompetitorError>;

// --- BatchAnalyseCompetitorsCommand ---
interface BatchAnalyseCompetitorsInput {
  tenant_id: string;
  serp_snapshot_id: string;
  urls: Array<{
    keyword_id: string;
    url: string;
    domain: string;
    serp_position: number;
  }>;
  pipeline_run_id: string;
}

interface BatchAnalyseCompetitorsOutput {
  total: number;
  succeeded: number;
  failed: number;
  robots_blocked: number;
  snapshots: AnalyseCompetitorPageOutput[];
  llm_tokens_total: number;
}
```

### Queries

```typescript
// --- GetCompetitorSnapshot ---
interface GetCompetitorSnapshotInput {
  tenant_id: string;
  url: string;
  latest?: boolean;                 // default true — most recent snapshot
}

type GetCompetitorSnapshotResult = Result<CompetitorSnapshotRecord | null, QueryError>;

// --- GetCompetitorBenchmarks ---
// Used by F-006 to get competitor benchmarks for a keyword
interface GetCompetitorBenchmarksInput {
  tenant_id: string;
  keyword_id: string;
}

interface CompetitorBenchmark {
  url: string;
  domain: string;
  serp_position: number;
  word_count: number | null;
  depth_score: number | null;
  h2_texts: string[];
  schema_types: string[];
  has_faq_section: boolean;
  topics_covered: string[];
}

type GetCompetitorBenchmarksResult = Result<CompetitorBenchmark[], QueryError>;
```

### Events

```typescript
interface CompetitorAnalysisCompleted {
  type: 'research.competitor.analysed';
  tenant_id: string;
  keyword_id: string;
  snapshot_id: string;
  crawl_status: string;
  content_changed: boolean;
}

interface CompetitorBatchCompleted {
  type: 'research.competitor.batch_completed';
  tenant_id: string;
  pipeline_run_id: string;
  total: number;
  succeeded: number;
  failed: number;
}
```

### Error Types

```typescript
type CompetitorError =
  | { code: 'ROBOTS_BLOCKED'; url: string; directive: string }
  | { code: 'HTTP_ERROR'; url: string; status_code: number; retries: number }
  | { code: 'RATE_LIMIT_EXCEEDED'; domain: string }
  | { code: 'LLM_UNAVAILABLE'; retries: number }
  | { code: 'EXTRACTION_FAILED'; url: string; reason: string };
```

## Component Design

### ContentExtractor

**Responsibility:** Parse HTML with cheerio, extract structural fields.
**Input:** Raw HTML string, URL
**Output:** `ExtractionResult` with all structural fields
**Key decisions:**
- Strip `<nav>`, `<footer>`, `<header>`, `<aside>`, `<script>`, `<style>` before word count
- Detect JSON-LD by parsing `<script type="application/ld+json">` blocks
- Detect FAQ section by: `<div itemtype="...FAQPage">` OR H2 containing "FAQ" OR `<details>` groups
- Flag JS-rendered pages by checking if body text < 100 chars after stripping (likely SPA)

### QualityAssessor

**Responsibility:** Send compressed page content to LLM, parse structured quality profile.
**Input:** `CompressedPageContent` (first 2000 chars + headings + author section)
**Output:** `QualityProfile` (depth_score, topics, E-E-A-T signals)
**Prompt:** Versioned at `prompts/competitor-quality-assessment/v1.txt`. Structured output (JSON mode) enforced.
**Batching:** Process 5 pages per LLM batch call to reduce overhead.
**Fallback:** If LLM fails after 2 retries, set `quality_assessment_status = "failed"`, continue pipeline.

### RobotsTxtChecker

**Responsibility:** Fetch and parse robots.txt, check if URL is crawlable.
**Input:** Domain, URL path
**Output:** `{ allowed: boolean; crawl_delay?: number }`
**Caching:** Cache robots.txt per domain for 24h (in-memory Map, cleared on restart).
**Library:** `robots-parser` npm package (lightweight, well-tested).

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **SSRF** — Competitor URL resolves to internal IP (169.254.x.x, 10.x.x.x, 127.0.0.1) | H | URL validation before fetch: allowlist `http://` and `https://` schemes only. Resolve DNS and reject private IP ranges. Block redirects to private IPs. Use `undici` with `connect` options to enforce. |
| **Tampering** — Malicious HTML in competitor page triggers XSS when data is rendered later | M | cheerio is parse-only (no script execution). DOMPurify on extracted text before storage. No raw HTML stored. Quality rationale (from LLM) is plain text, not HTML. |

## ATAM-Lite

| Decision | Quality Attribute | Sensitivity | Trade-off |
|----------|------------------|:-----------:|-----------|
| Compressed LLM input (2K tokens) | **Cost** vs **Accuracy** | High | Misses deep-page signals. Saves 5-10x token cost. Acceptable: structural extraction captures word count/headings accurately; LLM assesses quality from top-of-page signals. Upgrade path: Sonnet with full text if Haiku accuracy < 70%. |
| Per-domain rate limiting | **Compliance** vs **Speed** | High | Crawling 10 pages at 500ms intervals takes 5s minimum. Parallel domains help. Worth it: robots.txt compliance is non-negotiable, and competitor sites shouldn't be hammered. |
| No raw HTML storage | **Storage** vs **Re-analysability** | Medium | Can't re-run extraction without re-crawling. Saves significant storage. Hash-based change detection still works. Re-crawling is cheap and respects freshness requirements. |

## Build Boundaries

### Always (no approval needed)
- Write extractor, assessor, downloader code within this design
- Create fixture HTML files for testing
- Run tests and fix failures
- Update prompts in `prompts/competitor-quality-assessment/`

### Ask First
- Add a headless browser for JS-rendered pages (Playwright dependency)
- Change quality assessment from Haiku to Sonnet
- Store raw HTML beyond the MD5 hash
- Add new extraction fields beyond the schema above

### Never
- Crawl without checking robots.txt
- Remove rate limiting
- Store extracted competitor content without sanitisation
- Skip RLS on competitor_snapshot table

## Test Architecture

### Test Pyramid

| Level | Count | What | Tools |
|-------|:-----:|------|-------|
| Unit | ~15 | ContentExtractor with fixture HTML (word count, headings, schema detection, FAQ detection, link counts), RobotsTxtChecker with fixture robots.txt, URL validation (SSRF checks), compressed input generation | Vitest |
| Integration | ~8 | Full pipeline: download → extract → assess → store (with mock HTTP + mock LLM), batch processing with failures, snapshot change detection, portability (DB vs file adapters) | Vitest + testcontainers + msw |
| Property | ~3 | Word count is always non-negative, H2 count matches H2 texts array length, depth_score is always 1-5 or null | Vitest + fast-check |

### Mocking Strategy

- **HTTP (page downloads):** `msw` intercepting `fetch` calls. Fixture HTML files in `test/fixtures/competitor-pages/`.
- **LLM (quality assessment):** Mock AI gateway returning fixture quality profiles. Configured via DI.
- **robots.txt:** `msw` serving fixture robots.txt per domain.
- **Database:** testcontainers PostgreSQL for integration. Pure extraction tests need no DB.

### Property Invariants

1. `word_count >= 0` for all successful extractions — never negative, never NaN.
2. `h2_texts.length === h2_count` — heading text array matches the count.
3. `depth_score` is in `[1, 2, 3, 4, 5]` or null — never 0, never > 5.
4. `crawl_status !== 'success'` implies structural fields may be null — consumers must handle gracefully.
