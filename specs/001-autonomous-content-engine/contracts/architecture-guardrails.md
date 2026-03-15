# Architecture Guardrails — Autonomous Content Engine

> Constraints that apply across all epics. Violations require a change request against frozen decisions.

## Dependency Direction (ENFORCED)

- Modules depend on `packages/` only, never reverse
- No cross-module direct imports — use event bus
- CLI adapter depends on module internals; web adapter depends on API layer

## Five-Port Pattern (ENFORCED)

Every module operation uses exactly these 5 adapter interfaces:

| Port | Purpose | Standalone Adapter | Platform Adapter |
|------|---------|-------------------|-----------------|
| Database | Persistence | SQLite/JSON file | PostgreSQL via `packages/db` |
| Auth | Identity + tenant context | Config file | JWT + RLS via `packages/auth` |
| AIGateway | LLM calls | Direct API (Claude/GPT) | `packages/ai-gateway` with routing |
| FeatureFlags | Feature toggles | Environment variables | `packages/feature-flags` |
| Notifications | Alerts + status | Console output / Pushover | `packages/notifications` |

## Multi-Tenancy

- Every data model includes `tenant_id` column
- RLS enabled on all tenant-scoped tables
- Standalone mode uses config-file tenant context (single tenant)
- Platform mode uses JWT-derived tenant context

## Rate Limits & Cost Controls

- Google Autocomplete: max 100 requests/day, 2-second delay between requests
- Keywords Everywhere API: max 100 keywords per batch, 1 request/second
- DataForSEO: follow published rate limits (12 req/min for live endpoints)
- LLM calls: budget cap of $50/month total across all pipeline stages
- All external API calls logged with cost tracking

## Content Safety (YMYL)

- Health/medical content flagged for human review before publish
- No medical claims without source citations
- YMYL classification checked on every ContentBrief
