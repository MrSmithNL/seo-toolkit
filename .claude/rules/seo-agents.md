---
paths:
  - "scripts/**/*"
  - "configs/**/*"
  - "docs/agents/**/*"
---
# SEO Agent Architecture Rules

## The 8 SEO Agents

| # | Agent | Purpose | Key Tools |
|---|-------|---------|-----------|
| 1 | **Audit** | Technical site crawl — broken links, meta tags, schema, Core Web Vitals, security headers, mobile, speed | DataForSEO, claude-seo, custom crawlers |
| 2 | **Keywords** | Keyword research — volumes, difficulty, competitor gaps, SERP analysis, long-tail discovery | DataForSEO, Google Search Console, Rube MCP |
| 3 | **Content Optimizer** | On-page SEO — alt tags, headings, internal links, readability, keyword density, meta descriptions | Custom scripts, claude-seo |
| 4 | **Rank Tracker** | Position monitoring — keyword rankings, traffic trends, SERP feature changes, competitor movements | SE Ranking, Google Search Console, DataForSEO |
| 5 | **Content Writer** | Article generation — SEO-optimized long-form based on keyword strategy + source material | Claude API, keyword data, content configs |
| 6 | **Link Builder** | Backlink strategy — guest post sites, directory listings, broken link opportunities | DataForSEO, Ahrefs/SEMrush via Rube |
| 7 | **AI Discovery** | AI engine optimization — llms.txt, structured data, schema markup, AI-friendly content | Custom scripts, schema validators |
| 8 | **Reporter** | Dashboards and reports — weekly/monthly SEO summaries, alerts, recommendations | All data sources, report templates |

## Client Config Format

Each website gets a JSON config in `configs/`:

```json
{
  "name": "Love Over Exile",
  "domain": "loveoverexile.com",
  "project_path": "../loveoverexile-website/",
  "primary_keywords": ["parental alienation", "alienated parent"],
  "competitors": ["pasg.info", "isnaf.org"],
  "google_search_console_property": "sc-domain:loveoverexile.com",
  "schedule": { "audit": "weekly", "rank_check": "daily", "content_review": "weekly", "report": "weekly" }
}
```

## Project Structure

```
seo-toolkit/
├── configs/          # Per-website configuration files
├── docs/agents/      # Detailed specification per agent
├── scripts/          # Python scripts organised by agent (audit/, keywords/, content/, links/, reporting/, ai-discovery/)
├── skills/           # Claude Code skills (installed to ~/.claude/skills/)
└── requirements.txt  # Python dependencies
```
