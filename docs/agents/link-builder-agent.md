# Link Builder Agent

## Purpose

An "earned link engine" — NOT a posting bot. This agent helps clients systematically earn links through PR, editorial pitching, relationship building, and linkable content assets. AI makes this dramatically faster while staying within Google's guidelines.

## Critical Design Principle — Earned Links Only

Google has been explicit that large-scale guest-posting campaigns done primarily to build links violate their spam policies — especially when scaled, templated, or anchor-text optimised.

**This agent does NOT:**
- Auto-publish articles to external sites at scale
- Run mass templated outreach campaigns
- Manipulate anchor text distribution
- Build link networks or PBN-style placements
- Create "footprints" that Google can detect

**This agent DOES:**
- Discover high-quality editorial link opportunities
- Generate genuinely valuable content assets that earn links naturally
- Draft personalised, high-quality pitches (with human approval)
- Monitor backlink health and flag toxic links
- Track journalist queries and PR opportunities

---

## The Four Pillars

### 1. AI-Powered Prospect Discovery

Build a smart database of sites where links can be *earned* — not just a DA/DR list.

**What AI scores for each prospect:**
- **Topical fit** — semantic similarity between prospect site and client
- **Editorial likelihood** — active posts, contributor guidelines, outbound link patterns, author bios
- **Link type prediction** — resource page, mention, review, roundup, interview, data citation, podcast, local org, scholarship, supplier, community org
- **Contact graph** — editor/writer identity, likely email patterns, social profiles

**Opportunity types (ranked by value):**

| Type | Effort | Value | How |
|------|--------|-------|-----|
| Digital PR / journalist queries | Medium | Very High | Match HARO/Connectively queries, build expert responses fast |
| Expert roundups / interviews | Medium | High | Contribute expert quotes, podcast appearances |
| Linkable asset citations | High upfront | Very High | Create data/tools that sites want to reference |
| Resource page inclusion | Low | Medium | Find relevant resource pages, request addition |
| Broken link replacement | Low | Medium | Find 404s on relevant sites, offer your content |
| Unlinked mention conversion | Low | Medium | Find brand mentions, ask for link |
| Directory listings | Low | Low-Medium | Submit to relevant, high-authority directories |

### 2. Link Asset Generator (where AI is underused)

Most outreach fails because people pitch nothing of value. This agent generates assets editors actually want to link to:

- **Original data** — mini-studies from public datasets, surveys, statistics compilations
- **Interactive tools** — calculators, checklists, quizzes, self-assessments
- **Statistics pages** — "[Topic] Statistics 2026" — highly linkable, data-dense
- **Expert quotes / source pages** — quotable, citable expert material
- **Glossaries** — with real diagrams and visuals
- **Resource hubs** — curated collections with genuine editorial value

**AI assists with:**
- Topic selection (gap analysis — what's missing in the niche?)
- Data summarisation and packaging
- Visual and narrative formatting
- Turning one dataset into multiple pitch angles

**Example for Love Over Exile:**
- "Parental Alienation Statistics 2026" (country data, age cohorts, court outcomes)
- "Signs of Parental Alienation Checklist" (interactive self-assessment)
- "Expert Quotes on Parental Alienation" (citable source page)
- "Parental Alienation Resources by Country" (comprehensive directory)

Then the agent finds: family law blogs, psychology sites, parenting publications, universities, journalists covering custody/family topics — and pitches the data/tool as a citation, not as a guest post.

### 3. Quality Outreach (assistive, not blasting)

Automation is fine if it's assistive and personalised — not mass spam.

**Features:**
- **AI drafts 3–5 pitch angles per prospect** — based on what they've published recently
- **References one relevant page on the prospect site** — shows you actually read them
- **Follow-up scheduling with human-in-the-loop** — Malcolm approves every email
- **No-follow/sponsored detection** — flags and handles correctly
- **Pitch quality scoring** — predicts reply probability, flags spam-pattern language
- **Uniqueness thresholds** — prevents mass-template footprints

### 4. Attribution & Risk Control

Protect clients from toxic placements and Google penalties.

- **PBN detection** — flags likely private blog networks
- **Link seller detection** — identifies sites with unusual outbound link ratios
- **Spun content detection** — flags sites publishing AI-generated filler
- **Anchor text monitoring** — warns if anchor text distribution looks manipulated
- **rel attribute guidance** — ensures correct use of nofollow, sponsored, ugc
- **Publisher quality scoring** — ongoing health checks on linking domains

---

## Link Quality Assessment

| Signal | What It Measures | Weight |
|--------|-----------------|--------|
| Domain Authority / Rating | Overall domain strength | Medium |
| Topical relevance | How closely the site matches the client's niche | High |
| Real traffic | Whether the site actually gets visitors (not just DA) | High |
| Editorial signals | Active publishing, real authors, genuine content | High |
| Spam score | Link farms, PBNs, low-quality patterns | Critical (filter out) |
| Link type | Editorial mention > guest post > directory > forum > comment | Medium |

---

## Backlink Monitoring

- **New links detected** — alerts when new backlinks appear
- **Lost links** — alerts when existing backlinks disappear
- **Toxic links** — identifies spammy links that should be disavowed
- **Anchor text distribution** — monitors for over-optimised patterns
- **Competitor link velocity** — how fast competitors are earning links

---

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| DataForSEO Backlinks API | Backlink profile, competitor links, new/lost links | Primary |
| Ahrefs via Rube | Content explorer, backlink analysis, broken link finder | Primary |
| SEMrush via Rube | Backlink gap analysis, toxic link detection | Secondary |
| HARO / Connectively / Source of Sources | Journalist query matching | Primary |
| Custom web research | Prospect discovery, editorial analysis | Supplementary |

---

## Output

- `data/{domain}/backlinks/` — backlink profile snapshots
- `data/{domain}/opportunities/` — scored link building opportunities with AI fit scores
- `data/{domain}/assets/` — linkable asset outlines and drafts
- `data/{domain}/outreach/` — outreach CRM (tracking log, pitches, responses)
- `reports/{domain}/link-report-{date}.md` — monthly backlink report

---

## Build Order (MVP → Full)

**MVP 1: Prospecting + Fit Scoring**
- Niche/site discovery
- Topical alignment scoring
- Contact discovery
- Basic outreach CRM

**MVP 2: Asset-First Pitching**
- Generate linkable asset outlines
- Pitch angles per prospect
- Human approval workflow

**MVP 3: Risk & Compliance**
- Link scheme / footprint risk scoring
- rel attribute guidance
- Publisher quality scoring

---

## Schedule

- **Monthly** — full backlink profile review + new opportunity research
- **Weekly** — check for new/lost backlinks, scan for journalist queries
- **On demand** — targeted research for specific campaigns or assets

---

## Non-Negotiable Rules

1. **Never buy links** — Google penalises paid link schemes
2. **Never auto-publish** — no automated posting to external sites
3. **Quality over quantity** — one earned editorial link > 100 low-quality placements
4. **Malcolm approves all outreach** — no emails sent without human review
5. **Track everything** — every opportunity, pitch, response, and outcome gets logged
6. **Proper attribution** — use correct rel attributes (sponsored, ugc, nofollow)
7. **No footprints** — no templated mass campaigns, no anchor text manipulation

---

## Scripts

- `scripts/links/discover_prospects.py` — AI-powered prospect discovery + fit scoring
- `scripts/links/competitor_links.py` — analyse competitor backlink profiles
- `scripts/links/monitor_backlinks.py` — track new/lost/toxic backlinks
- `scripts/links/generate_assets.py` — create linkable asset outlines
- `scripts/links/generate_pitches.py` — draft personalised outreach (3–5 angles per prospect)
- `scripts/links/risk_scorer.py` — PBN/spam/footprint detection
- `scripts/links/outreach_crm.py` — log and manage outreach campaigns
- `scripts/links/journalist_matcher.py` — match HARO/Connectively queries to client expertise
