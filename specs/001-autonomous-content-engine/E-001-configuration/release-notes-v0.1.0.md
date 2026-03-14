# Release Notes — E-001 Configuration & Setup v0.1.0

## Release Date

2026-03-14

## What's New

The first release of the Autonomous Content Engine's configuration module. This lays the foundation for the entire content pipeline by enabling one-time site configuration that all downstream epics (Research, Generate, Publish, Monitor) depend on.

1. **Site URL Registration & Auto-Detection** — Register a site URL and automatically detect its CMS platform, available languages, and sitemap structure
2. **CMS Connection Setup** — Connect WordPress (REST API) and Shopify (GraphQL Admin API) with credential verification and write-access testing
3. **Brand Voice Training** — Define a voice profile per site (tone, vocabulary, sentence structure) with skip/default option for V1
4. **Topic & Niche Configuration** — Configure topic areas via seed keywords, auto-inference from existing content, or GSC import
5. **Quality Threshold Settings** — Set minimum SEO score, AISO score, readability target, and word count range with sensible defaults
6. **AISO Scoring Preferences** — Select priority factors from the 36-factor AISO model, configure schema types, and set AI platform targets

## Features

### F-001: Site URL Registration & Crawl Config

Register a target site URL. The system automatically:
- Detects the CMS platform (WordPress or Shopify) by inspecting HTTP responses and page content
- Discovers available languages and locales (tested with Hairgenetix's 9 languages)
- Parses the sitemap (including nested `sitemap_index` files) to inventory existing content
- Validates URL format and reachability with configurable timeouts (30s default)

### F-002: CMS Connection Setup

Connect your CMS with encrypted credential storage (AES-256-GCM):
- **WordPress** — Connect via REST API using application passwords. Verifies read and write permissions.
- **Shopify** — Connect via GraphQL Admin API using custom app credentials. Verifies blog article creation scope.
- Test publish capability to confirm write access before the pipeline runs
- Circuit breaker protection on all external CMS API calls

### F-003: Brand Voice Training

Define how the content engine writes for each site:
- Voice profile stores tone, vocabulary preferences, and sentence structure guidelines
- Skip option uses a professional default voice (recommended for V1)
- One voice profile per site (multi-voice support planned for V2)

### F-004: Topic & Niche Configuration

Tell the engine what to write about:
- Manual seed keyword entry (minimum 5 keywords)
- Auto-inference from existing site content via sitemap analysis
- Topic cluster detection for content hub planning
- Priority ranking for topic areas

### F-005: Quality Threshold Settings

Set the quality gates that content must pass before publishing:
- Minimum SEO content score (0-100, default: 70)
- Minimum AISO score (0-10, default: 7)
- Readability target (grade level, default: 8)
- Word count range (min/max, default: 1200-2500)
- Gate enforcement mode: block, warn, or allow
- Publish mode: draft or auto-publish

### F-006: AISO Scoring Preferences

Configure AI search optimisation priorities:
- Select which factors from the 36-factor AISO model to prioritise
- Configure schema.org types to generate per article (FAQ, HowTo, Article, etc.)
- Set AI platform targets (ChatGPT, Perplexity, Gemini)
- Recommended defaults provided based on agency experience

## Technical Details

| Metric | Value |
|--------|-------|
| Tasks completed | 33/33 |
| Total tests | 255 (253 unit/integration + 2 smoke) |
| Test files | 27 |
| TypeScript mode | Strict (zero suppressions) |
| ORM | Drizzle (ADR-007) with SQLite (local) / PostgreSQL (future) |
| Test framework | Vitest with in-memory SQLite |
| Build duration | ~30h actual (90h estimated) |
| Framework compliance | 97% across 12 frameworks |
| Spec accuracy | 97% (1 design adjustment during build) |

### Architecture

- **Pattern:** Repository + Service layers with dependency injection
- **Operations:** CQS (Command Query Separation) with `Result<T, OperationError>` returns — no naked `throw`
- **IDs:** Prefixed NanoIDs (`ste_`, `cms_`, `vce_`, `tpc_`, `tcl_`, `qth_`, `asp_`, `slg_`, `tnt_`)
- **Errors:** RFC 7807 problem details with `suggested_action` field
- **Events:** 7 CloudEvents 1.0 domain events declared
- **Logging:** Structured JSON via pino with PII redaction
- **Security:** AES-256-GCM encryption for CMS credentials, API keys never stored in plain text
- **Multi-tenancy:** Tenant context via `AsyncLocalStorage`, scoped queries, tenant isolation enforced (404 not 403)
- **Fitness functions:** 7 automated architecture constraints (FF-028 to FF-034)

## Known Limitations

- **CLI only** — No web UI. All configuration via command-line interface. Web UI planned for AISOGEN SaaS vertical.
- **Local SQLite only** — Data stored in local SQLite database. PostgreSQL with RLS planned for multi-tenant SaaS deployment.
- **Two CMS adapters** — Only WordPress (REST API) and Shopify (GraphQL Admin API) supported. Covers 90%+ of target market. Additional adapters (Wix, Squarespace, Webflow) planned for future releases.
- **No credential refresh** — CMS tokens assumed long-lived. Automatic token refresh planned for V2.
- **Single voice per site** — One brand voice profile per site. Multi-voice (e.g., per content type) planned for V2.
- **No GSC OAuth flow** — Google Search Console import requires manual API key setup. OAuth flow planned for web UI.
- **No real-time validation** — Site detection runs at registration time. Changes to the site (new CMS, new languages) require re-registration.
- **WordPress false-positive risk** — WordPress detector validates response body to avoid false positives on Shopify password pages (bug found and fixed during staging).

## Breaking Changes

None (initial release).

## Dependencies

### Runtime

| Package | Version | Purpose |
|---------|---------|---------|
| `drizzle-orm` | ^0.39.3 | Database ORM (schema-as-contract) |
| `better-sqlite3` | ^11.8.1 | SQLite driver for local storage |
| `nanoid` | ^5.1.5 | Prefixed ID generation |
| `pino` | ^9.6.0 | Structured JSON logging |
| `zod` | ^3.24.2 | Input validation and schema contracts |

### Development

| Package | Version | Purpose |
|---------|---------|---------|
| `vitest` | ^3.0.9 | Test framework |
| `drizzle-kit` | ^0.30.5 | Schema migration tooling |
| `typescript` | ^5.8.2 | TypeScript compiler (strict mode) |
| `yaml` | ^2.8.2 | Conformance suite YAML parsing |

## Upgrade Path

N/A (initial release). Future upgrades will follow the expand-migrate-contract pattern for schema changes, with feature flags controlling feature availability.
