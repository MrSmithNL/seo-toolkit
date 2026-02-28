# AI Discovery Agent

## Purpose

Optimise websites for discovery by AI engines — ChatGPT, Perplexity, Google Gemini, Copilot, and other AI assistants that answer user questions by referencing web content. This is a new and fast-evolving SEO frontier.

## Why This Matters

When someone asks ChatGPT "how do I cope with parental alienation?", AI engines pull from web sources to construct their answers. Being one of those cited sources drives traffic and authority — similar to ranking #1 on Google but for the AI era.

## What It Does

### llms.txt Implementation
- **Create `/llms.txt`** — a machine-readable file (like robots.txt but for AI) that tells LLMs what the site is about, what content is available, and how to cite it
- **Create `/llms-full.txt`** — extended version with full content summaries for deeper AI understanding
- **Maintain and update** — keep llms.txt current as site content changes

### Structured Data for AI
- **JSON-LD schema** — comprehensive schema markup on every page type:
  - `Organization` — site-wide identity
  - `Person` — author profiles with credentials
  - `Book` — book metadata
  - `Article` — for blog posts with author, date, topics
  - `FAQPage` — for FAQ content (highly cited by AI)
  - `HowTo` — for step-by-step guides
  - `BreadcrumbList` — navigation structure
- **Open Graph tags** — complete OG metadata for social + AI parsing
- **Dublin Core metadata** — academic/research-style metadata for scholarly AI systems

### Sitemap Optimisation
- **XML sitemap** — complete, valid, auto-updating with lastmod dates
- **HTML sitemap** — human-readable site map page
- **Content categorisation** — clear topic taxonomy that AI can understand
- **Priority signals** — indicate which content is most authoritative

### Content Structure for AI
- **Clear, factual claims** — AI engines prefer content that makes definitive, citable statements
- **Question-answer format** — structure content to match how people ask AI questions
- **Citation-friendly summaries** — opening paragraphs that work as AI-generated answer snippets
- **Author authority signals** — bio, credentials, expertise markers that AI uses for E-E-A-T
- **Data and statistics** — AI loves citing specific numbers and research findings

### AI Engine Monitoring
- **Track AI citations** — monitor when AI engines cite your content (where tools exist)
- **Test AI responses** — periodically ask AI engines your target questions to see if your content appears
- **Competitor AI presence** — check how competitors appear in AI answers

## Implementation Checklist

| Item | Standard SEO? | AI-Specific? | Status |
|------|:------------:|:------------:|--------|
| XML sitemap | ✅ | ✅ | Check per site |
| robots.txt (allow AI crawlers) | ✅ | ✅ | Check per site |
| llms.txt | — | ✅ | Create per site |
| llms-full.txt | — | ✅ | Create per site |
| JSON-LD schema on all pages | ✅ | ✅ | Check per site |
| FAQ schema on Q&A content | ✅ | ✅ | Check per site |
| Author schema with credentials | ✅ | ✅ | Check per site |
| Open Graph tags | ✅ | ✅ | Check per site |
| Clear topic taxonomy | ✅ | ✅ | Check per site |
| Citation-friendly content | — | ✅ | Content Writer handles |

## Data Sources

| Source | What It Provides | Priority |
|--------|-----------------|----------|
| Site files | Direct access to templates and content | Primary |
| Schema.org docs | Schema markup reference | Reference |
| llms-txt.org spec | llms.txt format specification | Reference |
| AI engine testing | Manual testing of AI responses | Supplementary |

## Output

- `/llms.txt` and `/llms-full.txt` files in site public directory
- Updated JSON-LD schema blocks in page templates
- `reports/{domain}/ai-discovery-{date}.md` — AI readiness report
- Recommendations for content structure improvements

## Schedule

- **After any content change** — update llms.txt and schema
- **Monthly** — full AI discovery audit
- **Quarterly** — test AI engine responses for target queries

## Scripts

- `scripts/ai-discovery/generate_llms_txt.py` — creates and updates llms.txt files
- `scripts/ai-discovery/validate_schema.py` — checks JSON-LD schema on all pages
- `scripts/ai-discovery/ai_presence_check.py` — tests AI engine responses
- `scripts/ai-discovery/sitemap_audit.py` — validates sitemap completeness
