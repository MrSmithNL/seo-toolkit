# SEO Toolkit — PROD-002

An 8-agent AI SEO automation platform built by Smith AI Agency.

---

## What This Is

The SEO Toolkit is a Python-based platform that automates search engine optimisation through 8 specialised AI agents. Each agent handles a different aspect of SEO — from technical audits to content creation to rank tracking. The toolkit is designed to work across multiple websites: add a config file for a new client, and all 8 agents can work on that site.

**First client:** [Love Over Exile](https://loveoverexile.com) (loveoverexile.com)

---

## The 8 Agents

| # | Agent | What It Does |
|---|-------|-------------|
| 1 | **Audit** | Technical site crawl — broken links, meta tags, schema, Core Web Vitals, security headers, mobile, speed |
| 2 | **Keywords** | Keyword research — volumes, difficulty, competitor gaps, SERP analysis, long-tail discovery |
| 3 | **Content Optimizer** | On-page SEO — alt tags, headings, internal links, readability, keyword density, meta descriptions |
| 4 | **Rank Tracker** | Position monitoring — keyword rankings, traffic trends, SERP feature changes, competitor movements |
| 5 | **Content Writer** | Article generation — SEO-optimized long-form content based on keyword strategy and source material |
| 6 | **Link Builder** | Backlink strategy — find high-value link opportunities, draft outreach pitches, monitor backlink profile |
| 7 | **AI Discovery** | AI engine optimization — llms.txt, structured data, schema markup, AI-friendly content structure |
| 8 | **Reporter** | Dashboards and reports — weekly/monthly SEO performance summaries, alerts, recommendations |

---

## Architecture

```
                        SEO TOOLKIT
    ┌──────────────────────────────────────────────┐
    │                                              │
    │   Audit  Keywords  Content   Rank Tracker    │
    │   Agent  Agent     Optimizer Agent           │
    │                                              │
    │   Content  Link     AI        Reporter       │
    │   Writer   Builder  Discovery Agent          │
    │                                              │
    │   ──────── SHARED DATA LAYER ────────        │
    └──────────┬─────────────────────┬─────────────┘
               │                     │
        ┌──────┴──────┐       ┌──────┴──────┐
        │  DATA APIs  │       │  CLIENTS    │
        │ DataForSEO  │       │ Love Over   │
        │ Google SC   │       │ Exile       │
        │ SE Ranking  │       │ (+ future)  │
        │ Rube MCP    │       └─────────────┘
        └─────────────┘
```

**Multi-client by design.** Each website gets a JSON config file in `configs/`. Adding a new client means adding a new config — no code changes required.

---

## Project Status

| Area | Status |
|------|--------|
| Architecture | Done — 8 agents defined, data flow designed |
| Client configs | Done — Love Over Exile config created |
| Data APIs | Not connected — DataForSEO, SE Ranking, Google Search Console pending |
| Agents | Not built — all 8 agents are defined but code not yet written |
| CI/CD | Basic — GitHub Actions lint + test pipeline |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| HTTP | requests, httpx |
| HTML parsing | BeautifulSoup4, lxml |
| Data processing | pandas |
| Schema validation | jsonschema |
| Report generation | Jinja2 |
| SEO data | DataForSEO API |
| Rank tracking | SE Ranking API |
| Search analytics | Google Search Console |
| Formatting | black |
| Linting | ruff |
| Testing | pytest |

---

## Project Structure

```
seo-toolkit/
├── CLAUDE.md                      # AI coding rules + project instructions
├── README.md                      # This file
├── .gitignore
├── .github/workflows/ci.yml       # Linting + testing on every push
├── requirements.txt               # Python dependencies
├── configs/                       # Per-client configuration files
│   ├── example.config.json        # Template
│   └── loveoverexile.config.json  # First client
├── docs/
│   ├── architecture.md            # System diagram, components, connections
│   ├── todo.md                    # Task tracking + roadmap
│   ├── decisions-log.md           # Technical decisions with reasoning
│   ├── accounts-and-access.md     # All accounts, services, credentials
│   ├── security-risk-log.md       # Security risks + mitigations
│   ├── processes-and-flows.md     # How agents run, how to add clients
│   ├── business-case.md           # Revenue model, costs, market opportunity
│   ├── market-research.md         # SEO tool market overview
│   ├── competitor-analysis.md     # Competitor breakdown
│   ├── metrics.md                 # KPIs and success metrics
│   ├── coding-standards.md        # Python coding rules for this project
│   └── agents/                    # Detailed spec per agent
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
└── skills/                        # Claude Code skills
```

---

## Quick Start

```bash
# Clone the repo
git clone git@github.com:MrSmithNL/seo-toolkit.git
cd seo-toolkit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your API keys
cp .env.example .env
# Edit .env with your DataForSEO credentials, etc.

# Run tests
pytest
```

---

## Adding a New Client

1. Copy `configs/example.config.json` to `configs/yourclient.config.json`
2. Fill in the domain, keywords, competitors, and schedule
3. All 8 agents will automatically work with the new config

See `docs/processes-and-flows.md` for the full onboarding process.

---

## Documentation

| File | What It Covers |
|------|---------------|
| [Architecture](docs/architecture.md) | System diagram, all components and connections |
| [Todo](docs/todo.md) | Current tasks, roadmap, session log |
| [Decisions](docs/decisions-log.md) | Every technical decision with reasoning |
| [Accounts](docs/accounts-and-access.md) | All services, credentials, access |
| [Security](docs/security-risk-log.md) | Risks, mitigations, credential policies |
| [Processes](docs/processes-and-flows.md) | Agent execution flow, client onboarding |
| [Business Case](docs/business-case.md) | Market opportunity, revenue model, costs |
| [Market Research](docs/market-research.md) | SEO tool market overview |
| [Competitors](docs/competitor-analysis.md) | Detailed competitor breakdown |
| [Metrics](docs/metrics.md) | KPIs and success tracking |
| [Coding Standards](docs/coding-standards.md) | Python rules for this project |

---

## Part of Smith AI Agency

This project is PROD-002 in the [Smith AI Agency](https://github.com/MrSmithNL/smith-ai-agency) portfolio. It will be battle-tested on Love Over Exile first, then offered as a SaaS service to external clients.
