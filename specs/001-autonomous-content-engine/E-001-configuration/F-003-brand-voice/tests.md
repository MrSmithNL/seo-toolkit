# Tests — F-003 Brand Voice Training

> Acceptance test scenarios derived from requirements.md per RE v4.15 Phase 3 step 13.
> These are human-authored specifications — the building agent implements them as executable tests.

---

## Acceptance Tests (GIVEN/WHEN/THEN)

### AT-001: Extract voice from multiple blog URLs (US-001 happy path)

```
GIVEN a registered site "hairgenetix.com"
WHEN the user provides 3 blog post URLs with rich content
THEN the system extracts text content from each URL (stripping nav, headers, footers)
AND generates a VoiceProfile with all fields populated
AND word_count_analysed is > 3000
AND confidence is "high"
```

### AT-002: Extract voice from minimal content (US-001 edge case)

```
GIVEN a registered site "skingenetix.com"
WHEN the user provides 1 product page URL with ~200 words
THEN the system generates a VoiceProfile
AND warns "Limited content found. Voice profile may be inaccurate."
AND confidence is "low"
```

### AT-003: Handle unreachable URL gracefully (US-001 error case)

```
GIVEN a registered site
WHEN the user provides 2 URLs, one of which returns 404
THEN the system extracts voice from the reachable URL
AND notes which URL failed
AND generates a partial profile
```

### AT-004: No extractable content (US-001 error case)

```
GIVEN a registered site
WHEN the user provides URLs that contain only images/video (no text)
THEN the system returns error "No text content found at the provided URLs."
AND no VoiceProfile is created
```

### AT-005: Manually adjust voice parameters (US-002 happy path)

```
GIVEN a VoiceProfile exists for "hairgenetix.com" with tone "formal"
WHEN the user changes tone to "conversational"
THEN the profile is updated with tone "conversational"
AND the profile is marked as "manually adjusted"
AND source_urls are preserved
```

### AT-006: Skip voice training (US-003 happy path)

```
GIVEN a registered site with no VoiceProfile
WHEN the user chooses to skip voice training
THEN a default VoiceProfile is created with:
  - tone: conversational
  - sentence_structure: mixed
  - vocabulary_level: intermediate
  - person: second
  - distinctive_patterns: []
AND confidence is "low"
AND a note "Default voice — no brand-specific training" is stored
```

### AT-007: Replace default voice with trained voice (US-003 -> US-001)

```
GIVEN a site with a default VoiceProfile (from skip)
WHEN the user provides URLs for voice extraction
THEN a new VoiceProfile replaces the default
AND confidence reflects the content analysed
```

---

## Integration Tests

### IT-001: End-to-end voice extraction

```
GIVEN a clean database with a registered site "hairgenetix.com"
WHEN the user provides 3 blog post URLs for voice extraction
THEN a VoiceProfile record exists in the database
AND all fields are populated (tone, sentence_structure, vocabulary_level, person)
AND source_urls contains the 3 input URLs
AND word_count_analysed is > 0
AND a structured log entry was created
```

### IT-002: Voice profile used as pipeline input

```
GIVEN a VoiceProfile exists for a site with tone "conversational" and person "second"
WHEN E-003 (Generation) reads the profile for content generation
THEN the voice profile JSON is accessible and parseable
AND contains all required fields for system prompt modification
```

### IT-003: Non-English voice extraction

```
GIVEN a registered site "digitalbouwers.nl" with Dutch content
WHEN the user provides Dutch blog post URLs
THEN the system detects the content language as Dutch
AND generates a voice profile appropriate for Dutch writing patterns
AND distinctive_patterns may include Dutch-specific observations
```

---

## Property Invariants

| Property | Description | Test Type |
|----------|-----------|-----------|
| tone is always one of: formal, conversational, technical, casual, authoritative | No other values allowed | Unit |
| sentence_structure is always one of: short, long, mixed | No other values allowed | Unit |
| vocabulary_level is always one of: simple, intermediate, advanced, technical | No other values allowed | Unit |
| person is always one of: first, second, third | No other values allowed | Unit |
| confidence is always one of: low, medium, high | No other values allowed | Unit |
| word_count_analysed >= 0 | Never negative | Unit |
| source_urls contains only valid URLs | All entries are parseable URLs | Unit |

---

## Hallucination Risk Scenarios

| Risk | Scenario | Mitigation |
|------|---------|------------|
| Agent might invent voice characteristics not present in source content | Profile describes "humorous tone" when source is purely formal | AT-001 verified manually; AI prompt instructs "base all parameters on actual content" |
| Agent might skip HTML stripping and analyse navigation text | Voice profile reflects nav menu text, not article content | IT-001 checks word_count_analysed is reasonable for article content only |
| Agent might hardcode profiles for known test sites | Profile for hairgenetix.com is always the same regardless of input URLs | Test with varied URL sets; verify profile changes with different inputs |

---

## Test Layer Classification

| Test ID | Layer | Automated? |
|---------|-------|:----------:|
| AT-001 to AT-004 | Acceptance (Extraction) | Yes |
| AT-005 | Acceptance (Manual Edit) | Yes |
| AT-006 to AT-007 | Acceptance (Skip/Default) | Yes |
| IT-001 to IT-003 | Integration | Yes |
| Property invariants | Unit | Yes |
