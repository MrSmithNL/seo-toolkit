# Tests — F-004 Topic/Niche Configuration

> Acceptance test scenarios derived from requirements.md per RE v4.15 Phase 3 step 13.
> These are human-authored specifications — the building agent implements them as executable tests.

---

## Acceptance Tests (GIVEN/WHEN/THEN)

### AT-001: Auto-infer topics from rich site content (US-001 happy path)

```
GIVEN a registered site "hairgenetix.com" with 45 pages crawled
WHEN the system auto-infers topics
THEN 3-10 topic clusters are created
AND each cluster has a descriptive name derived from actual page content
AND TopicConfig.source is "auto_inferred"
```

### AT-002: Auto-infer from site with minimal content (US-001 edge case)

```
GIVEN a registered site with fewer than 5 content pages
WHEN the system auto-infers topics
THEN the system warns "Limited content for topic inference. Consider adding seed keywords."
AND produces a best-effort topic config with 1-3 clusters
```

### AT-003: Enter seed keywords comma-separated (US-002 happy path)

```
GIVEN a registered site
WHEN the user enters "hair growth, biotin, hair loss, keratin, hair vitamins"
THEN keywords are parsed into 5 individual entries
AND clustered into 2-3 topic groups
AND TopicConfig.source is "manual"
```

### AT-004: Enter seed keywords newline-separated (US-002 variant)

```
GIVEN a registered site
WHEN the user enters keywords separated by newlines
THEN keywords are parsed correctly (same as comma-separated)
AND duplicates are removed
```

### AT-005: Few seed keywords (US-002 edge case)

```
GIVEN a registered site
WHEN the user enters 2 keywords
THEN the system accepts them
AND notes "Few seed keywords — consider adding more for better clustering"
AND creates 1-2 clusters
```

### AT-006: Import from GSC (US-003 happy path)

```
GIVEN a registered site with GSC connected
WHEN the system imports top queries from the last 90 days
THEN up to 500 queries are fetched
AND clustered into topic groups
AND each keyword has performance data (impressions, clicks, CTR, position)
AND TopicConfig.source is "gsc_import"
```

### AT-007: GSC import with limited data (US-003 edge case)

```
GIVEN a registered site with GSC connected but only 12 queries
WHEN the system imports from GSC
THEN 12 queries are imported
AND clustered into 1-3 groups
AND a note about limited data is added
```

### AT-008: GSC access failure (US-003 error case)

```
GIVEN a registered site with invalid GSC credentials
WHEN the system attempts GSC import
THEN the system reports the auth error
AND suggests using auto-inference or manual keywords instead
```

### AT-009: Set cluster priorities (US-004 happy path)

```
GIVEN topic clusters exist for a site
WHEN the user sets "Hair Growth" cluster priority to "high"
THEN the cluster priority is updated
AND this cluster will be used first by E-002 for content planning
```

### AT-010: Default priorities when none set (US-004 default)

```
GIVEN topic clusters exist with no user-set priorities
THEN all clusters default to "medium" priority
AND article_count_target is calculated based on cluster keyword count
```

---

## Integration Tests

### IT-001: End-to-end auto-inference

```
GIVEN a clean database with a registered and crawled site
WHEN auto-inference runs
THEN TopicConfig record exists with source "auto_inferred"
AND at least 1 TopicCluster exists
AND each cluster has a name and at least 1 keyword
AND a structured log entry was created
```

### IT-002: Keyword deduplication across sources

```
GIVEN topics auto-inferred from URL crawl
WHEN the user also enters manual seed keywords that overlap with inferred ones
THEN duplicate keywords are merged (not duplicated across clusters)
AND the merged TopicConfig reflects both sources
```

### IT-003: Non-English keyword clustering

```
GIVEN a registered site "digitalbouwers.nl" with Dutch content
WHEN the system clusters Dutch keywords
THEN clusters have Dutch-language names
AND semantic grouping works correctly for Dutch terms
```

---

## Property Invariants

| Property | Description | Test Type |
|----------|-----------|-----------|
| TopicConfig.source is always one of: auto_inferred, manual, gsc_import | No other values | Unit |
| TopicCluster.priority is always one of: high, medium, low | No other values | Unit |
| TopicCluster.article_count_target >= 0 | Never negative | Unit |
| TopicCluster.keywords is never empty | At least 1 keyword per cluster | Unit |
| Cluster count per site is 1-50 | Within capacity limits | Unit |
| Keywords per cluster is 1-500 | Within capacity limits | Unit |

---

## Hallucination Risk Scenarios

| Risk | Scenario | Mitigation |
|------|---------|------------|
| Agent might invent topic clusters not supported by actual site content | "Cryptocurrency" cluster from a hair care site | AT-001 specifies cluster names must derive from actual page content |
| Agent might create overly granular clusters (50 clusters for 10 keywords) | Each keyword becomes its own cluster | Property invariant: 1-50 clusters, and cluster count should be << keyword count |
| Agent might hardcode GSC data for test sites | Always returns same 500 queries | Use mock GSC API with configurable responses |

---

## Test Layer Classification

| Test ID | Layer | Automated? |
|---------|-------|:----------:|
| AT-001 to AT-002 | Acceptance (Auto-inference) | Yes |
| AT-003 to AT-005 | Acceptance (Manual Input) | Yes |
| AT-006 to AT-008 | Acceptance (GSC Import) | Yes |
| AT-009 to AT-010 | Acceptance (Priorities) | Yes |
| IT-001 to IT-003 | Integration | Yes |
| Property invariants | Unit | Yes |
