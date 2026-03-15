---
id: "FTR-SEO-002"
title: "Test Plan: Topic Clustering"
parent: "E-001"
phase: "3-requirements"
metrics:
  total_scenarios: 34
  implemented: 0
  coverage_pct: null
  mutation_score_pct: null
  oracle_gap: null
  assertion_density: null
  integration_test_count: 0
  regression_escapes: 0
  drift_incidents: 0
---

# F-002: Topic Clustering — Test Plan

## 1. Acceptance Test Scenarios (Phase 3)

### US-001: Semantic Keyword Clustering

**ATS-001: Happy path — standard clustering**

```
GIVEN F-001 has produced 150 keywords for hairgenetix.com in DE
WHEN clustering runs
THEN 8-15 clusters are produced
AND each cluster contains between 3 and 20 keywords
AND unclustered set contains <= 15 keywords
AND each cluster includes a grouping rationale (1-2 sentences)
```

**ATS-002: Tight semantic group**

```
GIVEN keywords ["FUE hair transplant", "FUE procedure", "FUE vs FUT", "FUE recovery time", "FUE cost Germany"]
WHEN clustering runs
THEN all 5 keywords are placed in one cluster named approximately "FUE Hair Transplant"
AND rationale explains: "All keywords relate to the FUE surgical technique"
```

**ATS-003: Loose keyword placed in unclustered**

```
GIVEN a keyword "celebrity hair transplant" with no related keywords in the set
WHEN clustering runs
THEN the keyword is placed in the "unclustered" set
AND is NOT forced into an unrelated cluster
```

**ATS-004: Variant detection**

```
GIVEN keywords ["hair transplant cost", "cost of hair transplant", "hair transplant price"]
WHEN clustering runs
THEN all three are in the same cluster
AND "hair transplant cost" is flagged as the primary keyword (highest volume)
AND the others are flagged as "variants"
```

**ATS-005: Very small keyword set**

```
GIVEN only 10 keywords
WHEN clustering runs
THEN 2-4 clusters are produced
AND all keywords are placed (no unclustered unless genuinely unrelated)
```

**ATS-006: Performance — 150 keywords within 60 seconds**

```
GIVEN 150 keywords
WHEN clustering runs
THEN the operation completes within 60 seconds
AND consumes fewer than 50,000 LLM tokens
```

**ATS-007: LLM failure with graceful degradation**

```
GIVEN the LLM call for clustering fails on the first attempt
WHEN the system retries once
AND the retry also fails
THEN all keywords are returned in the "unclustered" set
AND no pipeline halt occurs
AND the result is flagged: "clustering failed — all keywords unclustered"
```

### US-002: Pillar Page Identification

**ATS-008: Clear pillar — highest volume broadest scope**

```
GIVEN a cluster with keywords: "hair transplant" (vol: 8100), "hair transplant Germany" (vol: 2400), "hair transplant before after" (vol: 1300)
WHEN pillar identification runs
THEN "hair transplant" is selected as the pillar candidate
AND rationale: "Highest volume, broadest scope — covers the topic at the category level"
```

**ATS-009: All transactional cluster — no suitable pillar**

```
GIVEN a cluster with only transactional keywords: ["buy hair growth serum", "hair growth serum price", "order hair growth serum online"]
WHEN pillar identification runs
THEN the cluster is flagged: "no suitable pillar — consider informational expansion"
AND the highest-volume keyword is still returned as the provisional pillar
```

**ATS-010: Volume tie broken by intent scope**

```
GIVEN two keywords at volume 2400 in the same cluster
WHEN pillar identification runs
THEN the broader-intent keyword is selected
AND rationale explains the tie-breaking logic
```

### US-003: Cluster Quality Scoring

**ATS-011: Tight cluster scores high**

```
GIVEN a cluster "FUE Hair Transplant" with keywords all directly related to FUE technique
WHEN coherence scoring runs
THEN score is 8-10
AND explanation mentions "complementary intent" and "tight topic focus"
```

**ATS-012: Loose cluster scores low**

```
GIVEN a cluster "Hair Loss General" with keywords spanning multiple sub-topics ("hair loss", "hair transplant", "alopecia", "hair growth serum", "bald spot treatment")
WHEN coherence scoring runs
THEN score is 1-4
AND explanation recommends splitting into sub-clusters
```

**ATS-013: Low coherence warning for calendar**

```
GIVEN a cluster with coherence score < 4
WHEN cluster output is requested by F-007
THEN the cluster is flagged: "Low coherence — review before planning content"
```

**ATS-014: Coherence score as sort/filter field**

```
GIVEN clusters with scores [9, 4, 7, 3, 8]
WHEN F-007 requests clusters sorted by coherence
THEN clusters are returned in order: [9, 8, 7, 4, 3]
AND clusters with score < 4 have the low-coherence warning
```

---

## 2. Integration Test Scenarios (Phase 3)

**INT-001: F-001 output → F-002 input pipeline**

```
GIVEN F-001 has completed for hairgenetix.com
WHEN F-002 receives the keyword output
THEN all keywords have the required fields for clustering (keyword text, volume, language)
AND clustering produces valid output
```

**INT-002: F-002 output → F-007 input pipeline**

```
GIVEN F-002 has produced clusters
WHEN F-007 (Content Calendar) consumes the cluster data
THEN TopicCluster schema validates without errors
AND coherence scores are available for filtering
```

**INT-003: Claude API round-trip for clustering**

```
GIVEN valid Claude API credentials
WHEN a clustering prompt with 20 test keywords is submitted
THEN the response is parseable as structured cluster data
AND every input keyword appears in exactly one cluster or the unclustered set
```

**INT-004: Per-language independent clustering**

```
GIVEN keyword sets for DE (80 keywords) and EN (70 keywords)
WHEN clustering runs for both
THEN DE and EN keywords are clustered independently (no cross-language merging)
AND each produces its own cluster set
```

**INT-005: Standalone JSON output**

```
GIVEN standalone mode (no database)
WHEN clustering completes
THEN output is saved to data/clusters/{domain}.json
AND the file validates against TopicCluster schema
```

**INT-006: Custom cluster size parameters**

```
GIVEN --max-cluster-size=15 and --min-cluster-size=4
WHEN clustering runs
THEN no cluster exceeds 15 keywords
AND no cluster has fewer than 4 keywords (keywords that would form smaller groups go to unclustered)
```

---

## 3. Property Invariants (Phase 3)

| ID | Property | Invariant |
|----|----------|-----------|
| PI-001 | Complete keyword coverage | Every input keyword appears in exactly one cluster OR the unclustered set — no keyword omitted |
| PI-002 | No duplicate keywords | No keyword appears in more than one cluster |
| PI-003 | Cluster size bounds | Every cluster has >= min_cluster_size (default 3) and <= max_cluster_size (default 20) keywords |
| PI-004 | Coherence score range | Coherence score is always 1-10 inclusive (integer) |
| PI-005 | Pillar per cluster | Every cluster has exactly one pillar keyword identified |
| PI-006 | Rationale non-empty | Every cluster has a non-empty grouping rationale string |
| PI-007 | Primary keyword is highest volume | In each cluster, the keyword flagged as "primary" has the highest volume among variants |
| PI-008 | Token budget | Total LLM tokens consumed for clustering <= 50,000 |
| PI-009 | Cluster name non-empty | Every cluster has a non-empty name string |
| PI-010 | Score explanation present | Every coherence score has a non-empty explanation string |

---

## 4. Test Layer Classification (Phase 3)

| Test ID | Layer | Justification |
|---------|-------|---------------|
| ATS-001 to ATS-005 | Integration | Requires LLM call for semantic grouping |
| ATS-006 | E2E | Performance test — full pipeline timing |
| ATS-007 | Integration | Tests LLM failure handling with mocked API |
| ATS-008 to ATS-010 | Unit | Pillar selection is rule-based (highest volume + broadest scope) |
| ATS-011 to ATS-014 | Integration | Coherence scoring requires LLM evaluation |
| INT-001 to INT-006 | Integration | Cross-feature data flow and storage boundaries |
| PI-001 to PI-010 | Property | Fast-check on TopicCluster schema and keyword coverage |

---

## 5. Test Architecture (Phase 4)

> Phase 4 — to be completed during design phase.

---

## 6. Test Results (Phase 6)

> Phase 6 — to be completed during implementation and ship phases.
