# Keywords Agent

## Purpose

Research and manage keyword strategy for a website. Discovers high-value keywords, analyses search intent, identifies competitor gaps, and maintains a living keyword database that drives all other agents.

## What It Does

### Keyword Research
- **Seed expansion** — takes primary keywords, finds related terms, long-tail variations, questions
- **Volume & difficulty** — real monthly search volumes, keyword difficulty scores, CPC data
- **Search intent classification** — informational, navigational, transactional, commercial
- **SERP feature analysis** — which keywords trigger featured snippets, People Also Ask, knowledge panels
- **Seasonal trends** — identifies keywords with seasonal patterns

### Competitor Analysis
- **Keyword gap analysis** — keywords competitors rank for that you don't
- **Content gap analysis** — topics competitors cover that you haven't
- **Ranking comparison** — side-by-side position comparison for target keywords
- **Backlink keywords** — what anchor text competitors are getting

### Strategy Management
- **Keyword clusters** — groups related keywords into topic clusters
- **Priority scoring** — ranks keywords by opportunity (volume × achievability ÷ difficulty)
- **Content mapping** — assigns target keywords to existing or planned pages
- **Cannibalisation detection** — flags when multiple pages target the same keyword

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| DataForSEO Keywords API | Volumes, difficulty, CPC, SERP features | Primary |
| DataForSEO SERP API | Real-time SERP results for any keyword | Primary |
| Google Search Console | Actual click/impression data for current keywords | Primary |
| SEMrush via Rube | Competitor keyword data, keyword magic tool | Secondary |
| Ahrefs via Rube | Content explorer, keyword difficulty | Secondary |

## Output

- `data/{domain}/keywords.json` — master keyword database
- `data/{domain}/keyword-strategy.md` — human-readable strategy document
- `data/{domain}/content-map.json` — keyword-to-page assignments
- `reports/{domain}/keyword-report-{date}.md` — periodic research report

## Schedule

- **On demand** — new research when strategy needs updating
- **Monthly** — refresh volumes and difficulty scores
- **Quarterly** — full competitor gap analysis

## Scripts

- `scripts/keywords/research.py` — keyword discovery and expansion
- `scripts/keywords/competitor_gap.py` — competitor keyword gap analysis
- `scripts/keywords/cluster.py` — keyword clustering and intent classification
- `scripts/keywords/strategy.py` — strategy document generator
