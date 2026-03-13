# Tests — F-001 Site URL Registration & Crawl Config

> Acceptance test scenarios derived from requirements.md per RE v4.15 Phase 3 step 13.
> These are human-authored specifications — the building agent implements them as executable tests.

---

## Acceptance Tests (GIVEN/WHEN/THEN)

### AT-001: Register a valid URL (US-001 happy path)

```
GIVEN the system has no site registered for "hairgenetix.com"
WHEN the user enters "hairgenetix.com"
THEN the URL is normalised to "https://www.hairgenetix.com"
AND a SiteConfig record is created with status "crawling"
AND an automatic crawl is initiated
```

### AT-002: Register URL with scheme (US-001 variant)

```
GIVEN the system has no site registered for "digitalbouwers.nl"
WHEN the user enters "https://digitalbouwers.nl"
THEN the URL is stored as "https://digitalbouwers.nl"
AND a SiteConfig record is created
```

### AT-003: Reject invalid URL (US-001 error case)

```
GIVEN any system state
WHEN the user enters "not a url!!!"
THEN the system returns error "Invalid URL format. Enter a domain like example.com"
AND no SiteConfig record is created
```

### AT-004: Reject unreachable URL (US-001 error case)

```
GIVEN a URL that does not resolve in DNS
WHEN the user enters "https://thisdomaindoesnotexist12345.com"
THEN the system returns error "Could not reach this URL. Check the domain is correct and the site is live."
AND no SiteConfig record is created
```

### AT-005: Handle duplicate registration (US-001 edge case)

```
GIVEN "hairgenetix.com" is already registered
WHEN the user enters "hairgenetix.com"
THEN the system informs "This site is already registered"
AND offers options to update existing config or create new
```

### AT-006: Detect WordPress CMS (US-002 happy path)

```
GIVEN a site is registered with URL "https://digitalbouwers.nl"
WHEN the system crawls the site
AND GET /wp-json/wp/v2/ returns HTTP 200
THEN cms_type is set to "wordpress"
```

### AT-007: Detect Shopify CMS (US-002 happy path)

```
GIVEN a site is registered with URL "https://www.hairgenetix.com"
WHEN the system crawls the site
AND the HTML source contains "cdn.shopify.com"
THEN cms_type is set to "shopify"
```

### AT-008: Unknown CMS (US-002 edge case)

```
GIVEN a site is registered with URL "https://static-site.example.com"
WHEN the system crawls the site
AND no WordPress or Shopify indicators are found
THEN cms_type is set to "unknown"
AND the user is informed "CMS type could not be detected"
```

### AT-009: Detect multi-language Shopify site (US-003 happy path)

```
GIVEN a site is registered with URL "https://www.hairgenetix.com"
WHEN the system crawls the site
AND Shopify locale URLs are detected (en, nl, de, fr, es, it, pt, sv, da)
THEN languages array contains 9 entries with BCP-47 codes
AND primary_language is set to "en"
```

### AT-010: Single-language WordPress site (US-003 variant)

```
GIVEN a site is registered with URL "https://digitalbouwers.nl"
WHEN the system crawls the site
AND html lang="nl" is found
AND no hreflang tags are present
THEN languages array contains 1 entry: {code: "nl", name: "Dutch"}
AND primary_language is set to "nl"
```

### AT-011: Parse sitemap for content count (US-004 happy path)

```
GIVEN a site is registered and crawled
WHEN the system fetches /sitemap.xml
AND the sitemap contains 45 URL entries
THEN content_count is set to 45
```

### AT-012: Handle missing sitemap (US-004 edge case)

```
GIVEN a site is registered and crawled
WHEN the system fetches /sitemap.xml
AND the response is 404
THEN content_count is set to 0
AND a note is stored: "No sitemap found — content inventory unavailable"
```

---

## Integration Tests

### IT-001: End-to-end site registration (cross-component)

```
GIVEN a clean database with no sites
WHEN the user registers "hairgenetix.com"
THEN a SiteConfig record exists in the database
AND cms_type is "shopify"
AND languages contains at least "en" and "nl"
AND content_count is > 0
AND last_crawled is within the last 60 seconds
```

### IT-002: Crawl timeout handling

```
GIVEN a site URL that takes > 30 seconds to respond
WHEN the system attempts to crawl
THEN the crawl is aborted after 30 seconds
AND partial results are stored (URL registered, cms_type may be "unknown")
AND an error is logged: "Crawl timed out after 30s"
```

### IT-003: Crawl retry on transient failure

```
GIVEN a site URL that returns 503 on first attempt
WHEN the system crawls the site
THEN the system retries once after 5 seconds
AND if the retry succeeds, normal results are stored
AND if the retry fails, partial results with error note are stored
```

---

## Property Invariants

| Property | Description | Test Type |
|----------|------------|-----------|
| URL normalisation is idempotent | Normalising an already-normalised URL produces the same result | Property-based |
| cms_type is always one of: wordpress, shopify, unknown | No other values allowed | Unit |
| language codes are valid BCP-47 | All codes in languages array match BCP-47 pattern | Property-based |
| content_count is always ≥ 0 | Never negative | Unit |
| SiteConfig always has a primary_language | Never null after successful crawl | Unit |

---

## Hallucination Risk Scenarios

| Risk | Scenario | Mitigation |
|------|---------|-----------|
| Agent might hardcode CMS detection for known test sites | Test with unknown sites too | Include AT-008 (unknown CMS) in test suite |
| Agent might skip URL normalisation edge cases | Trailing slashes, www/non-www, HTTP/HTTPS | Include property-based test for normalisation |
| Agent might not handle sitemap index (nested sitemaps) | Only test with simple sitemaps | Include IT with sitemap_index.xml fixture |

---

## Test Layer Classification

| Test ID | Layer | Automated? |
|---------|-------|:----------:|
| AT-001 to AT-005 | Acceptance | Yes |
| AT-006 to AT-008 | Acceptance | Yes |
| AT-009 to AT-010 | Acceptance | Yes |
| AT-011 to AT-012 | Acceptance | Yes |
| IT-001 | Integration | Yes |
| IT-002 to IT-003 | Integration | Yes |
| Property invariants | Property-based | Yes |
