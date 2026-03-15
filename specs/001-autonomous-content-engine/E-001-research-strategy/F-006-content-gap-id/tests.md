---
id: "FTR-SEO-006"
title: "Test Plan: Content Gap Identification"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 39
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-006: Content Gap Identification — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: Gap Matrix Generation

**ATS-001: Happy path — GSC available, gap found**

```
GIVEN hairgenetix.com vs hairtransplantclinic.de
AND GSC data is available for hairgenetix.com
AND keyword "FUE vs DHI" has 0 GSC impressions for hairgenetix.com
AND competitor ranks #3 with a 3200-word page scoring depth 4/5
WHEN gap matrix generation runs
THEN a row is produced: keyword="FUE vs DHI", hairgenetix={position: null, GSC_impressions: 0}, competitor={position: 3, url, word_count: 3200, depth_score: 4}
AND classification is "own_gap"
```

**ATS-002: Thin content identified**

```
GIVEN keyword "hair transplant recovery week 3"
AND hairgenetix.com ranks #22 with a 450-word page
AND top-3 competitor average is 2800 words
WHEN gap matrix generation runs
THEN classification is "own_coverage"
AND thin_content=true
AND our_word_count=450, competitor_avg=2800
```

**ATS-003: Low-competition new opportunity**

```
GIVEN keyword "post-FUE scalp massage timing"
AND no competitor appears in top 10
AND no GSC impressions for hairgenetix.com
WHEN gap matrix generation runs
THEN classification is "new_opportunity"
AND competitor_presence=false
```

**ATS-004: No GSC fallback**

```
GIVEN hairgenetix.com with no GSC connected
WHEN gap matrix generation runs
THEN SERP-based coverage is used (checking top 50 for user domain)
AND a warning is included: "GSC unavailable — SERP-based coverage (lower accuracy)"
```

**ATS-005: All topics covered — no gaps**

```
GIVEN the user site ranks in top 50 for every keyword in the research set
WHEN gap matrix generation runs
THEN 0 own_gap rows are produced
AND new_opportunity rows are shown if any
```

**ATS-006: Missing competitor data handled gracefully**

```
GIVEN a competitor URL with crawl_failed=true in F-005
WHEN gap matrix generation runs
THEN that competitor is excluded from the keyword's gap calculation
AND the gap row is marked "partial — 1 competitor(s) excluded"
AND no pipeline halt occurs
```

### US-002: Thin Content Identification

**ATS-007: Classic thin content**

```
GIVEN hairgenetix.com ranks #18 for "FUE aftercare"
AND our page has 400 words
AND top-3 competitors average 2900 words
WHEN thin content identification runs
THEN thin_content=true
AND estimated_word_count_gap=2500
AND recommendation is "Update existing" with our page URL
AND rationale: "Ranks #18. Competitor average: 2900 words. Our page: 400 words. 86% below competitor average."
```

**ATS-008: Ranking well despite fewer words — NOT thin**

```
GIVEN hairgenetix.com ranks #4 for "hair transplant Turkey cost"
AND our page has 800 words vs competitor average 1200 words
WHEN thin content identification runs
THEN thin_content=false (ranking well — not flagged despite word count gap)
```

**ATS-009: Not ranking at all — not a thin content case**

```
GIVEN hairgenetix.com does not appear in top 50 for a keyword
WHEN thin content identification runs
THEN the keyword is classified as own_gap, NOT thin_content
```

**ATS-010: Word count unavailable for comparison**

```
GIVEN a competitor page had crawl_failed=true
WHEN thin content assessment runs for that keyword
THEN thin content assessment is skipped for that comparison
AND marked "insufficient data"
```

### US-003: Opportunity Scoring

**ATS-011: High-value gap scored**

```
GIVEN keyword "FUE vs DHI comparison" with volume=8100, difficulty=32, no competitor in top 5
WHEN opportunity scoring runs
THEN opportunity_score is approximately 0.74
AND score_rationale: "Score: 0.74 — High volume (8,100/mo), easy to rank (32/100), no competitor in top 5."
AND formula inputs (volume_normalised, difficulty_inverse, gap_score) are stored alongside
```

**ATS-012: Low-value gap scored**

```
GIVEN keyword "hair transplant Nairobi" with volume=40, difficulty=15, competitor at #3
WHEN opportunity scoring runs
THEN opportunity_score is approximately 0.18
AND score_rationale mentions "Low volume" and "competitor at position 3"
```

**ATS-013: Thin content priority scoring**

```
GIVEN a thin content entry: ranks #22, 380-word page, competitor avg 2900 words
WHEN thin content priority scoring runs
THEN thin_content_priority_score is approximately 0.82
AND rationale mentions ranking position and word count gap
```

**ATS-014: Zero volume keyword scored**

```
GIVEN a keyword with volume=0, flagged "low/zero volume"
WHEN opportunity scoring runs
THEN volume_normalised=0
AND score may be non-zero (due to low difficulty + gap)
AND flagged "zero volume — AISO value only"
```

**ATS-015: Score components stored for transparency**

```
GIVEN any scored gap row
WHEN opportunity scoring completes
THEN the record includes score_inputs: {volume_normalised, difficulty_inverse_normalised, gap_score}
AND the score is reproducible from these inputs using the documented formula
```

### US-004: Multilingual Gap Analysis

**ATS-016: Universal gap across all languages**

```
GIVEN keyword "FUE vs DHI comparison" is missing in DE, FR, NL, EN
WHEN multilingual gap analysis runs
THEN universal_gap=true
AND opportunity_score receives +0.1 bonus
AND note: "Missing in 4/4 analysed languages"
```

**ATS-017: Language-specific gap**

```
GIVEN keyword "Haartransplantation Kosten" is a gap in DE only
AND equivalent term is covered in EN
WHEN multilingual gap analysis runs
THEN the gap is tagged as language_specific: ["DE"]
AND EN coverage is referenced
```

**ATS-018: Already covered in all languages**

```
GIVEN keyword "hair transplant surgery" — user ranks top 5 in all configured languages
WHEN multilingual gap analysis runs
THEN no gap row is produced for this keyword
AND it appears in the own_coverage section only
```

**ATS-019: Per-language independent matrices**

```
GIVEN the pipeline is configured for DE and EN
WHEN gap analysis runs
THEN two separate gap matrices are produced (one per language)
AND a cross-language summary shows universal vs language-specific gaps
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: F-004 + F-005 → F-006 input pipeline**

```
GIVEN F-004 (SERP data) and F-005 (competitor snapshots) have completed
WHEN F-006 receives their outputs
THEN ranking positions, competitor URLs, word counts, and depth scores are available
AND ContentGap schema validates
```

**INT-002: GSC API integration**

```
GIVEN valid GSC OAuth credentials for hairgenetix.com
WHEN coverage data is requested
THEN GSC query/impression data is returned
AND cross-referenced against the F-001 keyword list
```

**INT-003: F-006 output → F-007 input pipeline**

```
GIVEN F-006 has produced a gap matrix with opportunity scores
WHEN F-007 (Content Calendar) consumes the output
THEN gap rows with classifications, scores, and rationales are available
AND ContentGap schema validates
```

**INT-004: GSC fallback to SERP-based coverage**

```
GIVEN GSC API returns an error or is not configured
WHEN gap analysis runs
THEN the system falls back to SERP-based coverage check (top 50)
AND the analysis completes with lower-accuracy flag
```

**INT-005: Fixture-based offline test**

```
GIVEN mock SERP records and mock competitor snapshots as fixture data
WHEN gap analysis runs in test mode
THEN the full gap matrix is produced without any network calls
AND all scoring and classification logic is exercised
```

**INT-006: Standalone JSON output**

```
GIVEN standalone mode (no database)
WHEN gap analysis completes
THEN the gap matrix is saved to data/gap-analysis/{domain}/{language}.json
AND the JSON validates against ContentGap schema
```

**INT-007: Performance — 100 keywords, 3 competitors, < 3 minutes**

```
GIVEN 100 keywords and 3 competitors with fixture data
WHEN gap matrix generation runs
THEN the operation completes within 3 minutes
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | Valid classification | gap classification is one of: "own_coverage", "own_gap", "new_opportunity" |
| PI-002 | No duplicate entries | No two rows in the gap matrix share the same (keyword, language) tuple |
| PI-003 | Opportunity score range | opportunity_score is always 0.0-1.0 inclusive (with +0.1 universal bonus, max 1.1) |
| PI-004 | Score inputs present | Every scored row includes score_inputs object with volume, difficulty, gap components |
| PI-005 | Thin content threshold | thin_content=true only when user ranks 11-50 AND word_count < 50% of competitor average |
| PI-006 | Rationale non-empty | Every scored row has a non-empty score_rationale or thin_content_rationale string |
| PI-007 | Per-language independence | Gap rows for DE and EN are computed independently — a gap in DE does not imply a gap in EN |
| PI-008 | LLM fields labelled | All fields sourced from F-005 LLM quality assessment are labelled "llm_assessed" |
| PI-009 | Tenant isolation | Every gap row has a non-null tenant_id |
| PI-010 | Existing page URL for thin content | If gap_type is "thin_content", existing_page_url is non-null |
| PI-011 | Formula reproducibility | opportunity_score can be exactly reproduced from score_inputs using the documented formula |
| PI-012 | Thin content excludes non-ranking | Keywords where user does not rank in top 50 are never classified as thin_content |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 to ATS-006 | Integration | Requires F-004/F-005 data and optionally GSC API |
| ATS-007 to ATS-010 | Unit | Thin content rules are pure computation on input data |
| ATS-011 to ATS-015 | Unit | Opportunity scoring formula is pure computation |
| ATS-016 to ATS-019 | Integration | Requires multi-language pipeline data |
| INT-001 to INT-007 | Integration | Cross-feature data flow and storage boundaries |
| PI-001 to PI-012 | Property | Fast-check on ContentGap schema and scoring constraints |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
