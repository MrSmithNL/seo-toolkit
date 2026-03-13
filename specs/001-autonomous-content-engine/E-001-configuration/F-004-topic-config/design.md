---
id: "FTR-CONFIG-004"
type: feature
title: "Topic/Niche Configuration"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 4-design
priority: must
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

# Feature Design — Topic/Niche Configuration (F-004)

> Slim feature design. See `../epic-design.md` for shared architecture (Drizzle schema, module boundary, coding guardrails, cross-cutting concerns).

---

## Architecture Overview

F-004 defines what topics the content engine writes about. It supports three input modes: auto-inference from existing site content, manual keyword entry, and Google Search Console import. Keywords are organised into clusters for topical authority building.

```
src/modules/content-engine/config/
├── topic-config/
│   ├── topic-config.service.ts          ← orchestrates topic configuration
│   ├── topic-config.repository.ts       ← TopicConfig + TopicCluster persistence
│   ├── topic-config.schema.ts           ← Zod input/output schemas
│   ├── topic-inferrer.ts                ← auto-extract topics from site content
│   ├── keyword-clusterer.ts             ← group keywords into semantic clusters
│   ├── gsc-importer.ts                  ← Google Search Console data import
│   └── __tests__/
│       ├── topic-config.service.test.ts
│       ├── topic-inferrer.test.ts
│       ├── keyword-clusterer.test.ts
│       └── gsc-importer.test.ts
```

---

## Component Design

```typescript
// === Value Objects ===

interface Keyword {
  term: string;
  volume?: number;   // from GSC or estimation
  position?: number; // current ranking position from GSC
}

type ClusterPriority = 'high' | 'medium' | 'low';

interface TopicCluster {
  name: string;
  keywords: Keyword[];
  priority: ClusterPriority;
  contentCount: number; // existing content targeting this cluster
}

// === Service ===

class TopicConfigService {
  constructor(
    private repo: TopicConfigRepository,
    private inferrer: TopicInferrer,
    private clusterer: KeywordClusterer,
    private gscImporter: GSCImporter,
    private eventEmitter: EventEmitter,
  ) {}

  async inferTopics(siteId: string): Promise<TopicConfig>;
  async setTopics(siteId: string, keywords: string[]): Promise<TopicConfig>;
  async importFromGSC(siteId: string, gscCredentials: GSCCredentials): Promise<TopicConfig>;
  async getTopics(siteId: string): Promise<TopicConfig | null>;
  async updateClusterPriority(clusterId: string, priority: ClusterPriority): Promise<TopicCluster>;
}

// === Topic Inferrer ===

class TopicInferrer {
  constructor(
    private contentFetcher: ContentFetcher,
    private llmClient: LLMClient,
  ) {}

  async infer(siteUrl: string, pageUrls: string[]): Promise<string[]>;
}

// === Keyword Clusterer ===

class KeywordClusterer {
  constructor(private llmClient: LLMClient) {}

  async cluster(keywords: string[]): Promise<TopicCluster[]>;
}
```

---

## DDD Tactical Patterns

| Pattern | Element | Notes |
|---------|---------|-------|
| **Aggregate** | `TopicConfig` | Child of `SiteConfig`, contains `TopicCluster` children |
| **Entity** | `TopicCluster` | Has identity (id), belongs to TopicConfig |
| **Value object** | `Keyword` | Term + optional volume/position data |
| **Value object** | `ClusterPriority` | Enum — drives content generation ordering |
| **Domain event** | `topics.configured` | `{ siteId, clusterCount, keywordCount }` — triggers E-002 Research |
| **Repository** | `TopicConfigRepository` | Manages TopicConfig + nested TopicCluster records |

---

## Key Algorithms

### Auto-Infer Topics from Site Content

```
1. Fetch sitemap.xml (or crawl homepage links if no sitemap)
2. Select up to 10 representative pages (homepage + top-level pages)
3. For each page:
   a. Fetch and clean HTML (reuse ContentFetcher from F-003)
   b. Extract: page title, h1-h3 headings, meta description
4. Send aggregated page data to LLM:
   - Prompt: "Given these page titles, headings, and descriptions from {url},
             identify the 5-15 core topics/keywords this site covers.
             Return as JSON array of strings."
5. Parse and deduplicate LLM response
6. Pass keywords to clustering algorithm
```

### Keyword Clustering

```
1. If keyword count ≤ 5 → single cluster named "Primary Topics"
2. If keyword count > 5:
   a. Send keywords to LLM:
      - Prompt: "Group these keywords into 2-7 semantic clusters.
                Each cluster should represent a distinct topic area.
                Return JSON: [{ name: string, keywords: string[] }]"
   b. Parse response
   c. Assign default priority: first cluster = "high", rest = "medium"
3. Validate: every input keyword appears in exactly one cluster
```

### GSC Import

```
1. Authenticate with Google Search Console API (OAuth2 service account)
2. Query: searchAnalytics.query for last 90 days
   - Dimensions: query
   - Metrics: clicks, impressions, position
   - Row limit: 500
3. Filter: remove branded queries (contain site name/brand)
4. Sort by impressions descending
5. Take top 50 queries as seed keywords
6. Pass to keyword clustering algorithm
7. Enrich clusters with volume (impressions) and position data
```

---

## API Surface

R1 CLI functions:

| Function | Signature | Description |
|----------|-----------|-------------|
| `inferTopics` | `(siteId) => Promise<TopicConfig>` | Auto-extract from site content |
| `setTopics` | `(siteId, keywords: string[]) => Promise<TopicConfig>` | Manual keyword entry + auto-clustering |
| `importFromGSC` | `(siteId, gscCredentials) => Promise<TopicConfig>` | Import from Search Console |

R2 HTTP routes:

| Method | Path | Handler |
|--------|------|---------|
| `PUT` | `/sites/:id/topics` | `configureTopics` |

---

## Integration Points

| External System | Protocol | Purpose | Timeout | Retry |
|----------------|----------|---------|---------|-------|
| Target site (pages) | HTTP GET | Content fetching for topic inference | 10s per page | No retry |
| Target site (sitemap) | HTTP GET | Page discovery | 10s | No retry |
| LLM API (Claude/GPT) | HTTPS | Topic inference + keyword clustering | 30s | 1 retry |
| Google Search Console API | HTTPS (OAuth2) | Query performance data import | 15s | 1 retry |

---

## Testing Strategy

| Category | What to Test | Approach |
|----------|-------------|----------|
| **Unit** | Topic inferrer (various site structures, empty sites) | Mock HTTP + LLM responses |
| **Unit** | Keyword clusterer (small set, large set, single topic) | Mock LLM responses |
| **Unit** | GSC importer (data parsing, branded query filtering) | Mock GSC API responses |
| **Integration** | Full inference flow (fetch → infer → cluster → persist) | In-memory SQLite + mocks |
| **Edge case** | Site with no content (empty sitemap, no pages) | Expect empty config or error |
| **Edge case** | GSC returns no data (new site) | Expect graceful fallback |

---

## Feature-Specific Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | LLM for clustering (not embedding-based) | Simpler for R1, no vector database needed. Embeddings can be added in R2 |
| 2 | Max 50 keywords from GSC | Enough for meaningful clusters without overwhelming the system |
| 3 | Auto-filter branded queries from GSC | Branded terms don't need content targeting — they already rank |
| 4 | Three input modes (auto, manual, GSC) | Different users have different data available; all paths lead to same cluster structure |
| 5 | Default priority assignment | High for first cluster reduces user friction; they can adjust manually |
