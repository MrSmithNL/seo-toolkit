---
id: FTR-SEO-003
type: feature
title: "Search Intent Classification"
project: PROD-001
domain: seo.content-pipeline
parent: PROD-001-SPEC-E-001
status: built
phase: 6-build
priority: must
size: M
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

# F-003: Search Intent Classification — Status

## Current State

Build complete. All 6 tasks implemented with TDD. 103 F-003 tests pass (23 + 27 + 17 + 12 + 6 + 4 + 14 config). Full suite: 365 tests, 92.49% coverage.

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

| Task | Description | Status |
|------|-------------|--------|
| T-001 | Intent Enums & Contract Types | Done — 23 tests |
| T-002 | Classification Prompt & Response Parser | Done — 27 tests |
| T-003 | Format Signal Detector | Done — 17 tests |
| T-004 | Chunked Classification Pipeline | Done — 12 tests |
| T-005 | Intent Distribution Query | Done — 6 tests |
| T-006 | Config & Module Bootstrap | Done — 4 tests (+ 14 existing config tests) |

## Files Created

| File | Purpose |
|------|---------|
| `src/research_engine/models/intent.py` | IntentType, IntentConfidence, ContentFormat enums + IntentClassification model |
| `src/research_engine/prompts/intent-classification-v1.txt` | Versioned LLM prompt template |
| `src/research_engine/__fixtures__/intent-classification-response.json` | 20-keyword fixture for parser tests |
| `src/research_engine/domain/intent_prompt_builder.py` | Prompt builder (loads template, sanitizes keywords) |
| `src/research_engine/domain/intent_response_parser.py` | Response parser (validates JSON, completeness, enums) |
| `src/research_engine/domain/format_signal_detector.py` | Rule-based format signal detection (8 regex patterns) |
| `src/research_engine/commands/classify_keyword_intent.py` | Full classification pipeline (7-step orchestrator) |
| `src/research_engine/events/intent_events.py` | IntentClassificationCompletedEvent + emit function |
| `src/research_engine/queries/get_intent_distribution.py` | Intent distribution query (aggregates by intent/confidence/format) |

## Files Modified

| File | Change |
|------|--------|
| `src/research_engine/config.py` | Added feature_intent_classification flag, intent_chunk_size, intent_max_retries |
| `src/research_engine/models/__init__.py` | Added exports for intent types |
| `src/research_engine/ports/storage.py` | Added update_intent_fields to KeywordStoragePort |
| `src/research_engine/adapters/json_storage.py` | Implemented update_intent_fields |
| `tests/test_research_engine/conftest.py` | Added update_intent_fields to MockStorage |
| `tests/test_research_engine/test_config.py` | Added 4 intent config tests |

## Decisions Made

1. CLI-first modality for R1 (Gate 1 decision, 2026-03-15)
2. IntentType/IntentConfidence/ContentFormat as StrEnum (consistent with F-001/F-002 pattern)
3. Prompt versioned in separate file (not inline string)
4. Format signal detection is rule-based (regex patterns, no LLM needed)
5. Pipeline uses chunked processing (50 keywords per LLM call)

## Open Questions

- [ ] Should the format recommendation list be extensible by the user? (Proposed: fixed enum for R1; extensible in R2+ via config)
- [ ] How should navigational keywords be handled in the content calendar? (Proposed: include but flag)

## UAT

N/A — Phase 6

## Retrospective

N/A — Phase 6

## Session Log

| Date | Summary | Next Step |
|------|---------|-----------|
| 2026-03-15 | Requirements complete — EARS criteria, NFR scan, competitive tags, dimensions A-F | Gate 2 presentation |
| 2026-03-15 | Build complete — 6 tasks, 103 tests, 92.49% coverage, all green | Ship / Retrospective |
