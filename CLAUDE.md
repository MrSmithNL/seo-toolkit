# Project Instructions — SEO Toolkit

These instructions apply to this project in every session.

---

## What This Project Is

A **reusable, multi-website SEO automation toolkit** built as a set of Claude Code agents and Python scripts. It can be pointed at any website to audit, optimize, track, and improve search engine performance — both for traditional search engines (Google, Bing) and AI discovery engines (ChatGPT, Perplexity, Gemini).

The toolkit is designed to work across all of Malcolm's websites — Love Over Exile is the first client, but the architecture supports any number of sites.

---

## Skills Check — Always First

Before taking any action (installing tools, running scripts, setting up integrations, publishing content, building workflows), check `~/.claude/skills/` for a relevant skill.

```
ls ~/.claude/skills/ | grep -i [relevant keyword]
```

If a skill exists: read it, understand what it needs, and use it.
If no skill exists: proceed with the direct approach.

---

## Architecture Maintenance — Always Automatic

After any change that adds, modifies, or removes a service, tool, account, connection, or credential:
1. Update `docs/architecture.md` — diagram, components, connections, accounts, change log
2. Update `docs/todo.md` — mark completed items, add new ones
3. Commit and push both files

This happens automatically without being asked.

---

## Autonomous Permissions

Malcolm has granted full autonomous permission for the following — no confirmation needed:

- **Update any `.md` documentation file** — in this project or in `~/.claude/docs/`
- **Create new documentation files** in the `docs/` folder
- **Commit and push** documentation-only changes to GitHub
- **Update project memory files** in `~/.claude/projects/.../memory/`
- **Run read-only API calls** — keyword lookups, SERP checks, site audits, crawl data
- **Run Python scripts** in the `scripts/` directory

Always confirm before:
- **Publishing content** to any live website
- **Submitting backlinks** or guest post requests
- **Making changes** to any client website's files or DNS
- **Creating accounts** on external platforms
- **Spending money** (API calls with cost above $1)

---

## The 8 SEO Agents

| # | Agent | Purpose | Key Tools |
|---|-------|---------|-----------|
| 1 | **Audit** | Technical site crawl — broken links, meta tags, schema, Core Web Vitals, security headers, mobile, speed | DataForSEO, claude-seo, custom crawlers |
| 2 | **Keywords** | Keyword research — volumes, difficulty, competitor gaps, SERP analysis, long-tail discovery | DataForSEO, Google Search Console, Rube MCP |
| 3 | **Content Optimizer** | On-page SEO — alt tags, headings, internal links, readability, keyword density, meta descriptions | Custom scripts, claude-seo |
| 4 | **Rank Tracker** | Position monitoring — keyword rankings, traffic trends, SERP feature changes, competitor movements | SE Ranking, Google Search Console, DataForSEO |
| 5 | **Content Writer** | Article generation — SEO-optimized long-form content based on keyword strategy + source material | Claude API, keyword data, content configs |
| 6 | **Link Builder** | Backlink strategy — find high-value guest post sites, directory listings, broken link opportunities, monitor backlink profile | DataForSEO, Ahrefs/SEMrush via Rube, custom research |
| 7 | **AI Discovery** | AI engine optimization — llms.txt, structured data, meta sitemaps, schema markup, AI-friendly content structure | Custom scripts, schema validators |
| 8 | **Reporter** | Dashboards and reports — weekly/monthly SEO performance summaries, alerts, recommendations | All data sources, report templates |

---

## Project Structure

```
seo-toolkit/
├── CLAUDE.md                      # This file
├── .gitignore
├── configs/                       # Per-website configuration files
│   ├── example.config.json        # Template
│   └── loveoverexile.config.json  # First client
├── docs/
│   ├── architecture.md            # Infrastructure diagram + all connections
│   ├── todo.md                    # Task tracking + roadmap
│   ├── decisions-log.md           # Technical decisions with reasoning
│   └── agents/                    # Detailed specification per agent
│       ├── audit-agent.md
│       ├── keywords-agent.md
│       ├── content-optimizer-agent.md
│       ├── rank-tracker-agent.md
│       ├── content-writer-agent.md
│       ├── link-builder-agent.md
│       ├── ai-discovery-agent.md
│       └── reporter-agent.md
├── scripts/                       # Python scripts organised by agent
│   ├── audit/
│   ├── keywords/
│   ├── content/
│   ├── links/
│   ├── reporting/
│   └── ai-discovery/
├── skills/                        # Claude Code skills (installed to ~/.claude/skills/)
└── requirements.txt               # Python dependencies
```

---

## Client Config Format

Each website gets a JSON config in `configs/`:

```json
{
  "name": "Love Over Exile",
  "domain": "loveoverexile.com",
  "project_path": "../loveoverexile-website/",
  "site_path": "../loveoverexile-website/site/",
  "primary_keywords": ["parental alienation", "alienated parent", "love over exile"],
  "content_source": "../loveoverexile-website/content/",
  "publish_to": "../loveoverexile-website/site/src/pages/articles/",
  "competitors": ["pasg.info", "isnaf.org", "amybaker.com"],
  "google_search_console_property": "sc-domain:loveoverexile.com",
  "se_ranking_project_id": null,
  "schedule": {
    "audit": "weekly",
    "rank_check": "daily",
    "content_review": "weekly",
    "report": "weekly"
  }
}
```

---

## Key Docs

| File | What It Covers |
|------|---------------|
| `docs/todo.md` | All open and completed tasks — check at session start |
| `docs/architecture.md` | Full infrastructure diagram — tools, APIs, connections |
| `docs/decisions-log.md` | Every technical decision with reasoning |
| `docs/agents/*.md` | Detailed spec for each of the 8 agents |

---

## Credential Access

All API keys and credentials go in `.env` (gitignored) or Bitwarden. Never in git. Never in plain text files.

Current credentials needed:
- `DATAFORSEO_LOGIN` + `DATAFORSEO_PASSWORD` — keyword/SERP data
- `GOOGLE_AI_API_KEY` — Gemini for content analysis (already in Love Over Exile .env)
- Google Search Console — via Rube MCP
- SE Ranking — via MCP or API key
- SEMrush / Ahrefs — via Rube MCP

---

## Communication Style

- Short, direct explanations — Malcolm is non-technical
- No jargon without explanation
- Always state what was done, why, and how to undo it
- When something is a temporary solution, say so and log it
