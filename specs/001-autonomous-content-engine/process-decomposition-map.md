# Process Decomposition Map — Autonomous Content Engine

> **Standalone PDM** extracted from `theme.md` per RE v4.15 requirement.
> This is the single source of truth for process decomposition. Updates here MUST be reflected back into `theme.md`.

---

## Full Process Decomposition

| Process ID | L1 Domain | L2 Process Area | L3 Sub-Process | Automation | Class | Evidence | Coverage | Target Epic |
|:----------:|-----------|-----------------|----------------|:----------:|:-----:|:--------:|:--------:|:-----------:|
| 1.0 | configure | Site & Brand Setup | — | — | — | — | — | E-001 |
| 1.1 | configure | Site & Brand Setup | Site URL registration & crawl config | AUTO | TS | 10/13 competitors | GAP | E-001 |
| 1.2 | configure | Site & Brand Setup | Brand voice training | ASSISTED | DF | 3/13 (Jasper, Frase, Copy.ai) | GAP | E-001 |
| 1.3 | configure | Site & Brand Setup | CMS connection setup (WordPress, Shopify) | ASSISTED | TS | 10/13 competitors | GAP | E-001 |
| 1.4 | configure | Site & Brand Setup | Topic/niche configuration | ASSISTED | TS | 8/13 competitors | GAP | E-001 |
| 1.5 | configure | Site & Brand Setup | Quality threshold settings | ASSISTED | DF | 2/13 (Surfer, Clearscope) | GAP | E-001 |
| 1.6 | configure | Site & Brand Setup | AISO scoring preferences | ASSISTED | IN | 0/13 competitors | GAP | E-001 |
| 2.0 | research | Keyword Intelligence | — | — | — | — | — | E-002 |
| 2.1 | research | Keyword Intelligence | Keyword research & discovery | AUTO | TS | 9/13 competitors | GAP | E-002 |
| 2.2 | research | Keyword Intelligence | Keyword clustering & topic mapping | AUTO | DF | 3/13 (Scalenut, MarketMuse, Frase) | GAP | E-002 |
| 2.3 | research | Keyword Intelligence | Search intent classification | AUTO | DF | 4/13 (Surfer, Frase, Scalenut, Clearscope) | GAP | E-002 |
| 2.4 | research | Keyword Intelligence | Keyword cannibalisation detection | AUTO | DF | 2/13 (Clearscope, MarketMuse) | GAP | E-002 |
| 2.5 | research | Content Gap Analysis | — | — | — | — | — | E-002 |
| 2.5.1 | research | Content Gap Analysis | Competitor content audit | AUTO | TS | 8/13 competitors | GAP | E-002 |
| 2.5.2 | research | Content Gap Analysis | Content gap identification | AUTO | TS | 7/13 competitors | GAP | E-002 |
| 2.5.3 | research | Content Gap Analysis | SERP analysis & feature detection | AUTO | TS | 8/13 competitors | GAP | E-002 |
| 2.6 | research | AISO Intelligence | — | — | — | — | — | E-002 |
| 2.6.1 | research | AISO Intelligence | AI engine citation analysis | AUTO | IN | 0/13 (Frase/Scalenut monitor but don't analyse for generation) | GAP | E-002 |
| 2.6.2 | research | AISO Intelligence | Entity coverage gap analysis | AUTO | IN | 0/13 competitors | GAP | E-002 |
| 2.6.3 | research | AISO Intelligence | Schema opportunity detection | AUTO | IN | 0/13 competitors | GAP | E-002 |
| 3.0 | generate | Content Generation | — | — | — | — | — | E-003 |
| 3.1 | generate | Content Generation | Content brief generation | AUTO | TS | 7/13 (Frase, Surfer, Scalenut, ContentShake, Writesonic, Koala, MarketMuse) | GAP | E-003 |
| 3.2 | generate | Content Generation | Article outline generation | AUTO | TS | 10/13 competitors | GAP | E-003 |
| 3.3 | generate | Content Generation | Full article generation (1,500-5,000 words) | AUTO | TS | 11/13 competitors | GAP | E-003 |
| 3.4 | generate | Content Generation | AISO-native content structuring | AUTO | IN | 0/13 (our 36-factor model is unique) | GAP | E-003 |
| 3.5 | generate | Content Generation | NLP term integration | AUTO | DF | 6/13 (Surfer, Frase, Scalenut, NeuronWriter, Clearscope, MarketMuse) | GAP | E-003 |
| 3.6 | generate | Content Generation | Image generation/sourcing | ASSISTED | DF | 4/13 (ArticleForge, Koala, Writesonic, ContentShake) | GAP | E-003 |
| 3.7 | generate | Content Optimisation | — | — | — | — | — | E-003 |
| 3.7.1 | generate | Content Optimisation | SEO content scoring (0-100) | AUTO | TS | 7/13 competitors | GAP | E-003 |
| 3.7.2 | generate | Content Optimisation | AISO content scoring (36-factor) | AUTO | IN | 0/13 competitors | GAP | E-003 |
| 3.7.3 | generate | Content Optimisation | Dual SEO+AISO scoring | AUTO | IN | 0/13 (Frase has dual but not 36-factor depth) | GAP | E-003 |
| 3.7.4 | generate | Content Optimisation | Iterative improvement loop | AUTO | DF | 2/13 (Surfer content editor, Frase AI agent) | GAP | E-003 |
| 3.7.5 | generate | Content Optimisation | Readability scoring | AUTO | TS | 5/13 competitors | GAP | E-003 |
| 3.7.6 | generate | Content Optimisation | Fact-checking & citation validation | ASSISTED | DF | 1/13 (Writesonic) | GAP | E-003 |
| 4.0 | publish | Content Publishing | — | — | — | — | — | E-004 |
| 4.1 | publish | Content Publishing | WordPress publishing (API) | AUTO | TS | 10/13 competitors | GAP | E-004 |
| 4.2 | publish | Content Publishing | Shopify blog publishing | AUTO | DF | 2/13 (Koala, Writesonic) | GAP | E-004 |
| 4.3 | publish | Content Publishing | Schema markup injection (6+ types) | AUTO | IN | 0/13 (Koala does entity-only) | GAP | E-004 |
| 4.4 | publish | Content Publishing | Internal link insertion | AUTO | DF | 2/13 (Koala, NeuronWriter) | GAP | E-004 |
| 4.5 | publish | Content Publishing | Image upload & alt text | AUTO | TS | 6/13 competitors | GAP | E-004 |
| 4.6 | publish | Content Publishing | Scheduled publishing | AUTO | DF | 2/13 (ArticleForge, Koala) | GAP | E-004 |
| 5.0 | monitor | Performance Monitoring | — | — | — | — | — | E-005 |
| 5.1 | monitor | Performance Monitoring | Traditional rank tracking | AUTO | TS | 5/13 (Surfer, Scalenut, Semrush ecosystem) | GAP | E-005 |
| 5.2 | monitor | Performance Monitoring | AI visibility tracking | AUTO | DF | 3/13 (Frase, Scalenut, Writesonic) | GAP | E-005 |
| 5.3 | monitor | Performance Monitoring | Content decay detection | AUTO | IN | 0/13 competitors | GAP | E-005 |
| 5.4 | monitor | Performance Monitoring | AI citation probability scoring | AUTO | IN | 0/13 competitors | GAP | E-005 |
| 5.5 | monitor | Content Refresh | — | — | — | — | — | E-005 |
| 5.5.1 | monitor | Content Refresh | Auto-refresh trigger (decay detected) | AUTO | IN | 0/13 competitors | GAP | E-005 |
| 5.5.2 | monitor | Content Refresh | Content update generation | AUTO | IN | 0/13 competitors | GAP | E-005 |

## Cross-Cutting Capabilities

| ID | Capability | Automation | Class | Evidence | Coverage |
|:--:|-----------|:----------:|:-----:|:--------:|:--------:|
| X.1 | Multi-model AI routing (choose best LLM per task) | AUTO | DF | 1/13 (Jasper) | GAP |
| X.2 | API access for programmatic use | AUTO | TS | 7/13 competitors | GAP |
| X.3 | Multi-language support | AUTO | TS | 8/13 competitors | GAP |
| X.4 | Bulk generation (batch mode) | AUTO | DF | 5/13 (Koala, Byword, Writesonic, ArticleForge, Scalenut) | GAP |
| X.5 | Brand voice profiles (per-client) | ASSISTED | DF | 3/13 (Jasper, Frase, Copy.ai) | GAP |
| X.6 | White-label/agency mode | HUMAN-LED | DF | 2/13 (SEO.AI, agency tiers) | GAP |

## Coverage Statistics

| Metric | Value |
|--------|-------|
| Total L3 sub-processes | 38 |
| AUTO | 34 (89%) |
| ASSISTED | 4 (11%) |
| HUMAN-LED | 0 (0%) |
| HUMAN-ONLY | 0 (0%) |
| Table-stakes | 14 |
| Differentiators | 13 |
| Innovations | 11 |
| Coverage gaps | 38 (100% — greenfield) |
| Competitors analysed | 13 |
| Cross-cutting capabilities | 6 |

## Legend

**Automation levels:** `AUTO` (no human input) | `ASSISTED` (AI does most, human reviews) | `HUMAN-LED` (human does primary, AI assists) | `HUMAN-ONLY` (no automation)

**Feature classes:** `TS` (table-stakes — most competitors have it) | `DF` (differentiator — 2-3 competitors have it) | `IN` (innovation — no competitor has it) | `EN` (enabler — never customer-facing)

**Coverage:** `BUILT` | `PLANNED` | `GAP`
