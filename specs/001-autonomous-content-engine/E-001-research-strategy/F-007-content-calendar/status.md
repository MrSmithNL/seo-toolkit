---
id: FTR-SEO-007
type: feature
title: "Content Calendar / Planning"
project: PROD-001
domain: seo.content-pipeline
parent: PROD-001-SPEC-E-001
status: draft
phase: 3-requirements
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
  completeness: pending
  build_approval: pending
---

# F-007: Content Calendar / Planning — Status

## Current State

Requirements complete. All user stories written with EARS acceptance criteria, NFR tables (35 categories), mandatory dimensions A-F, competitive context tags, and examples tables. Awaiting Gate 2 (Completeness Review).

## Phase Progress

- [x] Phase 1 — Understand
- [x] Phase 2 — Research
- [x] Gate 1 — Scope Approval
- [x] Phase 3 — Requirements
- [ ] Gate 2 — Completeness Review
- [ ] Phase 4 — Design
- [ ] Phase 5 — Tasks
- [ ] Gate 3 — Build Approval
- [ ] Phase 6 — Build
- [ ] Phase 7 — Ship
- [ ] Phase 8 — Retrospective

## Decisions Made

1. CLI-first modality for R1 (Gate 1 decision, 2026-03-15)

## Open Questions

- [ ] Should the Markdown review file include the full recommended heading list, or a summary? Proposed: full heading list (4-8 H2s per topic). At 10 topics, this is 40-80 headings — acceptable in a file; too much in a table. Confirm with Malcolm.
- [ ] Should approved-briefs.json be the direct E-002 input, or should there be a staging step? Proposed: direct input for R1 (E-002 reads approved-briefs.json). Staging step in R2+ when platform queuing (BullMQ) is added.
- [ ] What is the minimum calendar size to be useful? Proposed: minimum 3 approved briefs before E-002 is triggered. Single-brief batches waste E-002 LLM context setup overhead.
- [ ] Can Malcolm reject a topic and request a replacement from the pipeline? Proposed: R1 — rejected topics are noted but no auto-replacement. Re-run the pipeline to get fresh recommendations. R2+: rejection triggers replacement suggestion.

## UAT

N/A — Phase 3

## Retrospective

N/A — Phase 3

## Session Log

| Date | Summary | Next Step |
|------|---------|-----------|
| 2026-03-15 | Requirements complete — EARS criteria, NFR scan, competitive tags, dimensions A-F | Gate 2 presentation |
