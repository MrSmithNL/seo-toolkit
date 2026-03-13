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
| **Data storage** | SQLite via Drizzle ORM (local database) | PostgreSQL with RLS via PROD-004 database package |
| **Communication** | Direct function calls within the module | Event bus (`EventEmitter` → Trigger.dev) |
| **Multi-tenancy** | `StaticTenantResolver` — reads from `tenants.json` config | `DatabaseTenantResolver` via AsyncLocalStorage |
| **Configuration** | JSON config files per site | Per-tenant settings in database |
| **Auth** | API key per config file | JWT + RBAC via PROD-004 auth package |

### Migration Path (R1 → R2)

1. **Data migration:** SQLite → PostgreSQL migration script (Drizzle handles schema, need data export/import)
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
│   │   ├── repository.ts     ← Data access (Drizzle)
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
  tenant: 'tnt',
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
| All database access via repository pattern | Code review | No raw Drizzle calls in service logic — use `SiteRepository`, `CMSRepository` |
| Credentials never in logs or error messages | Security test (grep for credential patterns) | Logger automatically redacts fields matching `*password*`, `*token*`, `*secret*` |
| All entities include `tenant_id` in queries | Drizzle query wrapper | Wrapper auto-adds `WHERE tenant_id = ?` to all queries |
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

### Tenant Administration CLI (R1)

Until the SaaS platform (PROD-004) provides user registration and tenant management, E-001 needs CLI commands to manage `tenants.json`. Without this, adding a new client means manually editing JSON — error-prone and undocumented.

**Commands:**

```bash
# Add a new tenant — generates a secure API key automatically
seo-toolkit tenant add --name "Hairgenetix" --plan agency
# Output: Created tenant tenant_hg001. API key: apikey_<generated>

# List all tenants
seo-toolkit tenant list
# Output:
# ID              Name            Plan      Modules                    Created
# tenant_hg001    Hairgenetix     agency    content-engine-config      2026-03-13
# tenant_sg001    Skingenetix     agency    content-engine-config      2026-03-13

# Remove a tenant (confirms before deleting)
seo-toolkit tenant remove tenant_hg001
# Output: Remove tenant "Hairgenetix" and all associated data? (y/N)

# Rotate API key for a tenant
seo-toolkit tenant rotate-key tenant_hg001
# Output: New API key: apikey_<generated>  (old key invalidated immediately)
```

**Implementation:**

```typescript
// src/lib/tenant/tenant-admin.ts

import crypto from 'node:crypto';
import { generateId } from '../ids/generate.js';

interface TenantEntry {
  id: string;
  name: string;
  plan: 'agency' | 'starter' | 'pro';
  enabledModules: string[];
  createdAt: string;  // ISO 8601
}

function generateApiKey(): string {
  // 32 random bytes → base64url → prefixed
  const random = crypto.randomBytes(32).toString('base64url');
  return `apikey_${random}`;
}

function addTenant(name: string, plan: string): { tenant: TenantEntry; apiKey: string } {
  const tenants = loadTenantsFile();
  const apiKey = generateApiKey();
  const tenant: TenantEntry = {
    id: generateId('tenant'),  // tnt_xxxxxxxx
    name,
    plan: plan as TenantEntry['plan'],
    enabledModules: ['content-engine-config'],
    createdAt: new Date().toISOString(),
  };
  tenants[apiKey] = tenant;
  writeTenantsFile(tenants);
  return { tenant, apiKey };
}

function listTenants(): TenantEntry[] {
  const tenants = loadTenantsFile();
  return Object.values(tenants);
}

function removeTenant(tenantId: string): boolean {
  const tenants = loadTenantsFile();
  const entry = Object.entries(tenants).find(([_, t]) => t.id === tenantId);
  if (!entry) return false;
  delete tenants[entry[0]];
  writeTenantsFile(tenants);
  return true;
}

function rotateApiKey(tenantId: string): string | null {
  const tenants = loadTenantsFile();
  const entry = Object.entries(tenants).find(([_, t]) => t.id === tenantId);
  if (!entry) return null;
  const [oldKey, tenant] = entry;
  const newKey = generateApiKey();
  delete tenants[oldKey];
  tenants[newKey] = tenant;
  writeTenantsFile(tenants);
  return newKey;
}
```

**Prefixed ID addition:** `tnt_` prefix for tenant IDs (added to the 7 existing prefixes → 8 total).

**Security:**
- API keys are 32 random bytes (256-bit entropy) — cryptographically secure
- `tenants.json` should be in `.gitignore` (contains secrets)
- Key rotation invalidates old key immediately — no grace period for R1
- `tenant remove` requires confirmation and cascades to delete all associated site configs

**Migration to DatabaseTenantResolver:** Swap the constructor injection. No other code changes needed because all code uses the `TenantResolver` interface. The tenant admin CLI commands become database operations (CREATE/DELETE/UPDATE on `tenants` table) — same interface, different storage backend.

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

## Shared Data Model (Drizzle ORM)

All 6 features share one Drizzle schema. `siteConfig` is the root aggregate — all other entities hang off it via `siteId` FK. Per ADR-007: Drizzle over Prisma for native RLS support, SQL-first philosophy, and smaller bundle size.

**Data layer governance (ADR-017):**
- Column names are snake_case directly in schema definitions (Drizzle convention — no mapping decorators needed)
- All IDs use prefixed NanoID via `generateId()` — set by application, not DB default
- All tenant-scoped tables have `tenant_id` column with index
- RLS policies documented alongside each table (enforced via `pgPolicy()` for PostgreSQL R2, via query wrapper for SQLite R1)
- Migration linting blocks `DROP`, `RENAME`, `TRUNCATE` in CI

```typescript
// src/db/schema.ts — content-engine-config module

import { sqliteTable, text, integer, real, uniqueIndex, index } from 'drizzle-orm/sqlite-core';
import { relations } from 'drizzle-orm';
import { sql } from 'drizzle-orm';

// R1: SQLite tables. R2: swap imports to 'drizzle-orm/pg-core' (pgTable, pgPolicy, etc.)
// RLS Policy (R2): pgPolicy('site_config_tenant_isolation', { using: sql`tenant_id = current_setting('app.tenant_id')` })

export const siteConfig = sqliteTable('site_config', {
  id:              text('id').primaryKey(),             // Prefixed: ste_xxxxxxxxxxxx
  tenantId:        text('tenant_id').notNull(),
  url:             text('url').notNull(),
  name:            text('name').notNull(),
  cmsType:         text('cms_type').default('unknown'), // wordpress | shopify | unknown
  cmsDetectedAt:   text('cms_detected_at'),             // ISO 8601 string (SQLite has no DateTime)
  primaryLanguage: text('primary_language').default('en'), // BCP-47
  contentCount:    integer('content_count').default(0),
  lastCrawled:     text('last_crawled'),                // ISO 8601
  createdAt:       text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:       text('updated_at').notNull().default(sql`(datetime('now'))`),
}, (table) => [
  uniqueIndex('site_config_tenant_url_idx').on(table.tenantId, table.url),
  index('site_config_tenant_idx').on(table.tenantId),
]);

// RLS Policy (R2): Inherits via site_id FK — JOIN-based isolation
export const siteLanguage = sqliteTable('site_language', {
  id:         text('id').primaryKey(),                   // Prefixed: slg_xxxxxxxxxxxx
  siteId:     text('site_id').notNull().references(() => siteConfig.id, { onDelete: 'cascade' }),
  code:       text('code').notNull(),                    // BCP-47: "en", "nl", "de"
  name:       text('name').notNull(),                    // "English", "Dutch"
  urlPattern: text('url_pattern'),                       // e.g., "/nl/"
}, (table) => [
  uniqueIndex('site_language_site_code_idx').on(table.siteId, table.code),
]);

// RLS Policy (R2): Inherits via site_id FK
export const cmsConnection = sqliteTable('cms_connection', {
  id:                    text('id').primaryKey(),         // Prefixed: cms_xxxxxxxxxxxx
  siteId:                text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  cmsType:               text('cms_type').notNull(),      // wordpress | shopify
  status:                text('status').default('pending'), // pending | verified | failed | revoked
  wpSiteUrl:             text('wp_site_url'),
  wpUsername:             text('wp_username'),              // encrypted
  wpApplicationPassword: text('wp_application_password'),  // encrypted
  shopifyStoreDomain:    text('shopify_store_domain'),
  shopifyAccessToken:    text('shopify_access_token'),     // encrypted
  defaultPublishStatus:  text('default_publish_status').default('draft'), // draft | published
  verifiedAt:            text('verified_at'),              // ISO 8601
  lastUsedAt:            text('last_used_at'),             // ISO 8601
  createdAt:             text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:             text('updated_at').notNull().default(sql`(datetime('now'))`),
});

export const voiceProfile = sqliteTable('voice_profile', {
  id:               text('id').primaryKey(),              // Prefixed: vce_xxxxxxxxxxxx
  siteId:           text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  brandName:        text('brand_name'),
  industry:         text('industry'),
  targetAudience:   text('target_audience'),
  brandValues:      text('brand_values'),                 // JSON array
  keyTopics:        text('key_topics'),                   // JSON array
  tone:             text('tone').default('conversational'),
  sentenceStructure: text('sentence_structure').default('mixed'),
  vocabularyLevel:  text('vocabulary_level').default('intermediate'),
  person:           text('person').default('second'),      // first | second | third
  extractedFromUrl: text('extracted_from_url'),
  extractedAt:      text('extracted_at'),                  // ISO 8601
  createdAt:        text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:        text('updated_at').notNull().default(sql`(datetime('now'))`),
});

export const topicConfig = sqliteTable('topic_config', {
  id:           text('id').primaryKey(),                   // Prefixed: tpc_xxxxxxxxxxxx
  siteId:       text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  source:       text('source').default('manual'),          // auto_inferred | manual | gsc_import
  seedKeywords: text('seed_keywords'),                     // JSON array
  createdAt:    text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:    text('updated_at').notNull().default(sql`(datetime('now'))`),
});

export const topicCluster = sqliteTable('topic_cluster', {
  id:            text('id').primaryKey(),                  // Prefixed: tcl_xxxxxxxxxxxx
  topicConfigId: text('topic_config_id').notNull().references(() => topicConfig.id, { onDelete: 'cascade' }),
  name:          text('name').notNull(),
  keywords:      text('keywords').notNull(),               // JSON array
  priority:      text('priority').default('medium'),        // high | medium | low
  contentCount:  integer('content_count').default(0),
});

export const qualityThresholds = sqliteTable('quality_thresholds', {
  id:                text('id').primaryKey(),              // Prefixed: qty_xxxxxxxxxxxx
  siteId:            text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  seoScoreMin:       integer('seo_score_min').default(65),
  aisoScoreMin:      real('aiso_score_min').default(7.0),
  readabilityTarget: text('readability_target').default('grade_8'),
  wordCountMin:      integer('word_count_min').default(1500),
  wordCountMax:      integer('word_count_max').default(3000),
  publishMode:       text('publish_mode').default('draft_review'),
  createdAt:         text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:         text('updated_at').notNull().default(sql`(datetime('now'))`),
});

export const aisoPreferences = sqliteTable('aiso_preferences', {
  id:                text('id').primaryKey(),              // Prefixed: asp_xxxxxxxxxxxx
  siteId:            text('site_id').notNull().unique().references(() => siteConfig.id, { onDelete: 'cascade' }),
  useRecommended:    integer('use_recommended', { mode: 'boolean' }).default(true),
  priorityFactors:   text('priority_factors'),             // JSON array (subset of 36-factor model)
  schemaTypes:       text('schema_types'),                 // JSON array
  aiPlatformTargets: text('ai_platform_targets'),          // JSON array
  createdAt:         text('created_at').notNull().default(sql`(datetime('now'))`),
  updatedAt:         text('updated_at').notNull().default(sql`(datetime('now'))`),
});

// --- Relations (for Drizzle relational queries) ---

export const siteConfigRelations = relations(siteConfig, ({ many, one }) => ({
  languages:         many(siteLanguage),
  cmsConnection:     one(cmsConnection),
  voiceProfile:      one(voiceProfile),
  topicConfig:       one(topicConfig),
  qualityThresholds: one(qualityThresholds),
  aisoPreferences:   one(aisoPreferences),
}));
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
| Authorisation | Tenant isolation | Drizzle query wrapper adds `tenantId` filter to all queries |
| Input validation | Zod schemas at service boundary | Every service function validates input with Zod before processing |
| Encryption at rest | AES-256 for CMS credentials | `@smithai/crypto` utility wrapping Node.js `crypto.createCipheriv` |
| Credential logging | Auto-redaction | Pino logger with `redact: ['*.password', '*.token', '*.secret', '*.accessToken']` |
| OWASP | Injection, Broken Auth, Sensitive Data Exposure | Parameterised queries (Drizzle), schema validation (Zod), credential encryption |

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
| 1 | SQLite for R1, PostgreSQL for R2 | Zero infrastructure for CLI tool, Drizzle abstracts the swap | PostgreSQL from day 1 (rejected: overkill for CLI) |
| 2 | Drizzle ORM (ADR-007) | Native RLS support (`pgPolicy()`), SQL-first, smaller bundle, no code generation step, works with both SQLite and PostgreSQL | Prisma (rejected: no native RLS, multi-schema tenancy issue #12420), Knex (no type generation) |
| 3 | Zod for validation | Runtime + compile-time validation, great TypeScript inference. Mandatory per P-006 and FF-029/FF-031 | Joi (no TS inference), class-validator (decorators) |
| 4 | AES-256-GCM for credential encryption | Industry standard, built into Node.js crypto | Vault/KMS (overkill for R1), bcrypt (wrong tool — need reversible encryption) |
| 5 | Repository pattern for data access | Testable, swappable, prevents Drizzle leaking into service layer | Direct Drizzle in services (rejected: harder to test, couples to ORM) |
| 6 | Strategy pattern for CMS adapters | Pluggable — add new CMS by implementing interface (NFR #6) | Switch statement (rejected: violates OCP) |
| 7 | Result<T, E> over try/catch | Explicit error handling, composable, no untyped exceptions. Required by P-005 and FF-032 | try/catch (rejected: untyped errors, hidden control flow) |
| 8 | Operation Pattern (P-008) | Consistent 5-step structure for all commands/queries. Enforced by FF-030 | Ad-hoc service methods (rejected: inconsistent, hard to audit) |
| 9 | CloudEvents 1.0 for events | Industry standard envelope, vendor-neutral, required by logging standards §14 | Custom event format (rejected: non-standard, harder to integrate) |
| 10 | Prefixed NanoID for IDs | Human-readable entity type from ID alone (`ste_` = site). Required by API standards §4.3 | CUID2 (rejected: no prefix), UUID v7 (rejected: no prefix, longer) |
| 11 | Circuit breaker for external HTTP | Prevents cascading failures when target sites are down (error handling §8) | Simple retry (rejected: no protection against sustained failures) |

### Dependency List

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| drizzle-orm | ^0.39.x | ORM, SQL-first queries, type-safe schema | Apache 2.0 |
| drizzle-kit | ^0.30.x | Migration generation, schema push | MIT |
| better-sqlite3 | ^11.x | SQLite driver for R1 (swap to @neondatabase/serverless for R2) | MIT |
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
