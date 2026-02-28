# Content Optimizer Agent

## Purpose

Analyse every page on a website and optimise on-page SEO elements. Checks alt tags, headings, internal links, readability, keyword usage, and meta data — then either reports issues or applies fixes directly.

## What It Does

### Page-Level Checks
- **Title tag** — correct length (50–60 chars), contains target keyword, compelling for clicks
- **Meta description** — correct length (150–160 chars), contains keyword, has call to action
- **URL slug** — short, descriptive, keyword-inclusive, no stop words
- **H1 tag** — one per page, contains primary keyword, matches search intent
- **Heading hierarchy** — proper H1 → H2 → H3 nesting, keywords in subheadings

### Content Quality
- **Keyword density** — target keyword appears naturally (1–2%), no stuffing
- **Related terms** — LSI/related keywords present for topical depth
- **Content length** — meets minimum for the content type and search intent
- **Readability** — Flesch-Kincaid grade level, sentence/paragraph length
- **Freshness signals** — last modified date, publication date in schema

### Image SEO
- **Alt tags** — descriptive (80–125 chars), keyword where natural, not stuffed
- **File names** — SEO-friendly (hyphens, descriptive, 3–6 words)
- **File size** — compressed to target (hero < 150KB, cards < 90KB)
- **Format** — WebP or AVIF with fallbacks
- **Lazy loading** — applied to below-fold images

### Internal Linking
- **Link coverage** — every page reachable within 3 clicks from homepage
- **Anchor text** — descriptive, varied, keyword-relevant
- **Orphan pages** — pages with no internal links pointing to them
- **Link distribution** — important pages get more internal links

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| Site files (Astro/HTML) | Direct access to page source | Primary |
| Keywords database | Target keywords per page | Primary |
| DataForSEO On-Page API | Automated page analysis | Secondary |
| claude-seo | E-E-A-T scoring, content analysis | Secondary |

## Output

- **Report mode** — `reports/{domain}/content-audit-{date}.md` listing all issues
- **Fix mode** — directly edits site files to apply fixes (with confirmation)
- Page-by-page score card with before/after comparison

## Schedule

- **After any content change** — automatically checks new/modified pages
- **Weekly** — full site content review
- **On demand** — targeted check on specific pages

## Scripts

- `scripts/content/optimize_page.py` — single page analyser and fixer
- `scripts/content/site_review.py` — full site content audit
- `scripts/content/internal_links.py` — internal link analysis and recommendations
- `scripts/content/readability.py` — readability scoring
