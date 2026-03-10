# AGENTS.md — SEO Toolkit (PROD-001)

> Tool-agnostic agent instructions. Works with Claude Code, Cursor, Codex, Aider, and any tool that supports AGENTS.md.

## Project Overview

Reusable multi-website SEO automation toolkit — 8 agents + Python scripts. Audits, optimizes, tracks, and improves SEO for traditional search engines and AI discovery engines. Can be pointed at any website via JSON config.

## Tech Stack

- **Language:** Python 3.11+
- **Linting:** ruff + black (configured in pyproject.toml)
- **Type checking:** mypy (strict mode)
- **Testing:** pytest with --cov-fail-under=80
- **Mutation testing:** mutmut (weekly CI)
- **Pre-commit:** black, ruff, security hooks, pytest pre-push
- **CI:** GitHub Actions (lint, format, mypy, test, CodeQL SAST)
- **APIs:** DataForSEO, Google Search Console, SE Ranking, SerpAPI

## Commands

```bash
# Lint + format
ruff check scripts/ tests/
black --check scripts/ tests/

# Type check
mypy scripts/

# Test
python -m pytest tests/ -x --cov --cov-fail-under=80

# Pre-commit (all hooks)
pre-commit run --all-files
```

## Project Structure

```
configs/         # Per-website JSON configs
scripts/         # Python scripts by agent (audit/, keywords/, content/, links/, reporting/, ai-discovery/)
docs/agents/     # Detailed spec for each of 8 agents
tests/           # pytest test suite
skills/          # Claude Code skills (installed centrally)
```

## Style Guide

- Python: ruff-compliant, black-formatted, mypy strict
- Type hints on all function parameters and return values
- Google-style docstrings on public functions
- Max 30 lines per function, max 400 lines per file
- No bare `except:` — always catch specific exceptions

## Boundaries

- **Always do:** Run tests before committing. Update docs/todo.md and docs/architecture.md after changes.
- **Ask first:** Publishing content to live websites, submitting backlinks, making client site changes, spending >$1 on APIs.
- **Never do:** Hardcode API keys (use .env), commit .env files, bypass pre-commit hooks.
