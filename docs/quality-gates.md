# Quality Gates — SEO Toolkit (PROD-001)

> The CI/CD pipeline enforces 9 quality gate layers. This page documents what each gate checks, where it's configured, and what happens when it fails.
>
> **Last updated:** 2026-03-14

---

## Pipeline Overview

```
Push to main / PR opened
        │
        ▼
┌─────────────────────────────┐
│  ci.yml — Core Pipeline     │
│  ├── Python lint + type     │
│  ├── Python tests + cov     │
│  ├── TS type check          │
│  ├── TS tests + cov         │
│  └── Security audit         │
└─────────────┬───────────────┘
              │ (PRs only)
              ▼
┌─────────────────────────────┐
│  code-review.yml — PR Gates │
│  ├── Extended linting       │
│  ├── Complexity check       │
│  ├── Maintainability index  │
│  ├── Coverage gate (80%)    │
│  ├── AI anti-patterns (8)   │
│  ├── Secret scanning        │
│  ├── Mutation spot check    │
│  └── Duplication check      │
└─────────────┬───────────────┘
              │ (weekly)
              ▼
┌─────────────────────────────┐
│  Scheduled Workflows        │
│  ├── mutation-testing.yml   │
│  ├── debt-metrics.yml       │
│  └── codeql.yml (SAST)      │
└─────────────────────────────┘
```

---

## Gate Details

### Layer 1: Static Analysis

| Check | Tool | Config | Enforcement |
|-------|------|--------|-------------|
| Python formatting | Black 24.3.0 | `pyproject.toml` | Hard block |
| Python linting | Ruff v0.3.0 | `pyproject.toml` (18 rule categories) | Hard block |
| Python types | mypy | `pyproject.toml` | Hard block |
| TypeScript types | `tsc --noEmit` | `tsconfig.json` (strict mode) | Hard block |

### Layer 2: Unit Tests + Coverage

| Language | Runner | Threshold | Config |
|----------|--------|-----------|--------|
| TypeScript | Vitest | 85% statements, branches, functions, lines | `vitest.config.ts` |
| Python | pytest | 80% | `pyproject.toml` |

### Layer 3: Contract Tests
N/A for v0.1.0 — no external API endpoints yet. Will be added when REST API is exposed.

### Layer 4: Integration Tests
- Tenant isolation tests (`tests/integration/tenant-isolation.test.ts`)
- Event logging tests (`tests/integration/event-logging.test.ts`)
- Cross-module boundary tests

### Layer 5-7: Visual / Performance / Accessibility
N/A — CLI product with no UI.

### Layer 8: Security

| Check | Tool | Enforcement |
|-------|------|-------------|
| Python vulnerabilities | pip-audit | Hard block |
| Node vulnerabilities | pnpm audit | Warning (non-blocking) |
| Secret scanning | gitleaks v8.21.2 | Hard block (pre-commit + PR) |
| SAST analysis | CodeQL (Python) | Hard block |
| Private key detection | pre-commit hook | Hard block |

### Layer 9: Code Review
- Self-review checklist (automated via `code-review.yml`)
- Malcolm reviews production-bound changes

---

## AI Anti-Pattern Detection (8 Checks)

These run on every PR via `code-review.yml`:

| # | Check | Threshold | Action |
|---|-------|-----------|--------|
| 1 | Comment ratio | > 30% of file | Warning |
| 2 | Bare except clauses | > 3 in codebase | Warning |
| 3 | God functions | Radon complexity C or higher | Warning |
| 4 | Unused imports | Any F401 violations | Warning |
| 5 | TODO/FIXME/HACK | > 10 across codebase | Warning |
| 6 | Assertion density | < 1.5 assertions per test | **Hard fail** |
| 7 | Boundary test coverage | Missing edge-case tests | **Hard fail** |
| 8 | Security rule suppression | Any `noqa` on S### rules | **Hard fail** |

---

## Scheduled Quality Checks

| Workflow | Schedule | What It Does |
|----------|----------|-------------|
| `mutation-testing.yml` | Wed 03:00 UTC | mutmut on `scripts/shared/`, logs to [Mutation Metrics](mutation-metrics.md) |
| `debt-metrics.yml` | Mon 05:00 UTC | Complexity, duplication, dead code, open debt issues |
| `codeql.yml` | Every push + PR | GitHub CodeQL security analysis (Python) |
| `dependabot.yml` | Daily | Dependency version updates |

---

## Pre-Commit Hooks

Run locally before every commit:

| Hook | What It Does |
|------|-------------|
| Black | Python formatting |
| Ruff | Python linting (with auto-fix) |
| check-yaml | YAML syntax validation |
| check-added-large-files | Block accidental large file commits |
| detect-private-key | Block credential commits |
| gitleaks | Secret scanning |
| mypy | Python type checking |
| pytest (pre-push) | Run all Python tests before push |

---

## Workflow Files

All workflows are in `.github/workflows/`:

| File | Trigger | Purpose |
|------|---------|---------|
| `ci.yml` | Push to main, PRs | Core CI pipeline |
| `code-review.yml` | PRs only | Extended quality checks |
| `mutation-testing.yml` | Weekly (Wed) | Mutation testing + metrics |
| `debt-metrics.yml` | Weekly (Mon) | Tech debt tracking |
| `codeql.yml` | Push + PRs | Security analysis |
| `docs.yml` | Push to main | Documentation deployment |
