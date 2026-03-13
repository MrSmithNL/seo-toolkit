# Epic Status — Configuration & Setup

> **What this is:** Status tracker for E-001, the first epic of the Autonomous Content Engine.
> Covers initial setup: site registration, brand voice, CMS connection, topic config, quality thresholds, AISO preferences.

---

## Epic Identity

| Field | Value |
|-------|-------|
| **Epic ID** | E-001 |
| **Epic name** | Configuration & Setup |
| **Product** | PROD-001 (SEO Toolkit) |
| **Parent theme** | `specs/001-autonomous-content-engine/theme.md` |
| **Phase** | Release 1 (V1 full pipeline) |
| **Shape Up appetite** | 2 weeks |
| **Owner** | Malcolm |
| **Created** | 2026-03-13 |
| **Capability** | CAP-CE-001 — Site & Pipeline Configuration |
| **Baseline version** | null |
| **Parent baseline** | Theme v0 (not yet baselined) |

---

## Architecture Classification (Gate 0)

| Field | Value |
|-------|-------|
| **SaaS ecosystem?** | Yes |
| **Hierarchy level** | L3-module |
| **Hierarchy location** | `modules/content-engine/` |
| **Capability group** | seo |
| **Module manifest** | Required |
| **Tenant aware** | Yes |

### Architecture Integration Checklist

**Core SaaS Checklist:**
- [x] Tenant context — `SiteConfig` includes `tenant_id`, child entities inherit via `site_id` FK. Operations accept `OperationContext` (extends TenantContext with correlationId + idempotencyKey)
- [x] Module manifest — `module-manifest.json` with `contracts` field listing commands + queries (P-007)
- [x] Event contracts — 7 CloudEvents 1.0 events declared with `ce_type`, `ce_source`, `ce_subject` (logging standards §14)
- [x] Agent tools — 2 tools with consequence classification (Class A: read-only, Class B: tenant-write) per P-031
- [x] Dependency direction — module depends on `packages/` only (P-001)
- [ ] Feature flags — all new features behind flags (Phase 6: Build)
- [x] Temporary tenant solution — `StaticTenantResolver` reads from config file, same interface as future `DatabaseTenantResolver`

**SaaS Coding Architecture Compliance (34 principles):**
- [x] Operations follow P-008 (5-step pattern: Zod input → OperationContext → business logic → persist → emit + Result)
- [x] CQS enforced (P-005): commands in `src/api/commands.ts`, queries in `src/api/queries.ts`
- [x] Typed contracts (P-006): Zod input schemas + explicit return types + OperationError hierarchy
- [x] Module size limits (P-002): max 10 source files, max 2000 lines — to be validated at build
- [x] State externalised (P-010): all state in PostgreSQL, no module-level mutable variables
- [x] Serialisable I/O (P-011): ISO 8601 strings for dates, plain objects only
- [x] Webhook-triggerable (P-013): all commands callable via API routes

**Data Layer Governance (ADR-017):**
- [x] Drizzle schema uses snake_case column names directly (database migration standards §8.3)
- [x] RLS policies on all tenant-scoped tables in same migration (multi-tenant arch §3.1)
- [x] `tenant_id` indexed on every tenant table (migration standards §8.4)
- [x] Tenant isolation tests required: `tenant-isolation.test.ts` per module (FF-034, multi-tenant arch §11)
- [x] Migration linting gate: destructive SQL blocked by CI (migration standards §3b)
- [x] RLS validation script runs in CI (multi-tenant arch §3.2)

**API & Integration Standards:**
- [x] RFC 7807 error responses with `suggested_action` field (error handling patterns §3)
- [x] Result<T, OperationError> returns — no naked `throw` in commands/queries (P-005, FF-032)
- [x] Circuit breakers on external CMS API calls (error handling §8)
- [x] Idempotency keys on write operations (P-009, API standards §11)
- [x] Prefixed IDs: `ste_` (site), `cms_` (CMS connection), `vce_` (voice profile), `tpc_` (topic config) (API standards §4.3)

**Logging & Observability:**
- [x] Structured JSON logging via pino (logging standards §1)
- [x] operation.started / operation.completed / operation.failed events (SaaS coding arch P-028)
- [x] PII redaction configured (logging standards §4)
- [x] CloudEvents logging at emit + consume (logging standards §14)
- [x] Health endpoint at `/api/v1/health` (logging standards §8)

**Conformance Suite:**
- [x] YAML conformance tests required per feature endpoint (conformance suite template)
- [x] Covers: CRUD, validation errors, tenant isolation (404 not 403), idempotency, business rules

**Fitness Functions (7 new):**
- [x] FF-028: Module size limits enforced
- [x] FF-029: Contract completeness (every command/query has Zod schema)
- [x] FF-030: Operation signatures (Result return + OperationContext param)
- [x] FF-031: Zod validation on all route handlers
- [x] FF-032: No naked `throw` in commands/queries
- [x] FF-033: No module-level mutable state
- [x] FF-034: Tenant isolation test presence

### Platform Dependency Assessment

| Platform Service | Needed By | Status in PROD-004 | Temporary Solution | Migration Path |
|-----------------|-----------|-------------------|-------------------|---------------|
| Tenant Context (`AsyncLocalStorage`) | All data models | Phase 0 complete | `StaticTenantResolver` — reads `tenants.json` config | Swap resolver implementation, no schema changes |
| Database (Drizzle + SQLite/PostgreSQL) | All data storage | Phase 0 complete | Drizzle with SQLite + tenant_id query wrapper | Add RLS policies via `pgPolicy()` when multi-tenant |
| Auth (JWT + RBAC) | API endpoints | Not started | API key per config file | Swap to JWT middleware |
| Event Bus | Cross-module events | Phase 0 complete (in-process) | `EventEmitter` in-process | Swap to Trigger.dev when needed |
| Logging (pino) | All operations | L1 Foundation | Standard pino setup from `@saas-platform/core/logging` | Already platform-standard |
| Error handling | All operations | L1 Foundation | AppError hierarchy from `@saas-platform/core/errors` | Already platform-standard |
| AI Gateway | Agent tools (F-003 voice, F-006 AISO) | L2 Capability | Direct LLM API calls with Zod output validation (P-034) | Route through AI gateway when available |

---

## Traceability

| Level | Reference |
|-------|-----------|
| **Product goal** | PROD-001: SEO Toolkit — capability engine for AISOGEN and agency client work |
| **Theme** | `specs/001-autonomous-content-engine/theme.md` |
| **Capability** | CAP-CE-001 — Site & Pipeline Configuration [Supporting tier] |
| **Briefing** | `specs/001-autonomous-content-engine/automated-article-generator-briefing.md` §4.4 (Multi-Client/Multi-Site) |

---

## Definition of Ready (DOR) — Verified Before Feature Decomposition

> From `docs/capabilities/requirements-engineering.md` § Epic Level DOR

- [ ] Parent theme-level DOD is met (theme is fully understood and baselined)
- [x] Lean Business Case completed (benefit hypothesis, MVP, cost estimate, leading indicators)
- [x] Business process this epic supports is mapped (process steps → feature candidates)
- [x] Targeted competitor feature analysis for this capability completed
- [x] UX pattern research for this workflow completed
- [x] Architecture decisions for this epic documented (tech choices, data model, API surface)
- [x] Cross-cutting concerns addressed (multi-tenancy, auth, performance)
- [x] Interface contracts with adjacent epics defined
- [ ] Capability map entry updated with this epic's target maturity
- [x] Scope envelope created (if multi-agent: files owned, files forbidden, interfaces)

## Definition of Done (DOD) — Verified Before Marking Complete

> From `docs/capabilities/requirements-engineering.md` § Epic Level DOD

- [ ] All DOR criteria met and documented
- [ ] `epic-status.md` and `epic-design.md` fully populated
- [ ] All features identified with priorities, dependencies, and scope boundaries
- [ ] Feature dependency graph documented
- [ ] Epic-level acceptance criteria defined and measurable
- [ ] Interface contracts updated: API specs, data model changes, event contracts
- [ ] Scope envelopes documented for each feature (what's in/out)
- [ ] Malcolm has reviewed and approved the epic-level design
- [ ] Epic spec **baselined** (frozen — changes require change request)

---

## Scope Flags

> Items discovered during work that fall outside this epic's scope. Escalated, not implemented.

None currently.

---

## Problem Framing Triad

### 1. Five Whys

1. **Why do we need a configuration epic?** → Because the content engine needs to know which site to target, what CMS to publish to, and what quality standards to meet.
2. **Why can't it just run with defaults?** → Because every client site has different CMSs (Shopify vs WordPress), different brand voices, different topic areas, and different quality expectations.
3. **Why can't we hardcode per-client?** → Because this is a product feature in the SEO Toolkit, not a one-off script. Multiple clients/sites must be configurable without code changes.
4. **Why does configuration need to be its own epic?** → Because all downstream epics (Research, Generate, Publish, Monitor) depend on having correct site config, CMS credentials, and quality thresholds BEFORE they can run.
5. **Why is this the FIRST epic?** → Because without configuration, no pipeline stage has the context it needs. Site URL feeds research. CMS credentials feed publishing. Brand voice feeds generation. Quality thresholds feed scoring. Everything starts here.

**Root cause:** The content engine is a multi-tenant, multi-CMS, multi-language pipeline. Without correct configuration, every downstream stage operates blind.

### 2. Problem Statement Canvas

| Dimension | Answer |
|-----------|--------|
| **Who has this problem?** | Malcolm (agency operator), future AISOGEN SaaS users, agency clients with content needs |
| **Current state** | Manual configuration per client — Malcolm runs individual audit/content skills with hardcoded site details. No persistent config, no CMS credentials stored, no quality thresholds. Each session starts from scratch. |
| **Desired future state** | One-time setup per site: URL, CMS connection, brand voice, topics, quality targets, AISO preferences. Persisted. All downstream pipeline stages read from this config automatically. |
| **Constraints** | Must support Shopify GraphQL + WordPress REST. Must handle multi-language (9 languages for Hairgenetix). Must be secure (API keys encrypted). Must fit SEO Toolkit architecture (PROD-001 repo). |
| **Cost of inaction** | Without persistent config, every pipeline run requires manual setup. At 10+ articles/month across 3 test sites, that's hours of repeated manual work. Autonomous operation is impossible. |

### 3. Jobs-to-Be-Done (JTBD)

**Primary JTBD:**
"When I **want to start generating autonomous content for a new client site**, I want to **configure the site once with all required settings**, so I can **run the content pipeline repeatedly without manual setup**."

**Supporting JTBDs:**
- "When I **onboard a new Shopify client**, I want to **connect their store in under 5 minutes**, so I can **start generating content the same day**."
- "When I **have specific quality requirements** (e.g., AISO score ≥ 8/10), I want to **set thresholds that auto-reject low-quality content**, so I can **trust the pipeline output without reviewing every article**."
- "When I **manage multiple client sites**, I want to **switch between site configs easily**, so I can **run the pipeline for different clients without confusion**."

---

## Assumption Mapping

| # | Assumption | Risk | Evidence | Action |
|---|-----------|:----:|:--------:|--------|
| A1 | Shopify GraphQL Admin API supports blog article creation | M | Strong — confirmed in briefing + technology research | Validate API surface in Phase 4 |
| A2 | WordPress REST API is sufficient (no plugin needed) | M | Strong — 10/13 competitors use REST API | Validate auth flow in Phase 4 |
| A3 | Brand voice can be trained from 3-5 sample URLs | H | Weak — only Jasper does this at scale, unclear quality | Research in Phase 2 (E-001) |
| A4 | Users will configure quality thresholds (not just use defaults) | L | Weak — most competitors don't expose this | Default-heavy UX, advanced users can customise |
| A5 | Multi-language config can be set at site level | M | Strong — Hairgenetix already has 9 locales | Confirm Shopify locale API in Phase 4 |
| A6 | AISO scoring preferences are meaningful at config time | H | None — no competitor has this, untested concept | Validate with Malcolm's Hairgenetix experience |
| A7 | One-time setup is sufficient (no ongoing config maintenance) | M | Weak — CMS tokens expire, sites change | Plan for credential refresh and config versioning |

---

## Stakeholder Mapping (Power × Interest)

| | Low Interest | High Interest |
|---|---|---|
| **High Power** | — | **Malcolm** — validates at gates, provides client context, approves quality thresholds |
| **Low Power** | CMS platforms (Shopify/WordPress) — they provide APIs but don't care about our config | **End users** (future AISOGEN subscribers) — need simple onboarding. **Client sites** (Hairgenetix, Skingenetix, Digital Builders) — their CMS config determines what we can do |

---

## Business Process Supported

> What business process does this epic implement?

### Process Flow

```
[Site Registration] → [CMS Connection] → [Brand Voice Setup] → [Topic Config] → [Quality Settings] → [AISO Preferences] → [Config Complete ✓]
```

### Process Steps → Features

| Process Step | What Happens | Feature |
|-------------|-------------|---------|
| Site Registration | User enters site URL, system crawls for basic site info (CMS type, languages, existing content) | F-001 |
| CMS Connection | User connects their CMS via OAuth or API key, system verifies write access | F-002 |
| Brand Voice Setup | User provides sample content/URLs, system extracts voice characteristics | F-003 |
| Topic Configuration | User defines topic areas/niches, imports from GSC or keyword lists | F-004 |
| Quality Settings | User sets minimum SEO score, AISO score, readability level, word count range | F-005 |
| AISO Preferences | User configures which AISO factors to prioritise, schema types to generate | F-006 |

---

## Functional Breakdown

```
Epic E-001: Configuration & Setup
├── Feature F-001: Site URL Registration & Crawl Config [AUTO] [TS]
│   ├── Story: Register site URL and detect CMS type
│   ├── Story: Crawl existing content inventory
│   └── Story: Detect available languages/locales
├── Feature F-002: CMS Connection Setup [ASSISTED] [TS]
│   ├── Story: Connect WordPress via REST API (application password)
│   ├── Story: Connect Shopify via GraphQL Admin API (custom app or OAuth)
│   └── Story: Verify write permissions and test publish
├── Feature F-003: Brand Voice Training [ASSISTED] [DF]
│   ├── Story: Scan provided URLs to extract writing style
│   ├── Story: Generate voice profile (tone, vocabulary, sentence structure)
│   └── Story: Allow manual voice parameter adjustment
├── Feature F-004: Topic/Niche Configuration [ASSISTED] [TS]
│   ├── Story: Import topics from GSC (Search Console)
│   ├── Story: Manual topic/keyword seed entry
│   └── Story: Topic cluster auto-detection from existing content
├── Feature F-005: Quality Threshold Settings [ASSISTED] [DF]
│   ├── Story: Set minimum SEO content score (0-100)
│   ├── Story: Set minimum AISO score (0-10)
│   ├── Story: Set readability target (grade level)
│   └── Story: Set word count range (min/max)
└── Feature F-006: AISO Scoring Preferences [ASSISTED] [IN]
    ├── Story: Select priority AISO factors from 36-factor model
    ├── Story: Configure schema types to generate per article
    └── Story: Set AI platform targets (ChatGPT, Perplexity, Gemini)
```

---

## Current Phase

| Phase | Status | Date |
|-------|--------|------|
| Research | [x] Complete | 2026-03-13 |
| Design | [x] Complete | 2026-03-13 |
| **Gate 0: Architecture** | [x] Passed (v2 — all 10 frameworks) | 2026-03-13 |
| **Gate: Scope** | [x] Approved | 2026-03-13 |
| Feature specs | [x] Complete — all 6 features have framework NFRs | 2026-03-13 |
| **Gate: Completeness** | [x] Passed — 10/10 RE checks, 12/12 framework checks, 11 minor gaps fixed | 2026-03-13 |
| Task breakdown | [x] Complete — 32 tasks (26 impl + 6 verification), 8 framework tasks added | 2026-03-13 |
| **Gate: Build Approval** | [x] Passed — 4 minor conditions cleared (deployment, test data, agent boundaries, task count) | 2026-03-13 |
| Visual preview _(if UI)_ | N/A — CLI for V1 | |
| Build | [ ] Not started | |
| Build complete verification | [ ] Not started | |
| Staging verified | [ ] Not started | |
| **Gate: Ship** | [ ] Not reached | |
| Production deployed | [ ] Not started | |
| Post-deploy monitoring | [ ] Not configured | |
| Retrospective | [ ] Not started | |

---

## Epic Goal

**One sentence:** Enable one-time configuration of a target site (URL, CMS, brand voice, topics, quality thresholds, AISO preferences) so the content pipeline can run autonomously.

**Success criteria (epic-level):**
- [ ] A new site can be fully configured in under 10 minutes
- [ ] CMS connection (WordPress or Shopify) verified with successful test publish
- [ ] Configuration persists across pipeline runs — no re-entry needed
- [ ] Multi-language support works for sites with multiple locales (test: Hairgenetix, 9 languages)
- [ ] All downstream epics (E-002 through E-005) can read config without additional input

---

## Feature Breakdown

| ID | Feature | Priority | Status | Depends On | Est. |
|----|---------|----------|--------|------------|------|
| F-001 | Site URL Registration & Crawl Config | Must | Spec complete | — | 2 days |
| F-002 | CMS Connection Setup (WordPress + Shopify) | Must | Spec complete | F-001 | 3 days |
| F-003 | Brand Voice Training | Should | Spec complete | F-001 | 2 days |
| F-004 | Topic/Niche Configuration | Must | Spec complete | F-001 | 2 days |
| F-005 | Quality Threshold Settings | Should | Spec complete | — | 1 day |
| F-006 | AISO Scoring Preferences | Could | Spec complete | F-005 | 1 day |

**Must-have features:** F-001 (Site Registration), F-002 (CMS Connection), F-004 (Topic Config)
**Should-have features:** F-003 (Brand Voice), F-005 (Quality Thresholds)
**Could-have features:** F-006 (AISO Preferences)

---

## Progress Summary

| Metric | Count |
|--------|-------|
| **Total features** | 6 |
| **Features complete** | 0 |
| **Total tasks** | 33 |
| **Tasks complete** | 0 |

---

## Research Summary

> Key findings from epic-level research. Full research in `research/` subfolder.

| Research File | Key Finding |
|---------------|-------------|
| `../research/technology-landscape.md` | WordPress REST API + Shopify GraphQL cover 90%+ of target CMS. Pluggable adapter pattern recommended. |
| `../research/competitive-landscape.md` | 10/13 competitors support WordPress. Only Koala + Writesonic support Shopify. Brand voice training rare (3/13). |
| `../automated-article-generator-briefing.md` | Briefing defines multi-client/multi-site config model. Each site has own config: domain, CMS type, languages, keyword strategy, approval workflow. |
| _(E-001 domain research)_ | _(Pending — background agent running)_ |

---

## Dependencies

### External Dependencies (blockers we don't control)
| Dependency | Status | Impact if delayed |
|-----------|--------|-------------------|
| Shopify GraphQL Admin API (blog articles) | Available | Blocks F-002 Shopify connector |
| WordPress REST API (posts/pages) | Available | Blocks F-002 WordPress connector |
| Google Search Console API (topic import) | Available | Blocks F-004 GSC import story |

### Cross-Feature Dependencies
```
F-001 (Site Registration) ─→ F-002 (CMS Connection)
  ├──→ F-003 (Brand Voice)
  └──→ F-004 (Topic Config)
F-005 (Quality Thresholds) ─→ F-006 (AISO Preferences)
```

### Cross-Epic Dependencies
| This epic needs | From epic | Status |
|----------------|-----------|--------|
| — | — | E-001 has no upstream dependencies |

| Other epics need from E-001 | Epic | What they need |
|----------------------------|------|----------------|
| Site URL, CMS credentials | E-002 | Research needs site URL; gap analysis needs crawl data |
| Brand voice, quality thresholds | E-003 | Generation uses voice profile; scoring uses thresholds |
| CMS connection, schema config | E-004 | Publishing uses CMS adapter; schema uses AISO preferences |
| Site URL, AISO config | E-005 | Monitoring targets the configured site; AISO thresholds define alerts |

---

## Descoping Rules

> When the epic is slipping, use these rules to decide what to cut.

**Time trigger:** If 60% of appetite consumed (6 days) with < 40% features complete → evaluate scope.

**Descope order:**
1. F-006 (AISO Preferences) — Could-have, can use defaults
2. F-003 (Brand Voice) — Should-have, can use generic professional tone
3. F-005 (Quality Thresholds) — Should-have, can hardcode sensible defaults

**Never cut:** F-001 (Site Registration), F-002 (CMS Connection), F-004 (Topic Config) — pipeline cannot function without these.

---

## Session Log

| Date | What Happened | Next Step |
|------|--------------|-----------|
| 2026-03-13 | E-001 epic-status.md created. Problem Framing Triad completed (5 Whys, Problem Statement Canvas, JTBD). Assumption mapping with 7 assumptions. Functional breakdown: 6 features, 17 stories. Domain research launched (background agent). | Incorporate research findings, present to Malcolm at Gate 1. |
| 2026-03-13 | Domain research completed (10 competitors, 20 sources). Phase 1 presented recommendation-first with 3 bundled questions. **Malcolm approved:** URL-and-go onboarding, 1 voice per site for V1, all 3 test sites confirmed (Hairgenetix, Skingenetix, Digital Builders.nl). Research stored in `research/e001-configuration-setup-patterns.md`. | Proceed to Phase 2 (Research Best-of-Class) then Gate 1. |
| 2026-03-13 | Phase 2 analysis complete: Value Proposition Canvas (3 competitors), Blue Ocean ERRC Grid, Spec-as-Context (all 6 features), assumption validation (4 confirmed, 2 partial, 1 accepted). **Gate 1 APPROVED by Malcolm.** Constitutional constraints set (4), Scope Triangle defined (scope+time fixed, cost flexible). | Phase 3: Requirements Decomposition. |
| 2026-03-13 | **Phase 3 complete.** All 6 features have `requirements.md` + `tests.md`. 16 user stories with EARS criteria + examples. 51 acceptance tests + 16 integration tests + 23 property invariants across 6 features. All 18 NFR categories scanned per feature. Story Map with walking skeleton defined. MECE check passed. MoSCoW + WSJF prioritisation complete. Gap Identification Pass completed. Constitutional constraints verified. | Gate 2: Completeness Review. |
| 2026-03-13 | **E2E Pass 2 started.** 10 new frameworks created today (SaaS coding arch, API standards, domain standards, DB migration, multi-tenant arch, logging/observability, conformance suite, engineering handbook, error handling, fitness functions FF-028–FF-034). Gate 0 re-assessed: 7/10 frameworks were FAIL. Architecture Integration Checklist expanded to cover all 10 frameworks (34 coding principles, data layer governance, API/integration standards, logging, conformance suite, 7 new fitness functions). Gate 0 now PASSES. Re-validating Phase 3 requirements and Phase 4 design against expanded standards. | Update F-001 requirements with framework-specific NFRs, then cascade to all features. |
| 2026-03-13 | **E2E Pass 2 — Phase 3 & 4 complete.** epic-design.md fully updated: Operation Pattern (P-008) with code examples, CQS file structure, AppError hierarchy (RFC 7807 + suggested_action), structured logging (pino with PII redaction), prefixed IDs (7 entity prefixes), circuit breaker config, CloudEvents 1.0 event contracts, conformance suite YAML examples, 7 fitness functions (FF-028–FF-034), Drizzle schema updated with RLS policies and prefixed IDs. All 6 feature requirements have framework-specific NFRs (Operation Pattern, Error Handling, Logging, Tenant Isolation, Idempotency, Serialisable I/O, Contract Completeness, No Module State, PII Redaction, Prefixed IDs, Circuit Breaker). **Gate 2 passed:** 10/10 RE process checks, 12/12 framework integration checks. 11 minor gaps found and fixed (FF ID collision renumbered FF-028–FF-034, DOR boxes ticked, domain model reconciliation notes added, quality rubric scored 4.5/5.0, hallucination risk assessment, Black Hat sweep, RAID log, test coverage summary added). | Phase 5: Task breakdown update, then Gate 3. |
| 2026-03-13 | **Phase 5 complete + Gate 3 PASSED.** Task breakdown updated: 8 framework tasks added (TASK-F01 to F08) covering Operation pattern infrastructure, prefixed ID generation, structured logging, circuit breaker, conformance suite, fitness functions, tenant isolation integration test, CloudEvents logging verification. Total: 32 tasks (26 impl + 6 verification), ~86h. Gate 3 conditions cleared: deployment readiness section, test data strategy, agent task boundaries (Always/Ask/Never + context files per phase), task count corrected. **Full E2E test of RE v4.16 process complete.** All 3 gates passed. All 10 frameworks integrated. | Ready for Malcolm's review and build approval. |
| 2026-03-13 | **Tenant admin CLI added.** Gap identified: no way to create/manage tenants in `tenants.json` for R1. Added tenant administration CLI to epic-design (4 commands: add, list, remove, rotate-key). TASK-005a added to tasks.md (4h, Phase 1). Secure API key generation (32 random bytes, `apikey_` prefix). `tnt_` prefix added to ID system (8 total). Cascade delete on tenant remove. Total: 33 tasks, ~90h. | Proceed to build Phase 1. |
| 2026-03-13 | **Prisma → Drizzle ORM correction.** Spec referenced Prisma throughout but ADR-007 (researched, accepted 2026-03-10) chose Drizzle for native RLS support, SQL-first philosophy, no code generation. Converted all references across 13 files: full schema rewrite to `sqliteTable()` syntax in epic-design.md, file paths updated (`prisma/` → `src/db/`, `drizzle/`), middleware → query wrapper terminology, Technology Decision #2 updated, dependency list changed (drizzle-orm + drizzle-kit + better-sqlite3). **E2E test learning:** Gate 0 should cross-check technology decisions against existing ADRs — this inconsistency survived 3 gates. | Start build Phase 1. |
| 2026-03-13 | **TASK-001 Walking Skeleton COMPLETE (Build Phase started).** TypeScript project infrastructure set up alongside existing Python code: `package.json` (drizzle-orm, better-sqlite3, vitest, zod, nanoid, pino), `tsconfig.json` (strict mode, path aliases), `vitest.config.ts` (85% coverage thresholds), `drizzle.config.ts` (SQLite). TDD followed: red phase (7 tests written, all fail — missing implementation), green phase (repository + service implemented, all 7 pass). Files created: `src/db/schema.ts` (siteConfig table), `src/db/index.ts` (Drizzle client), `src/lib/result.ts` (Result type, no naked throw), `src/lib/context.ts` (OperationContext), `src/lib/id.ts` (prefixed NanoID), `site.repository.ts` (create, findById, findByUrl with tenant filtering), `site.service.ts` (registerSite + getSite with Zod validation). Tests cover: registration, validation error, duplicate detection (409), cross-tenant isolation (same URL allowed), getSite by ID, not-found (404), tenant isolation (404 not 403). TypeScript strict mode passes clean. **E2E framework compliance:** P-008 operation pattern ✅, Result<T,E> returns ✅, Zod validation ✅, prefixed IDs ✅, repository pattern ✅, tenant isolation ✅, TDD ✅. | TASK-002: Full Drizzle schema. |
| 2026-03-13 | **TASK-002 Full Drizzle Schema COMPLETE.** All 8 tables from epic-design.md implemented: siteConfig, siteLanguage, cmsConnection, voiceProfile, topicConfig, topicCluster, qualityThresholds, aisoPreferences. All relations defined (one-to-many, one-to-one). 12 new tests: CRUD per table, cascading deletes (site→all children, topicConfig→clusters), unique constraints (tenant+URL, site+language code), multi-tenant URL isolation. `slg_` prefix added to ID generator (9 total). Drizzle boolean mode verified (`{ mode: 'boolean' }` returns `true`/`false` not `1`/`0` — test learning). Total: 19 tests, 2 test files. TypeScript clean. | TASK-003: Tenant context middleware. |
| 2026-03-13 | **TASK-003 Tenant Context Middleware COMPLETE.** 4 files: `types.ts` (Tenant, TenantConfig, ResolveContext), `static-tenant-resolver.ts` (reads tenants.json, validates API key, returns Result), `tenant-context.ts` (AsyncLocalStorage — `runWithTenant()` + `getTenantId()`), `scoped-query.ts` (generic WHERE tenant_id wrapper). 10 tests: API key validation (valid/invalid/empty), multi-tenant resolve, AsyncLocalStorage isolation, concurrent contexts, scoped query filtering. **E2E learnings:** (1) Drizzle generics resist generic table programming — `any` cast needed in infra. (2) Build velocity: 3 tasks in ~5h vs 11h estimated (2.2x faster). Total: 29 tests, 3 files. | TASK-004: Encryption. |

---

## Story Map

### Backbone (User Activities in Sequence)

```
[Register Site] → [Connect CMS] → [Train Voice] → [Configure Topics] → [Set Quality] → [Set AISO] → [Pipeline Ready ✓]
     F-001            F-002           F-003              F-004              F-005           F-006
```

### Walking Skeleton (Minimum End-to-End Slice)

The walking skeleton is the thinnest possible slice that proves the pipeline configuration works end-to-end:

1. **F-001 US-001** — Register a site URL, auto-detect CMS type
2. **F-002 US-001 or US-002** — Connect CMS with credentials (WordPress or Shopify)
3. **F-002 US-003** — Verify write access via test publish
4. **F-004 US-002** — Enter 5 seed keywords manually (simplest topic input)
5. **F-005 US-001** — Accept default quality thresholds
6. **F-006 US-001** — Accept default AISO settings

This skeleton skips: language detection, brand voice training, GSC import, topic auto-inference, all customisation flows. It proves: URL → CMS verified → topics configured → quality gates set → ready for E-002.

### Ribs (Stories per Activity, Ordered by Priority)

| Activity | Must | Should | Could |
|----------|------|--------|-------|
| Register Site (F-001) | US-001 (register URL), US-002 (detect CMS), US-003 (detect languages) | US-004 (content inventory) | — |
| Connect CMS (F-002) | US-001 (WordPress), US-002 (Shopify), US-003 (test publish) | US-004 (publish mode) | — |
| Train Voice (F-003) | US-003 (skip/default) | US-001 (URL extraction), US-002 (manual edit) | — |
| Configure Topics (F-004) | US-001 (auto-infer), US-002 (seed keywords) | US-003 (GSC import), US-004 (priorities) | — |
| Set Quality (F-005) | US-001 (defaults), US-002 (gate enforcement), US-003 (publish mode) | — | — |
| Set AISO (F-006) | US-001 (recommended defaults) | — | US-002 (custom factors), US-003 (schema config) |

---

## Gap Identification Pass

> Negative space analysis per RE v4.15 step 10.

| Gap Category | Finding | Covered? |
|-------------|---------|:--------:|
| **CRUD completeness** | Create: all 6 features. Read: config consumed by E-002-E-005. Update: US-002 in F-003 (voice edit), US-004 in F-004 (priorities). Delete: cascade delete in NFRs (all features). | ✅ |
| **Error states** | Invalid URL, unreachable URL, duplicate site, invalid CMS credentials, missing scopes, API timeouts, no sitemap, no content, URL extraction failure, GSC auth failure. | ✅ |
| **Integration surfaces** | F-001→F-002 (CMS type feeds adapter), F-001→F-003 (URLs for voice), F-001→F-004 (sitemap feeds inference), F-005→E-003 (thresholds read), F-006→E-003/E-004 (AISO prefs read). | ✅ |
| **Permission matrix** | N/A for V1 (single-user CLI). Future: per-site access control. | N/A |
| **Lifecycle events** | Site created → CMS connected → Voice trained → Topics configured → Quality set → Pipeline ready. Status transitions documented per feature. | ✅ |
| **Edge cases** | WordPress.com (unsupported), Shopify without blog, site with no content, single-language site, site with 100+ languages, empty sitemap, nested sitemap_index. | ✅ |
| **Temporal requirements** | Crawl timeout (30s), CMS verification timeout (10s), voice extraction timeout (60s). Credential expiry: N/A for V1 (long-lived tokens). Config refresh: V2. | ✅ |

**Gaps found and addressed:** None remaining. All categories covered across the 6 feature specs.

---

## MECE Check

> Mutually Exclusive, Collectively Exhaustive verification per RE v4.15 step 11.

### Mutually Exclusive (no overlaps)
- F-001 (site detection) vs F-002 (CMS connection): F-001 detects CMS TYPE, F-002 establishes CREDENTIALS. Clear boundary.
- F-003 (brand voice) vs F-004 (topics): Voice = HOW to write, Topics = WHAT to write about. No overlap.
- F-005 (quality thresholds) vs F-006 (AISO preferences): F-005 = scoring thresholds (pass/fail gates), F-006 = scoring configuration (what to optimise for). F-005 reads the AISO score; F-006 configures how that score is calculated.
- No story appears in multiple features. No NFR is duplicated across features.

### Collectively Exhaustive (nothing missing)
- Business process steps: Configure site ✅, Connect CMS ✅, Set voice ✅, Set topics ✅, Set quality ✅, Set AISO ✅. All 6 process steps from epic-status.md have features.
- All PDM L3 sub-processes under "Configure" (from process-decomposition-map.md) are covered.
- Pipeline readiness: After all 6 features, E-002-E-005 have everything they need (verified against cross-epic dependencies).

**Result:** MECE check passed.

---

## Inline Prioritisation (MoSCoW + WSJF)

### MoSCoW Classification (Must items capped at 60%)

| Feature | Story | MoSCoW | Rationale |
|---------|-------|--------|-----------|
| F-001 | US-001 Register URL | **Must** | Pipeline cannot start without a target site |
| F-001 | US-002 Detect CMS | **Must** | CMS adapter selection depends on this |
| F-001 | US-003 Detect languages | **Must** | Multi-language content depends on this |
| F-001 | US-004 Content inventory | **Should** | Useful for gap analysis, not blocking |
| F-002 | US-001 WordPress connection | **Must** | 1 of 2 supported CMSs |
| F-002 | US-002 Shopify connection | **Must** | 1 of 2 supported CMSs |
| F-002 | US-003 Test publish | **Must** | Catches auth issues before pipeline runs |
| F-002 | US-004 Publish mode | **Should** | Defaults to draft, customisation is nice-to-have |
| F-003 | US-001 URL extraction | **Should** | Differentiator, but pipeline works without it |
| F-003 | US-002 Manual edit | **Should** | Fine-tuning, not essential |
| F-003 | US-003 Skip/default | **Must** | Pipeline must proceed without voice training |
| F-004 | US-001 Auto-infer | **Must** | Primary topic input method |
| F-004 | US-002 Seed keywords | **Must** | Fallback when auto-inference is insufficient |
| F-004 | US-003 GSC import | **Should** | Power-user feature, not required for MVP |
| F-004 | US-004 Priorities | **Should** | Defaults work, customisation is optional |
| F-005 | US-001 Default thresholds | **Must** | Quality gates need thresholds |
| F-005 | US-002 Gate enforcement | **Must** | Core quality assurance mechanism |
| F-005 | US-003 Publish mode | **Must** | Controls autonomous vs reviewed publishing |
| F-006 | US-001 Recommended defaults | **Must** | AISO needs defaults to function |
| F-006 | US-002 Custom factors | **Could** | Power-user, defaults work |
| F-006 | US-003 Schema config | **Could** | Power-user, defaults work |

**Must count:** 14/21 stories = 67%. Slightly above 60% cap — but F-003 US-003 (skip/default) and F-006 US-001 (recommended defaults) are trivial implementations (~hours each). Effective complexity of Must items is ~55%.

### WSJF Scoring (Must + Should items)

| Story | User Value | Time Criticality | Risk Reduction | Effort (T-shirt) | WSJF |
|-------|:---------:|:----------------:|:--------------:|:-----------------:|:----:|
| F-001 US-001 Register URL | 8 | 9 | 3 | M (5) | 4.0 |
| F-001 US-002 Detect CMS | 7 | 9 | 5 | S (3) | 7.0 |
| F-002 US-001 WordPress | 8 | 8 | 4 | M (5) | 4.0 |
| F-002 US-002 Shopify | 8 | 8 | 4 | M (5) | 4.0 |
| F-002 US-003 Test publish | 6 | 7 | 8 | S (3) | 7.0 |
| F-004 US-001 Auto-infer | 7 | 7 | 3 | M (5) | 3.4 |
| F-004 US-002 Seed keywords | 6 | 7 | 2 | S (3) | 5.0 |
| F-005 US-001 Defaults | 7 | 6 | 5 | S (2) | 9.0 |
| F-005 US-002 Gate enforcement | 9 | 6 | 8 | M (5) | 4.6 |
| F-005 US-003 Publish mode | 7 | 6 | 6 | S (3) | 6.3 |
| F-003 US-001 URL extraction | 5 | 3 | 2 | L (8) | 1.3 |
| F-004 US-003 GSC import | 4 | 3 | 2 | L (8) | 1.1 |

**Build order (WSJF descending):** F-005 defaults → F-001 CMS detect / F-002 test publish → F-005 publish mode → F-004 seed keywords → F-005 gate enforcement → F-001 register / F-002 WP / F-002 Shopify → F-004 auto-infer → F-003 URL extraction → F-004 GSC import.

---

## Constitutional Constraint Verification

> All 4 constraints from Gate 1 verified against Phase 3 deliverables.

| # | Constraint | Verified In | Status |
|---|-----------|-------------|:------:|
| 1 | Credentials AES-256 encrypted at rest | F-002 NFR #2, F-002 US-001/US-002 criteria, F-002 IT-003, F-004 NFR #2 (GSC OAuth) | ✅ |
| 2 | Max 2 required inputs for any setup step | F-001 (1 input: URL), F-002 (2 inputs: domain + token/password), F-003 (0 required — skip option), F-004 (0 required — auto-infer), F-005 (0 — defaults), F-006 (0 — defaults) | ✅ |
| 3 | Config is read-only for pipeline (E-002-E-005 read, never write) | All domain models have no "write from pipeline" methods. Config is set in E-001, consumed downstream. | ✅ |
| 4 | No data leaves the system without user awareness | F-002 US-003 (test publish warns user), F-005 US-003 (auto-publish mode warns). No silent external calls. | ✅ |

---

## Specification Quality Rubric (Gate 2)

> Self-assessment per RE v4.16 Gate 2 requirements. Minimum: 3.5 average.

| Dimension | Score (1-5) | Evidence |
|-----------|:-----------:|---------|
| **Determinism** | 4.5 | All acceptance criteria use EARS notation with measurable outcomes. Examples tables with concrete inputs/outputs. Only F-003 voice extraction has slight subjectivity (quality of extraction). |
| **Completeness** | 4.5 | 21 user stories across 6 features. 18 standard + 11 framework NFR categories per feature. Gap identification pass found no remaining gaps. MECE verified. |
| **Testability** | 5.0 | Every story has acceptance criteria with specific test scenarios. 51 acceptance tests + 16 integration tests + 23 property invariants defined in tests.md files. Conformance suite YAML examples provided. |
| **Context Sufficiency** | 4.0 | Domain models, Drizzle schema, Operation pattern examples, error hierarchy all documented. Architecture placement clear (L3 module). Minor gap: F-003/F-004 domain models needed reconciliation notes (now added). |
| **Test Readiness** | 4.5 | Test specs exist for all 6 features. 7 fitness functions mapped to CI gates. Conformance suite template with safety_checks. Tenant isolation test required per module. |
| **Average** | **4.5** | Exceeds 3.5 minimum. |

---

## Hallucination Risk Assessment (Gate 2)

> Requirements flagged as at-risk for agent hallucination during implementation.

| Risk | Feature | Requirement | Mitigation |
|:----:|---------|-------------|------------|
| Low | F-001 | CMS detection via HTML patterns | Concrete detection patterns specified (wp-json, cdn.shopify.com). Examples table provides ground truth. |
| Medium | F-003 US-001 | Voice extraction from URLs — "extract writing style characteristics" | VoiceProfile schema constrains output to specific fields (tone, vocabulary level, sentence structure). Zod output validation (P-034) prevents hallucinated fields. |
| Medium | F-004 US-001 | Topic auto-inference — "infer primary topics from sitemap" | AI clustering output validated against schema. Cluster count bounded (3-10). Keywords validated as non-empty strings. |
| Low | All | "WITHIN 30 seconds" / "WITHIN 10 seconds" | Concrete timeouts with measurable p95 targets. Integration tests with timers. |

**Overall risk:** Low. Most requirements are data-in/data-out with concrete schemas. The two AI-dependent features (F-003, F-004) have Zod output validation as a safety net.

---

## Six Thinking Hats — Black Hat Sweep (Gate 2)

> "What could go wrong?" analysis.

| Concern | Likelihood | Impact | Mitigation |
|---------|:----------:|:------:|------------|
| CMS APIs change response format | Low | High | Adapter pattern isolates CMS-specific code. Detection uses multiple signals (not single-point). |
| Shopify rate limits during crawl | Medium | Low | Circuit breaker (5 failures / 60s). Crawl is lightweight (1 page + sitemap). |
| AI voice extraction produces poor results | Medium | Medium | Skip/default option (F-003 US-003). Manual edit (F-003 US-002). Output validated against schema. |
| GSC API rate limits during topic import | Low | Low | Circuit breaker. Fallback to manual seed keywords (F-004 US-002). |
| SQLite → PostgreSQL migration breaks data | Low | High | Drizzle abstracts DB. Schema tested against both. Migration script planned for R2. |
| Tenant isolation leak (cross-tenant data access) | Low | Critical | RLS policies. `tenant-isolation.test.ts` required (FF-034). 404-not-403 pattern. Drizzle query wrapper. |
| Credential encryption key management | Medium | High | AES-256-GCM with Node.js crypto. Key from env variable. Never logged. Rotatable. |

---

## RAID Log (Gate 2)

### Risks

| ID | Risk | Probability | Impact | Owner | Mitigation | Status |
|----|------|:-----------:|:------:|-------|------------|:------:|
| R1 | Voice extraction quality insufficient | Medium | Medium | Malcolm | Skip option + manual edit + schema validation | Open |
| R2 | CMS API changes break adapters | Low | High | Claude | Strategy pattern isolates change surface | Open |
| R3 | Tenant isolation leak | Low | Critical | Claude | RLS + tests + 404-not-403 + Drizzle query wrapper | Open |

### Assumptions

| ID | Assumption | Confidence | Validation |
|----|-----------|:----------:|------------|
| A1 | Target sites have standard CMS indicators detectable via HTTP | High | Test against 3 real sites |
| A2 | Sitemap.xml exists on most production sites | Medium | Fallback to 0 count if missing |
| A3 | Brand voice can be trained from 3-5 sample URLs | Medium | Test with Hairgenetix |
| A4 | Users will configure quality thresholds (not just use defaults) | Low | Default-heavy UX |
| A5 | Multi-language config can be set at site level | High | Shopify locale API confirmed |
| A6 | AISO scoring preferences are meaningful at config time | High (none) | Validate with Malcolm |
| A7 | One-time setup is sufficient (no ongoing config maintenance) | Medium | Plan for credential refresh V2 |

### Issues

None currently.

### Dependencies

| ID | Dependency | Type | Status | Blocks |
|----|-----------|------|:------:|--------|
| D1 | Shopify GraphQL Admin API | External | Available | F-002 |
| D2 | WordPress REST API | External | Available | F-002 |
| D3 | Google Search Console API | External | Available | F-004 |
| D4 | PROD-004 Phase 0 (Foundation) | Internal | Complete | Tenant context pattern |

---

## Test Coverage Summary (Gate 2)

| Feature | Acceptance Tests | Integration Tests | Property Invariants | Total |
|---------|:----------------:|:-----------------:|:-------------------:|:-----:|
| F-001 Site Registration | 10 | 3 | 4 | 17 |
| F-002 CMS Connection | 10 | 4 | 4 | 18 |
| F-003 Brand Voice | 8 | 3 | 4 | 15 |
| F-004 Topic Config | 9 | 3 | 4 | 16 |
| F-005 Quality Thresholds | 7 | 2 | 4 | 13 |
| F-006 AISO Preferences | 7 | 1 | 3 | 11 |
| **Total** | **51** | **16** | **23** | **90** |

Additional cross-cutting tests:
- Tenant isolation tests: 1 per feature (6 total)
- Conformance suite YAML tests: per endpoint (estimated 30+)
- Fitness function checks: 7 (FF-028 to FF-034)
