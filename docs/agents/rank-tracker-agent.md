# Rank Tracker Agent

## Purpose

Monitor keyword rankings, traffic trends, and SERP changes over time. Detects drops early, spots opportunities, and tracks the impact of SEO changes.

## What It Tracks

### Keyword Positions
- **Daily rank checks** — position for each target keyword on Google (desktop + mobile)
- **Position changes** — gains, losses, new rankings, lost rankings
- **SERP feature presence** — featured snippets, People Also Ask, image pack, video results
- **Local vs national** — position differences by geography (if relevant)

### Traffic Metrics (via Google Search Console)
- **Clicks** — actual clicks from search results to the site
- **Impressions** — how often pages appear in search results
- **CTR** — click-through rate per page and per keyword
- **Average position** — Google's own position data

### Competitor Tracking
- **Head-to-head positions** — how you rank vs competitors for the same keywords
- **New competitor pages** — detect when competitors publish content targeting your keywords
- **Competitor gains/losses** — monitor competitor ranking changes

### Alerts
- **Significant drops** — alert when a key page drops 5+ positions
- **Deindexing** — alert if pages disappear from Google entirely
- **New opportunities** — alert when you start ranking for new valuable keywords
- **Algorithm updates** — flag ranking changes that correlate with known Google updates

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| SE Ranking | Daily rank tracking, competitor monitoring | Primary |
| Google Search Console | Clicks, impressions, CTR, average position | Primary |
| DataForSEO SERP API | On-demand position checks, SERP features | Secondary |

## Output

- `data/{domain}/rankings/` — daily position snapshots (JSON)
- `reports/{domain}/rank-report-{date}.md` — weekly ranking summary
- Alert messages (via email or Slack when connected)

## Schedule

- **Daily** — position check for top 50 target keywords
- **Weekly** — full ranking report with trends and recommendations
- **Real-time alerts** — triggered when significant changes detected

## Scripts

- `scripts/keywords/track_rankings.py` — daily position checker
- `scripts/keywords/ranking_report.py` — weekly report generator
- `scripts/keywords/alert_check.py` — change detection and alerting
