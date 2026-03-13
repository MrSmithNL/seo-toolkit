---
id: "FTR-CONFIG-002"
type: feature
title: "CMS Connection Setup"
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

# CMS Connection Setup — Requirements

## Problem Statement

After a site is registered (F-001), the content pipeline needs write access to the CMS to publish articles. Without verified CMS credentials, the pipeline can research and generate content but cannot publish. Today, CMS credentials are entered manually per session and never persisted — blocking autonomous operation.

## Research Summary

### Competitor Analysis

| Capability | SEObot | Koala | Byword | Our Approach |
|-----------|:------:|:-----:|:------:|:------------:|
| WordPress REST API | ✅ | ✅ (+ plugin) | ✅ | ✅ |
| Shopify Admin API | ✅ (Custom App) | ❌ | ⚠️ (pending) | ✅ (Custom App) |
| Test publish verification | ❌ | ❌ | ❌ | ✅ |
| Credential encryption at rest | Unknown | Unknown | Unknown | ✅ (AES-256) |
| Draft/publish toggle | ❌ | ✅ | ✅ | ✅ |

### Key Findings

- WordPress Application Passwords (WordPress 5.6+) are the standard auth method — no OAuth, no plugin needed
- Shopify Custom App + Admin API access token (`shpat_*`) requires no Shopify App Store approval
- No competitor verifies write access with a test publish during setup — we can differentiate here
- Credentials must be encrypted at rest (Constitutional Constraint #1)

### Sources

- `research/e001-configuration-setup-patterns.md` §2 (CMS Connection)
- `E-001-configuration/research/phase2-analysis.md` §Spec-as-Context for F-002

## Impact Map

```
Goal: Enable autonomous article publishing to any configured CMS
  +-- Actor: Agency operator (Malcolm) / Future SaaS user
       +-- Impact: Can connect a CMS once and publish repeatedly
            +-- Deliverable: WordPress connection via Application Password
            +-- Deliverable: Shopify connection via Custom App token
            +-- Deliverable: Connection verification (test publish)
            +-- Deliverable: Encrypted credential storage
```

## Domain Model

```
CMSConnection {
  id: UUID
  site_id: UUID (FK -> SiteConfig.id)
  cms_type: enum (wordpress, shopify)
  status: enum (pending, verified, failed, revoked)

  # WordPress-specific
  wp_site_url: URL (nullable)
  wp_username: string (nullable, encrypted)
  wp_application_password: string (nullable, encrypted)

  # Shopify-specific
  shopify_store_domain: string (nullable, e.g., "a24be5-c5.myshopify.com")
  shopify_access_token: string (nullable, encrypted, "shpat_*")

  # Common
  verified_at: timestamp (nullable)
  last_used_at: timestamp (nullable)
  default_publish_status: enum (draft, published) [default: draft]
  created_at: timestamp
  updated_at: timestamp
}
```

## User Stories

### US-001: Connect WordPress site via Application Password

**As a** content pipeline operator, **I want** to connect my WordPress site by entering my username and application password, **so that** the pipeline can publish articles to my WordPress blog.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

WHEN a user provides WordPress credentials (site URL, username, application password)
THE SYSTEM SHALL validate the credentials by making a GET request to `{site_url}/wp-json/wp/v2/users/me`
AND if valid, store the credentials encrypted (AES-256)
AND set connection status to "verified"

WHEN credentials are invalid (401 response)
THE SYSTEM SHALL return error "WordPress credentials are invalid. Check your username and application password."
AND NOT store any credentials

WHEN the WordPress site does not have the REST API enabled
THE SYSTEM SHALL return error "WordPress REST API is not available on this site. Ensure REST API is enabled."

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | URL: digitalbouwers.nl, user: admin, app password: xxxx xxxx xxxx | Verified. Credentials stored encrypted. Status: verified. |
| Invalid password | URL: digitalbouwers.nl, user: admin, app password: wrong | Error: "WordPress credentials are invalid." No credentials stored. |
| REST API disabled | URL: locked-down-wp.com, user: admin, app password: valid | Error: "WordPress REST API is not available." No credentials stored. |
| WordPress.com site | URL: mysite.wordpress.com, user: admin, app password: valid | Error: "WordPress.com sites are not supported. Use self-hosted WordPress." |

### US-002: Connect Shopify store via Custom App token

**As a** content pipeline operator, **I want** to connect my Shopify store by entering my Admin API access token, **so that** the pipeline can publish articles to my Shopify blog.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

WHEN a user provides a Shopify store domain and access token
THE SYSTEM SHALL validate the token by querying the Shopify GraphQL Admin API (`{store}.myshopify.com/admin/api/2024-10/graphql.json`)
AND verify `read_content` and `write_content` scopes are present
AND if valid, store the token encrypted (AES-256)
AND set connection status to "verified"

WHEN the token is invalid or missing required scopes
THE SYSTEM SHALL return a specific error identifying what's wrong (invalid token vs missing scopes)
AND NOT store any credentials

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | Domain: a24be5-c5.myshopify.com, token: shpat_xxx | Verified. Token stored encrypted. Status: verified. |
| Invalid token | Domain: a24be5-c5.myshopify.com, token: shpat_invalid | Error: "Shopify access token is invalid." |
| Missing scopes | Domain: a24be5-c5.myshopify.com, token: shpat_readonly | Error: "Token is missing required scopes: write_content." |
| Wrong domain | Domain: nonexistent.myshopify.com, token: shpat_xxx | Error: "Could not reach Shopify store. Check the store domain." |

### US-003: Verify write access with test publish

**As a** content pipeline operator, **I want** the system to verify it can actually publish content after connecting, **so that** I know the pipeline will work before generating articles.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN a CMS connection is verified (credentials valid)
THE SYSTEM SHALL create a test draft post with title "[SEO Toolkit] Connection Test" and minimal body
AND if the draft is created successfully, immediately delete it
AND confirm "Write access verified — your CMS connection is working"

WHEN the test publish fails (permissions error, quota exceeded)
THE SYSTEM SHALL report the specific failure and set connection status to "failed"
AND advise the user on how to fix the permissions

**Examples:**

| Scenario | CMS | Test Action | Expected Result |
|----------|-----|------------|-----------------|
| WordPress success | WP | POST /wp-json/wp/v2/posts (status: draft) | Draft created, deleted, "Write access verified" |
| WordPress no write | WP | POST returns 403 | "Cannot create posts. Check Application Password has 'Editor' or 'Author' role." |
| Shopify success | Shopify | createArticle mutation (draft) | Article created, deleted, "Write access verified" |
| Shopify no blog | Shopify | No blogs exist | "No blogs found on this Shopify store. Create a blog first in Shopify admin." |

### US-004: Set default publish status

**As a** content pipeline operator, **I want** to choose whether articles are published as drafts or live, **so that** I can review content before it goes live.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

WHEN configuring a CMS connection
THE SYSTEM SHALL offer a publish mode setting with options: "draft" (default) or "published"

WHEN publish mode is "draft"
THE SYSTEM SHALL create all articles with draft/unpublished status

WHEN publish mode is "published"
THE SYSTEM SHALL create all articles with published/active status
AND warn the user: "Articles will be published immediately without review"

**Examples:**

| Scenario | Setting | Expected Behaviour |
|----------|---------|-------------------|
| Default | Not set | Articles created as drafts |
| Draft mode | draft | Articles created as drafts |
| Publish mode | published | Articles published immediately + warning shown at config time |

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN verifying CMS credentials THE SYSTEM SHALL complete validation WITHIN 10 seconds | p95 < 10s | Integration test with timer | Yes |
| 2 | **Security** | WHEN storing CMS credentials THE SYSTEM SHALL encrypt them with AES-256 at rest AND never include credentials in log output or error messages | Zero plaintext credentials in storage or logs | Security audit + grep for credential patterns | Yes |
| 3 | **Reliability** | WHEN a CMS API is temporarily unavailable THE SYSTEM SHALL retry once after 5 seconds AND report the transient error if retry fails | Retry + clear error reporting | Integration test with mock timeout | Yes |
| 4 | **Scalability** | N/A — single-user system for V1, max ~10 CMS connections | — | — | No |
| 5 | **Availability** | N/A — not a hosted service for V1 | — | — | No |
| 6 | **Maintainability** | WHEN a new CMS type needs to be supported THE SYSTEM SHALL support it by adding an adapter module without modifying existing adapters | Pluggable adapter pattern (Strategy pattern) | Architecture review | No |
| 7 | **Portability** | N/A — Node.js runtime, no platform-specific dependencies | — | — | No |
| 8 | **Accessibility** | N/A — CLI interface for V1 | — | — | No |
| 9 | **Usability** | WHEN connecting a CMS THE SYSTEM SHALL provide step-by-step instructions for creating Application Passwords (WP) or Custom Apps (Shopify) | In-context guidance | Manual verification | No |
| 10 | **Interoperability** | WHEN connecting to WordPress THE SYSTEM SHALL use the standard REST API (wp-json/wp/v2). WHEN connecting to Shopify THE SYSTEM SHALL use the GraphQL Admin API (2024-10 version) | Standard API conformance | Integration tests against real APIs | Yes |
| 11 | **Compliance** | WHEN storing credentials THE SYSTEM SHALL comply with OWASP credential storage guidelines (no plaintext, no reversible encoding without encryption key management) | OWASP compliance | Security review | Yes |
| 12 | **Data Retention** | WHEN a CMS connection is deleted THE SYSTEM SHALL securely wipe all stored credentials (overwrite before delete) | Secure deletion | Integration test | Yes |
| 13 | **Backup / Recovery** | WHEN credentials are lost THE SYSTEM SHALL support re-entry (user can reconnect with new credentials without losing site config) | Reconnection flow | Integration test | No |
| 14 | **Logging** | WHEN a CMS connection attempt occurs THE SYSTEM SHALL log: CMS type, store domain (not credentials), outcome (success/failure), error type if failed, duration | Structured log with no secrets | Log assertion in test | Yes |
| 15 | **Cost** | WHEN connecting to CMS THE SYSTEM SHALL use no paid APIs (WordPress REST + Shopify Admin API are free) | $0 per connection | Code review | No |
| 16 | **Capacity** | N/A — one connection per site, max ~10 sites | — | — | No |
| 17 | **Internationalisation** | N/A — CMS APIs are language-agnostic | — | — | No |
| 18 | **Extensibility** | WHEN adding support for a new CMS THE SYSTEM SHALL only require implementing the CMSAdapter interface (connect, verify, testPublish, publish, unpublish) | Interface-based extension | Architecture review | No |
| 19 | **Operation Pattern** | WHEN any command or query is executed THE SYSTEM SHALL follow the 5-step Operation pattern (P-008): Zod input → OperationContext → business logic → persist → emit event + return Result<T, OperationError> | All operations return Result type | Architecture fitness test FF-030 | Yes |
| 20 | **Error Handling** | WHEN an operation fails THE SYSTEM SHALL return an OperationError (not throw) with RFC 7807-compatible error codes and `suggested_action` field | Zero naked `throw` in commands/queries | FF-032 + code review | Yes |
| 21 | **Structured Logging** | WHEN any CMS operation executes THE SYSTEM SHALL emit `operation.started`, `operation.completed`, and `operation.failed` structured JSON events via pino with correlationId + tenantId | 3 log events per operation | Log assertion in integration test | Yes |
| 22 | **Tenant Isolation** | WHEN querying CMS connection data THE SYSTEM SHALL enforce RLS so Tenant A cannot read/update/delete Tenant B's CMS credentials. Cross-tenant access returns 404 (not 403). | `tenant-isolation.test.ts` passes | Integration test (FF-034) | Yes |
| 23 | **Idempotency** | WHEN creating CMS connections THE SYSTEM SHALL accept an optional idempotencyKey. Duplicate requests with the same key return the original result without creating duplicates. | Duplicate request = same response | Integration test | Yes |
| 24 | **Serialisable I/O** | WHEN returning CMS connection data from any operation THE SYSTEM SHALL use ISO 8601 strings for dates (never Date objects), plain objects only (no class instances) | JSON.parse(JSON.stringify(output)) === output | Unit test | Yes |
| 25 | **Contract Completeness** | WHEN exposing CMS commands or queries THE SYSTEM SHALL have a Zod input schema AND explicit TypeScript return type for each | Every public function has Zod + return type | FF-029 | Yes |
| 26 | **No Module State** | THE SYSTEM SHALL NOT use `let` or `var` at module scope in CMS connection `src/` files (except type exports and `const`) | Zero mutable module-level state | FF-033 | Yes |
| 27 | **PII Redaction** | WHEN logging CMS connection data THE SYSTEM SHALL redact any email, phone, IP address, or personal data fields using pino's redaction config | PII fields show `[REDACTED]` in logs | Log inspection test | Yes |
| 28 | **Circuit Breaker** | WHEN making API calls to WordPress or Shopify CMS THE SYSTEM SHALL use a circuit breaker (5 failures / 60s window → open for 30s) to prevent cascading failures from CMS outages | Circuit breaker state logged | Integration test | No |
| 29 | **Credential Security** | WHEN storing CMS API credentials THE SYSTEM SHALL encrypt at rest using AES-256 and NEVER log credentials even at DEBUG level | Zero plaintext credentials in logs or DB | Security review + FF-032 | Yes |
| 30 | **Prefixed IDs** | WHEN creating a CMSConnection THE SYSTEM SHALL generate IDs with `cms_` prefix using NanoID or UUID v7 | All IDs match `cms_*` pattern | Unit test | Yes |

## Out of Scope

- OAuth flows for Shopify App Store listing — we use Custom App pattern (no approval needed)
- WordPress plugin development — REST API only for V1
- Zapier/Make webhook integration — deferred to V2
- Credential rotation/refresh automation — credentials don't expire for V1 (Application Passwords + Custom App tokens are long-lived)
- Multi-blog selection within a single Shopify store — use default blog for V1

## Open Questions

- [x] Should we support WordPress.com hosted sites? **Answer:** No — WordPress.com doesn't support Application Passwords. Self-hosted WordPress only.
- [x] Should we store one set of credentials per site or allow multiple? **Answer:** One per site for V1. Multiple CMS connections per site is a V2 feature.
- [x] Shopify API version pinning? **Answer:** Pin to `2024-10` (latest stable at time of spec). Update as part of routine maintenance.

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 (Site Registration) | Internal | In progress | CMS type detection feeds adapter selection |
| WordPress REST API | External | Ready | US-001 |
| Shopify GraphQL Admin API | External | Ready | US-002 |
| Encryption key management | Internal | Needs design (Phase 4) | US-001, US-002 (credential storage) |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | WordPress Application Passwords don't expire unless manually revoked | High | Confirmed by WordPress docs |
| A2 | Shopify Custom App access tokens don't expire | High | Confirmed by Shopify docs + SEObot pattern |
| A3 | Test publish + immediate delete won't trigger CMS rate limiting | Medium | Test against real Shopify and WordPress stores |
| A4 | AES-256 encryption is sufficient for credential storage (no HSM needed for V1) | High | OWASP guidelines for non-enterprise |
