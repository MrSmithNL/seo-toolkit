# Reporter Agent

## Purpose

Pull data from all other agents and produce readable SEO performance reports. Tracks progress over time, highlights wins, flags problems, and recommends next actions.

## What It Produces

### Weekly Report
- **Rankings snapshot** — position changes for top keywords
- **Traffic summary** — clicks, impressions, CTR from Google Search Console
- **New/lost backlinks** — backlink profile changes
- **Content published** — articles added this week
- **Issues detected** — new technical issues found by Audit Agent
- **Top 3 recommended actions** — what to do next, prioritised by impact

### Monthly Report
- Everything in weekly report, plus:
- **Trend analysis** — month-over-month traffic and ranking trends
- **Keyword progress** — movement toward target positions
- **Competitor comparison** — how you're doing vs competitors
- **Content performance** — which articles are driving the most traffic
- **Backlink growth** — link profile growth rate
- **ROI summary** — effort spent vs results (positions gained, traffic increase)

### Quarterly Strategy Review
- **Goal assessment** — are we on track for SEO goals?
- **Strategy effectiveness** — which agents/strategies are working best?
- **Budget review** — API costs, tool subscriptions, content costs
- **Next quarter plan** — updated priorities and targets

### Alert Reports (real-time)
- **Ranking drop** — immediate notification when key pages drop 5+ positions
- **Site down** — if the site is unreachable
- **Deindexing** — pages removed from Google's index
- **Toxic backlinks** — spam links detected pointing to the site

## Report Format

Reports are generated as Markdown files that are:
- Human-readable (written for Malcolm, not for SEO experts)
- Stored in `reports/{domain}/` for historical tracking
- Optionally emailed (when email integration is connected)
- Optionally posted to Slack (when Slack is connected)

## Data Sources

This agent doesn't collect its own data — it aggregates from all other agents:

| Agent | Data Used |
|-------|-----------|
| Audit Agent | Technical health score, issues count, fixes applied |
| Keywords Agent | Keyword database, search volumes, clusters |
| Content Optimizer | Page-level scores, issues fixed |
| Rank Tracker | Position data, traffic metrics |
| Content Writer | Articles published, topic coverage |
| Link Builder | Backlink profile, new opportunities, outreach results |
| AI Discovery | AI readiness score, schema coverage |

## Schedule

- **Weekly** — every Monday morning, covering the previous 7 days
- **Monthly** — 1st of each month, covering the previous 30 days
- **Quarterly** — 1st of Jan/Apr/Jul/Oct
- **Alerts** — real-time when triggered

## Scripts

- `scripts/reporting/weekly_report.py` — weekly report generator
- `scripts/reporting/monthly_report.py` — monthly report generator
- `scripts/reporting/quarterly_review.py` — quarterly strategy review
- `scripts/reporting/alerts.py` — real-time alert system
- `scripts/reporting/email_report.py` — email delivery (when connected)
