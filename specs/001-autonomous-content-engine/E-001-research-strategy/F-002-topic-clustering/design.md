# F-002: Topic Clustering — Design

> Feature-level architecture for LLM-based semantic keyword clustering.
> Cross-cutting decisions (pipeline orchestration, tenant isolation, LLM-first vs embedding trade-off) are in `epic-design.md`.

---

## Architecture ADRs

### ADR-F002-001: Single-Pass LLM Clustering with Structured Output

**Status:** Proposed
**Context:** Need to group 50-500 keywords into semantic clusters. Epic ADR-E001-003 decided LLM-first for R1. This ADR decides the specific prompting and output strategy.
**Decision:** Send the full keyword list (up to 150 keywords) to the LLM in a single call with a JSON schema constraint. The prompt instructs the LLM to return a structured response with cluster assignments, pillar selection, coherence scores, and rationale. For sets >150 keywords, chunk into 150-keyword batches and merge clusters by name similarity post-hoc.
**Alternatives considered:**
1. Multi-pass (cluster, then score, then name) — 3x LLM calls, 3x cost, 3x latency. Single-pass with structured output is cheaper and the LLM handles all three tasks well in one context.
2. Hierarchical chunking (cluster 50, then merge) — Adds merge complexity. At 150 keywords, context window is not a constraint.
3. Embedding + DBSCAN — Deferred to R2 per epic decision. Requires pgvector infrastructure.
**Consequences:** Token budget ~50K per clustering run. Single point of failure — if the LLM call fails, retry once, then fall back to all-unclustered. Max 150 keywords per call keeps response quality high.

### ADR-F002-002: Cluster Identity and Stability

**Status:** Proposed
**Context:** Clusters need stable IDs so downstream features (F-007 content calendar) can reference them across pipeline re-runs. LLM output doesn't guarantee the same cluster names across runs.
**Decision:** Assign cluster IDs on first creation (`tc_<uuid>`). On subsequent runs, use the LLM's cluster name as a soft match key: if a new cluster name is >80% similar (Jaccard on words) to an existing cluster for the same campaign, reuse the existing cluster ID and update the name. Otherwise create a new cluster. Orphaned clusters (no keywords after re-run) are soft-deleted (`deleted_at` timestamp).
**Alternatives considered:**
1. Always create new clusters — Breaks downstream references. Content calendar entries would point to dead cluster IDs.
2. Deterministic naming (hash of pillar keyword) — Cluster composition changes across runs; hash-based ID would create false stability.
**Consequences:** Cluster IDs are stable across keyword refreshes. Name matching is approximate — edge cases where clusters split or merge will create new IDs, which is the correct behaviour.

### ADR-F002-003: Per-Language Independent Clustering

**Status:** Proposed
**Context:** Requirements specify clustering each language's keyword set independently (NFR 13). Need to decide whether to attempt cross-language cluster alignment.
**Decision:** Cluster each locale independently. No cross-language merging for R1. Each `keyword_cluster` record has a `locale` field. The content calendar (F-007) can display clusters side-by-side per locale but they are independent entities.
**Alternatives considered:**
1. Cross-language clustering (translate then cluster) — Adds LLM translation cost and complexity. Deferred to R2 per requirements.
2. Cluster in English, map back — Translation quality issues with niche terminology (e.g., medical hair terms in Turkish).
**Consequences:** A campaign with 3 locales produces 3 independent cluster sets. Simple, correct, and avoids translation artifacts.

---

## Data Model

### Drizzle Schema

```typescript
// modules/content-engine/research/schema/cluster.ts

import { pgTable, uuid, text, integer, real, timestamp, index, uniqueIndex } from 'drizzle-orm/pg-core';
import { keyword } from './keyword';

export const keywordCluster = pgTable('keyword_cluster', {
  id: text('id').primaryKey(),                     // tc_<uuid>
  tenantId: uuid('tenant_id').notNull(),
  campaignId: text('campaign_id').notNull(),
  locale: text('locale').notNull(),                // "de", "en", etc.
  name: text('name').notNull(),                    // LLM-generated cluster name
  rationale: text('rationale').notNull(),           // 1-2 sentence grouping rationale
  pillarKeywordId: text('pillar_keyword_id').references(() => keyword.id),
  pillarRationale: text('pillar_rationale'),        // why this keyword is the pillar
  keywordCount: integer('keyword_count').notNull().default(0),
  coherenceScore: real('coherence_score'),          // 1-10
  coherenceRationale: text('coherence_rationale'),  // 1 sentence
  noPillarFlag: text('no_pillar_flag'),             // "no suitable pillar — consider informational expansion"
  promptVersion: text('prompt_version').notNull(),  // e.g., "clustering-v1"
  llmTokensUsed: integer('llm_tokens_used'),
  deletedAt: timestamp('deleted_at'),              // soft delete for orphaned clusters
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  tenantIdx: index('tc_tenant_idx').on(table.tenantId),
  campaignLocaleIdx: index('tc_campaign_locale_idx').on(table.campaignId, table.locale),
  coherenceIdx: index('tc_coherence_idx').on(table.coherenceScore),
}));

// keyword.clusterId FK points to keywordCluster.id (defined in F-001 schema)
// "unclustered" keywords have clusterId = null
```

### Relationship to F-001 Schema

The `keyword.clusterId` field (defined in F-001's schema) is the FK to `keyword_cluster.id`. When clustering runs:
1. All keywords for the campaign+locale get their `clusterId` set (or set to null for unclustered).
2. `keywordCluster.keywordCount` is updated to reflect the count.
3. `keywordCluster.pillarKeywordId` points to the keyword with highest volume and broadest scope in the cluster.

### RLS

`keyword_cluster` gets tenant RLS per ADR-E001-004.

---

## API Contracts

### Commands (Writes)

```typescript
// ClusterKeywords — main entry point
interface ClusterKeywordsCommand {
  tenantId: string;
  campaignId: string;
  locale: string;
  options?: {
    minClusterSize?: number;            // default 3
    maxClusterSize?: number;            // default 20
    forceRecluster?: boolean;           // ignore existing clusters, start fresh
  };
}

interface ClusterKeywordsResult {
  clustersCreated: number;
  clustersUpdated: number;              // existing clusters that matched by name
  clustersOrphaned: number;             // soft-deleted (no keywords matched)
  unclusteredCount: number;
  avgCoherenceScore: number;
  llmTokensUsed: number;
  duration: number;                     // milliseconds
}
```

### Queries (Reads)

```typescript
interface GetClustersQuery {
  tenantId: string;
  campaignId: string;
  locale: string;
  filters?: {
    minCoherence?: number;              // filter low-quality clusters
    includeDeleted?: boolean;           // default false
  };
}

// Returns cluster with its keywords expanded
interface GetClusterDetailQuery {
  tenantId: string;
  clusterId: string;
  includeMetrics?: boolean;             // join keyword_metric for volume data
}

interface ClusterListItem {
  id: string;
  name: string;
  rationale: string;
  pillarKeyword: { id: string; term: string; volume: number } | null;
  keywordCount: number;
  coherenceScore: number;
  coherenceRationale: string;
  noPillarFlag: string | null;
}

interface ClusterDetail extends ClusterListItem {
  keywords: {
    id: string;
    term: string;
    volume: number | null;
    difficulty: number | null;
    intent: string | null;
    isVariant: boolean;                 // flagged as variant of another keyword
    variantOf: string | null;           // ID of primary keyword if variant
  }[];
}
```

### Events (Async Out)

```typescript
interface ClusteringCompletedEvent {
  type: 'research.clustering.completed';
  tenantId: string;
  campaignId: string;
  locale: string;
  clusterCount: number;
  avgCoherenceScore: number;
}
```

---

## LLM Prompt Architecture

### Prompt File

Stored at `prompts/clustering-v1.txt`. Contains:
1. System instruction: "You are a keyword clustering expert..."
2. Output JSON schema (enforced via structured output / tool use)
3. Clustering rules: min 3 / max 20 keywords per cluster, one pillar per cluster, coherence scoring rubric
4. Few-shot example: 10 keywords clustered into 2 groups with rationale

### Structured Output Schema

```typescript
// The LLM must return this exact structure
interface ClusteringLLMResponse {
  clusters: {
    name: string;                       // human-readable cluster name
    rationale: string;                  // 1-2 sentences: why these keywords belong together
    pillar_keyword: string;             // the keyword text (not ID) selected as pillar
    pillar_rationale: string;           // 1 sentence: why this is the pillar
    coherence_score: number;            // 1-10
    coherence_rationale: string;        // 1 sentence
    keywords: string[];                 // keyword texts assigned to this cluster
  }[];
  unclustered: string[];                // keywords that don't fit any cluster
}
```

### Token Budget

- Input: ~150 keywords x avg 5 tokens = 750 tokens + prompt (~2000 tokens) = ~2750 input tokens
- Output: ~15 clusters x ~200 tokens each = ~3000 output tokens
- Total per call: ~6000 tokens (well under 50K budget)
- Larger sets (500 keywords): chunk into 150-keyword batches, ~4 calls, ~24K tokens total

---

## Cluster Name Matching (Re-run Stability)

```typescript
// Jaccard similarity on word sets for cluster name matching
function clusterNameSimilarity(a: string, b: string): number {
  const wordsA = new Set(a.toLowerCase().split(/\s+/));
  const wordsB = new Set(b.toLowerCase().split(/\s+/));
  const intersection = new Set([...wordsA].filter(w => wordsB.has(w)));
  const union = new Set([...wordsA, ...wordsB]);
  return intersection.size / union.size;  // 0-1
}

// Match threshold: 0.8 (>80% word overlap = same cluster)
const CLUSTER_MATCH_THRESHOLD = 0.8;
```

---

## STRIDE-Lite

| Threat | Risk | Mitigation |
|--------|:----:|------------|
| **Prompt injection via keyword text** | M | Keywords are user-derived (from their own site), not arbitrary user input. Nonetheless, escape keywords in the prompt: wrap each in quotes, strip control characters. LLM structured output constrains response format. |
| **Data loss on re-clustering** | M | Soft-delete orphaned clusters (`deleted_at`). Never hard-delete. Downstream references (F-007 calendar entries) check for `deleted_at` and warn if their cluster was orphaned. |

---

## ATAM-Lite

| Decision | Quality Attribute | Trade-off |
|----------|------------------|-----------|
| Single-pass LLM (ADR-F002-001) | Latency + Cost vs Accuracy | One LLM call is faster and cheaper than three. Slight accuracy risk vs multi-pass refinement, but at <150 keywords the single-pass quality is high. |
| Cluster ID stability (ADR-F002-002) | Stability vs Simplicity | Adds name-matching logic on re-runs. Worth it — downstream features depend on stable cluster IDs. |
| Per-language independence (ADR-F002-003) | Simplicity vs Completeness | Misses cross-language topic alignment. Correct for R1 — cross-language merging is a R2 feature. |

---

## Build Boundaries

| Tier | Actions |
|------|---------|
| **Always** | Write clustering logic, implement prompt, write tests, update cluster schema, refactor within feature |
| **Ask** | Change prompt structure significantly (affects output quality), modify keyword schema (F-001 owns), add new LLM model option |
| **Never** | Skip coherence scoring (downstream depends on it), hard-delete clusters, use inline prompt strings (must be versioned files) |

---

## Test Architecture

### Test Pyramid

| Level | Count | What | Framework |
|-------|:-----:|------|-----------|
| Unit | ~15 | Cluster name matching, keyword-to-cluster assignment, coherence score validation, prompt construction, response parsing | Vitest |
| Integration | ~8 | Full clustering pipeline with mock LLM, database persistence, re-run stability, cluster update/orphan flow | Vitest + testcontainers |
| Property | ~4 | Every keyword appears in exactly one cluster or unclustered, cluster sizes within bounds, coherence scores in range | fast-check |
| E2E | 1 | Full F-001 -> F-002 pipeline with fixture data, verify cluster output matches schema | Vitest |

### Mocking Strategy

- **LLM (clustering)**: Mock AI gateway. Fixture in `__fixtures__/clustering-llm-response.json` — a realistic response for a 50-keyword Hairgenetix set producing 5 clusters.
- **Database**: Testcontainers for integration tests. Seed with F-001 keyword fixtures.
- **No external API mocks needed** — F-002 only calls the LLM, no external keyword APIs.

### Property Invariants

```
P1: for input keywords K and output clusters C:
    union(C.keywords, C.unclustered) === K           // no keyword lost or invented
P2: for all clusters c: c.keywords.length >= minSize  // respects min cluster size
P3: for all clusters c: c.keywords.length <= maxSize  // respects max cluster size
P4: for all clusters c: 1 <= c.coherenceScore <= 10   // valid range
P5: for all clusters c: c.pillarKeyword in c.keywords // pillar is a member
P6: no keyword appears in more than one cluster       // exclusive assignment
```

### Golden Test

50-keyword Hairgenetix DE fixture. Expected: 5-8 clusters, each with coherence >= 5, one pillar per cluster, no keyword omitted. The golden test uses a deterministic mock LLM response so it is reproducible.
