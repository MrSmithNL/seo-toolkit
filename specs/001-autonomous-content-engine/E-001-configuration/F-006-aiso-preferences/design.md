---
id: "FTR-CONFIG-006"
type: feature
title: "AISO Scoring Preferences"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 4-design
priority: could
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

# Feature Design — AISO Scoring Preferences (F-006)

> Slim feature design. See `../epic-design.md` for shared architecture (Drizzle schema, module boundary, coding guardrails, cross-cutting concerns).

---

## Architecture Overview

F-006 lets users configure which AISO (AI Search Optimisation) factors to prioritise, which schema types to implement, and which AI platforms to target. It wraps the agency's 36-factor AISO model into a user-facing configuration layer. The `use_recommended=true` default covers 80%+ of use cases.

```
src/modules/content-engine/config/
├── aiso-preferences/
│   ├── aiso-preferences.service.ts      ← CRUD + defaults + factor validation
│   ├── aiso-preferences.repository.ts   ← AISOPreferences persistence
│   ├── aiso-preferences.schema.ts       ← Zod input/output schemas
│   ├── aiso-factor-registry.ts          ← 36-factor model definition + grouping
│   └── __tests__/
│       ├── aiso-preferences.service.test.ts
│       └── aiso-factor-registry.test.ts
```

---

## Component Design

```typescript
// === Value Objects ===

interface AISOFactor {
  id: string;           // e.g., "schema_faq", "citation_authority"
  name: string;         // "FAQ Schema", "Citation Authority"
  category: AISOCategory;
  description: string;
  defaultWeight: number; // 0.0-1.0
}

type AISOCategory =
  | 'structured_data'    // Schema.org implementation
  | 'content_structure'  // Headings, lists, definitions
  | 'authority_signals'  // Citations, expertise markers
  | 'technical_seo'      // Performance, crawlability
  | 'ai_discoverability' // LLM-specific optimisations
  | 'user_experience';   // Engagement signals

type SchemaType =
  | 'Article' | 'FAQPage' | 'HowTo' | 'Product' | 'Review'
  | 'BreadcrumbList' | 'Organization' | 'WebPage' | 'VideoObject';

type AIPlatform = 'chatgpt' | 'gemini' | 'perplexity' | 'claude' | 'copilot';

// === Service ===

class AISOPreferencesService {
  constructor(
    private repo: AISOPreferencesRepository,
    private factorRegistry: AISOFactorRegistry,
  ) {}

  async getAISOPrefs(siteId: string): Promise<AISOPreferences>;
  async setAISOPrefs(siteId: string, params: SetAISOPrefsInput): Promise<AISOPreferences>;
  async getFactorsByCategory(): Promise<Record<AISOCategory, AISOFactor[]>>;
  async resetToRecommended(siteId: string): Promise<AISOPreferences>;
}

// === Factor Registry ===

class AISOFactorRegistry {
  private factors: Map<string, AISOFactor>;

  getAllFactors(): AISOFactor[];
  getByCategory(category: AISOCategory): AISOFactor[];
  getRecommended(): AISOFactor[];     // default subset for use_recommended=true
  validate(factorIds: string[]): ValidationResult;
}
```

---

## DDD Tactical Patterns

| Pattern | Element | Notes |
|---------|---------|-------|
| **Aggregate** | `AISOPreferences` | Child of `SiteConfig`, one-to-one. Config-only — no domain events |
| **Value object** | `AISOFactor` | Immutable factor definition from registry |
| **Value object** | `SchemaType` | Constrained enum of supported Schema.org types |
| **Value object** | `AIPlatform` | Constrained enum of target AI platforms |
| **Repository** | `AISOPreferencesRepository` | Upsert pattern, same as F-005 |

No domain events — this feature is pure configuration consumed by E-003 AISO scoring.

---

## Key Algorithms

### Factor Grouping (Display)

```
Group the 36 AISO factors into 6 categories for user-facing display:

structured_data (8 factors):
  - FAQ Schema, HowTo Schema, Product Schema, Review Schema,
    Breadcrumb Schema, Article Schema, Organization Schema, Video Schema

content_structure (7 factors):
  - Heading hierarchy, Definition paragraphs, Numbered lists,
    Comparison tables, Summary boxes, Key takeaway sections, Topic clustering

authority_signals (6 factors):
  - Citation authority, Expert attribution, Statistical evidence,
    Source diversity, Recency signals, E-E-A-T markers

technical_seo (5 factors):
  - Page speed, Mobile responsiveness, Canonical URLs,
    XML sitemap inclusion, Internal linking depth

ai_discoverability (6 factors):
  - Concise answer paragraphs, Question-answer format,
    Definitive statements, Entity mentions, Topic completeness,
    Natural language phrasing

user_experience (4 factors):
  - Readability score, Content freshness, Visual content ratio,
    Engagement structure (scannable layout)
```

### Defaults-First Logic

```
function resolveEffectiveFactors(prefs: AISOPreferences): AISOFactor[] {
  if (prefs.useRecommended) {
    // Return curated subset — the 20 highest-impact factors
    return factorRegistry.getRecommended();
  }

  // User has customised — use their selection
  return prefs.priorityFactors.map(id => factorRegistry.get(id));
}
```

---

## API Surface

R1 CLI functions:

| Function | Signature | Description |
|----------|-----------|-------------|
| `getAISOPrefs` | `(siteId) => Promise<AISOPreferences>` | Get current preferences (creates defaults if none exist) |
| `setAISOPrefs` | `(siteId, params) => Promise<AISOPreferences>` | Update preferences; setting `useRecommended=false` requires `priorityFactors` |

R2 HTTP routes:

| Method | Path | Handler |
|--------|------|---------|
| `PUT` | `/sites/:id/aiso` | `setAISOPrefs` |

---

## Integration Points

None. This feature is self-contained — pure CRUD with factor registry validation. The 36-factor model is defined in code, not fetched from an external source.

---

## Testing Strategy

| Category | What to Test | Approach |
|----------|-------------|----------|
| **Unit** | Factor registry completeness (36 factors, 6 categories) | Snapshot test |
| **Unit** | Factor grouping (every factor belongs to exactly one category) | Registry assertion |
| **Unit** | Validation (reject unknown factor IDs, accept valid ones) | Table-driven tests |
| **Unit** | Defaults-first logic (useRecommended=true vs custom) | Service tests |
| **Integration** | Upsert behaviour (create defaults, then customise) | In-memory SQLite |
| **Edge case** | Set useRecommended=false without priorityFactors | Expect validation error |
| **Edge case** | Empty priorityFactors array | Expect validation error |

---

## Feature-Specific Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | `use_recommended=true` as default | 80%+ of users should never need to customise AISO factors — reduces friction |
| 2 | Factor registry in code, not database | Factors are part of the scoring engine logic, not user data. Updated with code releases |
| 3 | No domain events | Config-only feature — E-003 reads preferences at scoring time |
| 4 | Factor IDs are stable strings | Allows preference persistence across factor registry updates (new factors added, descriptions changed) |
| 5 | 6-category grouping | Matches the AISO audit skill's structure for consistency across agency tooling |
