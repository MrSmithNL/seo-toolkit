# Deployment & Release — SEO Toolkit (PROD-001)

> How the SEO Toolkit is built, released, and deployed. Covers CI/CD, versioning, environments, and rollback.
>
> **Last updated:** 2026-03-14

---

## Deployment Type

The SEO Toolkit is a **CLI tool / library** — not a web application. Deployment means:
- Building the TypeScript source to distributable JavaScript
- Running `npm link` for local development use
- Publishing to npm for external distribution (future)

---

## CI/CD Pipeline

Every push to `main` triggers two pipelines:

### 1. Code Pipeline (`ci.yml`)

```
Push to main
    │
    ├─► Python matrix (3.11, 3.12)
    │     ├── Lint (Black + Ruff)
    │     ├── Type check (mypy)
    │     ├── Tests + coverage (pytest)
    │     └── Security audit (pip-audit)
    │
    └─► TypeScript (Node 20)
          ├── Type check (tsc --noEmit)
          ├── Tests + coverage (vitest)
          └── Security audit (pnpm audit)
```

### 2. Documentation Pipeline (`docs.yml`)

```
Push to main
    │
    ├── Install MkDocs Material + encryption plugin
    ├── Copy specs/ into docs/ (build-time)
    ├── Build static site (mkdocs build)
    └── Deploy to GitHub Pages
```

---

## Release Process

### Versioning
Semantic versioning (`vX.Y.Z`):
- **Patch** (0.0.X): Bug fixes, no API changes
- **Minor** (0.X.0): New features, backward compatible
- **Major** (X.0.0): Breaking changes

### Release Checklist
1. All CI gates green
2. Ship Gate Checklist completed ([current: E-001](specs/001-autonomous-content-engine/E-001-configuration/ship-gate-checklist.md))
3. Release notes written
4. Version bumped in `package.json`
5. CHANGELOG.md updated
6. UAT approved by Malcolm
7. Tag and publish

### Current Release
- **Version:** v0.1.0 (E-001 Configuration & Setup)
- **Release Notes:** [v0.1.0 Release Notes](specs/001-autonomous-content-engine/E-001-configuration/release-notes-v0.1.0.md)
- **Deployment Report:** [Deployment Report](specs/001-autonomous-content-engine/E-001-configuration/deployment-report.md)
- **Ship Gate:** [Ship Gate Checklist](specs/001-autonomous-content-engine/E-001-configuration/ship-gate-checklist.md)

---

## Environments

| Environment | Purpose | Access |
|-------------|---------|--------|
| **Development** | Local dev machine | `pnpm install && pnpm build` |
| **CI** | GitHub Actions runners | Automatic on push/PR |
| **Staging** | Local `npm link` install | `npm link` from built output |
| **Production** | npm registry (future) | `npm publish` |

---

## Build Commands

```bash
# Install dependencies
pnpm install

# Build TypeScript
pnpm build

# Run all tests
pnpm test

# Run tests with coverage report
pnpm test:coverage

# Type check without building
pnpm typecheck

# Generate database types
pnpm db:generate

# Link for local use
npm link
```

---

## Rollback

Since this is a CLI/library (not a deployed service):
- **Git revert:** `git revert <commit>` for code rollbacks
- **npm unpublish:** Remove bad version (within 72h of publish)
- **Feature flags:** `content-engine-v1` flag in `src/lib/feature-flags.ts` — set to `false` to disable

---

## Feature Flags

| Flag | Controls | Default |
|------|----------|---------|
| `content-engine-v1` | Entire E-001 Configuration module | `true` |

Kill switch: Set flag to `false` and rebuild — no redeployment needed.

---

## Monitoring

Post-deployment monitoring for a CLI tool:
- **CI dashboard:** GitHub Actions tab shows pipeline health
- **Mutation metrics:** Auto-tracked weekly → [Mutation Metrics](mutation-metrics.md)
- **Tech debt metrics:** Auto-tracked weekly → tracked in `docs/debt-metrics.md`
- **Error reports:** Users report via GitHub Issues
