# Tests — F-005 Quality Threshold Settings

> Acceptance test scenarios derived from requirements.md per RE v4.15 Phase 3 step 13.
> These are human-authored specifications — the building agent implements them as executable tests.

---

## Acceptance Tests (GIVEN/WHEN/THEN)

### AT-001: Default thresholds on fresh site (US-001 happy path)

```
GIVEN a newly configured site with no custom quality settings
WHEN the quality thresholds are queried
THEN all defaults are applied:
  - seo_score_min: 65
  - aiso_score_min: 7.0
  - readability_target: grade_8
  - word_count_min: 1500
  - word_count_max: 3000
  - publish_mode: draft_review
```

### AT-002: Update single threshold (US-001 variant)

```
GIVEN a site with default quality thresholds
WHEN the user sets seo_score_min to 80
THEN seo_score_min is 80
AND all other thresholds remain at their defaults
```

### AT-003: Article passes all quality gates (US-002 happy path)

```
GIVEN a site with default thresholds (65/7.0/grade_8/1500-3000)
AND publish_mode is "auto_publish"
WHEN an article scores SEO: 78, AISO: 8.2, readability: grade_7, word count: 2100
THEN the article passes all quality gates
AND is published automatically per publish_mode
```

### AT-004: Article fails SEO threshold (US-002 failure case)

```
GIVEN a site with seo_score_min: 65
WHEN an article scores SEO: 52
THEN the article is held for review
AND the system reports "SEO score 52 < minimum 65"
```

### AT-005: Article fails multiple thresholds (US-002 failure case)

```
GIVEN a site with default thresholds
WHEN an article scores SEO: 52, AISO: 5.1, word count: 900
THEN the article is held for review
AND the system reports all failures: "SEO 52<65, AISO 5.1<7.0, Words 900<1500"
```

### AT-006: Quality gate overrides auto-publish (US-002 + US-003)

```
GIVEN a site with publish_mode "auto_publish"
WHEN an article fails any quality threshold
THEN the article is held for review (NOT auto-published)
AND the quality gate takes precedence over publish mode
```

### AT-007: Draft review mode (US-003 happy path)

```
GIVEN a site with publish_mode "draft_review"
WHEN an article passes all quality thresholds
THEN the article is created as a draft in the CMS
```

### AT-008: Manual only mode (US-003 variant)

```
GIVEN a site with publish_mode "manual_only"
WHEN an article passes all quality thresholds
THEN the article is stored locally
AND is NOT pushed to any CMS
```

### AT-009: Auto-publish warning at config time (US-003 guard)

```
GIVEN a site configuration screen
WHEN the user sets publish_mode to "auto_publish"
THEN the system warns "Articles will be published live without human review"
```

---

## Integration Tests

### IT-001: End-to-end threshold creation

```
GIVEN a clean database with a newly registered site
WHEN site configuration completes
THEN a QualityThresholds record exists with all default values
AND the record is linked to the correct site_id
```

### IT-002: Fail-safe on evaluation error

```
GIVEN a site with quality thresholds configured
WHEN the quality evaluation function throws an error
THEN the article is HELD for review (never auto-published)
AND the error is logged
```

### IT-003: Quality gate log entries

```
GIVEN an article evaluated against quality thresholds
WHEN the evaluation completes (pass or fail)
THEN a structured log entry contains: article ID, all scores, all thresholds, gate decision (pass/hold)
```

---

## Property Invariants

| Property | Description | Test Type |
|----------|-----------|-----------|
| seo_score_min is 0-100 | Never outside this range | Unit |
| aiso_score_min is 0.0-10.0 | Never outside this range | Unit |
| readability_target is one of: grade_6, grade_8, grade_10, grade_12 | No other values | Unit |
| word_count_min <= word_count_max | Min never exceeds max | Unit |
| word_count_min >= 0 and word_count_max >= 0 | Never negative | Unit |
| publish_mode is one of: auto_publish, draft_review, manual_only | No other values | Unit |
| Quality gate ALWAYS holds on evaluation failure | Fail-safe invariant | Integration |

---

## Hallucination Risk Scenarios

| Risk | Scenario | Mitigation |
|------|---------|------------|
| Agent might auto-publish when quality evaluation fails | Error in scorer = article published | IT-002 explicitly tests fail-safe behaviour |
| Agent might skip threshold checks for "draft" mode | "It's just a draft, no need to check" | AT-007 verifies quality gate runs regardless of publish mode |
| Agent might hardcode passing scores in tests | All test articles always pass | AT-004/AT-005 explicitly test failure cases with specific scores |

---

## Test Layer Classification

| Test ID | Layer | Automated? |
|---------|-------|:----------:|
| AT-001 to AT-002 | Acceptance (Defaults) | Yes |
| AT-003 to AT-006 | Acceptance (Quality Gate) | Yes |
| AT-007 to AT-009 | Acceptance (Publish Mode) | Yes |
| IT-001 to IT-003 | Integration | Yes |
| Property invariants | Unit | Yes |
