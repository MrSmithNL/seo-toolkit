---
id: "FTR-CONFIG-001"
type: feature
title: "Site URL Registration & Crawl Config"
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

# Site URL Registration & Crawl Config — Requirements

## Problem Statement

The content pipeline needs to know which site it's generating content for. Without a registered site URL, no downstream operation (keyword research, content generation, CMS publishing, monitoring) has context. Today, site details are entered manually each session — this blocks autonomous operation.

## Research Summary

### Competitor Analysis

| Capability | SEObot | SEO.ai | Byword | Koala | Our Approach |
|-----------|:------:|:------:|:------:|:-----:|:------------:|
| URL-and-go (single input) | ✅ | ✅ | ✅ | ❌ | ✅ |
| Auto-detect CMS type | ❌ | ❌ | ✅ | ❌ | ✅ |
| Crawl existing content | ✅ | ✅ | ❌ | ❌ | ✅ |
| Detect languages/locales | ✅ | ❌ | ❌ | ❌ | ✅ |
| Content inventory from sitemap | ❌ | ✅ | ❌ | ❌ | ✅ |

### Key Findings

- URL-and-go with auto-detection is the modern standard (SEObot, Byword)
- Sitemap parsing gives the most reliable content inventory
- CMS detection via known URL patterns (wp-json, cdn.shopify.com) is reliable
- Language detection via hreflang tags and Shopify locale URLs is standard

### Sources

- `research/e001-configuration-setup-patterns.md` §1 (Onboarding UX)
- `E-001-configuration/research/phase2-analysis.md` §Spec-as-Context

## Impact Map

```
Goal: Enable autonomous content pipeline for any target site
  └─ Actor: Agency operator (Malcolm) / Future SaaS user
       └─ Impact: Can register a new site in under 2 minutes
            ├─ Deliverable: URL input with auto-crawl
            ├─ Deliverable: CMS type detection
            ├─ Deliverable: Language/locale detection
            └─ Deliverable: Content inventory from sitemap
```

## Domain Model

```
SiteConfig {
  id: UUID
  tenant_id: UUID (FK -> Tenant.id, injected from AsyncLocalStorage context — NOT user input)
  url: URL (validated, normalised)
  name: string (auto-derived from site title, editable)
  cms_type: enum (wordpress, shopify, unknown)
  cms_detected_at: timestamp
  languages: Language[] (from hreflang/locales)
  primary_language: Language
  content_count: int (from sitemap)
  last_crawled: timestamp
  created_at: timestamp
  updated_at: timestamp
}

Language {
  code: string (BCP-47: "en", "nl", "de")
  name: string ("English", "Dutch", "German")
  url_pattern: string (e.g., "/nl/", "nl.example.com")
}
```

## User Stories

### US-001: Register a site by URL

**As a** content pipeline operator, **I want** to register a target site by entering its URL, **so that** all downstream pipeline stages know which site to target.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

WHEN a user enters a valid URL
THE SYSTEM SHALL normalise the URL (add https://, strip trailing slash, resolve www/non-www)
AND store the site configuration
AND initiate an automatic crawl of the site

WHEN a user enters an invalid URL (malformed, unreachable, non-HTTP)
THE SYSTEM SHALL reject the input with a specific error message explaining what's wrong

WHEN a user enters a URL that is already registered
THE SYSTEM SHALL inform the user and offer to update the existing config or create a duplicate

**Examples:**

| Scenario | Input | Expected Output |
|----------|-------|----------------|
| Happy path | `hairgenetix.com` | Normalised to `https://www.hairgenetix.com`. Stored. Crawl initiated. |
| With scheme | `https://digitalbouwers.nl` | Stored as-is. Crawl initiated. |
| Invalid URL | `not a url!!!` | Error: "Invalid URL format. Enter a domain like example.com" |
| Unreachable | `https://thisdomaindoesnotexist12345.com` | Error: "Could not reach this URL. Check the domain is correct and the site is live." |
| Duplicate | `hairgenetix.com` (already registered) | "This site is already registered. Update existing config or create new?" |
| Trailing slash | `https://hairgenetix.com/` | Normalised to `https://www.hairgenetix.com`. Same as without slash. |

### US-002: Auto-detect CMS type

**As a** content pipeline operator, **I want** the system to automatically detect whether the site runs WordPress or Shopify, **so that** the correct CMS adapter is used for publishing.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN the system crawls a registered site
THE SYSTEM SHALL check for WordPress indicators (wp-json endpoint returning 200, wp-content paths in HTML)
AND check for Shopify indicators (cdn.shopify.com in source, /admin path pattern, Shopify meta tags)
AND set the cms_type field accordingly

WHEN neither WordPress nor Shopify is detected
THE SYSTEM SHALL set cms_type to "unknown" and inform the user

**Examples:**

| Scenario | Input URL | Detection Method | Expected cms_type |
|----------|----------|-----------------|:-----------------:|
| WordPress site | `digitalbouwers.nl` | GET `/wp-json/wp/v2/` returns 200 | wordpress |
| Shopify site | `hairgenetix.com` | HTML contains `cdn.shopify.com` | shopify |
| Neither | `example-static-site.com` | No WP or Shopify signals | unknown |
| Shopify with custom domain | `skingenetix.com` | Shopify CDN + meta tag | shopify |

### US-003: Detect available languages/locales

**As a** content pipeline operator, **I want** the system to detect all available languages on the target site, **so that** content can be generated and published in the correct locales.

**Priority:** Must
**Size:** M

**Acceptance Criteria:**

WHEN the system crawls a registered site
THE SYSTEM SHALL check for hreflang tags in HTML head
AND check for Shopify locale URLs (/{locale}/ pattern)
AND check for WPML/Polylang alternate links
AND populate the languages array with detected locales

WHEN no language indicators are found
THE SYSTEM SHALL default to the site's primary language (from html lang attribute or "en" fallback)

**Examples:**

| Scenario | Site | Detection | Expected Languages |
|----------|------|-----------|-------------------|
| Shopify multi-lang | hairgenetix.com | 9 Shopify locales (en, nl, de, fr, es, it, pt, sv, da) | 9 languages, primary: en |
| WordPress single-lang | digitalbouwers.nl | html lang="nl", no hreflang | 1 language: nl |
| Shopify dual-lang | skingenetix.com | en + nl locales | 2 languages, primary: en |

### US-004: Crawl content inventory

**As a** content pipeline operator, **I want** the system to count existing content on the site, **so that** I know the starting point for content gap analysis.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

WHEN the system crawls a registered site
THE SYSTEM SHALL fetch and parse sitemap.xml (or sitemap_index.xml)
AND count the total number of content URLs (excluding images, CSS, JS)
AND store the content_count

WHEN no sitemap is found
THE SYSTEM SHALL set content_count to 0 and note "No sitemap found — content inventory unavailable"

**Examples:**

| Scenario | Site | Sitemap | Expected Count |
|----------|------|---------|:--------------:|
| Standard sitemap | hairgenetix.com | sitemap.xml with 45 URLs | 45 |
| Sitemap index | large-site.com | sitemap_index.xml → 3 sub-sitemaps | Sum of all sub-sitemap URLs |
| No sitemap | new-site.com | 404 on /sitemap.xml | 0 (with note) |

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN a user registers a site THE SYSTEM SHALL complete the initial crawl WITHIN 30 seconds | p95 < 30s | Integration test with timer | Yes |
| 2 | **Security** | WHEN the system crawls a site THE SYSTEM SHALL NOT store any site content, only metadata (CMS type, language, URL count) | Zero content storage | Code review + test | Yes |
| 3 | **Reliability** | WHEN a crawl fails (network timeout, DNS error) THE SYSTEM SHALL retry once after 5 seconds, then store partial results with error note | Retry + graceful degradation | Integration test with mock failures | Yes |
| 4 | **Scalability** | N/A — single-user system for V1, max ~10 sites | — | — | No |
| 5 | **Availability** | N/A — not a hosted service for V1 (CLI/local pipeline) | — | — | No |
| 6 | **Maintainability** | WHEN a new CMS type needs to be added THE SYSTEM SHALL support it by adding a detector module without modifying existing code | Pluggable detector pattern | Architecture review | No |
| 7 | **Portability** | N/A — Node.js runtime, no platform-specific dependencies | — | — | No |
| 8 | **Accessibility** | N/A — CLI interface for V1 (no UI) | — | — | No |
| 9 | **Usability** | WHEN registering a site THE SYSTEM SHALL require no more than 1 input (URL) before starting the crawl | Max 1 required field | Manual verification | No |
| 10 | **Interoperability** | WHEN detecting CMS type THE SYSTEM SHALL use standard HTTP requests only (no browser rendering required) | Standard fetch/HTTP | Integration test | Yes |
| 11 | **Compliance** | N/A — no PII collected, no regulated data | — | — | No |
| 12 | **Data Retention** | WHEN a site is deleted THE SYSTEM SHALL remove all associated config data within the same operation | Cascade delete | Integration test | Yes |
| 13 | **Backup / Recovery** | N/A — config is regenerable by re-crawling | — | — | No |
| 14 | **Logging** | WHEN a crawl completes THE SYSTEM SHALL log: URL, CMS detected, languages found, content count, duration, any errors | Structured log entry | Log assertion in test | Yes |
| 15 | **Cost** | WHEN crawling a site THE SYSTEM SHALL use no paid APIs (HTTP requests only) | $0 per crawl | Code review | No |
| 16 | **Capacity** | WHEN storing site configs THE SYSTEM SHALL support up to 100 sites per installation | 100 sites | Load test (future) | No |
| 17 | **Internationalisation** | WHEN detecting languages THE SYSTEM SHALL use BCP-47 language codes | BCP-47 compliance | Unit test | Yes |
| 18 | **Extensibility** | WHEN adding a new detection strategy THE SYSTEM SHALL support it via the pluggable detector pattern (see #6) | New detector = new module | Architecture review | No |
| 19 | **Operation Pattern** | WHEN any command or query is executed THE SYSTEM SHALL follow the 5-step Operation pattern (P-008): Zod input → OperationContext → business logic → persist → emit event + return Result<T, OperationError> | All operations return Result type | Architecture fitness test FF-030 | Yes |
| 20 | **Error Handling** | WHEN a crawl or detection operation fails THE SYSTEM SHALL return an OperationError (not throw) with RFC 7807-compatible error codes and `suggested_action` field | Zero naked `throw` in commands/queries | FF-032 + code review | Yes |
| 21 | **Structured Logging** | WHEN any operation executes THE SYSTEM SHALL emit `operation.started`, `operation.completed`, and `operation.failed` structured JSON events via pino with correlationId + tenantId | 3 log events per operation | Log assertion in integration test | Yes |
| 22 | **Tenant Isolation** | WHEN querying site configs THE SYSTEM SHALL enforce RLS so Tenant A cannot read/update/delete Tenant B's data. Cross-tenant access returns 404 (not 403). | `tenant-isolation.test.ts` passes | Integration test (FF-034) | Yes |
| 23 | **Idempotency** | WHEN registering a site THE SYSTEM SHALL accept an optional idempotencyKey. Duplicate requests with the same key return the original result without creating duplicates. | Duplicate request = same response | Integration test | Yes |
| 24 | **Prefixed IDs** | WHEN creating a SiteConfig THE SYSTEM SHALL generate IDs with `ste_` prefix (e.g., `ste_abc123def456`) using NanoID or UUID v7 | All IDs match `ste_*` pattern | Unit test | Yes |
| 25 | **Serialisable I/O** | WHEN returning data from any operation THE SYSTEM SHALL use ISO 8601 strings for dates (never Date objects), plain objects only (no class instances) | JSON.parse(JSON.stringify(output)) === output | Unit test | Yes |
| 26 | **Contract Completeness** | WHEN exposing commands or queries THE SYSTEM SHALL have a Zod input schema AND explicit TypeScript return type for each | Every public function has Zod + return type | FF-029 | Yes |
| 27 | **No Module State** | THE SYSTEM SHALL NOT use `let` or `var` at module scope in `src/` files (except type exports and `const`) | Zero mutable module-level state | FF-033 | Yes |
| 28 | **PII Redaction** | WHEN logging site data THE SYSTEM SHALL redact any email, phone, IP address, or personal data fields using pino's redaction config | PII fields show `[REDACTED]` in logs | Log inspection test | Yes |
| 29 | **Circuit Breaker** | WHEN making HTTP requests to target sites THE SYSTEM SHALL use a circuit breaker (5 failures / 60s window → open for 30s) to prevent cascading failures | Circuit breaker state logged | Integration test | No |

## Out of Scope

- Deep content analysis (reading article text, extracting topics) — that's E-002
- CMS connection/authentication — that's F-002
- Content quality assessment of existing pages — that's E-003
- Recurring re-crawls (scheduled refresh) — deferred to V2

## Open Questions

- [x] Should we detect CMS type from HTTP headers or HTML content? **Answer:** Both — check wp-json endpoint first (faster), fall back to HTML parsing.
- [x] What if the site uses a CDN that masks CMS signals? **Answer:** If neither CMS detected, set to "unknown" and let user manually select in F-002.

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| HTTP/HTTPS access to target site | External | Ready | All stories |
| Sitemap.xml convention | External (standard) | Ready | US-004 |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | Target sites have standard CMS indicators detectable via HTTP | High | Test against 3 real sites |
| A2 | Sitemap.xml exists on most production sites | Medium | Fallback to 0 count if missing |
