---
# === IDENTITY ===
id: "PROD-001-SPEC-001"
type: theme
title: "Autonomous Content Engine"
created: 2026-03-15

# === HIERARCHY ===
project: PROD-001
vertical: aisogen
domain: content-pipeline
parent: null
children: []
capability: "seo.content-pipeline"

# === STATE ===
status: in-progress
phase: phase-0
priority: must
size: XL
risk: medium
owner: claude
last_updated: 2026-03-15

# === RELEASE ===
target_release: R1-MVP
release: null
cycle: null

# === TIMESTAMPS ===
timestamps:
  created: 2026-03-15
  started: 2026-03-15
  review: null
  completed: null
  deployed: null

# === TRACEABILITY ===
refs:
  briefing: "./automated-article-generator-briefing.md"
  requirements: null
  design: null
  tasks: null
  code: []
  tests: []

# === AI PROVENANCE ===
ai:
  generation: autonomous
  model: claude-opus-4-6
  confidence: high
  reviewed: false
  review_date: null

# === GATES ===
gates:
  gate_0: pending
  scope: pending
  completeness: pending
  build_approval: pending

# === BASELINE ===
baseline:
  version: null
  date: null
  hash: null
  approved_by: null

# === ARCHITECTURE CLASSIFICATION (Gate 0 — RE v4.23) ===
saas_ecosystem: true
hierarchy_level: L3-module
hierarchy_location: "modules/content-engine/"
capability_group: seo
dual_mode: true  # standalone CLI now, platform web later
five_port: true  # Database, Auth, AIGateway, FeatureFlags, Notifications
module_manifest: required
tenant_aware: true
dependency_checklist_complete: true  # All 29 items in Sections A/B/C assessed
level_checklist_used: L3  # L3 full consumer checklist applied (all A1-A13, B1-B11, C1-C5)

# === TRACEABILITY ===
traces_to:
  product_goal: "Autonomous SEO/GEO/AISO content pipeline"
  theme: "001-autonomous-content-engine"
  epic: null
  feature: null
  capability: "seo.content-pipeline"

tags: [content-engine, seo, aiso, geo, pipeline, shopify, multilingual]
---

# Autonomous Content Engine — Status

## Current State

**Gate 0 (Architecture Classification) in progress.** This is a fresh RE run (v4.23) starting from the preserved BA briefing doc. All previous RE outputs were discarded for a clean-slate re-run.

**Input:** `automated-article-generator-briefing.md` (BA deliverable — preserved from first run)

---

## Architecture Classification (Gate 0)

### Step 1: Classification Decision

| Field | Value | Rationale |
|-------|-------|-----------|
| `saas_ecosystem` | `true` | Content engine is a module within the PROD-004 SaaS Platform |
| `hierarchy_level` | `L3-module` | Pluggable business feature — content pipeline orchestration |
| `hierarchy_location` | `modules/content-engine/` | Standard L3 module location in SaaS Platform monorepo |
| `capability_group` | `seo` | Part of the SEO & AISO capability group |
| `dual_mode` | `true` | Standalone CLI (Phase 1-2) + Platform web (Phase 3: AISOGEN integration) |
| `five_port` | `true` | Uses all 5 standard ports: Database, Auth, AIGateway, FeatureFlags, Notifications |
| `tenant_aware` | `true` | Multi-client/multi-site by design (briefing §4.4) |

### Step 2: Hierarchy Placement

```
PROD-004 SaaS Platform (Turborepo)
├── packages/              ← L1-L2 Foundation + Core
│   ├── core/              ← Auth, DB, tenant context
│   ├── ui/                ← Shared UI components
│   └── seo-engine/        ← SEO Toolkit agents (existing)
├── modules/
│   └── content-engine/    ← THIS MODULE (L3)
│       ├── commands/      ← Write operations (create article, publish, etc.)
│       ├── queries/       ← Read operations (get pipeline status, scores, etc.)
│       ├── events/        ← Emitted events (article.created, article.published, etc.)
│       ├── schemas/       ← Zod schemas (from drizzle-zod)
│       └── adapters/      ← Five-Port adapters (standalone + platform)
└── apps/
    └── aisogen/           ← L5 Vertical (consumes content-engine module)
```

### Step 3: Level-Specific Integration Checklist (L3 — Business Module)

As per RE v4.23, all L3 modules must check all Section A items, plus Section B if using LLMs, plus Section C if external connections.

This module uses LLMs (AI content generation, scoring, validation) AND has external connections (Shopify, CMS adapters, translation APIs). **All 3 sections apply.**

### Step 4: Standard Dependency Checklist

**Section A: Infrastructure Dependencies (ALL components)**

| # | Dependency | Needed? | If needed: Status / Temp Solution / Migration Path |
|---|-----------|---------|---------------------------------------------------|
| A1 | **Database & persistence** | **NEEDED** | Content pipeline state, article drafts, scores, audit history, content calendars. Tenant-scoped (tenant_id on all tables). **Temp:** SQLite + Drizzle (standalone mode). **Migrate:** Swap to PostgreSQL adapter when PROD-004 DB package ships. Same Drizzle schema, different driver. |
| A2 | **Authentication & tenant context** | **NEEDED** | Identify which client/site the pipeline is running for. **Temp:** Config file per client (JSON/YAML). **Migrate:** Swap to PROD-004 auth package (JWT + tenant context middleware). Five-Port AuthPort interface. |
| A3 | **Event bus** | **NEEDED** | Events: `article.researched`, `article.drafted`, `article.optimised`, `article.published`, `article.audited`, `score.dropped`, `reoptimisation.triggered`. **Temp:** In-process EventEmitter (Node.js). **Migrate:** Swap to PROD-004 event bus (Redis Streams or similar). Five-Port EventPort interface. |
| A4 | **Shared UI components** | **NEEDED** | Dashboard views (calendar, scorecard, article detail, strategy, publication status). **Temp:** Standalone Next.js app with local component library. **Migrate:** Swap to `packages/ui/` shared components when PROD-004 UI package ships. |
| A5 | **Logging & observability** | **NEEDED** | Structured logging for 5-stage pipeline execution, error tracking, request tracing. **Temp:** Pino structured JSON logger + console output. **Migrate:** Swap to PROD-004 logging package (OpenTelemetry integration). |
| A6 | **Notifications** | **NEEDED** | Notify user: article ready for review, score dropped, pipeline error, batch complete. **Temp:** Pushover (existing agency notification). **Migrate:** Swap to PROD-004 notifications package (email, in-app, push). Five-Port NotificationsPort interface. |
| A7 | **Feature flags** | **NEEDED** | Per-tenant feature toggles: auto-publish on/off, AISO scoring on/off, re-optimisation on/off. **Temp:** Config-file-based feature flags. **Migrate:** Swap to PROD-004 feature flags package (LaunchDarkly or similar). Five-Port FeatureFlagsPort interface. |
| A8 | **Scheduling & queueing** | **NEEDED** | Pipeline orchestration: 5-stage sequential pipeline, retry on failure, scheduled re-audits (24h, weekly, monthly). **Temp:** BullMQ + Redis (standalone). **Migrate:** Same BullMQ in platform context (Redis shared). |
| A9 | **File & asset storage** | **NEEDED** | Article images, generated schemas, exported reports. **Temp:** Local filesystem + S3 (standalone). **Migrate:** PROD-004 asset storage package. |
| A10 | **Rate limiting** | **NEEDED** | External API calls: Shopify API (2 req/s bucket), LLM APIs (RPM limits), translation APIs. **Temp:** p-throttle in-process rate limiter. **Migrate:** Platform-level rate limiting (API gateway). |
| A11 | **Caching** | **NEEDED** | SERP results (cache 24h), keyword data (cache 7d), LLM responses for idempotent queries. **Temp:** In-memory LRU cache (lru-cache). **Migrate:** Redis cache via platform. |
| A12 | **RBAC** | **DEFERRED** | Not needed for R1 (single-user per client). Needed for R2+ (agency view, team members). **Migrate:** PROD-004 RBAC when multi-user ships. |
| A13 | **Billing & usage tracking** | **DEFERRED** | Not needed for R1 (internal use). Needed for R4 (external users via AISOGEN). Track: articles generated, LLM tokens consumed, API calls made. **Migrate:** PROD-004 billing package (Stripe/Lemon Squeezy). |

**Section B: AI-Specific Dependencies (components using LLMs)**

| # | Dependency | Needed? | If needed: Status / Temp Solution / Migration Path |
|---|-----------|---------|---------------------------------------------------|
| B1 | **AI gateway** | **NEEDED** | Multi-model access: Claude (writing), GPT-4o (validation), Gemini 2.5 (validation). Cost tracking per article. **Temp:** Direct SDK calls (Anthropic, OpenAI, Google AI) with manual cost logging. **Migrate:** PROD-004 AI gateway package (unified interface, cost tracking, model routing). Five-Port AIGatewayPort interface. |
| B2 | **Agent runtime** | **NEEDED** | 6 pipeline agents: keyword research, content writer, SERP analyser, AISO auditor, CMS publisher, translation. **Temp:** Claude Code agent orchestration (existing skills + recipes). **Migrate:** PROD-004 agent runtime (tool registry, execution tracking). |
| B3 | **Prompt management & versioning** | **NEEDED** | Prompts for: article generation, SEO optimisation, AISO scoring, translation quality check. Need versioning for A/B testing prompt changes. **Temp:** Prompt files in `prompts/` directory with git versioning. **Migrate:** Platform prompt management (Langfuse or similar). |
| B4 | **Output validation & guardrails** | **NEEDED** | Content safety (YMYL health domain), PII detection, hallucination checks (medical claims need citations), schema validation (JSON-LD). **Temp:** Zod schema validation + custom guardrail checks. **Migrate:** Platform guardrails package. |
| B5 | **Embedding & vector storage (RAG)** | **DEFERRED** | Not needed for R1. Potential use in R3: content deduplication, semantic keyword clustering, knowledge base for re-optimisation recommendations. **Migrate:** PROD-004 vector storage (pgvector). |
| B6 | **Human-in-the-loop workflows** | **NEEDED** | Configurable approval gates: calendar approval, draft review, publish approval. Briefing §4.1 specifies "auto-approve or require approval" per stage. **Temp:** CLI prompts (standalone) + dashboard approval buttons (web). **Migrate:** Platform workflow engine. |
| B7 | **Durable execution & workflow state** | **NEEDED** | 5-stage pipeline runs >30 min end-to-end. Must survive crashes, resume from last completed stage. **Temp:** BullMQ job persistence (Redis-backed). **Migrate:** Platform durable execution (Temporal or similar). |
| B8 | **AI-specific observability** | **NEEDED** | Token costs per article, per tenant. Output quality drift (AISO scores trending down). Prompt version performance comparison. **Temp:** Custom metrics logged to structured JSON. **Migrate:** Langfuse or platform observability. |
| B9 | **Token budget management** | **DEFERRED** | Not needed for R1 (internal use, fixed budget). Needed for R2+ (per-client token budgets for pricing tiers). **Migrate:** Platform token budget (tied to billing). |
| B10 | **Model fallback & routing** | **NEEDED** | If Claude API down → fallback to GPT-4o for writing. If GPT-4o down → fallback to Gemini for validation. **Temp:** Try/catch with fallback model list. **Migrate:** Platform AI gateway handles routing. |
| B11 | **Evaluation & benchmarking** | **NEEDED** | Compare prompt versions: does v2 of the article prompt produce higher AISO scores than v1? **Temp:** Manual A/B testing with score comparison. **Migrate:** Platform evaluation framework (Langfuse evals). |

**Section C: Integration Dependencies (components with external connections)**

| # | Dependency | Needed? | If needed: Status / Temp Solution / Migration Path |
|---|-----------|---------|---------------------------------------------------|
| C1 | **Outbound webhooks** | **DEFERRED** | Not needed for R1. Needed for R3+ (notify external systems of published content, score changes). **Migrate:** Platform webhook package (Svix or similar). |
| C2 | **Secrets management** | **NEEDED** | Store customer CMS credentials (Shopify API keys), translation API keys, LLM API keys. **Temp:** Environment variables + `.env` files (gitignored). **Migrate:** Platform secrets management (Vault or similar). |
| C3 | **Audit trail & compliance logging** | **NEEDED** | Track all content changes for YMYL compliance: who generated, which model, which sources cited, approval chain. **Temp:** Append-only JSONL audit log. **Migrate:** Platform compliance logging. |
| C4 | **API key management** | **DEFERRED** | Not needed for R1. Needed for R4 (external API access). **Migrate:** Platform API key management. |
| C5 | **CMS / external system adapters** | **NEEDED** | R1: Shopify GraphQL Admin API (blog articles + translations). R2: WordPress REST API. R3+: headless CMS adapters. **Temp:** Direct Shopify GraphQL client. **Migrate:** Adapter pattern — each CMS gets a pluggable adapter implementing the same PublisherPort interface. |

### Dependency Summary

| Section | Total | NEEDED | DEFERRED | NOT NEEDED |
|---------|:-----:|:------:|:--------:|:----------:|
| A: Infrastructure | 13 | 11 | 2 (A12, A13) | 0 |
| B: AI-Specific | 11 | 8 | 3 (B5, B9, B11→NEEDED) | 0 |
| C: Integration | 5 | 3 | 2 (C1, C4) | 0 |
| **Total** | **29** | **22** | **7** | **0** |

**Note:** B11 (Evaluation) was initially considered for deferral but marked NEEDED because prompt quality directly affects article quality — the core product value. Manual A/B testing is the temporary solution.

### Five-Port Interface Summary

| Port | Standalone Adapter | Platform Adapter | Interface Contract |
|------|-------------------|------------------|-------------------|
| **DatabasePort** | SQLite + Drizzle | PostgreSQL + Drizzle | Same Drizzle schema, swap driver |
| **AuthPort** | Config file (JSON/YAML) | JWT + tenant middleware | `getCurrentTenant(): Tenant` |
| **AIGatewayPort** | Direct SDK calls | Platform AI gateway | `complete(model, prompt, options): Response` |
| **FeatureFlagsPort** | Config-file flags | LaunchDarkly / platform | `isEnabled(flag, context): boolean` |
| **NotificationsPort** | Pushover | Platform notifications | `notify(channel, message, severity): void` |

---

## Phase Progress

- [x] **Gate 0: Architecture Classification** — Complete (2026-03-15)
- [x] **Phase 0: Theme Identification** — Complete (2026-03-15)
- [ ] **Phase 1: Understand** — E-001 complete, E-002–E-006 pending
- [ ] **Phase 2: Research** — Competitive deep-dive (5 dimensions)
- [ ] **GATE 1: Scope Validation** — Malcolm reviews research and scope
- [ ] **Phase 3: Requirements** — EARS stories, NFRs, acceptance tests
- [ ] **GATE 2: Completeness Review** — Malcolm reviews full spec
- [ ] **Phase 4: Design** — Technical design, data model, API contracts
- [ ] **Phase 4b: Visual Preview** — Dashboard HTML mockups
- [ ] **Phase 4d: Process Design** — Pipeline state machines, decision tables
- [ ] **Phase 5: Tasks** — Agent-sized task breakdown
- [ ] **GATE 3: Build Approval** — Malcolm approves for implementation
- [ ] **Phase 6: Build** — TDD implementation
- [ ] **Phase 6.5: UAT** — Malcolm tests dashboard and pipeline
- [ ] **Phase 7: Ship** — Production deploy
- [ ] **Retrospective** — Estimation calibration, lessons captured

## Decisions Made

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | L3 Business Module classification | Pluggable business feature, not foundation or vertical | 2026-03-15 |
| 2 | Dual-mode (standalone CLI + platform web) | Build and prove standalone first, integrate into AISOGEN when platform is ready | 2026-03-15 |
| 3 | Five-Port architecture | Same interfaces, swap adapters — prevents rewrite when platform ships | 2026-03-15 |
| 4 | TypeScript for engine | Five-Port contract chain is TS-native, PROD-004 is Turborepo + TS | 2026-03-15 |
| 5 | 7 dependencies deferred (A12, A13, B5, B9, C1, C4 + B11 reconsidered) | Not needed for R1 MVP scope — internal use, single-user | 2026-03-15 |

## Open Questions

- [ ] None at this stage — briefing doc's 6 open questions (§12) will be addressed during Phase 1

## Session Log

| Date | What happened | Next steps |
|------|-------------|------------|
| 2026-03-15 | Gate 0 architecture classification completed. All 29 dependency items assessed (22 NEEDED, 7 DEFERRED). Five-Port interface contracts defined. | Phase 0: Theme Identification |
| 2026-03-15 | Phase 0 started. theme.md created with identity, process map, success criteria, frozen decisions. Competitive research launched for PDM evidence (8-10 competitors). | Populate PDM when research completes |
| 2026-03-15 | Phase 0 complete. PDM populated (33 L3 + 9 cross-cutting), FBS tree (~55 stories), capability map (10 capabilities), epic breakdown (6 epics, 16 weeks serial pipeline), D2 capability diagram rendered. Competitive feature matrix: 10 competitors, 21 TS / 9 DF / 3 IN / 5 EN. | Malcolm review of theme.md, then Phase 1 per-epic |

## Process Audit — Gate 0

### What Was Executed

| RE v4.23 Step | Executed? | Notes |
|---------------|:---------:|-------|
| Step 1: Architecture Classification Decision | Yes | All fields populated |
| Step 2: Hierarchy Placement | Yes | Full monorepo placement diagram |
| Step 3: Level-Specific Integration Checklist | Yes | L3 = all 3 sections apply |
| Step 4: Standard Dependency Checklist | Yes | 29 items assessed with status, temp solution, migration path |
| Step 5: Malcolm Reviews | Pending | Awaiting approval |

### Process Improvement Findings (PIFs)

| PIF | Finding | Severity | Action |
|-----|---------|----------|--------|
| PIF-001 | Dependency checklist was blank in RE v4.22 — had to be created from scratch during this run (now v4.23) | HIGH | Fixed — 25-item checklist now in RE v4.23 |
| PIF-002 | Level-specific integration checklists did not exist — had to be created during this run | HIGH | Fixed — L1-L5 checklists now in RE v4.23 |
| PIF-003 | Gate 0 section referenced in manager SOPs used outdated version (v4.16) | MEDIUM | Fixed — all manager SOPs updated to v4.23 |
