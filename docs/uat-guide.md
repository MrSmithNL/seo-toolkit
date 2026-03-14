# User Acceptance Testing (UAT) Guide

> **For Malcolm** — This page explains how UAT works and links to the current checklist.

---

\!\!\! tip "Interactive UAT Wizard"
    **[Launch the UAT Wizard](uat-wizard.html){target=_blank}** — a guided, step-by-step testing experience. It shows you one test at a time, explains what to check in plain English, and lets you mark Pass/Fail with comments. Your progress is saved automatically.

---

## What is UAT?

UAT is the final check before a feature ships. You (Malcolm) verify that what was built actually does what was specified. The same AI that builds the code cannot be the sole judge of whether it's correct — that's why your sign-off is a **hard block**.

---

## Current UAT

### E-001: Configuration & Setup (v0.1.0)

**Status:** Awaiting your approval

| Document | What's in it |
|----------|-------------|
| **[UAT Wizard (Recommended)](uat-wizard.html){target=_blank}** | Interactive step-by-step guide — the easiest way to do UAT |
| **[UAT Checklist](specs/001-autonomous-content-engine/E-001-configuration/uat-checklist.md)** | Step-by-step test scenarios with pass/fail checkboxes |
| [Release Notes](specs/001-autonomous-content-engine/E-001-configuration/release-notes-v0.1.0.md) | What was built, known limitations |
| [Ship Gate Checklist](specs/001-autonomous-content-engine/E-001-configuration/ship-gate-checklist.md) | Full readiness checklist (CI, deployment, monitoring) |

---

## How to Run UAT

### Step 1: Install
```bash
cd ~/Claude\ Code/Projects/seo-toolkit
pnpm install
pnpm build
```

### Step 2: Run All Tests
```bash
pnpm test
```
**Expected:** 255 tests passing, 0 failures.

### Step 3: Work Through the Checklist
Open the [UAT Checklist](specs/001-autonomous-content-engine/E-001-configuration/uat-checklist.md) and follow each scenario. Each feature has:
- A test command you can run
- Checkboxes for what to verify
- Expected results described in plain English

### Step 4: Sign Off
At the bottom of the checklist, mark either:
- **APPROVED** — the feature ships
- **REJECTED** — with your feedback on what needs fixing

---

## Severity Guide

If you find issues, classify them:

| Severity | What it means | Example |
|----------|--------------|---------|
| **Blocker** | Core functionality broken — cannot ship | Tests fail, data lost, crashes |
| **Major** | Works but wrong behaviour | Wrong detection, incorrect validation |
| **Minor** | Works correctly but rough edges | Unclear error message, missing edge case |

---

## Questions?

If anything is unclear during UAT, just ask in the next Claude Code session. UAT is a conversation, not a rubber stamp.
