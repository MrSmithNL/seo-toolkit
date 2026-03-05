# Schema Audit Agent

## Purpose

Audit, validate, score, and generate JSON-LD structured data markup for any website. Schema.org structured data is the machine-readable language that AI systems, search engines, and knowledge graphs rely on to understand, trust, and cite web content. Pages with comprehensive schema markup get a **36% advantage** in AI-generated summaries and citations.

In plain English: this agent checks whether your website is "speaking the right language" to machines, fixes what's wrong, and generates the correct markup so AI systems can read, understand, and recommend your content.

## Why This Matters

- Schema markup gives a **36% citation advantage** in AI-generated answers
- **96% of AI Overview citations** come from sources with strong E-E-A-T signals — schema is how you prove those signals to machines
- Google, ChatGPT, Perplexity, and Claude all use structured data to populate knowledge graph entries
- Duplicate or invalid schema **actively hurts** your visibility — it signals untrustworthiness
- AI systems extract Product prices, FAQ answers, HowTo steps, and AggregateRatings directly from schema
- Without schema, AI must guess what your content means — with schema, you tell it explicitly

---

## What It Audits

### Phase 1: Discovery — Find All Schema

| Check | What It Does |
|-------|-------------|
| **JSON-LD block extraction** | Parse all `<script type="application/ld+json">` blocks from page HTML |
| **Duplicate detection** | Flag when the same @type appears more than once (e.g., two Organization blocks) |
| **Source identification** | Identify where each schema comes from: custom snippet, CMS auto-generated, theme built-in, app injection |
| **Cross-page consistency** | Verify Organization and WebSite schemas are identical across all pages |
| **@id linking** | Check that schemas reference each other via @id (e.g., Product.manufacturer references Organization's @id) |

### Phase 2: Validation — Check Correctness

| Check | What It Does |
|-------|-------------|
| **JSON syntax** | Valid JSON? No trailing commas, unescaped quotes, or malformed arrays? |
| **Schema.org compliance** | Do @types and properties exist in the Schema.org vocabulary? |
| **Required properties** | Does each @type have its required and recommended properties? |
| **Value formats** | Prices as decimals (49.95 not 49,95), dates as ISO 8601, URLs as full paths |
| **Empty/null values** | Flag empty strings, null values, and arrays of empty strings (common CMS bug) |
| **URL validity** | Do all URL properties point to real, accessible pages? |
| **Image references** | Do image URLs resolve? Are dimensions specified for ImageObject? |
| **Rich Results eligibility** | Does the schema meet Google's Rich Results Test requirements? |

### Phase 3: Completeness — Score Coverage

| Schema Type | Required For | Key Properties to Check |
|-------------|-------------|------------------------|
| **Organization** | Every site | name, url, logo (as ImageObject), description, sameAs (non-empty), contactPoint, founder, foundingDate, @id |
| **BreadcrumbList** | Every page | itemListElement with position, name, item (URL) |
| **Product** | E-commerce | name, description, image, sku, gtin, brand, offers.price (decimal), offers.priceCurrency, offers.availability, aggregateRating |
| **FAQPage** | FAQ content | mainEntity with Question/Answer pairs, minimum 3 Q&As |
| **Article** | Blog/news | headline, author (Person with credentials), datePublished, dateModified, image, publisher |
| **MedicalScholarlyArticle** | Health/science | All Article properties + citation (ScholarlyArticle[]), about (MedicalCondition), reviewedBy, keywords |
| **HowTo** | Step-by-step guides | name, step[] with HowToStep (name, text, image), supply[], tool[], totalTime |
| **Person** | Author/expert pages | name, jobTitle, affiliation, sameAs, knowsAbout, credentials |
| **AggregateRating** | Products/services | ratingValue, reviewCount, bestRating, worstRating |
| **ItemList** | Collection/category | itemListElement[], numberOfItems, name |
| **WebPage / MedicalWebPage** | Generic/health pages | name, url, description, isPartOf, dateModified, specialty (medical) |
| **Review** | Testimonial pages | author, reviewRating, datePublished, reviewBody |
| **LocalBusiness** | Local businesses | All Organization + address, geo, openingHours, telephone |
| **SoftwareApplication** | SaaS products | applicationCategory, operatingSystem, offers |

### Phase 4: Content Alignment — Schema vs Visible Content

| Check | What It Does |
|-------|-------------|
| **Price match** | Product schema price matches the price visible on the page |
| **Title match** | Schema headline/name matches visible H1 or page title |
| **Image match** | Schema image is actually visible on the page |
| **Availability match** | Schema availability matches actual stock status |
| **Rating match** | Schema aggregateRating matches visible review data |
| **Author match** | Schema author matches visible byline |
| **FAQ match** | Schema FAQ questions match visible FAQ content |

---

## Schema Scoring Model

Each page gets a schema score on a **0-100 scale**:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| **Presence** | 25% | Are the right schema types present for this page type? |
| **Completeness** | 25% | Are all required and recommended properties populated? |
| **Correctness** | 25% | Are values properly formatted and valid? |
| **Alignment** | 15% | Does schema match visible content? |
| **Cross-linking** | 10% | Do schemas reference each other via @id? |

### Site-Wide Schema Score

The overall site score is the weighted average of all audited pages, with higher weight on key pages:

| Page Type | Weight |
|-----------|--------|
| Homepage | 2x |
| Product pages | 2x |
| FAQ page | 1.5x |
| Blog articles | 1x |
| Other pages | 0.5x |

---

## Platform-Specific Knowledge

### Shopify

| Source | Schema Generated | Known Issues |
|--------|-----------------|-------------|
| `{{ content_for_header }}` | Organization | Uses theme social settings — empty strings become `"sameAs": ["","","",""]`. Uses theme logo (often wrong image). Cannot be removed. |
| `{{ product \| structured_data }}` | Product | Basic product data. Often duplicates custom Product schema. Can be removed from template. |
| Custom snippets (e.g., `seo-schema.liquid`) | Any type | Full control. Must be rendered via `{% render 'seo-schema' %}` in theme.liquid. |
| Apps (Judge.me, Loox, etc.) | Review, AggregateRating | May duplicate or conflict with custom schema. |

**Shopify-specific fixes:**
- Remove `{{ product | structured_data }}` from `main-product.liquid` to prevent duplicate Product schema
- Populate theme social settings OR use conditional sameAs in custom schema to avoid empty strings
- Use `{{ variant.price | divided_by: 100.0 }}` for correct decimal price (Shopify stores prices in cents)
- Use `{{ variant.barcode }}` for GTIN
- Custom Organization must use `@id` to establish canonical version over Shopify's auto-generated one

### WordPress

| Source | Schema Generated | Known Issues |
|--------|-----------------|-------------|
| Yoast SEO | Organization, WebSite, BreadcrumbList, Article, WebPage | Generally well-structured. May conflict with other plugins. |
| Rank Math | Similar to Yoast | Different @id patterns. Cannot run alongside Yoast. |
| WooCommerce | Product | Basic product data. Needs enrichment for AI visibility. |
| Theme built-in | Varies | Quality varies wildly. Often outdated schema versions. |

### Static Sites / Custom CMS

- No auto-generated schema — everything must be built from scratch
- Advantage: no duplicate conflicts
- Disadvantage: requires manual maintenance

---

## Schema Generation

The agent can generate schema markup from page content analysis:

### Input
- URL or page content
- Page type (product, article, FAQ, how-to, etc.)
- Business information (name, logo, social links)

### Output
- Complete JSON-LD blocks ready to paste into HTML
- Platform-specific implementation instructions (where to put it in Shopify/WordPress)
- Validation report confirming schema passes Rich Results Test

### Generation Rules

1. **One canonical schema per type per page** — never generate duplicates
2. **@id on every entity** — enable cross-referencing between schemas
3. **Conditional properties** — only include properties with actual values (no empty strings)
4. **Proper value formats** — prices as decimals, dates as ISO 8601, URLs as absolute paths
5. **Medical content gets medical types** — MedicalScholarlyArticle, MedicalWebPage, MedicalCondition
6. **AggregateRating on products** — always include if review data exists
7. **Citation arrays on research content** — link to PubMed, DOI, or scholarly sources
8. **FAQPage on product pages** — top 5 product-specific questions as schema (invisible to readers, visible to AI)

---

## Audit Report Structure

```
# Schema Audit — {domain}
## Date: {date}

## Executive Summary
- Overall schema score: XX/100
- Pages audited: N
- Schema types found: [list]
- Critical issues: N
- Warnings: N

## Site-Wide Issues
- Duplicate schemas across pages
- Missing global schemas (Organization, WebSite)
- Cross-linking gaps

## Per-Page Results
### {page-url}
- Schema types found: [Organization, Product, ...]
- Score: XX/100
- Issues:
  - [Critical] Duplicate Product schema from two sources
  - [Warning] Price format uses comma instead of decimal
  - [Info] Missing optional property: gtin

## Schema Coverage Matrix
| Page | Org | Breadcrumb | Product | FAQ | Article | HowTo | Medical | Rating |
|------|-----|------------|---------|-----|---------|-------|---------|--------|
| /    | OK  | OK         | -       | -   | -       | -     | -       | -      |
| /products/x | OK | OK   | ERROR   | -   | -       | -     | -       | OK     |

## Recommended Fixes
### Critical (fix immediately)
### Warnings (fix this week)
### Enhancements (nice to have)

## Generated Schema (if requested)
[Complete JSON-LD blocks for each page]
```

---

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| Site crawl (WebFetch / curl) | HTML content with JSON-LD blocks | Primary |
| Shopify Admin API | Theme files, settings, product data | Primary (Shopify sites) |
| WordPress REST API | Page content, plugin settings | Primary (WordPress sites) |
| Schema.org vocabulary | Valid types and properties reference | Reference |
| Google Rich Results Test | Validation and eligibility check | Validation |
| invoke_llm | Content analysis for schema-content alignment | Supplementary |

---

## Integration with Other Agents

| Agent | Integration |
|-------|------------|
| **AI Discovery Agent** | Category B (Schema & Structured Data, 20% weight) uses this agent's scoring methodology |
| **Technical Audit Agent** | Includes basic schema presence check — this agent provides the deep dive |
| **Content Optimizer Agent** | Recommends schema updates when content changes (freshness signals) |

---

## Schedule

- **After any schema change** — immediate validation on affected pages
- **Monthly** — full site schema audit as part of AI Discovery Audit
- **After CMS/theme updates** — check for new duplicate sources or broken schema
- **On demand** — schema generation for new pages/page types

---

## Implementation Notes

### How to Run

The schema audit can run as:
1. **Part of the AI Discovery Audit** — Category B scoring
2. **Standalone audit** — full schema-only deep dive
3. **Generation mode** — produce schema for new pages

### Rube Recipe

**Status:** To be implemented (recipe not yet created)

The recipe would:
1. Accept a domain URL and optional list of specific pages
2. Crawl key pages (homepage, product, FAQ, blog, etc.)
3. Extract and parse all JSON-LD blocks
4. Validate against Schema.org specs
5. Check for duplicates and conflicts
6. Score each page and overall site
7. Generate fix recommendations
8. Optionally generate corrected schema blocks

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-05 | Initial agent spec. Comprehensive audit framework based on Hairgenetix schema audit learnings. Covers discovery, validation, completeness, alignment. Platform-specific knowledge for Shopify and WordPress. Generation capability. |
