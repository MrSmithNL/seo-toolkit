# F-007: Content Calendar / Planning — Tasks

## Task T-001: ContentBrief Zod Schema & Contract [Foundation]
**Story:** US-004 (Schema Validation)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Create the canonical ContentBrief Zod schema per ADR-F007-001 in `contracts/content-brief.schema.ts`. Generate TypeScript types from Zod (`z.infer`). Define the `approvedBriefsFileSchema` wrapper. This is the single source of truth for the E-001→E-002 interface, validated triple: on creation, on update, on export.

### Files
- Create: `modules/content-engine/research/contracts/content-brief.schema.ts`
- Create (tests): `modules/content-engine/research/contracts/__tests__/content-brief.schema.test.ts`

### Test Scenarios (from tests.md)
- ATS-020: Valid brief passes validation
- ATS-021: Missing required field rejected
- ATS-022: Schema version mismatch rejected
- ATS-023: Invalid enum value rejected
- ATS-024: Approved-briefs file validated before writing
- PI-001: ContentBrief ID unique (UUID)
- PI-002: All required fields present
- PI-003: Schema version pinned to "1.0.0"
- PI-004: Valid status values (5 options)
- PI-005: Valid content_type enum
- PI-006: Valid search_intent enum
- PI-007: Opportunity score range 0.0-1.1

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Full ContentBrief Zod schema per design.md (all fields, correct types)
- [ ] `ContentBrief` TypeScript type derived via `z.infer`
- [ ] `approvedBriefsFileSchema` wrapper with schema_version, generated_at, briefs array
- [ ] Validation tests: valid pass, every invalid case has clear error message
- [ ] Property tests: randomly generated valid briefs always pass parse
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write schema, types, tests
- Ask: add/remove/change fields (schema change = version bump + ADR)
- Never: hand-write TypeScript types (derive from Zod)

---

## Task T-002: ContentBriefBuilder [Domain Logic]
**Story:** US-001 (Calendar from Gap Analysis)
**Size:** M
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Implement the `ContentBriefBuilder` that assembles a ContentBrief record from pipeline data. Takes gap record (F-006), keyword (F-001), competitor benchmarks (F-005), intent (F-003). Computes `recommended_word_count` (10% above competitor avg, rounded to nearest 100), `include_faq` (competitors have FAQ OR informational intent), `existing_page_url` (thin_content only).

### Files
- Create: `modules/content-engine/research/services/content-brief-builder.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/content-brief-builder.test.ts`
- Create: `modules/content-engine/research/__fixtures__/brief-builder-inputs.json`

### Test Scenarios (from tests.md)
- ATS-001: 15 own_gap + 3 thin_content → correct brief count
- ATS-002: Commercial intent → comparison content_type with appropriate headings
- ATS-003: Competitors have FAQ → recommended_schema_types includes FAQPage
- PI-008: recommended_word_count > 0
- PI-012: thin_content → existing_page_url non-null

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `recommended_word_count = Math.round((competitor_avg * 1.1) / 100) * 100`
- [ ] `include_faq = competitors_have_faq || intent === 'informational'`
- [ ] `existing_page_url` set only for thin_content gap_type
- [ ] Status defaults to `pending_review`
- [ ] All ContentBriefs pass Zod validation on creation (triple validation: step 1)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change word count multiplier or FAQ logic
- Never: skip Zod validation on creation

---

## Task T-003: RecommendationEngine (LLM) [Domain Logic]
**Story:** US-001
**Size:** M
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Implement the `RecommendationEngine` per ADR-F007-003. LLM-powered recommendations grounded in competitor data. Input: keyword, intent, competitor headings (F-005), competitor schema types. Output: content_type, recommended_headings, recommended_schema_types. Prompt versioned at `prompts/content-calendar/v1.txt`. Fallback: if LLM fails after 2 retries, use competitor headings directly.

### Files
- Create: `modules/content-engine/research/services/recommendation-engine.ts`
- Create: `modules/content-engine/research/prompts/content-calendar/v1.txt`
- Create (tests): `modules/content-engine/research/services/__tests__/recommendation-engine.test.ts`
- Create: `modules/content-engine/research/__fixtures__/recommendation-response.json`

### Test Scenarios (from tests.md)
- ATS-002: Content type inferred from intent + competitive landscape
- ATS-003: Schema types from competitor analysis
- ATS-004: No F-002 cluster data → LLM infers topic cluster (tagged "inferred")
- ATS-007: LLM failure → fallback to competitor headings (tagged)
- INT-004: Heading generation < 1K tokens per brief

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Prompt grounded in competitor H2 headings
- [ ] Structured JSON output: content_type, headings, schema_types
- [ ] LLM failure → 2 retries → fallback to competitor headings
- [ ] Fallback tagged `"extracted from competitor — LLM unavailable"`
- [ ] Prompt versioned in `prompts/content-calendar/`
- [ ] Mock AI gateway in tests
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, version prompts
- Ask: switch from Haiku to Sonnet, add output fields
- Never: use inline prompts, invent headings without competitor grounding

---

## Task T-004: PublishScheduler [Domain Logic]
**Story:** US-001 (Publish Date Assignment)
**Size:** S
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the `PublishScheduler` that assigns `suggested_publish_date` to each brief based on priority. Sorts by opportunity_score descending, assigns round-robin with configurable cadence (default 2/week), starting from next Monday. New content before thin content updates.

### Files
- Create: `modules/content-engine/research/services/publish-scheduler.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/publish-scheduler.test.ts`

### Test Scenarios (from tests.md)
- ATS-005: 15 topics, 2/week → first on Monday, last ~7.5 weeks out
- ATS-006: 0 new content, 8 thin → only update section
- PI-009: Publish dates sorted by priority (highest score = earliest)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Sort by opportunity_score descending
- [ ] Cadence configurable (default 2/week)
- [ ] Start date: next Monday after pipeline run
- [ ] New content scheduled before thin content updates
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change default cadence
- Never: assign same date to multiple same-language briefs

---

## Task T-005: LanguageScheduler [Domain Logic]
**Story:** US-001 (Multilingual scheduling)
**Size:** S
**Depends on:** T-004
**Parallel:** No

### What
Implement the `LanguageScheduler` for multilingual campaigns. Groups briefs by keyword cross-language, staggers languages across consecutive weeks (EN week 1, DE week 2, FR week 3 etc.). Primary language goes first (configurable, default EN).

### Files
- Create: `modules/content-engine/research/services/language-scheduler.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/language-scheduler.test.ts`

### Test Scenarios (from tests.md)
- INT-006: Multi-language calendar with staggering
- PI-009: No scheduling collisions for same (keyword, language, date)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Groups briefs by keyword across languages
- [ ] Staggers languages across weeks
- [ ] Primary language first (configurable)
- [ ] No two briefs share same (keyword, language, date)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change language order logic
- Never: publish same keyword in all languages same week

---

## Task T-006: CalendarRenderer (Markdown + JSON) [Integration]
**Story:** US-003 (Human Review)
**Size:** M
**Depends on:** T-001 (schema for validation)
**Parallel:** Yes [P]

### What
Implement the `CalendarRenderer` per ADR-F007-002 that produces two output files: Markdown for human review and JSON for machine consumption. Markdown format per requirements US-003 with numbered entries, keyword details, rationale, competitor benchmarks, recommendations, headings, action checkboxes. Sections: "New Content" then "Content to Update".

### Files
- Create: `modules/content-engine/research/services/calendar-renderer.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/calendar-renderer.test.ts`

### Test Scenarios (from tests.md)
- ATS-013: Two files created (markdown + JSON)
- ATS-014: Markdown structure correct (numbered, keyword, volume, rationale, etc.)
- ATS-012: 10 rationales readable in < 5 minutes (concise format)
- INT-005: Standalone file output

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Markdown: numbered entries, keyword, volume, difficulty, rationale, benchmarks, recommendation, headings, checkboxes
- [ ] Sections: "New Content" (sorted by score) then "Content to Update" (thin content)
- [ ] JSON: full ContentBrief array, validated against Zod schema
- [ ] Output to `data/calendar/{domain}/calendar-YYYY-MM-DD.{md,json}`
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change markdown format
- Never: skip JSON validation, put approved-briefs logic in renderer

---

## Task T-007: ApprovalWorkflow [Integration]
**Story:** US-003 (Human Review and Approval)
**Size:** M
**Depends on:** T-001, T-006
**Parallel:** No

### What
Implement the `ApprovalWorkflow` with state machine: `pending_review → approved → in_progress → published` and `pending_review → rejected`. `ApproveBriefCommand`, `RejectBriefCommand`, and `ExportApprovedBriefsCommand`. Triple Zod validation: on approval, on rejection (re-validate), on export. Handles overrides (word count, publish date).

### Files
- Create: `modules/content-engine/research/services/approval-workflow.ts`
- Create: `modules/content-engine/research/commands/approve-brief.ts`
- Create: `modules/content-engine/research/commands/reject-brief.ts`
- Create: `modules/content-engine/research/commands/export-approved-briefs.ts`
- Create: `modules/content-engine/research/events/calendar-events.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/approval-workflow.test.ts`

### Test Scenarios (from tests.md)
- ATS-015: Full approval → approved-briefs created
- ATS-016: Partial approval → only approved in export
- ATS-017: Word count override preserved alongside original
- ATS-018: Invalid JSON edit caught by validation
- ATS-019: CLI approval command
- PI-010: Rejected briefs excluded from export
- PI-014: Approved/rejected always have reviewed_by + reviewed_at

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] State machine: valid transitions enforced, invalid blocked with clear error
- [ ] `ApproveBriefCommand` sets status, reviewed_by, reviewed_at, optional overrides
- [ ] `RejectBriefCommand` sets status, reviewed_by, reviewed_at, review_notes
- [ ] `ExportApprovedBriefsCommand` produces approved-briefs JSON (validated)
- [ ] Triple validation: on creation, on approval/rejection, on export
- [ ] Schema version check on export
- [ ] Rejected briefs NEVER in approved-briefs output
- [ ] `BriefApproved`, `BriefRejected`, `ApprovedBriefsExported` events emitted
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new status values, change state machine
- Never: auto-approve without human review, include rejected in export

---

## Task T-008: ContentBriefRepo (DB + File) [Integration]
**Story:** US-001, US-003
**Size:** M
**Depends on:** T-001 (schema)
**Parallel:** Yes [P]

### What
Implement the `ContentBriefPort` interface with `DatabaseContentBriefRepo` and `FileContentBriefRepo`. Both support create, update (status changes), getByBatch, getByStatus queries. Full brief stored as validated JSON in `brief_data` column with denormalised fields for queries.

### Files
- Create: `modules/content-engine/research/ports/content-brief-port.ts`
- Create: `modules/content-engine/research/repos/db-content-brief-repo.ts`
- Create: `modules/content-engine/research/repos/file-content-brief-repo.ts`
- Create (tests): `modules/content-engine/research/repos/__tests__/content-brief-repo.test.ts`

### Test Scenarios (from tests.md)
- INT-005: Standalone file output
- INT-008: Approved-briefs as E-002 input contract
- PI-013: Tenant isolation (tenant_id non-null)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Create, update, getByBatch, getByStatus queries
- [ ] `brief_data` JSONB column stores full validated brief
- [ ] Denormalised fields for query filtering (score, status, date, type)
- [ ] File adapter: `data/calendar/{domain}/briefs/{brief_id}.json`
- [ ] Both adapters produce identical query results (parity test)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change storage structure
- Never: store invalid briefs, skip tenant_id

---

## Task T-009: GenerateCalendarCommand [Integration]
**Story:** All user stories
**Size:** L
**Depends on:** T-002, T-003, T-004, T-005, T-006, T-007, T-008
**Parallel:** No

### What
Implement the `GenerateCalendarCommand` that orchestrates the full F-007 pipeline: load gap matrix → build ContentBriefs → get LLM recommendations → schedule publish dates → schedule languages → render Markdown + JSON → persist. Emits `CalendarGenerated` event.

### Files
- Create: `modules/content-engine/research/commands/generate-calendar.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/generate-calendar.test.ts`
- Modify: `modules/content-engine/research/index.ts` (export command)

### Test Scenarios (from tests.md)
- ATS-001: Full happy path — gap matrix to calendar output
- ATS-006: Only thin content → update section only
- ATS-007: LLM failure → fallback headings, no halt
- INT-001: F-006 output as input
- INT-002: F-001 + F-003 keyword data integration
- INT-003: F-005 competitor benchmarks integration
- INT-007: 10-topic calendar < 2 minutes

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Full pipeline: load → build briefs → recommend → schedule → render → persist → event
- [ ] `GenerateCalendarOutput` with counts, file paths, tokens, batch_id
- [ ] `CalendarGenerated` event emitted
- [ ] LLM failure → graceful fallback (no pipeline halt)
- [ ] Feature flag `FEATURE_CONTENT_CALENDAR` checked at entry
- [ ] Structured JSON logging: brief count, tokens, duration
- [ ] All produced ContentBriefs pass Zod validation
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change event schema
- Never: skip Zod validation, auto-approve briefs, bypass feature flag
