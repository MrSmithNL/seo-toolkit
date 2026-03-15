# F-002: Topic Clustering — Tasks

## Task T-001: Cluster Schema & Migration [Foundation]
**Story:** US-001 (Semantic Keyword Clustering)
**Size:** S
**Depends on:** F-001 T-001 (keyword schema must exist first)
**Parallel:** Yes [P]

### What
Create the Drizzle schema for the `keyword_cluster` table as defined in design.md. Include all fields: name, rationale, pillar FK, coherence score, prompt version, soft-delete timestamp. Generate Zod validation schemas. Write the migration with RLS policy. Wire the `keyword.clusterId` FK to `keyword_cluster.id`.

### Files
- Create: `modules/content-engine/research/schema/cluster.ts`
- Create: `modules/content-engine/research/contracts/topic-cluster.ts`
- Create: `modules/content-engine/research/migrations/0002_cluster_table.sql`
- Create (tests): `modules/content-engine/research/schema/__tests__/cluster.schema.test.ts`
- Read (context): `modules/content-engine/research/schema/keyword.ts` (FK relationship)

### Test Scenarios (from tests.md)
- PI-004: Coherence score range 1-10
- PI-005: Pillar per cluster (FK valid)
- PI-006: Rationale non-empty
- PI-009: Cluster name non-empty

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `keyword_cluster` table with all columns per design.md
- [ ] RLS policy applied in migration
- [ ] `keyword.clusterId` FK relationship defined
- [ ] Zod `TopicCluster` schema exported for F-007 consumption
- [ ] Soft delete via `deleted_at` column (not hard delete)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write schema code, run tests, validate RLS
- Ask: modify keyword table columns (F-001 owns)
- Never: skip RLS, hard-delete clusters

---

## Task T-002: Cluster Name Matching (Re-run Stability) [Domain Logic]
**Story:** US-001 (Semantic Keyword Clustering)
**Size:** S
**Depends on:** T-001
**Parallel:** Yes [P]

### What
Implement the Jaccard word-set similarity function for matching cluster names across pipeline re-runs per ADR-F002-002. Given a new LLM-generated cluster name, find existing clusters with >80% word overlap and reuse their IDs. Orphaned clusters (no matching keywords after re-run) get soft-deleted.

### Files
- Create: `modules/content-engine/research/domain/cluster-matcher.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/cluster-matcher.test.ts`

### Test Scenarios (from tests.md)
- INT-001: Re-run produces stable cluster IDs for matching names
- Design ADR-F002-002: >80% Jaccard threshold reuses ID

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `clusterNameSimilarity(a, b)` returns 0-1 Jaccard score
- [ ] Threshold constant `CLUSTER_MATCH_THRESHOLD = 0.8` is configurable
- [ ] Matched clusters keep existing ID; unmatched get new `tc_<uuid>` ID
- [ ] Orphaned clusters soft-deleted (`deleted_at` set)
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change threshold value (affects downstream stability)
- Never: hard-delete clusters, bypass soft-delete

---

## Task T-003: Clustering LLM Prompt & Response Parser [Domain Logic]
**Story:** US-001, US-002, US-003 (Clustering, Pillar, Scoring)
**Size:** M
**Depends on:** —
**Parallel:** Yes [P]

### What
Create the versioned clustering prompt (`prompts/clustering-v1.txt`) and the response parser that validates the LLM structured output. The prompt instructs the LLM to cluster keywords, select pillars, assign coherence scores, and provide rationale — all in a single pass per ADR-F002-001. The parser validates completeness (every keyword in exactly one cluster or unclustered), enum values, and score ranges.

### Files
- Create: `modules/content-engine/research/prompts/clustering-v1.txt`
- Create: `modules/content-engine/research/domain/clustering-prompt-builder.ts`
- Create: `modules/content-engine/research/domain/clustering-response-parser.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/clustering-prompt-builder.test.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/clustering-response-parser.test.ts`
- Create: `modules/content-engine/research/__fixtures__/clustering-llm-response.json`

### Test Scenarios (from tests.md)
- PI-001: Complete keyword coverage (no keyword lost or invented)
- PI-002: No duplicate keywords across clusters
- PI-003: Cluster size bounds (min 3, max 20)
- PI-004: Coherence score range 1-10
- PI-005: Pillar keyword is a member of its cluster

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Prompt stored in versioned file (not inline string)
- [ ] Prompt includes system instruction, JSON schema, clustering rules, few-shot example
- [ ] Parser validates: completeness, size bounds, score range, pillar membership
- [ ] Keywords escaped in prompt (control chars stripped, quoted)
- [ ] Invalid LLM response triggers retry signal
- [ ] Fixture covers 50-keyword Hairgenetix DE set with 5 clusters
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, version prompts
- Ask: change prompt structure significantly, add new output fields
- Never: use inline prompt strings, skip response validation

---

## Task T-004: Pillar Selection Logic [Domain Logic]
**Story:** US-002 (Pillar Page Identification)
**Size:** S
**Depends on:** T-003
**Parallel:** Yes [P]

### What
Implement the pillar keyword selection rules that validate and post-process the LLM's pillar choice. Confirm the pillar is the highest-volume keyword with broadest intent scope. Detect all-transactional clusters and flag them as "no suitable pillar — consider informational expansion". Handle volume ties by selecting the broader-intent keyword.

### Files
- Create: `modules/content-engine/research/domain/pillar-selector.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/pillar-selector.test.ts`

### Test Scenarios (from tests.md)
- ATS-008: Clear pillar — highest volume, broadest scope
- ATS-009: All transactional cluster — flagged, provisional pillar returned
- ATS-010: Volume tie broken by intent scope

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Pillar validated as highest-volume broad-scope keyword
- [ ] All-transactional clusters flagged with `noPillarFlag` text
- [ ] Tie-breaking by intent breadth implemented
- [ ] Selection rationale generated for every cluster
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change pillar selection criteria
- Never: skip pillar identification for any cluster

---

## Task T-005: Coherence Scoring Validation [Domain Logic]
**Story:** US-003 (Cluster Quality Scoring)
**Size:** S
**Depends on:** T-003
**Parallel:** Yes [P]

### What
Implement post-processing validation for LLM-generated coherence scores. Validate scores are in 1-10 range. Apply the low-coherence warning flag (score < 4) for downstream consumption by F-007. Ensure every score has a non-empty explanation string.

### Files
- Create: `modules/content-engine/research/domain/coherence-scorer.ts`
- Create (tests): `modules/content-engine/research/domain/__tests__/coherence-scorer.test.ts`

### Test Scenarios (from tests.md)
- ATS-011: Tight cluster scores 8-10
- ATS-012: Loose cluster scores 1-4
- ATS-013: Low coherence warning for F-007
- ATS-014: Coherence score as sort/filter field
- PI-010: Score explanation present

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Scores validated in 1-10 range
- [ ] Low-coherence warning text added when score < 4
- [ ] Explanation string required (empty = validation error)
- [ ] Scores usable as sort/filter field in query results
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change scoring rubric or threshold
- Never: skip coherence scoring (F-007 depends on it)

---

## Task T-006: Cluster Storage Adapter [Integration]
**Story:** US-001 (Semantic Keyword Clustering)
**Size:** S
**Depends on:** T-001, F-001 T-002 (storage port)
**Parallel:** Yes [P]

### What
Extend the storage port pattern with cluster-specific persistence: save new clusters, update matched clusters (re-run), soft-delete orphans, and update `keyword.clusterId` FK for all assigned keywords. Support both database and JSON standalone modes. JSON mode writes to `data/clusters/{domain}.json`.

### Files
- Create: `modules/content-engine/research/adapters/cluster-storage.adapter.ts`
- Create (tests): `modules/content-engine/research/adapters/__tests__/cluster-storage.adapter.test.ts`
- Read (context): `modules/content-engine/research/ports/keyword-storage.port.ts`

### Test Scenarios (from tests.md)
- INT-005: Standalone JSON output validates against TopicCluster schema
- Design ADR-F002-002: Orphaned clusters soft-deleted

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Save, update, soft-delete operations implemented
- [ ] `keyword.clusterId` updated for all assigned keywords
- [ ] JSON adapter writes valid file at `data/clusters/{domain}.json`
- [ ] Both adapters produce identical query results
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: change storage port interface
- Never: hard-delete clusters, bypass RLS

---

## Task T-007: Clustering Pipeline Command [Integration]
**Story:** All user stories
**Size:** M
**Depends on:** T-002, T-003, T-004, T-005, T-006
**Parallel:** No

### What
Implement the `ClusterKeywords` command handler that orchestrates the full F-002 pipeline: load keywords for campaign+locale → build prompt → call LLM → parse response → validate → match existing clusters → persist → update keyword FKs → emit event. Handles >150 keyword sets by chunking into 150-keyword batches and merging by cluster name post-hoc. Supports `forceRecluster` and custom size params.

### Files
- Create: `modules/content-engine/research/commands/cluster-keywords.ts`
- Create (tests): `modules/content-engine/research/commands/__tests__/cluster-keywords.test.ts`
- Modify: `modules/content-engine/research/index.ts` (export command)
- Read (context): `design.md` (API contracts, event schema)

### Test Scenarios (from tests.md)
- ATS-001: Happy path — 150 keywords produce 8-15 clusters
- ATS-006: Performance — completes within 60 seconds, < 50K tokens
- ATS-007: LLM failure — graceful degradation to all-unclustered
- INT-004: Per-language independent clustering
- INT-006: Custom cluster size parameters applied

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] Full pipeline: load → prompt → LLM → parse → validate → match → persist → event
- [ ] `ClusterKeywordsResult` returned with counts, coherence avg, tokens, duration
- [ ] `ClusteringCompletedEvent` emitted on success
- [ ] Chunking for >150 keywords with post-hoc merge
- [ ] `forceRecluster` bypasses existing cluster matching
- [ ] `--min-cluster-size` and `--max-cluster-size` params respected
- [ ] Feature flag `FEATURE_TOPIC_CLUSTERING` checked at entry
- [ ] Structured JSON logging: cluster count, sizes, scores, tokens, duration
- [ ] LLM retry once on failure, then graceful degradation
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests, update specs
- Ask: add dependency, change event schema
- Never: skip tests, bypass feature flag, use inline prompts

---

## Task T-008: Cluster Queries [Integration]
**Story:** US-003 (for downstream F-007)
**Size:** S
**Depends on:** T-006
**Parallel:** Yes [P]

### What
Implement the `GetClusters` and `GetClusterDetail` query handlers. Support filtering by minimum coherence score and include/exclude deleted clusters. `GetClusterDetail` returns the cluster with all its keywords expanded (including volume and intent data via JOIN).

### Files
- Create: `modules/content-engine/research/queries/get-clusters.ts`
- Create: `modules/content-engine/research/queries/get-cluster-detail.ts`
- Create (tests): `modules/content-engine/research/queries/__tests__/get-clusters.test.ts`
- Create (tests): `modules/content-engine/research/queries/__tests__/get-cluster-detail.test.ts`

### Test Scenarios (from tests.md)
- ATS-014: Clusters sortable/filterable by coherence score
- INT-002: F-002 output consumable by F-007

### Done When
- [ ] TDD: tests written first, implementation passes, refactor done
- [ ] `GetClusters` returns `ClusterListItem[]` with coherence, pillar, counts
- [ ] `GetClusterDetail` returns full keyword list with volume and intent
- [ ] `minCoherence` filter works correctly
- [ ] Deleted clusters excluded by default, includable via flag
- [ ] Tests pass
- [ ] No regression

### Boundaries
- Always: write code, run tests
- Ask: add new query fields
- Never: return clusters from other tenants (RLS enforced)
