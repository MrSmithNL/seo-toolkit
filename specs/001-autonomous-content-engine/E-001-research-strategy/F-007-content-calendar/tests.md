---
id: "FTR-SEO-007"
title: "Test Plan: Content Calendar / Planning"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 42
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-007: Content Calendar / Planning — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: AI-Generated Calendar from Gap Analysis

**ATS-001: Happy path — calendar from gap matrix**

```
GIVEN F-006 gap matrix with 15 own_gap rows and 3 thin_content rows
WHEN calendar generation runs
THEN 15 ContentBrief records are created for new content
AND they are sorted by opportunity_score descending
AND 3 thin_content entries appear in a separate "content to update" section
AND every ContentBrief has all required schema fields populated
```

**ATS-002: Content type inference from intent**

```
GIVEN keyword "FUE vs DHI comparison" with intent=commercial
WHEN calendar generation runs
THEN content_type="comparison"
AND recommended_headings includes entries like "What is FUE?", "What is DHI?", "Key differences", "Cost comparison"
AND a one-sentence rationale explains the recommendation
```

**ATS-003: Schema type recommendation from competitors**

```
GIVEN top competitors for a keyword all use Article + FAQPage schema
WHEN calendar generation runs
THEN recommended_schema_types=["Article", "FAQPage"]
AND include_faq=true
```

**ATS-004: No F-002 cluster data — LLM fallback**

```
GIVEN F-002 (Topic Clustering) has not been run
WHEN calendar generation runs
THEN topic_cluster is assigned via LLM inference (e.g. "Hair Transplant Techniques (inferred)")
AND tagged as "inferred" to distinguish from F-002 algorithm output
```

**ATS-005: Publish date assignment — 2/week cadence**

```
GIVEN 15 topics with pipeline run on 2026-03-15 (Sunday)
AND default cadence of 2 articles per week
WHEN publish dates are assigned
THEN first topic gets 2026-03-16 (Monday)
AND last topic gets approximately 2026-04-27 (7.5 weeks out)
AND topics are assigned in priority order (highest score = earliest date)
```

**ATS-006: Only thin content gaps**

```
GIVEN F-006 produces 0 own_gap rows and 8 thin_content rows
WHEN calendar generation runs
THEN 0 new content entries are created
AND the "update existing" section has 8 entries
```

**ATS-007: LLM failure — fallback to competitor headings**

```
GIVEN the LLM call for heading generation fails
WHEN the system retries and the retry also fails
THEN recommended_headings falls back to competitor heading data from F-005
AND headings are marked "extracted from competitor — LLM unavailable"
AND no pipeline halt occurs
```

### US-002: Priority Scoring Algorithm

**ATS-008: High-priority new topic rationale**

```
GIVEN volume=8100, difficulty=32, gap_score=1.0 (no competitor in top 5)
WHEN the ContentBrief is generated
THEN opportunity_score_rationale = "Score: 0.74 — High volume (8,100/mo), easy to rank (32/100), no competitor in top 5."
```

**ATS-009: Medium-priority topic rationale**

```
GIVEN volume=2400, difficulty=48, competitor at #7
WHEN the ContentBrief is generated
THEN rationale includes "Medium volume (2,400/mo)", "moderate competition (48/100)", "competitor at position 7"
```

**ATS-010: Thin content upgrade rationale**

```
GIVEN thin content: ranks #18, 420-word page, competitor avg 2800 words
WHEN the ContentBrief is generated
THEN rationale: "Priority: 0.82 — We rank #18. Our page is 420 words vs competitor average of 2,800. Strong update opportunity."
```

**ATS-011: Zero-volume AISO topic rationale**

```
GIVEN volume=0 with "zero volume" flag
WHEN the ContentBrief is generated
THEN rationale includes "Zero search volume" and "AISO value only"
```

**ATS-012: Rationale readable in < 5 minutes for 10 topics**

```
GIVEN 10 ContentBrief records with rationales
WHEN displayed in Markdown calendar format
THEN each rationale is a single line
AND 10 rationales can be read and understood in < 5 minutes
```

### US-003: Human Review and Approval Workflow

**ATS-013: Dual file output**

```
GIVEN calendar generation completes
WHEN output is written
THEN two files are created:
  - calendar-YYYY-MM-DD.md (Markdown for review)
  - calendar-YYYY-MM-DD.json (JSON array of ContentBrief records)
```

**ATS-014: Markdown format — correct structure**

```
GIVEN a generated calendar with 5 topics
WHEN the Markdown file is opened
THEN each entry includes: numbered title, keyword, volume, difficulty, rationale, competitor benchmarks, recommendation (word count, type, date), headings (bullet list), and action checkboxes (Approve/Reject/Edit)
```

**ATS-015: Full approval — JSON edit**

```
GIVEN Malcolm edits the JSON file and sets all 10 entries to status="approved"
WHEN approval is processed
THEN approved-briefs-YYYY-MM-DD.json is created with 10 records
AND each has reviewed_by set, reviewed_at timestamped
AND all records validate against ContentBrief schema
```

**ATS-016: Partial approval**

```
GIVEN Malcolm approves 7 topics and rejects 3
WHEN approval is processed
THEN approved-briefs file has 7 records
AND rejected briefs remain in calendar JSON with status="rejected"
AND rejected briefs are NOT in the approved-briefs output
```

**ATS-017: Edit during review — word count override**

```
GIVEN Malcolm changes overridden_word_count from null to 2400
WHEN the ContentBrief is updated
THEN overridden_word_count=2400 is preserved
AND recommended_word_count remains at the original value (e.g. 1800)
AND both values coexist in the record
```

**ATS-018: Invalid JSON edit caught by validation**

```
GIVEN Malcolm accidentally removes the target_keyword field from a JSON entry
WHEN approval is processed
THEN schema validation catches the error
AND outputs: "Invalid ContentBrief at index 3: required field 'target_keyword' is missing."
AND no approved-briefs file is written until fixed
```

**ATS-019: CLI approval command**

```
GIVEN a ContentBrief with id="abc123" in the calendar JSON
WHEN `seo-toolkit calendar approve --id abc123` is run
THEN the brief status changes to "approved"
AND reviewed_at is set to the current timestamp
```

### US-004: ContentBrief Schema Validation

**ATS-020: Valid brief passes validation**

```
GIVEN a ContentBrief with all required fields present and correct types
WHEN Zod schema validation runs
THEN validation passes
AND the brief is written to the output file
```

**ATS-021: Missing required field rejected**

```
GIVEN a ContentBrief without target_keyword
WHEN validation runs
THEN validation fails with: "Invalid ContentBrief: target_keyword is required."
AND the record is not written
```

**ATS-022: Schema version mismatch rejected**

```
GIVEN a ContentBrief with schema_version="0.9.0" and current version is "1.0.0"
WHEN validation runs
THEN error: "ContentBrief schema mismatch: brief version 0.9.0 is incompatible with current version 1.0.0. Regenerate this brief."
```

**ATS-023: Invalid enum value rejected**

```
GIVEN a ContentBrief with content_type="infographic" (not in the approved enum)
WHEN validation runs
THEN error: "Invalid ContentBrief: content_type must be one of: blog_post, comparison, how_to, faq, product_page, landing_page."
```

**ATS-024: Approved-briefs file validated before writing**

```
GIVEN 10 approved ContentBrief records
WHEN the approved-briefs file is about to be written
THEN every record is validated against the Zod schema
AND schema_version is included at the file root level
AND the file is only written if all records pass validation
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: F-006 output → F-007 input pipeline**

```
GIVEN F-006 gap matrix with classifications, scores, and rationales
WHEN F-007 receives the output
THEN all gap rows are available for calendar generation
AND ContentGap schema validates
```

**INT-002: F-001 + F-003 keyword data integration**

```
GIVEN F-001 keyword data (volume, difficulty) and F-003 intent classifications
WHEN F-007 generates ContentBrief records
THEN keyword_volume, keyword_difficulty, search_intent, and recommended_format fields are populated from upstream
```

**INT-003: F-005 competitor benchmarks integration**

```
GIVEN F-005 competitor snapshots (word counts, depth scores, headings, schema types)
WHEN F-007 generates ContentBrief records
THEN competitor_avg_word_count, competitor_depth_scores, top_competitor_url, competitor_schema_types, and competitors_have_faq are populated
AND recommended_word_count = competitor_avg_word_count * 1.1 (rounded to nearest 100)
```

**INT-004: Claude API heading generation round-trip**

```
GIVEN valid Claude API credentials and competitor heading data
WHEN heading recommendation LLM call runs
THEN recommended_headings is an array of 4-8 H2 suggestions
AND tokens consumed < 1K for a single brief
```

**INT-005: Standalone file output**

```
GIVEN standalone mode (no database)
WHEN calendar generation completes
THEN calendar-YYYY-MM-DD.md and calendar-YYYY-MM-DD.json are output to data/calendar/{domain}/
```

**INT-006: Multi-language calendar generation**

```
GIVEN gap data for DE and EN
WHEN calendar generation runs for both languages
THEN separate calendars are produced per language
AND a cross-language summary is generated
```

**INT-007: Performance — 10-topic calendar < 2 minutes**

```
GIVEN 10 gap rows with all upstream data available
WHEN calendar generation runs (including LLM calls)
THEN the operation completes within 2 minutes
```

**INT-008: Approved-briefs as E-002 input contract**

```
GIVEN approved-briefs-YYYY-MM-DD.json with 7 approved records
WHEN E-002 (Content Creation Engine) reads the file
THEN all 7 records validate against ContentBrief Zod schema
AND all required fields for content creation are present
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | ContentBrief ID unique | Every ContentBrief has a unique UUID id |
| PI-002 | All required fields present | Every ContentBrief has all non-nullable fields populated |
| PI-003 | Schema version pinned | schema_version is always "1.0.0" for R1 |
| PI-004 | Valid status values | status is one of: "pending_review", "approved", "rejected", "in_progress", "published" |
| PI-005 | Valid content_type | content_type is one of the approved enum values |
| PI-006 | Valid search_intent | search_intent is one of: "informational", "transactional", "navigational", "commercial" |
| PI-007 | Opportunity score range | opportunity_score is 0.0-1.1 inclusive |
| PI-008 | Word count positive | recommended_word_count is > 0 |
| PI-009 | Publish dates sorted | suggested_publish_dates are in chronological order matching priority rank |
| PI-010 | Rejected briefs excluded | approved-briefs output never contains records with status="rejected" |
| PI-011 | Rationale non-empty | opportunity_score_rationale is always a non-empty string |
| PI-012 | Existing page URL for thin content | If gap_type is "thin_content", existing_page_url is non-null |
| PI-013 | Tenant isolation | Every ContentBrief has a non-null tenant_id |
| PI-014 | Audit fields on approval | Approved/rejected records always have non-null reviewed_by and reviewed_at |
| PI-015 | Calendar sorted by score | Calendar entries are sorted by opportunity_score descending |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 to ATS-007 | Integration | Requires upstream pipeline data and LLM calls |
| ATS-008 to ATS-012 | Unit | Scoring rationale generation is template-based string formatting |
| ATS-013 to ATS-019 | Integration | Requires file I/O, schema validation, and CLI command |
| ATS-020 to ATS-024 | Unit | Zod schema validation is pure computation |
| INT-001 to INT-008 | Integration | Cross-feature data flow and API boundaries |
| PI-001 to PI-015 | Property | Fast-check on ContentBrief schema and calendar ordering constraints |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
