---
id: "FTR-SEO-003"
title: "Test Plan: Search Intent Classification"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 36
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-003: Search Intent Classification — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: Four-Type Intent Classification

**ATS-001: Clear informational keyword**

```
GIVEN a keyword "hair transplant recovery timeline"
WHEN intent classification runs
THEN intent is "informational"
AND confidence is "high"
AND rationale mentions "no purchase signal" or similar
```

**ATS-002: Clear commercial keyword**

```
GIVEN a keyword "best hair transplant clinic Germany"
WHEN intent classification runs
THEN intent is "commercial"
AND confidence is "high"
AND rationale mentions "comparing providers" or similar
```

**ATS-003: Clear transactional keyword**

```
GIVEN a keyword "book hair transplant consultation"
WHEN intent classification runs
THEN intent is "transactional"
AND confidence is "high"
AND rationale mentions "explicit action intent" or "book" as a transactional signal
```

**ATS-004: Clear navigational keyword**

```
GIVEN a keyword "hairgenetix"
WHEN intent classification runs
THEN intent is "navigational"
AND confidence is "high"
AND rationale mentions "specific brand"
```

**ATS-005: Ambiguous keyword — higher intent assigned**

```
GIVEN a keyword "hair transplant" (head term, ambiguous)
WHEN intent classification runs
THEN intent is "commercial" (higher-intent type wins)
AND confidence is "medium"
AND rationale includes both candidate intents (informational and commercial)
```

**ATS-006: Batch processing — 50 keywords per chunk**

```
GIVEN 120 keywords to classify
WHEN classification runs
THEN 3 LLM calls are made (chunks of 50, 50, 20)
AND all 120 keywords receive classifications
AND original keyword order is preserved
```

**ATS-007: LLM failure with graceful degradation**

```
GIVEN the LLM call fails for a batch of 50 keywords
WHEN the system retries once and it still fails
THEN those 50 keywords are marked "intent_unclassified"
AND the remaining batches are still processed
AND no pipeline halt occurs
```

**ATS-008: Non-English keyword classification**

```
GIVEN a German keyword "Haartransplantation Kosten Deutschland"
WHEN intent classification runs
THEN intent is classified using the English taxonomy ("commercial")
AND confidence and rationale are in English
```

### US-002: Content Format Recommendation

**ATS-009: "how to" signal detected**

```
GIVEN a keyword "how to care for hair after transplant" with intent=informational
WHEN format recommendation runs
THEN recommended_format is "how-to guide"
AND format_signal is "how to"
```

**ATS-010: "vs" signal detected**

```
GIVEN a keyword "FUE vs DHI hair transplant" with intent=commercial
WHEN format recommendation runs
THEN recommended_format is "comparison article"
AND format_signal is "vs"
```

**ATS-011: "best" signal detected**

```
GIVEN a keyword "best hair transplant clinics" with intent=commercial
WHEN format recommendation runs
THEN recommended_format is "listicle (top N list)"
AND format_signal is "best"
```

**ATS-012: "what is" signal detected**

```
GIVEN a keyword "what is alopecia areata" with intent=informational
WHEN format recommendation runs
THEN recommended_format is "definition / explainer"
AND format_signal is "what is"
```

**ATS-013: Location + transactional signal**

```
GIVEN a keyword "hair transplant consultation Berlin" with intent=transactional
WHEN format recommendation runs
THEN recommended_format is "location page"
AND format_signal includes location indicator
```

**ATS-014: Generic commercial keyword — no signal**

```
GIVEN a keyword "hair growth serum" with intent=commercial and no specific signal
WHEN format recommendation runs
THEN recommended_format is "category page"
AND format_signal is null
```

**ATS-015: Format is structured enum, not free text**

```
GIVEN any classified keyword
WHEN format recommendation runs
THEN recommended_format is one of the approved enum values
AND F-007 can group articles by format_type
```

### US-003: Batch Classification Output and Persistence

**ATS-016: First classification run — all fields populated**

```
GIVEN 150 keywords for hairgenetix.com
WHEN intent classification completes
THEN all 150 records are updated with: intent, intent_confidence, intent_rationale, recommended_format, format_signal, classified_at
```

**ATS-017: Volume refresh does NOT reclassify**

```
GIVEN 150 previously classified keywords
WHEN F-001 refreshes volume data (some keywords change > 30%)
THEN intent fields remain unchanged
AND only volume/trend fields are updated
```

**ATS-018: Manual reclassify flag**

```
GIVEN previously classified keywords
WHEN the --reclassify flag is passed
THEN all intent fields are recalculated from current keyword text
AND classified_at timestamps are updated
```

**ATS-019: Filter by intent type**

```
GIVEN 150 classified keywords (12 transactional, 80 informational, 50 commercial, 8 navigational)
WHEN getKeywordsByDomain("hairgenetix.com", { intent: "transactional" }) is called
THEN exactly 12 keywords are returned
```

**ATS-020: Filter by minimum confidence**

```
GIVEN 150 classified keywords with mixed confidence levels
WHEN getKeywordsByDomain("hairgenetix.com", { minConfidence: "high" }) is called
THEN only keywords with confidence = "high" are returned
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: F-001 output → F-003 input pipeline**

```
GIVEN F-001 has completed keyword research
WHEN F-003 receives the keyword records
THEN all keyword records have the required text field for classification
AND classification runs successfully
```

**INT-002: F-003 output → F-007 input pipeline**

```
GIVEN F-003 has classified all keywords
WHEN F-007 (Content Calendar) consumes keyword data
THEN intent and recommended_format fields are present
AND F-007 can filter/sort by intent type and format
```

**INT-003: Claude API batch classification round-trip**

```
GIVEN valid Claude API credentials and 50 keywords
WHEN a classification batch is submitted
THEN the LLM response is parseable with valid intent types
AND all 50 keywords receive classifications
AND total tokens consumed < 10,000 for the batch
```

**INT-004: KeywordRecord schema extension**

```
GIVEN the original KeywordRecord schema from F-001
WHEN F-003 intent fields are added
THEN the schema extension is additive (no breaking changes)
AND existing F-001 fields remain valid
AND Zod validation passes for records with intent fields
```

**INT-005: Classification performance within 90 seconds**

```
GIVEN 150 keywords to classify in 3 batches
WHEN classification runs end-to-end
THEN total time is < 90 seconds
AND total tokens consumed < 30,000
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | Valid intent type | `intent` is always one of: "informational", "commercial", "transactional", "navigational" |
| PI-002 | Valid confidence level | `intent_confidence` is always one of: "high", "medium", "low" |
| PI-003 | Rationale non-empty | `intent_rationale` is always a non-empty string |
| PI-004 | Valid format enum | `recommended_format` is always one of the approved format values |
| PI-005 | Classified_at present | Every classified keyword has a non-null `classified_at` ISO 8601 timestamp |
| PI-006 | Ambiguous keywords have medium confidence | If a keyword could be classified as two intent types, confidence is never "high" |
| PI-007 | All keywords classified or flagged | After classification, every keyword has either a valid intent OR is flagged "intent_unclassified" |
| PI-008 | Order preservation | Output keyword order matches input keyword order |
| PI-009 | No intent duplication | Each keyword has exactly one intent classification (not multiple) |
| PI-010 | English taxonomy for all languages | Non-English keywords receive intent values in the English enum (not translated) |
| PI-011 | Token budget | Total tokens for 150 keywords <= 30,000 |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 to ATS-008 | Integration | Requires LLM call for intent classification |
| ATS-009 to ATS-015 | Unit | Format recommendation from intent + keyword signals is rule-based logic |
| ATS-016 to ATS-020 | Integration | Requires storage layer for persistence and querying |
| INT-001 to INT-005 | Integration | Cross-feature data flow and API boundaries |
| PI-001 to PI-011 | Property | Fast-check on intent classification schema constraints |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
