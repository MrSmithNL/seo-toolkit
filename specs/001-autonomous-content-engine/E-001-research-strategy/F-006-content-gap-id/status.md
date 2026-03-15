---
id: FTR-SEO-006
type: feature
title: "Content Gap Identification"
project: PROD-001
domain: seo.content-pipeline
parent: PROD-001-SPEC-E-001
status: built
phase: 6-build
priority: must
size: L
risk: medium
owner: claude
created: 2026-03-15
last_updated: 2026-03-15
saas_ecosystem: true
hierarchy_level: L3-module
hierarchy_location: "modules/content-engine/"
capability_group: seo
dual_mode: true
five_port: true
module_manifest: required
tenant_aware: true
dependency_checklist_complete: false
level_checklist_used: L3
gates:
  scope: approved
  completeness: approved
  build_approval: approved
---

# F-006: Content Gap Identification — Status

## Current State

Build complete. All 7 tasks implemented with TDD. 92 F-006 tests passing, 769 total tests passing (zero regressions). Feature flag `FEATURE_CONTENT_GAP` controls activation.

## Phase Progress

- [x] Phase 1 — Understand
- [x] Phase 2 — Research
- [x] Gate 1 — Scope Approval
- [x] Phase 3 — Requirements
- [x] Gate 2 — Completeness Review
- [x] Phase 4 — Design
- [x] Phase 5 — Tasks
- [x] Gate 3 — Build Approval
- [x] Phase 6 — Build
- [ ] Phase 7 — Ship
- [ ] Phase 8 — Retrospective

## Task Status

| Task | Description | Status | Tests |
|------|-------------|--------|-------|
| T-001 | ContentGap models & contracts | Done | 21 |
| T-002 | CoverageClassifier (GSC + SERP fallback) | Done | 11 |
| T-003 | ThinContentDetector | Done | 12 |
| T-004 | OpportunityScorer | Done | 15 |
| T-005 | CrossLanguageSummariser | Done | 9 |
| T-006 | GapMatrixRepo (file adapter) | Done | 9 |
| T-007 | GenerateGapMatrix + CrossLanguageSummary commands | Done | 15 |
| **Total** | | **7/7** | **92** |

## Decisions Made

1. CLI-first modality for R1 (Gate 1 decision, 2026-03-15)
2. **ScoringConfig at module root** — placed `scoring_config.py` at `src/research_engine/` (not in `config/` subdirectory) to avoid shadowing the existing `config.py` module. Follows flat module pattern used by F-001–F-005.
3. **GSC primary, SERP fallback** — implemented ADR-F006-001. Coverage source tracked per record for auditability.
4. **Configurable scoring weights via env vars** — implemented ADR-F006-002. Defaults: volume 0.4, difficulty 0.3, gap 0.3, universal bonus 0.1, thin threshold 0.5.
5. **Per-language independent matrices** — implemented ADR-F006-003. Cross-language summary runs after all per-language matrices complete.
6. **Feature flag pattern** — `feature_enabled` parameter on command handlers (consistent with F-005 pattern), backed by `feature_content_gap` in ResearchConfig.
7. **Thin content = coverage for cross-language** — thin_content counts as coverage (we rank, just poorly), not as a gap. Only own_gap and new_opportunity count as gaps for universal gap detection.

## Open Questions

- [x] What is the minimum gap recall threshold? → Deferred to Phase 7 (Ship). Will validate with Hairgenetix manual audit.
- [ ] Should thin content rows appear in same calendar as gap rows? → Proposed: separate sections in F-007 ("New content" vs "Update existing"). Confirm with Malcolm.
- [ ] Default keyword volume minimum for calendar? → Proposed: 50 monthly searches. Confirm before F-007 build.

## Files Created

### Source (10 files)
- `src/research_engine/models/content_gap.py` — Domain models (GapType, ContentGapRecord, CrossLanguageSummaryRecord, input types)
- `src/research_engine/ports/coverage_data_source.py` — CoverageDataSource Protocol
- `src/research_engine/ports/gap_matrix_port.py` — GapMatrixPort Protocol
- `src/research_engine/repos/file_gap_matrix_repo.py` — File-based GapMatrixPort implementation
- `src/research_engine/scoring_config.py` — ScoringConfig (frozen dataclass, env var loading)
- `src/research_engine/services/coverage_classifier.py` — Coverage classification (GSC + SERP)
- `src/research_engine/services/thin_content_detector.py` — Thin content detection
- `src/research_engine/services/opportunity_scorer.py` — Opportunity + thin content priority scoring
- `src/research_engine/services/cross_language_summariser.py` — Cross-language gap summarisation
- `src/research_engine/events/gap_events.py` — Gap analysis events
- `src/research_engine/commands/generate_gap_matrix.py` — GenerateGapMatrix command handler
- `src/research_engine/commands/generate_cross_language_summary.py` — CrossLanguageSummary command handler

### Tests (8 files, 92 tests)
- `tests/test_research_engine/test_models/test_content_gap_models.py` — 21 tests
- `tests/test_research_engine/test_services/test_coverage_classifier.py` — 11 tests
- `tests/test_research_engine/test_services/test_opportunity_scorer.py` — 15 tests
- `tests/test_research_engine/test_services/test_thin_content_detector.py` — 12 tests
- `tests/test_research_engine/test_services/test_cross_language_summariser.py` — 9 tests
- `tests/test_research_engine/test_repos/test_gap_matrix_repo.py` — 9 tests
- `tests/test_research_engine/test_commands/test_generate_gap_matrix.py` — 10 tests
- `tests/test_research_engine/test_commands/test_generate_cross_language_summary.py` — 5 tests

### Modified (1 file)
- `src/research_engine/config.py` — Added `feature_content_gap: bool = False`

## UAT

N/A — Phase 6

## Retrospective

N/A — Phase 6

## Session Log

| Date | Summary | Next Step |
|------|---------|-----------|
| 2026-03-15 | Requirements complete — EARS criteria, NFR scan, competitive tags, dimensions A-F | Gate 2 presentation |
| 2026-03-15 | Build complete — 7 tasks, 92 tests, TDD throughout, zero regressions | Ship phase |
