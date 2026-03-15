---
id: FTR-SEO-007
type: feature
title: "Content Calendar / Planning"
project: PROD-001
domain: seo.content-pipeline
parent: PROD-001-SPEC-E-001
status: complete
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

# F-007: Content Calendar / Planning — Status

## Current State

**Build complete.** All 9 tasks implemented with TDD. 108 new tests added (897 total suite). Full test suite green. This is the FINAL feature of E-001 Research & Strategy Engine.

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
| T-001 | ContentBrief Pydantic model & schema validation | Done | 36 |
| T-002 | ContentBriefBuilder — assembles briefs from pipeline data | Done | 10 |
| T-003 | RecommendationEngine — LLM-powered recommendations | Done | 11 |
| T-004 | PublishScheduler — date assignment by priority | Done | 8 |
| T-005 | LanguageScheduler — multilingual staggering | Done | 6 |
| T-006 | CalendarRenderer — Markdown + JSON output | Done | 14 |
| T-007 | ApprovalWorkflow — approve/reject/export state machine | Done | 17 |
| T-008 | FileContentBriefRepo — file-based persistence | Done | 8 |
| T-009 | GenerateCalendarCommand — full pipeline orchestrator | Done | 14 |

**Total new tests: 124** (including property-based tests via Hypothesis)

## Decisions Made

1. CLI-first modality for R1 (Gate 1 decision, 2026-03-15)
2. Python implementation (not TypeScript) per DEC-008 in epic-design.md — SaaS Platform not ready yet
3. Pydantic v2 models as equivalent to Zod schemas — single source of truth for ContentBrief
4. ContentBrief is the E-001→E-002 interface contract (schema version 1.0.0)
5. Triple validation: on creation (Pydantic model_validators), on approval (re-validate after state change), on export (validate before writing approved-briefs file)
6. LLM recommendations are best-effort with fallback to competitor headings — no pipeline halt on LLM failure
7. Dual output (Markdown + JSON) per ADR-F007-002 — JSON is authoritative
8. State machine enforced: pending_review → approved → in_progress → published; pending_review → rejected; no other transitions allowed
9. File-based persistence for standalone mode (R1), stores each brief as individual JSON file
10. Publishing cadence default 2/week, starting from next Monday after pipeline run
11. Language staggering: primary language keeps original date, subsequent languages offset +1 week each per keyword

## Open Questions — Resolved

- [x] **Markdown heading list**: Full heading list (4-8 H2s per topic) — implemented as bullet list per entry. Decision: include full list; it's needed for review quality.
- [x] **approved-briefs.json as E-002 input**: Direct input for R1. No staging step. Decision: approved-briefs.json is the direct E-002 input contract.
- [x] **Minimum calendar size**: Not enforced at schema level — left to the orchestrator/user. Decision: deferred to R2.
- [x] **Rejection replacement**: R1 — rejected topics are excluded from export, no auto-replacement. Decision: re-run pipeline for fresh recommendations.

## Test Coverage Mapping

| Spec ID | Description | Test File |
|---------|-------------|-----------|
| ATS-001 | Happy path — calendar from gap matrix | test_generate_calendar.py |
| ATS-005 | Publish date assignment — 2/week cadence | test_publish_scheduler.py |
| ATS-006 | Only thin content | test_generate_calendar.py |
| ATS-007 | LLM failure — fallback | test_generate_calendar.py |
| ATS-013 | Dual file output | test_calendar_renderer.py |
| ATS-014 | Markdown format — correct structure | test_calendar_renderer.py |
| ATS-015 | Full approval | test_approval_workflow.py |
| ATS-016 | Partial approval | test_approval_workflow.py |
| ATS-017 | Word count override | test_approval_workflow.py |
| ATS-018 | Invalid JSON caught | test_approval_workflow.py |
| ATS-020-024 | Schema validation | test_content_brief.py |
| INT-005 | Standalone file output | test_generate_calendar.py, test_file_content_brief_repo.py |
| INT-006 | Multi-language calendar | test_language_scheduler.py |
| PI-001-015 | Property invariants | test_content_brief.py, test_publish_scheduler.py |

## Session Log

| Date | Summary | Next Step |
|------|---------|-----------|
| 2026-03-15 | Requirements complete — EARS criteria, NFR scan, competitive tags, dimensions A-F | Gate 2 presentation |
| 2026-03-15 | Build complete — 9 tasks, 124 tests, 897 total suite green | Ship (Phase 7) |
