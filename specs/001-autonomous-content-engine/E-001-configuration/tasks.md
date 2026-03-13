---
id: "EPC-CONFIG-001"
type: epic-tasks
title: "Configuration & Setup"
project: PROD-001
domain: configuration
parent: "THM-CE-001"
status: complete
phase: 6-build
created: 2026-03-13
last_updated: 2026-03-13
total_tasks: 33
completed_tasks: 33
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
2. **Data models / schemas** — Drizzle schema, migrations, tenant context
3. **Domain logic** — business rules, detection algorithms, encryption
4. **API / service layer** — CLI commands, service functions, validation
5. **Integration** — external HTTP calls, CMS adapters

## Phase 1: Foundation (Walking Skeleton + Data Layer)

- [x] **TASK-001:** Walking skeleton — register a site URL, store in database, read it back ✅
  - Story: US-001 (F-001)
  - Files: `src/modules/content-engine/config/index.ts`, `src/db/schema.ts`, `src/db/index.ts`, `src/lib/result.ts`, `src/lib/context.ts`, `src/lib/id.ts`, `src/modules/content-engine/config/site-registration/site.repository.ts`, `src/modules/content-engine/config/site-registration/site.service.ts`, `vitest.config.ts`, `package.json`, `tsconfig.json`, `drizzle.config.ts`
  - TDD: [x] Red (tests fail) → [x] Green (tests pass) → [ ] Refactor
  - Done when: `registerSite("https://example.com")` creates a row in `site_config` table with `tenant_id`, `getSite(id)` returns it. Tests pass.
  - Result: 7 tests pass (register, validation, duplicate detection, tenant isolation, getSite, not-found, cross-tenant 404)
  - Dependencies: none
  - Est: 4h | Actual: ~2h

- [x] **TASK-002:** Drizzle schema — full data model for all 6 features ✅
  - Story: All features (data layer)
  - Files: `src/db/schema.ts`, `src/db/schema.test.ts`, `src/lib/id.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: All 8 tables from `epic-design.md` §Shared Data Model are in schema, TypeScript types inferred. All relations and cascading deletes verified by test.
  - Result: 12 tests pass (CRUD for all 8 tables, cascading deletes site→children, topicConfig→clusters, unique constraints, multi-tenant URL isolation). `slg_` prefix added to ID generator (9 total).
  - Dependencies: TASK-001
  - Est: 3h | Actual: ~1h

- [x] **TASK-003:** Tenant context middleware — `StaticTenantResolver` + Drizzle query wrapper ✅
  - Story: Cross-cutting (multi-tenancy)
  - Files: `src/lib/tenant/types.ts`, `src/lib/tenant/static-tenant-resolver.ts`, `src/lib/tenant/tenant-context.ts`, `src/lib/tenant/scoped-query.ts`, `src/lib/tenant/tenant.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `StaticTenantResolver` reads `tenants.json`, validates API key, sets `tenantId` in AsyncLocalStorage. Drizzle query wrapper auto-adds `WHERE tenant_id = ?` to all queries. Tests verify tenant isolation (query with tenant A cannot see tenant B's data).
  - Result: 10 tests pass. StaticTenantResolver returns Result (not throw), AsyncLocalStorage isolates concurrent tenant contexts, scopedQuery filters by tenant_id. E2E learning: Drizzle's generic table types are complex — `any` cast needed for `db.from()` with generic table parameter (acceptable trade-off, typed at call site).
  - Dependencies: TASK-001
  - Est: 4h | Actual: ~1h

- [x] **TASK-004:** Encryption utility — AES-256-GCM encrypt/decrypt for credentials ✅
  - Story: US-001, US-002 (F-002 — Constitutional Constraint #1)
  - Files: `src/lib/crypto/encrypt.ts`, `src/lib/crypto/encrypt.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `encrypt(plaintext, key)` returns `{iv, ciphertext, tag}`. `decrypt(encrypted, key)` returns original plaintext. Key derived from `ENCRYPTION_KEY` env var. Tests verify roundtrip, tamper detection (modified ciphertext fails), different keys produce different ciphertext.
  - Result: 12 tests pass. Roundtrip (plain, unicode, empty string), random IV (same input → different output), different keys → different ciphertext, wrong key throws, tampered ciphertext throws, tampered tag throws, deriveKey determinism and uniqueness.
  - Dependencies: none
  - Est: 2h | Actual: ~20min

- [x] **TASK-005a:** Tenant administration — add, list, remove, rotate-key ✅
  - Story: Cross-cutting (tenant management — fills gap between manual JSON editing and PROD-004 SaaS)
  - Files: `src/lib/tenant/tenant-admin.ts`, `src/lib/tenant/__tests__/tenant-admin.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `TenantAdmin.add()` generates secure API key (32 random bytes hex, `apikey_` prefix) and writes to `tenants.json`. `list()` returns all tenants. `remove(id)` deletes tenant + API key. `rotateKey(id)` invalidates old key immediately, issues new one. `tenants.json` is in `.gitignore`. Prefixed tenant IDs use `tnt_` prefix.
  - Result: 16 tests pass. Add (prefixed ID, API key, persistence, multiple, unique keys, default plan). List (empty, all, pre-existing JSON). Remove (by ID, non-existent returns false, persists). RotateKey (new key, old key gone, same tenant, non-existent returns null, persists). CLI wrapper deferred — service layer is the value.
  - Dependencies: TASK-003, TASK-F02
  - Est: 4h | Actual: ~15min

- [x] **TASK-F01:** Operation pattern infrastructure — OperationContext, Result type, error hierarchy ✅ (completed as part of TASK-001)
  - Story: Cross-cutting (NFR 19-20 all features)
  - Files: `src/lib/context.ts`, `src/lib/result.ts` (built during walking skeleton)
  - Result: `OperationContext` (tenantId + correlationId + idempotencyKey), `Result<T, E>` with `ok()`/`err()`, `OperationError` interface with `operationError()` factory, RFC 7807 fields incl. `suggestedAction`. Error subtypes used in `site.service.ts` (validation 400, notFound 404, conflict 409). Logging wrapper deferred to TASK-F03.
  - Note: `withOperationLogging()` not yet implemented — needs pino from TASK-F03. `SiteOperationError` class not created (using `operationError()` factory instead — simpler, same compliance).
  - Est: 4h | Actual: included in TASK-001

- [x] **TASK-F02:** Prefixed ID generation utility ✅ (completed as part of TASK-001, extended in TASK-002)
  - Story: Cross-cutting (NFR 24 all features)
  - Files: `src/lib/id.ts`
  - Result: `generateId()` with 9 prefixes (ste, slg, cms, vce, tpc, tcl, qty, asp, tnt). NanoID 16 chars. Used in site.service.ts.
  - Est: 1h | Actual: included in TASK-001

- [x] **TASK-F03:** Structured logging setup — pino with PII redaction ✅
  - Story: Cross-cutting (NFR 21, 28 all features)
  - Files: `src/lib/logging/logger.ts`, `src/lib/logging/__tests__/logger.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: pino configured with JSON output, `redact` paths for `*.password`, `*.token`, `*.secret`, `*.accessToken`, `*.email`, `*.phone`, `*.ip`. ISO 8601 timestamps. Service name set. Tests verify PII fields show `[REDACTED]`.
  - Result: 14 tests pass. Basic logging (JSON output, structured data, all levels), PII redaction (7 field types + nested objects), non-PII preserved, child logger with tenantId/correlationId, ISO 8601 timestamps. `createLogger()` factory with custom destination support for testing.
  - Dependencies: none
  - Est: 2h | Actual: ~10min

- [x] **TASK-F04:** Circuit breaker wrapper for external HTTP calls ✅
  - Story: Cross-cutting (NFR 29 for F-001, F-002, F-003, F-004)
  - Files: `src/lib/http/circuit-breaker.ts`, `src/lib/http/__tests__/circuit-breaker.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: Circuit breaker with configurable failure threshold / window → open for configurable reset timeout. Throws descriptive error when open. Half-open recovery works. Tests verify open/closed/half-open states.
  - Result: 14 tests pass. Closed state (start, success, below threshold), open state (trip, reject, no-call), half-open (timeout transition, success→close, failure→reopen), window expiry resets count, success resets count, error propagation (original + circuit-open). Generic `CircuitBreaker` class — CMS adapters will wrap this.
  - Dependencies: TASK-F01
  - Est: 3h | Actual: ~10min

Phase 1 parallel groups:
  Group A: TASK-002, TASK-003 (both depend on TASK-001)
  Group B: TASK-004, TASK-F01, TASK-F02, TASK-F03 (independent — no dependencies)
  Group C: TASK-F04 (depends on TASK-F01)
  Group D: TASK-005a (depends on TASK-003 + TASK-F02)
  → TASK-001 runs first. Then Groups A and B run in parallel. TASK-F04 starts when TASK-F01 completes. TASK-005a starts when TASK-003 and TASK-F02 complete.

## Phase 2: Domain Logic (Detection + Adapters)

- [x] **TASK-005:** URL normalisation + validation logic ✅
  - Story: US-001 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/url.ts`, `src/modules/content-engine/config/site-registration/__tests__/url.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `normaliseUrl("hairgenetix.com")` → `https://hairgenetix.com`. Handles: add https://, upgrade http→https, strip trailing slash, lowercase hostname, strip default ports, strip fragments, reject invalid URLs. All spec examples pass. Idempotency verified.
  - Result: 19 tests pass. Protocol handling (3), trailing slash (2), hostname normalisation (4), spec examples (3), invalid URLs (3), idempotency (1), edge cases (3). Returns `Result<string, OperationError>`. www resolution deferred to crawl step (TASK-011) — normalisation is pure, no HTTP.
  - Dependencies: TASK-001
  - Est: 2h | Actual: ~10min

- [x] **TASK-006:** CMS detection logic (WordPress + Shopify detectors) ✅
  - Story: US-002 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/detectors/types.ts`, `detectors/wordpress.ts`, `detectors/shopify.ts`, `detectors/detect.ts`, `__tests__/detectors.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: Pluggable detector pattern works. WordPress detector checks `/wp-json/wp/v2/` endpoint + `/wp-login.php` fallback. Shopify detector checks for `cdn.shopify.com` and `Shopify.theme` in HTML. Unknown fallback works. All mocked HTTP tests pass.
  - Result: 12 tests pass. WordPress (wp-json 0.95, wp-login fallback 0.7, no signals → null, network error → null). Shopify (cdn.shopify.com 0.9, Shopify.theme 0.85, no signals → null, error → null). Orchestrator (wordpress, shopify, unknown, highest-confidence wins). `HttpFetcher` interface for testability. `CmsDetector` interface for pluggability.
  - Dependencies: TASK-001
  - Est: 3h | Actual: ~10min

- [x] **TASK-007:** Language detection logic (hreflang + Shopify locales + html lang) ✅
  - Story: US-003 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/detectors/language.ts`, `__tests__/language.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: Detects languages from hreflang tags, html lang attribute. Fallback to "en". Deduplicates. All mocked HTTP tests pass.
  - Result: 8 tests pass. Hreflang (multi-language, URL pattern extraction), html lang (simple + region code → base), Shopify locale alternates, fallback (no signals → en, fetch error → en), deduplication (same lang from multiple sources). 20-language name lookup table.
  - Dependencies: TASK-001
  - Est: 3h | Actual: ~10min

- [x] **TASK-008:** Sitemap parser — content inventory ✅
  - Story: US-004 (F-001)
  - Files: `src/modules/content-engine/config/site-registration/sitemap.ts`, `__tests__/sitemap.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: Parses `sitemap.xml` and `sitemap_index.xml`. Counts content URLs (excludes images/CSS/JS). Returns 0 with sitemapFound=false if no sitemap found.
  - Result: 6 tests pass. Simple sitemap (3 URLs), sitemap index (follows child sitemaps, sums counts), no sitemap (0 + false), fetch error (0 + false), asset exclusion (filters 15 extensions), sitemap_index.xml fallback. Regex-based XML parsing — no external dependency needed.
  - Dependencies: TASK-001
  - Est: 2h | Actual: ~10min

- [x] **TASK-009:** CMS adapter interfaces + WordPress adapter ✅
  - Story: US-001 (F-002)
  - Files: `cms-connection/adapters/types.ts`, `adapters/wordpress.ts`, `__tests__/wordpress.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `CmsAdapter` interface defined (verify, testPublish, publish, unpublish). `WordPressAdapter` implements it. `CmsHttpClient` abstraction for testability. All 4 operations tested with mocked HTTP.
  - Result: 8 tests pass. Verify (200 OK with username, 401 auth fail, network error → 502). TestPublish (create draft + delete, create fail). Publish (201 → id + url). Unpublish (200 → true, 404 → error). Basic auth via Application Passwords. All return `Result<T, OperationError>`.
  - Dependencies: TASK-002, TASK-004
  - Est: 4h | Actual: ~15min

- [x] **TASK-010:** Shopify adapter ✅
  - Story: US-002 (F-002)
  - Files: `cms-connection/adapters/shopify.ts`, `__tests__/shopify.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `ShopifyAdapter` implements `CmsAdapter`. Validates token via GraphQL Admin API. Checks `read_content` + `write_content` scopes. Creates test article and deletes it. All mocked HTTP tests pass.
  - Result: 6 tests pass. Verify (valid with scopes, 401 invalid token, missing scopes → 403). TestPublish (create + delete cycle). Publish (returns GID + handle). Unpublish (delete by GID). GraphQL mutations for article CRUD. Scope validation against REQUIRED_SCOPES constant.
  - Dependencies: TASK-009
  - Est: 3h | Actual: ~10min

Phase 2 parallel groups:
  Group A: TASK-005, TASK-006, TASK-007, TASK-008 (all depend only on TASK-001, independent of each other)
  Group B: TASK-009 (depends on TASK-002 + TASK-004)
  Group C: TASK-010 (depends on TASK-009)
  → Groups A and B can run in parallel once their deps complete. TASK-010 waits for TASK-009.

## Phase 3: Services + AI Features

- [x] **TASK-011:** Site registration service — orchestrate crawl pipeline ✅
  - Story: US-001, US-002, US-003, US-004 (F-001)
  - Files: `site.service.ts` (updated), `site.repository.ts` (update + addLanguage), `__tests__/registration-pipeline.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `registerAndCrawl(url, name)` normalises URL → stores site → detects CMS → detects languages → counts content → persists languages. Event emission deferred to TASK-017. Integration test with mocked HTTP passes.
  - Result: 6 tests pass. WordPress site (CMS detected, 3 content URLs, 2 languages persisted), Shopify site, unknown CMS, URL normalisation (whitespace/case/slash stripped), invalid URL rejection (400), multi-language persistence (3 languages). Repository extended with `update()` and `addLanguage()`. Crawl runs 3 detectors in parallel via `Promise.all`. SiteService backward-compatible (fetcher optional).
  - Dependencies: TASK-005, TASK-006, TASK-007, TASK-008
  - Est: 4h | Actual: ~15min

- [x] **TASK-012:** CMS connection service — connect, verify, manage ✅
  - Story: US-001, US-002, US-003, US-004 (F-002)
  - Files: `cms-connection/cms.service.ts`, `cms.repository.ts`, `__tests__/cms.service.test.ts`
  - TDD: [x] Red → [x] Green → [ ] Refactor
  - Done when: `connect()` encrypts credentials (AES-256-GCM) → stores → returns pending status. `getConnection()` retrieves. `updateStatus()` transitions state with verifiedAt timestamp. Duplicate connection rejected (409).
  - Result: 6 tests pass. WordPress connect (encrypted password, prefixed ID, pending status), duplicate rejection (409), Shopify connect (encrypted token), getConnection (found + 404), updateStatus (verified with timestamp). CmsRepository with create/findBySiteId/updateStatus. Event emission deferred to TASK-017.
  - Dependencies: TASK-009, TASK-010, TASK-003
  - Est: 4h | Actual: ~10min

- [x] **TASK-013:** Brand voice extraction service [P]
  - Story: US-001, US-002, US-003 (F-003)
  - Files: `src/modules/content-engine/config/brand-voice/voice.service.ts`, `src/modules/content-engine/config/brand-voice/voice.repository.ts`, `src/modules/content-engine/config/brand-voice/extraction-prompt.ts`, `src/modules/content-engine/config/brand-voice/__tests__/voice.service.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 5 tests. VoiceRepository (create/findBySiteId/update), VoiceService (extractVoice via LlmClient, createDefaults, getProfile, updateProfile). Mock LLM interface for testability.
  - Done when: `extractVoice(siteId, urls)` fetches page content → sends to LLM → parses structured JSON → stores VoiceProfile. Manual parameter editing works. Skip/default produces sensible defaults. `voice.extracted` event emitted. Token budget ≤4000. All F-003 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 5h

- [x] **TASK-014:** Topic configuration service [P]
  - Story: US-001, US-002, US-003, US-004 (F-004)
  - Files: `src/modules/content-engine/config/topic-config/topic.service.ts`, `src/modules/content-engine/config/topic-config/topic.repository.ts`, `src/modules/content-engine/config/topic-config/clustering.ts`, `src/modules/content-engine/config/topic-config/__tests__/topic.service.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 9 tests. TopicRepository (createConfig/findConfigBySiteId/addCluster/findClustersByConfigId/updateClusterPriority/deleteConfigBySiteId). TopicService (setTopics, inferTopics, getTopics, updateClusterPriority). Mock LlmClusterer. Dedup, normalisation, small-set single-cluster, re-entrant overwrite.
  - Done when: `inferTopics(siteId)` auto-extracts from site content. `setTopics(siteId, keywords)` accepts manual input. `importFromGSC(siteId, creds)` imports from Search Console. All inputs cluster into `TopicCluster` entities with priorities. `topics.configured` event emitted. All F-004 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 5h

- [x] **TASK-015:** Quality thresholds service [P]
  - Story: US-001, US-002, US-003 (F-005)
  - Files: `src/modules/content-engine/config/quality-thresholds/quality.service.ts`, `src/modules/content-engine/config/quality-thresholds/quality.repository.ts`, `src/modules/content-engine/config/quality-thresholds/__tests__/quality.service.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 13 tests. QualityRepository (create/findBySiteId/update). QualityService (createDefaults, getThresholds, updateThresholds, resetToDefaults). CMS-specific defaults (Shopify shorter content). Validation (ranges, enums, min>max). getDefaults pure function.
  - Done when: Defaults created on site registration (seo_score_min=65, aiso_score_min=7.0, readability=grade_8, word_count=1500-3000, publish=draft_review). Thresholds editable. Validation prevents invalid ranges. Falls back to defaults on corruption. All F-005 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 3h

- [x] **TASK-016:** AISO preferences service [P]
  - Story: US-001, US-002, US-003 (F-006)
  - Files: `src/modules/content-engine/config/aiso-preferences/aiso.service.ts`, `src/modules/content-engine/config/aiso-preferences/aiso.repository.ts`, `src/modules/content-engine/config/aiso-preferences/factor-registry.ts`, `src/modules/content-engine/config/aiso-preferences/__tests__/aiso.service.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 15 tests. AisoRepository (create/findBySiteId/update). AisoService (createDefaults, getPreferences, updatePreferences, resetToRecommended). FactorRegistry (36 factors, 6 categories, validation). Validates factors, schema types, AI platforms.
  - Done when: Defaults created with `use_recommended=true`. Factor registry contains all 36 factors grouped in 6 categories. Custom factor selection works when `use_recommended=false`. Schema type configuration works. Falls back to recommended on corruption. All F-006 acceptance criteria met.
  - Dependencies: TASK-002, TASK-003
  - Est: 3h

Phase 3 parallel groups:
  Group A: TASK-013, TASK-014, TASK-015, TASK-016 (all depend on TASK-002 + TASK-003, independent of each other)
  Group B: TASK-011 (depends on TASK-005-008)
  Group C: TASK-012 (depends on TASK-009 + TASK-010 + TASK-003)
  → Groups A and B can start as soon as their deps complete. Group C waits for CMS adapters.

## Phase 4: Integration + Module Manifest

- [x] **TASK-017:** Module manifest + event bus integration
  - Story: Cross-cutting (architecture)
  - Files: `src/modules/content-engine/module-manifest.json`, `src/modules/content-engine/config/events.ts`, `src/modules/content-engine/config/__tests__/events.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 11 tests. ConfigEventBus (typed emit/subscribe for all 7 CloudEvents 1.0 events). Module manifest JSON matching epic-design.md spec. Multiple subscribers, listener count, safe no-subscriber emit.
  - Done when: `module-manifest.json` matches the spec from `epic-design.md`. Event bus wired: all 7 events (`site.registered`, `site.crawled`, `cms.connected`, `cms.verified`, `voice.extracted`, `topics.configured`, `config.complete`) emit correctly with typed payloads. Event subscribers can receive and type-check payloads.
  - Dependencies: TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-016
  - Est: 3h

- [x] **TASK-018:** Configuration completeness orchestrator
  - Story: Cross-cutting (pipeline readiness)
  - Files: `src/modules/content-engine/config/orchestrator.ts`, `src/modules/content-engine/config/__tests__/orchestrator.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 7 tests. ConfigOrchestrator with pluggable ConfigCheckers. Tracks 6 features (3 required, 3 optional). Pipeline ready = all Must-haves configured. All/none/partial scenarios covered.
  - Done when: Orchestrator tracks which config features are complete per site. Emits `config.complete` when all Must-have features (F-001, F-002, F-004) are done. Reports config status showing which features are configured/pending. Pipeline won't start without minimum config.
  - Dependencies: TASK-017
  - Est: 3h

- [x] **TASK-F05:** Conformance suite YAML tests — expected I/O for all endpoints
  - Story: Cross-cutting (architecture — conformance suite template)
  - Files: `tests/conformance/site-registration.yaml`, `tests/conformance/cms-connection.yaml`, `tests/conformance/brand-voice.yaml`, `tests/conformance/topic-config.yaml`, `tests/conformance/quality-thresholds.yaml`, `tests/conformance/aiso-preferences.yaml`, `tests/conformance/runner.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 9 tests. 6 YAML suites (35 cases total), conformance runner validates structure, completeness, safety checks. ≥5 cases per feature, happy+error paths.
  - Done when: YAML test cases cover: happy path CRUD, validation errors, tenant isolation (404 not 403), idempotency, business rules per feature. Runner executes YAML cases against API endpoints. All `safety_checks` documented. ≥5 cases per feature.
  - Dependencies: TASK-011, TASK-012, TASK-013, TASK-014, TASK-015, TASK-016
  - Est: 4h

- [x] **TASK-F06:** Fitness function CI checks (FF-028 to FF-034)
  - Story: Cross-cutting (architecture — fitness functions)
  - Files: `tests/architecture/fitness-functions.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: 7 fitness functions pass: FF-028 (module ≤10 files, ≤2000 lines), FF-029 (every command/query has Zod + return type), FF-030 (Result return + OperationContext param), FF-031 (`.safeParse` in every handler), FF-032 (no `throw` in `src/api/`), FF-033 (no `let`/`var` at module scope in `src/`), FF-034 (`tenant-isolation.test.ts` exists).
  - Dependencies: TASK-017
  - Est: 3h

- [x] **TASK-F07:** Tenant isolation integration test
  - Story: Cross-cutting (NFR 22 all features — FF-034)
  - Files: `tests/integration/tenant-isolation.test.ts`
  - TDD: [ ] Red → [ ] Green → [ ] Refactor
  - Done when: Tests verify: Tenant A creates site → Tenant B queries same ID → gets 404 (not 403). Tenant B creates site → Tenant A cannot see it in list. Covers all 6 entity types. All CRUD operations tested.
  - Dependencies: TASK-003, TASK-011
  - Est: 3h

- [x] **TASK-F08:** CloudEvents event logging verification
  - Story: Cross-cutting (NFR 21 — logging standards §14)
  - Files: `tests/integration/event-logging.test.ts`
  - TDD: [x] Red → [x] Green → [x] Refactor
  - Result: 11 tests. All 7 CloudEvents verified (envelope, unique IDs, ISO 8601 timestamps, JSON serialisable, subscriber delivery).
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
| **Rollback** | `git revert` + delete SQLite DB file to reset schema |
| **Monitoring** | pino structured logs to stdout, review manually for R1 |

## Test Data Strategy

Test data approach: mocked HTTP responses for unit/integration tests (no real network calls in CI). Conformance suite uses fixture data modelled on real sites (hairgenetix.com = Shopify multi-lang, digitalbouwers.nl = WordPress single-lang, skingenetix.com = Shopify dual-lang). Test tenant IDs: `tenant_test_a`, `tenant_test_b`. Encryption tests use deterministic keys. AI/LLM responses (F-003) use fixture JSON — never call real LLM in tests.

## Agent Task Boundaries

**Always (autonomous, no approval needed):**
- Create/modify files within `src/modules/content-engine/config/`
- Create/modify test files within `tests/`
- Run tests via `pnpm test`
- Run `drizzle-kit push` to sync schema

**Ask (confirm before proceeding):**
- Add new npm dependencies
- Modify `src/db/schema.ts` beyond the spec
- Create files outside the module boundary
- Modify CI/CD config

**Never (hard block):**
- Push to main without PR
- Delete existing tests
- Modify files outside `seo-toolkit/` repo
- Store secrets in code

**Context files per phase:**
- Phase 1: Read `epic-design.md` (Drizzle schema, tenant resolver, Operation pattern)
- Phase 2: Read `F-001/requirements.md`, `F-002/requirements.md` (detection logic, adapters)
- Phase 3: Read all `F-*/requirements.md` + `F-*/tests.md` (acceptance criteria)
- Phase 4: Read `epic-design.md` (module manifest, events), `tasks.md` (verification checklist)

## Verification Tasks

- [x] **TASK-V01:** Run full test suite — all tests pass, coverage ≥ 85%
- [x] **TASK-V02:** Manual walkthrough of all user stories against acceptance criteria (21 stories across 6 features)
- [x] **TASK-V03:** Verify all NFRs (performance: crawl <30s + CMS verify <10s + config read <100ms; security: AES-256, no plaintext credentials; reliability: retry + fallback)
- [x] **TASK-V04:** Update documentation (CLAUDE.md, README with setup instructions)
- [x] **TASK-V05:** Security review — no secrets in logs, encryption verified, API keys in .env only, credential redaction confirmed
- [x] **TASK-V06:** Architecture guardrails verified — import directions correct, module boundary respected, no config → stages imports, tenant isolation confirmed

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
