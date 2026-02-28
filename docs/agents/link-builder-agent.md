# Link Builder Agent

## Purpose

Research, identify, and manage backlink opportunities. Finds high-value websites where guest posts, mentions, or directory listings can be placed. Monitors the backlink profile and competitor link strategies.

## What It Does

### Opportunity Research
- **Guest post targets** — finds blogs and publications that accept guest posts in the niche
- **Resource page links** — finds "resources" and "useful links" pages in the niche that could list the site
- **Broken link building** — finds broken links on relevant sites → suggest your content as replacement
- **Competitor backlink analysis** — see where competitors get their links → target the same sources
- **Unlinked mentions** — finds web pages that mention your brand/topic without linking to you
- **Directory listings** — relevant, high-authority directories in the niche

### Link Quality Assessment
- **Domain Authority / Domain Rating** — scores each potential linking domain
- **Relevance score** — how topically relevant the linking site is
- **Traffic estimate** — whether the linking site actually gets traffic
- **Spam score** — filters out link farms, PBNs, and low-quality sites
- **Link type** — editorial, guest post, directory, forum, comment (prioritise editorial)

### Outreach Preparation
- **Contact finding** — identifies editor/webmaster email for target sites
- **Pitch templates** — generates personalised outreach emails for each opportunity type
- **Tracking** — logs all outreach attempts and responses
- **Follow-up scheduling** — reminders for follow-up emails

### Backlink Monitoring
- **New links detected** — alerts when new backlinks appear
- **Lost links** — alerts when existing backlinks disappear
- **Toxic links** — identifies spammy links that should be disavowed
- **Anchor text distribution** — monitors for over-optimised anchor text patterns

## Link Building Strategies by Priority

| Strategy | Effort | Value | How |
|----------|--------|-------|-----|
| Guest posting on parental alienation / family law blogs | Medium | High | Write valuable articles, include author bio link |
| Resource page inclusion | Low | Medium | Find relevant resource pages, request addition |
| Broken link replacement | Low | Medium | Find 404s on relevant sites, offer your content |
| Directory listings | Low | Low-Medium | Submit to relevant directories (psychology, family, books) |
| Expert roundups / interviews | Medium | High | Contribute expert quotes to journalist requests (HARO/Connectively) |
| Unlinked mention conversion | Low | Medium | Find brand mentions, ask for link |

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| DataForSEO Backlinks API | Backlink profile, competitor links, new/lost links | Primary |
| Ahrefs via Rube | Content explorer, backlink analysis, broken link finder | Primary |
| SEMrush via Rube | Backlink gap analysis, toxic link detection | Secondary |
| Custom web research | Guest post opportunity discovery | Supplementary |

## Output

- `data/{domain}/backlinks/` — backlink profile snapshots
- `data/{domain}/opportunities/` — scored link building opportunities
- `reports/{domain}/link-report-{date}.md` — monthly backlink report
- `data/{domain}/outreach/` — outreach tracking log

## Schedule

- **Monthly** — full backlink profile review + new opportunity research
- **Weekly** — check for new/lost backlinks
- **On demand** — targeted research for specific link building campaigns

## Important Notes

- **Never buy links** — Google penalises paid link schemes
- **Quality over quantity** — one link from a DA 50+ relevant site > 100 low-quality links
- **Malcolm approves all outreach** — no emails sent without review
- **Track everything** — every opportunity, pitch, and response gets logged

## Scripts

- `scripts/links/find_opportunities.py` — discover link building opportunities
- `scripts/links/competitor_links.py` — analyse competitor backlink profiles
- `scripts/links/monitor_backlinks.py` — track new/lost/toxic backlinks
- `scripts/links/generate_pitches.py` — create outreach email templates
- `scripts/links/outreach_tracker.py` — log and manage outreach campaigns
