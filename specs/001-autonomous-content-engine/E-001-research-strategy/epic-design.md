# Epic Design — E-001: Research & Strategy Engine

> Cross-cutting architecture decisions shared across all 7 features.
> Feature-specific designs are in each feature's `design.md`.

---

## Architecture Overview

### System Context (C4 Level 1)

```
┌─────────────────────────────────────────────────────┐
│                   Content Engine Module              │
│              modules/content-engine/research/        │
│                                                     │
│  ┌───────────┐  ┌──────────┐  ┌───────────────┐   │
│  │ Commands  │  │ Queries  │  │   Events      │   │
│  │ (writes)  │  │ (reads)  │  │ (async out)   │   │
│  └─────┬─────┘  └────┬─────┘  └──────┬────────┘   │
│        │             │               │             │
│  ┌─────┴─────────────┴───────────────┴──────┐      │
│  │         Pipeline Orchestrator             │      │
│  │    (stage runner, state machine)           │      │
│  └─────┬──────┬──────┬──────┬──────┬────┘      │
│        │      │      │      │      │           │
│  ┌─────┴┐ ┌──┴──┐ ┌─┴──┐ ┌┴───┐ ┌┴────┐     │
│  │ KW   │ │SERP │ │Gap │ │Cal │ │Clust│     │
│  │ Res  │ │ Anl │ │ ID │ │Gen │ │ er  │     │
│  └──┬───┘ └──┬──┘ └─┬──┘ └─┬──┘ └──┬──┘     │
│     │        │      │      │       │         │
│  ┌──┴────────┴──────┴──────┴───────┴──┐      │
│  │     Data Source Abstraction Layer    │      │
│  │  (Adapter pattern per provider)     │      │
│  └──┬──────┬──────┬──────┬────────┘      │
│     │      │      │      │               │
└─────┼──────┼──────┼──────┼───────────────┘
      │      │      │      │
┌─────┴┐ ┌──┴──┐ ┌┴────┐ ┌┴───────┐
│ KW   │ │Data │ │Serp │ │ Google │
│ Every│ │ For │ │ API │ │ Search │
│ where│ │ SEO │ │     │ │Console │
└──────┘ └─────┘ └─────┘ └────────┘
```

### Container Diagram (C4 Level 2)

| Container | Technology | Purpose |
|-----------|-----------|---------|
| Research Module | TypeScript, Drizzle ORM | Business logic for all 7 features |
| PostgreSQL | PostgreSQL 16 + RLS | Persistent storage (keywords, results, calendars) |
| Redis | Redis 7 | Job queue (BullMQ), caching keyword data |
| AI Gateway | OpenAI/Anthropic API | LLM for clustering, intent, content analysis |
| External APIs | Keywords Everywhere, DataForSEO, SerpAPI, GSC | Keyword data, SERP data, search console data |

---

## ADR Index

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-E001-001 | Pipeline orchestration: BullMQ job chains | Proposed |
| ADR-E001-002 | Data source abstraction: Adapter pattern with interface per source type | Proposed |
| ADR-E001-003 | Topic clustering: LLM-first with embedding fallback | Proposed |
| ADR-E001-004 | Tenant isolation: tenant_id + RLS on all tables | Proposed |
| ADR-E001-005 | Keyword caching: tenant-scoped with 24h TTL | Proposed |
| ADR-E001-006 | Content brief schema: structured JSON output contract | Proposed |

---

## ADR-E001-001: Pipeline Orchestration

**Status:** Proposed
**Context:** The research pipeline has 7 stages with dependencies (F-001→F-004→F-006→F-007). Need reliable, resumable execution with error handling.
**Decision:** Use BullMQ job chains with Redis. Each pipeline stage is a separate job type. Jobs are chained via `FlowProducer` with parent-child relationships.
**Rationale:**
- Solo developer — Temporal requires a separate server + worker process (operational overhead)
- BullMQ is already in the SaaS Platform tech stack (packages/core)
- Job chains support the exact dependency pattern we need
- Built-in retry, backoff, progress tracking, and job state persistence
- Redis is already required for the platform
**Alternatives considered:**
1. Temporal — More powerful but operational overhead too high for solo dev. Revisit when team grows.
2. Simple async/await — No persistence, no retry, no progress tracking. Fails on timeout.
3. EventEmitter — No persistence. Lost on process restart.
**Consequences:** Requires Redis. Job payloads must be serialisable (no functions). Max job size ~512KB (Redis limit per key).

---

## ADR-E001-002: Data Source Abstraction

**Status:** Proposed
**Context:** Multiple keyword data sources (Keywords Everywhere, DataForSEO, SerpAPI, GSC) with different APIs, auth methods, and response formats.
**Decision:** Adapter pattern with a `KeywordDataSource` interface. Each provider implements the interface. A `DataSourceRegistry` selects the appropriate adapter based on capability + tenant config.

```typescript
interface KeywordDataSource {
  readonly capabilities: Set<'volume' | 'difficulty' | 'serp' | 'suggestions' | 'trends'>;
  getKeywordVolume(keywords: string[], locale: string): Promise<KeywordVolumeResult[]>;
  getKeywordSuggestions(seed: string, locale: string): Promise<string[]>;
  getSerpResults?(keyword: string, locale: string): Promise<SerpResult[]>;
}
```

**Rationale:**
- Clean separation — swapping DataForSEO for SEMrush = one new adapter class
- Capability-based selection — different sources excel at different things
- Testable — mock adapters for testing
**Alternatives considered:**
1. Strategy pattern — Similar but less discoverable. Adapter is more explicit about the transformation.
2. Direct API calls — No abstraction. Tight coupling to each provider.
**Consequences:** Slight overhead from abstraction. Worth it for provider flexibility.

---

## ADR-E001-003: Topic Clustering

**Status:** Proposed (updated from architecture research 2026-03-15)
**Context:** Need to group 50-500 keywords into topical clusters (pillar + support structure).
**Decision:** Two-phase approach: (1) Embedding-based clustering via OpenAI `text-embedding-3-small` (384-dim) + HDBSCAN, (2) LLM for cluster labelling only.

**R1 approach:**
1. Generate embeddings for all keywords via `text-embedding-3-small` ($0.02 per 1M tokens — negligible cost)
2. Optional UMAP dimensionality reduction (384→50 dims for HDBSCAN performance)
3. HDBSCAN clustering (no need to specify cluster count — auto-detects)
4. SERP overlap validation: keywords sharing ≥40% of top-10 URLs are merged into same cluster
5. LLM generates cluster name + rationale from keyword list (transparency requirement)

**R2 enhancement:** Store embeddings in pgvector for persistent similarity search. Incremental clustering (add new keywords to existing clusters).

**Rationale (from research):**
- HDBSCAN is deterministic — same input = same clusters (LLM clustering is stochastic)
- Embedding cost negligible ($0.02/1M tokens vs $0.01-0.05 per LLM batch)
- SERP overlap validation adds real-world signal (keywords ranking for same URLs = same topic)
- LLM used only for labelling (cheap, fast, transparent)
- No pgvector needed for R1 — embeddings processed in-memory
**Alternatives considered:**
1. LLM-only clustering — Stochastic, expensive at scale, non-reproducible
2. TF-IDF + cosine similarity — Lower quality for semantic similarity
3. pgvector + DBSCAN from day 1 — Store embeddings from R1 but don't require pgvector extension
**Consequences:** Requires OpenAI API for embeddings. HDBSCAN available via `hdbscan` npm package or Python subprocess. Deterministic results enable reliable testing.

---

## ADR-E001-004: Tenant Isolation

**Status:** Proposed
**Context:** Multi-tenant SaaS module. Each tenant has their own keywords, campaigns, and content calendars.
**Decision:** `tenant_id` column on every table. PostgreSQL RLS policies enforce isolation. BullMQ jobs include `tenant_id` in job data.

**Pattern:**
- Middleware sets `app.current_setting('app.tenant_id')` from auth token
- RLS policies: `USING (tenant_id = current_setting('app.tenant_id')::uuid)`
- BullMQ jobs: `{ data: { tenant_id, ...payload } }` — worker sets tenant context before processing
- Standalone CLI mode: single tenant, configured via env var

**Rationale:** Standard pattern per agency ADR-017 (data layer governance). RLS is enforced by CI gate.
**Alternatives considered:**
1. Schema-per-tenant — Too complex for solo dev. Scaling nightmare.
2. Application-level filtering only — Insecure. One missed WHERE clause = data leak.
**Consequences:** Every query is tenant-scoped. Must set tenant context in BullMQ workers.

---

## ADR-E001-005: Keyword Data Caching

**Status:** Proposed
**Context:** Keyword volume/difficulty lookups cost API credits. Same keywords queried across pipeline stages.
**Decision:** Tenant-scoped Redis cache with 24h TTL for keyword data. Cache key: `kw:{tenant_id}:{locale}:{keyword_hash}`.

**Rationale:**
- Keyword volume doesn't change hour-to-hour
- Saves API credits (Keywords Everywhere: 100K lookups for $10)
- 24h TTL balances freshness vs cost
**Alternatives considered:**
1. PostgreSQL cache table — Slower for lookups, simpler infrastructure
2. No caching — Wasteful API usage
**Consequences:** Redis required (already needed for BullMQ). Cache invalidation on demand available.

---

## ADR-E001-006: Content Brief Output Contract

**Status:** Proposed
**Context:** E-001 output feeds E-002 (Content Creation). Need a stable interface contract.
**Decision:** `ContentBrief` TypeScript interface + Zod schema, stored in `specs/contracts/content-brief.ts`.

```typescript
interface ContentBrief {
  id: string;                           // prefixed: cb_xxx
  tenant_id: string;
  keyword: {
    primary: string;
    secondary: string[];
    volume: number;
    difficulty: number;
    intent: 'informational' | 'transactional' | 'navigational' | 'commercial';
  };
  cluster: {
    id: string;
    name: string;
    pillar_keyword: string;
  };
  serp_analysis: {
    top_results: { url: string; title: string; word_count: number; }[];
    serp_features: string[];          // 'featured_snippet', 'paa', 'ai_overview'
    avg_word_count: number;
    content_gap_score: number;        // 0-100
  };
  competitors: {
    url: string;
    strengths: string[];
    weaknesses: string[];
  }[];
  recommendation: {
    target_word_count: number;
    suggested_format: 'how-to' | 'listicle' | 'guide' | 'comparison' | 'review';
    priority_score: number;           // 0-100
    estimated_traffic_potential: number;
  };
  calendar_position: {
    week: number;                     // week number in calendar
    sequence: number;                 // order within week
  };
  metadata: {
    created_at: string;               // ISO 8601
    pipeline_run_id: string;
    locale: string;
    source_data_freshness: string;    // ISO 8601 of oldest data source
  };
}
```

**Rationale:** Explicit contract prevents E-002 from depending on implementation details. Zod schema enables runtime validation at the boundary.
**Alternatives considered:**
1. Unstructured markdown output — Not machine-parseable for E-002
2. GraphQL schema — Over-engineering for internal module-to-module contract
**Consequences:** Both E-001 and E-002 depend on this contract. Changes require versioning.

---

## Cross-Cutting Data Model

### Entity Relationship Overview

```
Tenant ──1:M──→ Campaign ──1:M──→ PipelineRun
                    │
                    ├──1:M──→ Keyword ──M:1──→ KeywordCluster
                    │              │
                    │              ├──1:M──→ KeywordVolume (cached)
                    │              └──1:M──→ SerpResult
                    │
                    ├──1:M──→ CompetitorSite ──1:M──→ CompetitorPage
                    │
                    ├──1:M──→ ContentGap
                    │
                    └──1:M──→ ContentCalendar ──1:M──→ ContentBrief
```

### Core Tables

| Table | Key Fields | Notes |
|-------|-----------|-------|
| `campaign` | id, tenant_id, name, domain, locales[], seed_keywords[], status | One campaign per domain per tenant |
| `keyword` | id, tenant_id, campaign_id, term, locale, volume, difficulty, cpc, intent, cluster_id | Deduplicated per campaign+locale |
| `keyword_cluster` | id, tenant_id, campaign_id, name, pillar_keyword_id, keywords_count | LLM-generated cluster |
| `serp_result` | id, tenant_id, keyword_id, rank, url, title, snippet, word_count, serp_features[] | Top-10 per keyword |
| `competitor_site` | id, tenant_id, campaign_id, domain, crawl_status | Sites we compare against |
| `competitor_page` | id, tenant_id, competitor_site_id, url, title, word_count, topics[], quality_score | Per-page analysis |
| `content_gap` | id, tenant_id, campaign_id, keyword_id, gap_type (missing/weak/strong/shared/unique), gap_score, our_coverage, competitor_coverage, opportunity_score | Gap matrix with 5-type classification |
| `content_brief` | id, tenant_id, campaign_id, keyword_id, brief_json, priority_score, calendar_week, status | Output contract (JSON column) |
| `pipeline_run` | id, tenant_id, campaign_id, status, started_at, completed_at, stages_completed[], error | Pipeline execution tracking |

All tables have: `id` (prefixed UUID), `tenant_id` (UUID, RLS), `created_at`, `updated_at`.

---

## Event Contracts

| Event | Payload | Producer | Consumer |
|-------|---------|----------|----------|
| `research.pipeline.started` | `{ tenant_id, campaign_id, run_id }` | Pipeline orchestrator | Monitoring |
| `research.pipeline.stage.completed` | `{ tenant_id, run_id, stage, results_count }` | Stage worker | Pipeline orchestrator, Monitoring |
| `research.pipeline.completed` | `{ tenant_id, campaign_id, run_id, briefs_count }` | Pipeline orchestrator | E-002 (Content Creation) |
| `research.calendar.generated` | `{ tenant_id, campaign_id, calendar_id, entries_count }` | F-007 (Calendar) | Notification service |
| `research.brief.created` | `{ tenant_id, brief_id, keyword }` | F-007 (Calendar) | E-002 (Content Creation) |
| `research.pipeline.failed` | `{ tenant_id, run_id, stage, error }` | Stage worker | Monitoring, Notification |

---

## Security Architecture (STRIDE-Lite — Full Research)

> Based on OWASP API Security Top 10 (2023), OWASP SSRF Prevention Cheat Sheet, Google OAuth Best Practices, AWS Multi-Tenant RLS Guidance.

### Priority Mitigations for R1

| # | Threat | Category | Severity | Mitigation |
|---|--------|----------|:--------:|------------|
| 1 | **SSRF via URL input** (D-03) | DoS | Critical | Multi-layer: allowlist http/https schemes, reject private IPs (10.x, 172.16.x, 192.168.x, 127.x, 169.254.x), DNS rebinding protection (resolve once, pin IP), validate each redirect hop, max 5 redirects, 10s connect / 30s read timeout, max 10MB response. |
| 2 | **Cross-tenant data leakage** (I-01) | Info Disclosure | Critical | Three-layer defence: (1) middleware tenant_id check, (2) PostgreSQL RLS on every tenant_id table, (3) CI gate blocks merge if RLS missing. Opaque UUIDs for all resource IDs. |
| 3 | **Tenant impersonation** (S-03) | Spoofing | Critical | Set `app.current_tenant` exclusively from verified JWT in middleware. Reset on connection return to pool. |
| 4 | **BOLA — object-level auth bypass** (E-01) | Elevation | Critical | Every command/query handler verifies tenant_id matches authenticated tenant. RLS is safety net, not primary control. |
| 5 | **API key exposure** (I-02) | Info Disclosure | High | Secret manager (Bitwarden dev, cloud KMS prod). Never log request headers with keys. Pre-commit hook (gitleaks). Rotate quarterly. |
| 6 | **Injection via API responses** (T-01) | Tampering | High | Zod validation on ALL external API responses before storage. Parameterised queries only (Drizzle ORM enforces). Strip HTML from text fields. |
| 7 | **Rate limit exhaustion** (D-01) | DoS | High | Per-tenant token bucket per API. Global rate limiter at 80% of provider limit. Fair scheduling (round-robin across tenants). Circuit breaker: 3 failures → back off + alert. |
| 8 | **GSC OAuth token theft** (S-02) | Spoofing | Critical | Encrypt tokens at rest (AES-256-GCM). Dedicated `oauth_tokens` table with RLS. Refresh token rotation. Never log tokens. |
| 9 | **Malicious HTML in scraped content** (T-02) | Tampering | High | DOMPurify sanitisation. Store as plain text, never raw HTML. CSP on dashboard (R2+). |
| 10 | **CLI command injection** (E-03) | Elevation | High | Never construct shell commands from user input. Parameterised subprocess calls. Strict CLI argument schemas. |

### Shared vs Tenant-Scoped Data Model

| Data Type | Scope | Rationale |
|-----------|-------|-----------|
| Raw keyword metrics (volume, CPC, difficulty) | **Shared cache** | Public API data, identical for all tenants. Saves API costs. |
| Keyword lists (which keywords a tenant tracks) | **Tenant-scoped (RLS)** | Reveals competitive strategy. |
| SERP snapshots (raw) | **Shared cache** | Public search results. |
| Tenant's rank tracking | **Tenant-scoped (RLS)** | Private position monitoring. |
| GSC data | **Tenant-scoped (RLS)** | Highly sensitive first-party data. Never shared. |
| OAuth tokens | **Tenant-scoped (RLS + encrypted)** | Per-tenant credentials. AES-256-GCM. |
| API call audit logs | **Tenant-scoped (RLS)** | Per-tenant activity trail. |

### Cross-Cutting Security Controls

| ID | Control | Implementation |
|----|---------|----------------|
| X-01 | Zod validation at all boundaries | Every API response, scraped page, CLI input, GSC response → Zod schema → reject-by-default |
| X-02 | Structured audit logging | `audit_events` table: tenant_id, correlation_id, event_type, details, timestamp. Append-only. 90-day retention. |
| X-03 | Secret management | API keys + OAuth tokens in secret manager. Per-tenant encryption keys for OAuth. Quarterly rotation. |
| X-04 | Defence in depth (tenant isolation) | 3 layers: middleware check → RLS → CI gate. |

---

## Build Boundaries (Three-Tier)

| Tier | Actions |
|------|---------|
| **Always** (no approval) | Write module code, run tests, update specs, refactor within module scope |
| **Ask first** | Add npm dependency, change ContentBrief contract, modify shared database schema |
| **Never** | Delete production data, skip tests, bypass RLS, store API keys in code |

---

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | TypeScript 5.x | Agency standard |
| ORM | Drizzle | Agency standard (ADR-017) |
| Database | PostgreSQL 16 | Agency standard, RLS support |
| Queue | BullMQ + Redis 7 | ADR-E001-001 |
| AI Gateway | `packages/ai-gateway` | Agency shared package |
| HTTP Client | undici / fetch | Node.js built-in, no dependency |
| HTML Parsing | cheerio | Lightweight, well-maintained |
| Test | Vitest + fast-check | Agency standard |

---

## Agent Context Assessment

When the building agent starts implementation:

**Must read:**
1. This file (`epic-design.md`) — cross-cutting architecture
2. Feature-specific `design.md` — per-feature contracts
3. `specs/contracts/content-brief.ts` — output contract
4. `packages/core/` — shared utilities (Result type, event bus)
5. `docs/api-style-guide.md` — API conventions

**Patterns to follow:**
- Five-Port module pattern (commands/queries/events)
- Result type for all fallible operations
- Zod schemas generated from Drizzle (drizzle-zod)
- Structured logging with correlation IDs

**Constitutional constraints (from Gate 1):**
1. All API endpoints require tenant context
2. No PII stored unencrypted
3. Pipeline must be resumable (no lost work on failure)
4. Human approval gate before content calendar is finalised
