---
id: FTR-SEO-004
type: feature
title: "SERP Analysis"
project: PROD-001
domain: seo.content-pipeline
parent: PROD-001-SPEC-E-001
status: build-complete
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
dependency_checklist_complete: true
level_checklist_used: L3
gates:
  scope: approved
  completeness: approved
  build_approval: approved
---

# F-004: SERP Analysis — Status

## Current State

**Build complete.** All 7 tasks implemented with TDD. 141 F-004 tests passing, 506 total project tests passing (93.6% coverage). All acceptance test scenarios from tests.md are covered. Ready for Phase 7 (Ship).

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
| T-001 | SERP models (SerpSnapshot, SerpResult, SerpFeatures) | Done | 45 |
| T-002 | SerpDataSource Protocol + MockSerpDataSource + fixtures | Done | 12 |
| T-003 | Rate limiter (daily counter, per-source limits) | Done | 14 |
| T-004 | SerpFeatureDetector (normalize features from any source) | Done | 16 |
| T-005 | DataForSEO adapter (API client, retry, backoff) | Done | 12 |
| T-006 | SerpSnapshotRepo (file storage adapter) | Done | 20 |
| T-007 | AnalyseSerpCommand + BatchAnalyseSerpCommand | Done | 22 |
| **Total** | | **7/7** | **141** |

## Decisions Made

1. CLI-first modality for R1 (Gate 1 decision, 2026-03-15)
2. **ADR-F004-001: Python Adapter pattern** — SerpDataSource Protocol with DataForSEO + Mock implementations. MockSerpDataSource supports `set_error()` for failure testing.
3. **ADR-F004-002: In-memory rate limiter** — Token bucket with per-source daily counters, midnight UTC reset. Redis adapter deferred to R2+.
4. **ADR-F004-003: Feature detection as post-processing** — SerpFeatureDetector normalizes flags from any source into canonical SerpFeatures. AI Overview warning propagated via `get_warnings()`.
5. **File-based storage only for R1** — FileSerpSnapshotRepo (JSON files). DatabaseSerpSnapshotRepo deferred to R2+ when PostgreSQL is available.
6. **Cost tracking** — DataForSEO cost estimate ($0.0006/request) logged per snapshot. Cached results show $0.0000.
7. **Pydantic v2 models as source of truth** — Python equivalent of Drizzle schema. Validators enforce position range (1-10), locale/country allowlists, PAA cap (5).

## Open Questions — Resolved

- [x] ~~Should SERP snapshots older than 90 days be archived or deleted?~~ **Resolved: retain indefinitely for R1.** Data volume is small (< 50 snapshots/day). Retention policy deferred to R2+.
- [x] ~~When the daily SERP limit is reached mid-pipeline-run, should the pipeline halt or continue?~~ **Resolved: continue.** BatchAnalyseSerpCommand queues remaining keywords as `queued_for_tomorrow`, emits `SerpDailyLimitReached` event, and returns completed results. No pipeline halt.
- [x] ~~DataForSEO $50 deposit for R1 month 3?~~ **Resolved: deferred.** MockSerpDataSource and Google scraping are sufficient for R1 development. DataForSEO adapter is ready when credentials are provided.

## Files Created

### Source
- `src/research_engine/models/serp.py` — Core SERP models (enums, SerpFeatures, SerpResult, SerpSnapshot)
- `src/research_engine/ports/serp_data_source.py` — SerpDataSource Protocol + raw response types
- `src/research_engine/ports/serp_snapshot_port.py` — SerpSnapshotPort Protocol
- `src/research_engine/adapters/mock_serp_data_source.py` — Mock adapter + 5 fixture generators
- `src/research_engine/adapters/dataforseo_adapter.py` — DataForSEO REST API adapter with retry
- `src/research_engine/repos/file_serp_snapshot_repo.py` — File-based snapshot storage
- `src/research_engine/services/serp_rate_limiter.py` — Per-source daily rate limiter
- `src/research_engine/services/serp_feature_detector.py` — Feature flag normalizer
- `src/research_engine/commands/analyse_serp.py` — AnalyseSerpCommand + BatchAnalyseSerpCommand
- `src/research_engine/events/serp_events.py` — SerpAnalysisCompleted + SerpDailyLimitReached events

### Tests
- `tests/test_research_engine/test_models/test_serp_models.py` — 45 tests (property + acceptance)
- `tests/test_research_engine/test_ports/test_serp_data_source.py` — 12 tests
- `tests/test_research_engine/test_services/test_serp_rate_limiter.py` — 14 tests
- `tests/test_research_engine/test_services/test_serp_feature_detector.py` — 16 tests
- `tests/test_research_engine/test_adapters/test_dataforseo_adapter.py` — 12 tests
- `tests/test_research_engine/test_repos/test_serp_snapshot_repo.py` — 20 tests
- `tests/test_research_engine/test_commands/test_analyse_serp.py` — 22 tests

### Modified
- `src/research_engine/models/__init__.py` — Added SERP model exports
- `src/research_engine/config.py` — Added F-004 config fields

## UAT

N/A — ready for Phase 7

## Retrospective

N/A — Phase 8

## Session Log

| Date | Summary | Next Step |
|------|---------|-----------|
| 2026-03-15 | Requirements complete — EARS criteria, NFR scan, competitive tags, dimensions A-F | Gate 2 presentation |
| 2026-03-15 | Build complete — 7 tasks, 141 tests, TDD throughout, all acceptance scenarios covered | Phase 7 (Ship) |
