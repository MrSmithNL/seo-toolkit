---
id: "FTR-CONFIG-005"
type: feature
title: "Quality Threshold Settings"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 4-design
priority: should
created: 2026-03-13
last_updated: 2026-03-13
refs:
  requirements: "./requirements.md"

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

# Feature Design — Quality Threshold Settings (F-005)

> Slim feature design. See `../epic-design.md` for shared architecture (Drizzle schema, module boundary, coding guardrails, cross-cutting concerns).

---

## Architecture Overview

F-005 is the simplest feature in E-001 — it is a configuration CRUD for quality gates that E-003 (Scoring & QA) will consume. No external integrations, no complex algorithms. Sensible defaults mean most users never need to touch these settings.

```
src/modules/content-engine/config/
├── quality-thresholds/
│   ├── quality-thresholds.service.ts     ← CRUD + validation + defaults
│   ├── quality-thresholds.repository.ts  ← QualityThresholds persistence
│   ├── quality-thresholds.schema.ts      ← Zod input/output schemas
│   ├── default-thresholds.ts             ← sensible defaults per site type
│   └── __tests__/
│       ├── quality-thresholds.service.test.ts
│       └── default-thresholds.test.ts
```

---

## Component Design

```typescript
// === Value Objects ===

interface ScoreRange {
  min: number;
  max: number;
}

type ReadabilityGrade = 'grade_6' | 'grade_8' | 'grade_10' | 'grade_12' | 'college';

type PublishMode = 'draft_review' | 'auto_publish' | 'manual_only';

// === Service ===

class QualityThresholdsService {
  constructor(private repo: QualityThresholdsRepository) {}

  async getThresholds(siteId: string): Promise<QualityThresholds>;
  async setThresholds(siteId: string, params: SetThresholdsInput): Promise<QualityThresholds>;
  async resetToDefaults(siteId: string): Promise<QualityThresholds>;
}

// === Repository ===

interface QualityThresholdsRepository {
  findBySiteId(siteId: string): Promise<QualityThresholds | null>;
  upsert(siteId: string, data: ThresholdsData): Promise<QualityThresholds>;
}
```

---

## DDD Tactical Patterns

| Pattern | Element | Notes |
|---------|---------|-------|
| **Aggregate** | `QualityThresholds` | Child of `SiteConfig`, one-to-one. Config-only — no domain events |
| **Value object** | `ScoreRange` | Min/max pair with validation (min < max, within bounds) |
| **Value object** | `ReadabilityGrade` | Constrained enum of readability targets |
| **Value object** | `PublishMode` | Controls whether content auto-publishes or requires review |
| **Repository** | `QualityThresholdsRepository` | Upsert pattern — create with defaults if not exists |

No domain events — this feature is pure configuration consumed by E-003.

---

## Key Algorithms

### Default Threshold Calculation

```
function getDefaults(cmsType: string): ThresholdsData {
  const base = {
    seoScoreMin: 65,
    aisoScoreMin: 7.0,
    readabilityTarget: 'grade_8',
    wordCountMin: 1500,
    wordCountMax: 3000,
    publishMode: 'draft_review',
  };

  // Adjust based on CMS type
  if (cmsType === 'shopify') {
    // E-commerce: shorter content, simpler readability
    return { ...base, wordCountMin: 800, wordCountMax: 2000, readabilityTarget: 'grade_6' };
  }

  // WordPress blog: standard defaults
  return base;
}
```

### Input Validation Rules

```
- seoScoreMin: integer, 0-100
- aisoScoreMin: float, 0.0-10.0
- readabilityTarget: must be valid ReadabilityGrade enum value
- wordCountMin: integer, >= 300
- wordCountMax: integer, >= wordCountMin, <= 10000
- publishMode: must be valid PublishMode enum value
```

---

## API Surface

R1 CLI functions:

| Function | Signature | Description |
|----------|-----------|-------------|
| `getThresholds` | `(siteId) => Promise<QualityThresholds>` | Get current thresholds (creates defaults if none exist) |
| `setThresholds` | `(siteId, params) => Promise<QualityThresholds>` | Update one or more threshold values |

R2 HTTP routes:

| Method | Path | Handler |
|--------|------|---------|
| `PUT` | `/sites/:id/quality` | `setThresholds` |

---

## Integration Points

None. This feature is self-contained — pure CRUD with validation.

---

## Testing Strategy

| Category | What to Test | Approach |
|----------|-------------|----------|
| **Unit** | Default calculation per CMS type | Direct function tests |
| **Unit** | Validation rules (boundary values, invalid inputs) | Table-driven tests |
| **Unit** | Partial update (only change one field, others unchanged) | Service tests |
| **Integration** | Upsert behaviour (create on first call, update on subsequent) | In-memory SQLite |
| **Edge case** | wordCountMin > wordCountMax | Expect validation error |
| **Edge case** | Score values at boundaries (0, 100, 10.0) | Expect acceptance |

---

## Feature-Specific Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Defaults created at site registration time | User always has working thresholds without explicit configuration |
| 2 | CMS-aware defaults | Shopify (e-commerce) has different content norms than WordPress (blog) |
| 3 | `draft_review` as default publish mode | Safety first — no auto-publishing until user explicitly opts in |
| 4 | No domain events | Thresholds are static config, not state changes. E-003 reads them at scoring time |
