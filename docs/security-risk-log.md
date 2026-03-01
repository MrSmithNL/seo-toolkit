# SEO Toolkit — Security Risk Log

Last updated: 2026-03-01

---

## Active Risks

### RISK-001: API Keys Must Never Be Committed to Git

**Severity:** Critical
**Category:** Credential exposure
**Description:** DataForSEO, SE Ranking, and Google credentials are stored in `.env` for local use. If `.env` is ever committed to git, these credentials would be publicly exposed on GitHub.
**Current mitigations:**
- `.env` is listed in `.gitignore`
- `.env.example` contains only placeholder values (no real keys)
- All master copies stored in Bitwarden
- Claude Code is instructed (in CLAUDE.md) to never write credentials to tracked files
**Residual risk:** Low — `.gitignore` is in place and tested. Risk is accidental force-add or new `.env.*` variants.
**Action if breached:** Immediately rotate all exposed keys. DataForSEO: regenerate password. SE Ranking: regenerate API key. Google: revoke OAuth tokens and re-authorise.

---

### RISK-002: Client Data Is Sensitive Business Intelligence

**Severity:** Medium
**Category:** Data privacy
**Description:** The toolkit collects and stores keyword rankings, traffic data, backlink profiles, and competitor intelligence for each client. For Love Over Exile, this includes search performance data that reveals content strategy. For future external clients, this data is confidential business intelligence.
**Current mitigations:**
- Data stored locally in `reports/` and `cache/` directories (both gitignored)
- No client data is committed to the repository
- Multi-client architecture isolates data by client config
**Residual risk:** Medium — no encryption at rest for cached data. No access controls between client datasets on the same machine.
**Future mitigation (when productised):**
- Encrypted storage for client data
- Strict tenant isolation (each client's data in separate directory with access controls)
- Data retention policy — auto-delete data older than X months
- Client consent for data collection

---

### RISK-003: Link Builder Outreach Could Be Seen as Spam

**Severity:** Medium
**Category:** Reputation / compliance
**Description:** The Link Builder Agent researches backlink opportunities and can draft outreach emails. If used carelessly, mass outreach could be seen as spam by recipients and by Google, potentially leading to manual penalties.
**Current mitigations:**
- DEC-006 establishes the Link Builder as an "earned link engine" — not an automated posting bot
- All outreach requires human approval before sending (Malcolm reviews every pitch)
- Agent focuses on prospect research and pitch drafting, not automated sending
- Never buys links, never uses PBNs, never auto-publishes to external sites
**Residual risk:** Low — human approval gate prevents automated spam. Risk is Malcolm approving too many low-quality pitches.
**Additional safeguards to implement:**
- Rate limit: maximum 10 outreach pitches per week per client
- Quality threshold: minimum domain authority score for prospects
- Template review: pitches must be genuinely personalised, not templated mass emails

---

### RISK-004: Rate Limiting and API Cost Overruns

**Severity:** Low
**Category:** Operational / financial
**Description:** DataForSEO charges per API call. Bugs in agent code (infinite loops, duplicate requests, missing pagination limits) could burn through the prepaid balance quickly.
**Current mitigations:**
- DataForSEO uses prepaid balance — no surprise invoices, service stops when balance is zero
- CLAUDE.md requires confirmation before spending more than $1 on API calls
**Future mitigation:**
- Per-agent daily API call limits in config
- Cost tracking per request with running total
- Alert when balance drops below $10

---

### RISK-005: Google Search Console OAuth Token Scope

**Severity:** Low
**Category:** Credential scope
**Description:** When connecting Google Search Console (via Rube MCP or service account), the OAuth scope should be read-only. Write access to GSC is not needed and would be a risk.
**Current mitigations:**
- Not yet connected (pending SEO-002)
**Required mitigation when connecting:**
- Request read-only scope (`https://www.googleapis.com/auth/webmasters.readonly`)
- Do not request write or admin scopes
- Document the exact scopes granted

---

## Credential Storage Policy

| Rule | Detail |
|------|--------|
| Where credentials live | Bitwarden (master copy) and `.env` (working copy) |
| Where credentials never go | Git commits, plain text files, log files, report outputs |
| How to add a new credential | Add to Bitwarden first, then to `.env`, then document in `docs/accounts-and-access.md` |
| How to rotate a credential | Update Bitwarden, update `.env`, verify agents still work |
| Who has access | Malcolm (owner of all accounts), Claude Code (read via `.env` and `bw` CLI) |

---

## Incident Response

If a credential is exposed:

1. **Rotate immediately** — change the password/key on the service's website
2. **Update Bitwarden** — store the new credential
3. **Update `.env`** — replace the old value locally
4. **Check git history** — if the credential was committed, the repo may need to be cleaned with `git filter-branch` or BFG Repo-Cleaner
5. **Log the incident** — add an entry to this file with date, what happened, and resolution

---

## Change Log

| Date | Change |
|------|--------|
| 2026-03-01 | Security risk log created. Five initial risks documented. Credential policy established. |
