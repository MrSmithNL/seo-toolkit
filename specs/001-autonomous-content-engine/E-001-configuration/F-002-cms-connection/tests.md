# Tests — F-002 CMS Connection Setup

> Acceptance test scenarios derived from requirements.md per RE v4.15 Phase 3 step 13.
> These are human-authored specifications — the building agent implements them as executable tests.

---

## Acceptance Tests (GIVEN/WHEN/THEN)

### AT-001: Connect WordPress with valid credentials (US-001 happy path)

```
GIVEN a site registered with cms_type "wordpress" and URL "https://digitalbouwers.nl"
WHEN the user provides username "admin" and a valid application password
THEN GET /wp-json/wp/v2/users/me returns 200
AND credentials are stored encrypted (AES-256)
AND connection status is set to "verified"
```

### AT-002: Reject invalid WordPress credentials (US-001 error case)

```
GIVEN a site registered with cms_type "wordpress"
WHEN the user provides an invalid application password
THEN GET /wp-json/wp/v2/users/me returns 401
AND the system returns error "WordPress credentials are invalid. Check your username and application password."
AND no credentials are stored
```

### AT-003: Reject WordPress site without REST API (US-001 error case)

```
GIVEN a WordPress site with REST API disabled
WHEN the user provides credentials
THEN GET /wp-json/wp/v2/ returns 404 or connection refused
AND the system returns error "WordPress REST API is not available on this site."
AND no credentials are stored
```

### AT-004: Connect Shopify with valid token (US-002 happy path)

```
GIVEN a site registered with cms_type "shopify" and store domain "a24be5-c5.myshopify.com"
WHEN the user provides a valid access token with read_content and write_content scopes
THEN the GraphQL Admin API query succeeds
AND the token is stored encrypted (AES-256)
AND connection status is set to "verified"
```

### AT-005: Reject Shopify token with missing scopes (US-002 error case)

```
GIVEN a site registered with cms_type "shopify"
WHEN the user provides a token missing write_content scope
THEN the system returns error "Token is missing required scopes: write_content."
AND no token is stored
```

### AT-006: Reject invalid Shopify token (US-002 error case)

```
GIVEN a site registered with cms_type "shopify"
WHEN the user provides an invalid access token
THEN the GraphQL Admin API returns 401
AND the system returns error "Shopify access token is invalid."
AND no token is stored
```

### AT-007: WordPress test publish succeeds (US-003 happy path)

```
GIVEN a verified WordPress connection
WHEN the system performs a test publish
THEN a draft post with title "[SEO Toolkit] Connection Test" is created
AND the draft is immediately deleted
AND the system confirms "Write access verified — your CMS connection is working"
```

### AT-008: Shopify test publish succeeds (US-003 happy path)

```
GIVEN a verified Shopify connection
WHEN the system performs a test publish
THEN a draft article is created via createArticle mutation
AND the article is immediately deleted
AND the system confirms "Write access verified — your CMS connection is working"
```

### AT-009: Test publish fails — no write permission (US-003 error case)

```
GIVEN a WordPress connection where credentials have read-only access
WHEN the system performs a test publish
THEN POST /wp-json/wp/v2/posts returns 403
AND the system reports "Cannot create posts. Check Application Password has 'Editor' or 'Author' role."
AND connection status is set to "failed"
```

### AT-010: Default publish status is draft (US-004 happy path)

```
GIVEN a new CMS connection with no publish mode set
WHEN the system creates an article
THEN the article is created with draft/unpublished status
```

### AT-011: Publish mode set to published (US-004 variant)

```
GIVEN a CMS connection with publish mode set to "published"
WHEN configuring this setting
THEN the system warns "Articles will be published immediately without review"
AND when articles are created, they have published/active status
```

---

## Integration Tests

### IT-001: End-to-end WordPress connection

```
GIVEN a clean database with a registered WordPress site
WHEN the user provides valid WordPress credentials
THEN a CMSConnection record exists with status "verified"
AND credentials are AES-256 encrypted in storage
AND a test publish was performed and cleaned up
AND a structured log entry was created (no credentials in log)
```

### IT-002: End-to-end Shopify connection

```
GIVEN a clean database with a registered Shopify site
WHEN the user provides a valid Shopify access token
THEN a CMSConnection record exists with status "verified"
AND the token is AES-256 encrypted in storage
AND a test publish was performed and cleaned up
AND a structured log entry was created (no token in log)
```

### IT-003: Credential security verification

```
GIVEN stored CMS credentials (WordPress or Shopify)
WHEN the credential storage is inspected directly (bypassing the application)
THEN no plaintext credentials are found
AND no credentials appear in any log file
AND no credentials appear in any error message
```

### IT-004: Connection retry on transient failure

```
GIVEN a CMS API that returns 503 on first attempt
WHEN the system attempts to verify credentials
THEN the system retries once after 5 seconds
AND if the retry succeeds, connection status is "verified"
AND if the retry fails, a clear error is reported
```

---

## Property Invariants

| Property | Description | Test Type |
|----------|-----------|-----------|
| Credentials never in plaintext | No credential value appears unencrypted in storage, logs, or error output | Security scan |
| connection status is always one of: pending, verified, failed, revoked | No other values allowed | Unit |
| cms_type matches site's detected CMS | CMSConnection.cms_type must match SiteConfig.cms_type | Unit |
| default_publish_status is always one of: draft, published | No other values allowed | Unit |
| AES-256 encrypted values are reversible only with correct key | Decrypt with wrong key produces error, not wrong data | Unit |

---

## Hallucination Risk Scenarios

| Risk | Scenario | Mitigation |
|------|---------|------------|
| Agent might hardcode test credentials | Test only works with specific tokens | Use mock HTTP servers that validate request format, not specific credentials |
| Agent might skip encryption and store plaintext | Credentials stored as-is in JSON/SQLite | IT-003 explicitly scans storage for plaintext patterns |
| Agent might not actually delete test publish | Draft articles accumulate on CMS | AT-007/AT-008 verify deletion; IT-001/IT-002 check CMS state after test |
| Agent might log credentials in error messages | Tokens visible in log output | Property invariant: grep all log output for credential patterns |

---

## Test Layer Classification

| Test ID | Layer | Automated? |
|---------|-------|:----------:|
| AT-001 to AT-003 | Acceptance (WordPress) | Yes |
| AT-004 to AT-006 | Acceptance (Shopify) | Yes |
| AT-007 to AT-009 | Acceptance (Test Publish) | Yes |
| AT-010 to AT-011 | Acceptance (Publish Mode) | Yes |
| IT-001 to IT-004 | Integration | Yes |
| Property invariants | Security / Unit | Yes |
