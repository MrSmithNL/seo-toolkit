# Audit Agent

## Purpose

Crawl a website and produce a comprehensive technical SEO health report. Identifies issues that hurt search rankings and provides actionable fix recommendations.

## What It Checks

### Technical Health
- **Crawlability** — robots.txt, XML sitemap, canonical tags, redirect chains, 404s
- **Page speed** — Core Web Vitals (LCP, FID, CLS), Time to First Byte, total page weight
- **Mobile-friendliness** — viewport meta, responsive layout, tap target sizes
- **Security** — HTTPS, mixed content, security headers (HSTS, CSP, X-Frame-Options)
- **Indexability** — noindex tags, orphan pages, crawl depth, internal link structure

### On-Page SEO
- **Title tags** — length, uniqueness, keyword presence
- **Meta descriptions** — length, uniqueness, persuasiveness
- **Heading structure** — H1 presence/uniqueness, heading hierarchy
- **Image SEO** — alt tags, file names, file sizes, lazy loading, WebP/AVIF format
- **Schema markup** — JSON-LD validation, coverage (Organization, Article, FAQ, etc.)

### Content Quality
- **Thin content** — pages under 300 words
- **Duplicate content** — internal duplicates, near-duplicates
- **Broken links** — internal and external 404s
- **Readability** — Flesch reading score, sentence complexity

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| DataForSEO On-Page API | Full site crawl + issues | Primary |
| claude-seo | E-E-A-T analysis, schema validation | Secondary |
| Custom Python crawler | Gap-fill checks (security headers, specific schema) | Supplementary |
| Google PageSpeed Insights API | Core Web Vitals (free) | Supplementary |

## Output

A structured report saved to `reports/{domain}/audit-{date}.md` with:
1. **Score** — overall health score (0–100)
2. **Critical issues** — must fix immediately (broken pages, security, indexing blocks)
3. **Warnings** — should fix soon (slow pages, missing meta, heading issues)
4. **Opportunities** — nice to have (schema additions, image optimisation, internal links)
5. **Page-by-page breakdown** — every page with its issues

## Schedule

- **On demand** — run any time via Claude Code
- **Weekly automated** — scheduled via Rube recipe or cron
- **Post-deploy** — triggered after website changes are pushed

## Scripts

- `scripts/audit/run_audit.py` — main audit orchestrator
- `scripts/audit/crawl_site.py` — custom crawler for gap-fill checks
- `scripts/audit/generate_report.py` — report formatter
