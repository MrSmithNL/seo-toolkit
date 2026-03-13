---
id: "FTR-CONFIG-001"
type: feature
title: "Site URL Registration & Crawl Config"
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

# Feature Design — Site URL Registration & Crawl Config (F-001)

> Slim feature design. See `../epic-design.md` for shared architecture (Prisma schema, module boundary, coding guardrails, cross-cutting concerns).

---

## Architecture Overview

F-001 is the root feature of E-001 — it creates the `SiteConfig` aggregate that all other features hang off. It is the entry point for the entire content engine pipeline.

```
src/modules/content-engine/config/
├── site-registration/
│   ├── site-registration.service.ts     ← orchestrates registration flow
│   ├── site-registration.repository.ts  ← SiteConfig + SiteLanguage persistence
│   ├── site-registration.schema.ts      ← Zod input/output schemas
│   ├── cms-detector.ts                  ← CMS auto-detection logic
│   ├── language-detector.ts             ← language auto-detection logic
│   ├── url-normaliser.ts                ← URL canonicalisation
│   └── __tests__/
│       ├── site-registration.service.test.ts
│       ├── cms-detector.test.ts
│       ├── language-detector.test.ts
│       └── url-normaliser.test.ts
```

---

## Component Design

```typescript
// === Value Objects ===

class NormalisedUrl {
  readonly value: string;

  static create(raw: string): Result<NormalisedUrl, ValidationError> {
    // add https://, strip trailing slash, resolve www/non-www
  }
}

interface Language {
  code: string;       // BCP-47: "en", "nl"
  name: string;       // "English", "Dutch"
  urlPattern?: string; // "/nl/", "/de/"
}

// === Service ===

class SiteRegistrationService {
  constructor(
    private repo: SiteRepository,
    private cmsDetector: CMSDetector,
    private languageDetector: LanguageDetector,
    private eventEmitter: EventEmitter,
  ) {}

  async registerSite(input: RegisterSiteInput): Promise<SiteConfig>;
  async getSite(id: string): Promise<SiteConfig | null>;
  async reCrawl(id: string): Promise<SiteConfig>;
}

// === Repository ===

interface SiteRepository {
  create(data: CreateSiteData): Promise<SiteConfig>;
  findById(id: string): Promise<SiteConfig | null>;
  findByUrl(tenantId: string, url: string): Promise<SiteConfig | null>;
  update(id: string, data: UpdateSiteData): Promise<SiteConfig>;
  delete(id: string): Promise<void>;
}
```

---

## DDD Tactical Patterns

| Pattern | Element | Notes |
|---------|---------|-------|
| **Aggregate root** | `SiteConfig` | Root for the entire E-001 epic — all other entities reference via `siteId` |
| **Value object** | `NormalisedUrl` | Immutable, validated on creation, encapsulates normalisation rules |
| **Value object** | `Language` | Code + name + optional URL pattern |
| **Domain event** | `site.registered` | `{ siteId, url, tenantId }` — triggers downstream features |
| **Domain event** | `site.crawled` | `{ siteId, cmsType, languages[], contentCount }` — triggers CMS adapter selection |
| **Repository** | `SiteRepository` | Prisma-backed, tenant-scoped queries |

---

## Key Algorithms

### CMS Detection

```
1. Fetch GET / (follow redirects, 10s timeout)
2. Check for WordPress:
   a. GET /wp-json/wp/v2/ — if 200 → "wordpress"
   b. Check HTML for wp-content or wp-includes paths → "wordpress"
3. Check for Shopify:
   a. Check HTML for cdn.shopify.com → "shopify"
   b. Check response headers for X-ShopId → "shopify"
4. Else → "unknown"
```

### Language Detection

```
1. Parse HTML for <link rel="alternate" hreflang="..."> tags
   → if found, extract all language codes + URL patterns
2. Check for Shopify locale URLs (/en/, /nl/, /de/ patterns)
   → if found, map to BCP-47 codes
3. Read <html lang="..."> attribute
   → use as primary language
4. Fallback → "en"
```

### URL Normalisation

```
1. If no protocol prefix → prepend "https://"
2. Parse with URL constructor (validates format)
3. Lowercase the hostname
4. Strip trailing slash from pathname
5. Resolve www: prefer non-www canonical (check both, use the one that resolves)
6. Strip default ports (443, 80)
7. Return normalised string
```

---

## API Surface

R1 CLI functions (direct call, no HTTP server):

| Function | Signature | Description |
|----------|-----------|-------------|
| `registerSite` | `(url: string) => Promise<SiteConfig>` | Normalise URL, crawl, detect CMS + languages, persist |
| `getSite` | `(id: string) => Promise<SiteConfig>` | Retrieve site config by ID |

R2 HTTP routes (from epic module manifest):

| Method | Path | Handler |
|--------|------|---------|
| `POST` | `/sites` | `createSite` |
| `GET` | `/sites/:id` | `getSite` |

---

## Integration Points

| External System | Protocol | Purpose | Timeout | Retry |
|----------------|----------|---------|---------|-------|
| Target site (root page) | HTTP GET | Fetch HTML for CMS + language detection | 10s | 1 retry after 3s |
| Target site (wp-json) | HTTP GET | WordPress API endpoint check | 5s | No retry |
| Target site (sitemap.xml) | HTTP GET | Content count estimation | 10s | No retry |

---

## Testing Strategy

| Category | What to Test | Approach |
|----------|-------------|----------|
| **Unit** | URL normaliser (edge cases: unicode, punycode, no protocol, trailing slashes) | Table-driven tests |
| **Unit** | CMS detector (WordPress HTML, Shopify HTML, unknown) | Mock HTTP responses |
| **Unit** | Language detector (hreflang, Shopify locales, html lang, fallback) | Mock HTML parsing |
| **Integration** | Full registration flow (normalise → crawl → detect → persist) | In-memory SQLite |
| **Edge case** | Duplicate URL registration (same tenant) | Expect unique constraint error |
| **Edge case** | Unreachable site (timeout, DNS failure) | Mock network errors |

---

## Feature-Specific Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Crawl at registration time (not deferred) | User gets immediate feedback on CMS type and languages |
| 2 | Prefer non-www canonical | Industry standard; reduces duplicate content issues |
| 3 | WordPress detection via wp-json first, then HTML fallback | API check is definitive; HTML check catches headless/customised installs |
| 4 | Store content count estimate from sitemap | Useful context for topic inference (F-004) without full crawl |
