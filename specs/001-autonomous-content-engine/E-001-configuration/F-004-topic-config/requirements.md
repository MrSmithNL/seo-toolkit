---
id: "FTR-CONFIG-004"
type: feature
title: "Topic/Niche Configuration"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 3-requirements
priority: must
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

# Topic/Niche Configuration — Requirements

## Problem Statement

The content pipeline needs to know what topics to write about. Without topic configuration, the pipeline either generates random content or requires manual keyword entry per article — both unacceptable for autonomous operation. Topics drive E-002 (Research) keyword discovery, E-003 (Generation) article planning, and E-005 (Monitoring) topic authority tracking.

## Research Summary

### Competitor Analysis

| Capability | SEObot | SEO.ai | Byword | Keyword Insights | Our Approach |
|-----------|:------:|:------:|:------:|:---------------:|:------------:|
| Auto-infer from URL crawl | ✅ | ✅ | ❌ | ❌ | ✅ |
| Seed keyword input | ✅ | ❌ | ✅ (per article) | ✅ | ✅ |
| GSC import | ❌ | ❌ | ❌ | ✅ | ✅ |
| Auto-clustering | ❌ | ❌ | ❌ | ✅ | ✅ |
| Topic authority tracking | ❌ | ✅ | ❌ | ❌ | ✅ (E-005) |

### Key Findings

- URL crawl-based inference is the modern standard (SEObot, SEO.ai) — zero manual input
- GSC import is the power-user path — real search performance data
- Auto-clustering groups keywords into topic clusters — more useful than flat keyword lists
- No tool combines all three input modes (URL + seed keywords + GSC)

### Sources

- `research/e001-configuration-setup-patterns.md` §5 (Topic/Niche Setup)
- `E-001-configuration/research/phase2-analysis.md` §Spec-as-Context for F-004

## Impact Map

```
Goal: Give the content pipeline a clear topic strategy for the target site
  +-- Actor: Agency operator (Malcolm) / Future SaaS user
       +-- Impact: Pipeline generates on-topic content without per-article manual input
            +-- Deliverable: Auto-infer topics from site content
            +-- Deliverable: Manual seed keyword entry
            +-- Deliverable: GSC import for data-driven topics
            +-- Deliverable: Keyword clustering into topic groups
```

## Domain Model

```
TopicConfig {
  id: UUID
  site_id: UUID (FK -> SiteConfig.id)
  source: enum (auto_inferred, manual, gsc_import)
  clusters: TopicCluster[]
  seed_keywords: string[] (raw input before clustering)
  created_at: timestamp
  updated_at: timestamp
}

TopicCluster {
  id: UUID
  topic_config_id: UUID (FK -> TopicConfig.id)
  name: string (cluster label, e.g., "Hair Growth Supplements")
  keywords: string[] (member keywords)
  priority: enum (high, medium, low)
  article_count_target: int (how many articles to generate for this cluster)
  existing_coverage: int (articles already on site for this topic, from F-001 crawl)
}
```

Note: `article_count_target` and `existing_coverage` fields in TopicCluster are stored as JSON extensions within the Drizzle model. See epic-design.md for the full Drizzle schema.

## User Stories

### US-001: Auto-infer topics from existing site content

**As a** content pipeline operator, **I want** the system to automatically identify topic areas from my existing site content, **so that** new content aligns with my site's established niche.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

WHEN a site has been registered and crawled (F-001)
THE SYSTEM SHALL analyse existing page titles, headings, and meta descriptions from the sitemap data
AND use AI to identify 3-10 topic clusters
AND populate TopicConfig with source "auto_inferred"

WHEN the site has fewer than 5 content pages
THE SYSTEM SHALL warn "Limited content for topic inference. Consider adding seed keywords."
AND produce a best-effort topic config with fewer clusters

**Examples:**

| Scenario | Site | Existing Content | Expected Topics |
|----------|------|-----------------|----------------|
| Rich content site | hairgenetix.com | 45 pages about hair growth, supplements, ingredients | Clusters: "Hair Growth", "Hair Supplements", "Natural Ingredients", "Hair Care Tips" |
| New site | new-site.com | 3 pages (homepage, about, contact) | Warning: limited content. 1 generic cluster from page titles. |
| Niche WordPress | digitalbouwers.nl | 20 pages about digital marketing, web design | Clusters: "Digital Marketing", "Web Design", "SEO", "Online Strategie" |

### US-002: Enter seed keywords manually

**As a** content pipeline operator, **I want** to paste a list of seed keywords, **so that** I can direct the pipeline toward specific topics I want to cover.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN a user provides a list of seed keywords (one per line or comma-separated)
THE SYSTEM SHALL parse and deduplicate the keywords
AND cluster them into topic groups using semantic similarity
AND populate TopicConfig with source "manual"

WHEN the user provides fewer than 3 keywords
THE SYSTEM SHALL accept them but note "Few seed keywords — consider adding more for better clustering"

**Examples:**

| Scenario | Input Keywords | Expected Clusters |
|----------|---------------|-------------------|
| 10 hair-related keywords | "hair growth, biotin, hair loss, keratin, hair vitamins, thinning hair, hair regrowth, DHT blocker, minoxidil, hair supplements" | 3 clusters: "Hair Growth & Regrowth", "Hair Supplements & Vitamins", "Hair Loss Causes & Treatment" |
| 3 broad keywords | "SEO, content marketing, backlinks" | 2-3 clusters: "SEO", "Content Marketing", "Link Building" |
| 1 keyword | "biotin" | 1 cluster: "Biotin" with note about adding more keywords |

### US-003: Import topics from Google Search Console

**As a** content pipeline operator, **I want** to import my top-performing search queries from GSC, **so that** the pipeline builds on keywords I already rank for.

**Priority:** Should
**Size:** L

**Acceptance Criteria:**

WHEN a user connects their GSC account and selects a property
THE SYSTEM SHALL fetch the top 500 queries by impressions from the last 90 days
AND cluster them into topic groups
AND populate TopicConfig with source "gsc_import"
AND include performance data (impressions, clicks, CTR, position) per keyword

WHEN GSC access fails (invalid credentials, no data)
THE SYSTEM SHALL report the error and suggest using auto-inference or manual keywords instead

**Examples:**

| Scenario | GSC Data | Expected Result |
|----------|---------|-----------------|
| Active site with GSC | 500 queries, 50K impressions | 5-8 clusters with performance data |
| New site with little GSC data | 12 queries, 200 impressions | 2-3 clusters with note about limited data |
| GSC not connected | No property access | Error + suggestion to use auto-inference |

### US-004: Set topic cluster priorities

**As a** content pipeline operator, **I want** to prioritise which topic clusters to focus on first, **so that** the pipeline generates content for the most important topics.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

WHEN topic clusters have been created (from any source)
THE SYSTEM SHALL allow the user to set priority (high, medium, low) per cluster
AND allow setting an article count target per cluster

WHEN no priorities are set
THE SYSTEM SHALL default all clusters to "medium" priority
AND set article_count_target based on cluster size (more keywords = more articles)

**Examples:**

| Scenario | Action | Expected Result |
|----------|--------|----------------|
| Set high priority | Mark "Hair Growth" as high | This cluster gets articles generated first |
| Default priorities | Don't set any | All clusters medium, targets based on keyword count |
| Zero target | Set "Hair Loss Causes" target to 0 | No articles generated for this cluster |

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN auto-inferring topics THE SYSTEM SHALL complete analysis WITHIN 30 seconds | p95 < 30s | Integration test | Yes |
| 2 | **Security** | WHEN connecting to GSC THE SYSTEM SHALL use OAuth 2.0 and store tokens encrypted | Encrypted OAuth tokens | Security review | Yes |
| 3 | **Reliability** | WHEN topic inference produces poor results THE SYSTEM SHALL allow the user to retry or switch to manual input | Multiple input paths available | Manual verification | No |
| 4 | **Scalability** | N/A — single-user system for V1 | — | — | No |
| 5 | **Availability** | N/A — not a hosted service for V1 | — | — | No |
| 6 | **Maintainability** | WHEN the clustering algorithm needs updating THE SYSTEM SHALL isolate clustering logic in a separate module | Modular clustering | Architecture review | No |
| 7 | **Portability** | N/A — Node.js runtime | — | — | No |
| 8 | **Accessibility** | N/A — CLI interface for V1 | — | — | No |
| 9 | **Usability** | WHEN entering seed keywords THE SYSTEM SHALL accept both comma-separated and newline-separated input | Flexible parsing | Unit test | Yes |
| 10 | **Interoperability** | WHEN importing from GSC THE SYSTEM SHALL use the Google Search Console API v3 | Standard API | Integration test | Yes |
| 11 | **Compliance** | N/A — keyword data is not PII | — | — | No |
| 12 | **Data Retention** | WHEN a site is deleted THE SYSTEM SHALL delete all associated topic configs | Cascade delete | Integration test | Yes |
| 13 | **Backup / Recovery** | WHEN topic config is lost THE SYSTEM SHALL support re-import from the same sources | Re-runnable import | Manual verification | No |
| 14 | **Logging** | WHEN topics are configured THE SYSTEM SHALL log: source type, cluster count, total keywords, duration | Structured log | Log assertion in test | Yes |
| 15 | **Cost** | WHEN auto-inferring or clustering THE SYSTEM SHALL use one AI API call per operation | Max 1 API call per operation | Code review | No |
| 16 | **Capacity** | WHEN storing topic configs THE SYSTEM SHALL support up to 50 clusters per site and 500 keywords per cluster | Storage limits | Unit test | No |
| 17 | **Internationalisation** | WHEN keywords are in a non-English language THE SYSTEM SHALL cluster them correctly (semantic similarity works across languages) | Cross-language clustering | Integration test with Dutch keywords | No |
| 18 | **Extensibility** | WHEN adding a new topic source (e.g., Ahrefs, SEMrush) THE SYSTEM SHALL support it by implementing a TopicSourceAdapter | Adapter pattern | Architecture review | No |
| 19 | **Operation Pattern** | WHEN any command or query is executed THE SYSTEM SHALL follow the 5-step Operation pattern (P-008): Zod input → OperationContext → business logic → persist → emit event + return Result<T, OperationError> | All operations return Result type | Architecture fitness test FF-030 | Yes |
| 20 | **Error Handling** | WHEN a topic configuration or clustering operation fails THE SYSTEM SHALL return an OperationError (not throw) with RFC 7807-compatible error codes and `suggested_action` field | Zero naked `throw` in commands/queries | FF-032 + code review | Yes |
| 21 | **Structured Logging** | WHEN any topic configuration operation executes THE SYSTEM SHALL emit `operation.started`, `operation.completed`, and `operation.failed` structured JSON events via pino with correlationId + tenantId | 3 log events per operation | Log assertion in integration test | Yes |
| 22 | **Tenant Isolation** | WHEN querying topic configuration data THE SYSTEM SHALL enforce RLS so Tenant A cannot read/update/delete Tenant B's topic configs. Cross-tenant access returns 404 (not 403). | `tenant-isolation.test.ts` passes | Integration test (FF-034) | Yes |
| 23 | **Idempotency** | WHEN creating topic configurations THE SYSTEM SHALL accept an optional idempotencyKey. Duplicate requests with the same key return the original result without creating duplicates. | Duplicate request = same response | Integration test | Yes |
| 24 | **Serialisable I/O** | WHEN returning topic configuration data from any operation THE SYSTEM SHALL use ISO 8601 strings for dates (never Date objects), plain objects only (no class instances) | JSON.parse(JSON.stringify(output)) === output | Unit test | Yes |
| 25 | **Contract Completeness** | WHEN exposing topic configuration commands or queries THE SYSTEM SHALL have a Zod input schema AND explicit TypeScript return type for each | Every public function has Zod + return type | FF-029 | Yes |
| 26 | **No Module State** | THE SYSTEM SHALL NOT use `let` or `var` at module scope in topic configuration `src/` files (except type exports and `const`) | Zero mutable module-level state | FF-033 | Yes |
| 27 | **PII Redaction** | WHEN logging topic configuration data THE SYSTEM SHALL redact any email, phone, IP address, or personal data fields using pino's redaction config | PII fields show `[REDACTED]` in logs | Log inspection test | Yes |
| 28 | **Prefixed IDs** | WHEN creating a TopicConfig THE SYSTEM SHALL generate IDs with `tpc_` prefix using NanoID or UUID v7. WHEN creating a TopicCluster THE SYSTEM SHALL generate IDs with `tcl_` prefix. | All IDs match `tpc_*` or `tcl_*` pattern | Unit test | Yes |
| 29 | **Circuit Breaker** | WHEN making API calls to Google Search Console THE SYSTEM SHALL use a circuit breaker (5 failures / 60s window → open for 30s) to prevent cascading failures from GSC outages | Circuit breaker state logged | Integration test | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN calling AI for topic clustering THE SYSTEM SHALL timeout after 60 seconds | p95 < 60s | Integration test |
| Token economics | WHEN clustering keywords THE SYSTEM SHALL use no more than 5,000 input tokens per operation | Max 5K tokens | Token counting |
| Hallucination rate | WHEN generating cluster names THE SYSTEM SHALL derive names from the actual keywords, not invent unrelated topics | Manual review of cluster output | QA |

## Out of Scope

- Keyword research (discovering NEW keywords) — that's E-002
- Content calendar generation from topics — that's E-002
- Import from Ahrefs, SEMrush, or other third-party SEO tools — V2
- Automatic topic refresh based on ranking changes — V2
- Topic gap analysis (what competitors cover that we don't) — E-002

## Open Questions

- [x] Should clustering be AI-based or algorithm-based (e.g., KeyBERT)? **Answer:** AI-based for V1 (simpler, more accurate with small keyword sets). Algorithm-based for V2 when handling 10K+ keywords.
- [x] How many clusters is optimal? **Answer:** 3-10 per site. Fewer than 3 means the site is too narrow; more than 10 means clusters are too granular.

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 (Site Registration) | Internal | In progress | Sitemap data feeds auto-inference |
| Google Search Console API | External | Ready | US-003 (GSC import) |
| Claude API | External | Ready | AI-based clustering |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | AI clustering produces meaningful topic groups from 10-50 keywords | Medium | Test with Hairgenetix keywords, manual review |
| A2 | Sitemap data (page titles, URLs) is sufficient for topic inference | Medium | Test: do inferred topics match site's actual focus? |
| A3 | GSC API provides sufficient query data for topic discovery | High | Confirmed by Google API docs |
| A4 | 3-10 topic clusters is the right granularity for content planning | Medium | Review with Malcolm after first real site setup |
