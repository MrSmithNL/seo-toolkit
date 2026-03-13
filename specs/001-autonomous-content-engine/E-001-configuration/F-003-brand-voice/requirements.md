---
id: "FTR-CONFIG-003"
type: feature
title: "Brand Voice Training"
project: PROD-001
domain: configuration
parent: "EPC-CONFIG-001"
status: draft
phase: 3-requirements
priority: should
created: 2026-03-13
last_updated: 2026-03-13

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

# Brand Voice Training — Requirements

## Problem Statement

AI-generated content sounds generic unless guided by the brand's writing style. Without brand voice configuration, the content pipeline produces articles that don't match the client's existing tone, vocabulary, or style — requiring heavy manual editing that defeats the purpose of autonomous generation. Jasper is the only competitor with mature voice training; no autonomous content tool combines voice training with pipeline configuration.

## Research Summary

### Competitor Analysis

| Capability | Jasper | Copy.ai | Frase | Our Approach |
|-----------|:------:|:-------:|:-----:|:------------:|
| URL scan for voice extraction | ✅ (up to 8 URLs) | ❌ | ❌ | ✅ (1-5 URLs) |
| Text sample analysis | ✅ | ✅ (300+ words) | ❌ | ✅ |
| Auto-generated voice profile | ✅ | ✅ | ❌ | ✅ |
| Manual parameter editing | ✅ | ✅ | ✅ (style guides) | ✅ |
| Multiple voices per workspace | ✅ | ✅ | ❌ | ❌ (V2) |
| Voice as pipeline input | ❌ | ❌ | ❌ | ✅ |

### Key Findings

- URL scan is the lowest-friction input method (Jasper model)
- 3000+ words of sample content recommended for accurate voice extraction (Copy.ai finding)
- Two-component model works well: brand knowledge (what) + writing style (how) (Jasper architecture)
- V1 scope: one voice per site, stored as JSON profile used as system prompt modifier in E-003

### Sources

- `research/e001-configuration-setup-patterns.md` §3 (Brand Voice Training)
- `E-001-configuration/research/phase2-analysis.md` §Spec-as-Context for F-003

## Impact Map

```
Goal: Generate content that sounds like the brand, not like generic AI
  +-- Actor: Agency operator (Malcolm) / Future SaaS user
       +-- Impact: Content requires minimal voice editing after generation
            +-- Deliverable: URL-based voice extraction
            +-- Deliverable: Structured voice profile (JSON)
            +-- Deliverable: Manual voice parameter editing
```

## Domain Model

```
VoiceProfile {
  id: UUID
  site_id: UUID (FK -> SiteConfig.id)

  # Brand Knowledge (what the brand is about)
  brand_name: string
  industry: string
  target_audience: string
  brand_values: string[]
  key_topics: string[]

  # Writing Style (how the brand writes)
  tone: enum (formal, conversational, technical, casual, authoritative)
  sentence_structure: enum (short, long, mixed)
  vocabulary_level: enum (simple, intermediate, advanced, technical)
  person: enum (first, second, third)
  distinctive_patterns: string[] (e.g., "uses metaphors", "short paragraphs", "rhetorical questions")

  # Metadata
  source_urls: URL[] (URLs used for extraction)
  word_count_analysed: int (total words from source content)
  confidence: enum (low, medium, high) (based on word count analysed)
  created_at: timestamp
  updated_at: timestamp
}
```

Note: `source_urls`, `word_count_analysed`, `confidence`, and `distinctive_patterns` are stored as JSON fields within the Prisma VoiceProfile model. See epic-design.md for the full Prisma schema.

## User Stories

### US-001: Extract voice from existing site content

**As a** content pipeline operator, **I want** to provide 1-5 URLs from my site for voice analysis, **so that** the system learns my brand's writing style automatically.

**Priority:** Must
**Size:** L

**Acceptance Criteria:**

WHEN a user provides 1-5 URLs for voice extraction
THE SYSTEM SHALL crawl each URL and extract the main content (strip navigation, headers, footers, sidebars)
AND feed the extracted text to the AI with a structured voice analysis prompt
AND generate a VoiceProfile with all fields populated
AND store the profile linked to the site configuration

WHEN the total extracted content is less than 500 words
THE SYSTEM SHALL warn "Limited content found. Voice profile may be inaccurate. Provide URLs with more text content."
AND set confidence to "low"

WHEN a URL is unreachable or returns no content
THE SYSTEM SHALL skip it, continue with remaining URLs, and note which URLs failed

**Examples:**

| Scenario | Input URLs | Content Extracted | Expected Outcome |
|----------|-----------|-------------------|-----------------|
| Rich content (3 blog posts) | 3 Hairgenetix blog URLs | ~4500 words total | Full profile generated, confidence: high |
| Minimal content (1 product page) | 1 Skingenetix product URL | ~200 words | Profile generated with warning, confidence: low |
| Mixed (1 reachable, 1 404) | 2 URLs, 1 returns 404 | ~1500 words from 1 URL | Profile from reachable URL, note about failed URL, confidence: medium |
| No content extractable | 1 URL with only images/video | 0 words | Error: "No text content found at the provided URLs." |

### US-002: Manually adjust voice parameters

**As a** content pipeline operator, **I want** to edit the auto-generated voice profile, **so that** I can fine-tune aspects the AI got wrong or add brand-specific rules.

**Priority:** Should
**Size:** S

**Acceptance Criteria:**

WHEN the user views a generated voice profile
THE SYSTEM SHALL display all parameters in an editable format

WHEN the user modifies any parameter
THE SYSTEM SHALL update the stored profile immediately
AND note that the profile has been manually edited (preserve source_urls but mark as "manually adjusted")

**Examples:**

| Scenario | Parameter Changed | Expected Outcome |
|----------|------------------|-----------------|
| Change tone | formal -> conversational | Profile updated, used in next generation |
| Add distinctive pattern | Add "always ends with a call-to-action" | Pattern added to distinctive_patterns array |
| Override vocabulary | simple -> technical | Updated, affects next content generation |

### US-003: Skip voice training (use default)

**As a** content pipeline operator, **I want** to skip voice training and use a generic professional tone, **so that** I can start generating content immediately without providing samples.

**Priority:** Must
**Size:** S

**Acceptance Criteria:**

WHEN the user skips voice training
THE SYSTEM SHALL create a default VoiceProfile with: tone=conversational, sentence_structure=mixed, vocabulary_level=intermediate, person=second, distinctive_patterns=[]
AND set confidence to "low"
AND note "Default voice — no brand-specific training"

**Examples:**

| Scenario | Action | Expected Outcome |
|----------|--------|-----------------|
| Skip voice | User chooses "Skip, use default" | Default profile created, pipeline can proceed |
| Come back later | User skips, then returns to train voice | New profile from URLs replaces default |

## Non-Functional Requirements

| # | Category | Requirement (EARS format) | Fit Criterion | Measurement Method | CI Gate? |
|---|----------|--------------------------|---------------|--------------------|:--------:|
| 1 | **Performance** | WHEN extracting voice from URLs THE SYSTEM SHALL complete analysis WITHIN 60 seconds for up to 5 URLs | p95 < 60s | Integration test with timer | Yes |
| 2 | **Security** | N/A — voice profiles contain no sensitive data (public content analysis) | — | — | No |
| 3 | **Reliability** | WHEN one or more source URLs fail THE SYSTEM SHALL continue with remaining URLs and produce a partial profile | Graceful degradation | Integration test with mock failures | Yes |
| 4 | **Scalability** | N/A — single-user, one profile per site | — | — | No |
| 5 | **Availability** | N/A — not a hosted service for V1 | — | — | No |
| 6 | **Maintainability** | WHEN the voice analysis prompt needs updating THE SYSTEM SHALL store the prompt as a versioned template, not hardcoded | Prompt template file | Code review | No |
| 7 | **Portability** | N/A — Node.js runtime | — | — | No |
| 8 | **Accessibility** | N/A — CLI interface for V1 | — | — | No |
| 9 | **Usability** | WHEN training brand voice THE SYSTEM SHALL accept URLs only — no file uploads for V1 | URL-only input | Manual verification | No |
| 10 | **Interoperability** | N/A — voice profiles are internal JSON, consumed by E-003 only | — | — | No |
| 11 | **Compliance** | N/A — analysing publicly available website content | — | — | No |
| 12 | **Data Retention** | WHEN a site is deleted THE SYSTEM SHALL delete the associated voice profile | Cascade delete | Integration test | Yes |
| 13 | **Backup / Recovery** | WHEN a voice profile is lost THE SYSTEM SHALL support re-extraction from the same URLs | Re-runnable extraction | Manual verification | No |
| 14 | **Logging** | WHEN voice extraction completes THE SYSTEM SHALL log: source URLs, word count extracted, confidence level, duration | Structured log entry | Log assertion in test | Yes |
| 15 | **Cost** | WHEN extracting voice THE SYSTEM SHALL use one AI API call (Claude) per extraction | Max 1 API call per extraction | Code review | No |
| 16 | **Capacity** | N/A — one profile per site, max ~10 sites | — | — | No |
| 17 | **Internationalisation** | WHEN the source content is in a non-English language THE SYSTEM SHALL detect the language and generate the voice profile in that language context | Language-aware profile | Integration test with Dutch content | No |
| 18 | **Extensibility** | N/A — voice extraction is a single AI call, not a pluggable system for V1 | — | — | No |
| 19 | **Operation Pattern** | WHEN any command or query is executed THE SYSTEM SHALL follow the 5-step Operation pattern (P-008): Zod input → OperationContext → business logic → persist → emit event + return Result<T, OperationError> | All operations return Result type | Architecture fitness test FF-030 | Yes |
| 20 | **Error Handling** | WHEN a voice extraction or profile operation fails THE SYSTEM SHALL return an OperationError (not throw) with RFC 7807-compatible error codes and `suggested_action` field | Zero naked `throw` in commands/queries | FF-032 + code review | Yes |
| 21 | **Structured Logging** | WHEN any voice profile operation executes THE SYSTEM SHALL emit `operation.started`, `operation.completed`, and `operation.failed` structured JSON events via pino with correlationId + tenantId | 3 log events per operation | Log assertion in integration test | Yes |
| 22 | **Tenant Isolation** | WHEN querying voice profile data THE SYSTEM SHALL enforce RLS so Tenant A cannot read/update/delete Tenant B's voice profiles. Cross-tenant access returns 404 (not 403). | `tenant-isolation.test.ts` passes | Integration test (FF-034) | Yes |
| 23 | **Idempotency** | WHEN creating voice profiles THE SYSTEM SHALL accept an optional idempotencyKey. Duplicate requests with the same key return the original result without creating duplicates. | Duplicate request = same response | Integration test | Yes |
| 24 | **Serialisable I/O** | WHEN returning voice profile data from any operation THE SYSTEM SHALL use ISO 8601 strings for dates (never Date objects), plain objects only (no class instances) | JSON.parse(JSON.stringify(output)) === output | Unit test | Yes |
| 25 | **Contract Completeness** | WHEN exposing voice profile commands or queries THE SYSTEM SHALL have a Zod input schema AND explicit TypeScript return type for each | Every public function has Zod + return type | FF-029 | Yes |
| 26 | **No Module State** | THE SYSTEM SHALL NOT use `let` or `var` at module scope in voice profile `src/` files (except type exports and `const`) | Zero mutable module-level state | FF-033 | Yes |
| 27 | **PII Redaction** | WHEN logging voice profile data THE SYSTEM SHALL redact any email, phone, IP address, or personal data fields using pino's redaction config | PII fields show `[REDACTED]` in logs | Log inspection test | Yes |
| 28 | **Prefixed IDs** | WHEN creating a VoiceProfile THE SYSTEM SHALL generate IDs with `vce_` prefix using NanoID or UUID v7 | All IDs match `vce_*` pattern | Unit test | Yes |
| 29 | **Circuit Breaker** | WHEN making API calls to AI/LLM services for voice extraction THE SYSTEM SHALL use a circuit breaker (5 failures / 60s window → open for 30s) to prevent cascading failures from AI service outages | Circuit breaker state logged | Integration test | No |

### AI-Specific NFRs

| Category | Requirement (EARS format) | Fit Criterion | Measurement Method |
|----------|--------------------------|---------------|--------------------|
| Inference latency | WHEN calling the AI for voice analysis THE SYSTEM SHALL timeout after 90 seconds | p95 < 90s | Integration test |
| Token economics | WHEN analysing voice THE SYSTEM SHALL use no more than 10,000 input tokens per extraction | Max 10K input tokens | Token counting in test |
| Hallucination rate | WHEN generating a voice profile THE SYSTEM SHALL base all parameters on the actual source content, not invent characteristics | Human review of 3 test profiles | Manual QA |
| Prompt versioning | WHEN the voice analysis prompt is updated THE SYSTEM SHALL version the prompt and log which version was used for each profile | Prompt version in profile metadata | Code review |

## Out of Scope

- Multiple voice profiles per site — deferred to V2
- File upload for voice samples (PDF, DOCX) — V2
- Voice comparison/preview mode (with vs without) — V2
- Real-time voice enforcement during editing (Frase-style) — V2
- Voice sharing across sites — V2

## Open Questions

- [x] How many URLs should we accept? **Answer:** 1-5, matching Jasper's model. More than 5 adds diminishing returns.
- [x] What if the site has no blog content, only product pages? **Answer:** Accept product page URLs — extract voice from whatever content is available, but warn about low confidence.

## Dependencies

| Dependency | Type | Status | Blocks |
|-----------|------|--------|--------|
| F-001 (Site Registration) | Internal | In progress | Site URL needed for crawl context |
| Claude API | External | Ready | Voice analysis AI call |

## Assumptions

| ID | Assumption | Confidence | Validation Plan |
|----|-----------|-----------|----------------|
| A1 | Brand voice can be meaningfully extracted from 3-5 URLs (~3000+ words) | Medium | Test with Hairgenetix blog content, manual quality review |
| A2 | A JSON voice profile is sufficient as system prompt modifier for E-003 | Medium | Validate during E-003 development — does voice profile produce noticeably different output? |
| A3 | One AI call (Claude) per extraction is cost-effective | High | ~5000 input tokens × $0.015/1K = ~$0.075 per extraction |
