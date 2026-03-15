# F-003: Search Intent Classification — Design

> Feature-level architecture for LLM-based keyword intent classification and content format recommendation.
> Cross-cutting decisions (pipeline orchestration, tenant isolation) are in `epic-design.md`.

---

## Architecture ADRs

### ADR-F003-001: Batch Classification with Chunked LLM Calls

**Status:** Proposed
**Context:** Need to classify 50-200 keywords by intent and recommend content formats. Requirements specify batch processing in chunks of 50, completing within 90 seconds for 150 keywords.
**Decision:** Process keywords in chunks of 50. Each chunk is one LLM call with structured JSON output. Chunks are processed sequentially (not parallel) to respect rate limits and simplify error handling. Each chunk call includes the full format list and classification rubric in the system prompt. A failed chunk is retried once; on persistent failure, keywords in that chunk are marked `intent_unclassified`.
**Alternatives considered:**
1. Single call for all 150 keywords — Risks output truncation with large responses. 50 is a safe batch size for reliable structured output.
2. Parallel chunk processing — Adds complexity, risks rate limiting. Sequential is fast enough (3 calls x ~10s each = ~30s, well under 90s budget).
3. Per-keyword classification — 150 individual LLM calls = slow, expensive, wasteful.
**Consequences:** 3 sequential LLM calls for 150 keywords. ~30K tokens total. Partial failure is possible (one chunk fails, others succeed) — this is handled gracefully.

### ADR-F003-002: Intent Fields Extend F-001 Keyword Table (No Separate Table)

**Status:** Proposed
**Context:** Intent classification produces 6 fields per keyword. Need to decide whether to add columns to the `keyword` table or create a separate `keyword_intent` table.
**Decision:** Add intent fields directly to the `keyword` table (defined in F-001 schema). Fields: `intent`, `intent_confidence`, `intent_rationale`, `recommended_format`, `format_signal`, `classified_at`. These are nullable columns populated by F-003 after F-001 creates the keyword records.
**Alternatives considered:**
1. Separate `keyword_intent` table — Adds a JOIN for every downstream query that needs intent. Intent is a 1:1 attribute of a keyword, not a separate entity.
2. JSON column on keyword — Loses queryability. Downstream features need to filter by intent type.
**Consequences:** F-003 writes to F-001's table. Requires coordination: F-001 defines the columns, F-003 populates them. Schema change is additive (nullable columns), so no migration conflict.

### ADR-F003-003: Format Recommendation as Derived Attribute

**Status:** Proposed
**Context:** US-002 requires recommending a content format for each keyword. This could be a separate step or part of the intent classification call.
**Decision:** Include format recommendation in the same LLM call as intent classification. The prompt instructs the LLM to classify intent AND recommend format in a single pass. The format list is a fixed enum (9 values) included in the prompt. Format signals ("how to", "best", "vs", "what is", "near me") are detected by the LLM and reported in the response.
**Alternatives considered:**
1. Rule-based format mapping (intent -> format lookup table) — Misses keyword-specific signals. "best hair transplant clinics" should be a listicle, not a generic commercial page. LLM catches these nuances.
2. Separate format recommendation step — Doubles LLM calls. Intent and format are tightly coupled; the LLM considers both in the same reasoning.
**Consequences:** Single LLM call per chunk handles both intent and format. Slightly larger output schema, but well within token budget.

---

## Data Model

### Schema (extends F-001 keyword table)

F-003 does not create new tables. It populates the following columns on the `keyword` table (defined in F-001's schema):

```typescript
// These columns are DEFINED in F-001 keyword schema but POPULATED by F-003:
//
// intent: text('intent')                    — 'informational' | 'commercial' | 'transactional' | 'navigational'
// intentConfidence: text('intent_confidence') — 'high' | 'medium' | 'low'
// intentRationale: text('intent_rationale')  — 1 sentence
// recommendedFormat: text('recommended_format') — enum value from ContentFormat
// formatSignal: text('format_signal')        — detected signal or null
// classifiedAt: timestamp('classified_at')   — when classification ran
```

### Content Format Enum

```typescript
// contracts/content-format.ts
export const contentFormats = [
  'how-to-guide',
  'definition-explainer',
  'comparison-article',
  'listicle',
  'faq-page',
  'product-landing-page',
  'category-page',
  'location-page',
  'brand-navigational-page',
] as const;

export type ContentFormat = typeof contentFormats[number];

// Zod schema for validation
export const contentFormatSchema = z.enum(contentFormats);
```

### Intent Type Enum

```typescript
// contracts/intent-type.ts
export const intentTypes = [
  'informational',
  'commercial',
  'transactional',
  'navigational',
] as const;

export type IntentType = typeof intentTypes[number];

export const intentConfidenceLevels = ['high', 'medium', 'low'] as const;
export type IntentConfidence = typeof intentConfidenceLevels[number];
```

---

## API Contracts

### Commands (Writes)

```typescript
// ClassifyKeywordIntent — main entry point
interface ClassifyKeywordIntentCommand {
  tenantId: string;
  campaignId: string;
  locale: string;                       // classify keywords for this locale
  options?: {
    reclassify?: boolean;               // re-run even if already classified
    chunkSize?: number;                 // default 50
  };
}

interface ClassifyKeywordIntentResult {
  keywordsClassified: number;
  intentDistribution: Record<IntentType, number>;  // { informational: 45, commercial: 30, ... }
  confidenceDistribution: Record<IntentConfidence, number>;
  formatDistribution: Record<ContentFormat, number>;
  skipped: number;                      // already classified and reclassify=false
  failed: number;                       // LLM failures, marked as unclassified
  llmTokensUsed: number;
  duration: number;                     // milliseconds
}
```

### Queries (Reads)

```typescript
// Intent queries are handled by F-001's GetKeywordsByDomain query
// with intent filter support. No separate query interface needed.

// Convenience query for intent distribution statistics
interface GetIntentDistributionQuery {
  tenantId: string;
  campaignId: string;
  locale?: string;
}

interface IntentDistributionResult {
  total: number;
  classified: number;
  unclassified: number;
  byIntent: Record<IntentType, number>;
  byFormat: Record<ContentFormat, number>;
  byConfidence: Record<IntentConfidence, number>;
}
```

### Events (Async Out)

```typescript
interface IntentClassificationCompletedEvent {
  type: 'research.intent.completed';
  tenantId: string;
  campaignId: string;
  locale: string;
  keywordsClassified: number;
  intentDistribution: Record<IntentType, number>;
}
```

---

## LLM Prompt Architecture

### Prompt File

Stored at `prompts/intent-classification-v1.txt`. Contains:

1. **System instruction:** "You are a search intent classifier. For each keyword, determine the user's search intent and recommend the best content format."
2. **Intent definitions:** Precise definition of each intent type with 2 examples each.
3. **Ambiguity rule:** "When a keyword is ambiguous between informational and commercial, classify as commercial (higher intent). Set confidence to medium. Note both candidates in rationale."
4. **Format mapping guidance:** Intent-to-format heuristics + signal detection rules.
5. **Output JSON schema:** Enforced via structured output.
6. **Few-shot example:** 5 keywords classified with intent, confidence, rationale, format, and signal.

### Structured Output Schema

```typescript
interface IntentClassificationLLMResponse {
  classifications: {
    keyword: string;                    // echo back the input keyword
    intent: 'informational' | 'commercial' | 'transactional' | 'navigational';
    confidence: 'high' | 'medium' | 'low';
    rationale: string;                  // 1 sentence
    recommended_format: string;         // from ContentFormat enum
    format_signal: string | null;       // detected signal (e.g., "how to", "best", "vs")
  }[];
}
```

### Format Signal Detection

The LLM detects these signals in keyword text:

| Signal Pattern | Suggested Format | Example |
|---------------|-----------------|---------|
| "how to", "how do I" | how-to-guide | "how to care for hair after transplant" |
| "what is", "what are" | definition-explainer | "what is alopecia areata" |
| "best", "top" | listicle | "best hair transplant clinics Germany" |
| "vs", "versus", "compared to" | comparison-article | "FUE vs DHI hair transplant" |
| "near me", city/country name + transactional | location-page | "hair transplant Berlin" |
| Brand name | brand-navigational-page | "hairgenetix reviews" |
| Product category + commercial | category-page | "hair growth serums" |
| No signal + informational | definition-explainer (default) | "alopecia causes" |
| No signal + transactional | product-landing-page (default) | "book consultation" |

### Token Budget

- Input per chunk: 50 keywords x avg 5 tokens = 250 + prompt (~1500 tokens) = ~1750
- Output per chunk: 50 classifications x ~40 tokens = ~2000
- Per chunk total: ~3750 tokens
- 3 chunks for 150 keywords: ~11,250 tokens (well under 30K budget)

---

## Processing Flow

```
F-001 keywords (classified_at = null)
        │
        ▼
  Filter: unclassified keywords for campaign+locale
        │
        ▼
  Chunk into batches of 50
        │
        ▼
  For each chunk:
    ├── Build prompt (system + keyword list)
    ├── Call LLM with structured output
    ├── Validate response (all keywords present, valid enums)
    ├── On validation failure: retry once
    ├── On persistent failure: mark chunk as "intent_unclassified"
    └── Write intent fields to keyword table
        │
        ▼
  Emit IntentClassificationCompletedEvent
        │
        ▼
  Log: distribution stats, tokens used, duration
```

### Validation Rules (post-LLM)

1. **Completeness check:** Every input keyword must appear in the response. Missing keywords trigger a retry.
2. **Enum validation:** Intent type and format must be valid enum values. Invalid values trigger a retry.
3. **Confidence validation:** Must be one of high/medium/low.
4. **Order preservation:** Response keywords are matched to input by keyword text (exact match after normalisation), not by position (LLM may reorder).

---

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **Prompt injection via keyword text** | M | Same mitigation as F-002: keywords wrapped in quotes in prompt, control characters stripped. Structured output constrains response shape. Intent classification is low-stakes — worst case is a wrong label, caught by confidence scoring. |
| **Classification bias from LLM training data** | L | The "commercial > informational" ambiguity rule is explicit in the prompt, overriding any LLM default bias. Confidence scoring surfaces uncertain classifications for human review. Validated against 50-keyword manual audit (NFR: 90% agreement). |

---

## ATAM-Lite

| Decision | Quality Attribute | Trade-off |
|----------|------------------|-----------|
| Batch LLM calls (ADR-F003-001) | Latency vs Reliability | Sequential chunks are slower than parallel but simpler error handling. 30s total for 150 keywords is well within 90s budget. |
| Fields on keyword table (ADR-F003-002) | Query performance vs Modularity | Co-locating intent with keyword data means F-003 writes to F-001's table. Tight coupling, but avoids JOIN overhead on every downstream query. Acceptable — intent is an intrinsic keyword attribute. |
| Format in same LLM call (ADR-F003-003) | Cost vs Separation of Concerns | Single call handles both intent and format. If format quality is poor, cannot retry format independently. Mitigated by the `--reclassify` flag which re-runs the entire classification. |

---

## Build Boundaries

| Tier | Actions |
|------|---------|
| **Always** | Write classification logic, implement prompt, write tests, populate intent fields on keyword table |
| **Ask** | Add new content format to the enum (affects F-007 downstream), change ambiguity resolution rule, modify keyword table columns (F-001 owns the schema) |
| **Never** | Auto-reclassify on volume change (requirements explicitly forbid this), use inline prompts, skip validation of LLM response, remove confidence scoring |

---

## Test Architecture

### Test Pyramid

| Level | Count | What | Framework |
|-------|:-----:|------|-----------|
| Unit | ~15 | Prompt construction, response parsing, validation logic, enum checks, signal detection, chunk splitting | Vitest |
| Integration | ~6 | Full classification pipeline with mock LLM, database persistence, reclassify flow, partial failure handling | Vitest + testcontainers |
| Property | ~3 | All keywords classified or marked unclassified, valid enum values only, confidence always present | fast-check |
| E2E | 1 | Full F-001 -> F-003 pipeline with fixtures, verify keyword records have intent fields populated | Vitest |

### Mocking Strategy

- **LLM (classification)**: Mock AI gateway. Fixture in `__fixtures__/intent-classification-response.json` — realistic response for 50 Hairgenetix DE keywords with expected intent distribution (~40% informational, ~30% commercial, ~20% transactional, ~10% navigational).
- **Database**: Testcontainers for integration tests. Seed with F-001 keyword fixtures (same golden dataset as F-002).
- **No external API mocks needed** — F-003 only calls the LLM.

### Property Invariants

```
P1: for input keywords K and classified output C:
    |C| === |K|                                     // no keyword lost or invented
P2: for all c in C: c.intent in intentTypes         // valid enum
P3: for all c in C: c.confidence in confidenceLevels // valid enum
P4: for all c in C: c.format in contentFormats       // valid enum
P5: for all c in C where c.confidence === 'medium':
    c.rationale contains alternative intent reference // ambiguity documented
P6: classify(classify(K)) produces same intent       // idempotent (intent is stable)
```

### Accuracy Validation Test

A special test (not automated in CI, run manually during R1 pilot):
- 50-keyword Hairgenetix DE fixture with human-annotated expected intents
- Run classification against real LLM (not mock)
- Assert >= 90% agreement rate (45/50 correct)
- Log disagreements for prompt tuning

### Golden Test

50-keyword Hairgenetix DE fixture with deterministic mock LLM response. Verifies:
- All 50 keywords get intent + format populated
- Distribution is plausible (not all one intent)
- Confidence is present on every classification
- Format signals are detected where expected (e.g., "how to" -> how-to-guide)
- `classified_at` timestamp is set
- Re-running with `reclassify=false` skips already-classified keywords
