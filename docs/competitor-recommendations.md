# Competitor Recommendations — PROD-001: SEO Toolkit

> **Research produces information. This document turns it into valued, prioritized action.**
> Updated whenever `competitor-analysis.md` is updated. Reviewed quarterly.
> Every recommendation is scored on business value — not just "is this a good idea"
> but "how much does this actually improve the product?"
>
> **After review, approved recommendations are automatically added as tasks in `docs/todo.md`.**
>
> **Last updated:** 2026-03-01
> **Source:** `docs/competitor-analysis.md`

---

## Value Scoring

Every recommendation is scored on 4 dimensions (0-3 each, total 0-12):

| Dimension | Question | Score |
|-----------|----------|-------|
| **Strategic Value (Strat)** | Does this strengthen our market position, pricing, or differentiation? | 0 = none, 1 = minor, 2 = significant, 3 = major |
| **Revenue Impact (Rev)** | Does this directly enable selling, attract customers, or reduce churn? | 0-3 |
| **Effort (Eff)** | How much work to implement? | 0 = major (weeks+), 1 = significant (days), 2 = moderate (hours), 3 = quick win |
| **Competitive Urgency (Urg)** | How quickly will competitors close this gap? | 0 = no pressure, 1 = within a year, 2 = within months, 3 = imminent |

**Priority rules:**
- Total 10-12 = Critical — implement this week
- Total 7-9 = High — implement this month
- Total 4-6 = Medium — implement this quarter
- Total 0-3 = Low — backlog

---

## Strategy & Business Model

| # | Recommendation | Source | Strat | Rev | Eff | Urg | Total | Status |
|---|---------------|--------|:-----:|:---:|:---:|:---:|:-----:|--------|
| S-001 | Start as internal tool, productise after proven on Love Over Exile | All competitors charge $50-999/mo | 3 | 2 | 3 | 1 | 9 | Proposed |
| S-002 | Price at $99-199/mo for entry tier — below Ahrefs/SEMrush, above SE Ranking | Ahrefs $99, SEMrush $119, SE Ranking $31 | 2 | 3 | 3 | 1 | 9 | Proposed |
| S-003 | Position as "autonomous AI SEO" — agents that work on their own, not just dashboards | No competitor has autonomous agents | 3 | 3 | 3 | 2 | 11 | Proposed |
| S-004 | Offer per-website pricing (not per-user like competitors) | Ahrefs/SEMrush charge per user seat | 2 | 2 | 3 | 1 | 8 | Proposed |
| S-005 | Target solo operators and small agencies first — underserved by enterprise tools | Ahrefs/SEMrush overkill for solopreneurs | 2 | 2 | 3 | 1 | 8 | Proposed |

---

## Marketing & Sales

| # | Recommendation | Source | Strat | Rev | Eff | Urg | Total | Status |
|---|---------------|--------|:-----:|:---:|:---:|:---:|:-----:|--------|
| M-001 | Lead with "set it and forget it" messaging — agents work autonomously | Unique vs all competitors | 3 | 2 | 3 | 2 | 10 | Proposed |
| M-002 | Create comparison pages: "SEO Toolkit vs Ahrefs", "vs SEMrush" | Standard SaaS SEO strategy | 2 | 2 | 2 | 1 | 7 | Proposed |
| M-003 | Publish monthly SEO reports from Love Over Exile as case studies | Proves our own tool works | 2 | 3 | 2 | 1 | 8 | Proposed |
| M-004 | Offer free audit report as lead magnet (like Screaming Frog's free crawl) | Screaming Frog free tier drives upgrades | 1 | 3 | 2 | 1 | 7 | Proposed |
| M-005 | Target content creators and authors first (via Book Rocket vertical) | Underserved segment by all major tools | 2 | 2 | 2 | 0 | 6 | Proposed |

---

## Technology & Features

| # | Recommendation | Source | Strat | Rev | Eff | Urg | Total | Status |
|---|---------------|--------|:-----:|:---:|:---:|:---:|:-----:|--------|
| T-001 | Build AI Discovery Agent — no competitor tracks AI search engine visibility | Gap in entire market | 3 | 3 | 0 | 3 | 9 | Proposed |
| T-002 | Automated content optimization suggestions (like Surfer SEO but AI-driven) | Surfer SEO $59-239/mo, content-focused | 3 | 3 | 0 | 2 | 8 | Proposed |
| T-003 | Earned link discovery — find unlinked mentions and broken links automatically | Ahrefs has this but manual, not automated | 2 | 2 | 1 | 2 | 7 | Proposed |
| T-004 | Multi-site dashboard — manage all client sites from one view | SEMrush/Ahrefs have this, we need it too | 1 | 2 | 1 | 1 | 5 | Proposed |
| T-005 | White-label reports for agencies | SEMrush offers this at $230+/mo tier | 1 | 2 | 1 | 0 | 4 | Proposed |
| T-006 | Integration with Google Search Console (automated, not just data display) | All competitors have this | 2 | 2 | 2 | 3 | 9 | Proposed |
| T-007 | Schema markup generator from content analysis | Screaming Frog detects issues but doesn't fix them | 1 | 1 | 1 | 1 | 4 | Proposed |

---

## Services & Support

| # | Recommendation | Source | Strat | Rev | Eff | Urg | Total | Status |
|---|---------------|--------|:-----:|:---:|:---:|:---:|:-----:|--------|
| SV-001 | Self-serve setup — no onboarding calls needed (unlike enterprise tools) | Salesforce/HubSpot require onboarding | 2 | 2 | 2 | 1 | 7 | Proposed |
| SV-002 | In-product tutorials and contextual help for non-technical users | Moz does this well with their learning centre | 1 | 1 | 1 | 1 | 4 | Proposed |
| SV-003 | Community forum for users to share strategies (like Ahrefs community) | Ahrefs has active community driving retention | 1 | 1 | 1 | 0 | 3 | Proposed |
| SV-004 | Monthly "what changed in SEO" digest sent to users | Builds trust, reduces churn | 0 | 1 | 2 | 0 | 3 | Proposed |

---

## Priority Summary (Top 10 by Value Score)

| Rank | # | Recommendation | Total | Category | Status |
|:----:|---|---------------|:-----:|----------|--------|
| 1 | S-003 | Position as "autonomous AI SEO" | 11 | Strategy | Proposed |
| 2 | M-001 | "Set it and forget it" messaging | 10 | Marketing | Proposed |
| 3 | S-001 | Start as internal tool, prove on Love Over Exile | 9 | Strategy | Proposed |
| 4 | S-002 | Price at $99-199/mo entry tier | 9 | Strategy | Proposed |
| 5 | T-001 | AI Discovery Agent | 9 | Technology | Proposed |
| 6 | T-006 | Google Search Console integration | 9 | Technology | Proposed |
| 7 | S-004 | Per-website pricing model | 8 | Strategy | Proposed |
| 8 | S-005 | Target solo operators + small agencies | 8 | Strategy | Proposed |
| 9 | M-003 | Love Over Exile case studies | 8 | Marketing | Proposed |
| 10 | T-002 | Automated content optimization | 8 | Technology | Proposed |

---

## Auto-Task-Creation Rule

> When a recommendation is reviewed and approved (status moves to "Approved"):
> 1. A task is automatically created in `docs/todo.md`
> 2. Task format: `[CR-xxx] Implement: [recommendation summary]`
> 3. Task priority matches the recommendation priority
> 4. When new recommendations are added, a review task is also auto-created:
>    `Review new competitor recommendations (X new items)`
> This is autonomous — Claude creates these tasks without permission.

---

## Change Log

| Date | What Changed |
|------|-------------|
| 2026-03-01 | v2.0 — Added 4-dimension value scoring (Strategic Value, Revenue Impact, Effort, Competitive Urgency) on 0-12 scale. All 20 recommendations scored. Priority Summary table added. Auto-task-creation rule added. |
| 2026-03-01 | v1.0 — Initial recommendations from competitor analysis. 20 recommendations across 4 categories. |
