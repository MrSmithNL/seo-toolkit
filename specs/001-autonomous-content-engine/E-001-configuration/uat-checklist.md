# UAT Checklist — E-001 Configuration & Setup v0.1.0

**Spec:** specs/001-autonomous-content-engine/E-001-configuration/
**Product:** PROD-001 SEO Toolkit — Content Engine Configuration Module
**Submitted by:** Claude (interactive session)
**Date:** 2026-03-14
**UAT Type:** CLI tool (no web UI)

---

## How to Install and Test

### Step 1: Install
```bash
cd ~/Claude\ Code/Projects/seo-toolkit
pnpm install
pnpm build
```

### Step 2: Run the Tests (verify everything passes)
```bash
pnpm test
```
Expected: **255 tests passing, 0 failures**

### Step 3: Try Individual Features
Each feature below has a test you can run independently.

---

## Feature Tests

### F1: Site Registration
**What it does:** Registers a website URL, validates it, and stores the site configuration.

**Test command:**
```bash
pnpm vitest run src/modules/content-engine/config/site-registration/__tests__/site.service.test.ts
```

**What to check:**
- [ ] Tests pass — site can be registered with a valid URL
- [ ] Tests pass — duplicate URLs are rejected
- [ ] Tests pass — invalid URLs are rejected
- [ ] Tests pass — site can be retrieved by ID

### F2: CMS Detection (WordPress + Shopify)
**What it does:** Automatically detects whether a website runs WordPress or Shopify.

**Test command:**
```bash
pnpm vitest run src/modules/content-engine/config/site-registration/__tests__/detectors.test.ts
```

**What to check:**
- [ ] Tests pass — WordPress detected via wp-json endpoint
- [ ] Tests pass — WordPress detected via wp-login.php fallback
- [ ] Tests pass — Shopify detected via cdn.shopify.com
- [ ] Tests pass — Shopify detected via Shopify.theme script
- [ ] Tests pass — Returns "unknown" for non-CMS sites
- [ ] Tests pass — Shopify password pages don't false-positive as WordPress (bug fix)
- [ ] Tests pass — Network errors handled gracefully (no crashes)

### F3: CMS Connection
**What it does:** Stores API credentials for connecting to WordPress/Shopify CMS.

**Test command:**
```bash
pnpm vitest run src/modules/content-engine/config/cms-connection/__tests__/cms.service.test.ts
```

**What to check:**
- [ ] Tests pass — CMS connection can be created with API key
- [ ] Tests pass — API keys are encrypted before storage
- [ ] Tests pass — Connection can be tested (validates credentials)
- [ ] Tests pass — Connection can be revoked

### F4: Brand Voice Profile
**What it does:** Stores brand voice settings (tone, style, keywords) for content generation.

**Test command:**
```bash
pnpm vitest run src/modules/content-engine/config/brand-voice/__tests__/voice.service.test.ts
```

**What to check:**
- [ ] Tests pass — Voice profile can be created
- [ ] Tests pass — Multiple voice profiles supported per site
- [ ] Tests pass — Voice profile can be updated

### F5: Topic Configuration
**What it does:** Defines content topics and scheduling rules.

**Test command:**
```bash
pnpm vitest run src/modules/content-engine/config/topic-config/__tests__/topic.service.test.ts
```

**What to check:**
- [ ] Tests pass — Topics can be created with keywords
- [ ] Tests pass — Schedule can be set (daily/weekly/monthly)
- [ ] Tests pass — Topics can be paused and resumed

### F6: Quality Thresholds
**What it does:** Sets minimum quality standards for generated content.

**Test command:**
```bash
pnpm vitest run src/modules/content-engine/config/quality-thresholds/__tests__/quality.service.test.ts
```

**What to check:**
- [ ] Tests pass — Thresholds can be configured (min word count, max AI score, etc.)
- [ ] Tests pass — Default thresholds are applied when not specified
- [ ] Tests pass — Threshold validation rejects invalid values

---

## Cross-Cutting Checks

### Infrastructure
```bash
# Run all tests
pnpm test

# Check TypeScript compiles clean
pnpm typecheck
```

- [ ] All 255 tests pass
- [ ] TypeScript typecheck passes with zero errors
- [ ] No test files have `.skip()` or `.only()`

### Feature Flag
- [ ] Feature flag `content-engine-v1` is set to `true` (check `src/lib/feature-flags.ts`)

### Database Schema
```bash
pnpm vitest run src/db/schema.test.ts
```
- [ ] Schema tests pass — all tables have tenant_id
- [ ] Schema tests pass — all IDs use correct prefixes (ste_, cms_, vce_, tpc_)

### Smoke Tests (Real Sites)
```bash
# These test against live websites — run manually if network available
pnpm vitest run tests/smoke/real-site-detection.test.ts
```
- [ ] Hairgenetix.com detected as Shopify
- [ ] Skingenetix.com detected as Shopify

---

## Exploratory Testing (Optional but Encouraged)

- [ ] Try registering the same URL twice — does it give a clear error?
- [ ] Try an invalid URL (no protocol, bad domain) — does it reject gracefully?
- [ ] Check error messages — are they clear and helpful?

---

## Result

- [ ] **APPROVED** — proceed to complete Ship phase
- [ ] **REJECTED** — feedback: _______________

**Malcolm's signature:** _________________ **Date:** _____________
