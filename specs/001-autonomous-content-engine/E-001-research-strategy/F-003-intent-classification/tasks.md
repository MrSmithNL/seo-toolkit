# F-003: Search Intent Classification — Tasks

## Task T-001: Intent Enums & Contract Types [Foundation]
**Story:** US-001, US-002
**Size:** S
**Depends on:** F-001 T-001 (keyword schema must exist)
**Parallel:** Yes [P]

### What
Create the `IntentType`, `IntentConfidence`, and `ContentFormat` enum definitions and Zod schemas. Define the intent columns that F-001's keyword table needs (nullable, populated by F-003). Export contract types consumed by F-007.

### Files
- Create: `modules/content-engine/research/contracts/intent-type.ts`
- Create: `modules/content-engine/research/contracts/content-format.ts`
- Create (tests): `modules/content-engine/research/contracts/__tests__/intent-type.test.ts`
- Read (context): `modules/content-engine/research/schema/keyword.ts` (F-001 schema)

### Test Scenarios (from tests.md)
- PI-001: Valid intent type (always one of 4 values)
- PI-002: Valid confidence level (always one of 3 values)
- PI-004: Valid format enum (always one of 9 values)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `IntentType` enum: informational, commercial, transactional, navigational
- [ ] `IntentConfidence` enum: high, medium, low
- [ ] `ContentFormat` enum: 9 values per design.md
- [ ] Zod schemas for all three enums
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write types, enums, tests
- Ask: add new enum values (affects F-007 downstream)
- Never: define intent columns outside F-001's schema

---

## Task T-002: Classification Prompt & Response Parser [Domain Logic]
**Story:** US-001, US-002
**Size:** M
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Create the versioned classification prompt (`prompts/intent-classification-v1.txt`) and the structured output parser. The prompt instructs the LLM to classify intent AND recommend format in a single pass per ADR-F003-003. Parser validates completeness (every input keyword in output), enum values, confidence levels, and rationale presence. Handles keyword text escaping (control chars stripped, quoted).

### Files
- Create: `modules/content-engine/research/prompts/intent-classification-v1.txt`
- Create: `modules/content-engine/research/domain/intent-prompt-builder.ts`
- Create: `modules/content-engine/research/domain/intent-response-parser.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/intent-prompt-builder.test.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/intent-response-parser.test.ts`
- Create: `modules/content-engine/research/__fixtures__/intent-classification-response.json`

### Test Scenarios (from tests.md)
- PI-001: Valid intent type in output
- PI-002: Valid confidence level in output
- PI-003: Rationale non-empty
- PI-004: Valid format enum
- PI-007: All keywords classified or flagged
- PI-008: Order preservation

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Prompt stored in versioned file (not inline string)
- [ ] Prompt includes intent definitions, ambiguity rule, format signals, few-shot example
- [ ] Parser validates: completeness, valid enums, rationale, confidence
- [ ] Keywords escaped (control chars stripped, quoted in prompt)
- [ ] Invalid LLM response triggers retry signal
- [ ] Fixture covers 50-keyword Hairgenetix DE set
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, version prompts
- Ask: change ambiguity resolution rule, modify prompt structure
- Never: use inline prompt strings, skip response validation

---

## Task T-003: Format Signal Detector [Domain Logic]
**Story:** US-002 (Content Format Recommendation)
**Size:** S
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Implement the format signal detection logic from the design's signal detection table. Detects patterns in keyword text ("how to", "best", "vs", "what is", "near me", brand names) and maps them to recommended content formats. While the LLM also does this, the detector provides a deterministic baseline for validation and fallback.

### Files
- Create: `modules/content-engine/research/domain/format-signal-detector.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/format-signal-detector.test.ts`

### Test Scenarios (from tests.md)
- ATS-009: "how to" signal → how-to-guide
- ATS-010: "vs" signal → comparison-article
- ATS-011: "best" signal → listicle
- ATS-012: "what is" signal → definition-explainer
- ATS-013: Location + transactional → location-page
- ATS-014: Generic commercial, no signal → category-page
- ATS-015: Format is structured enum, not free text

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] All 8 signal patterns from design table detected
- [ ] Returns `{ format: ContentFormat; signal: string | null }`
- [ ] Default format logic: informational → definition-explainer, transactional → product-landing-page
- [ ] Works for non-English keywords (pattern matching is case-insensitive)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new signal patterns or format types
- Never: use LLM for signal detection (rule-based only)

---

## Task T-004: Chunked Classification Pipeline [Integration]
**Story:** US-001, US-003 (Batch Processing)
**Size:** L
**Depends on:** T-001, T-002, T-003
**Parallel:** No

### What
Implement the `ClassifyKeywordIntent` command handler per ADR-F003-001. Loads unclassified keywords for campaign+locale, chunks into batches of 50, processes sequentially via LLM, validates responses, writes intent fields to keyword table. Handles partial failure (one chunk fails, others succeed — failed keywords marked `intent_unclassified`). Supports `reclassify` flag and custom `chunkSize`.

### Files
- Create: `modules/content-engine/research/commands/classify-keyword-intent.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/classify-keyword-intent.test.ts`
- Modify: `modules/content-engine/research/index.ts` (export command)
- Read (context): `design.md` (API contracts, event schema)

### Test Scenarios (from tests.md)
- ATS-006: 120 keywords → 3 LLM calls (50, 50, 20)
- ATS-007: LLM failure → retry once → mark unclassified, continue
- ATS-008: Non-English keyword classified using English taxonomy
- ATS-016: All 150 records updated with intent fields
- ATS-017: Volume refresh does NOT reclassify
- ATS-018: --reclassify flag forces re-classification
- INT-001: F-001 output as input
- INT-005: 150 keywords within 90 seconds, < 30K tokens
- PI-011: Token budget compliance

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Chunking: 50 keywords per LLM call
- [ ] Sequential chunk processing (not parallel)
- [ ] `ClassifyKeywordIntentResult` returned with distribution stats
- [ ] `IntentClassificationCompletedEvent` emitted on success
- [ ] Partial failure: failed chunks → `intent_unclassified`, pipeline continues
- [ ] `reclassify=false` skips already-classified keywords
- [ ] Feature flag `FEATURE_INTENT_CLASSIFICATION` checked at entry
- [ ] Structured JSON logging: distribution, tokens, duration
- [ ] Tests pass (mock AI gateway)
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change event schema
- Never: skip tests, bypass feature flag, use inline prompts

---

## Task T-005: Intent Distribution Query [Integration]
**Story:** US-003
**Size:** S
**Depends on:** T-004
**Parallel:** Yes [P]

### What
Implement the `GetIntentDistribution` query handler that returns aggregate statistics: total, classified, unclassified counts, and breakdowns by intent, format, and confidence. Used by F-007 for calendar planning and by dashboards.

### Files
- Create: `modules/content-engine/research/queries/get-intent-distribution.ts`
- Create (tests): `modules/content-engine/research/queries/__tests__/get-intent-distribution.test.ts`

### Test Scenarios (from tests.md)
- ATS-019: Filter by intent type returns correct count
- ATS-020: Filter by minimum confidence
- INT-002: F-003 output consumable by F-007

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Returns `IntentDistributionResult` with all breakdown fields
- [ ] Filters by campaign, locale, intent type, confidence level
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new query filters
- Never: return data from other tenants (RLS enforced)

---

## Task T-006: Config & Module Bootstrap [Foundation]
**Story:** NFR
**Size:** S
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Create F-003 module configuration: feature flag, LLM model selection, chunk size, retry count. Wire the module factory that injects mock LLM adapter in test mode.

### Files
- Create: `modules/content-engine/research/config/intent-config.ts`
- Create (tests): `modules/content-engine/research/config/__tests__/intent-config.test.ts`

### Test Scenarios (from tests.md)
- PI-010: English taxonomy for all languages (config validates)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Feature flag `FEATURE_INTENT_CLASSIFICATION` defaults to false
- [ ] Chunk size configurable (default 50)
- [ ] Mock LLM adapter injected when `NODE_ENV=test`
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new config parameters
- Never: store secrets in code
