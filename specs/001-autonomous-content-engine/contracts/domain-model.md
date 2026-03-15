# Domain Model — Autonomous Content Engine

> Core entities and their relationships. To be detailed during Phase 4 (Design) for each epic.
> This is a theme-level overview — each epic adds entity detail during its design phase.

## Core Entities (Draft)

```
Keyword
├── text: string
├── volume: number (monthly searches)
├── difficulty: number (0-100)
├── intent: enum (informational | commercial | transactional | navigational)
├── language: string (ISO 639-1)
├── cpc: number (cost per click)
└── trend: number[] (12-month history)

TopicCluster
├── name: string
├── pillar_keyword: Keyword
├── supporting_keywords: Keyword[]
└── cluster_strength: number (semantic cohesion score)

SERPResult
├── keyword: Keyword
├── position: number
├── url: string
├── title: string
├── description: string
├── serp_features: string[] (PAA, featured_snippet, knowledge_panel, ai_overview)
└── scraped_at: datetime

ContentBrief (E-001 → E-002 output)
├── target_keyword: Keyword
├── cluster: TopicCluster
├── serp_baseline: SERPResult[]
├── competitor_urls: string[]
├── recommended_format: enum (blog_post | guide | listicle | comparison | faq)
├── word_count_target: number
├── outline: Section[]
└── priority_score: number

ContentCalendar
├── briefs: ContentBrief[]
├── publish_schedule: { brief_id: string, date: date }[]
├── approval_status: enum (draft | approved | rejected)
└── generated_at: datetime
```

## Entity Relationships

```
Keyword ──1:N──→ TopicCluster (via supporting_keywords)
Keyword ──1:N──→ SERPResult
Keyword ──1:1──→ ContentBrief (via target_keyword)
ContentBrief ──N:1──→ TopicCluster
ContentBrief ──N:1──→ ContentCalendar
```

## Cross-Epic Data Flow

```
E-001 (Research)  → ContentBrief    → E-002 (Creation)
E-001 (Research)  → KeywordTarget   → E-003 (Optimisation)
E-001 (Research)  → SERPBaseline    → E-005 (Measurement)
E-002 (Creation)  → Article         → E-003 (Optimisation)
E-003 (Optimised) → PublishReady    → E-004 (Distribution)
E-004 (Published) → LiveURL         → E-005 (Measurement)
```
