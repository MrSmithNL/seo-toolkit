---
id: "FTR-SEO-007"
type: feature
title: "Content Calendar / Planning"
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

# F-007: Content Calendar / Planning — Requirements

## Problem Statement

The E-001 Research & Strategy Engine produces keyword data, SERP analysis, competitor benchmarks, and gap identification — but all of that is useless if a human can't act on it. F-007 is the final stage of the research pipeline: it converts raw research data into an actionable, prioritised content calendar with enough context that Malcolm can review and approve 10 topics in under 15 minutes.

F-007 also serves a second, critical role: it defines the `ContentBrief` schema, the interface contract between E-001 (Research & Strategy) and E-002 (Content Creation). Every subsequent epic depends on this schema being well-defined. Getting it wrong here creates rework across multiple epics.

**Who has this problem:** Malcolm — needs to approve a content plan without becoming an SEO expert. Also every downstream pipeline stage — E-002 (Content Creation) consumes ContentBrief records produced here.

**Cost of inaction:** Without a calendar, all research stays in raw data form and Malcolm must manually synthesise it. The pipeline produces no actionable output. The 15-minute review target is impossible without structured recommendations. E-002 cannot start without a ContentBrief schema.

---

## Research Summary

> Extracted from E-001 Competitive Deep-Dive (539 lines, 4 competitors). Focus: calendar and planning features.

### Competitor Analysis (for this feature)

| Feature/Capability | Semrush | SEO.ai | Frase | SurferSEO | Prevalence | Our Approach | Rationale |
|-------------------|---------|--------|-------|-----------|:----------:|-------------|-----------|
| Content calendar / article queue | Yes — Content Calendar tool with scheduled publishing | Yes — auto-generates article queue (fully autonomous) | No — no calendar feature (weakness) | Not documented | 2/4 | AI-generated calendar with transparent priority scoring and human approval gate | Frase's missing calendar is cited as a product weakness on G2. SEO.ai's auto-publish without review gate is our documented anti-pattern. |
| Priority / opportunity scoring | Volume + KD shown per topic; no composite calendar score | Opaque scoring — topics appear in queue with no explanation | N/A | N/A | 1/4 | Transparent composite score: volume × difficulty inverse × gap × business value. Score components shown. | Differentiator — SEO.ai's black-box is top G2 complaint. Show your work. |
| Content format recommendation | Not documented | Auto-selects format (not shown) | Yes — brief-level format suggestion | Yes — type suggested | 2/4 | LLM recommends format with rationale (blog post / comparison / FAQ / how-to) based on intent classification (F-003) | Extends Frase/SurferSEO table stakes; adds transparent rationale |
| Human review workflow | Not applicable — web UI with manual editing | Auto-approved and queued (anti-pattern) | Not applicable | Not applicable | 0/4 | CLI: calendar output as Markdown + JSON; Malcolm reviews Markdown, edits JSON to approve/reject topics | Anti-pattern: SEO.ai auto-publish without approval (documented). HITL gate is our standard. |
| Cluster / pillar assignment | Yes | Not documented | Yes — brief includes cluster | Yes | 3/4 | Assign each calendar topic to a topic cluster (from F-002 if available; LLM fallback otherwise) | Table stakes — pillar/cluster structure is standard SEO practice |
| Suggested publish dates | Yes — calendar with scheduling | Yes | No | No | 2/4 | Suggest publish date based on topic priority rank (highest priority = earliest date, weekly cadence) | Simple rule-based scheduling sufficient for R1; not a UI calendar |
| ContentBrief output schema | Not applicable — web UI | Not applicable | Content Brief (UI output) | Content Brief (UI output) | 2/4 | Structured `ContentBrief` JSON schema — machine-readable interface contract to E-002 | Critical differentiator: competitors output human-readable briefs, not machine-readable contracts |

### Key Findings

- **Frase's lack of a calendar is a documented weakness** (G2 reviews cite it as missing). We ship a calendar and immediately exceed Frase's planning capability.
- **SEO.ai's auto-publish without review is the primary anti-pattern** to avoid. The 3.4/5 G2 rating is largely attributed to "it just does things and I don't know why." Human approval is non-negotiable.
- **Semrush's calendar is the closest competitor reference** but it requires the full Semrush subscription ($139/mo). Their table stakes: topic, keyword, format, word count estimate, scheduled date, assigned status.
- **The ContentBrief schema is our most important output** — it is not just a user-facing document, it is the machine-readable contract that E-002 (Content Creation), E-003 (Optimisation), and E-005 (Measurement) all depend on. Design it as a first-class API contract.
- **15-minute human review target** (epic-status.md success criteria): 10 topics × max 90 seconds each. This means each calendar entry must be self-explanatory with a brief rationale — not a wall of data.

### Sources

- Parent epic deep-dive: `specs/001-autonomous-content-engine/E-001-research-strategy/epic-status.md` § Competitive Deep-Dive
- Epic success criteria: `epic-status.md` § Epic Goal — "Human review time < 15 min for a 10-topic calendar"
- Hallucination risk: `epic-status.md` § Hallucination Risk Assessment — "< 15 min review: Define as 10 topics, each with 5 fields, max 90 sec per topic"
- Cross-epic dependency: `epic-status.md` § Dependencies — "ContentBrief schema (output contract to E-002)"

---

## ContentBrief Schema (Interface Contract: E-001 → E-002)

> This schema is the canonical definition of the data contract between the Research & Strategy Engine (E-001) and the Content Creation Engine (E-002). It MUST be defined here and referenced by all downstream features. Changes to this schema require a documented ADR.

```typescript
/**
 * ContentBrief — Interface contract between E-001 (Research) and E-002 (Content Creation).
 * Version: 1.0.0
 * Defined in: F-007 requirements (this file)
 * Consumed by: E-002 Content Creation, E-003 Optimisation, E-005 Measurement
 * Schema file: contracts/content-brief.schema.ts
 */
interface ContentBrief {
  // Identity
  id: string;                          // UUID — unique per brief
  tenant_id: string;                   // Multi-tenancy — Hairgenetix in R1
  created_at: string;                  // ISO 8601 timestamp
  schema_version: "1.0.0";             // Schema versioning — increment on breaking changes
  status: "pending_review" | "approved" | "rejected" | "in_progress" | "published";

  // Target and strategy
  target_keyword: string;              // Primary keyword to target (from F-001)
  target_language: string;             // BCP 47 language tag (e.g., "de", "fr", "en")
  target_country: string;              // ISO 3166-1 alpha-2 country code (e.g., "DE", "FR")
  supporting_keywords: string[];       // Related/LSI keywords to include (from F-001)
  search_intent: "informational" | "transactional" | "navigational" | "commercial"; // From F-003
  topic_cluster: string | null;        // Cluster name from F-002 (null if F-002 not run)
  content_type: "blog_post" | "comparison" | "how_to" | "faq" | "product_page" | "landing_page";

  // Research inputs (from pipeline stages)
  keyword_volume: number;              // Monthly search volume (from F-001, Keywords Everywhere)
  keyword_difficulty: number;          // 0-100 difficulty score (from F-001)
  opportunity_score: number;           // 0-1 composite score (from F-006)
  opportunity_score_rationale: string; // Human-readable explanation of score
  gap_type: "own_gap" | "thin_content" | "new_opportunity"; // From F-006
  existing_page_url: string | null;    // Populated if gap_type = "thin_content" (page to update)

  // Competitor benchmarks (from F-005)
  competitor_avg_word_count: number;   // Average word count of top-3 ranking competitor pages
  competitor_depth_scores: number[];   // Array of depth scores from F-005 quality assessment
  top_competitor_url: string | null;   // Highest-ranking competitor page for this keyword
  competitor_schema_types: string[];   // Schema types used by competitors (for AISO targeting)
  competitors_have_faq: boolean;       // True if any top competitor has an FAQ section

  // Content recommendations
  recommended_word_count: number;      // Suggested target (competitor_avg × 1.1, rounded to nearest 100)
  recommended_headings: string[];      // Suggested H2 structure (LLM-generated, based on competitor analysis)
  recommended_schema_types: string[];  // Schema types to implement (inferred from competitor analysis + intent)
  include_faq: boolean;                // Recommended if competitors_have_faq OR intent=informational
  suggested_publish_date: string;      // ISO 8601 date — based on priority rank and publishing cadence

  // Human review fields (populated during approval)
  reviewed_by: string | null;          // Set when approved/rejected
  reviewed_at: string | null;          // ISO 8601 timestamp
  review_notes: string | null;         // Optional Malcolm notes/edits
  overridden_word_count: number | null; // If Malcolm adjusts word count during review
  overridden_publish_date: string | null; // If Malcolm adjusts date during review
}
```

> **Schema governance:** This schema is the source of truth. The TypeScript interface above is generated into `contracts/content-brief.schema.ts`. All consumers (E-002, E-003, E-005) import from this contract file. Any breaking change (field removal, type narrowing) requires a new `schema_version` and an ADR.

---

## User Stories

### US-001: AI-Generated Calendar from Gap Analysis

**As a** pipeline operator, **I want** the system to generate a prioritised content calendar from the F-006 gap matrix, **so that** the research output becomes an actionable plan without manual synthesis.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

```
WHEN F-001 (keyword data) and F-006 (gap analysis) outputs are available
THE SYSTEM SHALL generate a ContentBrief record for each own_gap and new_opportunity row
AND sort ContentBrief records by opportunity_score descending
AND produce a separate "content to update" list for thin_content rows
AND each ContentBrief SHALL be fully populated with all required schema fields
```

```
WHEN generating ContentBrief records
THE SYSTEM SHALL use an LLM to produce:
  - content_type recommendation (based on search_intent from F-003 and competitor content types)
  - recommended_headings (H2 structure, 4-8 suggested headings based on competitor heading analysis from F-005)
  - recommended_schema_types (based on competitor schema + search intent)
AND include a one-sentence rationale for each LLM-generated recommendation
```

```
WHEN a keyword has no cluster assignment (F-002 not run or not complete)
THE SYSTEM SHALL use LLM-based cluster inference:
  - Group semantically related keywords
  - Assign cluster name based on dominant topic
  - Set topic_cluster field with the cluster name
  - Tag as "inferred" to distinguish from F-002 algorithm output
```

```
WHEN the calendar is generated
THE SYSTEM SHALL assign suggested_publish_date based on:
  - Publishing cadence: default 2 articles per week (configurable)
  - Priority order: highest opportunity_score = earliest date
  - Start date: next Monday after pipeline run date (configurable)
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | F-006 gap matrix: 15 own_gap rows, 3 thin_content rows | 15 ContentBrief records (new content), sorted by opportunity_score desc; 3 thin_content entries in separate "update" section |
| Content type inference | Keyword "FUE vs DHI comparison", intent=commercial | content_type="comparison", recommended_headings=["What is FUE?", "What is DHI?", "FUE vs DHI: Key differences", "Cost comparison", "Which is right for you?", "FAQ"] |
| Schema recommendation | Top competitors all use Article + FAQPage schema | recommended_schema_types=["Article", "FAQPage"], include_faq=true |
| No F-002 cluster data | F-002 not run | topic_cluster="Hair Transplant Techniques (inferred)", tagged as inferred cluster |
| Publish date assignment | 15 topics, 2/week cadence, pipeline runs 2026-03-15 (Sunday) | First topic: 2026-03-16 (Monday), last topic: 2026-04-27 (2/week × 7.5 weeks) |
| Only thin content gaps | All gaps are thin_content type | Calendar has 0 new content entries; "update" section has all entries; briefed accordingly |

---

### US-002: Priority Scoring Algorithm

**As a** store owner, **I want** to understand why each topic is ranked the way it is, **so that** I can trust the calendar recommendations and approve with confidence in under 15 minutes.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN generating ContentBrief records
THE SYSTEM SHALL populate opportunity_score from F-006 output (not recalculate)
AND populate opportunity_score_rationale with a human-readable explanation
USING the format:
  "Score: [score] — [volume_label] ([volume]/mo), [difficulty_label] ([difficulty]/100), [gap_label]."
WHERE:
  volume_label = "High volume" if volume > 5000 | "Medium volume" if 500-5000 | "Low volume" if < 500
  difficulty_label = "easy to rank" if difficulty < 30 | "moderate competition" if 30-60 | "hard to rank" if > 60
  gap_label = "no competitor in top 5" | "competitor at position [n]" | "we rank at #[n] but content is thin"
```

```
WHEN the opportunity_score_rationale is displayed in the Markdown calendar
THE SYSTEM SHALL show it as a one-line summary under each topic title
so that Malcolm can read 10 rationale lines in < 5 minutes during review
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| High-priority new topic | volume=8100, difficulty=32, gap_score=1.0 (no competitor in top 5) | rationale: "Score: 0.74 — High volume (8,100/mo), easy to rank (32/100), no competitor in top 5." |
| Medium-priority topic | volume=2400, difficulty=48, competitor at #7 | rationale: "Score: 0.52 — Medium volume (2,400/mo), moderate competition (48/100), competitor at position 7." |
| Thin content upgrade | ranks #18, our page 420 words, competitor avg 2,800 | rationale: "Priority: 0.82 — We rank #18. Our page is 420 words vs competitor average of 2,800. Strong update opportunity." |
| Zero-volume AISO topic | volume=0, flagged "zero volume — AISO value only" | rationale: "Score: 0.15 (AISO only) — Zero search volume. Low difficulty (18/100). Recommended for AI citation only, not organic traffic." |

---

### US-003: Human Review and Approval Workflow

**As a** store owner, **I want** to review and approve the content calendar in a simple format, **so that** I can make go/no-go decisions on each topic in under 15 minutes total.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

```
WHEN the calendar is generated
THE SYSTEM SHALL output two files:
  1. `calendar-YYYY-MM-DD.md` — Human-readable Markdown for review
  2. `calendar-YYYY-MM-DD.json` — Machine-readable JSON array of ContentBrief records for approval
```

```
WHEN generating the Markdown review file
THE SYSTEM SHALL format each calendar entry as:

## [n]. [Topic Title] ([content_type])
**Keyword:** [target_keyword] | **Volume:** [keyword_volume]/mo | **Difficulty:** [keyword_difficulty]/100
**Rationale:** [opportunity_score_rationale]
**Competitors:** Avg [competitor_avg_word_count] words, depth [avg_depth_score]/5. Top: [top_competitor_url]
**Our recommendation:** [recommended_word_count] words, [content_type], publish [suggested_publish_date]
**Headings:** [recommended_headings joined as bullet list]
**Action:** [ ] Approve | [ ] Reject | [ ] Edit (add notes below)

---
```

```
WHEN Malcolm approves a ContentBrief
THE SYSTEM SHALL accept approval via:
  - Editing the JSON file: set status = "approved" on each approved brief
  - OR running the CLI command: `seo-toolkit calendar approve --id [brief-id]`
AND set reviewed_by (from config), reviewed_at (current timestamp)
AND validate the JSON against the ContentBrief schema before accepting
```

```
WHEN Malcolm rejects a topic
THE SYSTEM SHALL set status = "rejected" AND preserve the brief record
AND NOT include rejected briefs in the E-002 pipeline input
```

```
WHEN a calendar is approved
THE SYSTEM SHALL output an `approved-briefs-YYYY-MM-DD.json` file
containing only status="approved" ContentBrief records
as the input to E-002 (Content Creation Engine)
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Full approval | Malcolm edits JSON, sets all 10 to status="approved" | approved-briefs file created with 10 records; all validated against ContentBrief schema |
| Partial approval | Malcolm approves 7, rejects 3 | approved-briefs file has 7 records; rejected briefs remain in calendar JSON with status="rejected" |
| Edit during review | Malcolm changes overridden_word_count from 1800 to 2400 | ContentBrief updated, overridden_word_count=2400 preserved alongside recommended_word_count=1800 |
| Invalid JSON edit | Malcolm accidentally corrupts JSON | Schema validation catches error, outputs: "Invalid ContentBrief at index 3: required field 'target_keyword' is missing." |
| CLI approval | `seo-toolkit calendar approve --id abc123` | ContentBrief with id=abc123 set to status="approved", reviewed_at=now |

---

### US-004: ContentBrief Schema Validation

**As a** developer building E-002, **I want** every ContentBrief record to be validated against the schema before it leaves E-001, **so that** E-002 can consume briefs without defensive validation logic.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

```
WHEN a ContentBrief record is created or updated
THE SYSTEM SHALL validate it against the Zod schema derived from the ContentBrief interface
AND reject any record that fails validation with a descriptive error message
AND NEVER write an invalid ContentBrief to the output file or database
```

```
WHEN the schema version in a ContentBrief record does not match the current schema version
THE SYSTEM SHALL reject the record AND output:
  "ContentBrief schema mismatch: brief version [n] is incompatible with current version [m]. Regenerate this brief."
```

```
WHEN outputting approved-briefs-YYYY-MM-DD.json
THE SYSTEM SHALL validate every record in the file as a final check before writing
AND include a schema_version field at the file root level alongside the records array
```

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Valid brief | All required fields present, correct types | Brief written to output file |
| Missing required field | ContentBrief without target_keyword | Error: "Invalid ContentBrief: target_keyword is required." Record not written. |
| Schema version mismatch | Brief created with schema v0.9.0, current is v1.0.0 | Error: "Schema mismatch: brief version 0.9.0, current 1.0.0. Regenerate this brief." |
| Invalid enum value | content_type = "infographic" (not in enum) | Error: "Invalid ContentBrief: content_type must be one of: blog_post, comparison, how_to, faq, product_page, landing_page." |

---

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN generating a 10-topic calendar THE SYSTEM SHALL complete within 2 minutes (including LLM calls for headings + format recommendations) | p95 < 2 min | Integration test with timer | No |
| 2 | **Scalability** | N/A — R1 targets calendars of 10-30 topics maximum. Not an at-scale requirement. | — | — | No |
| 3 | **Availability** | N/A — CLI tool, no uptime SLA for R1 | — | — | No |
| 4 | **Reliability** | WHEN an LLM call for heading generation fails THE SYSTEM SHALL fall back to competitor heading data from F-005 AND mark recommended_headings as "extracted from competitor — LLM unavailable" | 0 pipeline halts from LLM failures | Integration test with mock LLM failure | Yes |
| 5 | **Security** | N/A — no external systems accessed in this feature beyond the LLM API already covered by F-001 NFRs | — | — | No |
| 6 | **Privacy** | N/A — all data is SEO research data; no PII processed | — | — | No |
| 7 | **Compliance / Regulatory** | N/A — content planning feature; no regulatory requirements | — | — | No |
| 8 | **Interoperability** | WHEN outputting ContentBrief records THE SYSTEM SHALL validate against the canonical ContentBrief Zod schema (contracts/content-brief.schema.ts) | Schema validation on every write | Unit test: invalid brief is rejected | Yes |
| 9 | **Portability** | WHEN running in standalone mode THE SYSTEM SHALL output `calendar-YYYY-MM-DD.md` and `calendar-YYYY-MM-DD.json` to `data/calendar/{domain}/` | Output files produced in standalone mode | Integration test confirms file output | Yes |
| 10 | **Maintainability** | WHEN the ContentBrief schema changes THE SYSTEM SHALL increment schema_version AND all consumers SHALL check schema_version before consuming | Schema change = version bump + ADR | Architecture review | No |
| 11 | **Testability** | WHEN testing THE SYSTEM SHALL support fixture-based input (mock gap matrix + mock keyword data) so calendar generation tests run without live pipeline data | Unit tests run fully offline with fixture input | Test suite passes without network or DB | Yes |
| 12 | **Usability** | WHEN generating the Markdown review file THE SYSTEM SHALL produce an output that allows review of 10 topics in < 15 minutes | User test: Malcolm reviews 10 topics, time logged. Target: < 15 min | R1 pilot with Malcolm | No |
| 13 | **Localisation** | WHEN generating calendars for multiple languages THE SYSTEM SHALL produce a separate calendar per language AND a cross-language summary showing universal gaps vs language-specific gaps | 9-language calendar produced for Hairgenetix | Integration test with 2-language fixture | No |
| 14 | **Monitoring** | WHEN calendar generation completes THE SYSTEM SHALL log: topics generated, LLM calls made, tokens consumed, duration, file paths output | Structured JSON log entry | Log schema validation | No |
| 15 | **Auditability** | WHEN a ContentBrief is approved or rejected THE SYSTEM SHALL record reviewed_by, reviewed_at, and review_notes in the brief record | All state changes include audit fields | Unit test checks audit fields on approve/reject | No |
| 16-35 | Remaining categories | N/A — R1 CLI tool; enterprise NFRs apply from R2 (platform integration) | — | — | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN generating heading recommendations for a ContentBrief THE SYSTEM SHALL complete the LLM call within 15 seconds | p95 < 15s per brief | Integration test with timer |
| Token economics | WHEN generating heading recommendations and content type rationale THE SYSTEM SHALL consume < 1K tokens per ContentBrief AND < 15K tokens for a 10-topic calendar | < $0.15 per 10-topic calendar at Claude Haiku pricing | Token counter in logs |
| Hallucination rate | WHEN LLM generates recommended_headings THE SYSTEM SHALL ground them in competitor heading data from F-005 AND flag as "llm_recommended — based on competitor analysis" | 100% of LLM-recommended fields flagged | Unit test checks field flags |
| Model degradation detection | N/A — heading quality is reviewed by Malcolm before approval. Human review gate catches degraded output. | — | — |
| Prompt versioning | WHEN using LLM prompts for heading generation and format recommendation THE SYSTEM SHALL version prompts in `prompts/content-calendar/` directory | All prompts in prompts/ directory | File structure check |

---

## Mandatory Requirement Dimensions

### Dimension A: User Interaction & Experience

| Check | Status | Detail |
|-------|:------:|--------|
| Interaction modality confirmed | [x] | CLI for R1 (approved at Gate 1). Human review via generated Markdown + JSON files. |
| User personas and goals | [x] | JTBD 2 and 4: prioritised article list; transparent reasoning for approval in < 15 min. |
| User journeys mapped | [x] | Pipeline runs → calendar files generated → Malcolm opens .md file → reads rationale → edits .json to approve/reject → runs approve command → approved-briefs.json produced → E-002 starts. |
| N/A justification | [x] | No UI for R1. The Markdown review file IS the UX for this stage. Usability requirement in NFR #12 covers the 15-minute review target. Dashboard view in E-006 (R2+). |

### Dimension B: User Management & Access Control

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | R1 is single-user CLI. reviewed_by populated from config (not auth). Auth deferred to platform integration (R2+). |

### Dimension C: Administration & Software Management

| Check | Status | Detail |
|-------|:------:|--------|
| Feature flags | [x] | F-007 behind `FEATURE_CONTENT_CALENDAR` flag. Publishing cadence (default 2/week) and start date configurable via `.env`. |
| Config management | [x] | Publishing cadence, start date, and output directory configurable. ContentBrief schema version pinned in config. |
| N/A justification | [x] | No admin UI, billing, or reporting for R1. |

### Dimension D: Integration & Interoperability

| Check | Status | Detail |
|-------|:------:|--------|
| External system inventory | [x] | Claude API (heading + format recommendation LLM calls). No other external APIs. F-001, F-003, F-005, F-006 are all internal pipeline outputs. |
| API protocol | [x] | Internal: TypeScript module exports (commands/queries pattern). Output: JSON files (R1), later REST API (R2+). ContentBrief schema: contracts/content-brief.schema.ts (Zod + TypeScript types). |
| Resilience per dependency | [x] | LLM: retry 2x on 429/500, fallback to competitor-heading extraction if unavailable. Input data (F-006): validate completeness before running, warn if partial data. |
| Interface contract | [x] | ContentBrief schema defined in this file (§ ContentBrief Schema above). Consumed by E-002, E-003, E-005. Schema versioned. Changes require ADR. |

### Dimension E: Transition, Migration & Interim Solutions

| Check | Status | Detail |
|-------|:------:|--------|
| N/A justification | [x] | Greenfield feature — no migration. ContentBrief schema designed for forward-compatibility with platform DB. Schema versioning enables non-breaking evolution. |

### Dimension F: Operational Requirements

| Check | Status | Detail |
|-------|:------:|--------|
| Logging | [x] | Structured JSON logs: topics generated, LLM calls, tokens, output file paths, duration |
| Cost budget | [x] | LLM heading generation: < $0.15 per 10-topic calendar (15K tokens × Haiku pricing). Total E-001 LLM cost: < $0.50 per pipeline run. |
| N/A justification | [x] | No SLOs, alerting, or incident response for R1 CLI tool. Added at platform integration (R2+). |

### Competitive Context

| Requirement ID | Origin Tag | Source | Source Dimension |
|---------------|-----------|--------|:----------------:|
| US-001 (AI-generated calendar) | `[table-stakes]` | Semrush Content Calendar, SEO.ai article queue | 1-Features |
| US-001 (human approval gate) | `[anti-pattern]` | SEO.ai auto-publish without review — primary documented anti-pattern | 2-Workflows |
| US-002 (transparent scoring) | `[differentiator]` | SEO.ai black-box scoring = top G2 complaint. Semrush shows volume + KD separately but no composite score. | 2-Workflows |
| US-002 (rationale per topic) | `[differentiator]` | 0/4 competitors generate plain-English rationale per calendar entry | 3-UI |
| US-003 (Markdown + JSON dual output) | `[differentiator]` | All competitors are web-only UIs. Markdown + JSON enables CLI-first review without a dashboard. | 2-Workflows |
| US-004 (ContentBrief schema contract) | `[differentiator]` | All competitors output human-readable briefs, not machine-readable contracts. Schema contract enables the autonomous pipeline. | 5-Data |
| Schema (cluster assignment) | `[table-stakes]` | Frase, SurferSEO, Semrush all include cluster/pillar assignment in brief output | 1-Features |
| Schema (schema_type recommendations) | `[differentiator]` | 0/4 competitors recommend schema markup types in content briefs | 1-Features |

---

## ContentBrief Schema — Field Justification

> Every schema field must earn its place. This table justifies each field against a consumer or requirement.

| Field | Justification | Consumed by |
|-------|--------------|-------------|
| id | Required for approval workflow, deduplication, audit | US-003, E-002, E-003 |
| tenant_id | Multi-tenancy (R2+); populated from config in R1 | Platform integration |
| schema_version | Enables non-breaking schema evolution; consumers check before consuming | US-004, all downstream |
| status | Drives approval workflow and E-002 input filter | US-003, E-002 |
| target_keyword | Primary optimisation target for content writer | E-002 content creation |
| target_language + country | Multilingual pipeline support (9 languages for Hairgenetix) | E-002, E-005 |
| supporting_keywords | Related terms to include naturally in content | E-002 |
| search_intent | Determines content format and tone | US-001, E-002 |
| topic_cluster | Enables pillar/cluster linking in E-002 | E-002, E-003 |
| content_type | Tells E-002 the format to produce | US-001, E-002 |
| keyword_volume + difficulty | Reproduced in brief so E-002 doesn't need to re-query F-001 | Audit, E-005 |
| opportunity_score + rationale | Human review (US-002, US-003); priority sorting | US-002, US-003 |
| gap_type + existing_page_url | Tells E-002 whether to create new or update existing | US-001, E-002 |
| competitor_avg_word_count | Sets word count target for E-002 | E-002 |
| competitor_depth_scores | Context for E-002 quality benchmark | E-002 |
| top_competitor_url | E-002 can reference top competitor for structural inspiration | E-002 |
| competitor_schema_types | E-002 knows which schema to implement | E-002, E-003 |
| competitors_have_faq | Tells E-002 to include FAQ section | E-002 |
| recommended_word_count | Default word count target for E-002 (overridable by Malcolm) | E-002 |
| recommended_headings | Structural scaffold for E-002 content writer | E-002 |
| recommended_schema_types | E-002 implements these schema types in article | E-002, E-003 |
| include_faq | E-002 knows to generate FAQ section | E-002 |
| suggested_publish_date | Calendar scheduling; E-002 can prioritise work queue | US-003, E-002 |
| reviewed_by + reviewed_at + review_notes | Audit trail; Malcolm edits are preserved | US-003, US-004 |
| overridden_* fields | Malcolm's overrides preserved alongside recommendations | Audit, E-002 |

---

## Out of Scope

- Automatic publishing or scheduling to CMS — calendar only (auto-publish is the primary anti-pattern)
- Visual calendar UI or Gantt-style view — Markdown is the R1 interface; dashboard in E-006 (R2+)
- Team collaboration features (assign topics to writers, status tracking) — R2+
- Content calendar editing via web UI — CLI + JSON editing for R1
- Paid/sponsored content planning — organic content only
- Social media or email content calendar — web content only in R1
- Budget tracking or cost per article estimates — not in scope for research stage

---

## Open Questions

- [ ] Should the Markdown review file include the full recommended heading list, or a summary? Proposed: full heading list (4-8 H2s per topic). At 10 topics, this is 40-80 headings — acceptable in a file; too much in a table. Confirm with Malcolm.
- [ ] Should approved-briefs.json be the direct E-002 input, or should there be a staging step? Proposed: direct input for R1 (E-002 reads approved-briefs.json). Staging step in R2+ when platform queuing (BullMQ) is added.
- [ ] What is the minimum calendar size to be useful? Proposed: minimum 3 approved briefs before E-002 is triggered. Single-brief batches waste E-002 LLM context setup overhead.
- [ ] Can Malcolm reject a topic and request a replacement from the pipeline? Proposed: R1 — rejected topics are noted but no auto-replacement. Re-run the pipeline to get fresh recommendations. R2+: rejection triggers replacement suggestion.
- [x] Is < 15 minutes a hard requirement or a target? From Hallucination Risk Assessment: defined as 10 topics × 5 fields × max 90 sec per topic = 15 min maximum. This is a hard acceptance criterion for the R1 pilot.

---

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 Keyword Research | Internal | Not started | ContentBrief: keyword_volume, keyword_difficulty, supporting_keywords |
| F-003 Search Intent Classification | Internal | Not started | ContentBrief: search_intent — required for content_type recommendation |
| F-005 Competitor Content Analysis | Internal | Not started | ContentBrief: competitor fields, recommended_headings grounding |
| F-006 Content Gap Identification | Internal | Not started | ContentBrief: opportunity_score, gap_type, existing_page_url |
| Claude API (LLM) | External | Available | US-001 heading generation, content_type recommendations |
| E-002 Content Creation Engine | Internal (downstream) | Not started | Consumes approved ContentBrief records — schema must be finalised before E-002 starts |
| contracts/content-brief.schema.ts | Internal | Must create | All features — Zod schema file must be created from the interface defined in this spec |

---

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | A 10-topic Markdown calendar can be reviewed by Malcolm in < 15 minutes | Medium | Validate during R1 pilot. If review takes > 15 min, reduce fields shown or restructure Markdown format. |
| A2 | Claude Haiku can generate accurate H2 heading structures from competitor heading data + keyword + intent | High | Heading generation is a well-defined, low-hallucination task (grounded in competitor data) |
| A3 | The ContentBrief schema v1.0.0 is sufficient for E-002 to start content creation without additional research | Medium | E-002 lead reviews schema before their epic starts. Flag gaps before Gate 3. |
| A4 | A 2-articles/week default publishing cadence is appropriate for Hairgenetix R1 | Medium | Confirm with Malcolm. Configurable — this is only the default. |
| A5 | JSON file editing is an acceptable approval mechanism for Malcolm in R1 | Medium | Confirm. Alternative: simple CLI Y/N prompt per topic. Decide before build. |
