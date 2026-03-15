# F-006: Content Gap Identification — Tasks

## Task T-001: ContentGap Schema & Migration [Foundation]
**Story:** US-001 (Gap Matrix)
**Size:** M
**Depends on:** F-001 T-001 (keyword schema)
**Parallel:** Yes [P]

### What
Create the Drizzle schema for `content_gap` and `cross_language_summary` tables with all columns from design.md. Generate Zod validation schemas. Write the migration with RLS policies on both tables and all indexes.

### Files
- Create: `modules/content-engine/research/schema/content-gap.ts`
- Create: `modules/content-engine/research/contracts/content-gap.ts`
- Create: `modules/content-engine/research/migrations/0005_content_gap_tables.sql`
- Create (tests): `modules/content-engine/research/schema/__tests__/content-gap.schema.test.ts`

### Test Scenarios (from tests.md)
- PI-001: Valid classification (one of 3 valid values)
- PI-002: No duplicate entries (keyword, language unique)
- PI-009: Tenant isolation (tenant_id non-null)

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `content_gap` table with all columns per design.md
- [ ] `cross_language_summary` table with all columns
- [ ] RLS policies on both tables
- [ ] 4 indexes on content_gap, 2 on cross_language_summary
- [ ] Zod schemas auto-generated
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write schema, migration, tests
- Ask: add columns beyond design
- Never: skip RLS on either table

---

## Task T-002: CoverageClassifier [Domain Logic]
**Story:** US-001 (Gap Matrix)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the `CoverageClassifier` with the `CoverageDataSource` interface (ADR-F006-001). Two implementations: `GscCoverageSource` (primary, GSC impressions > 0 = covered) and `SerpCoverageSource` (fallback, user domain in top-50). Automatic fallback when GSC unavailable, flagged in output.

### Files
- Create: `modules/content-engine/research/services/coverage-classifier.ts`
- Create: `modules/content-engine/research/ports/coverage-data-source.ts`
- Create: `modules/content-engine/research/adapters/gsc-coverage-source.ts`
- Create: `modules/content-engine/research/adapters/serp-coverage-source.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/coverage-classifier.test.ts`

### Test Scenarios (from tests.md)
- ATS-001: GSC available, gap found → own_gap
- ATS-003: No competitor, no GSC → new_opportunity
- ATS-004: No GSC fallback → SERP-based coverage + warning
- ATS-005: All topics covered → 0 own_gap rows
- PI-007: Per-language independence

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `CoverageDataSource` interface with GSC and SERP implementations
- [ ] Automatic GSC → SERP fallback on unavailability
- [ ] Classification: own_coverage, own_gap, new_opportunity
- [ ] `coverage_source` flag: "gsc" | "serp_fallback"
- [ ] Tests pass with mock GSC and mock SERP data
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new classification types
- Never: make real GSC API calls in tests

---

## Task T-003: ThinContentDetector [Domain Logic]
**Story:** US-002 (Thin Content Identification)
**Size:** M
**Depends on:** T-002 (needs coverage classification)
**Parallel:** No

### What
Implement the `ThinContentDetector` that flags `own_coverage` keywords where our content is significantly weaker. Filters to keywords ranking 11-50, compares word count vs top-3 competitor average, flags when our word count < 50% of competitor average. Never flags top-10 rankings. Handles missing competitor data gracefully.

### Files
- Create: `modules/content-engine/research/services/thin-content-detector.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/thin-content-detector.test.ts`

### Test Scenarios (from tests.md)
- ATS-002: Ranks #22, 450 words vs 2800 avg → thin_content
- ATS-007: Classic thin: #18, 400 words vs 2900 avg
- ATS-008: Ranks #4, fewer words → NOT thin (ranking well)
- ATS-009: Not ranking → own_gap, not thin_content
- ATS-010: Competitor data missing → skip assessment, "insufficient data"
- PI-005: thin_content only when rank 11-50 AND < 50% competitor avg
- PI-012: Non-ranking never classified as thin_content

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Filters to rank 11-50 keywords only
- [ ] Compares word count vs top-3 competitor average
- [ ] Threshold: < 50% = thin content
- [ ] Top-10 rankings exempt regardless of word count
- [ ] Handles missing competitor data (crawl_failed)
- [ ] Calculates `word_count_gap` and generates `thin_content_rationale`
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change threshold from 50%
- Never: flag top-10 as thin content

---

## Task T-004: OpportunityScorer [Domain Logic]
**Story:** US-003 (Opportunity Scoring)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Implement the pure `calculateOpportunityScore` function per ADR-F006-002. Configurable weights via `ScoringConfig` (loaded from env vars with defaults). Also implements `calculateThinContentPriorityScore`. Both generate rationale strings and persist score_inputs for reproducibility.

### Files
- Create: `modules/content-engine/research/services/opportunity-scorer.ts`
- Create: `modules/content-engine/research/config/scoring-config.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/opportunity-scorer.test.ts`

### Test Scenarios (from tests.md)
- ATS-011: High value → score ≈ 0.74
- ATS-012: Low value → score ≈ 0.18
- ATS-013: Thin content priority → score ≈ 0.82
- ATS-014: Zero volume → volume_normalised=0, score may be non-zero
- ATS-015: Score components stored for transparency
- PI-003: Score always 0.0-1.0 (clamped)
- PI-004: Score inputs always present when score is set
- PI-006: Rationale non-empty
- PI-011: Score reproducible from inputs + formula

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Formula: `(volume_norm × 0.4) + (difficulty_inverse × 0.3) + (gap_score × 0.3)`
- [ ] Universal gap bonus: +0.1, clamped to max 1.0
- [ ] `ScoringConfig` loaded from env vars with defaults
- [ ] `calculateThinContentPriorityScore` with position + wordcount weights
- [ ] Score rationale generated for every calculation
- [ ] `score_inputs` object always persisted alongside score
- [ ] Property tests: score always 0.0-1.0 for any input combination
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change default weights
- Never: hardcode weights in business logic, skip rationale generation

---

## Task T-005: CrossLanguageSummariser [Domain Logic]
**Story:** US-004 (Multilingual Gap Analysis)
**Size:** M
**Depends on:** T-002, T-004
**Parallel:** No

### What
Implement the `CrossLanguageSummariser` per ADR-F006-003. Groups gap records by keyword_id across languages, identifies universal gaps (gap in all languages) vs language-specific gaps. Universal gaps get +0.1 bonus to opportunity score. Updates `is_universal_gap` flag on content_gap records.

### Files
- Create: `modules/content-engine/research/services/cross-language-summariser.ts`
- Create (tests): `modules/content-engine/research/services/__tests__/cross-language-summariser.test.ts`

### Test Scenarios (from tests.md)
- ATS-016: Universal gap across 4 languages → +0.1 bonus
- ATS-017: Language-specific gap (DE only) → tagged
- ATS-018: Covered in all languages → no gap row
- ATS-019: Per-language independent matrices produced

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Groups gaps by keyword_id across languages
- [ ] Universal gap: gap exists in ALL analysed languages
- [ ] Language-specific: gap in some languages
- [ ] +0.1 score bonus for universal gaps (clamped to 1.0)
- [ ] `cross_language_summary` records created
- [ ] `is_universal_gap` flag updated on content_gap records
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change universal gap bonus value
- Never: assume EN gaps exist in other languages

---

## Task T-006: GapMatrixRepo (DB + File) [Integration]
**Story:** US-001
**Size:** M
**Depends on:** T-001 (schema)
**Parallel:** Yes [P]

### What
Implement the `GapMatrixPort` interface with `DatabaseGapMatrixRepo` and `FileGapMatrixRepo`. Both support save, getGapMatrix (with filters), and getTopOpportunities queries. File adapter writes to `data/gap-analysis/{domain}/{language}.json`.

### Files
- Create: `modules/content-engine/research/ports/gap-matrix-port.ts`
- Create: `modules/content-engine/research/repos/db-gap-matrix-repo.ts`
- Create: `modules/content-engine/research/repos/file-gap-matrix-repo.ts`
- Create (tests): `modules/content-engine/research/repos/__tests__/gap-matrix-repo.test.ts`

### Test Scenarios (from tests.md)
- INT-006: Standalone JSON output validates
- PI-002: No duplicate (keyword, language) entries

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Save, getGapMatrix, getTopOpportunities implemented
- [ ] Filter by gap_type, sort by score, min_score threshold
- [ ] File adapter: `data/gap-analysis/{domain}/{language}.json`
- [ ] Both adapters produce identical query results (parity test)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change storage structure
- Never: skip tenant_id in queries

---

## Task T-007: GenerateGapMatrix + CrossLanguageSummary Commands [Integration]
**Story:** All user stories
**Size:** L
**Depends on:** T-002, T-003, T-004, T-005, T-006
**Parallel:** No

### What
Implement `GenerateGapMatrixCommand` and `GenerateCrossLanguageSummaryCommand` handlers. The gap matrix command: loads keywords + SERP + competitor data for campaign+locale, classifies coverage, detects thin content, scores opportunities, persists results, emits events. The cross-language command: runs after all per-language matrices are built.

### Files
- Create: `modules/content-engine/research/commands/generate-gap-matrix.ts`
- Create: `modules/content-engine/research/commands/generate-cross-language-summary.ts`
- Create: `modules/content-engine/research/events/gap-events.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/generate-gap-matrix.test.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/generate-cross-language-summary.test.ts`
- Modify: `modules/content-engine/research/index.ts` (export commands)

### Test Scenarios (from tests.md)
- ATS-001: Happy path — GSC available, gap found
- ATS-004: No GSC fallback → SERP coverage
- ATS-006: Missing competitor data handled gracefully
- INT-001: F-004 + F-005 → F-006 pipeline
- INT-003: F-006 output consumable by F-007
- INT-007: 100 keywords, 3 competitors < 3 minutes

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Full pipeline: load data → classify → thin detect → score → persist → event
- [ ] `GenerateGapMatrixOutput` with gap type counts, coverage source
- [ ] `GapMatrixGenerated` event emitted per language
- [ ] `CrossLanguageSummaryGenerated` event emitted
- [ ] Missing competitor data excluded gracefully (partial_data flag)
- [ ] Feature flag `FEATURE_CONTENT_GAP` checked at entry
- [ ] Structured JSON logging: gap counts, scores, duration
- [ ] Zero LLM calls (F-006 is pure computation)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change event schema
- Never: add LLM calls, skip tests, bypass feature flag
