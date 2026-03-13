# Tests — F-006 AISO Scoring Preferences

> Acceptance test scenarios derived from requirements.md per RE v4.15 Phase 3 step 13.
> These are human-authored specifications — the building agent implements them as executable tests.

---

## Acceptance Tests (GIVEN/WHEN/THEN)

### AT-001: Default recommended settings (US-001 happy path)

```
GIVEN a newly configured site
WHEN AISO preferences are queried
THEN use_recommended is true
AND all 36 factors are equally weighted
AND schema_types contains [Article, FAQPage, BreadcrumbList]
AND ai_platform_targets contains [chatgpt, perplexity, gemini]
```

### AT-002: Disable recommended and select priority factors (US-002 happy path)

```
GIVEN a site with use_recommended=true
WHEN the user disables recommended settings
AND selects priority_factors: ["structured_data", "entity_salience", "citation_hooks"]
THEN use_recommended is false
AND priority_factors contains exactly those 3 factors
AND those factors are weighted higher during E-003 scoring
```

### AT-003: Configure schema types (US-003 happy path)

```
GIVEN a site's AISO preferences
WHEN the user selects schema_types: [Article, Product, FAQPage, BreadcrumbList]
THEN schema_types is updated to the 4 selected types
AND E-004 uses this selection for schema injection
```

### AT-004: Reset to recommended (US-001 revert)

```
GIVEN a site with custom AISO preferences (use_recommended=false)
WHEN the user re-enables "Use recommended settings"
THEN use_recommended is true
AND custom priority_factors are cleared
AND schema_types and ai_platform_targets revert to defaults
```

---

## Integration Tests

### IT-001: End-to-end default creation

```
GIVEN a clean database with a newly registered site
WHEN site configuration completes
THEN an AISOPreferences record exists with use_recommended=true
AND default schema_types and ai_platform_targets are populated
```

### IT-002: Fallback to defaults on corruption

```
GIVEN AISO preferences that are corrupted (missing fields, invalid values)
WHEN the system reads AISO preferences
THEN it falls back to recommended defaults
AND logs a warning about corrupted preferences
```

### IT-003: AISO preferences consumed by downstream

```
GIVEN custom AISO preferences with schema_types: [Article, Product]
WHEN E-003/E-004 reads the preferences
THEN the JSON is parseable and contains the custom selection
AND only Article and Product schema are generated
```

---

## Property Invariants

| Property | Description | Test Type |
|----------|-----------|-----------|
| use_recommended is always boolean | true or false, never null | Unit |
| priority_factors only contain valid factor names from the 36-factor model | No invented factors | Unit |
| schema_types only contain valid enum values | Article, FAQPage, HowTo, Product, BreadcrumbList, Organization | Unit |
| ai_platform_targets only contain valid enum values | chatgpt, perplexity, gemini | Unit |
| When use_recommended=true, custom settings are ignored | Recommended overrides custom | Integration |

---

## Hallucination Risk Scenarios

| Risk | Scenario | Mitigation |
|------|---------|------------|
| Agent might invent AISO factors not in the 36-factor model | "social_media_presence" as a factor | Property invariant validates against factor enumeration |
| Agent might not respect use_recommended flag | Custom factors used even when recommended=true | IT integration test verifies flag behaviour |
| Agent might hardcode schema types | Always generates all 6 regardless of config | IT-003 verifies only selected types are used |

---

## Test Layer Classification

| Test ID | Layer | Automated? |
|---------|-------|:----------:|
| AT-001 | Acceptance (Defaults) | Yes |
| AT-002 | Acceptance (Custom Factors) | Yes |
| AT-003 | Acceptance (Schema Config) | Yes |
| AT-004 | Acceptance (Reset) | Yes |
| IT-001 to IT-003 | Integration | Yes |
| Property invariants | Unit | Yes |
