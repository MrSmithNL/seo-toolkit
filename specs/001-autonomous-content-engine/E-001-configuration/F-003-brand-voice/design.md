---
id: "FTR-CONFIG-003"
type: feature
title: "Brand Voice Training"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 4-design
priority: should
created: 2026-03-13
last_updated: 2026-03-13
refs:
  requirements: "./requirements.md"

# === PARENT ALIGNMENT ===
parent_baseline:
  id: "EPC-CONFIG-001"
  version: null
  hash: null
  status: aligned

# === ARCHITECTURE CLASSIFICATION (Gate 0) ===
saas_ecosystem: true
hierarchy_level: L3-module
hierarchy_location: "modules/content-engine/"
capability_group: "seo"
module_manifest: required
tenant_aware: true

# === TRACEABILITY ===
traces_to:
  product_goal: "PROD-001: SEO Toolkit capability engine"
  theme: "specs/001-autonomous-content-engine/theme.md"
  epic: "E-001 Configuration & Setup"
  capability: "CAP-CE-001 — Site & Pipeline Configuration"
---

# Feature Design — Brand Voice Training (F-003)

> Slim feature design. See `../epic-design.md` for shared architecture (Drizzle schema, module boundary, coding guardrails, cross-cutting concerns).

---

## Architecture Overview

F-003 extracts a writing style profile from existing site content using LLM analysis. The voice profile is consumed by E-003 (Writer stage) to match generated content to the brand's tone.

```
src/modules/content-engine/config/
├── brand-voice/
│   ├── brand-voice.service.ts           ← orchestrates extraction flow
│   ├── brand-voice.repository.ts        ← VoiceProfile persistence
│   ├── brand-voice.schema.ts            ← Zod input/output schemas
│   ├── voice-extractor.ts               ← LLM-based voice analysis
│   ├── content-fetcher.ts               ← fetch + clean page content
│   └── __tests__/
│       ├── brand-voice.service.test.ts
│       ├── voice-extractor.test.ts
│       └── content-fetcher.test.ts
```

---

## Component Design

```typescript
// === Value Objects ===

type Tone = 'formal' | 'conversational' | 'playful' | 'authoritative' | 'empathetic';
type VocabularyLevel = 'basic' | 'intermediate' | 'advanced' | 'technical';
type WritingStyle = 'concise' | 'descriptive' | 'narrative' | 'instructional';

interface VoiceExtractionResult {
  brandName: string | null;
  industry: string | null;
  targetAudience: string | null;
  brandValues: string[];
  keyTopics: string[];
  tone: Tone;
  sentenceStructure: 'short' | 'mixed' | 'long';
  vocabularyLevel: VocabularyLevel;
  person: 'first' | 'second' | 'third';
}

// === Service ===

class BrandVoiceService {
  constructor(
    private repo: VoiceProfileRepository,
    private contentFetcher: ContentFetcher,
    private voiceExtractor: VoiceExtractor,
    private eventEmitter: EventEmitter,
  ) {}

  async extractVoice(siteId: string, urls: string[]): Promise<VoiceProfile>;
  async updateVoice(siteId: string, params: UpdateVoiceInput): Promise<VoiceProfile>;
  async getVoice(siteId: string): Promise<VoiceProfile | null>;
}

// === Voice Extractor ===

class VoiceExtractor {
  constructor(private llmClient: LLMClient) {}

  async extract(pageContents: PageContent[]): Promise<VoiceExtractionResult>;
}

// === Content Fetcher ===

class ContentFetcher {
  async fetchAndClean(url: string): Promise<PageContent>;
  // Strips nav, footer, scripts → returns main content text
}
```

---

## DDD Tactical Patterns

| Pattern | Element | Notes |
|---------|---------|-------|
| **Aggregate** | `VoiceProfile` | Child of `SiteConfig`, one-to-one relationship |
| **Value object** | `Tone` | Enum — constrained set of voice tones |
| **Value object** | `VocabularyLevel` | Enum — reader sophistication level |
| **Value object** | `WritingStyle` | Enum — overall writing approach |
| **Domain event** | `voice.extracted` | `{ siteId, voiceProfileId }` — consumed by E-003 Writer |
| **Repository** | `VoiceProfileRepository` | Standard CRUD, tenant-scoped |

---

## Key Algorithms

### URL-Based Voice Extraction

```
1. For each URL in input (max 5 URLs):
   a. HTTP GET the page (10s timeout)
   b. Parse HTML, extract main content area:
      - Remove <nav>, <footer>, <header>, <script>, <style>
      - Extract text from <main> or <article>, fallback to <body>
   c. Truncate to ~2000 words (to fit token budget)
2. Concatenate cleaned content from all pages
3. Send to LLM with extraction prompt:
   - System: "You are a brand voice analyst..."
   - User: "Analyse the following content and extract the brand voice profile.
            Return JSON matching this schema: { brandName, industry,
            targetAudience, brandValues[], keyTopics[], tone, sentenceStructure,
            vocabularyLevel, person }"
   - Content: [concatenated page text]
4. Parse structured JSON response
5. Validate with Zod schema
6. Persist to VoiceProfile
```

### Token Budget Management

```
- Target: ~4000 tokens per extraction call
- System prompt: ~200 tokens
- Page content: ~3500 tokens (~2500 words across all pages)
- Response: ~300 tokens (structured JSON)
- If content exceeds budget: truncate each page proportionally
```

---

## API Surface

R1 CLI functions:

| Function | Signature | Description |
|----------|-----------|-------------|
| `extractVoice` | `(siteId, urls: string[]) => Promise<VoiceProfile>` | Fetch pages, run LLM extraction, persist |
| `updateVoice` | `(siteId, params: UpdateVoiceInput) => Promise<VoiceProfile>` | Manual override of extracted values |

R2 HTTP routes:

| Method | Path | Handler |
|--------|------|---------|
| `POST` | `/sites/:id/voice` | `extractVoice` |

---

## Integration Points

| External System | Protocol | Purpose | Timeout | Retry |
|----------------|----------|---------|---------|-------|
| Target site pages | HTTP GET | Fetch content for voice analysis | 10s per page | No retry |
| LLM API (Claude/GPT) | HTTPS | Voice profile extraction from content | 30s | 1 retry |

---

## Testing Strategy

| Category | What to Test | Approach |
|----------|-------------|----------|
| **Unit** | Content fetcher (HTML cleaning, element removal, truncation) | Mock HTML responses |
| **Unit** | Voice extractor (valid LLM response, malformed response, empty content) | Mock LLM client |
| **Unit** | Token budget calculation and truncation | Direct function tests |
| **Integration** | Full extraction flow (fetch → clean → extract → persist) | In-memory SQLite + mock LLM |
| **Edge case** | All URLs unreachable | Expect meaningful error |
| **Edge case** | LLM returns invalid JSON | Expect retry or fallback defaults |

---

## Feature-Specific Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | LLM extraction over rule-based analysis | Rules can't capture nuanced brand voice; LLM handles subjective attributes well |
| 2 | Max 5 URLs per extraction | Balances quality (enough samples) with cost (token usage) |
| 3 | Prompt versioning needed | Voice extraction quality depends on prompt; must track which version produced each profile |
| 4 | Manual override allowed | LLM extraction is a starting point — users can refine any field |
| 5 | ~4000 token budget | Keeps LLM cost low (~$0.01 per extraction) while providing enough context |
