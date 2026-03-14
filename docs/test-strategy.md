# Test Strategy — SEO Toolkit (PROD-001)

> How we test the SEO Toolkit. Covers the testing pyramid, tools, thresholds, and processes.
>
> **Last updated:** 2026-03-14

---

## Testing Philosophy

All code follows **TDD (Test-Driven Development)** — tests are written before implementation. AI-generated code is treated as a first draft and gets the same quality gates as human-written code.

**Principle:** No code is committed without passing tests. No test is deleted or weakened. Max 5 fix attempts before escalating to human review.

---

## Test Pyramid

```
        ╱ E2E / Smoke ╲           ~5%    (real sites, network)
       ╱  Integration   ╲        ~15%    (cross-module, tenant isolation)
      ╱  Conformance     ╲       ~10%    (YAML spec compliance)
     ╱    Unit Tests      ╲      ~70%    (services, utils, validators)
    ╱______________________╲
```

| Layer | Count | Tools | Threshold |
|-------|-------|-------|-----------|
| **Unit** | ~220 | Vitest (TypeScript), pytest (Python) | 85% coverage (TS), 80% coverage (Python) |
| **Conformance** | 6 suites | Custom YAML runner (`tests/conformance/`) | All specs pass |
| **Integration** | ~20 | Vitest | Tenant isolation verified |
| **Smoke / E2E** | ~10 | Vitest (real HTTP) | Live site detection works |

---

## Test Tools

| Tool | Purpose | Config |
|------|---------|--------|
| **Vitest** | TypeScript unit + integration tests | `vitest.config.ts` — 85% coverage threshold |
| **pytest** | Python script tests | `pyproject.toml` — 80% coverage threshold |
| **mutmut** | Mutation testing (weekly) | `pyproject.toml` — 60% kill threshold, 75% warning |
| **jscpd** | Code duplication detection | 5% threshold, 10-line minimum |
| **radon** | Cyclomatic complexity + maintainability | D/E/F grades = fail, C = warn |

---

## Quality Gate Layers

Nine layers enforced in CI — see [Quality Gates](quality-gates.md) for full details.

| # | Gate | Enforcement |
|---|------|-------------|
| 1 | Static analysis (TypeScript strict, Ruff, Black) | **Hard block** |
| 2 | Unit tests + coverage | **Hard block** (85% TS / 80% Python) |
| 3 | Contract tests | If API endpoints exist |
| 4 | Integration tests | **Hard block** |
| 5 | Visual regression | N/A (CLI product) |
| 6 | Performance regression | Benchmarks on changed paths |
| 7 | Accessibility | N/A (CLI product) |
| 8 | Security (CodeQL, pip-audit, gitleaks) | **Hard block** |
| 9 | Code review (self-review + Malcolm for production) | **Hard block** |

---

## AI-Specific Quality Checks

Eight anti-pattern detections run on every PR (see [Quality Gates](quality-gates.md)):

1. Comment ratio > 30% → warning
2. Bare except clauses > 3 → warning
3. God functions (radon C+) → warning
4. Unused imports (F401) → warning
5. TODO/FIXME/HACK > 10 → warning
6. **Assertion density < 1.5/test → HARD FAIL**
7. **Boundary test coverage missing → HARD FAIL**
8. **Security rule suppression → HARD FAIL**

---

## Mutation Testing

Runs weekly (Wednesday 03:00 UTC) via GitHub Actions. Targets `scripts/shared/`.

- **Threshold:** 60% mutation kill rate (hard fail), 75% (warning)
- **Results:** Auto-logged to [Mutation Metrics](mutation-metrics.md)
- **Tool:** mutmut

---

## Test Data Strategy

- **Unit tests:** In-memory fixtures, factory functions, no real databases
- **Conformance tests:** YAML fixture files per feature (`tests/conformance/*.yaml`)
- **Integration tests:** Test tenant IDs (`tnt_test_*`), in-memory SQLite
- **Smoke tests:** Real HTTP requests to live sites (hairgenetix.com, skingenetix.com)
- **Deterministic keys:** All test IDs use `ste_test_`, `cms_test_`, `vce_test_`, `tpc_test_` prefixes

---

## UAT Process

User Acceptance Testing is a **hard block** — the product cannot ship without Malcolm's explicit sign-off.

1. Claude creates the [UAT Checklist](specs/001-autonomous-content-engine/E-001-configuration/uat-checklist.md) from spec acceptance criteria
2. Testing instructions provided with install steps and expected output
3. Malcolm runs the checklist and marks pass/fail
4. Malcolm signs off (or provides feedback for fixes)

See the [UAT Guide](uat-guide.md) for step-by-step instructions.
