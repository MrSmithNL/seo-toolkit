# Content Writer Agent

## Purpose

Generate SEO-optimised long-form articles based on keyword strategy, source material, and competitor analysis. Articles are written to rank for specific keywords while providing genuine value to readers.

## What It Does

### Article Pipeline
1. **Topic selection** — picks the highest-priority keyword cluster that doesn't have content yet
2. **SERP analysis** — analyses the top 10 results to understand what Google rewards for this topic
3. **Outline generation** — creates a detailed outline with target headings, word count, and angle
4. **Source integration** — weaves in material from the book/content source (not just generic AI content)
5. **Writing** — produces the full article with proper heading structure, internal links, and natural keyword usage
6. **SEO check** — runs Content Optimizer checks before publishing
7. **Publishing** — commits the article to the website repo (with confirmation)

### Content Types
- **Pillar articles** — comprehensive guides (2000–3000 words) targeting primary keywords
- **Supporting articles** — focused pieces (1000–1500 words) targeting long-tail keywords
- **FAQ pages** — structured Q&A targeting question keywords (with FAQ schema)
- **Resource roundups** — curated lists targeting "best/top" keywords
- **Personal stories** — experience-based content for E-E-A-T (from book material)

### Quality Controls
- **Not generic AI content** — every article is grounded in the book or original research
- **E-E-A-T signals** — author bio, citations, real experience, expert perspective
- **Uniqueness check** — verifies content doesn't duplicate existing pages
- **Readability** — targets the audience reading level (not academic, not dumbed down)
- **Malcolm review** — always flagged for human review before publishing

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| Keyword database | Target keywords, search intent, volume | Primary |
| Content source files | Book chapters, research notes, original material | Primary |
| SERP analysis | What top-ranking content looks like | Primary |
| Competitor content | Gaps and angles to differentiate | Secondary |

## Output

- Astro-compatible `.astro` or `.md` article files
- Front matter with SEO metadata (title, description, keywords, schema)
- Placed in the client website's articles directory
- Article brief document for Malcolm's review

## Schedule

- **Bi-weekly** — 2 articles per month minimum
- **On demand** — when a specific keyword opportunity is identified
- **Always requires Malcolm's approval** before publishing

## Scripts

- `scripts/content/research_topic.py` — SERP analysis and outline generation
- `scripts/content/write_article.py` — article generation from outline + sources
- `scripts/content/seo_check.py` — pre-publish SEO validation
- `scripts/content/publish.py` — commit article to website repo
