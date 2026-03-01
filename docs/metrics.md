# SEO Toolkit — Metrics & KPIs

Last updated: 2026-03-01

---

## Overview

Every metric tracked by the SEO Toolkit falls into two categories:

1. **Per-client SEO metrics** — How well is each client's website performing in search? Tracked by the 8 agents, reported by the Reporter Agent.
2. **Toolkit health metrics** — How well is the toolkit itself working? Agent reliability, data freshness, cost efficiency.

All metrics feed into the INFRA-003 agency dashboard (Google Looker Studio + Sheets) once it is operational.

---

## Per-Client SEO Metrics

These are the metrics that matter to each website using the toolkit. The Reporter Agent compiles these into weekly and monthly reports.

### Organic Traffic

| Metric | Source | Frequency | Why It Matters |
|--------|--------|-----------|---------------|
| Organic sessions | Google Search Console / GA4 | Weekly | The bottom line — are more people finding the site through search? |
| Organic clicks | Google Search Console | Weekly | How many search appearances result in visits |
| Click-through rate (CTR) | Google Search Console | Weekly | Are titles and descriptions compelling enough to click? |
| Impressions | Google Search Console | Weekly | How often does the site appear in search results? |

### Keyword Rankings

| Metric | Source | Frequency | Why It Matters |
|--------|--------|-----------|---------------|
| Keywords in top 3 | SE Ranking / DataForSEO | Daily | Top 3 positions capture 60%+ of clicks |
| Keywords in top 10 | SE Ranking / DataForSEO | Daily | First page of Google — where traffic happens |
| Keywords in top 20 | SE Ranking / DataForSEO | Daily | Striking distance — close to first page |
| Average position (tracked keywords) | SE Ranking | Daily | Overall trend direction |
| Keywords gained vs. lost | SE Ranking | Weekly | Net movement — are we improving or declining? |
| SERP features won | DataForSEO | Weekly | Featured snippets, knowledge panels, AI overviews |

### Technical Health

| Metric | Source | Frequency | Why It Matters |
|--------|--------|-----------|---------------|
| Audit score (0-100) | Audit Agent | Weekly | Overall technical health of the site |
| Critical issues count | Audit Agent | Weekly | Broken pages, server errors, security issues |
| Warnings count | Audit Agent | Weekly | Non-critical issues that should be fixed |
| Core Web Vitals (LCP, CLS, INP) | Google PageSpeed API | Weekly | Google's performance metrics — affect rankings |
| Indexation rate | Google Search Console | Weekly | What percentage of pages are indexed by Google? |
| Crawl errors | Google Search Console | Weekly | Pages Google cannot access |

### Content Performance

| Metric | Source | Frequency | Why It Matters |
|--------|--------|-----------|---------------|
| Pages with no organic traffic | GSC + Audit Agent | Monthly | Content that is not working — needs optimisation or removal |
| Content score (readability + SEO) | Content Optimizer | Weekly | How well-optimised is each page? |
| Content pieces published | GitHub commits | Monthly | Are we maintaining publishing cadence? |
| Thin content pages (<300 words) | Audit Agent | Monthly | Pages that Google may consider low-value |
| Missing meta descriptions | Audit Agent | Weekly | Lost opportunity for CTR |
| Missing alt tags on images | Audit Agent | Weekly | Accessibility + image search opportunity |

### Backlink Profile

| Metric | Source | Frequency | Why It Matters |
|--------|--------|-----------|---------------|
| Total referring domains | DataForSEO | Monthly | Domain diversity matters more than total links |
| New referring domains (this month) | DataForSEO | Monthly | Growth rate of backlink profile |
| Lost referring domains (this month) | DataForSEO | Monthly | Are we losing valuable links? |
| Domain authority / domain rating | Moz/Ahrefs via Rube | Monthly | Overall site authority score |
| Toxic backlinks detected | DataForSEO | Monthly | Links that could trigger penalties |
| Outreach pitches sent | Link Builder Agent | Weekly | Activity metric for link building |
| Links earned from outreach | Link Builder Agent | Monthly | Conversion rate of link building efforts |

### AI Discovery

| Metric | Source | Frequency | Why It Matters |
|--------|--------|-----------|---------------|
| llms.txt present and valid | AI Discovery Agent | Monthly | Required for AI engine discoverability |
| Schema markup coverage | AI Discovery Agent | Monthly | Percentage of pages with valid structured data |
| AI engine citations | Manual / AI Discovery | Monthly | How often AI search engines cite our content |
| Structured data errors | AI Discovery Agent | Monthly | Schema markup issues that prevent rich results |

---

## Toolkit Health Metrics

These measure how well the SEO Toolkit itself is functioning.

| Metric | What It Measures | Target | Source |
|--------|-----------------|--------|--------|
| Agent uptime | Percentage of scheduled runs that completed successfully | 95%+ | Agent logs |
| Data freshness | How old is the most recent data for each metric? | <24 hours for daily, <7 days for weekly | Agent timestamps |
| API cost per client per month | Total DataForSEO + SE Ranking spend per client | <$50/month | API billing |
| Report delivery rate | Percentage of scheduled reports actually generated and delivered | 100% | Reporter Agent logs |
| Agent execution time | How long does each agent take to run? | <10 minutes per agent | Agent logs |
| API error rate | Percentage of API calls that fail | <5% | Agent error logs |

---

## Love Over Exile Targets (First Client)

Specific targets for the first client, to be measured after agents are operational:

| Metric | Current (estimate) | 3-month target | 6-month target |
|--------|-------------------|---------------|----------------|
| Organic sessions / month | ~0 (new site) | 500 | 2,000 |
| Keywords in top 10 | 0 | 5 | 20 |
| Keywords in top 20 | Unknown | 15 | 50 |
| Audit score | Unknown (not yet audited) | 70+ | 85+ |
| Content pages published | ~10 | 20 | 40 |
| Referring domains | ~0 | 10 | 30 |
| llms.txt in place | No | Yes | Yes |
| Schema coverage | Unknown | 80%+ | 95%+ |

---

## Reporting Schedule

| Report | Frequency | Contents | Audience |
|--------|-----------|----------|----------|
| Daily rank check | Daily | Keyword position changes, alerts for significant drops | Malcolm (email/notification) |
| Weekly SEO summary | Weekly | All per-client metrics, trends, recommendations | Malcolm (Markdown report) |
| Monthly SEO report | Monthly | Full analysis, content performance, backlink changes, strategy review | Malcolm (HTML report) |
| Quarterly business review | Quarterly | Cross-client metrics, toolkit health, cost analysis, strategy adjustments | Malcolm (strategic document) |

---

## Dashboard Integration

All metrics will flow into the agency-level BI dashboard (INFRA-003):

1. **Agents produce data** → stored as JSON in `reports/<client>/<agent>/<date>/`
2. **Reporter Agent compiles** → weekly/monthly summary JSON
3. **GitHub Action syncs** → pushes summary data to Google Sheets (INFRA-003)
4. **Looker Studio reads** → displays cross-project dashboard with SEO metrics alongside other agency metrics

---

## Change Log

| Date | Change |
|------|--------|
| 2026-03-01 | Metrics document created. Per-client SEO metrics, toolkit health metrics, Love Over Exile targets, reporting schedule, and dashboard integration documented. |
