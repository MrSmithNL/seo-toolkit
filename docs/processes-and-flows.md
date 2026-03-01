# SEO Toolkit — Processes & Flows

Last updated: 2026-03-01

---

## Agent Execution Flow

This is how every agent runs, regardless of which one it is. The flow is the same whether triggered manually or on a schedule.

```
┌──────────────┐
│  1. TRIGGER   │   Manual run, scheduled cron, or overnight runner
└──────┬───────┘
       │
┌──────┴───────┐
│ 2. LOAD      │   Read client config from configs/<client>.config.json
│    CONFIG    │   Get domain, keywords, competitors, targets, schedule
└──────┬───────┘
       │
┌──────┴───────┐
│ 3. AGENT     │   Agent receives task based on its speciality
│    RECEIVES  │   (e.g., "audit loveoverexile.com" or "research keywords")
│    TASK      │
└──────┬───────┘
       │
┌──────┴───────┐
│ 4. CALL APIs │   Agent calls external data sources:
│              │   - DataForSEO (keywords, SERPs, backlinks)
│              │   - Google Search Console (real search data)
│              │   - SE Ranking (rank positions, site audit)
│              │   - Rube MCP (SEMrush, Ahrefs, other tools)
└──────┬───────┘
       │
┌──────┴───────┐
│ 5. PROCESS   │   Agent analyses the raw data:
│    DATA      │   - Filters, scores, and ranks results
│              │   - Compares against targets from config
│              │   - Identifies issues, opportunities, changes
└──────┬───────┘
       │
┌──────┴───────┐
│ 6. PRODUCE   │   Agent generates its output:
│    REPORT    │   - Structured data (JSON for other agents)
│              │   - Human-readable report (HTML or Markdown)
│              │   - Alerts for critical issues
└──────┬───────┘
       │
┌──────┴───────┐
│ 7. STORE     │   Output saved to the data layer:
│    RESULTS   │   - reports/<client>/<agent>/<date>/
│              │   - cache/ for reusable API responses
│              │   - Shared data available to other agents
└──────────────┘
```

---

## Agent Interaction Map

Agents share data through the shared data layer. Here is how they connect:

```
Keywords Agent ──→ Content Writer (keyword targets for articles)
                ──→ Content Optimizer (keywords to optimise for)
                ──→ Rank Tracker (keywords to track positions for)

Audit Agent    ──→ Content Optimizer (technical issues to fix)
               ──→ AI Discovery (schema/structured data issues)
               ──→ Reporter (audit findings for reports)

Rank Tracker   ──→ Reporter (ranking trends and alerts)
               ──→ Keywords Agent (declining keywords to investigate)

Link Builder   ──→ Reporter (backlink profile changes)
               ──→ Content Writer (linkable asset ideas)

All Agents     ──→ Reporter (every agent feeds data into reports)
```

---

## How to Add a New Client

Adding a new website to the toolkit is a config-only operation. No code changes needed.

### Step-by-step

1. **Copy the template config:**
   ```bash
   cp configs/example.config.json configs/newclient.config.json
   ```

2. **Fill in the config fields:**
   - `name` — Client display name (e.g., "Acme Corp")
   - `domain` — The website domain (e.g., "acmecorp.com")
   - `primary_keywords` — 3-5 main keywords the site targets
   - `content_pillars` — Topic clusters with keyword lists
   - `competitors` — 3-5 competitor domains
   - `schedule` — How often each agent should run (daily/weekly/monthly)
   - `targets` — Minimum article length, image sizes, backlink goals

3. **Set up data sources for the new client:**
   - Add the domain to Google Search Console (if not already verified)
   - Create a project in SE Ranking for the domain
   - Update the config with `se_ranking_project_id` and `google_search_console_property`

4. **Run a first audit:**
   ```bash
   python scripts/audit/run_audit.py --config configs/newclient.config.json
   ```

5. **Review the audit report** and set priorities based on findings.

---

## How to Run an Audit Cycle

A full audit cycle runs all relevant agents in sequence for a client.

### Manual run

```bash
# Run individual agents
python scripts/audit/run_audit.py --config configs/loveoverexile.config.json
python scripts/keywords/run_keywords.py --config configs/loveoverexile.config.json
python scripts/content/run_optimizer.py --config configs/loveoverexile.config.json

# Generate combined report
python scripts/reporting/run_report.py --config configs/loveoverexile.config.json
```

### Scheduled run (future)

When the overnight runner is set up (see master strategy), agents will run on the schedule defined in each client's config:

| Agent | Typical Schedule | Why |
|-------|-----------------|-----|
| Rank Tracker | Daily | Keyword positions change daily |
| Audit | Weekly | Technical issues don't change hourly |
| Content Optimizer | Weekly | On-page content changes with publishes |
| Keywords | Weekly | New opportunities emerge weekly |
| Link Builder | Weekly | New prospects and backlink changes |
| Content Writer | On demand | Triggered when keyword strategy identifies gaps |
| AI Discovery | Monthly | AI search engine behaviour changes slowly |
| Reporter | Weekly | Weekly summary of all agent findings |

---

## How to Run a Single Agent

Every agent follows the same command pattern:

```bash
python scripts/<agent-dir>/run_<agent>.py --config configs/<client>.config.json [--options]
```

Common options (when implemented):
- `--dry-run` — Show what would be done without making API calls
- `--verbose` — Show detailed progress and API responses
- `--output-format json|html|md` — Choose report format
- `--since YYYY-MM-DD` — Only process data since a specific date

---

## Data Flow: From API to Report

This shows how a single piece of data (a keyword ranking) flows through the system:

```
1. SE Ranking API returns: "parental alienation" → position 47 on Google

2. Rank Tracker Agent stores this in:
   reports/loveoverexile/rank-tracker/2026-03-01/rankings.json

3. Keywords Agent reads this and notes:
   "parental alienation" is a high-volume keyword where we rank poorly → opportunity

4. Content Writer Agent picks this up:
   Generates an article brief targeting "parental alienation" with supporting keywords

5. Reporter Agent includes in weekly report:
   "Keyword 'parental alienation' ranks #47 — recommend targeted content"
```

---

## Error Handling

When an agent encounters a problem:

| Error Type | What Happens | Resolution |
|-----------|-------------|-----------|
| API key missing | Agent logs error, skips API calls, reports what it could not do | Add key to `.env` |
| API rate limited | Agent waits and retries (exponential backoff) | Automatic |
| API returned error | Agent logs the error with full response, continues with other tasks | Check API docs, fix request |
| Client config missing field | Agent logs warning, uses sensible defaults where possible | Update config file |
| No data returned | Agent produces report noting "no data available" rather than empty report | Check API account balance, verify domain is correct |

---

## Change Log

| Date | Change |
|------|--------|
| 2026-03-01 | Processes document created. Agent execution flow, interaction map, client onboarding, audit cycle, error handling documented. |
