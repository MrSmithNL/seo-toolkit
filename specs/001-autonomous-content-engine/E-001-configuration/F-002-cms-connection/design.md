---
id: "FTR-CONFIG-002"
type: feature
title: "CMS Connection Setup"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 4-design
priority: must
created: 2026-03-13
last_updated: 2026-03-13
refs:
  requirements: "./requirements.md"

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

# Feature Design — CMS Connection Setup (F-002)

> Slim feature design. See `../epic-design.md` for shared architecture (Prisma schema, module boundary, coding guardrails, cross-cutting concerns).

---

## Architecture Overview

F-002 manages credentials and connectivity to WordPress and Shopify CMS platforms. It is the highest-security feature in E-001 — all credential handling follows AES-256-GCM encryption.

```
src/modules/content-engine/config/
├── cms-connection/
│   ├── cms-connection.service.ts        ← orchestrates connection + verification
│   ├── cms-connection.repository.ts     ← CMSConnection persistence
│   ├── cms-connection.schema.ts         ← Zod input/output schemas
│   ├── adapters/
│   │   ├── cms-adapter.interface.ts     ← Strategy pattern interface
│   │   ├── wordpress.adapter.ts         ← WordPress REST API adapter
│   │   └── shopify.adapter.ts           ← Shopify GraphQL Admin API adapter
│   ├── credential-encryptor.ts          ← AES-256-GCM encrypt/decrypt
│   └── __tests__/
│       ├── cms-connection.service.test.ts
│       ├── wordpress.adapter.test.ts
│       ├── shopify.adapter.test.ts
│       └── credential-encryptor.test.ts
```

---

## Component Design

```typescript
// === Strategy Pattern Interface ===

interface CMSAdapter {
  readonly cmsType: 'wordpress' | 'shopify';

  validateCredentials(credentials: CMSCredentials): Promise<ValidationResult>;
  testPublish(): Promise<TestPublishResult>;
  revokeAccess(): Promise<void>;
}

// === WordPress Adapter ===

class WordPressAdapter implements CMSAdapter {
  readonly cmsType = 'wordpress';

  constructor(
    private siteUrl: string,
    private username: string,
    private applicationPassword: string,
  ) {}

  async validateCredentials(): Promise<ValidationResult> {
    // GET /wp-json/wp/v2/users/me with Basic Auth
  }

  async testPublish(): Promise<TestPublishResult> {
    // POST draft → DELETE draft → confirm write access
  }
}

// === Shopify Adapter ===

class ShopifyAdapter implements CMSAdapter {
  readonly cmsType = 'shopify';

  constructor(
    private storeDomain: string,
    private accessToken: string,
  ) {}

  async validateCredentials(): Promise<ValidationResult> {
    // GraphQL query to Admin API, check scopes
  }

  async testPublish(): Promise<TestPublishResult> {
    // Create draft article → delete → confirm write access
  }
}

// === Service ===

class CMSConnectionService {
  constructor(
    private repo: CMSConnectionRepository,
    private encryptor: CredentialEncryptor,
    private adapterFactory: CMSAdapterFactory,
    private eventEmitter: EventEmitter,
  ) {}

  async connectWordPress(siteId: string, credentials: WPCredentials): Promise<CMSConnection>;
  async connectShopify(siteId: string, credentials: ShopifyCredentials): Promise<CMSConnection>;
  async verifyConnection(siteId: string): Promise<VerificationResult>;
  async revokeConnection(siteId: string): Promise<void>;
}

// === Credential Encryptor ===

class CredentialEncryptor {
  constructor(private encryptionKey: Buffer) {} // from env var

  encrypt(plaintext: string): EncryptedCredential;   // AES-256-GCM
  decrypt(encrypted: EncryptedCredential): string;
}

interface EncryptedCredential {
  ciphertext: string;  // base64
  iv: string;          // base64
  authTag: string;     // base64
}
```

---

## DDD Tactical Patterns

| Pattern | Element | Notes |
|---------|---------|-------|
| **Aggregate** | `CMSConnection` | Child of `SiteConfig`, one-to-one relationship |
| **Value object** | `EncryptedCredential` | Ciphertext + IV + auth tag — never stored in plain text |
| **Value object** | `CMSType` | `'wordpress' \| 'shopify'` — determines adapter selection |
| **Domain event** | `cms.connected` | `{ siteId, cmsType, status }` — triggers downstream |
| **Domain event** | `cms.verified` | `{ siteId, writeAccessConfirmed }` — confirms publish capability |
| **Repository** | `CMSConnectionRepository` | Credential fields always encrypted before persistence |
| **Strategy** | `CMSAdapter` interface | WordPress and Shopify implement the same contract |

---

## State Machine

```
          connectWordPress()
          connectShopify()
                │
                ▼
           ┌─────────┐
           │ pending  │
           └────┬─────┘
                │ verifyConnection()
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
  ┌──────────┐     ┌────────┐
  │ verified  │     │ failed │
  └─────┬─────┘    └────┬───┘
        │                │
        │ revokeConnection()
        │ or credential   │ retry → pending
        │ expiry          │
        ▼                 │
  ┌──────────┐           │
  │ revoked  │ ◄─────────┘
  └──────────┘   revokeConnection()
```

**Transitions:**
- `pending → verified`: Successful `testPublish()` (create draft + delete)
- `pending → failed`: `testPublish()` or `validateCredentials()` fails
- `failed → pending`: User provides new credentials
- `verified → revoked`: Explicit revocation or credential expiry detected
- `failed → revoked`: Explicit revocation

---

## Key Algorithms

### WordPress Credential Validation

```
1. Build Basic Auth header: base64(username:applicationPassword)
2. GET {siteUrl}/wp-json/wp/v2/users/me
3. If 200 → credentials valid, extract user role
4. If 401/403 → credentials invalid
5. If network error → site unreachable
```

### Shopify Credential Validation

```
1. POST to https://{storeDomain}/admin/api/2024-01/graphql.json
   Header: X-Shopify-Access-Token: {accessToken}
   Query: { shop { name plan { displayName } } }
2. If 200 → token valid, extract shop info
3. Check required scopes: read_content, write_content
4. If missing scopes → partial access error
```

### Test Publish (Write Access Verification)

```
1. Create a draft post/article via CMS API
   - WordPress: POST /wp-json/wp/v2/posts { title: "SEO Toolkit Test", status: "draft" }
   - Shopify: mutation articleCreate { ... }
2. Capture the created resource ID
3. Delete the draft immediately
   - WordPress: DELETE /wp-json/wp/v2/posts/{id}?force=true
   - Shopify: mutation articleDelete { ... }
4. If both operations succeed → write access confirmed
5. If create fails → no write permission
6. If delete fails → log warning, write access partial (draft exists)
```

### AES-256-GCM Encryption

```
1. Generate random 12-byte IV per encryption
2. Create cipher: crypto.createCipheriv('aes-256-gcm', key, iv)
3. Encrypt plaintext → ciphertext
4. Extract 16-byte auth tag
5. Store: { ciphertext: base64, iv: base64, authTag: base64 }
6. Decryption: recreate decipher with same key + iv + authTag
```

---

## API Surface

R1 CLI functions:

| Function | Signature | Description |
|----------|-----------|-------------|
| `connectWordPress` | `(siteId, credentials: WPCredentials) => Promise<CMSConnection>` | Store encrypted credentials, set status=pending |
| `connectShopify` | `(siteId, credentials: ShopifyCredentials) => Promise<CMSConnection>` | Store encrypted token, set status=pending |
| `verifyConnection` | `(siteId) => Promise<VerificationResult>` | Validate + test publish, update status |

R2 HTTP routes:

| Method | Path | Handler |
|--------|------|---------|
| `POST` | `/sites/:id/cms` | `connectCMS` |

---

## Integration Points

| External System | Protocol | Purpose | Timeout | Retry |
|----------------|----------|---------|---------|-------|
| WordPress REST API | HTTP (Basic Auth) | Credential validation, test publish | 10s | 1 retry after 5s |
| Shopify GraphQL Admin API | HTTPS (Access Token) | Credential validation, test publish | 10s | 1 retry after 5s |

---

## Testing Strategy

| Category | What to Test | Approach |
|----------|-------------|----------|
| **Unit** | Credential encryption roundtrip (encrypt → decrypt = original) | Direct function tests |
| **Unit** | WordPress adapter (valid creds, invalid creds, unreachable) | Mock HTTP responses |
| **Unit** | Shopify adapter (valid token, invalid token, missing scopes) | Mock GraphQL responses |
| **Unit** | State machine transitions (valid and invalid transitions) | Service tests |
| **Integration** | Full connection flow (connect → verify → status update) | In-memory SQLite |
| **Security** | Credentials never appear in logs or error messages | Log output assertion |
| **Security** | Encrypted fields not readable without key | Database inspection |

---

## Feature-Specific Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Strategy pattern for CMS adapters | Adding a new CMS (e.g., Contentful) = implement interface, no existing code changes |
| 2 | AES-256-GCM (not bcrypt) | Credentials must be reversible — we need to use them for API calls |
| 3 | Test publish as verification step | Reading API ≠ writing. Must confirm actual write access before pipeline trusts it |
| 4 | Encryption key from environment variable | Never hardcoded, never in config files. `ENCRYPTION_KEY` env var |
| 5 | Separate pending/verified states | User can save credentials without immediate verification (offline setup) |
