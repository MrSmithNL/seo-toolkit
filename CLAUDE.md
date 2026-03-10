# Project Instructions — SEO Toolkit

These instructions apply to this project in every session.

---

## What This Project Is

A **reusable, multi-website SEO automation toolkit** — 8 Claude Code agents + Python scripts. Can be pointed at any website to audit, optimize, track, and improve SEO performance for both traditional search engines and AI discovery engines.

---

## Related Projects

- **Agency standards:** `~/Claude Code/Projects/smith-ai-agency/docs/capabilities/`
- **Platform (PROD-004):** `~/Claude Code/Projects/saas-platform/` — integrates toolkit as a service
- **CLIENT-001 Love Over Exile:** `~/Claude Code/Projects/loveoverexile-website/` — first client
- **CLIENT-002 Hairgenetix:** `~/Claude Code/Projects/hairgenetix/` — second client

---

## Agency-Wide Delivery Framework

This project operates under the agency's autonomous delivery framework. All standards, processes, and department manager oversight apply here:

- **Quality Manager** — Code quality, testing, documentation standards (`smith-ai-agency/docs/capabilities/quality-manager.md`)
- **DevOps Manager** — CI/CD, deployment, infrastructure reliability (`smith-ai-agency/docs/capabilities/devops-manager.md`)
- **Technical Architect** — Architecture decisions, fitness functions, dependency governance (`smith-ai-agency/docs/capabilities/technical-architect.md`)
- **Delivery Manager** — Sprint planning, objective tracking, blocker resolution (`smith-ai-agency/docs/capabilities/delivery-manager.md`)
- **Requirements Engineering** — Spec-driven development, 3-gate process (`smith-ai-agency/docs/capabilities/requirements-engineering.md`)
- **Sprint Management** — 2-week cadence, velocity tracking (`smith-ai-agency/objectives/sprints/`)

---

## Autonomous Permissions

No confirmation needed:
- Update any `.md` file, create new docs, commit and push docs-only changes
- Run read-only API calls (keyword lookups, SERP checks, audits, crawl data)
- Run Python scripts in `scripts/`

Always confirm before: publishing content to live sites, submitting backlinks, client site changes, creating external accounts, spending >$1 on API calls.

---

## Architecture Maintenance — Always Automatic

After any change to services, tools, accounts, or connections:
1. Update `docs/architecture.md` and `docs/todo.md`
2. Commit and push

---

## Key Docs

| File | What It Covers |
|------|---------------|
| `docs/todo.md` | All open and completed tasks |
| `docs/architecture.md` | Infrastructure diagram + connections |
| `docs/decisions-log.md` | Technical decisions with reasoning |
| `docs/agents/*.md` | Detailed spec for each of the 8 agents |

---

## Credential Access

All API keys in `.env` (gitignored) or Bitwarden. Never in git.

Needed: `DATAFORSEO_LOGIN` + `DATAFORSEO_PASSWORD`, `GOOGLE_AI_API_KEY`, Google Search Console (via Rube MCP), SE Ranking, SEMrush/Ahrefs (via Rube MCP).
