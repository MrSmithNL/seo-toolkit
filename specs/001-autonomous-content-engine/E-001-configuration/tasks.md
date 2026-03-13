---
id: "EPC-CONFIG-001"
type: epic-tasks
title: "Configuration & Setup"
project: PROD-001
domain: configuration
parent: "THM-CE-001"
status: draft
phase: 5-tasks
created: 2026-03-13
last_updated: 2026-03-13
total_tasks: 33
completed_tasks: 0
refs:
  requirements: "./F-*/requirements.md"
  design: "./epic-design.md"

# === PARENT ALIGNMENT ===
parent_baseline:
  id: "THM-CE-001"
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

# Configuration & Setup — Tasks

## Implementation Order

Tasks are ordered by dependency. Each task should take 2-8 hours. Tasks marked [P] can run in parallel.

**Foundation-first ordering (mandatory):**

1. **Walking skeleton** — thinnest end-to-end slice: register a site → detect CMS → store config → read config back
2. **Data models / schemas** — Prisma schema, migrations, tenant context
3. **Domain logic** — business rules, detection algorithms, encryption
4. **API / service layer** — CLI commands, service functions, validation
5. **Integration** — external HTTP calls, CMS adapters

## Phase 1: Foundation (Walking Skeleton + Data Layer)

- [ ] **TASK-001:** Walking skeleton — register a site URL, store in database, read it back
  - Story: US-001 (F-001)
  - Files: `src/modules/content-engine/config/index.ts`, `prisma/schema.prisma`, `prisma/migrations/`, `src/modules/content-engine/config/site-registration/site.repository.ts`, `src/modules/content-engine/config/site-registration/site.service.ts`, `vitest.config.ts`
  - TDD: [ ] Red (tests fail) → [ ] Green (tests pass) → [ ] Refactor
  - Done when: `registerSite("https://example.com")` creates a row in `site_config` table with `tenant_id`, `getSite(id)` returns it. Tests pass.
  - Dependencies: none
  - Est: 4h

- [ ] **TASK-002:** Prisma schema — full data model for all 6 features
  - Story: All features (data layer)
  - Files: `prisma/schema.prisma`, `prisma/migrations/YYYYMMDD_initial_schema/`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: All 8 models from `epic-design.md` §Shared Data Model are in schema, migration runs cleanly, TypeScript types generated. All relations and cascading deletes verified by test.
  - Dependencies: TASK-001
  - Est: 3h

- [ ] **TASK-003:** Tenant context middleware — `StaticTenantResolver` + Prisma middleware
  - Story: Cross-cutting (multi-tenancy)
  - Files: `src/lib/tenant/static-tenant-resolver.ts`, `src/lib/tenant/tenant-middleware.ts`, `src/lib/tenant/types.ts`, `tenants.json`, `src/lib/tenant/__tests__/tenant.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `StaticTenantResolver` reads `tenants.json`, validates API key, sets `tenantId` in AsyncLocalStorage. Prisma middleware auto-filters all queries by `tenantId`. Tests verify tenant isolation (query with tenant A cannot see tenant B's data).
  - Dependencies: TASK-001
  - Est: 4h

- [ ] **TASK-004:** Encryption utility — AES-256-GCM encrypt/decrypt for credentials
  - Story: US-001, US-002 (F-002 — Constitutional Constraint #1)
  - Files: `src/lib/crypto/encrypt.ts`, `src/lib/crypto/__tests__/encrypt.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `encrypt(plaintext, key)` returns `{iv, ciphertext, tag}`. `decrypt(encrypted, key)` returns original plaintext. Key derived from `ENCRYPTION_KEY` env var. Tests verify roundtrip, tamper detection (modified ciphertext fails), different keys produce different ciphertext.
  - Dependencies: none
  - Est: 2h

- [ ] **TASK-005a:** Tenant administration CLI — add, list, remove, rotate-key commands
  - Story: Cross-cutting (tenant management — fills gap between manual JSON editing and PROD-004 SaaS)
  - Files: `src/lib/tenant/tenant-admin.ts`, `src/lib/tenant/__tests__/tenant-admin.test.ts`, `src/cli/tenant.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `seo-toolkit tenant add --name "Test" --plan agency` generates secure API key (32 random bytes, `apikey_` prefix) and writes to `tenants.json`. `tenant list` shows all tenants in table format. `tenant remove <id>` prompts for confirmation, cascades to delete associated site configs. `tenant rotate-key <id>` invalidates old key immediately. `tenants.json` is in `.gitignore`. Prefixed tenant IDs use `tnt_` prefix. All 4 commands have unit tests.
  - Dependencies: TASK-003, TASK-F02
  - Est: 4h

- [ ] **TASK-F01:** Operation pattern infrastructure — OperationContext, Result type, error hierarchy
  - Story: Cross-cutting (NFR 19-20 all features)
  - Files: `src/lib/operations/context.ts`, `src/lib/operations/result.ts`, `src/lib/operations/errors.ts`, `src/lib/operations/logging.ts`, `src/lib/operations/__tests__/operations.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `OperationContext` type (tenantId + correlationId + idempotencyKey) defined. `Result<T, E>` type with `ok()` and `err()` helpers. `SiteOperationError` extends `OperationError` with factory methods (validation, notFound, cmsUnreachable, circuitOpen, authFailed, conflict). `withOperationLogging()` wrapper emits `operation.started`, `operation.completed`, `operation.failed`. All return RFC 7807 with `suggested_action`.
  - Dependencies: none
  - Est: 4h

- [ ] **TASK-F02:** Prefixed ID generation utility
  - Story: Cross-cutting (NFR 24 all features)
  - Files: `src/lib/ids/generate.ts`, `src/lib/ids/__tests__/generate.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `generateId('site')` → `ste_xxxxxxxxxxxxxxxx`. All 8 prefixes work (ste, cms, vce, tpc, tcl, qty, asp, tnt). IDs are 20+ chars. NanoID used. Unit tests verify prefix and length.
  - Dependencies: none
  - Est: 1h

- [ ] **TASK-F03:** Structured logging setup — pino with PII redaction
  - Story: Cross-cutting (NFR 21, 28 all features)
  - Files: `src/lib/logging/logger.ts`, `src/lib/logging/__tests__/logger.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: pino configured with JSON output, `redact` paths for `*.password`, `*.token`, `*.secret`, `*.accessToken`, `*.email`, `*.phone`, `*.ip`. ISO 8601 timestamps. Service name set. Tests verify PII fields show `[REDACTED]`.
  - Dependencies: none
  - Est: 2h

- [ ] **TASK-F04:** Circuit breaker wrapper for external HTTP calls
  - Story: Cross-cutting (NFR 29 for F-001, F-002, F-003, F-004)
  - Files: `src/lib/http/circuit-breaker.ts`, `src/lib/http/__tests__/circuit-breaker.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Circuit breaker with 5 failures / 60s window → open for 30s. Returns `SiteOperationError.circuitOpen()` when open. State transitions logged. Half-open recovery works. Tests verify open/closed/half-open states.
  - Dependencies: TASK-F01
  - Est: 3h

Phase 1 parallel groups:
  Group A: TASK-002, TASK-003 (both depend on TASK-001)
  Group B: TASK-004, TASK-F01, TASK-F02, TASK-F03 (independent — no dependencies)
  Group C: TASK-F04 (depends on TASK-F01)
  Group D: TASK-005a (depends on TASK-003 + TASK-F02)
  → TASK-001 runs first. Then Groups A and B run in parallel. TASK-F04 starts when TASK-F01 completes. TASK-005a starts when TASK-003 and TASK-F02 complete.

## Phase 2: Domain Logic (Detection + Adapters)

- [ ] **TASK-005:** URL normalisation + validation logic
  - Story: US-001 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/url.ts`, `src/modules/content-engine/config/site-registration/__tests__/url.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `normaliseUrl("hairgenetix.com")` → `https://www.hairgenetix.com`. Handles: add https://, strip trailing slash, resolve www/non-www, reject invalid URLs. All examples from F-001 US-001 pass.
  - Dependencies: TASK-001
  - Est: 2h

- [ ] **TASK-006:** CMS detection logic (WordPress + Shopify detectors)
  - Story: US-002 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/detectors/wordpress.ts`, `src/modules/content-engine/config/site-registration/detectors/shopify.ts`, `src/modules/content-engine/config/site-registration/detectors/types.ts`, `src/modules/content-engine/config/site-registration/__tests__/detectors.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Pluggable detector pattern works. WordPress detector checks `/wp-json/wp/v2/` endpoint. Shopify detector checks for `cdn.shopify.com` in HTML. Unknown fallback works. All examples from F-001 US-002 pass (mocked HTTP).
  - Dependencies: TASK-001
  - Est: 3h

- [ ] **TASK-007:** Language detection logic (hreflang + Shopify locales + html lang)
  - Story: US-003 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/detectors/language.ts`, `src/modules/content-engine/config/site-registration/__tests__/language.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Detects languages from hreflang tags, Shopify locale URLs, WPML alternate links, html lang attribute. Fallback to "en". All examples from F-001 US-003 pass (mocked HTTP).
  - Dependencies: TASK-001
  - Est: 3h

- [ ] **TASK-008:** Sitemap parser — content inventory
  - Story: US-004 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/sitemap.ts`, `src/modules/content-engine/config/site-registration/__tests__/sitemap.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Parses `sitemap.xml` and `sitemap_index.xml`. Counts content URLs (excludes images/CSS/JS). Returns 0 with note if no sitemap found. All examples from F-001 US-004 pass.
  - Dependencies: TASK-001
  - Est: 2h

- [ ] **TASK-009:** CMS adapter interfaces + WordPress adapter [P]
  - Story: US-001 (F-002)
  - Files: `src/modules/content-engine/config/cms-connection/adapters/types.ts`, `src/modules/content-engine/config/cms-connection/adapters/wordpress.ts`, `src/modules/content-engine/config/cms-connection/__tests__/wordpress.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `CMSAdapter` interface defined (connect, verify, testPublish, publish, unpublish). `WordPressAdapter` implements it. Validates credentials via GET `/wp-json/wp/v2/users/me`. Creates test draft post and deletes it. Credentials encrypted before storage. All examples from F-002 US-001, US-003 pass (mocked HTTP).
  - Dependencies: TASK-002, TASK-004
  - Est: 4h

- [ ] **TASK-010:** Shopify adapter [P]
  - Story: US-002 (F-002)
  - Files: `src/modules/content-engine/config/cms-connection/adapters/shopify.ts`, `src/modules/content-engine/config/cms-connection/__tests__/shopify.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `ShopifyAdapter` implements `CMSAdapter`. Validates token via GraphQL Admin API. Checks `read_content` + `write_content` scopes. Creates test article and deletes it. All examples from F-002 US-002, US-003 pass (mocked HTTP).
  - Dependencies: TASK-009
  - Est: 3h

Phase 2 parallel groups:
  Group A: TASK-005, TASK-006, TASK-007, TASK-008 (all depend only on TASK-001, independent of each other)
  Group B: TASK-009 (depends on TASK-002 + TASK-004)
  Group C: TASK-010 (depends on TASK-009)
  → Groups A and B can run in parallel once their deps complete. TASK-010 waits for TASK-009.

## Phase 3: Services + AI Features

- [ ] **TASK-011:** Site registration service — orchestrate crawl pipeline
  - Story: US-001, US-002, US-003, US-004 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/site.service.ts` (update), `src/modules/content-engine/config/site-registration/__tests__/site.service.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `registerSite(url)` normalises URL → stores site → detects CMS → detects languages → counts content → emits `site.registered` + `site.crawled` events. Retry on crawl failure (once after 5s). All F-001 acceptance criteria met. Integration test with mocked HTTP passes.
  - Dependencies: TASK-005, TASK-006, TASK-007, TASK-008
  - Est: 4h

- [ ] **TASK-012:** CMS connection service — connect, verify, manage
  - Story: US-001, US-002, US-003, US-004 (F-002)
  - Files: `src/modules/content-engine/config/cms-connection/cms.service.ts`, `src/modules/content-engine/config/cms-connection/cms.repository.ts`, `src/modules/content-engine/config/cms-connection/__tests__/cms.service.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `connectCMS(siteId, type, credentials)` selects adapter → validates → encrypts credentials → stores → runs test publish → emits `cms.connected` + `cms.verified`. State machine enforced (pending → verified/failed). Default publish status configurable. All F-002 acceptance criteria met.
  - Dependencies: TASK-009, TASK-010, TASK-003
  - Est: 4h

- [ ] **TASK-013:** Brand voice extraction service [P]
  - Story: US-001, US-002, US-003 (F-003)
  - Files: `src/modules/content-engine/config/brand-voice/voice.service.ts`, `src/modules/content-engine/config/brand-voice/voice.repository.ts`, `src/modules/content-engine/config/brand-voice/extraction-prompt.ts`, `src/modules/content-engine/config/brand-voice/__tests__/voice.service.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `extractVoice(siteId, urls)` fetches page content → sends to LLM → parses structured JSON → stores VoiceProfile. Manual parameter editing works. Skip/default produces sensible defaults. `voice.extracted` event emitted. Token budget ≤4000. All F-003 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 5h

- [ ] **TASK-014:** Topic configuration service [P]
  - Story: US-001, US-002, US-003, US-004 (F-004)
  - Files: `src/modules/content-engine/config/topic-config/topic.service.ts`, `src/modules/content-engine/config/topic-config/topic.repository.ts`, `src/modules/content-engine/config/topic-config/clustering.ts`, `src/modules/content-engine/config/topic-config/__tests__/topic.service.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `inferTopics(siteId)` auto-extracts from site content. `setTopics(siteId, keywords)` accepts manual input. `importFromGSC(siteId, creds)` imports from Search Console. All inputs cluster into `TopicCluster` entities with priorities. `topics.configured` event emitted. All F-004 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 5h

- [ ] **TASK-015:** Quality thresholds service [P]
  - Story: US-001, US-002, US-003 (F-005)
  - Files: `src/modules/content-engine/config/quality-thresholds/quality.service.ts`, `src/modules/content-engine/config/quality-thresholds/quality.repository.ts`, `src/modules/content-engine/config/quality-thresholds/__tests__/quality.service.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Defaults created on site registration (seo_score_min=65, aiso_score_min=7.0, readability=grade_8, word_count=1500-3000, publish=draft_review). Thresholds editable. Validation prevents invalid ranges. Falls back to defaults on corruption. All F-005 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 3h

- [ ] **TASK-016:** AISO preferences service [P]
  - Story: US-001, US-002, US-003 (F-006)
  - Files: `src/modules/content-engine/config/aiso-preferences/aiso.service.ts`, `src/modules/content-engine/config/aiso-preferences/aiso.repository.ts`, `src/modules/content-engine/config/aiso-preferences/factor-registry.ts`, `src/modules/content-engine/config/aiso-preferences/__tests__/aiso.service.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Defaults created with `use_recommended=true`. Factor registry contains all 36 factors grouped in 6 categories. Custom factor selection works when `use_recommended=false`. Schema type configuration works. Falls back to recommended on corruption. All F-006 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 3h

Phase 3 parallel groups:
  Group A: TASK-013, TASK-014, TASK-015, TASK-016 (all depend on TASK-002 + TASK-003, independent of each other)
  Group B: TASK-011 (depends on TASK-005-008)
  Group C: TASK-012 (depends on TASK-009 + TASK-010 + TASK-003)
  → Groups A and B can start as soon as their deps complete. Group C waits for CMS adapters.

## Phase 4: Integration + Module Manifest

- [ ] **TASK-017:** Module manifest + event bus integration
  - Story: Cross-cutting (architecture)
  - Files: `src/modules/content-engine/module-manifest.json`, `src/modules/content-engine/config/events.ts`, `src/modules/content-engine/config/__tests__/events.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: `module-manifest.json` matches the spec from `epic-design.md`. Event bus wired: all 7 events (`site.registered`, `site.crawled`, `cms.connected`, `cms.verified`, `voice.extracted`, `topics.configured`, `config.complete`) emit correctly with typed payloads. Event subscribers can receive and type-check payloads.
  - Dependencies: TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-016
  - Est: 3h

- [ ] **TASK-018:** Configuration completeness orchestrator
  - Story: Cross-cutting (pipeline readiness)
  - Files: `src/modules/content-engine/config/orchestrator.ts`, `src/modules/content-engine/config/__tests__/orchestrator.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Orchestrator tracks which config features are complete per site. Emits `config.complete` when all Must-have features (F-001, F-002, F-004) are done. Reports config status showing which features are configured/pending. Pipeline won't start without minimum config.
  - Dependencies: TASK-017
  - Est: 3h

- [ ] **TASK-F05:** Conformance suite YAML tests — expected I/O for all endpoints
  - Story: Cross-cutting (architecture — conformance suite template)
  - Files: `tests/conformance/site-registration.yaml`, `tests/conformance/cms-connection.yaml`, `tests/conformance/brand-voice.yaml`, `tests/conformance/topic-config.yaml`, `tests/conformance/quality-thresholds.yaml`, `tests/conformance/aiso-preferences.yaml`, `tests/conformance/runner.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: YAML test cases cover: happy path CRUD, validation errors, tenant isolation (404 not 403), idempotency, business rules per feature. Runner executes YAML cases against API endpoints. All `safety_checks` documented. ≥5 cases per feature.
  - Dependencies: TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-016
  - Est: 4h

- [ ] **TASK-F06:** Fitness function CI checks (FF-028 to FF-034)
  - Story: Cross-cutting (architecture — fitness functions)
  - Files: `tests/architecture/fitness-functions.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: 7 fitness functions pass: FF-028 (module ≤10 files, ≤2000 lines), FF-029 (every command/query has Zod + return type), FF-030 (Result return + OperationContext param), FF-031 (`.safeParse` in every handler), FF-032 (no `throw` in `src/api/`), FF-033 (no `let`/`var` at module scope in `src/`), FF-034 (`tenant-isolation.test.ts` exists).
  - Dependencies: TASK-017
  - Est: 3h

- [ ] **TASK-F07:** Tenant isolation integration test
  - Story: Cross-cutting (NFR 22 all features — FF-034)
  - Files: `tests/integration/tenant-isolation.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Tests verify: Tenant A creates site → Tenant B queries same ID → gets 404 (not 403). Tenant B creates site → Tenant A cannot see it in list. Covers all 6 entity types. All CRUD operations tested.
  - Dependencies: TASK-003, TASK-011
  - Est: 3h

- [ ] **TASK-F08:** CloudEvents event logging verification
  - Story: Cross-cutting (NFR 21 — logging standards §14)
  - Files: `tests/integration/event-logging.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: All 7 events emit with CloudEvents 1.0 envelope (specversion, id, source, type, time, tenantid, correlationid). Emit and consume are both logged as structured JSON. Tests capture log output and verify fields.
  - Dependencies: TASK-017
  - Est: 2h

Phase 4 parallel groups:
  Group A: TASK-017 (depends on all Phase 3 tasks)
  Group B: TASK-F05 (depends on all Phase 3 tasks — can run parallel with TASK-017)
  Group C: TASK-F07 (depends on TASK-003 + TASK-011 — can start earlier)
  Group D: TASK-018, TASK-F06, TASK-F08 (depend on TASK-017)
  → TASK-017 and TASK-F05 can run in parallel. TASK-F07 can start in Phase 3. TASK-018, TASK-F06, TASK-F08 run after TASK-017.

## Deployment Readiness

| Aspect | Plan |
|--------|------|
| **Deployment target** | Local CLI — `npm link` in seo-toolkit repo |
| **Feature flag** | `content-engine-v1` (on/off via `tenants.json` per tenant) |
| **Staging** | Run against real sites: hairgenetix.com, skingenetix.com, digitalbouwers.nl |
| **Rollback** | `git revert` + `prisma migrate reset` to drop schema |
| **Monitoring** | pino structured logs to stdout, review manually for R1 |

## Test Data Strategy

Test data approach: mocked HTTP responses for unit/integration tests (no real network calls in CI). Conformance suite uses fixture data modelled on real sites (hairgenetix.com = Shopify multi-lang, digitalbouwers.nl = WordPress single-lang, skingenetix.com = Shopify dual-lang). Test tenant IDs: `tenant_test_a`, `tenant_test_b`. Encryption tests use deterministic keys. AI/LLM responses (F-003) use fixture JSON — never call real LLM in tests.

## Agent Task Boundaries

**Always (autonomous, no approval needed):**
- Create/modify files within `src/modules/content-engine/config/`
- Create/modify test files within `tests/`
- Run tests via `pnpm test`
- Generate Prisma client

**Ask (confirm before proceeding):**
- Add new npm dependencies
- Modify `prisma/schema.prisma` beyond the spec
- Create files outside the module boundary
- Modify CI/CD config

**Never (hard block):**
- Push to main without PR
- Delete existing tests
- Modify files outside `seo-toolkit/` repo
- Store secrets in code

**Context files per phase:**
- Phase 1: Read `epic-design.md` (Prisma schema, tenant resolver, Operation pattern)
- Phase 2: Read `F-001/requirements.md`, `F-002/requirements.md` (detection logic, adapters)
- Phase 3: Read all `F-*/requirements.md` + `F-*/tests.md` (acceptance criteria)
- Phase 4: Read `epic-design.md` (module manifest, events), `tasks.md` (verification checklist)

## Verification Tasks

- [ ] **TASK-V01:** Run full test suite — all tests pass, coverage ≥ 85%
- [ ] **TASK-V02:** Manual walkthrough of all user stories against acceptance criteria (21 stories across 6 features)
- [ ] **TASK-V03:** Verify all NFRs (performance: crawl <30s + CMS verify <10s + config read <100ms; security: AES-256, no plaintext credentials; reliability: retry + fallback)
- [ ] **TASK-V04:** Update documentation (CLAUDE.md, README with setup instructions)
- [ ] **TASK-V05:** Security review — no secrets in logs, encryption verified, API keys in .env only, credential redaction confirmed
- [ ] **TASK-V06:** Architecture guardrails verified — import directions correct, module boundary respected, no config → stages imports, tenant isolation confirmed

## Summary

| Phase | Tasks | Est. Hours | Calendar | Parallel Groups |
|-------|:-----:|:----------:|----------|:---------------:|
| 1. Foundation + Framework Infra | 4 + 4 + 1 = 9 | 13h + 10h + 4h = 27h | Week 1 | 4 |
| 2. Domain Logic | 6 | 17h | Week 1-2 | 3 |
| 3. Services + AI | 6 | 24h | Week 2 | 3 |
| 4. Integration + Framework Verification | 2 + 4 = 6 | 6h + 12h = 18h | Week 2 | 4 |
| Verification | 6 | 4h | Week 2 | — |
| **Total** | **33** | **~90h** | **~2 weeks** | |

Critical path: TASK-001 → TASK-002 → TASK-009 → TASK-010 → TASK-012 → TASK-017 → TASK-F06 → TASK-018
Parallelism ratio: 22 of 26 implementation tasks can run in parallel with at least one other task

Framework infrastructure tasks (TASK-F01 to F04) are mostly independent and can run in parallel with Phase 1 foundation tasks, adding minimal calendar time despite 10h of effort.

## Story Coverage Check

> **MANDATORY.** Every user story from requirements.md must map to at least one task.

| Story | Feature | Task(s) | Covered? |
|-------|---------|---------|:--------:|
| US-001 (Register site by URL) | F-001 | TASK-001, TASK-005, TASK-011 | Yes |
| US-002 (Auto-detect CMS) | F-001 | TASK-006, TASK-011 | Yes |
| US-003 (Detect languages) | F-001 | TASK-007, TASK-011 | Yes |
| US-004 (Crawl content inventory) | F-001 | TASK-008, TASK-011 | Yes |
| US-001 (Connect WordPress) | F-002 | TASK-009, TASK-012 | Yes |
| US-002 (Connect Shopify) | F-002 | TASK-010, TASK-012 | Yes |
| US-003 (Test publish verification) | F-002 | TASK-009, TASK-010, TASK-012 | Yes |
| US-004 (Default publish status) | F-002 | TASK-012 | Yes |
| US-001 (Extract voice from URLs) | F-003 | TASK-013 | Yes |
| US-002 (Edit voice parameters) | F-003 | TASK-013 | Yes |
| US-003 (Skip/default voice) | F-003 | TASK-013 | Yes |
| US-001 (Auto-infer topics) | F-004 | TASK-014 | Yes |
| US-002 (Seed keywords) | F-004 | TASK-014 | Yes |
| US-003 (GSC import) | F-004 | TASK-014 | Yes |
| US-004 (Cluster priorities) | F-004 | TASK-014 | Yes |
| US-001 (Default thresholds) | F-005 | TASK-015 | Yes |
| US-002 (Gate enforcement) | F-005 | TASK-015 | Yes |
| US-003 (Publish mode) | F-005 | TASK-015 | Yes |
| US-001 (Recommended AISO) | F-006 | TASK-016 | Yes |
| US-002 (Custom AISO factors) | F-006 | TASK-016 | Yes |
| US-003 (Schema types) | F-006 | TASK-016 | Yes |

**All 21 stories covered.** No gaps.

## Framework NFR Coverage Check

> **MANDATORY.** Every framework-specific NFR must map to at least one task.

| NFR | Category | Task(s) | Covered? |
|-----|----------|---------|:--------:|
| NFR 19 | Operation Pattern (P-008) | TASK-F01, all Phase 3 tasks | Yes |
| NFR 20 | Error Handling (RFC 7807) | TASK-F01, all Phase 3 tasks | Yes |
| NFR 21 | Structured Logging (pino) | TASK-F03, TASK-F08 | Yes |
| NFR 22 | Tenant Isolation (RLS) | TASK-003, TASK-F07 | Yes |
| NFR 23 | Idempotency | TASK-F01, TASK-F05 | Yes |
| NFR 24 | Prefixed IDs | TASK-F02 | Yes |
| NFR 25 | Serialisable I/O | TASK-F01 (Result type uses plain objects) | Yes |
| NFR 26 | Contract Completeness | TASK-F06 (FF-029) | Yes |
| NFR 27 | No Module State | TASK-F06 (FF-033) | Yes |
| NFR 28 | PII Redaction | TASK-F03 | Yes |
| NFR 29 | Circuit Breaker | TASK-F04 | Yes |
| — | Conformance Suite | TASK-F05 | Yes |
| — | Fitness Functions (FF-028–FF-034) | TASK-F06 | Yes |
| — | CloudEvents Logging | TASK-F08, TASK-017 | Yes |

**All 11 framework NFRs + 3 cross-cutting requirements covered.** No gaps.
