# Epic Design — Configuration & Setup (E-001)

> Cross-cutting architecture and design decisions for all 6 features in E-001.
> Individual feature specs contain feature-specific domain models and acceptance criteria.
> This document captures the shared architecture, module boundary, and coding guardrails.

---

## Traceability

| Level | Reference |
|-------|-----------|
| **Product goal** | PROD-001: SEO Toolkit — capability engine for AISOGEN and agency client work |
| **Theme** | `specs/001-autonomous-content-engine/theme.md` |
| **Epic status** | `./epic-status.md` |
| **Capability** | CAP-CE-001 — Site & Pipeline Configuration |

---

## Epic Architecture

### How This Epic Fits in the System

E-001 Configuration lives at **L3 (Business Module)** in the SaaS hierarchy. It is the first module of the `content-engine` capability group.

```
L1  Foundation         packages/database, ui, config, utils
    │
L2  Platform           packages/core/auth, tenancy, billing, events
    │
L3  Business Module    modules/content-engine/     ← THIS EPIC
    │                  ├── config/                  ← E-001 features
    │                  ├── research/                ← E-002 (future)
    │                  ├── writer/                  ← E-003 (future)
    │                  └── publisher/               ← E-004 (future)
    │
L5  Vertical           apps/aisogen/               ← consumes this module
```

### Component Breakdown

| Component | Package | New/Modified | Purpose |
|-----------|---------|:------------:|---------|
| `config/site-registration` | `modules/content-engine/` | New | Site URL registration, CMS detection, language detection |
| `config/cms-connection` | `modules/content-engine/` | New | CMS credential management, connection verification |
| `config/brand-voice` | `modules/content-engine/` | New | Voice profile extraction and storage |
| `config/topic-config` | `modules/content-engine/` | New | Topic/niche configuration, keyword clustering |
| `config/quality-thresholds` | `modules/content-engine/` | New | Quality gate configuration |
| `config/aiso-preferences` | `modules/content-engine/` | New | AISO factor prioritisation |

---

## Architecture Placement & Interoperability

### Repository & Module Location

| Aspect | Detail |
|--------|--------|
| **Repository** | `seo-toolkit/` |
| **Path within repo** | `src/modules/content-engine/config/` |
| **Architecture layer** | L3 — Business Module |
| **Capability group** | `seo` |
| **Coexistence** | First module in this repo — establishes the module pattern for all subsequent modules |

### Module Boundary Contract

| Aspect | R1 (V1 — standalone CLI) | Future (SaaS platform) |
|--------|--------------------------|------------------------|
| **Deployment** | Standalone CLI in `seo-toolkit/` | Module in `saas-platform/modules/content-engine/` |
| **Data storage** | SQLite via Prisma (local database) | PostgreSQL with RLS via PROD-004 database package |
| **Communication** | Direct function calls within the module | Event bus (`EventEmitter` → Trigger.dev) |
| **Multi-tenancy** | `StaticTenantResolver` — reads from `tenants.json` config | `DatabaseTenantResolver` via AsyncLocalStorage |
| **Configuration** | JSON config files per site | Per-tenant settings in database |
| **Auth** | API key per config file | JWT + RBAC via PROD-004 auth package |

### Migration Path (R1 → R2)

1. **Data migration:** SQLite → PostgreSQL migration script (Prisma handles schema, need data export/import)
2. **Interface extraction:** Extract module manifest from code, register agentTools with platform registry
3. **Multi-tenancy:** `tenant_id` already on `SiteConfig` — add RLS policies, swap `StaticTenantResolver` for `DatabaseTenantResolver`
4. **Event integration:** Replace direct function calls between stages with event bus `emit`/`subscribe`
5. **Auth swap:** Replace API key check middleware with JWT verification from `packages/core/auth`

### Module Manifest (R1 — initial)

```json
{
  "name": "content-engine-config",
  "version": "0.1.0",
  "capability": "seo",
  "description": "Site configuration for the autonomous content engine",
  "dependencies": {
    "platform": ["database", "config"],
    "modules": []
  },
  "routes": [
    { "method": "POST", "path": "/api/v1/sites", "handler": "createSite" },
    { "method": "GET", "path": "/api/v1/sites/:id", "handler": "getSite" },
    { "method": "GET", "path": "/api/v1/sites", "handler": "listSites" },
    { "method": "PATCH", "path": "/api/v1/sites/:id", "handler": "updateSite" },
    { "method": "DELETE", "path": "/api/v1/sites/:id", "handler": "deleteSite" },
    { "method": "POST", "path": "/api/v1/sites/:id/cms", "handler": "connectCMS" },
    { "method": "POST", "path": "/api/v1/sites/:id/voice", "handler": "extractVoice" },
    { "method": "PUT", "path": "/api/v1/sites/:id/topics", "handler": "configureTopics" },
    { "method": "PUT", "path": "/api/v1/sites/:id/quality", "handler": "setThresholds" },
    { "method": "PUT", "path": "/api/v1/sites/:id/aiso", "handler": "setAISOPrefs" }
  ],
  "contracts": {
    "commands": [
      { "name": "createSite", "input": "CreateSiteInput", "output": "Result<SiteConfig, OperationError>" },
      { "name": "updateSite", "input": "UpdateSiteInput", "output": "Result<SiteConfig, OperationError>" },
      { "name": "deleteSite", "input": "DeleteSiteInput", "output": "Result<void, OperationError>" },
      { "name": "connectCMS", "input": "ConnectCMSInput", "output": "Result<CMSConnection, OperationError>" },
      { "name": "extractVoice", "input": "ExtractVoiceInput", "output": "Result<VoiceProfile, OperationError>" },
      { "name": "configureTopics", "input": "ConfigureTopicsInput", "output": "Result<TopicConfig, OperationError>" },
      { "name": "setThresholds", "input": "SetThresholdsInput", "output": "Result<QualityThresholds, OperationError>" },
      { "name": "setAISOPrefs", "input": "SetAISOPrefsInput", "output": "Result<AISOPreferences, OperationError>" }
    ],
    "queries": [
      { "name": "getSite", "input": "GetSiteInput", "output": "Result<SiteConfig, OperationError>" },
      { "name": "listSites", "input": "ListSitesInput", "output": "Result<PaginatedList<SiteConfig>, OperationError>" }
    ]
  },
  "events": {
    "emits": [
      "site.registered",
      "site.crawled",
      "cms.connected",
      "cms.verified",
      "voice.extracted",
      "topics.configured",
      "config.complete"
    ],
    "subscribes": []
  },
  "agentTools": [
    {
      "name": "register_site",
      "description": "Register a new site for content generation",
      "inputSchema": "CreateSiteInput",
      "outputSchema": "SiteConfig",
      "consequenceClass": "B",
      "consequenceDescription": "Creates a new site configuration record in tenant scope",
      "permissions": ["site:write"]
    },
    {
      "name": "get_site_config",
      "description": "Get full configuration for a site",
      "inputSchema": "GetSiteInput",
      "outputSchema": "SiteConfig",
      "consequenceClass": "A",
      "consequenceDescription": "Read-only — retrieves site configuration",
      "permissions": ["site:read"]
    }
  ],
  "permissions": ["site:read", "site:write", "cms:connect", "config:manage"],
  "healthEndpoint": "/api/v1/health"
}
```

> **P-007 compliance:** The `contracts` field explicitly lists every command and query with Zod input schema + Result return type. `agentTools` include consequence classification per P-031 (Class A = read-only, Class B = tenant-scoped write, Class C = cross-tenant, Class D = irreversible/financial).

### Event Contracts (CloudEvents 1.0)

All events follow CloudEvents 1.0 specification (logging standards §14). Each event envelope includes:

```typescript
interface CloudEventEnvelope<T> {
  specversion: '1.0';
  id: string;            // UUID v4
  source: string;        // e.g., '/modules/content-engine-config'
  type: string;          // e.g., 'com.smithai.site.registered.v1'
  subject?: string;      // e.g., 'ste_abc123' (entity ID)
  time: string;          // ISO 8601
  datacontenttype: 'application/json';
  tenantid: string;      // custom extension attribute
  correlationid: string; // custom extension attribute
  data: T;               // typed payload
}
```

| Event (`type`) | Payload (`data`) | Emitted By | Consumed By |
|-------|---------|-----------|-------------|
| `com.smithai.site.registered.v1` | `{ siteId, url, tenantId }` | F-001 | E-002 (Research stage) |
| `com.smithai.site.crawled.v1` | `{ siteId, cmsType, languages[], contentCount }` | F-001 | F-002 (CMS adapter selection) |
| `com.smithai.cms.connected.v1` | `{ siteId, cmsType, status }` | F-002 | E-004 (Publish stage) |
| `com.smithai.cms.verified.v1` | `{ siteId, writeAccessConfirmed }` | F-002 | E-004 (Publish stage) |
| `com.smithai.voice.extracted.v1` | `{ siteId, voiceProfileId }` | F-003 | E-003 (Writer stage) |
| `com.smithai.topics.configured.v1` | `{ siteId, clusterCount, keywordCount }` | F-004 | E-002 (Research stage) |
| `com.smithai.config.complete.v1` | `{ siteId, configuredFeatures[] }` | Orchestrator | Pipeline trigger |

> **Logging compliance:** Every event emit and consume is logged as structured JSON with `correlationId` and `tenantId` per logging standards §14.

### Operation Pattern (P-008) & CQS (P-005)

All operations follow the 5-step Operation pattern and strict Command/Query Separation:

**File structure per P-005:**
```
modules/content-engine/config/
├── src/
│   ├── api/
│   │   ├── commands.ts       ← All write operations (create, update, delete)
│   │   └── queries.ts        ← All read operations (get, list)
│   ├── domain/
│   │   ├── types.ts          ← Domain types + Zod schemas
│   │   ├── errors.ts         ← Module-specific OperationError subtypes
│   │   └── id.ts             ← Prefixed ID generation
│   ├── infrastructure/
│   │   ├── repository.ts     ← Data access (Prisma)
│   │   ├── adapters/         ← CMS adapters (WordPress, Shopify)
│   │   └── http-client.ts    ← Circuit-breaker-wrapped HTTP
│   ├── events/
│   │   ├── emitters.ts       ← CloudEvents emit functions
│   │   └── handlers.ts       ← Subscribed event handlers (none for E-001)
│   └── index.ts              ← Barrel export (commands, queries, events, types)
```

**5-step pattern example (createSite command):**
```typescript
// src/api/commands.ts

import { z } from 'zod';
import { type OperationContext, type Result, ok, err } from '@saas-platform/core';
import { CreateSiteInput, SiteConfig } from '../domain/types';
import { SiteOperationError } from '../domain/errors';

// Step 1: Zod input validation
const CreateSiteInput = z.object({
  url: z.string().url(),
  name: z.string().optional(),
  idempotencyKey: z.string().optional(),
});

export async function createSite(
  input: z.infer<typeof CreateSiteInput>,
  ctx: OperationContext  // Step 2: OperationContext (tenantId + correlationId + idempotencyKey)
): Promise<Result<SiteConfig, SiteOperationError>> {

  // Step 1: Validate
  const parsed = CreateSiteInput.safeParse(input);
  if (!parsed.success) {
    return err(SiteOperationError.validation(parsed.error, { suggestedAction: 'Check URL format' }));
  }

  // Step 2: Check idempotency
  if (ctx.idempotencyKey) {
    const existing = await repository.findByIdempotencyKey(ctx.idempotencyKey, ctx.tenantId);
    if (existing) return ok(existing);
  }

  // Step 3: Business logic (normalise URL, initiate crawl)
  const normalised = normaliseUrl(parsed.data.url);
  const crawlResult = await crawlSite(normalised);

  // Step 4: Persist
  const site = await repository.create({
    id: generateId('ste'),  // Prefixed ID: ste_xxxxxxxxxxxx
    tenantId: ctx.tenantId,
    url: normalised,
    name: parsed.data.name ?? crawlResult.title,
    cmsType: crawlResult.cmsType,
    // ...
  });

  // Step 5: Emit event + return Result
  await emitEvent('com.smithai.site.registered.v1', {
    siteId: site.id,
    url: site.url,
    tenantId: ctx.tenantId,
  }, ctx);

  return ok(site);
}
```

**OperationContext type:**
```typescript
// Extends TenantContext from @saas-platform/core
interface OperationContext {
  tenantId: string;       // From AsyncLocalStorage (StaticTenantResolver for R1)
  correlationId: string;  // UUID v4, propagated through all calls
  idempotencyKey?: string; // Optional, for write operations (P-009)
  requestId?: string;     // From HTTP request header
}
```

**Result type (no naked `throw` — FF-032):**
```typescript
type Result<T, E extends OperationError = OperationError> =
  | { success: true; data: T }
  | { success: false; error: E };

function ok<T>(data: T): Result<T, never>;
function err<E extends OperationError>(error: E): Result<never, E>;
```

### Error Handling (AppError Hierarchy)

All errors follow the AppError hierarchy from `docs/capabilities/error-handling-patterns.md`. RFC 7807 response format with `suggested_action` field.

```typescript
// src/domain/errors.ts

import { OperationError } from '@saas-platform/core/errors';

// Module-specific error factory
export class SiteOperationError extends OperationError {
  static validation(zodError: ZodError, opts?: { suggestedAction?: string }) {
    return new SiteOperationError({
      type: 'https://api.smithai.com/errors/validation',
      title: 'Validation Error',
      status: 400,
      detail: zodError.issues.map(i => `${i.path}: ${i.message}`).join('; '),
      suggestedAction: opts?.suggestedAction ?? 'Check input and retry',
    });
  }

  static notFound(siteId: string) {
    return new SiteOperationError({
      type: 'https://api.smithai.com/errors/not-found',
      title: 'Site Not Found',
      status: 404,  // 404, not 403 — tenant isolation (multi-tenant arch §3.1)
      detail: `Site ${siteId} not found`,
      suggestedAction: 'Check the site ID is correct',
    });
  }

  static cmsUnreachable(url: string) {
    return new SiteOperationError({
      type: 'https://api.smithai.com/errors/cms-unreachable',
      title: 'CMS Unreachable',
      status: 502,
      detail: `Could not reach ${url}`,
      suggestedAction: 'Check the URL is correct and the site is live',
    });
  }

  static circuitOpen(service: string) {
    return new SiteOperationError({
      type: 'https://api.smithai.com/errors/circuit-open',
      title: 'Service Temporarily Unavailable',
      status: 503,
      detail: `Circuit breaker open for ${service}`,
      suggestedAction: 'Wait 30 seconds and retry',
    });
  }
}
```

### Structured Logging (pino — P-028)

All operations emit 3 structured log events per the SaaS coding architecture P-028:

```typescript
// src/infrastructure/logger.ts

import pino from 'pino';

export const logger = pino({
  name: 'content-engine-config',
  level: process.env.LOG_LEVEL ?? 'info',
  redact: {
    paths: [
      '*.password', '*.token', '*.secret', '*.accessToken',
      '*.wpApplicationPassword', '*.shopifyAccessToken',
      '*.email', '*.phone', '*.ip',
    ],
    censor: '[REDACTED]',
  },
  serializers: {
    // ISO 8601 strings only — no Date objects (P-011)
    timestamp: () => `,"time":"${new Date().toISOString()}"`,
  },
});

// Operation logging wrapper
export function withOperationLogging<T>(
  operationName: string,
  ctx: OperationContext,
  fn: () => Promise<Result<T, OperationError>>
): Promise<Result<T, OperationError>> {
  const startTime = Date.now();

  logger.info({
    event: 'operation.started',
    operation: operationName,
    correlationId: ctx.correlationId,
    tenantId: ctx.tenantId,
  });

  try {
    const result = await fn();
    const duration = Date.now() - startTime;

    if (result.success) {
      logger.info({
        event: 'operation.completed',
        operation: operationName,
        correlationId: ctx.correlationId,
        tenantId: ctx.tenantId,
        durationMs: duration,
      });
    } else {
      logger.warn({
        event: 'operation.failed',
        operation: operationName,
        correlationId: ctx.correlationId,
        tenantId: ctx.tenantId,
        durationMs: duration,
        errorType: result.error.type,
        errorStatus: result.error.status,
      });
    }

    return result;
  } catch (unexpected) {
    logger.error({
      event: 'operation.failed',
      operation: operationName,
      correlationId: ctx.correlationId,
      tenantId: ctx.tenantId,
      durationMs: Date.now() - startTime,
      error: unexpected instanceof Error ? unexpected.message : 'Unknown error',
    });
    throw unexpected; // Re-throw unexpected errors — these should never happen
  }
}
```

### Prefixed ID Generation

All entity IDs use prefixed NanoID per API standards §4.3:

```typescript
// src/domain/id.ts

import { nanoid } from 'nanoid';

const ID_PREFIXES = {
  site: 'ste',
  cmsConnection: 'cms',
  voiceProfile: 'vce',
  topicConfig: 'tpc',
  topicCluster: 'tcl',
  qualityThresholds: 'qty',
  aisoPreferences: 'asp',
} as const;

export function generateId(entity: keyof typeof ID_PREFIXES): string {
  return `${ID_PREFIXES[entity]}_${nanoid(16)}`;
}
```

### Circuit Breaker (External HTTP Calls)

All HTTP calls to target sites and CMS APIs use circuit breaker pattern (error handling §8):

```typescript
// src/infrastructure/http-client.ts

// Circuit breaker config: 5 failures in 60s → open for 30s
const CIRCUIT_CONFIG = {
  failureThreshold: 5,
  windowMs: 60_000,
  cooldownMs: 30_000,
};
```

### Coding Guardrails

| Rule | Enforcement | Example |
|------|-------------|---------|
| Config features must not import from pipeline stages | ESLint boundary rule | `config/site-registration.ts` cannot import from `stages/research.ts` |
| All external HTTP calls go through adapter interfaces | Code review + architecture test | CMS calls only in `adapters/wordpress.ts` or `adapters/shopify.ts` |
| All database access via repository pattern | Code review | No raw Prisma calls in service logic — use `SiteRepository`, `CMSRepository` |
| Credentials never in logs or error messages | Security test (grep for credential patterns) | Logger automatically redacts fields matching `*password*`, `*token*`, `*secret*` |
| All entities include `tenant_id` in queries | Prisma middleware | Middleware auto-adds `WHERE tenant_id = ?` to all queries |
| Feature flags wrap all new functionality | Code review | `if (featureFlags.isEnabled('config-v1', tenantId))` |

### Temporary Tenant Solution (StaticTenantResolver)

Until PROD-004 Phase 1 (Auth + Tenancy) is production-ready, E-001 uses `StaticTenantResolver`:

```typescript
// Same interface as future DatabaseTenantResolver
interface TenantResolver {
  resolve(context: RequestContext): Promise<Tenant>;
  getTenantId(): string; // from AsyncLocalStorage
}

// R1 implementation — reads from config file
class StaticTenantResolver implements TenantResolver {
  private readonly tenants: Map<string, Tenant>;  // P-010: const, not let

  constructor(configPath: string = './tenants.json') {
    this.tenants = loadTenantsFromFile(configPath);
  }

  async resolve(ctx: RequestContext): Promise<Tenant> {
    const apiKey = ctx.headers['x-api-key'];
    const tenant = this.tenants.get(apiKey);
    if (!tenant) return err(AuthenticationError.invalidApiKey());  // Result, not throw
    return ok(tenant);
  }

  getTenantId(): string {
    return asyncLocalStorage.getStore()?.tenantId ?? 'default';
  }
}

// OperationContext factory — creates context for each request
function createOperationContext(tenant: Tenant, req: Request): OperationContext {
  return {
    tenantId: tenant.id,
    correlationId: req.headers['x-correlation-id'] ?? crypto.randomUUID(),
    idempotencyKey: req.headers['idempotency-key'],
    requestId: req.headers['x-request-id'],
  };
}
```

**tenants.json example:**
```json
{
  "apikey_hairgenetix": {
    "id": "tenant_hg001",
    "name": "Hairgenetix",
    "plan": "agency",
    "enabledModules": ["content-engine-config"]
  }
}
```

**Migration to DatabaseTenantResolver:** Swap the constructor injection. No other code changes needed because all code uses the `TenantResolver` interface.

---

## Quality Gate Stack

| Gate | Tool | Configuration |
|------|------|---------------|
| Linting | ESLint + typescript-eslint | `eslint.config.mjs` |
| Formatting | Prettier | `.prettierrc` |
| Type checking | `tsc --noEmit` | `tsconfig.json` (strict mode) |
| Tests | Vitest | `vitest.config.ts` (coverage ≥ 85%) |
| Conformance suite | YAML expected I/O tests | `tests/conformance/*.yaml` (see below) |
| Migration linting | Custom CI gate | Blocks `DROP`, `RENAME`, `TRUNCATE` in migrations |
| RLS validation | CI script | Verifies RLS policies on all tenant-scoped tables |
| Fitness functions | Architecture tests | FF-028 to FF-034 (see below) |
| Pre-commit | Husky + lint-staged | lint + typecheck + test affected |
| Security | Semgrep (AI rules) | `.semgrep.yml` |

### Conformance Suite

YAML-based expected I/O tests per `docs/blueprints/spec-templates/conformance-suite.yaml`:

```yaml
# tests/conformance/site-registration.yaml
suite: site-registration
endpoint: POST /api/v1/sites
cases:
  - name: "Happy path — register new site"
    input: { url: "https://hairgenetix.com" }
    headers: { "X-Api-Key": "apikey_hairgenetix", "Idempotency-Key": "idem_001" }
    expect:
      status: 201
      body:
        id: { pattern: "^ste_" }
        url: "https://www.hairgenetix.com"
        cmsType: "shopify"
      headers: { "Content-Type": "application/json" }
    safety_checks: "Verifies URL normalisation, CMS auto-detection, prefixed ID generation"

  - name: "Tenant isolation — cross-tenant read returns 404"
    input: { id: "ste_tenant_a_site" }
    headers: { "X-Api-Key": "apikey_tenant_b" }
    expect:
      status: 404
      body: { type: "https://api.smithai.com/errors/not-found" }
    safety_checks: "404 not 403 — prevents tenant enumeration (multi-tenant arch §3.1)"

  - name: "Idempotency — duplicate request returns original"
    input: { url: "https://hairgenetix.com" }
    headers: { "Idempotency-Key": "idem_001" }
    expect:
      status: 200
      body: { id: "ste_original_id" }
    safety_checks: "Idempotent write — no duplicate creation (P-009)"
```

Coverage required: CRUD, validation errors, tenant isolation (404 not 403), idempotency, business rules per feature.

### Fitness Function Compliance

| FF | What It Checks | How | CI Gate? |
|----|----------------|-----|:--------:|
| FF-028 | Module size limits (max 10 source files, max 2000 lines) | File count + `wc -l` | Yes |
| FF-029 | Contract completeness (every command/query has Zod schema + return type) | AST analysis | Yes |
| FF-030 | Operation signatures (Result return + OperationContext param) | AST analysis | Yes |
| FF-031 | Zod validation on all route handlers | Grep for `.safeParse` in every handler | Yes |
| FF-032 | No naked `throw` in commands/queries | Grep `throw` in `src/api/` | Yes |
| FF-033 | No module-level mutable state (`let`/`var` at module scope) | Grep `^(let|var) ` in `src/` | Yes |
| FF-034 | Tenant isolation test presence (`tenant-isolation.test.ts`) | File existence check | Yes |

---

## Shared Data Model (Prisma)

All 6 features share one Prisma schema. `SiteConfig` is the root aggregate — all other entities hang off it via `siteId` FK.

**Data layer governance (ADR-017):**
- All models use `@map`/`@@map` for snake_case DB column/table names
- All IDs use prefixed NanoID (not CUID) via `generateId()` — no `@default(cuid())`
- All tenant-scoped tables have `tenant_id` column with index
- RLS policies documented alongside each model (enforced via migration for PostgreSQL, via Prisma middleware for SQLite R1)
- Migration linting blocks `DROP`, `RENAME`, `TRUNCATE` in CI

```prisma
// schema.prisma — content-engine-config module

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"  // R1: SQLite. R2: swap to "postgresql"
  url      = env("DATABASE_URL")
}

// RLS Policy (R2): CREATE POLICY site_config_tenant_isolation ON site_config
//   USING (tenant_id = current_setting('app.tenant_id'))
//   WITH CHECK (tenant_id = current_setting('app.tenant_id'));
model SiteConfig {
  id              String   @id  // Prefixed: ste_xxxxxxxxxxxx (set by application, not DB default)
  tenantId        String   @map("tenant_id")
  url             String
  name            String
  cmsType         String   @default("unknown") @map("cms_type")   // wordpress | shopify | unknown
  cmsDetectedAt   DateTime? @map("cms_detected_at")
  primaryLanguage String   @default("en") @map("primary_language") // BCP-47
  contentCount    Int      @default(0) @map("content_count")
  lastCrawled     DateTime? @map("last_crawled")
  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  // Relations
  languages       SiteLanguage[]
  cmsConnection   CMSConnection?
  voiceProfile    VoiceProfile?
  topicConfig     TopicConfig?
  qualityThresholds QualityThresholds?
  aisoPreferences AISOPreferences?

  @@unique([tenantId, url])
  @@index([tenantId])
  @@map("site_config")
}

// RLS Policy (R2): Same as site_config — child tables inherit tenant isolation via site_id FK
model SiteLanguage {
  id         String @id  // Prefixed: slg_xxxxxxxxxxxx
  siteId     String @map("site_id")
  code       String // BCP-47: "en", "nl", "de"
  name       String // "English", "Dutch"
  urlPattern String? @map("url_pattern") // e.g., "/nl/"
  site       SiteConfig @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@unique([siteId, code])
  @@map("site_language")
}

// RLS Policy (R2): Inherits via site_id FK — JOIN-based isolation
model CMSConnection {
  id                    String   @id  // Prefixed: cms_xxxxxxxxxxxx
  siteId                String   @unique @map("site_id")
  cmsType               String   @map("cms_type") // wordpress | shopify
  status                String   @default("pending") // pending | verified | failed | revoked
  wpSiteUrl             String?  @map("wp_site_url")
  wpUsername             String?  @map("wp_username")         // encrypted
  wpApplicationPassword String?  @map("wp_application_password") // encrypted
  shopifyStoreDomain    String?  @map("shopify_store_domain")
  shopifyAccessToken    String?  @map("shopify_access_token") // encrypted
  defaultPublishStatus  String   @default("draft") @map("default_publish_status") // draft | published
  verifiedAt            DateTime? @map("verified_at")
  lastUsedAt            DateTime? @map("last_used_at")
  createdAt             DateTime @default(now()) @map("created_at")
  updatedAt             DateTime @updatedAt @map("updated_at")

  site SiteConfig @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@map("cms_connection")
}

model VoiceProfile {
  id               String   @id  // Prefixed: vce_xxxxxxxxxxxx
  siteId           String   @unique @map("site_id")
  brandName        String?  @map("brand_name")
  industry         String?
  targetAudience   String?  @map("target_audience")
  brandValues      String?  @map("brand_values")  // JSON array
  keyTopics        String?  @map("key_topics")     // JSON array
  tone             String   @default("conversational")
  sentenceStructure String  @default("mixed") @map("sentence_structure")
  vocabularyLevel  String   @default("intermediate") @map("vocabulary_level")
  person           String   @default("second") // first | second | third
  extractedFromUrl String?  @map("extracted_from_url")
  extractedAt      DateTime? @map("extracted_at")
  createdAt        DateTime @default(now()) @map("created_at")
  updatedAt        DateTime @updatedAt @map("updated_at")

  site SiteConfig @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@map("voice_profile")
}

model TopicConfig {
  id           String   @id  // Prefixed: tpc_xxxxxxxxxxxx
  siteId       String   @unique @map("site_id")
  source       String   @default("manual") // auto_inferred | manual | gsc_import
  seedKeywords String?  @map("seed_keywords") // JSON array
  createdAt    DateTime @default(now()) @map("created_at")
  updatedAt    DateTime @updatedAt @map("updated_at")

  site     SiteConfig    @relation(fields: [siteId], references: [id], onDelete: Cascade)
  clusters TopicCluster[]

  @@map("topic_config")
}

model TopicCluster {
  id            String @id  // Prefixed: tcl_xxxxxxxxxxxx
  topicConfigId String @map("topic_config_id")
  name          String
  keywords      String // JSON array
  priority      String @default("medium") // high | medium | low
  contentCount  Int    @default(0) @map("content_count")

  topicConfig TopicConfig @relation(fields: [topicConfigId], references: [id], onDelete: Cascade)

  @@map("topic_cluster")
}

model QualityThresholds {
  id               String   @id  // Prefixed: qty_xxxxxxxxxxxx
  siteId           String   @unique @map("site_id")
  seoScoreMin      Int      @default(65) @map("seo_score_min")
  aisoScoreMin     Float    @default(7.0) @map("aiso_score_min")
  readabilityTarget String  @default("grade_8") @map("readability_target")
  wordCountMin     Int      @default(1500) @map("word_count_min")
  wordCountMax     Int      @default(3000) @map("word_count_max")
  publishMode      String   @default("draft_review") @map("publish_mode")
  createdAt        DateTime @default(now()) @map("created_at")
  updatedAt        DateTime @updatedAt @map("updated_at")

  site SiteConfig @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@map("quality_thresholds")
}

model AISOPreferences {
  id               String   @id  // Prefixed: asp_xxxxxxxxxxxx
  siteId           String   @unique @map("site_id")
  useRecommended   Boolean  @default(true) @map("use_recommended")
  priorityFactors  String?  @map("priority_factors")    // JSON array (subset of 36-factor model)
  schemaTypes      String?  @map("schema_types")         // JSON array
  aiPlatformTargets String? @map("ai_platform_targets")  // JSON array
  createdAt        DateTime @default(now()) @map("created_at")
  updatedAt        DateTime @updatedAt @map("updated_at")

  site SiteConfig @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@map("aiso_preferences")
}
```

### Data Lifecycle

| Entity | Created | Updated | Deleted | Retention |
|--------|---------|---------|---------|-----------|
| SiteConfig | Site registration (F-001) | Re-crawl, manual edit | Cascade from site delete | Until site deleted |
| CMSConnection | CMS setup (F-002) | Re-verification, credential update | Cascade from site delete | Until site deleted; credentials securely wiped |
| VoiceProfile | Voice extraction (F-003) | Re-extraction, manual edit | Cascade from site delete | Until site deleted |
| TopicConfig | Topic setup (F-004) | GSC re-import, manual edit | Cascade from site delete | Until site deleted |
| QualityThresholds | Site registration (defaults) | Manual threshold edit | Cascade from site delete | Until site deleted |
| AISOPreferences | Site registration (defaults) | Manual preference edit | Cascade from site delete | Until site deleted |

---

## Cross-Cutting Concerns

### Security Controls

| Concern | Control | Implementation |
|---------|---------|---------------|
| Authentication | API key (R1) / JWT (R2) | `StaticTenantResolver` middleware validates API key → sets tenant context |
| Authorisation | Tenant isolation | Prisma middleware adds `tenantId` filter to all queries |
| Input validation | Zod schemas at service boundary | Every service function validates input with Zod before processing |
| Encryption at rest | AES-256 for CMS credentials | `@smithai/crypto` utility wrapping Node.js `crypto.createCipheriv` |
| Credential logging | Auto-redaction | Pino logger with `redact: ['*.password', '*.token', '*.secret', '*.accessToken']` |
| OWASP | Injection, Broken Auth, Sensitive Data Exposure | Parameterised queries (Prisma), schema validation (Zod), credential encryption |

### Observability

| Signal | What | Tool | Alert Threshold |
|--------|------|------|----------------|
| Logs | Structured JSON via pino — `operation.started`, `operation.completed`, `operation.failed` per P-028 | Pino → stdout (R1), BetterStack (R2) | Error rate > 5% → P2 |
| Metrics | Crawl duration, CMS verification time, config completeness | Custom counters → console (R1) | Crawl > 30s → P3 |
| Tracing | correlationId propagated through all calls, logged on every operation event | OperationContext.correlationId | N/A |
| PII Redaction | `*.password`, `*.token`, `*.secret`, `*.email`, `*.phone`, `*.ip` | pino `redact` config | N/A |
| Health | `/api/v1/health` endpoint (logging standards §8) | HTTP GET | 5xx → P2 |
| CloudEvents audit | Every event emit/consume logged with full envelope | Structured log entry | N/A |

### Error Handling

All errors use the `Result<T, OperationError>` pattern — no naked `throw` (FF-032). Error responses follow RFC 7807 with `suggested_action` field.

| Error Type | OperationError Subtype | Status | Strategy | suggested_action |
|-----------|----------------------|:------:|----------|-----------------|
| Validation error | `SiteOperationError.validation()` | 400 | Return Result.err with field details | "Check input and retry" |
| Not found (incl. cross-tenant) | `SiteOperationError.notFound()` | 404 | Return 404 (not 403 — tenant isolation) | "Check the ID is correct" |
| CMS unreachable | `SiteOperationError.cmsUnreachable()` | 502 | Retry once after 5s, then Result.err | "Check the URL and try again" |
| CMS auth failure | `SiteOperationError.authFailed()` | 401 | No retry, clear error | "Check credentials" |
| Circuit breaker open | `SiteOperationError.circuitOpen()` | 503 | Return immediately, no call attempted | "Wait 30 seconds and retry" |
| Duplicate (idempotency miss) | `SiteOperationError.conflict()` | 409 | Return existing entity or conflict info | "Use Idempotency-Key header" |
| Encryption failure | `InternalError` | 500 | Log critical, return generic error | "Contact support" |

---

## Technology Decisions

| # | Decision | Rationale | Alternatives Considered |
|---|----------|-----------|------------------------|
| 1 | SQLite for R1, PostgreSQL for R2 | Zero infrastructure for CLI tool, Prisma abstracts the swap | PostgreSQL from day 1 (rejected: overkill for CLI) |
| 2 | Prisma ORM | Type-safe, migration support, works with both SQLite and PostgreSQL | Drizzle (newer, less mature), Knex (no type generation) |
| 3 | Zod for validation | Runtime + compile-time validation, great TypeScript inference. Mandatory per P-006 and FF-029/FF-031 | Joi (no TS inference), class-validator (decorators) |
| 4 | AES-256-GCM for credential encryption | Industry standard, built into Node.js crypto | Vault/KMS (overkill for R1), bcrypt (wrong tool — need reversible encryption) |
| 5 | Repository pattern for data access | Testable, swappable, prevents Prisma leaking into service layer | Direct Prisma in services (rejected: harder to test, couples to ORM) |
| 6 | Strategy pattern for CMS adapters | Pluggable — add new CMS by implementing interface (NFR #6) | Switch statement (rejected: violates OCP) |
| 7 | Result<T, E> over try/catch | Explicit error handling, composable, no untyped exceptions. Required by P-005 and FF-032 | try/catch (rejected: untyped errors, hidden control flow) |
| 8 | Operation Pattern (P-008) | Consistent 5-step structure for all commands/queries. Enforced by FF-030 | Ad-hoc service methods (rejected: inconsistent, hard to audit) |
| 9 | CloudEvents 1.0 for events | Industry standard envelope, vendor-neutral, required by logging standards §14 | Custom event format (rejected: non-standard, harder to integrate) |
| 10 | Prefixed NanoID for IDs | Human-readable entity type from ID alone (`ste_` = site). Required by API standards §4.3 | CUID2 (rejected: no prefix), UUID v7 (rejected: no prefix, longer) |
| 11 | Circuit breaker for external HTTP | Prevents cascading failures when target sites are down (error handling §8) | Simple retry (rejected: no protection against sustained failures) |

### Dependency List

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| prisma | ^6.x | ORM, migrations, type generation | Apache 2.0 |
| zod | ^3.x | Input validation schemas (P-006, FF-029/FF-031) | MIT |
| pino | ^9.x | Structured JSON logging (logging standards §1) | MIT |
| nanoid | ^5.x | Prefixed ID generation (API standards §4.3) | MIT |
| vitest | ^3.x | Test runner | MIT |

---

## Alternatives Considered (Epic-Level)

| Approach | Pros | Cons | Why Rejected |
|----------|------|------|-------------|
| All config in JSON files (no database) | Simpler R1 | No querying, no relations, manual migration | Can't efficiently query across sites, poor for multi-tenancy |
| Separate micro-databases per feature | Full isolation | 6 databases to manage, no cross-feature queries | Over-engineering for config features |
| PostgreSQL from day 1 | No migration needed | Requires PostgreSQL server for CLI tool | Friction for agency use (Malcolm), unnecessary complexity for R1 |
| GraphQL API from day 1 | Future-proof for SaaS | Over-engineering for CLI, more boilerplate | REST-like function calls are sufficient for R1 |
