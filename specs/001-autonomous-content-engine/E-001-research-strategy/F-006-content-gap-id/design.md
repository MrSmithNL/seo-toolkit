---
id: "FTR-SEO-006"
type: feature
title: "Content Gap Identification"
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

# F-006: Content Gap Identification — Design

## Architecture Overview

F-006 is a pure computation stage: no external API calls, no crawling, no LLM. It takes F-004 SERP data, F-005 competitor benchmarks, F-001 keyword data, and optionally GSC query data, then produces a scored gap matrix. This is the analytical core of the research pipeline.

```
F-001 Keywords ──────────┐
F-004 SERP Snapshots ────┤
F-005 Competitor Data ───┤
GSC Query Data ──────────┘
         │
         ▼
  [GapMatrixBuilder]
         │
         ├──→ [CoverageClassifier] (own_gap / own_coverage / new_opportunity)
         │
         ├──→ [ThinContentDetector] (word_count < 50% competitor avg + rank 11-50)
         │
         ├──→ [OpportunityScorer] (configurable formula)
         │
         ▼
  [GapMatrixRepo] ──→ PostgreSQL / JSON file
         │
         ▼
  F-007 Content Calendar (consumer)
```

## Architecture Decision Records

### ADR-F006-001: GSC Integration with Graceful Fallback

**Status:** Proposed
**Context:** GSC provides authoritative "keywords we rank for" data (impressions, clicks, position). But GSC may be unavailable (not connected, API errors, new site with no data). The system must work without GSC.
**Decision:** `CoverageDataSource` interface with two implementations: `GscCoverageSource` (primary, uses Google Search Console API) and `SerpCoverageSource` (fallback, checks if user domain appears in top-50 SERP results). The fallback is automatic and flagged in output.
**Alternatives considered:**
1. GSC-only — fails for new sites or unconnected accounts. Requirements mandate SERP-based fallback.
2. Always use both and merge — over-complex. GSC is strictly more accurate when available.
**Consequences:** Two code paths for coverage detection. SERP fallback is less accurate (can't detect impressions without clicks). Output includes `coverage_source: "gsc" | "serp_fallback"` flag so downstream consumers know the confidence level.

### ADR-F006-002: Opportunity Scoring — Named Constants, Not Inline

**Status:** Proposed
**Context:** Requirements define a specific formula: `(volume_normalised × 0.4) + (difficulty_inverse × 0.3) + (gap_score × 0.3)`. Weights will likely need tuning after R1 pilot.
**Decision:** Store scoring formula weights and thresholds in a `ScoringConfig` object, loaded from env vars with defaults. The formula is a pure function that takes config + inputs and returns score + rationale string.
**Alternatives considered:**
1. Hardcoded formula — works but changing weights requires code changes.
2. User-configurable scoring in a config file — over-engineering for R1. Env vars are sufficient.
3. LLM-based scoring — unnecessary cost for what is a deterministic calculation. F-006 explicitly has zero LLM calls.
**Consequences:** Formula change = env var update, no code change. Score rationale is always generated from the same function, ensuring consistency.

### ADR-F006-003: Per-Language Gap Matrices

**Status:** Proposed
**Context:** Requirements mandate independent gap analysis per language (US-004). EN gaps are not assumed to exist in DE. Each language has its own SERP landscape.
**Decision:** `GapMatrixBuilder` takes a `language` parameter and produces one matrix per language. A `CrossLanguageSummariser` takes all per-language matrices and produces a summary identifying universal gaps (all languages) vs language-specific gaps. Universal gaps get a +0.1 bonus to opportunity score.
**Alternatives considered:**
1. Single merged matrix — violates requirements. "FUE vs DHI" ranking page 1 in EN but page 3 in DE are different opportunities.
2. Run entire pipeline per language — too coarse. F-006 already receives per-language data from F-004/F-005. Just partition the analysis.
**Consequences:** Output is an array of `LanguageGapMatrix` objects plus one `CrossLanguageSummary`. Storage grows linearly with language count — at 9 languages and 100 keywords, that's ~900 gap rows. Negligible.

## Data Model

### Drizzle Schema

```typescript
import { pgTable, uuid, text, integer, real, timestamp, boolean, jsonb, index } from 'drizzle-orm/pg-core';

// --- content_gap ---
export const contentGap = pgTable('content_gap', {
  id: text('id').primaryKey(),                              // cg_xxx
  tenant_id: uuid('tenant_id').notNull(),
  campaign_id: text('campaign_id').notNull()
    .references(() => campaign.id),
  keyword_id: text('keyword_id').notNull()
    .references(() => keyword.id),
  language: text('language').notNull(),                     // BCP 47

  // Classification
  gap_type: text('gap_type').notNull(),                    // "own_gap" | "own_coverage" | "thin_content" | "new_opportunity"
  coverage_source: text('coverage_source').notNull(),      // "gsc" | "serp_fallback"

  // Our coverage
  our_ranking_position: integer('our_ranking_position'),   // null if not ranking
  our_page_url: text('our_page_url'),                      // null if not ranking
  our_word_count: integer('our_word_count'),                // null if not ranking or not crawled
  gsc_impressions: integer('gsc_impressions'),              // null if no GSC

  // Competitor coverage
  competitor_best_position: integer('competitor_best_position'),
  competitor_best_url: text('competitor_best_url'),
  competitor_avg_word_count: integer('competitor_avg_word_count'),
  competitor_avg_depth_score: real('competitor_avg_depth_score'),
  competitors_analysed: integer('competitors_analysed').notNull().default(0),
  competitors_excluded: integer('competitors_excluded').notNull().default(0),

  // Thin content fields (populated when gap_type = "thin_content")
  word_count_gap: integer('word_count_gap'),                // competitor_avg - our_word_count
  thin_content_rationale: text('thin_content_rationale'),

  // Opportunity scoring
  opportunity_score: real('opportunity_score'),             // 0.0-1.0
  thin_content_priority_score: real('thin_content_priority_score'), // 0.0-1.0 (thin content only)
  score_rationale: text('score_rationale'),
  score_inputs: jsonb('score_inputs').$type<{
    volume: number;
    volume_normalised: number;
    difficulty: number;
    difficulty_inverse_normalised: number;
    gap_score: number;
    universal_gap_bonus: number;
  }>(),

  // Flags
  is_universal_gap: boolean('is_universal_gap').default(false),
  partial_data: boolean('partial_data').default(false),     // some competitors excluded
  partial_data_reason: text('partial_data_reason'),
  llm_assessed_fields: jsonb('llm_assessed_fields').$type<string[]>().default([]),

  // Pipeline tracking
  pipeline_run_id: text('pipeline_run_id'),

  created_at: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('content_gap_tenant_idx').on(table.tenant_id),
  campaignLangIdx: index('content_gap_campaign_lang_idx').on(table.tenant_id, table.campaign_id, table.language),
  gapTypeIdx: index('content_gap_type_idx').on(table.tenant_id, table.gap_type),
  scoreIdx: index('content_gap_score_idx').on(table.tenant_id, table.opportunity_score),
}));

// --- cross_language_summary ---
export const crossLanguageSummary = pgTable('cross_language_summary', {
  id: text('id').primaryKey(),                              // cls_xxx
  tenant_id: uuid('tenant_id').notNull(),
  campaign_id: text('campaign_id').notNull(),
  keyword_id: text('keyword_id').notNull(),
  keyword_text: text('keyword_text').notNull(),

  languages_with_gap: jsonb('languages_with_gap').$type<string[]>().default([]),
  languages_with_coverage: jsonb('languages_with_coverage').$type<string[]>().default([]),
  is_universal_gap: boolean('is_universal_gap').notNull().default(false),
  total_languages_analysed: integer('total_languages_analysed').notNull(),

  pipeline_run_id: text('pipeline_run_id'),
  created_at: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('cls_tenant_idx').on(table.tenant_id),
  campaignIdx: index('cls_campaign_idx').on(table.tenant_id, table.campaign_id),
}));
```

### RLS Policies

```sql
ALTER TABLE content_gap ENABLE ROW LEVEL SECURITY;
ALTER TABLE cross_language_summary ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON content_gap
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
CREATE POLICY tenant_isolation ON cross_language_summary
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

## API Contracts

### Commands

```typescript
// --- GenerateGapMatrixCommand ---
interface GenerateGapMatrixInput {
  tenant_id: string;
  campaign_id: string;
  language: string;
  pipeline_run_id: string;
}

interface GenerateGapMatrixOutput {
  total_keywords: number;
  own_gap_count: number;
  own_coverage_count: number;
  thin_content_count: number;
  new_opportunity_count: number;
  coverage_source: 'gsc' | 'serp_fallback';
  gap_ids: string[];
}

type GenerateGapMatrixResult = Result<GenerateGapMatrixOutput, GapError>;

// --- GenerateCrossLanguageSummaryCommand ---
interface GenerateCrossLanguageSummaryInput {
  tenant_id: string;
  campaign_id: string;
  languages: string[];
  pipeline_run_id: string;
}

interface CrossLanguageSummaryOutput {
  universal_gaps: Array<{ keyword_id: string; keyword_text: string; missing_in: string[] }>;
  language_specific_gaps: Array<{ keyword_id: string; keyword_text: string; gap_languages: string[]; covered_languages: string[] }>;
  total_keywords: number;
}

type GenerateCrossLanguageSummaryResult = Result<CrossLanguageSummaryOutput, GapError>;
```

### Queries

```typescript
// --- GetGapMatrix ---
interface GetGapMatrixInput {
  tenant_id: string;
  campaign_id: string;
  language: string;
  gap_type?: 'own_gap' | 'thin_content' | 'new_opportunity';
  sort_by?: 'opportunity_score' | 'thin_content_priority_score';
  min_score?: number;
}

type GetGapMatrixResult = Result<ContentGapRecord[], QueryError>;

// --- GetTopOpportunities ---
// Convenience query for F-007
interface GetTopOpportunitiesInput {
  tenant_id: string;
  campaign_id: string;
  language: string;
  limit: number;                   // default: 20
}

type GetTopOpportunitiesResult = Result<ContentGapRecord[], QueryError>;
```

### Scoring Config

```typescript
// Loaded from env vars with defaults
interface ScoringConfig {
  volume_weight: number;           // default: 0.4
  difficulty_weight: number;       // default: 0.3
  gap_weight: number;              // default: 0.3
  universal_gap_bonus: number;     // default: 0.1
  thin_content_threshold: number;  // default: 0.5 (50% of competitor avg)
  thin_position_weight: number;    // default: 0.5
  thin_wordcount_weight: number;   // default: 0.5
  min_volume_threshold: number;    // default: 50 (monthly searches)
}
```

### Events

```typescript
interface GapMatrixGenerated {
  type: 'research.gap.matrix_generated';
  tenant_id: string;
  campaign_id: string;
  language: string;
  own_gap_count: number;
  thin_content_count: number;
  new_opportunity_count: number;
}

interface CrossLanguageSummaryGenerated {
  type: 'research.gap.cross_language_summary';
  tenant_id: string;
  campaign_id: string;
  universal_gap_count: number;
  languages_analysed: number;
}
```

### Error Types

```typescript
type GapError =
  | { code: 'INSUFFICIENT_DATA'; reason: string; missing: string[] }
  | { code: 'GSC_UNAVAILABLE'; fallback_used: boolean }
  | { code: 'NO_KEYWORDS'; campaign_id: string };
```

## Component Design

### CoverageClassifier

**Responsibility:** For each keyword, determine whether the user's site covers it.
**Logic:**
1. If GSC available: check for impressions > 0 → `own_coverage`. No impressions + competitor ranks → `own_gap`. No impressions + no competitor → `new_opportunity`.
2. If GSC unavailable: check SERP top-50 for user domain. Present → `own_coverage`. Absent + competitor ranks → `own_gap`. Absent + no competitor → `new_opportunity`.

### ThinContentDetector

**Responsibility:** Flag `own_coverage` keywords where our content is significantly weaker.
**Logic:**
1. Filter to keywords where we rank 11-50 (underperforming but present).
2. Compare our word count vs top-3 competitor average.
3. If our word count < 50% of competitor average → `thin_content`.
4. Exception: if we rank top 10, don't flag as thin regardless of word count (ranking well despite fewer words).

### OpportunityScorer

**Responsibility:** Pure function that calculates score from inputs.
**Implementation:**

```typescript
function calculateOpportunityScore(
  input: { volume: number; difficulty: number; gapScore: number; isUniversalGap: boolean },
  config: ScoringConfig,
  maxVolume: number
): { score: number; rationale: string; inputs: ScoreInputs } {
  const volumeNorm = maxVolume > 0 ? input.volume / maxVolume : 0;
  const difficultyInverse = (100 - input.difficulty) / 100;

  let score =
    (volumeNorm * config.volume_weight) +
    (difficultyInverse * config.difficulty_weight) +
    (input.gapScore * config.gap_weight);

  if (input.isUniversalGap) score += config.universal_gap_bonus;
  score = Math.min(score, 1.0);

  // Generate rationale...
  return { score, rationale, inputs };
}
```

### CrossLanguageSummariser

**Responsibility:** Compare gap matrices across languages to find universal vs language-specific gaps.
**Logic:** Group gap records by keyword_id across languages. If gap exists in all analysed languages → universal. If gap exists in some → language-specific. Update `is_universal_gap` flag and apply score bonus.

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **Info Disclosure** — Cross-tenant gap data leakage | H | RLS on both tables. All queries scoped by `tenant_id`. CI gate validates. |
| **Tampering** — Manipulated F-005 depth_score leading to incorrect gap scoring | L | F-006 labels all LLM-derived fields with `llm_assessed_fields` array. Consumers know which fields are estimated vs factual. Score inputs are persisted alongside score for reproducibility. |

## ATAM-Lite

| Decision | Quality Attribute | Sensitivity | Trade-off |
|----------|------------------|:-----------:|-----------|
| GSC primary + SERP fallback | **Accuracy** vs **Availability** | High | SERP fallback misses "ranking but no clicks" keywords. Worth it: system works without GSC. Output flagged so consumers know the confidence. |
| Per-language independent matrices | **Correctness** vs **Simplicity** | High | More gap rows (×N languages), more storage. Worth it: multilingual gap analysis is our differentiator. Storage is negligible at R1 scale. |
| Configurable scoring weights | **Maintainability** vs **Simplicity** | Medium | Slightly more code for config loading. Worth it: weight tuning after R1 pilot is guaranteed (assumption A2 in requirements). One-line env var change vs code change. |

## Build Boundaries

### Always (no approval needed)
- Write classifier, scorer, summariser code within this design
- Create fixture gap data for testing
- Adjust scoring formula implementation (not weights — those are config)
- Run tests and fix failures

### Ask First
- Change the default scoring weights
- Add new gap classification types beyond own_gap/thin_content/new_opportunity
- Add LLM calls to F-006 (currently zero LLM by design)
- Change thin content threshold from 50%

### Never
- Present LLM-assessed fields (depth_score) as objective measurements
- Skip `llm_assessed_fields` labelling
- Hardcode scoring weights in business logic
- Skip RLS on any table

## Test Architecture

### Test Pyramid

| Level | Count | What | Tools |
|-------|:-----:|------|-------|
| Unit | ~18 | OpportunityScorer with various input combinations, CoverageClassifier with GSC + SERP data, ThinContentDetector edge cases, CrossLanguageSummariser with multi-language fixtures, rationale string generation, config loading | Vitest |
| Integration | ~6 | Full gap matrix generation from fixture SERP + competitor data, GSC fallback path, per-language matrix independence, cross-language summary, DB round-trip, file adapter | Vitest + testcontainers |
| Property | ~4 | opportunity_score is always 0.0-1.0 (clamped), thin_content_priority_score is always 0.0-1.0, gap_type is always one of 4 valid values, universal_gap_bonus never pushes score above 1.0 | Vitest + fast-check |

### Mocking Strategy

- **GSC API:** Mock `CoverageDataSource` returning fixture impression data. No real GSC calls in tests.
- **F-004/F-005 data:** Fixture objects matching the SERP snapshot and competitor benchmark schemas.
- **Database:** testcontainers PostgreSQL for integration. Pure scoring/classification tests are stateless.

### Property Invariants

1. `0.0 <= opportunity_score <= 1.0` — for any combination of volume, difficulty, gap_score, and universal_gap_bonus.
2. `gap_type ∈ {"own_gap", "own_coverage", "thin_content", "new_opportunity"}` — exhaustive, no other values.
3. `thin_content = true` implies `our_ranking_position >= 11` — never flag top-10 as thin.
4. `score_inputs` is always present when `opportunity_score` is set — scores are always reproducible.
5. `is_universal_gap = true` implies `languages_with_gap.length === total_languages_analysed` — definition consistency.
