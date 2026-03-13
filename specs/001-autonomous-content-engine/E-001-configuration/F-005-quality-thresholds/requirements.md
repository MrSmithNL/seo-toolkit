---
id: "FTR-CONFIG-005"
type: feature
title: "Quality Threshold Settings"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 3-requirements
priority: should
created: 2026-03-13
last_updated: 2026-03-13

# === PARENT ALIGNMENT ===
parent_baseline:
  id: "EPC-CONFIG-001"
  version: null
  hash: null
  status: aligned

# === ARCHITECTURE CLASSIFICATION (Gate 0) ===
saas_ecosystem: true
hierarchy_level: L3-module
hierarchy_location: "modules/content-engine/"
capability_group: "seo"
module_manifest: required
tenant_aware: true

# === TRACEABILITY ===
traces_to:
  product_goal: "PROD-001: SEO Toolkit capability engine"
  theme: "specs/001-autonomous-content-engine/theme.md"
  epic: "E-001 Configuration & Setup"
  capability: "CAP-CE-001 — Site & Pipeline Configuration"
---

# Quality Threshold Settings — Requirements

## Problem Statement

Without configurable quality gates, the content pipeline either publishes everything (risking low-quality content damaging the site) or requires manual review of every article (defeating autonomous operation). Quality thresholds let the operator define "good enough" once, and the pipeline enforces it automatically. No competitor offers user-configurable quality thresholds — this is a differentiator.

## Research Summary

### Competitor Analysis

| Capability | Surfer SEO | Clearscope | SEO.ai | Frase | Our Approach |
|-----------|:----------:|:----------:|:------:|:-----:|:------------:|
| SEO content score | ✅ (0-100) | ✅ (F-A++) | ❌ | ❌ | ✅ (0-100) |
| User-configurable threshold | ⚠️ (recommendation) | ❌ | ❌ | ❌ | ✅ |
| Readability target | ❌ | ❌ | ❌ | ❌ | ✅ |
| Word count range | ❌ | ❌ | ❌ | ❌ | ✅ |
| Publish mode gate | ❌ | ❌ | ✅ (3 modes) | ❌ | ✅ |
| AISO score threshold | ❌ | ❌ | ❌ | ❌ | ✅ |

### Key Findings

- No competitor offers all 5 quality settings as configurable user thresholds
- SEO.ai's 3-mode publish pattern (auto/draft/review) is the closest quality gate concept
- Surfer's score is a recommendation, not a hard gate — ours will be a hard gate (fail = don't publish)
- Sensible defaults are critical — most users won't customise, but power users want control

### Sources

- `research/e001-configuration-setup-patterns.md` §4 (Quality Configuration)
- `E-001-configuration/research/phase2-analysis.md` §Spec-as-Context for F-005

## Impact Map

```
Goal: Ensure only quality content reaches the CMS
  +-- Actor: Agency operator (Malcolm) / Future SaaS user
       +-- Impact: Can trust the pipeline output without reviewing every article
            +-- Deliverable: SEO score minimum threshold
            +-- Deliverable: AISO score minimum threshold
            +-- Deliverable: Readability target
            +-- Deliverable: Word count range
            +-- Deliverable: Publish mode setting
```

## Domain Model

```
QualityThresholds {
  id: UUID
  site_id: UUID (FK -> SiteConfig.id)

  seo_score_min: int (0-100) [default: 65]
  aiso_score_min: float (0.0-10.0) [default: 7.0]
  readability_target: enum (grade_6, grade_8, grade_10, grade_12) [default: grade_8]
  word_count_min: int [default: 1500]
  word_count_max: int [default: 3000]
  publish_mode: enum (auto_publish, draft_review, manual_only) [default: draft_review]

  created_at: timestamp
  updated_at: timestamp
}
```

## User Stories

### US-001: Set quality thresholds with sensible defaults

**As a** content pipeline operator, **I want** quality thresholds pre-filled with sensible defaults, **so that** I can start generating content immediately or customise only the settings I care about.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN a site is first configured
THE SYSTEM SHALL create QualityThresholds with all defaults: SEO score 65, AISO score 7.0, readability Grade 8, word count 1500-3000, publish mode draft_review

WHEN the user modifies any threshold
THE SYSTEM SHALL update only the changed value and preserve others

**Examples:**

| Scenario | Action | Expected State |
|----------|--------|---------------|
| Fresh site, no changes | Site configured | All defaults applied: 65/7.0/Grade 8/1500-3000/draft |
| Raise SEO bar | Set seo_score_min to 80 | 80/7.0/Grade 8/1500-3000/draft |
| Lower word count | Set word_count_min to 800 | 65/7.0/Grade 8/800-3000/draft |
| Auto-publish mode | Set publish_mode to auto_publish | 65/7.0/Grade 8/1500-3000/auto_publish |

### US-002: Quality gate enforcement in pipeline

**As a** content pipeline operator, **I want** articles that fail quality thresholds to be held for review, **so that** low-quality content never reaches the live site.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

WHEN an article is scored by E-003 (Generation)
THE SYSTEM SHALL compare the article's scores against the configured thresholds
AND if ALL thresholds are met, proceed according to publish_mode
AND if ANY threshold fails, hold the article for manual review regardless of publish_mode

WHEN an article is held for review
THE SYSTEM SHALL report which specific thresholds failed and by how much

**Examples:**

| Scenario | Article Scores | Thresholds | Expected Action |
|----------|---------------|-----------|-----------------|
| All pass, auto mode | SEO: 78, AISO: 8.2, words: 2100 | 65/7.0/1500-3000/auto | Published automatically |
| All pass, draft mode | SEO: 78, AISO: 8.2, words: 2100 | 65/7.0/1500-3000/draft | Created as draft |
| SEO fails | SEO: 52, AISO: 8.2, words: 2100 | 65/7.0/1500-3000/auto | HELD: "SEO score 52 < minimum 65" |
| Multiple fail | SEO: 52, AISO: 5.1, words: 900 | 65/7.0/1500-3000/auto | HELD: "SEO 52<65, AISO 5.1<7.0, Words 900<1500" |

### US-003: Set publish mode

**As a** content pipeline operator, **I want** to choose how articles are published, **so that** I can control whether content goes live automatically or requires review.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN publish mode is "auto_publish"
THE SYSTEM SHALL publish articles that pass all quality thresholds directly to the CMS
AND warn at config time: "Articles will be published live without human review"

WHEN publish mode is "draft_review"
THE SYSTEM SHALL create articles as drafts in the CMS for human review

WHEN publish mode is "manual_only"
THE SYSTEM SHALL generate articles but NOT push to CMS — store locally for manual upload

**Examples:**

| Mode | Pass Quality? | Expected Action |
|------|:------------:|-----------------|
| auto_publish | Yes | Published live on CMS |
| auto_publish | No | Held for review (quality gate overrides mode) |
| draft_review | Yes | Created as CMS draft |
| draft_review | No | Held for review |
| manual_only | Yes | Stored locally, not pushed |
| manual_only | No | Held for review |

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN checking quality thresholds THE SYSTEM SHALL evaluate all thresholds WITHIN 1 second | p95 < 1s | Unit test | Yes |
| 2 | **Security** | N/A — quality thresholds contain no sensitive data | — | — | No |
| 3 | **Reliability** | WHEN quality threshold evaluation fails THE SYSTEM SHALL default to HOLD (never auto-publish on evaluation error) | Fail-safe to hold | Integration test with broken scorer | Yes |
| 4 | **Scalability** | N/A — single-user system | — | — | No |
| 5 | **Availability** | N/A — not a hosted service | — | — | No |
| 6 | **Maintainability** | WHEN a new quality metric is added THE SYSTEM SHALL support it by adding a threshold field without modifying existing logic | Extensible threshold model | Architecture review | No |
| 7-8 | **Portability/Accessibility** | N/A | — | — | No |
| 9 | **Usability** | WHEN configuring thresholds THE SYSTEM SHALL show the current default alongside each setting | Default visible | Manual verification | No |
| 10-11 | **Interop/Compliance** | N/A | — | — | No |
| 12 | **Data Retention** | WHEN a site is deleted THE SYSTEM SHALL delete associated quality thresholds | Cascade delete | Integration test | Yes |
| 13-16 | **Backup/Logging/Cost/Capacity** | Logging: WHEN quality gate triggers THE SYSTEM SHALL log article ID, all scores vs thresholds, and gate decision | Structured log | Log assertion | Yes |
| 17-18 | **i18n/Extensibility** | N/A | — | — | No |
| 19 | **Operation Pattern** | WHEN any command or query is executed THE SYSTEM SHALL follow the 5-step Operation pattern (P-008): Zod input → OperationContext → business logic → persist → emit event + return Result<T, OperationError> | All operations return Result type | Architecture fitness test FF-030 | Yes |
| 20 | **Error Handling** | WHEN a quality threshold operation fails THE SYSTEM SHALL return an OperationError (not throw) with RFC 7807-compatible error codes and `suggested_action` field | Zero naked `throw` in commands/queries | FF-032 + code review | Yes |
| 21 | **Structured Logging** | WHEN any quality threshold operation executes THE SYSTEM SHALL emit `operation.started`, `operation.completed`, and `operation.failed` structured JSON events via pino with correlationId + tenantId | 3 log events per operation | Log assertion in integration test | Yes |
| 22 | **Tenant Isolation** | WHEN querying quality threshold data THE SYSTEM SHALL enforce RLS so Tenant A cannot read/update/delete Tenant B's quality thresholds. Cross-tenant access returns 404 (not 403). | `tenant-isolation.test.ts` passes | Integration test (FF-034) | Yes |
| 23 | **Idempotency** | WHEN creating quality thresholds THE SYSTEM SHALL accept an optional idempotencyKey. Duplicate requests with the same key return the original result without creating duplicates. | Duplicate request = same response | Integration test | Yes |
| 24 | **Serialisable I/O** | WHEN returning quality threshold data from any operation THE SYSTEM SHALL use ISO 8601 strings for dates (never Date objects), plain objects only (no class instances) | JSON.parse(JSON.stringify(output)) === output | Unit test | Yes |
| 25 | **Contract Completeness** | WHEN exposing quality threshold commands or queries THE SYSTEM SHALL have a Zod input schema AND explicit TypeScript return type for each | Every public function has Zod + return type | FF-029 | Yes |
| 26 | **No Module State** | THE SYSTEM SHALL NOT use `let` or `var` at module scope in quality threshold `src/` files (except type exports and `const`) | Zero mutable module-level state | FF-033 | Yes |
| 27 | **PII Redaction** | WHEN logging quality threshold data THE SYSTEM SHALL redact any email, phone, IP address, or personal data fields using pino's redaction config | PII fields show `[REDACTED]` in logs | Log inspection test | Yes |
| 28 | **Prefixed IDs** | WHEN creating a QualityThresholds record THE SYSTEM SHALL generate IDs with `qty_` prefix using NanoID or UUID v7 | All IDs match `qty_*` pattern | Unit test | Yes |

## Out of Scope

- Content scoring logic (SEO scoring, AISO scoring, readability calculation) — that's E-003
- Article rewriting loop when quality fails — E-003
- Per-article threshold overrides — V2
- A/B testing of different threshold levels — V2

## Open Questions

- [x] Should failed articles be auto-rewritten or just held? **Answer:** Held for V1. Auto-rewrite loop is E-003 scope.
- [x] Should readability use Flesch-Kincaid or another metric? **Answer:** Flesch-Kincaid Grade Level for V1 (most widely understood).

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| E-003 (Generation) scoring | Internal (downstream) | Not started | Quality gate enforcement reads thresholds at E-003 scoring time |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | Default thresholds (SEO 65, AISO 7.0) are achievable for most content | Medium | Test with generated articles — do >80% pass defaults? |
| A2 | Users want hard gates (fail = don't publish) not soft warnings | Medium | Validate with Malcolm's usage patterns |
| A3 | Readability at Grade 8 is appropriate for most content types | High | Industry standard for web content |
