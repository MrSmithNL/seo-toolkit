---
id: "FTR-SEO-007"
type: feature
title: "Content Calendar / Planning"
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

# F-007: Content Calendar / Planning — Design

## Architecture Overview

F-007 is the terminal stage of the E-001 pipeline. It consumes gap data (F-006), competitor benchmarks (F-005), keyword data (F-001), and intent classifications (F-003) to produce ContentBrief records, format them as a human-reviewable Markdown calendar, and output approved briefs as the E-002 input contract.

```
F-001 Keywords ──────────┐
F-003 Intent ────────────┤
F-005 Competitor Data ───┤
F-006 Gap Matrix ────────┘
         │
         ▼
  [CalendarGeneratorCommand]
         │
         ├──→ [ContentBriefBuilder] ──→ assembles ContentBrief from pipeline data
         │         │
         │         ▼
         │    [RecommendationEngine] ──→ LLM: headings, content_type, schema_types
         │
         ├──→ [PublishScheduler] ──→ assigns dates (priority order, 2/week cadence)
         │
         ├──→ [LanguageScheduler] ──→ spreads languages across weeks
         │
         ├──→ [CalendarRenderer] ──→ Markdown + JSON output files
         │
         ▼
  [ApprovalWorkflow]
         │
         ├──→ schema validation (Zod)
         ├──→ status transitions (pending → approved | rejected)
         │
         ▼
  approved-briefs-YYYY-MM-DD.json ──→ E-002 (Content Creation)
```

## Architecture Decision Records

### ADR-F007-001: ContentBrief as Schema-Validated Contract

**Status:** Proposed
**Context:** The ContentBrief is consumed by E-002 (Content Creation), E-003 (Optimisation), and E-005 (Measurement). Any schema drift between producer and consumer causes silent failures. The requirements define a detailed interface (§ ContentBrief Schema in requirements.md).
**Decision:** Define the canonical ContentBrief as a Zod schema in `contracts/content-brief.schema.ts`. Generate TypeScript types from Zod (`z.infer`). Validate every ContentBrief on creation, on update, and on final output (triple validation). Schema version field enables forward-compatible evolution. Breaking changes require a new version + ADR.
**Alternatives considered:**
1. TypeScript interface only (no runtime validation) — type-safe at compile time, but E-002 may receive invalid data at runtime (e.g., from corrupted JSON file).
2. JSON Schema — more portable, but Zod is the agency standard (drizzle-zod), and we need TypeScript type inference.
3. Protobuf — over-engineering for file-based R1 communication. Consider for R2+ if gRPC is adopted.
**Consequences:** Zod schema is the single source of truth. Types are derived, not hand-written. Breaking schema changes are versioned and documented.

### ADR-F007-002: Dual Output Format (Markdown + JSON)

**Status:** Proposed
**Context:** Malcolm reviews the calendar in Markdown (human-readable). E-002 consumes JSON (machine-readable). Requirements mandate both outputs.
**Decision:** `CalendarRenderer` produces two files from the same ContentBrief array: (1) `calendar-YYYY-MM-DD.md` formatted per the requirements template, (2) `calendar-YYYY-MM-DD.json` containing the full ContentBrief array. Approval is done by editing the JSON file (setting `status` field) or via CLI command.
**Alternatives considered:**
1. Markdown only, parse approval from checkboxes — fragile parsing, easy to corrupt.
2. JSON only with a CLI viewer — less accessible for quick review. Markdown is universally readable.
3. Interactive CLI prompt per topic — acceptable but slower for 10+ topics. JSON editing is faster for batch approval.
**Consequences:** Two files to maintain in sync. The JSON is authoritative; the Markdown is read-only output. If Malcolm edits the Markdown, those edits are NOT picked up — only JSON changes count.

### ADR-F007-003: LLM for Recommendations, Not for Scoring

**Status:** Proposed
**Context:** F-007 uses LLM for three specific tasks: (1) heading recommendations, (2) content type selection with rationale, (3) schema type recommendations. Scoring comes from F-006 (deterministic formula). This separation is deliberate.
**Decision:** LLM calls are isolated in a `RecommendationEngine` class. Inputs: competitor heading data (F-005), search intent (F-003), keyword. Outputs: structured JSON with `content_type`, `recommended_headings[]`, `recommended_schema_types[]`. LLM output is grounded in competitor data — headings are based on what competitors use, not invented. If LLM fails, fall back to competitor heading extraction (no LLM).
**Alternatives considered:**
1. LLM for everything including scoring — adds cost and non-determinism to what should be a reproducible calculation. Score transparency is a differentiator (anti-pattern: SEO.ai black-box).
2. No LLM — heading recommendations would be raw competitor headings without adaptation. LLM adds value by synthesising competitor patterns into a coherent outline.
**Consequences:** ~1K tokens per brief (heading + type + schema recommendation). 10-brief calendar = ~10K tokens. Cost: ~$0.10 at Haiku pricing. Well within the $0.15/calendar budget.

## Data Model

### ContentBrief Zod Schema (contracts/content-brief.schema.ts)

```typescript
import { z } from 'zod';

export const contentBriefSchema = z.object({
  // Identity
  id: z.string().uuid(),
  tenant_id: z.string().uuid(),
  created_at: z.string().datetime(),
  schema_version: z.literal('1.0.0'),
  status: z.enum(['pending_review', 'approved', 'rejected', 'in_progress', 'published']),

  // Target and strategy
  target_keyword: z.string().min(1),
  target_language: z.string().min(2).max(5),       // BCP 47
  target_country: z.string().length(2),             // ISO 3166-1
  supporting_keywords: z.array(z.string()),
  search_intent: z.enum(['informational', 'transactional', 'navigational', 'commercial']),
  topic_cluster: z.string().nullable(),
  content_type: z.enum(['blog_post', 'comparison', 'how_to', 'faq', 'product_page', 'landing_page']),

  // Research inputs
  keyword_volume: z.number().int().min(0),
  keyword_difficulty: z.number().int().min(0).max(100),
  opportunity_score: z.number().min(0).max(1),
  opportunity_score_rationale: z.string(),
  gap_type: z.enum(['own_gap', 'thin_content', 'new_opportunity']),
  existing_page_url: z.string().url().nullable(),

  // Competitor benchmarks
  competitor_avg_word_count: z.number().int().min(0),
  competitor_depth_scores: z.array(z.number().int().min(1).max(5)),
  top_competitor_url: z.string().url().nullable(),
  competitor_schema_types: z.array(z.string()),
  competitors_have_faq: z.boolean(),

  // Recommendations
  recommended_word_count: z.number().int().min(100),
  recommended_headings: z.array(z.string()),
  recommended_schema_types: z.array(z.string()),
  include_faq: z.boolean(),
  suggested_publish_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/), // YYYY-MM-DD

  // Human review
  reviewed_by: z.string().nullable(),
  reviewed_at: z.string().datetime().nullable(),
  review_notes: z.string().nullable(),
  overridden_word_count: z.number().int().min(100).nullable(),
  overridden_publish_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).nullable(),
});

export type ContentBrief = z.infer<typeof contentBriefSchema>;

// File-level wrapper for approved-briefs output
export const approvedBriefsFileSchema = z.object({
  schema_version: z.literal('1.0.0'),
  generated_at: z.string().datetime(),
  campaign_id: z.string(),
  briefs: z.array(contentBriefSchema),
});
```

### Drizzle Schema (DB persistence)

```typescript
import { pgTable, uuid, text, integer, real, timestamp, boolean, jsonb, index } from 'drizzle-orm/pg-core';

// --- content_brief ---
export const contentBrief = pgTable('content_brief', {
  id: text('id').primaryKey(),                              // cb_xxx
  tenant_id: uuid('tenant_id').notNull(),
  campaign_id: text('campaign_id').notNull()
    .references(() => campaign.id),
  keyword_id: text('keyword_id').notNull(),
  language: text('language').notNull(),
  status: text('status').notNull().default('pending_review'),
  schema_version: text('schema_version').notNull().default('1.0.0'),

  // Full brief stored as validated JSON
  brief_data: jsonb('brief_data').$type<ContentBrief>().notNull(),

  // Denormalised for queries (avoid JSON extraction in WHERE clauses)
  opportunity_score: real('opportunity_score'),
  gap_type: text('gap_type'),
  suggested_publish_date: text('suggested_publish_date'),
  content_type: text('content_type'),

  // Review
  reviewed_by: text('reviewed_by'),
  reviewed_at: timestamp('reviewed_at', { withTimezone: true }),
  review_notes: text('review_notes'),

  // Pipeline tracking
  pipeline_run_id: text('pipeline_run_id'),
  calendar_batch_id: text('calendar_batch_id'),             // groups briefs from same calendar generation

  created_at: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updated_at: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('content_brief_tenant_idx').on(table.tenant_id),
  campaignIdx: index('content_brief_campaign_idx').on(table.tenant_id, table.campaign_id),
  statusIdx: index('content_brief_status_idx').on(table.tenant_id, table.status),
  scoreIdx: index('content_brief_score_idx').on(table.tenant_id, table.opportunity_score),
  dateIdx: index('content_brief_date_idx').on(table.tenant_id, table.suggested_publish_date),
}));
```

### RLS Policies

```sql
ALTER TABLE content_brief ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON content_brief
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

## API Contracts

### Commands

```typescript
// --- GenerateCalendarCommand ---
interface GenerateCalendarInput {
  tenant_id: string;
  campaign_id: string;
  language: string;
  pipeline_run_id: string;
  cadence_per_week?: number;         // default: 2
  start_date?: string;               // default: next Monday, YYYY-MM-DD
  output_dir?: string;               // default: data/calendar/{domain}/
}

interface GenerateCalendarOutput {
  total_briefs: number;
  new_content_count: number;
  update_content_count: number;
  markdown_path: string;
  json_path: string;
  llm_tokens_used: number;
  calendar_batch_id: string;
}

type GenerateCalendarResult = Result<GenerateCalendarOutput, CalendarError>;

// --- ApproveBriefCommand ---
interface ApproveBriefInput {
  tenant_id: string;
  brief_id: string;
  reviewed_by: string;
  review_notes?: string;
  overridden_word_count?: number;
  overridden_publish_date?: string;
}

type ApproveBriefResult = Result<{ brief_id: string; status: 'approved' }, CalendarError>;

// --- RejectBriefCommand ---
interface RejectBriefInput {
  tenant_id: string;
  brief_id: string;
  reviewed_by: string;
  review_notes?: string;
}

type RejectBriefResult = Result<{ brief_id: string; status: 'rejected' }, CalendarError>;

// --- ExportApprovedBriefsCommand ---
interface ExportApprovedBriefsInput {
  tenant_id: string;
  campaign_id: string;
  calendar_batch_id: string;
  output_path?: string;               // default: data/calendar/{domain}/approved-briefs-YYYY-MM-DD.json
}

interface ExportApprovedBriefsOutput {
  output_path: string;
  brief_count: number;
  schema_version: string;
}

type ExportApprovedBriefsResult = Result<ExportApprovedBriefsOutput, CalendarError>;
```

### Queries

```typescript
// --- GetCalendarBriefs ---
interface GetCalendarBriefsInput {
  tenant_id: string;
  campaign_id: string;
  calendar_batch_id?: string;
  status?: 'pending_review' | 'approved' | 'rejected';
  language?: string;
}

type GetCalendarBriefsResult = Result<ContentBrief[], QueryError>;
```

### Events

```typescript
interface CalendarGenerated {
  type: 'research.calendar.generated';
  tenant_id: string;
  campaign_id: string;
  calendar_batch_id: string;
  brief_count: number;
  languages: string[];
}

interface BriefApproved {
  type: 'research.brief.approved';
  tenant_id: string;
  brief_id: string;
  keyword: string;
}

interface BriefRejected {
  type: 'research.brief.rejected';
  tenant_id: string;
  brief_id: string;
  keyword: string;
}

interface ApprovedBriefsExported {
  type: 'research.calendar.approved_exported';
  tenant_id: string;
  campaign_id: string;
  brief_count: number;
  output_path: string;
}
```

### Error Types

```typescript
type CalendarError =
  | { code: 'NO_GAP_DATA'; campaign_id: string }
  | { code: 'LLM_UNAVAILABLE'; fallback_used: boolean }
  | { code: 'SCHEMA_VALIDATION_FAILED'; brief_id: string; errors: string[] }
  | { code: 'SCHEMA_VERSION_MISMATCH'; expected: string; received: string }
  | { code: 'BRIEF_NOT_FOUND'; brief_id: string }
  | { code: 'INVALID_STATUS_TRANSITION'; current: string; requested: string };
```

## Component Design

### ContentBriefBuilder

**Responsibility:** Assemble a ContentBrief record from pipeline data.
**Input:** Gap record (F-006), keyword data (F-001), competitor benchmarks (F-005), intent (F-003)
**Output:** Partially populated ContentBrief (missing LLM recommendations and publish date)
**Key logic:**
- `recommended_word_count` = `Math.round((competitor_avg_word_count * 1.1) / 100) * 100` (10% above competitor avg, rounded to nearest 100)
- `include_faq` = `competitors_have_faq || search_intent === 'informational'`
- `existing_page_url` populated only when `gap_type === 'thin_content'`

### RecommendationEngine

**Responsibility:** LLM-powered recommendations grounded in competitor data.
**Input:** Keyword, intent, competitor headings (from F-005), competitor schema types
**Output:** `{ content_type, recommended_headings, recommended_schema_types }`
**Prompt:** Versioned at `prompts/content-calendar/v1.txt`. Structured JSON output enforced.
**Grounding:** Prompt includes competitor H2 headings as context. LLM synthesises (not invents). Output tagged `"llm_recommended"`.
**Fallback:** If LLM fails after 2 retries, use most common competitor content type + competitor H2 headings directly. Tag as `"extracted from competitor — LLM unavailable"`.

### PublishScheduler

**Responsibility:** Assign `suggested_publish_date` to each brief based on priority.
**Logic:**
1. Sort briefs by `opportunity_score` descending.
2. Starting from `start_date` (next Monday after pipeline run), assign briefs round-robin: `cadence_per_week` briefs per week.
3. New content briefs scheduled before thin content updates (separate section in calendar).

### LanguageScheduler

**Responsibility:** For multilingual campaigns, spread languages across weeks to avoid publishing 9 articles on the same topic in one week.
**Logic:**
1. Group briefs by keyword (cross-language).
2. Within each keyword group, stagger languages across consecutive weeks.
3. Primary language (from config, default EN) goes first; others follow in configured order.
**Example:** "FUE vs DHI" → EN in week 1, DE in week 2, FR in week 3, etc.

### CalendarRenderer

**Responsibility:** Generate Markdown and JSON output files.
**Markdown format:** Per requirements US-003 acceptance criteria (numbered entries with keyword, volume, difficulty, rationale, competitors, recommendation, headings, action checkboxes).
**Sections:** "New Content" (own_gap + new_opportunity, sorted by score) then "Content to Update" (thin_content, sorted by thin_content_priority_score).

### ApprovalWorkflow

**Responsibility:** Validate and process brief approvals/rejections.
**State machine:**
```
pending_review ──→ approved ──→ in_progress ──→ published
       │                              │
       └──→ rejected                  └──→ (set by E-002)
```
**Validation:** On approve/reject, validate entire ContentBrief against Zod schema. On export, re-validate all approved briefs.

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **Info Disclosure** — Cross-tenant calendar data leakage | H | RLS on content_brief table. All queries scoped by `tenant_id`. CI gate validates. |
| **Tampering** — Corrupted JSON during human editing breaks downstream pipeline | M | Triple Zod validation: on creation, on approval, on export. Descriptive error messages guide Malcolm to fix invalid edits. Schema version check prevents stale briefs from entering E-002. |

## ATAM-Lite

| Decision | Quality Attribute | Sensitivity | Trade-off |
|----------|------------------|:-----------:|-----------|
| Zod schema as single source of truth | **Reliability** vs **Flexibility** | High | Schema changes require version bump + ADR. Worth it: prevents silent data drift between E-001 and E-002. Schema evolution is managed, not ad-hoc. |
| Markdown + JSON dual output | **Usability** vs **Complexity** | Medium | Two renderers to maintain. Worth it: Markdown is the UX for Malcolm's 15-min review. JSON is the machine contract. Neither alone satisfies both audiences. |
| LLM for headings, not scoring | **Transparency** vs **Sophistication** | High | LLM could produce more nuanced scoring. But transparency is our differentiator (anti-pattern: SEO.ai black-box). Deterministic scoring is reproducible and auditable. LLM adds value where creativity matters (headings), not where formula matters (scoring). |
| Language staggering across weeks | **Quality** vs **Speed** | Medium | Multilingual topics take N weeks instead of 1 week for all languages. Worth it: avoids content cannibalism (same topic in 9 languages published same week). Spreads E-002 workload. |

## Build Boundaries

### Always (no approval needed)
- Write brief builder, renderer, scheduler code within this design
- Create the Zod schema file in `contracts/`
- Create prompt files in `prompts/content-calendar/`
- Run tests and fix failures
- Generate fixture calendars for testing

### Ask First
- Change the ContentBrief schema (any field addition, removal, or type change)
- Change the default publishing cadence (2/week)
- Add new content_type enum values
- Switch LLM from Haiku to Sonnet

### Never
- Write an invalid ContentBrief to output (skip validation)
- Auto-approve briefs without human review (the primary anti-pattern)
- Hardcode schema version (must come from config/constant)
- Skip RLS on content_brief table
- Include rejected briefs in approved-briefs export

## Test Architecture

### Test Pyramid

| Level | Count | What | Tools |
|-------|:-----:|------|-------|
| Unit | ~20 | ContentBriefBuilder assembly from fixture data, RecommendationEngine with mock LLM, PublishScheduler date assignment (edge cases: partial weeks, holidays), LanguageScheduler staggering logic, CalendarRenderer Markdown format, ApprovalWorkflow state transitions, Zod schema validation (valid + all invalid paths), rationale string generation | Vitest |
| Integration | ~8 | Full calendar generation from fixture gap matrix, approval workflow round-trip (create → approve → export), schema version mismatch detection, standalone file output, multi-language calendar with language staggering, LLM fallback path | Vitest + testcontainers |
| Property | ~4 | Every ContentBrief passes Zod validation (generate random valid briefs), publish dates are monotonically increasing for sorted briefs, no two briefs have the same date+language combination, approved export never contains rejected briefs | Vitest + fast-check |

### Mocking Strategy

- **LLM (RecommendationEngine):** Mock AI gateway returning fixture recommendations. Test both success and failure (fallback) paths.
- **Gap matrix (F-006):** Fixture `ContentGapRecord[]` arrays with various gap types and scores.
- **Competitor data (F-005):** Fixture benchmarks with headings, word counts, schema types.
- **Database:** testcontainers PostgreSQL for integration. Brief builder and renderer tests are stateless.
- **File system:** Use `tmp` directories for output file tests. Verify file contents match expected format.

### Property Invariants

1. Every `ContentBrief` produced passes `contentBriefSchema.parse()` — no invalid briefs escape the system.
2. `suggested_publish_date` values are in ascending order when sorted by `opportunity_score` descending — highest priority = earliest date.
3. `approved-briefs` export contains zero briefs with `status !== 'approved'` — rejected and pending briefs never leak into E-002 input.
4. `schema_version` is always `'1.0.0'` — version mismatch is caught before any processing.
5. For multilingual calendars, no two briefs share the same `(target_keyword, target_language, suggested_publish_date)` — no scheduling collisions.
